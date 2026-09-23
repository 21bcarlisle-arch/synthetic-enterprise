**Severity:** BLOCKING · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0 delivery
**Class:** `publish_gate_and_wedge` (primary) · `uncommitted_and_orphaned_work` (secondary)

# Both drawn pieces were spent before the draw, and what was actually owed was that the landed relation could not be imported in the tree it landed in

**Claim:** `discharge-the-standing-publish-red-in-the-shared-tree-then-build-the-producer-newer-than-artefact-relation`

## The premise, re-measured rather than inherited

The item named two pieces. **Both had landed before it was drawn.** Measured on the shared tree, not
taken from the item's word:

| Piece asked for | State when I measured it | Evidence |
|---|---|---|
| (1) regenerate the chain so the site leg goes green | **spent, 09:04** | `site/test_the_flat_churn_belief_reaches_the_reader.py` — **15 passed**; the artefact's mtime (12:06) is now NEWER than its producer's (12:05), the inversion the item was written on |
| (2) build the producer-newer-than-artefact relation | **spent, 11:03** | `59ccdb550`, which added `derived_artefact_producers`, `check_derived_artefacts`, `DERIVED_RED_VERDICTS` and `--derived-artefacts` |

The item's own PREMISE CHECK had already flagged that `be6b67b98` was an ancestor of `origin/main`.
What it could not see is that the *remedy* had landed too, in a commit the item never cites.

## What was actually owed, and nobody had drawn it

`59ccdb550` landed the relation at 11:03. The shared tree's working copy of
`tools/published_feed_regeneration_check.py` had mtime **09:10** — a fork of `61f4fceeb` carrying a
DIFFERENT lane's answer to the same defect (the working-tree clone-overlay mode:
`WATCHED_DERIVED_ARTEFACTS`, `_overlay_working_tree`, `--working-tree`).

Neither copy contained the other's names, and **the on-disk copy won every read.** So the test
`59ccdb550` landed beside itself — `tests/tools/test_a_derived_artefact_is_regenerated_when_its_
producer_changes.py`, COMMITTED at HEAD — raised at COLLECTION:

```
ImportError: cannot import name 'DERIVED_RED_VERDICTS' from 'tools.published_feed_regeneration_check'
```

A collection error is not one red test. It refuses the whole selection, and it had been standing
since 11:03 in the tree every lane commits from.

**This is the shape worth keeping.** Two lanes each solved a real defect correctly, each landed or
held work that passed its own controls, and the COMBINATION was broken in a way neither lane's tests
could see: the landing lane's test passes in any tree containing its module, and the holding lane's
test passes against its own copy. Only the shared tree runs both, and only there is either wrong.

## What I did

A **union**, not a pick. 3-way merge (base `61f4fceeb`, ours HEAD, theirs the disk copy) conflicted
in exactly two places and both were additive — one docstring section each, one argparse flag each.
Nothing either lane wrote is dropped.

One line neither lane wrote: `--derived-artefacts` + `--working-tree` + `--at-its-own-commit` are
three standpoints, and the merged `main()` would have accepted the first two together and **silently
graded one under the other's name**. The `--working-tree` lane had already written exactly that
guard against `--at-its-own-commit`; this extends theirs to the third flag.

## Measured, not assumed

* Both lanes' controls green together — 9 + 6 = **15 passed**.
* The relation is **live**, not merely importable: `--derived-artefacts` grades 22 attributed
  artefacts and reds a real instance today —
  `docs/observability/value_cycle_ab_floor_partition_probe_both_keys.json` against
  `tools/run_value_cycle_ab.py` — printing `unattributed=161 of 183` BESIDE the verdicts, so the
  silence is not readable as coverage.
* The 3 reds left in `test_a_published_feed_matches_what_its_generator_would_produce` are **not
  mine, and I ran the one-variable control rather than asserting it**: with HEAD's own copy of the
  module swapped back in, the same three fail identically. They are feeds whose provenance stamp
  says their bytes were read off a dirty working tree (`NO_STANDPOINT`) — a property of this shared
  tree, not of this merge.

## The correction I owe my own reading

My first read of the diff was **wrong and I acted on the check rather than the read**. The working
copy was 09:10 and the last commit to its path was 11:03, which is this repository's catalogued
"predates landing" signature, whose named door is `refresh_to_head` — *destroying the other lane's
work*. That door was the wrong one. Asking whether the copy supplied any name HEAD lacked is what
refuted it: it supplied six. **A copy older than the last commit to its path is not always a
revert — it can be a concurrent fork from a shared base**, and the age test alone cannot tell the
two apart. The question that separates them is whether the copy carries symbols the landing lacks.

## What is still open, and is not mine to close

`docs/staging/` shows the publisher's own state file still recording `wedge_since`
2026-09-21T20:40 and `episode_clean_publishes` 0. The site leg that wedged it is green and this
collection error is cleared, so the next publisher cycle is the measurement. **It has not run yet,
so I am not claiming the outage is over** — only that both reds it was standing on are gone.
