# Phase 11 Handoff — First Numeric State-Tax Engine

## Status

Phase 11 is complete, committed, pushed, and clean.

## Objective

Add the first isolated numeric state-tax calculation using the typed state contract only.

## Files Changed

- `models/state.py`
- `rules/state_policy.py`
- `engines/state_tax.py`
- `tests/test_state_contract.py`
- `tests/test_state_tax.py`

## What Changed

### StateTaxRequest

`StateTaxRequest` now includes a required explicit field:

- `state_taxable_income: float`

This field is the complete taxable base for the current prototype state engine. It is not inferred from any federal input or output.

The request remains frozen.

Negative state taxable-income values are rejected clearly.

### StateTaxResult

`StateTaxResult` was preserved as the state-only output model.

### Numeric state engine

Added:

```python
compute_state_tax(
    request: StateTaxRequest,
) -> StateTaxResult
```

The engine is isolated from all federal engines, the federal orchestrator, the federal reconciler, and `StateTaxPlugin`.

## Current Supported Numeric State Behavior

### Pennsylvania

- Supported as a flat-tax state.
- Uses a 2026 flat rate of `0.0307`.
- Calculates:

```text
state_tax_amount = state_taxable_income × 0.0307
```

### Florida

- Supported as a no-individual-income-tax state.
- Returns `state_tax_amount = 0.0`.

### Texas

- Supported as a no-individual-income-tax state.
- Returns `state_tax_amount = 0.0`.

### Unsupported states

- Raise `UnsupportedStateError`.
- Are never silently treated as zero-tax.
- `NC` remains unsupported.

## Important Boundaries Preserved

- No federal/state integration.
- No changes to `TaxScenarioInput`.
- No changes to `FederalTaxResult`.
- No changes to `FederalTaxReconciliation`.
- No changes to federal formulas, thresholds, engines, or orchestrator behavior.
- No changes to `StateTaxPlugin`.
- No deductions, exemptions, credits, Social Security treatment, LTCG/QD treatment, residency, sourcing, local tax, or filing logic.
- No progressive or multi-bracket states.

## Tests

### `tests/test_state_contract.py`

Covers:

- required explicit taxable-income base
- frozen-model behavior
- support classification
- unsupported-state handling
- separation from federal models

### `tests/test_state_tax.py`

Covers:

- PA known-base calculation
- PA zero-base calculation
- FL zero-tax result
- TX zero-tax result
- NC unsupported-state rejection
- unknown-state rejection
- negative-base rejection
- result preservation
- deterministic repeated calculations

## Validation

```text
python -m pytest -q tests/test_state_contract.py
6 passed

python -m pytest -q tests/test_state_tax.py
9 passed

python -m pytest -q
77 passed
```

## Current State

The prototype now includes:

- federal orchestration
- three federal sliver-analysis paths
- federal reconciliation support
- a typed state-tax contract
- an initial isolated numeric state-tax engine for PA, FL, and TX only

## Phase 12

Phase 12 has not yet been implemented.

Future state-tax work remains limited initially to flat-tax states or no-individual-income-tax states. Progressive and multi-bracket states remain deferred.
