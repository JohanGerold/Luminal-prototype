# Approved monochrome integration plan

Goal: apply the user-approved `cfb90fe` monochrome demo to the working AAP product, preserving execution and evidence semantics.

Architecture: keep Django server rendering, SQLite, existing run APIs and execution scripts. Add a read-only overview projection over saved runs. Reuse the approved monochrome CSS with small product-specific layout extensions; do not ship illustrative demo JavaScript in product pages.

Spec: the user approved `/design-assets/monochrome.html` on 3 October 2026 and asked to lock and integrate it. This approval supersedes the previous lavender design lock. No additional design approval is required.

Implementation uses the writing-plans / executing-plans workflow in the existing isolated prototype repository. Production remains read-only. No provider calls, credential changes, new dependencies or evaluator changes are required.

- [x] Test truthful dashboard aggregation: separate execution modes, pending/uncertain results, empty state, date windows, historical versions and saved links. Watch the new tests fail before implementation.
- [x] Implement `aap/dashboard.py`, root overview view/template and small dashboard interaction script. Only saved observations feed metrics, activity and the six-scenario results table. Missing results remain untested.
- [x] Replace shared `base.html` shell with the approved sidebar/header. Reuse `monochrome.css`; add product layouts in `product.css` and mobile navigation in `product.js`. Apply to agents, scenarios, start, run, saved runs, report and trace. Preserve existing run API hooks and protections.
- [x] Verify Python suite, JS syntax, desktop/mobile pages, filtering, report/trace links, keyboard behavior and one explicit fallback execution. No manual Gemini dispatch. Stop/restart only the identified idle prototype server to load templates; preserve historical evidence.
- [x] Fresh review of the integration, fix material findings, replace DESIGN_LOCK.md with the approved conventions, update TASKS/HANDOFF/startup documentation, commit and verify clean tree. Keep the original demo-ready tag unchanged; do not push.

Review focus: incomplete infrastructure evidence never becomes a behavioral pass; fallback never contributes to live metrics; missing/empty history has useful states; escaping and saved links survive the new shell; mobile navigation and wide evidence remain accessible. Existing runner/report tests cover the first and fourth, new overview tests cover aggregation and emptiness, browser checks cover interaction and responsive behavior.

Completed with 69 passing tests and one actual explicit fallback UI proof. Existing startup/evaluator/runner contracts retained. Fresh review: no material actionable findings. Final evidence is recorded in TASKS.md and HANDOFF.md.
