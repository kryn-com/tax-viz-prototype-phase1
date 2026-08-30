import pytest

from rules.irmaa_projected_2028 import build_projected_2028_overlay_result, resolve_projected_2028_irmaa


def test_projected_path_marks_estimate_true_and_official_false():
    result = build_projected_2028_overlay_result("single", 113001.0)
    assert result.is_estimate is True
    assert result.is_official is False
    assert result.premium_year == 2028
    assert result.income_year == 2026


def test_projected_path_sets_income_year_and_premium_year():
    result = build_projected_2028_overlay_result("single", 113001.0)
    assert result.income_year == 2026
    assert result.premium_year == 2028


def test_projected_threshold_boundaries_match_single_starts():
    row = resolve_projected_2028_irmaa("single", 113001.0)
    assert row.threshold_magi == 113001.0
    assert row.tier_name == "tier_1"

    row = resolve_projected_2028_irmaa("single", 143001.0)
    assert row.threshold_magi == 143001.0
    assert row.tier_name == "tier_2"


def test_unsupported_filing_statuses_are_rejected_in_projected_mode():
    with pytest.raises(ValueError, match="single only"):
        build_projected_2028_overlay_result("married_filing_jointly", 250000.0)
