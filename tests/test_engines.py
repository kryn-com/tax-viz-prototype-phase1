import pytest
from models.inputs import DeductionMode, TaxScenarioInput, FilingStatus
from engines.federal_ordinary import (
    compute_federal_ordinary_tax,
    reproduce_provisional_printed_tax_table_ordinary_tax,
)
from rules.federal.year_2026 import get_brackets_for_status


def create_base_scenario(
    income: float,
    deduction: float,
    status: FilingStatus = FilingStatus.SINGLE,
    deduction_mode: DeductionMode = DeductionMode.EXPLICIT,
) -> TaxScenarioInput:
    return TaxScenarioInput(
        tax_year=2026,
        state_code="TX",
        filing_status=status,
        taxpayer_age=45,
        spouse_age=45 if status is FilingStatus.MARRIED_FILING_JOINTLY else None,
        ordinary_income=income,
        deduction_amount=deduction,
        deduction_mode=deduction_mode,
    )


def test_zero_taxable_income():
    scenario = create_base_scenario(income=40000, deduction=50000)
    result = compute_federal_ordinary_tax(scenario)

    assert result.taxable_ordinary_income == 0.0
    assert result.total_tax == 0.0
    for slice in result.bracket_trace:
        assert slice.taxed_amount == 0.0
        assert slice.tax_generated == 0.0


def test_positive_taxable_income_one_bracket():
    scenario = create_base_scenario(income=15000, deduction=5000)
    result = compute_federal_ordinary_tax(scenario)

    assert result.taxable_ordinary_income == 0.0
    assert result.total_tax == 0.0
    assert result.bracket_trace[0].taxed_amount == 0.0
    assert result.bracket_trace[0].tax_generated == 0.0
    assert result.bracket_trace[1].taxed_amount == 0.0


def test_taxable_income_spanning_multiple_brackets():
    scenario = create_base_scenario(income=70000, deduction=10000)
    result = compute_federal_ordinary_tax(scenario)

    assert result.taxable_ordinary_income == 53900.0
    assert result.total_tax == pytest.approx(6570.0)

    assert result.bracket_trace[0].taxed_amount == 12400.0
    assert result.bracket_trace[1].taxed_amount == 38000.0
    assert result.bracket_trace[2].taxed_amount == 3500.0
    assert result.bracket_trace[3].taxed_amount == 0.0


def test_exact_threshold_boundary():
    scenario = create_base_scenario(
        income=28500.0,
        deduction=0.0,
        deduction_mode=DeductionMode.STANDARD,
    )
    result = compute_federal_ordinary_tax(scenario)

    assert result.taxable_ordinary_income == 12400.0
    assert result.total_tax == 1240.0
    assert result.bracket_trace[0].taxed_amount == 12400.0
    assert result.bracket_trace[1].taxed_amount == 0.0


def test_married_filing_jointly_taxable_income_spanning_multiple_brackets():
    scenario = create_base_scenario(
        income=152200.0,
        deduction=0.0,
        status=FilingStatus.MARRIED_FILING_JOINTLY,
        deduction_mode=DeductionMode.STANDARD,
    )
    result = compute_federal_ordinary_tax(scenario)

    assert result.taxable_ordinary_income == 120000.0
    assert result.total_tax == pytest.approx(15824.0)

    assert result.bracket_trace[0].taxed_amount == 24800.0
    assert result.bracket_trace[1].taxed_amount == 76000.0
    assert result.bracket_trace[2].taxed_amount == 19200.0
    assert result.bracket_trace[3].taxed_amount == 0.0


def test_head_of_household_taxable_income_spanning_multiple_brackets():
    scenario = create_base_scenario(
        income=144150.0,
        deduction=0.0,
        status=FilingStatus.HEAD_OF_HOUSEHOLD,
        deduction_mode=DeductionMode.STANDARD,
    )
    result = compute_federal_ordinary_tax(scenario)

    assert result.taxable_ordinary_income == 120000.0
    assert result.total_tax == pytest.approx(19587.0)

    assert result.bracket_trace[0].taxed_amount == 17700.0
    assert result.bracket_trace[1].taxed_amount == 49750.0
    assert result.bracket_trace[2].taxed_amount == 38250.0
    assert result.bracket_trace[3].taxed_amount == 14300.0


def test_married_filing_jointly_exact_first_threshold_boundary():
    scenario = create_base_scenario(
        income=57000.0,
        deduction=0.0,
        status=FilingStatus.MARRIED_FILING_JOINTLY,
        deduction_mode=DeductionMode.STANDARD,
    )
    result = compute_federal_ordinary_tax(scenario)

    assert result.taxable_ordinary_income == 24800.0
    assert result.total_tax == 2480.0
    assert result.bracket_trace[0].taxed_amount == 24800.0
    assert result.bracket_trace[1].taxed_amount == 0.0


