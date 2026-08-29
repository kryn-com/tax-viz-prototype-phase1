# Phase 32A Handoff — Age-Aware Scenario Input Validation Only

## Status

Phase 32A is complete and pushed to GitHub.

Commit: `dbe65c5`
Branch: `phase-2-social-security`

This phase was intentionally limited to scenario-contract validation. It added age-aware required scenario metadata without changing federal tax calculations, state-tax behavior, or presentation outputs.

## Objective

Keep the phase narrow and validation-only:

- make `taxpayer_age` a required validated scenario input,
- require `spouse_age` when `filing_status` is `married_filing_jointly`,
- allow `spouse_age` to remain optional for all other filing statuses,
- update curated scenario fixtures and direct `TaxScenarioInput` constructors to satisfy the new contract,
- preserve all existing tax logic and boundary constraints.

No federal formula changes, state-tax logic changes, presentation/SVG changes, or IRMAA work were introduced.

## Production Changes

### Age-aware input validation

`models/inputs.py` now enforces the following scenario contract:

- `taxpayer_age` is required and must be an integer within 0..120,
- `spouse_age` is required for `FilingStatus.MARRIED_FILING_JOINTLY`,
- `spouse_age` remains optional for non-MFJ filing statuses,
- age validation is separate from any tax calculation and does not infer or apply age-based deductions.

### Scenario and test contract alignment

Curated scenario JSON fixtures under `scenarios/cases` and direct `TaxScenarioInput` constructors in tests and example usage were mechanically updated to satisfy the validation contract.

This kept the repository consistent with the approved scenario-validation boundary without modifying taxes, outputs, or display behavior.

## Durable Design Note

Ages were added because later approved tax-rule phases may use them for verified age-based additional standard deductions or other age-dependent deductions.

Phase 32A does not calculate, apply, infer, or display any age-based deduction yet. It only secures the scenario input contract needed for future age-dependent rule work.

## Validation

Final repository validation:

```text
python -m pytest -q
179 passed
```

## Preserved Boundaries

This phase preserved all key architectural boundaries:

- no federal formula changes,
- no NC/state-tax logic changes,
- no presentation/SVG changes,
- no IRMAA changes.

The scenario validation layer remains separate from the tax calculation engines and from state and presentation layers.

## Next Session

No broader tax-rule implementation is approved by this handoff.

The next likely phase is a narrow North Carolina rule-selection/design pass using a redacted 2025 return as a practical reference. That work should begin with a focused proposal and should remain deliberately limited to state-rule design and selection, not to tax-engine changes or presentation work.
