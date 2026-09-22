**Severity:** LATENT · **Lane:** H_harness · **Epoch:** 3 · **Atom:** delivery-lane-disposition

# The residual disposition now names what it asked, and one of the two live blanks was a query that was never built

**Filed:** 2026-09-18 · **Claim id:** `the-ordinary-not-done-sweep-still-returns-an-empty-reason`
**Grades:** `a87749340` (HEAD at draw)

---

## State in one line

**Done and landed.** `background/delivery_lane._disposition` no longer ends
`return {"disposition": NOT_DONE, "evidence": ""}`; the residual names the paths it asked git
about, the window it asked over, and what came back — and, separately, says when it could not ask
at all. The property is controlled over the whole partition in
`tests/background/test_every_disposition_names_what_was_checked.py`.

## What the item predicted, and it was right

The item corrected a prior stretch's framing: the blank is **not** a stored field in
`.delivery_lane_claims.json`, it is a literal computed at read time, so a backfill would have
fixed nothing. Confirmed — `disposition_of` reads the *draws* ledger
(`docs/observability/.delivery_lane_claims.draws.json`) and composes the answer per call. The
repair is at the return and nowhere else.

## The reading the empty string was hiding, measured on the live ledger

Three rows were on the lane at 10:20Z. Two read `not_done` with an empty string, and **they were
not the same situation**:

| row | what the lane could actually say |
|---|---|
| `reconcile-the-fork-and-take-the-repair-that-is-already-on-the-branch` | asked git about 8 named paths between 08:35 and 11:15 and got **nothing back** — a genuine miss |
| `read-next12-alone-as-the-last-family-on-the-old-instrument-...` | **names no tracked path at all**, so `_claim_paths` was empty, no `git log` was ever constructed, and the lane had no basis for any statement about it |

The second is the finding the empty string was sitting on. Its prose has left both stores, so the
three commit-joins above the residual each declined for a reason that was never "we looked" — they
declined because there was nothing to look *with*. A reader told "nothing landed" about that row
would go to `git status`, find nothing, and conclude the work was never started; the truthful
answer is that the lane cannot answer, and the remedy is to recover the item's prose, not to redo
its work. That row is the one the item itself cited as the instance — clauses two and three DID
land as mechanisms — and this is why the lane could not see it.

`_nothing_answered` now separates the two, and every branch that cannot conclude is prefixed
`CANNOT ANSWER, not 'nothing landed'`.

## The four branches, and why the exception path is one of them

`_disposition` swallows each join's exceptions on purpose — this reading feeds the orientation
brief and a raising residual would cost the brief its other twenty keys. But **swallowing is not
the same as having nothing to say**: a declared `None` and a silent `None` were collapsing into the
flattering branch. Each `except` now records which join raised, and the residual carries it.

## What DONE was, and the control

Keyed to the property the item named: **every disposition `disposition_of` can return carries a
non-empty reason**, asserted as one statement over the whole partition. Two clauses, both
load-bearing — no answer is silent, *and* the fixture rows reach every disposition the module
declares, so the first clause is never asserted over a partition smaller than the one that exists.
The partition is discovered by `ast` from the module's own return sites rather than typed, because
a hand-kept list goes stale the first time a sixth value is added, and this lane has added two in
three days.

`NOT_DRAWN` and a path-less `DELIVERED` were in the same state and are repaired with it: the item
said *every* disposition, and both of those published the identical empty string.

**Mutations, each graded rather than asserted** (runtime legs graded by patching the subject in
memory; static leg graded against mutated copies of the module under `~/.cache`, never a
shared-tree write):

| mutation | outcome |
|---|---|
| (a) residual returns the empty string again | **RED** on both the runtime and static legs |
| (b) `NOT_DRAWN` loses its reason | **RED** (static leg, line 1557) |
| (c) `_nothing_answered` returns ONE constant sentence for all four branches | **RED** on the discrimination leg — this is the leg that stops the file being a guard that passes everything |
| (d) a raised join is not recorded | **RED** on the raised-join leg |
| (e) a sixth disposition with no row here | **fired for real during the build**: `landed_unbound` was unreachable because the fixture gave the unbound commit and the sibling's landing the same instant, and `_bound_by` is keyed to the second |

(e) is worth keeping: the fixture defect was **indistinguishable from the reading being dead**, and
only the reachability clause could tell them apart.

## What I corrected rather than deleted

Four sibling controls asserted `evidence == ""` for their residual row — six sites. Every one of
them was **keyed to today's answer**: the job each was doing is real (the newer reading must not
have widened into the residual), but the empty string was only how that happened to be checkable.
Each is now keyed to the property — the residual must not carry the *other* reading's fact (the
sha, the sibling's id, the stated instant) — which survives the residual learning to speak. The
module's own comment block said the residual *"carries no evidence by construction"*; that was a
description of the code mistaken for a property of the concept, and it is corrected beside the
claim rather than rewritten over it.

One `evidence: ""` fixture is deliberately **kept**, in
`test_a_swept_row_names_which_of_the_three_dispositions_it_was.py`: it feeds `delivery_seat._prompt`,
whose `if r.get("evidence")` is the reader-side default, and a reader leg that only ever sees
populated rows stops grading the branch that runs when a future disposition arrives before its
reason does.

## Not mine, and it will red every lane that commits from the working tree

`tests/architecture/test_static_quality_ratchet.py` is red in the shared working tree: I001 is
**1307 against a frozen baseline of 1308**. Attributed, not guessed — a `git archive HEAD` extract
censuses 1308 and matches, and the one file that differs is an **uncommitted** edit to
`tests/tools/test_generate_maturity_map_data.py` that removed an import-sort violation without
moving the baseline. None of the five files this change touches carries an I001. Whichever lane
holds that edit owes the baseline line with it; a commit gated on the tree it *would* create
(`surgical_land`) does not see it.

## Files

- `background/delivery_lane.py` — `_nothing_answered`; `unanswered` recording in `_disposition`;
  reasons for `NOT_DRAWN` and a path-less `DELIVERED`; the corrected comment block.
- `tests/background/test_every_disposition_names_what_was_checked.py` — new; the partition control.
- `tests/background/test_a_swept_row_names_which_of_the_three_dispositions_it_was.py`,
  `..._asks_git_whether_the_work_landed_under_another_name.py`,
  `..._names_the_sibling_that_holds_its_windows_commit.py`,
  `test_a_window_that_closed_before_its_own_subject_existed_says_so.py` — the six pinned
  assertions re-keyed to the property.
