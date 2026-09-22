**Severity:** RECORDED · **Lane:** G_data_learning · **Epoch:** 3 · **Atom:** none (LANE 0
DELIVERY, direction not an atom) · **Class:** figures_on_a_superseded_clock

**Knowledge:** consumed `docs/observability/settlement_ceiling_slope_20260921.json` (landed at
`c4bee75e3`) and the LIVE guest via `background.resource_headroom.sample()`. No number was
invented; every figure below is either read from the artefact or solved from it, and the one
judgement call (which fit to take) is named and defended.

# The settlement ceiling is a consequence of its curve now, and the band that defended 1,200 was a superseded ruler

**2026-09-21, delivery seat (worker tick), Lane 0.**
Claim: `the-settlement-ceiling-can-move-now-that-its-curve-has-landed`.

---

## What changed

`simulation/net_new_acquisition.SETTLEMENT_CUSTOMER_YEAR_BUDGET`: **1,200.0 → 1,330.0**, fitted from
`docs/observability/settlement_ceiling_slope_20260921.json` (landed at `c4bee75e3`) against the live
guest, not picked.

## The premise, re-measured before starting

The drawn item's cited commit `c4bee75e3` is an ancestor of `origin/main` — the ENABLING commit, and
the item is about the work it enables, so being landed is the precondition rather than the spend.
What made the premise worth re-asking is something else: `c4bee75e3` did not only land the curve, it
also wrote a decision into the constant's note — **"NOT MOVED, and deliberately"** — so the drawn
instruction ("move it off its historical value") was already answered in the negative by the seat,
same day, in the same file.

**That answer is wrong, and the reason is one sentence of it.** Point 3 of that section defends 1,200
because it "sits inside the whole admissible band (1,194.6–1,312.3)". The band's LOWER edge, 1,194.6,
is the ceiling the probe's menu reports **for a ninety-minute cadence** — the interval
`publish_freshness.PUBLISH_CADENCE_SECONDS` superseded on 2026-09-04 at 604,800s. At the interval the
director actually named there is no lower edge: the time leg is 154,227 customer-years, 117x the
memory leg, so exactly one bound exists and 1,200 sits 10% below it for no reason but its own
history. "It sits inside the band" was a coincidence against a ruler already replaced.

The rest of point 3 — the band is ±10%, the gain is precision not coverage — is an argument against
spending the effort. It is not an argument for the number. The effort was one afternoon.

## The fit

x-values: the artefact's own `clean` flags decide which figure each point contributes.

| pt | budget | committed cy | `campaign_record_agrees` | x used | peak RSS (MB) | wall (s) | refused |
|---|---|---|---|---|---|---|---|
| 1 | 1,200 | 1,197.0 | true  | **1,197.0** (its own) | 5,507.4 | 1,499.6 | 419 |
| 2 | 2,000 | 1,995.2 | false | **2,000.0** (budget seen) | 8,504.7 | 2,666.5 | 260 |
| 3 | 2,800 | 2,799.3 | false | **2,800.0** (budget seen) | 12,501.8 | 4,591.5 | 79 |
| 4 | 3,400 | 3,135.5 | true  | held out — see below | 13,920.9 | 5,296.0 | **0** |

Points 2 and 3 had another writer touch `book_growth_campaign.json` mid-run, so their committed
customer-years are not their own; their `customer_year_budget_seen` and `peak_rss_mb` are. Both
refused wins, so both ran taut against their budget, and x = budget is sound to the 0.25% the clean
points show between budget and committed. Point 4 refused NOTHING — 500 of 500 booked — so 3,400 is
not a point about this ceiling at all; it is the funnel's whole demand, and it is used only as a
held-out check.

**The curve is convex**, which is what moves the answer: 3.733, 4.996, 4.230 MB per marginal
customer-year across the three intervals. The probe's own `recommendation` prices the ceiling off the
1,197→3,135.5 **chord** (4.340 MB/cy) — cost incurred at three thousand customer-years charged
against the marginal customer-year at twelve hundred — which on a convex curve understates the
ceiling. That is why 1,312.3 is not copied.

    live guest (background.resource_headroom.sample(), 2026-09-21T20:51Z): total_mb 24,032.1
    allowed peak RSS = 0.25 × 24,032.1                  = 6,008.0 MB
    x = 1,197.0 + (6,008.0 − 5,507.4) / 3.7326          = 1,331.1 customer-years

| fit | ceiling |
|---|---|
| local secant 1,197→2,000 (**taken**) | **1,331.1** |
| quadratic least squares, three usable points | 1,344.2 |
| exact quadratic through points 1–3 | 1,352.4 |
| linear least squares | 1,353.3 |
| the artefact's chord (what `recommend()` published) | 1,312.3 |

