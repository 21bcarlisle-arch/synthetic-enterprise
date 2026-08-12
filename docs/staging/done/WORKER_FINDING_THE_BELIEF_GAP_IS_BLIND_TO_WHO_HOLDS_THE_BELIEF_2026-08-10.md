# WORKER FINDING — the belief gap is blind to WHO holds the belief

**Severity:** BLOCKING · **Lane:** H_harness

**Date:** 2026-08-10 · **Found by:** worker tick running Expert Hour #3 on `H27_payment_belief_gap` (2→3)
**Advances:** `D19_belief_gap_is_distribution_only`
**Verdict:** **HELD AT L2.** L3 means "no major flaws". A third was measured, in a third published headline.
**R12:** nothing was tuned. The belief gap is unchanged — `0.07125` before and after this tick.

**Discharged:** `tests/tools/test_couple_w2_11_d5.py::test_the_aggregate_scoring_contract_is_differential_not_a_blanket_ban`, `tests/tools/test_couple_w2_11_d5.py::test_a_lying_aggregate_declaration_fails_the_control`, `tests/tools/test_couple_w2_11_d5.py::test_a_declared_dimension_with_no_labels_raises_rather_than_skipping`, `tests/tools/test_couple_w2_11_d5.py::test_the_belief_headline_moves_under_a_permutation_since_d19` — each dimension declares what it cannot see and the declaration is measured against the shipped scorer, a lying declaration fires the control, and D19's reshape has since landed so the belief headline itself now moves under the permutation. 4 green, 2026-08-12.

## Why the Hour ran now

Hour #1 (2026-08-08/09) found the detection headline was an `as_of` artefact and counted one error
direction; it minted `D11`. Hour #2 (2026-08-09) found the instrument published one named quantity as
two different numbers; it minted `D16`. Both blockers landed at L2 and `depends_on` emptied, so this
is the third pass on the corrected instrument.

Two candidate leads were checked first and **both were already closed** — recorded here because "I
looked and it was handled" is the outcome that keeps a register honest:

- `missed_failure_rate` is **exactly 0.0000** on every seed, so the "balanced error" headline is
  precisely `false_flag_rate / 2`. Already known: `test_the_miss_direction_can_still_fire` names it,
  explains that expected-collection reconciliation catches every truly-failed invoice at `due+grace`,
  and mutation-proves the direction can fire by deleting the reconciliation channel.
- Ever-flagged being blind to the company *un*-knowing a case is filed as its own class
  (`WORKER_FINDING_EVER_FLAGGED_IS_BLIND_TO_UN_KNOWING`), closed at a measure inside D8.

## The finding — the BELIEF headline cannot see who holds which belief (observed, R9)

`belief_gap` is a total-variation distance between two **population distributions** of arrears
severity. `flagged`-style set membership never enters it. So permuting the company's per-case beliefs
among cases — destroying every correct per-case assignment while leaving the label multiset alone —
changes the published number by **exactly zero**.

Measured, 4000 customers, seed 7. Nothing re-simulated; only which account holds which belief:

| | per-case agreement | published belief gap |
|---|---|---|
| the real company | 0.9287 | 0.07125 |
| beliefs permuted | **0.6432** | **0.07125** |

Identical to machine precision. Seeds 11 and 23 agree at n=600. The degenerate strategy that scores
exactly what the real company scores is not "flag everything" — it is **"get the population MIX right
and every INDIVIDUAL wrong."**

### Why it survived the sweep that closed this class four times

D11/D12/D14/D15 closed the dual-degenerate class across all four **detection** dimensions, and
`DETECTION_DIRECTION_CONTRACT` is keyed to *detection scorers*. The belief dimension has a different
scorer and a different degenerate, so no register reached it.

### Why it hid in plain sight

On a book whose belief errors run **one way** — this company under-calls severity (`normal` 443→485,
`watch` 114→87, `high` 36→25) — total-variation distance is *arithmetically equal* to the per-case
disagreement rate:

```
seed  7 :  gap 0.0700   per-case disagreement 0.0700
seed 11 :  gap 0.1033   per-case disagreement 0.1033
seed 23 :  gap 0.0733   per-case disagreement 0.0733
```

