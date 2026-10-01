**Severity:** LATENT · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** `D_opening_dd_seasonal_sizing` — Lane 0 delivery

# Under the rate-sold rule, the estimated DD opening no longer beats the first bill on year-one drift

Claim `republish-dd-opening-arms-once-the-shared-tree-holds-68e4fb4bf`.

**Premise check.** At 16:31Z the shared tree was level with origin (0 ahead, 0 behind).
`docs/reports/run_output_latest.json` was produced at `c48eb1ff6` (16:11Z). That commit descends
from `68e4fb4bf` and the run output carries `opening_dd_by_customer`. So the instrument accepted it,
and `site/data/dd_opening_arms.json` is republished from that run.

## What moved, against the 2026-09-03 cap-rule page

The figure is the matched year-one (window-0) drift: the same households, opened under both rules.

| | cap rule, 09-03 | rate-sold rule, now |
|---|---|---|
| matched households | 96 | 194 |
| estimate ends closer to zero | 80 / 96 | 123 / 194 |
| mean change in \|drift\|, estimate − flat | **−£201.93** [−257.57, −143.50] | **−£0.40** [−77.20, +109.67] |
| refused (no published rate) | 82 | 0 |

The page's earlier claim was that the estimate cut year-one drift by about £200 per household, with
a CI that excluded zero. On this run that claim no longer holds. **We cannot tell the two rules
apart on mean \|drift\|.** The estimate still ends closer to zero for most households (123 of 194),
but the mean is driven by a tail.

## Attribution: what I can and cannot say

Three things changed at once: the opening rule (cap → rate sold), the population (the 82 pre-cap
refusals now open), and the run itself (09-09 substrate → `c48eb1ff6`). I ran the one-variable cut
that this substrate allows, in one process. It splits the 194 by the month the account opened:

| cohort | n | estimate closer | mean Δ\|drift\| [95% CI] |
|---|---|---|---|
| opened before 2019-01 (newly openable) | 99 | 61 | +£31.54 [−53.60, +129.41] |
| opened 2019-01 or later (the old population) | 95 | 62 | −£33.68 [−157.94, +163.55] |

**The collapse is not population composition.** The cohort the cap rule could already open, 95
households against the old 96, also loses its significant advantage. What remains is either the
rule change or the run change. This substrate cannot separate those two. The old run output does
not carry the rate-sold openings, so the comparison would need the old run re-run on the new code,
or the reverse.

## The tail that sets the mean

These are the worst window-0 balances under the estimate. "Opening" means the monthly DD each arm
opened at.

| account | opened | flat opening → drift | estimate opening → drift |
|---|---|---|---|
| PROS-2024-0082 | 2024-03 | £711.43 → −£4,022 | £69.38 → **−£11,727** |
| PROS-2018-0002 | 2018-01 | £281.44 → −£38 | £23.85 → −£3,129 |
| PROS-2016-0098 | 2016-03 | £174.81 → −£1,296 | £31.63 → −£3,014 |
| PROS-2016-0092 | 2016-03 | £149.87 → −£1,079 | £30.28 → −£2,514 |

In each case the estimate opens at between a tenth and a fifth of the first bill. This is the same
shape as `SEAT_FINDING_THE_YEAR_ONE_SHOCK_TAIL_IS_AN_EAC_A_FRACTION_OF_THE_HOMES_USE_2026-10-01.md`:
a registry EAC that is a fraction of the home's own use. No new mechanism is proposed here. That
finding owns the cause, and this page now carries its consequence.

**A prediction, filed before the test.** If the EAC-fraction tail is repaired at the world side,
the matched mean Δ\|drift\| on the 2019+ cohort goes negative with a CI that excludes zero. If it
stays across zero after the repair, the rate-sold rule itself is the cause and this prediction is
refuted.

**The page would have published a false sentence, and is repaired in the same landing.**
`site/capabilities/index.html` rendered the paired result as "falls by … The interval excludes
zero, so this is a difference and not noise" unconditionally. On this feed that reads as "falls by
£0.40 (95% £109.67 to £77.20)", which reverses the bounds and claims significance. The renderer now
chooses one of three sentences, falls, rises or spans zero, from where the interval actually sits.
`test_the_paired_sentence_is_chosen_by_where_its_interval_sits` controls all three branches in one
test. I mutated the renderer to force the old unconditional branch, the test went red, and I
reverted the mutation. The refusal test keyed on "2019", which was this run's cause word. It now
keys on "price cap", which is the cause itself.
