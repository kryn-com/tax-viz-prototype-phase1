# Scenario Validation Runbook

## Purpose

Use this runbook to execute one curated federal tax scenario end-to-end, inspect its deterministic review artifacts, and independently compare the results with an external tax calculator.

This repository is an analytical and educational prototype. It is not tax-preparation, tax-filing, e-file, or legal-tax-advice software.

## Scope

This process validates the prototype's supported 2026 federal-tax behavior for one predefined scenario fixture.

Supported end-to-end filing statuses:

- `single`
- `married_filing_jointly`
- `head_of_household`

`married_filing_separately` is permanently unsupported by this prototype and is rejected by the federal orchestrator.

## Choose a Fixture

Curated fixtures live in:

```text
scenarios/cases/
```

Current examples include:

```text
high-income-niit.json
hoh-ordinary-only.json
mf-joint-ordinary-only.json
single-baseline.json
zero-income.json
```

To test a new case, copy an existing fixture and give it a unique `id`. Keep test-only or experimental fixtures out of the curated catalog unless they are reviewed and intentionally added.

## Fixture Structure

A fixture is a JSON object with:

- `schema_version`: currently `1`
- `id`: non-empty scenario identifier
- `description`: short explanation of the case
- `scenario`: validated `TaxScenarioInput` fields
- `expected`: optional numeric expected results

Example:

```json
{
  "schema_version": 1,
  "id": "example-single-ordinary-only",
  "description": "Single filer with ordinary income only",
  "scenario": {
    "tax_year": 2026,
    "state_code": "TX",
    "filing_status": "single",
    "ordinary_income": 60000.0,
    "ltcg_qd_income": 0.0,
    "social_security_income": 0.0,
    "nontaxable_income": 0.0,
    "deduction_mode": "standard",
    "deduction_amount": 0.0
  },
  "expected": {
    "ordinary_tax": 0.0,
    "ltcg_qd_tax": 0.0,
    "niit_tax": 0.0,
    "total_federal_tax": 0.0
  }
}
```

Only include expected values after independently determining them. The runner permits these expected result fields:

```text
agi
magi
taxable_ordinary_income
taxable_preferential_income
ordinary_tax
ltcg_qd_tax
niit_tax
total_federal_tax
```

Expected values are compared with an absolute tolerance of $0.01.

## Run One Scenario

From the repository root, run:

```powershell
python -m scripts.scenario_runner `
  --scenario .\scenarios\cases\single-baseline.json `
  --output-dir .\artifacts\manual-validation
```

Replace `single-baseline.json` with the fixture under review.

The command prints absolute paths for:

- `result.json`
- `tax_stack.svg`
- a `file:///` URL for opening the SVG locally

## Inspect Results

The runner writes artifacts to:

```text
artifacts/manual-validation/<scenario-id>/
```

Review `result.json` first. It includes:

- The validated input values
- AGI and MAGI
- Taxable ordinary and preferential income
- Ordinary-income tax, LTCG/QD tax, NIIT tax, and total federal tax
- Taxable and tax-free Social Security details
- NIIT inputs and calculated tax base
- Ordinary-income bracket layers
- Preferential-rate layers
- Optional expected-versus-actual comparison results

Open `tax_stack.svg` as a supporting explanation of the prototype's calculated tax layers. It is not an independent calculation and should not replace review of `result.json`.

## Compare Externally

When using another tax calculator, match the fixture inputs exactly:

- Tax year: 2026
- Filing status
- Ordinary income
- Combined LTCG/qualified-dividend income
- Social Security income
- Nontaxable income
- Standard or explicit deduction amount

Compare these outputs where the external calculator exposes comparable values:

1. Taxable Social Security
2. Taxable ordinary income
3. Ordinary-income tax
4. LTCG/QD tax
5. NIIT tax
6. Total federal income tax

Record differences with enough context to explain them. Do not treat a mismatch as a code defect until assumptions, income classification, deduction treatment, and unsupported calculator features have been reconciled.

## Prototype Boundaries

Do not use this process to validate items outside the current model, including:

- Tax credits
- AMT
- Payroll or self-employment tax
- Business-entity tax
- Complex capital-gain/loss netting
- State-income tax integration
- IRMAA or Medicare-premium determinations
- Tax return preparation, filing, or e-file behavior

## Run the Catalog

To run all reviewed fixtures and generate artifacts for each:

```powershell
python -m scripts.scenario_runner `
  --all `
  --scenario-dir .\scenarios\cases `
  --output-dir .\artifacts\manual-validation
```

A nonzero command result means at least one fixture's expected-value comparison failed.

## Before Committing a Fixture

For an intentionally added or changed curated fixture:

```powershell
python -m pytest .\tests\test_scenario_runner.py -q
python -m pytest -q
git status --short
```

Review the fixture, its expected values, and generated artifacts before committing. Keep the catalog deterministic and limited to reviewed cases.