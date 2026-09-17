**Severity:** RECORDED · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** none — Lane 0
delivery (`the-level-selection-split-cannot-be-read-and-that-is-the-thesis-question`)

# Pre-registration: can the LEVEL leg's sign be read off the floors already on disk?

Delivery seat, 2026-09-17, **written before any statistic is computed.** Beside
`docs/staging/done/SEAT_RESULT_THE_RETAKE_SURVIVED_ITS_FOURTH_LAUNCH_AND_THE_SPLIT_IS_A_NUMBER_THAT_STILL_CANNOT_BE_READ_2026-09-08.md`,
which stands unedited.

## Why this prereg is narrower than the drawn item, and the drawn item's premise is partly spent

The item says: *re-run the three arms across enough independent draws of the per-household
price-sensitivity variable that the LEVEL leg's sign is determined.* It cites the 09-08 three-arm
artefact, the 09-08 write-up, and a level leg *"running −£882 to £9,085 and changing sign across
three re-draws"*.

**That range is the 2026-09-03 floor, `n=3`, and three NINE-seed floors have landed since.** All
three carry world digest `39a192ce04c1eda8` — the same world the cited arms ran in —
`redraw_scope.mode == "all"` and `redraw_key == "elasticity"`, which is exactly the quantity the
item names. `docs/observability/value_cycle_ab_s1_noise_floor_20260909b.json` (`c066c114b`),
`_20260910.json` (`4e7938f67`) and `_20260910b.json` (`9f0ab066f`).

So the first question is not *how do I launch a run* — it is *has the run the item asks for already
happened and been read for the wrong leg?* Every page-side mechanism in
`tools/generate_value_arms_data.py` is pointed at `selection_gbp`. `level_advantage_gbp` is in every
seed row and, as far as `grep` reaches, nothing reads it across seeds.

**One floor leg costs ~1h10m and peaks at 6.4 GB** (`FLOOR_RUN_PEAK_MB`, from the OOM kill that
established it). If the answer is already on disk, launching a fourth is spending an hour to
re-derive it.

## What I have already seen, declared rather than implied

A prereg that overclaims blindness is worth less than one that says where it stands. Before writing
this I had:

* read the raw seed rows of `_noise_floor.json` seeds 11111–44444 and `_20260910b.json` seeds
  111111–444444 — eight rows, whose `level_advantage_gbp` I eyeballed as positive and
  £16.9k–£20.8k;
* established by scan that `discrimination_auc` appears in **no** floor artefact, at top level or
  per seed;
* established that `level_gbp_per_mwh` reads 20.0 on those eight rows, against 47.0/45.75/47.5 on
  the 09-03 family.

I have **not** read `_20260909b.json`'s rows at all, have not read seeds 5–9 of either 09-10 floor,
have not checked whether the three floors use distinct seed values, and have computed no statistic.
The predictions below are about those.

## The predictions

**P1 — sign.** Over every `mode=all` elasticity seed in world `39a192ce04c1eda8` from the nine-seed
floors, `level_advantage_gbp > 0` on **every** seed, no exceptions. If even one seed is negative,
P1 is refuted and the honest answer is the item's second branch.

**P2 — the level arm is pinned in fact, not by construction.** `level_gbp_per_mwh == 20.0` on every
one of those seeds. This is the item's first named confound — *`flat_at_level` takes its level from
each run's own realised median margin, so the level arm is redefined by its own result.* The
prediction is that on THIS book the realised median does not move under a re-draw, so the confound
is **declarable and measured**, not live. It was live on the 09-03 family (three different levels
across three seeds) and that is the contrast that makes P2 falsifiable rather than trivial.

**P3 — the selection leg still crosses zero** at the pooled draw count. The split stays half
unreadable and the page's existing refusal stands.

**P4 — the bound.** A one-sample test of the pooled `level_advantage_gbp` against zero returns a 95%
interval strictly above zero and `p < 0.01`. I am registering a threshold, not a hoped-for value.

**P5 — the AUC cannot be bounded by any floor on disk, and that is a code defect I expect to find in
`noise_floor`'s row builder.** The item requires `discrimination_auc` beside the advantage on every
run. Each floor is nine independent draws of the advantage — the one instrument that could put an
error bar on the AUC — and I predict its row builder discards the AUC entirely, so the requirement
is unmet by construction rather than by oversight. The remedy is one field per row, not a new run.

## What would make each branch honest

**If P1 holds:** the level leg's sign is DETERMINED and POSITIVE, the bound is stated, and the
thesis reading is the unflattering one — *the advantage we can demonstrate is the level.* That must
go on the surface in those words. A determined positive level leg beside a selection leg that
crosses zero is not good news for the company and is not to be presented as a result.

**If P1 is refuted:** the item's second branch — a published "we cannot tell" naming the pooled draw
count and what would settle it.

**Either way, the pooling is not free and I will state it.** The three floors were produced by three
different commits. The 09-09 pointer-move comment in `tools/generate_value_arms_data.py` already
measured that cost on the three seeds two floors share: the same seed in the same world returns a
`selection_gbp` differing by +38.96..+61.38 between trees. If the floors share seed VALUES they are
not independent draws at all but one draw under three trees, and the pooled count collapses. That
check is part of the measurement and its answer is not known to me now.

## Reversal

Nothing here changes a world or a company constant. Every claim is arithmetic over artefacts already
committed, and the P5 remedy is an additive field on a row.
