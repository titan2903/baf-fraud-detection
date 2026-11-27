from typing import Literal

from pydantic import BaseModel, Field

# Semua fitur wajib. Nilai -1 berarti "data tidak ada" (konvensi dataset BAF), jadi tanpa batas bawah.

EXAMPLE = {"income": 0.1, "name_email_similarity": 0.7928278491100123, "prev_address_months_count": -1, "current_address_months_count": 3, "customer_age": 40, "days_since_request": 0.0301686999891298, "intended_balcon_amount": -1.2123557602962909, "payment_type": "AB", "zip_count_4w": 907, "velocity_6h": 4165.8648375101975, "velocity_24h": 3347.0249222680395, "velocity_4w": 4650.407172875624, "bank_branch_count_8w": 35, "date_of_birth_distinct_emails_4w": 4, "employment_status": "CA", "credit_risk_score": 82, "email_is_free": 1, "housing_status": "BB", "phone_home_valid": 1, "phone_mobile_valid": 0, "bank_months_count": 1, "has_other_cards": 1, "proposed_credit_limit": 200.0, "foreign_request": 1, "source": "INTERNET", "session_length_in_minutes": 2.726813455836169, "device_os": "linux", "keep_alive_session": 1, "device_distinct_emails_8w": 1}


class Application(BaseModel):
    """Satu pengajuan pembukaan rekening (29 fitur, urutan sama dengan model)."""

    model_config = {"json_schema_extra": {"examples": [EXAMPLE]}, "allow_inf_nan": False}

    income: float
    name_email_similarity: float
    prev_address_months_count: int
    current_address_months_count: int
    customer_age: int
    days_since_request: float
    intended_balcon_amount: float
    payment_type: Literal["AA", "AB", "AC", "AD", "AE"]
    zip_count_4w: int
    velocity_6h: float
    velocity_24h: float
    velocity_4w: float
    bank_branch_count_8w: int
    date_of_birth_distinct_emails_4w: int
    employment_status: Literal["CA", "CB", "CC", "CD", "CE", "CF", "CG"]
    credit_risk_score: int
    email_is_free: int = Field(ge=0, le=1)  # model hanya pernah melihat 0/1
    housing_status: Literal["BA", "BB", "BC", "BD", "BE", "BF", "BG"]
    phone_home_valid: int = Field(ge=0, le=1)  # model hanya pernah melihat 0/1
    phone_mobile_valid: int = Field(ge=0, le=1)  # model hanya pernah melihat 0/1
    bank_months_count: int
    has_other_cards: int = Field(ge=0, le=1)  # model hanya pernah melihat 0/1
    proposed_credit_limit: float
    foreign_request: int = Field(ge=0, le=1)  # model hanya pernah melihat 0/1
    source: Literal["INTERNET", "TELEAPP"]
    session_length_in_minutes: float
    device_os: Literal["linux", "macintosh", "other", "windows", "x11"]
    keep_alive_session: int = Field(ge=0, le=1)  # model hanya pernah melihat 0/1
    device_distinct_emails_8w: int


class Health(BaseModel):
    model_config = {"protected_namespaces": ()}

    status: str
    model_name: str
    model_version: str


class Prediction(BaseModel):
    model_config = {"protected_namespaces": ()}  # izinkan field berawalan model_

    model_name: str
    model_version: str
    fraud_score: float
    is_fraud: bool
    threshold: float
