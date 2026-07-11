# Production Readiness — Security Summary (sanitised)

Part of `docs/design/PRODUCTION_READINESS_EVIDENCE_PASS.md` (Part A). Detailed findings
(exact ports, file paths, process internals) are written to the PRIVATE ops repo per the
staging doc's security boundary — `~/synthetic-enterprise-ops/production_readiness_security_findings.md`
— never this public repo. This file is counts/tiers/status only.

## Secrets

- **2 secret files found** on this machine (`background/.env.ntfy`, `background/.env.file-api`).
  Both: correctly gitignored (verified via `git check-ignore -v`, not assumed), 600-permissioned
  (owner-read/write only), and confirmed **never present in git history** (`git log --all
  --full-history` on each path returns empty). No raw values printed or stored anywhere by this
  audit.
- Repo-wide grep for secret-shaped literals (API key/token/secret/password patterns) across all
  tracked source, config, and doc files: **zero matches** outside the two files above.
- **Verdict: CLEAN. No exposed credential values found this pass.**

## Exposed network surface

- 1 authenticated service confirmed (the File API on port 8765, referenced in CLAUDE.md) —
  header-based auth checked against a 403 on mismatch, path-traversal guarded, one deliberately
  public `/health` endpoint that returns no sensitive data.
- **1 medium-tier finding:** 5 stale, unauthenticated ad-hoc dev file-servers found running,
  accumulated over ~2 days, never terminated, bound to all network interfaces. They serve only
  already-public site content (not a data leak), but represent unnecessary attack surface and a
  process-hygiene gap. Not fixed by this audit (read-mostly scope) — flagged for remediation.
- 1 low-tier finding: wide-open CORS policy on the authenticated File API (low risk given
  header-based, not cookie-based, auth) — worth narrowing.
- All other listening ports on this machine are either localhost-only or Tailscale-daemon-internal.

## Dependency vulnerabilities

- `pip-audit` is **not installed** on this machine — no automated CVE-matched scan was possible
  this pass. This is itself a gap worth closing.
- 150 Python packages installed; ~38 have newer versions available per `pip list --outdated`.
  Manual read of version numbers found nothing suggesting an unpatched critical CVE at current
  versions, but this is an inferred read, not a verified database match — treat as unaudited
  until `pip-audit` (or similar) is actually run.

## Sandbox / harness hardening

Already assessed in `docs/design/HARNESS_BEST_PRACTICE_ASSESSMENT.md` (Pattern-C recommendation)
— linked, not re-derived here per the staged doc's instruction to absorb it as an input.

## Remediation ownership

Per the staging doc's explicit carve-out, any remediation of the findings above (killing stale
servers, installing `pip-audit`, narrowing CORS) is NOT actioned by this read-mostly audit —
decision and action rest with the orchestrator/director.
