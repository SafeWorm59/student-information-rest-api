from app.schemas.auth import LoginRequest, TokenResponse

from app.schemas.user import (
    UserCreate,
    UserResponse,
    UserUpdate,
)

from app.schemas.program import (
    ProgramCreate,
    ProgramResponse,
    ProgramUpdate,
)

from app.schemas.student import (
    StudentCreate,
    StudentResponse,
    StudentUpdate,
)

from app.schemas.course import (
    CourseCreate,
    CourseResponse,
    CourseUpdate,
)

from app.schemas.academic_term import (
    AcademicTermCreate,
    AcademicTermResponse,
    AcademicTermUpdate,
)

from app.schemas.course_offering import (
    CourseOfferingCreate,
    CourseOfferingResponse,
    CourseOfferingUpdate,
)

from app.schemas.enrollment import (
    EnrollmentCreate,
    EnrollmentResponse,
    EnrollmentUpdate,
)

from app.schemas.grade import (
    GradeCreate,
    GradeResponse,
    GradeUpdate,
)


__all__ = [
    "LoginRequest",
    "TokenResponse",
    "UserCreate",
    "UserResponse",
    "UserUpdate",
    "ProgramCreate",
    "ProgramResponse",
    "ProgramUpdate",
    "StudentCreate",
    "StudentResponse",
    "StudentUpdate",
    "CourseCreate",
    "CourseResponse",
    "CourseUpdate",
    "AcademicTermCreate",
    "AcademicTermResponse",
    "AcademicTermUpdate",
    "CourseOfferingCreate",
    "CourseOfferingResponse",
    "CourseOfferingUpdate",
    "EnrollmentCreate",
    "EnrollmentResponse",
    "EnrollmentUpdate",
    "GradeCreate",
    "GradeResponse",
    "GradeUpdate",
]