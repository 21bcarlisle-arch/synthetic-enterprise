# DISCOVER — D27: the census stops where the book stops, and the constant that picks the worlds is on the other side

**Atom:** `D27_belief_window_saturates_on_this_book` (lane D_billing_metering, L0, `loop_stage: idle`)
**Stage:** DISCOVER only. **No BUILD code was written** — the atom is epoch-parked and BUILD-gated
(`EPOCH_GATING_AND_ATOM_AUTHORSHIP.md` Rule 1). Nothing here is landed in `tools/couple_w2_11_d5.py`.
**Date:** 2026-08-14 (worker tick, DISCOVER/FRAME lane)
**Takes:** `docs/design/D27_CONSTANT_PROVENANCE_CENSUS_DISCOVER.md` §6 second bullet — *"The scoring
side. `scenario_constants()` derives its subject from `build_scenario`, so a confounder-removal choice
made in a scoring constant is outside the census's subject by construction. `RESOLUTION_SEEDS =
(7, 11, 23)` and `AGEING_RESOLUTION_TARGET_DAYS = 1` are the two visible candidates and neither was
examined here."* Both are examined here. D27 owns the census **shape**, which is what this is.

---

## 1. The subject boundary, measured off the AST (R9: observed)

`scenario_constants()` walks `build_scenario`'s AST and returns the module constants it reads.
`check_scenario_constant_census` then fails closed on that keyset — a scenario constant nobody
censused raises. That control is real and it has a hard edge: **it can only ever see constants the
book-builder reads.**

Measured over the module (`/tmp` scratch, AST only, nothing scored):

| | count | constants |
|---|---|---|
| module-level UPPER constants | 21 | — |
| census subject (`build_scenario` reads) | 8 | the D30 census's eight |
| read by `score_*`/`measure_*`/`predict_*`/`check_*` and **outside** the subject | 8 | below |

Of those eight outside, six are prose or atom-id strings (`AGEING_EXCLUSION_REASON`,
`BELIEF_FLOOR_DIMENSIONS`, `BELIEF_FLOOR_KNOB`, `BIT_EQUALITY_FLOOR_ATOM`, `ORGAN_CLOCK_REPAIR_ATOM`,
`RECON_DRIFT_KNOB`) — labels, not choices. **Two are choices**, exactly the two the previous DISCOVER
named:

* `RESOLUTION_SEEDS = (7, 11, 23)` — read by **five** measurement functions
  (`measure_dimension_drift_resolution`, `measure_organ_query_grid_saturation`,
  `measure_own_drift_resolution`, `measure_published_figure_caveat_coverage`,
  `measure_published_resolution_floor`), by **six caveat renderers that print its value into published
  prose** (`belief_resolution_caveat`, `ageing_resolution_caveat`, `detection_resolution_caveat`,
  `latency_terms_resolution_caveat`, `organ_query_grid_saturation_caveat`, `_own_floor_clause` — e.g.
  *"n=300, seeds [7, 11, 23]"*), by the CLI and by two tests. It decides **which worlds every published
  resolution verdict is measured on**, and it is named in the caveats that carry those verdicts.
* `AGEING_RESOLUTION_TARGET_DAYS = 1` — read by `check_ageing_resolution`, where it is the pass
  threshold for D25's deliverable.

Neither can ever be reached by `check_scenario_constant_census`, and not by oversight: the census's
subject is derived from the builder, so a scoring-side choice is out of scope **by construction**.
That is the same sentence D27 was minted for, one seam over — the previous DISCOVER found the census
records a constant's ROLE and never why its VALUE is the value; this one finds the census cannot see
the scoring side's values at all.

**Provenance of the seed constant, off `git log -S`:** it entered in `e6522928a` (H27 Expert Hour #8,
2026-08-10) with no stated reason, in the same commit that found the ageing headline's resolution was
the harness's calendar. Its `why` is not recorded anywhere in the module, the tests, or the design
docs. Class: **unstated**, same as the four the previous census found — and this one is not
scaffolding, it is the population of every resolution verdict.

## 2. `RESOLUTION_SEEDS`: what the choice buys, measured (n=300, 109-drift dense grid, 2026-08-14)

`DIMENSION_DRIFT_RESOLUTION` declares `"structural": True` on its entries, and
`measure_dimension_drift_resolution`'s own docstring states the claim plainly: *"the register's claims
are structural (they follow from the scenario calendar), so a band that holds on one seed and not
another is a claim this register must refuse."* **That is a falsifiable claim about seed-invariance,
and nothing has ever tested it** — it is checked on the three seeds it was derived from.

Tested here by re-running the shipped `measure_dimension_drift_resolution` /
`check_dimension_drift_resolution` pair, unmodified, over other seeds of the **same** book
construction (R13: a different customer draw, never a different world model — the grid itself is
identical at 109 drifts, −20…+88, on every seed measured, so the calendar side really is structural):

| seed set | violations from the register's OWN checker |
|---|---|
| **shipped `(7, 11, 23)`** | **0** |
| `(7, 11, 23)` + **one** more seed | seed 3 → 2, seed 5 → 5, seed 13 → 6, seed 17 → 4, seed 19 → 10, seed 29 → 11 |
| growing prefix, 4→9 seeds | 2, 7, 13, 14, 15, **19** |
| **all 83 other triples** drawn from the same nine seeds | **minimum 9, median 27, maximum 39 — not one clean** |

The shipped triple is the only zero-violation triple of the 84 tried. **The honest reading is not that
the seeds were picked to pass** — the declarations were *derived* on these three seeds (D28, Hour #10),
so of course they describe them; the finding is that a register whose declarations are derived from
three worlds carries a claim of seed-invariance that **is false, and the false-ness was reachable by
running the shipped controls on a fourth world for 33 seconds.**

What the 19 violations at nine seeds actually are, and none of them is a rounding artefact:

* **Every one of the twelve declared `detection` collapse runs is split by at least one outside
  seed** — `(6,7)`, `(9,10)`, `(11,12,13)`, `(17…24)`, `(28,29)`, `(44,45)`, `(61,62)`, `(65,66,67)`,
  `(68,69)`, `(72,73,74)`, `(76,77,78)`, `(82…88)`. The predicate is bit-equality
  (`D33_the_collapse_predicate_is_bit_equality`), so I measured the **magnitude** of each split rather
  than assuming it was float noise: **1.0% to 26.6% of the reading** (e.g. `(28,29)` on seed 17:
  0.00575, 26.6%; `(11,12,13)` on seed 17: 20.0%; `(9,10)` on seed 19: 12.5%). These are two companies
  the register says publish one number, publishing two numbers a fifth apart.
* **Five undeclared collapses appear** — `[19…24]`, `[65,66]`, `[73,74]`, `[82,83,84]`,
  `[85,86,87,88]` — i.e. the split runs re-group into *narrower* bit-identical blocks that the
  register does not name. The blindness does not go away with more seeds; it moves.
* **A declared saturation edge is wrong:** `detection` declares `saturates_above: 82` and the nine-seed
  sweep measures **85**. Three companies the register says are indistinguishable are distinguishable,
  and the caveat that interpolates that edge publishes the wrong tail.
* **A fail-open the three seeds never reach:** `detection_latency` publishes **no reading at all** at
  drift +86 on the wider set — `None != baseline` is counted as *movement*, i.e. as resolution, by
  every band below it. An instrument that has stopped reading is scored as one that saw the company
  move. The `undefined_witness` machinery exists for exactly this and is not armed at +86 because the
  shipped triple never produces it.

**The direction of the error is not symmetric, and this is the part that matters for the controls.**
`moved`/`unmoved` are intersections across seeds and collapse runs are a partition across seeds, so
adding seeds can only *shrink* declared-movement, *shrink* collapse runs and *widen* the measured
blind band. Concretely: the seed count sets the strictness of every declaration in the register, in a
direction nobody chose — three seeds is the most permissive end of the range that was available, and
the exactness rule (`_check_on_path_entry`'s *"the band must be EXACT, not merely true"*) is the one
leg that gets **weaker** as seeds are added, because a wider band requires fewer declarations.

**R12, explicitly:** no seed count and no seed value is proposed here, and nothing about the published
figures is being tuned. Nine seeds is a **falsification probe**, not a recommendation — running the
register at nine seeds would cost ~5 minutes of scoring per sweep against ~100 seconds today, and
whether the answer is a wider sweep, a recorded reason for three, or re-derived declarations is the
owning atoms' call (§4). The finding is that the strictness of every band control in this instrument
rides on an unstated constant, and that the register's own `structural: True` is measurably false.

## 3. `AGEING_RESOLUTION_TARGET_DAYS`: the one scoring constant whose value has a reason, and nothing holds it there

`check_ageing_resolution` fails when the measured resolution `> target_days`. Measured on eleven
seeds (n=300), the book resolves **1 day in both directions on every one** (over/under both `1`,
`n_aged` 81–113). So the target sits **exactly** on the achieved value, with zero slack.

That reads at first like a threshold set to what was achieved — the shape R12 exists to catch — but it
is not, and the reason is worth recording rather than re-deriving next Hour: **1 day is the integer
floor.** Ages are whole days, so no book can resolve better; a target of 1 is the strongest demand
expressible and cannot be met by a weaker book. The constant is defensible, its value is not stated,
and **nothing prevents a future edit to 5**: `check_scenario_constant_census` cannot see it (§1), no
test pins it, and the control would go on passing over a book five times blinder. Same class as the
buffer in the previous DISCOVER — the value is right, the reason is nowhere, and the census that
exists to catch exactly this cannot reach it.

## 4. What a BUILD would land, and the mutation that proves each control can fail (R15)

Not built here (epoch-gated). D27 owns the census shape; the register's declarations are **D28's**
(collapse runs, saturation edges) and the undefined-reading witness is **D31's**. Handed over in
writing:

1. **The census's subject includes the scoring side.** `scenario_constants()` gains a sibling deriving
   the constants the published-figure path reads — off the AST, never hand-listed — and every entry
   owes the same `value_provenance` the previous DISCOVER's criterion 1 defines, with `unstated` a
   visible answer. *Mutation:* add a constant to a scoring function and leave it uncensused → must
   raise, the way `_check_census_is_complete` already does for the builder's side. *Second mutation:*
   point the subject at `build_scenario` only → `RESOLUTION_SEEDS` must disappear from the census,
   i.e. the control reverts to today's blindness and the mutation is visible.
2. **A constant that selects the scored POPULATION owes a measured stability reading.**
   `RESOLUTION_SEEDS` must carry what re-running the register's own checker on seeds outside it
   returns — measured by running it, not declared. *Mutation:* freeze the recorded violation count →
   must fire. *Second mutation:* substitute a checker that ignores the extra seeds → the entry must be
   refused, so the control discriminates a real stability claim from a restated one.
3. **`structural: True` is earned, not asserted.** An entry claiming its band follows from the
   calendar must have been measured on at least one seed outside `RESOLUTION_SEEDS`, and the seed that
   witnessed it recorded. *Mutation:* declare a collapse run that holds only on the shipped triple →
   must fire (today it passes; twelve of twelve do).
4. **A threshold constant records whether it is at a floor.** `AGEING_RESOLUTION_TARGET_DAYS` declares
   `floor: 1 day, integer ages` and the check derives that floor rather than trusting it. *Mutation:*
   move the target to 5 → must fire on the floor claim even though every book still passes the
   resolution test, because a weakened threshold that nothing can fail is the whole class.

## 5. What this DISCOVER does not settle

* **Whether the register's declarations should be re-derived, or the sweep widened, or the three
  seeds justified.** Deliberately not chosen: it is D28's register and the cost is real (§2).
* **The other four measurement functions.** Only `measure_dimension_drift_resolution` was put on
  trial. `measure_organ_query_grid_saturation`, `measure_own_drift_resolution`,
  `measure_published_figure_caveat_coverage` and `measure_published_resolution_floor` read the same
  constant and none was swept here; each is a candidate for the same test at ~33s per seed.
* **Whether nine seeds is enough** to state a stable band. The violation count was still climbing at
  nine (2, 7, 13, 14, 15, 19) and no convergence was measured.
* **Whether `n_customers=300` carries the same exposure.** It is a parameter default rather than a
  module constant, so it is outside both censuses and was not examined.

## 6. Reproducing the measurement

From the repo root with `PYTHONPATH=.`; reads the shipped functions, monkeypatches nothing, writes
nothing. ~33s per seed (109 drifts × `score_triad`), and the module's `_RESOLUTION_SCORES` cache makes
every subset after the first free within one process:

```python
import itertools
from tools import couple_w2_11_d5 as C
SHIPPED, OUTSIDE = (7, 11, 23), (3, 5, 13, 17, 19, 29)
C.measure_dimension_drift_resolution(seeds=SHIPPED + OUTSIDE)      # warms the cache
def violations(seeds):
    return C.check_dimension_drift_resolution(
        C.measure_dimension_drift_resolution(seeds=tuple(seeds)))
