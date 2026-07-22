# PROPOSAL — engagement responds to market state (future mechanism, not built)

**Provenance.** `proposal` · DISCOVER/FRAME-workable now · **NOT built, NOT registered to `maturity_map.yaml`** (orchestrator is sole map writer). Routed **through the gate** (propose-then-proceed / DIRECTOR_TWIN §3a for BUILD-open; the values-adjacent curriculum framing keeps the OPEN decision director-reserved).
**Origin.** R13 ruling, director console 2026-07-22 (engagement-mix), Q-B verbatim: *"keep the mix STATIC for now; a hardcoded regime-timed schedule would be exactly the MC-1 script class, so never that — instead register 'engagement responds to market state (offer availability, fixed-vs-SVT spread)' as a future mechanism proposal through the gate."*

## The gap this serves
The engagement mix (`simulation/household_segments.py`, ACTIVE 0.45 / PASSIVE 0.35 / DISENGAGED 0.20) is a
**static** population constant. The real active-tariff share swung ~35% (2016–20 steady) → ~10% (2023
crisis trough) → ~45% (Oct-2025 recovery) — a 35-point swing driven by **market state**, not calendar time
(`svt_rates_active_passive_2016_2025.md` §2–3). A static constant cannot represent that; the crisis
collapse was *caused* (fixed tariffs withdrawn because wholesale exceeded the cap ceiling → no viable
product to switch to), not scheduled.

## The forbidden shape (explicitly ruled out)
A **hardcoded regime-timed schedule** — "in 2023 set active=0.10, in 2025 set active=0.45" — is the
**MC-1 script class**: a scripted, date-keyed override that hardwires a known-future outcome. **Never
that.** It fails the point-in-time blindfold in spirit (the number is written because we know how the year
turned out) and the R13 curriculum-must-be-caused principle.

## The proposed shape (caused, not scripted)
Engagement **emerges from observable market state**, so the crisis collapse and recovery *fall out of the
mechanism* rather than being typed in:
- **Drivers (all company-observable / world-published, no future leak):** (a) **offer availability** — are
  viable fixed products on sale at all (during 2021–22 they were not)? (b) **fixed-vs-SVT spread** — the
  live incentive to switch; when fixed > SVT (pre-EPG expensive fixes) the rational active share *should*
  collapse. Both are point-in-time market observables, not forward data.
- **Mechanism:** the per-renewal `active_renewal_probability` (or an effective engagement propensity) is
  **modulated by current market state** — a household's durable ACTIVE/PASSIVE/DISENGAGED *disposition*
  (Q-A: behavioural, unchanged) meets a *market* that may offer nothing worth switching to. Disposition ×
  opportunity = realised switching. When opportunity → 0 (no fixed offers), even ACTIVE households don't
  switch; the observed active *stock* collapses without any disposition change.
- **Why this beats a schedule:** it's **transferable** (a second market / second crisis reproduces the
  collapse from its own fundamentals), **blindfold-clean** (reads only current observables), and it makes
  the 2023 inversion a *test the company can fail* (does its churn model see switching dry up?) rather
  than a scripted input.

## Coupled-triad framing (per COUPLED_TRIAD doctrine)
- **SIM/WORLD:** market-state modulation of realised switching (offer availability + spread → opportunity).
- **COMPANY (through the wall):** discovers the drop in switching from its own churn observations — must
  not be *told* offers were withdrawn; infers it.
- **HARNESS:** measures the belief-vs-truth gap on the switching-collapse regime (does the company's churn
  forecast track the caused collapse, or does it assume a static active share and miss it?).

## Status / next
- **DISCOVER/FRAME now:** refine the driver set + the opportunity function shape (doc-only).
- **BUILD:** gated — this is a curriculum-mechanism change (R13, values-adjacent). Opens via the
  propose-then-proceed gate / DIRECTOR_TWIN §3a within an open front; **not** built here.
- Candidate atom name (for the orchestrator to register if opened): `ENGAGEMENT_MARKET_STATE_RESPONSE`.
