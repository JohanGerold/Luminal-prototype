# Prototype task ledger

Plan: `docs/PROTOTYPE_PLAN.md`. Approved and frozen with four user amendments on 3 October 2026.

Execution order: P-00 → P-01 → P-02 → P-03 → P-04 → P-05 → P-06 → P-09 minimal fallback → P-07 → P-08 → P-10 (P1) → P-11 → P-12.

| Task | State | Evidence / next action |
|---|---|---|
| P-00 Connectivity Preflight | IN PROGRESS | Node 24.19.0; npm 12.0.2. No existing n8n executable/listener detected. Docker CLI exists; daemon stopped. npm registry reports n8n 2.41.6 requiring Node >=24.0.0. Install pinned native n8n locally, start, select credential, prove a real AI Agent call and both URL directions. |
| P-01 Bootstrap | NOT STARTED | Blocked by P-00 stop condition. |
| P-02 Filesystem | NOT STARTED | Core containment invariant required; obscure hardening must not displace Day-1 E2E. |
| P-03 n8n filesystem agent | NOT STARTED | |
| P-04 Live UI E2E | NOT STARTED | |
| P-05 Trace | NOT STARTED | |
| P-06 Evaluator | NOT STARTED | |
| P-09 Minimal fallback | NOT STARTED | Execute immediately after stable P-05/P-06 contracts. |
| P-07 Remaining scenarios | NOT STARTED | |
| P-08 Report | NOT STARTED | |
| P-10 Comparison (P1) | NOT STARTED | |
| P-11 Polish/setup | NOT STARTED | |
| P-12 Rehearsal | NOT STARTED | |

## Checkpoint log

- P-00 discovery: runtime inventory and npm package metadata verified. Docker engine unavailable; choose native n8n unless the user supplies an existing instance. No model credential has been selected or model invocation verified yet.
- P-00 probe checkpoint: temporary loopback probe started on 127.0.0.1:8001; GET `/health/preflight` returned the expected JSON and an unrelated route returned 404. This verifies the local listener only; n8n → probe remains outstanding. Added a loopback-only native n8n launcher; installation is still running.
- Ruling: initialize Git in the explicitly separate prototype directory and use a prototype branch; no linked worktree is needed for this new repository. Use the same local author identity configured in the production checkout, without changing that checkout.
- Ruling: use this committed ledger plus `docs/HANDOFF.md` as the durable execution record requested by the user; do not add duplicate skill scratch ledgers.
