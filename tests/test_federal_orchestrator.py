import pytest
from models.inputs import TaxScenarioInput, FilingStatus, DeductionMode
from engines.federal_orchestrator import orchestrate_federal_tax


def test_orchestrator_zero_income():
    """Verifies pipeline execution with $0 income inputs."""
    scenario = TaxScenarioInput(
        tax_year=2026,
        state_code="NC",
        filing_status=FilingStatus.SINGLE,
        ordinary_income=0.0,
        ltcg_qd_income=0.0,
        social_security_income=0.0,
        nontaxable_income=0.0,
        deduction_mode=DeductionMode.STANDARD,
    )
    result = orchestrate_federal_tax(scenario)

    assert result.agi == 0.0
    assert result.magi == 0.0
    assert result.taxable_ordinary_income == 0.0
    assert result.ordinary_tax == 0.0
    assert result.ltcg_qd_tax == 0.0
    assert result.niit_tax == 0.0
    assert result.total_federal_tax == 0.0


def test_orchestrator_mfs_rejection():
    """Verifies that MFS filing status is explicitly rejected."""
    scenario = TaxScenarioInput(
        tax_year=2026,
        state_code="NC",
        filing_status=FilingStatus.MARRIED_FILING_SEPARATELY,
        ordinary_income=50000.0,
    )
    with pytest.raises(ValueError, match="Married Filing Separately \\(MFS\\) is unsupported."):
        orchestrate_federal_tax(scenario)


def test_orchestrator_does_not_mutate_input():
    """Verifies taxable Social Security is added only to an effective scenario."""
    scenario = TaxScenarioInput(
        tax_year=2026,
        state_code="NC",
        filing_status=FilingStatus.SINGLE,
        ordinary_income=40000.0,
        ltcg_qd_income=10000.0,
        social_security_income=30000.0,
        deduction_mode=DeductionMode.STANDARD,
    )
    original_values = scenario.model_dump()

    result = orchestrate_federal_tax(scenario)

    assert scenario.model_dump() == original_values
    assert result.scenario is scenario


def test_orchestrator_applies_deduction_floor_after_taxable_social_security():
    """Verifies deductions apply to effective ordinary income without reducing LTCG/QD income."""
    scenario = TaxScenarioInput(
        tax_year=2026,
        state_code="NC",
        filing_status=FilingStatus.SINGLE,
        ordinary_income=40000.0,
        ltcg_qd_income=20000.0,
        social_security_income=30000.0,
        deduction_mode=DeductionMode.EXPLICIT,
        deduction_amount=10000.0,
    )
    original_values = scenario.model_dump()

    result = orchestrate_federal_tax(scenario)

    effective_ordinary_income = (
        scenario.ordinary_income + result.ss_output.taxable_social_security
    )
    applied_deduction = 16100.0

    assert result.ordinary_output.ordinary_income == pytest.approx(
        effective_ordinary_income
    )
    assert result.ordinary_output.deduction_applied == applied_deduction
    assert result.taxable_ordinary_income == pytest.approx(
        max(0.0, effective_ordinary_income - applied_deduction)
    )
    assert result.taxable_preferential_income == scenario.ltcg_qd_income
    assert scenario.model_dump() == original_values


def test_orchestrator_rejects_mfs_before_downstream_calls(monkeypatch):
    """Verifies MFS rejection occurs before any imported downstream engine call."""
    scenario = TaxScenarioInput(
        tax_year=2026,
        state_code="NC",
        filing_status=FilingStatus.MARRIED_FILING_SEPARATELY,
        ordinary_income=50000.0,
    )

    def downstream_call_not_allowed(*args, **kwargs):
        raise AssertionError("Downstream engine was called for MFS.")

    monkeypatch.setattr(
        "engines.federal_orchestrator.compute_taxable_social_security",
        downstream_call_not_allowed,
    )
    monkeypatch.setattr(
        "engines.federal_orchestrator.compute_federal_ordinary_tax",
        downstream_call_not_allowed,
    )
    monkeypatch.setattr(
        "engines.federal_orchestrator.compute_preferential_tax",
        downstream_call_not_allowed,
    )
    monkeypatch.setattr(
        "engines.federal_orchestrator.compute_niit",
        downstream_call_not_allowed,
    )

    with pytest.raises(ValueError, match="Married Filing Separately \\(MFS\\) is unsupported."):
        orchestrate_federal_tax(scenario)


