from sqlalchemy import or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models import Course, CourseOffering, AcademicTerm
from app.schemas import CourseOfferingCreate, CourseOfferingUpdate


def get_course_offering(db: Session, offering_id: int):
    return db.get(CourseOffering, offering_id)


def get_course_offerings(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    search: str | None = None,
    course_id: int | None = None,
    term_id: int | None = None,
    sort_by: str = "id",
    sort_order: str = "asc",
):
    statement = select(CourseOffering)

    if search:
        search_pattern = f"%{search}%"
        statement = statement.where(
            or_(
                CourseOffering.section.ilike(search_pattern),
                CourseOffering.schedule.ilike(search_pattern),
                CourseOffering.room.ilike(search_pattern),
                CourseOffering.instructor.ilike(search_pattern),
            )
        )

    if course_id is not None:
        statement = statement.where(
            CourseOffering.course_id == course_id
        )

    if term_id is not None:
        statement = statement.where(
            CourseOffering.term_id == term_id
        )

    sort_columns = {
        "id": CourseOffering.id,
        "course_id": CourseOffering.course_id,
        "term_id": CourseOffering.term_id,
        "section": CourseOffering.section,
        "capacity": CourseOffering.capacity,
    }

    sort_column = sort_columns.get(sort_by, CourseOffering.id)

    if sort_order.lower() == "desc":
        statement = statement.order_by(sort_column.desc())
    else:
        statement = statement.order_by(sort_column.asc())

    statement = statement.offset(skip).limit(limit)

    return db.scalars(statement).all()


def create_course_offering(
    db: Session,
    offering_data: CourseOfferingCreate,
):
    course = db.get(Course, offering_data.course_id)

    if not course:
        raise ValueError("Course does not exist")

    term = db.get(AcademicTerm, offering_data.term_id)

    if not term:
        raise ValueError("Academic term does not exist")

    offering = CourseOffering(
        course_id=offering_data.course_id,
        term_id=offering_data.term_id,
        section=offering_data.section,
        schedule=offering_data.schedule,
        room=offering_data.room,
        instructor=offering_data.instructor,
        capacity=offering_data.capacity,
    )

    db.add(offering)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise ValueError(
            "Unable to create course offering because of a database constraint"
        )

    db.refresh(offering)

    return offering


def update_course_offering(
    db: Session,
    offering: CourseOffering,
    offering_data: CourseOfferingUpdate,
):
    update_data = offering_data.model_dump(exclude_unset=True)

    if "course_id" in update_data:
        course = db.get(Course, update_data["course_id"])

        if not course:
            raise ValueError("Course does not exist")

    if "term_id" in update_data:
        term = db.get(AcademicTerm, update_data["term_id"])

        if not term:
            raise ValueError("Academic term does not exist")

    for field, value in update_data.items():
        setattr(offering, field, value)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise ValueError(
            "Unable to update course offering because of a database constraint"
        )

    db.refresh(offering)

    return offering


def delete_course_offering(db: Session, offering: CourseOffering):
    try:
        db.delete(offering)
        db.commit()
    except IntegrityError:
        db.rollback()
        raise ValueError(
            "Course offering cannot be deleted because enrollments are associated with it"
        )