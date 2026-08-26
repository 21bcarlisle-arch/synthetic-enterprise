# WORKER FINDING — a concurrent lane's fix for the SAME priority-zero red can be WEAKER, and it wins by being later

**Severity:** LATENT · **Lane:** H_harness

**Date:** 2026-08-10
**Found while:** clearing the publish-gate wedge (episode 141+, blocking test
`tests/background/test_self_clearing_alarm_census.py::test_every_live_hit_is_dispositioned`).
**Class:** shared-tree concurrency × R15 fail-open. Not an instance fix — see THE CLASS below.
**Rank:** after the current P0 wedge work; backlog otherwise.

## Observed, with evidence

Two lanes drew the same priority-zero wedge and both wrote a fix to the same file
(`docs/design/self_clearing_alarm_dispositions.json`), dispositioning the same two new hits
(`publish_provenance.json`, `.remainder_annotation.json`).

1. `observed` — I committed my version as `2c1ecbeaa`. `census --check` exit 0.
2. `observed` — immediately after, `git status` showed the file MODIFIED again, 144 insertions /
   145 deletions. Not a linter: the prose was substantively different reasoning, not a reformat.
3. `observed` — the other lane's `publish_provenance.json` row carried **no `guard` field**:

   ```
   REAL HITS NOT YET GUARDED: publish_provenance.json (guard=MISSING)
   EXIT=1
   ```

   Its row is `{"verdict": "real", "why": ...}` — correct verdict, correct reasoning, and it
   would have RE-WEDGED publishing the moment anyone committed the working tree, because
   `unguarded_real_hits()` reds on a `real` row that is not `guarded` with a live test citation.
4. `observed` — I restored `git checkout HEAD -- <file>`; `census --check` exit 0 again.

## Why this is the dangerous shape, not just a merge conflict

A normal collision produces a conflict, or a diff someone reads. This one produces **a
working tree that looks fixed and is not**, in the direction that matters:

* Both versions pass `undispositioned()` — the row EXISTS in both. The gate's first rung is
  satisfied by the weaker version.
* Only the SECOND rung (`unguarded_real_hits`, PW4) catches it. That rung exists precisely
  because "a row could say guarded while nothing guarded anything"
  (`feedback_prose_inventory_needs_a_falsifier`). Here it caught the mirror case — a row that
  never claimed a guard at all, for a control that HAS one.
* The later writer wins on a shared tree by default. Correctness had nothing to do with it.
* Had I trusted my own commit and not re-run `--check` on the working tree afterwards, the next
  lane to commit that path re-opens a 141-episode publish outage, and the commit message would
  truthfully say it was dispositioning the wedge.

The generalisation: **on a shared tree, "I fixed it and committed" is not a terminal state for
a P0 red.** The file can be reverted-by-overwrite between your commit and anyone's next read,
by a lane acting in good faith on the same doorbell.

## THE CLASS (R10 — an instance fix is not a close)

The doorbell that woke me listed 70+ staged items and the same P0 wedge that every other tick
sees. Nothing in the draw mechanism tells a lane that another lane is already on this exact
red. So the class is: **any priority-zero red drawn by more than one concurrent lane produces
duplicate, divergent fixes to the same paths, and the merge is last-writer-wins with no
comparison of strength.** The disposition register is one instance; the same shape applies to
any single-file register a wedge fix must edit (`maturity_map.yaml`, the ruff baseline, the
ratchet files — all already known collision sites).

Closing this needs one of:

* **(a) A draw lease on the wedge.** The P0 wedge draw records which lane holds it and since
  when; a second lane drawing the same red is told, and takes the next rung instead. Cheapest,
  and matches the existing episode-state file the alarm already keeps.
* **(b) A strength comparison at commit.** The pre-commit gate, for register files, refuses a
  change that makes a control's own `--check` go from exit 0 to exit 1 — i.e. compare the
  checker's verdict before and after, not the file's bytes. This is the general form and would
  also catch a single lane weakening a register by accident.
* **(c) Nothing, and accept re-wedges.** Named so it is a choice rather than a default.

**Recommendation: (b), then (a).** (b) is the mechanism — it is the only one that works when
the two writers are a lane and a human, or a lane and a daemon, and it converts this from a
concurrency convention into an enforced check (MAKE_IT_STICK: prose-only rules evaporate). (a)
is a latency optimisation on top and can wait. Proceeding on that basis unless the director
objects; filing rather than building now because the P0 wedge itself outranks it and
SELF_INTERRUPT_DISCIPLINE says queue my own findings rather than fix on sight.

## Verification note for whoever builds this

The R15 mutation for (b) is direct and must be built with it: take the exact working-tree
version observed here (a `real` row with the `guard` key deleted), stage it, and assert the
pre-commit gate REDS. Opposite direction: the same row with `guard: "guarded"` and its live
test citation must pass. Without both, the check is a tautology against the file's bytes.
