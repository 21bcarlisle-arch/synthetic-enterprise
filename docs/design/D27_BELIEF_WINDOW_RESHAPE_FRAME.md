# FRAME — D27: where the scored company sits inside its own blind band

**Atom:** `D27_belief_window_saturates_on_this_book` (lane D_billing_metering, L0, `loop_stage: build`)
**Stage:** §§1–8 are the FRAME, written when the atom was `loop_stage: idle` and no BUILD code
existed. **§9 onwards is BUILD** — the atom's stage moved and the draw is live, so parts of this
document ARE now landed in `tools/couple_w2_11_d5.py`; §9.4 states exactly which, and §9.5 states
what is still only designed. The reshape itself is NOT landed — §12 lands step 1 of the
continuation and re-measures the declarations step 2 will need.
**Date:** 2026-08-14 FRAME (worker tick, DISCOVER/FRAME lane); §9–§12 2026-08-22 (worker ticks, BUILD lane)
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

---

## 12. BUILD pass 4 — 2026-08-22 (worker tick, BUILD lane) — §9.5 step 1

**Step 1 only.** The origin is still 400 and the reshape is still not landed; what changes here is
that the grid the reshape will be measured on can now answer about its own top edge.

### 12.1 The grid, measured before anything was edited

At HEAD `32c72b139`, n=300, `build_scenario` / `book_memory_grid` as shipped:

| seed | oldest observed failure | grid top 3 | saturation drift `oldest − window` | point it gains |
|---|---|---|---|---|
| 7 | 91d | −310, −309, 0 | −309 | **−308** |
| 11 | 92d | −309, −308, 0 | −308 | **−307** |
| 23 | 92d | −309, −308, 0 | −308 | **−307** |

So the grid's top book-derived point IS the saturation drift on every seed, and the only point above
it is 0 — which `_measure_collapse_runs` never counts, because 0 is the baseline every other company
is compared against. §9.3 predicted −307 for seeds 11/23 and that is what the grids read; seed 7's
own gain is −308, which the union already held from its siblings.

### 12.2 What the witness is, and what it is not

`book_memory_grid` now adds `oldest − window + 1`. The justification is a construction, not a
sweep: an event at age `a` is counted iff `a ≤ window` and nothing is older than `oldest`, so every
window at or above `oldest` counts the same events and the whole never-forgets family is
bit-identical. One point is therefore enough, and it is the *smallest* one — which matters.

