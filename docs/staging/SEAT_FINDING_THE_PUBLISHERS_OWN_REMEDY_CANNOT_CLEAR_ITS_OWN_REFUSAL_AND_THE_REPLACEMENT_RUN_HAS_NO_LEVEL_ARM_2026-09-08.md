**Severity:** BLOCKING · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# The publisher's own recorded remedy cannot clear the publisher's own refusal, and today's run that carries the two new estimands has no level arm

**Filed 2026-09-08 by the delivery seat (lane 0), working the direction
`the-page-publishes-a-run-that-predates-both-instruments-it-was-built-to-carry`. Both findings below
were established by running the things the direction named, in the order it named them, and reading
what they printed. Neither answer was known when the turn started.**

---

## 1. The remedy in `cause_evidence` is the same cause one level down

The direction is explicit that the cause must come from the publisher's own recorded output and not
from anything inferred. It does. `docs/observability/.publish_gate_state.json` carries 29 failures
this episode, `episode_clean_publishes: 0`, `last_clean_publish: null`, and every failure names
`behind_origin` with its own remedy written into `cause_evidence`:

> Reconcile first: `python3 -m background.origin_reconcile`, which does the gated merge in an
> ISOLATED worktree.

Run against the shared tree, that remedy answers **`NOT_ADVANCED`**. Origin is 7 ahead, the shared
tree is 0 ahead, and five paths block the fast-forward:

| path | kind |
|---|---|
| `site/data/evidence.json` | modified here, and origin changes it too |
| `tests/tools/test_stale_copy_refusal.py` | modified here, and origin changes it too |
| `tools/stale_copy_refusal.py` | modified here, and origin changes it too |
| `docs/staging/PREREG_HOW_MANY_ROWS_DOES_THE_CENSUS_MODULE_EVIDENCE_FALLBACK_HIDE_2026-09-08.md` | untracked here, and origin adds its own copy |
| `docs/staging/SEAT_RESULT_THE_CENSUS_DISMISSAL_RULE_WAS_FAIL_OPEN_AND_THE_SCOPE_IS_NOW_THE_WHOLE_CLASS_2026-09-08.md` | untracked here, and origin adds its own copy |

The two staging documents are byte-identical twins and `origin_reconcile` would clear them itself.
The three tracked paths are not, and it refuses — correctly, and in its own words: *"3 of 5 blocking
path(s) are NOT byte-identical to what origin brings, so clearing the 2 that are would delete files
and still not advance."*

**This is not a defect in `origin_reconcile`.** Its refusal is right and its docstring already says
it cannot fast-forward past uncommitted work. The defect is that the sentence it writes into the
publisher's `cause_evidence` reads as a complete remedy, and on this tree it is not one: it names a
command whose only possible answer is a second refusal. Three consecutive directions have now named
the publisher and the failure count has gone **up** — 24, then 25, now 29 — and this is why. Every
reader of that state file, human or daemon, is routed to a command that cannot clear what it is
cited as clearing.

**What the missing sentence is.** `origin_reconcile` clears a blocking path only when its bytes
ALREADY equal what origin brings. So the remedy is not "run reconcile" — it is *"land the blocking
paths, then run reconcile"*, and the blocking paths are the ones the tool already enumerates by
name. The refusal has the whole answer in it and stops one step short of stating it.

### What landed this turn against it

The four-file cluster, through `tools.surgical_land` from an isolated worktree.

**The cluster is four files and the refusal could only ever name three.** The three tracked
blockers alone are red: `tests/tools/test_stale_copy_refusal.py::test_the_landing_door_hands_the_guard_the_merge_ref`
reads `tools/surgical_land.py` *as source text* and asserts `merge_ref=merge_parent` appears in it —
the wiring half of a FAIL-SILENT control. `tools/surgical_land.py` is dirty in the shared tree too
(+19/−2 against origin) but origin does not change it, so it does not block the fast-forward and the
refusal had no reason to mention it. Landing the three named paths: **1 failed, 28 passed**. Landing
all four: **112 passed** across both suites.

That is a general shape worth keeping: *the paths a fast-forward refusal names are chosen by what
ORIGIN touches, not by what the working tree's own work depends on.* A refusal-driven landing is
therefore a lower bound on the cluster, never the cluster. Check the named paths' tests before
landing them, not after.

