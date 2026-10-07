from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import User
from app.schemas import LoginRequest


def authenticate_user(
    db: Session,
    login_data: LoginRequest,
):
    statement = select(User).where(
        User.username == login_data.username
    )

    user = db.scalars(statement).first()

    if not user:
        return None

    return user