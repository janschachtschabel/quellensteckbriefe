"""truth.make_record: the join/record-construction logic, focused on the
provenance-flag rules and the "effective spider" rule (use the field that is
NOT wirlernenonline_spider). These are the most subtle, most-changed pieces."""
from truth_record import make_record


def node(**over):
    """A parsed node (shape produced by truth._parse_node) with neutral defaults."""
    base = dict(
        nodeId="n-1", title="T", wwwUrl="", description="", publisher="",
        license="", oer=False, subjects=[], educationalContext=[], oehLrt=["Quelle"],
        language="", keywords=[], author="", quality={}, targetGroup=[], ageRange="",
        languageLevel=[], languageTarget="", curriculum=[], fsk="",
        previewUrl="", editorialStatus="", wfStatus="", modified="",
        replicationSource="", generalIdentifier="", crawlerSpider="", multiType=False,
    )
    base.update(over)
    return base


def make(n, kind="crawler", anchor="x_spider"):
    return make_record(kind, anchor, None, n, "", 0, {}, {}, {})


def test_wlo_migration_flag_and_no_false_spider():
    # replicationSource = wirlernenonline_spider is migration provenance, NOT a
    # real crawler binding -> WLO_MIGRATION, but spider stays empty.
    r = make(node(replicationSource="wirlernenonline_spider", crawlerSpider="",
                  generalIdentifier="", oehLrt=["Quelle"]))
    assert "WLO_MIGRATION" in r["flags"]
    assert r["identity"]["spider"] == ""
    assert "TYP_NICHT_QUELLE" not in r["flags"]
    assert "LEGACY_BINDUNG" not in r["flags"]


def test_effective_spider_uses_replicationsource_when_not_wlo():
    # No general_identifier, but replicationSource is a real spider -> that
    # becomes the effective binding.
    r = make(node(crawlerSpider="", generalIdentifier="",
                  replicationSource="serlo_spider", oehLrt=["Webseite"]))
    assert r["identity"]["spider"] == "serlo_spider"
    assert "TYP_NICHT_QUELLE" in r["flags"]  # bound, but LRT != Quelle


def test_mistyped_real_crawler():
    r = make(node(crawlerSpider="bpb_spider", generalIdentifier="bpb_spider",
                  oehLrt=["Webseite"]))
    assert r["identity"]["spider"] == "bpb_spider"
    assert r["id"] == "crawler:bpb_spider"
    assert "TYP_NICHT_QUELLE" in r["flags"]
    assert "LEGACY_BINDUNG" not in r["flags"]


def test_legacy_vocab_binding():
    r = make(node(crawlerSpider="http://w3id.org/openeduhub/vocabs/sources/abc",
                  oehLrt=["Quelle"]))
    assert "LEGACY_BINDUNG" in r["flags"]
    assert "TYP_NICHT_QUELLE" not in r["flags"]  # LRT contains "Quelle"


def test_multitype_is_fehltagging():
    r = make(node(multiType=True, oehLrt=["Quelle", "Video"]))
    assert "FEHLTAGGING" in r["flags"]


def test_oer_flag_from_public():
    r = make(node(oer=True))
    assert "OER" in r["flags"]


def test_pick_bq_reps_prefers_source_record_over_content():
    # When a Bezugsquelle has multiple Quelldatensaetze, the winning node is the
    # one whose title represents the Bezugsquelle (a real source record) — NOT a
    # single content item that happens to be iterated first.
    from truth import _pick_bq_reps
    nodes = [
        {"nodeId": "n-content", "crawlerSpider": "", "publisher": "Wikipedia",
         "title": "Relativsatz in der spanischen Sprache"},   # single content item
        {"nodeId": "n-source", "crawlerSpider": "", "publisher": "Wikipedia",
         "title": "Wikipedia – Die freie Enzyklopaedie"},  # real source record (Quelldatensatz)
    ]
    reps = _pick_bq_reps(nodes, {"wikipedia": "Wikipedia"}, {}, set(), set())
    assert reps == {"wikipedia": "n-source"}


def test_pick_bq_reps_skips_placeholder_bq():
    # A placeholder Bezugsquelle (wirlernenonline) is never represented by a
    # single content item -> no rep, so (ii) it is not listed under the placeholder name.
    from truth import _pick_bq_reps
    nodes = [{"nodeId": "n1", "crawlerSpider": "", "publisher": "WirLernenOnline",
              "title": "WirLernenOnline"}]
    reps = _pick_bq_reps(nodes, {"wirlernenonline": "WirLernenOnline"}, {}, set(), set())
    assert reps == {}


# --- _mark_data_problems: team data-problem flags (drive the team filter) ----
def _rec(**over):
    base = dict(kind="manuell", name="X", contentCount=10, flags=[], public={}, identity={})
    base.update(over)
    return base


