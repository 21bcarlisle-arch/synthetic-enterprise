**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 3

**Verified, no code change needed.** Filed so the next tick does not follow the letter of the
disposition doc and undo work a prior tick already got right.

## What was drawn

The lane-0 doorbell (2026-09-03, later tick) carried forward
`docs/direction/DIRECTION.yaml`'s focus item
`the-shared-tree-holds-a-second-copy-of-a-landed-control-and-is-armed-to-revert-it`, quoting
`docs/staging/done/SEAT_FINDING_THE_SIX_FILE_DIVERGENCE_MOVED_NO_ANCHOR_AND_ONE_CONTROL_WAS_BUILT_TWICE_2026-09-03.md`
verbatim: *"Salvage `_svt_drift_belief()` and the three `test_MUTATION_*` legs from
`refs/preserved/shared_tree_20260903T1104Z`... Discard the tree's `_world_moved_since()` /
`_staleness_caveat()` draft as the duplicate it is."*

## What is actually true, re-measured at HEAD (`1df22e3bd`)

All four of that item's own done-when clauses already hold, landed by a prior tick
(`06ce91bc9`, `ef9c801e3`), and the disposition doc already carries a `**Discharged:**` line
saying so:

- `git rev-list --left-right --count HEAD...origin/main` → `0 0`.
- `feed["world_provenance"]` is present in `site/data/value_arms.json` at HEAD;
  `world_currency` is absent.
- `_svt_drift_belief()` in `tools/generate_value_arms_data.py` is byte-identical (129 lines) to
  the copy in `refs/preserved/shared_tree_20260903T1104Z`.
- `grep -rn "_world_moved_since"` over code (py/js/html) returns 0 hits tree-wide; it survives
  only in prose (this doc, the archived finding, `.seat_continuation.json`, `DIRECTION.yaml`).
- The six subject paths are clean against HEAD (only the regenerated
  `site/data/value_arms.json` differs, and only in `book`/`generated_at`/`producing_commit`/
  `realised` — a re-run, not a divergence).

So there was nothing to land this tick. Confirming that took the whole check; it is recorded here
because of what the doc's own text would have caused if followed literally.

## The self-contradiction in the disposition doc itself

The same document that recommends salvaging *"the three `test_MUTATION_*` legs"* had, forty lines
earlier, listed those same three legs as part of the draft it says to **discard**:

> "Shared tree, uncommitted: `_world_moved_since()`, `_staleness_caveat()` and the door tests
> `test_the_vintage_of_the_comparison_reaches_the_reader`,
> `test_the_stale_world_statement_names_the_anchor_that_sets_the_surface`, **plus three
> `test_MUTATION_*` legs**."

Checked directly against `refs/preserved/shared_tree_20260903T1104Z`: the only three
`test_MUTATION_*` functions in that ref's copy of
`site/test_the_baseline_comparison_reaches_the_reader.py` that were not already on origin are
`test_MUTATION_figures_measured_on_this_very_tree_render_no_alarm`,
`test_MUTATION_a_vintage_that_could_not_be_established_still_warns`, and
`test_MUTATION_a_feed_with_no_world_currency_block_still_warns` — all three keyed to the
`world_currency` block, i.e. the exact draft the same document calls a duplicate to be discarded.
`_svt_drift_belief()` has no `test_MUTATION_*` legs of its own anywhere in the tree or in either
preserved ref (its door coverage is four plain-named tests:
`test_a_reading_that_clears_its_null_is_not_reported_as_cannot_tell`,
`test_an_arm_with_no_interval_renders_unknown_and_never_the_flattering_reading`,
`test_an_unavailable_reading_renders_its_reason_and_never_an_empty_block`,
`test_the_superseded_uncorrected_reading_never_reaches_the_reader` — all four already present at
HEAD, verified identical).

So "salvage `_svt_drift_belief()` and the three `test_MUTATION_*` legs" reads as one clause but
names two things on opposite sides of the doc's own keep/discard line. A tick that took it
literally — pulling the three `world_currency`-keyed mutation legs into the tree without their
subject — would either fail collection (`svt_drift_belief` fixture absent) or, worse, resurrect
`world_currency` handling to make them pass, reintroducing the second lineage the whole item exists
to remove. The prior tick that actually landed this evidently read it as I did (origin's
`world_provenance` lineage plus `_svt_drift_belief`, nothing from the `world_currency` draft) —
correctly — but the doc and the DIRECTION.yaml focus item still carry the literal, misleading
instruction verbatim, and will keep re-offering it that way until this is discharged or the wording
is fixed.

## Disposition

No code change. The correct salvage already happened. This finding exists only to stop the
misreading from being tried again by a future tick that has not yet re-derived what a prior one
already worked out — the exact failure mode `CLAUDE.md` names: *"the seat is the only place in the
architecture that can hold [cross-tick interconnection], so a defect of this class is invisible
everywhere else until it is expensive."*

Not filed as a discharge of anything else — nothing here is broken code and nothing needs a
falsifier. It is a standalone RECORDED note. The disposition doc's own text is left as-is (history
should not be edited retroactively); this finding is the pointer a future reader needs before
acting on its salvage clause literally.
