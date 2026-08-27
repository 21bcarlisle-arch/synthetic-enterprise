# The EP1 constant hazard is a property of the COUPLER'S BELIEF-SELECTION RULE, not of the estimator and not of the graded slice

**Date:** 2026-08-27 · **Subject:** `docs/observability/coupled_gap_ledger.json -> EP1_clv_three_horizon`
**Status:** correction of record. Three descriptions of this row are now on file and **all three are wrong**, including the one the current direction told me to write.

---

## 0. The short version

`components.lifetime_level` reports `distinct_hazards: 1`, `hazard_histogram {"0.05": 33}`. That is a
real number and it has now been explained three times:

| # | Description on record | Verdict |
|---|---|---|
| 1 | "The company's CLV cannot tell its accounts apart"; 0.05 is "a FLOOR, not a belief" — a property of the **estimator** | **Wrong** (§2) |
| 2 | The constant hazard is a property of the outcome-selected 33-account **graded slice**, "drawn from the floor bucket" | **Wrong** (§3) |
| 3 | *This document:* it is a property of the **coupler's rule that grades every account at its EARLIEST snapshot**, where the hazard is `BASE + 0×UPLIFT = 0.05` **by construction, for every account in the book** | Mechanism in §4 |

The estimator is not degenerate. The slice is not selected into the floor bucket. The measurement grades
every account at the single moment its churn input is structurally zero.

---

## 1. What the row actually says (observed, on disk)

Read from the committed ledger row (`measured_at` 2026-08-26T11:46:22Z, `run_git_commit` `8afa34ceb`):

- `components.hazard_calibration.distinct_believed_hazards` = **13**, over **622** decision points and 45 churn events.
- `components.lifetime_level.distinct_hazards` = **1**, `{0.05: 33}`.
- `components.population_selection.like_for_like_excluded_over_graded` = 2.964, `excluded_side_is_censored: true`, graded n=33 against 230 excluded-but-still-supplied.

**The current direction misreads the first of these.** It states "seven distinct believed hazards … over
401 decisions". There are thirteen, over 622. 401 is the sum of the **first seven rows of the table** —
the direction stopped reading at `0.23` and summed what it had seen. The four largest omitted buckets are
material to its own argument: `0.41` carries **135** decisions at `believed_over_realised` 3.69 and `0.38`
carries **56** at 2.36. Both are more pessimistic than the 0.08 bucket the direction singled out, and the
0.08 bucket's 7.6x rests on **one** churn event in 95 decisions.

## 2. Why description #1 is wrong — the estimator is NOT degenerate

`lifetime_level` and `hazard_calibration` do not disagree about the estimator. They cover **different
decisions**. `hazard_calibration` counts every renewal point in the run; `lifetime_level` reads one
snapshot each for 33 accounts. Comparing "13 distinct" with "1 distinct" is a population-and-timing
difference, not two estimators contradicting each other.

Measured directly — inverting the published `tenure_expected`/`contract_term` ratio over **every**
account-year snapshot in `docs/reports/run_output_latest.json` (written 2026-08-27 20:09), not just the
graded 33:

```
account-year snapshots with a recoverable hazard : 457   (337 blank horizons, 0 non-invertible)
distinct accounts ever snapshotted               : 154
DISTINCT HAZARDS across all account-years        : 13
  {0.05:194, 0.08:36, 0.11:10, 0.14:4, 0.17:3, 0.20:9, 0.23:10,
   0.26:5, 0.29:19, 0.32:5, 0.35:13, 0.38:39, 0.41:110}
accounts with >1 recoverable snapshot            : 101 of 154
  ...whose hazard EVER moves off its first value : 100 of 101
```

EP1 spreads its accounts across the full 13-value range and moves them over time (`C7`: 0.05 → 0.14 →
0.20 → 0.32 → 0.26 → 0.20 → 0.32 → 0.41 → 0.38 → 0.38). **"Cannot tell its accounts apart" is refuted.**

## 3. Why description #2 is wrong — it is not the graded slice either

The same computation, restricted to each account's **earliest** snapshot — which is the belief the coupler
grades:

```
accounts = 154   DISTINCT = 1   histogram = {0.05: 154}
```

**154 of 154 — the whole book, not a selected 33.** Any 33 accounts drawn by any rule whatsoever would
have returned `distinct_hazards: 1` at `0.05`. Outcome-selection is real and matters for the *magnitude*
of the gap (§5), but it contributes **nothing** to the constant hazard. The graded slice was not "drawn
from the floor bucket": at first snapshot there is no other bucket to be drawn from.

## 4. The mechanism (read from source; run-independent)

- `saas/churn_model.py:39` — `churn_probability = min(BASE + bill_shock_count × UPLIFT, MAX)` with
  `BASE = 0.05`, `UPLIFT = 0.03`, `MAX = 0.95`.
- `company/analytics/clv_three_horizon.py:580` — `hazard = latest.churn_probability`, the newest renewal
  point observable when the snapshot is taken.

