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

## Attribution, 2026-10-01 evening: the rule did not do it, and the tail is a wiring gap

Claim `attribute-the-dd-opening-collapse-rule-against-run`. One process, one substrate: the run output
produced at `c48eb1ff6`, which descends from both `68e4fb4bf` and `3bf64c4e7`. Three arms over the same
bills. **Flat** is the first issued bill. **Cap** is the OLD rule: the same `opening_monthly_amount`
door with no contracted rate, so it uses the cap and 53p, as it did before `ed41ffa1e`. **Sold** is the
run's own `opening_dd_by_customer`. Only the opening rule varies.

Matched window-0 change in |drift|, with the instrument's bootstrap:

| comparison | population | n | closer | mean Δ\|drift\| [95% CI] |
|---|---|---|---|---|
| cap − flat | 2019+ (all the cap rule opens) | 95 | 60 | −£30.42 [−156.02, +166.09] |
| sold − flat | 2019+ | 95 | 62 | −£33.68 [−157.94, +163.55] |
| **sold − cap** | **2019+** | **95** | 43 | **−£3.27 [−32.79, +25.46]** |
| sold − flat | all | 194 | 123 | −£0.40 [−77.20, +109.67] |
| sold − flat | pre-2019 | 99 | 61 | +£31.54 [−53.60, +129.41] |

**The rule did not move the mean.** On this substrate the OLD cap rule collapses as well: −£30, against
−£202 on the 09-03 page. Holding the households and the bills fixed, the rule change is worth −£3.27,
and that interval sits tightly on zero. It changes the openings by a median of −£11.80 a month. The
collapse came with the run. The company's own method did not regress.

**The tail did it.** Dropping the four named accounts is not a repair, but it shows where the mean comes
from:

| comparison | population | n | mean Δ\|drift\| [95% CI] |
|---|---|---|---|
| cap − flat | 2019+ less tail | 94 | −£111.58 [−167.28, −54.73] |
| sold − flat | 2019+ less tail | 94 | −£116.01 [−170.65, −58.10] |
| sold − flat | all less tail | 190 | −£73.82 [−112.62, −32.94] |

On the 2019+ cohort a single account, PROS-2024-0082, moves the mean from −£116 to −£34. Without the
tail, both rules beat the first bill with intervals that exclude zero, and they are indistinguishable
from each other. I cannot attribute the remaining gap between −£112 here and −£202 on 09-03. It is the
substrate (09-09 → `c48eb1ff6`), and this cut holds the substrate fixed.

**The prediction above is not yet tested.** Trimming the tail is not repairing it. The prediction stands
as written, to be graded on the first run in which the repair reaches the openings.

### The tail: `3bf64c4e7` did not reach it, and why

The registry EAC the company held when each account opened, against the household's own first-year use
as billed:

| account | EAC at opening | first-year use (billed, annualised) | ratio | provider |
|---|---|---|---|---|
| PROS-2024-0082 | 2,602 kWh | 41,951 kWh | 0.06 | fabric_physics |
| PROS-2018-0002 | 1,622 kWh | 18,087 kWh | 0.09 | fabric_physics |
| PROS-2016-0098 | 2,470 kWh | 20,296 kWh | 0.12 | fabric_physics |
| PROS-2016-0092 | 2,338 kWh | 10,222 kWh | 0.23 | fabric_physics |

All four are fabric premises, which is exactly the population `3bf64c4e7` re-sets to its own trailing
reads. The openings are still sized on the drawn band: the run's cap-equivalent for PROS-2024-0082 is
£78.19, which is precisely `opening_monthly_amount` at 2,602 kWh. At its own reads it would be
£1,016.65.

**Cause: the fix writes into a copy the DD opening never reads.** `run_phase2b` rewrites
`eac_kwh` on the records in its own module-level `CUSTOMERS = live_population()` (line 231).
`run_phase4c_on_phase2b` builds the DD openings from its own `CUSTOMERS = live_population()` (line 110),
which comes from a second call. `live_population()` returns the 13 static `CUSTOMERS` records by
identity, but it builds fresh dicts for every drawn account. Two calls in one process share 13 of
244 records, and none of the 231 drawn ones, PROS-* included. So the fix reaches what `run_phase2b`
reads (the quote, EFFECTIVE_EAC_KWH, and the renewal-shock figures its commit measured). It does not
reach anything in `run_phase4c` that reads `eac_kwh` through `_get_all_customers()`: the DD opening
(line 369), and possibly the readers at lines 405 and 530, which I have not audited. The 13 shared
static accounts are the only ones the fix reaches on the phase-4c side. `tools/dd_opening_arms`'s
`_basis_and_rate_by_customer` reads a third fresh copy and has the same gap.

This is a world defect in what the company inherits, not a defect in the company's method. On the
phase-4c side the company is still handed the band drawn blind to the dwelling.

**Next, as a separate pre-registered item. The opening rule is not touched here.** Make the
registry-EAC rewrite reach the record that `run_phase4c` reads: one population object, or the rewrite
handed across explicitly. Re-run, then grade the prediction above on the 2019+ cohort. A second
prediction, filed now: after that repair, `sold − cap` on 2019+ stays inside ±£35 and spans zero,
because the rule was never the variable.
