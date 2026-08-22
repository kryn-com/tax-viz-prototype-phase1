# Phase 29 Handoff — Curated Scenario Catalog Integration Coverage

## Status

Phase 29 is complete and pushed on branch `phase-2-social-security`.

This phase added one repository-level integration test for the curated scenario catalog. No federal tax rules, scenario fixtures, runner behavior, rendering, or other production code changed.

The working tree was clean after commit and push.

## Completed Work

Added a test to `tests/test_scenario_runner.py` that invokes `run_all_scenarios()` against `scenarios/cases` and verifies:

- The discovered and executed scenario IDs are stable and filename ordered:
  - `high-income-niit`
  - `hoh-ordinary-only`
  - `mf-joint-ordinary-only`
  - `single-baseline`
  - `zero-income`
- Every curated scenario returns a `passed` status.

This test provides catalog-level coverage in addition to the existing per-fixture and scenario-runner tests. The runner executes JSON scenario fixtures in stable filename order and writes deterministic result and SVG artifacts for each scenario.

## Validation

Completed validations:

```powershell
python -m pytest .\tests\test_scenario_runner.py -q
python -m pytest -q
```

Results:

```text
8 passed in 0.19s
169 passed in 0.39s
```

## Commit and Push

Committed and pushed:

```text
6bdd7a6 test: cover full scenario catalog
```

Remote tracking is configured:

```text
phase-2-social-security -> origin/phase-2-social-security
```

## Preserved Decisions

- The 2026 ordinary-income bracket audit for Single, MFJ, and HOH remains complete as documented in `PHASE_28_HANDOFF.md`.
- MFS remains permanently out of scope; the orchestrator must continue to reject it.
- No changes were made to Social Security, LTCG/QD, NIIT, deductions, tax-stack rendering, display models, state-tax behavior, CLI behavior, or scenario-runner production code.

## Deferred Backlog

Do not implement without separate written approval:

1. Add further MFJ and HOH ordinary-income boundary tests at additional bracket transitions.
2. Consider documentation-only treatment of inactive MFS rule-table data, while preserving MFS rejection.
3. Audit another 2026 tax-rule domain only with authoritative sourcing and a narrowly approved objective.
4. Revisit deduction visualization semantics only as a presentation/design phase.
5. Define future visualization or modeling enhancements as separately approved phases.

## Recommended Next Session

Begin by reading:

- `PROJECT_SCOPE.md`
- `PHASE_29_HANDOFF.md`
- only files directly relevant to one newly approved objective

No next implementation phase is selected or approved by this handoff.