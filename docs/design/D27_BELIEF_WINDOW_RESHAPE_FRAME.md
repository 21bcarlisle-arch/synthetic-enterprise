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
