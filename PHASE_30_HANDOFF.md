# Phase 30 Handoff — Tax-Core Closeout and UI/UX Preparation

## Status

Phase 30 is complete and pushed to GitHub.

This was a documentation-only closeout phase. No tax calculations, rule values, engine interfaces, fixtures, presentation models, SVG rendering, or automated tests were changed.

## Final Tax-Core State

The prototype’s validated 2026 federal ordinary-income coverage now includes:

- `SINGLE`
- `MARRIED_FILING_JOINTLY`
- `HEAD_OF_HOUSEHOLD`

The 2026 ordinary-income bracket values for those supported filing statuses were audited and corrected in earlier phases. Boundary and representative-income tests cover their supported rate transitions.

`MARRIED_FILING_SEPARATELY` remains permanently unsupported by the federal orchestrator. Its bracket-table entry remains executable data for compatibility, but it is explicitly marked inactive and must not be treated as supported scenario behavior.

## Scenario Validation Workflow

The curated scenario runner supports an end-to-end review path:

```text
JSON fixture -> validated TaxScenarioInput -> federal orchestrator -> deterministic result.json + tax_stack.svg
```

Use `SCENARIO_VALIDATION_RUNBOOK.md` to run one curated fixture, inspect its deterministic outputs, and compare comparable federal-tax values with an external calculator.

Generated scenario artifacts are review outputs only. Keep them untracked and do not commit them unless a later approved phase explicitly changes artifact-management policy.

## Validation Baseline

Latest completed validation:

```text
python -m pytest .\tests\test_scenario_runner.py -q
8 passed

python -m pytest -q
169 passed
```

The manual scenario-runner check also passed for `scenarios/cases/single-baseline.json`, producing `result.json` and `tax_stack.svg` in a temporary output directory.

## Documentation Updated

- `PROJECT_SCOPE.md` now describes completed phases through Phase 30 and the current 169-test baseline.
- `SCENARIO_VALIDATION_RUNBOOK.md` documents independent end-to-end fixture validation.
- `rules/federal/year_2026.py` includes the inactive-MFS clarification comment.

## Next Session

The next phase is not approved by this handoff.

The likely next activity is a separately approved UI/UX planning phase. It should begin with a narrow written proposal, not immediate implementation.

Before proposing UI/UX work, read:

1. `PROJECT_SCOPE.md`
2. This `PHASE_30_HANDOFF.md`
3. `SCENARIO_VALIDATION_RUNBOOK.md`
4. The relevant presentation-model and SVG-rendering files

## UI/UX Guardrails

Any future UI/UX phase must preserve these boundaries:

- Do not alter federal tax formulas, 2026 rule tables, or supported-filing-status policy without a separately approved tax-core phase.
- Keep federal tax calculation separate from presentation.
- Preserve deterministic, immutable presentation/view-model behavior.
- Keep state tax separate from federal tax.
- Keep IRMAA separate as a future Medicare-surcharge overlay, not federal income tax.
- Do not introduce tax-preparation, filing, e-file, legal-advice, or interactive user-input behavior without explicit scope approval.
- Treat the existing JSON scenario runner and its artifacts as a validation harness, not as a user-facing application.

## Git State

At handoff, the branch should contain the Phase 30 documentation reconciliation commit, be pushed to `origin/phase-2-social-security`, and have a clean working tree.