# Core Fidelity Before Loops — Phase Decomposition

Design note for `docs/staging/CORE_FIDELITY_BEFORE_LOOPS.md` (director reorientation,
2026-07-08, P1, RY deferred). Per that instruction's own sequencing guidance ("prefer the
audit and design/anchor-gathering work early since it is cheap"), the block decomposes into
four phases. A and B's *audits* run together first (cheap, no sim runs); their
*implementations* follow, informed by the audit findings; C rides on both.

## Phase 1 — Audits (this phase, evidence below)

### B: Unhappy-path audit — grounded in the actual codebase, not assumption

Swept every candidate process the staging instruction named, verified by reading the real
module (not recalled from memory):

**Already modelled with real latency/failure physics (not gaps — listed so Phase 3 doesn't
duplicate them):**
- Payment-failure dunning cascade: `simulation/arrears_engine.py` — `DD_FAILED` at due_date →
  `FIRST_NOTICE` (+7d) → `SECOND_NOTICE` (+21d) → ... Real day-offsets, though the offsets
  themselves are fixed constants, not drawn from a distribution — a refinement candidate for
  Phase 3, not a from-scratch build.
- Complaint resolution timing: `simulation/feedback_survey.py::dispatch_complaint_and_resolution`
  (Phase RU) — genuinely randomised days-to-resolve (57–120 days for ombudsman-escalated
  cases), real SLA-breach modelling against the 56-day Ofgem window.
- Post-write-off debt recovery: `simulation/arrears_engine.py` (Phase QS) — explicit day-offset
  windows for DCA placement (+30 days).

**Confirmed genuine gaps (verified absent, not just "not remembered"):**
1. **Meter-read arrival/estimation/failure — zero code found anywhere in the codebase.**
   Settlement records are treated as always-available and always-accurate; nothing models a
   read arriving late, failing to arrive, or being estimated. This is the single clearest
   "instant and perfect" process in the whole estate — highest-priority gap.
2. **Bill generation/delivery lag.** `company/billing/invoice.py:87` — `issue_date =
   period_end`: the bill is issued the same calendar day the billing period ends, with no
   generation or postal delay and zero chance of a late bill.
3. **Refund processing is built but completely unwired.** `company/billing/credit_refund.py`
   has a real deadline/overdue mechanic (`working_days_to_pay()`, `is_overdue()`,
   `breached_deadline()` against a real working-days SLA) — but grepping every file in
   `simulation/` for a caller returns nothing. The module is dead code: no refund event is
   ever generated in a live run.
4. **Contact-centre response/acknowledgement time.** No dedicated latency module exists —
   distinct from complaint *resolution* time (which is modelled); the *first-response* SLA is
   not.
5. **Switching-funnel stage timing.** `simulation/acquisition_funnel.py`'s five stages (quote
   → application → credit_check → onboarding → cooling_off) exist as discrete probabilistic
   gates but resolve against a single `term_start` date with no stage-to-stage calendar-day
   spacing modelled — the funnel is real in *outcome* but instant in *time*.

### A: Household segment & psychology design (this phase — design only, not implementation)

Archetype dimensions, informed by what the existing behavioural machinery already consumes
(so segments *parameterise* real mechanisms rather than requiring new ones):

| Dimension | Values (draft) | Feeds |
|---|---|---|
| Dwelling type & tenure | terraced/semi/detached/flat/bungalow × owner/renter | consumption baseline (existing `household.py` EPC hooks), switching friction (renters move more) |
| Occupancy | 1/2/3-4/5+ person | consumption scale |
| Income band / fuel-poverty status | above-median / near-median / fuel-poor (>10% income on energy) | `income_stress` trajectory severity, payment method mix, forgiveness buffer |
| Payment method | DD / prepay / on-receipt | `arrears_engine.py::payment_method()` — already segment-aware by `segment` (resi/SME/I&C); needs archetype-awareness within resi |
| Tech adoption | smart meter / EV / heat pump / solar (any combination) | consumption shape (`household_demand.py`'s existing EPC/EV/ASHP multipliers), export credits (SEG) |
| Engagement level | active / passive / disengaged | `company/crm/churn_model.py`'s existing active/passive renewal split (currently a flat 35%/65% population split, not segment-conditioned) |

Psychology parameters each archetype carries, mapped to existing consumers of them:
- Price sensitivity / elasticity → `simulation/market_switching_propensity.py` (currently
  population-uniform per year)
- Switching inertia → `company/crm/churn_model.py`'s `PASSIVE_RENEWAL_RATE` (currently a flat
  constant)
- Complaint propensity → `simulation/feedback_survey.py`'s complaint probability (currently
  driven by bill-shock count only, not archetype)
