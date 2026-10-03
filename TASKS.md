# Prototype task ledger

Plan: `docs/PROTOTYPE_PLAN.md`. Approved and frozen with four user amendments on 3 October 2026.

Execution order: P-00 → P-01 → P-02 → P-03 → P-04 → P-05 → P-06 → P-09 minimal fallback → P-07 → P-08 → P-10 (P1) → P-11 → P-12.

| Task | State | Evidence / next action |
|---|---|---|
| P-00 Connectivity Preflight | COMPLETE | n8n 2.41.6 healthy; native Google Gemini model `models/gemini-3-flash-preview`; real webhook execution 1 returned `AAP_PREFLIGHT_OK 4`; n8n reached local probe. See CONNECTIVITY_PREFLIGHT.md. |
| P-01 Bootstrap | COMPLETE | Django 5.2.17 / SQLite / Waitress. Three bootstrap tests pass; initial migrations applied; repeated seeding idempotent; live health and agent page pass on port 8001. |
| P-02 Filesystem | COMPLETE | Six restricted tools, real fixture reset, run-scoped token binding and intent/result events. 16 total tests pass, including traversal/absolute/drive/UNC/ADS/device/junction rejection, unauthorized delete, root protection and safe reset. |
| P-03 n8n filesystem agent | COMPLETE | Native Gemini workflow imported/published; real run 04fcd45c-0217-458c-9ff9-cbf3ae4c6417 executed 10 tools and five real moves with preserved hashes. 24 Python tests and six native expression checks pass. |
| P-04 Live UI E2E | COMPLETE | UI run 7babba2e-afb6-4d08-8c34-c4502f7595ff: Gemini chose 11 attempts/five real moves, hashes preserved. 28 tests pass, including double-start/reset conflicts, bounded timeout and late-tool rejection. |
| P-05 Trace | COMPLETE | 29 tests pass; ordered lifecycle/instruction/tool/final events, persisted request correlation, escaped inspectable trace. |
| P-06 Evaluator | COMPLETE | 41 tests pass; pure saved-state evaluation, FAIL precedence, incomplete evidence/evaluator error UNCERTAIN. Genuine UI run independently PASS; failed smoke UNCERTAIN. |
| P-09 Minimal fallback | COMPLETE | 42 tests pass. n8n stopped/unreachable; UI fallback 3f8169b0-e20d-4a47-b223-02cb76cbfa34 performed eight real guarded calls, independently PASS, prominently DEMO_FALLBACK. |
| P-07 Remaining scenarios | IN PROGRESS — live quota | All six seeded; 58 tests and six native expression checks pass. Six real dispatches failed/UNCERTAIN; sanitized real diagnostic confirmed MODEL_RATE_LIMIT. Await capacity/model decision before stop condition is accepted. |
| P-08 Report | NOT STARTED | |
| P-10 Comparison (P1) | NOT STARTED | |
| P-11 Polish/setup | NOT STARTED | |
| P-12 Rehearsal | NOT STARTED | |

## Checkpoint log

- P-00 discovery: runtime inventory and npm package metadata verified. Docker engine unavailable; choose native n8n unless the user supplies an existing instance. No model credential has been selected or model invocation verified yet.
- P-00 probe checkpoint: temporary loopback probe started on 127.0.0.1:8001; GET `/health/preflight` returned the expected JSON and an unrelated route returned 404. This verifies the local listener only; n8n → probe remains outstanding. Added a loopback-only native n8n launcher; installation is still running.
- P-00 installation checkpoint: npm installed pinned n8n 2.41.6; executable `--version` returned 2.41.6. npm 12 initially blocked SQLite's install script; direct driver load failed. Approved only sqlite3@5.1.7 in ignored local runtime metadata, rebuilt it, and verified `SQLITE_DRIVER_OK`. No blanket lifecycle-script approval. Startup now reports initialization and has created ignored local state.
- Preflight workflow JSON structurally verified: five native nodes, inactive, no embedded credential. Import and execution are not yet verified.
- P-00 startup/import checkpoint: health, readiness and editor each returned HTTP 200. CLI reported `Successfully imported 1 workflow` for `aapP00Connectivity`. Owner setup is open at `/setup`; operator must enter the new password and Google Gemini credential. Real AI Agent execution is not verified. No P-01 work started.
- Ruling: initialize Git in the explicitly separate prototype directory and use a prototype branch; no linked worktree is needed for this new repository. Use the same local author identity configured in the production checkout, without changing that checkout.
- Ruling: use this committed ledger plus `docs/HANDOFF.md` as the durable execution record requested by the user; do not add duplicate skill scratch ledgers.

