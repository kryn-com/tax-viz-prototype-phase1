from models.outputs import FederalTaxReconciliation, FederalTaxResult


def reconcile_federal_tax(
    result: FederalTaxResult,
) -> FederalTaxReconciliation:
    component_tax_total = result.ordinary_tax + result.ltcg_qd_tax + result.niit_tax
    reported_total_federal_tax = result.total_federal_tax
    reconciliation_delta = reported_total_federal_tax - component_tax_total

    return FederalTaxReconciliation(
        ordinary_tax=result.ordinary_tax,
        ltcg_qd_tax=result.ltcg_qd_tax,
        niit_tax=result.niit_tax,
        component_tax_total=component_tax_total,
        reported_total_federal_tax=reported_total_federal_tax,
        reconciliation_delta=reconciliation_delta,
    )