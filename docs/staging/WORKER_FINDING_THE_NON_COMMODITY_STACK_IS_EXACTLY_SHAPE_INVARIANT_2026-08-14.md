# WORKER FINDING — the whole non-commodity stack is exactly shape-invariant, including the quarter of it the scope brief says must not be

**Severity:** LATENT · **Lane:** W4_the_wall
**found:** 2026-08-14, running the scope brief's disqualification battery on
`EP14_adapter_published_cost_stack` (`docs/design/EP14_PUBLISHED_COST_STACK_BATTERY_2026-08-14.md` §2).
Queued rather than fixed on sight per SELF_INTERRUPT discipline.

## Why LATENT and not BLOCKING

The test for BLOCKING is that a control or instrument here is untrustworthy, or a published figure may
be wrong. Neither holds. No figure is claimed wrong: the levy totals are what the tabulated rates times
the settled volumes come to, and this finding fetched no source that could say the rates are wrong.
What is missing is a *mechanism* — the charge's dependence on when the kWh was consumed — and a missing
mechanism is a fidelity limit, not a false number. Nothing downstream is being misled today either:
`flexibility_revenue_gbp` is £0.00 across the whole run, so no live consumer is trading against the
flat signal. Graded on the definition. **A later pass that shows a published per-customer or
per-segment figure moving on this upgrades it.**

## The measurement

`observed-with-evidence`, at HEAD 5975a4e26, by executing the shipped functions and reading
`docs/reports/run_output_latest.json`. Nothing monkeypatched.

`simulation/hedged_settlement.py` applies every non-commodity charge **inside** its half-hourly loop
(`for period in range(1, 49)`, lines 166–177), against that period's own `consumption_kwh`. The
application is genuinely half-hourly. Every *rate* it multiplies by, however, is a function of the date
alone. Holding daily volume fixed at 24 kWh on a winter weekday (2022-01-19, resi) and redistributing
it across maximally different shapes:

| shape | non-commodity cost, £/day |
|---|---:|
| flat across all 48 periods | 2.15232 |
| 100% inside the 16 peak periods | 2.15232 |
| 100% outside them | 2.15232 |

Identical to eight decimal places. The combined rate takes exactly **one** distinct value across all 48
periods (£89.68/MWh). Structurally confirmed by a signature census over all 13 readers in
`simulation/policy_costs.py`: not one accepts an intraday time, a period index, or a half-hourly shape.
The entire argument surface is `(date_str, segment)`, plus `aq_kwh` for GGL.

## Why this is a defect and not just a modelling choice

`docs/domain_artefact_library/scope_briefs/ADVISOR_SCOPE_BRIEF_NONCOMMODITY_COST_STACK_2026-08-07.md`
scores exactly this. Its **B2** disqualifies a model where shifting peak changes TNUoS or BSUoS —
**and the stack passes B2.** But its time-variance census names what *should* vary, and lists DUoS band
structure and the CM window under **NOT simplifiable**, *"these carry the personalisation signal and
the true-up physics."* Measured against the run's own published components:

| line | £ | share of stack | brief says | model does |
|---|---:|---:|---|---|
| CM levy | 336,419.95 | 6.95% | charge falls in the ~winter weekday 16:00–19:00 window | flat £/MWh on all volume |
| electricity network | 869,332.79 | 17.97% | DUoS varies by time band | single combined rate, no bands |
| | | **24.92%** | | |

(Stack total £4,838,389.48 = electricity policy 3,404,188.65 + electricity network 869,332.79 + gas
policy 171,108.84 + gas network 393,759.19, summed 2016–2025.)

So **B2 is passed by a model that has no time-variance anywhere**, including the two components where
flatness is the wrong answer. That is the shape worth naming: a test that can only be failed by
over-modelling is passed by modelling nothing, and the green verdict then reads as fidelity when part
of it is the absence of the mechanism. The one DUoS-only table, `_DUOS_IC_BY_YEAR`, is a flat annual
£/MWh too, so the band structure is absent on both the resi and I&C paths.

## What this means for EP14 specifically

The brief frames this stack as *"the cost side of the abatement engine — time-shifting only creates
value where the stack is time-varying."* An adapter that ingests CDCM tariff spreadsheets **at full
fidelity** parses a DUoS band structure that the reader interface cannot express: today's readers
return one number per date, and a banded charge has no return slot. So this is a **seam** question that
lands before the parser, not after it — if EP14 is opened against the current reader signature, the
adapter's band data is discarded at the interface and the ingest is fidelity theatre.

Stated as a recommendation being acted on by recording it, not an ask: **EP14's exit criteria should
require the reader interface to carry the band/window dimension for the components the brief marks
non-simplifiable, and should NOT cite B2 as evidence** — B2 is currently passed by the absence of the
thing EP14 exists to build.

## What discharges it

Not an instance fix on the CM levy — R10 forbids closing an absurdity-class defect on one line. The
class is "a charge whose real incidence is time-banded, served as a flat per-MWh rate":

1. A declared incidence per component (flat / banded / windowed) covering all 13 tables, in the shape
   `YEAR_KEY_BASIS` already uses for the year convention — the population is already enumerated there.
2. A reader interface that can express a banded charge, so a correctly-parsed band survives the seam.
3. A census control failing when a component declared banded is read through a flat accessor, plus R15
   mutation proof both ways: declaring the CM levy flat must go red once its incidence is windowed, and
   the census must go red on a new undeclared component.

**Not settled here:** whether the CM window and DUoS bands should be modelled at full band resolution
or as a documented simplification with a Birth-Certificated register entry. The brief permits
simplification for minor levies and explicitly refuses it for these two, but that is a curriculum-
visible fidelity decision belonging to whoever draws it, not to this finding.

## Not claimed

That any tabulated rate is numerically wrong (no source fetched — this tick had no network). That any
published figure is wrong today. That TNUoS or BSUoS *should* vary with shape — the brief is explicit
that post-reform they should not, and the model is right about them. That `flexibility_revenue_gbp`
being £0.00 is itself a defect: it was read as evidence that nothing consumes the flat signal yet, and
its cause was not investigated.
