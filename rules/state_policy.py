STATE_TAX_RATES_2026 = {
    "PA": 0.0307,
    "NC": 0.0399,
    "IL": 0.0495,
    "IN": 0.029,
}

NC_2026_RULES = {
    "state_code": "NC",
    "tax_year": 2026,
    "supported": True,
    "deduction_modes": ["standard", "itemized"],
    "credits": [],
    "standard_deduction_by_filing_status": {
        "single": 12750.0,
        "head_of_household": 19125.0,
        "married_filing_jointly": 25500.0,
    },
    "flat_rate": 0.0399,
    "notes": "Phase 33B simplified NC taxable-income and pre-credit tax calculation only.",
}