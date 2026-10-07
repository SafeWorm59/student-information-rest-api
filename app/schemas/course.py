from pydantic import BaseModel, ConfigDict, Field


class CourseBase(BaseModel):
    code: str = Field(
        min_length=2,
        max_length=20,
    )

    title: str = Field(
        min_length=2,
        max_length=150,
    )

    description: str | None = None

    units: int = Field(
        ge=1,
        le=6,
    )


class CourseCreate(CourseBase):
    pass


class CourseUpdate(BaseModel):
    code: str | None = Field(
        default=None,
        min_length=2,
        max_length=20,
    )

    title: str | None = Field(
        default=None,
        min_length=2,
        max_length=150,
    )

    description: str | None = None

    units: int | None = Field(
        default=None,
        ge=1,
        le=6,
    )


class CourseResponse(CourseBase):
    model_config = ConfigDict(from_attributes=True)

    id: int