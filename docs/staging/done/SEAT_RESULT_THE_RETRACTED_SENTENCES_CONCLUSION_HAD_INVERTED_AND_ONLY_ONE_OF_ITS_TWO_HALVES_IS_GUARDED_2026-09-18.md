**Severity:** RECORDED · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** value-arms-error-bar

# The retracted sentence's CONCLUSION had inverted, and only one of its two halves is guarded

**Filed:** 2026-09-18 · **Claim id:** `the-arms-producer-asserts-a-promoted-run-stamp-that-a-repromotion-has-already-falsified`
**Pre-registration:** `docs/staging/PREREG_WHAT_RETRACTING_THE_ARMS_PRODUCERS_STAMP_PAIR_MOVES_ON_THE_CENSUS_2026-09-18.md`
**Subject:** `tools/generate_value_arms_data.py`, the comment block opening at `:230`

---

## The premise, re-measured: LIVE, and larger than the item drew

The draw-time check flagged `e6b482441` as already an ancestor of `origin/main`. The commit is spent;
the defect it made visible is not. `--check` refused on this tree before the repair, `STALE 2`, both
rows at `:230`.

The duplicate-work note named `republish-the-arms-decomposition-over-one-priced-book`. It is **not**
this work. That claim holds `docs/observability/value_cycle_ab_s1_three_arm.json` and
`site/data/value_arms.json` — the artefact and the feed. This item's subject is the producer's
comment, which that claim does not hold and did not touch. Carried on, as the note allows.

## The predictions against the results

| | predicted before | measured |
|---|---|---|
| `STALE` | 2 → 0 | **2 → 0** ✓ |
| `--check` exit | 1 → 0 | **1 → 0** ✓ |
| `RECORDED CORRECTIONS` | 3 → 7 | **3 → 5** ✗ — see below, and the miss is the finding |
| `false_retractions` | 0 | **0** ✓ |
| `site/data/value_arms.json` | byte-identical | **5 lines moved** ✗ — `generated_at` and `publishing_tree_commit`, no figure |

## The third row is wrong, and it is the more useful half of this turn

I predicted four new graded rows: two retracted literals and their two `until` closures. Five
appeared, not seven. The floor half of the correction —

> *"This paragraph stated that the floor was the folded family stamped 2026-09-17T15:14:19Z, and
> that wording stood only until 2026-09-17, when `5ce5c3c31` moved `NOISE_FLOOR_PATH` on again…"*

— **does not appear in the census at all**, in either population. Measured, not inferred:

    _constants_bound_to(generate_value_arms_data, {…noise_floor.json, …three_arm.json})
      → {'THREE_ARM_PATH': 'value_cycle_ab_s1_three_arm.json'}

`NOISE_FLOOR_PATH` resolves to `…_noise_floor_folded18_single_arm_20260917.json`, a **dated sibling**,
not the canonical promote-by-copy target. So it is not an alias, `_references` returns false for
every sentence that names it, and no row is built. The sentence is neither graded nor protected.

**Why that matters rather than being a tuning detail.** The census's stated defence of a correction is
that retractions are *"COUNTED AND PRINTED with their line and text, never silently dropped: the quiet
a retraction buys is visible quiet"*. That defence covers the arms half of this correction and not the
floor half. Delete the floor sentence tomorrow and nothing anywhere notices.

And the falsification it records was real and of a class nothing catches: `5ce5c3c31` moved
`NOISE_FLOOR_PATH` **in this same file, in one commit**, and left the paragraph above it asserting the
old artefact's stamp. That is not a promote-by-copy — it is a source-line change with a stale comment
four lines away, and `git diff` showed it to a reader who did not look up. Filed separately:
`SEAT_FINDING_A_COMMENT_ASSERTING_WHICH_ARTEFACT_A_CONSTANT_NAMES_IS_UNGUARDED_WHEN_THE_CONSTANT_MOVES_IN_THE_SAME_COMMIT_2026-09-18.md`.

## The finding the item did not know it had: the conclusion inverted, it did not merely go stale

The item described two stale literals. The sentence's **verdict** had also flipped, and that is the
part a reader acts on. Measured:

    _staleness_caveat(NOISE_FLOOR_PATH, THREE_ARM_PATH)
      floor  …_folded18_single_arm_20260917.json   2026-09-17T21:39:28Z
      arms   value_cycle_ab_s1_three_arm.json      2026-09-18T05:43:40Z
      → "THE ERROR BAR IS OLDER THAN THE FIGURE IT BOUNDS. … re-running the noise floor on the
         run published above is owed work."

The comment said *"`_staleness_caveat` is satisfied rather than bypassed"*. It is neither: it
**fires**. Both stale literals were false in a direction that flattered the design, and a repair that
only corrected the dates would have left a reader believing the page carries no caveat when it carries
one with a remedy attached. The repair therefore states the live answer in words and derives it from
nowhere written down — the ordering is `_staleness_caveat`'s to answer from the two payloads, every
run, and a prose pair of stamps beside it can only ever be a second copy drifting out of date at
whichever end moves first. Both ends moved within a day of that sentence being written.

## The fifth row is wrong too, and it is a hazard worth one line

`python3 -m tools.generate_value_arms_data --help` has no argparse, so it **regenerated the feed**.
In an isolated worktree that is harmless; on the shared tree it is the known write hazard. What is
new: the output is never byte-identical from a different tree, because `publishing_tree_commit` is
the *publishing* HEAD — here `e6b482441` against the shared tree's `756a86272`, in two places plus
the composed `reading` string. Restored with `git show HEAD:… >` rather than a checkout, and the
feed is **not** in this turn's pathspec: it is the republish lane's.

No substantive figure, caveat or verdict moved, so the comment was not load-bearing. That was the
row that could have refuted "this is documentation", and it did not.

## What is owed and to whom

`_staleness_caveat` names its own remedy: re-run the noise floor over the published 09-18 book. That
is **the republish lane's**, not this one's — it holds the artefact, and a floor drawn to quiet a
sentence in a file that only reads it would be the tail wagging the dog. The comment now says so in
place of doing it.
