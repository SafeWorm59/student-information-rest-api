from pydantic import BaseModel, ConfigDict, Field


class CourseOfferingBase(BaseModel):
    course_id: int = Field(
        gt=0,
    )

    term_id: int = Field(
        gt=0,
    )

    section: str = Field(
        min_length=1,
        max_length=30,
    )

    schedule: str | None = Field(
        default=None,
        max_length=100,
    )

    room: str | None = Field(
        default=None,
        max_length=50,
    )

    instructor: str | None = Field(
        default=None,
        max_length=150,
    )

    capacity: int = Field(
        ge=1,
        le=500,
    )


class CourseOfferingCreate(CourseOfferingBase):
    pass


class CourseOfferingUpdate(BaseModel):
    course_id: int | None = Field(
        default=None,
        gt=0,
    )

    term_id: int | None = Field(
        default=None,
        gt=0,
    )

    section: str | None = Field(
        default=None,
        min_length=1,
        max_length=30,
    )

    schedule: str | None = Field(
        default=None,
        max_length=100,
    )

    room: str | None = Field(
        default=None,
        max_length=50,
    )

    instructor: str | None = Field(
        default=None,
        max_length=150,
    )

    capacity: int | None = Field(
        default=None,
        ge=1,
        le=500,
    )


class CourseOfferingResponse(CourseOfferingBase):
    model_config = ConfigDict(from_attributes=True)

    id: int