def test_mark_data_problems_metadaten_duenn():
    from truth import _mark_data_problems
    full = _rec(identity={"nodeId": "n1"},
                public={"Beschreibung": "x", "Faecher": ["Mathe"], "Bildungsstufen": ["S1"]})
    thin = _rec(identity={"nodeId": "n2"}, public={"Beschreibung": "x"})  # no Faecher/Stufen
    _mark_data_problems([full, thin])
    assert "METADATEN_DUENN" not in full["flags"]
    assert "METADATEN_DUENN" in thin["flags"]


def test_mark_data_problems_bq_einzelinhalt():
    from truth import _mark_data_problems
    one = _rec(kind="bezugsquelle", contentCount=1, identity={"bezugsquelle": "X"})
    many = _rec(kind="bezugsquelle", contentCount=5, identity={"bezugsquelle": "Y"})
    _mark_data_problems([one, many])
    assert "BQ_EINZELINHALT" in one["flags"] and "BQ_EINZELINHALT" not in many["flags"]


def test_mark_data_problems_qd_ohne_bezugsquelle():
    from truth import _mark_data_problems
    with_bq = _rec(identity={"nodeId": "n1", "bezugsquelle": "X"})
    without = _rec(identity={"nodeId": "n2"})
    _mark_data_problems([with_bq, without])
    assert "QD_OHNE_BEZUGSQUELLE" in without["flags"]
    assert "QD_OHNE_BEZUGSQUELLE" not in with_bq["flags"]


def test_mark_data_problems_bindung_unvollstaendig():
    from truth import _mark_data_problems
    no_node = _rec(kind="crawler", identity={})
    with_node = _rec(kind="crawler", identity={"nodeId": "n1"})
    _mark_data_problems([no_node, with_node])
    assert "BINDUNG_UNVOLLSTAENDIG" in no_node["flags"]
    assert "BINDUNG_UNVOLLSTAENDIG" not in with_node["flags"]


def test_mark_data_problems_dublette_verdacht():
    from truth import _mark_data_problems
    a = _rec(name="Portal Globales Lernen", identity={"url": "http://a"})
    b = _rec(name="Portal Globales Lernen", identity={"url": "http://b"})  # same title as a
    c = _rec(name="Unique", identity={"url": "http://a"})                  # same url as a
    solo = _rec(name="Solo", identity={"url": "http://solo"})
    _mark_data_problems([a, b, c, solo])
    assert "DUBLETTE_VERDACHT" in a["flags"]   # shares title (b) and url (c)
    assert "DUBLETTE_VERDACHT" in b["flags"]   # shares title
    assert "DUBLETTE_VERDACHT" in c["flags"]   # shares url
    assert "DUBLETTE_VERDACHT" not in solo["flags"]


def test_mark_data_problems_status_visibility_spider_flags():
    from truth import _mark_data_problems
    filled = {"Beschreibung": "d", "Faecher": ["x"], "Bildungsstufen": ["y"]}
    ohne = _rec(name="one", identity={"nodeId": "n1", "bezugsquelle": "B"},
                internal={"Workflow-Status": "150_PUBLISH_IN_SEARCH"})         # empty status
    ink = _rec(name="two", identity={"nodeId": "n2", "bezugsquelle": "B"}, public=dict(filled),
               internal={"Erschliessungsstatus (genau)": "2. In Suche aufgenommen",
                         "Workflow-Status": "150_PUBLISH_IN_SEARCH"})           # filled, status < 9
    unpub = _rec(name="three", identity={"nodeId": "n3", "bezugsquelle": "B"},
                 internal={"Erschliessungsstatus (genau)": "9. ok",
                           "Workflow-Status": "125_METADATA_QUALITY_FOR_BUFFET"})  # not published
    amb = _rec(name="four", identity={"nodeId": "n4", "bezugsquelle": "B"},
               internal={"Erschliessungsstatus (genau)": "9. ok", "Workflow-Status": "150_PUBLISH_IN_SEARCH",
                         "general_identifier": "serlo_spider",
                         "replicationsource": "wirlernenonline_spider"})        # gi != rs
    bqq = _rec(name="five", kind="bezugsquelle", contentCount=9, identity={"bezugsquelle": "Z"})
    _mark_data_problems([ohne, ink, unpub, amb, bqq])
    assert "OHNE_STATUS" in ohne["flags"]
    assert "STATUS_INKONSISTENT" in ink["flags"] and "OHNE_STATUS" not in ink["flags"]
    assert "NICHT_PUBLIZIERT" in unpub["flags"] and "STATUS_INKONSISTENT" not in unpub["flags"]
    assert "SPIDER_UNEINDEUTIG" in amb["flags"] and "NICHT_PUBLIZIERT" not in amb["flags"]
    assert "BQ_OHNE_QD" in bqq["flags"]
