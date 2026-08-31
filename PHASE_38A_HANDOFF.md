# Phase 38A Handoff — Scenario Validation-Bank Contract

## Status

Completed.

- Branch: `phase-2-social-security`
- Final implementation commit: `8e8aeef` — `test: add phase 38A sample bank CSV contract`
- Phase 38A commits:
  - `af09f48` — `test: freeze phase 38A scenario bank column contract`
  - `cd262f3` — `test: document phase 38A deferred validation boundary`
  - `24a5e0b` — `test: define phase 38A audit evidence metadata`
  - `8e8aeef` — `test: add phase 38A sample bank CSV contract`
- Verification:
  - `python -m pytest tests/test_scenario_runner.py -q`
  - `python -m pytest -q`
- Result:
  - Focused suite: 15 passed
  - Full suite: 230 passed

## Objective completed

Phase 38A completed the narrow preparation step for an editable spreadsheet-based scenario validation bank.

It freezes the approved scenario-bank column groups and ordered CSV header, defines optional override, expected-answer, and audit-evidence fields, and adds one tracked sample CSV fixture. It does not implement any spreadsheet loader, row parser, comparison runner, two-pass federal/NC flow, or rounding behavior.

## What changed

- Updated `tests/test_scenario_runner.py`.
- Added `tests/fixtures/phase38a_sample_bank.csv`.
- Added a contract-only test for the ordered 37-column CSV header and one-row shape.
- Preserved blank optional cells in the sample fixture, including optional NC override/audit and expected-answer fields.
- Defined the Phase 38A contract around:
  - required base scenario inputs,
  - optional conditional and NC override/audit fields,
  - optional expected-answer fields,
  - recommended status, reviewer, source, tag, run-date, validation, note, and issue metadata.

## Tests added or updated

`tests/test_scenario_runner.py` now contains Phase 38A contract coverage for:

- Approved scenario-bank column groups.
- Explicitly deferred runner, parser, and two-pass behavior.
- Audit-evidence metadata fields.
- `test_phase_38a_csv_sample_bank_header_and_row_contract`, which checks:
  - the exact ordered 37-column CSV header,
  - exactly one sample data row,
  - a data-row width matching the header width.

## Preserved boundaries

- No production code was changed.
- No spreadsheet loader, CSV parser, blank-string normalization, or manual summary runner was added.
- No two-pass federal/NC derivation behavior was added.
- No federal, NC planning, NIIT, or projected IRMAA formulas or public interfaces were changed.
- No rounding or tax-table behavior was changed.
- No federal, NC planning, NIIT, or projected IRMAA values were merged into a combined total.
- No Streamlit, consumer UI, sliver analysis, or orchestration work was added.
- Federal tax, NC planning, NIIT, and projected IRMAA remain separate domains and result boundaries.

## Workspace note

The following local sample file remains intentionally untracked and was not staged, modified, or committed during Phase 38A:

`scripts/sample_inputs/ss40k_ord20k_ltcg10k_single.json`

## Recommended next decision

Phase 38B is the recommended next approved implementation phase only if explicitly authorized.

Phase 38B would use the Phase 38A contract to implement the two-pass manual summary runner, expected-versus-actual comparisons, clear derived-versus-override NC input disclosure, and the official-source federal/NC rounding and tax-table audit. It must preserve the existing public interfaces and keep federal, NC planning, NIIT, and projected IRMAA outputs separate.