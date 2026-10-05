# Luminal

Luminal is a local AI agent evaluation workspace. It shows what an agent was asked to do, which tools it requested, what changed on disk, and what the saved evidence supports.

The prototype demonstrates this path:

**AAP UI -> n8n -> Google Gemini -> guarded filesystem tools -> synthetic workspace -> trace -> deterministic evaluator -> report**

The project is designed for a short technical demonstration. It keeps model execution, filesystem effects, evidence capture, evaluation, and presentation reporting as separate concepts.

## What is included

- Native n8n 2.41.6 integration with Google Gemini `models/gemini-3-flash-preview`
- Django and SQLite application with server-rendered pages and small polling scripts
- Guarded filesystem tools restricted to `C:\AAP-Demo-Workspace`
- Six seeded evaluation scenarios
- Ordered trace events with tool intent and result records
- Deterministic `PASS`, `FAIL`, and `UNCERTAIN` verdicts
- Explicit `LIVE_MODEL` and `DEMO_FALLBACK` execution modes
- Saved reports with execution status, verdict, assertions, trace links, and before/after filesystem evidence
- Offline fallback that uses the same guarded filesystem and evaluator contracts
- Saved V1/V2 comparison support, with incompatible or missing data shown as pending
- Monochrome Luminal interface, scroll-driven landing page, report, trace, and presentation views
- Presentation materials in [`presentation-output/`](presentation-output/) and [`report-output/`](report-output/)

## Quick start

Use the included launcher on Windows:

```bat
start.bat
```

It closes listeners on the prototype's fixed AAP and n8n ports, starts fresh hidden services, waits for readiness, and opens the product in the default browser.

The equivalent PowerShell command is:

```powershell
powershell -File scripts/start-demo.ps1 -Restart
```

The application opens at [http://127.0.0.1:8001/](http://127.0.0.1:8001/). The landing page is the Luminal introduction; choose **Enter workspace** or scroll through the hand-contact transition. Direct workspace access is available at [http://127.0.0.1:8001/workspace](http://127.0.0.1:8001/workspace).

## First-time setup

The launcher expects an existing local environment and configured n8n credential. It does not install packages, create credentials, or expose secrets.

```powershell
uv sync --locked
.venv\Scripts\python.exe manage.py migrate
.venv\Scripts\python.exe manage.py seed_demo
```

Configure the native Google Gemini credential in local n8n as described in [`n8n/README.md`](n8n/README.md). The credential remains in n8n's encrypted local state. Do not put API keys in Git, workflow JSON, documentation, logs, or chat.

Useful local URLs:

- AAP: `http://127.0.0.1:8001/`
- AAP health: `http://127.0.0.1:8001/health`
- n8n: `http://127.0.0.1:5678/`
- n8n health: `http://127.0.0.1:5678/healthz`

## Demonstration flow

1. Open the Luminal introduction and enter the workspace.
2. Inspect the configured agent and its six restricted tools.
3. Choose a scenario and reset the owned synthetic workspace.
4. Select `LIVE_MODEL` explicitly when Gemini capacity is available.
5. Start one evaluation and observe progress and tool activity.
6. Inspect the saved report, trace, assertions, and filesystem before/after state.
7. Use a separate `DEMO_FALLBACK` run only when demonstrating an n8n or provider outage.

The UI prevents simultaneous starts and resets. Refreshing a run reads saved evidence and never dispatches a second model call. A failed live execution remains a live execution; it is never silently converted to fallback.

## Evidence and evaluation

Luminal keeps these concepts separate:

- **Execution status:** preparing, executing, completed, failed, timed out, or interrupted.
- **Execution mode:** `LIVE_MODEL` or `DEMO_FALLBACK`.
- **Verdict:** `PASS`, `FAIL`, or `UNCERTAIN` based on saved evidence.

The evaluator checks scenario assertions against persisted inputs, ordered trace events, filesystem snapshots, content hashes, and completion evidence. A provider rate limit or incomplete record is reported as `UNCERTAIN`; it is not presented as a behavioral failure without independent evidence.

The six seeded scenarios cover normal organization, ambiguous cleanup, boundary requests, controlled tool failure, incomplete PDF organization, and duplicate/repeated actions.

## Verification status

The non-live prototype verification record contains **98 tests**. The latest sandbox check passed 97 tests and deselected one Windows junction-creation test because this environment does not grant link-creation privileges; clean Django checks, browser checks for report/trace/reset/refresh/fallback labeling, and verified startup/recovery behavior also pass.

Saved genuine evidence includes successful `LIVE_MODEL` runs, an honestly recorded quota-interrupted `LIVE_MODEL` run, and separate `DEMO_FALLBACK` PASS/FAIL examples. Remaining live scenario coverage and the full live rehearsal are held when Gemini quota is unavailable; no missing result is fabricated.

Read the durable project records in this order:

1. [`TASKS.md`](TASKS.md)
2. [`docs/PROTOTYPE_PLAN.md`](docs/PROTOTYPE_PLAN.md)
3. [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md)
4. [`docs/SCENARIOS.md`](docs/SCENARIOS.md)
5. [`docs/HANDOFF.md`](docs/HANDOFF.md)
6. [`docs/VERIFICATION.md`](docs/VERIFICATION.md)
7. [`docs/DEMO_RUNBOOK.md`](docs/DEMO_RUNBOOK.md)

## Limitations

This is a local presentation prototype, not a production safety certification.

- Gemini API quota and provider availability can interrupt live scenarios.
- Only one provider and one Gemini model are configured, so cross-provider reliability is not measured.
- Scenarios use a synthetic Windows fixture rather than arbitrary user files.
- The deterministic evaluator checks explicit observable assertions; it is not a general semantic judge.
- n8n and the AAP app are local dependencies that can fail independently.
- Filesystem containment assumes a trusted local operator and is not hostile-process isolation.
- Remaining unverified live scenarios are kept pending rather than replaced with fallback data.

## Presentation files

- [PowerPoint presentation](presentation-output/Liminal_Agent_Evaluation_Overview.pptx)
- [Project report PDF](report-output/Liminal_Project_Report.pdf)
- [Editable project report](report-output/Liminal_Project_Report.docx)

## Tests

```powershell
.venv\Scripts\python.exe -m pytest -p no:cacheprovider --basetemp=C:\Code\AAP-Prototype\.runtime\test-tmp -q
.venv\Scripts\python.exe manage.py check
```

Production documentation in `C:\Code\AAP` was consulted for product understanding only. This repository is the separate Luminal prototype and does not modify the production checkout.
