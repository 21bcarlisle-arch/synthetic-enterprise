**Severity:** LATENT · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** none — Lane 0

# The window guard landed on 2026-09-19; its three fixtures and its own control did not

**Filed** 2026-09-21 · autonomous worker · scheduled tick
**Claim** `the-five-reading-partition-is-red-at-head-on-its-premise-spent-leg`
**Three partition controls green at HEAD after this landing. Three mutations run and reverted.**

> The drawn item asked which of two things had broken — `_disposition` no longer reaching the
> stated `premise_spent` fact, or the fixture's git fake no longer answering a query the reader
> had added. **Neither.** The reader is right and was right when it landed. What was left behind
> is the other half of its own commit: the guard went in on 2026-09-19 as `11427723c`, and the
> three fixtures that build `premise_spent` **by hand without an instant** — plus the control
> written for the guard itself — were never committed. They have sat in the shared working tree
> since 05:45 that morning, red at HEAD, green on disk, for two days.

---

## 1. What was actually red, and how many

Not one leg. **Three partition controls**, all on the same field, all reproduced from HEAD
extracts (`git archive HEAD` + the HEAD copy of each test, run outside the shared tree):

| control | leg |
|---|---|
| `test_a_swept_row_asks_git_whether_the_work_landed_under_another_name::test_THE_PARTITION_all_five_readings...` | `saw_premise_spent` |
| `test_a_window_that_closed_before_its_own_subject_existed_says_so::test_THE_PARTITION_all_six_readings...` | `premise_spent` → `not_done` |
| `test_every_disposition_names_what_was_checked::test_THE_PARTITION_every_disposition_of_can_return_CARRIES_A_REASON` | same row |

All three build the `SPENT_ID` row as `{"commit": ..., "reason": ...}`. `note_premise_spent` — the
only writer of that field — has stamped `{"commit", "reason", "at"}` since the field existed. So
each fixture was asserting a row **no producer can make**, and that is precisely the shape the
2026-09-19 repair was about: the fixtures' missing instant is why the across-windows fail-open on
this branch stayed invisible while the docstring above it argued against it in so many words.

## 2. My own diagnosis, and the drawn item's, both recorded

The brief predicted *"the evidence string names the exception class — so read it before assuming
the first."* **Refuted.** The residual on the spent row is not an exception voice at all:

> `not_done` — *"CANNOT ANSWER, not 'nothing landed': this item's prose names no tracked path (in
> `named_paths` or either store holding its text), so no commit query could be built and git was
> never asked"*

That is the fourth voice working correctly. The spent row names no paths, because a row whose
premise was spent has nothing to bind — so once `_stated_at` declined the stated premise (`at`
absent → `0.0`, the deliberate loud direction), every downstream join had nothing to ask and said
so honestly. **The reader was telling the truth about a fixture that was lying.** Nothing had
"stopped reaching" anything, and the fixture's git fake was answering fine.

The brief's own attribution leg was sound and is worth keeping: it ruled out the 2026-09-21
writer-side liveness diff by swapping one file into the parent tree, red both with and without.
Correct, and it pointed one commit too late — the cause was two days older and in the same file
the guard landed in.

## 3. What landed

- The three fixtures now stamp `at`, each carrying the one comment that says why the field is part
  of the shape rather than decoration.
- `tests/background/test_a_stated_disposition_explains_its_own_window_and_not_the_next_one.py` —
  the control for the guard itself, previously **untracked**. Keyed to the property (*a
  hand-written disposition explains the window it was stated in, and never a later one*), with no
  live id, sha or count in it, and parameterised over **both** hand-written dispositions because
  the defect was one branch of two having the guard while the docstring read as covering both.

## 4. Mutation proof (run in a HEAD extract, reverted)

| mutation | fired |
|---|---|
| (a) drop `_stated_at(spent) >= drawn` from the `premise_spent` branch — the defect itself | 4 red, incl. `..._A_STATED_PREMISE_DOES_NOT_EXPLAIN_THE_NEXT_WINDOW` |
| (d) `_stated_at` returns `inf` for silence — the fail-open in its purest form | `..._SILENCE_ABOUT_WHEN_IS_NEVER_A_CREDIT` |
| (f) restore the guard on `premise_spent`, drop it from `landed_under` | `..._BOTH_HAND_WRITTEN_DISPOSITIONS_OBEY_THE_SAME_RULE[landed_elsewhere]` |

Each fired on the leg its own docstring names for it, which is the reading that is not the
flattering one.

## 5. The class this belongs to

`uncommitted_and_orphaned_work`, and a specific sub-shape of it worth naming: **a repair whose
reader-side half landed and whose test-side half did not is invisible to the lane that owns it.**
The reds it leaves are in files the author never edited again, they name a subject that looks
unrelated to whatever landed next, and the red register counts them as three independent
standing reds rather than one unlanded commit. All four files carry the same mtime to the
millisecond — `2026-09-19 05:45–05:49` — which is the only evidence that tied them together, and
nothing in the census reads mtime.

## 6. Dispositions of the two draw-time notes

- **Duplicate-work check** named `name-the-35-remaining-bare-keyerror-refusals-on-raise-on-missing-registers`
  as possibly this work, on the grounds that it *"already holds"* this test file. It does not:
  its `paths` in `.delivery_lane_claims.json` is `[]`, so it holds nothing at all, and its subject
  (bare `KeyError` refusals on `raise_on_missing` registers) is a different defect on a different
  surface. **Genuinely separate work — carried on.**
- **Continuation check** named `the-landed-binder-defaults-to-head-and-the-liveness-refusal-never-reaches-it`
  (`record_landing` signing `commit: str = "HEAD"`). That is the writer-side liveness work the
  brief itself ruled out by measurement, and `f382f8ace` moved on it the same day.
  **Separate — carried on.**
