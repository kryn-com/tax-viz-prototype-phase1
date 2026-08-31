# Phase 38A Project Plan

## Status

Proposed preparatory detour before Phase 38 sliver analysis.

## Objective

Define the spreadsheet-based scenario validation bank and the validation workflow expectations without implementing the manual runner itself.

Phase 38A is intentionally narrow: it establishes the scenario-bank structure, required inputs, optional expected-answer columns, metadata/status columns, and the audit requirements that later drive the runner and rounding review. The manual summary runner, two-pass execution flow, and official-source rounding reproduction work are deferred to Phase 38B.

## Why this step exists

The repository already has a valid set of federal, NC planning, NIIT, and projected IRMAA contracts and a need for a deterministic, spreadsheet-driven regression workflow before sliver analysis begins. Phase 38A records the scenario-bank format and validation expectations so future implementation starts from a clear, approved contract instead of ad hoc spreadsheet work.

## In scope

- Spreadsheet-based scenario validation bank format.
- Required base inputs for each scenario row.
- Optional expected-answer columns for manual validation and audit review.
- Recommended metadata/status columns for case tracking.
- Validation workflow expectations for future manual comparisons.
- Audit preparation for federal and NC rounding behavior.
- Documentation of evidence requirements for later official-source tax-table and rounding review.
- Preserving the current architecture and result boundaries.

## Out of scope

- A manual summary runner implementation.
- Two-pass federal/NC execution logic.
- Federal or NC rounding implementation changes.
- New tax formulas.
- New engine interfaces or redesigned public result contracts.
- Streamlit or other consumer UI work.
- Combined totals or merged tax figures.
- Sliver analysis implementation.
- Official-source tax-table reproduction or rounding audit execution itself; those belong to Phase 38B.

## Required boundaries

1. Reuse existing engines and result contracts only.
2. Keep federal, NC planning, NIIT, and projected IRMAA visibly separate.
3. Do not merge totals into one combined tax figure.
4. Do not add a consumer UI layer.
5. Keep the audit work separate from the tax engines themselves.
6. Treat rounding behavior as an audit target first, not an automatic implementation change.
7. Preserve all existing public call paths, result contracts, and architectural boundaries.
8. Keep the manual runner implementation and official-source rounding audit in the follow-on Phase 38B.

## Current NC planning note

The current NC planning path still depends on `federal_agi` and `federal_taxable_social_security` inputs as part of the current NC planning contract. Phase 38A only documents that dependency and defines the expected spreadsheet contract around it; it does not implement the default derivation logic. The actual default-value derivation and two-pass runner behavior are intentionally deferred to Phase 38B.

Manual spreadsheet overrides remain available for audit or debug scenarios, but the default implementation belongs to the later runner. Phase 38A is not a tax-engine redesign; it is only a preparatory validation-bank and audit-definition step.

## Spreadsheet scenario/test-bank contract

The workbook should contain a single row per scenario, with a predictable column layout that can be loaded later by the manual runner.

### 1. Required input columns the user must supply

| Column name | Required | Purpose |
| --- | --- | --- |
| `case_id` | Yes | Stable unique key for the scenario row. |
| `scenario_name` | Yes | Human-readable label for review and reporting. |
| `tax_year` | Yes | Must remain `2026` for this prototype. |
| `state_code` | Yes | Example: `NC`. |
| `filing_status` | Yes | Federal filing status as supported by the current model. |
| `taxpayer_age` | Yes | Age input for planning context and validation. |
| `spouse_age` | Optional but required for MFJ | Required if the filing status is `married_filing_jointly`. |
| `ordinary_income` | Yes | Baseline ordinary income input. |
| `ltcg_qd_income` | Yes | Preferential income input. |
| `social_security_income` | Yes | Social Security income for the scenario. |
| `nontaxable_income` | Yes | Non-taxable income input used by the current contract. |
| `deduction_mode` | Yes | Federal deduction mode supported by the current rules. |
| `deduction_amount` | Yes | Explicit deduction value when applicable. |
| `net_nc_interest_dividend_adjustment` | Yes | NC planning adjustment input. |
| `bailey_exempt_pension_amount` | Optional | NC planning field when applicable. |
| `nc_deduction_mode` | Yes | NC deduction mode for the planning path. |
| `nc_itemized_deduction_amount` | Optional | Required when NC deduction mode is `itemized`. |
| `federal_agi` | Optional override/audit column | Optional manual override for NC planning; later default derivation belongs to Phase 38B. |
| `federal_taxable_social_security` | Optional override/audit column | Optional manual override for NC planning; later default derivation belongs to Phase 38B. |

