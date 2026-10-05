# Local presentation startup

**Live provider (5 October 2026):** `.env` `AAP_LIVE_PROVIDER=ollama` (default) uses local `qwen3:8b`; `gemini` restores the Gemini workflow. With Ollama selected the launcher also starts Ollama if needed, preloads the model into GPU memory (no evaluation, no file changes) and confirms the live n8n webhook is registered (HTTP 403 to an unauthenticated probe). If it warns that the webhook is not registered, run `start.bat` again. One-time install of the Ollama workflow: `ollama pull qwen3:8b`, then with n8n stopped `.venv\Scripts\python.exe scripts\install-ollama-workflow.py`.

From `C:\Code\AAP-Prototype`, double-click `start.bat` to start the demo and open the product in your default browser. From PowerShell, the equivalent command is:

```powershell
powershell -File scripts/start-demo.ps1
```

The batch file passes `-Restart`, so it closes only listeners on the prototype's fixed AAP (`8001`) and n8n (`5678`) ports before starting fresh hidden services. The PowerShell launcher without `-Restart` checks the existing environment, migrates/seeds the catalog only when starting AAP, starts missing services in hidden background processes, waits up to 180 seconds for readiness and opens the evaluation overview. It never invokes Gemini, changes credentials or resets the workspace. No secrets or provider output are logged by the launcher. Windows, Python 3.13 environment, installed pinned native n8n 2.41.6, Node on PATH and the existing local `.env`/n8n credential state are prerequisites. First-time dependency setup remains `uv sync --locked` and the existing `n8n/README.md` instructions; this launcher does not install or upgrade packages.

Options: `-NoBrowser` checks/starts without opening a browser; `-AppOnly` intentionally skips n8n for an outage demonstration; `-Restart` closes the fixed prototype listeners before starting. These can be combined. Readiness checks services only, not model quota or credential validity. A cold native n8n startup can exceed 90 seconds; allow the launcher to finish before starting a second copy.

## URLs and readiness

- Product overview: `http://127.0.0.1:8001/`
- Configured agent: `http://127.0.0.1:8001/agents/file-organization`
- Scenarios: `http://127.0.0.1:8001/scenarios`
- Prepare run/reset: `http://127.0.0.1:8001/runs/new`
- Saved V1/V2 comparison: `http://127.0.0.1:8001/compare`
- Saved evaluations: `http://127.0.0.1:8001/runs`
- AAP readiness: `http://127.0.0.1:8001/health` (AAP/database ready)
- n8n editor: `http://127.0.0.1:5678/`
- n8n readiness: `http://127.0.0.1:5678/healthz`

These are loopback URLs for the native local topology. The existing n8n→AAP tool URL is `http://127.0.0.1:8001`; AAP→n8n webhook is `http://127.0.0.1:5678/webhook/aap-filesystem-agent`. Never put keys into URLs, scripts or documentation.

## Presentation controls

Inspect agent → Scenarios → Select scenario → explicitly choose version/mode. Reset demo workspace operates on owned synthetic files inside `C:\AAP-Demo-Workspace` only. Start also resets that fixture. Reset and another start are refused during an active run; controls prevent duplicate clicks. Historical snapshots/events survive reset.

LIVE_MODEL means real Gemini through the currently configured n8n credential. Availability depends on external quota. DEMO_FALLBACK creates a separate scripted run through the same guarded service/evaluator; it does not measure model behavior or complete missing P-07 live verification. Failed live runs keep their identity and verdict.

## Recovery

If AAP/n8n is closed, rerun the launcher. If n8n will not start, use `powershell -File scripts/start-demo.ps1 -AppOnly`, inspect saved evidence and deliberately select DEMO_FALLBACK. Re-run the normal launcher when n8n can start. Existing credentials remain in encrypted n8n local state; update them manually in its Credentials UI when needed.

If a port is occupied by an unready service, the script stops with a clear error rather than kill an unknown process. If AAP crashes mid-run, restart marks the unfinished run interrupted with conservative evaluation; it never redispatches it. Reload saved status only fetches evidence. A fresh run is a separate explicit action.

For manual diagnosis only: Django uses `.venv\Scripts\python.exe manage.py serve_demo`; n8n uses `powershell -File scripts/start-n8n.ps1`. Do not run duplicate AAP processes. Normal presentation needs only the launcher and browser controls.
