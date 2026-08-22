# FRAME — D27: where the scored company sits inside its own blind band

**Atom:** `D27_belief_window_saturates_on_this_book` (lane D_billing_metering, L0, `loop_stage: build`)
**Stage:** §§1–8 are the FRAME, written when the atom was `loop_stage: idle` and no BUILD code
existed. **§9 onwards is BUILD** — the atom's stage moved and the draw is live, so parts of this
document ARE now landed in `tools/couple_w2_11_d5.py`; §9.4 states exactly which, and §9.5 states
what is still only designed. The reshape itself is NOT landed.
**Date:** 2026-08-14 FRAME (worker tick, DISCOVER/FRAME lane); §9 2026-08-22 (worker tick, BUILD lane)
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

---

## 9. BUILD pass 1 — 2026-08-22 (worker tick, BUILD lane)

**Everything in §2 re-measured at HEAD `34ee29090` before anything was built** (the FRAME's
figures were 8 days old and D30/D33 passes had landed on this module since). n=300, seeds 7/11/23,
shipped `build_scenario`/`score_triad`/`measure_belief_window_resolution`, origin substituted in a
scratch script.

**A and B reproduce bit-identically.** A (400): headroom +309/+308/+308, saturated.
B (organ default 90): headroom −1/−2/−2, not saturated, `predicted_saturates_above_drift`
+1/+2/+2 and `_below` −61/−61/−60. `belief` 0.1518987→0.1708861 (seed 7), 0.1913580→0.2037037 (11),
0.1352941→0.1411765 (23). R13 differential holds: `ageing`, `detection`, `detection_latency`
bit-identical between A and B on every seed.

### 9.1 One equality stronger than the FRAME had

The FRAME states reading 2 as "today's published belief figure IS the never-forgets company's
figure", evidenced by B's `+500` column. Measured this pass with the counterfactual reached by a
**book-derived** drift (`oldest observed failure age − window`) rather than by a large literal:
**A == never-forgets on ALL FIVE dimensions, every seed** — not just the two belief figures. So the
claim is checkable forever without the number 400 or 500 appearing anywhere, which is what
`test_todays_published_figure_is_the_never_forgets_companys_figure` now asserts.

### 9.2 The bands at the candidate origin, re-derived (not translated)

`measure_own_drift_resolution(n_customers=300)` over the book-derived grid with the two belief
entries' declarations emptied, so the grid is the book's alone (73s, 65 grid points × 3 seeds):

| | `belief` | `belief_population_mix` |
|---|---|---|
| measured **unmoved** (all seeds) | **none — the band is empty** | `(-1,)` |
| `own_collapsed_runs` | `(-90,-61), (-48,-47,-46), (-23,-22), (-21,-20)` | `(-90,-61), (-23,-22), (-1,0), (1,2)` |
| `own_saturates_below` | −61 | −61 |
| `own_saturates_above` | **None** (see §9.3) | +1 |
| readable floor, own scorer @4dp | **310d → 4d** | **314d → 4d** |

`measure_published_resolution_floor` (69s): both figures resolve a **4-day** memory error at the
organ's default, against 310d and 314d today, with `readable_at_every_drift_beyond_floor` True on
both. `measure_belief_band_population_axis`: `above_edge_range` (−23, 2), `below_edge_range`
(−61, −32); the derived null-control floor stays **n=17** and the invoice span stays (30, 92) — the
origin move does not move the law, which is what that null control exists to say.

Criterion 5 survives in a different shape than the FRAME predicted: the two figures' *readable
floors* become equal (4 and 4) where today they differ (310 vs 314), while the *bands* still differ —
`belief` has no invisible drift at all and the mix is blind at −1 and saturates above at +1. Per-
dimension bands are still required; a shared band would now be wrong in the opposite direction.

### 9.3 NEW FINDING — the reshape re-opens D29's defect at the other edge

`book_memory_grid` is `{a−W, a−1−W : a ∈ ages} ∪ {0, −W}`. Its **top point is `oldest − W`, which is
exactly the saturation point**, and a collapsed run needs two points. At the shipped origin the
declarations union in `+1`/`+500`, supplying the second point by accident. At the organ's default
they do not, and `belief`'s `saturates_above` is measured **None on a book that provably saturates
above** — the identical shape D29 named at the bottom ("D27 measured `saturates_below = None` on a
book that saturates below" because the low tail held one grid point), reappearing at the top,
*introduced by this reshape*.

The bottom extreme is total amnesia (`window == 0`). The symmetric top extreme is the never-forgets
company, and it is now derivable: **`book_memory_grid` must include `never_forgets_drift_days + 1`.**
One point suffices and that is provable rather than swept — an event at age `a` is counted iff
`a ≤ window` and no `a > oldest` exists, so every larger window is bit-identical by construction.

This changes the grid at the **current** origin too (seed 11/23 gain −307), so it moves the shipped
`own_collapsed_runs` declarations and must land in the same commit as the re-derivation.

### 9.4 What this pass built, and what it did not

**Built by pass 1; committed by pass 3 as `ccac8c0d6`** — passes 1 and 2 each wrote that this was
landed and neither committed anything (§10, §11), so for two passes the claim was true of no tree
but its author's. The commit id above is the point: it is checkable by `git show ccac8c0d6:` against
any later tree, which the word "Landed" never was. Files (`tools/couple_w2_11_d5.py`,
`tests/tools/test_couple_w2_11_d5.py`; no
published figure moves): `organ_default_failure_window_days()` (criterion 2's derivation, fail-closed at three
unreadable-organ shapes); `never_forgets_drift_days()` (book-derived, replacing the literal as the
route to the counterfactual — **0 on the shipped origin, which is the finding stated in the
coordinate the reshape moves**); `scenario_organ_default_shadows()`, which derives from
`build_scenario`'s AST *which* constants shadow a company organ default rather than naming this one
(R10), with its null control one line away in the same function (`LedgerEvent(amount_gbp=...)` is a
**required** parameter and is correctly not a shadow); `measure_/check_scored_window_provenance`,
wired into `main()`'s control block (the module's check-call census reads 25 controls, 0
UNREACHABLE); and `SCENARIO_CONSTANT_CENSUS["DD_FAILURE_WINDOW_DAYS"]["measured_divergence"]`, which
records the divergence and its **cost** with a date and a subject.

