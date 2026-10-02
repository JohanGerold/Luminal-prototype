# AAP three-day prototype implementation plan

> Approved and frozen, with the user's four amendments on 3 October 2026. Execute sequentially; see `../TASKS.md` for actual checkpoint state. After each meaningful checkpoint verify, update TASKS/HANDOFF, commit, and check the working tree.

**Goal:** Deliver a ten-minute demonstration of real n8n agent execution, restricted real file changes, independent deterministic evaluation, and inspectable failure evidence.

**Architecture:** One local Django application owns SQLite, execution orchestration, the restricted filesystem API, evaluation, and reports. Local n8n owns the real model/tool loop. One scenario executes at a time.

**Tech stack:** Python, Django, SQLite, Waitress, plain HTML/CSS/JavaScript, n8n, one OpenAI model. Versions are implementation-time pins, not inherited production requirements.

**Spec:** User's pasted “3-Day Working Prototype — Master Implementation Brief”; decisions are made concrete in [architecture](ARCHITECTURE.md), [scenarios](SCENARIOS.md), and [contract](../n8n/CONTRACT.md).

## Constraints and scope decisions

- Work only in `C:\Code\AAP-Prototype`; runtime demo files belong only in `C:\AAP-Demo-Workspace`.
- No production code copying, production task continuation, IAM, RLS, queues, leases, CI infrastructure, hosted deployment, billing, arbitrary code execution, or semantic judge.
- P0 precedes P1. Seed V1/V2 configuration as P0; defer comparison UI until all P0, including fallback, works. This resolves Stage 9 versus the brief's stronger P0-first instruction. Comparison remains desirable for the final story; report explicitly if omitted.
- Mixed live outcomes and V2 improvement are observations, not guaranteed outputs. Never force a live verdict. A recorded live failure may be shown as recorded; scripted runs remain fallback.
- Day numbers are work blocks, not a claimed start date. Budget approximately eight focused hours per day; cut optional work before compromising the live path.
- Every evaluation run records and visibly displays `LIVE_MODEL` or `DEMO_FALLBACK`; live outcomes are never fabricated or forced.
- P-02 must enforce that model-controlled paths cannot escape `C:\AAP-Demo-Workspace`. Obscure filesystem hardening must not jeopardize Day-1 live E2E; retain core containment and safe reset checks.
- Execute minimal P-09 immediately after P-05/P-06 stabilize trace/evaluator contracts, before remaining scenarios or significant polish. Later fallback refinement may stay on Day 3.

## Critical presentation path

Open agent/configuration → show scenarios → reset fixture → run Scenario 1 in LIVE_MODEL → watch logged tools and actual file changes → independent PASS/FAIL → inspect trace/report → run adversarial scenario → inspect attempted action and prevented effect. Compare versions only after P0. No terminal interaction during the presentation.

## Ordered tasks

Each row is a sequential checkpoint. Write focused failing tests for safety/evaluation behavior, implement, then verify; do not advance past a failed stop condition. Paths are prospective, not existing code.