**It is deliberately NOT `never_forgets_drift_days() + 1`,** which §9.3 wrote and which does not
survive contact with the function: that helper clamps at 0 to say something about the SCORED
company ("it already never forgets" — D27's whole finding in its own coordinate), so at this origin
it answers 0 and `+1` would put the witness at **+1**, 309 days above the edge. That is not a
derivation of the edge; it is the register's own `+1` declaration, which is the accident this repair
exists to remove. The test asserts both halves of that: the helper returns 0 here and `1` is not in
the grid.

### 12.3 The re-derivation, and the evidence the control fires

`measure_own_drift_resolution(n_customers=300)`, seeds 7/11/23, before and after the grid change
(76.2s cold; the second sweep costs 1.1s because only the new point per seed is unscored):

| | `belief` | `belief_population_mix` |
|---|---|---|
| grid points | 70 → **71** | 70 → **71** |
| top collapsed run | `(-308, -100, -1, 0, 1, 500)` → `(-308, **-307**, -100, -1, 0, 1, 500)` | `(-309, -308, -100, -1, 0, 1, 500)` → `(-309, -308, **-307**, -100, -1, 0, 1, 500)` |
| `own_saturates_above` | −308, **unmoved** | −309, **unmoved** |
| `own_saturates_below` | −371, unmoved | −371, unmoved |
| `off_target` / `world_identical` | `{}` / True | `{}` / True |

The edges not moving is the expected result and the reassuring one: −308/−309 were already the first
drifts bit-identical to the baseline on all three seeds, so the witness adds a MEMBER to the run
rather than extending resolution. Had an edge moved, the shipped one would have been an artefact of
the missing point rather than a measurement.

Before the declarations were updated, `check_own_drift_resolution` returned **six** violations —
three per belief entry: `-307` measured invisible and undeclared, a collapse the register does not
declare, and the declared run now read apart. That is the register's own control firing on the new
grid, which is why this is a re-derivation and not a re-typing.

### 12.4 R15 on the witness itself

`test_the_memory_grid_carries_a_witness_above_its_saturation_point` is new and carries its own
mutation: it rebuilds the pre-pass-4 grid on the same book and asserts that grid has **nothing**
above the saturation drift except 0, at BOTH the shipped origin and the organ's default. Run against
the pre-pass-4 `book_memory_grid` (monkeypatched into the module, not committed), the control fires
by name: *"window 400: the grid stops AT its saturation drift −309, so the top run has one member
and this instrument must measure `saturates_above = None` on a book that saturates above"* — and the
D29 provenance test's set equality fires too. Both are green on the shipped grid.

The control also asserts the equality the witness rests on (each witness drift counts the same event
set as the saturation drift) rather than assuming it, and refuses the book outright if `oldest` ever
drops below the organ's default — the state in which this edge no longer exists and the band would
need re-deriving anyway.

### 12.5 Verification

| selection | result |
|---|---|
| `-k "memory or band or saturat or collapse or grid or off_path or blind or witness"` — every test that reaches this grid, the two entries' declarations, the collapse/saturation checkers, the population axis and the resolution floors | **118 passed**, 495 deselected, **418.30s** |
| the new witness control + the D29 provenance control, run against the **pre-pass-4** grid | both **FAIL**, by name (§12.4) |
| `check_own_drift_resolution` on the new grid with the **un-updated** register | **6 violations**, 3 per belief entry (§12.3) |

The selection is chosen by what the change can reach, not by convenience:
`book_memory_grid` has exactly one caller in the repo (`measure_own_drift_resolution`, via
`OWN_DRIFT_BOOK_GRIDS`), and the two register entries are read by the checkers and the caveat, all
of which are inside it.

### 12.6 What did NOT move, checked rather than assumed

* **No published figure.** The gaps are unchanged; the only shipped value that moves is the
  `memory_blind_band_days` component on both belief dimensions, which gains −307. It reaches no
  artefact — `docs/observability/coupled_gap_ledger.json` carries no such key, and its W2_11 row is
  scored on a live population (31 events, oldest 3378d, window 6000d) whose caveat is re-derived per
  call. `docs/design/D27_COMPONENT_LIFT_SUFFIX_DISCOVER.md` quotes both literals and has been
  annotated in place so that record does not outrun the code.
* **The population axis.** `measure_belief_band_population_axis` reads
  `predicted_saturates_above_drift` off the book predictor and never touches this grid, so
  `above_edge_range` / `below_edge_range` / the derived n=17 floor are untouched by construction —
  verified by grep: `book_memory_grid` has exactly one caller in the repo,
  `measure_own_drift_resolution` via `OWN_DRIFT_BOOK_GRIDS`.
* **`measure_published_resolution_floor`** builds its own book-derived grid from
  `smallest_visible_shortening_days`, so the 310d/314d floors are unaffected.

### 12.7 The continuation

**§9.5 steps 2–4 are unchanged and still the reshape** (flip the origin to
`organ_default_failure_window_days()`, take §9.2's declarations, `recency_contribution`, then the
~30 assertions and the ledger row). Step 1 is now off that list.

**One correction step 2 must carry, and it is this pass's own doing.** §9.2's table reads
`own_saturates_above: None` for `belief` at the candidate origin — that reading *is* the artefact
§9.3 diagnosed, taken on the grid before the witness existed, and it does not survive the witness.
So §9.2's declarations cannot be copied wholesale into step 2. **Pass 4 re-measured them** rather
than leaving step 2 to discover it: same method as §9.2 (both belief entries' declarations emptied,
so the grid is the book's alone), `DD_FAILURE_WINDOW_DAYS` substituted to the organ's default 90,
n=300, seeds 7/11/23, 66 grid points, 73.2s:

| at the candidate origin | `belief` | `belief_population_mix` |
|---|---|---|
| measured **unmoved** | none — the band is empty (§9.2 agrees) | `(-1,)` (§9.2 agrees) |
| `own_collapsed_runs` | `(-90,-61), (-48,-47,-46), (-23,-22), (-21,-20), ` **`(2,3)`** | `(-90,-61), (-23,-22), (-1,0), ` **`(1,2,3)`** |
| `own_saturates_below` | −61 | −61 |
| `own_saturates_above` | **+2** — §9.2 read `None` | **+1**, as §9.2 read it |

Every other figure in §9.2 reproduces. The books read `oldest` 91/92/92 against a 90d window on
seeds 7/11/23, so the per-seed saturation drifts are +1/+2/+2 and the first all-seed bit-identical
drift is +2 — which is the edge `belief` now reports, and which the pre-witness grid could not have
reported at all because its top point WAS +2 with nothing above it. The mix entry sits one day
lower (+1) for its own D19 bluntness reason, exactly as it does at the shipped origin (−309 vs
−308). Steps 3–4 are untouched by this.

---

## 13. BUILD pass 5 — 2026-08-22 (worker tick, LAND lane) — §12 is in `21585a36b`

**What this pass did: it committed §12.** Nothing else. The origin is still 400 and the reshape is
still not landed; §9.5 steps 2–4 stand exactly as §12.7 left them, including the correction §12.7
hands to step 2.

### 13.1 What was found in the tree, before anything was written

At HEAD `32c72b139` — pass 3's addendum, the commit whose whole subject is passes that record work
they never committed — every symbol §12 describes returned nothing from `git show`:

| asked of `32c72b139` | answer |
|---|---|
| `book_memory_grid`'s added point `oldest − window + 1` in `tools/couple_w2_11_d5.py` | absent |
| `test_the_memory_grid_carries_a_witness_above_its_saturation_point` | absent |
| `−307` in either belief entry's `own_invisible_drifts` / `own_collapsed_runs` | absent |
| §12 itself, 137 lines of `D27_BELIEF_WINDOW_RESHAPE_FRAME.md` | absent |

All of it existed only in the shared working tree, which is the loss mode this atom has now met
four passes running.

### 13.2 Why this is NOT a third false landing claim, and what it is instead

**§12 never said it landed.** Its first sentence says the opposite — *"the origin is still 400 and
the reshape is still not landed"* — and no sentence in it claims a commit. Passes 1 and 2 wrote
"Landed" about work in no commit; pass 4 did not, so `record_landing_claim_check.py` has nothing to
fire on here even had it been reachable, and R3's two-strike counter does not advance.

**The exposure is identical anyway, and that is the finding.** A pass that says nothing about
landing and a pass that says the wrong thing end the tick in the same state: the atom's work
reachable from one lane's uncommitted worktree, where a concurrent lane's revert or checkout is the
documented loss mode. §11.2 established that this control cannot see a pass that commits nothing,
because a pass that commits nothing never reaches a pre-commit hook. Pass 4 shows the *second* half
of that gap: even a tick-boundary sweep keyed on the word "landed" would have passed pass 4 clean.
**The observable is the dirty `file_scope` at tick end, not the claim** — which is what
`CLASS_UNCOMMITTED_AND_ORPHANED_WORK` already carries, and this pass adds a member to that class
rather than proposing a second control.

### 13.3 The landing, verified by the tree rather than by the command

`python3 -m tools.surgical_land` over the four paths (`tools/couple_w2_11_d5.py`,
`tests/tools/test_couple_w2_11_d5.py`, this file, `D27_COMPONENT_LIFT_SUFFIX_DISCOVER.md`), gate
run to completion undetached — **`landed 21585a36b (4 paths)`, exit 0**, ~15 min wall clock.

Re-verified against the commit, not against the tool's own line:

| asked of `21585a36b` | answer |
|---|---|
| `grid.add(int(ages[-1]) - int(window) + 1)` | present, `tools/couple_w2_11_d5.py:3237` |
| `test_the_memory_grid_carries_a_witness_above_its_saturation_point` | present |
| `belief` → `own_invisible_drifts` | `(-308, -307, -100, -1, 1, 500)` at `:5113` |
| `belief_population_mix` → `own_invisible_drifts` | `(-309, -308, -307, -100, -1, 1, 500)` at `:5308` |
| `git status` on all four paths | empty |

Independently reproduced before landing rather than translated from §12.5's table: the two
memory-grid nodes, **2 passed, 0.38s** (611 deselected). The register declarations that `−307`
moves are covered by the gate's own stem selection over `test_couple_w2_11_d5.py`, which is what
`surgical_land` ran on the tree this commit creates.

### 13.4 What this pass did not do

**Step 2 was not attempted.** It is a re-measurement (§12.7's re-derived declarations, the ~30
assertions, the axis edges) whose sweeps alone cost more than the wall clock this tick had left
after a ~15-minute gate, and starting it would have ended the tick with a second uncommitted half —
the exact state §13.2 is about. The next pass takes §9.5 step 2 with §12.7's correction in hand.

---

## 14. BUILD pass 6 — 2026-08-22 (worker tick, BUILD lane) — §9.5 step 3, and why not step 2

**What this pass built and landed: exit criterion 4** — the recency contribution, as a published
component with a falsifier. **The origin is still 400 and the reshape is still not landed.** §9.5
steps 2 and 4 stand exactly as §12.7 left them.

### 14.1 Why step 3 was taken before step 2 (LAW A: deviation logged with its reason)

§9.5 is an order, not a target, and this pass re-ranked inside it. The reason is measured rather
than asserted. Step 2 flips the origin, and the flip is **atomic** — `check_scored_window_provenance`
fires four independent ways the moment `DD_FAILURE_WINDOW_DAYS` moves (§9.4), so a half-flipped tree
is not a landable tree. Its change set, counted on this tree rather than estimated: **10 register
fields across the two belief entries**, their surrounding declarations' comments (which state the
shipped-origin story in prose, not just in literals), the whole `SCENARIO_CONSTANT_CENSUS`
`measured_divergence` block, and — the part §9.4 did not name — **the semantic inversion of the six
tests that currently assert the defect** (`test_the_shipped_company_sits_inside_its_own_blind_band`,
`test_never_forgets_drift_is_derived_from_the_book_and_is_zero_today`,
`test_todays_published_figure_is_the_never_forgets_companys_figure`, and three siblings). Those do
not move by re-typing a literal; each has to become the criterion-1 claim with the 400 as its
mutation. That is not a bounded-tick change, and **five consecutive passes on this atom have ended
with uncommitted work in the shared tree** (§10–§13) — the loss mode is documented, not hypothetical.

Step 3 is **independent of the origin**: the subtraction it publishes is defined at any window, and
at the shipped origin its value is exactly the finding. So it lands now and moves by itself when the
origin does.

### 14.2 Step 2's measurements re-confirmed, so the next pass does not re-measure

Re-run this pass at HEAD `9b9815459` with `DD_FAILURE_WINDOW_DAYS` substituted to
`organ_default_failure_window_days()` (= 90), n=300, seeds 7/11/23, both belief entries'
declarations emptied so the grid is the book's alone — **71.8s, 66 grid points**:

| at the candidate origin | `belief` | `belief_population_mix` |
|---|---|---|
| measured **unmoved** | none — the band is empty | `(-1,)` |
| `own_collapsed_runs` | `(-90,-61), (-48,-47,-46), (-23,-22), (-21,-20), (2,3)` | `(-90,-61), (-23,-22), (-1,0), (1,2,3)` |
| `own_saturates_below` / `_above` | −61 / **+2** | −61 / **+1** |
| readable floor, own scorer @4dp | 4d | 4d |

`above_edge_range` (−23, 2), `below_edge_range` (−61, −32), null-control floor **17**, invoice span
**(30, 92)** — §9.2 and §12.7 reproduce **exactly**, including §12.7's correction of §9.2's
`own_saturates_above: None`. Step 2 is now an editing job with no measurement left in it.

### 14.3 What criterion 4 publishes, measured

`measure_recency_contribution()` — each belief figure minus the **never-forgets company's figure on
the same book**, reached by `never_forgets_drift_days` (book-derived; 0 on every seed today):

| n=300 | seed 7 | seed 11 | seed 23 |
|---|---|---|---|
| `belief` contribution | **0.0** | **0.0** | **0.0** |
| `belief` amnesiac probe | 0.3481013 | 0.3086420 | 0.3647059 |
| `belief_population_mix` contribution | **0.0** | **0.0** | **0.0** |
| `belief_population_mix` amnesiac probe | 0.1833333 | 0.1666667 | 0.2066667 |

The zero row **is** D27's finding, in the units the figure is published in and re-derived on every
run — where before it lived in a caveat, a register comment and a `cost` block carrying a
measurement date.

### 14.4 The constraint the FRAME did not state, made a property of the artefact

`dd_failure_window_days` is a **constructor** argument, so the never-forgets company is a second
BUILD and `score_triad` — handed one already-built company — cannot compute it.

* `score_triad` publishes `recency_contribution = None` plus
  `recency_contribution_basis = RECENCY_NOT_MEASURED_ON_THIS_CALL`. **Never 0.0**: on this dimension
  0.0 is also the true answer, so a placeholder would be unreadable from the finding. The live
  `background/live_payment_triad` path is exactly such a caller (51 tests pass unchanged; the
  suffix-derived caveat lift is untouched — neither new key ends in `_caveat`).
* `measure()` has a builder, so it replaces the refusal with the subtraction and stamps
  `never_forgets_drift_days` beside it.

### 14.5 R15 — and the control fired on its own first design

**The probe is the falsifier.** The true contribution is 0.0 on every seed today, so a control
asking only about the scored company would agree with a component frozen at zero and could never
fail here. The instrument is asked about two companies; the second is the **amnesiac** one —
memory below the book's newest observed failure (`amnesia_floor_window_days`, derived per seed),
where the organ counts nothing, which is **provably** a different company from never-forgets on any
book with an observed failure. This is the one place in this module a degenerate is the right probe,
and the reason is stated beside it: the question is whether the component still moves with the
company, not how finely it resolves — the `own_drift` band answers that, over a graded grid.

**The first probe was wrong and the control said so before any comment did.** It was the book's
`smallest_visible_shortening_days` — whose own docstring says it is the smallest shortening that
*may* be visible — and at the shipped origin **seed 11 publishes a recency contribution of exactly
0.0 at it**, because the events it drops carry no account across a severity tier. The clean tree was
RED with `not a discriminator` on both dimensions. `test_a_probe_that_is_silent_on_one_seed_is_refused`
keeps that live, and asserts the premise first so it fails loudly if the book ever moves.

Four mutations, each fires by name (run live, not quoted):

| mutation | violation |
|---|---|
| freeze the component (probe := scored) | `the scored company and the book's own AMNESIAC probe … the component no longer moves` |
| placeholder 0.0 where a refusal belongs | `a placeholder zero standing where a refusal belongs` |
| bare `None`, no basis | `a bare None is a hole` |
| component parted from the subtraction | `publishes recency_contribution 0.5 and re-measuring this book returns [0.0]` |

`check_recency_contribution` is wired into `main()`'s default control block, so the module's own
check-call census reads it as reachable (`0 UNREACHABLE`, asserted).

### 14.6 Verification

* 7 new nodes, **7 passed** (`-k recency or amnesiac or subtraction`: 5 passed 4.04s;
  `-k silent_on_one_seed or cannot_build_refuses`: 2 passed 4.91s).
* Component-population controls, the class that a new component breaks: **8 passed, 6.60s**.
* `tests/background/test_live_payment_triad.py`: **51 passed, 38.33s** — the live path still gets
  the refusal and the caveat lift is unmoved.
* Ruff on both touched files: 4 findings, all pre-existing (`tests/…:11, 950, 972`, `tools/…:139`),
  none inside the added ranges.

### 14.7 What this pass did not do

The origin is unmoved. **§9.5 step 2** (flip the origin, take §12.7's re-derived declarations, invert
the six defect-asserting tests) and **step 4** (`own_readable_resolution_floor_days`, the axis edge
ranges, the ~30 assertions, the coupled-gap ledger row) remain, in that order. §14.2 means step 2
opens with no sweep to run.

---

## 15. BUILD pass 7 — 2026-08-22 (worker tick, BUILD lane) — step 2's register half, DRY-RUN

**The origin is still 400 and the reshape is still not landed.** What this pass adds is the half of
§9.5 step 2 that was still a guess: §14.2 hands the next pass four measured numbers per entry, and
the register has **ten** fields that move. This pass derived the remaining six, then put the whole
candidate-origin register on trial against the module's own shipped checker — so step 2 is no longer
"take §14.2's table and work the rest out", it is a transcription that has already been run.

### 15.1 Why this pass did not flip the origin

Two reasons, both observed rather than judged.

1. **§14.1 stands unamended.** The flip is atomic, its change set includes the semantic inversion of
   six tests, and six consecutive passes on this atom have now ended with uncommitted work in the
   shared tree. Re-attempting the same shape a seventh time is the R3 defect, not persistence.
2. **A full suite was live on the shared tree for the whole tick** — `pytest tests/ -q` as PID
   4003393, started 05:49, still running at 06:2x, `cwd` = the shared worktree. `tools/couple_w2_11_d5.py`
   is imported by that run. Mutating a shared module while a long suite is in flight is a recorded
   defect class in this repo, and it would have reddened a suite this change has nothing to do with.
   Everything below was therefore measured in scratch scripts against the shipped functions with the
   origin substituted **in the process, never in the tree** — the same method §9/§12/§14 used.

### 15.2 The six fields §14.2 does not carry, measured

Same method as §14.2 (both belief entries' declarations emptied so the grid is the book's alone,
`DD_FAILURE_WINDOW_DAYS` substituted to `organ_default_failure_window_days()` = 90, n=300, seeds
7/11/23, 66 grid points). §14.2's four fields per entry reproduce **exactly**, so the table below
gives the whole ten-field diff, marked by provenance.

| field | `belief` | `belief_population_mix` | from |
|---|---|---|---|
| `own_invisible_drifts` | `()` — the band is empty | `(-1,)` | §14.2 |
| `own_collapsed_runs` | `(-90,-61), (-48,-47,-46), (-23,-22), (-21,-20), (2,3)` | `(-90,-61), (-23,-22), (-1,0), (1,2,3)` | §14.2 |
| `own_saturates_below` | `-61` | `-61` | §14.2 |
| `own_saturates_above` | `+2` | `+1` | §14.2 |
| `own_visible_drifts` | `(-60, -45, -30, -4)` | `(-60, -45, -30, -4)` | **this pass** |
| `own_readable_resolution_floor_days` | `4` | `4` | **this pass** |
| `own_bit_equality_floor_days` | `4` | `4` | **this pass** |
| `own_floor_predicate_atom` | `None` (unchanged) | **`None`** — today `D33_the_collapse_predicate_is_bit_equality` | **this pass** |
| `own_draw_size_axis.above_edge_range` | `(-23, 2)` | `(-23, 2)` | §14.2 |
| `own_draw_size_axis.below_edge_range` | `(-61, -32)` | `(-61, -32)` | §14.2 |

`measure_published_resolution_floor` at the candidate origin (n=300, seeds 7/11/23):
`floor_days` **4/4**, per-seed **4/4/1** (`belief`) and **4/4/2** (mix), `bit_equality_floor_days`
**4/4** with the same per-seed rows, `readable_at_every_drift_beyond_floor` **True** on both. The
books read `oldest` 91/92/92 against the 90d window, headroom **−1/−2/−2**, `saturated` **False**,
`amnesia_floor_window_days` 29/29/30 — the scored company stops being the never-forgets company,
which is the whole reshape.

### 15.3 NEW FINDING — D33's two-predicate divergence is an artefact of the saturated origin

`belief_population_mix` is the one entry in this register that declares a
`own_floor_predicate_atom`. It has to today: its readable floor is 314d and its bit-equality floor
312d, because at seed 11 the figure "moves" at −310..−313 by 1.4e-17 — a difference no 4dp consumer
can render, counted by the collapse predicate as one company told apart from another. D33 exists
because those two numbers disagree.

**At the organ's own default they agree: 4 and 4, on every seed, on both dimensions.** The
disagreement was never a property of the predicate — it is what a 1.4e-17 float wobble looks like
when the *only* drifts large enough to reach the figure at all are 310 days out. Move the origin to
where the book can resolve a 4-day error and the wobble is nowhere near the floor. So step 2 must
set `own_floor_predicate_atom` back to `None` on the mix entry, and D33's own claim on this pair
needs re-stating as origin-conditional rather than deleted — the predicate is still the right one,
its *witness on this pair* does not survive the reshape. That is a fact about D33 discovered by
D27's dry-run, and it is not in §9.2, §12.7 or §14.2.

### 15.4 The dry-run, and the control fired on the first choice

The ten fields above were applied to a deep copy of `DIMENSION_DRIFT_RESOLUTION` at the candidate
origin and run through the shipped `measure_own_drift_resolution` → `check_own_drift_resolution`:
**0 violations**.

That number is only worth reading because the same instrument refused the first attempt. The
visible-drift set is the one field here with a genuine choice in it, and the obvious choice — mirror
today's `(-370, -350, -320, -310)`, four points spanning the sighted region starting at the first
drift above the low saturation — puts **−61** in the set. `−61` differs from the baseline, so a
weaker check would take it; it is also the top member of the collapsed run `[-90, -61]`, so it reads
identically to the companies beside it. The clean tree was **RED, twice, by name**:

> `belief: drift -61d is declared VISIBLE and sits inside the collapsed run [-90, -61] -- it differs
> from the baseline but not from the companies beside it, so it evidences no resolution; declare a
> drift the sweep reads APART from its neighbours`

— and the identical violation on the mix. `−60` is the first drift outside that run, which is the
direct analogue of why `−370` replaced `−380` at the shipped origin (§ the `own_visible_drifts`
comment, atom D29). **This is why the register half is now transcription and was not before:** a
plausible reading of §14.2 lands a register that D27's own control rejects.

### 15.5 What is verified, and what is carried

* **Verified live this pass**, against the shipped checker on the candidate-origin register: every
  field in §15.2 except the two `own_draw_size_axis` ranges — `check_own_drift_resolution` returns
  `[]`.
* **Carried from §14.2, not re-measured here**: `above_edge_range` (−23, 2), `below_edge_range`
  (−61, −32), the derived null-control floor **17** and the invoice span **(30, 92)**.
  `check_belief_band_population_axis` sweeps eight population sizes and was not run this tick; step 2
  must run it, and it is the one place in the register half where a surprise is still possible.

### 15.6 What this pass did not do

The origin is unmoved and no `file_scope` file was touched. **§9.5 step 2** is now: apply §15.2's ten
fields, flip the constant, rewrite the `SCENARIO_CONSTANT_CENSUS["DD_FAILURE_WINDOW_DAYS"]`
`measured_divergence` block (`divergence_days` 310 → **0**, `never_forgets_drift_days` 0 → **1/2/2**
per seed, `scored_saturated` True → **False**, and the `cost` block's two `readable_floor_days_at_*`
maps collapse into one), invert the six defect-asserting tests, and run
`check_belief_band_population_axis`. **Step 4** (the ~30 assertions, the coupled-gap ledger row)
follows it unchanged.

---

## 16. BUILD pass 8 — 2026-08-23 (worker tick, BUILD lane) — §15.5's open item, closed

**The origin is still 400.** What this pass removes is the last place §15 said "a surprise is still
possible", so step 2 now has no measurement left in it at all.

### 16.1 The population axis at the candidate origin — no surprise

§15.5 carried `above_edge_range` and `below_edge_range` from §14.2, which measured at **n=300 only**.
`check_belief_band_population_axis` sweeps **eight** draw sizes, and its whole reason for existing
(atom D30) is that an edge measured on one population is not a property of the instrument. Carrying
a one-population reading into a declaration the axis checker will then put on trial is precisely the
class D30 exists to close, so it was run rather than assumed.

Method: `measure_belief_band_population_axis()` with `DD_FAILURE_WINDOW_DAYS` substituted to
`organ_default_failure_window_days()` = 90 **in the process, never in the tree** (the same method
§9/§12/§14/§15 used). 24 books, n = 17/24/40/60/120/300/600/1200 × seeds 7/11/23, 0.5s — the sweep is
predictor-only, which is what makes this axis askable at all.

| reading | at the candidate origin | §15.5 carried | verdict |
|---|---|---|---|
| `above_edge_range` | **(-23, 2)** | (-23, 2) | reproduces |
| `below_edge_range` | **(-61, -32)** | (-61, -32) | reproduces |
| `invoice_span_invariant` (null control) | **(30, 92)**, single-valued across all 24 books | (30, 92) | unmoved |
| derived null-control floor | **17** | 17 | unmoved |

`above_edges` (-23, -18, -3, 1, 2), `below_edges` (-61, -60, -57, -45, -32).

Two of the checker's six rules are worth naming because they are the ones a translated range would
have failed. **The declared literal must lie inside the measured range:** §15.2's
`own_saturates_above` is **+2** (`belief`) and **+1** (mix) against a measured above-range topping at
**+2**, and `own_saturates_below` is **−61** on both against a below-range bottoming at **−61** — both
declarations sit ON their range edge, so a range translated by arithmetic rather than swept would
have had no margin to be wrong in. **The edges must actually MOVE along the axis:** above-spread by
seed {7: 20, 11: 0, 23: 25}, below-spread {7: 1, 11: 29, 23: 1} — non-degenerate, so the scope stays
a claim rather than reverting to a bare number.

The **null control is the load-bearing half**: the invoice span is single-valued (30, 92) across all
24 books, so the failure-side movement above is the sample moving and not the law. Had the invoice
span moved with the origin, every reading in this table would have been draw noise — and the origin
move would have been perturbing the world rather than the company, which is the R13 wall.

### 16.2 The floor is unmoved, and that is a prediction met rather than a coincidence

`measure_belief_axis_null_control_floor` returns **17** at the candidate origin, the same value the
shipped register declares. That is the expected result and it is worth stating why: the floor is
derived off the **invoice-side** span predictor, and the invoice span is dense by construction — every
account draws every period — so it contains no dependence on the company's memory window. A floor
that HAD moved with the origin would have meant the derivation was reaching the organ, which is the
D20 tautology the floor's own comment says it exists not to be. The origin move is a company-side
change; the floor is a world-side derivation; they are independent, and now that has been observed
rather than argued.

### 16.3 What this pass did not do

The origin is unmoved and no `file_scope` file was touched — the two `file_scope` files were imported
by live pytest processes for the whole tick (§15.1's hazard, checked again rather than assumed).
**§9.5 step 2 is now pure transcription with zero open measurements**: apply §15.2's ten fields (all
ten now verified — the eight of §15.2 against the shipped checker, the two `own_draw_size_axis` ranges
here), flip the constant, rewrite the census `measured_divergence` block, and invert the
defect-asserting tests.

**One correction to §14.1/§15.6 for the next pass, and it enlarges the change set.** "The six tests"
understates it. The origin is asserted well beyond those six — `test_the_recency_contribution_is_zero_
and_that_zero_is_the_finding` asserts `contribution == {0.0}` and `scored_already_never_forgets is
True` on both belief dimensions, and §15.2's own measurements say the contributions become
(0.0189873, 0.0123457, 0.0058824) on `belief` and **(0.0033333, 0.0, 0.0)** on the mix — note the mix
keeps a 0.0 on two of three seeds, so the inverted assertion is NOT simply "now non-zero" and a
mechanical inversion would write a false claim. The next pass must count the true blast radius by
running the atom's test file with the origin substituted in-process, and treat that failure list —
not a prose count — as the change set. That measurement was started this tick and had not returned
when the tick closed.

---

## 17. BUILD pass 8 (continued) — the blast radius, MEASURED, and what it settles

§16.3 said the next pass must take step 2's change set from a measured failure list rather than a
prose count. That measurement returned within this tick, and it does not support the plan §14.1 and
§15.6 were carrying.

### 17.1 The two runs

Both are the atom's own test file, same machine, run concurrently:

| run | origin | result |
|---|---|---|
| BASELINE, at HEAD `e9e30d78b` | 400 (shipped) | **620 passed**, 0 failed, 0 errors, 829s |
| FLIPPED, origin substituted in-process via a pytest plugin | `organ_default_failure_window_days()` = 90 | **33 failed, 543 passed, 44 errors**, 771s |

The baseline is what makes the flipped run readable. A red list gathered without it would have been
attributed wholesale to the flip on the assumption that HEAD was green — an assumption this repo has
a recorded lesson about (a named red can already be fixed, or already broken, at HEAD). HEAD is
clean on this file, so **all 77 affected nodes are caused by the origin move**, with nothing
inherited and nothing to subtract.

### 17.2 What that settles: step 2 is not a bounded-tick change, and now that is a measurement

§14.1 estimated the test-side change as "the semantic inversion of the six tests that currently
assert the defect", and §15.6 repeated it. **The measured figure is 77 of 620 nodes — 12.4% of the
file — which is 12.8× the estimate.** §16.3 had already caught the estimate being wrong by one test
by reading; the sweep shows it is wrong by an order of magnitude.

This is the fact seven previous passes did not have. §14.1's reasoning was sound given its inputs —
it declined the flip because the change was too big for a tick — but it was arguing from an estimate
of six. The decision to defer was right for a reason that turns out to be far stronger than stated.
And §15.1's counter-argument (that re-attempting the same shape is the R3 defect) is now answerable
without either persisting or deferring again: **the shape was never the problem — the scope was.**
Attempting this flip inside a bounded tick was not going to succeed on the seventh attempt or the
tenth, and the loss mode each time (uncommitted work in a shared tree) is a consequence of starting
work that cannot finish inside the window, not of insufficient preparation.

**So the recommendation this pass makes, and acts on: step 2 stops being drawn as a bounded worker
tick.** It needs either a dedicated long session, or a decomposition that makes it landable in
pieces. The second is worth investigating first and this pass did not do it — the constraint that
makes the flip atomic is `check_scored_window_provenance` firing four ways the moment the constant
moves (§9.4), and whether that control can legitimately admit a declared in-progress origin move is a
design question, not a mechanical one. Recording it as the open question rather than guessing at it.

What is NOT in doubt any more is the register half. §15.2's ten fields are verified against the
shipped checker, §16.1's two range fields are verified against the population axis, and the null
control and derived floor are both confirmed unmoved. **Every measurement step 2 needs has now been
taken.** What remains is 77 test nodes of semantic rewriting, and that is bounded, known, and
enumerable — the list is below.

### 17.3 The 33 named failures

They are not a homogeneous block, which is the other reason a mechanical inversion would have gone
wrong. Four distinct kinds are present:

* **The atom's own defect-assertions** — `test_the_scored_company_sits_outside_the_band_it_is_graded_on`,
  `test_never_forgets_drift_is_derived_from_the_book_and_is_zero_today`,
  `test_the_recency_contribution_is_zero_and_that_zero_is_the_finding`,
  `test_the_reshape_moves_no_published_figure`. These invert to the criterion-1 claim with the 400 as
  their mutation, as §14.1 described.
* **D30/D33 sibling-atom claims measured on this pair** — `test_the_two_belief_figures_do_not_share_a_
  resolution`, `test_bit_equality_counts_a_difference_no_consumer_can_render`,
  `test_a_predicate_divergence_with_no_owner_fires_the_control`, `test_the_belief_edges_move_on_the_
  draw_size_alone`, `test_the_band_shipped_before_this_repair_is_false_at_the_derived_floor`. §15.3
  already found that D33's two-predicate divergence is an artefact of the saturated origin and does
  not survive the reshape; these are the nodes that carry that, and they are **another atom's claims**
  — they need re-stating as origin-conditional, not deleting, and that is a cross-atom decision D27
  does not get to take alone.
* **The null control itself** — `test_the_invoice_span_is_the_null_control_and_does_not_move`. §16.1
  measured the invoice span as unmoved at the candidate origin, so this failing is a signal worth
  reading carefully in the next pass rather than inverting: the sweep says the law does not move, and
  a test asserting exactly that is red. Most likely the node pins the span against the *declaration*
  rather than the measurement, but that is **inferred, not observed** — it was not opened this tick.
* **Publication surfaces** — `test_cli_runs_and_prints_all_three_gaps`, `test_cli_write_ledger_
  publishes_the_measured_note_not_a_retired_one`, `test_the_memory_resolution_caveat_travels_with_both_
  numbers`, `test_the_census_caveat_travels_with_both_belief_figures`. Every published caveat states
  the saturation in prose; the reshape falsifies the sentence, not just the number, which is R11
  territory and is where step 4's ~30 assertions live.

### 17.4 The 44 errors are NOT named, and that is a gap in this record

§17.3 enumerates the 33 FAILURES. It does not enumerate the **44 errors**, and nothing above should
be read as if it did. The cause is mundane and worth writing down so the next pass does not repeat
it: the run used `-rf`, which reports failed nodes only. The summary line counts the errors but the
short-summary section never lists them, so their identities were never captured.

A re-run with `-rEf` was started this tick and was **killed unfinished** — it reached 42 of 620 nodes
in 4.5 minutes under CPU contention from two other live suites, i.e. roughly an hour to complete,
which is past this tick's window. Leaving it running past the tick would have been an orphan process
contending with the operational suite for no reader, so it was stopped deliberately rather than
abandoned.

**To name them, next pass:**

```
PYTHONPATH=<dir-with-flip_plugin>:. python3 -m pytest tests/tools/test_couple_w2_11_d5.py \
    -p flip_plugin -q --no-header -rEf --tb=no
```

where `flip_plugin.py` is a two-line `pytest_configure` setting
`pair.DD_FAILURE_WINDOW_DAYS = pair.organ_default_failure_window_days()` — the origin substituted in
the PROCESS, never in the tree, which is what let this be measured at all while both `file_scope`
files were imported by live suites.

**Why the identities matter rather than the count.** 44 errors against 33 failures is a suspicious
ratio for a change that edits one integer. An ERROR is a fixture blowing up, not an assertion
disagreeing, so the likely shape is a small number of module-scoped fixtures raising and taking their
whole dependent set with them — `own_drift_resolution` and `recency_contribution` are both
module-scoped and both re-score at the origin. If that is what it is, the 44 collapse to perhaps two
or three root causes and the real remaining work is **smaller than 77 nodes implies**. If instead the
errors are spread across many independent fixtures, it is larger. **That is INFERRED, not observed** —
no error traceback was read this tick, and the sizing in §17.2 and in the atom's `size_basis`
deliberately takes the conservative reading (77 nodes) rather than the optimistic one. A pass that
names the errors may legitimately re-size this atom DOWN; that would be evidence arriving, not the
dial being tuned.

---

## 18. BUILD pass 9 — 2026-08-23 (worker tick, BUILD lane) — §17.2's open question closed, §17.4's errors root-caused

This pass took the two items §17 left for its successor and closed both. It did **not** attempt the
flip, and the origin is still 400 — but the reason to defer it has changed, because the size the
deferral rested on is now measured to be wrong in the *other* direction.

### 18.1 The open question, answered: NO — and it was aimed at the wrong constraint

§17.2 recorded the open question as *"whether `check_scored_window_provenance` can legitimately admit
a declared in-progress origin move"*, naming that control as **"the constraint that makes the flip
atomic"**. Measured this pass (`observed-with-evidence`, origin substituted in-process, never in the
tree, seed 7, n=300, at HEAD `2211cf534`):

