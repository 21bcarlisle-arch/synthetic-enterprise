**Severity:** LATENT · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** promoted-artefact-claim-census

# SEAT RESULT — the census read corrections as claims, and the unit it read them in was hiding a live one

**Pre-registration:**
`docs/staging/PREREG_WHAT_A_RETRACTION_CLASS_AND_A_COMMENT_BLOCK_UNIT_MOVE_ON_THE_PROMOTED_ARTEFACT_CENSUS_2026-09-18.md`
**Claim id:** `repair-the-census-that-reads-a-retraction-as-a-live-claim`
**Class:** `controls_that_cannot_fail`

---

## What was wrong, and it was the control rather than the code

`tools/promoted_artefact_claim_census.py --check` refused the whole tree for
`tools/generate_value_arms_data.py:9883` — a comment whose own text says the sentence it describes
*read "published beside the 2026-08-31 run" until 2026-09-09* and was repaired. The live expression
beside it is a `{when}` placeholder resolved from the other panel's payload. **The code was right
and the census was wrong.**

The instance matters less than what it priced. CLAUDE.md requires *"Correct yourself plainly, in the
record, beside the claim"* — a wrong prediction kept next to the result is the only evidence the
experiment predated its answer. This control refused the tree for exactly that, and **the cheapest
way to clear the red was to delete the account of the defect**, which destroys the attribution and
leaves the census green. The control was paying for the destruction of its own evidence.

---

## The repair, and why neither half is a narrowing

**(A) The claim unit for comments is now the contiguous BLOCK.** `tokenize` hands back one row per
`#` line because that is how the file is stored; a wrapped comment is one piece of prose and the
place it wraps is set by the column ruler. Blocks are joined, then `_sentences` cuts them — the same
order a docstring already got. Trailing comments (`x = 1  # foo`) are never joined: two remarks
about two statements are not one wrapped sentence, and running them together would mint a claim
nobody made.

**(B) A RETRACTION is a graded class, not an exemption.** A sentence is one when it carries BOTH a
past-tense report of a former *wording* (`read`, `said`, `stated`, `called`, `previously`, `used
to`, `no longer`, `withdrawn`) AND a stated ending (`until <run-identity token>`, `became false`,
`went false`, `no longer`, `has since`). Then it is graded:

- literal no longer matches the run at the path → the retraction is **accurate**: printed under its
  own heading, kept out of STALE.
- literal **still** matches → **FALSE RETRACTION**, and `--check` refuses. You say this ended; the
  bytes say it did not.
- the `until <token>` half is exempt from that grading — it names *when* the wording ended, so a
  correction written on the day of the promotion it records does not red itself.

Both halves are required precisely because either alone is a password: `read` appears in every other
line about an artefact and `until` in every deferral. **A writer who wants the census to stand down
must state what it read and until when — which is the attribution the control exists to protect.**

**The limit, on the surface and not in a footnote.** This cannot detect prose that lies. A
fabricated retraction of a *live* claim is caught (that is the false-retraction leg); a fabricated
retraction of a genuinely dead one is not, and no rule over English could be. The protection is that
retractions are **counted and printed with line and text** — the quiet a retraction buys is visible
quiet, so deleting the account of a defect is no longer the cheap path.

---

## Predictions, against results

| | Prediction | Result |
|---|---|---|
| **P1** | (A) alone does NOT clear the 9883 red | **HELD.** Still STALE at 9882 with the joined sentence. Had it cleared, (A) would have been a silencer. |
| **P2** | (A) alone raises the total row count | **HELD, larger than expected.** Rows 16 → 23, distinct claims 11 → 17, **STALE 1 → 4**. Six claims the line-at-a-time unit could not see. |
| **P3** | (A)+(B) takes STALE to 0 and `--check` to exit 0 | **REFUTED, and the refutation is the finding below.** STALE is **2**, not 0. `--check` still exits 1. |
| **P4** | the three pre-repair instances out of `77d92e0d1^` still replay | **HELD.** All 10 pre-existing controls green, unchanged. |
| **P5** | no other reported row is reclassified as a retraction | **HELD.** ordering-only 8 → 12 (block join, not reclassification); cannot-tell unchanged at 2; all 3 retractions are at the two sites named below. |

**P3 was wrong because I assumed the only STALE in the tree was the false positive I was sent to
fix.** That was the drawn item's claim about the tree and I carried it forward without re-asking it.
Widening the unit found live claims that had never been gradable, and the census is now *more*
honest and *still* red. Recording the wrong prediction beside the result rather than revising it —
which is the habit this whole repair exists to stop the census punishing.

