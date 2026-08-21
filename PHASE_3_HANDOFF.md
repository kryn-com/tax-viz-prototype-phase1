# Phase 3 Handoff — Federal Pipeline Orchestrator

## Status
Phase 3 is complete and merged into `phase-2-social-security`.

- Merge commit: `8df067c`
- Implementation commit: `1ed2415`
- Pull request: #1
- Test result: `33 passed`

## Implemented Files
- `engines/federal_orchestrator.py`
- `models/outputs.py`
- `tests/test_federal_orchestrator.py`

## Public Entry Point
`orchestrate_federal_tax(scenario: TaxScenarioInput) -> FederalTaxResult`

## Actual Engine Interfaces
- Social Security: `compute_taxable_social_security(scenario: TaxScenarioInput) -> SocialSecurityOutput`
- Ordinary tax: `compute_federal_ordinary_tax(scenario: TaxScenarioInput) -> FederalOrdinaryOutput`
- Preferential tax: `compute_preferential_tax(scenario: TaxScenarioInput) -> LTCG_QD_Output`
- NIIT: `compute_niit(filing_status: FilingStatus, magi: float, net_investment_income: float) -> NIITOutput`
- Deduction helper: `compute_taxable_ordinary_income(ordinary_income: float, deduction_amount: float) -> float`

## Pipeline Behavior
1. Reject MFS explicitly.
2. Calculate taxable Social Security.
3. Create an effective scenario with taxable Social Security added to ordinary income.
4. Run ordinary tax and LTCG/QD tax against the effective scenario.
5. Calculate AGI and prototype MAGI.
6. Map `ltcg_qd_income` to NIIT net investment income for this prototype.
7. Return component outputs plus transparent aggregate tax totals.

## Important Constraints
- No tax formulas or thresholds were changed.
- The deductions helper returns a scalar, not a structured output; `FederalTaxResult` intentionally has no speculative deduction-output object.
- Keep tax logic separate from future presentation/UI work.
- MFS remains permanently unsupported.
- State tax and IRMAA remain out of scope.

## Validation
- `python -m pytest -q`
- Result: `33 passed in 0.11s`

## Starting Point for Next Phase
Start from the updated `phase-2-social-security` branch.
Read `PROJECT_SCOPE.md`, this handoff, and the current repository before proposing any next implementation phase.