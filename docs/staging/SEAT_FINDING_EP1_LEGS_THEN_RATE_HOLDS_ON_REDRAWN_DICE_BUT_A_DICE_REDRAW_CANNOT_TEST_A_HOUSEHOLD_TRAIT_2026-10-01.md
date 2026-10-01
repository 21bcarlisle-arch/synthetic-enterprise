**Severity:** LATENT · **Lane:** B_commercial · **Epoch:** 2 · **Atom:** EP1_clv_three_horizon — Lane 0 delivery

# EP1: "legs, then rate" holds on re-drawn dice, but a dice redraw cannot test a household trait

Claim `ep1-fuel-split-rule-replicate-on-independent-run`. Pre-registration:
`records/SEAT_PREREGISTRATION_EP1_LEGS_THEN_RATE_REPLICATED_ON_REDRAWN_RENEWAL_DICE_2026-10-01.md`
(landed `aed6bf966`, before either run was read). Scripts and logs are in `/tmp/ep1r/`:
`run_floor.py` to run, `rep.py` to grade, `c1.py` for C1, and `posthoc.py`.

## Verdict

- **The licence is NOT granted.** Every prediction held on both runs, but the informativeness
  control C1 failed on both. By the rule filed first, these runs cannot license the rule.
- **EP1's company-side ranking input stays as it is.**
- **The binding blocker is now the director's.** A replication that can test the rule needs a
  different book. That is `EP17_varied_population_draw` (R13 curriculum), and
  `docs/design/curriculum/varied_population_draw_activation.json` does not exist. An NTFY with
  the recommendation was sent with this finding.

## How the population question was answered

`run_phase2b.main` has no seed argument.

- **A different cast of households:** the only route is rebinding
  `live_population._DEFAULT_BASE_SEED`, which `run_value_cycle_ab --book-seeds` does. It refuses
  any non-default seed without the director's ruling. I did not rebind it by hand.
- **A different `report_end` or policy:** this changes only the truncation or the company's
  decisions over the same households, which is less independent than the route used.
- **The route used:** the two sanctioned noise-floor keys re-drawn for every account on the
  default book. These are `churn_roll` and `elasticity`, through `resolve_redraw_target`. Floor
  seeds were 101 and 202. Both patches reached their subjects: 113–124 calls per key were
  re-drawn, over about 70 accounts.

## Results

C0 holds. Over the discovery run, `rep.py` reproduces the discovery sample exactly: 298 rows,
+0.131 [+0.069, +0.211], and M2 ratios 0.24 and 1.01. So the grade does not need the published
run output.

| | Prediction | Floor 101 | Floor 202 |
|---|---|---|---|
| C1 | ≥ 25% of shared accounts change their last-settlement month | **16% (12/74). FAILED** | **11% (9/81). FAILED** |
| R1 | LEX(L, I1) − I1 > 0, CI excludes 0, point in [+0.05, +0.25] | +0.152 [+0.089, +0.228]. Held | +0.165 [+0.098, +0.248]. Held |
| R2 | LEX − L: CI contains 0, \|point\| < 0.08 | +0.015 [−0.074, +0.106]. Held | −0.005 [−0.098, +0.092]. Held |
| R3 | L − I1 > 0 | +0.140 [+0.018, +0.267]. Held | +0.170 [+0.031, +0.314]. Held |
| R4 | Single-fuel IQR ratio < 0.5; dual-fuel in [0.7, 1.4] | 0.31 and 0.85. Held | 0.35 and 0.90. Held |

Graded rows were 304 (89 accounts) and 322 (97 accounts). Of each run's rows, 16% and 17% are
(account, cutoff) pairs absent from the discovery sample.

## Why C1 failed, and why that is the result rather than bad luck

1. **The leg count differed on 0 shared accounts in either run.** L is a household trait: it is
   fixed by the dwelling and the fuels it takes, not by any roll. Re-drawing renewal dice and
   price sensitivity therefore cannot test whether L's ranking power is a property of *these*
   households. That was the question.
2. **Exits barely move.** About 115 renewal rolls were re-drawn and only 9–12 exit months moved.
   One plausible contributor is the world-lane finding landed at `9d6ad4551`: about 65% of
   fixed-term ends are passive and get no departure roll at all. Many re-drawn rolls cannot
   change an outcome, and a survivor's last settlement is the run's end in every draw. **If the
   world lane adds that roll, re-run this:** it would move the realisation much more.

## Post hoc (NOT pre-registered)

I restricted the grade to the floor runs' rows that were absent from the discovery sample. These
are 48 and 55 rows, mostly accounts the campaign won differently.

| | LEX − I1 |
|---|---|
| Floor 101 | +0.102 [+0.000, +0.375] |
| Floor 202 | +0.145 [−0.009, +0.473] |

The direction agrees, but at about 20 accounts each the CIs reach 0, so this settles nothing.

## What this changes

- Nothing company-side.
- **Recommendation (sent to the director):** authorise two book seeds for EP17 as a measurement
  run only, with the published run staying on the default book. Re-run `/tmp/ep1r/rep.py` on each
  book under the same R1–R4, with C1 re-keyed to the property that matters: the share of graded
  accounts that are different households.
- **When that ruling arrives,** `book_member` in `tools/run_value_cycle_ab.py` is the door. It
  already rebinds the seed before import and re-draws the churn roll at the same seed.
