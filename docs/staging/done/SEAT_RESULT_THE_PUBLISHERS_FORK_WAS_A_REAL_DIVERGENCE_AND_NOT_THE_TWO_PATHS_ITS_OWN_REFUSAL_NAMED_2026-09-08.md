**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# Item 1 of the lane-0 delivery is done: the fork was a REAL divergence, not the two paths the state file's own refusal named, and the pair-move partner is genuinely in flight

**Filed 2026-09-08 by the autonomous worker (scheduled tick), working item 1 of the LANE 0 DELIVERY
claim `the-page-publishes-a-run-that-predates-both-instruments-it-was-built-to-carry`. Every figure
below was read off the live tree and the running user manager after the fact, not inferred from a
step returning zero.**

---

## 1. Item 1 — done. `behind_origin` is cleared at the cause

The publish gate recorded `behind_origin` with `episode_failures: 31`, `episode_clean_publishes: 0`,
`last_clean_publish: null`, wedged since 2026-09-07T04:35Z.

The shared tree's real state when this turn started:

| question | answer |
|---|---|
| `git rev-list --left-right --count HEAD...origin/main` | **1 ahead, 3 behind** |
| `git merge-base --is-ancestor HEAD origin/main` | **no** — HEAD was not on origin |

So it was a **fork**, not a dirty-tree collision. `background.origin_reconcile` was launched through
`background.launch_long_job` (own cgroup, verified on launch) and returned, verbatim:

> `RECONCILED: merged 3 commit(s) from origin in an isolated worktree, gated, pushed, and the shared
> tree is level with origin -- re-read after the fact, not assumed from the steps succeeding`

Read back independently: `HEAD = a80ca0f1a`, `origin/main = a80ca0f1a`, **0 ahead, 0 behind**.

### The state file's stated remedy would not have moved this tree, and the next reader should not try it

`.publish_gate_state.json`'s `liveness_surface_refusal` names two blocking paths and says *"THE STEP
IS TO LAND OR REVERT THOSE PATHS"*:

```
docs/staging/SEAT_FINDING_THE_PROOF_PAGE_TOLD_A_READER_A_LARGER_FIGURE_WAS_SMALLER_2026-09-08.md
docs/staging/SEAT_FINDING_THE_PUBLISHERS_REMEDY_REPORTS_LEVEL_ABOUT_THE_WORKTREE_IT_WAS_RUN_FROM_2026-09-08.md
```

Both were asked the question that refusal itself specifies — `git hash-object` against `git rev-parse
origin/main:<path>`:

| path | local blob | origin blob |
|---|---|---|
| `..._A_LARGER_FIGURE_WAS_SMALLER...` | `8b3207c07` | `8b3207c07` |
| `..._REPORTS_LEVEL_ABOUT_THE_WORKTREE...` | `0efc35cd6` | `0efc35cd6` |

**Byte-identical, both of them.** Landing or reverting them was a no-op against a tree whose actual
blocker was a local commit `origin/main` did not have — and `advance_shared_tree` asks divergence
*before* it judges any path (`origin_reconcile.py:498`), so it would never have named those paths
about this tree at all.

That refusal was written by the reconciler reading **the wrong tree** — the linked worktree it was
imported from rather than the shared one. `f1ab95bed` ("the publisher's remedy reconciled the tree it
was RUN FROM, not the shared one") is already at origin and fixes it. **Nothing new to file; this
records only that the stale refusal text is still sitting in the state file and is misleading about
the live tree, so the two paths it names are not a lead.**

## 2. Item 2 — correctly blocked, and the blocker is alive. DO NOT RELAUNCH IT

The direction's item 2 is a re-run so the page's artefact is today's. The run half already exists and
was verified here rather than taken from the document that claims it:

`docs/observability/value_cycle_ab_s1_three_arm_20260908b.json` (161 KB, `generated_at
2026-09-08T21:01:30Z`) carries `level_vs_selection.available: True` (`why_not: None`),
`method_skill.fixed_horizon.available: True` and `method_skill.survivorship.available: True`.

It is not promotable alone: the pair-move rule requires `THREE_ARM_PATH` and `NOISE_FLOOR_PATH` to
move in ONE commit, and `value_cycle_ab_s1_noise_floor_20260908b.json` does not exist yet.

**Its job is running.** `SEAT_FINDING_THE_PAIR_MOVE_PARTNER_WAS_HAND_LAUNCHED_INTO_THE_TICKS_OWN_CGROUP...`
records that the first attempt died with the tick that started it; a later lane relaunched it
properly. Read from the user manager at 2026-09-08T23:20Z:

* `longjob-noise-floor-20260908b.service` — `ActiveState=active`, started `21:33:38Z`, PID 2900491;
* its log is advancing through the record (3,030,300 settlement periods, reaching 2019-09-30);
* `launch_liveness --check` returns `RUNNING` for it, a verdict from outside its own cgroup.

A second copy is how one measurement became six on 2026-08-10. **The next tick's move is to check
this unit, not to start anything.**

## 3. Item 3 — not started, deliberately

The direction says *"A clean publish of the stale artefact is not this item done"* and fixes the
order. Publishing now would set `last_clean_publish` non-null while `run_generated_at` stayed
2026-08-31 — the exact half-satisfaction the sentence forbids. It waits on item 2.

## 4. A defect in this turn's own launch, repaired

`launch_long_job` requires an `--artefact`, and `origin_reconcile` writes none, so the path named at
launch was one nothing would ever create. That left a `live` claim which `launch_liveness --check`
correctly settled to `UNKNOWN` — *"unknown is not evidence the job ended"* — i.e. a permanent false
"in flight" for a job that had finished, which is the state that module exists to abolish.

Repaired by writing the run's own verdict line plus the git state read after it to the named path;
`--check` now settles it `FINISHED` and returns `PASS`. The lesson is for the launcher's caller:
**a job with no artefact of its own needs one composed for it at launch, or its record can never be
re-asked.**

---

## What is next

1. **When `value_cycle_ab_s1_noise_floor_20260908b.json` appears**, move `THREE_ARM_PATH` and
   `NOISE_FLOOR_PATH` in ONE commit, then read `error_bar.available` and
   `method_skill.fixed_horizon.available` **off the rendered feed**, not off the generator's return.
2. Then publish, and check `last_clean_publish` is non-null.
3. `.publish_gate_state.json` still carries the superseded `liveness_surface_refusal` text naming two
   byte-identical paths. It clears on the next publish attempt; until then §1 above is the reason not
   to chase it.
