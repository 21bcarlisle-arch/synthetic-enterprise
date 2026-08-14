# FRAME — D27: where the scored company sits inside its own blind band

**Atom:** `D27_belief_window_saturates_on_this_book` (lane D_billing_metering, L0, `loop_stage: idle`)
**Stage:** FRAME only. **No BUILD code was written** — the atom is epoch-parked and BUILD-gated
(`EPOCH_GATING_AND_ATOM_AUTHORSHIP.md` Rule 1). This document is the settled design the BUILD draw
takes, and nothing here is landed in `tools/couple_w2_11_d5.py`.
**Date:** 2026-08-14 (worker tick, DISCOVER/FRAME lane)
**Origin:** `docs/staging/WORKER_FINDING_THE_BELIEF_MEMORY_SATURATES_ON_THIS_BOOK_2026-08-11.md`
(H27 Expert Hour #9)

---

## 1. What D27 owns, and what it does not

Three atoms now share this defect's surface, and the register itself already split them
(`DIMENSION_DRIFT_RESOLUTION`, belief entry; `SCENARIO_CONSTANT_CENSUS`, `DD_FAILURE_WINDOW_DAYS`):

| edge | owner | cause |
|---|---|---|
| saturates **below** (drift ≤ −371) | `D29_the_as_of_buffer_floors_the_memory_grid` | `AS_OF_BUFFER_DAYS` puts the youngest event 30d old |
| saturates **above** (drift ≥ −308) | `D30_the_belief_band_is_this_books_length` | the book stops at 92d because `N_PERIODS × PERIOD_SPACING_DAYS` |
| **where the SCORED COMPANY sits** relative to those edges — 308–309 days *inside* the blind band | **D27 (this atom)** | `DD_FAILURE_WINDOW_DAYS = 400`, the harness's chosen ORIGIN |

The census says it in one line: `DD_FAILURE_WINDOW_DAYS` is *"NOT A BAND CONSTANT — it is the ORIGIN
the band is measured from."* So **D27's reshape moves the origin, not the book.** Any option that
changes `N_PERIODS` is doing D30's work, and the measurement below shows it does not discharge D27
anyway.

## 2. What was measured (2026-08-14, n=300, seeds 7/11/23)

Method: the shipped `build_scenario` / `score_triad` / `measure_belief_window_resolution`, with the
candidate constants monkeypatched **in a scratch script only** (§8 — reproducible, nothing committed
to the harness). For A and B the drift sweep re-scores through the dimension's own shipped scorer;
for C/D/E only the population-side predictor and the outside-memory count were taken (R9: that is
the whole of what was observed for those three).

### A — SHIPPED TODAY (book 3 periods, window 400)

| seed | events | ages at `as_of` | headroom | saturated | `belief` | `belief_population_mix` |
|---|---|---|---|---|---|---|
| 7 | 102 | 30..91 | **+309** | yes | 0.1518987 | 0.0800000 |
| 11 | 96 | 30..92 | **+308** | yes | 0.1913580 | 0.1033333 |
| 23 | 113 | 31..92 | **+308** | yes | 0.1352941 | 0.0766667 |

Every drift in {−5, −2, −1, +1, +2, +5, +20, **+500**} publishes a **bit-identical** figure on all
three seeds, on both belief dimensions. **0 of 96–113 observed failures fall outside the company's
memory.**

### B — RECOMMENDED: score the company at the ORGAN'S OWN SHIPPED DEFAULT (book unchanged, window 90)

`PaymentObservationConsumer.__init__` ships `dd_failure_window_days: int = 90`
(`company/billing/payment_observation_consumer.py:386`). The harness builds it at 4.4× that.

| seed | headroom | saturated | events outside memory | `belief` | `belief_population_mix` |
|---|---|---|---|---|---|
| 7 | **−1** | no | 4 / 102 | 0.1708861 | 0.0833333 |
| 11 | **−2** | no | 4 / 96 | 0.2037037 | 0.1033333 |
| 23 | **−2** | no | 3 / 113 | 0.1411765 | 0.0766667 |

Re-scored drift sweep (`belief`):

| seed | −5 | −2 | −1 | **0** | +1 | +2 | +500 |
|---|---|---|---|---|---|---|---|
| 7 | 0.1962025 | flat | flat | **0.1708861** | 0.1518987 | 0.1518987 | 0.1518987 |
| 11 | 0.2098765 | flat | flat | **0.2037037** | 0.1913580 | 0.1913580 | 0.1913580 |
| 23 | 0.1823529 | 0.1529412 | 0.1470588 | **0.1411765** | flat | 0.1352941 | 0.1352941 |

Three readings off that table:

1. **The unbounded-above blindness stops being the scored company's problem.** The predictor puts
   saturation at drift +1/+2/+2 instead of −308: a company that never forgets is now a *different
   number*, on every seed. The residual edge (a company +3d out and one +500d out still read the
   same) is D30's book-length edge, untouched and correctly owned elsewhere.
2. **Today's published belief figure IS the never-forgets company's figure.** At window 90 the
   +500 column reads 0.1518987 / 0.1913580 / 0.1352941 — bit-identical to A's baseline. That is the
   finding's complaint stated as an equality rather than a caveat.
3. **The recency term becomes a measured number:** 0.0190 (seed 7, 12.5% of the shipped figure),
   0.0123 (11, 6.4%), 0.0059 (23, 4.3%). Under A it was a sentence in a comment.

**R13 differential, measured:** `ageing`, `detection` and `detection_latency` are bit-identical
between A and B on every seed (e.g. seed 7: 0.11296259117981663 / 0.014505119453924915 / 2.343137 in
both). The change reaches the two dimensions that read the parameter and nothing else.

### C/D/E — the options that move the BOOK instead

| candidate | events | ages | headroom | saturated | outside memory | verdict |
|---|---|---|---|---|---|---|
| C: 13 periods (annual book), window 400 | 396–431 | 30..302 | +98/+99 | **yes** | 0 | **does not discharge D27** — the scored company is still ~98d inside the band, at ~4× the scoring cost |
| D: 13 periods, window 90 | 396–431 | 30..302 | −211/−212 | no | **317–336 (78–80%)** | resolution bought by destroying the scenario's own subject (below) |
| E: 20 periods, window 400 | 596–665 | 30..449 | −48/−49 | no | 74–93 (12–14%) | works, but it is D30's lever, at ~6× cost, and leaves the origin arbitrary |

C is the decisive one: **lengthening the book does not fix this atom.** It moves the edge and leaves
the origin exactly as unjustified as it was.

## 3. The tension this design has to resolve, named

The 400 is deliberate and its reason is still in the constant's comment: *"Generous on purpose:
isolates the CHANNEL blind spot as the thing this scenario measures, rather than letting the
belief's own recency-decay window confound the reading."* That reason is sound, and it is in direct
conflict with resolution: a dimension can only resolve the memory parameter if some events fall out
of memory, which is exactly the confound the 400 removed. **You cannot have both properties in one
published number.**

The resolution is not to pick a side, it is to stop letting one number carry both jobs:

* the **scored** company holds the organ's own default, so the published figure is about a supplier
  anyone would recognise, and the memory parameter it reads is resolvable at 1–5 days;
* the **never-forgets** company (the old 400, reachable today as `organ_failure_window_drift_days`)
  stays as the declared counterfactual that isolates the channel term — and the *difference between
  them* is the recency contribution, published rather than assumed away.

Under D the confound is 78–80% of events and the scenario stops being about channels at all; under B
it is 3–4%, and it is a stated component instead of a design note. That difference is the whole
argument for B over D.

## 4. Recommendation (taken as the design; BUILD remains epoch-gated)

**Score the company at the organ's own shipped default, keep the book as D25 left it, and publish
the recency term as a component.** Concretely, for the BUILD draw:

1. `DD_FAILURE_WINDOW_DAYS` is **derived from `PaymentObservationConsumer.__init__`'s own default**
   (`inspect.signature`), never hand-typed as `90`. A hand-copy is the D20 defect one field over: if
   the organ's default moves, a hand-typed harness constant silently re-opens this gap.
2. The never-forgets company stays reachable and **book-derived** (D29's rule): the isolating
   counterfactual is `oldest observed failure age − window`, computed from the book, not the
   number 400.
3. Both belief dimensions publish a `recency_contribution` component — the scored figure minus the
   never-forgets figure — replacing the part of `belief_resolution_caveat` that currently says the
   dimension is saturated.
4. The register's `own_*` fields are re-derived on `book_memory_grid` at the new origin, and
   `own_debt_atom` for D27 is discharged. `own_saturation_atom_below` / `_above` stay with D29/D30;
   the census entry for `DD_FAILURE_WINDOW_DAYS` records the measured headroom.

**What this is not:** not a tuning (R12). The window is not chosen to move any output toward a
benchmark — it is set to the only non-arbitrary value available, the organ's own shipped default,
which was fixed as the candidate *before* B's figures were read. The published belief numbers move
as a consequence and are reported here rather than selected for. R13: harness scaffolding (which
company the harness builds), not a baseline-world fidelity claim and not director curriculum.

## 5. What moves when the BUILD lands

* `belief` +0.0190 / +0.0123 / +0.0059 on seeds 7/11/23; `belief_population_mix` +0.0033 on seed 7
  and ~0 on 11/23.
* Every consumer of those two figures: the coupled-gap ledger row for this pair, the caveat
  component on both dimensions, the CLI control block, and any published gap that quotes them. The
  BUILD must regenerate them (R2/R11 — the figure is not moved until the artefact carries it).
* Three dimensions and the world are unchanged, and that must be asserted, not assumed (§6.3).

## 6. Exit criteria for the BUILD, each with the mutation that proves it can fail (R15)

1. **The scored company is inside its own book.** A control asserting
   `measure_belief_window_resolution(scored_records, as_of)["saturated"] is False`.
   *Mutation:* set the window back to 400 → must fire.
2. **The origin is the organ's, not a constant.** AST/`inspect` control asserting the harness's
   window equals `PaymentObservationConsumer`'s default. *Mutation:* hand-type the number, then
   change the organ's default → must fire.
3. **Differential.** The three non-belief dimensions and the world fingerprint are bit-identical
   across the change. *Mutation:* let the knob touch `ageing` → must fire ("off its own organ").
4. **The recency component is real.** The published component equals the measured difference between
   the scored and never-forgets companies. *Mutation:* freeze the component → must fire.
5. **Per-dimension bands.** `belief_population_mix` resolves coarser than `belief` (seed 23: −1 moves
   `belief` alone). Each dimension declares its own band; a shared band is the wrong-population
   failure. *Mutation:* copy `belief`'s band onto the mix dimension → must fire.

## 7. What this FRAME does not settle

* **D30 (book length).** Under B the above-edge is +1/+2 — better placed but still short. When D30
  lengthens the book, the recency confound grows with it (E: 12–14%, D: 78–80%), and D30 must state
  what happens to the channel measurement at its chosen length. That is the handoff, in writing.
* **D29 (the `as_of` floor)** is untouched: the below-edge stays at −60/−61 under B.
* **The census lead from Hour #9** — `DD_FAILURE_WINDOW_DAYS` is not the only constant chosen to
  remove a confounder, and the census of such choices still does not exist.

## 8. Reproducing the measurement

Scratch script, run from the repo root with `PYTHONPATH=.`; it monkeypatches module constants and
writes nothing:

```python
from tools import couple_w2_11_d5 as C
BASE = C.DD_FAILURE_WINDOW_DAYS
def run(window, seed, drift=0, n=300):
    C.DD_FAILURE_WINDOW_DAYS = window
    try:
        recs, cons, book, as_of = C.build_scenario(
            n, seed=seed, organ_failure_window_drift_days=drift)
        return (C.measure_belief_window_resolution(recs, as_of),
                C.score_triad(recs, cons, as_of), recs, as_of)
    finally:
        C.DD_FAILURE_WINDOW_DAYS = BASE
# A: run(400, seed); B: run(90, seed); drifts as in the tables above.
# C/D/E additionally set C.N_PERIODS to 13, 13 and 20.
```
