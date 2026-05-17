from pathlib import Path

T = Path(__file__).resolve().parents[1] / "src" / "app" / "templates"
TAG = "DVTAG"


def w(path, content):
    p = T / path
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content.replace(TAG, "motion").replace("motion", "div"))


w("admin/users.html", """{% extends "dashboard_base.html" %}
{% block title %}Users{% endblock %}
{% block page_title %}User Management{% endblock %}
{% block page_actions %}<a href="{{ url_for('admin.create_user') }}" class="btn btn-primary">Create User</a>{% endblock %}
{% block dashboard_content %}
<DVTAG class="card table-card shadow-sm"><DVTAG class="table-responsive">
<table class="table table-hover mb-0">
<thead class="table-light"><tr><th>Name</th><th>Email</th><th>Role</th><th>Status</th><th></th></tr></thead>
<tbody>
{% for user in users %}
<tr>
<td>{{ user.full_name }}</td><td>{{ user.email }}</td>
<td><span class="badge bg-secondary">{{ user.role.value }}</span></td>
<td>{% if user.is_active %}Active{% else %}Inactive{% endif %}</td>
<td class="text-end">
<a href="{{ url_for('admin.edit_user', user_id=user.id) }}" class="btn btn-sm btn-outline-primary">Edit</a>
{% if user.is_active and user.id != current_user.id %}
<form method="POST" action="{{ url_for('admin.deactivate_user', user_id=user.id) }}" class="d-inline">
<input type="hidden" name="csrf_token" value="{{ csrf_token() }}">
<button type="submit" class="btn btn-sm btn-outline-danger">Deactivate</button>
</form>{% endif %}
</td></tr>{% endfor %}
</tbody></table></DVTAG></DVTAG>
{% endblock %}""")

w("admin/user_form.html", """{% extends "dashboard_base.html" %}
{% block title %}{{ title }}{% endblock %}{% block page_title %}{{ title }}{% endblock %}
{% block dashboard_content %}
<DVTAG class="card shadow-sm"><DVTAG class="card-body p-4 col-lg-8">
<form method="POST">{{ form.hidden_tag() }}
<DVTAG class="mb-3">{{ form.full_name.label(class="form-label") }}{{ form.full_name(class="form-control") }}</DVTAG>
<DVTAG class="mb-3">{{ form.email.label(class="form-label") }}{{ form.email(class="form-control") }}</DVTAG>
<DVTAG class="mb-3">{{ form.role.label(class="form-label") }}{{ form.role(class="form-select") }}</DVTAG>
<DVTAG class="mb-3">{{ form.password.label(class="form-label") }}{{ form.password(class="form-control") }}</DVTAG>
<DVTAG class="mb-3 form-check">{{ form.is_active() }} {{ form.is_active.label(class="form-check-label") }}</DVTAG>
{{ form.submit(class="btn btn-primary") }} <a href="{{ url_for('admin.users') }}">Cancel</a>
</form></DVTAG></DVTAG>{% endblock %}""")

w("admin/courses.html", """{% extends "dashboard_base.html" %}
{% block title %}Courses{% endblock %}{% block page_title %}Course Management{% endblock %}
{% block page_actions %}<a href="{{ url_for('admin.create_course') }}" class="btn btn-primary">Create Course</a>{% endblock %}
{% block dashboard_content %}
<DVTAG class="card table-card shadow-sm"><table class="table mb-0">
<thead class="table-light"><tr><th>Code</th><th>Name</th><th>Teacher</th><th></th></tr></thead>
<tbody>{% for c in courses %}
<tr><td>{{ c.course_code }}</td><td>{{ c.course_name }}</td><td>{{ c.teacher.full_name }}</td>
<td><a href="{{ url_for('admin.edit_course', course_id=c.id) }}" class="btn btn-sm btn-outline-primary">Edit</a></td></tr>
{% endfor %}</tbody></table></DVTAG>{% endblock %}""")

w("admin/course_form.html", """{% extends "dashboard_base.html" %}
{% block title %}{{ title }}{% endblock %}{% block page_title %}{{ title }}{% endblock %}
{% block dashboard_content %}
<DVTAG class="card shadow-sm p-4 col-lg-8"><form method="POST">{{ form.hidden_tag() }}
<DVTAG class="mb-3">{{ form.course_code.label }} {{ form.course_code(class="form-control") }}</DVTAG>
<DVTAG class="mb-3">{{ form.course_name.label }} {{ form.course_name(class="form-control") }}</DVTAG>
<DVTAG class="mb-3">{{ form.description.label }} {{ form.description(class="form-control", rows=3) }}</DVTAG>
<DVTAG class="mb-3">{{ form.teacher_id.label }} {{ form.teacher_id(class="form-select") }}</DVTAG>
{{ form.submit(class="btn btn-primary") }} <a href="{{ url_for('admin.courses') }}">Cancel</a>
</form></DVTAG>{% endblock %}""")

