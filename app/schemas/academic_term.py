from datetime import date

from pydantic import BaseModel, ConfigDict, Field


class AcademicTermBase(BaseModel):
    name: str = Field(
        min_length=2,
        max_length=50,
    )

    school_year: str = Field(
        min_length=4,
        max_length=20,
    )

    start_date: date
    end_date: date

    is_active: bool = False


class AcademicTermCreate(AcademicTermBase):
    pass


class AcademicTermUpdate(BaseModel):
    name: str | None = Field(
        default=None,
        min_length=2,
        max_length=50,
    )

    school_year: str | None = Field(
        default=None,
        min_length=4,
        max_length=20,
    )

    start_date: date | None = None
    end_date: date | None = None
    is_active: bool | None = None


class AcademicTermResponse(AcademicTermBase):
    model_config = ConfigDict(from_attributes=True)

    id: int