from fastapi import FastAPI
from sqlalchemy import text
from sqlalchemy.orm import Session
from fastapi import Depends

from app.api.routes import (
    auth,
    programs,
    students,
    courses,
    academic_terms,
    course_offerings,
    enrollments,
    grades,
)
from app.db.session import get_db


app = FastAPI(
    title="Student Academic Records API",
    description="REST API for managing student academic records.",
    version="1.0.0",
)

API_V1_PREFIX = "/api/v1"

app.include_router(programs.router, prefix=API_V1_PREFIX)
app.include_router(students.router, prefix=API_V1_PREFIX)
app.include_router(courses.router, prefix=API_V1_PREFIX)
app.include_router(academic_terms.router, prefix=API_V1_PREFIX)
app.include_router(course_offerings.router, prefix=API_V1_PREFIX)
app.include_router(enrollments.router, prefix=API_V1_PREFIX)
app.include_router(grades.router, prefix=API_V1_PREFIX)
app.include_router(auth.router, prefix=API_V1_PREFIX)

@app.get("/")
def root():
    return {
        "message": "Student Academic Records API is running"
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }


@app.get("/health/database")
def database_health_check(db: Session = Depends(get_db)):
    result = db.execute(text("SELECT 1"))
    return {
        "status": "healthy",
        "database": result.scalar()
    }