# H4 — Go-Live NFR Register

**Atom:** `H4_go_live_nfr_register` (epoch 5, `docs/design/maturity_map.yaml`). Registered
2026-07-11 (PRODUCTION_READINESS_BASELINE.md, P2). This register is populated now (per the atom's
own registration text: "the register itself starts being populated now", consumed at Epoch 5) using
`H3_production_readiness_nfr_evidence`'s real, measured Part A findings — H3 reached L1 on
2026-07-11/12 with real findings across all four sub-areas, satisfying this register's own stated
dependency ("Depends on H3's Part A evidence existing before entries can carry a real 'current
measured state' column").

One row per category. **Go-live tier** is blocker / should-have / post-live, per this atom's own
schema. **Measured state** is quoted directly from H3's real findings (R9: measure, don't assert) —
where H3 did not measure a sub-area, that is stated as an open gap, not filled by assumption.

| Category | Current measured state (from H3 Part A) | Go-live tier | Landing epoch |
|---|---|---|---|
| **Availability / SLOs** | Whole stack is single-machine by design, no redundancy. 6 daemons share a single NTFY-env-var SPOF (confirmed this session — the exact class that caused the recurring `process_run_complete.py` failures, since fixed for `background-worker` specifically). Real crash history: 2 crash-loop episodes + one ~22min nvm-path outage in the last week (session-watchdog-log.md). No formal SLO/availability target has ever been set for this project (a simulation, not a live service — but Epoch 5 go-live would need one). | Blocker | Epoch 5 |
| **Latency budgets** | Not separately measured by H3 — full-run wall time (~470-510s for the 2016-2025 replay) is a throughput/capacity figure, not a request-latency budget. No live customer-facing request-latency SLO exists (site/ is static/JSON-fetch, no measured p50/p95). | Should-have | Epoch 5 |
| **Security (authn/authz/secrets/pen test)** | 2/2 secret files confirmed gitignored, 600-permissioned, never in git history; zero raw secret-shaped strings found elsewhere. 1 medium finding: 5 stale unauthenticated dev file-servers running ~2 days (not a data leak). 1 low finding: wide-open CORS on an otherwise-authenticated endpoint. `pip-audit` not installed — no automated CVE/dependency-vulnerability scan has ever run. No penetration test has been performed (this is a simulation with no real customer data, but Epoch 5 go-live framing would need one against the actual production surface). | Blocker (dependency-scan gap + no pen test); should-have (the 2 low/medium findings, real but not exploitable) | Epoch 5 |
| **Data protection (GDPR / encryption / backups)** | All customer records are synthetic (simulation-generated), so no live GDPR exposure exists TODAY — but no privacy-policy page exists on the public site at all (coldwalk:no_privacy_policy_page, adjudicated-real, registered backlog) — a real gap that would need closing before this project could ever be perceived as handling real customer data. Backups: `company/data/*.db` (4 SQLite files, the company's own operational state) and both `.env.*` secret files were previously gitignored with NO upstream copy — ACTED ON already (background/backup_company_data.py now backs up all 4 DB files to the private ops repo every cycle, verified via md5sum match). No encryption-at-rest has been assessed for any of these files. | Blocker (no privacy policy, no encryption-at-rest assessment); backup gap already closed | Epoch 5 |
| **Operational resilience** | Real crash history exists and is logged (session-watchdog-log.md); the NTFY-env-var SPOF above is the concrete operational-resilience finding this session's own infra fix directly addressed for one of the 6 sharing daemons — the other 5 were already correctly configured, only `background-worker` had the gap. No formal incident-response runbook exists; recovery today is ad hoc (an interactive session running the recovery checklist embedded in the session-watchdog's own wake prompt). | Should-have | Epoch 5 |
| **Capacity / scaling** | Confirmed 19 customers / ~470-510s run / ~2.9-3.8MB output matches CLAUDE.md's established figure. Two real O(n^2) patterns found by direct code read in simulation/run_phase2b.py (per-customer full linear scans of all_records) — code-verified (not load-tested) at ~100x cost at 10x population, ~10,000x at 100x population. docs/observability/risk-committee-log.md found unbounded, already at 277MB. This is the single most concrete, quantified, actionable capacity risk in the whole register — a real scaling cliff already identified, not hypothetical. | Blocker (the two O(n^2) patterns, at any population scale beyond the current 19-31 customer cast); should-have (the unbounded log file) | Epoch 5 (matches W2_2_population_draw's own real-population-scale dependency) |
| **Incident response** | No formal incident-response process exists beyond the ad hoc recovery-checklist pattern above. This project's own retrospective discipline (`.claude/skills/incident-retro/SKILL.md`) is a real, existing PROCESS artefact for POST-hoc learning, but is not itself a live incident-RESPONSE runbook (detection → triage → mitigate → recover → retro). | Should-have | Epoch 5 |

## Honest summary (R9/R10)

Of the seven NFR categories, **three carry a real blocker-tier gap right now**: availability (no
redundancy/SLO), security (no dependency-vulnerability scan, no pen test), and capacity (two
code-verified O(n^2) scaling cliffs). None of these are live-risk-tier findings under H3's own
carve-out criteria (no imminent danger — this is a simulation, not a live customer-facing service
today) — they are real, measured, Epoch-5-relevant gaps, not urgent fixes. This register does not
itself close any of them; it exists so Epoch 5's go-live analysis has a real, evidence-backed
starting point rather than having to re-derive "what's actually missing" from scratch.

## Not yet done (why this register stays at L1, not claimed higher)

This is a first population pass, not a hardened, maintained-over-time register. Not yet done: a
mechanism keeping "current measured state" fresh as the codebase changes (this document is a
point-in-time snapshot of H3's own point-in-time findings); a formal SLO-setting exercise for
availability/latency (both currently read "no target has ever been set," not a measured gap against
a real target); a genuine dependency/CVE scan (`pip-audit` still not installed).