| field | at shipped origin | at candidate origin |
|---|---|---|
| `organ_default_window_days` | 90 | 90 |
| `harness_window_days` | 400 | **90** |
| `divergence_days` | 310 | **0** |
| `never_forgets_drift_days` | 0 | **1** |
| `scored_saturated` | `True` | **`False`** |
| `check_scored_window_provenance` | **0 violations** | **4 violations** |

The four violations are the four §9.4 predicted. But reading them settles the question, because
**each one prints its own replacement value**:

```
DD_FAILURE_WINDOW_DAYS: declares harness_window_days=400 and this run measures 90 -- re-derive it ...
DD_FAILURE_WINDOW_DAYS: declares divergence_days=310 and this run measures 0 -- re-derive it ...
DD_FAILURE_WINDOW_DAYS: declares never_forgets_drift_days=0 and this run measures 1 -- re-derive it ...
DD_FAILURE_WINDOW_DAYS: declares scored_saturated=True and this run measures False -- re-derive it ...
```

So satisfying this control after the flip is **a four-value edit to one dict literal**, whose values
the control itself hands you. It costs roughly ten lines of the flip commit. It is not a design
question, it does not need an escape hatch, and **it was never what made the flip atomic** — §17.2
misattributed the constraint. The atomicity lives entirely in the test file (§18.2, §18.4).

