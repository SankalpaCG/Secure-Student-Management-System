#!/usr/bin/env python3
"""
Safe local-only security incident simulation for assessment evidence.

ONLY run against a development server on localhost / 127.0.0.1.
Never use against production, staging, or external hosts.

Usage (from src/ with Flask app running):
    python simulate_incident.py --base-url http://127.0.0.1:5000 --confirm

Optional environment variables:
    SIM_TARGET_EMAIL      Account for failed-login attempts (default: emma.johnson@school.edu)
    SIM_STUDENT_EMAIL     Student for 2FA / IDOR / admin tests (default: emma.johnson@school.edu)
    SIM_STUDENT_PASSWORD  Student password (default: ChangeMe123!)
    SIM_STUDENT_TOTP      Current 6-digit TOTP (required for admin + IDOR web tests)
    SIM_OTHER_GRADE_ID    Another student's grade primary key (default: 3)
"""

from __future__ import annotations

import argparse
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from http.cookiejar import CookieJar

# ---------------------------------------------------------------------------
# Safety: local targets only
# ---------------------------------------------------------------------------

_ALLOWED_HOSTS = frozenset({"localhost", "127.0.0.1", "::1"})

ETHICAL_WARNING = """
================================================================================
  ETHICAL USE — LOCAL DEVELOPMENT ONLY
================================================================================
  This script generates intentional security events for coursework evidence.
  It must ONLY be run against YOUR OWN local Flask dev server.

  - Targets: localhost / 127.0.0.1 only
  - No destructive actions (no deletes, no password changes, no data wipes)
  - No external systems or third-party URLs

  By passing --confirm you accept responsibility for local-only use.
================================================================================
"""

EXPECTED_AUDIT_EVENTS = [
    ("LOGIN_FAILED", "Failed login attack (wrong passwords)"),
    ("TWO_FA_FAILED", "Failed 2FA (wrong TOTP after valid password)"),
    ("FORBIDDEN_ROUTE", "Student attempted admin-only web route"),
    ("IDOR_ATTEMPT", "Student attempted another student's grade"),
    ("API_LOGIN_FAILED", "Repeated invalid API login attempts"),
    ("RATE_LIMIT_TRIGGERED", "API login rate limit exceeded (may follow API abuse)"),
]

SCREENSHOT_CHECKLIST = [
    "Admin → Audit Logs filtered by LOGIN_FAILED (last 15 minutes)",
    "Admin → Audit Logs filtered by TWO_FA_FAILED",
    "Admin → Audit Logs filtered by FORBIDDEN_ROUTE or IDOR_ATTEMPT",
    "Admin → Audit Logs filtered by RATE_LIMIT_TRIGGERED / API_LOGIN_FAILED",
    "Admin → Security Dashboard (/admin/security-dashboard) — summary cards",
    "Security Dashboard — Suspicious IP table (your machine's IP)",
    "Security Dashboard — Recent high-risk events table",
    "Security Dashboard — Risk Score card and charts",
]


def _assert_local_base_url(base_url: str) -> str:
    parsed = urllib.parse.urlparse(base_url.strip())
    if parsed.scheme not in ("http", "https"):
        sys.exit("Error: base URL must use http or https.")
    if not parsed.hostname:
        sys.exit("Error: base URL must include a hostname.")
    if parsed.hostname not in _ALLOWED_HOSTS:
        sys.exit(
            f"Error: refusing to run against non-local host '{parsed.hostname}'.\n"
            "Allowed hosts: localhost, 127.0.0.1, ::1"
        )
    netloc = parsed.hostname
    if parsed.port:
        netloc = f"{parsed.hostname}:{parsed.port}"
    path = parsed.path.rstrip("/")
    return f"{parsed.scheme}://{netloc}{path}"


def _extract_csrf(html: str) -> str | None:
    match = re.search(r'name="csrf_token"\s+value="([^"]+)"', html, re.I)
    return match.group(1) if match else None