| Task / time | Files and deliverable | Verification / stop condition |
|---|---|---|
| [ ] P-00 / Day 1, first checkpoint | Record exact n8n version; start n8n; configure/select real model credential; trivial native AI Agent request; determine native/Docker hosting; document exact n8n → Django and Django → n8n URLs. | n8n starts, a trivial AI Agent reaches the real model, and both URL directions are established and documented. **Do not begin P-01 until this passes.** |
| [ ] P-01 / Day 1, 1h | `manage.py`, `config/*`, `aap/models.py`, `aap/management/commands/seed_demo.py`, `templates/base.html`, dependency/config files. Minimal schema, seed agent versions, app shell. | App starts, SQLite migrates, repeated seeding produces one copy; health page and agent detail render. |
| [ ] P-02 / Day 1, 2.5h | `aap/filesystem/{paths,service,fixtures}.py`, `aap/api.py`, `tests/test_filesystem.py`. Six tools, fixture reset, structured events, serialized access. | Real create/move/delete works in owned fixture. Traversal, absolute paths, junctions, root deletion and foreign files are refused; refused attempts logged. |
| [ ] P-03 / Day 1, 2.5h | `n8n/aap-filesystem-agent.json`, `n8n/README.md`, `aap/prompts/*`, `tests/test_contract.py`. Webhook → native AI Agent + real model + six HTTP tools → normalized response. | Import on recorded n8n version; user selects credential; manual webhook causes real model-selected file changes. **Do not continue without this proof.** |
| [ ] P-04 / Day 1, 2h | `aap/runs.py`, `aap/n8n_client.py`, `templates/run.html`, `static/run.js`, `tests/test_runs.py`. Start API returns run ID; bounded background execution; polling. Scenario 1 only. | UI click organizes files through real n8n model. Double start/reset during execution returns conflict; timeout closes tools; late calls cannot alter files. |
| [ ] P-05 / Day 2, 1h | `aap/traces.py`, `templates/trace.html`. Ordered user/tool/final-response events, timestamps and errors. | Every filesystem attempt has an inspectable event; sequence/order survives reload; no invented thoughts. |
| [ ] P-06 / Day 2, 2h | `aap/evaluation.py`, `tests/test_evaluation.py`. Pure evaluation of recorded evidence and snapshots. | Scenario 1 state checks; proven violation wins over missing unrelated evidence; missing required evidence never passes; evaluator exception yields UNCERTAIN. |
| [ ] P-07 / Day 2, 2h | `aap/seeds/scenarios.json`, seed command, `tests/test_scenarios.py`. Remaining five scenarios and server-owned fault injection. | All six can run; synthetic positive/negative evidence tests prove each rule. Record actual live outcomes without requiring a predetermined pass rate. |
| [ ] P-08 / Day 2, 2h | `aap/reporting.py`, `templates/report.html`, `templates/agent.html`. Before/after, assertions, categories, timing, counts, configuration/tools. | Report links findings to event/state evidence; execution status separate from verdict; failed run understandable without terminal. |
| [ ] P-09 / immediately after P-06, 1.5h | `aap/fallback.py`, `aap/seeds/fallback_actions.json`, `tests/test_fallback.py`. Minimal explicit emergency scripted mode using same guarded tools and evaluator, before P-07; polish later. | Disconnect n8n; fresh fallback run still completes with prominent DEMO_FALLBACK label; never relabel failed live run. |
| [ ] P-10 / Day 3, at most 1h; P1 | `aap/comparison.py`, `templates/compare.html`. Pair same six scenarios/fixture/rules/limits for V1 and V2. | Fixed/new/unchanged failures and uncertain transitions reflect saved results; mismatched inputs labelled incomparable. Skip if any P0 unresolved. |
| [ ] P-11 / Day 3, 2h | `static/app.css`, templates, README, `scripts/start-demo.ps1`. Restrained presentation, accessible states, startup/preflight guide. | Keyboard/reduced-motion checks; loading/error/empty states; no backend rewrite; launcher tested from documented prerequisites. |
| [ ] P-12 / Day 3, remaining time | `docs/DEMO_RUNBOOK.md`, `docs/VERIFICATION.md`, focused bug fixes. | Three reset/live/trace/report repetitions; adversarial case; outage fallback; restart recovery. Record failures, actual versions and limitations. |

## Review focus

1. Windows path aliases/reparse points: P-02 tests reject device/UNC/drive-relative/ADS paths, prefix siblings and linked ancestors.
2. Lost response after side effect: P-04 does not resend dispatch automatically; closes token and preserves evidence; P-06 refuses fabricated success.
3. Late tools versus reset: P-04 tests terminal tokens and active reset conflict under concurrent requests.
4. Confusing no-op/retry with repeated effect: P-07 tests successful effects separately from attempts and controlled retries.
5. Provider outage or truncated evidence: P-06/P-09 preserve UNCERTAIN unless an independently supported violation proves FAIL; fallback is a new labelled run.

If Day 1 misses live E2E, stop design work and fix connectivity/tool execution. If Day 2 slips, remove comparison, editing, charts, generation and elaborate motion. Do not remove safety checks, trace evidence, deterministic evaluation or fallback.
