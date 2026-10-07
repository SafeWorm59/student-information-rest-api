from sqlalchemy import or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models import Program, Student
from app.schemas import StudentCreate, StudentUpdate


def get_student(db: Session, student_id: int):
    return db.get(Student, student_id)


def get_students(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    search: str | None = None,
    program_id: int | None = None,
    year_level: int | None = None,
    status: str | None = None,
    sort_by: str = "id",
    sort_order: str = "asc",
):
    statement = select(Student)

    if search:
        search_pattern = f"%{search}%"

        statement = statement.where(
            or_(
                Student.student_number.ilike(search_pattern),
                Student.first_name.ilike(search_pattern),
                Student.last_name.ilike(search_pattern),
                Student.middle_name.ilike(search_pattern),
                Student.email.ilike(search_pattern),
            )
        )

    if program_id is not None:
        statement = statement.where(
            Student.program_id == program_id
        )

    if year_level is not None:
        statement = statement.where(
            Student.year_level == year_level
        )

    if status is not None:
        statement = statement.where(
            Student.status == status
        )

    sort_columns = {
        "id": Student.id,
        "student_number": Student.student_number,
        "first_name": Student.first_name,
        "last_name": Student.last_name,
        "year_level": Student.year_level,
        "status": Student.status,
    }

    sort_column = sort_columns.get(sort_by, Student.id)

    if sort_order.lower() == "desc":
        statement = statement.order_by(sort_column.desc())
    else:
        statement = statement.order_by(sort_column.asc())

    statement = statement.offset(skip).limit(limit)

    return db.scalars(statement).all()


def create_student(
    db: Session,
    student_data: StudentCreate,
):
    existing_student = db.scalars(
        select(Student).where(
            or_(
                Student.student_number
                == student_data.student_number,
                Student.email
                == student_data.email,
            )
        )
    ).first()

    if existing_student:
        if (
            existing_student.student_number
            == student_data.student_number
        ):
            raise ValueError(
                "Student number already exists"
            )

        raise ValueError(
            "Student email already exists"
        )

    program = db.get(
        Program,
        student_data.program_id,
    )

    if not program:
        raise ValueError(
            "Program does not exist"
        )

    student = Student(
        student_number=student_data.student_number,
        first_name=student_data.first_name,
        last_name=student_data.last_name,
        middle_name=student_data.middle_name,
        email=student_data.email,
        program_id=student_data.program_id,
        year_level=student_data.year_level,
        status=student_data.status,
    )

    db.add(student)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise ValueError(
            "Unable to create student because of a database constraint"
        )

    db.refresh(student)

    return student


def update_student(
    db: Session,
    student_id: int,
    student_data: StudentUpdate,
):
    student = db.get(Student, student_id)

    if not student:
        return None

    update_data = student_data.model_dump(
        exclude_unset=True
    )

    if "student_number" in update_data:
        existing = db.scalars(
            select(Student).where(
                Student.student_number
                == update_data["student_number"],
                Student.id != student_id,
            )
        ).first()

        if existing:
            raise ValueError(
                "Student number already exists"
            )

    if "email" in update_data:
        existing = db.scalars(
            select(Student).where(
                Student.email
                == update_data["email"],
                Student.id != student_id,
            )
        ).first()

        if existing:
            raise ValueError(
                "Student email already exists"
            )

    if "program_id" in update_data:
        program = db.get(
            Program,
            update_data["program_id"],
        )

        if not program:
            raise ValueError(
                "Program does not exist"
            )

    for field, value in update_data.items():
        setattr(student, field, value)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise ValueError(
            "Unable to update student because of a database constraint"
        )

    db.refresh(student)

    return student


def delete_student(
    db: Session,
    student_id: int,
):
    student = db.get(Student, student_id)

    if not student:
        return False

    try:
        db.delete(student)
        db.commit()
    except IntegrityError:
        db.rollback()
        raise ValueError(
            "Student cannot be deleted because academic records are associated with this student"
        )

    return True