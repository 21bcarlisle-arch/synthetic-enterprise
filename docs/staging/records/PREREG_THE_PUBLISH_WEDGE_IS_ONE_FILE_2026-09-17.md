**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 3 · **Atom:** publish_gate_and_wedge

# PRE-REGISTRATION — the 7-day publish wedge is one file, not twelve defects

**Filed:** 2026-09-17, before running the subject.
**Claim id:** the-publisher-has-never-graded-a-clean-publish-and-the-site-lane-is-red-right-now

## What I have already established (not a prediction)

The drawn item's FIRST premise is SPENT. It names three site-lane controls
(`site/_browser_probe.mjs`, `site/harness/test_the_deployment_reading_is_visible_to_a_browser.py`,
`site/test_the_browser_reading.py`) as existing in no commit. All three are tracked at HEAD —
landed by `7f40070a6` ("the browser-reading controls the site lane already ran existed in no
commit"), extended by `407ec5930`. `site/test_the_site_lane_runs_no_untracked_control.py`
**passes in 0.05s** at `b6bd93f2e`. That red was repaired before this item was drawn.

## The state that is NOT spent

`docs/observability/.publish_gate_state.json` on the SHARED tree (`/home/rich/synthetic-enterprise`,
HEAD `2e075e3ff`): `last_clean_publish: null`, `episode_clean_publishes: 0`,
`episode_failures: 62`, `wedge_since` 1789011039.7 (7.2 days), `total_red: 21`,
`blocking_tests` len 12.

## The prediction, written before the run

All 12 blocking tests sit in ONE file,
`tests/background/test_a_recorded_red_says_how_far_its_tree_stood_from_origin.py`, and that file's
ENTIRE test set is failing — including all three params of
`test_every_refusal_is_not_established_and_names_why`.

**I predict this is ONE cause at module scope — a collection/import error or a module-scope fixture
that raises — and not twelve independent logic defects.** Twelve independent defects landing in one
file, covering a control's every branch including its refusal params, is not a shape this project
produces; a single bad import is.

**I further predict it is still red at `origin/main` (`b6bd93f2e`).** The gate's own record says
`red_at_head: not_established` because the red was measured at `6371f89d1` and the shared HEAD has
since moved to `2e075e3ff` — so the record says nothing about HEAD either way, and a 7.2-day wedge
with 62 failures is not consistent with the cause having been repaired.

## What would refute me

- The 12 failures having 12 distinct assertion messages at distinct lines → twelve real defects,
  and the one-cause frame is wrong.
- The file collecting and passing at `b6bd93f2e` → the red is an artefact of the shared tree's
  fork (1 behind / 1 ahead), not a defect at origin, and the remedy is reconciliation, not repair.

## What DONE means for the claim

One non-null `last_clean_publish` in `.publish_gate_state.json`, stamped by the gate on its own
grading. A fifth, sharper diagnosis of why it is null is NOT progress and must not be filed as
though it were.

---

# RESULT — graded against the prediction above, 2026-09-17

## The prediction was right on the shape and WRONG on the count

**Right:** one cause, at module scope. Every failure in
`tests/background/test_a_recorded_red_says_how_far_its_tree_stood_from_origin.py` is the same
`KeyError: 'red_tree_fork'`. Not twelve defects.

**Wrong:** I predicted the 12 the gate recorded. At `b6bd93f2e` the file fails **18**, not 12. The
gate's record was taken at `6371f89d1` and the tree has moved since; the record was not an
undercount of a static thing, it described a different tree. I should not have carried the number
12 forward as though it were a property of the defect — the gate's own `red_at_head:
not_established` said so, and I read past it.

**Right on the second prediction:** still red at `origin/main`.

## The cause, established rather than inferred

`4138879cd` landed this control GREEN and gated, naming the field `red_tree_fork`.
`9b563a563` then landed `background/process_run_complete.py` as a **working-tree copy** (528
insertions), and carried another lane's in-place rewrite of that region inside it, renaming
`red_tree_fork*` → `fork_state*` and `RED_TREE_FORK_*` → `FORK_*`. Its stated subject was the
deferred-delivery verdict; the rename was a passenger.

Its gate reported `1178 passed`. This control was not among them — **gate selection is by
subject-module stem**, and a control named for the defect it closes shares no stem with
`process_run_complete`. So the rename could not be seen by the gate that blessed it.

## Which name is correct — decided on evidence, not preference

Adopt `fork_state`. It is what `background/origin_reconcile.py`, `tests/background/conftest.py`
and the **published `site/data/delivery.json`** already read, and what the live
`.publish_gate_state.json` carries. The control was the ONLY remaining reader of the old name in
the whole tree. Reverting would have broken live readers to satisfy one file.

## TWO REGRESSIONS THE RENAME CARRIED, restored in the MODULE rather than deleted from the control

Neither was visible as a test failure — both were live in the record the RUNG-1 draw quotes.

1. **The refusal named the wrong reason.** The call site suppresses the fork read when nothing is
   blocking and passed `(None, None)`, which came back as *"the fork with origin/main could not be
   counted when this red was graded"* — a sentence about a red that does not exist, blaming a
   fetch that never ran. A reader arguing with that refusal would have gone looking at the remote.
   Restored as `fork_state_no_red_refusal()`, kept OUT of `fork_state_verdict` so that function
   stays pure over its two counts — the shape the rename correctly introduced.
2. **A negative count no longer refused.** The pre-rename guard required `v >= 0`. Without it,
   `behind=-1` renders *"-1 commit(s) behind origin/main"*, **inventing a divergence** — the same
   fail-open direction as the bool leg the control already guarded.

## A SECOND, INDEPENDENT RED — found, fixed, and not the same cause

`test_publish_gate_wedge_draw.py::test_the_publishers_kinds_and_the_supervisors_set_have_not_drifted`
was red at HEAD before any edit of mine (verified by measuring HEAD's bytes directly).

It asserted `f'kind="{kind}"' in src` — a **text grep over Python source**. The publisher writes
`delivery_did_not_reach_origin` at `process_run_complete.py:6712` as
`kind=DELIVERY_NOT_REACHED_KIND`, a named constant. The grep saw no literal and reported *"no
longer written by the publisher -- this set is describing a producer that has moved"*. **The
producer had not moved.** It had been given a constant — the shape this repository asks for
everywhere else — and the control punished it for that.

Repaired to resolve `kind=` arguments by `ast.parse`, resolving module-level `NAME = "literal"`
bindings. Fail-closed by construction: a spelling the resolver cannot see (f-string, dict lookup,
parameter) resolves to nothing and the assertion fails, because a kind it cannot vouch for must
not read the same as a present one.

## R15 — every repair mutation-proven, in this isolated worktree

| Mutation | Control that fired |
|---|---|
| Drop the `behind < 0 or ahead < 0` guard | `test_a_negative_count_is_not_a_fork` + a refusal param |
| Route the no-red case back through `(None, None)` | `test_a_failure_naming_no_red_records_the_refusal_and_its_reason` |
| Resolver sees literals only (pre-repair grep) | the drift control + `test_the_kind_reader_sees_a_named_constant_and_not_only_a_literal` |

The control's needles are now keyed to **properties, not sentences**. The pre-repair assertions
pinned whole clauses of the prose (`"Check one of them at origin/main"`), so a rewrite that
preserved every property still reddened them — which is how a rename became a seven-day wedge.

## The class, stated once and not built into a register

Both reds are the same shape: **a control whose subject is another module, keyed to that module's
surface TEXT, and unreachable from the gate that blesses changes to it.** Stem-based selection
cannot reach a control named for its defect, so the two facts compound — the coupling is invisible
at exactly the moment it breaks.

## What is NOT established by this document

That these were the only blockers. `total_red` was 21 and these two files account for 19. The
remainder is measured next, not assumed.