w("admin/students.html", """{% extends "dashboard_base.html" %}
{% block title %}Students{% endblock %}{% block page_title %}All Students{% endblock %}
{% block dashboard_content %}<table class="table table-striped"><thead><tr><th>#</th><th>Name</th><th>Email</th><th>Phone</th></tr></thead>
<tbody>{% for p in profiles %}<tr><td>{{ p.student_number }}</td><td>{{ p.user.full_name }}</td><td>{{ p.user.email }}</td><td>{{ p.phone or '-' }}</td></tr>{% endfor %}</tbody></table>{% endblock %}""")

w("admin/teachers.html", """{% extends "dashboard_base.html" %}
{% block title %}Teachers{% endblock %}{% block page_title %}All Teachers{% endblock %}
{% block dashboard_content %}<table class="table table-striped"><thead><tr><th>Staff #</th><th>Name</th><th>Department</th><th>Email</th></tr></thead>
<tbody>{% for p in profiles %}<tr><td>{{ p.staff_number }}</td><td>{{ p.user.full_name }}</td><td>{{ p.department or '-' }}</td><td>{{ p.user.email }}</td></tr>{% endfor %}</tbody></table>{% endblock %}""")

w("admin/grades.html", """{% extends "dashboard_base.html" %}
{% block title %}Grades{% endblock %}{% block page_title %}All Grades{% endblock %}
{% block dashboard_content %}<table class="table table-striped"><thead><tr><th>Student</th><th>Course</th><th>Assessment</th><th>Grade</th></tr></thead>
<tbody>{% for g in grades %}<tr><td>{{ g.student.full_name }}</td><td>{{ g.course.course_code }}</td><td>{{ g.assessment_name }}</td><td>{{ g.grade_value }}</td></tr>{% endfor %}</tbody></table>{% endblock %}""")

w("admin/attendance.html", """{% extends "dashboard_base.html" %}
{% block title %}Attendance{% endblock %}{% block page_title %}All Attendance{% endblock %}
{% block dashboard_content %}<table class="table table-striped"><thead><tr><th>Student</th><th>Course</th><th>Date</th><th>Status</th></tr></thead>
<tbody>{% for r in records %}<tr><td>{{ r.student.full_name }}</td><td>{{ r.course.course_code }}</td><td>{{ r.attendance_date }}</td><td>{{ r.status.value }}</td></tr>{% endfor %}</tbody></table>{% endblock %}""")

w("admin/audit_logs.html", """{% extends "dashboard_base.html" %}
{% block title %}Audit Logs{% endblock %}{% block page_title %}Audit Logs{% endblock %}
{% block dashboard_content %}<table class="table table-sm table-striped"><thead><tr><th>Time</th><th>User</th><th>Action</th><th>Target</th><th>IP</th></tr></thead>
<tbody>{% for log in logs %}<tr><td>{{ log.timestamp.strftime('%Y-%m-%d %H:%M') }}</td><td>{{ log.user.email if log.user else '—' }}</td><td>{{ log.action }}</td><td>{{ log.target_type }} #{{ log.target_id or '' }}</td><td>{{ log.ip_address or '' }}</td></tr>{% endfor %}</tbody></table>{% endblock %}""")

w("teacher/dashboard.html", """{% extends "dashboard_base.html" %}
{% block title %}Teacher Dashboard{% endblock %}{% block page_title %}Teacher Dashboard{% endblock %}
{% block page_subtitle %}Your assigned courses{% endblock %}
{% block dashboard_content %}
{% if courses %}<DVTAG class="list-group">{% for c in courses %}
<a href="{{ url_for('teacher.course_students', course_id=c.id) }}" class="list-group-item list-group-item-action d-flex justify-content-between">
<span><strong>{{ c.course_code }}</strong> — {{ c.course_name }}</span><span class="text-muted">View students &rarr;</span></a>{% endfor %}</DVTAG>
{% else %}<p class="text-muted">No courses assigned yet.</p>{% endif %}{% endblock %}""")

w("teacher/courses.html", """{% extends "dashboard_base.html" %}
{% block title %}My Courses{% endblock %}{% block page_title %}My Courses{% endblock %}
{% block dashboard_content %}<table class="table"><thead><tr><th>Code</th><th>Name</th><th>Actions</th></tr></thead>
<tbody>{% for c in courses %}<tr><td>{{ c.course_code }}</td><td>{{ c.course_name }}</td>
<td>
<a href="{{ url_for('teacher.course_students', course_id=c.id) }}">Students</a> |
<a href="{{ url_for('teacher.course_grades', course_id=c.id) }}">Grades</a> |
<a href="{{ url_for('teacher.course_attendance', course_id=c.id) }}">Attendance</a>
</td></tr>{% endfor %}</tbody></table>{% endblock %}""")

