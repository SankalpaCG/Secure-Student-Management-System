# Incident Response Playbook

Detection and response for security events using audit logs and the Admin Security Dashboard. Supports local simulation via `src/simulate_incident.py` (**localhost only**).

---

## Scenario

Simulated **credential and access-abuse** incident (assessment):

| Phase | Attacker action | Control tested |
|-------|-----------------|----------------|
| 1 | Failed password attempts | `LOGIN_FAILED`, login rate limit |
| 2 | Valid password, wrong TOTP | `TWO_FA_FAILED` |
| 3 | Student accesses `/admin/*` | `FORBIDDEN_ROUTE` |
| 4 | Student opens another's grade URL | `IDOR_ATTEMPT` |
| 5 | API login flood | `API_LOGIN_FAILED`, `RATE_LIMIT_TRIGGERED` |

No destructive actions (no deletes, password changes, or data wipes).

### Run simulation

```bash
cd src && python run.py
python simulate_incident.py --base-url http://127.0.0.1:5000 --confirm
# For steps 3–4: enable 2FA on test student; export SIM_STUDENT_TOTP=<code>
```

---

## Detection

| Source | What to check |
|--------|----------------|
| **Security Dashboard** | Risk score, failed login/2FA counters, suspicious IPs |
| **Audit Logs** | Filter `LOGIN_FAILED`, `IDOR_ATTEMPT`, `FORBIDDEN_ROUTE` |
| **HTTP 429** | Rate limit triggered (logged) |

Admin path: `/admin/security-dashboard`, `/admin/audit-logs`.

---

## Audit evidence

| Action | Severity (typical) |
|--------|-------------------|
| `LOGIN_FAILED` | HIGH |
| `TWO_FA_FAILED` | HIGH |
| `FORBIDDEN_ROUTE` | HIGH |
| `IDOR_ATTEMPT` | CRITICAL |
| `RATE_LIMIT_TRIGGERED` | HIGH |

Export CSV from audit logs for your report appendix.

---

## Response steps

1. **Identify source IP** — audit log / suspicious IP table.
2. **Review targeted account** — `details.email` or user_id on events.
3. **Deactivate account** if needed — Admin → Users → Deactivate.
4. **Reset 2FA** if TOTP compromise — Admin → Users → Reset 2FA.
5. **Review full audit trail** — export and correlate timestamps with simulation.
6. **Document** actions taken and residual risk.

---

## Dashboard evidence

| Widget | Expected after simulation |
|--------|---------------------------|
| Failed logins (24h) | Increased |
| Failed 2FA (24h) | Increased (if 2FA enabled) |
| Unauthorized (24h) | Increased |
| Risk score | Elevated |
| High-risk events | New rows |

---

## Lessons learned

- Layered controls (password + 2FA + RBAC + rate limits + audit) detect different attack types.
- Fail-closed design returns 403 without exposing data.
- Centralized logging supports coursework evidence and real incident triage.

---

## Screenshot placeholders

| # | Description |
|---|-------------|
| 1 | Audit log filtered by `LOGIN_FAILED` |
| 2 | `IDOR_ATTEMPT` row detail |
| 3 | Security dashboard risk score |
| 4 | Suspicious IP table |

---

## Related documents

- [admin-guide.md](admin-guide.md)
- [security-dashboard.md](security-dashboard.md)
- [threat-model.md](threat-model.md)
