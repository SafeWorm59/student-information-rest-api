from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.core.dependencies import require_roles, get_current_user
from app.models import CourseOffering, Enrollment

from app.db.session import get_db
from app.schemas import (
    CourseOfferingCreate,
    CourseOfferingResponse,
    CourseOfferingUpdate,
    EnrollmentResponse,
)
from app.services.course_offering_service import (
    create_course_offering,
    delete_course_offering,
    get_course_offering,
    get_course_offerings,
    update_course_offering,
)

router = APIRouter(
    prefix="/course-offerings",
    tags=["Course Offerings"],
)


@router.get("/", response_model=list[CourseOfferingResponse])
def list_course_offerings(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    search: str | None = None,
    course_id: int | None = None,
    term_id: int | None = None,
    sort_by: str = "id",
    sort_order: str = "asc",
    db: Session = Depends(get_db),
):
    return get_course_offerings(
        db,
        skip=skip,
        limit=limit,
        search=search,
        course_id=course_id,
        term_id=term_id,
        sort_by=sort_by,
        sort_order=sort_order,
    )

@router.get(
    "/{offering_id}/students",
    response_model=list[EnrollmentResponse],
)
def get_course_offering_students(
    offering_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    offering = db.get(CourseOffering, offering_id)

    if not offering:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course offering not found",
        )

    return (
        db.query(Enrollment)
        .filter(Enrollment.course_offering_id == offering_id)
        .order_by(Enrollment.id.asc())
        .all()
    )


@router.get("/{offering_id}", response_model=CourseOfferingResponse)
def read_course_offering(
    offering_id: int,
    db: Session = Depends(get_db),
):
    offering = get_course_offering(db, offering_id)

    if offering is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course offering not found",
        )

    return offering


@router.post(
    "/",
    response_model=CourseOfferingResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_course_offering_endpoint(
    offering_data: CourseOfferingCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin", "registrar")),
):
    try:
        return create_course_offering(db, offering_data)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        )


@router.patch(
    "/{offering_id}",
    response_model=CourseOfferingResponse,
)
def update_course_offering_endpoint(
    offering_id: int,
    offering_data: CourseOfferingUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin", "registrar")),
):
    offering = get_course_offering(db, offering_id)

    if offering is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course offering not found",
        )

    try:
        return update_course_offering(db, offering, offering_data)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        )


@router.delete(
    "/{offering_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_course_offering_endpoint(
    offering_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin", "registrar")),
):
    offering = get_course_offering(db, offering_id)

    if offering is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course offering not found",
        )

    try:
        delete_course_offering(db, offering)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        )

    return None