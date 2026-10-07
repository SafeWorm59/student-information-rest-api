from pydantic import BaseModel, ConfigDict, Field


class ProgramBase(BaseModel):
    code: str = Field(
        min_length=2,
        max_length=20,
    )

    name: str = Field(
        min_length=2,
        max_length=150,
    )

    description: str | None = None

    status: str = Field(
        default="active",
        min_length=1,
        max_length=20,
    )


class ProgramCreate(ProgramBase):
    pass


class ProgramUpdate(BaseModel):
    code: str | None = Field(
        default=None,
        min_length=2,
        max_length=20,
    )

    name: str | None = Field(
        default=None,
        min_length=2,
        max_length=150,
    )

    description: str | None = None

    status: str | None = Field(
        default=None,
        min_length=1,
        max_length=20,
    )


class ProgramResponse(ProgramBase):
    model_config = ConfigDict(from_attributes=True)

    id: int