#!/usr/bin/env bash
# Escena de la demo: daemon arriba, un login normal (denegado) y el atacante
# entrando por el backdoor (RCE pre-auth como root).
set -e
cd "$(dirname "$0")"

python3 sshd_toy.py serve &
sleep 0.5

echo
echo "=== Cliente normal (no tiene la clave del atacante) ==="
python3 sshd_toy.py login hunter2

echo
echo "=== Atacante: payload firmado escondido en el handshake ==="
python3 sshd_toy.py attack "id; hostname; head -n1 /etc/shadow"

echo
echo ">>> Ejecución de comandos como root, ANTES de cualquier login."
echo ">>> sshd nunca fue tocado: el backdoor vivía en la 'liblzma' que importa."
