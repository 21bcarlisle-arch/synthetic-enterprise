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

---

# PASS 4 — 2026-08-17: the invariance is real, its evidence was mostly singletons, and it holds because the belief organ is blind to when the company was told

**Stage:** FRAME only, **fourth pass**. **No BUILD code written**; nothing in `file_scope`
(`tools/couple_w2_11_d5.py`, `tests/tools/test_couple_w2_11_d5.py`) touched — both **clean at HEAD**
this tick, as in pass 3. Measured in a detached worktree at HEAD `b7349bee0`. n=300, seeds 7/11/23,
shipped `build_scenario` / `score_triad`, no monkeypatching: `W` moves through the declared
counterfactual `organ_failure_window_drift_days`, `b` through the `as_of` passed to the scorer.

This pass takes §6's remaining NOT-ESTABLISHED lead — *"whether the belief pair's `W − b` invariance
also holds on a live `run_phase2b` population"* — because that invariance is, after pass 3's scope
reduction, **this atom's sole remaining deliverable** (§4.1). Everything below is
`observed-with-evidence` unless labelled otherwise (R9).

## 8. FINDING 8 — Finding 6's grid could not have failed on 72% of its own cells

Finding 6 reports "**complete over the grid: 217 distinct `W − b` families per seed, 756 cells, ZERO
violations**". An invariance of the form *"cells sharing `W − b` agree"* is only testable on a family
of **size ≥ 2**; a singleton family is a cell with nobody to disagree with. Re-deriving pass 3's own
declared grid (`W ∈ {1,3,4,5,6,10,29,30,398,399,400,401}` × its 21 buffers):

| | |
|---|---|
| cells per seed | 252 |
| distinct `W − b` families | 217 |
| family-size histogram | **{1: 182, 2: 35}** |
| cells that cannot violate (singletons) | **182 (72.2%)** |
| real within-family comparisons | **35 per seed, 105 in total** |

So "756 cells, ZERO violations" is **105 comparisons**, and the number 756 measures the cost of the
sweep rather than its power. The 217-families figure, quoted as evidence of coverage, is in fact the
symptom: 217 families over 252 cells is near-total singleton-ness.

This is not a claim that Finding 6 is wrong. It is a claim that its stated evidence did not weigh what
it appeared to weigh — the same shape as the memory entry *a blocked test can stand for a whole
battery*, and R15's "controls must be able to fail" applied to a measurement rather than a control.

## 9. The invariance re-measured on a grid where every cell has a partner — and it HOLDS

Grid designed so that no family is a singleton: `Δ = W − b ∈ {20, 40, 60, 90}` × `b ∈ {0,1,2,3,5,10,30}`,
3 seeds = **84 cells, 12 families of 7, 72 real comparisons**, and deliberately extended **down to
`b = 0`**, below pass 3's minimum of 5.

**Result: 12 of 12 families invariant** — one distinct `belief` and one distinct
`belief_population_mix` per family, all three seeds. Sample (seed 7, Δ=90): `belief` =
0.151898734177 and `mix` = 0.080000000000 at every one of `b = 0,1,2,3,5,10,30` against
`W = 90,91,92,93,95,100,120`.

**Finding 6's conclusion stands, on evidence that can now fail.** That is the useful half of this
pass for the atom's deliverable.

## 10. FINDING 9 — it holds because the belief filter cannot see when the company was told, and the same scorer already knows better

The filter behind both belief figures (`company/billing/payment_observation_consumer.py:613,617`):

```python
dd_failures = [
    f for f in self._dd_failures.get(account_id, [])
    if f.value_date <= as_of and (as_of - f.value_date).days <= self._dd_failure_window_days
]
```

Both clauses read **`value_date`** — the collection date. Neither reads **`observed_at`**, the
bank-feed REPORT date, which `payment_seam_adapter` lags by a per-case draw of
`0..ARUDD_NOTIFICATION_LAG_DAYS`. Measured on this book: DD lags are **{0, 1, 2} days**, `n_dd` =
69/61/83 on seeds 7/11/23, and `as_of₀` sits **29 days** past the newest `observed_at` on all three
seeds (30/30/31 days past the newest `value_date`).

**So a reading date is not a knowledge date.** At `b = 0`, exactly **one** counted DD failure per seed
has `observed_at > as_of` — the belief counts a failure whose own bank-feed report lands after the
date the harness claims to be reading on. It is counted at every `b`, because the filter never looks.

