from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class Enrollment(Base):
    __tablename__ = "enrollments"

    __table_args__ = (
        UniqueConstraint(
            "student_id",
            "course_offering_id",
            name="uq_student_course_offering",
        ),
    )

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True,
    )

    student_id: Mapped[int] = mapped_column(
        ForeignKey("students.id"),
        nullable=False,
    )

    course_offering_id: Mapped[int] = mapped_column(
        ForeignKey("course_offerings.id"),
        nullable=False,
    )

    enrolled_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
    )

    status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="enrolled",
    )

    student: Mapped["Student"] = relationship(
        back_populates="enrollments",
    )

    course_offering: Mapped["CourseOffering"] = relationship(
        back_populates="enrollments",
    )

    grade: Mapped["Grade | None"] = relationship(
        back_populates="enrollment",
        uselist=False,
    )