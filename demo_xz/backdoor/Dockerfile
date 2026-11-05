# Demo XZ — "entrar por el backdoor" (CVE-2024-3094), simulación didáctica.
# Un sshd de juguete importa una 'liblzma' con un hook escondido y keyed; el
# atacante manda un payload firmado y ejecuta comandos PRE-auth como root.
# Todo fake y offline. NO es el binario real de XZ (eso es ED448 + IFUNC + amd64);
# acá el mecanismo es el mismo con HMAC de stdlib, reproducible en cualquier arch.
FROM python:3.12-slim
WORKDIR /backdoor
COPY backdoor_lib.py sshd_toy.py demo.sh ./
RUN chmod +x demo.sh
CMD ["bash", "demo.sh"]
