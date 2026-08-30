# Phase 33 Handoff — North Carolina Simplified Tax Engine

## Status

**Complete and pushed**

- Branch: `phase-2-social-security`
- Phase 33A commit: `9997874` — `Add NC input contract scaffolding`
- Phase 33B commit: `c47dac1` — `Add simplified NC pre-credit tax engine`
- Latest verification: `python -m pytest -q` → **190 passed**
- Working tree was clean after Phase 33B commit and push.

## Objective Completed

Phase 33 added a narrow, deterministic, explainable North Carolina planning layer for tax year 2026.

The implementation remains separate from federal tax computation, presentation/SVG work, Streamlit/UI work, and IRMAA.

## Phase 33A — NC Input Contract

Added the following NC-specific fields to `TaxScenarioInput`:

- `federal_agi`
- `federal_taxable_social_security`
- `net_nc_interest_dividend_adjustment`
- `bailey_exempt_pension_amount`
- `nc_deduction_mode`
- `nc_itemized_deduction_amount`

Validation behavior:

- `net_nc_interest_dividend_adjustment` accepts positive or negative values.
- `bailey_exempt_pension_amount` is optional and cannot be negative.
- `nc_itemized_deduction_amount` is required when `nc_deduction_mode` is `itemized`.
- `nc_itemized_deduction_amount` is rejected when `nc_deduction_mode` is `standard`.
- Taxpayer ages remain unused by NC logic in Phase 33.

## Phase 33B — Simplified NC Computation

Added `compute_nc_tax(scenario)` in `engines/state_tax.py`.

The supported formula is:

```text
NC taxable income =
  max(
    0,
    federal_agi
    - federal_taxable_social_security
    + net_nc_interest_dividend_adjustment
    - bailey_exempt_pension_amount
    - selected_nc_deduction
  )

NC income tax before credits =
  NC taxable income × 0.0399
```

Implementation behavior:

- Uses a 2026 NC flat rate of **3.99%**.
- Uses filing-status-specific NC standard deductions:
  - Single: $12,750
  - Head of household: $19,125
  - Married filing jointly: $25,500
- Uses `nc_itemized_deduction_amount` when the input deduction mode is `itemized`.
- Floors NC taxable income at zero.
- Rounds the final pre-credit NC tax result to cents.
- Returns a typed `NCStateTaxResult` with taxable income, pre-credit tax, and an explainable breakdown.

## Personal 2025 Reference Tie-Out

A personal 2025 return was used as a practical formula validation reference only. Personal tax-return data was not committed to the repository or test fixtures.

Reference inputs:

- Filing status: single
- Federal AGI: $109,251
- Federally taxable Social Security: $6,089
- Net NC interest/dividend adjustment: -$1,110
- Bailey exemption: $0
- NC itemized deduction: $17,543
- Reported NC tax before foreign-tax credit: $3,592

2025 formula check:

```text
109,251
- 6,089
- 1,110
- 17,543
= 84,509 NC taxable income

84,509 × 4.25% = 3,591.63
```

Rounded to whole dollars, this equals the reported **$3,592** pre-credit NC tax.

This validates the simplified formula structure against the available 2025 reference values. The 2026 engine correctly uses 3.99%, so it is a planning engine and is not intended to reproduce a 2025 return exactly.

## Tests

Focused NC tests cover:

- NC input-contract validation.
- Signed interest/dividend adjustments.
- Optional Bailey amount behavior.
- Standard versus itemized deduction validation.
- Filing-status-specific standard deduction selection.
- Taxable Social Security subtraction.
- Zero taxable-income floor.
- Flat-rate pre-credit tax calculation.
- No NC credit fields or broader credit behavior.

Validation completed:

```text
python -m pytest tests/test_state_contract.py -q
18 passed

python -m pytest -q
190 passed
```

## Preserved Boundaries

Do not broaden these without explicit approval:

- No NC credits, including foreign-tax or other-state credits.
- No withholding, estimated payments, refunds, penalties, or consumer-use tax.
- No broader NC additions, subtractions, or detailed itemized-deduction categories.
- No federal formula or output changes.
- No age-based NC logic.
- No presentation, SVG, Streamlit, UI, chart, or IRMAA changes.

## Known Limitations

Phase 33 is a simplified NC pre-credit planning model, not a complete statutory NC return engine.

It models only the approved inputs and does not claim to calculate all possible NC adjustments, deductions, credits, or payment/refund outcomes.

`models/state.py` includes an `NCStateTaxBreakdown` dataclass that is currently unused because the returned `NCStateTaxResult` stores its breakdown as a dictionary. This is harmless but may be cleaned up in a later narrow maintenance phase.

## Recommended Next Decision

Before more implementation, choose one narrow direction:

1. **NC refinement planning only** — identify which additional NC adjustments or deduction rules are worth supporting based on real planning scenarios, without coding them yet.
2. **State-result integration planning only** — decide how the separate NC result should eventually be composed with federal results while preserving domain boundaries.
3. **IRMAA overlay planning** — define a separate, age-aware Medicare premium overlay without mixing it into tax computation.
4. **Presentation recovery** — resume the explicitly paused SVG layout review only after reviewing a generated artifact before any presentation commit.

Do not start Streamlit/UI work until an explicit decision is made.