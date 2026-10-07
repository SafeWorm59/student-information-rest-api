from sqlalchemy import String, cast, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models import CourseOffering, Enrollment, Student
from app.schemas import EnrollmentCreate, EnrollmentUpdate


def get_enrollment(db: Session, enrollment_id: int):
    return db.get(Enrollment, enrollment_id)


def get_enrollments(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    search: str | None = None,
    student_id: int | None = None,
    course_offering_id: int | None = None,
    status: str | None = None,
    sort_by: str = "id",
    sort_order: str = "asc",
):
    statement = select(Enrollment)

    if search:
        search_pattern = f"%{search}%"
        statement = statement.where(
            or_(
                cast(Enrollment.student_id, String).ilike(search_pattern),
                cast(Enrollment.course_offering_id, String).ilike(search_pattern),
                Enrollment.status.ilike(search_pattern),
            )
        )

    if student_id is not None:
        statement = statement.where(
            Enrollment.student_id == student_id
        )

    if course_offering_id is not None:
        statement = statement.where(
            Enrollment.course_offering_id == course_offering_id
        )

    if status is not None:
        statement = statement.where(
            Enrollment.status == status
        )

    sort_columns = {
        "id": Enrollment.id,
        "student_id": Enrollment.student_id,
        "course_offering_id": Enrollment.course_offering_id,
        "status": Enrollment.status,
    }

    sort_column = sort_columns.get(sort_by, Enrollment.id)

    if sort_order.lower() == "desc":
        statement = statement.order_by(sort_column.desc())
    else:
        statement = statement.order_by(sort_column.asc())

    statement = statement.offset(skip).limit(limit)

    return db.scalars(statement).all()

def create_enrollment(
    db: Session,
    enrollment_data: EnrollmentCreate,
):
    student = db.get(
        Student,
        enrollment_data.student_id,
    )

    if not student:
        raise ValueError(
            "Student does not exist"
        )

    course_offering = db.get(
        CourseOffering,
        enrollment_data.course_offering_id,
    )

    if not course_offering:
        raise ValueError(
            "Course offering does not exist"
        )

    existing = db.scalars(
        select(Enrollment).where(
            Enrollment.student_id
            == enrollment_data.student_id,
            Enrollment.course_offering_id
            == enrollment_data.course_offering_id,
        )
    ).first()

    if existing:
        raise ValueError(
            "Student is already enrolled in this course offering"
        )

    enrollment = Enrollment(
        student_id=enrollment_data.student_id,
        course_offering_id=enrollment_data.course_offering_id,
        status=enrollment_data.status,
    )

    db.add(enrollment)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise ValueError(
            "Unable to create enrollment"
        )

    db.refresh(enrollment)

    return enrollment


def update_enrollment(
    db: Session,
    enrollment_id: int,
    enrollment_data: EnrollmentUpdate,
):
    enrollment = db.get(
        Enrollment,
        enrollment_id,
    )

    if not enrollment:
        return None

    update_data = enrollment_data.model_dump(
        exclude_unset=True
    )

    if "student_id" in update_data:
        if not db.get(
            Student,
            update_data["student_id"],
        ):
            raise ValueError(
                "Student does not exist"
            )

    if "course_offering_id" in update_data:
        if not db.get(
            CourseOffering,
            update_data["course_offering_id"],
        ):
            raise ValueError(
                "Course offering does not exist"
            )

    for field, value in update_data.items():
        setattr(enrollment, field, value)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise ValueError(
            "Enrollment conflicts with an existing enrollment"
        )

    db.refresh(enrollment)

    return enrollment


def delete_enrollment(
    db: Session,
    enrollment_id: int,
):
    enrollment = db.get(
        Enrollment,
        enrollment_id,
    )

    if not enrollment:
        return False

    try:
        db.delete(enrollment)
        db.commit()
    except IntegrityError:
        db.rollback()
        raise ValueError(
            "Enrollment cannot be deleted because a grade is associated with it"
        )

    return True