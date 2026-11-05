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

## El cierre (encaja en el bloque de supply chain)

"No lo encontró un scanner ni un code review: lo encontró un ingeniero que
notó medio segundo de más. La lección no es 'tené mejores ojos' — es que el
riesgo vivía en una dependencia transitiva compilada, antes de tu producción.
Por eso el A03 del OWASP 2025 es Supply Chain, y por eso pinnear y escanear
dependencias deja de ser opcional."

> La firma (`f30f1efa...`) es la del hook real documentada por amlweems/xzbot.
> Los dos `.so` son fixtures de mentira con esa firma plantada: no hay backdoor
> ejecutable acá, sólo los bytes que el detector busca.
