from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.dependencies import (
    require_roles,
    get_current_user,
    get_current_student,
)
from app.models import Grade, Enrollment

from app.db.session import get_db
from app.schemas import GradeCreate, GradeResponse, GradeUpdate
from app.services import grade_service


router = APIRouter(
    prefix="/grades",
    tags=["Grades"],
)


@router.get("/", response_model=list[GradeResponse])
def get_grades(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    search: str | None = None,
    enrollment_id: int | None = None,
    min_grade: float | None = Query(None, ge=0),
    max_grade: float | None = Query(None, ge=0, le=5),
    sort_by: str = "id",
    sort_order: str = "asc",
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return grade_service.get_grades(
        db,
        skip=skip,
        limit=limit,
        search=search,
        enrollment_id=enrollment_id,
        min_grade=min_grade,
        max_grade=max_grade,
        sort_by=sort_by,
        sort_order=sort_order,
    )


@router.get("/me", response_model=list[GradeResponse])
def get_my_grades(
    db: Session = Depends(get_db),
    current_student=Depends(get_current_student),
):
    return (
        db.query(Grade)
        .join(Grade.enrollment)
        .filter(
            Enrollment.student_id == current_student.id
        )
        .order_by(Grade.id.asc())
        .all()
    )


@router.get("/{grade_id}", response_model=GradeResponse)
def get_grade(
    grade_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    grade = grade_service.get_grade(
        db,
        grade_id,
    )

    if not grade:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Grade not found",
        )

    if current_user.role == "student":
        if grade.enrollment.student.email != current_user.email:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only access your own grade",
            )

    return grade


@router.post(
    "/",
    response_model=GradeResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_grade(
    grade_data: GradeCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin", "registrar")),
):
    try:
        return grade_service.create_grade(
            db,
            grade_data,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        )


@router.patch(
    "/{grade_id}",
    response_model=GradeResponse,
)
def update_grade(
    grade_id: int,
    grade_data: GradeUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin", "registrar")),
):
    try:
        grade = grade_service.update_grade(
            db,
            grade_id,
            grade_data,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        )

    if not grade:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Grade not found",
        )

    return grade


@router.delete(
    "/{grade_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_grade(
    grade_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin", "registrar")),
):
    try:
        deleted = grade_service.delete_grade(
            db,
            grade_id,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        )

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Grade not found",
        )

    return None
