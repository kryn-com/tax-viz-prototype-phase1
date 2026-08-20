from models.inputs import TaxScenarioInput, FilingStatus
from models.outputs import SocialSecurityOutput

def compute_taxable_social_security(scenario: TaxScenarioInput) -> SocialSecurityOutput:
    """
    Calculates the taxable portion of Social Security benefits based on provisional income.
    Implements thresholds and logic for Single, Head of Household, and Married Filing Jointly.
    Married Filing Separately is explicitly out of scope.
    """
    
    if scenario.filing_status == FilingStatus.MARRIED_FILING_SEPARATELY:
        raise NotImplementedError("Married Filing Separately is permanently out of scope for this project.")
        
    if scenario.filing_status in (FilingStatus.SINGLE, FilingStatus.HEAD_OF_HOUSEHOLD):
        threshold_1 = 25000.0
        threshold_2 = 34000.0
        base_amount = 4500.0
    elif scenario.filing_status == FilingStatus.MARRIED_FILING_JOINTLY:
        threshold_1 = 32000.0
        threshold_2 = 44000.0
        base_amount = 6000.0
    else:
        raise ValueError(f"Unsupported filing status: {scenario.filing_status}")

    benefits = scenario.social_security_income
    
    # Handle the trivial case where there are no benefits to tax
    if benefits == 0.0:
        return SocialSecurityOutput(
            total_social_security=0.0,
            taxable_social_security=0.0,
            tax_free_social_security=0.0,
            provisional_income=scenario.ordinary_income + scenario.ltcg_qd_income + scenario.nontaxable_income
        )

    # Provisional income includes half of Social Security benefits plus other incomes
    provisional_income = (
        scenario.ordinary_income + 
        scenario.ltcg_qd_income + 
        scenario.nontaxable_income + 
        (0.5 * benefits)
    )

    taxable_ss = 0.0

    if provisional_income <= threshold_1:
        # Below first threshold: 0% taxable
        taxable_ss = 0.0
        
    elif provisional_income <= threshold_2:
        # Between first and second threshold: up to 50% taxable
        taxable_ss = min(
            0.5 * benefits, 
            0.5 * (provisional_income - threshold_1)
        )
        
    else:
        # Above second threshold: up to 85% taxable
        # Bug fix: Add the smaller of the base amount or 50% of benefits
        taxable_ss = min(
            0.85 * benefits, 
            0.85 * (provisional_income - threshold_2) + min(base_amount, 0.5 * benefits)
        )

    return SocialSecurityOutput(
        total_social_security=benefits,
        taxable_social_security=taxable_ss,
        tax_free_social_security=benefits - taxable_ss,
        provisional_income=provisional_income
    )