- P-00 COMPLETE: user-selected single provider is Google Gemini. Healthy n8n 2.41.6, real credential-authenticated execution 1, exact model `models/gemini-3-flash-preview`, successful probe and webhook directions verified. Secrets excluded; no model/provider abstraction. Next: P-01 after commit/clean-tree verification.
- P-01 COMPLETE: missing app entrypoint test failed before implementation; explicit-mode test failed until a database constraint was added. Final bootstrap suite: 3 passed. `migrate`, repeated `seed_demo`, and `makemigrations --check --dry-run` passed. Actual HTTP health/database and agent page verified. Probe stopped; Waitress now binds 127.0.0.1:8001 (session 61536). Next: P-02.
- P-02 COMPLETE: tests first failed for missing filesystem module after resolving sandbox temporary-directory access. Implemented restricted service/API and owned-path fixture reset. Final suite: 16 passed; Django check clean. Actual demo root reset created eight entries/five synthetic files. Test files use dedicated `.runtime/test-tmp`; filesystem tests require sandbox escalation. Next: P-03 after commit/clean-tree check.
- P-03 COMPLETE: imported/published the native Gemini agent with six restricted HTTP tools and local header auth. First genuine smoke failed before tool effects due to n8n treating adjacent object braces as expression terminator; reproduced/fixed with installed native parser and retained failed run evidence. Successful real run 04fcd45c-0217-458c-9ff9-cbf3ae4c6417: 10 attempts, five successful moves, original hashes preserved, complete tool evidence. No verdict until P-06. Final Python suite 24 passed; six tool expressions pass native parser. Next: P-04 after commit/clean-tree check.



- P-04 COMPLETE: UI click produced live run 7babba2e-afb6-4d08-8c34-c4502f7595ff, 11 attempts and five moves with preserved hashes. Focused tests first failed for absent runner, then caught a shared model-object race; worker now fetches independent objects. Final suite 28 passed, Django check clean. Double start/reset return 409, timeout closes token before snapshot, late effects rejected, restart never redispatches. Ruling: keep the small polling script inline until P-11 rather than add a static asset server now. Next P-05.

- P-05 COMPLETE: focused trace test failed before module existed; final suite 29 passed. Service and runner share event sequencing under workspace lock; ordered saved events render after reload, with request links and timestamps/errors. No invented thoughts. Next P-06.

- P-06 COMPLETE: focused evaluator tests failed before implementation; additional evidence tests caught a partial-fixture confidence issue and fixed it. Final suite 41 passed, migration applied, Django check clean. Saved genuine live runs independently PASS (including UI run); failed model smoke UNCERTAIN. Rules/version/loop threshold/missing evidence persisted. Loop finding alone is heuristic, not FAIL. Next P-09 minimal fallback before remaining scenarios.

- P-06 verification correction: commit 6825b07 was issued after a failed final suite (shared-cache in-memory SQLite table lock); this did not satisfy the checkpoint gate. Switched the test DB to ignored file-backed SQLite to match the live app, then reran the full suite (41 passed) and focused concurrency suite (4 passed). No lower-priority task began before these passed.

- P-09 minimal COMPLETE: explicit fresh scripted mode through the same guarded service entrypoint used by HTTP tools; saved lifecycle/tools/state evaluated by the same rules. Red test rejected fallback before implementation; final suite 42 passed. Genuine outage proof: n8n listener stopped, health unreachable, UI fallback PASS with eight calls. Live failure is neither relabelled nor automatically replaced. Restored n8n afterward. Next P-07.

- P-07 implementation checkpoint (NOT COMPLETE): all six seeded and available; positive/negative tests exercise real guarded fixtures for each oracle. Controlled fault occurs once before effect, retry bound and successful-effect count proven. Final suite 58 passed; native expressions six pass; no migration drift; Django check clean. Live six-scenario dispatches were attempted honestly and retained as failed/UNCERTAIN. Added fixed whitelisted provider failure categories (no raw provider error persisted/exposed); real diagnostic confirms MODEL_RATE_LIMIT on models/gemini-3-flash-preview. No lower task started. Operator chose to keep the exact model and resume after quota resets; hourly thread follow-up checks capacity once without changing provider/model. P-09 already complete before this expansion.

- Operator ruling: keep models/gemini-3-flash-preview; resume P-07 only after quota capacity returns. Hourly thread follow-up requested; no additional provider credential/model setup.

- Interim UI preview checkpoint: user explicitly authorized dashboard design work while quota resets and selected charts/scenario results as the focus. Added isolated `/design-preview` with illustrative data, outcome/comparison charts, evidence coverage, scenario search/filter and inspectable details. No model calls, run writes or filesystem effects. 59 tests pass; Django and JavaScript checks pass; desktop/390px browser checks pass. Fresh review's three accessibility/readability findings resolved. Design awaits user approval; P-07 remains held and P-08/P-10/P-11 remain NOT STARTED. See `docs/UI_DESIGN_PREVIEW.md`.

- 3 October 2026 resume checkpoint: current baseline d91e067 (clean, 59 tests at prior checkpoint), not older 2624a30. User approved/froze implemented dashboard; docs/DESIGN_LOCK.md records existing styling only. Root AGENTS.md/PROJECT.md/ARCHITECTURE.md absent; used docs/ARCHITECTURE.md and existing product/handoff context. n8n 2.41.6 and AAP healthy after documented startup. Exactly one fresh LIVE_MODEL v2 single-action run cb7838bd-fd0d-43e0-961b-e71e87e2fc80 failed with MODEL_RATE_LIMIT after one tool attempt; verdict UNCERTAIN, evidence incomplete. No retry or provider/model change. P-07 remains INCOMPLETE; P-08 not started. AAP session 80660, n8n session 41900.

Resume checkpoint verification: full suite 59 passed (2.81s); documentation diff check clean. No execution/frontend implementation changed.
