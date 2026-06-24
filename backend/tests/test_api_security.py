"""Security boundary: the public API must never leak internal fields, and the
thumb proxy must not be an open relay (SSRF). These are HTTP-level invariants."""
import pytest


@pytest.fixture(scope="module")
def internal_record(records):
    # A record that actually has internal data and a URL-safe id (no spaces).
    return next(r for r in records if r.get("internal") and " " not in r["id"])


def test_list_never_leaks_internal(client):
    d = client.get("/api/sources?page_size=50").json()
    assert d["items"], "expected at least one source"
    for it in d["items"]:
        assert "internal" not in it
        assert "hasInternal" in it


def test_detail_public_hides_internal(client, internal_record):
    rid = internal_record["id"]
    r = client.get(f"/api/sources/{rid}")
    assert r.status_code == 200
    body = r.json()
    assert "internal" not in body
    assert body["hasInternal"] is True


def test_detail_wrong_password_stays_public(client, internal_record):
    r = client.get(f"/api/sources/{internal_record['id']}?pw=wrong")
    assert "internal" not in r.json()


def test_detail_correct_password_reveals_internal(client, internal_record, team_pw):
    r = client.get(f"/api/sources/{internal_record['id']}",
                   headers={"X-Team-Password": team_pw})
    assert r.status_code == 200
    assert "internal" in r.json()


def test_auth_endpoint(client, team_pw):
    assert client.post("/api/auth", headers={"X-Team-Password": "nope"}).status_code == 403
    ok = client.post("/api/auth", headers={"X-Team-Password": team_pw})
    assert ok.status_code == 200 and ok.json()["ok"] is True


def test_team_stats_requires_password(client, team_pw):
    assert client.get("/api/stats/team").status_code == 403
    assert client.get("/api/stats/team",
                      headers={"X-Team-Password": team_pw}).status_code == 200


@pytest.mark.parametrize("bad_url", [
    "http://evil.com/x.jpg",
    "http://openeduhub.net.attacker.com/x.jpg",   # suffix-spoof
    "http://notopeneduhub.net/x.jpg",             # missing dot boundary
    "https://169.254.169.254/latest/meta-data",   # cloud metadata
])
def test_thumb_rejects_non_wlo_hosts(client, bad_url):
    # Host check happens before any outbound request, so this needs no network.
    assert client.get("/api/thumb", params={"url": bad_url}).status_code == 400