- Forgiveness buffer / bill-shock response → `simulation/satisfaction_churn.py`,
  `simulation/switching_propensity.py` (currently uniform stress-multiplier bands)

**Anchored-noise law**: every segment share and behavioural-parameter value must cite a real
published UK source (English Housing Survey, ONS, Ofgem consumer-archetype research) via the
discovery agent, registered in `docs/market_research/ASSUMPTIONS.md` with provenance — several
of these already have partial entries there (EPC bands, tenure, EV/solar adoption — see the
"Household Physical Property Attributes" table, currently marked "Gap — household.py not yet
built" for most rows). Phase 2 closes those gaps as part of building the archetype layer, not
as a separate task.

### C: Bill artefact audit (this phase — comparison against a real UK bill)

Read the actual live rendering (`site/customers/index.html`'s `billEquationHtml`/`renderBills`)
against the compliant-bill checklist the staging instruction named:

| Element | Status |
|---|---|
| Standing charge / unit rate split | **Present** — `billEquationHtml()` shows usage × rate = commodity charge, + standing charge, as separate lines |
| VAT | **Present** — separate VAT line when non-zero |
| Network/environmental pass-through | **Present** — shown as a combined line, not itemised by scheme |
| Billing period & consumption | **Present** — consumption_kwh shown; period is a single date, not an explicit start–end range |
| MPAN | **Present, but at profile level, not per-bill** — shown in the account header, not repeated on each bill |
| Meter serial number | **Absent** |
| Actual-vs-estimated read basis | **Absent** — no field exists to flag this (blocked on the meter-read gap above; Phase 3 must produce this flag before Phase 4 can render it) |
| Payment method | **Absent from the per-bill view** (present at account level as `d.ledger`, not repeated per bill) |
| Balance carried forward | **Partial** — an aggregate "Outstanding" total exists at the summary level; no per-bill running balance |
| Back-billing limits context | **Absent** |
| TDCV / annual-comparison context | **Partial** — a "why different vs previous / vs same month last year" waterfall exists, which serves a similar comparative purpose but isn't framed as the regulatory TDCV benchmark |

## Phase 2 — Household segments & psychology (implementation)

Build the archetype layer designed in Phase 1: `simulation/household_segments.py` (or extend
`household.py`/`household_demand.py`) assigns each customer a segment at generation time,
anchored to the real shares registered in ASSUMPTIONS.md. Thread segment-conditioning through
the consumers named in the Phase 1 table above — each becomes a lookup on the customer's
archetype instead of a population-wide constant. Evidence per rule 0b: a named household on
the Customers tab whose segment and psychology visibly shaped a real event (e.g. a fuel-poor,
disengaged archetype's churn-journey trajectory differing from an engaged, above-median one
under the same market conditions).

## Phase 3 — Unhappy paths & time as a random variable (implementation)

Close the five gaps found in Phase 1's audit, in priority order (meter reads first — it blocks
Phase 4's actual-vs-estimated bill flag):
1. Meter-read arrival/estimation/failure — new module, distributions calibrated to real
   data-quality statistics where anchors exist.
2. Wire `credit_refund.py` into the live run (it already has the SLA mechanic — this is
   activation, not a build).
3. Bill generation/delivery lag — a small, real distribution around `issue_date`.
4. Contact-centre first-response time.
5. Switching-funnel stage-to-stage calendar spacing.
Company-observable consequences throughout: late bills, estimated reads, missed SLAs feeding
complaints and (where SLCs require it) compensation — epistemic wall unchanged, the company
sees delays/errors only as a real supplier would. Evidence: the Sim tab showing a latency
distribution doing real work (e.g. a histogram of meter-read delay, with the tail visibly
producing estimated bills).

## Phase 4 — UK-compliant bill artefact (implementation)

Closes the gaps found in Phase 1's bill audit: meter serial, the actual-vs-estimated flag
(consumes Phase 3's meter-read events), payment method and running balance per bill,
back-billing context, and a TDCV-framed annual comparison. `docs/staging/done/
Bill_instructions_and_discovery.md` is prior art for the underlying financial correctness (the
P&L-level non-commodity/VAT figures) — already closed; this phase is purely about the
*document* a customer would see, not the numbers behind it. Portal rendering follows the
existing site design laws. Evidence: a late/estimated/corrected bill a reader can open on the
portal and recognise as what it claims to be.

## Sequencing

Phase 1 (this phase) → Phase 2 and Phase 3 may interleave (Phase 3's meter-read work should
land before Phase 4 needs it, but Phase 2's segment layer doesn't block Phase 3 starting) →
Phase 4 rides on both. RY re-enters the queue after Phase 4 closes, per the staging
instruction's own text.
