# FRAME — D29: the reading date and the company's memory are one variable

**Atom:** `D29_the_as_of_buffer_floors_the_memory_grid` (lane D_billing_metering, L0, `loop_stage: idle`)
**Stage:** FRAME only, **third pass** on this atom. **No BUILD code was written** — the atom is
epoch-parked and BUILD-gated (`EPOCH_GATING_AND_ATOM_AUTHORSHIP.md` Rule 1). Nothing in `file_scope`
(`tools/couple_w2_11_d5.py`, `tests/tools/test_couple_w2_11_d5.py`) is touched.
**Date:** 2026-08-14 (worker tick, LANE 3 DISCOVER/FRAME draw)
**Prior passes:** two records in `docs/design/simplifications/D29_the_as_of_buffer_floors_the_memory_grid.yaml`
(2026-08-13, Findings 1–5). This pass takes the one lead pass 2 left explicitly NOT-ESTABLISHED —
*"that a set of per-reading figures should be COMBINED into one published number, and how"* — and in
taking it withdraws pass 2's own load-bearing conclusion.

Everything below is `observed-with-evidence` unless labelled otherwise (R9).

---

## 0. Hygiene

Measured in a detached worktree at HEAD `e71e6ac7f` (`git worktree add --detach`). Both `file_scope`
paths are **clean at HEAD this tick** (`git status --porcelain` empty on both) — the first pass on
this atom for which that is true; passes 1 and 2 each recorded the module dirty or the map's shared
index carrying another lane's staged hunks. n=300, seeds 7/11/23 throughout, shipped `build_scenario`
/ `score_triad` / `measure_belief_window_resolution`. A company memory `W` is built through the
declared counterfactual `organ_failure_window_drift_days` (never a monkeypatch — the D20 rule); a
reading buffer `b` is a shift of the `as_of` date passed to the scorer, never an edit to
`AS_OF_BUFFER_DAYS`.

