\# Phase 38B Handoff



\## Status



Completed: two-pass manual scenario-bank runner and audit-reporting framework.



Commit: `eab7c78` — `Implement Phase 38B two-pass runner audit path fix`



Verification:



\- `pytest tests/test\_scenario\_runner.py -q` — 54 passed

\- `pytest -q` — 269 passed



\## Implemented



\- Added CSV scenario-bank execution using the approved Phase 38A row contract.

\- Added a two-pass workflow: federal calculation first, followed by NC planning calculation.

\- Defaulted NC `federal\_agi` and `federal\_taxable\_social\_security` from the federal pass.

\- Preserved CSV values in those fields as manual NC overrides when supplied.

\- Added human-readable per-case summaries.

\- Added expected-versus-actual comparisons for populated expected-result cells.

\- Added an audit-reporting entry point with a default Phase 38A sample-bank fixture path.

\- Added `phase38b\_manual\_review.csv` as a manual-review scenario-bank artifact.



\## Result Boundaries



\- Federal income-tax outputs remain separate from NC planning-tax outputs.

\- NIIT remains a separate federal tax component.

\- Projected IRMAA premium and surcharge remain separate planning overlays, not tax.

\- The runner must not create a combined federal, NC, NIIT, or IRMAA total.



\## Rounding Research Still Required



The implemented audit report records observed results but is not yet completed official-source rounding research.



Before changing any federal or NC formula or rounding behavior:



1\. Document the official source and tax year.

2\. Record whether the official method uses a tax table, rate schedule, worksheet, whole dollars, or cents.

3\. Run a representative scenario through the model.

4\. Record the official expected result, model result, and difference.

5\. Classify the result as `matches\_official\_source`, `rounding\_presentation\_difference`, or `potential\_formula\_defect`.

6\. Propose a code change only when evidence supports a real defect.



Required review areas:



\- 2026 IRS tax-table behavior below the published cutoff

\- 2026 IRS rate-schedule or worksheet behavior at and above the cutoff

\- 2026 North Carolina income-tax calculation and rounding instructions

### Provisional 2026 IRS Tax-Table Policy

Official 2026 statutory amounts, including filing-status deduction amounts and ordinary-income marginal-rate thresholds, are used by the prototype.

The official printed 2026 Form 1040 Tax Table is not yet available. Until it is published, the project adopts the following provisional tax-table reproduction policy for independent validation of printed-table results for taxable income below 100,000; the current federal engine remains an exact-calculation planning model unless a separately approved phase adds a tax-table calculation mode.

1. Map exact taxable income to the applicable IRS-style “at least / but less than” tax-table interval.
2. Use the midpoint of that interval:
   - 0 for taxable income below 5
   - 10 for 5 through less than 15
   - 20 for 15 through less than 25
   - 25-dollar intervals with a 12.50 midpoint for 25 through less than 3,000
   - 50-dollar intervals with a 25.00 midpoint for 3,000 through less than 100,000
3. Apply the official 2026 statutory marginal-rate schedule for the supported filing status to the midpoint.
4. Round the resulting tax to the nearest whole dollar using half-up rounding.
5. Use the exact taxable income and the official rate-schedule or worksheet method at 100,000 or above.

This is a project-controlled provisional reproduction method derived from separate tax-table research. It is not a claim that the unpublished 2026 IRS printed table has already been independently verified.

When the official 2026 IRS Tax Table is available, validate representative rows across the below-3,000 and 3,000-through-less-than-100,000 ranges. Record any difference and revise the policy or implementation only if the official material requires it.

### Recorded NC Baseline Review

- Source: NCDOR documentation states that the 2026 individual income-tax rate is 3.99%; NCDOR individual return instructions direct taxpayers to round entries to the nearest whole dollar.
- Scenario: `single_case_001` in `phase38b_manual_review.csv`.
- Model inputs: single filer, 2026, NC, ordinary income 60,000, standard deductions.
- Model result: NC taxable income 47,250.00; pre-credit NC planning tax 1,885.27.
- Rate check: 47,250.00 × 3.99% = 1,885.275.
- Whole-dollar return presentation: 1,885.
- Classification: `rounding_presentation_difference`.
- Decision: No formula or rounding-code change. The runner’s cents-level pre-credit planning output is retained and remains separate from a whole-dollar tax-return presentation convention.

### Recorded Federal Baseline Review

- Source: IRS 2026 inflation-adjustment guidance and 2026 federal ordinary-income rate schedule.
- Scenario: `single_case_001` in `phase38b_manual_review.csv`.
- Model inputs: single filer, 2026, AGI 60,000.00, standard deduction.
- Model taxable ordinary income: 43,900.00.
- Standard-deduction check: 60,000.00 - 16,100.00 = 43,900.00.
- Rate-schedule check: 1,240.00 + 12% × (43,900.00 - 12,400.00) = 5,020.00.
- Model ordinary tax and total federal tax: 5,020.00.
- Classification for this tested case: `matches_official_source`.
- Limitation: this case confirms the applicable 2026 single-filer rate-schedule result for the tested income, but it does not by itself validate exact reproduction of the printed IRS Tax Tables for sub-100,000 taxable income ranges.
- Follow-up research: compare representative sub-100,000 federal cases against the separately documented IRS tax-table midpoint method before approving any statement that printed-table reproduction is fully verified.
- Decision: No federal formula or rounding-code change.

\## NIIT and IRMAA



No NIIT or projected-IRMAA formula changes were made in Phase 38B.



Future scenario-bank work may add independently sourced expected values for:



\- `expected\_niit\_tax`

\- `expected\_projected\_irmaa\_2028\_premium`

\- `expected\_projected\_irmaa\_2028\_surcharge`



Blank expected-result cells mean “not independently validated yet”; they do not mean zero.



\## Deferred



\- Official-source federal and NC rounding evidence collection

\- Any tax formula or rounding modification

\- Incremental-income sliver analysis

\- Streamlit or other consumer UI work