`never_forgets_drift_days = 1` at the candidate origin is **new** — §15.2 carried the per-seed
headroom (−1/−2/−2) but the census field itself had never been read at the flipped origin. With it,
every field `check_scored_window_provenance` compares is now measured on both sides, so step 2's
census half needs no further measurement at all.

**And the concession would have been wrong on its own merits.** The four fields are re-derived live
on every check call, from the organ's signature, this module's constant and a live book. Admitting a
*declared* in-progress value for a field the control can measure **for free** is the FAIL-OPEN shape
R15 names, and it would make the control answer from the declaration instead of the measurement —
the TAUTOLOGY pattern one register over. This module already draws that line in the right place and
says so: the `cost` block is declared-and-dated *because* re-deriving it costs two ~70s sweeps
(§17 / lines 8002-8005), while the live fields are live *because* they do not. An in-progress flag
would move a cheap field to the expensive side of a line drawn on expense. Recommendation, taken:
**leave `check_scored_window_provenance` exactly as it is.**

### 18.2 The 44 errors: ONE root cause, not 44 — and §17.4's inference was half wrong

§17.4 asked for the errors to be named by a full `-rEf` sweep and predicted ~1 hour. This pass got
the answer in **seconds** by a cheaper route that goes at the stated hypothesis directly: §17.4
inferred the errors were "a small number of module-scoped fixtures raising and taking their whole
dependent set with them", so rather than re-run 620 nodes, **evaluate the module-scoped fixtures
themselves at the candidate origin**. The test file has 18; 16 take no arguments and were called
directly:

| result | fixtures |
|---|---|
| **OK (14)** | `_books`, `_pre_d22_ageing_scorer`, `axis_floors`, `band_population_axis`, `belief_band_axis`, `component_walk`, `constant_census`, `detection_resolution`, `drift_resolution`, `interior_change_points`, `reader_walk`, **`recency_contribution`**, `recon_saturation`, `resolution_floors`, `stress_axis` |
| **RAISED (2)** | `own_drift_resolution`, `caveat_coverage` |
| not evaluated (2) | `retired_door`, `door_walk` — take arguments |

Both raise **the same exception, from the same cause**:

```
ValueError: organ_failure_window_drift_days=-370 takes the company's lookback window to
-280 days -- a negative memory is not a company this harness can build
```

§17.4's shape is therefore **confirmed as observed**: the 44 errors are two fixtures taking their
dependents down, and behind the two fixtures is **one** root cause. Its two specific guesses fare
less well and are corrected here — `own_drift_resolution` was right, **`recency_contribution` was
wrong** (it evaluates cleanly at the candidate origin), and `caveat_coverage` was not on the list.

**The full `-rEf` sweep §17.4 asked for then completed in-tick and confirms this exactly.** It ran
to `33 failed, 543 passed, 44 errors in 770.26s`, reproducing §17.1's flipped counts
(33/543/44) bit for bit, so the population is stable across runs. Attributing each of the 44 error
nodes to the fixture it requests — resolving indirect requests through intermediate fixtures —
gives:

| fixture | error nodes |
|---|---|
| `own_drift_resolution` | 22 |
| `caveat_coverage` | 22 |
| requesting both | 0 |
| **unattributed** | **0** |

Every one of the 44 is accounted for by the two fixtures, and both fail on the same `−370` probe.
The fixture probe's answer and the sweep's answer agree completely — which is what makes the cheap
route trustworthy here rather than merely faster.

### 18.3 NEW FINDING — the caveat probe grid is origin-relative, and its own justification dissolves at the new origin

The root cause is not a fixture defect. `CAVEAT_COVERAGE_PROBES` (`tools/couple_w2_11_d5.py:4424`)
probes the memory knob at `(-370, -350, -310)`, and `build_scenario` computes
`window_days = DD_FAILURE_WINDOW_DAYS + organ_failure_window_drift_days` (line 612) with a
fail-closed refusal below zero (line 613). At the shipped origin `400 − 370 = 30`, a buildable
company. At the candidate origin `90 − 370 = −280`, and the guard **correctly** refuses it.

The probe grid is stated in **absolute days** while being **origin-relative** in meaning, and the
constant's own comment says why it is large:

> *"The memory knob's readable band is far from zero on this book (atom D29/D30: everything from
> −308 up is one number), so ±1 would probe an inert region and hand every cell a free pass."*

**The probes are large precisely BECAUSE the origin is saturated — which is the defect the reshape
removes.** So the same change that makes `−370` unbuildable also destroys the reason it was chosen:
§15.2 measures the readable resolution floor at the candidate origin as **4 days on both dimensions
and every seed**, so at origin 90 a small probe lands in a *resolving* region, not an inert one, and
the memory knob stops needing a special case at all — it would take the same shape as its two
siblings (`organ_terms_drift_days`, `organ_reconciliation_drift_days`, both `(-1, 1, 5)`).

This is a constraint no earlier section states, and it is the reason a mechanical inversion of the
77 nodes would have gone wrong: **part of the change set is re-choosing a probe grid, not re-deriving
a number.** Candidate `(-1, 1, 5)`, on the floor-4 measurement and the sibling convention —
**INFERRED, not measured. It was not swept this tick and must be before it is taken**, since a probe
of ±1 sits *below* the measured floor of 4 and could reintroduce exactly the free pass the original
comment guarded against. Naming the candidate so the next pass sweeps a hypothesis rather than
searching.

### 18.4 What this settles about the decomposition

§17.2 asked for "a decomposition that makes it landable in pieces" and named the wrong obstacle.
With the control cleared (§18.1) and the errors reduced to one cause (§18.2), the remaining change
set is:

1. **The probe grid** — one dict literal, once §18.3's candidate is swept. Clears all 44 errors.
2. **The census** — four values, printed by the control itself (§18.1).
3. **~33 failing assertions**, which are the real work and are **not** homogeneous (§17.3).

And the axis that makes (3) landable in pieces is visible in the nodes themselves. Within a single
test, some assertions already track the origin symbolically and others pin the saturated origin's
coordinates — `test_the_scored_company_sits_outside_the_band_it_is_graded_on` asserts
`scored_company_window_days == pair.DD_FAILURE_WINDOW_DAYS` (origin-agnostic, survives the flip) two
lines after `scored_company_headroom_days == 308` (pins the 400). File-wide the split is **48
hard-coded origin literals against 31 symbolic references**. So the decomposition is: **restate each
defect-assertion as the LAW plus an origin-conditional coordinate** — e.g. `is_inert ==
(headroom_days >= 0)` rather than `is_inert is True` — which is green at the CURRENT origin, lands
in as many commits as one likes while the origin is still 400, and reduces the flip itself to the
one-line constant move plus §18.4(1)–(2). That is the piecewise landing §17.2 wanted, and it needs
no concession from any control.

### 18.5 Re-sizing, and what this pass did not do

§17.4 said naming the errors "may legitimately re-size this atom DOWN; that would be evidence
arriving, not the dial being tuned." It has: the conservative 77-node reading is superseded by
**~33 assertion rewrites + 2 dict literals**, with 44 of the 77 collapsing to one grid decision.
R12/G5 — this is a DIAL informing decomposition and remaining effort, never a gate and never a
target.

**Not done, deliberately:** the origin is NOT flipped, no level moved (D27 stays at 0), the probe
grid is NOT edited, and §18.3's candidate is NOT swept. The full `-rEf` sweep was left running to
completion rather than killed a second time (§17.4 had abandoned it once already); it finished
inside this tick at 770s and its result is folded into §18.2 rather than left as a loose end. The
XL label is deliberately RETAINED despite the re-size — see the atom's `size_basis` for why
§18.3's unmeasured probe grid is the reason to wait before dropping it to L.

**Method note for the next pass:** the fixture-evaluation route (§18.2) answered in seconds what
§17.4 budgeted an hour for, because it went at the stated hypothesis instead of re-measuring the
whole population. Where a sweep is being re-run to identify a *cause*, check whether the cause can be
evaluated directly first.

## 19. BUILD pass 10 — 2026-08-23 (worker tick, BUILD lane) — §18.3's probe grid SWEPT

§18.3 named `(-1, 1, 5)` as a candidate probe grid, marked it **INFERRED, not measured**, and said it
"must be swept before it is taken" — and the atom's `size_basis` named exactly that unswept grid as
the one honest reason the XL label was retained after §18.5's re-size. This pass swept it. The origin
is still 400, no code moved, and the grid is **not** edited (§19.4 says why it cannot be, yet).

All figures below: `observed-with-evidence`, n=300, seeds 7/11/23, origin substituted in-process via
`setattr` on the module and restored in a `finally` (never in the tree), at HEAD `46d1984f5`.

### 19.1 The sweep: where the memory knob actually reaches at the candidate origin

Every published dimension, scored at drift `k` against its own base at the candidate origin, compared
with this module's only equality on a published figure (`_same_reading`), `k ∈ ±1…±12`. Cells give
**how many of the three seeds move**:

| dimension | −12…−4 | −3 | −2 | −1 | +1 | +2 | +3…+12 |
|---|---|---|---|---|---|---|---|
| `ageing` | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| `belief` | 3 | 1 | 1 | **1** | **2** | 3 | 3 |
| `belief_population_mix` | 3 | 1 | 1 | **0** | **2** | 2 | 2 |
| `detection` | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| `detection_latency` | 0 | 0 | 0 | 0 | 0 | 0 | 0 |

**§18.3's stated reason is refuted by its own numbers.** The inference was that a ±1 probe "sits
below the measured floor of 4 and could reintroduce the free pass". It does sit below that floor —
and it moves the figure anyway, because the two statistics ask different questions. §15.2's floor of
4d is a **floor over all three seeds** (the smallest error readable on *every* seed); `moves` is a
**disjunction over seeds and probes** (did *anything* shift *anywhere*). A 4-day all-seed floor is
perfectly compatible with a 1-day single-seed movement, and that is what the book does.

### 19.2 The candidate grid, through the shipped function, at the post-flip origin

Not the sweep above re-read — `measure_published_figure_caveat_coverage` itself, with
`DD_FAILURE_WINDOW_DAYS = 90` and `organ_failure_window_drift_days: (-1, 1, 5)`, against the shipped
grid at the shipped origin as the control. The `moves` column, which is the only column the register
declares:

| dimension | shipped origin + `(-370,-350,-310)` | candidate origin + `(-1,1,5)` |
|---|---|---|
| `belief` | True, at all three | True, at all three |
| `belief_population_mix` | True, at all three | True, at `(1, 5)` |
| `ageing` / `detection` / `detection_latency` | False | False |

**The reach map is identical, cell for cell.** So the grid swap costs **zero edits to
`PUBLISHED_FIGURE_CAVEAT_CONTRACT`** — §18.4's item (1) is one dict literal and nothing downstream of
it, which is one fewer thing in the flip commit than the decomposition assumed.

Two smaller things, both checked rather than assumed:

- `belief_population_mix` is inert at −1 on every seed (its smallest negative is −2), so that cell is
  carried by the positive leg alone. Not a free pass — `moves` is a disjunction and `+1`/`+5` both
  move it — but the negative probe does no work on one of the two reached dimensions, which is a fact
  about this grid worth having on the record before someone reads `(-1, 1, 5)` as symmetric.
- Three cells move `step_days: None → {7: 0.0, 11: 0.0, 23: 0.0}`, because the step branch runs only
  when both −1 and +1 are in the grid. **Inert to the checker**: `check_published_figure_caveat_coverage`
  reaches the step comparison only after `if not row["moves"]: continue`, and neither belief cell
  declares a `published_step_component` at all (both are `BOOK`-sourced with a
  `published_floor_component`). The value is also the honest one and matches what both sibling knobs
  already publish on their own inert cells.

### 19.3 The whole control, dry-run at the candidate origin — and it is NOT in the 33

`check_published_figure_caveat_coverage` with the candidate grid at the candidate origin returns
**2 violations**, and neither is about the grid:

