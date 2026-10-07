from pydantic import BaseModel, ConfigDict, EmailStr, Field


class StudentBase(BaseModel):
    student_number: str = Field(
        min_length=3,
        max_length=30,
    )

    first_name: str = Field(
        min_length=1,
        max_length=100,
    )

    last_name: str = Field(
        min_length=1,
        max_length=100,
    )

    middle_name: str | None = Field(
        default=None,
        max_length=100,
    )

    email: EmailStr

    program_id: int = Field(
        gt=0,
    )

    year_level: int = Field(
        ge=1,
        le=6,
    )

    status: str = Field(
        default="active",
        min_length=1,
        max_length=30,
    )


class StudentCreate(StudentBase):
    pass


class StudentUpdate(BaseModel):
    student_number: str | None = Field(
        default=None,
        min_length=3,
        max_length=30,
    )

    first_name: str | None = Field(
        default=None,
        min_length=1,
        max_length=30,
    )

    last_name: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
    )

    middle_name: str | None = Field(
        default=None,
        max_length=100,
    )

    email: EmailStr | None = None

    program_id: int | None = Field(
        default=None,
        gt=0,
    )

    year_level: int | None = Field(
        default=None,
        ge=1,
        le=6,
    )

    status: str | None = Field(
        default=None,
        min_length=1,
        max_length=30,
    )


class StudentResponse(StudentBase):
    model_config = ConfigDict(from_attributes=True)

    id: int