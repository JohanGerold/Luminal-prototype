"""Explicit emergency script; same guarded service entrypoint as the HTTP API."""
import json
from pathlib import Path

SCRIPT_VERSION = 'fallback-v1'


def execute(result, token, workspace):
    actions = json.loads((Path(__file__).parent / 'seeds/fallback_actions.json').read_text(encoding='utf-8'))
    for tool, arguments in actions[result.scenario_id]:
        response = workspace.execute(str(result.run_id), result.scenario_id, token, tool, arguments)
        if not response['success']:
            return {'status': 'failed', 'final_response': 'DEMO_FALLBACK script stopped after a refused or failed tool.'}
    return {'status': 'completed', 'final_response': 'DEMO_FALLBACK scripted actions finished. Independent evaluation uses the recorded tools and real file state.'}
