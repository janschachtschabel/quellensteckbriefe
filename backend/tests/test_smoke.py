"""Smoke test: the app imports, startup loads truth.json, and basic shape holds.

If this fails, the test infrastructure (pythonpath / fixtures / data) is wrong;
fix that before trusting any other test.
"""


def test_data_loaded(records, meta):
    assert isinstance(records, list) and len(records) > 0
    assert meta["total"] == len(records)


def test_stats_endpoint_ok(client):
    r = client.get("/api/stats")
    assert r.status_code == 200
    assert "meta" in r.json()
