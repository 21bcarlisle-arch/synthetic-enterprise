**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 3 · **Atom:** value_arms_floor_family

# PRE-REGISTRATION — moving `NOISE_FLOOR_PATH` to the single-arm eighteen

**Filed:** 2026-09-17 22:5x, before rendering the page either way.
**Claim id:** read-next12-alone-it-cannot-be-folded-into-the-eighteen

## What I have already established, by measurement, not prediction

The drawn item's premise is NOT spent. Its three commits are ancestors of `origin/main`, but the
work they gate is not done: `site/data/value_arms.json` still publishes the mixed-arm family.

**The longjob has NOT settled.** `longjob-floor-next12-20260917` is PID 3819244, started 19:11,
158 min CPU at 22:50. `/var/tmp/value_cycle_ab_s1_noise_floor_next12_20260917.json` does not exist.
The item's own estimate — ~8h left at 22:50 — is the live state, not a stale one. **Part 1 of the
item (copy it in, read it as its own twelve-seed family) cannot be started this turn.** This turn
takes part 2, which is decidable on evidence already on disk.

**The three trees are three instruments, and I diffed them over the value-arm paths**
(`simulation/`, `company/`, `saas/`, `tools/run_value_cycle_ab.py`):

| pair | diff over the value-arm paths | so |
|---|---|---|
| `c066c114b` vs `9f0ab066f` | `value_based_renewal.py` +93, `run_value_cycle_ab.py` +1036 | **different arms** |
| `4e7938f673` vs `9f0ab066f` | *empty* | **same arm** |
| `7da627b90` vs `4e7938f673` | 18 files, −3294 | **a third arm** |

Row 3 is the item's reason for refusing the fold, and it holds: the twelve seeds in flight are
drawn by a tree that matches neither published family. They are their own family or they are
nothing.

Rows 1 and 2 are the decision. The **published** floor
(`value_cycle_ab_s1_noise_floor_folded18_20260917.json`, wired at
`tools/generate_value_arms_data.py:271`) folds `c066c114b` with `9f0ab066f` — two arms — and its
own `value_arm_pairing` field is **`null`**: it cannot say whether its members share an arm,
because it was written before the field existed. The **single-arm** eighteen
(`..._folded18_single_arm_20260917.json`, landed `471dfd417`) folds `4e7938f673` with `9f0ab066f`
and declares `same_value_arm: true`, `differing_paths: []`.

| family | n | selection mean | sem | sems from 0 | sign |
|---|---|---|---|---|---|
| folded18 (published) | 18 | −£624.13 | 347.16 | 1.80 | **none, refused** |
| folded18_single_arm | 18 | −£959.78 | 384.62 | 2.50 | **NEGATIVE, stateable** |

The single-arm family is not the *tighter* one — its stdev is **larger** (1631.80 vs 1472.89) and
its sem is **larger** (384.62 vs 347.16). The sign appears because the **mean moves**, and the
artefact records why: on nine identical seeds `c066c114` sits **£671.31** above `9f0ab066`, at
20.4 sems from zero. That is an instrument step, and the published family is carrying it inside a
number labelled redraw noise.

## The decision I am making, and the direction it moves

**Move `NOISE_FLOOR_PATH` to the single-arm eighteen.** The page will state a negative sign it
currently refuses.

**This is the direction that should be distrusted, and I am naming that rather than hoping nobody
does.** This project's own comment at that constant says, of the last move: *"THE MOVE MAKES THE
PAGE LESS CONFIDENT AND THAT IS THE HONEST DIRECTION."* This move goes the other way.

It is defensible on one ground only, and it is not "more seeds" or "tighter bar": **the published
family is not a redraw-noise family.** Its spread is a mixture of a redraw spread and a £671
step between two pricing instruments. A mean over two instruments is not an estimate of either.
The refusal it currently publishes is therefore not a cautious reading of the evidence — it is an
artefact of pooling, and being wrong in the cautious direction is still being wrong about what the
number counts. Between a family that can answer "do my members share an arm" and one whose field
for that question is `null`, publishing the one that can answer is the fail-closed choice even
when its answer is the less comfortable one.

I am NOT moving `CURRENT_WORLD_NOISE_FLOOR_PATH`. Moving both puts one family's selection mean in
two regions of one headline, which is what `_the_legs_own_regions` refused in words on 2026-09-09.

## The predictions, written before the render

1. Rebuilding `site/data/value_arms.json` with only that one constant changed will move
   `error_bar`'s selection figure from −624.13 to −959.78 and flip its `distinguishable_from_zero`
   to `true`.
2. **No prose sentence needs editing.** `legs_on_one_bar` recomposes from the two signs, so the
   page's selection verdict will change from a refusal to a stated NEGATIVE without any string in
   the publisher being touched. If this is false — if I have to hand-write a sentence to make the
   page read correctly — that is a finding about the publisher, not a licence to write the
   sentence.
3. `error_bar.floor_tree_pairing` will stop reporting a tree difference, because the new family's
   members share a commit-pair over the value-arm paths. I do not know which branch it will take
   and I am not predicting the wording.
4. The `current_world` block's figures will be **byte-identical**, because its constant does not
   move.
5. `site/test_the_baseline_comparison_reaches_the_reader.py` will pass. Specifically
   `_the_legs_own_regions` will NOT fire, because −959.78 renders in the `error_bar` region and
   the `current_world` region still carries the 09-09b family's own figure.

If prediction 5 is false the move does not land, whatever I think of the argument.

## What this turn does NOT settle

The twelve seeds in flight are the independent test of this sign, at a third tree. They can refute
it. This pre-registration is the record that the sign was published from the single-arm eighteen
**before** those twelve were readable, so that when they land they are a test and not a
confirmation. Written down now: **if the next12 family's selection mean lands positive, or its
own sign is not negative, the move made here is the thing to re-open first.**
