# Production Readiness — NFR Register, Parts B and C

**Status:** DISCOVER/FRAME (Lane-3, doc-only). **No code changed by this doc; no tests run; no gating.**
Design of the go-live non-functional-requirements register, continuing the work Part A began.
**Atoms served:** `H3_production_readiness_nfr_evidence` (the evidence pass, "Part A") and
`H4_go_live_nfr_register` (epoch 5, the register itself) — the director noted "NFR Parts B/C still open".
**Author:** discovery fork, 2026-07-13.
**Inputs read directly:** `docs/design/PRODUCTION_READINESS_EVIDENCE_PASS.md` (Part A),
`docs/design/PRODUCTION_READINESS_SECURITY_SUMMARY.md`, `docs/design/H4_GO_LIVE_NFR_REGISTER.md`,
`docs/design/GO_LIVE_SEAM_AND_INTERNAL_SEAMS_DESIGN.md`, `docs/market_research/ofgem_licence_readiness.md`,
CLAUDE.md scale constraints C-S1..C-S5, `maturity_map.yaml` H3/H4 registrations.

---

## 0. What A covered, and the split into B and C

**Part A (`PRODUCTION_READINESS_EVIDENCE_PASS.md`)** is a point-in-time *measurement* pass over four
SRE-style areas: **recoverability, security posture, performance/capacity, availability**. H4 organised
those into a seven-row register. Part A's value is that it *measured* (R9: observed-with-evidence), but it
is a snapshot and it deliberately left whole NFR classes untouched (observability, DR/RTO-RPO, change
management, audit/non-repudiation, data-protection lifecycle, and every *regulatory* operational NFR).

**Parts B and C name and status those remaining classes so the Epoch-5 go-live analysis has a complete
register, not four measured areas plus silence.** The split:

- **Part B — Operational & Resilience NFRs** (the SRE/operability class): availability & redundancy,
  recovery (RTO/RPO/DR), observability & alerting, incident response & runbooks, change management &
  rollback, capacity & performance-at-scale. *"Can we keep it running, know when it isn't, and get it
  back?"*
- **Part C — Security, Data-Protection & Regulatory-Compliance NFRs** (the licence/go-live class):
  authn/authz & segregation of duties, secrets & key management, vulnerability management, data protection
  (GDPR/encryption/retention/erasure), audit trail & non-repudiation, and the **Ofgem operational-capability
  and financial-resilience NFRs that gate holding a supply licence at all**. *"Are we allowed to operate,
  and can we prove it?"*

### 0a. The honesty note that governs every status below (two subjects, one register)

Part A measured **the autonomous-build harness** (Skynet, the six background daemons, git backup, the
two `.env` secret files) — because that is the only running system that exists to measure today. A real
go-live NFR register is about a **second, not-yet-built subject: the deployed energy-supply platform** the
company would actually run in production. These are different systems with different NFRs. This doc tags
each row's subject so the two never get conflated into a false "met":

- **[HARNESS]** — a property of the running build machine, measurable now. Real evidence, but *not* the
  go-live subject; it is a proxy and a lower bar.
