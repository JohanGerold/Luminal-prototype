"""Register the local Ollama credential and publish the Ollama filesystem workflow in local n8n.

Run once with n8n stopped:  .venv\\Scripts\\python.exe scripts\\install-ollama-workflow.py
Re-running is safe: the credential and workflow keep fixed IDs and are replaced in place.
The Ollama credential holds only the loopback base URL; no secret is involved. The webhook
reuses the existing header-auth credential, referenced by ID, never read or copied.
"""
import json
import os
import socket
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
N8N = ["node", str(ROOT / ".runtime/n8n/node_modules/n8n/bin/n8n")]
WORKFLOW = ROOT / "n8n/aap-filesystem-agent-ollama.json"
WEBHOOK_AUTH = {"httpHeaderAuth": {"id": "aapLocalWebhookAuth", "name": "AAP Local Webhook Authentication"}}
OLLAMA = {"id": "aapLocalOllama", "name": "Local Ollama", "type": "ollamaApi",
          "data": {"baseUrl": "http://127.0.0.1:11434"}}


def n8n(*args):
    env = {**os.environ, "N8N_USER_FOLDER": str(ROOT / ".runtime/n8n-state")}
    print("n8n", *args, flush=True)
    subprocess.run([*N8N, *args], env=env, check=True)


def main():
    with socket.socket() as probe:
        if probe.connect_ex(("127.0.0.1", 5678)) == 0:
            sys.exit("Stop n8n first (port 5678 is in use); the CLI import must not race the running server.")
    workflow = json.loads(WORKFLOW.read_text(encoding="utf-8"))
    for node in workflow["nodes"]:
        if node["name"] == "AAP Webhook":
            node["credentials"] = WEBHOOK_AUTH
        elif node["type"] == "@n8n/n8n-nodes-langchain.lmChatOllama":
            node["credentials"] = {"ollamaApi": {"id": OLLAMA["id"], "name": OLLAMA["name"]}}
    with tempfile.TemporaryDirectory() as scratch:
        credential_file, workflow_file = Path(scratch, "credential.json"), Path(scratch, "workflow.json")
        credential_file.write_text(json.dumps([OLLAMA]), encoding="utf-8")
        workflow_file.write_text(json.dumps([workflow]), encoding="utf-8")
        n8n("import:credentials", f"--input={credential_file}")
        n8n("import:workflow", f"--input={workflow_file}")
    n8n("publish:workflow", f"--id={workflow['id']}")
    print("Published", workflow["name"], "at /webhook/" + workflow["nodes"][0]["parameters"]["path"])


if __name__ == "__main__":
    main()
