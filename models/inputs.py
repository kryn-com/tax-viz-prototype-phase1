from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, field_validator, model_validator


class FilingStatus(str, Enum):
    SINGLE = "single"
    MARRIED_FILING_JOINTLY = "married_filing_jointly"
    MARRIED_FILING_SEPARATELY = "married_filing_separately"
    HEAD_OF_HOUSEHOLD = "head_of_household"


class DeductionMode(str, Enum):
    STANDARD = "standard"
    ITEMIZED = "itemized"
    EXPLICIT = "explicit"  # Used for Phase 1 where amount is strictly provided


class NCDeductionMode(str, Enum):
    STANDARD = "standard"
    ITEMIZED = "itemized"


class TaxScenarioInput(BaseModel):
    # Required base fields for Phase 1 rules
    tax_year: int
    state_code: str = Field(min_length=2, max_length=2)
    filing_status: FilingStatus

    # Demographics
    taxpayer_age: int = Field(ge=0, le=120)
    spouse_age: Optional[int] = Field(default=None, ge=0, le=120)

    # Incomes
    ordinary_income: float = Field(ge=0.0, default=0.0)
    ltcg_qd_income: float = Field(ge=0.0, default=0.0)
    social_security_income: float = Field(ge=0.0, default=0.0)
    nontaxable_income: float = Field(ge=0.0, default=0.0)

    # Federal AGI and NC-specific fields approved for Phase 33A
    federal_agi: float = Field(ge=0.0, default=0.0)
    federal_taxable_social_security: float = Field(ge=0.0, default=0.0)
    net_nc_interest_dividend_adjustment: float = Field(default=0.0)
    bailey_exempt_pension_amount: Optional[float] = Field(default=None, ge=0.0)
    nc_deduction_mode: NCDeductionMode = Field(default=NCDeductionMode.STANDARD)
    nc_itemized_deduction_amount: Optional[float] = Field(default=None, ge=0.0)

    # Deductions
    deduction_mode: DeductionMode = Field(default=DeductionMode.EXPLICIT)
    deduction_amount: float = Field(ge=0.0, default=0.0)

    @field_validator("tax_year")
    @classmethod
    def validate_tax_year(cls, v: int) -> int:
        if v != 2026:
            raise ValueError(f"Unsupported tax year: {v}. Only 2026 is supported in Phase 1.")
        return v

    @field_validator("deduction_amount")
    @classmethod
    def validate_deduction(cls, v: float) -> float:
        if v < 0:
            raise ValueError("Deduction amount cannot be negative.")
        return v

    @field_validator("bailey_exempt_pension_amount")
    @classmethod
    def validate_bailey_exempt_pension_amount(cls, v: Optional[float]) -> Optional[float]:
        if v is not None and v < 0:
            raise ValueError("bailey_exempt_pension_amount cannot be negative")
        return v

    @model_validator(mode="after")
    def validate_age_contract(self):
        if self.filing_status is FilingStatus.MARRIED_FILING_JOINTLY and self.spouse_age is None:
            raise ValueError("spouse_age is required when filing_status is married_filing_jointly")
        return self

    @model_validator(mode="after")
    def validate_nc_contract(self):
        if self.nc_deduction_mode is NCDeductionMode.STANDARD and self.nc_itemized_deduction_amount is not None:
            raise ValueError("nc_itemized_deduction_amount is only allowed when nc_deduction_mode is itemized")
        if self.nc_deduction_mode is NCDeductionMode.ITEMIZED and self.nc_itemized_deduction_amount is None:
            raise ValueError("nc_itemized_deduction_amount is required when nc_deduction_mode is itemized")
        return self