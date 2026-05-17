import re
from pathlib import Path

T = Path(__file__).resolve().parents[1] / "src" / "app" / "templates"
G = "DVTAG"

def w(path, content):
    p = T / path
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(re.sub(rf"</?{G}\b", lambda m: m.group(0).replace(G, "motion").replace("motion", "motion").replace("motion", "motion").replace("motion", "div"), content))

w("teacher/students.html", """{% extends "dashboard_base.html" %}
{% set breadcrumb_title = course.course_code %}
{% block title %}Students — {{ course.course_code }}{% endblock %}
{% block page_title %}Students: {{ course.course_name }}{% endblock %}
{% block page_actions %}<a href="{{ url_for('teacher.courses') }}" class="btn btn-outline-secondary btn-sm"><i class="bi bi-arrow-left"></i> Back</a>{% endblock %}
{% block dashboard_content %}
<DVTAG class="card card-app"><DVTAG class="card-body">
{% include 'components/table_controls.html' %}
<table class="table table-app" id="dataTable"><thead><tr><th>Name</th><th>Email</th><th>Student #</th></tr></thead>
<tbody>{% for e in enrollments %}<tr>
<td>{{ e.student.full_name }}</td><td>{{ e.student.email }}</td>
<td>{{ e.student.student_profile.student_number if e.student.student_profile else '—' }}</td></tr>{% endfor %}</tbody></table>
</DVTAG></DVTAG>{% endblock %}""")

w("teacher/grades.html", """{% extends "dashboard_base.html" %}
{% set breadcrumb_title = course.course_code %}
{% block title %}Grades{% endblock %}{% block page_title %}Grades: {{ course.course_name }}{% endblock %}
{% block dashboard_content %}
<DVTAG class="row g-3">
<DVTAG class="col-lg-4"><DVTAG class="card card-app"><DVTAG class="card-header">Add Grade</DVTAG><DVTAG class="card-body">
<form method="POST">{{ form.hidden_tag() }}
<DVTAG class="mb-2">{{ form.student_id(class="form-select") }}</DVTAG>
<DVTAG class="mb-2">{{ form.assessment_name(class="form-control", placeholder="Assessment") }}</DVTAG>
<DVTAG class="mb-2">{{ form.grade_value(class="form-control", placeholder="Grade") }}</DVTAG>
<DVTAG class="mb-2">{{ form.feedback(class="form-control", rows=2, placeholder="Feedback") }}</DVTAG>
{{ form.submit(class="btn btn-primary w-100") }}</form></DVTAG></DVTAG></DVTAG>
<DVTAG class="col-lg-8"><DVTAG class="card card-app"><DVTAG class="card-body">
{% include 'components/table_controls.html' %}
<table class="table table-app" id="dataTable"><thead><tr><th>Student</th><th>Assessment</th><th>Grade</th><th></th></tr></thead>
<tbody>{% for g in grades %}<tr><td>{{ g.student.full_name }}</td><td>{{ g.assessment_name }}</td><td class="fw-semibold">{{ g.grade_value }}</td>
<td><a href="{{ url_for('teacher.edit_grade', course_id=course.id, grade_id=g.id) }}" class="btn btn-sm btn-outline-primary">Edit</a></td></tr>{% endfor %}</tbody></table>
</DVTAG></DVTAG></DVTAG></DVTAG>{% endblock %}""")

w("teacher/attendance.html", """{% extends "dashboard_base.html" %}
{% block page_title %}Attendance: {{ course.course_name }}{% endblock %}
{% block dashboard_content %}
<DVTAG class="row g-3">
<DVTAG class="col-lg-4"><DVTAG class="card card-app"><DVTAG class="card-header">Record Attendance</DVTAG><DVTAG class="card-body">
<form method="POST">{{ form.hidden_tag() }}
{{ form.student_id(class="form-select mb-2") }}{{ form.attendance_date(class="form-control mb-2") }}
{{ form.status(class="form-select mb-2") }}{{ form.remarks(class="form-control mb-2", rows=2) }}
{{ form.submit(class="btn btn-primary w-100") }}</form></DVTAG></DVTAG></DVTAG>
<DVTAG class="col-lg-8"><DVTAG class="card card-app"><DVTAG class="card-body">
<table class="table table-app" id="dataTable"><thead><tr><th>Student</th><th>Date</th><th>Status</th></tr></thead>
<tbody>{% for r in records %}<tr><td>{{ r.student.full_name }}</td><td>{{ r.attendance_date }}</td><td>{{ r.status.value }}</td></tr>{% endfor %}</tbody></table>
</DVTAG></DVTAG></DVTAG></DVTAG>{% endblock %}""")

