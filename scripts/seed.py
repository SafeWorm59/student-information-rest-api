from datetime import date

from pwdlib import PasswordHash
from sqlalchemy import select

from app.db.session import SessionLocal
from app.models import (
    User,
    Program,
    Student,
    Course,
    AcademicTerm,
    CourseOffering,
    Enrollment,
    Grade,
)


password_hash = PasswordHash.recommended()


def seed_database():
    db = SessionLocal()

    try:
        print("Starting database seed...")

        # =========================================================
        # USERS
        # =========================================================

        users = [
            {
                "username": "admin",
                "email": "admin@studentapi.com",
                "password": "Admin123!",
                "role": "admin",
            },
            {
                "username": "registrar",
                "email": "registrar@studentapi.com",
                "password": "Registrar123!",
                "role": "registrar",
            },
            {
                "username": "instructor1",
                "email": "instructor1@studentapi.com",
                "password": "Instructor123!",
                "role": "instructor",
            },
            {
                "username": "student1",
                "email": "juan.delacruz@studentapi.com",
                "password": "Student123!",
                "role": "student",
            },
            {
                "username": "student2",
                "email": "maria.santos@studentapi.com",
                "password": "Student123!",
                "role": "student",
            },
        ]

        for user_data in users:
            existing = db.scalar(
                select(User).where(
                    User.username == user_data["username"]
                )
            )

            if not existing:
                db.add(
                    User(
                        username=user_data["username"],
                        email=user_data["email"],
                        password_hash=password_hash.hash(
                            user_data["password"]
                        ),
                        role=user_data["role"],
                        is_active=True,
                    )
                )

        db.commit()
        print("[OK] Users seeded")

        # =========================================================
        # PROGRAMS
        # =========================================================

        programs = [
            (
                "BSIT",
                "Bachelor of Science in Information Technology",
                "Program focused on information technology, software development, databases, and computing systems.",
            ),
            (
                "BSCS",
                "Bachelor of Science in Computer Science",
                "Program focused on computing theory, algorithms, programming, and software systems.",
            ),
            (
                "BSBA",
                "Bachelor of Science in Business Administration",
                "Program focused on business management, administration, and organizational operations.",
            ),
        ]

        for code, name, description in programs:
            existing = db.scalar(
                select(Program).where(Program.code == code)
            )

            if not existing:
                db.add(
                    Program(
                        code=code,
                        name=name,
                        description=description,
                        status="active",
                    )
                )

        db.commit()
        print("[OK] Programs seeded")

        # =========================================================
        # GET PROGRAMS
        # =========================================================

        bsit = db.scalar(
            select(Program).where(Program.code == "BSIT")
        )

        bscs = db.scalar(
            select(Program).where(Program.code == "BSCS")
        )

        bsba = db.scalar(
            select(Program).where(Program.code == "BSBA")
        )

        program_list = [bsit, bscs, bsba]

        # =========================================================
        # STUDENTS
        # =========================================================

        first_names = [
            "Juan",
            "Maria",
            "Ahmad",
            "Fatima",
            "Daniel",
            "Aisha",
            "Mohammad",
            "Sarah",
            "David",
            "Hannah",
            "James",
            "Nadia",
            "Michael",
            "Zainab",
            "Mark",
            "Sofia",
            "John",
            "Amira",
            "Robert",
            "Layla",
        ]

        last_names = [
            "Dela Cruz",
            "Santos",
            "Macapaar",
            "Sinsuat",
            "Reyes",
            "Garcia",
            "Abdullah",
            "Cruz",
            "Hassan",
            "Rahman",
        ]

        middle_names = [
            "Santos",
            "Garcia",
            "Usman",
            "Ali",
            "Cruz",
            "Reyes",
            "Ahmad",
            "Salim",
            "Khan",
            "Dela Rosa",
        ]

        for i in range(1, 101):
            student_number = f"2024-{i:04d}"

            existing = db.scalar(
                select(Student).where(
                    Student.student_number == student_number
                )
            )

            if existing:
                continue

            # Preserve the original first five student records.
            if i == 1:
                first_name = "Juan"
                last_name = "Dela Cruz"
                middle_name = "Santos"
                email = "juan.delacruz@studentapi.com"
                program = bsit
                year_level = 4

            elif i == 2:
                first_name = "Maria"
                last_name = "Santos"
                middle_name = "Garcia"
                email = "maria.santos@studentapi.com"
                program = bsit
                year_level = 3

            elif i == 3:
                first_name = "Ahmad"
                last_name = "Macapaar"
                middle_name = "Usman"
                email = "ahmad.macapaar@studentapi.com"
                program = bscs
                year_level = 2

            elif i == 4:
                first_name = "Fatima"
                last_name = "Sinsuat"
                middle_name = "Ali"
                email = "fatima.sinsuat@studentapi.com"
                program = bsba
                year_level = 3

            elif i == 5:
                first_name = "Daniel"
                last_name = "Reyes"
                middle_name = "Cruz"
                email = "daniel.reyes@studentapi.com"
                program = bsit
                year_level = 1

            else:
                first_name = first_names[(i - 1) % len(first_names)]
                last_name = last_names[(i - 1) % len(last_names)]
                middle_name = middle_names[(i - 1) % len(middle_names)]
                email = (
                    f"student{i}@studentapi.com"
                )
                program = program_list[(i - 1) % len(program_list)]
                year_level = ((i - 1) % 4) + 1

            db.add(
                Student(
                    student_number=student_number,
                    first_name=first_name,
                    last_name=last_name,
                    middle_name=middle_name,
                    email=email,
                    program_id=program.id,
                    year_level=year_level,
                    status="active",
                )
            )

        db.commit()
        print("[OK] 100 students seeded")

        # =========================================================
        # COURSES
        # =========================================================

        courses = [
            (
                "IT101",
                "Introduction to Information Technology",
                "Fundamentals of information technology and computing.",
                3,
            ),
            (
                "IT202",
                "Database Management Systems",
                "Relational databases, SQL, database design, and normalization.",
                3,
            ),
            (
                "IT303",
                "Web Application Development",
                "Development of modern web-based applications and APIs.",
                3,
            ),
            (
                "CS201",
                "Data Structures and Algorithms",
                "Fundamental data structures and algorithmic problem solving.",
                3,
            ),
            (
                "BA101",
                "Principles of Management",
                "Introduction to management concepts and organizational practices.",
                3,
            ),
        ]

        # Add courses 6-20.
        additional_courses = [
            (
                "IT304",
                "Mobile Application Development",
                "Development of mobile applications using modern frameworks.",
                3,
            ),
            (
                "IT305",
                "Software Engineering",
                "Software development methodologies, requirements, and design.",
                3,
            ),
            (
                "IT306",
                "Information Assurance",
                "Security principles, risk management, and information protection.",
                3,
            ),
            (
                "IT307",
                "Cloud Computing",
                "Cloud infrastructure, services, deployment, and architecture.",
                3,
            ),
            (
                "IT308",
                "Network Administration",
                "Network configuration, administration, and troubleshooting.",
                3,
            ),
            (
                "IT309",
                "Human Computer Interaction",
                "User interface design and human-computer interaction principles.",
                3,
            ),
            (
                "IT310",
                "Systems Analysis and Design",
                "Analysis, modeling, and design of information systems.",
                3,
            ),
            (
                "CS301",
                "Operating Systems",
                "Operating system concepts, processes, memory, and file systems.",
                3,
            ),
            (
                "CS302",
                "Computer Networks",
                "Networking concepts, protocols, and network architecture.",
                3,
            ),
            (
                "CS303",
                "Artificial Intelligence",
                "Introduction to artificial intelligence concepts and applications.",
                3,
            ),
            (
                "CS304",
                "Machine Learning",
                "Fundamental machine learning algorithms and applications.",
                3,
            ),
            (
                "CS305",
                "Computer Architecture",
                "Computer organization, processors, memory, and architecture.",
                3,
            ),
            (
                "BA201",
                "Financial Management",
                "Financial planning, analysis, and management principles.",
                3,
            ),
            (
                "BA202",
                "Marketing Management",
                "Marketing principles, strategies, and consumer behavior.",
                3,
            ),
            (
                "BA203",
                "Business Analytics",
                "Data analysis and decision-making for business operations.",
                3,
            ),
        ]

        courses.extend(additional_courses)

        for code, title, description, units in courses:
            existing = db.scalar(
                select(Course).where(Course.code == code)
            )

            if not existing:
                db.add(
                    Course(
                        code=code,
                        title=title,
                        description=description,
                        units=units,
                        status="active",
                    )
                )

        db.commit()
        print("[OK] 20 courses seeded")

        # =========================================================
        # GET COURSES
        # =========================================================

        all_courses = db.scalars(
            select(Course).order_by(Course.id)
        ).all()

        # =========================================================
        # ACADEMIC TERMS
        # =========================================================

        terms = [
            AcademicTerm(
                name="1st Semester",
                school_year="2025-2026",
                start_date=date(2025, 8, 1),
                end_date=date(2025, 12, 20),
                is_active=False,
            ),
            AcademicTerm(
                name="2nd Semester",
                school_year="2025-2026",
                start_date=date(2026, 1, 5),
                end_date=date(2026, 5, 30),
                is_active=True,
            ),
        ]

        for term in terms:
            existing = db.scalar(
                select(AcademicTerm).where(
                    AcademicTerm.name == term.name,
                    AcademicTerm.school_year == term.school_year,
                )
            )

            if not existing:
                db.add(term)

        db.commit()
        print("[OK] Academic terms seeded")

        # =========================================================
        # GET ACTIVE TERM
        # =========================================================

        active_term = db.scalar(
            select(AcademicTerm).where(
                AcademicTerm.school_year == "2025-2026",
                AcademicTerm.name == "2nd Semester",
            )
        )

        # =========================================================
        # COURSE OFFERINGS
        # =========================================================

        instructor_names = [
            "Dr. Roberto Garcia",
            "Prof. Ana Reyes",
            "Prof. Michael Cruz",
            "Dr. Karim Abdullah",
            "Prof. Elena Santos",
        ]

        for i, course in enumerate(all_courses[:20], start=1):
            section = f"SEC-{i:02d}"

            existing = db.scalar(
                select(CourseOffering).where(
                    CourseOffering.course_id == course.id,
                    CourseOffering.term_id == active_term.id,
                    CourseOffering.section == section,
                )
            )

            if not existing:
                db.add(
                    CourseOffering(
                        course_id=course.id,
                        term_id=active_term.id,
                        section=section,
                        schedule=f"Day {i} 8:00-11:00 AM",
                        room=f"ROOM-{100 + i}",
                        instructor=instructor_names[
                            (i - 1) % len(instructor_names)
                        ],
                        capacity=40,
                    )
                )

        db.commit()
        print("[OK] 20 course offerings seeded")

        # =========================================================
        # GET OFFERINGS
        # =========================================================

        all_offerings = db.scalars(
            select(CourseOffering)
            .where(
                CourseOffering.term_id == active_term.id
            )
            .order_by(CourseOffering.id)
        ).all()

        # =========================================================
        # GET STUDENTS
        # =========================================================

        all_students = db.scalars(
            select(Student).order_by(Student.id)
        ).all()

        # =========================================================
        # ENROLLMENTS
        # =========================================================
        #
        # Each of the 100 students receives two course offerings.
        # This produces at least 200 enrollments while preventing
        # duplicate student/offering combinations.

        enrollments = []

        for index, student in enumerate(all_students[:100]):
            offering_a = all_offerings[index % len(all_offerings)]
            offering_b = all_offerings[
                (index + 1) % len(all_offerings)
            ]

            for offering in (offering_a, offering_b):
                existing = db.scalar(
                    select(Enrollment).where(
                        Enrollment.student_id == student.id,
                        Enrollment.course_offering_id == offering.id,
                    )
                )

                if existing:
                    enrollments.append(existing)
                else:
                    enrollment = Enrollment(
                        student_id=student.id,
                        course_offering_id=offering.id,
                        status="enrolled",
                    )
                    db.add(enrollment)
                    db.flush()
                    enrollments.append(enrollment)

        db.commit()
        print("[OK] At least 200 enrollments seeded")

        # =========================================================
        # GRADES
        # =========================================================
        #
        # Ensure every student has at least one graded enrollment.
        # Existing grades are preserved.

        grade_values = [
            1.25,
            1.50,
            1.75,
            2.00,
            2.25,
        ]

        students_with_grade = set()

        existing_grades = db.scalars(
            select(Grade)
        ).all()

        for grade in existing_grades:
            enrollment = db.scalar(
                select(Enrollment).where(
                    Enrollment.id == grade.enrollment_id
                )
            )

            if enrollment:
                students_with_grade.add(
                    enrollment.student_id
                )

        for enrollment in enrollments:
            if enrollment.student_id in students_with_grade:
                continue

            grade_value = grade_values[
                enrollment.student_id % len(grade_values)
            ]

            existing = db.scalar(
                select(Grade).where(
                    Grade.enrollment_id == enrollment.id
                )
            )

            if not existing:
                db.add(
                    Grade(
                        enrollment_id=enrollment.id,
                        grade=grade_value,
                        remarks="Passed",
                    )
                )

                students_with_grade.add(
                    enrollment.student_id
                )

        db.commit()

        total_grades = db.scalar(
            select(Grade.id)
        )

        print("[OK] At least 100 grades seeded")

        # =========================================================
        # FINAL COUNTS
        # =========================================================

        user_count = len(
            db.scalars(select(User)).all()
        )

        program_count = len(
            db.scalars(select(Program)).all()
        )

        student_count = len(
            db.scalars(select(Student)).all()
        )

        course_count = len(
            db.scalars(select(Course)).all()
        )

        term_count = len(
            db.scalars(select(AcademicTerm)).all()
        )

        offering_count = len(
            db.scalars(select(CourseOffering)).all()
        )

        enrollment_count = len(
            db.scalars(select(Enrollment)).all()
        )

        grade_count = len(
            db.scalars(select(Grade)).all()
        )

        print()
        print("====================================")
        print("DATABASE SEED COMPLETED SUCCESSFULLY")
        print("====================================")
        print()
        print("Seeded record counts:")
        print(f"Users:             {user_count}")
        print(f"Programs:          {program_count}")
        print(f"Students:          {student_count}")
        print(f"Courses:           {course_count}")
        print(f"Academic Terms:    {term_count}")
        print(f"Course Offerings:  {offering_count}")
        print(f"Enrollments:       {enrollment_count}")
        print(f"Grades:            {grade_count}")
        print()
        print("Test accounts:")
        print("Admin:       admin / Admin123!")
        print("Registrar:   registrar / Registrar123!")
        print("Instructor:  instructor1 / Instructor123!")
        print("Student 1:   student1 / Student123!")
        print("Student 2:   student2 / Student123!")
        print()

    except Exception as error:
        db.rollback()
        print("ERROR:", error)
        raise

    finally:
        db.close()


if __name__ == "__main__":
    seed_database()