# Phase 31 Handoff — Deduction Floor and Preferential Stacking Consistency

## Status

Phase 31 is complete and pushed to GitHub.

This phase corrected two tax-core consistency issues:
1. explicit deductions below the filing-status standard deduction are now floored to the standard deduction, and
2. LTCG/QD preferential stacking now uses taxable ordinary income after the resolved applied deduction rather than the raw input deduction amount.

## Objective

Keep the phase narrow and tax-core only:

- enforce the deduction floor at the ordinary-tax boundary even when `deduction_mode` is explicit,
- make ordinary-income taxation and LTCG/QD stacking use the same resolved deduction,
- add focused regression tests for the corrected behavior,
- reconcile the scenario-runner catalog assertion with the current curated case set.

No presentation architecture, SVG rendering, state tax, IRMAA, or user-input behavior was changed.

## Production Changes

### Deduction resolution

`engines/deductions.py` now resolves the applied deduction as follows:

- `DeductionMode.STANDARD` returns the 2026 standard deduction for the filing status.
- `DeductionMode.EXPLICIT` returns the greater of the supplied explicit deduction amount and the filing-status standard deduction.

This preserves explicit deductions only when they exceed the standard deduction and prevents below-standard explicit deductions from understating the applied deduction.

### Preferential stacking

`engines/ltcg_qd.py` now resolves the applied deduction before computing the ordinary-income base used for LTCG/QD stacking.

As a result, the preferential engine now uses the same deduction-aware taxable ordinary income concept already used by the ordinary-income engine, eliminating an internal inconsistency where LTCG/QD calculations had previously used `scenario.deduction_amount` directly.

## Tests Updated

Focused tests were updated to reflect the corrected policy:

- `tests/test_engines.py`
  - rewrote threshold and bracket-boundary tests so taxable-income targets are reached intentionally under standard-deduction behavior,
  - replaced the old “non-standard deduction remains unchanged” assumption with:
    - explicit deduction below standard is floored to standard,
    - explicit deduction above standard remains unchanged.
- `tests/test_federal_orchestrator.py`
  - updated the deduction-after-taxable-social-security assertion to expect the applied deduction floor.
- `tests/test_ltcg_qd.py`
  - updated preferential-band expectations to reflect deduction-aware taxable ordinary income,
  - added/updated direct coverage showing the deduction floor can expand remaining 0% LTCG/QD capacity.
- `tests/test_tax_stack_data.py`
  - updated deduction shielding expectations to reflect the applied deduction, not merely the raw requested explicit amount.
- `tests/test_scenario_runner.py`
  - updated the catalog assertion from the stale 15-case list to the current 25 curated scenario IDs.

## Scenario Catalog

This phase also added the currently reviewed curated scenario fixtures required by the updated runner-catalog assertion:

- `scenarios/cases/hoh-1000k-190k-ltcg-explicit-40k.json`
- `scenarios/cases/hoh-188k-001k-ltcg-010k-ss-standard.json`
- `scenarios/cases/mfj-055k-055k-ltcg-explicit-30k.json`
- `scenarios/cases/mfj-075k-009k-ltcg-023k-ss-standard.json`
- `scenarios/cases/mfj-1285k-158k-ltcg-standard.json`
- `scenarios/cases/mfj-128k-012k-ltcg-standard.json`
- `scenarios/cases/mfj-385k-068k-ltcg-021k-ss-explicit-39k.json`
- `scenarios/cases/single-080k-020k-ltcg-030k-ss-explicit-20k.json`
- `scenarios/cases/single-110k-040k-ss-explicit-40k.json`
- `scenarios/cases/single-280k-030k-ltcg-standard.json`

Generated artifact folders remain untracked review outputs and were not committed.

## Validation

Focused validation completed during the phase:

```text
python -m pytest -q tests/test_engines.py
17 passed

python -m pytest -q tests/test_ltcg_qd.py
7 passed

python -m pytest -q tests/test_scenario_runner.py
8 passed
```

Final repository validation:

```text
python -m pytest -q
170 passed
```

## Preserved Boundaries

This phase preserved all existing architectural boundaries:

- no changes to Social Security taxability formulas,
- no changes to NIIT logic,
- no state-tax changes,
- no presentation/SVG contract redesign,
- no user-input or app-shell work,
- no MFS support expansion.

Federal tax logic remains separate from presentation, state tax, and future IRMAA work.

## Next Session

No future phase is approved by this handoff.

Before proposing the next phase, read:

1. `PROJECT_SCOPE.md`
2. This `PHASE_31_HANDOFF.md`
3. `SCENARIO_VALIDATION_RUNBOOK.md`
4. the relevant engine, scenario-runner, and presentation files

Likely future work should begin with a narrow written proposal and should not reopen this phase’s tax-core rules unless a new, explicit defect is identified.