# D28 — the detection register's population-side predictor

**Atom:** `D28_the_detection_gap_is_quantised_by_this_books_placement`
**Stage:** DISCOVER/FRAME pass 5, 2026-08-18 (worker tick, LANE 3 idle draw). Level stays 0,
`loop_stage` stays `idle`, nothing in `file_scope` touched. This document and the atom's
store note are the whole output.
**Claim labelling (R9):** everything below is `observed-with-evidence` unless a sentence says
otherwise. **R12:** no published number was moved, read or tuned — the sweeps score
counterfactual companies (`organ_terms_drift_days != 0`) plus the `k = 0` baseline, which is
the register's own probe.

---

## 0. What this closes

Residual item 1 of this atom — *"it owes the population-side PREDICTOR of these edges that
D25 has for ageing and D27 has for the belief window"* — has been open since the mint. Note 1
solved the negative side (`k* = days_late − grace`, exact on 95–98% of negatives). Note 3 took
the failure side, refuted both obvious candidates, and left it **UNIDENTIFIED**, with the
instruction that *"whoever builds the predictor must derive the failure side, not adopt either
candidate."*

It is derived here, and the two sides turn out to be **one formula**. It does not merely
predict the two edges: it reproduces **the entire published curve** — the headline and both of
its components, at every point of the book-derived grid — with no call to `score_triad`
anywhere.

---

## 1. The predictor

For one invoice `c`:

```
    k*(c) = min( as_of − due(c),  cover(c) − due(c) − 1 ) − grace + 1

    flagged(c, k)  =  dd(c)  or  k < k*(c)
```

* `grace` = `DEFAULT_RECONCILIATION_GRACE_DAYS` (5).
* `cover(c)` — **the observable cover date**: the first date at which the ledger's own
  allocation (`AccountLedger.allocate(as_of=d)`, remittance-else-oldest-first) reports this
  invoice settled. `None` (never covered inside the book) → the `min` has one term.
* `dd(c)` — the DD channel: an observed Bacs/rail failure whose `value_date` joins this
  period and whose `observed_at` is on or before `as_of`. Read off the consumer's own
  snapshot. **Measured invariant in `k` at all 109 drifts on all three seeds**, which is why
  it is a flat disjunct and not a second threshold.

Every input is population-side: the harness's truth records, the consumer's observed
failures, and the ledger the company itself holds. Nothing here reads a scored output.

### Why it is that expression, not note 1's

