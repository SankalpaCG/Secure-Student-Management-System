"""Generate/update UI templates for the design system."""
import re
from pathlib import Path

T = Path(__file__).resolve().parents[1] / "src" / "app" / "templates"
TAG = "DVTAG"


def w(path, content):
    p = T / path
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(re.sub(rf"</?{TAG}\b", lambda m: m.group(0).replace(TAG, "motion").replace("motion", "div"), content))


TABLE_WRAP = """
<DVTAG class="card card-app">
  <DVTAG class="card-body">
    {% include 'components/table_controls.html' %}
    <DVTAG class="table-responsive">
      <table class="table table-app" id="dataTable">
        {thead}
        <tbody>{tbody}</tbody>
      </table>
    </DVTAG>
  </DVTAG>
</DVTAG>
"""

w("admin/dashboard.html", """{% extends "dashboard_base.html" %}
{% set breadcrumb_title = "Dashboard" %}
{% block title %}Admin Dashboard{% endblock %}
{% block page_title %}Admin Dashboard{% endblock %}
{% block page_subtitle %}<p class="page-subtitle">System overview and management</p>{% endblock %}
{% block dashboard_content %}
<DVTAG class="row g-3 mb-4">
  {% for icon, label, value in [
    ('people','Users',stats.users),('mortarboard','Students',stats.students),
    ('person-badge','Teachers',stats.teachers),('journal-bookmark','Courses',stats.courses),
    ('award','Grades',stats.grades),('calendar-check','Attendance',stats.attendance)] %}
  <DVTAG class="col-6 col-md-4 col-xl-2">
    <DVTAG class="card card-app stat-card h-100">
      <DVTAG class="card-body d-flex align-items-center gap-3">
        <DVTAG class="stat-icon"><i class="bi bi-{{ icon }}"></i></DVTAG>
        <DVTAG><DVTAG class="stat-label">{{ label }}</DVTAG><DVTAG class="stat-value">{{ value }}</DVTAG></DVTAG>
      </DVTAG>
    </DVTAG>
  </DVTAG>
  {% endfor %}
</DVTAG>
<DVTAG class="row g-3">
  <DVTAG class="col-lg-8">
    <DVTAG class="card card-app"><DVTAG class="card-header">Users by Role</DVTAG>
      <DVTAG class="card-body"><DVTAG class="chart-container"><canvas id="roleChart"></canvas></DVTAG></DVTAG>
    </DVTAG>
  </DVTAG>
  <DVTAG class="col-lg-4">
    <DVTAG class="card card-app h-100"><DVTAG class="card-body">
      <h6 class="fw-semibold mb-3">Quick Actions</h6>
      <DVTAG class="d-grid gap-2">
        <a href="{{ url_for('admin.users') }}" class="btn btn-outline-primary"><i class="bi bi-people me-2"></i>Users</a>
        <a href="{{ url_for('admin.courses') }}" class="btn btn-outline-primary"><i class="bi bi-journal-bookmark me-2"></i>Courses</a>
        <a href="{{ url_for('admin.security_dashboard') }}" class="btn btn-outline-primary"><i class="bi bi-shield-lock me-2"></i>Security</a>
      </DVTAG>
    </DVTAG></DVTAG>
  </DVTAG>
</DVTAG>
{% endblock %}
{% block extra_js %}
<script>
new Chart(document.getElementById('roleChart'), {
  type: 'doughnut',
  data: { labels: {{ role_counts.keys()|list|tojson }}, datasets: [{ data: {{ role_counts.values()|list|tojson }}, backgroundColor: ['#2563eb','#f59e0b','#6366f1'] }] },
  options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { position: 'bottom' } } }
});
</script>
{% endblock %}""")

