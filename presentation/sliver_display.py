from models.outputs import (
    FederalCombinedSliverResult,
    FederalLTCGQDSLiverResult,
    FederalSliverResult,
)
from models.sliver_display import FederalSliverDisplayModel


def _build_model(
    result,
    *,
    result_kind: str,
    ordinary_income_increment: float = 0.0,
    ltcg_qd_income_increment: float = 0.0,
) -> FederalSliverDisplayModel:
    scenario = result.baseline_result.scenario
    return FederalSliverDisplayModel(
        tax_year=scenario.tax_year,
        filing_status=scenario.filing_status,
        result_kind=result_kind,
        baseline_total_federal_tax=result.baseline_result.total_federal_tax,
        altered_total_federal_tax=result.altered_result.total_federal_tax,
        federal_tax_delta=result.federal_tax_delta,
        ordinary_income_increment=ordinary_income_increment,
        ltcg_qd_income_increment=ltcg_qd_income_increment,
    )


def build_federal_sliver_display_model(
    result: FederalSliverResult,
) -> FederalSliverDisplayModel:
    return _build_model(
        result,
        result_kind="ordinary_income",
        ordinary_income_increment=result.ordinary_income_increment,
    )


def build_federal_ltcg_qd_sliver_display_model(
    result: FederalLTCGQDSLiverResult,
) -> FederalSliverDisplayModel:
    return _build_model(
        result,
        result_kind="ltcg_qd_income",
        ltcg_qd_income_increment=result.ltcg_qd_income_increment,
    )


def build_federal_combined_sliver_display_model(
    result: FederalCombinedSliverResult,
) -> FederalSliverDisplayModel:
    return _build_model(
        result,
        result_kind="combined_income",
        ordinary_income_increment=result.ordinary_income_increment,
        ltcg_qd_income_increment=result.ltcg_qd_income_increment,
    )
