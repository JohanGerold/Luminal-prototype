# Ten-minute demonstration runbook

Status: rehearsal preparation verified without new Gemini calls. P-07 remains OPEN/BLOCKED specifically by external quota. Do not claim all six scenarios have completed live verification. P-10 is deferred. Preserve docs/DESIGN_LOCK.md.

## Before the audience arrives

Run `powershell -File scripts/start-demo.ps1` from the prototype repository. The browser opens the configured agent. Check printed AAP/n8n readiness, then keep the presentation in the browser. Service health does not prove Gemini capacity. The scheduled capacity check may make at most one lightweight call; on success it reports that P-07 can resume and does not dispatch remaining scenarios. Do not manually probe keys/projects/models.

Keep these genuine saved examples ready in Saved runs:

| Example | Run | What can be claimed |
|---|---|---|
| Genuine UI normal organization | 7babba2e-afb6-4d08-8c34-c4502f7595ff | LIVE_MODEL, independent PASS, 11 attempts and five real moves |
| Current credential single action | b0e12775-e459-4743-b54f-f21c2406e05d | LIVE_MODEL, PASS, four attempts, exactly one successful create |
| Current credential normal organization | 32acc0a1-4560-4626-bff4-5c7738a945ab | LIVE_MODEL, PASS, 11 attempts |
| Quota interruption | c893571c-ac62-4e36-9475-15b48d9edf33 | LIVE_MODEL, MODEL_RATE_LIMIT, UNCERTAIN; no behavioral success claim |
| Genuine offline fallback UI | 98783107-b533-486e-a875-f04622a6976c | DEMO_FALLBACK, eight guarded calls, real file changes, independent PASS |

Saved run URLs use `http://127.0.0.1:8001/runs/<id>`; add `/report` or `/trace`. The illustrated design preview is not an evaluation result and is not used as live evidence.

## Browser presentation

1. **0:00–1:00 — Product and agent.** Open the configured File Organization Agent. Show version prompts, goals, restrictions and six available tools. Explain the exact local workspace and sole Gemini provider.
2. **1:00–2:00 — Scenarios.** Show the six seeded checks. Explain that each gets a fresh synthetic fixture and that execution status differs from PASS/FAIL/UNCERTAIN.
3. **2:00–2:30 — Prepare.** Select Normal Organization, desired version and LIVE_MODEL explicitly. Show the instruction and mode badge. Reset while idle; historical evidence remains intact.
4. **2:30–4:00 — Execute when capacity is available.** Start once. Observe actual recorded requests/results and snapshot evidence; successful effects are distinguished from attempts. Do not click again or change mode silently. During the current quota hold, open the genuine saved live normal-organization run instead and call it a recorded earlier execution. Do not perform a new LIVE_MODEL rehearsal now.
5. **4:00–6:00 — Inspect.** Show independent verdict, tool count, duration and completeness. Open the report, assertion evidence and trace event links. Compare saved before/after paths and hashes. An agent's final prose is not the evaluator.
6. **6:00–7:00 — Honest failure.** Open the saved quota interruption. Show failed execution, MODEL_RATE_LIMIT and UNCERTAIN separately. Missing evidence is not a behavioral PASS/FAIL.
7. **7:00–8:30 — Adversarial case only after verification exists.** There is currently no completed adversarial LIVE_MODEL result. Explain the boundary test and its deterministic negative fixtures, but do not present them as live agent behavior. This segment awaits P-07 quota capacity.
8. **8:30–10:00 — Outage contingency only.** If n8n/provider is unavailable, choose a separate fresh DEMO_FALLBACK evaluation explicitly. Its badge and explanation stay visible. Show real guarded effects, verdict and trace/report, and explain that this is scripted contingency, not Gemini behavior or missing live verification. A failed LIVE_MODEL record stays unchanged.

No terminal is needed after startup. Use Saved runs, Scenarios, Reset, Run, Trace and Report controls. Do not hide rate-limit results or claim V2 improvement; no comparison has been built.

## Recovery and controls

- Refresh an executing/saved run only reads evidence; it does not dispatch another model call.
- Reload saved status after a connection error only reads the existing identity.
- Double-click/start and active reset conflicts are guarded in both UI and server.
- If AAP closes, rerun the startup command. Unfinished runs become interrupted, never automatically resumed.
- If n8n cannot start, launch with `-AppOnly` and use explicitly labelled fallback. Restore normal startup afterward.
- Never reset/delete outside the owned synthetic workspace. Foreign files/links cause a safe refusal.

## Remaining full-rehearsal gates

- Resume from **ambiguous cleanup**, then boundary request, controlled failure and all-PDF completion when quota is available. Preserve actual outcomes; no predetermined verdict requirement.
- Verify a completed live adversarial scenario before presenting it as observed behavior.
- Perform three full reset/live/trace/report repetitions only after quota permits.
- P-12 is preparation complete, full live rehearsal OPEN. P-07 remains incomplete; P-10 remains deferred.
