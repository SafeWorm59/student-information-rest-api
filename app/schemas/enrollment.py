from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class EnrollmentBase(BaseModel):
    student_id: int = Field(
        gt=0,
    )

    course_offering_id: int = Field(
        gt=0,
    )

    status: str = Field(
        default="enrolled",
        min_length=1,
        max_length=30,
    )


class EnrollmentCreate(EnrollmentBase):
    pass


class EnrollmentUpdate(BaseModel):
    status: str | None = Field(
        default=None,
        min_length=1,
        max_length=30,
    )


class EnrollmentResponse(EnrollmentBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    enrolled_at: datetime