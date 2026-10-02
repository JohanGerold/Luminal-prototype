# n8n setup handoff

Planning artifact only. `aap-filesystem-agent.json` will be created in P-03, after the filesystem API exists; there is no importable workflow yet.

Use local n8n on the same Windows host so its fixed HTTP tools can reach AAP at `127.0.0.1:8001`. Prefer a pinned local npm installation; record supported Node/n8n versions before installation. Container networking is an optional setup change, not the baseline.

Implementation/setup order:

1. Record exact n8n version and export node `typeVersion` values from that installation.
2. Build the workflow described in [CONTRACT.md](CONTRACT.md), export JSON without credentials, import into a clean workflow and verify all six connections.
3. User selects/configures the one Google Gemini model credential in n8n. Record the actual model ID after a successful tool-calling smoke test; do not silently substitute models.
4. Configure fixed tool base URL and header-auth webhook credential. Keep model credentials and run tokens out of prompts/browser/logs.
5. Publish/activate as required by the installed n8n version. Set AAP's server-side webhook URL to the production webhook path, not the temporary test listener.
6. Verify manual webhook → real model-selected tool → real fixture mutation → matching AAP event. Then verify UI E2E, timeout and stale-token refusal.
7. Update this file with tested start/import/configuration steps and troubleshooting for connection refusal, wrong webhook path, missing credential and model/tool errors.

Proposed configuration names: `AAP_N8N_WEBHOOK_URL`, `AAP_N8N_AUTH_TOKEN`, `AAP_DEMO_ROOT` (server-owned fixed demo directory). n8n model credentials stay in n8n. AAP's startup script also needs a normal local Django secret and ignored local data directory. A run token is generated at dispatch, not a persistent frontend setting.

Official documentation checked while planning:

- [Tools Agent](https://docs.n8n.io/integrations/builtin/cluster-nodes/root-nodes/n8n-nodes-langchain.agent/tools-agent/) supports attached chat models/tools and an iteration limit. The plan uses this native agent architecture.
- [HTTP Request](https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-base.httprequest/) can serve as an AI Agent tool. URLs and transport fields remain fixed in this design.
- [Webhook](https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-base.webhook/) documents separate test/production URLs and response configuration.
- [npm installation](https://docs.n8n.io/hosting/installation/npm/) is the setup reference; verify runtime compatibility when pinning.

Documentation support does not prove that a generated workflow imports or runs. P-03 must capture that evidence.
