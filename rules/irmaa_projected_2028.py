from typing import Optional

from models.irmaa import IRMAAOverlayResult, IRMAAThresholdRow, validate_filing_status, validate_magi

# Active planning path for 2026 income decisions that project 2028 IRMAA outcome.
# These values are estimates and are not official premium-year rules.

IRMAA_PROJECTED_2028_RULES = (
    IRMAAThresholdRow(
        filing_status="single",
        threshold_magi=0.0,
        part_b_monthly_surcharge=0.0,
        part_d_monthly_surcharge=0.0,
        tier_name="base",
    ),
    IRMAAThresholdRow(
        filing_status="single",
        threshold_magi=113001.0,
        part_b_monthly_surcharge=81.20,
        part_d_monthly_surcharge=14.50,
        tier_name="tier_1",
    ),
    IRMAAThresholdRow(
        filing_status="single",
        threshold_magi=143001.0,
        part_b_monthly_surcharge=171.20,
        part_d_monthly_surcharge=32.50,
        tier_name="tier_2",
    ),
    IRMAAThresholdRow(
        filing_status="single",
        threshold_magi=179001.0,
        part_b_monthly_surcharge=245.20,
        part_d_monthly_surcharge=54.50,
        tier_name="tier_3",
    ),
    IRMAAThresholdRow(
        filing_status="single",
        threshold_magi=215001.0,
        part_b_monthly_surcharge=319.20,
        part_d_monthly_surcharge=78.50,
        tier_name="tier_4",
    ),
    IRMAAThresholdRow(
        filing_status="single",
        threshold_magi=500000.0,
        part_b_monthly_surcharge=487.00,
        part_d_monthly_surcharge=91.00,
        tier_name="tier_5",
    ),
)


def _rows_for_filing_status(filing_status: str) -> tuple[IRMAAThresholdRow, ...]:
    status = validate_filing_status(filing_status)
    return tuple(row for row in IRMAA_PROJECTED_2028_RULES if row.filing_status == status)


def resolve_projected_2028_irmaa(filing_status: str, magi: Optional[float]) -> IRMAAThresholdRow:
    if filing_status != "single":
        raise ValueError("Projected 2028 IRMAA planning mode is currently scoped to single only.")
    validated_magi = validate_magi(magi)
    rows = _rows_for_filing_status(filing_status)
    applicable = rows[0]
    for row in rows[1:]:
        if row.threshold_magi <= validated_magi:
            applicable = row
        else:
            break
    return applicable


def build_projected_2028_overlay_result(
    filing_status: str,
    magi: Optional[float],
    magi_source: str = "federal_result.magi",
    notes: str = "Projected 2028 IRMAA overlay for 2026 planning; estimate only."
) -> IRMAAOverlayResult:
    status = validate_filing_status(filing_status)
    if status != "single":
        raise ValueError("Projected 2028 IRMAA planning mode is currently scoped to single only.")
    magi_used = validate_magi(magi)
    row = resolve_projected_2028_irmaa(status, magi_used)
    total_monthly = round(row.part_b_monthly_surcharge + row.part_d_monthly_surcharge, 2)
    annual_surcharge = round(total_monthly * 12, 2)
    return IRMAAOverlayResult(
        filing_status=status,
        magi_used=magi_used,
        magi_source=magi_source,
        threshold_applied=row.threshold_magi,
        part_b_monthly_surcharge=row.part_b_monthly_surcharge,
        part_d_monthly_surcharge=row.part_d_monthly_surcharge,
        total_monthly_surcharge=total_monthly,
        annual_surcharge=annual_surcharge,
        income_year=2026,
        premium_year=2028,
        is_estimate=True,
        is_official=False,
        estimate_basis="Projected 2028 premium-year overlay for 2026 tax-planning scenarios.",
        source_note="Estimate only; not an official premium-year IRMAA table.",
        rule_version="projected_2028_v1",
        notes=notes,
    )