w("admin/users.html", """{% extends "dashboard_base.html" %}
{% set breadcrumb_title = "Users" %}
{% block title %}Users{% endblock %}
{% block page_title %}User Management{% endblock %}
{% block page_subtitle %}<p class="page-subtitle">Create, view, update, and deactivate accounts</p>{% endblock %}
{% block page_actions %}<a href="{{ url_for('admin.create_user') }}" class="btn btn-primary"><i class="bi bi-person-plus me-1"></i>Create User</a>{% endblock %}
{% block dashboard_content %}
<DVTAG class="card card-app"><DVTAG class="card-body">
{% include 'components/table_controls.html' %}
<DVTAG class="table-responsive"><table class="table table-app" id="dataTable">
<thead><tr><th>Name</th><th>Email</th><th>Role</th><th>Status</th><th class="text-end">Actions</th></tr></thead>
<tbody>{% for user in users %}<tr>
<td class="fw-medium">{{ user.full_name }}</td><td>{{ user.email }}</td>
<td><span class="badge badge-role-{{ user.role.value|lower }}">{{ user.role.value }}</span></td>
<td>{% if user.is_active %}<span class="badge badge-status-active">Active</span>{% else %}<span class="badge badge-status-inactive">Inactive</span>{% endif %}</td>
<td class="text-end">
<a href="{{ url_for('admin.edit_user', user_id=user.id) }}" class="btn btn-sm btn-outline-primary"><i class="bi bi-pencil"></i></a>
{% if user.is_active and user.id != current_user.id %}
<form method="POST" action="{{ url_for('admin.deactivate_user', user_id=user.id) }}" class="d-inline">
<input type="hidden" name="csrf_token" value="{{ csrf_token() }}">
<button class="btn btn-sm btn-outline-danger" onclick="return confirm('Deactivate?')"><i class="bi bi-person-x"></i></button>
</form>{% endif %}</td></tr>{% endfor %}</tbody></table></DVTAG></DVTAG></DVTAG>
{% endblock %}""")

w("admin/courses.html", """{% extends "dashboard_base.html" %}
{% set breadcrumb_title = "Courses" %}
{% block title %}Courses{% endblock %}
{% block page_title %}Course Management{% endblock %}
{% block page_actions %}<a href="{{ url_for('admin.create_course') }}" class="btn btn-primary"><i class="bi bi-plus-lg me-1"></i>Create Course</a>{% endblock %}
{% block dashboard_content %}
<DVTAG class="card card-app"><DVTAG class="card-body">
{% include 'components/table_controls.html' %}
<table class="table table-app" id="dataTable"><thead><tr><th>Code</th><th>Name</th><th>Teacher</th><th></th></tr></thead>
<tbody>{% for c in courses %}<tr>
<td><span class="fw-semibold">{{ c.course_code }}</span></td><td>{{ c.course_name }}</td><td>{{ c.teacher.full_name }}</td>
<td class="text-end"><a href="{{ url_for('admin.edit_course', course_id=c.id) }}" class="btn btn-sm btn-outline-primary"><i class="bi bi-pencil"></i> Edit</a></td>
</tr>{% endfor %}</tbody></table></DVTAG></DVTAG>
{% endblock %}""")

w("admin/enrollments.html", """{% extends "dashboard_base.html" %}
{% set breadcrumb_title = "Enrollments" %}
{% block title %}Enrollments{% endblock %}
{% block page_title %}Enrollments{% endblock %}
{% block dashboard_content %}
<DVTAG class="card card-app"><DVTAG class="card-body">
{% include 'components/table_controls.html' %}
<table class="table table-app" id="dataTable"><thead><tr><th>Student</th><th>Course</th><th>Status</th><th>Enrolled</th></tr></thead>
<tbody>{% for e in enrollments %}<tr>
<td>{{ e.student.full_name }}</td><td>{{ e.course.course_code }} — {{ e.course.course_name }}</td>
<td><span class="badge bg-secondary">{{ e.status.value }}</span></td><td>{{ e.enrolled_at.strftime('%Y-%m-%d') }}</td>
</tr>{% endfor %}</tbody></table></DVTAG></DVTAG>
{% endblock %}""")

w("admin/security_dashboard.html", """{% extends "dashboard_base.html" %}
{% set breadcrumb_title = "Security Dashboard" %}
{% block title %}Security{% endblock %}
{% block page_title %}Security Dashboard{% endblock %}
{% block dashboard_content %}
<DVTAG class="row g-3 mb-4">
  <DVTAG class="col-md-3"><DVTAG class="card card-app stat-card"><DVTAG class="card-body">
    <DVTAG class="stat-label">2FA Enabled</DVTAG><DVTAG class="stat-value">{{ users_2fa }}/{{ users_total }}</DVTAG>
  </DVTAG></DVTAG></DVTAG>
  <DVTAG class="col-md-3"><DVTAG class="card card-app stat-card"><DVTAG class="card-body">
    <DVTAG class="stat-label">Failed Logins</DVTAG><DVTAG class="stat-value">{{ failed_logins }}</DVTAG>
  </DVTAG></DVTAG></DVTAG>
  <DVTAG class="col-md-3"><DVTAG class="card card-app stat-card"><DVTAG class="card-body">
    <DVTAG class="stat-label">Failed 2FA</DVTAG><DVTAG class="stat-value">{{ failed_2fa }}</DVTAG>
  </DVTAG></DVTAG></DVTAG>
</DVTAG>
<DVTAG class="card card-app"><DVTAG class="card-header">Audit Events by Action</DVTAG>
<DVTAG class="card-body"><DVTAG class="chart-container"><canvas id="auditChart"></canvas></DVTAG></DVTAG>
</DVTAG>
{% endblock %}
{% block extra_js %}
<script>
new Chart(document.getElementById('auditChart'), {
  type: 'bar',
  data: { labels: {{ audit_by_action|map(attribute=0)|list|tojson }}, datasets: [{ label: 'Events', data: {{ audit_by_action|map(attribute=1)|list|tojson }}, backgroundColor: '#2563eb' }] },
  options: { responsive: true, maintainAspectRatio: false }
});
</script>
{% endblock %}""")