```
belief/organ_failure_window_drift_days: publishes a resolution floor of 310d and the sweep measures 4d ...
belief_population_mix/...: publishes a resolution floor of 314d and the sweep measures 4d ...
```

Those are the *rendered* `measured_resolution_floor_days`, which `score_triad` stamps straight from
`DIMENSION_DRIFT_RESOLUTION[dim]["own_readable_resolution_floor_days"]` — i.e. they are §15.2's
register half, already measured (4/4) and already dry-run clean at §15.4. Re-running the check with
§15.2's two values applied to a patched register: **0 violations**. So this control is **green at the
candidate origin** once step 2's register edit lands, and it is not one of §17.3's 33.

**R15 — the grid still discriminates at the new origin,** proven by mutation on the same measurement:

| mutation | result |
|---|---|
| `belief` cell declared `moves: False` (a reached cell called inert) | 1 violation: *declared moves=False but MEASURED moves=True at (-1, 1, 5)* |
| `ageing` cell declared `moves: True` (an unreached cell called moving) | 1 violation: *declared moves=True but MEASURED moves=False at ()* |

Both directions fire, which is what "the grid hands no free pass" has to mean to be worth anything.

### 19.4 NEW FINDING — the grid and the origin are a matched pair, and the vacuity guard proves it

The candidate grid cannot be landed *before* the flip, and this is not a preference: the candidate
grid at the **shipped** origin returns **7 violations**, five of them the `probe_bit` guard —

> *"the probe moved NOTHING on any published dimension — an inert counterfactual company certifies
> every `moves: False` in its column for free"*

— plus the two belief cells reading `declared moves=True but MEASURED moves=False`. That is precisely
the free pass §18.3 feared, arriving from the opposite direction: **the old grid is invalid at the new
origin (fail-closed, §18.2), and the new grid is invalid at the old origin (probe_bit, here).** Each
is unbuildable without the other, so the dict literal is genuinely inside the flip commit rather than
landable ahead of it — and the vacuity guard that makes the second half true is a control this module
already had, firing on its own named defect without being asked to.

### 19.5 Re-sizing, and what this pass did not do

The `size_basis`'s stated reason for retaining **XL** after §18.5's re-size was §18.3's unswept grid.
It is now swept, the candidate is confirmed, and the change set did not enlarge — it shrank by the
register edits §19.2 shows are not owed. **Re-sized XL → L** on that evidence (R12/G5: a DIAL
informing decomposition and remaining effort, never a gate and never a target). The remaining step 2
is ~33 assertion rewrites + 2 dict literals, all of them measured.

**Not done, deliberately:** the origin is NOT flipped, `CAVEAT_COVERAGE_PROBES` is NOT edited (§19.4),
no level moved (D27 stays at 0), and §18.4's piecewise route — restating each defect-assertion as the
LAW plus an origin-conditional coordinate, green at the current origin — is untouched and remains the
next pass's work.

---

## 20. BUILD pass 11 — 2026-08-24 (worker tick, BUILD lane) — §18.4's piecewise route STARTED

§19.5 handed this pass one item: the piecewise route — *restate each defect-assertion as the LAW plus
an origin-conditional coordinate, green at the current origin* — "untouched and remains the next
pass's work." This pass **started it and landed the first increment**. The origin is still 400, the
reshape is still not landed, no level moved (D27 stays at 0), and `CAVEAT_COVERAGE_PROBES` is still
untouched (§19.4 — it cannot move before the flip).

**This is the first pass on this atom since §12 to change a `file_scope` file, and the first ever to
change one in a way that is green at BOTH origins.** That is the whole point of the route: eleven
passes have measured, and the reason none could land the flip is that every measured edit was only
valid on one side of it. An origin-agnostic assertion is valid on both, so it lands now.

