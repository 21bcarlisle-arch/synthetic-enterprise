**Severity:** LATENT · **Lane:** H_harness · **Epoch:** 3 · **Class:** publish_gate_and_wedge · **Atom:** (Lane 0 delivery — the publisher has never recorded a clean publish in this episode)

# FINDING — the publish gate measures its red before the advance that cures it, then records a failure about a tree it has already left

**Measured:** 2026-09-16, publish cycle pid 2726081, 09:56–10:22Z. Not reconstructed — observed
live in `docs/observability/sim-runner-log.md` and confirmed against the code path.

## What happened, in one process

| time | event | tree |
|---|---|---|
| 10:20 | red census runs; 1 red; `Publish gate RED -- blocking test(s): ...test_the_channel_reads_the_SHARED_trees_log_not_the_importing_trees` | `4187c7d9a` |
| 10:20 | `Scoped publish-path gate FAILED - not committing content` | `4187c7d9a` |
| 10:20 | `Advance attempt: fast-forwarded the shared tree onto origin/main` | → `5a63cb3a3` |
| 10:22 | `Publish-gate failure #2 (test_regression, rc=1)`; `episode_failures` 35 → 36 | `2ec310fd8` |

**The commit it fast-forwarded onto is the commit that cures the red it had just measured.** That
test is green at `5a63cb3a3` — verified in a clean extract, 31 passed. The cycle held the cure in
hand for two minutes and recorded the stale verdict anyway.

## The code path, not an inference

In `_process`:

    tests_ok, timed_out = run_fast_tests(git_hash)
    if not tests_ok:
        code, log_line, reason = _gate_refusal(timed_out, git_hash, last_blocking_tests()[0])
        log(log_line)
        _publish_provenance_banner(git_hash, reason=reason)   # <-- advances the tree
        return code

`_publish_provenance_banner` reaches `_commit_and_push_paths`, which is where the fast-forward
lives. So the advance is downstream of the verdict by construction: the gate can never see a cure
that arrives with the very advance it performs.

## Why this reads as a wedge when it is not one

The recorded failure names a real, correctly-observed red — and names it against
`git_hash=edded3973`, a tree three commits behind where the process ended. The attribution added
by `7a9e4c117` does its job and says so:

    red_at_head: not_established
    red_at_head_reason: the red was measured at git=edded3973 and HEAD is now git=2ec310fd8 --
    that record describes a different commit's tree, so it says nothing about HEAD.

So the instrument is honest and the record is still misleading in aggregate: 36 `episode_failures`
where an unknown number were measured on trees the publisher had already left. **A steer reading
that count concludes "the gate cannot pass" when the observable fact is "the gate could not pass
26 minutes ago".** That is what sent the last three steers at a subject which had already moved —
see the RESULT beside this finding, section 1.

## Bounded, and that is why this is LATENT and not BLOCKING

The marker is NOT archived on the refusal path — `marker.rename(DONE_DIR / ...)` sits below the
`return code`. Verified: `pending_run_complete_markers()` is still 1 and
`run_complete_20260916T085959Z.md` is still in `docs/staging/`. So **the next cycle re-runs at the
cured tree and self-heals.** The cost is one wasted cycle (~26 min) per advance plus one
misattributed entry in the failure record — not a permanent wedge. Stating the bound because the
alarming reading ("every cycle poisons itself") is available here and is wrong.

## The repair, when it is drawn

Not implemented this turn — the turn's budget went to the `last_clean_publish` repair, which had
to land before the next cycle. The shape:

**After the advance, if HEAD moved, re-measure the blocking node ids before recording a failure.**
Re-running only the named blocking ids is seconds, not a full selection. Three outcomes:

- still red at the new HEAD → record the failure, attributed to the tree it was actually measured
  on. This is the only branch entitled to increment `episode_failures`.
- green at the new HEAD → the verdict is SUPERSEDED, not a failure. Record it as such and return a
  retry-now outcome so the next cycle starts immediately rather than waiting a full cadence.
- cannot re-measure → fail closed, and say on the record that the verdict is unattributable.

**Key it to the property, not to this instance:** the question is "was the tree this verdict
describes still HEAD when the verdict was recorded?", which is answerable for every cause, not
only for a fast-forward. A control keyed to `behind_origin` specifically would go green the moment
the advance moved for any other reason.

**Do not repair this by moving the advance before the gate.** The advance is deliberately on the
refusal path — ruling property 3, "BEHIND, NEVER FROZEN, NEVER SILENT": the banner must reach
origin precisely when the content publish is refused. Reordering would trade this defect for a
silent site.
