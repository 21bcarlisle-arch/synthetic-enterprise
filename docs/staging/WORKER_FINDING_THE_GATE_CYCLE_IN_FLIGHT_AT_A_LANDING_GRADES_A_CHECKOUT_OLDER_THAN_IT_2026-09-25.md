**Severity:** LATENT · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# The gate cycle in flight when a repair lands grades a checkout OLDER than the repair, so its refusal is not a verdict on the repair

## The prediction, written BEFORE its answer was known

Filed at 2026-09-25 03:08 UTC, while the cycle it describes was still running. This is a
prediction and not a report, and it is here so that it can refute me.

* `619cb3cda` landed at **2026-09-25 03:05:47 UTC**. It repairs
  `tests/background/test_a_live_record_read_from_a_linked_worktree_reads_the_shared_tree.py::test_the_supervisors_wedge_draw_sees_the_live_failures_not_the_committed_placeholder`,
  the SOLE entry in `blocking_tests` and the whole citation holding the publisher.
* The publish gate cycle running at that instant took its **throwaway HEAD checkout at
  02:56 UTC** (`sim-runner-log.md`, "using a throwaway checkout for this cycle"), and computed
  its 264-file blocking scope at 02:57 UTC. Both precede the landing by ~9 minutes.

**PREDICTED:** that cycle refuses again on the same test, taking `episode_failures` to 56 with
`citation_at_head: reproduces` — and that refusal grades a tree that does not contain the fix.
The FIRST cycle able to grade the repair is the first one whose checkout is taken after
03:05:47 UTC.

**WHAT WOULD REFUTE ME:** that cycle publishing clean, or refusing on a different citation.
Either would mean the checkout instant is not what determines the graded tree here, and the
reasoning above is wrong.

## Why this is worth a document rather than a log line

The harmful reading is available and it is the flattering-looking one: a tick that reads
`episode_failures` going 55 -> 56 *after* a commit claiming to repair the sole citation will
conclude the repair failed, and the obvious next move is to revert or re-derive a fix that was
correct. The cost is not one wasted invocation but a correct repair undone.

The general shape, which is the part that outlives this instance: **a gate that grades a
checkout is a gate that grades an INSTANT, and the instant is when the checkout was taken, not
when the verdict is read.** Any landing made while a cycle is in flight is invisible to it.
Nothing currently records the checkout instant beside the refusal, so a reader comparing a
commit time to a refusal time has no way to tell whether the commit was in the graded tree.

## The one-line remedy this argues for

`record_publish_gate_failure` already stamps `git_hash`. The checkout instant — or the SHA the
throwaway checkout was taken at, which is strictly better — belongs in the same record, so the
question "was my landing in this tree?" is answerable from the state file instead of by reading
a log for the word "throwaway". Not built here; this document is the finding, not the fix.

## Status

Left OPEN deliberately. It closes when the checkout's own subject reaches the failure record,
or when the prediction above is refuted and this document is corrected beside the claim.
