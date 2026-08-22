# Phase 28 Handoff — 2026 MFJ and HOH Bracket Audit, Tests, and Fixtures

## Status

The 2026 ordinary-income bracket audit is complete for the filing statuses supported by this prototype:

- `FilingStatus.SINGLE`
- `FilingStatus.MARRIED_FILING_JOINTLY`
- `FilingStatus.HEAD_OF_HOUSEHOLD`

The working tree was clean after the completed commits and pushes on branch `phase-2-social-security`.

`MARRIED_FILING_SEPARATELY` is permanently out of scope for this project. The federal orchestrator must continue to reject MFS, and no MFS rule, test, fixture, or scenario-runner support work is approved.

## Completed Work

### Single filer

Phase 27 corrected and validated 2026 single-filer ordinary-income brackets.

For `scenarios/cases/single-baseline.json`:

- Ordinary tax: $9,980
- LTCG/QD tax: $3,000
- NIIT tax: $0
- Total federal tax: $12,980

The scenario passes with:

```powershell
python -m scripts.scenario_runner --scenario .\scenarios\cases\single-baseline.json
```

### MFJ and HOH brackets

The subsequent audit corrected the 2026 ordinary-income brackets in `rules/federal/year_2026.py` for:

- `MARRIED_FILING_JOINTLY`
- `HEAD_OF_HOUSEHOLD`

The correction was based on authoritative 2026 IRS inflation-adjustment material, including Revenue Procedure 2025-32.

Validated bracket starts:

| Filing status | 10% | 12% | 22% | 24% | 32% | 35% | 37% |
|---|---:|---:|---:|---:|---:|---:|---:|
| Married Filing Jointly | $0 | $24,800 | $100,800 | $211,400 | $403,550 | $512,450 | $768,700 |
| Head of Household | $0 | $17,700 | $67,450 | $105,700 | $201,775 | $256,200 | $640,600 |

The 2026 standard deductions remain:

- Single: $16,100
- Married Filing Jointly: $32,200
- Head of Household: $24,150

## Test and Fixture Coverage

Focused ordinary-tax coverage now includes:

- Corrected single-filer multi-bracket and first-threshold tests.
- MFJ representative-income and exact first-threshold tests.
- HOH representative-income and exact first-threshold tests.

The scenario fixtures now include assertion-backed ordinary-only cases:

- `scenarios/cases/mf-joint-ordinary-only.json`
  - Taxable ordinary income: $87,800
  - Ordinary tax and total federal tax: $10,040
  - LTCG/QD tax: $0
  - NIIT tax: $0

- `scenarios/cases/hoh-ordinary-only.json`
  - Taxable ordinary income: $95,850
  - Ordinary tax and total federal tax: $13,988
  - LTCG/QD tax: $0
  - NIIT tax: $0

## Validation

Completed validations:

```powershell
python -m pytest .\tests\test_engines.py -q
python -m pytest .\tests\test_federal_orchestrator.py -q
python -m pytest .\tests\test_scenario_runner.py -q
python -m scripts.scenario_runner --scenario .\scenarios\cases\single-baseline.json
python -m scripts.scenario_runner --scenario .\scenarios\cases\mf-joint-ordinary-only.json
python -m scripts.scenario_runner --scenario .\scenarios\cases\hoh-ordinary-only.json
python -m pytest -q
```

Final full-suite result:

```text
164 passed
```

## Preserved Boundaries

No changes were made to:

- UI, SVG rendering, display models, or chart behavior
- Social Security logic
- LTCG/QD logic
- NIIT logic
- Deduction design
- API or scenario-runner architecture
- State-tax logic
- MFS orchestration behavior

## Deferred Backlog

Do not implement these items without separate written approval:

1. Add MFJ and HOH boundary tests at additional transitions, especially 12%/22% and 22%/24%.
2. Decide whether inactive MFS bracket data should be removed or explicitly documented as intentionally inactive, without changing orchestrator rejection.
3. Audit other tax-rule domains only if separately scoped and supported by authoritative sources.
4. Revisit deduction visualization semantics as a presentation/design issue, not as a tax-calculation defect.
5. Collect additional potential corrections and enhancements in a prioritized backlog without combining them with rule changes.

## Recommended Next Session

Begin by reading:

- `PROJECT_SCOPE.md`
- `PHASE_28_HANDOFF.md`
- only the files directly relevant to one newly approved objective

A suitable next objective is either:

- additional MFJ/HOH ordinary-bracket boundary-test expansion, or
- a documentation-only review of inactive MFS rule-table handling.

Do not begin either objective without explicit approval.