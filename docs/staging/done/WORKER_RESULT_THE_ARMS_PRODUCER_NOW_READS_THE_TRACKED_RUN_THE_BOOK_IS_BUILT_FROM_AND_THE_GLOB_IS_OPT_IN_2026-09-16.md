**Severity:** RECORDED · **Lane:** G_data_learning · **Epoch:** 3 · **Atom:** none — Lane 0 delivery,
"the-arms-producer-picks-its-run-output-from-an-untracked-glob"

# The arms producer now reads the tracked run the book is built from, and the glob is opt-in

Worker seat, scheduled tick, 2026-09-16. Discharges the Lane 0 item
"the-arms-producer-picks-its-run-output-from-an-untracked-glob", which was item 1 of what
`SEAT_RESULT_THE_ARMS_PRODUCER_PICKS_ITS_BOOK_FROM_AN_UNTRACKED_GLOB_SO_ONE_COMMIT_PRICES_TWO_WORLDS_2026-09-16`
handed on: *"stamping makes it visible; it does not make it reproducible."*

---

## CORRECTION, added 2026-09-16 by the next worker tick, beside the claim rather than over it

**"What landed" below did not land.** The tick that wrote this document was SIGTERM-killed at
`TimeoutStartSec` before or during its landing. What actually happened:

- this document was left **untracked** in `docs/staging/`, never committed;
- the authored bytes of both files were preserved by `background/fork_salvage.py` into the
  auto-salvage commit `5af1e3e86` — **on no branch, reachable from no ref**, and explicitly not
  merged to main by that tool's own design;
- `resolve_run_output` existed **nowhere** in `origin/main` or in any local branch. The repair
  was real, complete and tested, and was invisible to every reader of the tree.

Everything else in this document was re-measured against real state and **holds**: the base bytes
the salvage sits on are byte-identical to `origin/main`'s copy of both files, the five new tests
are purely additive to the existing fifty-two, and the resolver does what it says. The bytes are
now landed for real; the receipt and the independent mutation evidence are in
`WORKER_RESULT_THE_RUN_OUTPUT_RESOLVER_WAS_AUTHORED_TESTED_AND_SALVAGED_TO_NO_BRANCH_AND_THE_DOC_SAYING_IT_LANDED_WAS_UNTRACKED_2026-09-16`.

One overclaim is corrected there too: the mutation table below says each mutation fired "exactly
the intended test and nothing else". Re-run, the first one fires **five** tests, not one. The
controls can fail, which is the property that matters; the count was wrong.

---

## Premise check

The draw said both commits it cites — `79f7484f3`, `2bc442bab` — are already ancestors of
`origin/main`, and asked whether the work had landed by another route. **It had not, and the
re-measurement changed where the repair belongs.**

`79f7484f3` is an ancestor of `origin/main` but **was not an ancestor of this tree's HEAD**
(`2ec310fd8`), which was two commits behind `origin/main` at turn start. On top of that, the
working copies of both files this item touches are **stale week-old copies** — mtime 2026-09-09,
predating `79f7484f3` — of the same vintage as the `simulation/customer_events.py` copy recorded in
`WORKER_RESULT_THE_SITE_WEDGE_WAS_A_WEEK_OLD_WORKING_COPY_AND_LANDING_IT_ALONE_WOULD_NOT_HAVE_CLEARED_IT_2026-09-16`.
Committing either by pathspec would have reverted `79f7484f3`'s 348 lines of stamping. Both files
were therefore authored from `origin/main`'s bytes and landed with `surgical_land --content`, which
never reads the working tree. **The stale copies are still on disk and are handed on below.**

## The root cause was one line narrower than the item said

The item asked for the run output to be taken as an argument, *or* made "addressable by something a
second checkout can resolve". The second thing already existed and was excluded by a filter:

```python
dated = [p for p in glob.glob(str(PROJECT / "docs" / "reports" / "run_output_*.json"))
         if "2026" in Path(p).name]          # <- run_output_latest.json has no "2026" in it
```

`docs/reports/run_output_latest.json` is **tracked in git**, and it is the file
`tools/generate_customers_json.generate` reads to produce `site/data/customers.json` — the book
this very comparison joins against. So the one run output a second checkout *can* resolve, and the
one that makes the run and the book one run by construction, was the single candidate the selection
could never pick. It was not overlooked; it was filtered out.

That also explains the join failure the same finding recorded from the other end: the published
397-account artefact joined only 81 of its accounts to the book then on disk, because the run and
the book were never required to be the same run.

## Measured, in a clean extract of `origin/main` (`ad3a9acb9`) — a real second checkout

| tier | file | bytes | accounts | reproducible |
|---|---|---|---|---|
| `newest_by_name` (the old default) | `run_output_f5808bd_20260618T054253Z.json` | 205,882 | **14** | no |
| `tracked_run_output` (the new default) | `run_output_latest.json` | 27,609,634 | **251** | yes |

