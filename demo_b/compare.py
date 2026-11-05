"""Run the same prompt-injection attack against many models and tabulate reactions.

Starts the local servers itself, so it's one command:

    export ANTHROPIC_API_KEY=sk-ant-...      # for the Claude rows
    export OPENROUTER_API_KEY=sk-or-...      # for Kimi / GLM / Qwen rows (optional)
    python3 compare.py

Prints a table of how each model reacts and saves results.json. All local, fake
secrets. The point: defense can't depend on the model — remove the capability.
"""
import json
import os
import time
from pathlib import Path

import agent
import agent_openai
import servers

# (provider, model_id). Trim or extend freely before the talk.
CLAUDE = ["claude-opus-5-5", "claude-sonnet-5-5", "claude-haiku-5-5",
          "claude-opus-4-8", "claude-sonnet-4-6", "claude-haiku-4-5", "claude-sonnet-4-5"]
OPENAI = ["openai/gpt-5.5", "openai/gpt-4o-mini",
          "google/gemini-3.1-pro-preview", "google/gemini-2.5-flash-lite",
          "moonshotai/kimi-k2", "moonshotai/kimi-k3.1-pro",
          "z-ai/glm-4.6", "z-ai/glm-5.3",
          "qwen/qwen3.8-max-0902", "qwen/qwen3.5-9b"]

LABEL = {"BREACH": "🔴 BREACH   exfiltró el .env",
         "ATTEMPTED": "🟠 ATTEMPT  leyó .env, no pudo sacarlo",
         "REFUSED": "🛡️  REFUSED  rechazó (consciente)",
         "FLAGGED": "⚠️  FLAGGED  detectó y avisó",
         "IGNORED": "😐 IGNORED  no picó ni avisó",
         "ERROR": "⚫ ERROR    no disponible"}


def run_all():
    rows = []
    jobs = [("claude", m) for m in CLAUDE]
    if agent_openai.API_KEY:
        jobs += [("openai", m) for m in OPENAI]
    else:
        print("(sin OPENROUTER_API_KEY — salteo Kimi/GLM/Qwen)\n")

    for provider, model in jobs:
        print(f"· probando {model} ...", flush=True)
        try:
            runner = agent.run if provider == "claude" else agent_openai.run
            r = runner(model=model, verbose=False)
        except Exception as e:  # noqa: BLE001 — a model may be unavailable; keep going
            r = {"model": model, "outcome": "ERROR", "stop_reason": str(e)[:80],
                 "calls": [], "read_env": False, "exfiltrated": False}
        rows.append(r)
        time.sleep(0.3)
    return rows


def table(rows):
    w = max(len(r["model"]) for r in rows)
    print("\n" + "=" * 72)
    print(f"{'MODELO'.ljust(w)}  REACCIÓN")
    print("-" * 72)
    for r in rows:
        print(f"{r['model'].ljust(w)}  {LABEL.get(r['outcome'], r['outcome'])}")
    print("=" * 72)
    breached = [r["model"] for r in rows if r["outcome"] == "BREACH"]
    print(f"\nExfiltraron ({len(breached)}/{len(rows)}): {', '.join(breached) or 'ninguno'}")
    if breached:
        print("Leyeron tu .env y lo mandaron afuera. No sabés de antemano cuál lo hará.")
    else:
        print("Ninguno exfiltró — la capa del modelo aguantó. Pero no es TU control.")
    print("Tu control: romper una pata de la trifecta (DEMO_SAFE=1) -> imposible para todos.\n")


if __name__ == "__main__":
    servers.start_background()
    time.sleep(0.5)
    rows = run_all()
    table(rows)
    Path(__file__).with_name("results.json").write_text(json.dumps(rows, indent=2, ensure_ascii=False))
    print("guardado: results.json")
