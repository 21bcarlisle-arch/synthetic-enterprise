**Severity:** BLOCKING · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# PRE-REGISTRATION — what the stash-clock repair to `taken_before` will and will not admit

*Filed by the delivery seat from an isolated worktree, 2026-09-24, BEFORE the repaired code was run
against the shared tree. Claim id
`taken-before-should-take-its-clock-from-the-stash-object-not-the-file-mtime`.*

## The duplicate-work check, resolved first

The draw named two live claims that "may be this work under another name".

1. **`taken-before-should-take-its-clock-from-the-stash-object-not-the-file-mtime`** — this very
   id, sitting in `docs/observability/.seat_work_in_hand.json` with `"paths": []` and
   `claimed_at` 1790262305 (2026-09-24 15:05:05Z), written by the invocation that filed
   `d11ddba3c`. The two claim stores are separate and `delivery_lane --release` does not clear
   `.seat_work_in_hand.json`, so a residue under the same id is the expected shape, not a
   collision. **No disposition is owed; the work is unspent.** `d11ddba3c`'s message says the
   repair is "named, not built", and `grep -in stash tools/stale_copy_refusal.py` at `f76f34e84`
   returns exactly one line — a prose mention of the never-do list at line 1742, no mechanism.
   Nothing is built.
2. **`value-arms-error-bar`** holds `tests/background/test_a_swept_row_names_...py` and
   `tests/background/test_publish_gate_subject_is_head.py` — two of the paths this item names.
   It holds them because `delivery_lane` binds by path and those two are gap paths a prior
   landing touched. It is **genuinely different work on the same subject**: this item does not
   edit either file's content, it decides whether the shared tree's stale copy of them may be
   discarded. Carrying on, as the draw's own note licenses.

## What is being changed

`tools/stale_copy_refusal.taken_before` asks `committed_at(commit) > mtime`. A `git stash` restore
rewrites every file it touches with one fresh mtime, so bytes snapshotted before a landing read as
authored after it. The repair: when the file on disk is byte-identical to a stash-shaped commit's
blob for that path, and that stash is older than the landing, `taken_before` says True.

Established before writing the prediction (these are facts, not predictions):

* All **six** contested `.py` gap paths on the shared tree are byte-identical to `23e9917bc`'s blob
  for their own path. Verified by `git hash-object` vs `git rev-parse 23e9917bc:<path>`.
* `23e9917bc` committer date is **1790258469** (2026-09-24T15:01:09+01:00).
* Three of the six (`site/test_the_book_is_bounded_by_compute_reaches_the_reader.py`,
  `tests/background/test_harden_rung_pass_ceiling.py`,
  `tests/tools/test_discovery_pass_ceiling.py`) are ALSO byte-identical to `origin/main`, so they
  are `already_at_head` and no door is owed for them.
* The repo holds **15** stash-shaped commits nameable from a ref, and `refs/stash` still resolves.

## PREDICTIONS

Written before running the repaired `refresh_to_head --base origin/main` over the shared tree.

1. **`taken_before` flips to True for all three contested paths** — `test_a_swept_row_names_...`,
   `test_publish_gate_subject_is_head.py`, `test_publish_gate_wedge_draw.py` — because each one's
   last landing on `origin/main` is after 15:01:09+01:00. It stays False for the three
   `already_at_head` paths only incidentally (they have no `judge` complaint to reach).

2. **`refresh_to_head --base origin/main` will admit exactly TWO of the three, not three.** The two
   that were refused `refused_head_does_not_supersede_it` (`test_a_swept_row_names_...`,
   `test_publish_gate_subject_is_head.py`) are refused for want of a stale-copy complaint, and that
   is precisely what this repair supplies. `test_publish_gate_wedge_draw.py` was refused
   `refused_supplies_names_head_lacks` (`prc`) — a CONTENT verdict about a name the base lacks,
   which the clock does not touch. **I predict it is still refused after the repair**, and that if
   it is not, the reason is not this change and must be attributed separately.

