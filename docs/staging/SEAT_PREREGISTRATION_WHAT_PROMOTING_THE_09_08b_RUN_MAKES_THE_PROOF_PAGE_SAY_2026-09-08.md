# PRE-REGISTRATION — what promoting the 2026-09-08b run makes the value-arms page say

**Severity:** LATENT · **Lane:** H_harness

**Filed 2026-09-08 ~22:10Z, before the promotion was driven and before the noise floor it waits on
had finished.** Filed because the answer moves a published headline by ~8x in the UNFLATTERING
direction, and a prediction written after that number is on the page is not a prediction.

## What is already settled, and is therefore not a prediction

Established by reading, not by measuring:

1. **The `behind_origin` refusal in `docs/observability/.publish_gate_state.json` is spent.** The
   record (ts 2026-09-08T21:09:11Z) says `origin/main is 3 commit(s) AHEAD of HEAD`. At 22:02Z
   `git rev-list --count` reads 0 both ways and the shared tree, `origin/main` and this worktree
   are all `35446fa0c`. The remedy the refusal itself named — `python3 -m background.origin_reconcile`
   — was run and returned `LEVEL: local and origin/main agree; nothing to reconcile`. The fork was
   closed by another lane's landing at 22:00:48Z, not by anything filed here. **No inferred cause
   was substituted for the recorded one; the recorded one was tested and had expired.**
2. **The value-arms re-run the direction asks for has already happened.**
   `docs/observability/value_cycle_ab_s1_three_arm_20260908b.json`, `generated_at`
   2026-09-08T21:01:30Z, produced by `b8bcbac2c`, world `39a192ce04c1eda8`. It is tracked and
   committed. It carries **both** estimands the direction names: `method_skill.fixed_horizon`
   (`available: true`, `decisions_priced: 214`, `horizon_days: 365`) and `method_skill.survivorship`.
   Neither exists on `_20260908.json` (00:19:54Z) nor on the currently-promoted `_20260831.json`.
3. **The matching noise floor is in flight, not missing.** PID 2900491,
   `run_value_cycle_ab --noise-floor-seeds 11111,22222,33333 --redraw-mode all
   --redraw-accounts-from ..._three_arm_20260908b.json --out ..._noise_floor_20260908b.json`,
   ~30 minutes in at 22:02Z. So the pair completes without a new run being launched here.
4. **The promotion is a file copy, not a constant edit.** `AUC_RUN_HISTORY`'s own comment states
   `value_cycle_ab_s1_three_arm.json` is "the path the newest run is PROMOTED to". `THREE_ARM_PATH`
   and `NOISE_FLOOR_PATH` therefore do not move; their contents do. The dated copies stay on disk,
   so superseded-with-provenance is preserved by construction rather than by care.

## The predictions

Measured on the promoted canonical pair, `site/data/value_arms.json` rebuilt by today's
`tools/generate_value_arms_data.py`.

**P1 — the headline falls ~8x.** The published selection figure goes from **£2,574.37** (08-31 run)
to **£323.52** (09-08b), while `value_advantage_gbp` RISES from £12,071.08 to £17,452.61 and
`level_share_of_advantage` rises **0.7867 → 0.9814**. The reading that follows: on this run the
per-customer selection buys almost nothing — 98.1% of the advantage is available from a flat
higher margin. This is a WORSE result for the method than the page currently shows, and it is the
reason this file exists.

**P2 — the staleness caveat stays `None`, and only because the floor is newer.** `_staleness_caveat`
compares stamps only. The 09-08b floor must stamp **after** 21:01:30Z for `error_bar.staleness_caveat`
to remain `None`. Predicted: it will, since it started ~20:32Z and had not finished at 22:02Z.
**If it stamps before 21:01:30Z, the promotion is abandoned, not shipped with a caveat** — that is
the reverted 2026-09-08 mistake (headline 7.6x larger with no error bar) on the canonical pair
instead of the current-world one.

**P3 — the figure becomes emphatically indistinguishable from zero.** From the same-world 04:10Z
floor the three `selection_gbp` seeds were +1199.55, −3075.22, +433.07 (stdev ≈ £2,296). Against a
point estimate of £323.52 that is `spread_to_point_estimate_ratio` ≈ **7.1**, up from 1.467.
Predicted: ratio > 5, `distinguishable_from_zero` stays **false**. I am predicting the RATIO band,
not the 09-08b floor's own stdev, which is the thing being measured.

**P4 — both estimands light up.** `method_skill.fixed_horizon.available` and
`method_skill.survivorship.available` both become `true`, from `false`/absent. `fixed_horizon` is
read off the run and never recomputed, so this is a pass-through and not a new claim.

