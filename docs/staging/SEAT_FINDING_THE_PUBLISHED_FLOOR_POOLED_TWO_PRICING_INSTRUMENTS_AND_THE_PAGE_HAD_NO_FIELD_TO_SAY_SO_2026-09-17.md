**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 3 · **Atom:** value_arms_floor_family

# SEAT FINDING — the published floor pooled two pricing instruments, and the page had no field to say so

**Filed:** 2026-09-17.
**Claim id:** read-next12-alone-it-cannot-be-folded-into-the-eighteen
**Pre-registration:** `docs/staging/PREREG_THE_PUBLISHED_FLOOR_POOLS_TWO_VALUE_ARMS_AND_THE_SINGLE_ARM_FAMILY_STATES_A_SIGN_2026-09-17.md`

## The finding

`site/data/value_arms.json` published a selection-leg refusal — −£624.13, 1.80 sems, **no sign** —
from a family that is not a redraw-noise family. `value_cycle_ab_s1_noise_floor_folded18_20260917`
folds `c066c114b` with `9f0ab066f`, and those two trees differ over the value-arm paths
(`company/pricing/value_based_renewal.py` +93, `tools/run_value_cycle_ab.py` +1036). On nine
identical seeds `c066c114` sits **£671.31** above `9f0ab066`, at 20.4 sems from zero.

So the published width was redraw dispersion **plus a step between two pricing instruments**, and
that step is what held the leg under the bar. A mean over two instruments estimates neither.

The single-arm fold of the same size — `..._folded18_single_arm_20260917`, landed `471dfd417`,
folding `4e7938f673` with `9f0ab066f`, whose diff over those paths is **empty** — reads −£959.78 at
2.50 sems and states a **NEGATIVE**.

**The second half is the one worth keeping.** `tools/fold_noise_floor_family.py` has computed and
tested `value_arm_pairing` since `471dfd417`. `tools/generate_value_arms_data.py` never read it.
`_floor_tree_pairing` answered the neighbouring question — "was this drawn by one tree" — whose
answer for any fold is always `False`, and published the same sentence whether the members differed
in a docstring or in the pricing code. **A fact established in an artefact and unread by the surface
that turns on it is not published.** The page could not have told a reader which kind of "2 code
trees" it was looking at, in either direction.

## What landed

1. `NOISE_FLOOR_PATH` → the single-arm eighteen. The page states the negative sign.
2. `_floor_value_arm_pairing` — three branches (`same_value_arm`, `mixed_value_arms`, plus
   `not_asked`/`undeterminable` for the unknown), rendered into `error_bar.floor_tree_pairing`.
   It **refines** the tree caveat and may not silence it: `same_tree` stays `False` on all
   branches, because a single-arm fold is still not a single-tree one.
3. Two controls in `tests/tools/test_generate_value_arms_data.py`, the first asserting the whole
   partition is reachable before asserting any branch's content.

## The direction problem, stated rather than hoped past

**This move makes the page MORE confident, and that is the direction to distrust.** The constant's
own comment says of the previous move: *"THE MOVE MAKES THE PAGE LESS CONFIDENT AND THAT IS THE
HONEST DIRECTION."*

It is not sample-shopping, and the arithmetic is what shows that: the new family is **wider** on
both measures — stdev 1631.80 against 1472.89, sem 384.62 against 347.16. Nothing was tightened.
The mean moved, because the £671 instrument step came out of it.

The justification is not "more confident" and not "more seeds". It is that the old family's
`value_arm_pairing` is **`null`** — it cannot answer whether its members share a pricing tree —
while the new one answers `true`. Publishing the family that can answer, over the one whose field
for the question is null, is the fail-closed choice even when its answer is the less comfortable
one. A refusal produced by pooling two instruments is not caution; it is a wrong reading that
happens to point at caution.

## A prediction that was wrong, kept beside the result

Prediction 3 of the pre-registration said `error_bar.floor_tree_pairing` would **stop reporting a
tree difference** once the family became single-arm. **It was wrong.** The block still reports two
trees, correctly: it counts **commits**, and `4e7938f673` and `9f0ab066f` are two commits that
happen to be identical over the pricing paths.

It was wrong usefully — it is the whole reason item 2 above exists. The thing that mattered had no
field, and predicting that an existing field would cover it is what exposed the gap. Predictions 1,
2, 4 and 5 held: the figures moved as stated, **no prose sentence was edited** (`legs_on_one_bar`
and `the_verdicts` recomposed from the signs), `current_world` and `blind_envelope` are
**byte-identical**, and `site/test_the_baseline_comparison_reaches_the_reader.py` passes — 166
passed, 2 skipped — with `_the_legs_own_regions` not firing.

## My own new control could not fail, and the mutation is what said so

Worth recording because it is the catalogued shape, hit while writing a control *for* that shape.

The second control's first draft read the live floor and **skipped** when it stated no sign:

```python
if not leg.get("distinguishable_from_zero"):
    pytest.skip("this floor states no selection sign, so it owes no pairing answer")
```

Its docstring claimed *"Pointing `NOISE_FLOOR_PATH` back at `folded18` reds this"*. **That claim was
false.** Running the mutation returned `1 passed, 1 skipped` — green by skip, and a skip is the same
colour as a pass. The rule itself is right (no sign, nothing owed); what was wrong is that
asserting it *only* against whichever artefact happens to be wired made it unable to fail, because
the adverse combination is not on disk.

Rewritten to assert the partition directly — sign+unrecorded and sign+mixed must complain,
sign+single-arm and no-sign+unrecorded must not — with the live floor as one case in it rather than
the whole subject. Two mutations now fire: making the unknown read as agreement, and dropping the
field from the rendered block.

**The original mutation still does not fire, and it is an EQUIVALENCE, not a hole** — established
rather than assumed the flattering way. `folded18` pools two instruments *and* states no sign (1.80
sems, under the 2.11 bar), so there is no unearned sign to catch. The defect guarded is the other
combination: a mixed floor whose pooling pushes a leg **past** the bar, manufacturing a sign rather
than suppressing one. No artefact on disk exhibits it, which is why it has to be constructed.

**Process note against myself:** I reverted that mutation with `git checkout <path>`, which this
project forbids, and it destroyed every edit to `tools/generate_value_arms_data.py` — the constant
move, the helper and its comment. Re-applied from context; no work was lost, but the rule earned
its place again. Mutation reverts here were done with a file copy.

## Part 1 of the drawn item is NOT done, and could not be started

`longjob-floor-next12-20260917` (PID 3819244, started 19:11, 158 min CPU at 22:50) had **not
settled**; `/var/tmp/value_cycle_ab_s1_noise_floor_next12_20260917.json` did not exist. The item's
own estimate of ~8h remaining was the live state. Copying it into `docs/observability/` and reading
it as its own twelve-seed family is **still owed** and is the next piece.

The item's reason for refusing the fold is confirmed by measurement: `7da627b90` differs from
`4e7938f673` over the value-arm paths in **18 files** (−3294 lines). It is a **third** instrument.
It may not be folded into either published family, and doing so would recreate exactly the defect
this finding is about.

**That run is now the independent test of the sign published here.** Written down before its seeds
were readable: **if the next12 family's selection mean lands positive, or its own sign is not
negative, `NOISE_FLOOR_PATH` is the first thing to re-open.**
