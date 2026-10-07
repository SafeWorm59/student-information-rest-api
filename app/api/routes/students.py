from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.models import Enrollment, Grade, Student

from app.core.dependencies import (
    require_roles,
    get_current_user,
    get_current_student,
)
from app.db.session import get_db
from app.schemas import (
    EnrollmentResponse,
    GradeResponse,
    StudentCreate,
    StudentResponse,
    StudentUpdate,
)

from app.services import student_service


router = APIRouter(
    prefix="/students",
    tags=["Students"],
)



@router.get("/", response_model=list[StudentResponse])
def list_students(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    search: str | None = None,
    program_id: int | None = None,
    year_level: int | None = None,
    status: str | None = None,
    sort_by: str = "id",
    sort_order: str = "asc",
    db: Session = Depends(get_db),
):
    return student_service.get_students(
        db,
        skip=skip,
        limit=limit,
        search=search,
        program_id=program_id,
        year_level=year_level,
        status=status,
        sort_by=sort_by,
        sort_order=sort_order,
    )


@router.get("/me", response_model=StudentResponse)
def get_my_student_record(
    current_student=Depends(get_current_student),
):
    return current_student


@router.get(
    "/{student_id}/enrollments",
    response_model=list[EnrollmentResponse],
)
def get_student_enrollments(
    student_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    student = db.get(Student, student_id)

    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found",
        )

    if current_user.role == "student":
        if student.email != current_user.email:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not authorized to access this student's enrollments",
            )

    return (
        db.query(Enrollment)
        .filter(Enrollment.student_id == student_id)
        .order_by(Enrollment.id.asc())
        .all()
    )


@router.get(
    "/{student_id}/grades",
    response_model=list[GradeResponse],
)
def get_student_grades(
    student_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    student = db.get(Student, student_id)

    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found",
        )

    if current_user.role == "student":
        if student.email != current_user.email:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not authorized to access this student's grades",
            )

    return (
        db.query(Grade)
        .join(Grade.enrollment)
        .filter(Enrollment.student_id == student_id)
        .order_by(Grade.id.asc())
        .all()
    )


@router.get("/{student_id}", response_model=StudentResponse)
def get_student(
    student_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    student = student_service.get_student(
        db,
        student_id,
    )

    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found",
        )

    if current_user.role == "student":
        if student.email != current_user.email:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only access your own student record",
            )

    return student


@router.post(
    "/",
    response_model=StudentResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_student(
    student_data: StudentCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin", "registrar")),
):
    try:
        return student_service.create_student(
            db,
            student_data,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        )


@router.patch(
    "/{student_id}",
    response_model=StudentResponse,
)
def update_student(
    student_id: int,
    student_data: StudentUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin", "registrar")),
):
    try:
        student = student_service.update_student(
            db,
            student_id,
            student_data,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        )

    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found",
        )

    return student


@router.delete(
    "/{student_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_student(
    student_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin", "registrar")),
):
    try:
        deleted = student_service.delete_student(
            db,
            student_id,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        )

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found",
        )

    return None