- **[PLATFORM]** — a property the deployed supplier platform would need at go-live. Mostly design-level
  today (the platform isn't built), so "status" here is honestly "gap / not-yet-applicable-but-required",
  never "met" on the strength of a harness measurement.
- **[COMPANY-SIM]** — already modelled inside the simulated company layer (`company/**`), which is real
  code with real tests; this is where the *regulatory* NFRs have genuine partial coverage.

Marking a HARNESS measurement as satisfying a PLATFORM NFR would be exactly the category error R9/R14
exist to prevent. Where a row can only be evidenced against the harness, it says so and stays a PLATFORM gap.

---

## Part B — Operational & Resilience NFRs

Tier: **Blocker** (go-live cannot proceed) / **Should-have** (needed for a credible service, not a hard
gate) / **Later** (post-live hardening). Status: **met / partial / gap**.

| # | NFR (requirement) | Evidence that would satisfy it | Current status | Tier |
|---|---|---|---|---|
| **B1** | **Availability & redundancy.** A stated availability SLO for each critical service and no single point of failure that takes the whole service down. | A published SLO (e.g. 99.9% for the billing/collections path), redundancy across ≥2 failure domains, a measured availability figure against the target. | **[HARNESS] gap → [PLATFORM] gap.** Whole stack is single-machine by design (CLAUDE.md Technical env), no redundancy; 6 daemons share one NTFY-env SPOF; real crash history (2 crash-loops + a ~22min nvm-path outage/week, `session-watchdog-log.md`). **No SLO has ever been set** — the register reads "no target", not "measured against a target". | **Blocker** |
| **B2** | **Recovery — RTO / RPO / DR.** A stated recovery-point and recovery-time objective per data class, and a *tested* restore from an off-machine copy. | Named RTO/RPO per data class; an off-machine backup of all canonical state; a restore drill from that off-machine copy (not a local `cp`). | **[HARNESS] partial.** Git-tracked content has real off-machine recoverability (GitHub mirror). `company/data/*.db` gap from Part A is **closed** — `background/backup_company_data.py` now mirrors all 4 DBs to the private ops repo (verified present). **Still gap:** no RTO/RPO is *stated* per data class; Part A's "restore test" was a 236-byte local `cp` (~22ms), **not** a machine-loss restore drill; no encryption of the backup assessed (see C4). | **Blocker** (RTO/RPO undefined; no real DR drill) |
| **B3** | **Observability & alerting.** Defined SLIs, a metrics/health surface, alerting that fires on the SLI breach (not just on process death), and bounded log retention. | An SLI catalogue mapped to B1's SLO; a metrics endpoint; alert rules tied to SLIs; log-rotation policy. | **[HARNESS] partial → [PLATFORM] gap.** Rich transition-only NTFY alerting exists (R5) and `agent_status.json`/observability logs are real telemetry, but they alert on *process/build* transitions, **not on service SLIs** (because no SLI/SLO exists — B1). **Concrete regression:** `risk-committee-log.md` is now **~316 MB** (301 MB at Part A's 277 MB reading) — still unbounded, no rotation — the log-retention gap named in Part A has *grown*, confirming no mechanism closed it. | **Should-have** (SLIs); **Later** (log rotation, but do it — it is cheap and drifting) |
| **B4** | **Incident response & runbooks.** A live detect→triage→mitigate→recover→retro runbook for the *service*, distinct from post-hoc learning. | Named runbooks per failure class with tested release actions (R11: no orphan transitions). | **[HARNESS] partial → [PLATFORM] gap.** Real artefacts exist but are **harness-scoped**: `docs/design/ALARM_RESPONSE_RUNBOOK.md`, `docs/staging/done/MAINTENANCE_RUNBOOK.md`, and the `incident-retro` skill (post-hoc learning, the source of the R-rules). None is a *service* incident-response runbook for the deployed platform (e.g. "settlement feed down → fall back to last-known, flag stale" — that obligation is designed in the go-live seam §1.3 but has no runbook). | **Should-have** |
| **B5** | **Change management & rollback.** Every change is reversible with a tested rollback, and a release's *effect* is verified on the live surface. | Versioned deploys, a rollback procedure, R11 live-pixel verification, R2 "committed != running". | **[HARNESS] partial.** Strong *within the build discipline*: git revert is the rollback (PROCEED_BY_DEFAULT's whole asymmetry), R2/R11 are enforced rules, the `tree_lock` serialises writers, `FORCE_REPUBLISH_FLAG` was the fix to a real orphan-transition (R11). **Gap for [PLATFORM]:** no deploy/rollback story for a running supplier platform (there is no deploy — the site is static JSON regen); "rollback" today means reverting source, not rolling back a live service with in-flight customer state. | **Should-have** |
| **B6** | **Capacity & performance at scale.** Logic behaves correctly and affordably at go-live population, and the design is scale-safe by construction (C-S1..C-S5). | Load test at target population; no super-linear hot paths; the C-S constraints demonstrably held. | **[HARNESS/COMPANY-SIM] partial, with a named blocker.** Part A code-verified **two O(n²) patterns in `simulation/run_phase2b.py`** (per-customer full scans of `all_records`) — ~100× at 10× pop, ~10,000× at 100× pop; invisible at today's 19 customers but a real cliff. **No load test at scale exists.** Scale-*safety* is addressed by design (C-S1..C-S5, see §B7 cross-ref) but not yet retrofitted into the O(n²) paths. | **Blocker** (the O(n²) paths, at any real population — matches `W2_2_population_draw`'s own scale dependency) |

### B7. C-S1..C-S5 are Part-B scale evidence — cross-reference

The CLAUDE.md scale-readiness constraints are **not separate from this register; they are the design-time
evidence for B6 (and B2's replay/RPO and B5's determinism).** They are cheap-now/brutal-to-retrofit
constraints, so their *status* is "constraint declared, retroactively applied on-touch" — a real, honest
state, not "met".

