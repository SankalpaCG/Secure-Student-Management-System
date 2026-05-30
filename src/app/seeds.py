from datetime import date, datetime

from app.extensions import db
from app.models import (
    Attendance,
    AuditLog,
    Course,
    Enrollment,
    Grade,
    RevokedToken,
    StudentProfile,
    TeacherProfile,
    User,
)
from app.models.enums import AttendanceStatus, EnrollmentStatus, UserRole
from app.utils.security import hash_password

DEFAULT_SEED_PASSWORD = "ChangeMe123!"


def seed_database(password: str = DEFAULT_SEED_PASSWORD):
    """Populate the database with sample data. Safe to re-run — skips if admin exists."""
    if User.query.filter_by(email="admin@school.edu").first():
        print("Database already seeded. Skipping.")
        return

    admin = User(
        full_name="System Administrator",
        email="admin@school.edu",
        password_hash=hash_password(password),
        role=UserRole.ADMIN,
        is_active=True,
    )

    teachers = [
        User(
            full_name="Dr. Sarah Chen",
            email="sarah.chen@school.edu",
            password_hash=hash_password(password),
            role=UserRole.TEACHER,
        ),
        User(
            full_name="Prof. James Wilson",
            email="james.wilson@school.edu",
            password_hash=hash_password(password),
            role=UserRole.TEACHER,
        ),
    ]

    students = [
        User(
            full_name="Emma Johnson",
            email="emma.johnson@school.edu",
            password_hash=hash_password(password),
            role=UserRole.STUDENT,
        ),
        User(
            full_name="Liam Martinez",
            email="liam.martinez@school.edu",
            password_hash=hash_password(password),
            role=UserRole.STUDENT,
        ),
        User(
            full_name="Olivia Brown",
            email="olivia.brown@school.edu",
            password_hash=hash_password(password),
            role=UserRole.STUDENT,
        ),
    ]

    db.session.add(admin)
    db.session.add_all(teachers)
    db.session.add_all(students)
    db.session.flush()

    teacher_profiles = [
        TeacherProfile(
            user_id=teachers[0].id,
            staff_number="TCH-001",
            department="Computer Science",
            phone="555-0101",
        ),
        TeacherProfile(
            user_id=teachers[1].id,
            staff_number="TCH-002",
            department="Mathematics",
            phone="555-0102",
        ),
    ]

    student_profiles = [
        StudentProfile(
            user_id=students[0].id,
            student_number="STU-001",
            date_of_birth=date(2004, 3, 15),
            phone="555-1001",
            address="123 Campus Drive",
            emergency_contact="Mary Johnson (555-9001)",
        ),
        StudentProfile(
            user_id=students[1].id,
            student_number="STU-002",
            date_of_birth=date(2004, 7, 22),
            phone="555-1002",
            address="456 University Ave",
            emergency_contact="Carlos Martinez (555-9002)",
        ),
        StudentProfile(
            user_id=students[2].id,
            student_number="STU-003",
            date_of_birth=date(2003, 11, 8),
            phone="555-1003",
            address="789 College Road",
            emergency_contact="Kate Brown (555-9003)",
        ),
    ]

    db.session.add_all(teacher_profiles)
    db.session.add_all(student_profiles)
    db.session.flush()

    courses = [
        Course(
            course_code="CS101",
            course_name="Introduction to Programming",
            description="Fundamentals of programming with Python.",
            teacher_id=teachers[0].id,
        ),
        Course(
            course_code="MATH201",
            course_name="Calculus II",
            description="Integration techniques and series.",
            teacher_id=teachers[1].id,
        ),
        Course(
            course_code="CS201",
            course_name="Data Structures",
            description="Arrays, trees, graphs, and algorithm analysis.",
            teacher_id=teachers[0].id,
        ),
    ]

    db.session.add_all(courses)
    db.session.flush()

    enrollments = [
        Enrollment(student_id=students[0].id, course_id=courses[0].id, status=EnrollmentStatus.ACTIVE),
        Enrollment(student_id=students[0].id, course_id=courses[2].id, status=EnrollmentStatus.ACTIVE),
        Enrollment(student_id=students[1].id, course_id=courses[0].id, status=EnrollmentStatus.ACTIVE),
        Enrollment(student_id=students[1].id, course_id=courses[1].id, status=EnrollmentStatus.ACTIVE),
        Enrollment(student_id=students[2].id, course_id=courses[1].id, status=EnrollmentStatus.ACTIVE),
        Enrollment(student_id=students[2].id, course_id=courses[2].id, status=EnrollmentStatus.COMPLETED),
    ]

    grades = [
        Grade(
            student_id=students[0].id,
            course_id=courses[0].id,
            teacher_id=teachers[0].id,
            assessment_name="Midterm Exam",
            grade_value="88.5",
            feedback="Strong understanding of core concepts.",
        ),
        Grade(
            student_id=students[0].id,
            course_id=courses[2].id,
            teacher_id=teachers[0].id,
            assessment_name="Assignment 1",
            grade_value="92.0",
            feedback="Excellent implementation.",
        ),
        Grade(
            student_id=students[1].id,
            course_id=courses[0].id,
            teacher_id=teachers[0].id,
            assessment_name="Midterm Exam",
            grade_value="76.0",
            feedback="Review loops and functions.",
        ),
        Grade(
            student_id=students[1].id,
            course_id=courses[1].id,
            teacher_id=teachers[1].id,
            assessment_name="Quiz 1",
            grade_value="85.0",
            feedback="Good progress.",
        ),
        Grade(
            student_id=students[2].id,
            course_id=courses[2].id,
            teacher_id=teachers[0].id,
            assessment_name="Final Project",
            grade_value="95.0",
            feedback="Outstanding work.",
        ),
    ]

    attendance_records = [
        Attendance(
            student_id=students[0].id,
            course_id=courses[0].id,
            teacher_id=teachers[0].id,
            attendance_date=date(2026, 5, 1),
            status=AttendanceStatus.PRESENT,
        ),
        Attendance(
            student_id=students[0].id,
            course_id=courses[0].id,
            teacher_id=teachers[0].id,
            attendance_date=date(2026, 5, 2),
            status=AttendanceStatus.PRESENT,
        ),
        Attendance(
            student_id=students[1].id,
            course_id=courses[0].id,
            teacher_id=teachers[0].id,
            attendance_date=date(2026, 5, 1),
            status=AttendanceStatus.LATE,
            remarks="Arrived 10 minutes late.",
        ),
        Attendance(
            student_id=students[1].id,
            course_id=courses[1].id,
            teacher_id=teachers[1].id,
            attendance_date=date(2026, 5, 1),
            status=AttendanceStatus.PRESENT,
        ),
        Attendance(
            student_id=students[2].id,
            course_id=courses[1].id,
            teacher_id=teachers[1].id,
            attendance_date=date(2026, 5, 2),
            status=AttendanceStatus.ABSENT,
            remarks="Medical leave.",
        ),
        Attendance(
            student_id=students[2].id,
            course_id=courses[2].id,
            teacher_id=teachers[0].id,
            attendance_date=date(2026, 5, 1),
            status=AttendanceStatus.PRESENT,
        ),
    ]

    audit_logs = [
        AuditLog(
            user_id=admin.id,
            action="seed_database",
            target_type="system",
            target_id=None,
            ip_address="127.0.0.1",
            user_agent="flask-seed-cli",
            timestamp=datetime.utcnow(),
        ),
    ]

    revoked_tokens = [
        RevokedToken(jti="00000000-0000-0000-0000-000000000001"),
    ]

    db.session.add_all(enrollments)
    db.session.add_all(grades)
    db.session.add_all(attendance_records)
    db.session.add_all(audit_logs)
    db.session.add_all(revoked_tokens)
    db.session.commit()

    print("Database seeded successfully.")
    print(f"  Default password for all users: {password}")
    print("  Admin:    admin@school.edu")
    print("  Teachers: sarah.chen@school.edu, james.wilson@school.edu")
    print("  Students: emma.johnson@school.edu, liam.martinez@school.edu, olivia.brown@school.edu")
