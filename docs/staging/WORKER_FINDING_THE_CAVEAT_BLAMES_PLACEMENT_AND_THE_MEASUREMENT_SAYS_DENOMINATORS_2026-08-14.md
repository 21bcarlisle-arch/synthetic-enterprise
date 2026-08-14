# WORKER FINDING (QUEUED) — the detection caveat blames the book's placement, and the measurement says it is the denominators

**Severity:** BLOCKING · **Lane:** D_billing_metering

**Found by:** the D28 LANE-3 DISCOVER/FRAME tick, 2026-08-14, testing the one thing note 1
of that atom's record left flagged as NOT ESTABLISHED — whether the interior collapsed
runs are predicted by the book's `days_late` multiset. They are not, and the reason is a
population the caveat never mentions. Queued per SELF-INTERRUPT DISCIPLINE: the fix lives
in `tools/couple_w2_11_d5.py`, which is the `file_scope` of an atom at `loop_stage: idle`,
so this tick may not write it.

**Why BLOCKING rather than LATENT:** the false clause is not in a comment. It is in
`detection_resolution_caveat()`, which is stamped into `det.note` AND
`det.components["drift_resolution_caveat"]` — the component the ledger writer, the live
wiring and the dashboard read. A reader of the published component is told something about
the instrument that is measurably false, so a published claim is wrong even though every
published NUMBER is right. Not self-scored down to keep the lane open
(`background/finding_severity.py`'s own warning).

## Observed, with evidence

Sweep: `build_scenario` + `score_triad`, n=300, seeds 7/11/23, the whole book-derived grid
`dense_drift_grid` = **-20..+88 (109 points, 108 adjacent pairs)**. For every drift `k` the
flagged set `D`, the truth set `S`, the never-flaggable set `N` and the published
`detection` gap were captured. `S` and `N` are invariant in `k` (asserted every point).

### 1. The flagged family is NESTED, so every reading is one CDF read-off

`|D|` is monotone non-increasing across the whole grid — 900 → 69 / 61 / 83 — and **every
case that ever leaves `D` leaves exactly once and never re-enters** (831 / 839 / 817 cases,
zero re-entries on any seed). So each invoice has a single exit threshold `k*`, and

    missed_failure_rate = |{s in S : k*(s) <= k}| / |S|
    false_flag_rate     = |{n in N : k*(n) >  k}| / |N|

The register's entire content is therefore the multiset of exit thresholds restricted to
`S ∪ N`. Nothing else can move the figure.

### 2. The figure moves iff the set movement touches `S ∪ N` — 324/324, no exceptions

| seed | adjacent pairs | pairs where the flagged SET moves | pairs where the FIGURE moves | set moves, figure still |
|---|---|---|---|---|
| 7 | 108 | 74 | 39 | 35 |
| 11 | 108 | 76 | 36 | 40 |
| 23 | 108 | 70 | 33 | 37 |

The predicate `gap moves ⟺ (D_k Δ D_{k+1}) ∩ (S ∪ N) ≠ ∅` agrees on **108/108 pairs on all
three seeds, zero disagreements**, and there is no pair anywhere where the figure moved on
an empty delta.

### 3. Every one of those 112 silent movements lands 100% in the EXCLUDED band

For all 35 + 40 + 37 pairs where the set moved and the figure did not, the symmetric
difference is **entirely inside `U − S − N`**: 0 cases in `S`, 0 in `N`, on every pair, on
every seed. That band is the D10/D11 exclusion — an invoice paid late but past its grace
date, which the company was RIGHT to chase — and it is **212 / 209 / 213 invoices, 23.6% /
23.2% / 23.7% of the book**.

### 4. So the interior of the sweep is dense with crossings, and the headline's own populations are barren in it

Distinct `k` at which some invoice crosses the company's grace line, over the interior
between the two saturated tails (`-5..+81`, 87 integers):

| seed | `k` with an EXCLUDED crossing | `k` with an `S ∪ N` crossing | interior barren of `S ∪ N` |
|---|---|---|---|
| 7 | 63 (spanning +1..+82) | 39 | 48 of 87 |
| 11 | 63 (spanning +1..+79) | 36 | 52 of 87 |
| 23 | 61 (spanning +1..+75) | 33 | 54 of 87 |

And the two counted populations are structurally unable to fill it:

* **`N` is a step function.** 556 / 548 / 551 of the negatives — **94.9% / 92.1% / 96.0%** —
  exit at `k = -5` exactly, and only 17 / 26 / 11 of them (2.9% / 4.4% / 1.9%) exit anywhere
  above `k = 0`. The false-flag direction is one cliff, not a gradient.
* **`S` mostly never exits.** Only 33 / 35 / 30 of the failures leave the flagged set
  anywhere inside the grid; **69 / 61 / 83 of them (68% / 64% / 73%) stay flagged at every
  drift the book can be asked about.**

The whole interior resolution of a published headline therefore rests on ~33 case-exits out
of a 900-invoice book — **3.7% / 3.9% / 2.7%**.

## What is false, quoted

`DIMENSION_DRIFT_RESOLUTION["detection"]["why"]`, shipped:

> "In between the reading is quantised rather than continuous (fourteen interior
> collapses), **because the number of invoices sitting BESIDE the grace line at any one
> distance is small.**"

