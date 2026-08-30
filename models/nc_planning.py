from dataclasses import dataclass

from models.outputs import FederalTaxResult
from models.state import NCStateTaxResult


@dataclass(frozen=True)
class NCPlanningResult:
    federal_result: FederalTaxResult
    nc_state_result: NCStateTaxResult


def compose_nc_planning_result(
    federal_result: FederalTaxResult,
    nc_state_result: NCStateTaxResult,
) -> NCPlanningResult:
    return NCPlanningResult(
        federal_result=federal_result,
        nc_state_result=nc_state_result,
    )
