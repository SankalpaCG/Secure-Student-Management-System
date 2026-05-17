# Testing Plan

Automated and manual testing strategy for assessment evidence. Tests use **pytest**; database via `TEST_DATABASE_URL` (MySQL) or SQLite fallback.

---

## 1. Functional tests

| Module | Scope | Pass criteria |
|--------|-------|---------------|
| `test_auth.py` | Login, logout, inactive user | Correct redirects / flash messages |
| `test_admin.py` | Dashboard, create user/course, audit logs | HTTP 200; data persisted |
| `test_teacher.py` | Courses scope, grades, attendance | Own course only; records saved |
| `test_student.py` | Profile, enroll, grades, attendance | Own data visible |
| `test_routes.py` | 403, 404 | Correct status codes |
| `test_api.py` | JWT auth, refresh, RBAC | JSON responses; 401/403 |

**Run:** `pytest tests/test_auth.py tests/test_admin.py … -v`

---

## 2. Security tests

| Module | OWASP focus | Key assertions |
|--------|-------------|----------------|
| `test_security_rbac.py` | A01 | 403 cross-role; IDOR grade |
| `test_security_input.py` | A01, A03, A07, A09 | CSRF 400; XSS sanitized; SQLi fails; audit rows |
| `test_security_jwt.py` | A01, A07 | Expired/revoked token; API forbidden |
| `test_security_rate_limit.py` | A07 | Login → 429 |
| `test_security.py` | Unit | Policy, encrypt, sanitize |

**Run:** `pytest tests/test_security_*.py -v`

---

## 3. Unit tests

| Module | Focus |
|--------|-------|
| `test_audit_service.py` | Audit writer, secret redaction |
| `test_security.py` | Crypto/sanitize helpers |

---

## 4. Performance tests (manual / future)

No automated load suite is bundled. For distinction evidence, optional manual checks:

| Scenario | Tool | Target |
|----------|------|--------|
| Login under 10 concurrent users | `locust` or `ab` | p95 &lt; 2s (local) |
| Audit log query (1000 rows) | MySQL EXPLAIN | Index use on `timestamp`, `action` |
| Dashboard load | Browser devtools | &lt; 3s on LAN |

Document results in your report if required by rubric.

---

## 5. Static / dependency scans

| Tool | Script | CI job |
|------|--------|--------|
| Bandit | `ci-cd/run_bandit.sh` | `sast` |
| pip-audit | `ci-cd/run_dependency_scan.sh` | `dependency-scan` |
| OWASP ZAP | `ci-cd/run_zap_baseline.sh` | `dast` (placeholder) |

See [security-testing-results.md](security-testing-results.md).

---

## Environment

```bash
export TEST_DATABASE_URL='mysql+pymysql://user:pass@localhost:3306/secure_student_test?charset=utf8mb4'
pytest --cov=app --cov-report=html
```

---

## Expected results summary

| Category | Failure means |
|----------|----------------|
| Functional | Regression in role workflow |
| Security RBAC | Access control bypass |
| Security input | CSRF/XSS/SQLi weakness |
| JWT | Token or API authorization flaw |
| Bandit High+ | Serious code pattern |
| pip-audit | Known CVE in dependencies |

---

## Evidence placeholders

| # | Capture |
|---|---------|
| 1 | Full `pytest` green |
| 2 | Coverage HTML summary |
| 3 | `test_security_rbac` output |
| 4 | CI Actions test job |

---

## Related documents

- [devsecops-pipeline.md](devsecops-pipeline.md)
- [security-testing-results.md](security-testing-results.md)
- [README.md](../README.md)
