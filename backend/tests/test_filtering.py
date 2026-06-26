"""_filter_records: every filter dimension, on synthetic records.

This is the most behavior-critical and most-frequently-changed logic. Imported
from `app` today; the import moves to `filtering` during the extraction (the
test assertions are unchanged).
"""
from config import WLO_SPIDERS
from filtering import filter_records


def rec(**over):
    base = dict(
        id="x", name="Test", kind="crawler",
        identity={"nodeId": "", "bezugsquelle": "", "spider": "",
                  "spiderVocabName": "", "url": ""},
        internal={}, contentCount=10, flags=[], fieldGeneration=[], public={},
    )
    for k, v in over.items():
        if k in ("identity", "public", "internal") and isinstance(v, dict):
            base[k] = {**base[k], **v}
        else:
            base[k] = v
    return base


def filt(recs, **kw):
    defaults = dict(
        q=None, kind=None, oer=None, subject=None, level=None, min_count=0,
        has_node=None, only_field_profile=False, license_=None, language=None,
        lrt=None, flag=None, has_bezugsquelle=None, spider_real=False,
        wlo_migration=False, exclude_wlo=False, show_blacklist=False,
    )
    defaults.update(kw)
    return filter_records(recs, **defaults)


def test_blacklist_hidden_by_default():
    recs = [rec(flags=["BLACKLIST"])]
    assert filt(recs) == []
    assert len(filt(recs, show_blacklist=True)) == 1
    assert len(filt(recs, flag="BLACKLIST")) == 1


def test_zweitdatensatz_hidden_by_default():
    # Secondary datasets duplicate an already-listed Bezugsquelle, so they are
    # hidden from the default/end-user view like the blacklist; the team reveals
    # them via flag=ZWEITDATENSATZ (or show_blacklist).
    recs = [rec(flags=["ZWEITDATENSATZ"])]
    assert filt(recs) == []
    assert len(filt(recs, show_blacklist=True)) == 1
    assert len(filt(recs, flag="ZWEITDATENSATZ")) == 1


def test_zweitdatensatz_visible_in_quelldatensatz_view():
    # Secondary datasets are distinct source-dataset OBJECTS: hidden in the default and
    # Bezugsquelle (tag) view, but visible when filtering by Quelldatensatz (has_node=True).
    z = rec(flags=["ZWEITDATENSATZ"], identity={"nodeId": "n1", "bezugsquelle": "X"})
    assert filt([z]) == []                               # default: collapsed (tag view)
    assert len(filt([z], has_node=True)) == 1            # object view: visible
    assert filt([z], has_bezugsquelle=True) == []        # tag view: collapsed


def test_data_problem_flag_stays_visible_by_default():
    # A data-problem flag that is NOT hidden-by-default must remain in the clean
    # view; the team can still isolate it via flag=<NAME>.
    recs = [rec(flags=["METADATEN_DUENN"])]
    assert len(filt(recs)) == 1
    assert len(filt(recs, flag="METADATEN_DUENN")) == 1


def test_team_flag_reveals_even_hidden_records():
    # The hide applies only to the unfiltered default view. A record that is both a
    # secondary dataset AND carries a data problem must surface when the team filters
    # by that data-problem flag — otherwise the problem stays invisible.
    recs = [rec(flags=["ZWEITDATENSATZ", "METADATEN_DUENN"])]
    assert filt(recs) == []                              # hidden by default (zweit)
    assert len(filt(recs, flag="METADATEN_DUENN")) == 1  # revealed by team filter


def test_kind():
    recs = [rec(kind="crawler"), rec(kind="manuell"), rec(kind="bezugsquelle")]
    assert len(filt(recs, kind="crawler")) == 1
    assert len(filt(recs, kind="bezugsquelle")) == 1


def test_has_node_and_bezugsquelle():
    recs = [rec(identity={"nodeId": "n1"}), rec(identity={"bezugsquelle": "Serlo"})]
    assert len(filt(recs, has_node=True)) == 1
    assert len(filt(recs, has_node=False)) == 1
    assert len(filt(recs, has_bezugsquelle=True)) == 1


def test_has_spider():
    with_sp = rec(identity={"spider": "serlo_spider"})
    without_sp = rec(identity={"spider": ""})
    assert filt([with_sp, without_sp], has_spider=True) == [with_sp]
    assert filt([with_sp, without_sp], has_spider=False) == [without_sp]


def test_spider_real_127_rule():
    has_gi = rec(internal={"general_identifier": "bpb_spider"})
    has_rs = rec(internal={"replicationsource": "serlo_spider"})
    only_wlo = rec(internal={"replicationsource": "wirlernenonline_spider"})
    nothing = rec()
    recs = [has_gi, has_rs, only_wlo, nothing]
    out = filt(recs, spider_real=True)
    assert has_gi in out and has_rs in out
    assert only_wlo not in out and nothing not in out


def test_exclude_wlo():
    wlo = rec(identity={"spider": "wirlernenonline_spider"})
    real = rec(identity={"spider": "serlo_spider"})
    out = filt([wlo, real], exclude_wlo=True)
    assert real in out and wlo not in out
    assert all(o["identity"]["spider"] not in WLO_SPIDERS for o in out)


def test_wlo_migration():
    by_rs = rec(internal={"replicationsource": "wirlernenonline_spider"})
    by_spider = rec(identity={"spider": "wirlernenonline_spider"})
    other = rec(identity={"spider": "serlo_spider"},
                internal={"replicationsource": "serlo_spider"})
    out = filt([by_rs, by_spider, other], wlo_migration=True)
    assert by_rs in out and by_spider in out and other not in out


def test_oer():
    oer = rec(flags=["OER"])
    plain = rec()
    assert filt([oer, plain], oer=True) == [oer]
    assert filt([oer, plain], oer=False) == [plain]


def test_min_count():
    recs = [rec(contentCount=3), rec(contentCount=50)]
    assert len(filt(recs, min_count=5)) == 1


def test_only_field_profile():
    recs = [rec(fieldGeneration=[{"field": "x"}]), rec(fieldGeneration=[])]
    assert len(filt(recs, only_field_profile=True)) == 1


def test_license_exact_and_lrt_substring():
    recs = [rec(public={"Lizenz": "CC BY 4.0", "Inhaltstypen": ["Quelle", "Webseite"]})]
    assert len(filt(recs, license_="CC BY 4.0")) == 1
    assert len(filt(recs, license_="CC0")) == 0
    assert len(filt(recs, lrt="quelle")) == 1   # case-insensitive substring
    assert len(filt(recs, lrt="video")) == 0


def test_subject_substring_and_query():
    recs = [rec(name="Serlo", public={"Faecher": ["Mathematik"],
                                       "Beschreibung": "Freie Lernplattform"})]
    assert len(filt(recs, subject="mathe")) == 1
    assert len(filt(recs, q="lernplatt")) == 1
    assert len(filt(recs, q="zzz")) == 0
