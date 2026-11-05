# Demo XZ — el momento del descubrimiento (CVE-2024-3094), aislado y reproducible.
# Construye dos liblzma falsas (una limpia, una con la firma del backdoor) y corre
# el detector contra las dos. Todo fake y offline: los bytes de la firma están
# plantados a mano, no hay backdoor real. ponytail: coreutils (od/tr/grep) alcanza,
# cero apt install.
FROM debian:12-slim
WORKDIR /lab
COPY detect.sh .
# bash: dash no interpreta \xHH en printf (los fixtures saldrían sin la firma)
SHELL ["/bin/bash", "-c"]
RUN chmod +x detect.sh \
 && printf 'una liblzma normal, nada raro adentro' > liblzma.clean.so \
 && printf 'padding\xf3\x0f\x1e\xfa\x55\x48\x89\xf5\x4c\x89\xce\x53\x89\xfb\x81\xe7\x00\x00\x00\x80\x48\x83\xec\x28\x48\x89\x54\x24\x08\x48\x89\x4c\x24\x10morepadding' > liblzma.vuln.so
# 5.6.0/5.6.1 = versiones backdooreadas; 5.6.1 queda etiquetada como la "mala".
CMD bash -c 'echo "== v5.4.6 (previa, buena) =="; ./detect.sh liblzma.clean.so; echo; echo "== v5.6.1 =="; ./detect.sh liblzma.vuln.so'
