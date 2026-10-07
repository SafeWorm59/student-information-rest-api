from sqlalchemy import select, or_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models import AcademicTerm
from app.schemas import AcademicTermCreate, AcademicTermUpdate


def get_academic_term(db: Session, term_id: int):
    return db.get(AcademicTerm, term_id)


def get_academic_terms(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    search: str | None = None,
    is_active: bool | None = None,
    sort_by: str = "id",
    sort_order: str = "asc",
):
    statement = select(AcademicTerm)

    if search:
        search_pattern = f"%{search}%"
        statement = statement.where(
            or_(
                AcademicTerm.name.ilike(search_pattern),
                AcademicTerm.school_year.ilike(search_pattern),
            )
        )

    if is_active is not None:
        statement = statement.where(
            AcademicTerm.is_active == is_active
        )

    sort_columns = {
        "id": AcademicTerm.id,
        "name": AcademicTerm.name,
        "school_year": AcademicTerm.school_year,
        "start_date": AcademicTerm.start_date,
        "end_date": AcademicTerm.end_date,
    }

    sort_column = sort_columns.get(sort_by, AcademicTerm.id)

    if sort_order.lower() == "desc":
        statement = statement.order_by(sort_column.desc())
    else:
        statement = statement.order_by(sort_column.asc())

    statement = statement.offset(skip).limit(limit)

    return db.scalars(statement).all()


def create_academic_term(
    db: Session,
    term_data: AcademicTermCreate,
):
    term = AcademicTerm(
        name=term_data.name,
        school_year=term_data.school_year,
        start_date=term_data.start_date,
        end_date=term_data.end_date,
        is_active=term_data.is_active,
    )

    db.add(term)
    db.commit()
    db.refresh(term)

    return term


def update_academic_term(
    db: Session,
    term: AcademicTerm,
    term_data: AcademicTermUpdate,
):
    update_data = term_data.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(term, field, value)

    db.commit()
    db.refresh(term)

    return term


def delete_academic_term(db: Session, term: AcademicTerm):
    try:
        db.delete(term)
        db.commit()
    except IntegrityError:
        db.rollback()
        raise ValueError(
            "Academic term cannot be deleted because course offerings are associated with it"
        )