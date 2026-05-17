# Security Testing Results

Summary of automated security tooling. Reports: [`security-reports/`](../security-reports/).

---

## Tool purposes

| Tool | Purpose |
|------|---------|
| **Bandit** | SAST — Python security anti-patterns |
| **pip-audit** | Dependency CVE scan |
| **OWASP ZAP** | DAST — running web app (headers, cookies, crawl) |

---

## Commands

```bash
./ci-cd/run_bandit.sh
./ci-cd/run_dependency_scan.sh
./ci-cd/run_zap_baseline.sh    # app running; Docker required
```

---

## Findings (representative run)

| Tool | High | Medium | Low | Notes |
|------|------|--------|-----|-------|
| Bandit | 0 | 0 | 4 | B105 false positives (`Bearer`, seed password) |
| pip-audit | — | — | — | No known CVEs |
| ZAP | _Run locally_ | | | See placeholder in CI |

### Remediation

| Finding | Action | Status |
|---------|--------|--------|
| B105 `Bearer` | Document false positive | Accepted |
| B105 seed password | Dev-only; document in README | Accepted |
| CVEs | Upgrade package when reported | None at scan |

---

## OWASP mapping (tooling)

| OWASP | Tool coverage |
|-------|----------------|
| A03 | Bandit, ZAP, pytest XSS/SQLi |
| A06 | pip-audit |
| A05 | ZAP headers |
| A01, A07 | pytest security, ZAP auth (manual) |
| A09 | pytest audit tests |

---

## Screenshot placeholders

| # | Description |
|---|-------------|
| 1 | `bandit-report.html` in browser |
| 2 | pip-audit terminal output |
| 3 | `zap-baseline-report.html` summary |
| 4 | CI `sast` + `dependency-scan` jobs green |

---

## Related documents

- [devsecops-pipeline.md](devsecops-pipeline.md)
- [testing-plan.md](testing-plan.md)
- [security-controls.md](security-controls.md)
