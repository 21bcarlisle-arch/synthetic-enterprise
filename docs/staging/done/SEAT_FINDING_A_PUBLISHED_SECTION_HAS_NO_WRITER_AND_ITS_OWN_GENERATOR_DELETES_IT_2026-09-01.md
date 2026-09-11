# [SEAT FINDING] `value_arms.json` publishes a section no committed code writes, and the file's own generator deletes it on sight

**Severity:** LATENT · **Lane:** G_data_learning · **Epoch:** 3 · **Atom:** `A46_the_priced_menu`
**Found:** 2026-09-01, by the delivery seat, while working the bill-shock lane-0 item in an isolated
worktree. Found by accident, which is the part worth keeping: nothing looks for this.
**Class:** `uncommitted_and_orphaned_work`, and a sibling of
`a_published_capture_was_produced_by_code_that_was_never_committed`.

---

## The fact

`site/data/value_arms.json` at `318066998` publishes a `svt_drift_belief` section:

    {"available": true, "route": "the standard variable tariff", "decisions": 1266,
     "departures": 50, "ceiling": 0.6091441315862838, "ceiling_null_low": 0.4159...,
     "ceiling_null_high": ..., ...}

**`tools/generate_value_arms_data.py` owns that file — its module docstring is "Generate
site/data/value_arms.json" — and contains zero occurrences of `svt_drift_belief`.** Checked on
`origin/main`, not on a working tree. Nothing else writes the key into that artefact either:
`simulation/run_phase2b.py` mentions it once, in a comment about a test;
`tools/measure_churn_heterogeneity.py` derives quantities of that name but never opens
`value_arms.json`.

## The consequence, observed rather than reasoned about

I ran the owning generator against the current tree, for an unrelated reason. It completed cleanly
(`wrote .../value_arms.json (available=True, realised=True, error bar=True)`, rc=0) and **the
`svt_drift_belief` section was gone from the output** — 24 top-level keys before, 23 after.

No error. No warning. The full `site/` suite stayed green at **520 passed, 31 skipped**, so not one
control anywhere noticed that a published section carrying a measured ceiling of 0.609 and its null
band had ceased to exist.

**So the section survives exactly until the next legitimate run of the generator that owns its
file** — and the run that removes it will look like a routine regeneration, because that is what it
will be.

## Why this matters more than one orphaned field

The number in it is load-bearing. `ceiling: 0.609` with a published null band is the SVT drift
belief's own measured ceiling, and `tests/architecture/test_the_svt_drift_belief_is_not_wired_to_
any_decision.py` exists precisely to hold open the question of whether that belief reaches a
decision. The feed is where a reader sees it. A control that guards how a belief is *used* does not
notice the belief's publication silently ending.

And it is the second instance found in one afternoon. `site/data/dashboard.json` was serving
`shock_by_population`, `avg_shock_pct_definition` and `mixed_all_population_avg_pct` while
`tools/generate_dashboard_data.py` at HEAD produced none of them — that one has since been closed by
`98db658f2`, which landed a real producer. This one has not, and it is the mirror image: there, the
artefact ran ahead of the code and the code caught up; here, the artefact holds something the code
will destroy.

**The general shape: an artefact and its generator can disagree in either direction, and this
project has now hit both within a few hours, in two different published feeds, with no control able
to see either.**

## What is owed

1. **Establish what was supposed to write `svt_drift_belief` into `value_arms.json` and land it.**
   That is the SVT lane's subject and needs that lane's knowledge — the figures are real
   measurements and inventing a producer for them would put numbers on a page with nothing behind
   them. **Not done here for exactly that reason.**
2. **A control that compares one publish's field set against the last one's.** This is the control
   whose absence let both instances exist, and unlike (1) it is not any one lane's: a published feed
   losing a top-level section between publishes should be a red, not a diff nobody reads. It is
   filed rather than built because a control over the publish surface is its own subject and should
   not be grown as a side-effect of a bill-shock pass — but it is the piece with the most leverage
   here, because it would have caught both instances the moment they appeared.

## What this finding does not claim

Not that the published figures are wrong — the section reads as a real measurement and nothing
suggests otherwise. Not that regenerating the file is wrong; it is the correct thing to do and it is
how this was discovered. The claim is narrower and worse: **a published section is one ordinary
regeneration away from silently disappearing, and nothing in the repository would report it.**

## How this was found, recorded because the route matters

Not by looking for it. I regenerated `value_arms.json` while trying to clear an unrelated red
(`test_the_level_on_the_page_is_the_one_the_measuring_tool_REPORTS`), diffed the before and after to
check what my own change had moved, and the section was missing from the diff's "after" side. **The
diff was taken because the file was a published surface, not because anything suspected a loss.**
Had I regenerated and committed without diffing — which is the normal shape of a regeneration — the
section would have gone and this document would not exist.

*(Separately: my repair of that red was the WRONG one and was discarded rather than landed. I
regenerated the page to match the tool; `b46318106` had already landed the capture the published
figures were actually produced from, so the page was right and the capture was missing. Recorded
because a discarded wrong repair is evidence about which of two symmetrical fixes to reach for when
a page and its tool disagree: establish which side is stale before assuming it is the page.)*