**P5 — the whole-page world caveat clears.** The current headline opens "THE FIGURE BELOW AND THE
BOUND ON IT WERE MEASURED IN DIFFERENT WORLDS. The runs behind it are dated 2026-08-31." Predicted:
that sentence goes, because both promoted artefacts will carry digest `39a192ce04c1eda8` and the
08-31 floor's `world_identity` was absent altogether.

**P6 — what I predict will NOT move, and it is the risk.** The `current_world` block reads
`CURRENT_WORLD_THREE_ARM_PATH` (`_20260908.json`, 00:19:54Z) and is NOT part of the promotion. Once
the canonical run is the 21:01:30Z run, that block presents an OLDER run of the SAME world as "the
world as it is now", beside a newer one. `_later_runs_in_this_world` should detect exactly this and
say so. **Predicted: it fires and names `_20260908b.json` as a later run in this world.** If it
does not fire, the page carries two current-world figures and prefers the older silently, and that
is a BLOCKING finding to file — not a caveat to write into the prose.

## What refutes this

- P1 refuted if the rebuilt feed's selection headline is not £323.52: then `_realised` /
  `_split_on_the_realised_clock` are routing by something other than the artefact's declared clock,
  and the number I read off `level_vs_selection` is not the number the page publishes.
- P3 refuted if `distinguishable_from_zero` comes back `true`: the 09-08b floor would have to have
  collapsed to a spread under ~£165, which for three seeds in this world would itself be the finding.
- P5 refuted if the caveat persists: the world guard is keyed to something other than the digest
  pair I read.
- P6 is the one I most expect to be wrong in the flattering direction, so it is written as the
  test of a mechanism I have not run rather than as a description of one I have.

## Result

**Measured 2026-09-08 ~22:15Z by calling `build()` on the candidate artefacts directly — no
canonical path was written to, so nothing was published to get these numbers.** The promotion itself
is NOT yet done: it waits on the floor (see P2). Predictions scored as filed.

| | Predicted | Measured | |
|---|---|---|---|
| P1 | headline falls to £323.52; share 0.7867 → 0.9814 | `bounds_figure_gbp` £323.52; share 0.9814628 | **CONFIRMED** |
| P2 | staleness caveat fires on a floor older than 21:01:30Z | fires, naming 04:10:26Z vs 21:01:30Z | **CONFIRMED (mechanism); promotion still blocked)** |
| P3 | ratio > 5, `distinguishable_from_zero` false | ratio **7.045**, false | **CONFIRMED** |
| P4 | both estimands become available | `fixed_horizon.available` True, `survivorship.available` True | **CONFIRMED** |
| P5 | the "DIFFERENT WORLDS" whole-page caveat clears | `world_caveat: None`, opener gone | **CONFIRMED** |
| P6 | `later_runs_in_this_world` fires and names `_20260908b.json` | fires, names it with share 0.9815 | **CONFIRMED** |

**P6 was briefly mis-scored as refuted and that is recorded rather than tidied away.** The first read
looked for `later_runs_in_this_world` at the top of `current_world`, found `null`, and I wrote it
down as the mechanism failing to fire. It is nested at
`current_world.composition.later_runs_in_this_world` and had fired correctly all along. The
prediction was right; the first reading of its result was wrong, at the wrong nesting level. `null`
at a key that does not exist is indistinguishable, from a `.get()`, from a mechanism returning
nothing — which is the same shape as this project's "probe both ends of a pointer" rule.

### What the pre-registration did not predict, and it is the whole finding

Nothing above is why this turn matters. Checking P1's baseline against the **live** feed found that
the page as published already said:

> IN THE WORLD AS IT IS NOW, the same comparison gives £17,739 … It is a **SMALLER** advantage than
> the £12,071 below, **not a larger one**: what moved is the floor, which fell further than the
> advantage did.

£17,739 is larger than £12,071. That is a live published falsehood, it predates this turn, and no
prediction here anticipated it — it was found by reading the number the page already carried in
order to establish a baseline for a prediction about a different number. Filed as
`SEAT_FINDING_THE_PROOF_PAGE_TOLD_A_READER_A_LARGER_FIGURE_WAS_SMALLER_2026-09-08.md`, **BLOCKING**,
and fixed in this turn.

The reason it belongs in this file too: **P1 through P6 were all about what promoting would change,
and the defect was in what promoting would leave alone.** The pre-registration asked "what does the
new run make the page say" and the answer that mattered was "the page was already lying about the old
one". A prediction set scoped to the change cannot see a standing defect in the thing being changed
*from*, and this is the second time that shape has cost this project a published figure.
