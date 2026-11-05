#!/usr/bin/env bash
# Detección del backdoor de XZ Utils (CVE-2024-3094), al estilo del script que
# circuló en el disclosure de marzo 2024: busca en el binario la firma del hook
# que liblzma 5.6.0/5.6.1 inyectaba en sshd. No ejecuta nada del backdoor; sólo
# lee bytes. Firma tomada del análisis de amlweems/xzbot.
#
#   ./detect.sh <ruta-a-liblzma.so>
#
# Sale 1 si la firma está presente (comprometida), 0 si no.
set -eu

lib="${1:?uso: detect.sh <ruta a liblzma.so>}"
SIG='f30f1efa554889f54c89ce5389fb81e7000000804883ec28488954240848894c2410'

echo "escaneando: $lib"
# od -v: sin squeezing de líneas repetidas; tr: hex continuo; grep: la firma
if od -v -An -tx1 "$lib" | tr -d ' \n' | grep -q "$SIG"; then
  echo "🔴 BACKDOOR: firma de CVE-2024-3094 encontrada — liblzma comprometida (5.6.0/5.6.1)"
  exit 1
else
  echo "🟢 LIMPIO: no se encontró la firma del backdoor"
  exit 0
fi