**The counterfactual is decisive.** Recomputing the counted set under a knowledge-honest filter
(adding `f.observed_at.date() <= as_of`) over the §9 grid:

| seed | shipped counted set | knowledge-honest counted set |
|---|---|---|
| 7 | 1 distinct value in **4 of 4** families | 2 distinct values in **4 of 4** |
| 11 | 1 distinct in 4 of 4 | 2 distinct in 4 of 4 |
| 23 | 1 distinct in 4 of 4 | 2 distinct in 4 of 4 |

**12 of 12 families break.** The exclusion depends on `b` alone, never on `W − b`, so it cannot be a
function of the difference. The `W − b` invariance is therefore not a structural truth about arrears
belief — **it is an artefact of the organ being blind to `observed_at`.**

**And the same scorer already applies the honest rule one dimension over.** `score_triad`, on the
DETECTION dimension (`tools/couple_w2_11_d5.py:9414-9425`):

> *"A report landing after `as_of` is not yet knowledge: witnessed, never counted. POINT-IN-TIME FIX
> (D11, 2026-08-09): the not-yet-knowable case is now excluded from `flagged_via_dd_channel` as well
> … which is the detection dimension's own small version of a point-in-time blindfold breach."*

It counts them into `n_dd_observed_after_as_of` and drops them. **D11's fix reached the detection
dimension and not the belief dimension** — one of two sites, the shape the memory entry *the reader
precision was read at one of two sites* names. The field is available to the company: its own ledger
is explicitly bitemporal (`valid_time=value_date, transaction_time=observed_at`,
`payment_observation_consumer.py:461-462`), so the belief organ holds both legs and filters on one.

**NOT ESTABLISHED (R9), and it is a design call this pass does not take:** whether the *company* organ
SHOULD filter on `observed_at`. A real supplier's "arrears view as at a past date" is a bitemporal
query and the honest answer may be that the harness should stop asking retroactively rather than that
the organ should change. What IS established is that the two dimensions of one scorer disagree about
what the company knew, and that nothing currently states which is intended.

## 11. THE CONSEQUENCE — pass 3's deliverable §4.1 is a ratchet against its own repair

Pass 3 §4.1 says: land the `W − b` invariance as a control, with

> *R15 mutation: give `_arrears_risk_belief` any explicit `as_of` dependence (a recency weight) and
> the control must fire.*

**That named mutation is the repair.** Adding the `observed_at` clause is precisely "an explicit
`as_of` dependence", and §10 measures that it breaks the invariance on 12 of 12 families. A control
whose specified mutation is the correct fix does not protect the figure — it fails the day someone
fixes the defect, and its red is indistinguishable from a regression. This is R15 read the other way:
the control CAN fail, but what it fires on is the cure.

**§4.1 is therefore re-specified** (pass 4 replaces it):

> Assert the `W − b` invariance **together with its precondition** — that the belief filter is
> knowledge-blind — so the pair states *"these figures are functions of `W − b` BECAUSE the organ
> ignores `observed_at`."* When the organ is made knowledge-honest, the control's own precondition
> goes false and the assertion is retired by the fix rather than reddened by it.
> **R15 mutations, both directions:** (i) make `_arrears_risk_belief` knowledge-honest → the
> precondition clause must fire and the invariance clause must NOT be read as a regression;
> (ii) leave the organ blind and perturb `ageing` to read `W` → must fire.

§4.2 (stamp the floor as a label) and §4.3 (refuse the aggregate) are **unchanged** by this pass.

## 12. FINDING 10 — the live lead, answered: untestable there, for two structural reasons

Pass 3's §6 lead is **resolved as NOT-APPLICABLE rather than left unmeasured.** `run_phase2b` was not
run this tick; the answer comes off the live path's own code and its published artefact.

**(a) There is no live belief figure to be invariant of.** The live ledger entry
`docs/observability/coupled_gap_ledger.json → W2_11_payment_behaviour_source` publishes
`metric: "detection"`, `gap: 0.0833907649896623` (measured_at 2026-08-17T21:50:21Z, run commit
`99dba222c`). The belief pair rides **only as prose inside that entry's `note`** — by design:
`live_payment_triad.py:731` says the companion gaps ride inline because `::`-suffixed ledger keys
"would wedge the publish gate". Live values, read out of the note: `belief balanced error 0.1818`,
`belief_population_mix 0.2105`, `per-case disagreement 0.2105 (4 of 19)`.