w("teacher/grade_edit.html", """{% extends "dashboard_base.html" %}
{% block page_title %}Edit Grade{% endblock %}
{% block dashboard_content %}
<DVTAG class="card card-app col-lg-6"><DVTAG class="card-body">
<form method="POST">{{ form.hidden_tag() }}
{{ form.student_id(class="form-select mb-2") }}{{ form.assessment_name(class="form-control mb-2") }}
{{ form.grade_value(class="form-control mb-2") }}{{ form.feedback(class="form-control mb-2", rows=2) }}
{{ form.submit(class="btn btn-primary") }}</form></DVTAG></DVTAG>{% endblock %}""")

w("teacher/profile.html", """{% extends "dashboard_base.html" %}
{% set breadcrumb_title = "My Profile" %}
{% block page_title %}My Profile{% endblock %}
{% block dashboard_content %}
<DVTAG class="card card-app col-lg-6"><DVTAG class="card-body">
<ul class="list-group list-group-flush">
<li class="list-group-item"><strong>Name</strong><br>{{ current_user.full_name }}</li>
<li class="list-group-item"><strong>Email</strong><br>{{ current_user.email }}</li>
{% if profile %}<li class="list-group-item"><strong>Staff #</strong><br>{{ profile.staff_number }}</li>
<li class="list-group-item"><strong>Department</strong><br>{{ profile.department or '—' }}</li>
<li class="list-group-item"><strong>Phone</strong><br>{{ profile.phone or '—' }}</li>{% endif %}
</ul></DVTAG></DVTAG>{% endblock %}""")

w("teacher/courses.html", """{% extends "dashboard_base.html" %}
{% set breadcrumb_title = "My Courses" %}
{% block page_title %}My Courses{% endblock %}
{% block dashboard_content %}
<DVTAG class="card card-app"><DVTAG class="card-body">{% include 'components/table_controls.html' %}
<table class="table table-app" id="dataTable"><thead><tr><th>Code</th><th>Name</th><th>Actions</th></tr></thead>
<tbody>{% for c in courses %}<tr><td class="fw-semibold">{{ c.course_code }}</td><td>{{ c.course_name }}</td>
<td>
<a href="{{ url_for('teacher.course_students', course_id=c.id) }}" class="btn btn-sm btn-outline-primary">Students</a>
<a href="{{ url_for('teacher.course_grades', course_id=c.id) }}" class="btn btn-sm btn-outline-primary">Grades</a>
<a href="{{ url_for('teacher.course_attendance', course_id=c.id) }}" class="btn btn-sm btn-outline-secondary">Attendance</a>
</td></tr>{% endfor %}</tbody></table></DVTAG></DVTAG>{% endblock %}""")

w("student/profile.html", """{% extends "dashboard_base.html" %}
{% set breadcrumb_title = "My Profile" %}
{% block page_title %}My Profile{% endblock %}
{% block page_subtitle %}<p class="page-subtitle">Update contact information only</p>{% endblock %}
{% block dashboard_content %}
<DVTAG class="card card-app col-lg-7"><DVTAG class="card-body">
<p><strong>Name:</strong> {{ current_user.full_name }}<br><strong>Email:</strong> {{ current_user.email }}<br><strong>Student #:</strong> {{ profile.student_number }}</p>
<form method="POST">{{ form.hidden_tag() }}
<DVTAG class="mb-3">{{ form.phone.label(class="form-label") }}{{ form.phone(class="form-control") }}</DVTAG>
<DVTAG class="mb-3">{{ form.address.label(class="form-label") }}{{ form.address(class="form-control", rows=2) }}</DVTAG>
<DVTAG class="mb-3">{{ form.emergency_contact.label(class="form-label") }}{{ form.emergency_contact(class="form-control") }}</DVTAG>
{{ form.submit(class="btn btn-primary") }}</form></DVTAG></DVTAG>{% endblock %}""")