def test_head_of_household_exact_first_threshold_boundary():
    scenario = create_base_scenario(
        income=41850.0,
        deduction=0.0,
        status=FilingStatus.HEAD_OF_HOUSEHOLD,
        deduction_mode=DeductionMode.STANDARD,
    )
    result = compute_federal_ordinary_tax(scenario)

    assert result.taxable_ordinary_income == 17700.0
    assert result.total_tax == 1770.0
    assert result.bracket_trace[0].taxed_amount == 17700.0
    assert result.bracket_trace[1].taxed_amount == 0.0


def test_married_filing_jointly_exact_12_percent_threshold_boundary():
    scenario = create_base_scenario(
        income=133000.0,
        deduction=0.0,
        status=FilingStatus.MARRIED_FILING_JOINTLY,
        deduction_mode=DeductionMode.STANDARD,
    )
    result = compute_federal_ordinary_tax(scenario)

    assert result.taxable_ordinary_income == 100800.0
    assert result.total_tax == 11600.0
    assert result.bracket_trace[0].taxed_amount == 24800.0
    assert result.bracket_trace[1].taxed_amount == 76000.0
    assert result.bracket_trace[2].taxed_amount == 0.0


def test_married_filing_jointly_exact_22_percent_threshold_boundary():
    scenario = create_base_scenario(
        income=243600.0,
        deduction=0.0,
        status=FilingStatus.MARRIED_FILING_JOINTLY,
        deduction_mode=DeductionMode.STANDARD,
    )
    result = compute_federal_ordinary_tax(scenario)

    assert result.taxable_ordinary_income == 211400.0
    assert result.total_tax == 35932.0
    assert result.bracket_trace[0].taxed_amount == 24800.0
    assert result.bracket_trace[1].taxed_amount == 76000.0
    assert result.bracket_trace[2].taxed_amount == 110600.0
    assert result.bracket_trace[3].taxed_amount == 0.0


def test_head_of_household_exact_12_percent_threshold_boundary():
    scenario = create_base_scenario(
        income=91600.0,
        deduction=0.0,
        status=FilingStatus.HEAD_OF_HOUSEHOLD,
        deduction_mode=DeductionMode.STANDARD,
    )
    result = compute_federal_ordinary_tax(scenario)

    assert result.taxable_ordinary_income == 67450.0
    assert result.total_tax == 7740.0
    assert result.bracket_trace[0].taxed_amount == 17700.0
    assert result.bracket_trace[1].taxed_amount == 49750.0
    assert result.bracket_trace[2].taxed_amount == 0.0


def test_head_of_household_exact_22_percent_threshold_boundary():
    scenario = create_base_scenario(
        income=129850.0,
        deduction=0.0,
        status=FilingStatus.HEAD_OF_HOUSEHOLD,
        deduction_mode=DeductionMode.STANDARD,
    )
    result = compute_federal_ordinary_tax(scenario)

    assert result.taxable_ordinary_income == 105700.0
    assert result.total_tax == 16155.0
    assert result.bracket_trace[0].taxed_amount == 17700.0
    assert result.bracket_trace[1].taxed_amount == 49750.0
    assert result.bracket_trace[2].taxed_amount == 38250.0
    assert result.bracket_trace[3].taxed_amount == 0.0


def test_deterministic_repeated_runs():
    scenario = create_base_scenario(
        income=200000,
        deduction=15000,
        status=FilingStatus.MARRIED_FILING_JOINTLY,
    )

    run_1 = compute_federal_ordinary_tax(scenario)
    run_2 = compute_federal_ordinary_tax(scenario)

    assert run_1.total_tax == run_2.total_tax
    assert run_1.taxable_ordinary_income == run_2.taxable_ordinary_income
    assert run_1.bracket_trace == run_2.bracket_trace


def test_standard_deduction_single_is_resolved_from_2026_rules():
    scenario = TaxScenarioInput(
        tax_year=2026,
        state_code="TX",
        filing_status=FilingStatus.SINGLE,
        taxpayer_age=45,
        ordinary_income=50000.0,
        deduction_mode=DeductionMode.STANDARD,
    )

    result = compute_federal_ordinary_tax(scenario)

    assert result.deduction_applied == 16100.0
    assert result.taxable_ordinary_income == 33900.0


def test_standard_deduction_married_filing_jointly_is_resolved_from_2026_rules():
    scenario = TaxScenarioInput(
        tax_year=2026,
        state_code="TX",
        filing_status=FilingStatus.MARRIED_FILING_JOINTLY,
        taxpayer_age=45,
        spouse_age=45,
        ordinary_income=50000.0,
        deduction_mode=DeductionMode.STANDARD,
    )

    result = compute_federal_ordinary_tax(scenario)

    assert result.deduction_applied == 32200.0
    assert result.taxable_ordinary_income == 17800.0


def test_explicit_deduction_below_standard_is_floored_to_standard():
    scenario = create_base_scenario(
        income=50000.0,
        deduction=7000.0,
    )
    scenario = scenario.model_copy(update={"deduction_mode": DeductionMode.EXPLICIT})

    result = compute_federal_ordinary_tax(scenario)

    assert result.deduction_applied == 16100.0
    assert result.taxable_ordinary_income == 33900.0


