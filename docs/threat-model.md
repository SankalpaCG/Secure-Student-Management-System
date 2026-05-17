# Threat Model (STRIDE)

Scope: Secure Student Management System web UI + JWT API on a university network. Trust boundary: Internet/untrusted client → Flask app → MySQL.

---

## Assets

| Asset | Sensitivity | Location |
|-------|-------------|----------|
| User credentials | High | `users.password_hash` |
| TOTP secrets | High | `users.totp_secret` (encrypted) |
| Student PII | High | `student_profiles` (encrypted fields) |
| Grades / attendance | Medium | `grades`, `attendances` |
| JWT / session tokens | High | Client storage, `revoked_tokens` |
| Audit logs | Medium | `audit_logs` |
| Admin actions | High | User/course management |

---

## STRIDE analysis

### Spoofing

| Threat | Attack vector | Impact | Mitigation | Residual risk |
|--------|---------------|--------|------------|---------------|
| Stolen password | Phishing, credential stuffing | Account takeover | 2FA mandatory; rate limits; strong password policy | User shares TOTP |
| Session hijack | XSS, network sniffing | Impersonation | HttpOnly cookies; CSP; HSTS in production | Malware on client |
| JWT forgery | Stolen signing key | API abuse | `JWT_SECRET_KEY` in env; short TTL; revocation table | Key leakage from misconfig |

### Tampering

| Threat | Attack vector | Impact | Mitigation | Residual risk |
|--------|---------------|--------|------------|---------------|
| CSRF state change | Malicious site POST | Unauthorized action | Flask-WTF CSRF on forms | API exempt (token auth) |
| IDOR grade/profile | Guess URLs | Data breach | `access_control` + audit `IDOR_ATTEMPT` | Logic bugs in new routes |
| SQL injection | Malicious input | DB compromise | SQLAlchemy ORM only | Future raw SQL mistakes |

### Repudiation

| Threat | Attack vector | Impact | Mitigation | Residual risk |
|--------|---------------|--------|------------|---------------|
| Deny admin action | User claims "I didn't" | Dispute | Central `audit_logs` with user, IP, action | Logs not WORM/immutable |
| Log deletion | Compromised admin DB | No trace | DB backups; least privilege on MySQL | Insider with DB access |

### Information disclosure

| Threat | Attack vector | Impact | Mitigation | Residual risk |
|--------|---------------|--------|------------|---------------|
| Horizontal access | Student views other grade | Privacy breach | Ownership checks; 403 | New endpoint without check |
| XSS | Stored script in profile | Cookie/token theft | Bleach + Jinja escape | `|safe` misuse |
| Error verbosity | Stack traces | Info leak | Custom 500 page in production | Debug mode left on |
| API over-fetch | `/api/admin/users` as student | Enumeration | JWT + RBAC | Misconfigured route |

### Denial of service

| Threat | Attack vector | Impact | Mitigation | Residual risk |
|--------|---------------|--------|------------|---------------|
| Login flood | Automated POST | Lockout noise | Rate limit 5/min; 429 page | Distributed attack |
| DB exhaustion | Heavy queries | Outage | Indexes; connection pool | No query timeout tuning |

### Elevation of privilege

| Threat | Attack vector | Impact | Mitigation | Residual risk |
|--------|---------------|--------|------------|---------------|
| Student → admin | URL `/admin/*` | Full control | `@admin_required` | Decorator omitted |
| Teacher → other course | Course ID tampering | Wrong class data | `require_teacher_course` | API parameter bypass |
| Role assignment | Mass assignment | Admin created wrongly | Admin-only user forms | Compromised admin account |

---

## Attack surface summary

| Surface | Examples |
|---------|----------|
| Web forms | Login, 2FA, profile, grades, enrollment |
| REST API | `/api/auth/*`, `/api/student/*`, `/api/teacher/*`, `/api/admin/*` |
| Static/session | Cookies, JWT Bearer header |
| Operations | `flask seed`, MySQL admin, GitHub secrets |

---

## Mitigation priorities

1. **Enforce RBAC and ownership** on every new route (web + API).
2. **Keep secrets in environment** — never commit `.env`.
3. **Run CI gates** — Bandit High+, pip-audit, pytest security modules.
4. **Monitor** via Security Dashboard and audit log exports.

---

## Related documents

- [security-controls.md](security-controls.md)
- [incident-response.md](incident-response.md)
- [testing-plan.md](testing-plan.md)