3. **The repair does not reach a copy anybody typed.** Measured as: over the shared tree's
   tracked-modified paths, the set of paths on which `taken_before` newly returns True is a subset
   of the 321 files `23e9917bc` restored. I predict the newly-True count is **between 3 and 40**
   — non-zero because the three above are in it, and bounded well under 321 because most restored
   files have had no landing since 15:01:09 for the clock to be compared against.

4. **The enactment does not clear the checkout.** `contains_origin` stays `false` after enacting
   what the repair admits, because the two live daemon-written JSON artefacts
   (`docs/observability/agent_status.json`, `site/data/tick_heartbeat.json`) are untouched by this
   item on purpose and are a different class.

## What done means for this item

Direction, not an atom, so this is stated rather than inherited:

* `taken_before` takes the stash object's clock when the bytes came out of a stash — **landed**.
* A control that fails when it does not — a test that goes red if the stash leg is deleted, and
  green only because the stash leg is there — **landed**.
* `refresh_to_head --base origin/main` re-run over the six paths on the shared tree and whatever it
  now admits **enacted**, with the result written up beside this prediction whether or not it
  matches.
* The two daemon-written artefacts **left alone**, named as the residue.

---

# RESULT — written after the run, beside the predictions it refutes

## Prediction 1 — PARTLY WRONG, and the wrong part is an attribution error

I said `taken_before` "flips to True for all three contested paths". Measured against the shared
tree with the OLD leg and the NEW leg asked separately:

| path | `landed > mtime` (old leg) | stash clock adds it |
|---|---|---|
| `tests/background/test_a_swept_row_names_...windows_commit.py` | **True already** | True |
| `tests/background/test_publish_gate_subject_is_head.py` | False | **True** |
| `tests/background/test_publish_gate_wedge_draw.py` | False | **True** |

`test_a_swept_row_...` was **already** `taken_before`-True before this repair: its last landing
`8d84c67b5` is at 15:15:10+01:00 and the restore stamp is 15:02:31+01:00, so the mtime leg answered
True on its own. The repair changed nothing for that path, and the inherited finding's claim that
"six of the nine contested gap paths are in that cohort" is true about the RESTORE but not about
which paths the clock leg was blocking. **Two paths flip, not three.**

## Prediction 2 — REFUTED. One admitted, not two

`refresh_to_head --base origin/main` over the six, with the repair live:

| path | verdict | what happened |
|---|---|---|
| `tests/background/test_publish_gate_subject_is_head.py` | `refreshable` | **REFRESHED**, 9 lines preserved at `refs/preserved/refresh-to-head/seat-stash-clock-subject-is-head` (`a62507b70`) |
| `tests/background/test_a_swept_row_names_...windows_commit.py` | `refused_head_does_not_supersede_it` | still refused |
| `tests/background/test_publish_gate_wedge_draw.py` | `refused_supplies_names_head_lacks` (`prc`) | still refused — **as predicted** |
| the other three | `already_at_head` | nothing owed |

### Why `test_a_swept_row_...` is still refused, and it is a SECOND defect, not this one

`taken_before` is True for it and `judge` still returns `None`, because `judge`'s older-clock leg
is `if missing and taken_before(...)` and `missing` is **zero**. `8d84c67b5` added exactly two
distinctive lines:

```
lambda *_a, **_k: ([SUBJECT_PATH],
[(OWNED_SHA, IN_WINDOW, "the work", [SUBJECT_PATH])],
```

and the stashed copy carries **both** — because the stash is where that fix came from. A lane had
it uncommitted at 15:01:09, another stash captured the whole tree, and the lane landed it at
15:15:10. So the copy genuinely is not a revert of `8d84c67b5`'s code.

**What it IS a revert of is `8d84c67b5`'s six-line comment**, which explains that the stub had
drifted on both axes and was red at HEAD — replaced in the working copy by the four-line comment
that landing superseded. `_trivial(..., comments_are_evidence=False)` excludes comments from
`distinctive_lines` by construction, so no rule in this module can see a copy whose only loss is
landed prose inside a `.py` file.

