# P-00 connectivity preflight

**COMPLETE — 3 October 2026. Execution mode: LIVE_MODEL.**

Native n8n **2.41.6**, Node **24.19.0**, npm **12.0.2**. n8n uses the single real-model provider **Google Gemini**, through its native Google Gemini Chat Model node v1.2 and the operator-configured credential. Exact selected model: **`models/gemini-3-flash-preview`**. No provider abstraction.

## Verified evidence

| Check | Observed result |
|---|---|
| Executable version | `n8n --version` returned 2.41.6. |
| Health/readiness | GET `/healthz` and `/healthz/readiness` each HTTP 200. |
| Host/AAP client → n8n | POST `{}` to `http://127.0.0.1:5678/webhook/aap-filesystem-agent` returned `{"output":"AAP_PREFLIGHT_OK 4"}`. |
| n8n → local app address | HTTP Request node reached `http://127.0.0.1:8001/health/preflight`; returned `{"service":"aap-preflight-probe","ok":true}`. |
| Credential and real model | Execution **1**, mode `webhook`, status `success`; native Gemini node completed two real calls; Calculator and AI Agent completed successfully. |
| Model selection | UI selected `models/gemini-3-flash-preview`; credential-authenticated model list loaded. Installed node default agrees; checked-in workflow pins the exact model explicitly. |

Execution timestamps from n8n: **2026-10-02T19:15:35.087Z–2026-10-02T19:15:38.408Z** (3 October in Asia/Calcutta). The exact observed marker differs from the user's example but verifies the same real-model requirement; agent used the Calculator to obtain 4. No pinned data or fabricated response.

Workflow ID `aapP00Connectivity`, name **AAP P-00 Connectivity Preflight**, published locally. Runtime workflow already contained the operator's Gemini node/credential; preserved its existing four other nodes and connections. Checked-in JSON replaces only the provider node/configuration and its connection name; it contains no credential reference or secret.

## Fixed topology

- Native n8n editor: `http://127.0.0.1:5678`.
- Django/AAP → n8n: `http://127.0.0.1:5678/webhook/aap-filesystem-agent`.
- n8n → Django/filesystem-service base: `http://127.0.0.1:8001`.
- Future tool endpoints: `http://127.0.0.1:8001/api/tools/<tool>`.

P-00 used a temporary standard-library probe at the future Django address. Actual Django/tool handling does not exist yet and must be verified in P-03/P-04. Stop the probe before P-01 binds Django. Replace the preflight workflow at the same webhook path when P-03 is ready; do not leave two active workflows competing for the path.

## Runtime and secrets

Start n8n with `powershell -File scripts/start-n8n.ps1`. Local packages, cache, state, encrypted credentials and raw execution storage remain in ignored `.runtime`. npm 12 initially blocked sqlite3's install script; only sqlite3@5.1.7 was approved/rebuilt, then direct driver load passed. No other blanket install-script approval.

The Gemini API key remains in n8n credential storage. It was not read, decrypted, printed, exported to Git or placed in workflow JSON/docs/chat. Only nonsecret credential metadata was used to confirm native node binding. Verification output records sanitized response and node statuses. Do not export credential values into future logs/evidence.

P-00 stop condition passed. Commit this checkpoint and verify the working tree before P-01.