### 2. Optional expected-result columns

These columns should be optional and are intended to support later manual validation and comparison work.

| Column name | Optional | Purpose |
| --- | --- | --- |
| `expected_federal_total_tax` | Yes | Manual expected total federal tax. |
| `expected_ordinary_tax` | Yes | Manual expected ordinary-income tax. |
| `expected_ltcg_qd_tax` | Yes | Manual expected LTCG/QD tax. |
| `expected_niit_tax` | Yes | Manual expected NIIT tax. |
| `expected_nc_tax` | Yes | Manual expected NC planning result value if supported by the case. |
| `expected_projected_irmaa_2028_premium` | Yes | Manual expected premium overlay estimate. |
| `expected_projected_irmaa_2028_surcharge` | Yes | Manual expected surcharge output. |
| `expected_status` | Yes | Reviewer-supplied pass/fail/needs-review classification. |
| `expected_notes` | Yes | Free-form notes for expected-result rationale. |

### 3. Recommended metadata / status columns

| Column name | Recommended | Purpose |
| --- | --- | --- |
| `status` | Yes | Draft, ready, reviewed, approved, skipped. |
| `owner` | Yes | Case owner or reviewer. |
| `reviewer` | Yes | Final reviewer for audit sign-off. |
| `source` | Yes | External calculator, prior run, manual estimate, or note. |
| `tags` | Yes | Example: `niit`, `nc`, `social_security`, `ira`, `rounding_audit`. |
| `last_run_date` | Yes | Last manual summary-run timestamp. |
| `validation_status` | Yes | Pass, fail, mismatch, not-run. |
| `notes` | Yes | Free-form context for the case. |
| `issue_id` | Optional | Links to a defect or review item. |

## Validation workflow expectations

This phase defines the expected validation process, not the implementation of the runner itself. The later sequence should be:

- define the spreadsheet contract,
- define expected-answer fields,
- call the existing engines through approved public paths,
- compare and review results,
- capture discrepancies and audit evidence,
- keep all outputs separate by domain.

## Rounding and audit preparation

Phase 38A should define the evidence requirements and audit targets for the later official-source review. This includes:

- exact federal rounding behavior,
- exact NC rounding behavior,
- whether the observed behavior is a product requirement or a presentation-only convention,
- whether values should be recorded in whole dollars or cents according to the current engine contracts.

The actual official-source tax-table and rounding reproduction work is deferred to Phase 38B. Phase 38A defines what must be audited and what evidence must be captured.

## Risks and constraints

- The spreadsheet may expose a real mismatch between the current NC planning contract and reviewer assumptions.
- The current NC planning path still depends on specific supplied values that later need default derivation in the runner.
- Rounding differences can look like tax-model defects when they are only presentation or conventional-rounding differences.
- Over-eager comparison logic could accidentally merge separate domains or create a fake combined total.
- If the bank becomes too broad, it may drift into app design or UI work.

## Smallest safe implementation sequence

1. Define the core spreadsheet inputs for the federal scenario row.
2. Define the optional override columns for audit/debug use, including `federal_agi` and `federal_taxable_social_security`.
3. Define the optional expected-answer columns and metadata/status columns.
4. Define the validation process and audit-evidence expectations.
5. Capture the later manual-runner and official-source rounding work as Phase 38B scope.
6. Stop before runner implementation, sliver analysis, or UI integration.

## Recommended next step

Proceed with Phase 38A first as the narrow scenario-bank and validation-contract preparation step. The implementation of the two-pass manual summary runner and the official-source rounding audit belong to Phase 38B, which should follow afterward and before any sliver-analysis work begins.
