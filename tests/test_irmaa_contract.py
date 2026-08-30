import pytest

from rules.irmaa_2026 import build_irmaa_overlay_result, resolve_irmaa_2026


def test_rejects_missing_magi():
    with pytest.raises(ValueError, match="required"):
        resolve_irmaa_2026("single", None)


def test_rejects_negative_magi():
    with pytest.raises(ValueError, match="cannot be negative"):
        resolve_irmaa_2026("single", -1.0)


def test_supports_only_single_and_married_filing_jointly():
    with pytest.raises(ValueError, match="single and married_filing_jointly"):
        resolve_irmaa_2026("head_of_household", 100000.0)


def test_zero_below_first_threshold():
    row = resolve_irmaa_2026("single", 100000.0)
    assert row.tier_name == "base"
    assert row.part_b_monthly_surcharge == 0.0
    assert row.part_d_monthly_surcharge == 0.0

    result = build_irmaa_overlay_result("single", 100000.0)
    assert result.total_monthly_surcharge == 0.0
    assert result.annual_surcharge == 0.0


def test_single_tier_selection_at_threshold():
    row = resolve_irmaa_2026("single", 109000.0)
    assert row.tier_name == "tier_1"
    assert row.threshold_magi == 109000.0


def test_mfj_tier_selection_at_threshold():
    row = resolve_irmaa_2026("married_filing_jointly", 218000.0)
    assert row.tier_name == "tier_1"
    assert row.threshold_magi == 218000.0


def test_total_monthly_equals_part_b_plus_part_d():
    result = build_irmaa_overlay_result("single", 109000.0)
    assert result.total_monthly_surcharge == pytest.approx(
        result.part_b_monthly_surcharge + result.part_d_monthly_surcharge
    )


def test_annual_equals_12_times_monthly_rounded():
    result = build_irmaa_overlay_result("married_filing_jointly", 218000.0)
    assert result.annual_surcharge == pytest.approx(round(result.total_monthly_surcharge * 12, 2))
