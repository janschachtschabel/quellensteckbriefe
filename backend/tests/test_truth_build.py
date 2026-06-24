"""truth.make_record: the join/record-construction logic, focused on the
provenance-flag rules and the "effective spider" rule (use the field that is
NOT wirlernenonline_spider). These are the most subtle, most-changed pieces."""
from truth import make_record


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
