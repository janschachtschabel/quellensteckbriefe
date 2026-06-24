"""field_policy: the single source of truth for the public/internal split."""
import field_policy as fp


def test_coarse_erschliessung_content_wins():
    # Any positive content count means "available", regardless of node presence.
    assert fp.coarse_erschliessung(5, True) == "im Bestand verfuegbar"
    assert fp.coarse_erschliessung(10, False) == "im Bestand verfuegbar"


def test_coarse_erschliessung_node_without_content():
    assert fp.coarse_erschliessung(0, True) == "Quelle erfasst, (noch) keine Inhalte"


def test_coarse_erschliessung_facets_only():
    assert fp.coarse_erschliessung(0, False) == "nur als Bezugsquelle bekannt"


def test_public_and_internal_flags_disjoint():
    # A flag must never be both public and internal, or the split is ambiguous.
    assert not (fp.PUBLIC_FLAGS & fp.INTERNAL_FLAGS)


def test_sensitive_flags_are_internal_only():
    # Curation lists are internal; their names must not leak to the public view.
    for flag in ("BLACKLIST", "WHITELIST", "FEHLTAGGING"):
        assert flag in fp.INTERNAL_FLAGS
        assert flag not in fp.PUBLIC_FLAGS


def test_provenance_markers_are_public():
    # Provenance markers are intentionally public (transparency requirement).
    for flag in ("WLO_MIGRATION", "LEGACY_BINDUNG", "TYP_NICHT_QUELLE"):
        assert flag in fp.PUBLIC_FLAGS
