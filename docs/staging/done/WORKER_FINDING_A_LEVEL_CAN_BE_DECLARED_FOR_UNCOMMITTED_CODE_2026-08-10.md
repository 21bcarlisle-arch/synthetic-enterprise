# WORKER FINDING — the map declared H39 at L2 for a program the repo did not contain, one commit after the commit about that

**Found:** 2026-08-10, at the start of the `H_GAP_fabric_belief_truth_gap` tick (the build was sitting in that atom's `file_scope`).
**Disposition:** QUEUED as a mint candidate — `a level_current whose file_scope is dirty is not a record`. NOT fixed on sight.
**Rank:** harness queue, above the cosmetic items — this is the third instance in three days and the second in two commits.

## Observed, with evidence

The tick opened by checking `git status` against the drawn atom's `file_scope`, and found an
entire build uncommitted:

```
$ git status --porcelain | grep -E "fabric_gap_ledger|premise_two_level|band_null_sweep"
 M background/band_null_sweep.py
 M background/fabric_gap_ledger.py
 M tests/harness/test_premise_two_level.py
 M docs/design/BAND_NULL_SWEEP.md          # 853 insertions across the four
```

Meanwhile **HEAD already declared the atom complete at L2, with measured figures**:

```
$ git show HEAD:docs/design/maturity_map.yaml | grep -A3 "H39_the_texture"
  level_current: 2
  gain: "...L1.1n reads that generator at exactly 1.0 and fails it 15 of 15.
         CORRECTED 2026-08-10: the mint's inferred cause (peaky profiles) is REFUTED at r=-0.05..."
```

`docs/design/simplifications/H39_*.yaml` carried the full `build_note` too, naming
`flatten_to_mean_profile`, `half_hourly_texture_vs_own_null` and the band — none of which existed
in any commit. **Nothing in the repository could produce the numbers the map published.**

## Why this one is a class and not an incident

The commit immediately before HEAD is `f0493363b`, titled:

> *Unwedge publishing: the map declared four notes that were never written, and **H38 was the
> second pass to land uncommitted***

So: H38 landed uncommitted, a commit was written whose entire subject was that class, and **the
very next atom did the same thing**. Three instances (the four notes, H38, H39), and the first two
already have a commit-message apiece explaining the lesson. That is the signature `MAKE_IT_STICK`
describes exactly — *every rule that DECAYED was an exhortation; every rule that HELD was a
mechanism* — and the response so far has been three exhortations.

The failure mode is structural, not careless. A tick builds, verifies green in the working tree,
writes the map and store entries **from the working tree**, and is cut off at its bounded edge
before committing. Every artefact it wrote is truthful about what it *measured*; the repo is the
only thing that disagrees. Both known cousins are already on file — the capability index reads the
working tree (`feedback_capability_index_reads_the_working_tree`) and the gate lints the working
tree — so this is the same seam a third time: **a control whose subject is the tree, publishing a
claim whose subject is the commit.**

## The recommendation, which is one gate

`tools/level_promotion_gate.py` already refuses an *unrecorded* level move at commit time. It
should also refuse a **recorded-but-unbuilt** one: at commit time, for any atom whose
`level_current` is being raised, fail if that atom's `file_scope` has uncommitted modifications
that are not part of this commit's pathspec. The information is all local (`git status --porcelain
-- <file_scope>`), it needs no new channel, and it turns "remember to commit the code with the
claim" into a thing the tree enforces.

R15 both ways it must be: a mutation that lets a dirty `file_scope` through has to red a named
test, and the gate has to be shown **passing** on an ordinary clean level move, or it is a control
that can only fail and will be routed around within a day
(`feedback_control_that_can_only_fail_wedges`).

## What I did this tick

**Adopted, did not rebuild** — the correct response when the guard flags unmerged work. Audited
the diff, ran the evidence *before* trusting it (`tests/harness/test_premise_two_level.py` 174
passed 2 xfailed; `tests/harness/test_band_null_sweep.py` 34 passed), and landed it at `317a7b62f`
so the repo now contains the program its own map has been advertising. The recurrence is recorded
in that commit message and in the H39 store note rather than being quietly tidied away — the map
was right about the physics and wrong about the repo, and only the second half was mine to fix.
