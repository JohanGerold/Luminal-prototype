# Prototype task ledger

Plan: `docs/PROTOTYPE_PLAN.md`. Approved and frozen with four user amendments on 3 October 2026.

Execution order: P-00 → P-01 → P-02 → P-03 → P-04 → P-05 → P-06 → P-09 minimal fallback → P-07 → P-08 → P-10 (P1) → P-11 → P-12.

| Task | State | Evidence / next action |
|---|---|---|
| P-00 Connectivity Preflight | AWAITING CREDENTIAL SETUP | Native n8n 2.41.6 starts; health/readiness/editor HTTP 200. Preflight workflow imported. Operator must finish owner setup and select OpenAI credential; real model response and n8n → probe still unverified. |
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
- P-00 installation checkpoint: npm installed pinned n8n 2.41.6; executable `--version` returned 2.41.6. npm 12 initially blocked SQLite's install script; direct driver load failed. Approved only sqlite3@5.1.7 in ignored local runtime metadata, rebuilt it, and verified `SQLITE_DRIVER_OK`. No blanket lifecycle-script approval. Startup now reports initialization and has created ignored local state.
- Preflight workflow JSON structurally verified: five native nodes, inactive, no embedded credential. Import and execution are not yet verified.
- P-00 startup/import checkpoint: health, readiness and editor each returned HTTP 200. CLI reported `Successfully imported 1 workflow` for `aapP00Connectivity`. Owner setup is open at `/setup`; operator must enter the new password and OpenAI credential. Real AI Agent execution is not verified. No P-01 work started.
- Ruling: initialize Git in the explicitly separate prototype directory and use a prototype branch; no linked worktree is needed for this new repository. Use the same local author identity configured in the production checkout, without changing that checkout.
- Ruling: use this committed ledger plus `docs/HANDOFF.md` as the durable execution record requested by the user; do not add duplicate skill scratch ledgers.