---

## What (A) found: a second retraction, and a live stale claim

**A SECOND instance of the retraction class**, at `tools/generate_value_arms_data.py:340`:

> `IT SAID "IN THIS REPOSITORY" UNTIL 2026-09-18 AND THAT WENT FALSE IN THE COMMIT THAT LANDED
> value_cycle_ab_s1_noise_floor_next12_20260917.json …`

Independent of the drawn one, written by another lane, invisible to the old unit, and caught by the
predicate without tuning. **That is what makes this a class repair rather than a rule fitted to one
comment** — the thing a narrowing added for a false positive can never show.

**A LIVE STALE CLAIM the census has been blind to for its whole life**, at
`tools/generate_value_arms_data.py:230` — and it is owed, not fixed:

> `Both floors and THREE_ARM_PATH carry world digest 39a192ce04c1eda8 … and the folded family is
> stamped 2026-09-17T15:14:19Z against the arms' 2026-09-10T14:04:08Z, so _staleness_caveat is
> satisfied rather than bypassed.`

`docs/observability/value_cycle_ab_s1_three_arm.json` now declares `generated_at
2026-09-18T05:43:40Z`. **The sentence is false as the tree stands** — falsified by a promote-by-copy
with no source edit, which is the exact mechanism this census exists for. It was invisible because
`THREE_ARM_PATH` and `2026-09-10T14:04:08Z` sit on different physical lines.

It is **not a retraction** — it is a present-tense justification of a current design keyed to the run
that used to be there — and the predicate correctly declines to stand down for it.

**Why it is not fixed here.** The draw is explicit: *"Fix the class at the census, NOT the instance
at the contested producer."* `tools/generate_value_arms_data.py` is the subject of the live claim
`republish-the-arms-decomposition-over-one-priced-book`, which is republishing that very artefact
right now; its stamps are the thing in flight. Rewriting another lane's in-flight sentence to clear
my own red is how a repair destroys an attribution. **Owed to the republish lane**, and the honest
repair is the one this census now rewards: say what it read and until when, or derive the stamp from
the payload as `how_to_read_this` already does with `{when}`.

## A second, smaller thing fixed in passing

`--json --check` refused on `result["feed"]`, while `--check` alone did not. The feed leg is
documented as fail-open and `test_the_feed_leg_fails_open_and_the_module_says_so` pins the text path
— so the two exits disagreed about whether a legitimate dated record is a refusal, and only the text
path was controlled. The JSON path now refuses on the same two legs as the text path.

---

## Controls, and the mutation each one is proven against

Seven mutations applied in this isolated worktree, each reverted; every one is caught, and each
control fires on the mutation it names. The first is the partition control, because the rest are
worthless without it: a classifier answering "retraction" to everything passes every stand-down
test, and one answering "live claim" to everything passes every still-refuses test.

| Mutation | Caught by |
|---|---|
| `_is_retraction` → `False` | partition · past-tense-account · not-yet-true · closure-date |
| `_is_retraction` → `True` | `test_a_stale_claim_is_caught_and_a_true_one_is_not` (pre-existing) |
| verb alone is enough | `test_half_a_retraction_buys_no_silence` |
| closure token graded as a claim | `test_the_date_a_retraction_closes_at_is_not_graded_as_a_claim_about_the_run` |
| `false_retractions = []` | partition · `test_a_retraction_that_is_not_yet_true_refuses` |
| blocks not joined | `test_a_wrapped_comment_is_one_claim…` · `test_a_dated_measurement_is_still_a_live_claim` |
| trailing comments joined | `test_two_trailing_comments_are_not_joined_into_a_sentence_nobody_wrote` |

18 controls green in `tests/tools/test_promoted_artefact_claim_census.py`, up from 10.

---

## The duplicate-work check

`republish-the-arms-decomposition-over-one-priced-book` was named at draw time as possibly this work,
"already holds `tools/generate_value_arms_data.py`". **That premise is false** — read out of
`docs/observability/.delivery_lane_claims.json`, its bound paths are the arms feed, the three-arm
artefact, two site doors and four staging docs; the producer is not among them. This turn touched
`tools/promoted_artefact_claim_census.py` and its test file only: **zero path overlap**. Disposition:
carried on, neither `--landed-under` nor `--release`.
