# A stayer pays the default, so the value rule should not price above it

**Pre-registered 2026-10-03 by the delivery seat, before any run of the change below.**

## What was found

The world has a live decline-and-stay rule (`DECLINE_A_FIX_ABOVE_THE_DEFAULT = True`,
`customer_events.renewal_outcome`). A household that stays never contracts a fix above the default
it would otherwise be on. It refuses the fix and is billed the default.

The per-decision probe (`tools/decision_probe.py`) credited every stayer with the offer, so on an
offer above the default it counted margin the world never pays. Re-scored offline with the world's
own rule on the four 2025 reference paths:

| path | value offers above default | level offers above default | value - level, old | value - level, corrected (SNR) | value - flat, old -> corrected |
|---|---|---|---|---|---|
| default | 74 / 82 | 67 | -2,668 | -1,184 (1.25) | 7,250 -> 3,663 |
| 61001 | 69 / 80 | 66 | -3,046 | -1,482 (1.69) | 8,356 -> 4,068 |
| 61002 | 68 / 78 | 59 | -2,146 | -1,019 (1.43) | 7,071 -> 3,882 |
| 61003 | 69 / 77 | 62 | -2,827 | -1,560 (1.79) | 7,979 -> 3,462 |

**Correction to earlier records, stated beside them.** Every probe figure published today
overstated margin on above-default offers:
- `SEAT_PREREG_A_PER_DECISION_COMPARISON_...`, `..._WHICH_BELIEF_...` and the B8 record;
- the "-2,146 to -3,046" headline;
- the oracle bounds.

