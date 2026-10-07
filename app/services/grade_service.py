from sqlalchemy import String, cast, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models import Enrollment, Grade
from app.schemas import GradeCreate, GradeUpdate


def get_grade(db: Session, grade_id: int):
    return db.get(Grade, grade_id)


def get_grades(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    search: str | None = None,
    enrollment_id: int | None = None,
    min_grade: float | None = None,
    max_grade: float | None = None,
    sort_by: str = "id",
    sort_order: str = "asc",
):
    statement = select(Grade)

    if search:
        search_pattern = f"%{search}%"
        statement = statement.where(
            or_(
                cast(Grade.enrollment_id, String).ilike(search_pattern),
                Grade.remarks.ilike(search_pattern),
            )
        )

    if enrollment_id is not None:
        statement = statement.where(
            Grade.enrollment_id == enrollment_id
        )

    if min_grade is not None:
        statement = statement.where(
            Grade.grade >= min_grade
        )

    if max_grade is not None:
        statement = statement.where(
            Grade.grade <= max_grade
        )

    sort_columns = {
        "id": Grade.id,
        "enrollment_id": Grade.enrollment_id,
        "grade": Grade.grade,
    }

    sort_column = sort_columns.get(sort_by, Grade.id)

    if sort_order.lower() == "desc":
        statement = statement.order_by(sort_column.desc())
    else:
        statement = statement.order_by(sort_column.asc())

    statement = statement.offset(skip).limit(limit)

    return db.scalars(statement).all()

def create_grade(
    db: Session,
    grade_data: GradeCreate,
):
    enrollment = db.get(
        Enrollment,
        grade_data.enrollment_id,
    )

    if not enrollment:
        raise ValueError(
            "Enrollment does not exist"
        )

    existing = db.scalars(
        select(Grade).where(
            Grade.enrollment_id
            == grade_data.enrollment_id
        )
    ).first()

    if existing:
        raise ValueError(
            "A grade already exists for this enrollment"
        )

    grade = Grade(
        enrollment_id=grade_data.enrollment_id,
        grade=grade_data.grade,
        remarks=grade_data.remarks,
    )

    db.add(grade)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise ValueError(
            "Unable to create grade"
        )

    db.refresh(grade)

    return grade


def update_grade(
    db: Session,
    grade_id: int,
    grade_data: GradeUpdate,
):
    grade = db.get(
        Grade,
        grade_id,
    )

    if not grade:
        return None

    update_data = grade_data.model_dump(
        exclude_unset=True
    )

    if "enrollment_id" in update_data:
        enrollment = db.get(
            Enrollment,
            update_data["enrollment_id"],
        )

        if not enrollment:
            raise ValueError(
                "Enrollment does not exist"
            )

        existing = db.scalars(
            select(Grade).where(
                Grade.enrollment_id
                == update_data["enrollment_id"],
                Grade.id != grade_id,
            )
        ).first()

        if existing:
            raise ValueError(
                "A grade already exists for this enrollment"
            )

    for field, value in update_data.items():
        setattr(grade, field, value)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise ValueError(
            "Unable to update grade"
        )

    db.refresh(grade)

    return grade


def delete_grade(
    db: Session,
    grade_id: int,
):
    grade = db.get(
        Grade,
        grade_id,
    )

    if not grade:
        return False

    db.delete(grade)
    db.commit()

    return True