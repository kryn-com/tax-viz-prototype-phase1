import pytest
from models.inputs import DeductionMode, TaxScenarioInput, FilingStatus
from engines.federal_ordinary import compute_federal_ordinary_tax


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