from models.inputs import TaxScenarioInput, FilingStatus
from models.outputs import FederalTaxResult
from engines.social_security import compute_taxable_social_security
from engines.deductions import compute_taxable_ordinary_income
from engines.federal_ordinary import compute_federal_ordinary_tax
from engines.ltcg_qd import compute_preferential_tax
from engines.niit import compute_niit


def orchestrate_federal_tax(scenario: TaxScenarioInput) -> FederalTaxResult:
    """
    Top-level federal tax pipeline orchestrator for 2026 tax scenario.
    Deterministic, side-effect free, and preserves all engine-level outputs.
    """
    
    # 1. Validation Guard (MFS explicit rejection)
    if scenario.filing_status == FilingStatus.MARRIED_FILING_SEPARATELY:
        raise ValueError("Married Filing Separately (MFS) is unsupported.")

    # 2. Compute Social Security Taxability
    # This runs first to determine how much SS income must be added to the ordinary base.
    ss_output = compute_taxable_social_security(scenario)

    # 3. Derived Income Aggregates (AGI & MAGI)
    gross_ordinary = scenario.ordinary_income + ss_output.taxable_social_security
    gross_preferential = scenario.ltcg_qd_income
    agi = gross_ordinary + gross_preferential
    magi = agi  # 2026 prototype scope mapping (no foreign earned income exclusions)

    # 4. Effective Scenario Construction
    # We update the scenario with ordinary income inclusive of taxable Social Security
    # to feed correctly into deductions, ordinary tax, and LTCG/QD stacking.
    if hasattr(scenario, "model_copy"):
        effective_scenario = scenario.model_copy(update={"ordinary_income": gross_ordinary})
    else:
        effective_scenario = scenario.copy(update={"ordinary_income": gross_ordinary})

    # 5. Deductions & Ordinary Tax Computation
    ordinary_output = compute_federal_ordinary_tax(effective_scenario)

    # 6. Preferential Tax (LTCG / QD) Invocation
    # The LTCG/QD engine internally uses the effective scenario to stack 
    # preferential income on top of the taxable ordinary base.
    ltcg_qd_output = compute_preferential_tax(effective_scenario)

    # 7. Net Investment Income Tax (NIIT) Invocation
    # Prototype mapping: scenario.ltcg_qd_income serves directly as net_investment_income
    niit_output = compute_niit(
        filing_status=scenario.filing_status,
        magi=magi,
        net_investment_income=scenario.ltcg_qd_income,
    )

    # 8. Tax Totals Assembly
    ordinary_tax = ordinary_output.total_tax
    ltcg_qd_tax = ltcg_qd_output.total_preferential_tax
    niit_tax = niit_output.niit_tax
    total_federal_tax = ordinary_tax + ltcg_qd_tax + niit_tax

    return FederalTaxResult(
        scenario=scenario,
        agi=agi,
        magi=magi,
        taxable_ordinary_income=ordinary_output.taxable_ordinary_income,
        taxable_preferential_income=ltcg_qd_output.total_preferential_income,
        ss_output=ss_output,
        ordinary_output=ordinary_output,
        ltcg_qd_output=ltcg_qd_output,
        niit_output=niit_output,
        ordinary_tax=ordinary_tax,
        ltcg_qd_tax=ltcg_qd_tax,
        niit_tax=niit_tax,
        total_federal_tax=total_federal_tax,
    )