w("admin/students.html", """{% extends "dashboard_base.html" %}
{% set breadcrumb_title = "Students" %}
{% block title %}Students{% endblock %}{% block page_title %}All Students{% endblock %}
{% block dashboard_content %}
<DVTAG class="card card-app"><DVTAG class="card-body">{% include 'components/table_controls.html' %}
<table class="table table-app" id="dataTable"><thead><tr><th>#</th><th>Name</th><th>Email</th><th>Phone</th></tr></thead>
<tbody>{% for p in profiles %}<tr><td>{{ p.student_number }}</td><td>{{ p.user.full_name }}</td><td>{{ p.user.email }}</td><td>{{ p.phone or '—' }}</td></tr>{% endfor %}</tbody></table>
</DVTAG></DVTAG>{% endblock %}""")

w("admin/teachers.html", """{% extends "dashboard_base.html" %}
{% set breadcrumb_title = "Teachers" %}
{% block title %}Teachers{% endblock %}{% block page_title %}All Teachers{% endblock %}
{% block dashboard_content %}
<DVTAG class="card card-app"><DVTAG class="card-body">{% include 'components/table_controls.html' %}
<table class="table table-app" id="dataTable"><thead><tr><th>Staff #</th><th>Name</th><th>Department</th><th>Email</th></tr></thead>
<tbody>{% for p in profiles %}<tr><td>{{ p.staff_number }}</td><td>{{ p.user.full_name }}</td><td>{{ p.department or '—' }}</td><td>{{ p.user.email }}</td></tr>{% endfor %}</tbody></table>
</DVTAG></DVTAG>{% endblock %}""")

w("admin/grades.html", """{% extends "dashboard_base.html" %}
{% set breadcrumb_title = "Grades" %}
{% block title %}Grades{% endblock %}{% block page_title %}All Grades{% endblock %}
{% block dashboard_content %}
<DVTAG class="card card-app"><DVTAG class="card-body">{% include 'components/table_controls.html' %}
<table class="table table-app" id="dataTable"><thead><tr><th>Student</th><th>Course</th><th>Assessment</th><th>Grade</th></tr></thead>
<tbody>{% for g in grades %}<tr><td>{{ g.student.full_name }}</td><td>{{ g.course.course_code }}</td><td>{{ g.assessment_name }}</td><td><span class="fw-semibold">{{ g.grade_value }}</span></td></tr>{% endfor %}</tbody></table>
</DVTAG></DVTAG>{% endblock %}""")

w("admin/attendance.html", """{% extends "dashboard_base.html" %}
{% set breadcrumb_title = "Attendance" %}
{% block title %}Attendance{% endblock %}{% block page_title %}All Attendance{% endblock %}
{% block dashboard_content %}
<DVTAG class="card card-app"><DVTAG class="card-body">{% include 'components/table_controls.html' %}
<table class="table table-app" id="dataTable"><thead><tr><th>Student</th><th>Course</th><th>Date</th><th>Status</th></tr></thead>
<tbody>{% for r in records %}<tr><td>{{ r.student.full_name }}</td><td>{{ r.course.course_code }}</td><td>{{ r.attendance_date }}</td><td>{{ r.status.value }}</td></tr>{% endfor %}</tbody></table>
</DVTAG></DVTAG>{% endblock %}""")

w("admin/audit_logs.html", """{% extends "dashboard_base.html" %}
{% set breadcrumb_title = "Audit Logs" %}
{% block title %}Audit Logs{% endblock %}{% block page_title %}Audit Logs{% endblock %}
{% block dashboard_content %}
<DVTAG class="card card-app"><DVTAG class="card-body">{% include 'components/table_controls.html' %}
<table class="table table-app table-sm" id="dataTable"><thead><tr><th>Time</th><th>User</th><th>Action</th><th>Target</th><th>IP</th></tr></thead>
<tbody>{% for log in logs %}<tr><td>{{ log.timestamp.strftime('%Y-%m-%d %H:%M') }}</td><td>{{ log.user.email if log.user else '—' }}</td><td><code>{{ log.action }}</code></td><td>{{ log.target_type }} #{{ log.target_id or '' }}</td><td>{{ log.ip_address or '' }}</td></tr>{% endfor %}</tbody></table>
</DVTAG></DVTAG>{% endblock %}""")

