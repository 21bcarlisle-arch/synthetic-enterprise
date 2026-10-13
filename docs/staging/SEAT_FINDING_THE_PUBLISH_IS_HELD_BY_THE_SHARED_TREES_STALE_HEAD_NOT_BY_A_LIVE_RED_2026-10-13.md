**Severity:** LATENT · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted` · **Claim:** `the-weekly-publish-died-on-a-demand-estimate-with-no-error` (Lane 0 delivery)

# The publish is held by the shared tree's stale HEAD, not by a live red

*2026-10-13 15:10 BST, delivery seat (executor). This invocation re-measured the claim's premise. Two
earlier invocations had already done most of it.*

**Where each part of the item stands (re-measured against origin/main 776dfcd2e):**

| Part | State | Evidence |
|---|---|---|
| The SLC 20-24 fix and its None control | on origin | 5f61c2262. Averages over graded rows only, gives the ungraded count in the notes, and records AMBER "unavailable" when no row is graded. Both mutations (crash, `or 0.0`) red. |
| Red #10, the ceiling test, skips at origin HEAD | confirmed | `tests/simulation/test_net_new_acquisition.py` at 776dfcd2e: 62 passed, 1 SKIPPED, "UNAVAILABLE ... none of the 0 run process peak(s)". 168137d37 predicted this. sim-runner's code (2248e3baf) does log the peak line. It arms after the first completed run on code carrying the curve's head. |
| The 145 banners | on origin | 3a692ad58. They were never committed locally, despite the 2026-10-12 stretch log. They sat as uncommitted edits in `/var/tmp/se-canon` and were ported with `git apply --3way`. |
| A publish's figures on origin | **NOT YET** | see below |

**What held the publish.** The dead run's JSON was saved, and its marker
`run_complete_20261013T033930Z.md` was processed by `process_run_complete` (pid 59360). At 14:00Z
the publisher wrote a "verification paused" banner. `site/data/publish_provenance.json` records the
reason as `scoped publish-path suite red at git=2f5c926dc`, and the only blocking test is
`test_a_log_the_run_makes_and_a_section_reads_survives_the_reduction.py::test_the_census_selects_enough_logs_to_be_capable_of_finding_one_dropped`.

That test is **green at origin** (3 passed at 776dfcd2e). It went red when a070c2195 (2026-10-12)
changed the run's return to `_result = {...}; return _result`, and 81c129fe8 (06:49 BST today)
repaired the walk. The gate's subject is a clean checkout of the **shared tree's HEAD**
(`_head_checkout`), not of the run's sha. The shared HEAD is **2248e3baf: 49 commits behind origin,
0 ahead**. It lacks 81c129fe8.

**Why the shared tree has not advanced.** A `--ff-only` advance is refused while an incoming path is
dirty. 49 of origin's 226 incoming paths are dirty in the shared tree:
- 30 already equal origin's blob, so they are harmless and git would accept them if they were the only ones.
- 19 differ from origin. Among them are the console seat's staged DD pile (`company/billing/dd_review.py`,
  `company/interfaces/dd_review_outcome.py`, `simulation/dd_balance_book.py`,
  `simulation/run_phase2b.py`, `tools/dd_book_legs.py`, ...). Per
  `SEAT_NOTE_THE_DD_DESIGN_PILE_IS_IN_THE_CONSOLE_SEATS_LANDING_SEQUENCE_2026-10-13.md`, that pile
  is in the interactive console session's landing sequence, under the director's instruction.

So this is not a defect in the publish path and not a live red. The publish waits on the shared tree
reaching origin, and that waits on the console seat's landing sequence. Nothing in this lane may
move another lane's staged work.

**Prediction, filed before it is observed:** the sim-runner run that started 11:24Z (on 2248e3baf,
importing the shared tree's on-disk copy, which carries the 5f61c2262 fix) will not die on abs(None).
If the shared HEAD has not advanced when it ends, its publish will be refused on the same test, for
the same reason.

**Not done, deliberately:**
- I did not run `process_run_complete` from an origin worktree to gate origin instead. That would
  put a second publisher beside the live one on the same marker, and it would publish by a route
  nothing has tested.
- I did not alter the shared tree.

**Hand-off:** `the-publish-lands-once-the-shared-tree-reaches-origin`.

**Re-measured by the publish-wedge draw, 2026-10-13 (worker).** The draw re-fired at the shared HEAD
2248e3baf. The named test passes there on disk (3 passed), because the on-disk copy carries
81c129fe8's bytes. HEAD itself still lacks them. The shared HEAD is now 52 behind origin 8b0cbf04c
and 0 ahead. 42 incoming paths are dirty, and 17 of those differ from origin. They are the same DD
pile plus the hedge-desk and renewal edits. So the prediction above still holds and nothing in the
publish path needs fixing. I sent the director the one-line cause on NTFY (id `TCpCYvtpTTm3`).

**Re-measured again by the publish-wedge draw, 2026-10-13 (worker).** The live gate run was pid 951905
on marker `run_complete_20261013T033930Z.md`. I did not run a second suite beside it. The publisher
refused the same test in a checkout of graded_sha 2248e3baf. The shared HEAD is still 2248e3baf, now
54 behind origin 6f7ec5fb1 and 0 ahead. 42 incoming paths are dirty, and the same 17 differ from origin.
That is the DD pile plus the hedge-desk, renewal, growth-desk and DIRECTION edits. The diagnosis
is unchanged, so I sent no second NTFY. The cause went out as `TCpCYvtpTTm3`. The wedge clears once
the console seat lands its sequence and the shared tree fast-forwards.

**Re-measured a third time, 2026-10-13 ~17:40 BST (worker).** The publisher graded marker
`run_complete_20261013T134447Z.md` (pid 1448887) in `/var/tmp/publish-gate-head-sc763uof`, a clean
checkout of 2248e3baf, and refused it on the same census test. I ran that one file in the gate's own
checkout while the suite ran: red, "the census selected only [] -- under the floor of 4". It is not a
second suite. After that refusal, the publish commit was refused **by the hook chain** in the shared
tree, which named **73** reds (`.last_gate_blocking_tests.json`, census `hook_chain`), mostly
`site/test_the_baseline_comparison_reaches_the_reader.py` and `site/test_explore_second_clock.py`.
Those are the same cause. `site/test_explore_second_clock.py` is red in the shared tree (2 failed)
and green at origin ed07176b1. At origin, those two files and the census file are 210 passed and 15 skipped.
**What has moved:** the shared HEAD is 57 behind origin and 0 ahead. Only **9** dirty incoming paths
now differ from origin, down from 17, and the DD pile is no longer among them. The 9 are
`company/interfaces/growth_desk.py`, `docs/direction/DIRECTION.yaml`, `docs/status/SEAT_STRETCH_LOG.md`,
`site/data/knowledge_topics.json`, `tests/harness/test_premise_two_level.py`, and four staging notes.
Each is older than origin's commit to its path, so the fast-forward is now held by stale copies and
other lanes' edits, not by a landing sequence. I moved none of them. No second NTFY was sent.
