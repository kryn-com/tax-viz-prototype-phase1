import pytest

from engines import sliver_analysis
from models.inputs import FilingStatus, TaxScenarioInput
from models.outputs import (
    FederalCombinedSliverResult,
    FederalLTCGQDSLiverResult,
    FederalSliverResult,
)


def create_sliver_scenario(
    filing_status: FilingStatus = FilingStatus.SINGLE,
) -> TaxScenarioInput:
    return TaxScenarioInput(
        tax_year=2026,
        state_code="NC",
        filing_status=filing_status,
        taxpayer_age=45,
        spouse_age=45 if filing_status is FilingStatus.MARRIED_FILING_JOINTLY else None,
        ordinary_income=40000.0,
        ltcg_qd_income=20000.0,
        social_security_income=30000.0,
        deduction_amount=10000.0,
    )


def test_ordinary_income_sliver_recomputes_full_pipeline_and_delta():
    scenario = create_sliver_scenario()

    result = sliver_analysis.analyze_ordinary_income_sliver(scenario, increment=1000.0)

    assert isinstance(result, FederalSliverResult)
    assert result.baseline_result.scenario is scenario
    assert result.altered_result.scenario.ordinary_income == 41000.0
    assert result.ordinary_income_increment == 1000.0
    assert result.federal_tax_delta == pytest.approx(
        result.altered_result.total_federal_tax
        - result.baseline_result.total_federal_tax
    )
    assert result.altered_result.ss_output is not None
    assert result.altered_result.ordinary_output is not None
    assert result.altered_result.ltcg_qd_output is not None
    assert result.altered_result.niit_output is not None


def test_ordinary_income_sliver_does_not_mutate_input():
    scenario = create_sliver_scenario()
    original_values = scenario.model_dump()

    result = sliver_analysis.analyze_ordinary_income_sliver(scenario, increment=1000.0)

    assert scenario.model_dump() == original_values
    assert result.baseline_result.scenario is scenario
    assert result.altered_result.scenario is not scenario


def test_ordinary_income_sliver_calls_orchestrator_twice(monkeypatch):
    scenario = create_sliver_scenario()
    real_orchestrator = sliver_analysis.orchestrate_federal_tax
    calls = []

    def tracking_orchestrator(call_scenario):
        calls.append(call_scenario)
        return real_orchestrator(call_scenario)

    monkeypatch.setattr(sliver_analysis, "orchestrate_federal_tax", tracking_orchestrator)

    sliver_analysis.analyze_ordinary_income_sliver(scenario, increment=1000.0)

    assert len(calls) == 2
    assert calls[0] is scenario
    assert calls[1] is not scenario
    assert calls[1].ordinary_income == 41000.0


@pytest.mark.parametrize("increment", [0.0, -1.0])
def test_ordinary_income_sliver_requires_positive_increment(increment):
    with pytest.raises(ValueError, match="must be greater than zero"):
        sliver_analysis.analyze_ordinary_income_sliver(
            create_sliver_scenario(), increment=increment
        )


def test_ordinary_income_sliver_preserves_mfs_rejection():
    with pytest.raises(ValueError, match="Married Filing Separately \\(MFS\\) is unsupported"):
        sliver_analysis.analyze_ordinary_income_sliver(
            create_sliver_scenario(FilingStatus.MARRIED_FILING_SEPARATELY),
            increment=1000.0,
        )


def test_ltcg_qd_sliver_recomputes_full_pipeline_and_delta():
    scenario = create_sliver_scenario()

    result = sliver_analysis.analyze_ltcg_qd_sliver(scenario, increment=1000.0)

    assert isinstance(result, FederalLTCGQDSLiverResult)
    assert result.baseline_result.scenario is scenario
    assert result.altered_result.scenario.ltcg_qd_income == 21000.0
    assert result.altered_result.scenario.ordinary_income == scenario.ordinary_income
    assert result.ltcg_qd_income_increment == 1000.0
    assert result.federal_tax_delta == pytest.approx(
        result.altered_result.total_federal_tax
        - result.baseline_result.total_federal_tax
    )
    assert result.altered_result.ss_output is not None
    assert result.altered_result.ordinary_output is not None
    assert result.altered_result.ltcg_qd_output is not None
    assert result.altered_result.niit_output is not None


def test_ltcg_qd_sliver_does_not_mutate_input():
    scenario = create_sliver_scenario()
    original_values = scenario.model_dump()

    result = sliver_analysis.analyze_ltcg_qd_sliver(scenario, increment=1000.0)

    assert scenario.model_dump() == original_values
    assert result.baseline_result.scenario is scenario
    assert result.altered_result.scenario is not scenario


