# Non-live completion audit and plan — 3 October 2026

User-authorized scope: finish non-Gemini work, including P-10 despite the P-07 hold. Preserve existing design and execution architecture. No Gemini requests; the capacity automation was inspected and is already PAUSED. Root AGENTS.md/PROJECT.md/ARCHITECTURE.md are absent; used docs/ARCHITECTURE.md, the frozen plan, task ledger, handoff, design lock and runbook.

| Scope | Audit classification | Action |
|---|---|---|
| P-00–P-06, P-08, P-09, P-11 | COMPLETE | Preserve; run regression and saved/offline integration checks. |
| P-07 implementation and deterministic positive/negative fixtures | COMPLETE | Do not rewrite working behavior. |
| P-07 remaining live scenarios | BLOCKED BY LIVE GEMINI VERIFICATION | Ambiguous cleanup first, then boundary, controlled failure, all PDFs. |
| P-10 saved V1/V2 comparison | IMPLEMENTABLE NOW WITHOUT LIVE MODEL | Read-only projection; same scenario, snapshots, fixture, rules and limits; reject unknown/mismatched inputs. |
| P-10 complete genuine live dataset | BLOCKED BY LIVE GEMINI VERIFICATION | Label implementation separately from empirical demonstration. |
| P-12 non-live rehearsal/recovery | IMPLEMENTABLE NOW WITHOUT LIVE MODEL | Verify startup, offline fallback, reset, restart, saved evidence and navigation. |
| P-12 three full live rehearsals/adversarial segment | BLOCKED BY LIVE GEMINI VERIFICATION | No simulated substitution. |
| Partial rate-limit regression and documentation | IMPLEMENTABLE NOW WITHOUT LIVE MODEL | Test effects retained with UNCERTAIN; present provider error separately; consolidate stale handoff/README claims. |

Implementation plan (executed inline, with tests before behavior changes):

- [x] Add `aap/comparison.py`, `/compare`, and `templates/compare.html` using existing models and visual components. Select latest saved V1/V2 per scenario within one explicit mode; disclose run IDs/times and missing data. No execution or re-evaluation. Count fixed only FAIL→PASS, introduced only PASS→FAIL, unchanged failures only FAIL→FAIL; show all UNCERTAIN transitions separately. Unknown/mismatched contracts are incomparable, not improvement. Test fixtures stay exclusively in the isolated test DB.
- [x] Snapshot the existing run timeout for future comparisons, without changing its value; never backfill historical limits. Test compatibility across recorded scenario/fixture/rules/limits/tools/provider. Add a partial-tool-effects then rate-limit runner regression. Display error code separately from verdict in saved lists/overview; retain report/trace evidence.
- [ ] Verify full suite, UI comparison/links, saved genuine PASS and partial-rate-limit report, explicit fallback with n8n offline, reset and restart without extra live runs. Inspect exact processes before stopping; restart using documented launchers. No credentials printed.
- [ ] Fresh read-only review; update task/handoff states to COMPLETE vs BLOCKED and exact resume point; focused commits and clean tree. P-10 ends IMPLEMENTED — LIVE VERIFICATION/DATA PENDING if genuine compatible coverage is absent.

Fair-comparison limits: newest recorded pair only (no cherry-picking older successes); matching scenario snapshot, initial filesystem snapshot, evaluator version/loop threshold, tool configuration and execution limits. LIVE_MODEL also requires the same recorded provider/model; DEMO_FALLBACK requires the same script version. Legacy missing metadata remains visible and incomparable.

Checkpoint 1: 20 comparison tests observed failing before implementation, then passed; full suite 90 passed (2.50s), Django clean. Partial-rate-limit fixture initially used invalid empty root, correctly causing FAIL; corrected to documented `.` without evaluator changes. Browser observed real saved partial run UNCERTAIN/11 attempts/MODEL_RATE_LIMIT and new read-only comparison with zero compatible legacy pairs. No model dispatch.
