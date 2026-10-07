from datetime import date, timedelta
from decimal import Decimal

import pytest

from app.core.security import create_access_token, get_password_hash
from app.models import (
    AcademicTerm,
    Course,
    CourseOffering,
    Enrollment,
    Grade,
    Program,
    Student,
    User,
)


def create_user(db, username, email, password, role, is_active=True):
    user = User(
        username=username,
        email=email,
        password_hash=get_password_hash(password),
        role=role,
        is_active=is_active,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


def login(client, username, password):
    response = client.post(
        "/api/v1/auth/login",
        json={
            "username": username,
            "password": password,
        },
    )

    assert response.status_code == 200

    return response.json()["access_token"]


def create_admin_and_login(client, db, prefix="admin"):
    user = create_user(
        db,
        f"{prefix}user",
        f"{prefix}.admin@example.com",
        "Admin123!",
        "admin",
    )
    return login(client, user.username, "Admin123!")


def create_registrar_and_login(client, db, prefix="registrar"):
    user = create_user(
        db,
        f"{prefix}user",
        f"{prefix}.registrar@example.com",
        "Registrar123!",
        "registrar",
    )
    return login(client, user.username, "Registrar123!")


def auth_headers(token):
    return {"Authorization": f"Bearer {token}"}


def create_program(db, code, name):
    program = Program(
        code=code,
        name=name,
        description="Test program",
    )
    db.add(program)
    db.commit()
    db.refresh(program)
    return program


def create_student(db, number, first, last, email, program_id, year=2, status="active"):
    student = Student(
        student_number=number,
        first_name=first,
        last_name=last,
        email=email,
        program_id=program_id,
        year_level=year,
        status=status,
    )
    db.add(student)
    db.commit()
    db.refresh(student)
    return student


def create_course(db, code, title):
    course = Course(
        code=code,
        title=title,
        description="Test course",
        units=3,
    )
    db.add(course)
    db.commit()
    db.refresh(course)
    return course


def create_term(db, name, school_year):
    term = AcademicTerm(
        name=name,
        school_year=school_year,
        start_date=date(2025, 1, 1),
        end_date=date(2025, 6, 30),
        is_active=True,
    )
    db.add(term)
    db.commit()
    db.refresh(term)
    return term


def create_offering(db, course_id, term_id, section):
    offering = CourseOffering(
        course_id=course_id,
        term_id=term_id,
        section=section,
        schedule="MWF 8:00-11:00",
        room="R-101",
        instructor="Test Instructor",
        capacity=40,
    )
    db.add(offering)
    db.commit()
    db.refresh(offering)
    return offering


def create_enrollment(db, student_id, offering_id):
    enrollment = Enrollment(
        student_id=student_id,
        course_offering_id=offering_id,
        status="enrolled",
    )
    db.add(enrollment)
    db.commit()
    db.refresh(enrollment)
    return enrollment


def create_grade(db, enrollment_id, grade_value=1.50, remarks="Passed"):
    grade = Grade(
        enrollment_id=enrollment_id,
        grade=grade_value,
        remarks=remarks,
    )
    db.add(grade)
    db.commit()
    db.refresh(grade)
    return grade


def create_academic_chain(db, prefix="chain"):
    program = create_program(db, f"{prefix}-PROG", f"{prefix} Program")
    student = create_student(
        db,
        f"{prefix}-0001",
        "Chain",
        "Student",
        f"{prefix}.student@example.com",
        program.id,
    )
    course = create_course(db, f"{prefix}101", f"{prefix} Course")
    term = create_term(db, f"{prefix} Term", "2025-2026")
    offering = create_offering(db, course.id, term.id, f"{prefix}-1A")
    enrollment = create_enrollment(db, student.id, offering.id)
    return program, student, course, term, offering, enrollment


def test_root(client):
    response = client.get("/")

    assert response.status_code == 200
    assert response.json()["message"] == "Student Academic Records API is running"


def test_health(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_database_health(client):
    response = client.get("/health/database")

    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
    assert response.json()["database"] == 1


def test_login_success(client, db):
    create_user(
        db,
        "testadmin",
        "testadmin@example.com",
        "TestAdmin123!",
        "admin",
    )

    response = client.post(
        "/api/v1/auth/login",
        json={
            "username": "testadmin",
            "password": "TestAdmin123!",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_invalid_password(client, db):
    create_user(
        db,
        "wrongpass",
        "wrongpass@example.com",
        "Correct123!",
        "admin",
    )

    response = client.post(
        "/api/v1/auth/login",
        json={
            "username": "wrongpass",
            "password": "Wrong123!",
        },
    )

    assert response.status_code == 401


def test_login_nonexistent_user(client):
    response = client.post(
        "/api/v1/auth/login",
        json={
            "username": "does-not-exist",
            "password": "Wrong123!",
        },
    )

    assert response.status_code == 401


def test_login_inactive_user(client, db):
    create_user(
        db,
        "inactiveuser",
        "inactive@example.com",
        "Correct123!",
        "student",
        is_active=False,
    )

    response = client.post(
        "/api/v1/auth/login",
        json={
            "username": "inactiveuser",
            "password": "Correct123!",
        },
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "User account is inactive"


def test_malformed_bearer_token_rejected(client, db):
    create_user(
        db,
        "malformedtokenuser",
        "malformedtoken@example.com",
        "Correct123!",
        "student",
    )

    response = client.get(
        "/api/v1/students/me",
        headers={"Authorization": "Bearer not-a-valid-token"},
    )

    assert response.status_code == 401


def test_student_pagination_validation(client):
    response = client.get("/api/v1/students/?limit=-10")

    assert response.status_code == 422


def test_student_skip_validation(client):
    response = client.get("/api/v1/students/?skip=-10")

    assert response.status_code == 422


def test_student_limit_maximum(client):
    response = client.get("/api/v1/students/?limit=101")

    assert response.status_code == 422


def test_invalid_grade_validation(client, db):
    program = create_program(db, "GRDVAL", "Grade Validation Program")
    student = create_student(
        db,
        "GRDVAL-0001",
        "Grade",
        "Validation",
        "grade.validation@example.com",
        program.id,
    )
    term = create_term(db, "Grade Validation Term", "2025-2026")
    course = create_course(db, "GRDVAL101", "Grade Validation Course")
    offering = create_offering(db, course.id, term.id, "GRDVAL-1A")
    enrollment = create_enrollment(db, student.id, offering.id)
    token = create_admin_and_login(client, db, "gradevalidation")

    response = client.post(
        "/api/v1/grades/",
        headers=auth_headers(token),
        json={
            "enrollment_id": enrollment.id,
            "grade": 150,
        },
    )

    assert response.status_code == 422


def test_unauthenticated_student_access(client):
    response = client.get("/api/v1/students/1")

    assert response.status_code == 401


def test_student_cannot_create_enrollment(client, db):
    create_user(
        db,
        "teststudent",
        "teststudent@example.com",
        "TestStudent123!",
        "student",
    )

    token = login(
        client,
        "teststudent",
        "TestStudent123!",
    )

    response = client.post(
        "/api/v1/enrollments/",
        headers={
            "Authorization": f"Bearer {token}",
        },
        json={
            "student_id": 1,
            "course_offering_id": 1,
            "status": "enrolled",
        },
    )

    assert response.status_code == 403


# ---------------------------------------------------------------------------
# Student self-access (/me) and object-level authorization tests
# ---------------------------------------------------------------------------


def _setup_student_self_access_data(db, prefix="me"):
    """Create a program, student, user, and related records for /me tests."""
    program = create_program(db, f"{prefix}-PROG", f"{prefix} Program")
    student = create_student(
        db,
        f"{prefix}-0001",
        "Self",
        "Access",
        f"{prefix}.student@test.com",
        program.id,
    )
    user = create_user(
        db,
        f"{prefix}user",
        f"{prefix}.student@test.com",
        "Student123!",
        "student",
    )
    return program, student, user


def _setup_student_other_data(db, prefix="other"):
    """Create a second student, user, and related records for access-denied tests."""
    program = create_program(db, f"{prefix}-PROG", f"{prefix} Program")
    student = create_student(
        db,
        f"{prefix}-0002",
        "Other",
        "Student",
        f"{prefix}.student@test.com",
        program.id,
    )
    user = create_user(
        db,
        f"{prefix}user",
        f"{prefix}.student@test.com",
        "OtherStudent123!",
        "student",
    )
    return program, student, user


def test_student_me_returns_own_record(client, db):
    program, student, _ = _setup_student_self_access_data(db, "meown")

    token = login(client, "meownuser", "Student123!")

    response = client.get(
        "/api/v1/students/me",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == student.id
    assert data["email"] == "meown.student@test.com"
    assert data["student_number"] == "meown-0001"


def test_student_me_unauthenticated_rejected(client):
    response = client.get("/api/v1/students/me")

    assert response.status_code == 401


def test_student_me_no_matching_student_rejected(client, db):
    """A student user whose email has no matching Student record gets 403."""
    create_user(
        db,
        "nostatstudent",
        "nostat.student@test.com",
        "Student123!",
        "student",
    )

    token = login(client, "nostatstudent", "Student123!")

    response = client.get(
        "/api/v1/students/me",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 403


def test_student_me_enrollments_returns_own_only(client, db):
    prog_me, stud_me, _ = _setup_student_self_access_data(db, "meenr")
    prog_other, stud_other, _ = _setup_student_other_data(db, "meenother")

    term = create_term(db, "1st Sem", "2025-2026")
    course = create_course(db, "MEENR101", "Self-Access Course")
    offering = create_offering(db, course.id, term.id, "MEENR-1A")

    enroll_me = create_enrollment(db, stud_me.id, offering.id)
    enroll_other = create_enrollment(db, stud_other.id, offering.id)

    token = login(client, "meenruser", "Student123!")

    response = client.get(
        "/api/v1/enrollments/me",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["student_id"] == stud_me.id
    assert data[0]["id"] == enroll_me.id


def test_student_me_enrollments_unauthenticated_rejected(client):
    response = client.get("/api/v1/enrollments/me")

    assert response.status_code == 401


def test_student_me_grades_returns_own_only(client, db):
    prog_me, stud_me, _ = _setup_student_self_access_data(db, "megrd")
    prog_other, stud_other, _ = _setup_student_other_data(db, "megrdother")

    term = create_term(db, "2nd Sem", "2025-2026")
    course = create_course(db, "MEGRD101", "Grades Self-Access Course")
    offering = create_offering(db, course.id, term.id, "MEGRD-1A")

    enroll_me = create_enrollment(db, stud_me.id, offering.id)
    enroll_other = create_enrollment(db, stud_other.id, offering.id)

    grade_me = create_grade(db, enroll_me.id, 1.75, "Passed")
    grade_other = create_grade(db, enroll_other.id, 2.00, "Passed")

    token = login(client, "megrduser", "Student123!")

    response = client.get(
        "/api/v1/grades/me",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["enrollment_id"] == enroll_me.id
    assert data[0]["id"] == grade_me.id


def test_student_me_grades_unauthenticated_rejected(client):
    response = client.get("/api/v1/grades/me")

    assert response.status_code == 401


def test_student_cannot_access_other_student_record(client, db):
    _, _, _ = _setup_student_self_access_data(db, "accs1")
    prog_other, stud_other, _ = _setup_student_other_data(db, "accsother1")

    token = login(client, "accs1user", "Student123!")

    response = client.get(
        f"/api/v1/students/{stud_other.id}",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 403


def test_student_can_access_own_student_record(client, db):
    _, stud_me, _ = _setup_student_self_access_data(db, "accs2")

    token = login(client, "accs2user", "Student123!")

    response = client.get(
        f"/api/v1/students/{stud_me.id}",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == stud_me.id


def test_student_cannot_access_other_student_enrollment(client, db):
    prog_me, stud_me, _ = _setup_student_self_access_data(db, "enc1")
    prog_other, stud_other, _ = _setup_student_other_data(db, "encother1")

    term = create_term(db, "Enc Term", "2025-2026")
    course = create_course(db, "ENC101", "Enrollment Course")
    offering = create_offering(db, course.id, term.id, "ENC-1A")

    enroll_me = create_enrollment(db, stud_me.id, offering.id)
    enroll_other = create_enrollment(db, stud_other.id, offering.id)

    token = login(client, "enc1user", "Student123!")

    response = client.get(
        f"/api/v1/enrollments/{enroll_other.id}",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 403


def test_student_can_access_own_enrollment(client, db):
    prog_me, stud_me, _ = _setup_student_self_access_data(db, "enc2")

    term = create_term(db, "Enc2 Term", "2025-2026")
    course = create_course(db, "ENC201", "Own Enrollment Course")
    offering = create_offering(db, course.id, term.id, "ENC2-1A")

    enroll_me = create_enrollment(db, stud_me.id, offering.id)

    token = login(client, "enc2user", "Student123!")

    response = client.get(
        f"/api/v1/enrollments/{enroll_me.id}",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == enroll_me.id


def test_student_cannot_access_other_student_grade(client, db):
    prog_me, stud_me, _ = _setup_student_self_access_data(db, "grd1")
    prog_other, stud_other, _ = _setup_student_other_data(db, "grdother1")

    term = create_term(db, "Grd Term", "2025-2026")
    course = create_course(db, "GRD101", "Grade Course")
    offering = create_offering(db, course.id, term.id, "GRD-1A")

    enroll_me = create_enrollment(db, stud_me.id, offering.id)
    enroll_other = create_enrollment(db, stud_other.id, offering.id)

    grade_me = create_grade(db, enroll_me.id, 1.50, "Passed")
    grade_other = create_grade(db, enroll_other.id, 2.25, "Passed")

    token = login(client, "grd1user", "Student123!")

    response = client.get(
        f"/api/v1/grades/{grade_other.id}",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 403


def test_student_can_access_own_grade(client, db):
    prog_me, stud_me, _ = _setup_student_self_access_data(db, "grd2")

    term = create_term(db, "Grd2 Term", "2025-2026")
    course = create_course(db, "GRD201", "Own Grade Course")
    offering = create_offering(db, course.id, term.id, "GRD2-1A")

    enroll_me = create_enrollment(db, stud_me.id, offering.id)
    grade_me = create_grade(db, enroll_me.id, 1.75, "Passed")

    token = login(client, "grd2user", "Student123!")

    response = client.get(
        f"/api/v1/grades/{grade_me.id}",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == grade_me.id


def test_student_cannot_create_grade(client, db):
    _setup_student_self_access_data(db, "gradecreate")

    token = login(client, "gradecreateuser", "Student123!")

    response = client.post(
        "/api/v1/grades/",
        headers=auth_headers(token),
        json={
            "enrollment_id": 1,
            "grade": 1.75,
            "remarks": "Unauthorized",
        },
    )

    assert response.status_code == 403

def test_program_create_success(client, db):
    token = create_admin_and_login(client, db)
    response = client.post(
        "/api/v1/programs/",
        headers=auth_headers(token),
        json={
            "code": "CRUD-001",
            "name": "CRUD Program",
            "description": "Test program for CRUD",
        },
    )
    
    print(response.status_code)
    print(response.json())
    assert response.status_code == 201
    data = response.json()
    assert data["code"] == "CRUD-001"
    assert data["name"] == "CRUD Program"
    assert "id" in data


def test_program_get_success(client, db):
    token = create_admin_and_login(client, db)
    response = client.post(
        "/api/v1/programs/",
        headers=auth_headers(token),
        json={
            "code": "CRUD-002",
            "name": "CRUD Program Get",
            "description": "Test program for GET",
        },
    )

    assert response.status_code == 201
    program_id = response.json()["id"]

    response = client.get(
        f"/api/v1/programs/{program_id}",
        headers=auth_headers(token),
    )

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == program_id
    assert data["code"] == "CRUD-002"
    assert data["name"] == "CRUD Program Get"


def test_program_update_success(client, db):
    token = create_admin_and_login(client, db)
    response = client.post(
        "/api/v1/programs/",
        headers=auth_headers(token),
        json={
            "code": "CRUD-003",
            "name": "CRUD Program Update",
            "description": "Original description",
        },
    )

    assert response.status_code == 201
    program_id = response.json()["id"]

    response = client.patch(
        f"/api/v1/programs/{program_id}",
        headers=auth_headers(token),
        json={
            "name": "CRUD Program Updated",
            "description": "Updated description",
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == program_id
    assert data["name"] == "CRUD Program Updated"
    assert data["description"] == "Updated description"


def test_program_delete_success(client, db):
    token = create_admin_and_login(client, db)
    response = client.post(
        "/api/v1/programs/",
        headers=auth_headers(token),
        json={
            "code": "CRUD-004",
            "name": "CRUD Program Delete",
            "description": "Test program for DELETE",
        },
    )

    assert response.status_code == 201
    program_id = response.json()["id"]

    response = client.delete(
        f"/api/v1/programs/{program_id}",
        headers=auth_headers(token),
    )

    assert response.status_code == 204


def test_program_deleted_cannot_be_retrieved(client, db):
    token = create_admin_and_login(client, db)
    response = client.post(
        "/api/v1/programs/",
        headers=auth_headers(token),
        json={
            "code": "CRUD-005",
            "name": "CRUD Program Deleted",
            "description": "Test program for delete verification",
        },
    )

    assert response.status_code == 201
    program_id = response.json()["id"]

    client.delete(
        f"/api/v1/programs/{program_id}",
        headers=auth_headers(token),
    )

    response = client.get(
        f"/api/v1/programs/{program_id}",
        headers=auth_headers(token),
    )

    assert response.status_code == 404

# ============================================================
# STUDENT CRUD, VALIDATION, AND AUTHORIZATION TESTS
# ============================================================

def test_student_create_success(client, db):
    token = create_admin_and_login(client, db)

    program = create_program(
        db,
        "STU-001",
        "Student Test Program",
    )

    response = client.post(
        "/api/v1/students/",
        headers=auth_headers(token),
        json={
            "student_number": "STU-0001",
            "first_name": "Juan",
            "middle_name": "Dela",
            "last_name": "Cruz",
            "suffix": None,
            "birth_date": "2004-01-15",
            "email": "juan.create@test.com",
            "contact_number": "09171234567",
            "address": "Maramag, Bukidnon",
            "program_id": program.id,
            "year_level": 1,
            "status": "active",
        },
    )

    assert response.status_code == 201

    data = response.json()
    assert data["student_number"] == "STU-0001"
    assert data["first_name"] == "Juan"
    assert data["last_name"] == "Cruz"
    assert data["program_id"] == program.id


def test_student_get_success(client, db):
    token = create_admin_and_login(client, db)

    program = create_program(
        db,
        "STU-002",
        "Student Get Program",
    )

    student = create_student(
        db,
        "STU-0002",
        "Maria",
        "Santos",
        "maria.get@test.com",
        program.id,
    )

    response = client.get(
        f"/api/v1/students/{student.id}",
        headers=auth_headers(token),
    )

    assert response.status_code == 200

    data = response.json()
    assert data["id"] == student.id
    assert data["student_number"] == "STU-0002"
    assert data["first_name"] == "Maria"


def test_student_update_success(client, db):
    token = create_admin_and_login(client, db)

    program = create_program(
        db,
        "STU-003",
        "Student Update Program",
    )

    student = create_student(
        db,
        "STU-0003",
        "Pedro",
        "Garcia",
        "pedro.update@test.com",
        program.id,
    )

    response = client.patch(
        f"/api/v1/students/{student.id}",
        headers=auth_headers(token),
        json={
            "first_name": "Pedro Updated",
            "contact_number": "09991234567",
        },
    )

    assert response.status_code == 200

    data = response.json()
    assert data["first_name"] == "Pedro Updated"


def test_student_duplicate_student_number_rejected(client, db):
    token = create_admin_and_login(client, db)

    program = create_program(
        db,
        "STU-004",
        "Student Duplicate Program",
    )

    create_student(
        db,
        "STU-0004",
        "First",
        "Student",
        "first.student@test.com",
        program.id,
    )

    response = client.post(
        "/api/v1/students/",
        headers=auth_headers(token),
        json={
            "student_number": "STU-0004",
            "first_name": "Second",
            "middle_name": None,
            "last_name": "Student",
            "suffix": None,
            "birth_date": "2004-05-10",
            "email": "second.student@test.com",
            "contact_number": "09170000000",
            "address": "Bukidnon",
            "program_id": program.id,
            "year_level": 1,
            "status": "active",
        },
    )

    assert response.status_code in (400, 409, 422)


def test_student_invalid_email_rejected(client, db):
    token = create_admin_and_login(client, db)

    program = create_program(
        db,
        "STU-005",
        "Student Email Program",
    )

    response = client.post(
        "/api/v1/students/",
        headers=auth_headers(token),
        json={
            "student_number": "STU-0005",
            "first_name": "Invalid",
            "middle_name": None,
            "last_name": "Email",
            "suffix": None,
            "birth_date": "2004-05-10",
            "email": "not-an-email",
            "contact_number": "09170000000",
            "address": "Bukidnon",
            "program_id": program.id,
            "year_level": 1,
            "status": "active",
        },
    )

    assert response.status_code == 422


def test_student_not_found(client, db):
    token = create_admin_and_login(client, db)

    response = client.get(
        "/api/v1/students/999999",
        headers=auth_headers(token),
    )

    assert response.status_code == 404


def test_student_cannot_create_student(client, db):
    create_user(
        db,
        "studentcrud",
        "studentcrud@test.com",
        "Student123!",
        "student",
    )

    token = login(
        client,
        "studentcrud",
        "Student123!",
    )

    program = create_program(
        db,
        "STU-006",
        "Student Authorization Program",
    )

    response = client.post(
        "/api/v1/students/",
        headers=auth_headers(token),
        json={
            "student_number": "STU-0006",
            "first_name": "Unauthorized",
            "middle_name": None,
            "last_name": "Student",
            "suffix": None,
            "birth_date": "2004-05-10",
            "email": "unauthorized.student@test.com",
            "contact_number": "09170000000",
            "address": "Bukidnon",
            "program_id": program.id,
            "year_level": 1,
            "status": "active",
        },
    )

    assert response.status_code == 403


# ============================================================
# ACADEMIC TERM CRUD, VALIDATION, AND AUTHORIZATION TESTS
# ============================================================

def test_academic_term_create_success(client, db):
    token = create_admin_and_login(client, db)

    response = client.post(
        "/api/v1/academic-terms/",
        headers=auth_headers(token),
        json={
            "name": "First Semester",
            "school_year": "2025-2026",
            "start_date": "2025-08-01",
            "end_date": "2025-12-20",
            "is_active": True,
        },
    )

    assert response.status_code == 201

    data = response.json()
    assert data["name"] == "First Semester"
    assert data["school_year"] == "2025-2026"
    assert data["is_active"] is True


def test_academic_term_get_success(client, db):
    token = create_admin_and_login(client, db)

    term = create_term(
        db,
        "Second Semester",
        "2025-2026",
    )

    response = client.get(
        f"/api/v1/academic-terms/{term.id}",
        headers=auth_headers(token),
    )

    assert response.status_code == 200

    data = response.json()
    assert data["id"] == term.id
    assert data["name"] == "Second Semester"
    assert data["school_year"] == "2025-2026"


def test_academic_term_update_success(client, db):
    token = create_admin_and_login(client, db)

    term = create_term(
        db,
        "First Semester",
        "2025-2026",
    )

    response = client.patch(
        f"/api/v1/academic-terms/{term.id}",
        headers=auth_headers(token),
        json={
            "name": "Updated First Semester",
            "is_active": False,
        },
    )

    assert response.status_code == 200

    data = response.json()
    assert data["name"] == "Updated First Semester"
    assert data["is_active"] is False


def test_academic_term_delete_success(client, db):
    token = create_admin_and_login(client, db)

    term = create_term(
        db,
        "Term To Delete",
        "2025-2026",
    )

    response = client.delete(
        f"/api/v1/academic-terms/{term.id}",
        headers=auth_headers(token),
    )

    assert response.status_code in (200, 204)


def test_academic_term_deleted_cannot_be_retrieved(client, db):
    token = create_admin_and_login(client, db)

    term = create_term(
        db,
        "Deleted Term",
        "2025-2026",
    )

    delete_response = client.delete(
        f"/api/v1/academic-terms/{term.id}",
        headers=auth_headers(token),
    )

    assert delete_response.status_code in (200, 204)

    get_response = client.get(
        f"/api/v1/academic-terms/{term.id}",
        headers=auth_headers(token),
    )

    assert get_response.status_code == 404


def test_academic_term_not_found(client, db):
    token = create_admin_and_login(client, db)

    response = client.get(
        "/api/v1/academic-terms/999999",
        headers=auth_headers(token),
    )

    assert response.status_code == 404


def test_academic_term_invalid_data_rejected(client, db):
    token = create_admin_and_login(client, db)

    response = client.post(
        "/api/v1/academic-terms/",
        headers=auth_headers(token),
        json={
            "name": "A",
            "school_year": "25",
            "start_date": "not-a-date",
            "end_date": "2025-12-20",
            "is_active": True,
        },
    )

    assert response.status_code == 422


def test_student_cannot_create_academic_term(client, db):
    create_user(
        db,
        "studentterm",
        "studentterm@test.com",
        "Student123!",
        "student",
    )

    token = login(
        client,
        "studentterm",
        "Student123!",
    )

    response = client.post(
        "/api/v1/academic-terms/",
        headers=auth_headers(token),
        json={
            "name": "Unauthorized Term",
            "school_year": "2025-2026",
            "start_date": "2025-08-01",
            "end_date": "2025-12-20",
            "is_active": True,
        },
    )

    assert response.status_code == 403


# ============================================================
# COURSE OFFERING CRUD, VALIDATION, AND AUTHORIZATION TESTS
# ============================================================

def test_course_offering_create_success(client, db):
    token = create_admin_and_login(client, db)

    course = create_course(
        db,
        "OFF101",
        "Offering Test Course",
    )

    term = create_term(
        db,
        "Offering Test Term",
        "2025-2026",
    )

    response = client.post(
        "/api/v1/course-offerings/",
        headers=auth_headers(token),
        json={
            "course_id": course.id,
            "term_id": term.id,
            "section": "1A",
            "schedule": "MWF 8:00-9:00",
            "room": "R-101",
            "instructor": "Test Instructor",
            "capacity": 40,
        },
    )

    assert response.status_code == 201

    data = response.json()
    assert data["course_id"] == course.id
    assert data["term_id"] == term.id
    assert data["section"] == "1A"
    assert data["capacity"] == 40


def test_course_offering_get_success(client, db):
    token = create_admin_and_login(client, db)

    course = create_course(
        db,
        "OFF102",
        "Offering Get Course",
    )

    term = create_term(
        db,
        "Offering Get Term",
        "2025-2026",
    )

    offering = create_offering(
        db,
        course.id,
        term.id,
        "2A",
    )

    response = client.get(
        f"/api/v1/course-offerings/{offering.id}",
        headers=auth_headers(token),
    )

    assert response.status_code == 200

    data = response.json()
    assert data["id"] == offering.id
    assert data["course_id"] == course.id
    assert data["term_id"] == term.id
    assert data["section"] == "2A"


def test_course_offering_update_success(client, db):
    token = create_admin_and_login(client, db)

    course = create_course(
        db,
        "OFF103",
        "Offering Update Course",
    )

    term = create_term(
        db,
        "Offering Update Term",
        "2025-2026",
    )

    offering = create_offering(
        db,
        course.id,
        term.id,
        "3A",
    )

    response = client.patch(
        f"/api/v1/course-offerings/{offering.id}",
        headers=auth_headers(token),
        json={
            "section": "3B",
            "room": "R-202",
            "capacity": 50,
        },
    )

    assert response.status_code == 200

    data = response.json()
    assert data["section"] == "3B"
    assert data["room"] == "R-202"
    assert data["capacity"] == 50


def test_course_offering_delete_success(client, db):
    token = create_admin_and_login(client, db)

    course = create_course(
        db,
        "OFF104",
        "Offering Delete Course",
    )

    term = create_term(
        db,
        "Offering Delete Term",
        "2025-2026",
    )

    offering = create_offering(
        db,
        course.id,
        term.id,
        "4A",
    )

    response = client.delete(
        f"/api/v1/course-offerings/{offering.id}",
        headers=auth_headers(token),
    )

    assert response.status_code in (200, 204)


def test_course_offering_deleted_cannot_be_retrieved(client, db):
    token = create_admin_and_login(client, db)

    course = create_course(
        db,
        "OFF105",
        "Offering Deleted Course",
    )

    term = create_term(
        db,
        "Offering Deleted Term",
        "2025-2026",
    )

    offering = create_offering(
        db,
        course.id,
        term.id,
        "5A",
    )

    delete_response = client.delete(
        f"/api/v1/course-offerings/{offering.id}",
        headers=auth_headers(token),
    )

    assert delete_response.status_code in (200, 204)

    get_response = client.get(
        f"/api/v1/course-offerings/{offering.id}",
        headers=auth_headers(token),
    )

    assert get_response.status_code == 404


def test_course_offering_not_found(client, db):
    token = create_admin_and_login(client, db)

    response = client.get(
        "/api/v1/course-offerings/999999",
        headers=auth_headers(token),
    )

    assert response.status_code == 404


def test_course_offering_invalid_data_rejected(client, db):
    token = create_admin_and_login(client, db)

    course = create_course(
        db,
        "OFF106",
        "Offering Validation Course",
    )

    term = create_term(
        db,
        "Offering Validation Term",
        "2025-2026",
    )

    response = client.post(
        "/api/v1/course-offerings/",
        headers=auth_headers(token),
        json={
            "course_id": course.id,
            "term_id": term.id,
            "section": "",
            "schedule": "MWF 8:00-9:00",
            "room": "R-101",
            "instructor": "Test Instructor",
            "capacity": 0,
        },
    )

    assert response.status_code == 422


def test_course_offering_invalid_course_rejected(client, db):
    token = create_admin_and_login(client, db)

    term = create_term(
        db,
        "Offering Invalid Course Term",
        "2025-2026",
    )

    response = client.post(
        "/api/v1/course-offerings/",
        headers=auth_headers(token),
        json={
            "course_id": 999999,
            "term_id": term.id,
            "section": "1A",
            "schedule": "MWF 8:00-9:00",
            "room": "R-101",
            "instructor": "Test Instructor",
            "capacity": 40,
        },
    )

    assert response.status_code in (400, 404, 409, 422)


def test_course_offering_invalid_term_rejected(client, db):
    token = create_admin_and_login(client, db)

    course = create_course(
        db,
        "OFF107",
        "Offering Invalid Term Course",
    )

    response = client.post(
        "/api/v1/course-offerings/",
        headers=auth_headers(token),
        json={
            "course_id": course.id,
            "term_id": 999999,
            "section": "1A",
            "schedule": "MWF 8:00-9:00",
            "room": "R-101",
            "instructor": "Test Instructor",
            "capacity": 40,
        },
    )

    assert response.status_code in (400, 404, 409, 422)


def test_student_cannot_create_course_offering(client, db):
    create_user(
        db,
        "studentoffering",
        "studentoffering@test.com",
        "Student123!",
        "student",
    )

    token = login(
        client,
        "studentoffering",
        "Student123!",
    )

    course = create_course(
        db,
        "OFF108",
        "Unauthorized Offering Course",
    )

    term = create_term(
        db,
        "Unauthorized Offering Term",
        "2025-2026",
    )

    response = client.post(
        "/api/v1/course-offerings/",
        headers=auth_headers(token),
        json={
            "course_id": course.id,
            "term_id": term.id,
            "section": "1A",
            "schedule": "MWF 8:00-9:00",
            "room": "R-101",
            "instructor": "Test Instructor",
            "capacity": 40,
        },
    )

    assert response.status_code == 403


# ============================================================
# COURSE CRUD, VALIDATION, AND AUTHORIZATION TESTS
# ============================================================

def test_course_create_success(client, db):
    token = create_admin_and_login(client, db)

    response = client.post(
        "/api/v1/courses/",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "code": "IT999",
            "title": "Advanced REST API Testing",
            "description": "Test course for API CRUD operations.",
            "units": 3,
        },
    )

    assert response.status_code == 201

    data = response.json()
    assert data["code"] == "IT999"
    assert data["title"] == "Advanced REST API Testing"
    assert data["units"] == 3


def test_course_get_success(client, db):
    token = create_admin_and_login(client, db)

    create_response = client.post(
        "/api/v1/courses/",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "code": "IT998",
            "title": "Course Retrieval Test",
            "description": "Testing course retrieval.",
            "units": 3,
        },
    )

    assert create_response.status_code == 201
    course_id = create_response.json()["id"]

    response = client.get(
        f"/api/v1/courses/{course_id}",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200

    data = response.json()
    assert data["id"] == course_id
    assert data["code"] == "IT998"


def test_course_update_success(client, db):
    token = create_admin_and_login(client, db)

    create_response = client.post(
        "/api/v1/courses/",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "code": "IT997",
            "title": "Original Course Title",
            "description": "Original description.",
            "units": 3,
        },
    )

    assert create_response.status_code == 201
    course_id = create_response.json()["id"]

    response = client.patch(
        f"/api/v1/courses/{course_id}",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "title": "Updated Course Title",
            "description": "Updated description.",
        },
    )

    assert response.status_code == 200

    data = response.json()
    assert data["title"] == "Updated Course Title"
    assert data["description"] == "Updated description."


def test_course_delete_success(client, db):
    token = create_admin_and_login(client, db)

    create_response = client.post(
        "/api/v1/courses/",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "code": "IT996",
            "title": "Course Deletion Test",
            "description": "Course to be deleted.",
            "units": 3,
        },
    )

    assert create_response.status_code == 201
    course_id = create_response.json()["id"]

    response = client.delete(
        f"/api/v1/courses/{course_id}",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 204


def test_course_deleted_cannot_be_retrieved(client, db):
    token = create_admin_and_login(client, db)

    create_response = client.post(
        "/api/v1/courses/",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "code": "IT995",
            "title": "Deleted Course",
            "description": "This course will be deleted.",
            "units": 3,
        },
    )

    assert create_response.status_code == 201
    course_id = create_response.json()["id"]

    delete_response = client.delete(
        f"/api/v1/courses/{course_id}",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert delete_response.status_code == 204

    get_response = client.get(
        f"/api/v1/courses/{course_id}",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert get_response.status_code == 404


def test_course_duplicate_code_rejected(client, db):
    token = create_admin_and_login(client, db)

    first_response = client.post(
        "/api/v1/courses/",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "code": "IT994",
            "title": "First Course",
            "description": "First course using this code.",
            "units": 3,
        },
    )

    assert first_response.status_code == 201

    second_response = client.post(
        "/api/v1/courses/",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "code": "IT994",
            "title": "Duplicate Course",
            "description": "Duplicate course code test.",
            "units": 3,
        },
    )

    assert second_response.status_code in (400, 409, 422)


def test_course_invalid_data_rejected(client, db):
    token = create_admin_and_login(client, db)

    response = client.post(
        "/api/v1/courses/",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "code": "",
            "title": "",
            "description": "Invalid course data.",
            "units": -1,
        },
    )

    assert response.status_code in (400, 422)


def test_student_cannot_create_course(client, db):
    create_user(
        db,
        "student1",
        "student1@test.com",
        "Student123!",
        "student",
    )

    token = login(client, "student1", "Student123!")

    response = client.post(
        "/api/v1/courses/",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "code": "IT993",
            "title": "Unauthorized Course",
            "description": "Student should not create courses.",
            "units": 3,
        },
    )

    assert response.status_code == 403

def test_course_not_found(client, db):
    token = create_admin_and_login(client, db)

    response = client.get(
        "/api/v1/courses/999999",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 404

# ============================================================
# ENROLLMENT BUSINESS, CRUD, VALIDATION, AND AUTHORIZATION TESTS
# ============================================================

def test_enrollment_create_success(client, db):
    token = create_admin_and_login(client, db)

    program = create_program(
        db,
        "ENR001-P",
        "Enrollment Create Program",
    )

    student = create_student(
        db,
        "ENR001-0001",
        "Create",
        "Enrollment",
        "create.enrollment@test.com",
        program.id,
    )

    course = create_course(
        db,
        "ENR001",
        "Enrollment Create Course",
    )

    term = create_term(
        db,
        "Enrollment Create Term",
        "2025-2026",
    )

    offering = create_offering(
        db,
        course.id,
        term.id,
        "1A",
    )

    response = client.post(
        "/api/v1/enrollments/",
        headers=auth_headers(token),
        json={
            "student_id": student.id,
            "course_offering_id": offering.id,
            "status": "enrolled",
        },
    )

    assert response.status_code == 201

    data = response.json()
    assert data["student_id"] == student.id
    assert data["course_offering_id"] == offering.id
    assert data["status"] == "enrolled"
    assert "id" in data
    assert "enrolled_at" in data


def test_enrollment_get_success(client, db):
    token = create_admin_and_login(client, db)

    program, student, course, term, offering, enrollment = create_academic_chain(
        db,
        "ENR002",
    )

    response = client.get(
        f"/api/v1/enrollments/{enrollment.id}",
        headers=auth_headers(token),
    )

    assert response.status_code == 200

    data = response.json()
    assert data["id"] == enrollment.id
    assert data["student_id"] == student.id
    assert data["course_offering_id"] == offering.id


def test_enrollment_update_success(client, db):
    token = create_admin_and_login(client, db)

    program, student, course, term, offering, enrollment = create_academic_chain(
        db,
        "ENR003",
    )

    response = client.patch(
        f"/api/v1/enrollments/{enrollment.id}",
        headers=auth_headers(token),
        json={
            "status": "dropped",
        },
    )

    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "dropped"


def test_enrollment_delete_success(client, db):
    token = create_admin_and_login(client, db)

    program, student, course, term, offering, enrollment = create_academic_chain(
        db,
        "ENR004",
    )

    response = client.delete(
        f"/api/v1/enrollments/{enrollment.id}",
        headers=auth_headers(token),
    )

    assert response.status_code in (200, 204)


def test_enrollment_deleted_cannot_be_retrieved(client, db):
    token = create_admin_and_login(client, db)

    program, student, course, term, offering, enrollment = create_academic_chain(
        db,
        "ENR005",
    )

    delete_response = client.delete(
        f"/api/v1/enrollments/{enrollment.id}",
        headers=auth_headers(token),
    )

    assert delete_response.status_code in (200, 204)

    get_response = client.get(
        f"/api/v1/enrollments/{enrollment.id}",
        headers=auth_headers(token),
    )

    assert get_response.status_code == 404


def test_enrollment_not_found(client, db):
    token = create_admin_and_login(client, db)

    response = client.get(
        "/api/v1/enrollments/999999",
        headers=auth_headers(token),
    )

    assert response.status_code == 404


def test_enrollment_invalid_student_rejected(client, db):
    token = create_admin_and_login(client, db)

    program = create_program(
        db,
        "ENR006-P",
        "Enrollment Invalid Student Program",
    )

    course = create_course(
        db,
        "ENR006",
        "Enrollment Invalid Student Course",
    )

    term = create_term(
        db,
        "Enrollment Invalid Student Term",
        "2025-2026",
    )

    offering = create_offering(
        db,
        course.id,
        term.id,
        "1A",
    )

    response = client.post(
        "/api/v1/enrollments/",
        headers=auth_headers(token),
        json={
            "student_id": 999999,
            "course_offering_id": offering.id,
            "status": "enrolled",
        },
    )

    assert response.status_code in (400, 404, 409, 422)


def test_enrollment_invalid_offering_rejected(client, db):
    token = create_admin_and_login(client, db)

    program = create_program(
        db,
        "ENR007-P",
        "Enrollment Invalid Offering Program",
    )

    student = create_student(
        db,
        "ENR007-0001",
        "Invalid",
        "Offering",
        "invalid.offering@test.com",
        program.id,
    )

    response = client.post(
        "/api/v1/enrollments/",
        headers=auth_headers(token),
        json={
            "student_id": student.id,
            "course_offering_id": 999999,
            "status": "enrolled",
        },
    )

    assert response.status_code in (400, 404, 409, 422)


def test_duplicate_enrollment_rejected(client, db):
    token = create_admin_and_login(client, db)

    program, student, course, term, offering, enrollment = create_academic_chain(
        db,
        "ENR008",
    )

    response = client.post(
        "/api/v1/enrollments/",
        headers=auth_headers(token),
        json={
            "student_id": student.id,
            "course_offering_id": offering.id,
            "status": "enrolled",
        },
    )

    assert response.status_code in (400, 409, 422)


def test_student_cannot_create_enrollment(client, db):
    create_user(
        db,
        "studentenrollment",
        "studentenrollment@test.com",
        "Student123!",
        "student",
    )

    token = login(
        client,
        "studentenrollment",
        "Student123!",
    )

    program = create_program(
        db,
        "ENR009-P",
        "Enrollment Authorization Program",
    )

    student = create_student(
        db,
        "ENR009-0001",
        "Authorized",
        "Student",
        "authorized.student@test.com",
        program.id,
    )

    course = create_course(
        db,
        "ENR009",
        "Enrollment Authorization Course",
    )

    term = create_term(
        db,
        "Enrollment Authorization Term",
        "2025-2026",
    )

    offering = create_offering(
        db,
        course.id,
        term.id,
        "1A",
    )

    response = client.post(
        "/api/v1/enrollments/",
        headers=auth_headers(token),
        json={
            "student_id": student.id,
            "course_offering_id": offering.id,
            "status": "enrolled",
        },
    )

    assert response.status_code == 403


def test_student_enrollments_endpoint_success(client, db):
    token = create_admin_and_login(client, db)

    program, student, course, term, offering, enrollment = create_academic_chain(
        db,
        "ENR010",
    )

    response = client.get(
        f"/api/v1/students/{student.id}/enrollments",
        headers=auth_headers(token),
    )

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)
    assert any(
        item["id"] == enrollment.id
        for item in data
    )


def test_course_offering_students_endpoint_success(client, db):
    token = create_admin_and_login(client, db)

    program, student, course, term, offering, enrollment = create_academic_chain(
        db,
        "ENR011",
    )

    response = client.get(
        f"/api/v1/course-offerings/{offering.id}/students",
        headers=auth_headers(token),
    )

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)
    assert any(
        item["student_id"] == student.id
        for item in data
    )

def test_grade_create_success(client, db):
    token = create_admin_and_login(client, db)

    program, student, course, term, offering, enrollment = create_academic_chain(
        db,
        "GRD001",
    )

    response = client.post(
        "/api/v1/grades/",
        headers=auth_headers(token),
        json={
            "enrollment_id": enrollment.id,
            "grade": 1.75,
            "remarks": "Passed",
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["enrollment_id"] == enrollment.id
    assert float(data["grade"]) == 1.75
    assert data["remarks"] == "Passed"
    assert "id" in data
    assert "graded_at" in data


def test_grade_get_success(client, db):
    token = create_admin_and_login(client, db)

    program, student, course, term, offering, enrollment = create_academic_chain(
        db,
        "GRD002",
    )

    grade = create_grade(
        db,
        enrollment.id,
        1.50,
        "Good",
    )

    response = client.get(
        f"/api/v1/grades/{grade.id}",
        headers=auth_headers(token),
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == grade.id
    assert data["enrollment_id"] == enrollment.id
    assert float(data["grade"]) == 1.50


def test_grade_update_success(client, db):
    token = create_admin_and_login(client, db)

    program, student, course, term, offering, enrollment = create_academic_chain(
        db,
        "GRD003",
    )

    grade = create_grade(
        db,
        enrollment.id,
        2.00,
        "Initial",
    )

    response = client.patch(
        f"/api/v1/grades/{grade.id}",
        headers=auth_headers(token),
        json={
            "grade": 1.25,
            "remarks": "Updated",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == grade.id
    assert float(data["grade"]) == 1.25
    assert data["remarks"] == "Updated"


def test_grade_delete_success(client, db):
    token = create_admin_and_login(client, db)

    program, student, course, term, offering, enrollment = create_academic_chain(
        db,
        "GRD004",
    )

    grade = create_grade(
        db,
        enrollment.id,
        2.25,
        "Delete me",
    )

    response = client.delete(
        f"/api/v1/grades/{grade.id}",
        headers=auth_headers(token),
    )

    assert response.status_code == 204


def test_grade_not_found(client, db):
    token = create_admin_and_login(client, db)

    response = client.get(
        "/api/v1/grades/999999",
        headers=auth_headers(token),
    )

    assert response.status_code == 404


def test_grade_invalid_enrollment_rejected(client, db):
    token = create_admin_and_login(client, db)

    response = client.post(
        "/api/v1/grades/",
        headers=auth_headers(token),
        json={
            "enrollment_id": 999999,
            "grade": 1.75,
            "remarks": "Invalid enrollment",
        },
    )

    assert response.status_code in (400, 404, 409, 422)


def test_duplicate_grade_rejected(client, db):
    token = create_admin_and_login(client, db)

    program, student, course, term, offering, enrollment = create_academic_chain(
        db,
        "GRD005",
    )

    create_grade(
        db,
        enrollment.id,
        1.75,
        "Original",
    )

    response = client.post(
        "/api/v1/grades/",
        headers=auth_headers(token),
        json={
            "enrollment_id": enrollment.id,
            "grade": 2.00,
            "remarks": "Duplicate",
        },
    )

    assert response.status_code == 409


def test_invalid_grade_value_rejected(client, db):
    token = create_admin_and_login(client, db)

    program, student, course, term, offering, enrollment = create_academic_chain(
        db,
        "GRD006",
    )

    response = client.post(
        "/api/v1/grades/",
        headers=auth_headers(token),
        json={
            "enrollment_id": enrollment.id,
            "grade": 6.00,
            "remarks": "Invalid grade",
        },
    )

    assert response.status_code == 422



def test_student_grades_endpoint_success(client, db):
    token = create_admin_and_login(client, db)

    program, student, course, term, offering, enrollment = create_academic_chain(
        db,
        "GRD007",
    )

    grade = create_grade(
        db,
        enrollment.id,
        1.50,
        "Passed",
    )

    response = client.get(
        f"/api/v1/students/{student.id}/grades",
        headers=auth_headers(token),
    )

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)
    assert any(
        item["id"] == grade.id
        for item in data
    )


def test_student_cannot_access_other_student_grades(client, db):
    admin_token = create_admin_and_login(client, db)

    program1, student1, course1, term1, offering1, enrollment1 = create_academic_chain(
        db,
        "GRD008",
    )

    grade = create_grade(
        db,
        enrollment1.id,
        1.75,
        "Private",
    )

    program2 = create_program(
        db,
        "GRD008-P2",
        "Second Grade Program",
    )

    student2 = create_student(
        db,
        "GRD008-0002",
        "Second",
        "Student",
        "second.grade@test.com",
        program2.id,
    )

    response = client.get(
        f"/api/v1/students/{student2.id}/grades",
        headers=auth_headers(admin_token),
    )

    assert response.status_code == 200

    data = response.json()

    assert all(
        item["id"] != grade.id
        for item in data
    )