w("admin/user_form.html", """{% extends "dashboard_base.html" %}
{% block title %}{{ title }}{% endblock %}{% block page_title %}{{ title }}{% endblock %}
{% block dashboard_content %}
<DVTAG class="card card-app col-lg-8"><DVTAG class="card-body">
<form method="POST">{{ form.hidden_tag() }}
<DVTAG class="mb-3">{{ form.full_name.label(class="form-label") }}{{ form.full_name(class="form-control") }}</DVTAG>
<DVTAG class="mb-3">{{ form.email.label(class="form-label") }}{{ form.email(class="form-control") }}</DVTAG>
<DVTAG class="mb-3">{{ form.role.label(class="form-label") }}{{ form.role(class="form-select") }}</DVTAG>
<DVTAG class="mb-3">{{ form.password.label(class="form-label") }}{{ form.password(class="form-control") }}</DVTAG>
<DVTAG class="mb-3 form-check">{{ form.is_active() }} {{ form.is_active.label(class="form-check-label") }}</DVTAG>
{{ form.submit(class="btn btn-primary") }} <a href="{{ url_for('admin.users') }}" class="btn btn-link">Cancel</a>
</form></DVTAG></DVTAG>{% endblock %}""")

w("admin/course_form.html", """{% extends "dashboard_base.html" %}
{% block title %}{{ title }}{% endblock %}{% block page_title %}{{ title }}{% endblock %}
{% block dashboard_content %}
<DVTAG class="card card-app col-lg-8"><DVTAG class="card-body">
<form method="POST">{{ form.hidden_tag() }}
<DVTAG class="mb-3">{{ form.course_code.label }} {{ form.course_code(class="form-control") }}</DVTAG>
<DVTAG class="mb-3">{{ form.course_name.label }} {{ form.course_name(class="form-control") }}</DVTAG>
<DVTAG class="mb-3">{{ form.description.label }} {{ form.description(class="form-control", rows=3) }}</DVTAG>
<DVTAG class="mb-3">{{ form.teacher_id.label }} {{ form.teacher_id(class="form-select") }}</DVTAG>
{{ form.submit(class="btn btn-primary") }} <a href="{{ url_for('admin.courses') }}">Cancel</a>
</form></DVTAG></DVTAG>{% endblock %}""")

# Teacher templates
w("teacher/dashboard.html", """{% extends "dashboard_base.html" %}
{% set breadcrumb_title = "Dashboard" %}
{% block title %}Teacher Dashboard{% endblock %}{% block page_title %}Teacher Dashboard{% endblock %}
{% block page_subtitle %}<p class="page-subtitle">Your assigned courses and teaching tools</p>{% endblock %}
{% block dashboard_content %}
{% if courses %}
<DVTAG class="row g-3">{% for c in courses %}
<DVTAG class="col-md-6 col-lg-4">
  <DVTAG class="card card-app h-100"><DVTAG class="card-body">
    <h5 class="fw-semibold">{{ c.course_code }}</h5><p class="text-muted mb-3">{{ c.course_name }}</p>
    <a href="{{ url_for('teacher.course_students', course_id=c.id) }}" class="btn btn-sm btn-outline-primary me-1">Students</a>
    <a href="{{ url_for('teacher.course_grades', course_id=c.id) }}" class="btn btn-sm btn-outline-primary">Grades</a>
  </DVTAG></DVTAG>
</DVTAG>{% endfor %}</DVTAG>
{% else %}<DVTAG class="alert alert-info">No courses assigned yet.</DVTAG>{% endif %}
{% endblock %}""")

for name, title, link_tpl in [
    ("students_hub", "Course Students", "teacher.course_students"),
    ("grades_hub", "Manage Grades", "teacher.course_grades"),
    ("attendance_hub", "Attendance", "teacher.course_attendance"),
]:
    w(f"teacher/{name}.html", f"""{{% extends "dashboard_base.html" %}}
{{% set breadcrumb_title = "{title}" %}}
{{% block title %}}{title}{{% endblock %}}{{% block page_title %}}{title}{{% endblock %}}
{{% block page_subtitle %}}<p class="page-subtitle">Select a course to continue</p>{{% endblock %}}
{{% block dashboard_content %}}
<DVTAG class="row g-3">{{% for c in courses %}}
<DVTAG class="col-md-6"><DVTAG class="card card-app"><DVTAG class="card-body d-flex justify-content-between align-items-center">
  <DVTAG><strong>{{{{ c.course_code }}}}</strong><br><span class="text-muted">{{{{ c.course_name }}}}</span></DVTAG>
  <a href="{{{{ url_for('{link_tpl}', course_id=c.id) }}}}" class="btn btn-primary btn-sm">Open <i class="bi bi-arrow-right"></i></a>
</DVTAG></DVTAG></DVTAG>{{% endfor %}}</DVTAG>
{{% endblock %}}""")

