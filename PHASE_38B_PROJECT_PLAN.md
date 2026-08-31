# Phase 38B Project Plan - Two-Pass Manual Summary Runner and Rounding Audit

## Status

Follow-on implementation phase after Phase 38A.

## Objective

Implement the larger two-pass manual summary runner and the official-source rounding audit needed to validate spreadsheet scenarios against the current federal, NC planning, NIIT, and projected IRMAA contracts without redesigning the tax engine or merging result domains.

This phase continues the approved validation work by turning the Phase 38A specification into a practical manual runner. It also performs the official-source evidence review for federal and NC rounding and tax-table behavior before any formula or rounding change is approved.

## Why this follow-on phase exists

Phase 38A defines the scenario bank, expected-answer structure, and audit requirements. Phase 38B is the first implementation pass that uses those definitions to execute the validation workflow. It creates the runner that reuses the current engines and result contracts while disclosing when NC inputs are derived or manually overridden.

## In scope

- Two-pass manual summary runner.
- Pass 1: run the federal path from the spreadsheet's core scenario inputs.
- Pass 2: derive default NC planning inputs from the federal result and then run the NC planning path with NC-specific spreadsheet values.
- Optional override/audit columns for `federal_agi` and `federal_taxable_social_security`.
- Human-readable per-case summary output.
- Expected-vs-actual comparison output for each case.
- Official-source audit of federal tax tables and rounding behavior.
- Official-source audit of NC rounding and tax computation instructions.
- Preserving separate federal, NC, NIIT, and projected IRMAA outputs.
- Clear summary labeling of NC inputs as either derived from pass 1 or manually overridden.

## Out of scope

- Tax-engine redesign.
- Combined totals or merged federal+NC+IRMAA figures.
- New tax formulas.
- New engine interfaces or result contract redesign.
- Streamlit or any consumer UI work.
- Sliver analysis implementation.
- Any automatic formula change unless the audit proves a defect.

## Required boundaries

1. Reuse existing engines and result contracts only.
2. Keep federal, NC planning, NIIT, and projected IRMAA visibly separate.
3. Do not merge totals into one combined tax figure.
4. Do not add a consumer UI layer.
5. Keep the audit work separate from the tax engines themselves.
6. Treat rounding behavior as an audit target first, not an automatic implementation change.
7. Preserve the current public call paths and architectural boundaries.
8. No formula or rounding implementation change is approved unless the official-source audit proves a defect.

## Two-pass workflow

The default two-pass flow is:

1. Run federal from the spreadsheet's core scenario inputs.
2. Derive default NC inputs from the federal result when no manual override is present.
3. Run NC planning with the derived default NC values plus NC-specific spreadsheet inputs.
4. Keep the result section separate for federal, NC planning, NIIT, and projected IRMAA.
5. Compare the actual values with any optional expected-answer columns.

This is a validation-runner composition convenience only. It does not merge federal and NC tax logic, does not redesign the NC engine contract, and does not create a combined total contract.

## Current NC planning note

The current NC planning path still depends on `federal_agi` and `federal_taxable_social_security` inputs. Phase 38B should use the federal pass-1 result as the default source for those values when the spreadsheet does not supply an override. This preserves the current NC contract while allowing the validation runner to execute the existing NC path without requiring manual entry of those federal-derived values.

The runner should disclose whether the NC values were:

- derived from the federal pass-1 result, or
- supplied as a manual override.

Manual spreadsheet overrides remain available for audit and debug scenarios when a reviewer intentionally compares the NC path against a custom value.

## Spreadsheet contract dependencies from Phase 38A

Phase 38B depends on the Phase 38A spreadsheet contract, including:

- required base scenario inputs,
- optional expected-answer columns,
- metadata/status columns,
- override/audit columns for `federal_agi` and `federal_taxable_social_security`,
- the validation workflow expectations and evidence requirements.

Phase 38A defines the contract; Phase 38B implements the actual runner and comparisons based on that contract.

## Optional override/audit columns

The following columns should remain optional and deliberately audit-focused:

| Column name | Required | Purpose |
| --- | --- | --- |
| `federal_agi` | Optional override/audit column | Manual override for NC planning; default is derived from the federal pass-1 result. |
| `federal_taxable_social_security` | Optional override/audit column | Manual override for NC planning; default is derived from the federal pass-1 result. |

These columns are not universally required base inputs for the validation runner. They are optional override values for controlled comparison or debugging scenarios.

## Manual summary output requirements

The summary output for each case should be human-readable and should include:

- case header and metadata,
- core scenario inputs,
- federal summary,
- NC planning summary,
- NIIT summary,
- projected IRMAA summary,
- expected-vs-actual comparison,
- NC input source note (`derived from federal pass 1` or `manual override`),
- any rounding or audit notes.

The output must preserve domain separation and must not imply a combined tax result.

## Official-source rounding / tax-table audit scope

This phase should perform the official-source evidence review required before any rounding or tax-table change is approved. The audit scope includes:

- 2026 IRS tax table below the published cutoff,
- 2026 IRS worksheet/rate-schedule method at and above the cutoff,
- 2026 NC tax computation and rounding instructions,
- verification that any observed difference is a real defect and not a presentation or conventional-rounding issue.

Required evidence should include the source reference, the calculation method used, and whether the observed result matches the official method or indicates a defect. No formula or rounding implementation change is approved unless the audit proves a defect.

## Validation approach

- Validate each spreadsheet row against the Phase 38A contract.
- Reuse the existing federal and NC planning engine calls without duplicating formulas.
- Keep US federal, NC planning, NIIT, and projected IRMAA outputs separate in the summary.
- Capture expected-vs-actual mismatches and document whether they are caused by:
  - scenario data,
  - model interpretation,
  - rounding difference,
  - unsupported filing status,
  - or a real formula defect.
- Require official-source evidence before any tax or rounding logic change is proposed.

## Risks and constraints

- The manual spreadsheet flow may expose differences between assumptions and the current NC planning contract.
- The default NC derivation can mask a real contract mismatch if the summary does not clearly disclose the source of the NC inputs.
- Rounding differences can look like tax defects when they are only conventional or presentation issues.
- Over-eager comparison logic could accidentally merge separate domains or create a fake combined total.
- If the runner becomes too broad, it may drift into app design or UI work.

## Smallest safe implementation sequence

1. Define the Phase 38A spreadsheet contract and expected-answer fields.
2. Implement the two-pass manual summary runner.
3. Run federal pass 1 from the core spreadsheet inputs.
4. Derive default NC inputs from the federal pass-1 result when no override is supplied.
5. Run NC planning pass 2 with derived values and NC-specific inputs.
6. Render human-readable summaries and expected-vs-actual comparisons.
7. Perform official-source federal and NC rounding/tax-table audit review.
8. Stop before sliver analysis or UI integration.

## Recommended next step

Proceed with Phase 38B after Phase 38A and before sliver analysis. This is the implementation phase that turns the validated spreadsheet contract into a two-pass manual summary runner and an official-source rounding audit without redesigning the tax engine or folding results into a combined total.

## Phase 38B closeout note

Phase 38B is now implemented as a validated spreadsheet-driven two-pass manual runner/reporting path. The runner supports expected-vs-actual comparisons for the currently supported fields, and the official-source federal + NC audit artifact documents current behavior and mismatch classification without changing formulas or rounding logic. NIIT and projected IRMAA remain intentionally deferred unless they are added later through the existing public execution paths; no formula or rounding changes were made as part of this audit.
