# Ambiguities Requiring Review

During Phase 1 construction, the following under-specified details were resolved using provisional assumptions to guarantee engine completion:

1. **2026 Tax Bracket Tables**
   - **Ambiguity:** Official 2026 IRS tax brackets are not yet published and depend on the legislative future of the TCJA (Tax Cuts and Jobs Act).
   - **Provisional Assumption:** Extrapolated brackets mimicking recent structures were hardcoded into `rules/federal/year_2026.py`. **Action Required:** Update `rules/federal/year_2026.py` when official laws are passed/inflation adjustments are finalized.

2. **Negative Ordinary Income**
   - **Ambiguity:** The prompt required rejecting negative deductions but did not explicitly constrain negative *ordinary income* (which can occur with severe business losses). 
   - **Provisional Assumption:** Pydantic validation enforces `ge=0.0` on ordinary income. **Action Required:** Re-evaluate if Phase 2+ requires handling Net Operating Losses (NOLs).

3. **Empty Bracket Upper Bounds**
   - **Ambiguity:** The highest tax brackets have no ceiling, making visualization calculations tricky without a definitive numeric end point.
   - **Provisional Assumption:** Programmatically represented as `upper: None`. The trace output preserves this `None`. Downstream chart generation will need logic to invent a ceiling for visualization purposes.