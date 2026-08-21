# Phase 12 Handoff — Flat-Tax / No-Income-Tax State Expansion

## Status

Phase 12 is complete. This phase expanded the isolated numeric state-tax policy.

## What Was Completed

Added flat-tax support for:

- `NC`: 2026 rate `0.0399` (3.99%)
- `IL`: flat rate `0.0495` (4.95%)
- `IN`: 2026 rate `0.029` (2.9%)

Added no-individual-income-tax support for:

- `WA`
- `NV`
- `SD`
- `WY`

Each supported flat-tax state applies its rate directly to the explicit `StateTaxRequest.state_taxable_income` base. No state-specific income treatment is inferred.

Michigan was reviewed but remains unsupported because an authoritative 2026 rate was not verified during this phase.

## Files Changed

- `engines/state_policy.py`
- `rules/state_policy.py`
- `tests/test_state_contract.py`
- `tests/test_state_tax.py`

## Current Supported-State Policy

Flat-tax states:

- `PA`: `0.0307`
- `NC`: `0.0399`
- `IL`: `0.0495`
- `IN`: `0.029`

No-individual-income-tax states:

- `FL`
- `TX`
- `WA`
- `NV`
- `SD`
- `WY`

All other states, including `MI`, remain unsupported and raise `UnsupportedStateError`.

## Important Boundaries Preserved

- State tax remains isolated from federal code.
- `state_taxable_income` remains the explicit state tax base boundary.
- No federal files changed.
- `StateTaxPlugin` was not changed.
- `TaxScenarioInput`, `FederalTaxResult`, and reconciler logic were not changed.
- No progressive or multi-bracket state support was added.
- No deductions, exemptions, credits, Social Security treatment, LTCG/QD treatment, residency, sourcing, withholding, or local taxes were added.

## Validation

```text
python -m pytest -q tests/test_state_contract.py
6 passed

python -m pytest -q tests/test_state_tax.py
16 passed

python -m pytest -q
84 passed
```

## Recommended Next Phase

Phase 13 has not been selected. Keep future work narrow and isolated, such as adding one explicitly verified flat/no-tax state policy or improving state-policy rule versioning. Progressive and multi-bracket states remain deferred.