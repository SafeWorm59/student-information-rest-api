from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.dependencies import (
    get_current_student,
    get_current_user,
    require_roles,
)
from app.db.session import get_db
from app.models import CourseOffering, Enrollment, Student
from app.schemas import EnrollmentCreate, EnrollmentResponse, EnrollmentUpdate
from app.services import enrollment_service


router = APIRouter(prefix="/enrollments", tags=["Enrollments"])


@router.get("/", response_model=list[EnrollmentResponse])
def get_enrollments(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    search: str | None = None,
    student_id: int | None = None,
    course_offering_id: int | None = None,
    status: str | None = None,
    sort_by: str = "id",
    sort_order: str = "asc",
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return enrollment_service.get_enrollments(
        db,
        skip=skip,
        limit=limit,
        search=search,
        student_id=student_id,
        course_offering_id=course_offering_id,
        status=status,
        sort_by=sort_by,
        sort_order=sort_order,
    )


@router.get("/me", response_model=list[EnrollmentResponse])
def get_my_enrollments(
    db: Session = Depends(get_db),
    current_student=Depends(get_current_student),
):
    return (
        db.query(Enrollment)
        .filter(Enrollment.student_id == current_student.id)
        .order_by(Enrollment.id.asc())
        .all()
    )


@router.get(
    "/{enrollment_id}",
    response_model=EnrollmentResponse,
)
def get_enrollment(
    enrollment_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    enrollment = enrollment_service.get_enrollment(
        db,
        enrollment_id,
    )

    if not enrollment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Enrollment not found",
        )

    if current_user.role == "student":
        if enrollment.student.email != current_user.email:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not authorized to access this enrollment",
            )

    return enrollment


@router.get(
    "/students/{student_id}/enrollments",
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


@router.post(
    "/",
    response_model=EnrollmentResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_enrollment(
    enrollment_data: EnrollmentCreate,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_roles("admin", "registrar")
    ),
):
    try:
        return enrollment_service.create_enrollment(
            db,
            enrollment_data,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        )


@router.patch(
    "/{enrollment_id}",
    response_model=EnrollmentResponse,
)
def update_enrollment(
    enrollment_id: int,
    enrollment_data: EnrollmentUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_roles("admin", "registrar")
    ),
):
    try:
        enrollment = enrollment_service.update_enrollment(
            db,
            enrollment_id,
            enrollment_data,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        )

    if not enrollment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Enrollment not found",
        )

    return enrollment


@router.delete(
    "/{enrollment_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_enrollment(
    enrollment_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_roles("admin", "registrar")
    ),
):
    try:
        deleted = enrollment_service.delete_enrollment(
            db,
            enrollment_id,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        )

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Enrollment not found",
        )

    return None