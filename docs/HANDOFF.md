# Implementation handoff and risks

## Current state

**P-00 COMPLETE** on 3 October 2026. Native n8n 2.41.6 is healthy; the operator's native Google Gemini Chat Model credential works. Exact selected model `models/gemini-3-flash-preview`. Real webhook execution **1** returned `AAP_PREFLIGHT_OK 4`; the HTTP probe and Calculator completed successfully. See [CONNECTIVITY_PREFLIGHT.md](CONNECTIVITY_PREFLIGHT.md) and [TASKS.md](../TASKS.md).

The single provider is Google Gemini. Preserve the configured credential in n8n; never print/decrypt/copy its key into Git, JSON, docs, logs or chat. The checked-in preflight workflow is credential-free. No provider abstraction.

Fixed native topology: AAP → `http://127.0.0.1:5678/webhook/aap-filesystem-agent`; n8n → AAP base `http://127.0.0.1:8001`. P-00 proved reachability using the temporary probe, not actual Django/tools. Stop probe before P-01 starts the app. Replace temporary published preflight with the filesystem workflow at P-03.

P-00 committed as `aeeb57a`, with a verified clean tree. **P-01 COMPLETE:** Django 5.2.17, SQLite schema, idempotent V1/V2/normal-scenario seed and basic agent/scenario pages implemented. Three bootstrap tests pass; migrations, drift check and live health/agent HTTP checks pass. Database enforces explicit `LIVE_MODEL|DEMO_FALLBACK` for every saved run. No evaluation runner or filesystem tools yet.

Resume at P-02 after the P-01 checkpoint commit/clean-tree verification. After P-06, implement minimal P-09 before P-07. Update TASKS/HANDOFF and commit each meaningful verified checkpoint. Production remains read only.

Runtime processes: n8n session 76871; Waitress/Django session 61536. Temporary probe 20882 was stopped before Django started. Restart n8n with `scripts/start-n8n.ps1`; start Django using the README command. The preflight's `/health/preflight` endpoint belonged to the stopped probe; P-03 will replace that temporary workflow with actual tool callbacks. Ignore native-hosting/optional Python-runner deprecation for this deadline; native HTTP/model/tool path works without Python runner infrastructure.

## Production inspection and deliberate boundaries

| Read source in `C:\Code\AAP` | Product understanding retained | Excluded |
|---|---|---|
| `README.md`, `AGENTS.md` | Current production status and distinction between design and verified behavior. | Production task gates and production workspace rules do not govern a separate prototype. |
| `docs/PROJECT_BRIEF.md` | Evaluate configured agents; explain evidence and uncertainty; compare versions; avoid certification claims. | Production adapter, tenants, publishing and funding systems. |
| `docs/EVALUATION_DESIGN.md` | Observable attempts, pure rules, failure precedence, incomplete evidence cannot default to PASS, heuristic labels. | Semantic judge/corpora, CI gate, production metrics program. |
| `docs/ARCHITECTURE.md` | Separation of execution, evaluation and reporting responsibilities. | Queue, worker, network topology and deployment controls. |
| `docs/EXECUTION_MODEL.md` (reviewed portions) | Execution status distinct from verdict; record reproducible inputs. | Leases, fencing, dispatch accounting, recovery machinery. |
| `docs/DATA_MODEL.md` (ownership/record definitions and relevant matches) | AgentVersion, EvaluationRun, Scenario and TraceEvent concepts. | Tenant FKs, database roles, RLS, ledger and retention schema. |
| `docs/design/PRODUCT_UI.md` | Investigation from scenario outcome to evidence; plain counts and observable traces. | Production route contracts, static synthetic metrics and full screen inventory. |

Production uses in-memory simulated tools; this prototype deliberately uses guarded real file operations on synthetic local data. Do not claim architectural parity. Some production docs contain historical status/approval text; it has no authority over this new plan. Production implementation plans and application source were not used as implementation inputs.

## Risks and responses

| Risk | Response / proof needed |
|---|---|
| Windows aliases, junctions or reset mistakes affect external files | P-02 containment checks and synthetic sentinel tests; fail closed on unknown workspace contents. This is an application boundary, not hostile-process isolation. |
| Required demo root lies outside current writable roots | During implementation request the narrowly scoped filesystem access needed for `C:\AAP-Demo-Workspace`, or have the operator create it. Do not silently relocate it. No access request is needed for today's docs. |
| Missing credential, runtime mismatch or unreachable n8n | Resolve connectivity and trivial real-model execution at P-00. P-03 verifies actual filesystem-agent import/tools. User handles credential selection. |
| Model does not fail or improve on cue | Rehearse; display actual outcomes. Show saved genuine live failure with recorded label, or explicit fallback. Never alter a live verdict for the presentation. |
| n8n timeout leaves agent running | Close run token before final snapshot; serialize closure with tool execution; reject late requests. No automatic redispatch. |
| Shared demo folder contaminated between scenarios | One active scenario, automatic reset per case, visible manual reset while idle; preserve historical snapshots in DB. |
| Crash between filesystem effect and event completion | Intent/result records, interrupted status and incomplete evidence; conservative verdict; restart never silently resumes. |
| Three days consumed by optional product work | Cut comparison first, then all other P1. Protect live execution, safety, evaluator, trace/report, fallback and rehearsal. |
| “Clean up” clarification cannot be judged by file rules | Report only verified safe non-action; do not claim semantic correctness. Narrow scenario assertion is explicit. |

## Acceptance handoff

- [ ] P-01–P-08 and P-09 pass with recorded evidence, covering every mandatory P0 capability.
- [ ] Normal LIVE_MODEL path changes actual files through n8n; reset and repeat three times.
- [ ] Six scenarios have inspectable assertions; negative evaluator fixtures prove failure detection even if a live sample passes.
- [ ] An observed unsafe attempt is distinguished from its blocked effect.
- [ ] UI shows mode, agent/version, instruction, tool count, time, assertions, findings, trace and before/after state; no hidden reasoning or score.
- [ ] Model/n8n outage and app restart produce honest failure/uncertainty; fresh labelled fallback works.
- [ ] Launch/setup instructions verified; presentation needs no terminal after startup.
- [ ] Optional comparison either demonstrates measured changes or is explicitly listed as omitted.

Future delivery files: tested `n8n/aap-filesystem-agent.json`, expanded startup README, `docs/DEMO_RUNBOOK.md` (ten-minute script), and `docs/VERIFICATION.md` (actual commands/results, versions, live proof and limitations). These are implementation deliverables, not placeholders claiming completion now.
