# System Architecture

## High-level view

```
┌──────────────┐     HTTPS      ┌─────────────────────────────────────┐
│   Browser    │ ─────────────► │  Flask application (src/app)         │
│  (Bootstrap) │                │  ┌─────────┐ ┌─────────┐ ┌────────┐ │
└──────────────┘                │  │  auth   │ │ admin   │ │ teacher│ │
                                │  └────┬────┘ └────┬────┘ └───┬────┘ │
┌──────────────┐     JSON       │       │    RBAC    │          │    │
│ API client   │ ─────────────► │  ┌────▼────────────▼──────────▼──┐ │
└──────────────┘                │  │ student │ api (JWT)            │ │
                                │  └────┬────────────────────────────┘ │
                                │       │ services: audit, jwt        │
                                │       ▼                             │
                                │  SQLAlchemy ORM ──► MySQL             │
                                └─────────────────────────────────────┘
```

---

## Application layers

| Layer | Location | Responsibility |
|-------|----------|----------------|
| Blueprints | `auth/`, `admin/`, `teacher/`, `student/`, `api/` | HTTP routes, forms, templates |
| Services | `*/services.py`, `services/audit_service.py` | Business logic, aggregations |
| Access control | `utils/access_control.py`, `utils/permissions.py` | Ownership and role checks |
| Models | `models/` | Persistence, relationships |
| Cross-cutting | `security/`, `utils/sanitize.py`, `extensions.py` | Headers, CSRF, limiter, DB |

---

## Authentication flow

```
User → GET /login
     → POST email + password (rate limited)
     → verify_password + is_active
     → session: pre_2fa_user_id set
     → if first time: GET /setup-2fa (QR + verify TOTP)
     → else: GET /verify-2fa
     → POST TOTP or recovery code
     → session: 2fa_verified = True
     → Flask-Login login_user()
     → redirect to role dashboard
```

Session keys are cleared on `logout` via `logout_fully()`. API clients use a **separate** JWT path (`/api/auth/login`) with TOTP when 2FA is enabled.

---

## 2FA flow

| Step | Component | Detail |
|------|-----------|--------|
| Secret generation | `utils/totp.py` | PyOTP base32 secret |
| Storage | `User.totp_secret` | Fernet-encrypted |
| Verification | `verify_totp_code()` | ±1 time window |
| Recovery | `RecoveryCode` model | Hashed single-use codes |
| Enforcement | `@two_factor_required` | Blocks dashboards until verified |

---

## RBAC flow

```
Request → Flask-Login (user loaded)
        → @two_factor_required (2fa_verified?)
        → @roles_required(ADMIN|TEACHER|STUDENT)
        → route handler
        → optional: access_control (course/grade ownership)
        → response OR abort(403) + audit log
```

API routes use `@jwt_required` + `@roles_required` with the same ownership helpers in `access_control.py`.

---

## Database relationships (summary)

```
User ──┬── StudentProfile (1:1)
       ├── TeacherProfile (1:1)
       ├── courses_taught (Teacher → Course)
       ├── enrollments (Student → Enrollment → Course)
       ├── grades_received / grades_recorded
       └── audit_logs

Course ── Enrollment, Grade, Attendance
RevokedToken (JWT jti blacklist, standalone)
AuditLog → User (optional FK)
```

Unique constraints: `User.email`, `Course.course_code`, `StudentProfile.student_number`, attendance per (student, course, date).

---

## CI/CD architecture

```
GitHub (push/PR)
    │
    ├─► build job ──────────────┐
    │                           │
    ├─► sast (Bandit) ◄─────────┤
    ├─► test (pytest + MySQL) ◄──┤
    ├─► dependency-scan ◄───────┤
    ├─► secret-scan ◄───────────┘
    │
    ├─► dast (placeholder)
    └─► deploy (placeholder)
```

Artifacts: Bandit HTML/JSON, pip-audit JSON, coverage XML. See [devsecops-pipeline.md](devsecops-pipeline.md).

---

## Related documents

- [threat-model.md](threat-model.md)
- [security-controls.md](security-controls.md)
- [security-dashboard.md](security-dashboard.md)
