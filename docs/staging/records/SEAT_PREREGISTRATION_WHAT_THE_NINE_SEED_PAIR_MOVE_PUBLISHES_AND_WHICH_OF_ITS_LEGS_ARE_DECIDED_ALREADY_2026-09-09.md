**Severity:** RECORDED · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** (Lane 0 delivery — grade the per-leg conditioning pre-registration) · **Class:** measurements_that_mirror

# PRE-REGISTRATION — what the nine-seed pair move publishes, and which of its legs were decided before it ran

**Written 2026-09-09T15:10Z, while PID 704091 is still in flight.** 22 of its 27 passes have
completed (counted in `docs/observability/arms_rerun_20260909b.log`); the artefact
`docs/observability/value_cycle_ab_s1_noise_floor_20260909b.json` **does not exist**. Nothing below
is a reading of that run's output.

Filed because the Lane 0 item's remaining half — *"publish the run, check the page renders the
'Departures this cut can see' column with real counts instead of the named absence"* — is about to
be executed against an artefact that does not exist yet, and a statement about what the publish
does, made after the publish, cannot be refuted by it.

---

## The premise, re-measured at draw time

`856d7bb6b` is an ancestor of `origin/main`, as the draw said. **The grading half of the item is
spent**: P1–P6 were graded and landed at `4e393cf56`, and the corrected re-run at `c01eaf12d`.
**The publishing half is not spent**, and this document is about that half only.

Re-measured on today's HEAD rather than assumed from the 12:45Z Q5 reading, by calling
`generate_value_arms_data.build()` with substituted artefacts in memory — nothing written:

```
(a) live paths                                   leg_conditioning FALSE   contrast_bounds TRUE  n=3
(b) canonical three-arm <- 09-09c, floor as-is   leg_conditioning TRUE    contrast_bounds FALSE
(c) (b) + the SAME floor, generated_at re-stamped
    to 16:30Z and nothing else changed           leg_conditioning TRUE    contrast_bounds TRUE  n=3
```

Row (b) reproduces Q5 on current HEAD: **publishing the run alone still costs every directional
bound**, and the refusal recorded at 13:00Z stands rather than having been overtaken by defect 1's
repair. Row (c) is a **mechanism probe and its numbers are not publishable** — it is the real floor
with one field overwritten, run to establish what is *load-bearing*, not to produce a figure. What
it establishes: the only thing standing between the pair move and restored bounds is
`_staleness_caveat`'s stamp ordering. The world digests already match, the reconciliation already
passes, and the seed rows are already readable. So a floor of the same world stamped after
13:58:12Z restores the bounds — and the nine-seed run, whose `generated_at` is stamped by
`datetime.now()` at artefact assembly (`run_value_cycle_ab.py:4644`), will be.

## The publish, stated as three pointers rather than one file copy

Because the two blocks are fed by two different constants, and `method_skill` by a third read of
the first:

| Block | Fed from | Constant |
|---|---|---|
| `method_skill.fixed_horizon.leg_conditioning` — **the column the item is about** | `value_cycle_ab_s1_three_arm.json` | `THREE_ARM_PATH` |
| `contrast_bounds` — what every directional claim is gated on | `value_cycle_ab_s1_noise_floor.json` | `NOISE_FLOOR_PATH` |
| `current_world.bound`, `current_world.selection_leg` | `value_cycle_ab_s1_noise_floor_20260908.json` | `CURRENT_WORLD_NOISE_FLOOR_PATH` |

1. `three_arm_20260909c.json` → `value_cycle_ab_s1_three_arm.json`
2. `noise_floor_20260909b.json` → `value_cycle_ab_s1_noise_floor.json`
3. `CURRENT_WORLD_NOISE_FLOOR_PATH` → `..._noise_floor_20260909b.json` (a one-line constant move)

`CURRENT_WORLD_THREE_ARM_PATH` is **held** at `_20260908.json` deliberately. Moving it to 09-09c
would make the superseded panel and the headline the same run, which is the tautology the comment
at that constant warns about — two identical numbers under two headings.

---

## The predictions

- **R1 — the column renders 0 / 0 / 0 / 37 of 40, residue 3, one reason.** *Not a prediction: this
  is already measured on the 09-09c artefact in row (b) above, and it is the same grading P1–P6
  took on 09-09b.* Recorded here so that if the published page shows anything else, the difference
  is attributable to the publish and not to the run.
- **R2** — after steps 1+2, `contrast_bounds.available` is **true** with `seeds: 9` and
  `world_measured_in: 39a192ce04c1eda8`.
- **R3** — `_seed_spreads`' reconciliation passes on the nine-seed floor: this feed's derived
  `selection_gbp` stdev over the 9 rows matches the floor's own published `selection_gbp_spread.stdev`.
  **A disagreement withholds all three contrasts, not one**, so this is the single leg that can
  turn a successful run into a page with no bounds at all.
- **R4** — after step 3, `current_world.selection_leg` reads **n = 9**; after steps 1+2 *alone* it
  still reads **n = 3**. The second half is a poison round: without it, "the leg moved" and "the
  probe cannot see the leg" are the same observation.
- **R5 — DECIDED BEFORE THE RUN, and graded vacuous whatever it returns.** The selection leg still
  states **no direction** at n=9. This is not a test the run can fail: `8b846013e` derives, two
  ways, that a nine-point sample retaining the three original seeds has an arithmetic minimum
  stdev of **£1,145.99**, and the gate needs the stdev under the point — £319.10 on
  `realised.split.selection_gbp`, £270.21 on `current_world.selection_gbp`. Both are more than
  3× under the floor's own minimum. **Grading this as a prediction that survived would be a control
  keyed to an answer it could not fail to give**, which is the defect one document along.
- **R6 — the one I am least sure of, and the one that would change the decision.** **No figure
  currently on the page loses its stated direction to the wider nine-seed spread.** The two
  directional contrasts are `value_advantage_gbp` (£18,918.51 mean, £1,457.33 stdev at n=3) and
  `level_advantage_gbp` (£19,345.47, £968.62). For either to lose its direction the nine-seed
  stdev would have to exceed the point — a 13× and 20× widening respectively. I predict neither
  happens and both stay resolved. `selection_gbp` is already unresolved and cannot be lost.
- **R7** — the publish costs **nothing that is on the page today**. Q5 predicted exactly this about
  the single move and was refuted 10-lost-3-gained, so this is the same prediction one step along
  and it is written down with that history attached rather than without it. The difference between
  the two is step 2, and if R7 is refuted the residue is measured and published the same way Q5's
  was.

## The declared limit, before the answer

A nine-seed floor is still a nine-point sample of a quantity whose sign is not established. **R2
holding does not make the bounds good, only measured**, and the honest surface is `n` beside every
spread it publishes — which is what `world_measured_in` and `seeds` are already for. Nothing here
licenses reading a tighter interval as a stronger result: the six new seeds can only widen the
three retained ones' sum of squared deviations or leave it alone, so a *narrower* spread at n=9
than at n=3 would be arithmetically impossible and would itself be the finding.

## Independence

R2 and R4 are independent of each other by construction — they read different constants, proven in
both directions by the poison round in R4 rather than argued from the two names. R6 is independent
of R2: the spread that decides R6 is computed from the floor's seed rows, and the availability that
decides R2 is decided by a stamp comparison that never looks at them.
