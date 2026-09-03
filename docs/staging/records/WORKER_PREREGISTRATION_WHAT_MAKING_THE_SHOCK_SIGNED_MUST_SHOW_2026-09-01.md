# [WORKER PREREGISTRATION] What making the bill shock signed must show

**Severity:** RECORDED · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** `A46_the_priced_menu`
**Filed:** 2026-09-01, **before the change.** Every number below was measured on
`docs/reports/run_output_latest.json` (11,565 bills, 11,255 carrying both a shock and its baseline)
BEFORE any line of `saas/bill_generator.py` was edited, and none was written after a result.
**Knowledge:** `docs/market_research/what_bill_shock_is.md` — the definition, established and NOT re-opened.
**Finding:** `WORKER_FINDING_BILL_SHOCK_IS_THREE_CAUSES_AND_A_SIGN_COLLAPSED_INTO_ONE_ABS_2026-09-01`,
owed item 2: *"Sign first, and separately."*
**Predecessor:** `WORKER_PREREGISTRATION_WHAT_SPLITTING_THE_SHOCK_SERIES_BY_POPULATION_MUST_SHOW_2026-09-01`
(the population split, landed `98db658f2`). This is the second of the two commits that item required
and it is deliberately not bundled with it.

## The question this answers first, because the rest follows from it

**Is the quantity signed?** Yes — and therefore a *shock* is not the quantity.

The established definition says a shock is an **increase**, for both populations. For standard
credit the three published triggers are cold weather, a usage change, and a catch-up after
estimates: all upward. For a level direct debit the regulated trigger (SLC 27B, ±5%) and Ofgem's
2022 escalation cut (>100%) are about a payment **rise**. Nothing in the published record describes
a household shocked by being asked for less.

So the repair is not to publish a negative shock. It is:

* `bill_movement_pct` — **signed**, positive meaning the bill went up. The honest quantity, always
  present when a baseline exists.
* `bill_shock_pct` — the movement **when it is an increase**, and **`None` when the bill fell.**

**`None`, not `0.0`.** A bill that fell has not been measured at zero shock; no shock happened to
it. `0.0` would enter every downstream mean and drag it toward a number no household experienced —
this project's `a_default_zero_parameter_turns_an_unobservable_cause_into_a_published_measured_zero`
class. `None` is already fully supported at every consumer because a first bill has always carried
it. A bill that did **not** move keeps `0.0`: that is measured, and it is zero.

**The fail-closed guard in `simulation.contact_propensity` STAYS.** It refused a shock of
-1.4434 on 2026-09-01 and took the publish cycle down with it for 75 minutes, and it was right: a
negative should never have reached it. The repair belongs at the definition, not at the guard.
Wrapping the consumer in another `abs()` or an `or 0` is the naive repair that reinstates the fold
while looking like resilience, and it is already in this project's catalogue.

**And the arithmetic stops being written twice.** `company.billing.monthly_bill_assembly` recomputed
the shock in the same shape after folding a catch-up onto the bill. A catch-up *refund* is exactly
the bill that branch runs on, so a sign fix made in one copy and missed in the other would have left
the defect live in the place it bites hardest. Both now call `saas.bill_generator.bill_movement`.

## The predictions

**P1 — 5,161 of 11,255 bills (45.9%) lose their shock and gain a movement.** That is the size of
the defect: nearly half of every "bill shock" this codebase has computed is a bill that went DOWN.

**P2 — the published shock-event count falls 3,161 → 1,748**, a drop of 1,413 (44.7%). Events are
selected at `bill_shock_pct >= 0.20` and that selection becomes direction-aware with no change to
the selecting code.

**P3 — 5,161 bills gain clarity, by a mean of +0.0876 and at most +0.5.** The clarity penalty was
`min(shock, 1.0) * 0.5` applied to households the supplier had just refunded. This is the leg with
the widest blast radius: clarity drives `contact_propensity`, which drives the contact-centre log,
which drives satisfaction and through it churn. **I am not predicting those downstream figures**,
because more than one thing about a household's year moves at once and a number I cannot attribute
is not a prediction. The DIRECTION is predicted: fewer contacts, higher average clarity.

**P4 — THE HEADLINE GETS WORSE, IN EVERY SINGLE YEAR, AND THAT IS THE POINT.**
`financial.annual[].avg_bill_shock_pct`, before → after:

| year | before | after | n before → after |
|---|---:|---:|---|
| 2016 | 0.3081 | **0.4312** | 631 → 393 |
| 2017 | 0.2840 | **0.3575** | 1,037 → 604 |
| 2018 | 0.2567 | **0.3092** | 1,004 → 577 |
| 2019 | 0.3376 | **0.4346** | 1,016 → 559 |
| 2020 | 0.2995 | **0.4069** | 1,145 → 583 |
| 2021 | 0.3415 | **0.4226** | 1,256 → 751 |
| 2022 | 0.4216 | **0.5752** | 1,327 → 799 |
| 2023 | 0.3797 | **0.4672** | 1,393 → 769 |
| 2024 | 0.3218 | **0.4348** | 1,601 → 783 |
| 2025 | 0.3397 | **0.4641** | 845 → 276 |

Ten years, ten rises. **If removing half the events had made the figure smaller I would distrust
it** — it would have meant I had selected the flattering half. Decreases are on average the milder
movements, so dropping them raises the mean of what is left.

