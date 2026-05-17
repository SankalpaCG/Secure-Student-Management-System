# Security Controls

Mapping of implemented controls to **OWASP Top 10 (2021)**. Each section includes evidence and test pointers.

---

## OWASP Top 10 summary

| ID | Category | Primary controls in this project |
|----|----------|----------------------------------|
| **A01** | Broken Access Control | RBAC decorators, `access_control.py`, IDOR logging, 403 pages |
| **A02** | Cryptographic Failures | PBKDF2 passwords, Fernet PII/TOTP, `JWT_SECRET_KEY`, no plaintext secrets in API |
| **A03** | Injection | SQLAlchemy ORM, Bleach sanitization, Jinja auto-escape |
| **A04** | Insecure Design | 2FA by default, rate limits, separate test DB, fail-closed auth |
| **A05** | Security Misconfiguration | CSP/HSTS headers, secure cookies (prod), `.env.example` |
| **A06** | Vulnerable Components | `pip-audit` in CI; pinned `requirements.txt` |
| **A07** | Auth Failures | 2FA, session timeout, JWT expiry/revocation, account `is_active` |
| **A08** | Software/Data Integrity | GitHub Actions pipeline; no unsigned deps policy (document) |
| **A09** | Logging Failures | `audit_service`, severity, Security Dashboard, export CSV |
| **A10** | SSRF | Not applicable (no user-controlled outbound fetch) |

---

## A01 — Broken Access Control

| Control | Implementation |
|---------|----------------|
| Role decorators | `admin_required`, `teacher_required`, `student_required` |
| Ownership | `require_teacher_course`, `require_student_grade`, etc. |
| API parity | Same helpers in `api/` routes |
| Evidence | pytest `test_security_rbac.py`; screenshot 403 page |

---

## A02 — Cryptographic Failures

| Control | Implementation |
|---------|----------------|
| Passwords | PBKDF2-SHA256 (600k iterations) |
| PII | Fernet via `FIELD_ENCRYPTION_KEY` |
| TOTP | Encrypted at rest |
| JWT | HS256, short access TTL, `RevokedToken` |
| Evidence | DB hash ≠ plaintext; `test_password_hash_not_plaintext` |

---

## A03 — Injection (incl. XSS)

| Control | Implementation |
|---------|----------------|
| SQL | ORM only; `filter_by` / parameterized |
| XSS | Bleach + no `\|safe` on user content |
| Evidence | SQLi login tests; XSS profile/grade tests |

---

## A05 — Security Misconfiguration

| Control | Implementation |
|---------|----------------|
| Headers | CSP, X-Frame-Options, nosniff, Referrer-Policy |
| CSRF | Global Flask-WTF |
| Cookies | HttpOnly, SameSite; Secure in production |
| Evidence | `curl -I`; ZAP header alerts |

---

## A07 — Identification & Authentication Failures

| Control | Implementation |
|---------|----------------|
| 2FA | TOTP + recovery codes |
| Rate limits | Login, 2FA, API login |
| Session | `2fa_verified` gate before dashboards |
| Inactive users | Rejected at login |
| Evidence | Rate limit 429; inactive user test |

---

## A09 — Security Logging & Monitoring

| Control | Implementation |
|---------|----------------|
| Audit log | `log_event`, severity, details redaction |
| Dashboard | `/admin/security-dashboard`, risk score |
| Actions | `LOGIN_FAILED`, `IDOR_ATTEMPT`, `FORBIDDEN_ROUTE`, etc. |
| Evidence | Audit UI screenshot; incident simulation |

---

## Detailed control reference

### SQL injection

ORM-only queries; pytest rejects `' OR '1'='1` login bypass.

### XSS

`sanitize_text()` on profile, feedback, descriptions; templates auto-escape.

### CSRF

POST without token → HTTP 400.

### Rate limiting

| Route | Limit |
|-------|-------|
| Login | 5 / minute |
| 2FA | 5 / minute |
| API login | 10 / minute |
| Enrollment | 20 / hour |

### HTTP headers

CSP, `X-Content-Type-Options`, `X-Frame-Options`, HSTS (production).

### Password policy

Min 10 chars; upper, lower, digit, special.

### Session

HttpOnly, SameSite, timeout via `PERMANENT_SESSION_LIFETIME`.

### Field encryption

Phone, address, emergency contact encrypted in DB.

---

## Evidence screenshots

| ID | Description |
|----|-------------|
| E01 | SQLi login failed |
| E02 | XSS escaped output |
| E03 | CSRF 400 |
| E04 | Rate limit 429 |
| E05 | Security headers |
| E06 | Password policy rejection |
| E07 | Session cookie flags |
| E08 | Encrypted DB column |
| E09 | RBAC 403 |

---

## Related documents

- [threat-model.md](threat-model.md)
- [testing-plan.md](testing-plan.md)
- [security-testing-results.md](security-testing-results.md)