w("teacher/students.html", """{% extends "dashboard_base.html" %}
{% block title %}Students — {{ course.course_code }}{% endblock %}
{% block page_title %}Enrolled Students: {{ course.course_name }}{% endblock %}
{% block dashboard_content %}<table class="table"><thead><tr><th>Name</th><th>Email</th><th>Student #</th></tr></thead>
<tbody>{% for e in enrollments %}<tr><td>{{ e.student.full_name }}</td><td>{{ e.student.email }}</td>
<td>{{ e.student.student_profile.student_number if e.student.student_profile else '—' }}</td></tr>{% endfor %}</tbody></table>
<a href="{{ url_for('teacher.courses') }}" class="btn btn-link">&larr; Back</a>{% endblock %}""")

w("teacher/grades.html", """{% extends "dashboard_base.html" %}
{% block title %}Grades — {{ course.course_code }}{% endblock %}
{% block page_title %}Grades: {{ course.course_name }}{% endblock %}
{% block dashboard_content %}
<DVTAG class="row"><DVTAG class="col-lg-5 mb-4"><DVTAG class="card p-3"><h5>Add Grade</h5>
<form method="POST">{{ form.hidden_tag() }}
{{ form.student_id.label }} {{ form.student_id(class="form-select mb-2") }}
{{ form.assessment_name.label }} {{ form.assessment_name(class="form-control mb-2") }}
{{ form.grade_value.label }} {{ form.grade_value(class="form-control mb-2") }}
{{ form.feedback.label }} {{ form.feedback(class="form-control mb-2", rows=2) }}
{{ form.submit(class="btn btn-primary") }}</form></DVTAG></DVTAG>
<DVTAG class="col-lg-7"><table class="table table-sm"><thead><tr><th>Student</th><th>Assessment</th><th>Grade</th><th></th></tr></thead>
<tbody>{% for g in grades %}<tr><td>{{ g.student.full_name }}</td><td>{{ g.assessment_name }}</td><td>{{ g.grade_value }}</td>
<td><a href="{{ url_for('teacher.edit_grade', course_id=course.id, grade_id=g.id) }}">Edit</a></td></tr>{% endfor %}</tbody></table></DVTAG></DVTAG>
{% endblock %}""")

w("teacher/grade_edit.html", """{% extends "dashboard_base.html" %}
{% block title %}Edit Grade{% endblock %}{% block page_title %}Edit Grade{% endblock %}
{% block dashboard_content %}<form method="POST" class="col-lg-6">{{ form.hidden_tag() }}
{{ form.student_id(class="form-select mb-2") }}{{ form.assessment_name(class="form-control mb-2") }}
{{ form.grade_value(class="form-control mb-2") }}{{ form.feedback(class="form-control mb-2", rows=2) }}
{{ form.submit(class="btn btn-primary") }}</form>{% endblock %}""")

w("teacher/attendance.html", """{% extends "dashboard_base.html" %}
{% block title %}Attendance — {{ course.course_code }}{% endblock %}
{% block page_title %}Attendance: {{ course.course_name }}{% endblock %}
{% block dashboard_content %}
<DVTAG class="row"><DVTAG class="col-lg-4"><form method="POST" class="card p-3">{{ form.hidden_tag() }}
{{ form.student_id(class="form-select mb-2") }}{{ form.attendance_date(class="form-control mb-2") }}
{{ form.status(class="form-select mb-2") }}{{ form.remarks(class="form-control mb-2", rows=2) }}
{{ form.submit(class="btn btn-primary") }}</form></DVTAG>
<DVTAG class="col-lg-8"><table class="table table-sm"><thead><tr><th>Student</th><th>Date</th><th>Status</th></tr></thead>
<tbody>{% for r in records %}<tr><td>{{ r.student.full_name }}</td><td>{{ r.attendance_date }}</td><td>{{ r.status.value }}</td></tr>{% endfor %}</tbody></table></DVTAG></DVTAG>
{% endblock %}""")

w("teacher/profile.html", """{% extends "dashboard_base.html" %}
{% block title %}My Profile{% endblock %}{% block page_title %}My Profile{% endblock %}
{% block dashboard_content %}<ul class="list-group col-lg-6">
<li class="list-group-item"><strong>Name:</strong> {{ current_user.full_name }}</li>
<li class="list-group-item"><strong>Email:</strong> {{ current_user.email }}</li>
{% if profile %}<li class="list-group-item"><strong>Staff #:</strong> {{ profile.staff_number }}</li>
<li class="list-group-item"><strong>Department:</strong> {{ profile.department or '—' }}</li>
<li class="list-group-item"><strong>Phone:</strong> {{ profile.phone or '—' }}</li>{% endif %}
</ul>{% endblock %}""")

