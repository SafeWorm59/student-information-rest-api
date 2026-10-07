from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class Grade(Base):
    __tablename__ = "grades"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True,
    )

    enrollment_id: Mapped[int] = mapped_column(
        ForeignKey("enrollments.id"),
        unique=True,
        nullable=False,
    )

    grade: Mapped[Decimal] = mapped_column(
        Numeric(4, 2),
        nullable=False,
    )

    remarks: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    graded_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
    )

    enrollment: Mapped["Enrollment"] = relationship(
        back_populates="grade",
    )