The class rule is the point: *a scenario constant that shadows a company organ's default owes a
measured divergence, and a design note is not one.* Both directions fail — a shadow with no
declaration, and a declaration on a constant that shadows nothing.

**Not landed: the reshape itself.** The origin is still 400. Measured reason for stopping here
rather than half-landing: the flip invalidates every memory declaration in the register (they are
stated in drift coordinates whose zero IS this constant), and this test file runs **~55 minutes**,
so the ~30 assertions carrying `-308`/`-309`/`-371`/`400` cannot be re-derived and verified inside
one bounded tick. The sweeps themselves are cheap (73s / 69s / 2s) and their results are in §9.2, so
the continuation does not need to re-measure.

The provenance control is a **ratchet on that continuation, not a description of the defect**:
moving the origin fires it four independent ways (`harness_window_days`, `divergence_days`,
`never_forgets_drift_days`, `scored_saturated`), verified live this pass. The reshape cannot land
without re-deriving the record.

### 9.5 The continuation, in order

1. Add the never-forgets point to `book_memory_grid` (§9.3) and re-derive the shipped
   `own_collapsed_runs` at the **current** origin — this is a standalone, publishable repair.
2. Flip the origin to `organ_default_failure_window_days()` and take §9.2's declarations.
3. `recency_contribution` (criterion 4). Note the constraint the FRAME does not state: the window is
   a **constructor** argument and `_arrears_risk_belief` reads it off the consumer, so `score_triad`
   — which holds one consumer and no builder — cannot compute it. It needs a reference reading
   threaded in from a second build (`measure()` can; the live `run_phase2b` path cannot, and must
   publish "not measured on this call" rather than a frozen number).
4. Re-derive `own_readable_resolution_floor_days` (4/4) and the axis edge ranges (§9.2), update the
   ~30 assertions, and regenerate the coupled-gap ledger row (R2/R11 — the figure is not moved until
   the artefact carries it).

---

## 10. BUILD pass 2 — 2026-08-22 03:54 (worker tick, LAND lane)

**Pass 2 wrote no new mechanism.** It found pass 1's entire output — 640 insertions across the two
`file_scope` files, plus §9 of this document — sitting **uncommitted in the shared working tree**,
verified it, and wrote the sentence "and landed it" here. **It did not land it** (§11): the reflog's
last `surgical-land` was `02:53:53` and no commit followed, so this paragraph as pass 2 left it was
the second false landing claim in this document — made inside the section diagnosing the first.
At `34ee29090` every symbol §9.4 called "Landed" was absent: `git show
HEAD:tools/couple_w2_11_d5.py | grep -c` returned **0** for `organ_default_failure_window_days`,
`never_forgets_drift_days`, `scenario_organ_default_shadows` and `measure_scored_window_provenance`,
and 0 for `measured_divergence` in the census. Pass 1 ended ~03:52; the tick that drew this atom
began 03:54, so the work was two minutes from being the next lane's revert.

**What pass 2 verified** (targeted, not the ~55-minute whole file) — reproduced independently by
pass 3 in §11, which is the only reason this table survives at all:

| selection | result |
|---|---|
| the five new tests (`-k "memory_origin or shadow_finder or shadowed_organ_default or never_forgets_drift or never_forgets_companys_figure"`) | **5 passed**, 8.45s |
| `-k "census or runs_in_the_cli"` — the control-reachability and constant-census population | **25 passed**, 133s, exit 0 |

The diff is **pure addition — 640 insertions, 0 deletions**, which is why a targeted selection is
adequate evidence here and would not be for a pass that changed a shipped derivation.

### 10.1 The class this belongs to

