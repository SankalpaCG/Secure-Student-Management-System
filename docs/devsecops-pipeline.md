# DevSecOps Pipeline

Workflow: [`.github/workflows/devsecops.yml`](../.github/workflows/devsecops.yml)

**Flow:** Build → SAST → Test → Dependency Scan → DAST → Deploy

---

## Diagram

```
Trigger (push / PR / manual)
         │
         ▼
    ┌─────────┐
    │  BUILD  │  compileall, create_app()
    └────┬────┘
         ├──────────────┬──────────────┐
         ▼              ▼              ▼
    ┌─────────┐   ┌─────────┐   ┌──────────────┐
    │  SAST   │   │  TEST   │   │ DEP SCAN     │
    │ Bandit  │   │ pytest  │   │ pip-audit    │
    └────┬────┘   └────┬────┘   └──────┬───────┘
         │              │              │
         └──────────────┼──────────────┘
                        ▼
                 ┌─────────────┐
                 │ DAST (stub) │
                 └──────┬──────┘
                        ▼
                 ┌─────────────┐
                 │ DEPLOY stub │
                 └─────────────┘
```

---

## Stages

| # | Job | Security value | Fails build? |
|---|-----|----------------|--------------|
| 1–5 | `build` | Catches broken deploys early | Yes |
| 6–8 | `sast` | Python vulnerability patterns | Yes (High+) |
| 6–7 | `test` | Regressions in auth/RBAC/API | Yes |
| 9 | `dependency-scan` | Known CVEs in deps | Yes |
| 10 | `secret-scan` | Leaked credentials in git | No (placeholder) |
| 11 | `dast` | Runtime web flaws | No (placeholder) |
| 12 | `deploy` | Gated release | N/A |

---

## Secrets (GitHub)

| Secret | Purpose |
|--------|---------|
| `SECRET_KEY` | Required — Flask sessions |
| `JWT_SECRET_KEY` | JWT signing |
| `FIELD_ENCRYPTION_KEY` | PII encryption |
| `MYSQL_ROOT_PASSWORD` | CI MySQL service |
| `TEST_DATABASE_URL` | Optional pytest URI |
| `DATABASE_URL` | Deploy placeholder only |

Never commit credentials in the workflow YAML.

---

## Failure handling

| Failure | Action |
|---------|--------|
| Bandit High+ | Fix code or document `# nosec` with justification |
| pip-audit CVE | Upgrade dependency |
| pytest red | Fix test or bug |
| Missing secret | Add in repo Settings → Secrets |

Re-run from Actions tab after fix.

---

## Artifacts

`bandit-reports`, `pip-audit-report`, `coverage-report`, `secret-scan-reports`, `dast-placeholder` (14–30 day retention).

---

## Local parity

```bash
pytest
./ci-cd/run_bandit.sh
./ci-cd/run_dependency_scan.sh
```

---

## Screenshot placeholders

| # | Capture |
|---|---------|
| 1 | Actions workflow all green |
| 2 | `sast` job log |
| 3 | `dependency-scan` job |
| 4 | Downloaded Bandit artifact |

---

## Related documents

- [testing-plan.md](testing-plan.md)
- [security-testing-results.md](security-testing-results.md)
- [README.md](../README.md)
