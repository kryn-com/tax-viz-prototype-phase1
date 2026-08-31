from dataclasses import dataclass

from models.irmaa import IRMAAOverlayResult
from models.outputs import FederalTaxResult, NIITOutput
from models.state import NCStateTaxResult


@dataclass(frozen=True)
class NCSupportedResult:
    supported: bool
    result: NCStateTaxResult | None
    message: str | None = None


@dataclass(frozen=True)
class ProjectedIRMAASupportedResult:
    supported: bool
    result: IRMAAOverlayResult | None
    message: str | None = None


@dataclass(frozen=True)
class OrdinaryIncomeSliverDeltas:
    federal_total_tax_delta: float
    federal_ordinary_tax_delta: float
    federal_ltcg_qd_tax_delta: float
    federal_niit_tax_delta: float
    nc_income_tax_before_credits_delta: float | None
    niit_component_delta: float
    projected_irmaa_annual_surcharge_delta: float | None


@dataclass(frozen=True)
class OrdinaryIncomeSliverCompositionResult:
    result_kind: str
    additional_ordinary_income: float
    baseline_federal_result: FederalTaxResult
    altered_federal_result: FederalTaxResult
    baseline_nc_result: NCSupportedResult
    altered_nc_result: NCSupportedResult
    baseline_niit_component: NIITOutput
    altered_niit_component: NIITOutput
    baseline_projected_irmaa_2028: ProjectedIRMAASupportedResult
    altered_projected_irmaa_2028: ProjectedIRMAASupportedResult
    deltas: OrdinaryIncomeSliverDeltas