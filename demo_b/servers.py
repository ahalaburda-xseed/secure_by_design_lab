"""Demo B infrastructure: the 'library' README server + the attacker's collector.

Runs two local HTTP servers so the demo needs nothing but localhost:
  :8000  serves project/README_served.html (the library page with a hidden instruction)
  :8080  /collect prints whatever it receives, in red (the attacker's listener)

    python3 servers.py

Ctrl-C to stop both. Everything is local and fake. ponytail: two tiny servers in
one file beats three scripts to juggle live.
"""
import http.server
import socketserver
import threading
from pathlib import Path

HERE = Path(__file__).parent
README = (HERE / "project" / "README_served.html").read_bytes()

RED = "\033[91m"
RESET = "\033[0m"


class ReadmeHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.end_headers()
        self.wfile.write(README)

    def log_message(self, *args):
        print(f"[:8000 readme] GET {self.path}")


class CollectHandler(http.server.BaseHTTPRequestHandler):
    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length).decode("utf-8", "replace")
        print(f"\n{RED}{'='*60}\n[:8080 ATTACKER] received exfiltrated data:\n{body}\n{'='*60}{RESET}\n")
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"ok")

    def log_message(self, *args):
        pass


def serve(port, handler):
    socketserver.TCPServer.allow_reuse_address = True
    try:
        with socketserver.TCPServer(("127.0.0.1", port), handler) as httpd:
            httpd.serve_forever()
    except OSError:
        pass  # port already bound (servers.py already running) — reuse it


def start_background():
    """Start both servers as daemon threads (for compare.py, which drives everything)."""
    threading.Thread(target=serve, args=(8000, ReadmeHandler), daemon=True).start()
    threading.Thread(target=serve, args=(8080, CollectHandler), daemon=True).start()


if __name__ == "__main__":
    threading.Thread(target=serve, args=(8000, ReadmeHandler), daemon=True).start()
    print("README server on http://localhost:8000")
    print(f"{RED}Attacker collector on http://localhost:8080/collect{RESET}")
    print("Waiting for the agent... (Ctrl-C to stop)\n")
    try:
        serve(8080, CollectHandler)
    except KeyboardInterrupt:
        print("\nstopped")