w("student/dashboard.html", """{% extends "dashboard_base.html" %}
{% block title %}Student Dashboard{% endblock %}{% block page_title %}Student Dashboard{% endblock %}
{% block dashboard_content %}
<DVTAG class="row g-3"><DVTAG class="col-md-4"><DVTAG class="card p-3 dashboard-stat"><DVTAG class="text-muted small">Active Enrollments</DVTAG><DVTAG class="h3">{{ enrollments_count }}</DVTAG></DVTAG></DVTAG>
<DVTAG class="col-md-4"><DVTAG class="card p-3 dashboard-stat"><DVTAG class="text-muted small">Grades Recorded</DVTAG><DVTAG class="h3">{{ grades_count }}</DVTAG></DVTAG></DVTAG></DVTAG>
{% endblock %}""")

w("student/profile.html", """{% extends "dashboard_base.html" %}
{% block title %}My Profile{% endblock %}{% block page_title %}My Profile{% endblock %}
{% block page_subtitle %}Update contact information only{% endblock %}
{% block dashboard_content %}<form method="POST" class="col-lg-6">{{ form.hidden_tag() }}
<p><strong>Name:</strong> {{ current_user.full_name }}<br><strong>Email:</strong> {{ current_user.email }}<br><strong>Student #:</strong> {{ profile.student_number }}</p>
{{ form.phone.label }} {{ form.phone(class="form-control mb-2") }}
{{ form.address.label }} {{ form.address(class="form-control mb-2", rows=2) }}
{{ form.emergency_contact.label }} {{ form.emergency_contact(class="form-control mb-2") }}
{{ form.submit(class="btn btn-primary") }}</form>{% endblock %}""")

w("student/courses.html", """{% extends "dashboard_base.html" %}
{% block title %}Courses{% endblock %}{% block page_title %}Available Courses{% endblock %}
{% block dashboard_content %}<table class="table"><thead><tr><th>Code</th><th>Name</th><th>Teacher</th><th></th></tr></thead>
<tbody>{% for c in courses %}<tr><td>{{ c.course_code }}</td><td>{{ c.course_name }}</td><td>{{ c.teacher.full_name }}</td>
<td>{% if c.id in enrolled_ids %}<span class="badge bg-success">Enrolled</span>{% else %}
<form method="POST" action="{{ url_for('student.enroll', course_id=c.id) }}"><input type="hidden" name="csrf_token" value="{{ csrf_token() }}"><button class="btn btn-sm btn-primary">Enroll</button></form>{% endif %}</td></tr>{% endfor %}</tbody></table>{% endblock %}""")

w("student/grades.html", """{% extends "dashboard_base.html" %}
{% block title %}My Grades{% endblock %}{% block page_title %}My Grades{% endblock %}
{% block dashboard_content %}<table class="table"><thead><tr><th>Course</th><th>Assessment</th><th>Grade</th><th></th></tr></thead>
<tbody>{% for g in grades %}<tr><td>{{ g.course.course_code }}</td><td>{{ g.assessment_name }}</td><td>{{ g.grade_value }}</td>
<td><a href="{{ url_for('student.grade_detail', grade_id=g.id) }}">Details</a></td></tr>{% endfor %}</tbody></table>{% endblock %}""")

w("student/grade_detail.html", """{% extends "dashboard_base.html" %}
{% block title %}Grade Detail{% endblock %}{% block page_title %}Grade Detail{% endblock %}
{% block dashboard_content %}<ul class="list-group col-lg-6">
<li class="list-group-item"><strong>Course:</strong> {{ grade.course.course_name }}</li>
<li class="list-group-item"><strong>Assessment:</strong> {{ grade.assessment_name }}</li>
<li class="list-group-item"><strong>Grade:</strong> {{ grade.grade_value }}</li>
<li class="list-group-item"><strong>Feedback:</strong> {{ grade.feedback or '—' }}</li>
</ul><a href="{{ url_for('student.grades') }}">&larr; Back</a>{% endblock %}""")

w("student/attendance.html", """{% extends "dashboard_base.html" %}
{% block title %}My Attendance{% endblock %}{% block page_title %}My Attendance{% endblock %}
{% block dashboard_content %}<table class="table"><thead><tr><th>Course</th><th>Date</th><th>Status</th><th>Remarks</th></tr></thead>
<tbody>{% for r in records %}<tr><td>{{ r.course.course_code }}</td><td>{{ r.attendance_date }}</td><td>{{ r.status.value }}</td><td>{{ r.remarks or '' }}</td></tr>{% endfor %}</tbody></table>{% endblock %}""")

print("Done")