All figures `observed-with-evidence`, at HEAD `2598ca8c0` plus this pass's edit; the candidate origin
is substituted **in the process** via a `pytest_configure` plugin on `PYTHONPATH`, never in the tree
(§17.4's method, unchanged).

### 20.1 The two nodes restated, and what each now says

| node | pinned before | says now |
|---|---|---|
| `test_the_scored_company_sits_outside_the_band_it_is_graded_on` | `is_inert is True`, `headroom == 308` | `headroom == WINDOW − 92`, `is_inert == (WINDOW ≥ 92)` |
| `test_never_forgets_drift_is_derived_from_the_book_and_is_zero_today` | `drift == 0`, `saturated` true | `drift == max(0, 91 − WINDOW)`, `saturated is (WINDOW ≥ 91)` |

`WINDOW` is `pair.DD_FAILURE_WINDOW_DAYS` — the origin, symbolically. The literals are the **book's**
coordinates, and each is asserted independently in the same node (`measured_oldest_age_days == 92`,
`oldest_event_age_days == 91`) so the law is not checked against a number the law itself produced.

### 20.2 Green at both origins, which is the acceptance test for this route

```
shipped origin (400):   2 passed in 0.99s
candidate origin (90):  2 passed in 0.37s   (-p flip_plugin)
```

Before this pass both nodes were in §17.3's 33. **They are not any more**, and they did not have to
wait for the flip to stop being.

And the two new module constants did not disturb their neighbours: the whole
`census|never_forgets|window_resolution|saturat|band` selection over this file — 81 nodes, every one
that reads either coordinate — is **81 passed, 0 failed, 376.73s** at the shipped origin.

### 20.3 R15 — the restatement did not weaken the control

A restatement is exactly the move that can quietly turn an assertion into a tautology (the law
re-derived from the value it checks). Four mutations, run against the restated nodes, each on the
side of the origin where it is the honest defect:

| mutation | origin | result |
|---|---|---|
| `headroom` read off the YOUNGEST band edge instead of the oldest | 400 | **1 failed** |
| `scored_company_is_inert` hard-wired `True` | 90 | **1 failed** |
| `never_forgets_drift_days` returns a constant `0` | 90 | **1 failed** |
| `saturated` hard-wired `True` | 90 | **1 failed** |

The last three are the specific defect this atom exists to name — *a company that never forgets,
reported as though it had been tested* — and all three now fire from the test side at the origin
where they are wrong, which the pinned form could not do at all.

### 20.4 NEW FINDING — there are TWO book coordinates, not one, and they differ by a day on one seed

The obvious reading of §18.4 is that the flip-invariant coordinate is "the top of the book", one
number. It is two, and they are the D30 edge-setting-population distinction arriving on the test side:

| coordinate | seed 7 | seed 11 | seed 23 |
|---|---|---|---|
| oldest **invoice** age (the band top) | 92 | 92 | 92 |
| oldest **observed failure** age | **91** | 92 | 92 |

The invoice side is dense by construction — every account draws every period — so it reaches the
constants' band on every seed. A *failure* has to **land** on the extreme invoice, which is a draw,
so it is per-seed and one day short on seed 7. A restatement that used the band top for both would be
green on two seeds of three. Recorded as `_INVOICE_BAND_TOP_DAYS` (scalar) and
`_OLDEST_OBSERVED_FAILURE_AGE_DAYS` (per-seed dict) with the reason on the constants, so the next
increment does not have to rediscover it. Measured at both origins and identical at each — which is
what qualifies them as anchors at all.

### 20.5 What this pass did not do

The origin is **not** flipped. 31 of §17.3's 33 remain pinned — including all four publication
surfaces (§17.3's R11 group, where the *prose* states the saturation and not just the number) and the
five D30/D33 sibling-atom claims (§15.3 — a cross-atom decision D27 does not take alone). The
probe-grid dict and the census values stay inside the flip commit (§19.4). `recency_contribution`'s
node was **examined and deliberately left**: its law — *the contribution is zero exactly when the
scored company already never forgets* — is sound, but its `readable`/`epsilon` assertions need a
measurement at the candidate origin that this tick did not take, and inferring them would put an
unmeasured number on the record. Named here rather than guessed.

**The route is now proven rather than proposed**, and the remaining 31 land the same way, in as many
commits as anyone likes, while the origin is still 400.

---

## 21. BUILD pass 12 — 2026-09-30 (worker tick, BUILD lane) — two more nodes off §17.3's list, and a cache that faked the finding

Carries on §20's piecewise route. The origin is still 400, the reshape has not landed, no level
moved (D27 stays at 0), and `CAVEAT_COVERAGE_PROBES` has not been touched (§19.4). The candidate
origin was substituted in the process through the §17.4 `flip_plugin`, never in the tree.

### 21.1 The null control: §17.3's inference is now an observation

§17.3 guessed that `test_the_invoice_span_is_the_null_control_and_does_not_move` fails at the
candidate origin because it pins the register, not the span. **Confirmed.** At 90, both span
assertions (`invoice_spans == ((30, 92),)` and the constants' predictor) pass. The red comes from
the node's last line, `check_belief_band_population_axis(...) == []`, and the eight violations it
returns are all register edges ("declares its above edge inside [-333, -308] … the sweep read
[-23, 2]"), none from the NULL CONTROL leg. The node is now split in two:

* the null-control node keeps the span assertions, plus only the check's `NULL CONTROL` violations.
  It is green at both origins.
* the new `test_the_belief_register_describes_the_draw_size_axis` keeps the full `== []`. It is red
  at 90 by design: its replacement values are §15.2/§16.1's, and it belongs to the flip commit.

So the list does not get shorter here. One node leaves it and one joins. What changes is that the
remaining node now means only the register half.

### 21.2 NEW FINDING — the drift cache is keyed without the origin, so a two-origin process reads the finding back

`_OWN_RESOLUTION_SCORES` caches one built company per `(n, seed, knob, k)`. `k` is a drift *from*
`DD_FAILURE_WINDOW_DAYS`, and the origin was not part of the key. A process that measures at 400 and
then substitutes 90 therefore gets the 400 company back for `k = 0`, and scores it against a
freshly built never-forgets company. Measured this pass, seed 7, `measure_recency_contribution`:

| process | belief contribution at 90 | readable |
|---|---|---|
| 400 first, then 90 (stale key) | 0.0 / 0.0 / 0.0 | False |
| 90 alone (fresh process) | **0.0190 / 0.0123 / 0.0059** | **True** |

The first row is exactly what this atom complains about, *the scored company reads as the
never-forgets company*, and here the cache produced it. pytest runs were never exposed: the plugin
substitutes at configure time, before anything fills the cache. A scratch script that measures both
origins in one process was exposed. §14.2/§15.2's figures were taken in scratch scripts, but their
belief numbers match the fresh 90 reading (0.1709 − 0.1519 = 0.0190 at seed 7), so there is no
evidence that any of them hit the cache. The origin is now part of the key in all three runners.
`test_the_recency_cache_does_not_hand_one_origin_the_other_origins_company` warms the cache at 400,
switches to the organ default, and asserts belief is readable. **R15:** re-executing the module
with the old key reds it, reading contribution `{7: 0.0}`.

### 21.3 `recency_contribution` restated — the measurement §20.5 said it lacked, taken

Taken at 90 in a fresh process:

| | seed 7 | seed 11 | seed 23 |
|---|---|---|---|
| never-forgets drift | 1 | 2 | 2 |
| `belief` contribution | 0.01899 | 0.01235 | 0.00588 |
| `belief_population_mix` contribution | 0.00333 | −1.4e-17 | 0.0 |

`belief` is readable on every seed. `belief_population_mix` is not: one day of lost memory drops a
few failures and they cross no mix tier on seeds 11 and 23. The converse of "drift 0 ⇒ contribution
exactly 0" therefore holds per figure and not per dimension. The node now asserts:

* `never_forgets_drift_days == max(0, _OLDEST_OBSERVED_FAILURE_AGE_DAYS[s] − WINDOW)`;
* on every seed where that is 0, the contribution is exactly 0.0 in both dimensions. When that holds
  on all seeds, `scored_already_never_forgets` is True and `readable` is False (this is today's
  finding);
* when any seed forgets, at least one belief figure is `readable`. This is the reshape's own claim,
  and it is not keyed to a dimension name.

Green at both origins. **R15, six mutations, each fired on the origin where it is the real defect:**
at 400, `readable` forced True, contribution forced 0.01, `scored_already_never_forgets` forced
False; at 90, `readable` forced False, contribution forced 0.0, never-forgets drift forced 0. Each
gives 1 failed.

### 21.4 Where §17.3 stands

The four defect-assertions: two restated in §20, one here (`recency_contribution`). One is left,
`test_the_reshape_moves_no_published_figure`. The null control is done in the sense of §21.1. Not
touched: the five D30/D33 sibling claims and the four publication surfaces.

---

## 22. BUILD pass 13 — 2026-09-30 (worker tick, BUILD lane) — the last defect-assertion, and a class control the frame never listed

The origin is still 400, no level moved, `CAVEAT_COVERAGE_PROBES` untouched (§19.4). The candidate
origin was substituted in the process through the §17.4 `flip_plugin`, never in the tree.

### 22.1 `test_the_reshape_moves_no_published_figure` restated

At 90 it red on `all(co_read_dimensions_identical)`: `belief` and `belief_population_mix` read
different figures at the two reading dates. Measured through the shipped
`measure_detection_resolution`, seed 7, n=300, window set by `organ_failure_window_drift_days`:

| window | detection | detection_latency | belief | belief_population_mix |
|---|---|---|---|---|
| 400 | same | same | same | same |
| 92 | same | same | same | same |
| 91 | same | same | same | same |
| 90 | same | same | **moves** | **moves** |
| 89 | same | same | **moves** | **moves** |

The edge is exactly the book's oldest observed failure (`_OLDEST_OBSERVED_FAILURE_AGE_DAYS[7]` = 91).
The node now builds three arms at explicit windows (the shipped origin, 91 and 90), so both sides of
the edge run whatever the origin is, and asserts: non-memory dimensions always identical; memory
dimensions identical when the window reaches the oldest failure; at least one of them moves when it
does not. It also asserts that both sides were reached. Green at 400 and at 90. **R15, three
mutations through a wrapping plugin:** co-read forced all-identical (fires on the 90 arm), `belief`
forced to move (fires on the 400 arm), `detection` forced to move (fires on the 400 arm). All three
give 1 failed.

That was the last of §17.3's four defect-assertions.

### 22.2 NEW FINDING — the as_of class control reds at the flip, and the frame never listed it

`test_every_dimension_declares_its_as_of_contract_and_the_declaration_is_measured` fails at 90:
`belief: declared gap_is_as_of_invariant=True but the gap went 0.1866 -> 0.4925 over 60 days`
(n=250, `_SEED`). No section of this frame names the as_of contract. §17.3's "33 named failures"
names 14 of them, so this one sat in the unnamed remainder.

It is not a test rewrite. `DIMENSION_AS_OF_CONTRACT["belief"]["why"]` says the invariance holds
because "a failure does not resolve itself by the clock moving". That is true of the TRUTH side. On
the company side the failure window is a clock, and past the book's span it only looked frozen.
After the flip the declaration is false for both belief dimensions. The control's only sanctioned
exemption shape ("VIOLATES THE INVARIANT" plus naming D11) does not fit either. That shape is for a
figure that moves because of the question's timing. This one moves because of a company parameter,
which is the thing the dimension exists to grade. The flip commit therefore has to decide between:

* a third contract kind: the gap moves on a company-side clock and that movement is a measurement,
  keyed to the saturation property (§22.1's edge) rather than a literal; or
* a truth side that also forgets. That would change what "at risk" means, and it is not D27's
  decision.

The first is recommended. §22.1 already shows the property is sharp and measurable. Two knock-ons
follow. `DETECTION_CO_READ_DIMENSIONS` is derived from the declaration, so the belief dimensions
leave the co-read set by themselves and §22.1's memory arm goes empty. The node stays green because
its non-memory arm and the both-sides guard do not depend on them. Second, R15 must-fire #1
(`test_the_as_of_class_control_fires_when_a_clean_dimension_starts_drifting`) poisons `belief` on
the premise that it "measures clean today". After the flip it has to poison a dimension that still
measures clean.

### 22.3 Where §17.3 stands

Defect-assertions: 4 of 4 restated. Null control: done (§21.1). Still pinned: the five D30/D33
sibling claims, the four publication surfaces, the register node (§21.1) and, new here, the as_of
class control (§22.2). That last one belongs to the flip commit with the contract edit.

---

## 23. BUILD pass 14 — 2026-09-30 (worker tick, BUILD lane) — §22.2's third contract kind, landed ahead of the flip

The origin is still 400, no level moved, `CAVEAT_COVERAGE_PROBES` untouched (§19.4). The candidate
origin was substituted in the process through the §17.4 `flip_plugin`, never in the tree.

### 23.1 The contract kind, and why it can land now

§22.2 recommended a third as_of contract kind keyed to the saturation property. It lands as a field
rather than a new boolean: `gap_invariance_condition = COMPANY_WINDOW_COVERS_THE_BOOK` on `belief` and
`belief_population_mix`, evaluated by `as_of_gap_invariance_expected`, which reads
`measure_belief_window_resolution(records, later, consumer.dd_failure_window_days)["saturated"]` at
the LATER reading date (the older of the two ages, so covered there means no failure changed side).
Both `why` strings now say what is true: the truth side is settled facts, the company side is a
window, and a window is a clock.

Measured n=250, sweep 60 days, one process per origin:

| seed | oldest failure | 400: saturated at later / belief / mix | 90: saturated at later / belief / mix |
|---|---|---|---|
| 101 | 92 | True / same / same | False / 0.1866→0.4925 / 0.088→0.264 |
| 7 | 91 | True / same / same | False / 0.1769→0.4923 / 0.084→0.256 |
| 11 | 92 | True / same / same | False / 0.1884→0.5000 / 0.100→0.272 |
| 23 | 92 | True / same / same | False / 0.1522→0.5000 / 0.084→0.276 |

Detection and detection_latency are identical at both origins on every seed.

The class control now asserts: covered ⇒ that gap is identical (per dimension, as before);
uncovered ⇒ at least one conditional gap moved (not per dimension: a failure ageing out may cross no
tier, so demanding each would overclaim). The exemption leg reads the raw declaration, so the
condition cannot be used to buy a D11-style exemption. Must-fire #1 now poisons `detection`, the
dimension that is unconditionally clean. New node
`test_the_belief_invariance_condition_is_reachable_on_both_sides_and_is_not_a_free_pass` builds
explicit windows (oldest + 60 and oldest − 1), so both branches run at any origin, and strips the
condition to show the class control's equality reds on the uncovered arm.

**Green at 400 and at 90**, 6 passed each. **R15, two evaluator mutations × two origins:**

| mutation | at 400 | at 90 |
|---|---|---|
| condition ignored (always covered) | 1 failed (new node only) | 2 failed (class control + new node) |
| condition never holds | 2 failed (class control's "none moved" leg + new node) | 1 failed (new node only) |

"Condition ignored" at 400 is caught only by the explicit-window node. The class control cannot see
it at the saturated origin, which is this atom's finding in miniature.

### 23.2 CORRECTION to §22.2 — the co-read knock-on does not happen, and would have red §22.1's node

§22.2 said `DETECTION_CO_READ_DIMENSIONS` "leaves the belief dimensions by itself" and that §22.1's
node "stays green because its non-memory arm and the both-sides guard do not depend on them". The
second half is wrong: that node's uncovered-arm assertion is `not all(identical[d] for d in memory &
set(identical))`, and over an empty intersection `all(...)` is True, so it would red. Under the
design landed here nothing leaves the set: `gap_is_as_of_invariant` stays True on both belief
entries and the co-read derivation is unchanged, so §22.1's node is untouched.

What the flip commit still owes on this seam: at the organ default, `measure_detection_resolution`
co-reads the belief dimensions at the shipped and own reading dates, and at 90 they move between
them (§22.1's table). Whether `check_detection_resolution` then fires on the production reading was
not measured this pass. If it does, the co-read loop should skip a conditional dimension whose
condition fails, via the same `as_of_gap_invariance_expected`, not by editing the derivation.

### 23.3 Where §17.3 stands

The as_of class control (§22.2) is off the list: green at both origins. Must-fire #1 moved with it.
Still pinned: the five D30/D33 sibling claims, the four publication surfaces and the register node
(§21.1), plus the co-read question in §23.2, which needs measuring.

---

## 24. BUILD pass 15 — 2026-10-02 (worker tick, BUILD lane) — §23.2's co-read question, measured and closed

The origin is still 400, no level moved, `CAVEAT_COVERAGE_PROBES` untouched (§19.4). The candidate
origin was substituted in the process through the §17.4 `flip_plugin`, never in the tree.

### 24.1 The measurement §23.2 said was owed

`measure_detection_resolution` → `check_detection_resolution` on the production reading (n=300;
shipped `as_of` 2024-04-16, own reading date 2024-03-22), one process per origin:

| seed | 400: violations | 90: belief / mix identical at both dates | 90: violations |
|---|---|---|---|
| 7 | 0 | False / False | 2 |
| 11 | 0 | False / False | 2 |
| 23 | 0 | False / **True** | 1 |
| 5 | 0 | False / False | 2 |

So yes: at the flip, rule 5 fires on every seed, on a second reading date that is telling the
truth. Seed 23's mix staying put while belief moves is §23.1's "not per dimension" point again.
Detection edges are unchanged by the origin (2/1, 4/1, 6/2, 3/1 shipped/own).

### 24.2 The remedy, as §23.2 recommended

The co-read loop now skips a dimension whose `as_of_gap_invariance_expected(...)` is False at
`max(as_of, own)`, and REPORTS it in a new field `co_read_condition_unmet` rather than dropping it.
`DETECTION_CO_READ_DIMENSIONS`' derivation is untouched.

§22.1's node read the belief pair out of `co_read_dimensions_identical` on its uncovered arm — the
empty-intersection trap §23.2 described, arriving by the other door: with the pair excused,
`all(...)` over nothing is True and the node red at BOTH origins. Restated: the two maps partition
the co-read set; the unconditional pair is always co-read; every co-read dimension is identical and
`check_detection_resolution` is clean on every arm; the excuse is empty at or above the edge and is
exactly the belief pair below it; and below it the excused figure is shown to move by scoring both
dates directly, so the excuse is load-bearing.

**Green at 400 and at 90**, 14 passed each over the detection/as_of selection. **R15**, three
mutations of the excuse, each red at the node:

| mutation | fires on |
|---|---|
| excuse never taken | the 90d arm: belief co-read and not identical |
| excuse taken for belief + `detection_latency` regardless | the 400d arm: unconditional dimension excused |
| excuse taken for belief regardless of the condition | the 400d arm: excuse non-empty above the edge |

### 24.3 Where §17.3 stands

The co-read question is closed and off the flip commit. Still pinned: the five D30/D33 sibling
claims, the four publication surfaces and the register node (§21.1).

---

## 25. BUILD pass 16 — 2026-10-02 (worker tick, BUILD lane) — the four publication surfaces, two restated and two re-classified

The origin is still 400, no level moved, `CAVEAT_COVERAGE_PROBES` untouched (§19.4). The candidate
origin was substituted in the process through the §17.4 `flip_plugin`, never in the tree.

### 25.1 The two caveat nodes, restated

`test_the_memory_resolution_caveat_travels_with_both_numbers` and
`test_the_census_caveat_travels_with_both_belief_figures` pinned the saturated sentence. Both caveat
functions already had the other branch ("NOT saturated", "SITS INSIDE IT … Nd SHORT of it"), so the
restatement is §18.4's law plus a book coordinate: `saturated is (WINDOW >= _OLDEST_OBSERVED_FAILURE_
AGE_DAYS[7])` picks which sentence must travel, and `inert is (WINDOW >= _INVOICE_BAND_TOP_DAYS)` picks
the census sentence, with the headroom asserted as `WINDOW - 92` on one arm and `92 - WINDOW` on the
other. **Green at 400 and at 90.** R15, four mutations in the process:

| mutation | 400 | 90 |
|---|---|---|
| `saturated` forced True in `measure_belief_window_resolution` | red (the short-window leg) | red |
| `belief_resolution_caveat` always takes the saturated branch | red | red |
| `scored_company_is_inert` forced True | green — an equivalence, it IS True at 400 | red |
| census headroom off by one | red | red |

### 25.2 The two CLI nodes are not publication-surface failures — they are the register

`test_cli_runs_and_prints_all_three_gaps` (ERROR) and `test_cli_write_ledger_publishes_the_measured_
note_not_a_retired_one` (FAILED) red at 90 for one reason, and it is not their prose:
`measure_own_drift_resolution` unions the register's `own_visible_drifts` (-370, -350, …) into its grid,
and at a 90d origin `-370` is a -280d window, which `build_scenario` refuses. §17.3 filed them as
publication surfaces by name; the traceback says they are the register node's subject reached through
`main()`. They cannot be restated test-side — the CLI must run end to end — so they move with the
register re-declaration in the flip commit. This is the same shape as §21.1: two nodes off one list
and onto another, not off the work.

### 25.3 Where §17.3 stands

Publication surfaces: 2 of 4 restated; the other 2 are the register's and travel with it. Still pinned:
the five D30/D33 sibling claims and the register node (§21.1), which now carries the two CLI nodes.

---

## 26. BUILD pass 17 — 2026-10-02 (worker tick, BUILD lane) — the five D30/D33 sibling nodes, restated

The origin is still 400, no level moved, `CAVEAT_COVERAGE_PROBES` untouched (§19.4). The candidate
origin was substituted in the process through the §17.4 `flip_plugin`, never in the tree.

### 26.1 What the two origins measure

`measure_belief_band_population_axis` and `measure_published_resolution_floor(n_customers=300)`, one
process per origin (the §21.2 cache is keyed by the origin now, but separate processes anyway):

| | 400 | 90 |
|---|---|---|
| `above_edge_range` | (−333, −308) | (−23, 2) |
| `below_edge_range` | (−371, −342) | (−61, −32) |
| above / below spread by seed | 20,0,25 / 1,29,1 | identical |
| `belief` floor / bit-equality floor | 310 / 310 | 4 / 4 |
| `belief_population_mix` floor / bit-equality floor | 314 / 312 | 4 / 4 |
| book bound by seed (7, 11, 23) | 310, 309, 309 | 1, 1, 1 |

Every edge moves by exactly 310, which is the origin difference, so the edge plus the window is a book
coordinate: above (67, 92), and its top is `_INVOICE_BAND_TOP_DAYS`. The book bound is
`max(1, WINDOW − oldest observed failure + 1)` on every seed at both origins. At 90 the two belief
figures share a 4d resolution and the two predicates agree, which is §15.3 re-measured.

### 26.2 The five nodes

| node | at 90 it failed on | now |
|---|---|---|
| `test_the_belief_edges_move_on_the_draw_size_alone` | register `own_saturates_above` (−308) vs the measured top (2) | the spread legs were already origin-free; the top edge is asserted as `92 − WINDOW`. The declaration-equals-top leg moved to `test_the_belief_register_describes_the_draw_size_axis`, which is the register node. `check_belief_band_population_axis` only asks for membership of the range, so dropping that leg would have weakened the control. |
| `test_the_band_shipped_before_this_repair_is_false_at_the_derived_floor` | the measured range pinned at 400 | the range is `_ABOVE_EDGE_BOOK_RANGE − WINDOW`, and D30's shipped band is `(72, 92) − WINDOW`, which is the same defect at either origin |
| `test_the_two_belief_figures_do_not_share_a_resolution` | 310 pinned | the book bound is the law above, the "bound is a bound" loop is unconditional, and the 310/314 split is asserted only where the window covers the book; below it, both are 4 |
| `test_bit_equality_counts_a_difference_no_consumer_can_render` | 312 pinned | below the edge, the predicates agree on every seed and both figures; above it, unchanged. The register-owner legs were dropped here because `test_the_floor_register_is_measured_not_asserted`'s `check_published_resolution_floor` enforces divergence ⇔ owner exactly, in both directions |
| `test_a_predicate_divergence_with_no_owner_fires_the_control` | at 90 there is no divergence to leave unowned | both cases are BUILT on a copy of the measurement (inject a divergence, inject agreement), so the rule is shown to fire whether or not this book diverges |

**5 passed at 400 and 5 passed at 90.** The two register nodes are red at 90 and green at 400, as
they should be: they carry the literals the flip rewrites.

### 26.3 R15, in the process

| mutation | 400 | 90 |
|---|---|---|
| above-edge top +1 in `measure_belief_band_population_axis` | red (edges, band) | red (edges, band) |
| book bound +1 on every seed | red | red |
| mix floor forced equal to belief floor | red | green — an equivalence, they ARE equal at 90 |
| mix bit-equality floor = readable − 2 | green — an equivalence, it IS 312 = 314 − 2 at 400 | red |
| owner rule removed from `check_published_resolution_floor` | red | red |
| debt rule removed | red | red |
| range comparison removed from `check_belief_band_population_axis` | red | red |

### 26.4 The whole file at both origins

In this worktree (origin/main 407bdb1c3 plus this pass), one process per origin:

| origin | result |
|---|---|
| 400 | **623 passed**, 0 failed |
| 90 | 560 passed, **18 failed, 45 errors** |

The five sibling nodes are green at 90. The tracebacks carry 51 `ValueError` lines, and every one
of them is §25.2's mechanism: the register's `own_visible_drifts` (−370, −320) asking `build_scenario`
for a −280d or −230d window. They move with the register. The 18 failures were NOT classified this
pass. They include the two register nodes and the CLI ledger node, but also nodes this frame has never
named (for example `test_the_coverage_only_claim_is_measured_not_asserted[7,11,23]`,
`test_the_inert_verdict_is_falsifiable_in_both_directions` and `test_a_shadowed_organ_default_owes_a_
measured_divergence`). Whether each one is register-borne or a test-side pin is the next pass's
question. So §17.3's original list is clear test-side, but **the flip's change set is not yet
enumerated**.

A trap for whoever repeats this: `cd WT && (A) & (B) & wait` runs B in the caller's directory, not in
WT, because `&&` binds tighter than `&`. Two of this pass's 90d runs did exactly that. They graded the
shared tree's copy of the file and showed these five nodes red. The cause was found from the
traceback's line numbers, which matched the old file. Put `cd` on its own line, ended with `;`.

---

## 27. BUILD pass 18 — 2026-10-02 (worker tick, BUILD lane) — §26.4's 18 failures, classified, and four of them are not pins

The origin is still 400, no level moved, `CAVEAT_COVERAGE_PROBES` untouched. The candidate origin was
substituted in the process only (§17.4's `flip_plugin`).

### 27.1 The run, and why it read 23

Whole file at 90, `-rEf --tb=short`, in a worktree at origin/main `238cbb6e2`: **23 failed, 555
passed, 45 errors** (14 min). Pass 17 (`73bb200a0`) was on local main and not yet on origin, and the
only difference on the two `file_scope` files is pass 17's test diff. The five sibling nodes it
restated were then re-run at 90 against `73bb200a0`'s copy: **5 passed**. So §26.4's 18 are exactly
these 23 minus those five, by observation rather than by subtraction.

Prediction, filed before the run returned: the majority register-borne, with 3 to 6 test-side pins.
**Refuted on both counts**, as the table shows.

### 27.2 The 18, by cause

| cause | nodes | moves with |
|---|---|---|
| **R — register, via `own_visible_drifts`.** −370 at a 90 origin is a −280d window, and `build_scenario` refuses it (§25.2) | `test_cli_write_ledger_publishes_the_measured_note_not_a_retired_one`, `test_a_broken_memory_probe_fires_by_name[off its own organ]`, `[CHANGED THE WORLD]` | the register re-declaration |
| **R — register literals graded by their checks** | `test_the_belief_register_describes_the_draw_size_axis` (declares −333..−308, sweep reads −23..2), `test_the_floor_register_is_measured_not_asserted` (declares 310, sweep 4) | the register re-declaration |
| **C — census.** `SCENARIO_CONSTANT_CENSUS["DD_FAILURE_WINDOW_DAYS"]["measured_divergence"]` declares 310, and at 90 there is no shadow (divergence 0) | `test_a_shadowed_organ_default_owes_a_measured_divergence` | the census entry: at the flip the constant stops shadowing, so the entry's `shadows_organ_default` and `measured_divergence` go, and MUTATION 1–6 need a constructed shadow |
| **T1 — test-side, origin-relative drift.** `organ_failure_window_drift_days=-320` means "window 80" only at 400 | `test_the_census_reads_the_window_off_the_scored_company_not_the_constant`, `test_the_inert_verdict_is_falsifiable_in_both_directions`, `test_score_triad_threads_the_scored_company_into_both_predictors` | restatable now: `80 − DD_FAILURE_WINDOW_DAYS` |
| **T2 — test-side, a saturated value or sentence pinned** | `test_the_memory_grid_carries_a_witness_above_its_saturation_point` (`never_forgets_drift_days == 0`; 1 at 90, §18.1), `test_the_memory_caveat_names_both_edges` (`'NEVER forgets'`), `test_each_belief_figure_publishes_its_own_floor_and_the_sentence_says_it` (`'can move ANY figure here'`), `test_a_sibling_quantity_that_moves_with_the_figure_is_not_a_render_of_it` (a rendered figure), `test_a_declared_floor_the_sweep_contradicts_fires_the_control` (`"the sweep measures 314d"`) | restatable now, in the §26.2 way: assert the saturated branch where the window covers the book, and the unsaturated sentence below it |
| **F — a published claim that is false at 90** | `test_the_coverage_only_claim_is_measured_not_asserted[7]`, `[11]`, `[23]`, `test_measure_builds_the_second_company_and_publishes_the_subtraction` | **a contract decision, below** |

Count: R 5, C 1, T1 3, T2 5, F 4 = 18. **All 45 errors are R**: every error traceback ends in
`build_scenario`'s −370 ValueError.

### 27.3 NEW FINDING — the belief's "coverage only" claim holds only because the company never forgets

`measure_coverage_only_residual(n_customers=600, seed=7)`, one process, both origins:

| dimension | residual at 400 | residual at 90 | scored gap at 90 |
|---|---|---|---|
| `belief` | 0.0 | **0.0191** | 0.1497 |
| `belief_population_mix` | 0.0 | **0.0050** | 0.0733 |
| `ageing` | 0.0 | 0.0 | 0.0901 |

(The 0.0191, 0.0252 and 0.0181 on seeds 7, 11 and 23 come from the failing node's own message.)

`COVERAGE_ONLY_CLAIM_CONTRACT` publishes both belief sides as "same rule, different-coverage inputs".
With coverage equalised, what survives at 90 is the company's 90-day memory against a truth side that
forgets nothing. At 400 the memory covers the whole book, so the claim is true **for the same reason
D27 exists**: the saturation that hides a memory error also hides the memory term from this control.
The flip therefore **falsifies a published sentence**. It does not only re-declare literals.

This is not a pin, and the remedy is not to restate the test. There are two choices. My
recommendation is the first:

1. **Restate the contract for the two belief dimensions as coverage AND memory, and publish the
   coverage-equalised residual as the memory's share.** That residual is the quantity D27 asked the
   dimension to resolve, already measured by an existing instrument.
2. Give the truth-side rule the company's window. That makes the truth side read a company
   parameter, so a memory error would cancel on both sides. That is the blindness D27 was opened to
   remove, so this is rejected.

`ageing` stays coverage-only at both origins, because it does not read the window.

### 27.4 The flip's change set, now enumerated

- **Test-side, landable ahead of the flip (8):** T1 ×3, T2 ×5, restated to hold at both origins.
- **Travels with the register re-declaration (5 failures and 45 errors):** R.
- **Travels with the census (1):** C.
- **A contract change, which needs its own pass before the flip (4):** F, under §27.3's option 1.

So the flip commit is the register, the census and the contract, and the next pass is the eight
test-side restatements.

---

## 28. BUILD pass 19 — 2026-10-02 (worker tick, BUILD lane) — §27.4's eight test-side nodes, restated, and two of them were not pins

The origin is still 400, no level moved, `CAVEAT_COVERAGE_PROBES` untouched. The candidate origin was
substituted in the process only (§17.4's `flip_plugin`).

### 28.1 The eight

| node | at 90 it failed on | now |
|---|---|---|
| `test_the_census_reads_the_window_off_the_scored_company_not_the_constant` | drift −320 = a −230d window | the sweep is declared as WINDOWS `(WINDOW, 80, 50, 600, 6000)` and the drifts are derived from them |
| `test_the_inert_verdict_is_falsifiable_in_both_directions` | the same | `80 − WINDOW` and `600 − WINDOW` |
| `test_score_triad_threads_the_scored_company_into_both_predictors` | the same, plus a baseline pinned at 400 / inert | drift `80 − WINDOW`; the baseline is `WINDOW`, inert iff `WINDOW ≥` seed 7's oldest failure (91) |
| `test_the_memory_grid_carries_a_witness_above_its_saturation_point` | `never_forgets_drift_days == 0` | the clamp is the law, `max(0, oldest − WINDOW)`; the "+1 is the accident" leg holds only where the window is strictly past the book (at the edge, +1 is the true witness) |
| `test_a_declared_floor_the_sweep_contradicts_fires_the_control` | `"the sweep measures 314d"` | built on the measurement: declare `measured + 4`, expect `measured` in the refusal |
| `test_each_belief_figure_publishes_its_own_floor_and_the_sentence_says_it` | 310/314 and `'can move ANY figure here'` | the per-figure floors are read from the register (the floor-register node grades the register against the sweep, and goes with the flip); the literals 310/314 are asserted only where the window covers the book; the book bound is `max(1, WINDOW − 91 + 1)`; the ANY-figure sentence travels where the window covers the book, "by a day" below it |
| `test_the_memory_caveat_names_both_edges` | `'NEVER forgets'` absent | **not a pin — see §28.2** |
| `test_a_sibling_quantity_that_moves_with_the_figure_is_not_a_render_of_it` | seed 23: mix 0.0767, per-case 0.0800 | **not a pin — see §28.3** |

### 28.2 NEW FINDING — the unsaturated caveat named neither edge

`belief_resolution_caveat`'s NOT-saturated branch said only "a memory error in either direction can
move this figure by a day". Both edges still exist there: every window at or above the oldest observed
failure counts every event, and every window at or below `newest − 1` counts none. So at the flip, the
caveat the scenario publishes would have dropped the D29 amnesia edge and the never-forgets edge both,
which is exactly the state the node's docstring forbids ("a caveat that names only the tail somebody
swept is the D27 state"). The branch now names both edges, in words that do not use the saturated
branch's "NEVER forgets" sentence (§25.1's node forbids that sentence when unsaturated, rightly: it
says THIS company is indistinguishable from one that never forgets). Nothing published moves at 400:
the scenario is saturated there and the live publisher runs at 6000. The node now scores the shipped
window, the oldest age, and one day under it in one process, so both branches are graded at either
origin.

### 28.3 NEW FINDING — the mix/per-case coincidence is a saturation artefact

`PUBLISHED_GAP_CONSUMERS["belief_population_mix"]`'s comment says the mix figure equals belief's
per-case disagreement "on every book measured … and no real book performs that permutation". Measured,
one process per origin, `_resolution_population(300, seed)`:

| seed | 400: mix / per-case | 90: mix / per-case |
|---|---|---|
| 7 | 0.0800 / 0.0800 | 0.0833 / 0.0900 |
| 11 | 0.1033 / 0.1033 | 0.1033 / 0.1100 |
| 23 | 0.0767 / 0.0767 | 0.0767 / 0.0800 |
| 101 | 0.0867 / 0.0867 | 0.0867 / 0.0967 |
| 999 | 0.0767 / 0.0767 | 0.0833 / 0.0867 |

A company that forgets performs the permutation: it under-calls accounts without moving the mix by the
same amount. The node now asserts coincidence on every seed where the window covers the book and
separation on every seed below it. That makes the D19 claim stronger, not weaker (they are different
quantities, and a real company shows it). The register comment is prose on the register and goes
with the flip. **Not explained this pass:** at 90 the reader walk still lists the
`format_belief_summary` site in `cross_attributed` (the node's first two legs passed at 90). Whether
the `value_collisions` declaration is still needed below the edge is a question for the flip.

### 28.4 R15, in the process

| mutation | 400 | 90 |
|---|---|---|
| §28.2's edge clause removed (HEAD's caveat) | red | red — the node scores an unsaturated window at both origins |
| clamp removed from `never_forgets_drift_days` | red | green — an equivalence, the clamp does not bind at 90 (91 − 90 = 1) |
| the unsaturated branch also carries "can move ANY figure here" | green — an equivalence, the scenario never reaches that branch at 400 | red |

The eight passed at 90 and the eight plus every caveat node passed at 400 (27). Whole-file results at
both origins are in §28.5.

### 28.5 The whole file at both origins

In this worktree (HEAD `b17da3db3` plus this pass), one process per origin, run concurrently:

| origin | result |
|---|---|
| 400 | **623 passed**, 0 failed |
| 90 | 568 passed, **10 failed, 45 errors** |

Prediction, filed before the run returned: exactly §27.2's R (5), C (1) and F (4), and all 45 errors
R. **Confirmed**, node for node. So what is left red at 90 is the flip commit's own change set: the
register (now also carrying §28.3's comment), the census, and §27.3's contract.

---

## 29. BUILD pass 20 — 2026-10-02 (worker tick, BUILD lane) — §27.3's contract, restated as coverage AND memory

The origin is still 400, no level moved, `CAVEAT_COVERAGE_PROBES` untouched. The candidate origin was
substituted in the process only (§17.4's `flip_plugin`).

### 29.1 The measurement option 1 needed

§27.3 recommended restating the belief contract as coverage AND memory. That holds only if the
coverage-equalised residual at 90 is ALL memory: with the company's memory also taken to the all-DD
book's oldest failure (the never-forgets company, `never_forgets_drift_days` on THAT book), nothing
may survive. Measured, n=600, one process per origin:

| seed | 400: cf drift / belief / mix | 90: cf drift / belief cov-only → cov+memory / mix cov-only → cov+memory |
|---|---|---|
| 7 | 0 / 0 / 0 | 2 / 0.0191 → **0** / 0.0050 → **0** |
| 11 | 0 / 0 / 0 | 2 / 0.0252 → **0** / 0.0067 → **0** |
| 23 | 0 / 0 / 0 | 2 / 0.0181 → **0** / 0.0050 → **0** |

`ageing` and `detection` read 0 and `detection_latency` 0.93–1.07 either way, at both origins. So the
whole residual is the company's forgetting and none of it is rule divergence: option 1 is a
measurement, not a reading.

### 29.2 What changed

- `COVERAGE_ONLY_CLAIM_CONTRACT` gains `reads_company_memory` on every entry (True for the two belief
  dimensions only), and the belief entries' `why` now says coverage AND memory.
- `measure_coverage_only_residual` builds the never-forgets company on the all-DD book when the
  scored one forgets part of it (drift > 0; at 400 the drift is 0 and no second build is made). For a
  memory-reading dimension `residual` is the coverage-AND-memory gap, which must be 0, and
  `memory_share` is the coverage-only gap minus it. The result carries `cf_never_forgets_drift_days`,
  and the CLI prints `memory_share`.
- The belief note's D20 sentence says the control equalises coverage AND memory, and names the
  memory's share. No figure moves at 400.

`recency_contribution` (§21.3) is the same forgetting measured on the SCORED book, and
`memory_share` is the same thing on the all-DD book. They are different populations, so they are
not the same number, and neither is published as the other.

### 29.3 The four F nodes and two new ones

| node | now |
|---|---|
| `test_the_coverage_only_claim_is_measured_not_asserted[7,11,23]` | unchanged assertion (`residual == 0`), now true at both origins because the residual equalises memory; plus `memory_share is None` ⇔ the dimension does not read memory |
| `test_measure_builds_the_second_company_and_publishes_the_subtraction` | the drift is §28.1's clamp law `max(0, oldest − WINDOW)`, and the contribution is 0.0 iff the drift is 0 (at 90: drift 1, belief 0.0190, mix 0.0033) |
| NEW `test_the_memory_leg_can_be_taken_and_carries_the_whole_residual` | sets the origin to the organ's default itself, so the rare branch is reached at either shipped origin: drift > 0, `memory_share` > 0 on both memory dimensions, residual 0 |
| NEW `test_the_memory_declaration_is_the_set_the_window_moves` | the dimensions whose gap moves between the book's oldest failure and one day under it must EQUAL the declared `reads_company_memory` set, so the flag is graded against the scorer and not the author |

The first draft of the declaration node compared the oldest failure with ONE DAY under it, and it
red at both origins: that step moves `belief` alone at seed 7, because the mix is coarser (§26.1's
314 against 310). It was grading the mix's resolution and calling the mix a non-reader. It now
compares the oldest failure with a one-day memory.

### 29.4 R15, in the process

Each mutation is loaded over the worktree's module by a pytest plugin; the unmutated module through the
same plugin is the placebo arm (2 passed).

| mutation | 400 | 90 |
|---|---|---|
| memory leg removed (`cf_nf = cf` always) | red (memory-leg node) | red (memory-leg node + coverage-only ×3) |
| `belief_population_mix` declared a non-reader | red (declaration node); the coverage-only node green, an equivalence (the mix's cf gap is 0 whether or not memory is equalised at 400) | — |
| `memory_share` computed as `cf_nf − cf_nf` | red (memory-leg node) | — |

### 29.5 The whole file at both origins

Prediction, filed before the run: at 400, 625 passed (623 + the two new nodes); at 90, 574 passed,
**6 failed (§27.2's R 5 + C 1), 45 errors (all R)**. The F row of §27.2 is empty.

| origin | result |
|---|---|
| 400 | **625 passed**, 0 failed |
| 90 | 574 passed, **6 failed, 45 errors** |

**Confirmed**, node for node: the six are the two register nodes, the CLI ledger node and the two
`own_visible_drifts` probe cases (R), plus the census node (C), and every error is R. What is left
red at 90 is the flip commit: the register, the census, and §28.3's register comment.

---

## 30. BUILD pass 21 — 2026-10-03 (worker tick, BUILD lane) — THE FLIP

**The origin is now the organ's.** `DD_FAILURE_WINDOW_DAYS = organ_default_failure_window_days()`
(90), read off `PaymentObservationConsumer.__init__`'s signature (§4 item 1), and the same commit
carries what §27.4 enumerated: the register, the census, the probe grid and §28.3's comment.

### 30.1 What changed in `tools/couple_w2_11_d5.py`

- **The register**, both belief entries: §15.2's ten fields, transcribed (`own_invisible_drifts`
  `()` / `(-1,)`, `own_visible_drifts` `(-60, -45, -30, -4)`, the collapsed runs, edges −61 and
  +2/+1, draw-size ranges (−23, 2) and (−61, −32), floors 4/4, and the mix's
  `own_floor_predicate_atom` back to `None` per §15.3). Both `own_why` sentences now describe a
  readable company rather than one 308 days inside its blind band.
- **`CAVEAT_COVERAGE_PROBES`** memory row `(-370, -350, -310)` → `(-1, 1, 5)` (§19: the matched pair).
- **The census**: `measured_divergence`'s live fields now read `harness_window_days` 90,
  `divergence_days` 0, `never_forgets_drift_days` 1, `scored_saturated` False. The shadow stays: the
  AST still hands the constant to the organ's parameter, so the entry still owes the fields, and
  `check_scored_window_provenance` returns `[]` on them. The dated `cost` block is kept as the
  measurement that justified the flip ("harness origin" in it means the 400).
- **§28.3's comment** on `PUBLISHED_GAP_CONSUMERS["belief_population_mix"]["value_collisions"]`:
  the coincidence was a saturation artefact. The declaration is kept, because §28.3 left open why
  the reader walk still lists the site.

### 30.2 The whole file after the source edits, before any test edit — prediction REFUTED

Prediction, filed before the run: 625 passed, or a handful of prose pins; 0 errors.
**Result: 613 passed, 12 failed, 0 errors** (15 min). The errors went, as predicted. The 12 are
not §27.2's six, and that is the lesson of this pass. Passes 18–20 measured "the whole file at 90"
by substituting the ORIGIN in-process and leaving the REGISTER at its 400-origin values. A node that
reads a register field directly and asserts the defect's shape (`own_saturates_above == -308`, an
invisible `+500`, a 310d floor) was therefore green in those runs and could only go red once the
register itself moved. §27.4's "the flip commit is the register, the census and the contract" was
right about the source and blind to the test-side nodes that pin the register.

| node | at the flip it failed on | now |
|---|---|---|
| `test_the_saturation_rule_is_not_keyed_to_a_register_state` | `own_saturates_above == -308` / `-309` | the law: `oldest − WINDOW` and one less for the mix |
| `test_the_off_path_saturation_declaration_is_tried_too` | `"measured saturates_above=-308"` | the entry's own edge, read before the mutation |
| `test_the_belief_memory_band_is_unbounded_above` | the finding itself | **renamed `test_the_scored_company_is_inside_its_own_book`** = exit criterion 1 |
| `test_the_shipped_company_sits_inside_its_own_blind_band` | `WINDOW > organ default` | **renamed `test_the_scored_company_is_the_organs_own`** = exit criterion 2, plus the 400 company still reads a different gap |
| `test_the_book_predicts_the_band_the_sweep_measured` | `measured == predicted` | **a bound, see §30.3** |
| `test_the_memory_resolution_caveat_travels_with_both_numbers` | `memory_blind_band_days` truthy | equals the register's band; non-empty only where saturated |
| `test_a_lying_memory_band_fires_by_name` ×3 | `belief` has no blind drift left to understate or leave unowned | the three hole mutations act on the mix, still blind at −1 |
| `test_the_pre_hour_caveat_fires_the_control` | `"310d … 314d"` | every figure whose book bound differs from its floor must fire, and at least one must |
| `test_stamping_the_siblings_floor_fires_the_control` | nothing fired | **an equivalence, see §30.4** |
| `test_a_shadowed_organ_default_owes_a_measured_divergence` | `divergence_days == 310` | 0, and `origin_is_organ_default` True |

### 30.3 NEW FINDING — the book predictor equals the sweep only at the saturated origin

`test_the_book_predicts_the_band_the_sweep_measured` asserted that the population-side predictor
(`smallest_visible_shortening_days`, from event dates) and the all-seed sweep agree on the number.
At 400 they did (310 = 310). At 90 the book says 1 day and the figure first moves on every seed at
4. The equality was another saturation artefact: the first shortening that reached the book at 400
dropped whole invoices at once, and at 90 the first one drops a single age that need not move a
severity tier. The predictor is a **floor** on the readable floor. That is the split the published
components already carry (`book_bound_floor_days` against `measured_resolution_floor_days`, atom
D33). The node now asserts `measured ≥ predicted`. Its independence leg (the AST ban on the organ)
is unchanged. The node also read the smallest *positive* moved drift as a shortening, because at
400 no positive drift moved. It now reads shortenings only.

### 30.4 An equivalence, stated

At 90 both figures have a 4d floor, so stamping `belief`'s floor on the mix stamps the mix's own
number, and nothing may fire. The node asserts that, and asserts firing wherever the floors differ.
The firing comparison is the same one `test_the_pre_hour_caveat_fires_the_control` proves. The
shared-sentence defect D33 named does not exist at the organ's default.

The first restatement of `test_the_scored_company_is_inside_its_own_book` asserted that a longer
memory moves BOTH figures on every seed. It was red on the mix: §19.1 already measured the mix
moving on two seeds of three at every positive drift. The node now asks for a longer memory read
apart on at least one seed.

### 30.5 R15, in the process

| arm | `…is_inside_its_own_book` | `…is_the_organs_own` |
|---|---|---|
| mutation: `DD_FAILURE_WINDOW_DAYS = 400` (pytest plugin, never in the tree) | red | red |
| placebo: unmutated | green | green |

### 30.6 The whole file, and what is left

After the test edits: **625 passed, 0 failed** (14 min). Eight dependent test files
(`site/test_published_caveat_reaches_the_reader.py`, the D6/D7 ageing suites, the gap-ledger
reconciler, the gap-metric class tests, the live-triad bridge, map-assertion provenance): **246
passed**.

Not done, and not D27's to do in this commit. The live `W2_11` ledger row is `support_changed`
(truth 717 → 417): that is a population decision outside this atom. The register-sourced floor the
live run stamps (`measured_resolution_floor_days`, 310 → 4) reaches the door only when that row is
re-measured and landed. No level moved here. The note tenant for this atom is 32.7k of a 32,768 B
ceiling, so this record lives here and not on the map row.
