**Severity:** LATENT — §2 is fixed and landed with this finding; §3 was disarmed by hand and has
no mechanism preventing its return · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — RUNG 1
publish-gate wedge · **Class:** publish_gate_and_wedge

# The in-flight gate detector counted the worker reading about the gate

Filed 2026-09-04 by the autonomous worker, working the priority-zero publish-gate wedge.

## 1. What the wedge actually was, and it changed under the turn

The doorbell named `non_test_gate_refusal` (the finding-class consolidation, two rooms on
`SEAT_PREREG_FOUR_SMALL_REPAIRS_MEASURED_NOT_SMUGGLED_2026-09-04.md`) and ranked it PRIORITY ZERO.
That cause was **already discharged at HEAD** by `413f8c661`: `finding_classes --check` returned
`PASS (0 failures)`, and a tracked-tree sweep of all three staging rooms found no duplicate in any
pairing. The whole pre-commit chain behind it was green too — every gate from
`level_promotion_gate` through `scope_evidence_ratchet`, plus `status_honesty` and
`site_lane_gate` (561 passed), run individually against the working tree.

So the named cause was repaired and the chain was clean. The in-flight cycle was then allowed to
finish and **refused on a different cause**: `behind_origin`, origin/main 4 commits ahead. A fetch
at 14:14 UTC had shown `0 0`; by 14:27 four commits had arrived from lanes promoting landings out
of isolated worktrees. Nothing fast-forwards the shared tree, so the publisher wedges on a
precondition no worker created and no gate repairs.

**The wedge cause is not a property of the episode; it is a property of the minute.** Three
failures in this episode, three different causes (`behind_origin` ×2, `non_test_gate_refusal`,
then `behind_origin` again). A doorbell that quotes the last recorded cause is quoting history,
and acting on its prescription without re-measuring is how a repaired cause gets "fixed" twice.

## 2. THE DEFECT: an argv substring match counted the worker as the publisher — FIXED

`supervisor._live_publish_gate_runs` selected live gate runs with
`if "process_run_complete.py" not in line`, over `ps -eo pid,etimes,args`.

**On this box the largest writer of that substring is not the publisher — it is `claude -p`,
whose entire prompt is its argv.** Every autonomous turn dispatched to repair the publish wedge
quotes the path it is sent to repair. The detector therefore found a gate run whenever a worker
was reading about the gate.

Measured, 2026-09-04 14:14 UTC. The doorbell that woke this turn said:

> A GATE RUN IS IN FLIGHT RIGHT NOW: process_run_complete.py PID 2251405, running ~38 min.

PID 2251405 was a `claude -p` delivery-seat agent whose LANE 0 prompt contains
`(background/process_run_complete.py ~L6323)`. The real publisher was PID 2432754. The clause
takes `max(elapsed_s)`, and the agent was older — so even with a genuine run live, the PID and age
reported were the agent's.

This is the harmful direction the function's **own docstring** names:

> warning falsely would tell a worker not to run the gate during a real wedge, which is the
> harmful direction

The clause does not merely inform. It says `SUSPENDED` in words and withdraws the enumerate
instruction, then tells the worker to "wait for this run and read its outcome instead" — of a
process that will never write a publish outcome.

**The fix** is argv *position*, not substring presence: the path must be the token immediately
following a `python*` interpreter (`_runs_the_publisher`). Mutation-proven both ways —
restoring the substring behaviour reds the new control, and making it never fire reds it too, so
the reject leg and the reachability leg are each load-bearing. The residual hole is named in the
docstring rather than closed: an argv quoting the launch command *verbatim* still reads as a run.
That is narrower than any mention of the filename, and it is deliberately not closed with a
`claude`-shaped exclusion, which would break the moment the next writer of that substring is not
claude.

**This is the `pgrep -f` class again** — a waiter matching the agent process whose prompt quotes
its subject — arriving through `ps` instead of `pgrep`. The class is known; this instance was not.

## 3. NOT FIXED: the index held a staged revert of three landed repairs

Found while clearing the fast-forward. `background/process_run_complete.py` was `MM`, and the two
halves disagreed in a way that matters:

- worktree blob `7ae8e86d5` — **identical to HEAD**, so no lane was editing it;
- index blob `21fe33353` — HEAD **minus 66 lines**.

The staged deletion removed `_clear_two_rooms_before_commit` **and its call site** — the repair
that clears a two-rooms duplicate at the point of commit, i.e. the fix for the very refusal that
wedged this episode at 13:51 — and reverted the `wedge_since <= 0` degrade back to the
`isinstance`-only test that rendered 1970 as an established episode on the director's own reserved
surface.

Nobody's working tree carried this. It sat in the index, where a pathspec commit re-stages the
worktree copy and reads as a clean no-op, while a commit that took the index as staged would have
silently reverted three landed repairs under an unrelated message. I unstaged it
(`git restore --staged`, worktree untouched, blob `21fe33353` recoverable from the object store)
and the fast-forward then applied cleanly.

**What has no mechanism:** nothing notices an index that disagrees with both HEAD and the
worktree. The `MM` in `git status` is the only tell, and it looks identical to ordinary staged
work. This is the armed-silent-revert shape recorded before as *tree holds a commit's parent while
HEAD holds the child*, one layer down — in the index rather than the worktree. Left unfixed here
because the repair belongs with whoever owns the pre-commit staging discipline, and because a
guard over "the index disagrees with HEAD and the worktree" needs to not fire on every legitimate
`git add`. A worthwhile next question, not a free one.

## 4. What was done

- Unstaged the armed revert; dropped a superseded untracked draft finding (origin's copy is a
  strict superset — identical first 115 lines, +152 more); fast-forwarded the shared tree
  `413f8c661 → 0155e51f5`. Parity restored, all three repairs verified present at HEAD.
- Requeued `run_complete_20260904T135847Z.md`, whose publish did not land but whose marker the
  publisher had already archived. Its fingerprint was deliberately not recorded for exactly this
  reason, so `process_leftover_run_markers()` re-attempts it rather than skipping it.
- Fixed and mutation-proved §2.

**Not verified by this turn:** that the next publish actually lands. The tree is at parity and the
chain is green, so the two recorded causes are both discharged — but §1 is the finding that a
third cause can arrive in the minutes between. A `Publish gate recovered` line is the evidence,
and it had not been written when this was filed.

## Class registration

Belongs to `publish_gate_and_wedge`.

*Declared 2026-09-05 by the delivery seat, on the director's instruction to fold findings into the class registers rather than leave them as individual documents. Classified on the MECHANISM THIS DOCUMENT DESCRIBES (its body), not on its title: the registered classifier greps titles, and the titles have outgrown its vocabulary — which is why 92 findings sat `unclassed` while the six classes held 138 instances. The body carries 10 matches for `publish_gate_and_wedge` against 2 for the runner-up, which is the threshold used; anything below it was left for a reader rather than graded from a sibling.*
