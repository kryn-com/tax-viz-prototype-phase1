from dataclasses import dataclass

from models.ordinary_income_sliver import (
    NCSupportedResult,
    ProjectedIRMAASupportedResult,
)
from models.outputs import FederalTaxResult, NIITOutput


@dataclass(frozen=True)
class LTCGQDSliverDeltas:
    federal_total_tax_delta: float
    federal_ordinary_tax_delta: float
    federal_ltcg_qd_tax_delta: float
    federal_niit_tax_delta: float
    nc_income_tax_before_credits_delta: float | None
    niit_component_delta: float
    projected_irmaa_annual_surcharge_delta: float | None


@dataclass(frozen=True)
class LTCGQDSliverCompositionResult:
    result_kind: str
    additional_ltcg_qd_income: float
    baseline_federal_result: FederalTaxResult
    altered_federal_result: FederalTaxResult
    baseline_nc_result: NCSupportedResult
    altered_nc_result: NCSupportedResult
    baseline_niit_component: NIITOutput
    altered_niit_component: NIITOutput
    baseline_projected_irmaa_2028: ProjectedIRMAASupportedResult
    altered_projected_irmaa_2028: ProjectedIRMAASupportedResult
    deltas: LTCGQDSliverDeltas