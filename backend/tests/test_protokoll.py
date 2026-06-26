"""protokoll.build_protokoll: Markdown structure, counts, recommendations, computed rubrics."""
import protokoll


def _rec(flags, name="X", node="n1", bq="", url="", content=0, internal=None, pub=None, kind="manuell"):
    public = {"URL": url}
    public.update(pub or {})
    return {"id": node or name, "name": name, "kind": kind, "contentCount": content,
            "flags": list(flags), "identity": {"nodeId": node, "bezugsquelle": bq, "url": url},
            "public": public, "internal": internal or {}}


def test_protokoll_has_all_rubrics_counts_and_recommendation():
    recs = [
        _rec(["WLO_MIGRATION"], name="bpb", node="b23",
             bq="Bundeszentrale für politische Bildung", content=63034,
             internal={"Erschliessungsstatus (genau)": "geprüft"}),
        _rec(["WLO_MIGRATION"], node="n2", internal={"Erschliessungsstatus (genau)": "geprüft"}),
        _rec(["FEHLTAGGING"], node="n3", internal={"Erschliessungsstatus (genau)": "geprüft"}),
        _rec([], node="n4", internal={"Erschliessungsstatus (genau)": "geprüft"}),  # no problem
    ]
    md = protokoll.build_protokoll(recs, {"generatedAt": "2026-06-26 00:00"})
    assert md.startswith("# Fehler-Protokoll")
    for entry in protokoll.CATALOG:                       # every rubric title is present
        assert entry[1] in md
    assert "| `WLO_MIGRATION` | 2 |" in md                # overview count
    assert "bpb" in md and "b23" in md                    # the case is listed
    assert "Bundeszentrale für politische Bildung" in md  # with the correct Bezugsquelle
    assert "Bezugsquelle (ccm:oeh_publisher_combined) am Quelldatensatz" in md  # the fix
    assert "mit mindestens einem Datenproblem: 3" in md   # 3 of 4 records


def test_protokoll_dubletten_concrete_keep_and_delete():
    recs = [
        _rec(["DUBLETTE_VERDACHT"], name="A", node="n1", url="http://x", content=10),
        _rec(["DUBLETTE_VERDACHT", "BLACKLIST"], name="B", node="n2", url="http://x"),
    ]
    md = protokoll.build_protokoll(recs, {})
    assert "Gruppe" in md and "2 Kandidaten" in md
    keep = next(l for l in md.splitlines() if "behalten:" in l)
    drop = next(l for l in md.splitlines() if "entfernen/prüfen" in l)
    assert "A" in keep and "n1" in keep                  # non-blacklist, more content → keep
    assert "B" in drop and "n2" in drop and "Blacklist" in drop  # the concrete duplicate to remove


def test_protokoll_dubletten_clusters_url_and_title_transitively():
    # A~B share a URL, A~C share a title (different URL) → one cluster of 3, nothing dropped.
    recs = [
        _rec(["DUBLETTE_VERDACHT"], name="Portal", node="n1", url="http://a", content=5),
        _rec(["DUBLETTE_VERDACHT"], name="Other", node="n2", url="http://a"),   # same URL as A
        _rec(["DUBLETTE_VERDACHT"], name="Portal", node="n3", url="http://c"),  # same title as A
    ]
    md = protokoll.build_protokoll(recs, {})
    assert "3 Kandidaten" in md                          # transitively merged into one cluster
    for node in ("n1", "n2", "n3"):
        assert node in md                                # none silently dropped


def test_protokoll_concrete_detail_columns():
    recs = [
        _rec(["METADATEN_DUENN"], name="thin", node="n1"),                         # only URL → 3 core fields missing
        _rec(["FEHLTAGGING"], name="mix", node="n2", pub={"Inhaltstypen": ["Quelle", "Webseite"]}),
        _rec(["ZWEITDATENSATZ"], name="zweit", node="n3", bq="ACME"),
        _rec([], name="primär", node="n4", bq="ACME", content=99),                 # the merge target for ACME
    ]
    md = protokoll.build_protokoll(recs, {})
    assert "fehlende Kernfelder" in md
    assert "Beschreibung, Fächer, Bildungsstufen" in md                            # which fields exactly are empty
    assert "Inhaltstypen (außer Quelle entfernen)" in md
    assert "Quelle, Webseite" in md                                                # the types to clean up
    merge = next(l for l in md.splitlines() if "zweit" in l and "n3" in l)
    assert "primär" in merge                                                       # the concrete primary to merge into


def test_protokoll_bezugsquelle_ohne_quelldatensatz():
    recs = [
        _rec(["BQ_OHNE_QD"], name="BigPublisher", node="", kind="bezugsquelle", content=50),
        _rec([], name="Tiny", node="", kind="bezugsquelle", content=1),            # not flagged
    ]
    md = protokoll.build_protokoll(recs, {})
    lines = md.splitlines()
    start = next(i for i, l in enumerate(lines)
                 if l.startswith("## ") and "Bezugsquelle mit Inhalten" in l)
    end = next(i for i in range(start + 1, len(lines)) if lines[i].startswith("## "))
    sec = "\n".join(lines[start:end])
    assert "BigPublisher" in sec           # publisher with real content but no Quelldatensatz
    assert "Tiny" not in sec               # single-content long tail excluded (it is BQ_EINZELINHALT)


def test_protokoll_new_status_visibility_spider_rubrics():
    recs = [
        _rec(["STATUS_INKONSISTENT"], name="Half", node="n1"),
        _rec(["NICHT_PUBLIZIERT"], name="Hidden", node="n2"),
        _rec(["SPIDER_UNEINDEUTIG"], name="Ambig", node="n3",
             internal={"general_identifier": "serlo_spider"}),
    ]
    md = protokoll.build_protokoll(recs, {})
    assert "Status-Inkonsistenz" in md and "Half" in md
    assert "nicht in der Suche veröffentlicht" in md and "Hidden" in md
    assert "Spider-Bindung uneindeutig" in md and "Ambig" in md
    assert "serlo_spider" in md             # SPIDER_UNEINDEUTIG detail = real binding (general_identifier)


def test_every_rubric_is_a_registered_filterable_flag():
    # Each protocol rubric must be a real, registered flag, so the team filter (flag=<NAME>)
    # and the protocol always cover the exact same categories.
    import field_policy as fp
    known = fp.PUBLIC_FLAGS | fp.INTERNAL_FLAGS
    for entry in protokoll.CATALOG:
        assert entry[0] in known, f"rubric {entry[0]} is not a registered flag"


def test_protokoll_computed_status_fuellstand_and_notes():
    recs = [
        _rec(["OHNE_STATUS"], node="n1"),     # carries the flag (set in the build)
        _rec([], node="n2"),                  # not flagged
    ]
    md = protokoll.build_protokoll(recs, {})
    assert "Quelldatensatz ohne Erschließungsstatus (1)" in md   # only the flagged record
    assert "Metadaten-Füllstand" in md                          # aggregate section present
    assert "Nicht automatisch pro Quelle prüfbar" in md         # governance/process note
