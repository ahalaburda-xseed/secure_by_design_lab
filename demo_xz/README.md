# Demo XZ — "medio segundo de más" (CVE-2024-3094)

Reproduce el **momento del descubrimiento**, no el backdoor. Freund notó un SSH
lento; tiró del hilo; encontró la firma del hook en `liblzma`. Esto hace lo último:
corre el detector del disclosure contra dos binarios plantados (uno limpio, uno
con la firma), todo fake y offline. El punto: el código malicioso no estaba a la
vista en el repo — se detectó por una **firma en el binario compilado**, no en un
code review.

## Correr (docker, aislado — no toca el liblzma real de tu Mac)

```bash
cd demo_xz
docker build -t xz-demo .
docker run --rm xz-demo
```

Salida esperada:
```
== v5.4.6 (previa, buena) ==
🟢 LIMPIO: no se encontró la firma del backdoor
== v5.6.1 ==
🔴 BACKDOOR: firma de CVE-2024-3094 encontrada — liblzma comprometida (5.6.0/5.6.1)
```

## Fallback sin docker

```bash
cd demo_xz
printf 'nada raro' > /tmp/clean.so
printf 'x\xf3\x0f\x1e\xfa\x55\x48\x89\xf5\x4c\x89\xce\x53\x89\xfb\x81\xe7\x00\x00\x00\x80\x48\x83\xec\x28\x48\x89\x54\x24\x08\x48\x89\x4c\x24\x10y' > /tmp/vuln.so
./detect.sh /tmp/clean.so   # 🟢
./detect.sh /tmp/vuln.so    # 🔴
```

## Parte 2 (opcional, más fuerte): entrar por el backdoor — `backdoor/`

El detector muestra que *estaba ahí*; esto muestra *qué se puede hacer*. Un sshd de
juguete importa una "liblzma" con un hook escondido y **keyed**; el atacante manda
un payload firmado en el handshake y ejecuta comandos **pre-autenticación, como root**.

```bash
cd backdoor
docker build -t xz-backdoor .
docker run --rm xz-backdoor      # login normal → denegado; atacante → shell root pre-auth
```

Salida clave:
```
=== Cliente normal (no tiene la clave del atacante) ===
acceso denegado: credenciales invalidas
=== Atacante: payload firmado escondido en el handshake ===
[backdoor] comando ejecutado pre-auth, como root:
uid=0(root) gid=0(root) groups=0(root)
```

Interactivo (si querés tipear el comando en vivo):
```bash
docker run --rm -it xz-backdoor bash
# dentro del container:
python3 sshd_toy.py serve &
python3 sshd_toy.py attack "id; cat /etc/shadow"   # RCE como root, sin login
python3 sshd_toy.py login s3cr3t                   # el login normal, para contrastar
```

**Honestidad (decilo en la charla):** es una *simulación del mecanismo*, no el binario
real de XZ. El real hookea `RSA_public_decrypt` vía IFUNC y verifica una firma **ED448**
del atacante (x86-64). Acá reproducimos lo que importa —**keyed, pre-auth, RCE, escondido
en una dependencia**— con HMAC de la stdlib para que corra offline en cualquier máquina.
Lo *keyed* es fiel y clave: por eso XZ no se explotó masivamente — solo el dueño de la
clave podía disparar el backdoor.

## El cierre (encaja en el bloque de supply chain)

"No lo encontró un scanner ni un code review: lo encontró un ingeniero que
notó medio segundo de más. La lección no es 'tené mejores ojos' — es que el
riesgo vivía en una dependencia transitiva compilada, antes de tu producción.
Por eso el A03 del OWASP 2025 es Supply Chain, y por eso pinnear y escanear
dependencias deja de ser opcional."

> La firma (`f30f1efa...`) es la del hook real documentada por amlweems/xzbot.
> Los dos `.so` son fixtures de mentira con esa firma plantada: no hay backdoor
> ejecutable acá, sólo los bytes que el detector busca.