**P5 — the monthly headline peak rises 465.3% → 501.5%, and months above 200% rise 7 → 18.**
On `monthly_ops.monthly[].avg_shock_pct` as `98db658f2` left it (the `"bill"` population, events at
≥0.20): the worst month moves from 2017-02 (n=3) to 2019-02 (n=2), and the count of months above
200% rises. **The thin months get thinner** — 18 months above 200% on samples this small is a
statement about the bound, not about the world, and the bound landed in `8e395664e` is what a
reader has to read those months through. Sharper, and worse-looking, in both directions at once.

## What would refute this, stated before the run

- Any count other than **5,161 / 1,748** means the direction is not being read off the same baseline
  the published field was computed against, and the recomputation is not the one on the bill.
- **Any bill whose `bill_shock_pct` is negative** refutes the whole design: the point is that the
  field's contract (never negative) is now true by construction rather than by an `abs()`.
- **Any bill publishing `bill_shock_pct: 0.0` where the bill FELL** refutes the central choice. A
  measured zero there is the defect wearing the fix's clothes.
- **Any year's `avg_bill_shock_pct` falling** refutes P4 and would mean I had quietly chosen the
  flattering partition.
- A `bill_movement_pct` that does not recompute as `(total - baseline) / abs(baseline)` on every
  bill carrying a baseline refutes the claim that the published trio is checkable.

## What this commit explicitly does NOT do

1. **It does not split the shock by cause** (finding item 1). Causes (a) catch-up and (b) DD reset
   are labelled upstream and (c) price change has no marker at all. Separate, and it must come
   after this: a cause attached to a movement of the wrong sign would be a label on the wrong event.
2. **It does not touch `bill_shock_yoy_pct`, which still takes an `abs()`.** Same defect, second
   address, named here so it cannot be read as deliberate. It is gated behind `bill_shock_pct >=
   0.20` at its only consumer (`bill_shock_likely_seasonal`), so it is not reachable today in the
   direction that matters — which is why it is owed rather than bundled. Bundling it would move
   the seasonal labelling in the same window and neither change could be attributed.
3. **It does not model what a large DECREASE does to a household.** It plainly does something — an
   unexpected credit is half of definition A ("a credit or debit balance they do not understand") —
   but that is about the *payment and the balance*, not the bill, and no published source gives a
   magnitude for it. So `bill_movement_pct` is published and drives nothing: a named gap, not an
   invented coefficient. **The decrease is not deleted. 45.9% of the record is still there, under a
   name that says what it is.**
4. **It does not repair the direct-debit population's measure.** Still out of scope by instruction.

---

## OUTCOME — scored after the change, against the predictions above

*Scored by applying the new `saas.bill_generator.bill_movement` over the published artefact's own
11,255 baseline-carrying bills — the same method the predecessor prereg was graded by. Nothing above
this line was edited.*

| prediction | result |
|---|---|
| **P1** — 5,161 of 11,255 (45.9%) lose their shock | **CONFIRMED to the bill.** 5,161 / 11,255 = 45.9% |
| **P2** — events 3,161 → 1,748 | **CONFIRMED exactly.** |
| **P3** — 5,161 bills gain clarity, mean +0.0876, max +0.5 | **CONFIRMED** at the bill; the downstream contact/satisfaction/churn move was deliberately not predicted and is not claimed |
| **P4** — every year's `avg_bill_shock_pct` RISES | **CONFIRMED, ten years out of ten.** 2016 0.3081→0.4312 … 2022 0.4216→0.5752 … 2025 0.3397→0.4641 |
| **P5** — peak 465.3% → 501.5%, months>200% 7 → 18 | **CONFIRMED.** Peak moves 2017-02 (n=3) → 2019-02 (n=2) |

**Every named refuter was run and none fired.** Zero bills publish a negative `bill_shock_pct`.
Zero bills publish `0.0` where the bill fell. `bill_movement_pct` recomputes as
`(total − baseline) / abs(baseline)` on **all 11,255** — irreproducible on none.

**Nothing was refuted, and the unflattering prediction is the whole of the evidence.** Ten years of
`avg_bill_shock_pct` all rose and the worst published month got worse. Had removing 45.9% of the
events made the figures smaller I would have suspected the half I kept of having been chosen for its
answer.

**R15 — five mutations, five red against their named tests, null control green.** Applied to the
imported module object via a scratch pytest plugin outside the repo and never to a file, because a
full pytest run held this shared tree throughout. **M1** restores `abs()` on the numerator (the
defect itself) — reds 3. **M2** is `max(movement, 0.0)`, *the naive repair*, and the load-bearing
one: the one-line change that turns the sign tests green while publishing a measured zero for 45.9%
of the book — reds 3. **M3** returns `None` for everything that is not a *strict* increase, which
kills the flat-bill case and would replace a perfectly measured zero with "we cannot tell" — reds 1.
**M4** drops `abs()` from the denominator, the original outage inverted, so a rising bill reads
`None` and a falling one reads a shock — reds 1. **M5** lifts the world's fail-closed guard by
wrapping the consumer in `abs()` — the repair that looks like resilience — reds 1. **M0**, the null
control, is green.

### Two things found while doing this, neither fixed here

1. **The `avg_bill_shock_pct` name is now wrong in the same way the old measure was.** It is a mean
   over *bills that carry a shock*, and after this change that population is "bills that rose ≥ the
   threshold". The figure is honest; its name says "average bill shock" as though it spanned the
   book. Not renamed here because renaming a published field and moving what it measures in one
   window is unattributable — it is the next one-variable change.
2. **`monthly_ops` is thinner than it looks.** The worst month is now n=2 and 18 months read above
   200%. The bound from `8e395664e` covers this and is doing exactly its job, but a reader meeting
   "501.5%" needs the n beside it more than ever. Nothing to repair; worth saying in the record
   rather than discovering later.
