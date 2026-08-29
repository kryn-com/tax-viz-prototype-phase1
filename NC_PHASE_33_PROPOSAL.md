I’m tightening the proposal wording to match the exact field names and the approved Bailey-definition without changing the phase scope.

Searched for files matching `**/NC_PHASE_33_PROPOSAL.md`, no matches

Read memory

Created memory file 

# NC_PHASE_33_PROPOSAL.md

## Goal

Define a narrow North Carolina state module for simplified taxable-income and pre-credit income-tax calculation, while preserving the approved architecture boundaries: federal logic remains separate, presentation remains separate, and IRMAA remains separate. This proposal is intentionally limited to the approved NC scope and does not authorize broader state-tax implementation.

## 1. Module boundaries

- The NC module is a separate state-tax calculation layer, not a federal tax engine extension.
- It consumes federal AGI and other approved scenario inputs, but it does not alter federal formulas or outputs.
- It does not participate in presentation, SVG rendering, charting, or display-model logic.
- It does not model IRMAA or Medicare-premium overlays.
- Ages remain validated scenario metadata only and are not used in NC logic for this phase.
- The module produces only NC taxable income and NC income tax before credits.

## 2. Input/output contract

### Inputs

The module should accept only the following approved simplified inputs:

- federal_agi
- federal_taxable_social_security
- net_nc_interest_dividend_adjustment
  - signed numeric adjustment
  - reflects only interest/dividend taxability differences
  - may be positive or negative
- bailey_exempt_pension_amount
  - optional numeric field
  - blank or None when not applicable
  - otherwise the deductible Bailey-exempt pension amount already included in federal AGI
  - this is not total pension received; it is only the portion of pension included in federal AGI that is deductible under the Bailey exemption
- nc_deduction_mode
  - standard or itemized
- nc_itemized_deduction_amount
  - direct user-supplied amount for this phase
  - only relevant when nc_deduction_mode is itemized
- filing_status
- other existing validated scenario metadata required by the repo, but not used in NC logic for this phase

### Outputs

The module should return a minimal NC state result object containing:

- nc_taxable_income
- nc_income_tax_before_credits
- optional explanatory breakdown fields limited to:
  - starting federal AGI
  - minus federal_taxable_social_security
  - plus or minus net_nc_interest_dividend_adjustment
  - minus bailey_exempt_pension_amount when applicable
  - minus selected NC deduction amount
- no credit amounts
- no refunds, withholding, payments, or penalties
- no consumer-use tax or other NC adjustments outside the approved simplified fields

## 3. Exact simplifications

This phase intentionally uses a practical approximation model, not a full statutory NC engine.

- Start from federal AGI.
- Subtract federal_taxable_social_security as a separate NC adjustment.
- Apply a single signed user-entered NC interest/dividend adjustment through net_nc_interest_dividend_adjustment.
- Apply Bailey exemption only through bailey_exempt_pension_amount when the user enters an applicable deductible amount already included in federal AGI.
- Choose NC deduction as either standard or itemized.
- For this phase, itemized deduction is a direct user-supplied amount; no category-by-category itemization logic is included.
- Calculate only:
  - NC taxable income
  - NC income tax before credits
- Do not include any credit logic, including:
  - foreign tax credit
  - other-state credit
  - any other NC credit mechanism
- Do not include:
  - withholding
  - refunds
  - estimated payments
  - penalties
  - consumer-use tax
  - other NC adjustments outside the approved simplified fields
- Do not use age-based rules in this phase, even though ages remain validated scenario inputs.

This is intentionally an approximation layer for future NC state-tax work and should be clearly labeled as such.

## 4. Reconciliation approach using the provided 2025 return

The approved 2025 return is to be used as an approximation reference and a sanity check, not as a legal authority or final filing result.

### Reconciliation method

- Use the redacted 2025 return to identify the rough structure of:
  - federal AGI
  - federal taxable Social Security
  - interest/dividend amounts
  - pension amounts potentially eligible for Bailey treatment
  - standard-vs-itemized deduction posture
- Map these values into the simplified NC input fields above.
- Compare the resulting NC taxable income and pre-credit NC income tax to the 2025 return’s rough NC position as an approximate tie-out.
- Treat differences as expected due to the simplified scope and explicitly record any unsupported assumptions.
- The goal is directional approximation, not exact statutory replication.

### Reconciliation guardrails

- The 2025 return is used only as a practical benchmark.
- No hidden assumptions may be created beyond the approved simplified inputs.
- Any unresolved item should be recorded as an approximation gap rather than silently assumed.
- The reconciliation note should clearly say that the modeled NC tax is an approximation for prototype usage, not a legal result.

## 5. Non-goals

This phase explicitly excludes:

- Full NC statutory calculation logic
- Itemized-deduction category-by-category modeling
- County or local tax logic
- Credit logic, including all NC credits and other-state/foreign tax offsets
- Withholding, refund, payment, or penalty mechanics
- State filing or e-file behavior
- Presentation-layer integration
- IRMAA or Medicare surcharge overlays
- Any change to federal engine behavior or interfaces
- Any broader multi-state or federal-state integration work

## 6. Phased implementation sequence

1. Define the NC state module boundary
   - confirm separation from federal logic, presentation, and IRMAA
   - confirm the approved simplified input set

2. Add the NC input contract
   - formalize the required and optional fields
   - validate signed treatment for net_nc_interest_dividend_adjustment
   - validate optional blank/None handling for bailey_exempt_pension_amount

3. Implement the NC taxable-income formula
   - start from federal AGI
   - subtract federal_taxable_social_security
   - add or subtract net_nc_interest_dividend_adjustment
   - subtract bailey_exempt_pension_amount when present
   - subtract the selected NC deduction amount

4. Implement the NC tax-before-credits calculation
   - use the approved simplified NC rate schedule for the relevant year only
   - output pre-credit income tax
   - no credit logic in this phase

5. Add reconciliation and approximation reporting
   - compare output to the provided 2025 return as a sanity benchmark
   - record assumptions and gaps

6. Run focused validation and regression check
   - confirm no federal logic drift
   - confirm no presentation or IRMAA boundaries are crossed

## 7. Test plan

### Unit tests

- federal AGI base case
- federal taxable Social Security subtraction
- positive and negative net_nc_interest_dividend_adjustment
- blank and provided bailey_exempt_pension_amount
- standard deduction path
- itemized deduction path using a direct user-entered amount
- no-credit output validation

### Edge-case tests

- zero or empty values
- negative NC adjustment
- missing Bailey pension amount when not applicable
- itemized deduction chosen with no amount entered
- unsupported or out-of-scope field rejection

### Reconciliation tests

- compare approximate NC taxable income to the reference 2025 return range
- confirm assumptions are explicitly documented when the return cannot be matched exactly
- confirm the model does not overstate statutory completeness

### Regression tests

- run the existing full suite to confirm no federal-tax logic changes
- confirm NC module remains isolated from presentation and IRMAA outputs
- confirm no new state-tax leakage enters federal rendering logic

## Decision summary

This phase should be approved only as a limited, approximation-based NC state module that computes taxable income and pre-credit income tax from federal AGI, with explicit simplifications and no credit logic. The implementation objective is architectural separation, deterministic calculations, and a documented approximation path tied to the 2025 return reference rather than a complete NC return engine.