def test_explicit_deduction_above_standard_remains_unchanged():
    scenario = create_base_scenario(
        income=50000.0,
        deduction=20000.0,
    )
    scenario = scenario.model_copy(update={"deduction_mode": DeductionMode.EXPLICIT})

    result = compute_federal_ordinary_tax(scenario)

    assert result.deduction_applied == 20000.0
    assert result.taxable_ordinary_income == 30000.0


def _compute_exact_tax_from_brackets(status: FilingStatus, taxable_income: float) -> float:
    brackets = get_brackets_for_status(status)
    tax = 0.0
    for bracket in brackets:
        lower = bracket["lower"]
        upper = bracket["upper"]
        rate = bracket["rate"]
        if taxable_income <= lower:
            continue
        taxed_amount = taxable_income - lower if upper is None else min(taxable_income, upper) - lower
        tax += taxed_amount * rate
    return tax


def test_provisional_table_midpoint_below_5_uses_0_midpoint():
    result = reproduce_provisional_printed_tax_table_ordinary_tax(
        filing_status=FilingStatus.SINGLE,
        taxable_income=4.99,
    )

    assert result.interval_lower_bound == 0.0
    assert result.interval_upper_bound_exclusive == 5.0
    assert result.midpoint_used == 0.0
    assert result.reproduced_ordinary_tax == 0.0
    assert result.fallback_to_exact is False


def test_provisional_table_midpoint_5_to_less_than_15_uses_10_midpoint():
    result = reproduce_provisional_printed_tax_table_ordinary_tax(
        filing_status=FilingStatus.SINGLE,
        taxable_income=5.0,
    )

    assert result.interval_lower_bound == 5.0
    assert result.interval_upper_bound_exclusive == 15.0
    assert result.midpoint_used == 10.0
    assert result.reproduced_ordinary_tax == 1.0
    assert result.fallback_to_exact is False


def test_provisional_table_midpoint_15_to_less_than_25_uses_20_midpoint():
    result = reproduce_provisional_printed_tax_table_ordinary_tax(
        filing_status=FilingStatus.SINGLE,
        taxable_income=15.0,
    )

    assert result.interval_lower_bound == 15.0
    assert result.interval_upper_bound_exclusive == 25.0
    assert result.midpoint_used == 20.0
    assert result.reproduced_ordinary_tax == 2.0
    assert result.fallback_to_exact is False


def test_provisional_table_midpoint_25_dollar_interval_behavior():
    result = reproduce_provisional_printed_tax_table_ordinary_tax(
        filing_status=FilingStatus.SINGLE,
        taxable_income=26.0,
    )

    assert result.interval_lower_bound == 25.0
    assert result.interval_upper_bound_exclusive == 50.0
    assert result.midpoint_used == 37.5
    assert result.fallback_to_exact is False


def test_provisional_table_midpoint_50_dollar_interval_behavior():
    result = reproduce_provisional_printed_tax_table_ordinary_tax(
        filing_status=FilingStatus.SINGLE,
        taxable_income=3049.99,
    )

    assert result.interval_lower_bound == 3000.0
    assert result.interval_upper_bound_exclusive == 3050.0
    assert result.midpoint_used == 3025.0
    assert result.fallback_to_exact is False


def test_provisional_table_rounds_to_whole_dollar_half_up():
    result = reproduce_provisional_printed_tax_table_ordinary_tax(
        filing_status=FilingStatus.SINGLE,
        taxable_income=3025.0,
    )

    assert result.midpoint_used == 3025.0
    assert result.reproduced_ordinary_tax == 303.0


def test_provisional_table_100000_boundary_uses_exact_fallback():
    result = reproduce_provisional_printed_tax_table_ordinary_tax(
        filing_status=FilingStatus.SINGLE,
        taxable_income=100000.0,
    )

    expected_exact = _compute_exact_tax_from_brackets(FilingStatus.SINGLE, 100000.0)
    assert result.fallback_to_exact is True
    assert result.interval_lower_bound == 100000.0
    assert result.interval_upper_bound_exclusive is None
    assert result.midpoint_used == 100000.0
    assert result.reproduced_ordinary_tax == expected_exact


@pytest.mark.parametrize(
    ("status", "taxable_income"),
    [
        (FilingStatus.SINGLE, 50000.0),
        (FilingStatus.MARRIED_FILING_JOINTLY, 50000.0),
        (FilingStatus.HEAD_OF_HOUSEHOLD, 50000.0),
    ],
)
def test_provisional_table_uses_supported_2026_statutory_schedules(status: FilingStatus, taxable_income: float):
    result = reproduce_provisional_printed_tax_table_ordinary_tax(
        filing_status=status,
        taxable_income=taxable_income,
    )

    expected_exact_midpoint_tax = _compute_exact_tax_from_brackets(status, result.midpoint_used)
    expected_whole_dollar = float(int(expected_exact_midpoint_tax + 0.5))

    assert result.fallback_to_exact is False
    assert result.reproduced_ordinary_tax == expected_whole_dollar