The number therefore **reads as a per-case error rate, and numerically is one**, while being a
different quantity that a permutation leaves untouched. The equality is a coincidence of the error
direction, not a property of the metric — and it is exactly why nobody looked twice.

## What was done this tick (HARDEN, not the reshape)

- **Stamped at source.** `background.gap_metric.belief_gap` now carries
  `BELIEF_GAP_PERMUTATION_CAVEAT` in its `baseline` and `note`, so the caveat lands on **all three**
  pairs that call it — W2_11↔D5, W2_4↔C6, `couple_cohort` — not only where it was found (the D6/D11
  precedent).
- **The direction it cannot see rides beside the score.** `n_cases` / `n_cases_misassigned` /
  `per_case_disagreement_rate`, computed from the caller's own per-case labels. `None`, never `0`,
  when a caller cannot supply them: a `0` there is the strongest possible claim ("the company got
  every case right") handed out free to a caller that simply did not measure.
- **The limit prints with the headline** at the CLI and in `bel.note`, with the witness interpolated
  from the measurement rather than typed into a sentence once.

### The class control (R10 — the class, not the instance)

```
a dimension's DECLARED per-case sensitivity must match what a PERMUTATION actually does to it
```

Declared per dimension in `AGGREGATE_SCORING_CONTRACT`, and **measured** by actually permuting the
company's per-case labels and re-scoring through each dimension's **own shipped scorer** (R15
independence — a control carrying its own copy of the TV formula could not fail if the shipped one
changed):

| dimension | declared aggregate-only | gap moves under permutation? | verdict |
|---|---|---|---|
| belief | yes | **no** (0.0713 → 0.0713) | **BLIND — the defect** |
| ageing | no | yes (0.1787 → 1.1675) | per-case, as declared |
| detection | no | yes (0.0143 → 0.5020) | per-case, as declared |

**Differential on purpose.** A blanket "no dimension may be permutation-invariant" would fire on
`belief` as a *design fact* (a distribution distance is supposed to be one) and teach everyone to
skip the gate — the `DIMENSION_AS_OF_CONTRACT` lesson. What the control tries is the **declaration**.

**R15, mutating the SOURCE (not the test's own copy):**
- flip `belief`'s declared `is_aggregate_only` to `False` → fires (and the differential assertion
  fires too: every dimension lands on one side, so the register is a blanket rule in disguise).
- make `permute_belief_labels` a no-op → three tests fire, including the vacuity guard.
- a declared dimension whose labels the scorer stops publishing **raises** rather than dropping out
  of the sweep — an unreachable register entry reads exactly like a clean one.
- `gap_before` must reproduce the published headline for every dimension, or the control is scoring
  a copy of the instrument rather than the instrument.

### Caught by the new control on its first run

Rendering detection truth as `failed`/`ok` against belief `flagged`/`clear` made per-case agreement
**0 on every case by construction**, so the probe's vacuity bit read "the permutation changed
nothing" when it meant "these two label sets never agree in the first place" — that dimension would
have been silently unprobed. Both sides now share one vocabulary. The guard caught its own probe.

## What was NOT done, and why

The belief dimension's definition is untouched. Giving it a per-case shape moves a published number
on all three pairs that call `belief_gap`, and R12 forbids reshaping a metric because its value looks
wrong — the value is fine; what was missing is the direction it cannot see and the declaration that
it cannot see it. `D19_belief_gap_is_distribution_only` carries the reshape, with the acceptance
criterion already measurable (the permutation sweep must come out MOVED) and the shape known twice
over: copy detection's set-membership scoring, or D7's per-case denominators.

## Tests

7 new in `tests/tools/test_couple_w2_11_d5.py`; 143 green across every file touching `gap_metric` and
the pairs that call `belief_gap` (`test_couple_w2_11_d5.py`, `test_gap_metric.py`,
`test_live_payment_triad.py`, `test_couple_w2_4_c6.py`, `test_couple_cohort.py`), plus 49 green on the
maturity-map contract after the D19 mint.
