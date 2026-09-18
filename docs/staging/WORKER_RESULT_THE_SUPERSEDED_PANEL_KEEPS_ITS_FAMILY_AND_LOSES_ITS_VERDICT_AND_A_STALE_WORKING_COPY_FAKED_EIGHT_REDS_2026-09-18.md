**Severity:** RECORDED · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** value-arms-current-world-verdict

# The superseded panel keeps its family and loses its verdict, and a stale working copy faked eight reds

**Filed:** 2026-09-18 · **Claim id:** `the-page-publishes-two-runs-and-the-older-one-is-the-one-that-resolves`
**Grades:** `0f975710f` (HEAD at draw) · **Landed:** `ea3de3efe`

---

## State in one line

**Done and landed.** No verdict on the arms page now rests on a run the page itself marks
superseded. The 2026-09-08 block stays — its nine-seed family, its bound, its `distance_to_a_sign`
and its composition are untouched — and its two `resolved: true` verdicts are withdrawn, with the
ordering and both stamps in the sentence the reader meets. The item's recommendation was not
overturned by anything measured here.

## What was on the page

`is_the_later_run` landed 2026-09-09 and is honest: the payload says the run beside it is newer,
and `_current_world_clause` composes nothing at all on that branch. What it never withdrew is the
block's own verdict.

| field | was | is |
|---|---|---|
| `current_world.resolved` | `true`, at **24.09** SEMs from zero | `null` + reason |
| `current_world.level_leg.resolved` | `true`, at **49.46** SEMs | `null` + reason |
| `current_world.selection_leg.resolved` | `null` (its own re-draws straddle zero) | unchanged |

`legVerdict` renders `resolved: true` as **"A direction IS stated for this leg"** with nothing
beside it naming the run. So the page's most confident sentence was its oldest — ten days older
than the headline it sits under, whose own later run states no direction anywhere because its
error bar was measured over a different book. A reader taking the one that resolves was reading
the page, not misreading it.

## The cut, and why the block stays

Only `resolved` moves. `bound`, `verdict_stability`, `distance_to_a_sign`, `redraw_band` and
`composition` are asserted byte-identical across both sides of the ordering. Withdrawing the block
outright was tried in 2026-09-09's landing and reverted in the same turn — `composition` lives in
this payload, so an unavailable block takes the mission's own question, value made or value moved,
off the page with it. The claim goes and the measurement stays, which is the same cut
`_current_world_clause` makes one layer up.

**A leg already withholding keeps its own reason.** The selection leg withholds because its own
nine re-draws fall on both sides of zero — the stronger reason and the one with a remedy. The
ordering sentence is appended, never written over it. `resolved is None` is therefore left exactly
as it is; `False` is not that state and is withdrawn like `True`.

**Keyed to the ordering, not to today's pair.** The subject is the two artefacts' own stamps, so
this goes quiet of its own accord the moment a genuinely later run lands on
`CURRENT_WORLD_THREE_ARM_PATH`, and fires again with nobody editing it the next time a
promote-by-copy inverts them.

## What can fail, and what killed it

`test_which_panel_is_the_LATER_run_decides_whether_the_headline_may_claim_currency` already drove
both sides of `is_the_later_run` from three real runs; it now drives the VERDICT over the same
partition. Which legs it grades is read off the LATER run's own answer, never asserted as a
literal `True` — so the day a floor stops resolving them it says it has nothing to withdraw rather
than passing because both sides are `None` for unrelated reasons.

| mutation | outcome |
|---|---|
| the withdrawal never fires | KILLED — "a direction is stated from a run this page marks superseded" |
| withdrawal applied unconditionally | KILLED — "the withdrawal below has nothing to withdraw" |
| the bound goes with the claim | KILLED — "`level_leg.bound` moved with the withdrawal" |
| a leg's own reason clobbered | KILLED — "no reason names the ordering that removed it" |

`test_no_leg_of_a_superseded_run_states_a_direction_to_the_reader` (new, site door) is the
reader-side half, asserted BOTH ways off the published feed's own flag. Mutations killed: a
direction restored on the superseded panel; the verdicts withdrawn with no cause named; the figure
withdrawn with the claim.

`test_the_resolved_leg_is_not_given_the_withheld_legs_sentence` was keyed to today's answer — it
read the PUBLISHED level leg and `pytest.fail`ed unless it resolved — so it went red the day the
page became more honest. Re-keyed onto `_feed_whose_current_world_block_speaks`, the feed that
carries both verdict states, which is the property it was always about. That is the project's own
backwards-control shape, caught by the change that triggered it.

## The finding worth the next session's time: eight reds that were not mine

The first full run of `tests/tools/test_generate_value_arms_data.py` came back **8 failed, 239
passed**, every message about the error bar being older than the figure it bounds. None of them was
mine and none was pre-existing at HEAD.

**The shared working copy of `tools/generate_value_arms_data.py` was 187 lines BEHIND HEAD.**
Sibling lanes land through `surgical_land`, which commits the tree the commit would create and
never writes the shared working tree — so a file nobody in this session touched can sit at
HEAD-minus-several-landings while `git log` shows those landings present. The diff's direction is
what says so: hunks that DELETE content relative to HEAD are staleness, hunks that ADD it are a
holder's live work.

Attribution took a swap of exactly one file into a clean worktree at HEAD, per the standing rule:

| tree | code | result |
|---|---|---|
| worktree @ HEAD | HEAD's | 10 passed |
| worktree @ HEAD | mine (stale base + my hunks) | 8 failed |
| shared tree | HEAD's bytes + my hunks re-applied | **250 passed** |

The remedy is the one already on the map — write HEAD's bytes, re-apply only the holder hunks. The
cost of not doing it would have been a repair aimed at the error-bar pairing, which is a different
lane's live blocking finding and was never the subject.

**The one that would not have been caught by reading:** had the 8 been taken at face value, the
obvious reading is "my withdrawal broke the error bar" — the two are three functions apart and the
failures name a pairing my change cannot reach. A red whose message does not mention your subject
is the cheapest staleness tell there is, and it is worth asking before it is worth debugging.

## What this does NOT establish

The 18-seed `error_bar` family still reads `distinguishable_from_zero: true` while stating no
direction, and its bar is still older than the figure it bounds. That is
`SEAT_FINDING_THE_PAGE_PAIRED_ITS_ERROR_BAR_ON_A_CURRICULUM_SETTING_AND_CALLED_IT_THE_BOOK_2026-09-18.md`,
this lane's live blocking finding, and it is a different subject: the error bar's run is not one
the page marks superseded. Nothing here touches it and nothing here should be read as having.

`current_world.verdict_stability.sign_determined` stays `true` on the whole advantage and the level
leg. It is a property of the nine-seed FAMILY, it publishes no sentence on the branch where it is
true (`_no_sign_clause` renders only when it is `False`), and it is exactly the evidence the item
asked to keep. A reader meets no direction from it.
