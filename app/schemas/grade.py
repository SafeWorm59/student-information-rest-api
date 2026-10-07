from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class GradeBase(BaseModel):
    enrollment_id: int = Field(
        gt=0,
    )

    grade: Decimal = Field(
        ge=0,
        le=5,
        decimal_places=2,
    )

    remarks: str | None = Field(
        default=None,
        max_length=100
    )


class GradeCreate(GradeBase):
    pass


class GradeUpdate(BaseModel):
    grade: Decimal | None = Field(
        default=None,
        ge=0,
        le=5,
        decimal_places=2,
    )

    remarks: str | None = Field(
        default=None,
        max_length=100,
    )


class GradeResponse(GradeBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    graded_at: datetime