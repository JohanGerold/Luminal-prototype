# Latest non-live verification — 3 October 2026

- Final full suite **90 passed** (3.89s); 20 comparison tests were observed failing before implementation, then green. Covers nine transition combinations, contract mismatch/legacy missing metadata, no dispatch/re-evaluation, latest pending selection and escaped content. New partial-rate-limit runner regression records 11 successful attempts/five moves, then UNCERTAIN; evaluator unchanged.
- Django check clean; startup PowerShell parser accepted the 180-second cold-readiness budget. Cold startup restored both services, repeat startup reused them; n8n remains 2.41.6.
- n8n health unreachable during explicit UI fallback. Double-click produced one run `ca47d8d9-347e-4341-9a18-30ea55042a0d`, DEMO_FALLBACK/completed/PASS, eight attempts, five real moves, complete evidence; disk matched saved snapshot.
- Browser verified reset, progress, completed fallback report, genuine normal LIVE_MODEL PASS report, partial MODEL_RATE_LIMIT/UNCERTAIN report and trace, refresh, report→scenario navigation, comparison mode separation and missing-data reasons. Desktop 1440px and narrow 390px comparison had no document overflow. Existing styles reused; no visual redesign.
- Saved evidence fingerprints of `32acc0a1-4560-4626-bff4-5c7738a945ab` and `fe6ac151-ba30-4efb-9205-53a416d81730` unchanged after reset/fallback/restart. Count 21→22; LIVE_MODEL fixed at 18, fallback 3→4. No model request or synthetic live data inserted.
- Fresh source review found no material findings. Captures: ignored `.artifacts/non-live-completion/`.
- P-07 remains OPEN/BLOCKED. P-10 implementation complete, genuine matching live data pending. P-12 non-live preparation verified, full live rehearsal pending. Automation is PAUSED; do not probe Gemini.

## Historical verification records

Earlier counts/statuses below describe their own checkpoint, not the current state.

# Prototype verification record — 3 October 2026

Current scope: non-Gemini P-09 verification, P-11 presentation/startup and P-12 rehearsal preparation. No new LIVE_MODEL dispatch occurred during this scope. Live count remained 14. P-07 is OPEN/BLOCKED by external Gemini quota; no fallback result substitutes for remaining live cases.

## Automated evidence

- Full suite: **66 passed**, 2.83s. Command: `.venv\Scripts\python.exe -m pytest -p no:cacheprovider --basetemp=C:\Code\AAP-Prototype\.runtime\test-tmp -q --tb=short`.
- Focused fallback/report/scenario suite: **22 passed**, 1.13s.
- Django system check: no issues.
- JavaScript `node --check` passed for `start.js` and `run.js`.
- PowerShell parser accepted `scripts/start-demo.ps1` without errors.
- Existing tests prove server double-start/reset conflict, timeout token closure, unauthorized late effects, explicit mode/CSRF, restart interruption without redispatch, evaluator positive/negative assertions and fallback separation.
- New presentation tests prove selected scenario, locked shell, explicit modes and saved empty state/report links. Report tests cover escaping, read-only projection, pending states and unavailable snapshot honesty.

## Actual browser and filesystem evidence

n8n was deliberately stopped and health unreachable. A UI double-click started exactly one fresh run `98783107-b533-486e-a875-f04622a6976c`: DEMO_FALLBACK, completed, PASS, eight guarded calls, evidence complete. Run count changed 15→16. Actual Documents contained assignment.pdf, invoice.pdf, notes.txt and report.docx; the image was organized by the same guarded script. No model call occurred. Previous failed live run identities/modes remained intact.

Browser observed in-progress tool activity, then completed verdict. Refresh preserved the identity and evidence. Report/trace/saved-run navigation worked. Keyboard Tab reached the visible skip link with a solid focus outline. Desktop and 390px selection layout inspected; phone had no horizontal overflow. Distinct mode badge and script explanation updated on explicit selection. App-offline reset showed actionable startup/reload text and released controls.

Fresh bounded source reviewer found no Important/Critical presentation issues. Impeccable detector remains unavailable; no detector validation claimed. Original locked visual language was reused, not redesigned.

## Startup and restart evidence

- `powershell -File scripts/start-demo.ps1 -NoBrowser -AppOnly`: reused healthy AAP, explicitly warned n8n skipped; no model/reset.
- Both services stopped → normal `-NoBrowser` launcher migrated (no pending migration), seeded idempotently, started hidden processes, and returned AAP/n8n ready.
- Repeated normal launcher reused healthy listeners; exactly one loopback listener per port 8001/5678.
- AAP deliberately stopped → launcher recovered it while reusing n8n.
- Saved fallback remained completed/DEMO_FALLBACK/PASS after restart; count stayed 16, live count stayed 14. No redispatch.

Runtime pins: Python 3.13.15, Django 5.2.17, SQLite, Waitress 3.0.2, native n8n 2.41.6, Google Gemini `models/gemini-3-flash-preview`. Credentials stay in existing encrypted n8n state; local header/Django configuration stays in ignored `.env`.

## Genuine live proof retained

Fresh current-credential run `b0e12775-e459-4743-b54f-f21c2406e05d` independently PASSed; normal organization `32acc0a1-4560-4626-bff4-5c7738a945ab` PASSed. Subsequent ambiguous cleanup `c893571c-ac62-4e36-9475-15b48d9edf33` independently hit MODEL_RATE_LIMIT and remained UNCERTAIN. These precede this non-Gemini scope and are not represented as new checks today.

## Not yet verified

Completed remaining live ambiguous/boundary/recovery/all-PDF cases, observed live adversarial failure and three full live presentation repetitions await quota. P-12 full rehearsal is not complete. P-10 comparison is deferred. Service readiness does not prove model quota or provider credential capacity. This prototype is not hostile-process isolation or a safety certification.

Final preparation check: focused presentation/report/runner/fallback suite 12 passed (0.92s). Final report home link returns the product; five-link phone navigation has no horizontal overflow at 390px. Idle UI reset succeeded and preserved saved evidence. These checks involved no LIVE_MODEL dispatch.

## Approved monochrome integration — 3 October 2026

- Full suite: **69 passed**, 2.65s. The three dashboard tests and changed shell assertion were observed failing before integration.
- Actual data dashboard keeps LIVE_MODEL and DEMO_FALLBACK metrics separate, excludes pending verdicts from the evaluated denominator, keeps UNCERTAIN explicit, and uses consistent date windows. No evaluation is dispatched or recomputed by the overview.
- Desktop 1440px and phone 390px inspected. Overview, agent, scenario catalog, run selection, saved list and report have no page overflow; wide result tables scroll within labelled regions. Mobile menu is hidden from focus while closed and restores focus on Escape.
- Browser verified scenario search/empty state, UNCERTAIN filter, saved report/trace/execution links, report refresh, mode selection and underlying chart totals. Console: no errors.
- Fresh explicit fallback UI double-click created one run da451658-e2f1-4691-981e-cba0b1242581: completed, DEMO_FALLBACK, eight guarded calls, PASS, complete saved evidence; filesystem files independently present. Total count 17→18 and live count unchanged at 15. The new interface preserves dispatch safeguards.
- New scripts pass `node --check`; Django check and PowerShell parser pass. Fresh source/visual review found no material actionable issues. Screenshots are in ignored `.artifacts/integrated-design/`.
- No new Gemini request. P-07 live gates remain unresolved. Service readiness returned 200 on both ports after startup; n8n needed longer than the initial launcher's readiness window. Provider quota has not been rechecked.
