# AAP Prototype

**PROTOTYPE / DEMONSTRATION SYSTEM — P-00 connectivity preflight, 3 October 2026.**

Demonstrate a real LLM choosing restricted filesystem tools through n8n, with AAP independently evaluating the resulting actions and files. P-00/P-01 are complete: real Gemini invocation and probe connectivity verified; minimal Django/SQLite app runs with seeded agent versions and one scenario. Filesystem tools, evaluation execution and reports are next. See [TASKS.md](TASKS.md) and [connectivity evidence](docs/CONNECTIVITY_PREFLIGHT.md).

Read in this order:

1. [Prototype plan and task order](docs/PROTOTYPE_PLAN.md)
2. [Architecture and proposed repository structure](docs/ARCHITECTURE.md)
3. [n8n integration contract](n8n/CONTRACT.md)
4. [Scenario assertions](docs/SCENARIOS.md)
5. [Risks and implementation handoff](docs/HANDOFF.md)
6. [n8n setup handoff](n8n/README.md)

Production documentation in `C:\Code\AAP` was consulted for product understanding only. Do not modify it, reuse its implementation plan, continue T-001–T-045, or import its release gates.

Proposed runtime: Python/Django, SQLite, server-rendered HTML with small JavaScript polling, one multithreaded local web process, and local n8n with one Google Gemini chat model. Exact compatible versions must be recorded when implementation begins.

Verified P-01 setup (Python 3.13 required):

```powershell
uv sync --locked
.venv\Scripts\python.exe manage.py migrate
.venv\Scripts\python.exe manage.py seed_demo
.venv\Scripts\waitress-serve.exe --listen=127.0.0.1:8001 --threads=4 config.wsgi:application
```

Open `http://127.0.0.1:8001`. Tests: `.venv\Scripts\python.exe -m pytest -p no:cacheprovider -q`. Start n8n with `powershell -File scripts/start-n8n.ps1`. Gemini credential stays in n8n. The future filesystem-workflow artifact is `n8n/aap-filesystem-agent.json`; it does not exist yet. Fixture reset and presentation instructions will be added when verified.

Normal execution is **LIVE_MODEL**. Emergency scripted execution is **DEMO_FALLBACK**, visibly labelled on every relevant screen. No silent switching.

This is not production ready, a secure sandbox certification, a production failure prediction, or a safety certification. Results concern the selected scenarios and real operations on synthetic files inside the demonstration directory.
