from app.core.dependencies import require_roles
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas import (
    ProgramCreate,
    ProgramResponse,
    ProgramUpdate,
)
from app.services.program_service import (
    create_program,
    delete_program,
    get_program,
    get_programs,
    update_program,
)


router = APIRouter(
    prefix="/programs",
    tags=["Programs"],
)


@router.get(
    "/",
    response_model=list[ProgramResponse],
)
def list_programs(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    search: str | None = None,
    status: str | None = None,
    sort_by: str = "id",
    sort_order: str = "asc",
    db: Session = Depends(get_db),
):
    return get_programs(
        db,
        skip=skip,
        limit=limit,
        search=search,
        status=status,
        sort_by=sort_by,
        sort_order=sort_order,
    )


@router.get(
    "/{program_id}",
    response_model=ProgramResponse,
)
def read_program(
    program_id: int,
    db: Session = Depends(get_db),
):
    program = get_program(
        db,
        program_id,
    )

    if program is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Program not found",
        )

    return program


@router.post(
    "/",
    response_model=ProgramResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_program_endpoint(
    program_data: ProgramCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin", "registrar")),
):
    try:
        return create_program(
            db,
            program_data,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        )


@router.patch(
    "/{program_id}",
    response_model=ProgramResponse,
)
def update_program_endpoint(
    program_id: int,
    program_data: ProgramUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin", "registrar")),
):
    program = get_program(
        db,
        program_id,
    )

    if program is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Program not found",
        )

    try:
        return update_program(
            db,
            program,
            program_data,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        )


@router.delete(
    "/{program_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_program_endpoint(
    program_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin", "registrar")),
):
    program = get_program(
        db,
        program_id,
    )

    if program is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Program not found",
        )

    try:
        delete_program(
            db,
            program,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        )

    return None