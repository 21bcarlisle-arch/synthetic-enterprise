# H27 Expert Hour #14 — the caveat travelling with the number stated a different number's resolution

**Date:** 2026-08-11 · **Atom:** `H27_payment_belief_gap` (HARDEN, self-refill draw 2→3)
**Subject:** `tools/couple_w2_11_d5.py` · **Reshape minted as:**
`D32_the_latency_headline_cannot_attribute_its_two_knobs` (L0)
**Held at L2.** Fourteen Hours, fourteen defects, and #14 changed the instrument again.

---

## The lead this took

Hour #13 left three. Lead 1:

> **The route now proves every knob reaches the shared rule. Nothing proves the CAVEATS do.**
> Three registers now stamp resolution caveats at source; whether every published dimension
> carries the caveat of every knob that reaches it is the same coverage question one layer up,
> and it has never been asked.

Asking it needs the reach grid first, and the reach grid had never been measured either — each
register knows its own knob and says nothing about the other two.

## The reach grid, measured (n=300, seeds 7/11/23, every run identical on all three)

Three counterfactual company knobs × five published dimensions. **Seven of the fifteen cells
move.**

| | detection | detection_latency | belief | belief_pop_mix | ageing |
|---|---|---|---|---|---|
| `organ_terms_drift_days` | **MOVES** | **MOVES** | inert | inert | **MOVES** |
| `organ_reconciliation_drift_days` | **MOVES** | **MOVES** | inert | inert | inert |
| `organ_failure_window_drift_days` | inert | inert | **MOVES** | **MOVES** | inert |

Nine cells are inert and are now *measured* inert. That is the half of this control that had no
owner at all: an unmeasured cell reads exactly like an inert one, and nothing anywhere would have
fired if a future change had let the memory knob reach the ageing report.

## The finding, and it is two failures in one dimension

### 1. WRONG SUBJECT — the caveat's number belongs to a sub-reading

`ORGAN_QUERY_GRID["recon_lag_days"]` declares `reported_days_for_a_one_day_drift: 1.0`, and it is
**true** — of the reading the entry names in its own `headline_key`:
`mean_lag_days_without_dd_channel`, the DD-channel-DELETED counterfactual. Measured, that
sub-reading moves exactly 1.000000 per drift day.

The figure the caveat is **stamped on** is `detection_latency.gap` = `mean_lag_days`. It does not.

| drift | published `mean_lag_days` (s7) | register's `…without_dd_channel` (s7) |
|---|---|---|
| −1 | 2.019608 | 4.0 |
| 0 | 2.343137 | 5.0 |
| +1 | 2.666667 | 6.0 |
| +2 | 2.990196 | 7.0 |

**Step for a one-day-slower detector:** published **+0.323530** (s7), **+0.364583** (s11),
**+0.265487** (s23) — against the **1.0** the caveat put in the reader's hands.

A reader converting a movement in this headline into days of company error with the stamped
number **understates it about threefold**. And the ratio is not a constant to correct by: it is
the recon arm's share of the latency population — a case whose earliest knowledge came from the
DD channel does not move when the reconciliation detector does — so it is a property of the
book's payment-method mix and varies 0.27–0.36 across three seeds of one scenario.

The register was never dishonest about itself. `headline_key` says plainly which reading it
measures. What nobody checked is that the *caveat* crossed from that reading to a different one
without the number changing.

### 2. MISSING KNOB — the second company error that moves the same figure

`DIMENSION_DRIFT_RESOLUTION["detection_latency"]` has declared `organ_terms_drift_days`
`in_causal_path: True` since D28, with a measured band and a saturation edge at −19d. **None of it
reached the published figure**: both stamped caveats were about the reconciliation detector.

Worse than an omission — measured across `−3/−1/+1/+3/+5` on every seed, **the two knobs are
bit-identical in this headline**. A supplier holding payment terms *k* days long and one whose
detector fires *k* days late publish the same latency number. So the dimension whose entire
subject is *how late does the company learn a payment failed* cannot say **which company error
made it late**, and a reader given only the recon caveat attributes the whole reading to a
detector fault it may have no part in.

## Closed at the class (R10)

* **`PUBLISHED_FIGURE_CAVEAT_CONTRACT`** — keyset DERIVED both ways (`published_dimensions` ×
  `counterfactual_knobs`), so an undeclared cell **RAISES**: the fallback IS the defect, the
  D29/D31 rule one layer up. Every cell declares moves/inert and is MEASURED each run; every
  moving cell owes a caveat component that a real `score_triad` must actually **render** (naming
  one is not stamping one — Hour #11's *a lead is not a control*); and any cell declaring a step
  is checked against the **published headline's own measured step**, not against the register
  sentence that supplied it. Vacuity-guarded on the probe itself: a knob that had silently stopped
  drifting the company would otherwise certify every inert cell in its column.
* **`predict_published_latency_step_days`** — the corrected number, derived from this book's own
  coverage witnesses with no sweep, no seed and no re-scoring (the D25/D30 population-side
  predictor), AST-asserted to read neither scorer nor register, and cross-checked against the
  sweep on all three seeds. `None`, never `0.0`, on an empty population — a zero there would read
  as "the headline is inert", the strongest claim handed out for free.
* **The caveat now states BOTH numbers and which reading each belongs to**, at source, so it lands
  on every coupled pair calling the scorer rather than the one whose Hour found it (the D6/D22
  precedent). `published_headline_step_days` rides beside it as a component, because the ledger
  writer, the live wiring and the dashboard read `components` and never the prose.
* **`latency_terms_resolution_caveat`** — the terms limit this figure never carried, interpolated
  from the register on every call.

## R15 both ways

The control fires, by name, on: the **pre-Hour step** (1.0 republished as the headline's); a
**moving cell with no caveat** (the pre-Hour terms cell); a **caveat the consumer never renders**;
a moving cell **declared inert**; an inert cell **declared moving**; an **undeclared cell**
(raises); a **missing** and an **orphan** dimension (both raise); and an **inert probe** —
exercised with a memory drift inside the band D29/D30 measured saturated, so the knob is real and
the probe is not.

## R12

**No published number moved.** The detection gap, the latency mean and both belief figures are
bit-identical before and after. What moved is what the instrument admits about itself.

## Why still L2

Fourteen Hours, fourteen defects, none predicted by the Hour before it, and this is again the tick
that changed the instrument — the reputation-of-the-old-instrument problem in its purest form.
Hour #4's stated-in-advance criterion of **two consecutive clean Hours** has still not been
approached.

## Hour #15 leads, in order

1. **The reshape itself is D32 and it is unbuilt:** a latency measure that separates a terms error
   from a detector error. Until it exists, the published number does not attribute, and whether
   that is acceptable at L3 is a judgement this build declined to make on the promoter's behalf.
2. **The step check reached exactly one cell.** `published_step_component` is declared on
   `detection_latency`/recon and nowhere else, because it is the only cell whose reading is
   day-linear either way. The other six moving cells have caveats whose numbers are *bands and
   edges*, and nothing checks those against the published figure the way the step now is — the
   same coverage question one level further in.
3. **Carried forward, still untaken:** the interior collapses have no owner of their own (Hour
   #11's lead 1, twice deferred); and Hour #8's two — the pinned generated value
   `assert c["n_recon_detected_undated"] == 0`, and whether the other dimensions' normalisation
   notes have the same gap between what they DENY and what they ESTABLISH.