class LocalSession:
    """Minimal HTTP client with cookie jar for form posts."""

    def __init__(self, base_url: str, timeout: float = 15.0):
        self.base_url = base_url
        self.timeout = timeout
        self._jar = CookieJar()
        self._opener = urllib.request.build_opener(
            urllib.request.HTTPCookieProcessor(self._jar)
        )

    def get(self, path: str) -> tuple[int, str, dict]:
        url = f"{self.base_url}{path}"
        req = urllib.request.Request(url, method="GET")
        try:
            with self._opener.open(req, timeout=self.timeout) as resp:
                body = resp.read().decode("utf-8", errors="replace")
                return resp.status, body, dict(resp.headers)
        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")
            return exc.code, body, dict(exc.headers)

    def post_form(self, path: str, fields: dict) -> tuple[int, str, dict]:
        url = f"{self.base_url}{path}"
        data = urllib.parse.urlencode(fields).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=data,
            method="POST",
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        try:
            with self._opener.open(req, timeout=self.timeout) as resp:
                body = resp.read().decode("utf-8", errors="replace")
                return resp.status, body, dict(resp.headers)
        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")
            return exc.code, body, dict(exc.headers)

    def post_json(self, path: str, payload: dict) -> tuple[int, str, dict]:
        import json

        url = f"{self.base_url}{path}"
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=data,
            method="POST",
            headers={"Content-Type": "application/json"},
        )
        try:
            with self._opener.open(req, timeout=self.timeout) as resp:
                body = resp.read().decode("utf-8", errors="replace")
                return resp.status, body, dict(resp.headers)
        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")
            return exc.code, body, dict(exc.headers)


def _log(step: str, detail: str) -> None:
    print(f"  [{step}] {detail}")


def simulate_failed_logins(client: LocalSession, email: str, count: int = 6) -> None:
    print("\n1. Failed login attack")
    for i in range(1, count + 1):
        status, html, _ = client.get("/login")
        csrf = _extract_csrf(html)
        if not csrf:
            _log("WARN", f"Attempt {i}: could not read CSRF token (HTTP {status})")
            continue
        status, _, _ = client.post_form(
            "/login",
            {
                "email": email,
                "password": f"WrongPassword!{i}",
                "remember_me": "y",
                "csrf_token": csrf,
                "submit": "Sign In",
            },
        )
        _log("POST /login", f"attempt {i} → HTTP {status}")
        time.sleep(0.3)


def simulate_failed_2fa(
    client: LocalSession, email: str, password: str, count: int = 4
) -> None:
    print("\n2. Failed 2FA attempts")
    status, html, _ = client.get("/login")
    csrf = _extract_csrf(html)
    if not csrf:
        _log("SKIP", "Could not load login page.")
        return

    status, body, _ = client.post_form(
        "/login",
        {
            "email": email,
            "password": password,
            "remember_me": "n",
            "csrf_token": csrf,
            "submit": "Sign In",
        },
    )
    if "/verify-2fa" not in body and status not in (200, 302):
        _log(
            "SKIP",
            "Account did not reach /verify-2fa (2FA may not be enabled). "
            "Enable 2FA for this student via the web UI, then re-run.",
        )
        return

    for i in range(1, count + 1):
        status, html, _ = client.get("/verify-2fa")
        csrf = _extract_csrf(html)
        if not csrf:
            _log("WARN", f"Attempt {i}: no CSRF on verify-2fa (HTTP {status})")
            continue
        status, _, _ = client.post_form(
            "/verify-2fa",
            {
                "token": f"{100000 + i:06d}"[-6:],
                "recovery_code": "",
                "csrf_token": csrf,
                "submit": "Verify",
            },
        )
        _log("POST /verify-2fa", f"wrong TOTP {i} → HTTP {status}")
        time.sleep(0.3)


def _student_session(
    client: LocalSession, email: str, password: str, totp: str
) -> bool:
    status, html, _ = client.get("/login")
    csrf = _extract_csrf(html)
    if not csrf:
        return False
    status, body, _ = client.post_form(
        "/login",
        {
            "email": email,
            "password": password,
            "remember_me": "n",
            "csrf_token": csrf,
            "submit": "Sign In",
        },
    )
    if "/verify-2fa" in body or status in (200, 302):
        status, html, _ = client.get("/verify-2fa")
        csrf = _extract_csrf(html)
        if not csrf:
            return False
        status, body, _ = client.post_form(
            "/verify-2fa",
            {
                "token": totp.strip(),
                "recovery_code": "",
                "csrf_token": csrf,
                "submit": "Verify",
            },
        )
    return status in (200, 302) and "dashboard" in body.lower() or status in (200, 302)


def simulate_unauthorized_admin(
    client: LocalSession, email: str, password: str, totp: str | None
) -> None:
    print("\n3. Unauthorized access (student → admin route)")
    if not totp:
        _log(
            "SKIP",
            "Set SIM_STUDENT_TOTP to a valid code for a 2FA-enabled student, "
            "or pass --student-totp.",
        )
        return

    session = LocalSession(client.base_url)
    if not _student_session(session, email, password, totp):
        _log("SKIP", "Could not complete student login with provided TOTP.")
        return

    for path in ("/admin/users", "/admin/dashboard", "/admin/audit-logs"):
        status, _, _ = session.get(path)
        _log("GET", f"{path} → HTTP {status}")
        time.sleep(0.2)


