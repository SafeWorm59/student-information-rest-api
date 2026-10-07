from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.core.dependencies import require_roles

from app.db.session import get_db
from app.schemas import (
    AcademicTermCreate,
    AcademicTermResponse,
    AcademicTermUpdate,
)
from app.services.academic_term_service import (
    create_academic_term,
    delete_academic_term,
    get_academic_term,
    get_academic_terms,
    update_academic_term,
)

router = APIRouter(
    prefix="/academic-terms",
    tags=["Academic Terms"],
)


@router.get("/", response_model=list[AcademicTermResponse])
def list_academic_terms(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    search: str | None = None,
    is_active: bool | None = None,
    sort_by: str = "id",
    sort_order: str = "asc",
    db: Session = Depends(get_db),
):
    return get_academic_terms(
        db,
        skip=skip,
        limit=limit,
        search=search,
        is_active=is_active,
        sort_by=sort_by,
        sort_order=sort_order,
    )


@router.get("/{term_id}", response_model=AcademicTermResponse)
def read_academic_term(
    term_id: int,
    db: Session = Depends(get_db),
):
    term = get_academic_term(db, term_id)

    if term is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Academic term not found",
        )

    return term


@router.post(
    "/",
    response_model=AcademicTermResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_academic_term_endpoint(
    term_data: AcademicTermCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin", "registrar")),
):
    return create_academic_term(db, term_data)


@router.patch(
    "/{term_id}",
    response_model=AcademicTermResponse,
)
def update_academic_term_endpoint(
    term_id: int,
    term_data: AcademicTermUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin", "registrar")),
):
    term = get_academic_term(db, term_id)

    if term is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Academic term not found",
        )

    return update_academic_term(db, term, term_data)


@router.delete(
    "/{term_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_academic_term_endpoint(
    term_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin", "registrar")),
):
    term = get_academic_term(db, term_id)

    if term is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Academic term not found",
        )

    try:
        delete_academic_term(db, term)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        )

    return None