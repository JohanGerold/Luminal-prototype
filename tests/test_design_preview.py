def test_design_preview_is_explicitly_illustrative_and_cannot_dispatch(client, monkeypatch):
    from aap import runs
    def forbidden(*args, **kwargs):
        raise AssertionError('A design preview must not start an evaluation')
    monkeypatch.setattr(runs, 'start', forbidden)
    response = client.get('/design-preview')
    assert response.status_code == 200
    assert b'Design preview' in response.content
    assert b'Illustrative data' in response.content
    assert b'/api/runs' not in response.content
