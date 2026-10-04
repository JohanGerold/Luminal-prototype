import pytest
from tests.test_reporting import saved_run


def test_story_explains_quota_without_inventing_failure(saved_run):
    from aap.story import project
    story = project(saved_run)
    assert 'not enough evidence' in story['conclusion'].lower()
    assert 'usage limit' in story['interruption']
    assert story['before'][0]['name'] == 'a.txt'
    assert 'sha256' not in str(story['before'])
    assert story['steps'][-1]['title'] == 'UNCERTAIN'


def test_missing_snapshot_is_not_an_empty_folder(saved_run):
    from aap.story import project
    saved_run.results.update(after={})
    story = project(saved_run)
    assert not story['after_available']
    assert 'not recorded' in story['files_summary']


def test_attempt_and_blocked_effect_are_distinct():
    from aap.story import event_story
    event = {'kind':'tool_requested','tool':'read_file','arguments':{'relative_path':'../outside.txt'}}
    assert event_story(event)['title'].startswith('Asked to read')
    event.update(kind='tool_result',success=False,error={'code':'BOUNDARY_REJECTED'})
    assert 'Blocked' in event_story(event)['title']
    assert 'outside' in event_story(event)['explanation']


def test_panel_story_is_read_only_and_escaped(client, saved_run, monkeypatch):
    from aap import runs, evaluation
    monkeypatch.setattr(runs,'start',lambda *a: pytest.fail('story dispatched'))
    monkeypatch.setattr(evaluation,'evaluate',lambda **kw: pytest.fail('story evaluated'))
    for page in ('report','trace'):
        response=client.get(f'/runs/{saved_run.id}/{page}')
        assert b'What happened' in response.content
        assert b'Run story' in response.content
        assert b'<script>alert(1)</script>' not in response.content
