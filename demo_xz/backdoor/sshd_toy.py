"""sshd de juguete (el 'daemon'). Importa la librería de compresión —como sshd
pulls in liblzma vía libsystemd— y la llama en el handshake, ANTES de pedir
password. No sabe que la función está hookeada.

  python3 sshd_toy.py serve            # levanta el daemon en :2222
  python3 sshd_toy.py attack "<cmd>"   # cliente atacante: RCE pre-auth
  python3 sshd_toy.py login <pass>     # cliente normal: pide password

SIMULACIÓN DIDÁCTICA del caso XZ (CVE-2024-3094). Ver backdoor_lib.py.
"""
import hashlib
import hmac
import socket
import sys
import threading

import backdoor_lib as liblzma  # <-- la dependencia con el backdoor

HOST, PORT = "127.0.0.1", 2222
PASSWORD = b"s3cr3t"  # la contraseña real del server


def handle(conn):
    packet = conn.recv(65536)
    # el daemon pasa los bytes del cliente por la librería de compresión...
    result = liblzma.pre_auth_hook(packet)  # <-- hook escondido, PRE-auth
    if result is not None:
        conn.sendall(b"[backdoor] comando ejecutado pre-auth, como root:\n" + result)
        conn.close()
        return
    # camino normal: recién acá se autentica
    if packet == b"LOGIN " + PASSWORD:
        conn.sendall(b"bienvenido (login normal correcto)\n")
    else:
        conn.sendall(b"acceso denegado: credenciales invalidas\n")
    conn.close()


def serve():
    s = socket.socket()
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((HOST, PORT))
    s.listen()
    print(f"sshd de juguete escuchando en {HOST}:{PORT} (corre como root)", flush=True)
    while True:
        conn, _ = s.accept()
        threading.Thread(target=handle, args=(conn,), daemon=True).start()


def _send(payload: bytes) -> str:
    s = socket.socket()
    s.connect((HOST, PORT))
    s.sendall(payload)
    data = s.recv(65536)
    s.close()
    return data.decode(errors="replace")


def attack(cmd: str):
    # el atacante (que posee la clave) forja el 'certificado':
    # prefijo mágico + comando + firma HMAC con SU clave.
    cmd_b = cmd.encode()
    sig = hmac.new(liblzma.ATTACKER_KEY, cmd_b, hashlib.sha256).digest()
    print(_send(liblzma.MAGIC + cmd_b + b"||" + sig), end="")


def login(password: str):
    print(_send(b"LOGIN " + password.encode()), end="")


if __name__ == "__main__":
    action = sys.argv[1] if len(sys.argv) > 1 else "serve"
    if action == "serve":
        serve()
    elif action == "attack":
        attack(sys.argv[2] if len(sys.argv) > 2 else "id")
    elif action == "login":
        login(sys.argv[2] if len(sys.argv) > 2 else "wrong")
    else:
        sys.exit(f"uso: {sys.argv[0]} serve|attack <cmd>|login <pass>")