def test_orchestrator_head_of_household_smoke():
    """Verifies a supported Head of Household scenario completes the pipeline."""
    scenario = TaxScenarioInput(
        tax_year=2026,
        state_code="NC",
        filing_status=FilingStatus.HEAD_OF_HOUSEHOLD,
        ordinary_income=40000.0,
        ltcg_qd_income=10000.0,
    )

    result = orchestrate_federal_tax(scenario)

    assert result.scenario is scenario
    assert result.agi == 50000.0
    assert result.total_federal_tax == pytest.approx(
        result.ordinary_tax + result.ltcg_qd_tax + result.niit_tax
    )


def test_orchestrator_ss_flow():
    """Verifies Social Security income flows into gross ordinary income and increases ordinary tax."""
    scenario = TaxScenarioInput(
        tax_year=2026,
        state_code="NC",
        filing_status=FilingStatus.SINGLE,
        ordinary_income=40000.0,
        social_security_income=30000.0,
        deduction_mode=DeductionMode.STANDARD,
    )
    result = orchestrate_federal_tax(scenario)

    assert result.ss_output.taxable_social_security > 0.0
    
    # Assert ordinary engine receives the cascade exactly
    expected_gross_ordinary = scenario.ordinary_income + result.ss_output.taxable_social_security
    assert result.ordinary_output.ordinary_income == expected_gross_ordinary
    
    # Assert AGI correctly aggregates gross ordinary and preferential income
    assert result.agi == expected_gross_ordinary + scenario.ltcg_qd_income


def test_orchestrator_preferential_stacking():
    """Verifies LTCG/QD preferential income stacks properly on taxable ordinary income."""
    scenario = TaxScenarioInput(
        tax_year=2026,
        state_code="NC",
        filing_status=FilingStatus.SINGLE,
        ordinary_income=60000.0,
        ltcg_qd_income=20000.0,
        deduction_mode=DeductionMode.STANDARD,
    )
    result = orchestrate_federal_tax(scenario)

    assert result.taxable_preferential_income == 20000.0
    assert result.ltcg_qd_output.taxed_at_15 > 0.0
    assert result.ltcg_qd_tax > 0.0
    assert result.agi == 80000.0


def test_orchestrator_niit_trigger():
    """Verifies NIIT calculation when MAGI exceeds threshold ($200k Single)."""
    scenario = TaxScenarioInput(
        tax_year=2026,
        state_code="NC",
        filing_status=FilingStatus.SINGLE,
        ordinary_income=220000.0,
        ltcg_qd_income=50000.0,
        deduction_mode=DeductionMode.STANDARD,
    )
    result = orchestrate_federal_tax(scenario)

    assert result.magi == 270000.0
    assert result.niit_output.magi_over_threshold == 70000.0
    assert result.niit_output.tax_base == 50000.0  # min(50k NII, 70k excess)
    assert result.niit_tax == pytest.approx(50000.0 * 0.038)


def test_orchestrator_total_reconciliation():
    """Verifies mathematical reconciliation that total federal tax equals component sum across scenarios."""
    scenarios = [
        TaxScenarioInput(
            tax_year=2026, state_code="NC", filing_status=FilingStatus.SINGLE, ordinary_income=15000.0
        ),
        TaxScenarioInput(
            tax_year=2026,
            state_code="NC",
            filing_status=FilingStatus.MARRIED_FILING_JOINTLY,
            ordinary_income=120000.0,
            ltcg_qd_income=30000.0,
        ),
        TaxScenarioInput(
            tax_year=2026,
            state_code="NC",
            filing_status=FilingStatus.SINGLE,
            ordinary_income=250000.0,
            ltcg_qd_income=40000.0,
            social_security_income=20000.0,
        ),
    ]

    for scenario in scenarios:
        res = orchestrate_federal_tax(scenario)
        expected_total = res.ordinary_tax + res.ltcg_qd_tax + res.niit_tax
        assert res.total_federal_tax == pytest.approx(expected_total)