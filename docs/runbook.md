# Runbook de demos — Secure by Design (05/11)

Dos demos. A corre en GitHub Actions (nube, gratis) + CLI local de fallback.
B es 100% local. **Railway no hace falta** para ninguna (ver abajo).

---

## Qué necesitás instalar (antes de la charla)

En tu Mac:

```bash
# Herramientas de la Demo A (fallback local; el CI ya las corre en la nube)
brew install gitleaks pre-commit trivy
pipx install semgrep checkov      # o: pip install semgrep checkov

# Demo B
cd demo_b && python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export ANTHROPIC_API_KEY=sk-ant-...      # <-- IMPRESCINDIBLE para la Demo B
```

Checklist del guion que sigue vigente:
- [ ] `trivy image --download-db-only` la mañana de la charla (DB de CVEs fresca)
- [ ] Probar que el secreto falso elegido **sí** dispara gitleaks (ver Demo A, paso 1)
- [ ] Ensayar la Demo B 3 veces; si falla 1 de 3, tener grabación de backup
- [ ] Terminal a 20pt+, tema claro

---

## Demo A — "El PR que no pasa" (~8 min)

**Ya está preparado:** `main` está limpio (CI verde). La rama `demo/risky-change`
mete las 4 vulnerabilidades y el PR queda en **rojo** con un hallazgo por herramienta.
El PR ya está abierto (link más abajo).

### Secuencia en vivo

**1. El secret (1.5 min)** — en `main`, en vivo. Generá una key falsa pero con
formato válido (NO la pegues en ningún archivo versionado del repo, sólo en el `.env`):
```bash
# key falsa con formato Stripe: sk_live_ + 24+ alfanuméricos (sin guiones)
echo "STRIPE_KEY=sk_live_$(LC_ALL=C tr -dc 'a-zA-Z0-9' </dev/urandom | head -c 24)" > .env
git add .env && git commit -m "wip"
```
El hook de gitleaks **bloquea el commit**. "200 ms y te ahorrás rotar credenciales
un viernes a la noche."
> ⚠️ Verificar en el ensayo que el string dispara gitleaks. Evitar `AKIA...EXAMPLE`
> (gitleaks lo ignora). Alternativa: PAT falso `ghp_` + 36 alfanuméricos.

**2. El dev apurado (1 min):**
```bash
git commit --no-verify -m "wip"      # saltea el hook local
git push
```
"El hook es local y se saltea." Acá pasan DOS cosas, y las dos son la lección:
- **GitHub Push Protection** rechaza el push ahí mismo (este repo lo tiene activo —
  lo confirmamos preparando la demo: una Stripe key falsa frenó hasta el push de los docs).
- Y si push protection estuviera apagado, el **job de gitleaks en CI** queda rojo.
  "Tres capas: pre-commit local → push protection → CI. Y los logs del CI son públicos."

**3. El PR rojo (4 min)** — abrir los checks del PR y recorrer un hallazgo por tool:
- **semgrep** → SQL injection en `app.py` (línea exacta + fix: query parametrizada)
- **trivy** → CVEs en `requests==2.19.1` y `PyYAML==5.3`; Dockerfile como root, base vieja
- **checkov** → bucket S3 público y SSH 0.0.0.0/0 en `infra/main.tf`

**4. Cierre (1 min):** "Cuatro herramientas open source, cero licencias, un YAML.
Secrets, deps, IaC, injection — todo frenado antes del merge."

### Fallback local (si el CI o el WiFi fallan)
```bash
git checkout demo/risky-change
gitleaks dir . -v
semgrep scan --config p/owasp-top-ten --config p/python .
trivy fs --scanners vuln,misconfig .
checkov -d infra/ --compact
```

---

## Demo B — "El README que da órdenes" (~5 min)

Ver `demo_b/README.md`. **Hallazgo:** la inyección explícita no la ejecuta ningún
Claude vigente (probados 7: rechazan, avisan o la ignoran). La narrativa es
tranquilizadora pero con el asterisco correcto — "hoy el modelo te cubrió, pero no
dependas de eso; cerrá la puerta por arquitectura".

Secuencia en vivo:

1. **La tabla (el momento):** `cd demo_b && python3 compare.py` → corre la inyección
   contra todos los modelos y muestra la reacción de cada uno. Si hay key de OpenRouter,
   suma Kimi/GLM/Qwen (si alguno exfiltra, ahí está la prueba de "no dependas del modelo").
2. **Un caso en vivo:** `python3 agent.py` contra opus-5-5 → `refusal`/avisa.
   "La defensa funcionó. Pero mirá por qué no alcanza:"
3. **La mitigación (sólida):** `DEMO_SAFE=1 python3 agent.py` → sin `http_post`, el
   ataque es imposible para cualquier modelo. Esa pata rota es TU control.

Cierre: "No hace falta volverse paranoico; hace falta no darle a un agente las tres
patas a la vez. Con eso dormís tranquilo aunque el modelo tenga un mal día."

> Para probar modelos no-Claude: `OPENROUTER_API_KEY` (openrouter.ai/keys) y
> `python3 agent_openai.py moonshotai/kimi-k2`. Detalle en `demo_b/README.md`.

---

## ¿Por qué no Railway?

- **Demo A** corre en GitHub Actions (nube, gratis) + CLI local. No hay app que hostear.
- **Demo B** es a propósito 100% localhost (el guion lo pide): el README malicioso y
  el listener del atacante viven en `localhost:8000/8080`. Hostearlo afuera agrega
  dependencia de red (el guion dice "no depender del WiFi") y nada de valor.

Si igual querés algo desplegado (p.ej. mostrar la Flask app vulnerable corriendo),
se puede subir `demo/risky-change` a Railway en 2 min — pero no es necesario para
que ninguna de las dos demos funcione.
