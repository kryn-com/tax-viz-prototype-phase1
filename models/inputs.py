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

    @model_validator(mode="after")
    def validate_age_contract(self):
        if self.filing_status is FilingStatus.MARRIED_FILING_JOINTLY and self.spouse_age is None:
            raise ValueError("spouse_age is required when filing_status is married_filing_jointly")
        return self