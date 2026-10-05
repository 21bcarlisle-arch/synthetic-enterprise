**Severity:** RECORDED · **Lane:** W4_the_wall · **Epoch:** 3 · **Atom:** `EP13_adapter_carbon_intensity`

# Parking EP13 was already done, except for the knowledge map link

Claim `park-ep13-at-a-clean-point-with-its-findings-written-up`. I re-measured the premise against origin/main
(`1e687e06b`) before building. Four of the five asks had landed by another route:

- **The row is parked.** `de323eb13` set `loop_stage: idle` at `level_current: 2`. Its
  `block_reason` names the director's steer and the return condition ("if first-principles carbon
  is ever needed").
- **The knowledge note is on origin.** `f98a30805` landed
  `docs/market_research/what_ep13_established_about_gb_grid_carbon.md`, and the row names it. It
  covers Viking and ElecLink left out of the mix, North Sea Link at Norway's mix, the Drax RO units,
  and the coal band above 30 GW of gas. It carries a `**Knowledge:**` line, set to `none` with a
  reason because no knowledge page covers grid carbon.
- **The clean point.** s43 (`3e7236f43`) landed before the park, as `de323eb13` intended. No EP13
  step has landed since.
- **The remaining part:** `docs/institutional/knowledge_map.md` did not name the note. This claim
  lands that link as one row in Simulation-Specific Calibration.

The duplicate-work note's other claim, `the-unmerged-work-guard-diffs-against-origin-not-a-behind-local-main`,
holds the EP13 frame and simplification files. Those are a different subject, and this landing does
not touch them. The continuation `g14-takes-the-published-carbon-series-and-a-weather-fitted-future`
carries the carbon work forward. This claim is released once the link lands.

## What landing this record found

Landing this record went red. The cause was `test_no_committed_discharge_cites_an_unlanded_falsifier`,
not this file. G14 (`09e2bf07f`) deleted `test_the_headline_says_we_OVERSTATE_and_by_how_much`. It
was right to: the feed now *is* NESO's series, so there is no overstatement left to test. But the
file that held it survives, and a closed record in `done/` still cites the node. The control already
accepts a falsifier whose file was deleted on purpose. It had no answer for a node deleted from a
file that survives, so it went red at origin for every commit that selects it.

The repair widens the retirement answer to cover nodes. A node is admitted when git names a commit
whose parent holds it and whose own tree does not. A node no commit ever carried is still refused.
Two mutants were checked: always-admit reds five tests, and never-admit reds the tripwire and the
new arm.