| Constraint | What it guarantees | NFR it evidences | Status |
|---|---|---|---|
| **C-S1** event-arrival tolerance (no batch-completeness assumption) | correctness under late/out-of-order/one-at-a-time events | B6 (scale), B3 (partial-data observability) | Constraint declared; enforced at next touch. The go-live seam's async envelope (`correlation_id`, out-of-order match) is its concrete mechanism (GO_LIVE_SEAM §1.2). |
| **C-S2** idempotency + deterministic replay + RNG substream discipline | processing twice is harmless; replay reproduces state | **B2 (RPO/replay = recovery)**, B5 (deterministic rollback) | Declared; the seam's `correlation_id` idempotency key is the mechanism. RNG-substream discipline proven necessary by the real 01:09Z life-event incident. |
| **C-S3** asynchronous wall contracts (request/response separated in time) | latency is representable; no same-step resolution | B1/B6, and the go-live SLA boundary | **Design resolved** (GO_LIVE_SEAM §1.1: async-shaped contract, sync resolver under it). Same law as A3_approval_interface's "schema cannot represent pending latency" — build one mechanism. |
| **C-S4** persistence behind an interface (append-only event log) | storage swappable without touching logic | **B2 (DR), C5 (audit)** | `company/interfaces/bitemporal_event_log.py` exists and is the append-only abstraction. Serves both DR and the C5 audit trail. |
| **C-S5** time-scale invariance declaration | logic isn't secretly tied to sim clock speed | B6 (portability of scale claims) | Declaration convention exists (L3+ atoms); no global audit. |

**Simplicity guard (CLAUDE.md, binding):** none of B1-B6 is closed by building distributed infrastructure —
current volumes can't exercise it and CLAUDE.md bars it. B6's fix is de-quadratic-ing two loops and load-testing;
B1/B2's fix is *stating targets and doing one real drill*, not a cluster.

---

## Part C — Security, Data-Protection & Regulatory-Compliance NFRs

