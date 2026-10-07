from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models import Course
from app.schemas import CourseCreate, CourseUpdate


def get_course(db: Session, course_id: int):
    return db.get(Course, course_id)


def get_courses(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    search: str | None = None,
    status: str | None = None,
    sort_by: str = "id",
    sort_order: str = "asc",
):
    statement = select(Course)

    if search:
        search_pattern = f"%{search}%"
        statement = statement.where(
            Course.code.ilike(search_pattern)
            | Course.title.ilike(search_pattern)
        )

    if status:
        statement = statement.where(Course.status == status)

    sort_columns = {
        "id": Course.id,
        "code": Course.code,
        "title": Course.title,
        "units": Course.units,
    }

    sort_column = sort_columns.get(sort_by, Course.id)

    if sort_order == "desc":
        statement = statement.order_by(sort_column.desc())
    else:
        statement = statement.order_by(sort_column.asc())

    statement = (
        statement
        .offset(skip)
        .limit(limit)
    )

    return db.scalars(statement).all()


def create_course(db: Session, course_data: CourseCreate):
    existing = db.scalars(
        select(Course).where(Course.code == course_data.code)
    ).first()

    if existing:
        raise ValueError("Course code already exists")

    course = Course(
        code=course_data.code,
        title=course_data.title,
        description=course_data.description,
        units=course_data.units,
    )

    db.add(course)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise ValueError(
            "Unable to create course because of a database constraint"
        )

    db.refresh(course)

    return course


def update_course(db: Session, course: Course, course_data: CourseUpdate):
    update_data = course_data.model_dump(exclude_unset=True)

    if "code" in update_data:
        existing = db.scalars(
            select(Course).where(
                Course.code == update_data["code"],
                Course.id != course.id,
            )
        ).first()

        if existing:
            raise ValueError("Course code already exists")

    for field, value in update_data.items():
        setattr(course, field, value)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise ValueError(
            "Unable to update course because of a database constraint"
        )

    db.refresh(course)

    return course


def delete_course(db: Session, course: Course):
    try:
        db.delete(course)
        db.commit()
    except IntegrityError:
        db.rollback()
        raise ValueError(
            "Course cannot be deleted because course offerings are associated with it"
        )