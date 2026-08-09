# WORKER FINDING — the H27 Expert Hour ran, and the detection headline failed it twice

**Date:** 2026-08-09 · **Found by:** worker tick running the Expert-Hour pass on `H27_payment_belief_gap` (2→3)
**Advances:** D11_detection_gap_is_recall_only
**Verdict:** **HELD AT L2.** L3 means "no major flaws". Two were measured, both in the published headline.
**R12:** nothing was tuned. The detection gap is byte-identical — `0.09547325102880659` before and after this tick.

## Why the Hour ran now

The 2026-08-08 tick held H27 at L2 for two reasons and mechanised the hold as a `depends_on`. Both were
discharged: D7 reshaped the ageing dimension, D10 gave detection a latency shape. The 2026-08-09 note then
released the block and left an explicit instruction rather than taking the promotion:

> a promoter must run the Expert-Hour pass on the CORRECTED instrument, not on the reputation of the old one.

The D10 finding doc handed over one named question with it: whether the detection dimension *should* be an
ever-detected set rather than a believed-at-`as_of` set "belongs to whoever takes H27 to L3". This is that pass.
The answer to the handed-over question is **yes, and it is worse than a design preference — it is a live defect.**

## Finding 1 — the headline is an `as_of` artefact (observed, R9)

`truth_set` is `result == 'failed'`: a settled fact about a payment, which does not move with the clock.
`flagged_set` is the company's belief held **at** `as_of`. So the number moves when nothing it measures does.

Same `records`, same `consumer`, nothing re-simulated — only the date the scorer asks on:

| `as_of` | +0 | +7 | +14 | +30 | +60 | +90 |
|---|---|---|---|---|---|---|
| **detection gap** | 0.0725 | 0.0870 | 0.0942 | 0.1087 | **0.1232** | 0.1232 |
| detection_latency | — | — | — | — | *unmoved* | *unmoved* |

**+70% over 60 days with the company standing still.** The mechanism is D8's (Clayton's Case): a case detected
on time is later *un*-flagged when an ambiguous non-DD payment is allocated oldest-first onto the failed invoice.

The sting is that this was already solved **one dimension over**. `detection_latency` was deliberately built on
an EVER-KNEW population for exactly this reason, and its test is even named
`test_detection_latency_is_the_real_thing_and_not_an_as_of_artefact` — sitting directly beside a headline that is one.
The fix was applied to the neighbour and the headline was left behind. That is the third instance of this class
(D7's prevalence scalar, D10's retired `detection_latency_days` key), which is why it is closed at the class below.

## Finding 2 — the headline counts one error direction

`detection_gap` is `1 - |S∩D|/|S|`. `flagged_set` enters only through the intersection, so **enlarging it can
never make the score worse**, and the dual degenerate scores perfectly:

```
real company            : detection gap = 0.0725
flag NOBODY (stated g0) : detection gap = 1.0000
flag EVERYTHING         : detection gap = 0.0000   <-- PERFECT SCORE
...on a population where only 138/1200 = 11.5% truly failed
```

The published `baseline` names only `"flag nobody (all detectable harm missed -> gap = 1)"`, which reads as
though 0 were earned. It is not: 0 is what a perfect detector *and* an indiscriminate one both score.

What the company actually does, measured:

| seed | detection gap | false flags | as % of all flags | rate over truly-current |
|------|---------------|-------------|-------------------|-------------------------|
| 7    | 0.0725        | 101         | **44.1%**         | 0.0951 |
| 11   | 0.1515        | 115         | **50.7%**         | 0.1077 |
| 23   | 0.0811        | 108         | **44.3%**         | 0.1027 |

Every one is an invoice that truly **succeeded**. And seed 7's `101 of 1062` is *literally the same 101/1062*
that D7's `overstated_arrears_rate` publishes on the ageing dimension — the wrongful-dunning exposure. **The
error direction was already visible one dimension over, and invisible here.**

It had even been *noticed*. `tests/background/test_live_payment_triad.py` carried this comment:

> so flagged can EXCEED true (the reconciliation path also picks up mis-allocated/late-boundary invoices). The
> honest invariant is the RESIDUAL detection gap staying strictly positive, never that belief undercounts truth.

An anomaly seen, explained, and explicitly not asserted on. That is where it hid for a fortnight.

## What was done this tick (HARDEN, not the reshape)

The reshape moves three published numbers and is queued as its own atom (SELF_INTERRUPT_DISCIPLINE — the machine
is not blocked). What landed is everything that makes the limits impossible to read past:

- **Stamped at source** (the D6 precedent). `background.gap_metric.detection_gap` now carries
  `DETECTION_GAP_DUAL_DEGENERATE` in its `baseline` and `note`, so the caveat lands on **all three** coupled
  triads that call it — W2_11↔D5, W2_5↔C7, W2_8↔C10 — not only where it was found.
- **The other direction rides beside the score.** `n_false_flags` / `false_flag_rate`, on the truly-negative
  denominator (D7's rule — a whole-population rate would re-import the class-balance dependence D7 exists to
  remove). `None`, never `0`, when the universe is unknown: a `0` there is the strongest possible claim
  ("no false flags at all") handed out for free.
- **Both limits print with the headline** — at the CLI, in `det.note`, and in the LIVE ledger note the Proof
  door reads, with the witness interpolated from the measurement rather than typed into a sentence once.

### The class control (R10 — the class, not the instance)

```
if a dimension's TRUTH side is invariant under as_of, its published gap MUST be too
```

Declared per dimension in `DIMENSION_AS_OF_CONTRACT`, and **measured** by actually sweeping `as_of`:

| dimension | truth moves? | gap moves? | verdict |
|---|---|---|---|
| detection | no | **yes** | **ARTEFACT — the defect** |
| detection_latency | no | no | invariant, as it should be |
| belief | no | no | invariant, as it should be |
| ageing | **yes** | yes | legitimate — an invoice really does age |

It is **differential on purpose**. A blanket "nothing may move with `as_of`" would fire on ageing, where moving
is correct — a false positive that jams the gate teaches everyone to skip the gate.

**R15, mutating the SOURCE (not the test's own copy):**
- flip `detection`'s declared `gap_is_as_of_invariant` to `True` → fires: *"declared gap_is_as_of_invariant=True
  but the gap went 0.0909 -> 0.1590 over 60 days"*
- strip the fix-atom name from its exemption → fires the named-debt assertion.
- Plus a vacuity guard: both sides of the differential must be genuinely exercised, or a pass proves nothing.

### A coverage hole found on the way

`background/live_payment_triad.py::measure_and_write` — **the path that actually publishes** the gap into
`coupled_gap_ledger.json` for the Proof door — had **no test reaching it**. Every word of the note it stamps was
unexercised; a rotted sentence or a `KeyError` would have surfaced only in a live `run_phase2b`. Now covered.

## What was NOT done, and why

The detection dimension's own definition is untouched. Changing it moves a published number, and R12 forbids
reshaping a metric because its value looks wrong — the value is fine, what was missing is its other half and its
invariance. `D11_detection_gap_is_recall_only` carries the reshape, with the acceptance criterion already
measurable (the `as_of` sweep must come out flat) and the shape already known twice over: copy
`detection_latency` for the population, copy D7 for the two directions.

## Tests

38 in `tests/tools/test_couple_w2_11_d5.py`, 7 in `tests/background/test_live_payment_triad.py`; 130 green
across every file touching `gap_metric` and the three triads that call `detection_gap`.