The direction holds (the value rule's choosing still loses to a flat price at its own median) and
the size about halves. The oracle and B8 figures are re-scored when the probe re-runs with the
column.

The probe now records what a stayer pays (`stayer_pays_gbp_per_mwh`, `level_grid[*].paid`) and
scores on it.

## The company-side change

**The company does not know this rule.** Its value scorer prices a stayer at the offer, so an
above-default fix looks like more margin at some churn cost, when it is only churn cost.

This is not a constant. It is a structural fact any GB supplier knows from its own licence:
- a fix does not auto-renew (SLC 22C.2/22C.5);
- doing nothing puts the household on the default (22C.7/22C.8);
- so a household that stays pays at most the default.

Behind a new policy switch `renewal_stayer_pays_at_most_default`, the value scorer:
- prices a stayer's margin, revenue and bad debt at `min(offer, published default) - base`;
- leaves P(stay) at the offered rate.

An above-default candidate is then strictly dominated. Scored on the probe (`value_capped` rule)
with the corrected scoring.

## Predictions, written before the run

- **V1.** The value_capped rule offers above the default on at most 5 decisions per path (the
  value rule: 68-74).
- **V2.** value_capped - value > 0 on every path, between +300 and +1,500 per path.
- **V3.** value_capped - level (level at value_capped's own median, corrected scoring) is still
  negative on at least 3 of 4 paths, because the churn belief's year-level error is untouched.
- **V4.** Its magnitude is smaller than value - level's corrected figure on at least 3 of 4 paths.

## Grading

Filled in below after the runs.

## Grading, default path (the three seeded paths are filled in below when they return)

`/var/tmp/se-probe-out/probe_capped_default.json`, the probe with the stayer column, run at the
change as pre-registered. All figures include bad debt.

| | default path |
|---|---|
| value above the world's default | 69 / 82 |
| value_capped above the world's default | **59 / 82** |
| value - level (level at value's median 50.5) | -1,152 (SNR 1.21) |
| value_capped - value | **+408 (SNR 3.77)** |
| value_capped - level (level at its own median 44.3) | **-592 (SNR 0.73)** |
| value_capped - flat | +4,723 (SNR 4.84) |

- **V1 REFUTED, and the cause is mine.** The rule read `published_default_rate_gbp_per_mwh`, which
  is the published cap and is None before 2019. The 59 split as follows:
  - **32 are before the cap.** The company was told no default, so the switch could not act,
    while the world bills a decliner the published SVT series.
  - **About 17 sit at the default within GBP 0.1/MWh** (the candidate-grid snap). The world reads
    them as above and bills the default, which is the same margin.
  - **5 have the default below the base cost.** Every stayer loses money there, so pricing them
    out is the scorer working as designed.
  - **About 5 equal the value rule's offer exactly**, a path that does not reach the scorer.
    Not yet traced.
- **V2 HELD:** +408, inside +300 to +1,500, at SNR 3.77.
- **V3 HELD:** -592, still negative.
- **V4 HELD:** |-592| < |-1,152|.

So knowing the rule recovers about half of value's corrected loss to a flat price, using only the
post-2019 half of the book. The other half had no default to read.

## Grading, all four paths (v1)

| path | value_capped above default | value - level (SNR) | capped - value (SNR) | capped - level (SNR) | capped median |
|---|---|---|---|---|---|
| default | 59 / 82 | -1,152 (1.21) | +408 (3.77) | -592 (0.73) | 44.3 |
| 61001 | 55 / 80 | -1,676 (1.71) | +406 (4.22) | -872 (1.14) | 44.6 |
| 61002 | 51 / 78 | -1,041 (1.24) | +191 (1.54) | -652 (0.90) | 42.6 |
| 61003 | 51 / 77 | -1,269 (1.49) | +285 (4.20) | -650 (0.87) | 45.4 |

- **V1: refuted on 4 of 4,** for the reason given above. The pre-2019 half had no default to read.
- **V2: held on 2 of 4.** The +191 and +285 fall short of the +300 floor. The direction is positive
  on all four paths, at SNR 1.5-4.2. As registered, this is refuted on two paths.
- **V3: held on 4 of 4.** The rule that knows the default still loses to a flat price at its own
  median.
- **V4: held on 4 of 4.** That loss is 37-48% smaller than the value rule's.

## v2, pre-registered before its run

The company now knows its OWN default tariff on the day. The world passes it, as the price it
bills a household on the company's SVT:
`own_default_tariff_inc_vat_gbp_per_mwh` -> `renewal_rate_chain._stayer_default_ex_vat`. The
scorer takes that rate as a stayer's bill. Before 2019 this is the only default there is; from
2019 it is the cap.

The control path never reads it, because the chain passes it only under the policy. The churn
belief's reference is untouched, so CURRENT_POLICY moves nothing.

- **V1'.** value_capped sits above the world's default by more than GBP 0.5/MWh on at most 12
  decisions per path. That allows for the default-below-cost cases and the untraced equal-to-value
  ones.
- **V2'.** value_capped - value is larger than v1's on every path (default path: > +408).
- **V3'.** value_capped - level (its own median) is still negative on at least 3 of 4 paths,
  because the churn belief's year-level error is untouched.

## Grading v2 (own default known before the cap), all four paths

Source: `/var/tmp/se-probe-out/probe_v2_*.json`, run at the v2 code (landed 3475058ef). With bad
debt.

| path | capped above default by >0.5 | of which default<base / ==value / other | capped - value (v1 -> v2) | capped - level at its median (SNR) | capped median | best flat level | capped - best level (SNR) |
|---|---|---|---|---|---|---|---|
| default | 14 | 8 / 4 / 2 | +408 -> +433 | +599 (1.34) | 23.7 | 55 | -776 (0.70) |
| 61001 | 11 | 7 / 2 / 2 | +406 -> +619 | +1,966 (2.36) | 20.7 | 55 | -1,057 (1.05) |
| 61002 | 14 | 9 / 3 / 2 | +191 -> +202 | +1,459 (2.64) | 18.2 | 55 | -956 (0.98) |
| 61003 | 14 | 7 / 3 / 4 | +285 -> +285 | +1,289 (1.76) | 26.4 | 60 | -1,190 (1.08) |

- **V1': refuted on 3 of 4** (14, 11, 14, 14 against <=12).
  - **Above-default offers fell from 51-59 to 11-14.** What remains is mostly the default-below-cost
    case, where pricing the stayer out is the scorer working as designed (7-9 per path).
  - **2-4 per path are the value rule's offer exactly.** Those never reached the stayer term; the
    fallback is still untraced.
- **V2': held on 4 of 4, but barely on two paths** (+11 and +1). Knowing the default before 2019
  adds little: those pre-cap offers now sit at the default, and the world's churn at those prices
  was already high.
- **V3': refuted on 4 of 4,** with the sign reversed. Against a flat price at its OWN median, the
  rule that knows the default WINS: +599 to +1,966, SNR 1.3-2.6.

**That win must not be read as the choosing working.**
- **Clipping at the default drags the rule's median down** to GBP 18-26/MWh, so the comparison is
  against a flat price the rule's own clipping made low.
- **Against the best flat level it still loses,** by 776-1,190 at SNR 0.7-1.1. The best level is
  GBP 55-60, which the default also caps for any stayer.
- **But that comparison flatters flat.** The best level is chosen with hindsight, over the very
  decisions it is scored on.

The fair reading is that the choosing with the default known sits **between** a flat price at its
own median and the best flat price in hindsight. It has not yet beaten a flat rule a company could
have chosen in advance.

The next lever is the churn belief's level. The best flat level is GBP 55-60, about 2-3x the
capped rule's median. What sends the rule's choices so far below it has not been measured.
The probe now records the company's believed P(stay) at every grid offer beside the world's, so
the next run can answer that directly.