| # | NFR (requirement) | Evidence that would satisfy it | Current status | Tier |
|---|---|---|---|---|
| **C1** | **Authn / authz / segregation of duties.** Every privileged action is authenticated, authorised, and the actor recorded; duties segregated (no single actor both raises and approves). | Auth on every endpoint; a role/permission model; SoD enforced; the actor logged per action. | **[HARNESS] partial → [PLATFORM] gap.** Harness has real auth on the File API (header auth, 403 on mismatch, path-traversal guarded) and a strong *governance* SoD model (director-reserved one-way doors, twin read-only, console-only Tier-1). `F4_company_internal_authz` models internal segregation at the company layer. **Gap:** no authz model for a *customer-facing* platform (none exists); 1 low finding (wide-open CORS) from Part A open. | **Blocker** for [PLATFORM] at go-live; **Should-have** (CORS narrowing) now |
| **C2** | **Secrets & key management.** No secret in the tree; least-privilege access; a rotation policy. | Secrets outside the working tree; rotation cadence; egress allowlist. | **[HARNESS] partial (strong).** Part A: 2/2 secrets gitignored, 600-perm, never in git history; zero secret-shaped strings elsewhere; `background/secrets_location.py` (Option-2 floor, secrets out of tree) and `background/egress_allowlist.py` both present. **Gap:** no key-**rotation** policy or cadence assessed; secret *backup* (B2) is now to the ops repo — confirm it is encrypted at rest (C4). | **Should-have** (rotation); Blocker for [PLATFORM] |
| **C3** | **Vulnerability management.** Automated dependency-CVE scanning in the pipeline; a pen test against the real surface. | `pip-audit`/equivalent run on a cadence; a pen-test report. | **[HARNESS] gap.** `pip-audit` **still not installed** (confirmed this pass — unchanged since Part A); no automated CVE scan has ever run; 150 packages, ~38 outdated, only an *inferred* manual read done. No pen test performed. | **Blocker** (dependency scan is cheap and overdue; pen test for [PLATFORM]) |
| **C4** | **Data protection — GDPR, encryption, retention/erasure.** Lawful basis, a privacy policy, encryption at rest and in transit, retention limits, a right-to-erasure path. | Privacy-policy page; encryption-at-rest on customer stores + backups; retention/erasure mechanism; DPIA. | **[PLATFORM] gap (largest single gap — see §C8).** All customer data is synthetic today (no *live* GDPR exposure), but: **no privacy-policy page exists on the public site at all** (confirmed: zero matches in `site/`; `coldwalk:no_privacy_policy_page` registered); **no encryption-at-rest assessed** for `company/data/*.db` or the ops-repo backup; no retention/erasure mechanism modelled. | **Blocker** (privacy policy + encryption-at-rest) for [PLATFORM] |
| **C5** | **Audit trail & non-repudiation.** Every material state change is recorded immutably with who/when/what; restatements append, never mutate. | Append-only log with valid-time/transaction-time; tamper-evidence; retention. | **[COMPANY-SIM] partial (genuinely strong foundation).** `company/interfaces/bitemporal_event_log.py` is a real append-only, valid-time/transaction-time store (`as_known_at()→None`, restatements append) — this is exactly the audit-trail primitive, and C-S4's persistence interface. **Gap:** no tamper-evidence (hashing/signing) and no coverage audit that *all* material actions route through it (the go-live seam envelope §1.2 would make this structural). Note: `director_input_log.py` HMAC-verifies director inputs — real non-repudiation on that one channel. | **Should-have** (extend coverage + tamper-evidence) |
| **C6** | **Ofgem operational-capability & financial-resilience NFRs (licence-gating).** The operational and capital NFRs that gate *holding a supply licence*: SLC 4A operational capability, 4B financial-responsibility, 4C ongoing fit-and-proper (SMR&I), the post-2021 Minimum Capital Requirement, and customer-credit-balance protection where directed. | Evidence of operational capability per SLC 4A; capital held ≥ Capital Target; role-holder fit-and-proper coverage; a licence-application readiness pack. | **[COMPANY-SIM] discovered, not built.** `docs/market_research/ofgem_licence_readiness.md` holds real sourced findings: SLC 4A/4B/4C; **Capital Target ~£115–130 / dual-fuel-equiv domestic customer** (an honest, unresolved source discrepancy, needs the primary FRC decision PDF); milestone assessments are **customer-count-triggered** (pause onboarding at 50k/200k for Ofgem review). This is the `H6/licence-readiness` proposal atom's territory — **DISCOVER done, BUILD gated to Epoch 5.** Distinct from B2/F3/F4 and from B2_opex segment-ROCE (confirmed independent by code read). | **Blocker for real go-live** (it is the go/no-go licence gate); not a build item this epoch |
| **C7** | **Regulatory-reporting resilience & timeliness.** Statutory returns/data-flows produced accurately and *on the regulator's calendar*, with resilience if a run is late. | A reporting calendar; the returns modelled; timeliness SLAs; a late-run fallback. | **[COMPANY-SIM] partial (real coverage).** `company/regulatory/` has genuine modelled returns: `desnz_returns.py`, `ofgem_supply_return.py`, `reporting_calendar.py`, `settlement_reconciliation.py`, `annual_compliance_attestation_register.py`, plus the levy registers (CfD, RO, ECO, EBRS/EBSS, CCL). **Gap:** these model *content*, not *timeliness-under-failure* — no NFR that a return is late-tolerant/re-runnable (ties to B3 observability + C-S1 late-arrival). | **Should-have** (timeliness/resilience layer); content already partial |

### C8. The biggest genuine gap

**Data protection (C4) for the [PLATFORM] subject is the largest genuine gap**, because *every* sub-item
is missing at once and each is a hard prerequisite the moment a single real customer record exists: no
privacy-policy page (confirmed absent), no encryption-at-rest anywhere (not even assessed, and it now also
covers the new ops-repo DB backup), and no retention/erasure path. It is currently masked only by the fact
that all data is synthetic — the instant that changes, C4 flips from "no live exposure" to "operating
unlawfully". It is cheap to *begin* (a privacy page, an encryption assessment) and expensive to retrofit
across a live customer base, which is precisely the CLAUDE.md scale-readiness argument applied to compliance.

### C9. The top go-live blocker

**C6 — the Ofgem licence gate — is the top go-live blocker**, and it is a different *kind* of blocker from
all the others: B1/B2/B6/C3/C4 are things the company *builds and fixes*; C6 is a go/no-go decision made by
**Ofgem's licensing function**, not by the company's own ops/security review, and it carries a real ~6-month
processing timescale (Ofgem guidance, 27 Feb 2026) plus a hard capital floor (~£115–130/customer) and
customer-count-triggered onboarding pauses. No amount of internal NFR closure substitutes for it. It is
correctly Epoch-5-gated and director-reserved (values/one-way-door adjacent), but it belongs at the *top*
of the register because it is the constraint that can invalidate a go-live even when every other NFR is green.

---

## Part D — Ordered build/evidence plan (what to do, in what order)

