# PRODUCTION_READINESS_BASELINE — measure the baseline, register the bar (P2)

**Staged:** 2026-07-11 by advisor; director-decided (originated in a parallel
director session; advisor reviewed and amended — amendments marked). **Place
in the arc:** feeds Epoch 3 (the wall is the go-live seam; adapters must carry
production properties) and Epoch 5 (go-live analysis). Epoch-2-compatible:
an evidence pass, a register, and standing constraints — **no hardening
builds are authorised by this doc.** Background-lane compatible; do not
displace the spike queue. Register as map atoms under Lane H (+ links from
W4/Epoch-5 prep) as part of actioning.

## Problem
No measured baseline exists for non-functional properties (availability,
latency, capacity, security posture, recoverability) and no register of what
production-grade means for this business at go-live. We cannot currently
answer: what breaks if Skynet's disk fails, what our recovery time is, what
scales with population, or what a regulator/auditor would demand operationally.

## Part A — Non-functional evidence pass (measure, don't assert; R9 throughout)
- **Recoverability:** enumerate everything canonical that exists ONLY on
  Skynet (caches, state, ledgers, logs). Test an actual restore of one
  representative artefact — **AMENDED: restore to a scratch location, never
  over live state; a restore test is not read-only and must be treated with
  care.** Report measured RTO/RPO, not assumed.
- **Security posture:** secrets inventory (what credentials exist, where they
  live, rotation state), exposed-surface inventory (Funnel endpoints, open
  ports, write paths), dependency vulnerability scan of the Python estate.
  **AMENDED — routing:** raw security findings (secrets locations, open
  ports, vulns) go to the PRIVATE ops repo ONLY; the public/business surface
  carries a sanitised posture summary (counts, tiers, remediation status),
  never the map of weaknesses. **Absorb the harness sprint's existing
  sandbox/Pattern-C recommendation as an input here rather than re-deriving
  it — link both.**
- **Performance/capacity:** measured full-run wall time, peak memory, disk
  footprint, and how each scales with customer count (extends evidence-pass
  Q3). Identify the first resource that breaks at 10x/100x population.
- **Availability:** the daemon stack's real uptime from existing logs, and
  every single point of failure in the current operation.

## Part B — Go-live NFR register (extends the obligations-register pattern)
One entry per production category: availability/SLOs, latency budgets,
security (authn/authz, secrets, pen test), data protection (GDPR, encryption,
backups), operational resilience (link the existing cyber-baseline
obligation), change management/rollback, capacity, incident response. Each
entry: what a real UK supplier needs, current measured state (from Part A),
go-live tier (blocker / should-have / post-live), and which epoch it lands
in. This register is the input to Epoch 5, maintained from now.

## Part C — Standing design constraints (add to CLAUDE.md's constraint set)
(1) No credentials ever in the repo or in code. (2) Every financial-effect
operation must be idempotent and leave an audit trail sufficient to
reconstruct it — the bitemporal ledger work should satisfy this natively:
VERIFY rather than assume, and record the verification. (3) Every walled
interface's typed contract must be able to carry operational terms (timeouts,
retries, failure modes) so the wall can become a real SLA boundary at go-live
without redesign.

## Immediate-action carve-out
Any Part A finding that is a live risk to today's operation (unrecoverable
canonical data, an exposed credential) is fixed under normal tiering NOW, not
deferred to an epoch boundary.

## Non-negotiables
Measurements against the real system; register before remediation; no
production-hardening builds under this doc; findings land on a business/ops
surface (sanitised where security-sensitive, per the routing amendment), not
just in a report.

## DoD
Part A findings filed (private routing honoured) with measured numbers;
Part B register live and linked from the obligations surface; Part C in
CLAUDE.md with the ledger-idempotency verification recorded; atoms
registered; any carve-out items actioned; one digest line. Pixel rule applies
to the public posture summary.