w("teacher/grade_analytics.html", """{% extends "dashboard_base.html" %}
{% set breadcrumb_title = "Grade Analytics" %}
{% block title %}Grade Analytics{% endblock %}{% block page_title %}Grade Analytics{% endblock %}
{% block dashboard_content %}
<DVTAG class="card card-app"><DVTAG class="card-header">Average Grade by Course</DVTAG>
<DVTAG class="card-body"><DVTAG class="chart-container"><canvas id="gradeChart"></canvas></DVTAG></DVTAG>
</DVTAG>{% endblock %}
{% block extra_js %}
<script>new Chart(document.getElementById('gradeChart'),{type:'bar',data:{labels:{{ chart_labels|tojson }},datasets:[{label:'Avg Grade',data:{{ chart_values|tojson }},backgroundColor:'#2563eb'}]},options:{responsive:true,maintainAspectRatio:false}});</script>
{% endblock %}""")

# Student templates  
w("student/dashboard.html", """{% extends "dashboard_base.html" %}
{% set breadcrumb_title = "Dashboard" %}
{% block title %}Student Dashboard{% endblock %}{% block page_title %}Student Dashboard{% endblock %}
{% block dashboard_content %}
<DVTAG class="row g-3">
  <DVTAG class="col-md-6"><DVTAG class="card card-app stat-card"><DVTAG class="card-body d-flex gap-3 align-items-center">
    <DVTAG class="stat-icon"><i class="bi bi-card-checklist"></i></DVTAG>
    <DVTAG><DVTAG class="stat-label">Enrollments</DVTAG><DVTAG class="stat-value">{{ enrollments_count }}</DVTAG></DVTAG>
  </DVTAG></DVTAG></DVTAG>
  <DVTAG class="col-md-6"><DVTAG class="card card-app stat-card"><DVTAG class="card-body d-flex gap-3 align-items-center">
    <DVTAG class="stat-icon"><i class="bi bi-award"></i></DVTAG>
    <DVTAG><DVTAG class="stat-label">Grades</DVTAG><DVTAG class="stat-value">{{ grades_count }}</DVTAG></DVTAG>
  </DVTAG></DVTAG></DVTAG>
</DVTAG>
{% endblock %}""")

w("student/enrollments.html", """{% extends "dashboard_base.html" %}
{% set breadcrumb_title = "My Enrollments" %}
{% block title %}Enrollments{% endblock %}{% block page_title %}My Enrollments{% endblock %}
{% block dashboard_content %}
<DVTAG class="card card-app"><DVTAG class="card-body">{% include 'components/table_controls.html' %}
<table class="table table-app" id="dataTable"><thead><tr><th>Course</th><th>Status</th><th>Enrolled</th></tr></thead>
<tbody>{% for e in enrollments %}<tr><td>{{ e.course.course_code }} — {{ e.course.course_name }}</td><td>{{ e.status.value }}</td><td>{{ e.enrolled_at.strftime('%Y-%m-%d') }}</td></tr>{% endfor %}</tbody></table>
</DVTAG></DVTAG>{% endblock %}""")

w("student/security_settings.html", """{% extends "dashboard_base.html" %}
{% set breadcrumb_title = "Security Settings" %}
{% block title %}Security{% endblock %}{% block page_title %}Security Settings{% endblock %}
{% block dashboard_content %}
<DVTAG class="card card-app col-lg-8"><DVTAG class="card-body">
<ul class="list-group list-group-flush">
<li class="list-group-item d-flex justify-content-between"><span>Two-Factor Authentication</span>
  {% if current_user.is_2fa_enabled %}<span class="badge badge-status-active">Enabled</span>{% else %}<span class="badge badge-status-inactive">Disabled</span>{% endif %}</li>
<li class="list-group-item d-flex justify-content-between"><span>Unused Recovery Codes</span><strong>{{ unused_codes }}</strong></li>
<li class="list-group-item"><span class="text-muted small">Contact an administrator to reset 2FA if you lose access to your authenticator.</span></li>
</ul></DVTAG></DVTAG>{% endblock %}""")

print("Templates updated.")
