# Lane 0 — the three-arm A/B on the S1 world: half landed, the run is in flight

**BLOCKING SUB-ITEM:** the second row of the three-arm table. It needs the artefact
`docs/observability/value_cycle_ab_s1_three_arm.json`, which a detached run is writing now.

**WHAT UNBLOCKS IT:** that file existing with `level_vs_selection.available == true`. Nothing else.
Do not re-run the A/B to get it — check the log first.

**Claim id (bind every commit to it):** `re-run-the-three-arm-ab-on-the-s1-world`

---

## What is already landed and pushed — do NOT redo it

`bafa625d1` (on origin/main):

1. **Act one, complete.** The 2019 ladder section of `docs/design/THE_VALUE_CYCLE_REALISED_AB.md`
   now opens with a forward pointer to the full-window reading, in the headline table's own
   supersession style. It separates what survives (the win is not price — both windows agree) from
   what does not (the 1.16× figure's direction and size, computed on 6 decisions because 18 priced
   renewals rolled after 2019-12-31 and were dropped). Anchors verified to resolve. **Finished.**
2. **The runner learned the third arm.** `tools/run_value_cycle_ab.py --level-arm` runs
   `flat_at_level` as a third pass **at the value arm's own realised median read off the same
   run** — never the remembered £44.50. New `level_vs_selection` block. 9 R15 tests in
   `tests/tools/test_the_level_arm_in_the_ab_runner.py`, mutation-proven both directions.

The finding that closed the `flat_at_level` build called this gap *"a standing instrument rather
than a one-off"*. It was not one — the arm existed, the runner did not know about it, and the
published 119.7% came from an ad-hoc invocation no committed code could reproduce. Now it can.

## The run in flight

```
started   2026-08-27T15:08:25Z, detached under setsid (PID==PGID==SESS==1128717)
log       docs/observability/three_arm_s1_run.log     ("END rc=" appears when it finishes)
artefact  docs/observability/value_cycle_ab_s1_three_arm.json
command   python3 -m tools.run_value_cycle_ab --level-arm --out <artefact>
```

Three full-window passes (control, `value_based`, `flat_at_level`). Budget from the measured
2-arm cost of ~25 min: **expect ~35–40 min**, so ~15:45Z.

**Check the log before anything else.** `END rc=0` means done. `END rc=` non-zero means it failed
and the reason is above that line — a 0-byte artefact plus no `END` line means it was killed from
outside, which is the failure mode this wrapper exists to make visible.

## What to do when it lands

Add **a second row** to the three-arm table in
`docs/staging/done/WORKER_FINDING_THE_VALUE_ARMS_ADVANTAGE_IS_THE_LEVEL_NOT_THE_SELECTION_2026-08-27.md`,
naming the **S1 world**, and state the book and the clock per R14. Read all of it off
`level_vs_selection` in the artefact — every number below is a key in that block:

| what to report | key |
|---|---|
| the three nets | `control_net_gbp`, `value_arm_net_gbp`, `level_arm_net_gbp` |
| the level's share of the advantage | `level_share_of_advantage` (was **119.7%**) |
| what the selection was worth | `selection_gbp` (was **−£1,388.80** decade, −£991.38 on 2019) |
| the level actually used | `level_gbp_per_mwh` — the arm's own median, **expect it to have moved** |

The book is in `book_identity.control_arm`; the clock is **settled** (R14), as `basis` says.

**Then say, in the document's own words, whether the selection leg moved off negative.**

## The two things that would make this dishonest

* **R12 — a selection still worth less than nothing FINISHES this item completely.** It is the
  honest and quite likely outcome of widening the world along a single axis. It is *not* a cue to
  tune the arm until it wins. Report it and close.
* **Do not report the enterprise-value reading beside the net as "a second clock."** EV projects
  CLV from `churn_risk` — the company's own belief — and the arm maximises expected value under
  `enriched_churn_estimate`. The arm optimises under a model and EV re-scores the book under the
  same model: R15 TAUTOLOGY, with the scoring belief anti-informative at AUC 0.4653. The runner
  withholds it on purpose and a test pins that. Realised net is the verdict.

**Do NOT chain a price ladder to this in the same tick** — that was the direction's own instruction
and the ladder costs a further ~51 min.

## On landing

`python3 -m tools.surgical_land` (or tree_lock + pathspec), then **immediately**:

```
python3 -m background.delivery_lane --landed re-run-the-three-arm-ab-on-the-s1-world
python3 -m background.delivery_lane --release re-run-the-three-arm-ab-on-the-s1-world   # when done
```

Archive this file to `docs/staging/done/` once the second row exists.
