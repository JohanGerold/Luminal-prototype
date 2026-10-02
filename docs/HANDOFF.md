# Implementation handoff and risks

## Current state

Implementation authorized on 3 October 2026. P-00 connectivity preflight is in progress; no application code or filesystem agent exists yet. The demo directory did not exist at the original inspection. Production remains read only. Current evidence and task states are in [TASKS.md](../TASKS.md).

Start with [PROTOTYPE_PLAN.md](PROTOTYPE_PLAN.md), then architecture, contract and scenarios. P-00 must pass before P-01. After P-06, implement minimal P-09 before P-07. Keep one prototype task order; do not consult or resume the production implementation plan. Inline execution; no subagent execution method has been requested.

### P-00 discovery checkpoint

- Node 24.19.0 and npm 12.0.2 are installed.
- No n8n executable or listener on 5678 was detected; Docker engine is not running.
- Registry metadata identifies n8n 2.41.6, requiring Node >=24.0.0; pinned native installation is underway under ignored `.runtime/n8n`.
- Candidate topology is same-host native: n8n → Django `http://127.0.0.1:8001`; Django → n8n `http://127.0.0.1:5678/webhook/aap-filesystem-agent`. These URLs are not yet connectivity-verified.
- Credential selection and real-model AI Agent verification are outstanding. Do not mark P-00 complete or start P-01 based only on installation/startup.
- Temporary probe is running at `http://127.0.0.1:8001/health/preflight`; direct GET and 404 rejection checks passed. This is not n8n-origin connectivity proof. Stop probe before P-01 Django startup.
- `scripts/start-n8n.ps1` configures native n8n on loopback port 5678 with isolated ignored local state. Startup and real-model checks remain outstanding while installation completes.
- Installation finished: n8n executable reports **2.41.6**. npm 12 blocked install scripts; the missing sqlite3 binary was diagnosed with a failed direct load, then repaired by approving only sqlite3@5.1.7 and rebuilding. Direct load now prints `SQLITE_DRIVER_OK`. Startup is initializing; health/editor verification is still pending.
- `n8n/p00-connectivity-preflight.json` is a five-node native workflow (webhook → HTTP loopback probe → AI Agent with OpenAI model and Calculator). It contains no credential. Its model is the installed node's default `gpt-5-mini`; operator must select a credential and confirm an available model. JSON checks passed; import/model execution remain unverified.

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
