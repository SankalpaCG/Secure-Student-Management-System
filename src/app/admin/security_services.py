"""Security dashboard aggregations from audit logs."""

import json
from datetime import datetime, timedelta

from sqlalchemy import case, func
from sqlalchemy.orm import joinedload

from app.extensions import db
from app.models.audit_log import AuditLog
from app.models.user import User

# Action groups (include legacy names for historical rows).
LOGIN_FAILED = ("LOGIN_FAILED", "login_failure")
TWO_FA_FAILED = ("TWO_FA_FAILED", "2fa_verification_failed")
UNAUTHORIZED = (
    "UNAUTHORIZED_ACCESS",
    "unauthorized_access",
    "FORBIDDEN_ROUTE",
    "IDOR_ATTEMPT",
)
RATE_LIMIT = ("RATE_LIMIT_TRIGGERED",)
SECURITY_ACTIONS = LOGIN_FAILED + TWO_FA_FAILED + UNAUTHORIZED + RATE_LIMIT


def _cutoff(hours=24):
    return datetime.utcnow() - timedelta(hours=hours)


def _count_since(actions, since):
    return AuditLog.query.filter(
        AuditLog.action.in_(actions),
        AuditLog.timestamp >= since,
    ).count()


def _calculate_risk_score(failed_logins, failed_2fa, unauthorized, rate_limits):
    """
    Distinction-level composite risk score (0–100) from 24h security signals.
    Weights reflect relative severity of each event type.
    """
    raw = (
        failed_logins * 2
        + failed_2fa * 3
        + unauthorized * 5
        + rate_limits * 2
    )
    score = min(100, int(raw))
    if score >= 76:
        level = "Critical"
        variant = "danger"
    elif score >= 51:
        level = "High"
        variant = "danger"
    elif score >= 26:
        level = "Medium"
        variant = "warning"
    else:
        level = "Low"
        variant = "success"
    return {"score": score, "level": level, "variant": variant}


def _ip_risk_level(failed_login, failed_2fa, unauthorized, total):
    if unauthorized >= 2 or failed_login >= 5 or total >= 10:
        return "High"
    if unauthorized >= 1 or failed_2fa >= 3 or failed_login >= 3 or total >= 5:
        return "Medium"
    if total > 0:
        return "Low"
    return "Low"


def _suspicious_ips(cutoff):
    rows = (
        db.session.query(
            AuditLog.ip_address,
            func.sum(case((AuditLog.action.in_(LOGIN_FAILED), 1), else_=0)).label(
                "failed_login"
            ),
            func.sum(case((AuditLog.action.in_(TWO_FA_FAILED), 1), else_=0)).label(
                "failed_2fa"
            ),
            func.sum(case((AuditLog.action.in_(UNAUTHORIZED), 1), else_=0)).label(
                "unauthorized"
            ),
            func.count(AuditLog.id).label("total"),
            func.max(AuditLog.timestamp).label("last_seen"),
        )
        .filter(
            AuditLog.timestamp >= cutoff,
            AuditLog.ip_address.isnot(None),
            AuditLog.action.in_(SECURITY_ACTIONS),
        )
        .group_by(AuditLog.ip_address)
        .having(func.count(AuditLog.id) >= 1)
        .order_by(func.count(AuditLog.id).desc())
        .limit(20)
        .all()
    )
    result = []
    for row in rows:
        fl = int(row.failed_login or 0)
        f2 = int(row.failed_2fa or 0)
        ua = int(row.unauthorized or 0)
        total = int(row.total or 0)
        result.append({
            "ip_address": row.ip_address,
            "failed_login": fl,
            "failed_2fa": f2,
            "unauthorized": ua,
            "last_seen": row.last_seen,
            "risk_level": _ip_risk_level(fl, f2, ua, total),
        })
    return result


def _recent_high_risk_events(limit=15):
    logs = (
        AuditLog.query.options(joinedload(AuditLog.user))
        .filter(
            AuditLog.severity.in_(["CRITICAL", "HIGH"]),
            AuditLog.timestamp >= _cutoff(48),
        )
        .order_by(AuditLog.timestamp.desc())
        .limit(limit)
        .all()
    )
    events = []
    for log in logs:
        details_display = _safe_details_preview(log.details)
        events.append({
            "timestamp": log.timestamp,
            "user": log.user.full_name if log.user else "System",
            "user_email": log.user.email if log.user else "",
            "action": log.action,
            "ip": log.ip_address or "—",
            "severity": log.severity,
            "details": details_display,
        })
    return events


