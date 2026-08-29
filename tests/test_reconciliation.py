from dataclasses import replace

import pytest

from engines.federal_orchestrator import orchestrate_federal_tax
from engines.reconciliation import reconcile_federal_tax
from models.inputs import FilingStatus, TaxScenarioInput


def create_reconciliation_scenario(
    ordinary_income: float = 100000.0,
    ltcg_qd_income: float = 20000.0,
) -> TaxScenarioInput:
    return TaxScenarioInput(
        tax_year=2026,
        state_code="NC",
        filing_status=FilingStatus.SINGLE,
        taxpayer_age=45,
        ordinary_income=ordinary_income,
        ltcg_qd_income=ltcg_qd_income,
    )


def test_reconcile_normal_orchestrated_result():
    result = orchestrate_federal_tax(create_reconciliation_scenario())

    reconciliation = reconcile_federal_tax(result)

    assert reconciliation.ordinary_tax == result.ordinary_tax
    assert reconciliation.ltcg_qd_tax == result.ltcg_qd_tax
    assert reconciliation.niit_tax == result.niit_tax
    assert reconciliation.component_tax_total == pytest.approx(
        result.ordinary_tax + result.ltcg_qd_tax + result.niit_tax
    )
    assert reconciliation.reported_total_federal_tax == result.total_federal_tax
    assert reconciliation.reconciliation_delta == pytest.approx(0.0)


def test_reconcile_zero_tax_result():
    scenario = TaxScenarioInput(
        tax_year=2026,
        state_code="NC",
        filing_status=FilingStatus.SINGLE,
        taxpayer_age=45,
    )

    reconciliation = reconcile_federal_tax(orchestrate_federal_tax(scenario))

    assert reconciliation.ordinary_tax == 0.0
    assert reconciliation.ltcg_qd_tax == 0.0
    assert reconciliation.niit_tax == 0.0
    assert reconciliation.component_tax_total == 0.0
    assert reconciliation.reported_total_federal_tax == 0.0
    assert reconciliation.reconciliation_delta == 0.0


def test_reconcile_detects_altered_reported_total():
    result = orchestrate_federal_tax(create_reconciliation_scenario())
    altered_result = replace(result, total_federal_tax=result.total_federal_tax + 100.0)

    reconciliation = reconcile_federal_tax(altered_result)

    assert reconciliation.reconciliation_delta == pytest.approx(100.0)


def test_reconcile_does_not_mutate_result_or_scenario():
    result = orchestrate_federal_tax(create_reconciliation_scenario())
    original_values = result.scenario.model_dump()
    original_total = result.total_federal_tax

    reconcile_federal_tax(result)

    assert result.scenario.model_dump() == original_values
    assert result.total_federal_tax == original_total


def test_reconcile_does_not_call_orchestrator(monkeypatch):
    result = orchestrate_federal_tax(create_reconciliation_scenario())

    def orchestrator_call_not_allowed(*args, **kwargs):
        raise AssertionError("Reconciliation must not rerun the tax pipeline.")

    monkeypatch.setattr(
        "engines.federal_orchestrator.orchestrate_federal_tax",
        orchestrator_call_not_allowed,
    )

    reconciliation = reconcile_federal_tax(result)

    assert reconciliation.reported_total_federal_tax == result.total_federal_tax