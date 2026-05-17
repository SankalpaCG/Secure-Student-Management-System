# Admin Guide

Security and management procedures for **Administrator** accounts.

---

## Responsibilities

- User lifecycle (create, deactivate, role assignment)
- Course and teacher assignment
- Review **audit logs** and **security dashboard**
- Respond to suspected incidents (see [incident-response.md](incident-response.md))

---

## User management

| Action | Path | Notes |
|--------|------|-------|
| List / filter users | `/admin/users` | Search, role, active status |
| Create user | **Create User** | Strong password required; student/teacher profile fields |
| View detail | User row → detail | Decrypted student PII shown to admin |
| Deactivate | User → **Deactivate** | Blocks login |
| Reset 2FA | User → **Reset 2FA** | User must set up 2FA again |
| Export | **Export CSV** | No password hashes included |

**Screenshot placeholder:** `admin-users.png`

---

## Course management

| Action | Path |
|--------|------|
| List courses | `/admin/courses` |
| Create | **Create Course** — code, name, **assigned teacher** |
| Edit | Course → **Edit** |

Assigning a teacher updates `Course.teacher_id` and is audited (`ASSIGN_TEACHER`).

---

## Security monitoring

### Audit logs (`/admin/audit-logs`)

- Filter by action, severity, user, date, search term.
- Export CSV for evidence packs.
- Key actions: `LOGIN_FAILED`, `TWO_FA_FAILED`, `FORBIDDEN_ROUTE`, `IDOR_ATTEMPT`, `RATE_LIMIT_TRIGGERED`.

### Security dashboard (`/admin/security-dashboard`)

- 24h counters: failed logins, 2FA failures, unauthorized access, rate limits.
- **Risk score** (weighted composite).
- Suspicious IP table and high-risk events.
- Incident response checklist (inline).

**Screenshot placeholders:** `admin-audit.png`, `admin-security-dashboard.png`

---

## Incident response (summary)

1. **Identify** source IP from audit logs or dashboard.
2. **Review** targeted accounts.
3. **Deactivate** account if needed (`/admin/users`).
4. **Reset 2FA** if TOTP compromise suspected.
5. **Export** audit CSV for records.
6. **Document** timeline and actions.

Full playbook: [incident-response.md](incident-response.md).  
Local simulation: `python src/simulate_incident.py --confirm` (localhost only).

---

## JWT / API administration

- Revoked tokens stored in `revoked_tokens` (populated on API logout).
- No UI for token list — use DB or future admin tool for forensics.
- API admin endpoints: `/api/admin/users`, `/api/admin/audit-logs`, `/api/admin/security-summary` (Bearer token required).

---

## Security checklist for new admins

- [ ] Change default seed password immediately
- [ ] Complete 2FA setup before storing real student data
- [ ] Set strong `SECRET_KEY` and `FIELD_ENCRYPTION_KEY` in production
- [ ] Use separate MySQL user with least privilege
- [ ] Review security dashboard weekly
- [ ] Never share recovery codes or export files over insecure channels

---

## Related documents

- [user-guide.md](user-guide.md)
- [security-dashboard.md](security-dashboard.md)
- [security-controls.md](security-controls.md)
- [devsecops-pipeline.md](devsecops-pipeline.md)