Grid: `W ∈ {1,3,4,5,6,10,29,30,398,399,400,401}` × `b ∈` 21 buffers (the shipped `[30]`, pass 2's
span-spaced seven `[5,66,127,188,249,310,340]`, and a MONTHLY fourteen `range(5,402,30)` — the
real-world twin's own cadence, a collections pack run monthly over the book) = **252 scored cells per
seed, 756 in total**, plus 12 targeted pairs in §1.

## 1. FINDING 6 — both belief figures are functions of `W − b` ALONE, and that is the whole atom

An event counts iff `age ≤ W`, and every age at a reading is `b + offset` where `offset ∈ [0, span]`
is a property of the book. So `counted ⟺ offset ≤ W − b`. **Complete over the grid: 217 distinct
`W − b` families per seed, 756 cells, ZERO violations** — every pair of cells sharing `W − b`
publishes bit-identical `belief` and `belief_population_mix`.

Checked on informative values rather than the degenerate 0.5, 12 pairs, all three seeds, all
**bit-identical to 12 dp**:

| reading of the SCORED company | shipped reading of a DRIFTED company | seed 7 | seed 11 | seed 23 |
|---|---|---|---|---|
| `W=400, b=340` | `W=90,  b=30` | 0.170886075949 | 0.203703703704 | 0.141176470588 |
| `W=400, b=365` | `W=65,  b=30` | 0.354430379747 | 0.327160493827 | 0.329411764706 |
| `W=400, b=395` | `W=35,  b=30` | 0.481012658228 | 0.462962962963 | 0.482352941176 |
| `W=400, b=310` | `W=120, b=30` | 0.151898734177 | 0.191358024691 | 0.135294117647 |

The other three dimensions place the invariance: `ageing` is a function of **`b` alone** (one distinct
value per buffer across all 12 windows, every seed), and `detection` / `detection_latency` are
invariant to both (**one** distinct value across all 756 cells per seed). So the belief pair reads a
difference, the ageing dimension reads a date, and the detection pair reads neither.

**THE CONSEQUENCE, AND IT IS PASS 2's CONCLUSION WITHDRAWN.** Pass 2's Finding 5 measured that a SET
of readings breaks the `floor + headroom` identity and exhibited, at `b=340`, "the first measurement
in this atom's line where either belief figure moves at the memory the scored company actually
holds." Those numbers are all correct. What they are is **the shipped drift sweep in different
clothes**: reading the scored company at buffer `b` IS reading the declared counterfactual company at
`organ_failure_window_drift_days = -(b - 30)`, a knob this harness has shipped since D27. And the
value it exhibits — seed 7, 0.170886075949 — is, to 12 dp, **the number D27's own FRAME published for
its recommendation B** (`docs/design/D27_BELIEF_WINDOW_RESHAPE_FRAME.md` §2B: window 90, seed 7,
`belief` 0.1708861). The multi-reading instrument adds no information about this company's memory
that the harness did not already have; it re-labels a counterfactual company as a reading date.

Pass 2 was right that pass 1's universal ("only a change to `event_age_span` moves the conserved
sum") is false. It is false, and the move that falsifies it is another atom's reshape wearing this
atom's clothes.

## 2. FINDING 7 — a reading resolves the memory parameter only where the memory is BINDING, and where it binds the figure is starved

Because `counted ⟺ offset ≤ W − b`, "the parameter binds" and "the parameter is resolvable" are the
**same condition**: unless `0 ≤ W − b ≤ span`, every event is on one side and a 1-day memory error
moves nothing. Measured across the monthly fourteen at the scored `W = 400` (`frac` = share of this
book's observed failures still inside the company's memory at that reading; `dbelief` = the larger of
|gap(400)−gap(399)|, |gap(401)−gap(400)|):

| seed | readings with `frac = 1.000` | their `dbelief` | resolving readings | their `frac` | their `belief` | their `dbelief` |
|---|---|---|---|---|---|---|
| 7 | 12 of 14 (`b = 5..335`) | **0.000000000, exactly** | `b=365`, `b=395` | 0.549, 0.088 | 0.354430, 0.481013 | 0.006329, 0.006329 |
| 11 | 12 of 14 | **0.000000000, exactly** | `b=365`, `b=395` | 0.583, 0.115 | 0.327160, 0.462963 | 0.006173, 0.006173 |
| 23 | 12 of 14 | **0.000000000, exactly** | `b=365`, `b=395` | 0.540, 0.035 | 0.329412, 0.482353 | 0.011765, 0.005882 |

The no-skill baseline for this figure is **0.5** (`g0`, "every severity-blind rule"). So the two
readings in a monthly year that can tell a 1-day memory error apart are the two at which the company
has forgotten 45% and 91% of its book and is publishing a number **71%–96% of the way to no skill**.
That is the atom's own defect — an indiscriminate degenerate standing in for a resolution measurement
— reappearing as the *price* of resolution rather than as an oversight.

**So aggregation is not a free choice, it is the defect's delivery mechanism.** Mean over the reading
set, `W = 400`, against the single shipped fed reading:

| seed | shipped fed reading | span-7 mean | monthly-14 mean |
|---|---|---|---|
| 7 | 0.151899 | 0.154611 (+1.8%) | **0.189873 (+25.0%)** |
| 11 | 0.191358 | 0.193122 (+0.9%) | **0.220459 (+15.2%)** |
| 23 | 0.135294 | 0.136134 (+0.6%) | **0.173950 (+28.6%)** |

A published belief gap a quarter higher than today's, moved entirely by scoring the same company at
dates where its memory had expired, is not a resolution improvement — it is the starved company's
figure mixed into the fed company's.

**The dilution, stated honestly rather than overclaimed.** The mean *does* still resolve at 4dp:
`published_reading_epsilon("belief") = 5e-05`, the monthly-14 mean moves 4.52e-4 between `W=399` and
`W=400` (≈9 epsilons), and a single resolving reading moves 6.33e-3 (≈127 epsilons). The signal is
divided by the number of readings, so the mean crosses below the reader's own precision at ~127
monthly readings (seed 7). Today's fourteen are above it. The objection to the mean is the **+25%
level shift**, not an unreadable difference.

## 3. The one configuration that is fed AND resolving — and it is already owned

`frac` falls linearly in `W − b`, so the fed-and-resolving reading is the one whose window cuts at the
book's OLD edge: `W − b ≈ span`. On this book that is `b = 340` at `W = 400` — `frac ≈ 0.98`, `belief`
0.170886, resolving. Which is, by Finding 6, **exactly D27's recommendation B** (score the company at
the organ's own shipped default of 90 days against the book as D25 left it). D27 framed it, owns it,
and reached it from the origin side.

There is therefore no reshape left on this axis that is D29's. Pass 1 concluded D29 must wait behind
D30's span; pass 2 withdrew that on the multi-reading finding; this pass shows the multi-reading
finding to be D27's move re-parameterised. **The reshape is D27's; what remains D29's is a control and
a caveat.** That is a scope REDUCTION for this atom and it is stated as one rather than absorbed
quietly.

## 4. Recommendation (taken as the design; BUILD remains epoch-gated)

**Re-scope D29 from RESHAPE to INSTRUMENT-INVARIANCE CONTROL.** For the BUILD draw:

1. **Land the `W − b` invariance as a control, not as prose.** Assert that both belief dimensions are
   functions of `W − b` alone, and that `ageing` is a function of `b` alone — over a small declared
   grid, re-scored, not predicted. This is the sentence three passes have each rediscovered from
   scratch (MAKE IT STICK: convert policy to mechanism or accept it evaporates), and it is the reason
   every candidate in this atom's `name` is a translation.
   *R15 mutation:* give `_arrears_risk_belief` any explicit `as_of` dependence (a recency weight) and
   the control must fire; make the ageing bucket rule read the window and it must fire the other way.
2. **Stamp the floor in the caveat as a LABEL, not a bound.** The amnesia floor is `b − 1` in
   `W`-space and moves one-for-one with `AS_OF_BUFFER_DAYS` (pass 1's identity, complete over 421
   buffers in pass 2). The caveat should say the floor is the harness's reading date wearing the
   company's units — which is what makes "a supplier who forgets after three weeks" and "a supplier
   who never remembers" one number here.
   *R15 mutation:* freeze the floor at a hand-typed 29 and move `AS_OF_BUFFER_DAYS` → must fire.
3. **Refuse the aggregate.** Any figure published from more than one reading must assert every
   contributing reading has `frac == 1.0` (fed). *R15 mutation:* include `b=365` in a published mean →
   must fire (measured: +25.0% on seed 7).
4. **Record the redundancy in the map** — D29's resolution is DELIVERED by D27's origin move, not by
   any value of `AS_OF_BUFFER_DAYS` and not by any set of reading dates. The atom's `name` still says
   the reshape "moves every published belief figure on this pair"; pass 1 measured that false (only
   `ageing` moves under a buffer change) and staged
   `WORKER_FINDING_THE_FLOOR_AND_THE_HEADROOM_ARE_ONE_CONSTANT_2026-08-13.md`. This pass adds the
   second half: the part that IS true is true of D27's edit.

## 5. Exit criteria for the BUILD, replacing pass 2's four

1. **UNCHANGED (pass 2, criterion 1).** `amnesia_floor_window_days + headroom_days` has moved off
   `DD_FAILURE_WINDOW_DAYS − span − 1`. Invariant over 421 buffers × 3 seeds, so a reshape that leaves
   it alone resolved nothing.
2. **REPLACED.** Pass 2's criterion 4 — *"at least one company memory error resolved AT the scored
   company's own W=400"* — is **greenable by another atom's move**: it is satisfied by reading at
   `b=340`, which Finding 6 shows to be D27's recommendation B relabelled, with nothing of D29's
   changed. A criterion another atom discharges is not this atom's criterion. It becomes: **a resolved
   memory error at `W=400` AND every published reading `frac == 1.0`** — the two halves that Finding 7
   shows are in tension, in one test.
3. **NEW.** The invariance control of §4.1 exists and fires under its named mutation. This is the
   atom's actual deliverable.
4. **UNCHANGED (pass 2, criterion 3), now complete rather than sampled.** `ageing` re-certified
   alongside the belief pair, and `detection` / `detection_latency` asserted bit-identical — measured
   here as one distinct value across all 756 cells per seed.

## 6. What this FRAME does not settle

* **Whether D29 should be closed into D27 outright.** The evidence says its reshape is redundant; the
  scope call on a minted atom is recorded here and queued rather than taken on sight
  (SELF-INTERRUPT DISCIPLINE). The three items in §4 are real work whichever way that lands.
* **D30's span.** A book whose span is comparable to the company's memory is the only thing that makes
  a reading fed AND resolving anywhere except at the old edge. That remains D30's lever, unmeasured
  here.
* **NOT ESTABLISHED (R9):** whether the belief pair's `W − b` invariance also holds on a live
  `run_phase2b` population. Everything above is this offline book, n=300, seeds 7/11/23.

## 7. Reproducing the measurement

Scratch scripts, run from a detached worktree with `PYTHONPATH=.`; they write nothing to the repo:

```python
from datetime import timedelta
from tools import couple_w2_11_d5 as C
BASE, SHIP = C.DD_FAILURE_WINDOW_DAYS, C.AS_OF_BUFFER_DAYS   # 400, 30

def read(seed, W, b, n=300):
    recs, cons, _book, as_of0 = C.build_scenario(
        n, seed=seed, organ_failure_window_drift_days=W - BASE)
    as_of = as_of0 + timedelta(days=b - SHIP)
    s = C.score_triad(recs, cons, as_of)
    ages = sorted((as_of - r.due_date).days for r in recs if r.result == "failed")
    frac = sum(1 for a in ages if a <= W) / len(ages)
    return s["belief"].gap, s["belief_population_mix"].gap, frac

# Finding 6: read(7, 400, 340) == read(7, 90, 30) on both figures, to 12dp.
# Finding 7: [read(7, 400, b)[2] for b in range(5, 402, 30)] -> 1.0 x12, then 0.549, 0.088.
```

R12: no published number was tuned and none was written to any artefact. Every figure above was scored
inside a throwaway worktree to find out which of them this reshape reaches. R13: harness scaffolding
(which company the harness builds, and on what date it reads it) — not a baseline-world fidelity claim
and not director curriculum.

**STATUS: DISCOVER/FRAME only.** `level_current` unchanged at 0, `loop_stage` unchanged at `idle`,
`provenance` unchanged at `proposal`. `simplifications_count` 2 → 3 (the map is clean in the tree this
tick, unlike passes 1 and 2, so the count is folded here rather than deferred).