At an account's **first** year-end it has accrued no bill-shock history, so `bill_shock_count = 0` and the
hazard is exactly `BASE`. This is not a floor being hit, and not a failure — 0.05 is the *correct* base
rate for an account nothing is yet known about. It is the coupler asking every account the question at the
one moment none of them can answer it.

*Free provenance check:* all 457 recovered hazards land exactly on the `0.05 + 0.03k` lattice for
k = 0…12. The bisection inversion in `recover_hazard` is therefore exact, and the recovered numbers are
demonstrably EP1's own — an independent confirmation, not an assumption.

## 5. What the graded slice IS and IS NOT evidence for

**IS evidence for:**
- The margin term alone produced whatever ranking the graded CLV had. With the hazard identical across all
  33, the tenure horizon contributed zero cross-account variation *to this measurement*.
- A genuine selection problem in the magnitude: the graded population is outcome-selected and, like for
  like within `resi`, realised **2.96x less** than the excluded-but-still-supplied population — a **lower
  bound**, since the excluded side is censored and still accruing.

**IS NOT evidence for:**
- That EP1 cannot distinguish accounts (§2 refutes it: 13 distinct hazards, 100 of 101 accounts move).
- That the tenure horizon is degenerate *in the company's actual operation*. It is degenerate only in the
  belief the coupler chose to grade.
- That 0.05 is a floor artefact. It is the base rate at zero observed shocks.
- Any level move on EP1, in either direction.

## 6. Decision: the headline gap of 2.529 should NOT be published in its current form

Recommendation, taken: **withhold `gap = 2.529` as a headline figure for EP1; keep the row as a
diagnostic.** Three independent defects compound in one number, and they do not point the same way:

1. **The belief is taken at minimum information.** Every account is graded on a CLV whose lifetime term is
   the base rate, even where 14 of the 20 still-present graded accounts have a later, better-informed
   snapshot on record (§7).
2. **The baseline is fitted on the population it grades.** The ledger's own `baseline` field says so: g0 =
   the mean realised margin *of the graded population*, a figure the company could not have formed at
   belief time. `gap > 1` therefore does not cleanly mean "less information than the mean".
3. **Truth-window bias**, already recorded in `note`: realised value spans the whole lifetime while the
   belief is a first-year snapshot, which flatters an over-estimating belief.

A single ratio carrying all three is not a statement about the company's skill, and R12 forbids treating it
as something to move. Publishing it as a headline invites exactly the reading that has already been made
three times.

## 7. Decision: the re-run was NOT worth the hour, and here is the reason

The direction offered a re-run at a commit ≥ `353fe96b8`, with a level move available "if the re-measure
genuinely puts more than one distinct hazard into the graded population".

**It structurally cannot, and that is now measured rather than assumed.** The result in §3 is computed on
the *latest* run — already at a commit past the estimator change — and the earliest-snapshot hazard is
`0.05` for 154 of 154 accounts. Re-running `tools.couple_clv` unchanged would return `distinct_hazards: 1`
again, because the belief-selection rule, not the run, produces that 1. **No level move is available on
this evidence.**

**The fix is in the coupler, not in a re-run.** `couple_clv`'s stated reason for taking the earliest
snapshot is that it "is also the only one a ceased account has — EP1 blanks the forward horizons once an
account stops settling". **That justification is empirically false for the majority:** of the 33 graded
accounts in the row, 20 are still present in the latest run, and **14 of those 20 have more than one
recoverable snapshot** (`PROS-2019-0024`: 0.05 → 0.41 → 0.08 → 0.41 → 0.41 → 0.41). The coupler is
discarding better-informed beliefs that exist on disk.

**Named follow-on (queued, not fixed on sight per SELF-INTERRUPT DISCIPLINE):** grade the LAST non-blank
snapshot rather than the first — or publish both and report the pair. That change would put genuine hazard
dispersion into the graded population and make the tenure horizon readable for the first time. It also
moves the truth-window bias (§6.3) rather than removing it, so it needs its own R15 treatment and is a
build item, not an edit to slip into this correction.

---

## Provenance and limits (R9)

- **Observed:** every figure in §1 read from the committed ledger row; every figure in §2/§3/§7 computed
  from `docs/reports/run_output_latest.json` by inverting published horizons with
  `tools.clv_gap_selection.recover_hazard`; the constants in §4 read from source.
- **Inferred:** that `bill_shock_count = 0` is the *reason* the first snapshot is `BASE`. The lattice check
  in §4 and the 154/154 result make this the only consistent reading, but no per-account
  `bill_shock_count` is published to confirm it directly.
- **Limit:** §2/§3/§7 are measured on a **different run** from the row (`8afa34ceb`); only 20 of the 33
  graded accounts persist into it. The cross-run generalisation rests on the **mechanism** in §4, which is
  a property of the code and not of any run, and not on the population coincidence.
- R12: every figure here is a diagnostic. None of it is a target.