---

## 2. The run that carries both new estimands cannot be promoted: it has no level arm

The direction's second item says `method_skill.fixed_horizon.available` and
`method_skill.survivorship.available` are false *"purely because `run_generated_at` is 2026-08-31
and the estimands landed today"*. The first half is right and the second half turns out to
understate the work.

`site/data/value_arms.json` reads `run_generated_at` from
`generate_value_arms_data.THREE_ARM_PATH` = `docs/observability/value_cycle_ab_s1_three_arm.json`,
whose `generated_at` is `2026-08-31T03:47:57Z`. Its `method_skill` has no `fixed_horizon` key at
all, and `survivorship` is the explicit withholding: *"the run that produced this artefact predates
the survivorship split"*.

**A run from today already carries both.** `docs/observability/value_cycle_ab_fixed_horizon_2026-09-08.json`
(`2026-09-08T15:13:31Z`, world `39a192ce04c1eda8`, producing commit `e1a7f1a56`) has
`method_skill.fixed_horizon.available: true` and `method_skill.survivorship.available: true`. It is
tracked, committed at `f78daf5ef`, and it is the same live world as the current-world leg.

**And it is not promotable, for a reason nothing on the surface says.** Its
`level_vs_selection.available` is `false`, and its own `why_not` states the cause:

> the level arm was not run -- pass `--level-arm`. Without it the artefact cannot say whether the
> advantage was the level or the selection, and must not be read as if it could.

`level_arm` is `None`. It is a **two-arm** run. Promoting it to `THREE_ARM_PATH` would give the page
today's date and both new estimands while silently withdrawing the level/selection split that is the
whole reason the third arm exists — the page would gain two instruments and lose the control that
makes its headline answerable at all.

**The second blocker, and it is the pair-move rule.** `THREE_ARM_PATH`'s bound comes from
`NOISE_FLOOR_PATH` = `value_cycle_ab_s1_noise_floor.json`, measured `2026-08-31T07:05:53Z` at a
level of ~53 £/MWh. Today's world runs at 20.0 £/MWh. Moving the point estimate to a today run
without moving the floor with it puts a spread from one world over an estimate from another —
`_staleness_caveat` fires and the page publishes a caveated bar it cannot stand behind. The
`CURRENT_WORLD_THREE_ARM_PATH` docstring records the same mistake being made and reverted on
2026-09-08 at 04:10Z, where the headline republished 7.6× larger with no error bar at all.

### So item 2 is a run, not a pointer move, and it is in flight

Launched this turn, detached, from the shared tree:

```
python3 -m tools.run_value_cycle_ab --level-arm \
  --out docs/observability/value_cycle_ab_s1_three_arm_20260908b.json
```

The comparable run (`value_cycle_ab_s1_three_arm_20260908.json`) took roughly 2.5 hours for its
three passes, so this does not finish inside one turn. **What it still needs after it lands is a
noise floor measured on it** — `--noise-floor-seeds 11111,22222,33333 --redraw-mode all`, nine
passes — and then `THREE_ARM_PATH` and `NOISE_FLOOR_PATH` moved together in **one** commit. Moving
either alone is the defect the pair exists to prevent, in both directions.

---

## What is next

1. When `value_cycle_ab_s1_three_arm_20260908b.json` lands, check its `level_vs_selection.available`
   is `true` and its `method_skill.fixed_horizon.available` is `true`. If either is false the run
   answered a different question and the promotion is still not owed.
2. Run the undecomposed noise floor on it. `BOUNDING_REDRAW_MODE` is `all` and neither partition leg
   bounds the whole.
3. Move `THREE_ARM_PATH` and `NOISE_FLOOR_PATH` in one commit, and check the page's
   `error_bar.available` and `method_skill.fixed_horizon.available` on the rendered feed, not on the
   generator's return value.
4. Separately, and cheaply: make `origin_reconcile`'s `NOT_ADVANCED` detail state the landing step.
   It already computes the blocking set and already knows byte-identity is what clears a path; the
   remedy sentence it hands the publisher is the only thing missing.