def _safe_details_preview(details_raw, max_len=120):
    """Return a redacted, truncated details string for UI display."""
    if not details_raw:
        return "—"
    try:
        data = json.loads(details_raw)
        if isinstance(data, dict):
            safe = {
                k: v
                for k, v in data.items()
                if k.lower() not in ("password", "token", "secret", "totp")
            }
            text = json.dumps(safe, separators=(",", ":"))
        else:
            text = str(details_raw)
    except (json.JSONDecodeError, TypeError):
        text = str(details_raw)
    if len(text) > max_len:
        return text[: max_len - 3] + "..."
    return text


def _login_failure_trend(days=14):
    results = []
    for i in range(days - 1, -1, -1):
        day = datetime.utcnow().date() - timedelta(days=i)
        start = datetime.combine(day, datetime.min.time())
        end = start + timedelta(days=1)
        count = AuditLog.query.filter(
            AuditLog.action.in_(LOGIN_FAILED),
            AuditLog.timestamp >= start,
            AuditLog.timestamp < end,
        ).count()
        results.append({"label": day.strftime("%m/%d"), "count": count})
    return results


def _events_by_severity(cutoff):
    rows = (
        db.session.query(AuditLog.severity, func.count(AuditLog.id))
        .filter(AuditLog.timestamp >= cutoff)
        .group_by(AuditLog.severity)
        .all()
    )
    order = ["CRITICAL", "HIGH", "MEDIUM", "LOW", "INFO"]
    counts = {sev: cnt for sev, cnt in rows}
    return {
        "labels": [s for s in order if counts.get(s, 0) > 0],
        "values": [counts.get(s, 0) for s in order if counts.get(s, 0) > 0],
        "colors": {
            "CRITICAL": "#dc2626",
            "HIGH": "#f59e0b",
            "MEDIUM": "#2563eb",
            "LOW": "#64748b",
            "INFO": "#16a34a",
        },
    }


def _top_attacked_endpoints(cutoff, limit=8):
    """Aggregate path/endpoint from audit details (no secrets exposed)."""
    logs = (
        AuditLog.query.filter(
            AuditLog.timestamp >= cutoff,
            AuditLog.action.in_(UNAUTHORIZED + RATE_LIMIT + ("IDOR_ATTEMPT",)),
        )
        .with_entities(AuditLog.details, AuditLog.action, AuditLog.target_type)
        .all()
    )
    counts = {}
    for details, action, target_type in logs:
        label = None
        if details:
            try:
                data = json.loads(details)
                if isinstance(data, dict):
                    label = data.get("path") or data.get("endpoint")
            except (json.JSONDecodeError, TypeError):
                pass
        if not label:
            label = target_type or action
        counts[label] = counts.get(label, 0) + 1
    sorted_items = sorted(counts.items(), key=lambda x: x[1], reverse=True)[:limit]
    return {"labels": [k for k, _ in sorted_items], "values": [v for _, v in sorted_items]}


def get_security_dashboard_data():
    """Build all context for the admin security dashboard."""
    cutoff_24h = _cutoff(24)
    cutoff_7d = _cutoff(24 * 7)

    failed_logins_24h = _count_since(LOGIN_FAILED, cutoff_24h)
    failed_2fa_24h = _count_since(TWO_FA_FAILED, cutoff_24h)
    unauthorized_24h = _count_since(UNAUTHORIZED, cutoff_24h)
    rate_limit_24h = _count_since(RATE_LIMIT, cutoff_24h)
    high_severity_24h = AuditLog.query.filter(
        AuditLog.timestamp >= cutoff_24h,
        AuditLog.severity.in_(["CRITICAL", "HIGH"]),
    ).count()

    active_users = User.query.filter_by(is_active=True).count()
    risk = _calculate_risk_score(
        failed_logins_24h, failed_2fa_24h, unauthorized_24h, rate_limit_24h
    )

    return {
        "failed_logins_24h": failed_logins_24h,
        "failed_2fa_24h": failed_2fa_24h,
        "unauthorized_24h": unauthorized_24h,
        "rate_limit_24h": rate_limit_24h,
        "high_severity_24h": high_severity_24h,
        "active_users": active_users,
        "risk_score": risk,
        "suspicious_ips": _suspicious_ips(cutoff_24h),
        "recent_high_risk": _recent_high_risk_events(),
        "login_trend": _login_failure_trend(14),
        "severity_chart": _events_by_severity(cutoff_7d),
        "endpoint_chart": _top_attacked_endpoints(cutoff_24h),
        "generated_at": datetime.utcnow(),
    }