def simulate_idor_grade(
    client: LocalSession,
    email: str,
    password: str,
    totp: str | None,
    other_grade_id: int,
) -> None:
    print("\n4. IDOR attempt (student → another student's grade)")
    if not totp:
        _log("SKIP", "Requires SIM_STUDENT_TOTP / --student-totp.")
        return

    session = LocalSession(client.base_url)
    if not _student_session(session, email, password, totp):
        _log("SKIP", "Could not complete student login.")
        return

    path = f"/student/grades/{other_grade_id}"
    status, _, _ = session.get(path)
    _log("GET", f"{path} → HTTP {status} (expect 403 if grade belongs to another student)")


def simulate_api_abuse(client: LocalSession, email: str, attempts: int = 12) -> None:
    print("\n5. API abuse (repeated failed API logins → rate limit)")
    for i in range(1, attempts + 1):
        status, body, headers = client.post_json(
            "/api/auth/login",
            {"email": email, "password": f"bad-api-password-{i}"},
        )
        code = ""
        if "rate_limit" in body.lower() or status == 429:
            code = " [RATE LIMITED]"
        _log("POST /api/auth/login", f"attempt {i} → HTTP {status}{code}")
        if status == 429:
            break
        time.sleep(0.15)


def print_post_run_report() -> None:
    print("\n" + "=" * 72)
    print("  EXPECTED AUDIT LOG EVENTS (Admin → Audit Logs)")
    print("=" * 72)
    for action, description in EXPECTED_AUDIT_EVENTS:
        print(f"  • {action:<28} {description}")
    print(
        "\n  Note: Timestamps are UTC. Filter by severity HIGH/CRITICAL for a quick review."
    )

    print("\n" + "=" * 72)
    print("  SCREENSHOTS FOR ASSESSMENT REPORT")
    print("=" * 72)
    for i, item in enumerate(SCREENSHOT_CHECKLIST, 1):
        print(f"  {i}. {item}")
    print("\n  See docs/incident-response.md for detection and response narrative.\n")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate safe local security events for assessment evidence."
    )
    parser.add_argument(
        "--base-url",
        default=os.environ.get("SIM_BASE_URL", "http://127.0.0.1:5000"),
        help="Local Flask base URL (default: http://127.0.0.1:5000)",
    )
    parser.add_argument(
        "--confirm",
        action="store_true",
        help="Required: acknowledge local-only ethical use",
    )
    parser.add_argument(
        "--target-email",
        default=os.environ.get("SIM_TARGET_EMAIL", "emma.johnson@school.edu"),
        help="Email used for failed login / API abuse",
    )
    parser.add_argument(
        "--student-email",
        default=os.environ.get("SIM_STUDENT_EMAIL", "emma.johnson@school.edu"),
    )
    parser.add_argument(
        "--student-password",
        default=os.environ.get("SIM_STUDENT_PASSWORD", "ChangeMe123!"),
    )
    parser.add_argument(
        "--student-totp",
        default=os.environ.get("SIM_STUDENT_TOTP"),
        help="6-digit TOTP for student (required for steps 3–4)",
    )
    parser.add_argument(
        "--other-grade-id",
        type=int,
        default=int(os.environ.get("SIM_OTHER_GRADE_ID", "3")),
        help="Grade ID belonging to another student (seed default: 3)",
    )
    args = parser.parse_args()

    print(ETHICAL_WARNING)
    if not args.confirm:
        print("Re-run with --confirm to execute the simulation.\n")
        return 1

    base_url = _assert_local_base_url(args.base_url)
    print(f"\nTarget: {base_url}")
    print("Checking server reachability…")
    client = LocalSession(base_url)
    try:
        status, _, _ = client.get("/login")
        if status >= 500:
            sys.exit(f"Error: server returned HTTP {status}. Start Flask first.")
    except urllib.error.URLError as exc:
        sys.exit(
            f"Error: cannot reach {base_url} — start the app with:\n"
            f"  cd src && FLASK_APP=run.py flask run\n"
            f"  ({exc})"
        )

    print("\nStarting simulation (non-destructive)…\n")

    simulate_failed_logins(client, args.target_email)
    simulate_failed_2fa(client, args.student_email, args.student_password)
    simulate_unauthorized_admin(
        client, args.student_email, args.student_password, args.student_totp
    )
    simulate_idor_grade(
        client,
        args.student_email,
        args.student_password,
        args.student_totp,
        args.other_grade_id,
    )
    simulate_api_abuse(client, args.target_email)

    print_post_run_report()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