def test_ltcg_qd_sliver_calls_orchestrator_twice(monkeypatch):
    scenario = create_sliver_scenario()
    real_orchestrator = sliver_analysis.orchestrate_federal_tax
    calls = []

    def tracking_orchestrator(call_scenario):
        calls.append(call_scenario)
        return real_orchestrator(call_scenario)

    monkeypatch.setattr(sliver_analysis, "orchestrate_federal_tax", tracking_orchestrator)

    sliver_analysis.analyze_ltcg_qd_sliver(scenario, increment=1000.0)

    assert len(calls) == 2
    assert calls[0] is scenario
    assert calls[1] is not scenario
    assert calls[1].ltcg_qd_income == 21000.0
    assert calls[1].ordinary_income == scenario.ordinary_income


@pytest.mark.parametrize("increment", [0.0, -1.0])
def test_ltcg_qd_sliver_requires_positive_increment(increment):
    with pytest.raises(ValueError, match="must be greater than zero"):
        sliver_analysis.analyze_ltcg_qd_sliver(
            create_sliver_scenario(), increment=increment
        )


def test_ltcg_qd_sliver_preserves_mfs_rejection():
    with pytest.raises(ValueError, match="Married Filing Separately \\(MFS\\) is unsupported"):
        sliver_analysis.analyze_ltcg_qd_sliver(
            create_sliver_scenario(FilingStatus.MARRIED_FILING_SEPARATELY),
            increment=1000.0,
        )


def test_combined_income_sliver_recomputes_full_pipeline_and_delta():
    scenario = create_sliver_scenario()

    result = sliver_analysis.analyze_combined_income_sliver(
        scenario,
        ordinary_income_increment=1000.0,
        ltcg_qd_income_increment=2000.0,
    )

    assert isinstance(result, FederalCombinedSliverResult)
    assert result.baseline_result.scenario is scenario
    assert result.altered_result.scenario.ordinary_income == 41000.0
    assert result.altered_result.scenario.ltcg_qd_income == 22000.0
    assert result.ordinary_income_increment == 1000.0
    assert result.ltcg_qd_income_increment == 2000.0
    assert result.federal_tax_delta == pytest.approx(
        result.altered_result.total_federal_tax
        - result.baseline_result.total_federal_tax
    )
    assert result.altered_result.ss_output is not None
    assert result.altered_result.ordinary_output is not None
    assert result.altered_result.ltcg_qd_output is not None
    assert result.altered_result.niit_output is not None


def test_combined_income_sliver_does_not_mutate_input():
    scenario = create_sliver_scenario()
    original_values = scenario.model_dump()

    result = sliver_analysis.analyze_combined_income_sliver(
        scenario,
        ordinary_income_increment=1000.0,
        ltcg_qd_income_increment=2000.0,
    )

    assert scenario.model_dump() == original_values
    assert result.baseline_result.scenario is scenario
    assert result.altered_result.scenario is not scenario


def test_combined_income_sliver_calls_orchestrator_twice(monkeypatch):
    scenario = create_sliver_scenario()
    real_orchestrator = sliver_analysis.orchestrate_federal_tax
    calls = []

    def tracking_orchestrator(call_scenario):
        calls.append(call_scenario)
        return real_orchestrator(call_scenario)

    monkeypatch.setattr(sliver_analysis, "orchestrate_federal_tax", tracking_orchestrator)

    sliver_analysis.analyze_combined_income_sliver(
        scenario,
        ordinary_income_increment=1000.0,
        ltcg_qd_income_increment=2000.0,
    )

    assert len(calls) == 2
    assert calls[0] is scenario
    assert calls[1] is not scenario
    assert calls[1].ordinary_income == 41000.0
    assert calls[1].ltcg_qd_income == 22000.0


@pytest.mark.parametrize(
    ("ordinary_increment", "ltcg_qd_increment", "message"),
    [
        (0.0, 2000.0, "ordinary-income"),
        (-1.0, 2000.0, "ordinary-income"),
        (1000.0, 0.0, "LTCG/QD"),
        (1000.0, -1.0, "LTCG/QD"),
    ],
)
def test_combined_income_sliver_requires_positive_increments(
    ordinary_increment,
    ltcg_qd_increment,
    message,
):
    with pytest.raises(ValueError, match=f"{message}.*greater than zero"):
        sliver_analysis.analyze_combined_income_sliver(
            create_sliver_scenario(),
            ordinary_income_increment=ordinary_increment,
            ltcg_qd_income_increment=ltcg_qd_increment,
        )


def test_combined_income_sliver_preserves_mfs_rejection():
    with pytest.raises(ValueError, match="Married Filing Separately \\(MFS\\) is unsupported"):
        sliver_analysis.analyze_combined_income_sliver(
            create_sliver_scenario(FilingStatus.MARRIED_FILING_SEPARATELY),
            ordinary_income_increment=1000.0,
            ltcg_qd_income_increment=2000.0,
        )
