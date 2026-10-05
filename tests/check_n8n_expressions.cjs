const assert = require('node:assert/strict');
const fs = require('node:fs');
const {Expression} = require('../.runtime/n8n/node_modules/n8n-workflow');
const expression = new Expression('UTC');
const scope = {
  $: () => ({first: () => ({json: {run_id:'test-run', scenario_id:'test-case', tool_token:'synthetic-test-token'}})}),
  $fromAI: name => 'synthetic-' + name,
};
for (const file of ['n8n/aap-filesystem-agent.json', 'n8n/aap-filesystem-agent-ollama.json']) {
  const workflow = JSON.parse(fs.readFileSync(file, 'utf8'));
  const tools = workflow.nodes.filter(n => n.type.endsWith('httpRequestTool'));
  assert.equal(tools.length, 6);
  for (const node of tools) {
    const body = expression.resolveSimpleParameterValue(node.parameters.jsonBody, scope);
    assert.equal(body.run_id, 'test-run');
    assert.equal(body.scenario_id, 'test-case');
    assert.ok(Object.keys(body.arguments).length >= 1);
  }
  console.log(`${file}: all six tool bodies pass the installed n8n expression parser.`);
}
