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
