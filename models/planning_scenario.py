from dataclasses import dataclass

from models.irmaa import IRMAAOverlayResult
from models.inputs import TaxScenarioInput
from models.nc_planning import NCPlanningResult
from models.outputs import FederalTaxResult


@dataclass(frozen=True)
class PlanningScenarioResult:
    scenario: TaxScenarioInput
    federal_result: FederalTaxResult
    nc_planning_result: NCPlanningResult
    projected_irmaa_2028: IRMAAOverlayResult | None