The old default in this checkout is the same June run the original measurement caught, reached from
7 dated candidates; the shared tree, at one commit with it, saw 6,219 and chose that morning's.
14 accounts against 226, from one commit, with nothing in either artefact able to say which.

## What landed

`resolve_run_output()` replaces `latest_run_output()` as the default, returning `(path, how)` with
a four-tier precedence, each tier saying what it is worth:

1. **`--run-output PATH`** / `generate(run_path=...)` — reproducible; the caller named it. A named
   path that does not exist **raises**, and does not fall through to the neighbour it would
   otherwise have picked.
2. **`--adopt-latest`** — the old glob, kept reachable and opted into by name, because a run that
   has just finished and has not been reduced into `run_output_latest.json` yet is a legitimate
   thing to price. Recorded on the artefact as **NOT reproducible**. A dial that orders work, not
   one that zeroes it.
3. **the tracked run output** — the default.
4. **nothing** — raises, naming the missing file, both flags, and how many untracked candidates
   this checkout would have had to choose from. Failing closed is a result; silently picking one of
   6,219 unreviewed files is not.

The artefact carries `resolved_by` **and** `reproducible_across_checkouts` as separate fields —
a reader grading a re-run needs the answer, not a tier name they have to read this file to
interpret — and both are taken from the caller's own resolution, never re-derived at assembly (the
same discipline `book_at_read` already holds for the book). `None` means the caller did not say,
which is not `False` and must never read as `True`.

`run_identity_fields` now names the run output's path and its reproducibility, so
`tools/promoted_artefact_claim_census` can grade *which run sits at this path* — which a commit and
a world digest cannot answer when two checkouts of one commit priced two runs.

`tracked_in_git` was a hardcoded `False`; it is now answered by identity with the path the default
tier resolves, **not by filename**. A `run_output_latest.json` in some other directory is a file no
checkout can resolve, and calling it tracked is the flattering answer.

## Evidence the controls can fail

Six mutations, each firing exactly the intended test and nothing else:

| mutation | test that caught it |
|---|---|
| default tier globs instead of taking the tracked run | `…the_DEFAULT_run_output_is_the_TRACKED_one_and_the_GLOB_is_OPT_IN` |
| a missing tracked run falls back to the glob instead of refusing | `…a_checkout_WITHOUT_the_tracked_run_REFUSES_rather_than_picking_one_of_the_glob` |
| a named path that does not exist falls through instead of raising | `…a_run_output_NAMED_by_the_caller_wins_and_a_MISSING_one_never_falls_back` |
| the snapshot asserts reproducibility instead of reading the resolution | `…the_artefact_says_whether_a_SECOND_CHECKOUT_would_read_the_SAME_file` (+ the unrecorded-branch test) |
| `run_identity_fields` drops which run was read | `…the_RUN_IDENTITY_FIELDS_a_census_grades_include_WHICH_RUN_was_read` |
| `tracked_in_git` answered by name instead of identity | `…the_artefact_says_whether_a_SECOND_CHECKOUT_would_read_the_SAME_file` |

Each of the three new resolver tests asserts **both branches in one test**: the tier that must win
*and* the tier that must still be reachable. A resolver that always returned the tracked file would
satisfy every "the default is tracked" assertion and would not be the mechanism.

57 tests in `tests/tools/test_couple_value_based_pricing.py`, green in the clean extract.

## A test I shipped that passed for the wrong reason, and its own fixture caught it

The first draft of the fixture named the dated sibling `run_output_ffffffff_20991231T235959Z.json`,
chosen so it would sort above the tracked name. **It contains no "2026"**, so the glob tier's own
filter dropped it and the tier resolved nothing — three tests failed on a refusal that had nothing
to do with what they were asserting. The fixture is now built around that filter and names it,
because the filter *is* the defect's mechanism: it is the reason the one resolvable run output was
the one candidate the selection could never see. Recorded rather than quietly fixed, because a
fixture retuned until it agrees is a fixture fitted to its conclusion.

## What is owed next, and is NOT fixed here

1. **The stale week-old working copies are still on disk** —
   `tools/couple_value_based_pricing.py` and `tests/tools/test_couple_value_based_pricing.py`,
   both mtime 2026-09-09, both predating `79f7484f3`. The landed bytes are correct;
   `surgical_land --content` does not touch the working tree, which is the same half-repair already
   recorded for `simulation/customer_events.py`. The producer copy additionally holds real
   unlanded authored work — the `bill_scale_for` / `annual_bill_gbp` repair, absent from
   `origin/main` — tangled with a revert of the stamping. `tools/isolate_hunks.py` is the route;
   it is a separate item and is not attempted here.
2. **The tracked `run_output_latest.json` blob carries no `_cache_meta.git_commit`**, so in a fresh
   checkout `producing_commit` on the run side reads `None`. That is reported honestly rather than
   filled in, but it means the reproducible tier is currently *less* self-describing than the glob
   tier it replaces. The fix belongs in whatever reduces a run into that file, not here.
3. The site feed still does not surface this provenance to a reader of the page; the artefact
   carries it and `generate_value_arms_data` passes through unchanged.