Not a new class: `CLASS_UNCOMMITTED_AND_ORPHANED_WORK_2026-08-12.md`, and the same shape as
`WORKER_FINDING_THE_LIVE_VALUATION_IS_SERVED_BY_AN_UNCOMMITTED_GENERATOR_2026-08-17.md`. What this
instance adds is that **the false claim was load-bearing for the continuation**: §9.5 tells the next
pass to build *on top of* `book_memory_grid` and `organ_default_failure_window_days()`. A pass
drawing D27 after a concurrent lane reverted the tree would have read "Landed", found the symbols
gone, and had no way to tell a revert from a rename — the document names no commit to check against.

The durable lesson is in the asymmetry: pass 1 spent a full tick measuring (73s + 69s sweeps, three
seeds, bit-identical reproduction) and then risked all of it on the one step that costs seconds. A
measurement that is not committed is not evidence, because nothing can be asked to reproduce it.

---

## 11. BUILD pass 3 — 2026-08-22 (worker tick, LAND lane) — the second false landing claim

**Pass 3 wrote no new mechanism either.** It drew this atom, read §9.4's "Landed" and §10's "and
landed it", and checked both against git rather than against the document. Both were false:

| asked of git | answer |
|---|---|
| `git show HEAD:tools/couple_w2_11_d5.py \| grep -c <symbol>` for the four new functions | **0, 0, 0, 0** |
| `grep -c measured_divergence` in the census, at HEAD | **0** |
| the same five greps in the **working tree** | 2, 6, 3, 4, 8 |
| `git reflog --date=iso` — the last `surgical-land` before this tick | **`34ee29090`, 02:53:53**, and nothing after it but publisher commits at 03:07 and 03:47 |

So pass 2 diagnosed pass 1's false claim, wrote a section about it, verified the work — and then
made the identical claim itself. The 640 insertions had by then survived three publisher commits in
the shared tree by luck.

**Reproduced before landing, on pass 3's own run rather than on pass 2's table:**

| selection | pass 2 recorded | pass 3 measured |
|---|---|---|
| the five new tests | 5 passed, 8.45s | **5 passed, 8.31s** |
| `-k "census or runs_in_the_cli"` | 25 passed, 133s | **25 passed, 135.91s, exit 0** |

Landed as **`ccac8c0d6`**, 640 insertions / 0 deletions across the two `file_scope` files, and
verified **by the tree**: all five symbols return non-zero from `git show ccac8c0d6:`, and the only
path left dirty afterwards is this document.

### 11.1 Why this is R3, not a third instance of §10.1

Two false completion claims on the same component is the two-strike rule, and the answer is not a
third paragraph saying "commit your work". What both passes actually lacked was a **checkable
referent**: "Landed" names no tree, so a later pass cannot tell a lost commit from a revert from a
rename, and cannot tell a true claim from a false one *at all* without re-deriving the whole diff.
`ccac8c0d6` in §9.4 can be asked. That is the whole of the repair that belongs in this document.

### 11.2 The control for this class already exists, and is structurally blind to this instance

Grepped before proposing anything, which is the reason this section says something rather than
filing a sixteenth near-duplicate: `CLASS_UNCOMMITTED_AND_ORPHANED_WORK_2026-08-12.md` already lists
`WORKER_FINDING_THREE_CONSECUTIVE_PASSES_RECORDED_A_LANDING_THAT_IS_IN_NO_COMMIT_2026-08-19.md`
(severity RECORDED, **discharged**), and its recommendation 1 was built as
`tools/record_landing_claim_check.py`, wired into `tools/pre_commit_test_gate.py` at
`_record_landing_claim_check` — deliberately placed *before* the pure-docs early return, fail-closed
if the checker is unimportable. That control is the right one for the class and it could not have
fired on passes 1 or 2, for two independent structural reasons:

1. **Invocation.** It runs `git diff-tree since_tree..tree` from the pre-commit gate. Passes 1 and 2
   committed nothing at all, so the gate never ran and there was no tree to diff. This is the
   *ask what invokes a control before you ask what it checks* shape: the predicate is sound and the
   trigger cannot reach the failure. Closing it needs a **tick-boundary sweep**, not a hook.
2. **Subject.** `STORE_PREFIX = "docs/design/simplifications/"` — the control reads the atom's store
   record, because that is where EP6's five false claims lived. D27 has such a record
   (`D27_belief_window_saturates_on_this_book.yaml`) and the false claims were **not in it**: they
   were in §9.4 and §10 of this design document, under `docs/design/` but outside the prefix.

Neither of these is a defect in that control — its own docstring is explicit that the unit of claim
is the store record, and widening the prefix to all of `docs/design/**` would re-import the
prose-parser problem it was narrowed to avoid. **What this instance adds to the class is that the
built control's coverage is bounded by two things nobody has measured: which documents can carry a
landing claim, and whether the pass commits at all.** Registered here as the finding, not fixed on
sight (SELF_INTERRUPT_DISCIPLINE) and out of this atom's `file_scope`; the sizing evidence for
whoever takes it is that the *second* axis is the one that caught this file twice, and it is the
axis a hook can never cover.

**§9.5 is unchanged and still the continuation.** The reshape is not landed; the origin is still
400. Step 1 (the never-forgets point in `book_memory_grid`, §9.3) remains the standalone repair to
take next, and it now has a committed base to build on.
