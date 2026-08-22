import pytest
from models.inputs import DeductionMode, TaxScenarioInput, FilingStatus
from engines.federal_ordinary import compute_federal_ordinary_tax

def create_base_scenario(income: float, deduction: float, status: FilingStatus = FilingStatus.SINGLE) -> TaxScenarioInput:
    return TaxScenarioInput(
        tax_year=2026,
        state_code="TX",
        filing_status=status,
        ordinary_income=income,
        deduction_amount=deduction
    )

def test_zero_taxable_income():
    scenario = create_base_scenario(income=40000, deduction=50000)
    result = compute_federal_ordinary_tax(scenario)
    
    assert result.taxable_ordinary_income == 0.0
    assert result.total_tax == 0.0
    # Confirm the trace still returns bounds but zeroed values
    for slice in result.bracket_trace:
        assert slice.taxed_amount == 0.0
        assert slice.tax_generated == 0.0

def test_positive_taxable_income_one_bracket():
    scenario = create_base_scenario(income=15000, deduction=5000)
    result = compute_federal_ordinary_tax(scenario)
    
    assert result.taxable_ordinary_income == 10000.0
    # Single bracket 10%: 10000 * 0.10 = 1000
    assert result.total_tax == 1000.0
    assert result.bracket_trace[0].taxed_amount == 10000.0
    assert result.bracket_trace[0].tax_generated == 1000.0
    assert result.bracket_trace[1].taxed_amount == 0.0

def test_taxable_income_spanning_multiple_brackets():
    # Taxable = $60,000 (Single).
    # 10%: $0 to $12,400 -> $1,240
    # 12%: $12,400 to $50,400 -> $4,560
    # 22%: $50,400 to $60,000 -> $2,112
    # Total = $7,912.
    scenario = create_base_scenario(income=70000, deduction=10000)
    result = compute_federal_ordinary_tax(scenario)

    assert result.taxable_ordinary_income == 60000.0
    assert result.total_tax == pytest.approx(7912.0)

    assert result.bracket_trace[0].taxed_amount == 12400.0
    assert result.bracket_trace[1].taxed_amount == 38000.0
    assert result.bracket_trace[2].taxed_amount == 9600.0
    assert result.bracket_trace[3].taxed_amount == 0.0

def test_exact_threshold_boundary():
    # Exactly on the 2026 single 10% bracket ceiling.
    scenario = create_base_scenario(income=12400, deduction=0)
    result = compute_federal_ordinary_tax(scenario)

    assert result.taxable_ordinary_income == 12400.0
    assert result.total_tax == 1240.0
    assert result.bracket_trace[0].taxed_amount == 12400.0
    assert result.bracket_trace[1].taxed_amount == 0.0

def test_married_filing_jointly_taxable_income_spanning_multiple_brackets():
    # Taxable = $120,000 (MFJ).
    # 10%: $0 to $24,800 -> $2,480
    # 12%: $24,800 to $100,800 -> $9,120
    # 22%: $100,800 to $120,000 -> $4,224
    # Total = $15,824.
    scenario = create_base_scenario(
        income=120000.0,
        deduction=0.0,
        status=FilingStatus.MARRIED_FILING_JOINTLY,
    )
    result = compute_federal_ordinary_tax(scenario)

    assert result.taxable_ordinary_income == 120000.0
    assert result.total_tax == pytest.approx(15824.0)

    assert result.bracket_trace[0].taxed_amount == 24800.0
    assert result.bracket_trace[1].taxed_amount == 76000.0
    assert result.bracket_trace[2].taxed_amount == 19200.0
    assert result.bracket_trace[3].taxed_amount == 0.0

def test_head_of_household_taxable_income_spanning_multiple_brackets():
    # Taxable = $120,000 (HOH).
    # 10%: $0 to $17,700 -> $1,770
    # 12%: $17,700 to $67,450 -> $5,970
    # 22%: $67,450 to $105,700 -> $8,415
    # 24%: $105,700 to $120,000 -> $3,432
    # Total = $19,587.
    scenario = create_base_scenario(
        income=120000.0,
        deduction=0.0,
        status=FilingStatus.HEAD_OF_HOUSEHOLD,
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
        income=24800.0,
        deduction=0.0,
        status=FilingStatus.MARRIED_FILING_JOINTLY,
    )
    result = compute_federal_ordinary_tax(scenario)

    assert result.taxable_ordinary_income == 24800.0
    assert result.total_tax == 2480.0
    assert result.bracket_trace[0].taxed_amount == 24800.0
    assert result.bracket_trace[1].taxed_amount == 0.0


def test_head_of_household_exact_first_threshold_boundary():
    scenario = create_base_scenario(
        income=17700.0,
        deduction=0.0,
        status=FilingStatus.HEAD_OF_HOUSEHOLD,
    )
    result = compute_federal_ordinary_tax(scenario)

    assert result.taxable_ordinary_income == 17700.0
    assert result.total_tax == 1770.0
    assert result.bracket_trace[0].taxed_amount == 17700.0
    assert result.bracket_trace[1].taxed_amount == 0.0

def test_married_filing_jointly_exact_12_percent_threshold_boundary():
    scenario = create_base_scenario(
        income=100800.0,
        deduction=0.0,
        status=FilingStatus.MARRIED_FILING_JOINTLY,
    )
    result = compute_federal_ordinary_tax(scenario)

    assert result.taxable_ordinary_income == 100800.0
    assert result.total_tax == 11600.0
    assert result.bracket_trace[0].taxed_amount == 24800.0
    assert result.bracket_trace[1].taxed_amount == 76000.0
    assert result.bracket_trace[2].taxed_amount == 0.0


def test_married_filing_jointly_exact_22_percent_threshold_boundary():
    scenario = create_base_scenario(
        income=211400.0,
        deduction=0.0,
        status=FilingStatus.MARRIED_FILING_JOINTLY,
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
        income=67450.0,
        deduction=0.0,
        status=FilingStatus.HEAD_OF_HOUSEHOLD,
    )
    result = compute_federal_ordinary_tax(scenario)

    assert result.taxable_ordinary_income == 67450.0
    assert result.total_tax == 7740.0
    assert result.bracket_trace[0].taxed_amount == 17700.0
    assert result.bracket_trace[1].taxed_amount == 49750.0
    assert result.bracket_trace[2].taxed_amount == 0.0


def test_head_of_household_exact_22_percent_threshold_boundary():
    scenario = create_base_scenario(
        income=105700.0,
        deduction=0.0,
        status=FilingStatus.HEAD_OF_HOUSEHOLD,
    )
    result = compute_federal_ordinary_tax(scenario)

    assert result.taxable_ordinary_income == 105700.0
    assert result.total_tax == 16155.0
    assert result.bracket_trace[0].taxed_amount == 17700.0
    assert result.bracket_trace[1].taxed_amount == 49750.0
    assert result.bracket_trace[2].taxed_amount == 38250.0
    assert result.bracket_trace[3].taxed_amount == 0.0

def test_deterministic_repeated_runs():
    scenario = create_base_scenario(income=200000, deduction=15000, status=FilingStatus.MARRIED_FILING_JOINTLY)
    
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


def test_non_standard_deduction_amount_remains_unchanged():
    scenario = create_base_scenario(
        income=50000.0,
        deduction=7000.0,
    )
    scenario = scenario.model_copy(update={"deduction_mode": DeductionMode.EXPLICIT})

    result = compute_federal_ordinary_tax(scenario)

    assert result.deduction_applied == 7000.0
    assert result.taxable_ordinary_income == 43000.0