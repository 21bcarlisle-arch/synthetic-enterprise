**Severity:** RECORDED · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** none — Lane 0
delivery

*Continues `SEAT_PREREG_MOVING_THE_VALUE_ARMS_PAIR_TO_THE_20260908B_RUN_AND_ITS_FLOOR_2026-09-09.md`
(in commit `c51f98241`, never promoted) and
`SEAT_PREREGISTRATION_WHAT_PROMOTING_THE_09_08b_RUN_MAKES_THE_PROOF_PAGE_SAY_2026-09-08.md`. Both
pre-registered the same move by a different route; this document is about what survives the
collision.*

# Pre-registration: reconciling two live answers to one question, onto the set that landed

**Written BEFORE any repair was ported.** What is measured at HEAD below was measured first, and
the predictions are about what porting does — not about what the tree already says.

---

## The premise, re-measured 2026-09-09T05:2xZ — and it is HALF SPENT

The drawn item says two commits are "already landed in the isolated worktree" and need promoting.
They are not landed anywhere a promotion could reach:

- `c51f98241` and `076664967` are **ancestors of nothing**. `git branch -a --contains` names no
  branch; `git merge-base --is-ancestor <c> HEAD` is false for both. They are reachable only
  through this worktree's reflog (`HEAD@{10}`, `HEAD@{11}`), because the fork was `reset --hard`
  onto `origin/main` twice since they were cut.
- This worktree's HEAD is `9d7cd5e4f`, **identical to `origin/main`**. There is nothing to push.
  `dba27b77d`, which the item names as the new origin, is already an ancestor.

So "promote the two commits" is not the work. The rival lane won the race and its answer is on
`origin/main`. The work is **reconciliation**: decide which of the two constant sets survives, and
carry across whatever repair is still a live defect under the survivor.

## What the item got wrong about the rival's answer, checked not assumed

The item states the rival lane "moved `CURRENT_WORLD_THREE_ARM_PATH` and
`CURRENT_WORLD_NOISE_FLOOR_PATH` to 09-08b so the current-world block becomes a self-announcing
tautology". **It did not.** At HEAD those constants are held on `_20260908.json` /
`_noise_floor_20260908.json`, and the constants' own comments record that the move to 09-08b was
*tried and reverted* — because both panels then published the same £324 selection figure and
`_the_legs_own_regions` in the site door refused it in words. That reversion is right and this seat
agrees with it.

What the rival lane actually did is **promote by file copy**: `value_cycle_ab_s1_three_arm.json`
now holds the 21:01:30Z run and `value_cycle_ab_s1_noise_floor.json` the 23:29:22Z floor, with the
constants left pointing at the canonical names.

## THE DECISION: the promoted set survives, and this seat's constant move is DROPPED

Not a coin toss. Three reasons, in order:

1. **It is on `origin/main`.** Reverting landed work needs new evidence, and there is none: the two
   sets reach the *same rendered figures*. `THREE_ARM_PATH` resolves to the 21:01:30Z run either
   way — this seat by moving the constant, the rival by moving the bytes.
2. **Promote-by-copy is the convention** and the whole release machinery is built on it.
   `c51f98241`'s message argued for diverging from it, on the grounds that copying over
   `value_cycle_ab_s1_noise_floor.json` destroys `_current_world_bound`'s sole world-guard witness.
   That argument was *correct about the hazard and wrong about the remedy*: the fix is to move the
   witness off the overwritable path (which is exactly what `076664967` did), not to bend the
   release convention around one docstring.
3. The 09-08b floor artefact this seat's commit was carrying as untracked bytes **is now tracked**
   at HEAD. That reason to land is spent.

## What is STILL a live defect under the surviving set — measured at HEAD, not predicted

Ran `python3 -m tools.generate_value_arms_data` at `9d7cd5e4f` and read the payload:

**D1 — the headline calls the older run "now", verbatim, on the live feed.** `current_world` is the
00:19:54Z run; the panel below it is the 21:01:30Z run, **twenty-one hours later**. The composed
headline at HEAD reads:

> "IN THE WORLD AS IT IS NOW, the same comparison gives £17,739, measured 2026-09-08T00:19:54Z. …
> It is a **LARGER** advantage than the £17,453 below."

Every world guard passes — both name `39a192ce04c1eda8`. This is the *identical* defect
`c51f98241` repaired, reached by promoting bytes instead of moving a constant, and it is on the
live page now. The rival lane's `_later_runs_in_this_world` names the later run in a *footnote*;
it does not stop the headline making the currency claim. Both mechanisms are wanted.