Measured false. 212 invoices sit past the grace line at **63 distinct distances covering
almost every integer in the interior**. What is small is not the invoices beside the line
but the invoices beside the line **that this headline's denominators count**. The stated
cause is placement; the measured cause is the exclusion.

`detection_resolution_caveat()`'s head, stamped into `components`:

> "This headline is SET MEMBERSHIP, so a company's terms error moves it **only where that
> error carries an invoice across the grace line.**"

Measured false as an inference licence. An invoice crosses the line at 74 / 76 / 70 of the
108 steps and the number moves at 39 / 36 / 33. Crossing the line is **necessary and not
sufficient** — the invoice must also be in `S` or `N`. A reader entitled to run the sentence
backwards ("it did not move, so nothing crossed") is wrong at 35 / 40 / 37 steps.

## What it re-scopes, and the acceptance test it fixes

Note 1 of the D28 record stated the reshape's acceptance test as "a book whose settle-delay
distribution has no gaps across the swept span". **That test is satisfiable without moving
the figure at all** — the gaps would fill with excluded cases, which is exactly what this
book already does at 63 distinct distances. The corrected test, which follows from §1:

> the reshape must make the exit-threshold multiset **restricted to `S ∪ N`** contiguous
> across the swept interior — not the book's settle-delay distribution, and not the flagged
> set's change points.

That is a materially different build. It needs failures whose ages relative to `as_of` span
the interior (today 68% of them never exit at all) and negatives spread across their grace
distance (today 95% sit on one point) — not merely more invoices beside the line.

## Two options, and the recommendation

1. **Correct the two sentences to name the denominator** (small, in-scope at the next touch
   of this module): the `why` states the exclusion as the cause, and the caveat's head says
   crossing the line is necessary-not-sufficient and names the `S ∪ N` restriction. Cheap,
   and it stops the false backwards inference immediately.
2. **Publish the barrenness as a number**, i.e. carry `interior k with an S∪N change point /
   interior k` (39/87) beside the collapsed runs, so the caveat's claim is re-derived per
   book rather than asserted — the D19/D20/D22/D23/D25 rule this caveat already follows for
   its edges.

**Recommendation: both, in that order, whenever D28 or D31 next opens for BUILD** — 1 is the
correction, 2 is what stops it decaying again, and 2 alone would leave a false sentence
shipped beside a true number. Neither is done here; this atom is `loop_stage: idle`.

## Not established, flagged rather than asserted (R9)

The **population-side predictor** D28 owes (its residual item 1) is now half-solved and
half-open, and the open half must not be read as done:

* `N` side: `k* = days_late − grace` is **exact on 568/586, 566/595, 563/574 (96.9% /
  95.1% / 98.1%)** of negatives. Note 1's arithmetic, confirmed on the honest grid.
* `S` side: **not solved.** `k* = (as_of − due) − grace + 1` is exact on only 22/33, 18/35,
  18/30. The mismatches all exit far EARLIER than predicted (e.g. 16 against a predicted 67)
  and all sit in 3-period accounts, which suggests an account-level attribution effect; an
  account-newest-due cap was tried this tick and made it **worse** (30%), so the mechanism is
  unidentified. Whoever builds the predictor must derive it, not adopt either candidate.

R12: no published number was moved, read or tuned. The sweep scored counterfactual companies
(`organ_terms_drift_days != 0`) plus the `k = 0` baseline, which is the register's own probe;
nothing was written to any artefact.
