**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# PREREG — are the eight stale copies pure stale checkouts, or do they carry holder work?

**Filed: 2026-09-08, before the measurement, by the delivery seat (lane 0). The result is at the
bottom, beside the predictions and not in place of them.**

## The question

`tools/stale_copy_refusal --census` names eight working copies in `/home/rich/synthetic-enterprise`
that would revert a landing if committed by pathspec. The direction I drew says to repair each by
`tools/isolate_hunks.py --survey` then `surgical_land --content`, "which lands the holder hunks over
HEAD without reading the file."

**That instruction presupposes there ARE holder hunks.** There is a second possibility it does not
name: the working copy is a PURE STALE CHECKOUT — byte-identical to the file's content at some
ancestor commit, with no local edit at all. `tools/surgical_land.py` never writes the working tree
(deliberately: that is what makes it safe for a two-lane file), so **every** landing leaves every
other tree's copy at the pre-landing bytes. On that route the copy is stale with zero holder work
in it, `isolate_hunks --keep` has nothing legitimate to name, and landing anything built from it
would land a REVERT under my name.

The first diffs already lean that way — every one of the eight is deletion-dominated against HEAD
(`promote_worktree_landing.py` 37+/75−, `test_r1_inference_ceiling.py` 343+/673−) — which is the
signature of a copy that is BEHIND, not one that is ahead. But deletion-dominated is not proof:
insertions could be holder work or could be lines the intervening commits removed.

## The measurement

For each of the eight paths, walk `git log` for that path and ask whether the working copy is
byte-identical to the blob at any ancestor commit. Byte-identical ⇒ pure stale checkout, no holder
work, and the correct repair is NOT a `--content` landing.

## The predictions, written before running it

1. **At least 6 of the 8 are pure stale checkouts** — byte-identical to some ancestor blob.
2. `tools/promote_worktree_landing.py` is one of them, and the ancestor it matches is the commit
   immediately before `b06fa3528` (the binding repair).
3. **At most 2 carry genuine holder hunks** — a real in-place edit on top of a stale base.
4. **Will NOT move:** the count of eight itself. This measurement classifies the eight; it does not
   change which paths the census names, because the census's rule 1 is about traces of the last
   landing and is indifferent to whether the copy is an exact ancestor blob.

## What each answer means for the work

- **Pure stale checkout** — there is nothing of anyone's to preserve. Refreshing that copy to HEAD
  destroys no work. `git checkout <path>` is forbidden here, so the honest repair is either a
  `surgical_land --content path=<HEAD bytes>` no-op (refused: "landing HEAD's own bytes back over
  itself is an empty change"), or writing HEAD's bytes into the shared working tree directly. The
  second is what actually clears the refusal, and it is safe **only** on this branch of the answer.
- **Carries holder hunks** — the drawn instruction is right for that path and I follow it.

If prediction 1 is refuted — if most of the eight carry real edits — then the drawn direction is
right as written and the `--content` route is the whole job.

---

## THE RESULT — predictions 1, 2 and 3 are all REFUTED, and so is the drawn remedy

Measured 2026-09-08, same day, against `/home/rich/synthetic-enterprise`.

**Zero of the eight is a pure stale checkout.** Not one working copy is byte-identical to any
ancestor blob on its own path's history, and five of the eight hash to a blob that is in the object
database only via a `preserved shared-tree worktree state` snapshot. Prediction 1 said "at least
six"; the answer is none. Prediction 2 named `tools/promote_worktree_landing.py` specifically; it is
not one either. Prediction 3 said "at most 2 carry genuine holder hunks"; the true count of copies
carrying *something* HEAD does not have is eight.

**Prediction 4 held.** The census still names eight paths. Classifying them moved nothing.

### But the third possibility was the real one, and neither the direction nor I had named it

The eight are not stale checkouts and they are not stale-base-plus-an-edit. They are **rival
copies**: another lane wrote the same feature, independently, and the two versions differ in prose
throughout. That is `feedback_two_lanes_can_fix_the_same_defect_concurrently` at file scale.

And they split cleanly in two, by a test that is not a matter of taste — does the copy supply any
**symbol** HEAD does not have?

| | path | new symbols | what the "insertions" actually are |
|---|---|---|---|
| A | `tools/promote_worktree_landing.py` | **0** | a `_bind_to_claim(commit, work_id)` **without the `since` argument** — i.e. the pre-`b06fa3528` version, differently worded |
| A | `simulation/policy_costs.py` | **0** | alternative wording of two error strings; missing the 2026-27 RO rate and the 2026/2027 CCL rates entirely |
| B | `background/self_clearing_alarm_census.py` | 4 | `_cited_siblings`, `_own_carriers_named`, `rows_graded_by_resemblance`, `REASONED_FIELDS` |
| B | `site/test_harness_delivery_record.py` | 2 tests | |
| B | `tests/tools/test_commit_refusal_attribution.py` | 3 tests | |
| B | `tests/tools/test_dd_opening_arms.py` | 2 tests | |
| B | `tests/tools/test_r1_inference_ceiling.py` | ~10 tests | |
| B | `site/harness/index.html` | (not measured — page anchors, not Python) | |

### What this does to the drawn instruction

The direction said: *"Route each through `isolate_hunks --survey` then `surgical_land --content`,
which lands the holder hunks over HEAD."* For the two **Kind A** files that instruction has **no
legal application**: there are no holder hunks. Every hunk they carry is either identical prose
reworded or a strictly weaker version of code HEAD already has. `isolate_hunks` is default-deny and
refuses when nothing is selected — *"landing HEAD's own bytes back over itself is an empty change
wearing a commit's clothes"* — which is the correct refusal, and it means **the `--content` route
cannot repair a Kind-A copy at all.**

Most sharply: the direction says `promote_worktree_landing.py` "is missing all 14 lines of
`_bind_to_claim`, the binding repair". It is not. `_bind_to_claim` is right there in the shared
copy. What is missing is the **`since` parameter** — the fix for the defect where the binding bound
four of *another lane's* paths and printed a plausible success line. The census's own wording ("not
one of the 14 distinctive lines commit `b06fa3528` added here") is exact and the direction's
paraphrase of it is not; the paraphrase reads as "the function is gone" when the truth is "the
repair inside it is gone". Same conclusion about the danger, materially different repair.

### Why that changes what "repair" can mean

A Kind-A copy needs its bytes **replaced by HEAD's**, and that is a write into the shared working
tree, which `--content` explicitly never does. The only in-repo moves that do it are `git checkout
<path>` and `git stash`, both of which `CLAUDE.md` forbids — and they are forbidden *for exactly
this class's sake*: they discard the holder's work. The prohibition is right in general and, for a
Kind-A copy where the holder's work is provably nil, it forbids the only move that helps.

**That gap is the finding, and it is filed separately** as
`SEAT_FINDING_THE_STALE_COPY_REMEDY_HAS_NO_MOVE_FOR_A_RIVAL_COPY_HEAD_ALREADY_SUPERSEDES_2026-09-08.md`.
This turn did not invent a move for it; inventing an unsanctioned write into another lane's tree is
precisely the class of decision that should not be made inside one bounded turn.
