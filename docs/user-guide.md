# User Guide

How **Admin**, **Teacher**, and **Student** users work with the Secure Student Management System.

**URL:** [http://127.0.0.1:5000](http://127.0.0.1:5000) (local dev)

---

## Sign in (all roles)

1. Open **Sign in** (`/login`).
2. Enter institutional **email** and **password**.
3. **First login:** scan the QR code with an authenticator app (Google Authenticator, Authy, etc.), enter the 6-digit code, and **save recovery codes**.
4. **Returning users:** enter the current TOTP code at **Verify 2FA**.
5. You are redirected to your role dashboard.

**Sign out:** use **Logout** in the top bar.

---

## Student

| Task | Navigation |
|------|------------|
| View dashboard | `/student/dashboard` — enrollments, GPA, attendance summary |
| Edit profile | **Profile** → **Edit Profile** (phone, address, emergency contact) |
| Security / 2FA | **Security Settings** — view 2FA status, regenerate backup codes |
| Browse courses | **Courses** — available active courses |
| Enroll | **Enroll** on a course → confirm |
| My enrollments | **Enrollments** |
| Grades | **Grades** — list and detail |
| Attendance | **Attendance** — records and chart |

Students see **only their own** academic data.

---

## Teacher

| Task | Navigation |
|------|------------|
| Dashboard | `/teacher/dashboard` — courses, charts |
| My courses | **Courses** — assigned courses only |
| Class roster | Course → **Students** |
| Student record | Student → academic history for that course |
| Add grade | **Grades** → **Add Grade** (course + student + assessment) |
| Mark attendance | **Attendance** → select course and date → save grid |
| Attendance history | **Attendance** → **History** |

Teachers cannot access courses assigned to other teachers.

---

## Admin

| Task | Navigation |
|------|------------|
| Dashboard | `/admin/dashboard` — statistics |
| Users | **Users** — create, edit, deactivate, reset 2FA |
| Courses | **Courses** — create, edit, assign teacher |
| Students / teachers | **Students**, **Teachers** directories |
| Records | **Enrollments**, **Grades**, **Attendance** (global views) |
| Audit logs | **Audit Logs** — filter, export CSV |
| Security | **Security Dashboard** — risk score, suspicious IPs |

See [admin-guide.md](admin-guide.md) for security procedures.

---

## Common messages

| Message | Meaning |
|---------|---------|
| Invalid email or password | Wrong credentials or inactive account |
| Invalid verification code | Wrong TOTP — try again or use recovery code |
| 403 Forbidden | Your role cannot access that page (logged) |
| Too many requests (429) | Rate limit — wait one minute |

---

## Screenshot placeholders

| # | Role | Screen |
|---|------|--------|
| 1 | All | Login |
| 2 | Student | Dashboard |
| 3 | Teacher | Mark attendance |
| 4 | Admin | User list |

---

## Related documents

- [admin-guide.md](admin-guide.md)
- [README.md](../README.md)
