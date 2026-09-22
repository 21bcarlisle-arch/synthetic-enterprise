**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 3 · **Atom:** —

# The publisher's own clean-publish machinery was in no commit, and the red wedging every commit counted two chains as one

Autonomous worker, 2026-09-17. Claim `the-publisher-has-never-graded-a-clean-publish-and-the-site-lane-is-red-right-now`.

**`last_clean_publish` is still null. This is an increment, not the item.** Two causes are closed
and landed; the cause that refused the 12:40 publish is still live and named in §4.

## 1. The precondition was already spent

The item directs: clear the site-lane red on the three untracked `site/` controls, then drive a
publish. Re-measured at turn start, `site/test_the_site_lane_runs_no_untracked_control.py` passes
in 0.04s — another lane landed it at `330b54ac8` (12:15 UTC) while the item was in flight, and the
12:35/12:40 cycle got past it. Local `HEAD` and `origin/main` were level, no fork.

## 2. The same defect the item names, one layer deeper, on the publish path itself

`background/publish_delivery_deferral.py` and its twelve-leg control
`tests/background/test_a_lost_push_race_holds_its_verdict_and_is_graded_on_the_ref.py` were on
disk **untracked** from 10:27 UTC, with matching uncommitted edits in `process_run_complete.py`,
`publish_cause.py` and `supervisor.py`. `git log --all -S EXIT_PUBLISH_DELIVERY_DEFERRED` and
`git log --all -S publish_delivery_deferral` both return nothing: **the work reached no commit on
any ref.** Section 5 of `WORKER_RESULT_THE_PUBLISH_VERDICT_WAS_TAKEN_BEFORE_ITS_DELIVERY_FINISHED…`
says all four landed in one `surgical_land` call. They did not, and that doc is untracked too.

This is the item's own sentence — *assurance that exists on this machine only* — applied to the
machinery that decides whether a publish counts as clean. **The publisher imports the working tree,
not `HEAD`**, so every cycle since 10:34 UTC ran it while no clone had it. `last_clean_publish`
could not have been trusted even had it been stamped.

Landed `9b563a563`, merged `080a19318`, on `origin/main`.

**It is five paths, not four, and the gate is what said so.** The control asserts
`DELIVERY_NOT_REACHED_KIND ∈ supervisor.WEDGE_KINDS_NO_TEST_JUDGED`. That leg passes in the shared
tree, where `supervisor.py` has the kind, and **failed in the extract**, where `supervisor.py` is
`HEAD` — a green suite measuring five lanes at once. `supervisor.py` carries eight hunks from at
least three subjects, so it went in via `isolate_hunks --keep 1` + `surgical_land --content`:
`HEAD` plus five lines, none of the discovery-pass-ceiling work beside them.

## 3. The red refusing every commit was measuring something the deadline does not bound

`test_the_deadline_has_headroom_over_what_THIS_MACHINE_actually_costs_today` fails at
**666.95 against 660.0 — seven seconds** — and named itself the blocking test on the 13:02 UTC
publish refusal. 666.95s is the row for `b55667741`, and it is **two chains of ~333s**:
`surgical_land.land` re-gates after losing the compare-and-swap, one stopwatch times the whole
call, and the publisher's own log says *lost the race on attempt 1/2* and *2/2*.

Every consumer of that series speaks one chain — `ceiling_seconds` is
`GIT_COMMIT_HOOK_TIMEOUT_SECONDS`, which bounds one `git commit`; the reader is called
`_recent_hook_chain_seconds` and documented *PER CHAIN*. **No re-measurement could clear this
red**: the remedy the assertion names is to re-measure the committed constant, and the failing
comparison does not contain it.

The 2026-09-16 repair reads the same contradiction off the row and is **one-sided** — it fires only
when the TOTAL clears the ceiling, and 666.95 < 880. Same defect two days later through the one
door a threshold left open. Fixed at the producer, which always knew the count: `387798957`.

**An off-by-one I put in and took out, because it pointed the unsafe way.** The first draft used
`len(lost) + 1` everywhere. `on_lost` fires *after* a chain has run, so the plus-one is right only
when a further chain ran; on exhaustion there is none. **Both multi-chain rows this machine has
ever recorded (`2c89bd534`, `b55667741`) are exhaustions**, so the draft would have filed 222s as a
chain that really cost 333s — inventing headroom in the control whose job is to refuse when
headroom has gone.

## 4. What is still live, and what I deliberately did not do

- **The landing race is the cause that refused 12:40.** Two attempts, both lost, ~333s each against
  a median inter-commit gap of 328s over the last six hours. It gave up with **2471s of its own
  budget unspent**; `PUBLISH_LAND_ATTEMPTS = 2` is a count that cannot see the budget, justified by
  a comment reading *"the next cycle is a cheaper place to try again"* — the next cycle was 4685s
  away. `_remaining_path_budget_seconds` already exists and its docstring invites a second caller.
- **The headroom control's staleness leg is probably telling the truth.** Committed measurement:
  134s, 2026-09-04. A chain now typically costs ~330s. That re-measurement is real work with its
  own evidence and is **not** bought by `387798957`.
- **I did not rewrite the two historical rows.** Correcting only `b55667741` goes green; correcting
  both — the only non-arbitrary choice — puts `2c89bd534` at 690.76s per chain, inside the window it
  is currently excluded from, and the control reds again **on a number that is true**. Picking the
  row that flatters is the asymmetric narrowing this repo has a scar from.

## 5. Evidence

Six controls in `test_a_multi_chain_landing_is_not_recorded_as_one_chain.py`; three mutations run
**in a clean extract**, not the shared tree: drop the division → two legs red; drop `chains=` from
one of three recording exits → the partition leg reds naming 2 of 3; make `_chains_run` blind to
how the loop ended → the exhaustion leg reds. `9b563a563`, `080a19318`, `387798957` are all
ancestors of `origin/main`; all six paths bound to the claim.
