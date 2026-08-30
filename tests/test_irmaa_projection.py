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


@pytest.mark.parametrize(
    "filing_status",
    ["head_of_household", "married_filing_separately"],
)
def test_unsupported_projected_statuses_are_rejected(filing_status):
    with pytest.raises(ValueError, match="single and married_filing_jointly|single only"):
        build_projected_2028_overlay_result(filing_status, 250000.0)


@pytest.mark.parametrize(
    ("magi", "expected_threshold", "expected_tier"),
    [
        (226001.0, 226001.0, "tier_1"),
        (286001.0, 286001.0, "tier_2"),
        (358001.0, 358001.0, "tier_3"),
        (430001.0, 430001.0, "tier_4"),
        (750000.0, 750000.0, "tier_5"),
    ],
)
def test_projected_mfj_threshold_boundaries_match_expected_tiers(magi, expected_threshold, expected_tier):
    row = resolve_projected_2028_irmaa("married_filing_jointly", magi)
    assert row.threshold_magi == expected_threshold
    assert row.tier_name == expected_tier


@pytest.mark.parametrize(
    ("magi", "part_b", "part_d", "tier_name"),
    [
        (226001.0, 89.00, 15.80, "tier_1"),
        (286001.0, 224.00, 40.60, "tier_2"),
        (358001.0, 358.00, 65.50, "tier_3"),
        (430001.0, 492.00, 90.20, "tier_4"),
        (750000.0, 537.00, 98.80, "tier_5"),
    ],
)
def test_projected_mfj_surcharge_values_by_tier(magi, part_b, part_d, tier_name):
    row = resolve_projected_2028_irmaa("married_filing_jointly", magi)
    assert row.tier_name == tier_name
    assert row.part_b_monthly_surcharge == pytest.approx(part_b)
    assert row.part_d_monthly_surcharge == pytest.approx(part_d)


def test_projected_mfj_metadata_matches_existing_estimate_only_values():
    result = build_projected_2028_overlay_result("married_filing_jointly", 226001.0)
    assert result.filing_status == "married_filing_jointly"
    assert result.income_year == 2026
    assert result.premium_year == 2028
    assert result.is_estimate is True
    assert result.is_official is False
    assert result.estimate_basis == "Projected 2028 premium-year overlay for 2026 tax-planning scenarios."
    assert result.source_note == "Estimate only; not an official premium-year IRMAA table."
    assert result.rule_version == "projected_2028_v1"


def test_projected_mfj_total_monthly_and_annual_math_are_consistent():
    result = build_projected_2028_overlay_result("married_filing_jointly", 430001.0)
    assert result.total_monthly_surcharge == pytest.approx(result.part_b_monthly_surcharge + result.part_d_monthly_surcharge)
    assert result.annual_surcharge == pytest.approx(round(result.total_monthly_surcharge * 12, 2))


def test_single_filer_projection_behavior_remains_unchanged():
    row = resolve_projected_2028_irmaa("single", 143001.0)
    assert row.threshold_magi == 143001.0
    assert row.tier_name == "tier_2"

    result = build_projected_2028_overlay_result("single", 113001.0)
    assert result.part_b_monthly_surcharge == pytest.approx(81.20)
    assert result.part_d_monthly_surcharge == pytest.approx(14.50)
    assert result.estimate_basis == "Projected 2028 premium-year overlay for 2026 tax-planning scenarios."