**That is BLOCKING by construction and it is not the clock.** `refresh_to_head` tells the reader
*"the stale-copy control has NO complaint about this copy … Refreshing it would discard an ordinary
edit"* — an instrument asserting something it has not measured, about a copy that demonstrably
reverts a landed comment block. Widening `comments_are_evidence` at this call site is a decision
with its own blast radius (every reformat and every docstring edit becomes evidence) and is
deliberately NOT taken here. **Filed, not built** — the next item, and it is the reason the
fast-forward is still short two paths.

## Prediction 3 — CONFIRMED, and near the bottom of the range

Over the 459 paths the shared tree has modified against `origin/main`: **11** were already True by
mtime, and the stash clock newly reaches **6** — inside the 3-to-40 band I registered, and every
one of the 6 is a file `23e9917bc` differs from its parent on (the check I registered; the commit
touches 435 paths against its parent, where the inherited finding's 321 counted what the restore
wrote — two different counts and the difference is stated rather than smoothed over):

```
background/supervisor.py
docs/design/ANNUAL_REPORT_IMPORT_DEBT.md
docs/observability/self_clearing_alarm_census.json
tests/architecture/test_no_tree_scan_passes_on_an_empty_population.py
tests/background/test_publish_gate_subject_is_head.py
tests/background/test_publish_gate_wedge_draw.py
```

Six newly-reached paths out of 459, all of them inside the restore. The repair does not reach a
copy anybody typed.

## Prediction 4 — CONFIRMED, and the residue has changed shape

`checkout_drift()` after the enactment: `{"behind": 22, "ahead": 0, "contains_origin": false,
"gap_paths": 29}`. **`ahead` is now 0**, so the advance is a pure fast-forward and the inherited
finding's "the advance is a MERGE, not an FF" is stale — `origin_reconcile` closed the ahead leg
while the behind leg grew. Ten of the 29 gap paths are dirty or untracked, down from the set that
included `test_publish_gate_subject_is_head.py` before this turn:

* **2 stash-restored `.py`** — `test_a_swept_row_...` (the comment-block defect above) and
  `test_publish_gate_wedge_draw.py` (`prc`, holder work, needs `isolate_hunks`).
* **3 stash-restored `.py` byte-identical to `origin/main`** — dirty against the behind HEAD only.
* **5 untracked `docs/staging/` findings that origin already carries** — a third class again, and
  not one any refresh door reads.

The two live daemon-written artefacts (`docs/observability/agent_status.json`,
`site/data/tick_heartbeat.json`) are **no longer in the gap at all**, so the item's instruction to
leave them alone cost nothing.

## What landed

* `tools/stale_copy_refusal.stash_snapshots` / `stashed_before` / `blob_ids`, and `taken_before`
  reading the earliest instant the bytes can be shown to have existed rather than the file's stamp.
* `tests/tools/test_stale_copy_refusal.py::test_the_clock_reads_the_stash_that_holds_the_bytes_and_not_the_stamp_of_the_restore`
  — a five-way partition over one landing, seven mutations run and all seven red:

  | mutation | flips |
  |---|---|
  | drop the stash leg from `taken_before` | `a.py`, `e.py` |
  | drop `stashed_before`'s `oid == disk` test | `b.py` |
  | drop its `when < before` bound | `c.py` |
  | drop the mtime comparison | `d.py` |
  | stop reading the stash reflog | `e.py` |
  | stop reading the ref namespace | the source assertion |
  | order snapshots latest-first | the source assertion |

  **The first draft of that control had a NO-OP mutation and it is recorded in the docstring**:
  both stashes were reachable through `for-each-ref`, so deleting the reflog reader left the suite
  green. `e.py`'s stash is now buried under a later one, which is the ordinary state of any stash
  that is not the most recent, and the reflog is the only thing that can find it.
