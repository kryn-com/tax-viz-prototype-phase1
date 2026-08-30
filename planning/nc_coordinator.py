from engines.federal_orchestrator import orchestrate_federal_tax
from engines.state_tax import compute_nc_tax
from models.inputs import TaxScenarioInput
from models.nc_planning import NCPlanningResult, compose_nc_planning_result


def orchestrate_nc_planning(scenario: TaxScenarioInput) -> NCPlanningResult:
    federal_result = orchestrate_federal_tax(scenario)
    nc_state_result = compute_nc_tax(scenario)
    return compose_nc_planning_result(federal_result, nc_state_result)