**D2 — `_current_world_bound`'s world guard has no witness.** Line 4108's docstring names
`value_cycle_ab_s1_noise_floor.json` as the sole disk witness that satisfies the LEG guard and must
still fail the WORLD one, "which is what stops each guard being an equivalence the other one covers
for". That file now carries `world_identity.digest = 39a192ce04c1eda8`, because it is the promotion
target, and has stopped having the property the sentence claims for it.

> **CORRECTED 2026-09-09, after the port, beside the claim.** The paragraph above said the guard
> had gone *untestable* and that no artefact on disk drives that branch. **That is false, and it
> was false when written** — it was carried over from `076664967`'s reasoning without being
> re-measured against the surviving set, which is exactly the mistake this document exists to
> catch. `NOISE_FLOOR_NO_WORLD` in `tests/tools/test_generate_value_arms_data.py` — the constant
> that actually drives the world leg — **was moved to `_20260831.json` on 2026-09-09 by the same
> lane that did the promoting**, and carries a comment describing the same hazard. The guard kept
> its witness and stayed drivable throughout. What was stale is *only the producer's docstring*:
> the module's own account of its guards named one file while the control named another. That is a
> real defect — a path in a comment is a reachability edge, and this one pointed at an artefact
> that no longer refuses — but it is a documentation divergence, not a dead guard. The docstring
> repair still lands; the claim about its severity does not. **D2 is downgraded accordingly.**
> Two lanes reaching the same hazard from opposite ends within one day is the second instance of
> concurrent duplicate repair in this reconciliation (the first being `_row`'s rounding).

**D3 — `sources[]` cites an artefact the page does not read and omits two it does.** At HEAD the
field is four literals including `value_cycle_ab_s1_three_arm_20260903.json`, which `generate`
never opens, and it names neither current-world path. A citation field a reader would use to check
the page.

**Already fixed by the rival, independently — dropped from this port.** `_row`'s banker's rounding
against the door's `Math.round`. HEAD carries a `decimal.ROUND_HALF_UP` helper with a docstring
naming the same 09-08b run and the same 2026-09-09 date. Two lanes fixed one defect concurrently.
No second implementation is added.

---

## Predictions — written before the port was run

**P1.** Porting `is_the_later_run` onto the surviving set makes it `False` on the live feed, and
the string `IN THE WORLD AS IT IS NOW` disappears from `site/data/value_arms.json` entirely.
*Refuted if the string survives, or if the field comes out `True`.*

**P2.** `current_world.available` stays `True` and `composition` stays on the page. The currency
claim goes; no figure does. Specifically `value_advantage_gbp` remains 17738.642093 and
`selection_gbp` remains 270.207087 to the penny. *Refuted if any figure in the block moves.*

**P3.** The page **loses no bound**. `bound_available` stays `True` on all three legs and
`error_bar` stays available at the top level. *Refuted if the headline goes unbounded — which is
the failure mode this whole family of moves keeps producing.*

**P4.** `world_provenance.one_world_across_every_figure` stays `True`. The port touches no
constant, so nothing about which world any figure was measured in can change. This is the
**will-not-move** figure, and it is independent rather than merely conceptually separate: no code
path this port edits is upstream of `_world_provenance`, which reads the five artefacts' own
`world_identity` before `_current_world_contrast` is called. *Refuted if it moves at all.*

**P5.** `sources[]` becomes five entries, dropping `..._three_arm_20260903.json` and gaining
`..._three_arm_20260908.json` and `..._noise_floor_20260908.json`. *Refuted if the derived list
does not match what `generate` actually opens.*

**P6 — the one I am least sure of.** The two site-door mutation rungs
(`test_MUTATION_a_verdict_rendered_under_the_other_legs_lead_...` and
`test_MUTATION_an_unbounded_current_figure_is_never_rendered_bare`) currently build their subject
from `THREE_ARM_PATH`. Once the clause goes silent on the live pairing, they have no sentence to
mutate and go **vacuously green or red** — not silently correct. They need a fixture that names the
pairing. In `c51f98241` that fixture read `value_cycle_ab_s1_three_arm.json` for the *earlier* run;
under the surviving set that path is the *later* run, so **the ported helper must pin
`_20260831.json` or the fixture inverts**. I predict the unported helper fails loudly rather than
passing vacuously, because it asserts `is_the_later_run is not False` before returning.
*Refuted if it passes.*

## What would make this port wrong

If `_later_runs_in_this_world` already withdraws the currency claim, D1 is not live and the port is
duplicate machinery. Checked before writing this: it does not — the sentence above is quoted from
the payload built at HEAD, with that function present and firing.
