"""Statistics and export endpoints: structural invariants and the
transparency-breakdown identities the stats UI relies on."""


def test_stats_full_structure(client):
    s = client.get("/api/stats/full").json()
    for key in ("meta", "byKind", "totals", "herkunft", "inhalte",
                "provenienz", "fieldGeneration", "contentBrackets"):
        assert key in s


def test_stats_full_inhalte_matches_meta(client):
    s = client.get("/api/stats/full").json()
    assert s["inhalte"]["zuordenbar"] == s["meta"]["totalContents"]


def test_quellenverwaltung_matches_filter(client):
    # The "Quellenverwaltung" chart must report the SAME counts the list filter
    # returns (visible records, blacklist hidden) — otherwise stats != filter.
    qv = client.get("/api/stats/full").json()["quellenverwaltung"]

    def total(query):
        return client.get(f"/api/sources?{query}&page_size=1").json()["total"]

    assert qv["gesamt"] == total("")                                  # all sources
    assert qv["mitQuelldatensatz"] == total("has_node=true")
    assert qv["mitBezugsquelle"] == total("has_bezugsquelle=true")
    assert qv["ueberschneidung"] == total("has_node=true&has_bezugsquelle=true")


def test_stats_full_schnittmenge_breakdown_sums(client):
    # The "sauber + Zweit + Blacklist" split must reconstruct the intersection
    # total exactly — this is the public transparency derivation.
    h = client.get("/api/stats/full").json()["herkunft"]
    parts = (h["schnittmengeSauber"] + h["schnittmengeZweitdatensatz"]
             + h["schnittmengeBlacklist"])
    assert parts == h["quelldatensatzMitBezugsquelle"]


def test_meta_filters_lists(client):
    f = client.get("/api/meta/filters").json()
    for key in ("kinds", "subjects", "levels", "licenses", "languages", "lrts"):
        assert isinstance(f[key], list)


def test_export_json_filtered(client):
    rows = client.get("/api/export.json?kind=crawler").json()
    assert isinstance(rows, list) and rows
    assert all(r["kind"] == "crawler" for r in rows)


def test_export_honors_structural_filters(client):
    # The export must return exactly the on-screen list's filtered set. These
    # structural params (has_bezugsquelle, has_spider) used to be ignored.
    cases = [
        ("has_node=false&has_bezugsquelle=true", lambda r: r["bezugsquelle"] and not r["nodeId"]),
        ("has_spider=true", lambda r: bool(r["spider"])),
    ]
    for query, check in cases:
        list_total = client.get(f"/api/sources?{query}&page_size=1").json()["total"]
        rows = client.get(f"/api/export.json?{query}").json()
        assert len(rows) == list_total, query
        assert all(check(r) for r in rows), query


def test_export_csv_has_bom_and_header(client):
    r = client.get("/api/export.csv")
    assert r.status_code == 200
    assert "attachment" in r.headers.get("content-disposition", "")
    text = r.text
    assert text.startswith("﻿")  # UTF-8 BOM for Excel
    assert "id;name;kind" in text


def test_stats_team_breakdown_sums(client, team_pw):
    h = client.get("/api/stats/team",
                   headers={"X-Team-Password": team_pw}).json()["herkunft"]
    parts = (h["schnittmenge_sauber"] + h["schnittmenge_zweitDatensatz"]
             + h["schnittmenge_blacklist"])
    assert parts == h["schnittmenge_QuelldatensatzUndBezugsquelle"]


def test_stats_team_fuellstand(client, team_pw):
    ff = client.get("/api/stats/team",
                    headers={"X-Team-Password": team_pw}).json()["feldFuellstand"]
    assert ff["metadatenBasis"] > 0 and ff["kiBasis"] > 0
    for section in ("metadaten", "ki"):
        assert ff[section]
        for row in ff[section]:
            assert {"feld", "anzahl", "prozent"} <= set(row)
            assert 0 <= row["prozent"] <= 100
            assert row["anzahl"] <= (ff["metadatenBasis"] if section == "metadaten"
                                     else ff["kiBasis"])
