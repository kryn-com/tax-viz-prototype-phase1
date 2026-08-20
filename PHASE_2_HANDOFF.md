# Phase 2 Handoff Document

## Completed in Phase 1

* **Strict typed input validation:** via Pydantic (`TaxScenarioInput`). Automatically rejects invalid states (e.g., negative deductions, unsupported years).

* **Tax Bracket Framework:** A versionable rule structure (`rules.federal.year_2026`) that cleanly segregates tax policy data from engine logic.

* **Ordinary Income Tax Engine:** Determines `taxable_ordinary_income` and generates a precise `bracket_trace` showing the exact slice of income taxed per bracket.

* **Automated Tests:** Covered edge cases (spanning brackets, exactly hitting bounds, zero taxable income floors).

* **Architecture Stubs:** `interfaces/stubs.py` outlines where future calculation engines belong.

## Recommended Phase 2 Build Order

1. **LTCG & Qualified Dividends Engine:**

   * Integrate with the existing bracket trace concept. Preferential income stacks *on top* of ordinary income.

2. **Social Security Taxability Engine:**

   * Needs to pre-process before deductions, computing provisional income to find the taxable SS portion, which is then injected back into ordinary income.

3. **NIIT (Net Investment Income Tax):**

   * Requires knowing both MAGI and total investment income.

4. **State Tax Plugin Framework:**

   * Requires abstracting state-level rules in `rules/states/` mimicking the federal pattern.

## Major Design Choices

* **Pydantic for Inputs:** Chosen over standard dataclasses to push validation logic (like `ge=0` and custom validators) out of the calculation engine.

* **Full Bracket Traces:** The engine processes *every* bracket, even if 0 income falls into it. This ensures chart generating utilities downstream have full context of the bracket bounds.

* **Explicit Deductions:** `deduction_amount` is explicitly passed rather than auto-inferring standard vs itemized at this phase.