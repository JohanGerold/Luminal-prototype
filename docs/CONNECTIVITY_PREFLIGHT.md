# P-00 connectivity preflight

Status: IN PROGRESS. This record is not proof of real model execution yet.

## Runtime inventory

Observed on 3 October 2026: Node 24.19.0, npm 12.0.2. No pre-existing n8n executable/listener detected. Docker CLI is installed, but its Linux engine pipe is absent. Native npm installation is the selected baseline, unless the operator supplies an existing instance.

Registry metadata: n8n **2.41.6**, Node requirement **>=24.0.0**. Install location: `.runtime/n8n`; package cache and local n8n state also stay under ignored `.runtime`. No global npm installation or Docker startup is needed.

## Exact topology to prove

| Direction | Address | Verification needed |
|---|---|---|
| Browser/operator → n8n | `http://127.0.0.1:5678` | n8n health response and editor loads. |
| Django → n8n | `http://127.0.0.1:5678/webhook/aap-filesystem-agent` | P-00 temporary webhook responds; P-03 installs filesystem workflow at this path. |
| n8n → Django | `http://127.0.0.1:8001` | n8n HTTP Request reaches temporary `/health/preflight` probe; P-01 later starts Django on this verified address. |

`scripts/preflight_probe.py` is a temporary standard-library HTTP listener, not application scaffolding. It serves only `/health/preflight` on loopback. Stop it before Django startup. P-00 verifies network reachability to the planned app address; actual Django callback behavior belongs to P-03/P-04.

## Stop condition

Probe verification: direct GET `http://127.0.0.1:8001/health/preflight` returned `{service: aap-preflight-probe, ok: true}`; GET `/` returned 404. This is direct host verification, not n8n-origin proof. Native startup command after installation: `powershell -File scripts/start-n8n.ps1`.

- [ ] Exact installed n8n version verified from executable.
- [ ] n8n starts and editor/health responds.
- [ ] Model credential selected/configured by operator without copying secrets into repository or chat.
- [ ] Native AI Agent executes a trivial prompt using the real model; preserve execution ID, observed response and selected model ID.
- [ ] Native/Docker topology established, and both URL directions proven.
- [ ] TASKS/HANDOFF updated, focused commit created, working tree checked.

Do not start P-01 while any prerequisite above is unverified. Keep credentials and raw n8n execution storage ignored; evidence contains only nonsecret IDs/version/response and endpoint results.
