# AAP Prototype

**PROTOTYPE / DEMONSTRATION SYSTEM — P-00 connectivity preflight, 3 October 2026.**

Demonstrate a real LLM choosing restricted filesystem tools through n8n, with AAP independently evaluating the resulting actions and files. The approved plan is frozen with the user's amendments. Native n8n 2.41.6 is installed/running with an imported connectivity preflight; a real Gemini invocation and both connection directions are verified. No Django application, evaluator, demo filesystem or filesystem-agent workflow exists yet. See [TASKS.md](TASKS.md) and [connectivity evidence](docs/CONNECTIVITY_PREFLIGHT.md).

Read in this order:

1. [Prototype plan and task order](docs/PROTOTYPE_PLAN.md)
2. [Architecture and proposed repository structure](docs/ARCHITECTURE.md)
3. [n8n integration contract](n8n/CONTRACT.md)
4. [Scenario assertions](docs/SCENARIOS.md)
5. [Risks and implementation handoff](docs/HANDOFF.md)
6. [n8n setup handoff](n8n/README.md)

Production documentation in `C:\Code\AAP` was consulted for product understanding only. Do not modify it, reuse its implementation plan, continue T-001–T-045, or import its release gates.

Proposed runtime: Python/Django, SQLite, server-rendered HTML with small JavaScript polling, one multithreaded local web process, and local n8n with one Google Gemini chat model. Exact compatible versions must be recorded when implementation begins.

Installation and launch commands will be added only after they work. Planned setup covers app/database initialization, embedded filesystem service, n8n startup and workflow import, model credentials, webhook configuration, fixture reset, and presentation rehearsal. The future import artifact is `n8n/aap-filesystem-agent.json`; it does not exist yet.

Normal execution is **LIVE_MODEL**. Emergency scripted execution is **DEMO_FALLBACK**, visibly labelled on every relevant screen. No silent switching.

This is not production ready, a secure sandbox certification, a production failure prediction, or a safety certification. Results concern the selected scenarios and real operations on synthetic files inside the demonstration directory.
