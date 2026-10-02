"""Export the single-provider native n8n filesystem workflow, without credentials."""
import json
from pathlib import Path

nodes = []


def add(name, node_type, version, parameters, position, **extra):
    nodes.append({"id": name.lower().replace(" ", "-"), "name": name, "type": node_type,
                  "typeVersion": version, "parameters": parameters, "position": position, **extra})


add("AAP Webhook", "n8n-nodes-base.webhook", 2.1,
    {"httpMethod": "POST", "path": "aap-filesystem-agent", "authentication": "headerAuth",
     "responseMode": "responseNode", "options": {}}, [0, 0], webhookId="aap-filesystem-agent-v1")
add("Validate Input", "n8n-nodes-base.code", 2, {"jsCode": """
const b = $input.first().json.body;
const keys = ['contract_version','run_id','scenario_id','agent_version','system_prompt','instruction','scenario_context','tool_token'];
if (!b || Object.keys(b).length !== keys.length || !keys.every(k => k in b)) throw new Error('Invalid envelope');
if (b.contract_version !== '1' || !/^[0-9a-f-]{36}$/i.test(b.run_id) || typeof b.scenario_id !== 'string') throw new Error('Invalid identity');
if (!['v1','v2'].includes(b.agent_version) || typeof b.system_prompt !== 'string' || !b.system_prompt || b.system_prompt.length > 16000 || typeof b.instruction !== 'string' || !b.instruction || b.instruction.length > 8000) throw new Error('Invalid prompt');
const c = b.scenario_context;
if (!c || Object.keys(c).length !== 2 || typeof c.destructive_actions_allowed !== 'boolean' || !Number.isInteger(c.max_tool_calls) || c.max_tool_calls < 1 || c.max_tool_calls > 12 || typeof b.tool_token !== 'string' || b.tool_token.length < 32) throw new Error('Invalid context');
return [{json: {...b, started_at: new Date().toISOString()}}];
"""}, [220, 0])
add("Filesystem Agent", "@n8n/n8n-nodes-langchain.agent", 3.1,
    {"promptType": "define", "text": "={{ $('Validate Input').first().json.instruction + '\\nScenario context: ' + JSON.stringify($('Validate Input').first().json.scenario_context) }}",
     "options": {"systemMessage": "={{ $('Validate Input').first().json.system_prompt }}", "maxIterations": 12}},
    [450, 0], onError="continueRegularOutput")
add("Google Gemini Chat Model", "@n8n/n8n-nodes-langchain.lmChatGoogleGemini", 1.2,
    {"modelName": "models/gemini-3-flash-preview", "options": {"maxOutputTokens": 2048}}, [400, 250])

tools = {
    "list_directory": ("Inspect files and directories at a workspace-relative path. Use . to inspect the root.", ["relative_path"]),
    "read_file": ("Read a bounded file using a workspace-relative path.", ["relative_path"]),
    "create_directory": ("Create one directory; its parent must exist.", ["relative_path"]),
    "create_file": ("Create one new UTF-8 file. Existing files cannot be overwritten.", ["relative_path", "content"]),
    "move_path": ("Move a file or directory; destination parent must exist. No overwrite.", ["source_relative_path", "destination_relative_path"]),
    "delete_path": ("Delete a file or empty directory only when scenario authority explicitly permits the exact path.", ["relative_path"]),
}
for index, (name, (description, fields)) in enumerate(tools.items()):
    arguments = ', '.join(f"{key}: $fromAI('{key}', '{'UTF-8 file contents' if key == 'content' else 'Workspace-relative path'}', 'string')" for key in fields)
    # Separate object-closing braces so n8n does not treat them as the expression terminator.
    body = "={{ {run_id: $('Validate Input').first().json.run_id, scenario_id: $('Validate Input').first().json.scenario_id, arguments: {" + arguments + "} } }}"
    add(name, "n8n-nodes-base.httpRequestTool", 4.3,
        {"method": "POST", "url": f"http://127.0.0.1:8001/api/tools/{name}",
         "descriptionType": "manual", "toolDescription": description, "sendHeaders": True,
         "headerParameters": {"parameters": [{"name": "Authorization", "value": "={{ 'Bearer ' + $('Validate Input').first().json.tool_token }}"}]},
         "sendBody": True, "specifyBody": "json", "jsonBody": body,
         "options": {"timeout": 10000, "response": {"response": {"neverError": True, "responseFormat": "json"}}}},
        [550 + index * 160, 250], retryOnFail=False)

add("Normalize Output", "n8n-nodes-base.code", 2, {"jsCode": """
const b = $('Validate Input').first().json;
const output = $input.first().json;
const failed = Boolean(output.error);
return [{json: {contract_version:'1', run_id:b.run_id, scenario_id:b.scenario_id, execution_mode:'LIVE_MODEL',
status:failed ? 'failed' : 'completed', final_response:failed ? null : String(output.output || '').slice(0,16000), tool_call_count:null,
started_at:b.started_at, completed_at:new Date().toISOString(),
error:failed ? {code:'MODEL_EXECUTION_FAILED', message:'Agent execution failed.'} : null}}];
"""}, [800, 0])
add("Respond", "n8n-nodes-base.respondToWebhook", 1.4,
    {"respondWith": "json", "responseBody": "={{ $json }}", "options": {}}, [1050, 0])

connections = {}
for source, target in [("AAP Webhook", "Validate Input"), ("Validate Input", "Filesystem Agent"),
                       ("Filesystem Agent", "Normalize Output"), ("Normalize Output", "Respond")]:
    connections[source] = {"main": [[{"node": target, "type": "main", "index": 0}]]}
connections["Google Gemini Chat Model"] = {"ai_languageModel": [[{"node": "Filesystem Agent", "type": "ai_languageModel", "index": 0}]]}
for tool in tools:
    connections[tool] = {"ai_tool": [[{"node": "Filesystem Agent", "type": "ai_tool", "index": 0}]]}

workflow = {"id": "aapFilesystemAgent", "name": "AAP Filesystem Agent", "active": False, "nodes": nodes,
    "connections": connections, "settings": {"executionOrder": "v1", "executionTimeout": 90,
        "saveDataSuccessExecution": "none", "saveDataErrorExecution": "none", "saveManualExecutions": False,
        "saveExecutionProgress": False}, "pinData": {}, "tags": []}
Path("n8n/aap-filesystem-agent.json").write_text(json.dumps(workflow, indent=2) + "\n", encoding="utf-8")
