# [WORKER FINDING] The world models first response, and the published record says resolution is what matters

**Severity:** LATENT · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** `A46_the_priced_menu`
**Found:** 2026-09-01, by the delivery seat, completing the knowledge pass the director asked for before satisfaction's rationale is built.
**Knowledge:** `docs/market_research/satisfaction_drivers_and_the_three_bill_shocks.md`.

## Class registration

Belongs to `measurements_that_mirror`. Refused consolidation — `H_harness` register, `W2` finding.

## What the published record says

Satisfaction in GB domestic energy is not driven by the ordinary bill. Everything routine scores
74–87% (billing accuracy 80%, understanding 82%, delivery timing 87%, ease of contact 75–77%).
**Satisfaction with how a complaint was HANDLED is 44%** — half of everything else, and that gap is
where the whole spread of the variable lives.

Ofgem names the drivers of that dissatisfaction directly: *"the length of time taken to resolve the
issue, not being kept up to date with the progress of the complaint and suppliers not providing
complainants with a clear view of how long the resolution will take."* Corroborated by a different
instrument: **42% of complainants whose case the SUPPLIER had closed thought it remained
unresolved.** Accessibility was fine — 77% found contact details easily. What happened next was not.

## What our world models

Measured on `run_output_latest.json` — 2,299 contact-centre events across 239 of 251 accounts:

| | |
|---|---|
| `first_response_hours` | median **0.1** (six minutes), mean 3.51, max 92.6, 554 distinct values |
| `breached_sla` | **92 of 2,299 = 4.0%** |
| contacts per customer | median **6**, max **49**, sd **9.70** |
| per-customer SLA-breach rate (≥3 contacts) | mean 0.036, sd 0.066, max 0.333 |
| **resolution time** | **does not exist** |

`saas/contact_model.py` says so in its own words: `COMPLAINT_ESCALATION_DAYS` is *"how long a contact
can go unresolved"* — and *"there's no per-contact resolution-date data to track an actual 14-day
clock"*.

## The finding

**The world models the half of the process the published record says does not drive satisfaction,
and models it implausibly well.** A median first response of six minutes and a 96% within-SLA rate
is not a GB energy supplier; and even if it were, first response is not resolution. The variable
Ofgem names first — *length of time taken to resolve* — has no representation at all.

**Its one time constant matches neither published cut-point.** `COMPLAINT_ESCALATION_DAYS = 14`,
sourced to an internal Phase 4c sub-phase spec. The regulator's two reported cut-points are **Day+1**
(resolved by the end of the next working day) and **8 weeks / 56 days** (the deadlock boundary, after
which the customer may go to the Energy Ombudsman). Fourteen days is neither, and it is the £150
shape once more: an internal number where two published ones exist.

**And there is no "closed but not resolved" state**, which is the single largest measured feature of
the real process — 42% of closed cases. In this world a contact is answered or it breaches an SLA;
it cannot be *shut* while the household still considers it open, which is precisely the state that
produces the 44%.

## What is genuinely there and is worth keeping

Contact **volume** varies richly per household — median 6, max 49, sd 9.70 — and it varies for
reasons the household owns (bill clarity, bill shock, engagement archetype), with the archetype
structurally unreadable by the company by design. That is real per-household heterogeneity with a
real rationale, and it is the raw material a satisfaction term should be built on. What is missing is
not the *arrival* of contacts; it is what happens to them.

## What is owed

1. **Give a contact a resolution, not just a first response** — a resolution clock with the two
   published cut-points as its shape. Two published quantiles determine a distribution; Day+1 and
   8-week shares are reported quarterly per supplier, so the model needs no invented mean.
2. **Give it a "closed but not resolved" state**, at the published 42%, because that is what the
   44% satisfaction figure is measuring and it cannot be reproduced without it.
3. **Re-source `COMPLAINT_ESCALATION_DAYS`** to 56 days (the deadlock boundary) or state why 14 is
   the right internal SLA and stop calling it the escalation point.
4. **Then** wire resolution experience into `sim_satisfaction` — which is the rationale the director
   asked for, and the reason this knowledge pass came first. It is NOT built here: it moves every
   financial figure and needs its own pre-registration and one-variable run.

## What this does not claim

Not that the contact-centre model is wrong for what it is — it is careful, and the archetype term is
exactly the kind of structurally-unreadable driver the wall wants. The claim is narrower: the
process it models stops at the point the published evidence says the interesting part begins, and
the constant it uses to mark that point is not the one the regulator reports against.
