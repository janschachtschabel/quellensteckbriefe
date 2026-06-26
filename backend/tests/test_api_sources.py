"""/api/sources: pagination, sorting and the filter dimensions that the
frontend dropdown maps to. Asserts invariants against the real snapshot."""
from config import WLO_SPIDERS


def test_pagination_shape(client):
    d = client.get("/api/sources?page_size=5").json()
    assert set(d) >= {"total", "page", "pageSize", "pages", "items"}
    assert len(d["items"]) <= 5
    assert d["pages"] >= 1


def test_kind_crawler(client):
    d = client.get("/api/sources?kind=crawler&page_size=50").json()
    assert d["items"]
    assert all(it["kind"] == "crawler" for it in d["items"])


def test_real_crawler_excludes_wlo_spiders(client):
    # The "Crawler-Quellen (kuratiert)" dropdown sends kind=crawler&exclude_wlo.
    d = client.get("/api/sources?kind=crawler&exclude_wlo=true&page_size=100").json()
    assert all(it["identity"]["spider"] not in WLO_SPIDERS for it in d["items"])


def test_sort_desc_by_content(client):
    items = client.get("/api/sources?sort=contentCount&order=desc&page_size=20").json()["items"]
    counts = [it["contentCount"] or 0 for it in items]
    assert counts == sorted(counts, reverse=True)


def test_min_count(client):
    items = client.get("/api/sources?min_count=1000&page_size=20").json()["items"]
    assert all((it["contentCount"] or 0) >= 1000 for it in items)


def test_blacklist_filter_returns_records(client):
    # Blacklisted records are reachable only via the explicit filter.
    assert client.get("/api/sources?flag=BLACKLIST&page_size=1").json()["total"] >= 1


def test_unknown_source_404(client):
    assert client.get("/api/sources/does-not-exist").status_code == 404


def test_new_data_problem_flags_filterable(client):
    # Every new protocol rubric is a real flag, so each is retrievable via flag=<NAME>.
    for fl in ("NICHT_PUBLIZIERT", "BQ_OHNE_QD", "OHNE_STATUS", "STATUS_INKONSISTENT", "SPIDER_UNEINDEUTIG"):
        assert client.get(f"/api/sources?flag={fl}&page_size=1").json()["total"] >= 1, fl
