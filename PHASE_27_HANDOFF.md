# Phase 27 Handoff — Standard Deduction and 2026 Single-Bracket Correction

## Status

Phase 27 is partially complete and pushed to GitHub.

A standard-deduction application issue was corrected, and the 2026 federal ordinary-income brackets were corrected and validated for `FilingStatus.SINGLE` only.

## Changes Made

- Preserved the broader Copilot-generated working state in commit:
  - `37e1eaa WIP freeze before manual 2026 bracket audit`
- Corrected `FilingStatus.SINGLE` ordinary-income bracket thresholds in:
  - `rules/federal/year_2026.py`
- Updated the `single-baseline` scenario expected values in:
  - `scenarios/cases/single-baseline.json`

## Single-Filer Rule Correction

The corrected 2026 single ordinary-income bracket thresholds are:

- 10%: $0 to $12,400
- 12%: $12,400 to $50,400
- 22%: $50,400 to $105,700
- 24%: $105,700 to $201,775
- 32%: $201,775 to $256,225
- 35%: $256,225 to $640,600
- 37%: over $640,600

The standard deduction for single filers remains $16,100.

## Baseline Validation

For `scenarios/cases/single-baseline.json`:

- Taxable ordinary income: $69,400
- 10% layer: $12,400, tax $1,240
- 12% layer: $38,000, tax $4,560
- 22% layer: $19,000, tax $4,180
- Ordinary tax: $9,980
- LTCG/QD tax: $3,000
- NIIT tax: $0
- Total federal tax: $12,980

The scenario runner passed when invoked as:

```powershell
python -m scripts.scenario_runner --scenario .\scenarios\cases\single-baseline.json
```

The single-filer tax result was also manually cross-checked against another tax engine.

## Important Limitation

Only `FilingStatus.SINGLE` brackets were corrected and validated.

Do not assume that bracket thresholds for:

- `MARRIED_FILING_JOINTLY`
- `MARRIED_FILING_SEPARATELY`
- `HEAD_OF_HOUSEHOLD`

are correct. The existing `year_2026.py` comments indicate the bracket table was originally provisional/extrapolated, and those statuses require a separate source-based audit and dedicated tests.

## Commit History

- `37e1eaa WIP freeze before manual 2026 bracket audit`
- Follow-up commit: corrected 2026 single federal brackets and `single-baseline` expectation

Both commits were pushed to `phase-2-social-security`.

## Visual Notes

The tax-stack rendering now reflects the corrected single-filer bracket layer amounts and produces a coherent baseline total.

The deduction section remains a conceptual “Deduction relief” zone rather than an allocated reduction of a specific tax layer. Treat that as a future visualization/design enhancement, not as evidence of a remaining single-filer calculation error.

## Recommended Next Session

The next session should be a bounded 2026 rule-audit and test-expansion phase:

1. Audit all non-single 2026 ordinary-income bracket thresholds against authoritative sources.
2. Decide whether `MARRIED_FILING_SEPARATELY` should remain explicitly rejected or receive only rule-table correction without orchestrator support.
3. Add focused boundary and representative-income tests for every supported filing status.
4. Add scenario fixtures for MFJ and HOH after their rules are verified.
5. Run focused tests first, then the full suite before each commit.
6. Collect, but do not implement, a prioritized backlog of visualization and modeling enhancements.
7. Do not change visual rendering, Social Security logic, LTCG/QD logic, NIIT logic, or deduction design unless separately approved.

Copilot should not be assumed available for the next session. Use a deliberate manual workflow: inspect, source-check, write tests, make one narrow edit, validate, commit, and push.