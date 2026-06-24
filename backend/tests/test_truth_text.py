"""truth_text: text-normalization and small parsing helpers (pure functions)."""
from truth_text import (
    _age,
    _clean_q,
    _is_junk_bq,
    _node_id_from_url,
    _norm,
    _nurl,
    p1,
    pA,
)


def test_norm_strips_accents_case_and_whitespace():
    assert _norm("  Ärzte\tKammer  ") == "arzte kammer"
    assert _norm("WLO   Spider") == "wlo spider"
    assert _norm(None) == ""


def test_nurl_canonicalizes():
    assert _nurl("http://www.Example.com/Path/") == "https://example.com/path"
    assert _nurl("https://Example.com") == "https://example.com"
    assert _nurl("") == ""


def test_p1_first_value_or_scalar():
    assert p1({"k": ["a", "b"]}, "k") == "a"
    assert p1({"k": "v"}, "k") == "v"
    assert p1({"k": []}, "k") == ""
    assert p1({}, "k") == ""


def test_pA_filters_empty():
    assert pA({"k": ["a", "", None, "b"]}, "k") == ["a", "b"]
    assert pA({}, "k") == []


def test_is_junk_bq():
    for junk in ("", "0", "  ", "123", "null", "n/a", "-"):
        assert _is_junk_bq(junk) is True
    for real in ("KI Campus", "Serlo", "bpb"):
        assert _is_junk_bq(real) is False


def test_node_id_from_url_extracts_uuid():
    uuid = "b23cf2a4-1026-4171-b88e-3b3a915d1673"
    assert _node_id_from_url(f"https://x/components/render/{uuid}?foo=1") == uuid
    assert _node_id_from_url("https://x/no-uuid-here") == ""


def test_clean_q_removes_stars():
    assert _clean_q("★ 4.5  Punkte") == "4.5 Punkte"
    assert _clean_q("") == ""


def test_age_range():
    assert _age({}) == ""
    assert _age({"ccm:educationaltypicalagerange_from": "0",
                 "ccm:educationaltypicalagerange_to": "99"}) == ""
    assert _age({"ccm:educationaltypicalagerange_from": "6",
                 "ccm:educationaltypicalagerange_to": "9"}) == "6–9 Jahre"
