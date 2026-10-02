# AAP Prototype

**PROTOTYPE / DEMONSTRATION SYSTEM — 3 October 2026.**

Demonstrate a real LLM choosing restricted filesystem tools through n8n, with AAP independently evaluating the resulting actions and files. P-00–P-04 are complete: the UI invokes real Google Gemini through n8n, restricted tools change the real demo files, and AAP records evidence. Full trace presentation and deterministic evaluation are next. See [TASKS.md](TASKS.md) and [connectivity evidence](docs/CONNECTIVITY_PREFLIGHT.md).

Read in this order:

1. [Prototype plan and task order](docs/PROTOTYPE_PLAN.md)
2. [Architecture and proposed repository structure](docs/ARCHITECTURE.md)
3. [n8n integration contract](n8n/CONTRACT.md)
4. [Scenario assertions](docs/SCENARIOS.md)
5. [Risks and implementation handoff](docs/HANDOFF.md)
6. [n8n setup handoff](n8n/README.md)

Production documentation in `C:\Code\AAP` was consulted for product understanding only. Do not modify it, reuse its implementation plan, continue T-001–T-045, or import its release gates.

Runtime: Python 3.13.15, Django 5.2.17, SQLite, Waitress 3.0.2, server-rendered HTML with JavaScript polling, and native n8n 2.41.6 with Google Gemini `models/gemini-3-flash-preview`. Run one app process only.

Verified P-01 setup (Python 3.13 required):

```powershell
uv sync --locked
.venv\Scripts\python.exe manage.py migrate
.venv\Scripts\python.exe manage.py seed_demo
.venv\Scripts\python.exe manage.py serve_demo
```

Open `http://127.0.0.1:8001/runs/new`. Tests: `.venv\Scripts\python.exe -m pytest -p no:cacheprovider --basetemp=C:\Code\AAP-Prototype\.runtime\test-tmp -q`. The UI resets the owned fixture before each run and rejects simultaneous start/reset. CLI reset is only for a stopped app: `.venv\Scripts\python.exe manage.py reset_demo`. Start n8n with `powershell -File scripts/start-n8n.ps1`; import/configure the committed workflow as described in `n8n/README.md`. Gemini credential stays in n8n. `serve_demo` marks unfinished historical runs interrupted on startup; it never resumes or retries them. Presentation instructions will be added when verified.

Normal execution is **LIVE_MODEL**. Emergency scripted execution is **DEMO_FALLBACK**, visibly labelled on every relevant screen. No silent switching.

This is not production ready, a secure sandbox certification, a production failure prediction, or a safety certification. Results concern the selected scenarios and real operations on synthetic files inside the demonstration directory.