Ordered by "cheap + unblocks the most" first. Each item names its NFR and whether it is a **go-live blocker**
or **later**. Everything here is BUILD/evidence work — this doc authors none of it (Lane-3 doc-only); it is
the queue for when the work is drawn.

**Do now (cheap, closes real gaps, mostly harness — not epoch-gated):**
1. **Install and run `pip-audit`** (C3). Cheapest highest-value item in the whole register; a CVE scan has
   *never* run. → **go-live blocker** (removes an unknown).
2. **Rotate/bound `risk-committee-log.md` and set a log-retention policy** (B3). It has grown 277→316 MB
   *since Part A named it*; it is drifting. → later, but do it — it is a one-liner and self-worsening.
3. **Narrow the File-API CORS** and terminate the stale dev file-servers (C1, Part A findings still open). → later.
4. **Write a privacy-policy page** for the public site and **assess encryption-at-rest** for `company/data/*.db`
   and the ops-repo backup (C4). → **go-live blocker** (the largest gap, §C8); the page is cheap now.

**Evidence / measure (turns "no target" into a real gap-against-target):**
5. **Set SLIs and an availability SLO** for the critical path, and wire alerting to the SLI breach (B1/B3).
   Until this exists, B1's status is "no target", which is weaker than a measured gap. → go-live blocker (define it).
6. **Run one real DR drill** — restore `company/data/*.db` from the ops-repo backup on a clean location, and
   **state RTO/RPO per data class** (B2). Part A's 22ms local `cp` is not this. → go-live blocker.
7. **Load-test at 10× and 100× population** to convert B6's O(n²) extrapolation into measurement, and
   **de-quadratic the two `run_phase2b.py` scans** (index `all_records` by `customer_id` once). → go-live
   blocker at real population (matches `W2_2_population_draw`).

**Design-then-build (Epoch-gated / larger):**
8. **Author service incident-response runbooks** for the go-live seam's degraded-feed obligations (B4), with
   tested release actions (R11 no-orphan-transitions). → should-have.
9. **Extend the bitemporal event log to a full audit trail** — coverage audit that all material actions route
   through it, plus tamper-evidence (C5); make it structural via the go-live-seam envelope. → should-have.
10. **A regulatory-reporting timeliness/resilience layer** over `reporting_calendar.py` (C7): late-tolerant,
    re-runnable returns (ties to C-S1/C-S2). → should-have.
11. **Ofgem licence-readiness pack** (C6) — the SLC 4A/4B/4C evidence, capital-adequacy model against the
    Capital Target, role-holder fit-and-proper coverage. **DISCOVER done; BUILD stays Epoch-5-gated and
    director-reserved.** → the top go-live blocker, but not a this-epoch build.

**Go-live blocker set (the honest short list):** C3 (no CVE scan ever), C4 (data-protection, §C8), C6 (Ofgem
licence, §C9 — the top one), B1 (no SLO), B2 (no RTO/RPO, no real DR drill), B6 (the O(n²) cliff at population).
Everything else is should-have or later. **None is a live-risk-tier emergency today** — this is a simulation,
not a live customer-facing service — but each is a genuine, evidenced Epoch-5 go-live prerequisite, not a
checkbox.

---

## Appendix — grounding checks run this pass (direct repo read, 2026-07-13)

- `background/backup_company_data.py`, `background/secrets_location.py`, `background/egress_allowlist.py` — **present** (B2/C2 evidence).
- `company/interfaces/bitemporal_event_log.py` — **present** (C5/C-S4 audit + persistence primitive).
- `site/` grep for "privacy policy"/"privacy-policy" — **zero matches** (C4 gap confirmed).
- `pip-audit` — **not installed** (C3 gap confirmed, unchanged since Part A).
- `docs/observability/risk-committee-log.md` — **~316 MB** (B3: grown from Part A's 277 MB, still unbounded).
- `company/regulatory/` — `desnz_returns.py`, `ofgem_supply_return.py`, `reporting_calendar.py`,
  `settlement_reconciliation.py`, plus levy/obligation registers — **present** (C7 partial coverage).
- `docs/design/ALARM_RESPONSE_RUNBOOK.md`, `docs/staging/done/MAINTENANCE_RUNBOOK.md`,
  `.claude/skills/incident-retro/SKILL.md` — **present** (B4 harness-scoped artefacts).
- `docs/market_research/ofgem_licence_readiness.md` — **present** (C6 discovery evidence).
- SLO/SLI grep across `docs/ company/ background/` — only mentions in `H4`/`maturity_map`, **no definition** (B1/B3 gap).
