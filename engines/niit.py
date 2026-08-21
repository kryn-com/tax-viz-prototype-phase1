from models.inputs import FilingStatus
from models.outputs import NIITOutput

def compute_niit(filing_status: FilingStatus, magi: float, net_investment_income: float) -> NIITOutput:
    if magi < 0 or net_investment_income < 0:
        raise ValueError("MAGI and net investment income cannot be negative.")

    if filing_status == FilingStatus.MARRIED_FILING_SEPARATELY:
        raise NotImplementedError("Married Filing Separately is not implemented.")
    elif filing_status == FilingStatus.MARRIED_FILING_JOINTLY:
        threshold = 250000.0
    elif filing_status in (FilingStatus.SINGLE, FilingStatus.HEAD_OF_HOUSEHOLD):
        threshold = 200000.0
    else:
        raise ValueError(f"Unsupported status for NIIT: {filing_status}")

    niit_rate = 0.038
    magi_over_threshold = max(magi - threshold, 0.0)
    tax_base = min(net_investment_income, magi_over_threshold)
    niit_tax = tax_base * niit_rate

    return NIITOutput(
        net_investment_income=net_investment_income,
        magi=magi,
        threshold_applied=threshold,
        magi_over_threshold=magi_over_threshold,
        tax_base=tax_base,
        niit_rate=niit_rate,
        niit_tax=niit_tax
    )