w("student/courses.html", """{% extends "dashboard_base.html" %}
{% set breadcrumb_title = "Courses" %}
{% block page_title %}Available Courses{% endblock %}
{% block dashboard_content %}
<DVTAG class="card card-app"><DVTAG class="card-body">{% include 'components/table_controls.html' %}
<table class="table table-app" id="dataTable"><thead><tr><th>Code</th><th>Name</th><th>Teacher</th><th></th></tr></thead>
<tbody>{% for c in courses %}<tr><td>{{ c.course_code }}</td><td>{{ c.course_name }}</td><td>{{ c.teacher.full_name }}</td>
<td>{% if c.id in enrolled_ids %}<span class="badge badge-status-active">Enrolled</span>{% else %}
<form method="POST" action="{{ url_for('student.enroll', course_id=c.id) }}"><input type="hidden" name="csrf_token" value="{{ csrf_token() }}">
<button class="btn btn-sm btn-primary">Enroll</button></form>{% endif %}</td></tr>{% endfor %}</tbody></table>
</DVTAG></DVTAG>{% endblock %}""")

w("student/grades.html", """{% extends "dashboard_base.html" %}
{% set breadcrumb_title = "My Grades" %}
{% block page_title %}My Grades{% endblock %}
{% block dashboard_content %}
<DVTAG class="card card-app"><DVTAG class="card-body">{% include 'components/table_controls.html' %}
<table class="table table-app" id="dataTable"><thead><tr><th>Course</th><th>Assessment</th><th>Grade</th><th></th></tr></thead>
<tbody>{% for g in grades %}<tr><td>{{ g.course.course_code }}</td><td>{{ g.assessment_name }}</td><td class="fw-semibold">{{ g.grade_value }}</td>
<td><a href="{{ url_for('student.grade_detail', grade_id=g.id) }}" class="btn btn-sm btn-outline-primary">Details</a></td></tr>{% endfor %}</tbody></table>
</DVTAG></DVTAG>{% endblock %}""")

w("student/grade_detail.html", """{% extends "dashboard_base.html" %}
{% block page_title %}Grade Detail{% endblock %}
{% block dashboard_content %}
<DVTAG class="card card-app col-lg-6"><DVTAG class="card-body">
<ul class="list-group list-group-flush">
<li class="list-group-item"><strong>Course</strong><br>{{ grade.course.course_name }}</li>
<li class="list-group-item"><strong>Assessment</strong><br>{{ grade.assessment_name }}</li>
<li class="list-group-item"><strong>Grade</strong><br><span class="fs-4 fw-bold text-primary">{{ grade.grade_value }}</span></li>
<li class="list-group-item"><strong>Feedback</strong><br>{{ grade.feedback or '—' }}</li>
</ul>
<a href="{{ url_for('student.grades') }}" class="btn btn-link mt-3">&larr; Back to grades</a>
</DVTAG></DVTAG>{% endblock %}""")

w("student/attendance.html", """{% extends "dashboard_base.html" %}
{% set breadcrumb_title = "My Attendance" %}
{% block page_title %}My Attendance{% endblock %}
{% block dashboard_content %}
<DVTAG class="card card-app"><DVTAG class="card-body">{% include 'components/table_controls.html' %}
<table class="table table-app" id="dataTable"><thead><tr><th>Course</th><th>Date</th><th>Status</th><th>Remarks</th></tr></thead>
<tbody>{% for r in records %}<tr><td>{{ r.course.course_code }}</td><td>{{ r.attendance_date }}</td><td>{{ r.status.value }}</td><td>{{ r.remarks or '' }}</td></tr>{% endfor %}</tbody></table>
</DVTAG></DVTAG>{% endblock %}""")

print("fixed")