**(b) The live company is pinned deep inside the saturated region, deliberately.**
`_RUN_SPANNING_WINDOW_DAYS = 6000` (`live_payment_triad.py:119`) is what the live consumer's
`dd_failure_window_days` is constructed with (`:528`) — i.e. live `W = 6000` against a run the same
comment sizes at ~3650 days. `saturated = window >= oldest` is then True with ~2,350 days of headroom
(**inferred** on the ~3650, which is the module's own comment, not a figure measured here;
**observed** on the constant and the wiring). Every longer memory publishes one number — the exact
collapse D27 named at this edge, sitting on the live figure.

So the invariance is neither confirmed nor refuted live: the live path has no published belief gap,
and its memory parameter is inert by construction. **The atom's deliverable is offline-only, and that
should be stated in the control rather than discovered by the next pass.**

**Consequence, and it is filed rather than fixed** (SELF-INTERRUPT DISCIPLINE): `_RUN_SPANNING_WINDOW_DAYS`
is the THIRD confounder-removing constant of the class `SCENARIO_CONSTANT_CENSUS` exists for — its
comment reads "a comfortable ceiling", in the same voice as `DD_FAILURE_WINDOW_DAYS` "generous on
purpose" (D27) and `AS_OF_BUFFER_DAYS` "comfortably past" (D29). The census cannot name it:
`_check_census_is_complete` takes its subject from **`build_scenario`'s AST**, so it is fail-closed
over the offline builder and structurally blind to the live one. `grep "6000\|RUN_SPANNING"` over
`tools/couple_w2_11_d5.py` returns nothing; the census's 8 members are all offline. Filed against
**D30**, whose census it is, as
`WORKER_FINDING_THE_CONSTANT_CENSUS_IS_BLIND_TO_THE_LIVE_PATHS_OWN_WINDOW_2026-08-17` — it classifies
into `controls_that_cannot_fail` and was consolidated and archived to `docs/staging/done/` in the same
tick it was written, so the **live index for it is
`docs/staging/CLASS_CONTROLS_THAT_CANNOT_FAIL_2026-08-12.md`**, not the staging root.

**LEAD, NOT ESTABLISHED (R9):** live `belief_population_mix` (0.2105) and live per-case disagreement
(0.2105, 4 of 19) are numerically identical. D19's reshape exists precisely because the TV-distance
figure was degenerate to permutation while per-case agreement was not (the note's own
`0.0713 → 0.0713` vs `0.9287 → 0.6432`). At n=19 the two coincide. Whether that is arithmetic
coincidence at small n or the two figures collapsing live is unmeasured, and it is D19's question.

## 13. Exit criteria — pass 3's four, with §4.1's amended

1. **UNCHANGED** (pass 2 c1). `amnesia_floor_window_days + headroom_days` has moved off
   `DD_FAILURE_WINDOW_DAYS − span − 1`.
2. **UNCHANGED** (pass 3 c2). A resolved memory error at `W = 400` AND every published reading
   `frac == 1.0`.
3. **AMENDED by §11.** The invariance control exists, is stated **with its knowledge-blindness
   precondition**, and fires under both named mutations — including the direction that proves it does
   not redden when the organ is repaired.
4. **UNCHANGED** (pass 2 c3 / pass 3 c4). `ageing` re-certified alongside the belief pair;
   `detection` / `detection_latency` asserted bit-identical.
5. **NEW.** The control declares itself **offline-only**, naming §12's two reasons — no published live
   belief gap, and live `W` inert by construction.

## 14. What pass 4 does not settle

* Whether the belief organ should be knowledge-honest at all (§10, R9) — a design call, and the
  strongest single question this atom has produced.
* Whether D29 should be closed into D27 outright. Pass 3 queued it; this pass **weakens the case for
  closure**: §10 and §11 are D29's own content and are not D27's reshape, so the atom now has a
  deliverable that no other atom carries. Still queued, not taken.
* The live population empirically — `run_phase2b` was not run (§12 answers from code and artefact).

R12: no published number was tuned and none was written to any artefact; every figure was scored in a
throwaway worktree. R13: harness scaffolding, not a baseline-world fidelity claim.

**STATUS: DISCOVER/FRAME only.** `level_current` unchanged at **0**, `loop_stage` unchanged at
`idle`, `provenance` unchanged at `proposal`. Nothing in `file_scope` written.
