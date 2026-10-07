from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models import Program
from app.schemas import ProgramCreate, ProgramUpdate


def get_program(db: Session, program_id: int):
    return db.get(Program, program_id)


def get_programs(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    search: str | None = None,
    status: str | None = None,
    sort_by: str = "id",
    sort_order: str = "asc",
):
    statement = select(Program)

    if search:
        search_pattern = f"%{search}%"
        statement = statement.where(
            Program.code.ilike(search_pattern)
            | Program.name.ilike(search_pattern)
        )

    if status:
        statement = statement.where(Program.status == status)

    sort_columns = {
        "id": Program.id,
        "code": Program.code,
        "name": Program.name,
    }

    sort_column = sort_columns.get(sort_by, Program.id)

    if sort_order.lower() == "desc":
        statement = statement.order_by(sort_column.desc())
    else:
        statement = statement.order_by(sort_column.asc())

    statement = statement.offset(skip).limit(limit)

    return db.scalars(statement).all()


def create_program(
    db: Session,
    program_data: ProgramCreate,
):
    existing = db.scalars(
        select(Program).where(Program.code == program_data.code)
    ).first()

    if existing:
        raise ValueError("Program code already exists")

    existing_name = db.scalars(
        select(Program).where(Program.name == program_data.name)
    ).first()

    if existing_name:
        raise ValueError("Program name already exists")

    program = Program(
        code=program_data.code,
        name=program_data.name,
        description=program_data.description,
    )

    db.add(program)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise ValueError(
            "Unable to create program because of a database constraint"
        )

    db.refresh(program)

    return program


def update_program(
    db: Session,
    program: Program,
    program_data: ProgramUpdate,
):
    update_data = program_data.model_dump(exclude_unset=True)

    if "code" in update_data:
        existing = db.scalars(
            select(Program).where(
                Program.code == update_data["code"],
                Program.id != program.id,
            )
        ).first()

        if existing:
            raise ValueError("Program code already exists")

    if "name" in update_data:
        existing = db.scalars(
            select(Program).where(
                Program.name == update_data["name"],
                Program.id != program.id,
            )
        ).first()

        if existing:
            raise ValueError("Program name already exists")

    for field, value in update_data.items():
        setattr(program, field, value)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise ValueError(
            "Unable to update program because of a database constraint"
        )

    db.refresh(program)

    return program


def delete_program(
    db: Session,
    program: Program,
):
    try:
        db.delete(program)
        db.commit()
    except IntegrityError:
        db.rollback()
        raise ValueError(
            "Program cannot be deleted because students are associated with it"
        )