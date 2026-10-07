# The DD-opening cohort split drops 60 accounts, and the published comparison's substrate no longer exists

**Severity:** LATENT · **Lane:** D_billing_metering · **Epoch:** 3 · **Atom:** `D_opening_dd_seasonal_sizing`

*Worker, 2026-10-07. Found while grading the atom's own predictions for its L1 → L2 move. The move
rests on the whole-book matched figure, which neither defect below touches.*

## What was measured

`tools/dd_opening_arms.py` re-run at origin `1058f5dd2` on three substrates:

| substrate | DD households matched | year-one change in \|drift\|, estimate − first bill | closer to square (est / bill) | peak held credit, bill → estimate | cap cohort (n, verdict) |
|---|---|---|---|---|---|
| `run_output_registry_eac_reaches_4c.json` (published 2026-10-01; sha `69861bd6`) | 194 | −£129.79 [−182.90, −72.42] | 141 / 53 | £3,672 → £5,566 | 95, held |
| `run_output_latest.json` at origin (run `998814330`, sha `ec86d4ef`) | 129 | −£84.46 [−154.30, +0.75] | 92 / 37 | £3,992 → £4,902 | 18, refuted |
| today's untracked `run_output_f07af3845_20261007T063005Z.json` | 129 | −£146.59 [−220.33, −57.91] | 98 / 31 | £3,613 → £5,039 | 18, refuted |

Unestimated accounts are 0 on all three.

## Defect 1 — the published comparison cites a file that is not on disk

`site/data/dd_opening_arms.json` and `docs/reports/dd_opening_arms.json` name
`docs/reports/run_output_registry_eac_reaches_4c.json` as their substrate. It is untracked, and it no
longer exists in the shared tree or under `/var/tmp`. So the page's figures cannot be reproduced. It
was not republished in this commit because of defect 2: republishing would put a "refuted" verdict on
the page that rests on an instrument-selected subset.

## Defect 2 — the cap-cohort split counts only accounts in a fresh population draw

`window0_matched_by_opening_cohort` keeps an account only if it has a basis row. Basis rows come from
`live_population() + successor_supply_points()`, drawn fresh in the instrument's own process
(`tools/dd_opening_arms.py`, `run()`). On both 129-household runs, **60 accounts are
`not_in_population`** (it was 2 on 2026-10-01). The cap cohort shrinks from 95 to 18, and the filed
2026-10-01 prediction now reads "refuted" over those 18, with an interval of [−161.18, +492.27].

That verdict is about which accounts the instrument could place, not about the opening rule.
Explanations, ranked by the evidence:

1. **The run's population is no longer the one a fresh draw produces.** Most likely. 5803d08c3
   already found the same shape for registry EAC: in-process records differ from a fresh draw. That
   the same holds for which accounts exist at all has not been tested.
2. The successor book grew and `successor_supply_points()` doesn't see the new accounts. Not tested.
3. The rule genuinely doesn't beat the first bill for cap-era openings. **Can't tell** at n = 18
   with an interval spanning ±£300.

## Recommendation

Read each account's opening date from the run output itself (its first bill's `period_start` is
held by both parties), not from a fresh draw. Then republish both artefacts from a TRACKED substrate,
and re-grade the 2026-10-01 prediction. The control is one partition: the two cohorts' n must sum to the
matched n. Today 65 + 18 = 83 against 129.