len(violations(SHIPPED))                                            # 0
len(violations(SHIPPED + OUTSIDE))                                  # 19
[len(violations(t)) for t in itertools.combinations(SHIPPED + OUTSIDE, 3)]   # min 9 excl. SHIPPED
# split magnitudes: score_triad(..., organ_terms_drift_days=k)["detection"].gap over each
# declared run in C._DETECTION_COLLAPSED_RUNS, per outside seed.
# §3: C.measure_ageing_resolution(*C.build_scenario(300, seed=s)[::3]) -> over/under = 1/1.
```

**Subject boundary (§1), AST only, no scoring:**

```python
import ast, inspect, sys
from tools import couple_w2_11_d5 as C
tree = ast.parse(inspect.getsource(sys.modules[C.__name__]))
consts = {t.id for n in tree.body if isinstance(n, ast.Assign) for t in n.targets
          if isinstance(t, ast.Name) and t.id.isupper() and not t.id.startswith("_")}
subject = set(C.scenario_constants())
for f in (n for n in tree.body if isinstance(n, ast.FunctionDef)
          and n.name.startswith(("score_", "measure_", "predict_", "check_"))):
    print(f.name, sorted({n.id for n in ast.walk(f)
                          if isinstance(n, ast.Name) and n.id in consts} - subject))
```
