# Admin Security Dashboard

## Overview

The **Security Operations Center** (`/admin/security-dashboard`) provides administrators with a real-time view of authentication failures, access-control violations, and high-severity audit events. It aggregates data from the centralized `AuditLog` table populated by `app.services.audit_service.log_event()`.

Access is restricted to users with the **Admin** role via `@admin_required` (RBAC + completed 2FA).

Legacy URL `/admin/security` redirects to `/admin/security-dashboard`.

---

## Composite Risk Score (Distinction Feature)

A **0–100 risk score** summarizes the security posture over the **last 24 hours**:

| Signal | Weight per event |
|--------|------------------|
| Failed login (`LOGIN_FAILED`) | 2 |
| Failed 2FA (`TWO_FA_FAILED`) | 3 |
| Unauthorized access (`UNAUTHORIZED_ACCESS`, `FORBIDDEN_ROUTE`, `IDOR_ATTEMPT`) | 5 |
| Rate limit (`RATE_LIMIT_TRIGGERED`) | 2 |

**Formula:** `score = min(100, Σ weighted events)`

| Score | Level | UI indicator |
|-------|--------|--------------|
| 0–25 | Low | Green |
| 26–50 | Medium | Amber |
| 51–75 | High | Red |
| 76–100 | Critical | Red (emphasized) |

The score is informational and supports triage; it does not trigger automated blocking.

---

## Dashboard Sections

### 1. Security summary cards

| Card | Source |
|------|--------|
| Failed logins (24h) | `AuditLog` where `action` ∈ `LOGIN_FAILED`, `login_failure` |
| Failed 2FA (24h) | `TWO_FA_FAILED`, `2fa_verification_failed` |
| Unauthorized (24h) | `UNAUTHORIZED_ACCESS`, `FORBIDDEN_ROUTE`, `IDOR_ATTEMPT` |
| Rate limits (24h) | `RATE_LIMIT_TRIGGERED` |
| High severity (24h) | `severity` ∈ `CRITICAL`, `HIGH` |
| Active users | `User.is_active == True` |

### 2. Suspicious IP table

IPs with at least one security-related event in 24h, showing:

- Failed login count  
- Failed 2FA count  
- Unauthorized attempt count  
- Last seen timestamp  
- **Risk level** (per IP):

| IP risk | Criteria |
|---------|----------|
| **High** | ≥2 unauthorized, or ≥5 failed logins, or ≥10 total security events |
| **Medium** | ≥1 unauthorized, or ≥3 failed 2FA/logins, or ≥5 total events |
| **Low** | Any other tracked activity |

### 3. Recent high-risk events

Last 15 audit rows (48h window) where `severity` is `CRITICAL` or `HIGH`.  
`details` are parsed from JSON and **redacted** (passwords, tokens, secrets removed) before display.

### 4. Charts

| Chart | Data |
|-------|------|
| Failed login trend | Daily `LOGIN_FAILED` counts, 14 days |
| Events by severity | Count by `severity` column, 7 days |
| Top attacked routes | Paths/endpoints from `details.path` or `details.endpoint` on unauthorized, IDOR, and rate-limit events (24h) |

### 5. Incident response checklist

Embedded playbook linking to User management and Audit Logs for containment and documentation.

---

## Backend implementation

| Component | Path |
|-----------|------|
| Aggregations | `src/app/admin/security_services.py` |
| Route | `src/app/admin/routes/security.py` |
| Template | `src/app/templates/admin/security_dashboard.html` |

Queries use SQLAlchemy `func.sum(case(...))` for efficient per-IP breakdowns. No passwords, TOTP secrets, or tokens are read from user tables or audit `details`.

Viewing the dashboard logs `VIEW_SECURITY_DASHBOARD` (severity `INFO`) for accountability.

---

## Evidence & testing

1. Log in as admin and open `/admin/security-dashboard`.  
2. Trigger a failed login; confirm **Failed logins (24h)** and risk score update.  
3. Verify suspicious IP row appears for the client IP.  
4. Confirm charts render (Chart.js).  
5. Screenshot placeholders: risk score card, IP table, checklist, charts.

---

## Related documentation

- [security-controls.md](./security-controls.md) — OWASP controls and audit logging  
- Admin **Audit Logs** (`/admin/audit-logs`) — full searchable event history with export
