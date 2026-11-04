# Demo B — "El README que da órdenes"

Prompt injection contra un agente. 100% local, secretos falsos. El punto es la
arquitectura (lethal trifecta), no el payload.

## Setup (una vez)

```bash
cd demo_b
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export ANTHROPIC_API_KEY=sk-ant-...     # necesario para que el agente corra
```

## Correr la demo

Dos terminales, lado a lado:

**Terminal 1 — los servidores** (README en :8000, listener del atacante en :8080):
```bash
python3 servers.py
```

**Terminal 2 — el agente:**
```bash
python3 agent.py            # VULNERABLE: tiene las tres patas de la trifecta
```

Se le pide algo inocente ("resumime el README"). El agente hace fetch del README,
lee la instrucción escondida en un comentario HTML, lee `project/.env` y lo manda
al listener. En la Terminal 1 aparece el `.env` en rojo.

## La mitigación (romper una pata)

```bash
DEMO_SAFE=1 python3 agent.py   # saca http_post -> el agente ya no puede exfiltrar
```

El agente puede leer el `.env`, pero no tiene forma de sacarlo. Ataque fallido.

## Las tres patas (demo_b/agent.py)

| Pata | Tool | De dónde viene el riesgo |
|------|------|--------------------------|
| Datos privados | `read_file` | lee `project/.env` |
| Contenido no confiable | `fetch_url` | el README servido en :8000 |
| Salida hacia afuera | `http_post` | manda al listener en :8080 |

Si el modelo se resiste en vivo: también es lección — la defensa no puede depender
de que el modelo tenga un buen día. Tener grabada la corrida donde sí funciona.
