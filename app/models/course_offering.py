from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class CourseOffering(Base):
    __tablename__ = "course_offerings"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True,
    )

    course_id: Mapped[int] = mapped_column(
        ForeignKey("courses.id"),
        nullable=False,
    )

    term_id: Mapped[int] = mapped_column(
        ForeignKey("academic_terms.id"),
        nullable=False,
    )

    section: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )

    schedule: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    room: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    instructor: Mapped[str | None] = mapped_column(
        String(150),
        nullable=True,
    )

    capacity: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=40,
    )

    course: Mapped["Course"] = relationship(
        back_populates="offerings",
    )

    term: Mapped["AcademicTerm"] = relationship(
        back_populates="offerings",
    )

    enrollments: Mapped[list["Enrollment"]] = relationship(
        back_populates="course_offering",
    )