`age_open_items` dates an invoice at `issue + payment_terms_days`, and `build_scenario` issues
every invoice at `due − PAYMENT_TERMS_DAYS` from one expression. So a company drifted by `k`
puts its grace line exactly `k` days later than the harness's, and
`expected_collection_misses` fires at candidate date `d` iff `d ≥ due + k + grace` **and the
invoice is still open at `d`** — the fail-open guard the reconciliation detector was built
with. Note 1 modelled the first condition and not the second. The second is the whole failure
side: on a non-DD account the correlation id matches no invoice, so a later period's payment
allocates **oldest-first onto the failed invoice** (Clayton's Case, atom D8) and closes it
before the drifted company's window ever opens. That is why a failure can exit at `k = 16`
against a predicted 67 (note 3's own example): its cover date is the *next* period's payment,
21 days on, and `21 − 1 − 5 + 1 = 16`.

The negative side is the same formula specialised. A payment that arrives on time and is not
cross-allocated has `cover = due + days_late`, so
`k* = (days_late − 1) − grace + 1 = days_late − grace` — note 1's arithmetic, recovered rather
than replaced.

---

## 2. Evidence

### 2.1 Exit thresholds, n = 300, seeds 7/11/23 (the register's own population)

The family is nested — **0 re-entries** in 2,700 case-sweeps, re-asserted here rather than
carried from note 3 — so each case has a single exit threshold.

| | seed 7 | seed 11 | seed 23 |
|---|---|---|---|
| cases (`\|U\|`) | 900 | 900 | 900 |
| `S` / `N` / excluded | 102 / 586 / 212 | 96 / 595 / 209 | 113 / 574 / 213 |
| **reconciliation-channel `k*` predicted exactly** | **900 / 900** | **900 / 900** | **900 / 900** |
| union-channel exits predicted exactly | 831 / 831 | 839 / 839 | 817 / 817 |
| cases that never exit the union | 69 | 61 | 83 |
| …of which DD-channel-flagged | 69 | 61 | 83 |

The never-exiting cases are **exactly** the DD-flagged set, on all three seeds. Note 3's
"68%/64%/73% of `S` stays flagged at every drift" now has its mechanism: they are not held by
the reconciliation rule at all.

Both refuted candidates reproduce at their published accuracy — note 3's
`(as_of − due) − grace + 1` at 22/33, 18/35, 18/30, and note 1's `days_late − grace` at
568/586, 566/595, 563/574. Passes 1 and 3 are **re-verified unrepaired**.

### 2.2 The published curve, with no scorer call

Predicted `gap`, `missed_failure_rate` and `false_flag_rate` compared against `score_triad`'s
own output at every point of `dense_drift_grid`:

| book | grid | points agreeing | run partition |
|---|---|---|---|
| n=300 seed 7 | −20…+88 | **109 / 109** | — |
| n=300 seed 11 | −20…+88 | **109 / 109** | — |
| n=300 seed 23 | −20…+88 | **109 / 109** | — |
| n=600 seed 3 *(never swept by any prior pass)* | −20…+88 | **109 / 109** | identical |
| n=600 seed 41 *(never swept by any prior pass)* | −20…+88 | **109 / 109** | identical |

`gap` to float equality, both components to the published 6 d.p. On the two unswept books the
collapsed-run partition derived from the predictor is identical to the one derived from the
sweep, run for run.

Applying the register's **own** across-seed rule (a run is collapsed only if bit-identical on
every seed) to the predicted curves at n=300, seeds 7/11/23 reproduces the shipped
`_DETECTION_COLLAPSED_RUNS` tuple **bit for bit — all sixteen runs**.

Cost, on the same book: predictor **0.2 s** against the sweep's **62 s** (n=600), ≈250×. The
109-point sweep the register runs to declare its edges is arithmetic over one book.

---

## 3. What the predictor then says about the two declared edges

Predictor-only, across 25 books (n ∈ {150, 300, 600, 1200, 2400} × seeds {7, 11, 23, 3, 41}):

**`saturates_below = −6` on all 25.** It is `−(grace + 1)`, and it holds for any book
containing one invoice paid on its due date, because `cover = due` gives `k* = −grace − 1 + 1`.
That is a closed-form bound and a claim about an unswept live book. The register already calls
this edge `BOUND:the flag-everything set`; it now has the arithmetic behind the word.

**`saturates_above` is a property of the DRAW SIZE, not of the book's shape.** Per-seed upper
edge:

| | seed 7 | seed 11 | seed 23 | seed 3 | seed 41 |
|---|---|---|---|---|---|
| n=150 | 70 | 80 | 75 | 77 | 87 |
| n=300 | 80 | **82** | 75 | 77 | 87 |
| n=600 | 85 | 84 | 75 | 84 | 87 |
| n=1200 | 87 | 87 | 85 | 84 | 87 |
| n=2400 | *none* | 87 | 87 | *none* | *none* |

*none* = the reading is still moving at the grid's last point; there is **no upper saturation
inside the grid at all**. Across-seed intersected runs over seeds 7/11/23 shrink with the same
axis: 20 runs at n=150 (upper tail 80…88), 16 at n=300 (82…88, the shipped declaration), 13 at
n=600 (85…88), 9 at n=1200 (87, 88), and 4 at n=2400 with **no upper tail** — the last
collapsed run is (23, 24).

Nothing about the book's *shape* changed across that table: same one-cycle spread, same single
`as_of`, same grace line, same terms. Only how many customers were drawn.

The mechanism follows from the predictor. The upper edge is
`max over (S ∪ N) of k*`, and it is attained by a **non-DD failure that is never covered and
sits at the smallest cycle offset** — the oldest invoice in the book. Whether such a customer
exists is a draw. `saturates_below` is attained by *any* on-time payment, of which every book
has hundreds; `saturates_above` by the single luckiest case, of which a small book may have
none.

---

## 4. The consequence that ships, and is staged as a separate finding

`det.components["recon_saturation_band_days"]` is the literal pair
`(ORGAN_QUERY_GRID["flagged_via_reconciliation"]["saturates_below"], […]["saturates_above"])`
= `(-6, 82)`, stamped onto **every** detection result — the offline `measure()`, the live
triad, and the published `docs/observability/coupled_gap_ledger.json`, where it sits today as
`[-6, 82]`.

On `measure()`'s own default book (n = 4000), the **shipped scorer** publishes **seven distinct
figures** between +82 and +88:

| k | +82 | +83 | +84 | +85 | +86 | +87 | +88 |
|---|---|---|---|---|---|---|---|
| gap | 0.136214 | 0.136626 | 0.137037 | 0.137449 | 0.138272 | 0.138683 | 0.139095 |
| `flagged_size` | 885 | 883 | 882 | 881 | 879 | 878 | 877 |

The component says everything above +82 is one figure.

`measure_organ_query_grid_saturation` defaults to `n_customers = 300` — the draw size the
declaration was authored at — so the control re-derives the edge exactly where the register
already answered. That is **this atom's own founding observation** (*"the register was asked
exactly where it had already answered"*), recurring on the **population-size axis** instead of
the grid axis, on the register D28 itself re-derived. Filed as
`docs/staging/WORKER_FINDING_THE_SATURATION_EDGE_IS_A_PROPERTY_OF_THE_DRAW_SIZE_2026-08-18.md`,
BLOCKING in `D_billing_metering`. **QUEUED, not fixed on sight** (SELF-INTERRUPT DISCIPLINE).

---

## 5. What this leaves for the builder

**Item 1, the predictor — CLOSED as a measurement, OPEN as code.** Nothing in the repo
computes it. What it is worth is stated so the next tick weighs it rather than re-deriving it:
it turns the register's declarations from a 109-point re-scoring into arithmetic over one book
(250× cheaper), and it is the only form in which those declarations can be checked on a book
that was **not** the one they were authored on — which is the whole of §3.

**Item 3, the reshape — its target is now checkable before it is built.** Note 3 restated the
acceptance test as *"the exit-threshold multiset restricted to `S ∪ N` must be contiguous
across the swept interior."* That multiset is now a closed-form function of the book, so a
candidate reshape can be scored from its own construction with no scoring run at all. Three
constraints fall straight out, and the first two are not in the atom's brief:

1. **A DD-flagged failure contributes no threshold whatever.** 68%/64%/73% of `S` is
   unreachable by any terms reshape. Only non-DD failures can move the
   `missed_failure_rate` direction at all.
2. **The lower half of the interior is a step, not a spread.** Every uncovered on-time
   negative lands on the single threshold `−grace`, and 94.9%/92.1%/96.0% of `N` exits at
   `k = −5` exactly (note 3, re-measured). Spreading `N` needs *cover dates* spread across the
   interior — i.e. cross-allocation timing — not more invoices beside the line.
3. **Growing the book is not the reshape, but it dominates the reading.** 12 of the 16
   declared collapsed runs disappear between n=300 and n=2400 with the book's shape untouched.
   Any reshape evaluated at n=300 against a declaration measured at n=300 will be crediting
   itself with an effect the draw size already had. *(Inferred, R9 — not a claim that the
   reshape is unnecessary; a claim about what its evidence must control for.)*

**Not attempted here:** the live book (`LivePaymentTriad`, 114 monthly periods) was not
measured, so §3's table is a statement about the offline scenario's shape only. The predictor
should hold there by construction — nothing in it assumes three periods — but that is
`inferred`, not observed.
