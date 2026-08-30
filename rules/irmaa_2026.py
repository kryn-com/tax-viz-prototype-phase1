from typing import Optional

from models.irmaa import IRMAAOverlayResult, IRMAAThresholdRow, validate_filing_status, validate_magi

# Reference-only historical table. This is not the default planning path.
# Premium-year IRMAA uses a two-year income lookback; projected planning estimates should be modeled separately.

IRMAA_2026_RULES = (
    IRMAAThresholdRow(
        filing_status="single",
        threshold_magi=0.0,
        part_b_monthly_surcharge=0.0,
        part_d_monthly_surcharge=0.0,
        tier_name="base",
    ),
    IRMAAThresholdRow(
        filing_status="single",
        threshold_magi=109000.0,
        part_b_monthly_surcharge=81.20,
        part_d_monthly_surcharge=14.50,
        tier_name="tier_1",
    ),
    IRMAAThresholdRow(
        filing_status="single",
        threshold_magi=137000.0,
        part_b_monthly_surcharge=171.20,
        part_d_monthly_surcharge=32.50,
        tier_name="tier_2",
    ),
    IRMAAThresholdRow(
        filing_status="single",
        threshold_magi=171000.0,
        part_b_monthly_surcharge=245.20,
        part_d_monthly_surcharge=54.50,
        tier_name="tier_3",
    ),
    IRMAAThresholdRow(
        filing_status="single",
        threshold_magi=205000.0,
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
    IRMAAThresholdRow(
        filing_status="married_filing_jointly",
        threshold_magi=0.0,
        part_b_monthly_surcharge=0.0,
        part_d_monthly_surcharge=0.0,
        tier_name="base",
    ),
    IRMAAThresholdRow(
        filing_status="married_filing_jointly",
        threshold_magi=218000.0,
        part_b_monthly_surcharge=81.20,
        part_d_monthly_surcharge=14.50,
        tier_name="tier_1",
    ),
    IRMAAThresholdRow(
        filing_status="married_filing_jointly",
        threshold_magi=274000.0,
        part_b_monthly_surcharge=171.20,
        part_d_monthly_surcharge=32.50,
        tier_name="tier_2",
    ),
    IRMAAThresholdRow(
        filing_status="married_filing_jointly",
        threshold_magi=342000.0,
        part_b_monthly_surcharge=245.20,
        part_d_monthly_surcharge=54.50,
        tier_name="tier_3",
    ),
    IRMAAThresholdRow(
        filing_status="married_filing_jointly",
        threshold_magi=410000.0,
        part_b_monthly_surcharge=319.20,
        part_d_monthly_surcharge=78.50,
        tier_name="tier_4",
    ),
    IRMAAThresholdRow(
        filing_status="married_filing_jointly",
        threshold_magi=750000.0,
        part_b_monthly_surcharge=487.00,
        part_d_monthly_surcharge=91.00,
        tier_name="tier_5",
    ),
)


def _rows_for_filing_status(filing_status: str) -> tuple[IRMAAThresholdRow, ...]:
    status = validate_filing_status(filing_status)
    return tuple(row for row in IRMAA_2026_RULES if row.filing_status == status)


def resolve_irmaa_2026(filing_status: str, magi: Optional[float]) -> IRMAAThresholdRow:
    status = validate_filing_status(filing_status)
    validated_magi = validate_magi(magi)
    rows = _rows_for_filing_status(status)
    applicable = rows[0]
    for row in rows[1:]:
        if row.threshold_magi <= validated_magi:
            applicable = row
        else:
            break
    return applicable


def build_irmaa_overlay_result(
    filing_status: str,
    magi: Optional[float],
    magi_source: str = "federal_result.magi",
    notes: str = "Separate Medicare premium surcharge overlay; not federal income tax."
) -> IRMAAOverlayResult:
    status = validate_filing_status(filing_status)
    magi_used = validate_magi(magi)
    row = resolve_irmaa_2026(status, magi_used)
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
        premium_year=2026,
        is_estimate=False,
        is_official=True,
        estimate_basis="",
        source_note="Official premium-year IRMAA reference table; not the default planning path.",
        rule_version="2026_official_reference",
        notes=notes,
    )