The local secant is taken because on a convex curve it is a strict upper bound on marginal cost in
[1,197, 2,000] and therefore a **lower** bound on the ceiling — the conservative member of the
family. The exact quadratic's held-out prediction at point 4 is 14,478 MB against 13,921 observed:
4.0% high, conservative in the same direction. **1,330.0** is that fit rounded down to the nearest
ten.

## Which leg binds, at the value chosen

* **MEMORY.** Implied peak RSS 5,507.4 + 133.0 × 3.7326 = **6,004 MB = 24.98% of the 24,032.1 MB
  guest.** Spent almost exactly to the probe's 25%-of-TOTAL share.
* TIME. Implied run 1,693s + the publisher's worst measured gate 1,205s = 2,898s = **0.48% of the
  604,800s weekly interval.** Does not bind and cannot be made to at this cadence.
* SUPPLY. The funnel's whole demand is 3,135.5 cy, so the book is still engine-bound and going
  further is a memory question, not a commercial one.

## The declared weight, which this constant does not own

`resource_headroom.CLASS_WEIGHTS_MB["sim_run"]` = 13,824 MB. The implied 6,004 MB is 43% of it, so it
is **not outgrown and is not re-declared**. The probe's 13,920.9 MB peak that did exceed it was taken
at budget 3,400, a budget nothing runs at. Re-declaring it *downward* to the implied peak would be
the same error in the other direction: `weight_drift` re-derives this class from systemd's own record
(live reading 5,734.4 MB peak across 7 runs in −24h) and the same journal recorded 23,164 MB on
2026-09-04. A declared weight is a ceiling over the worst run, not a fit to the median.

## What it buys, stated so it is not over-read

About +11% of settled book (~1,197 → ~1,330 customer-years at the same funnel): a larger chosen
sample, tighter arms. It does **not** reach the 3,163.9 customer-years `what_would_settle_the_sign`
needs, and point 4 establishes that no ceiling can — the world tops out at 3,135.5. The gain is
precision, not the sign.

## Pre-registered, before the next producer run

Peak RSS **6,004 MB ± 4%** (5,764–6,244), wall clock **~1,693s**, and **no `resource_headroom`
episode** opened by it. Outside that band the FIT is wrong rather than the box, and the constant
returns to 1,200 rather than being re-justified. This is registered here before the run rather than
after, which is the only thing that makes it a prediction.

## The downstream that disagreed, and what was done about it

* `tools/generate_book_growth_data.py::engine_bound_basis` — the published page said "the memory leg
  is measured and slack", "STILL NOT YET KNOWN", "ONE clean point ... no slope exists", and quoted a
  3,952.4 MB peak. Every one of those went false when the curve landed. Rewritten in the same commit:
  memory is the binding leg, the ceiling is stated, and the artefact path is in the sentence.
* `site/test_the_book_is_bounded_by_compute_reaches_the_reader.py` — its control pinned the literal
  `"NOT YET KNOWN"`, i.e. to today's answer, so it would have gone RED for the page becoming more
  honest. **Re-keyed to the property**: the basis either says the ceiling is unknown, or it states
  one AND names an artefact that is in a commit. Both failure modes are reachable.
* **NOT touched, deliberately:** `simulation/premise_population.py` and
  `tools/generate_value_arms_data.py` — a live lane was writing both at 21:22/21:24 repairing the
  published memory bound.

## Owed after this

1. `tools/generate_value_arms_data.py` carries prose literals "1,312 customer-years against the
   budget's **1,200**" and "slack of 1.09x". At 1,330 the slack is ~1.00x and the budget is no longer
   1,200. Left for the lane that holds that file; it is a stale literal, not an inverted conclusion —
   the direction ("memory binds, slack is thin") is now MORE true, not less.
2. `site/data/book_growth.json` carries the old basis sentence until the next producer cycle
   regenerates it. The door control reads the producer, not the artefact, so it is honest in the
   meantime; the published bytes are one cycle stale by construction.
3. `docs/design/A46_THE_PRICED_MENU_2026-08-30.md` §"What I am doing without you" tells the
   director the budget is being *left* at 1,200. That is now superseded and the doc should carry a
   dated line saying so — **not done here because another lane has A46 dirty in this tree**, and a
   pathspec commit would have carried their edit inside mine.
4. The interval sentence higher in the constant's note ("an interval preference nobody has stated")
   is **not deleted** despite the drawn item asking for it: the section immediately below quotes and
   corrects it in place, dated, and deleting a quoted claim leaves a correction with nothing to
   correct. Kept corrected rather than kept true.
