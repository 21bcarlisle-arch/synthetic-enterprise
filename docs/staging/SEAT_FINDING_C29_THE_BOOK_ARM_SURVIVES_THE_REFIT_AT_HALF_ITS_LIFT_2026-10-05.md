**Severity:** RECORDED · **Lane:** C_customer_ops · **Epoch:** 4 · **Atom:** `C29_decisions_stop_being_lookup_tables`

# The book arm survives the refit at half its lift; the weighted guard saves a quarter of retention spend for almost nothing, but mostly by rediscovering the SVT roll

Claim `c29-book-arm-regrade-after-the-arms-retake-frees-the-runner`, worker tick 2026-10-05 14:05 BST.

## 1. The book arm, graded against the prediction filed before the run

Run: `docs/reports/run_output_7a3cdd060_20261005T115844Z.json`. It is the first run on disk whose
sha has `ae552db75` (the refit) as an ancestor; `git merge-base --is-ancestor` was checked over the
fifteen newest. `python3 -m tools.c29_engagement_ranking`:

| arm | channel ρ | estimate ρ | lift | null band (95%, 200 shuffles) | accounts |
|---|---|---|---|---|---|
| book, pre-refit (`SEAT_FINDING_C29_A_PER_ACCOUNT_…`) | 0.189 | 0.734 | 0.545 | −0.32 … +0.05 | 108 |
| **book, refitted** | **0.281** | **0.549** | **0.268** | **−0.303 … +0.015** | 108 (10 with no anniversary) |
| world, refitted, 5 anniversaries | 0.160 | 0.671 | 0.511 | (−0.163 … 0.102, earlier finding) | 125 |

**Prediction (filed before the run):** the lift falls by about a third, 0.545 → ~0.35, and stays
above the null's upper bound.

- **Above the null: held.** 0.268 against an upper bound of 0.015. The frame's refutation clause
  does not fire for the book, so the wiring may be switched on in an arm.
- **Size: refuted.** It fell by half (−51%), not a third. The world arm fell 31%. So the book lost
  more than the world did. Two things moved together: the channel ρ ROSE (0.189 → 0.281) and the
  estimate ρ fell (0.734 → 0.549). Both changes are in the book's own data, not the instrument. I
  cannot yet say which carries the gap to the world arm. The book is 108 accounts with mostly 1–4
  anniversaries, where the world arm rolls 5 per account. The channel rising is consistent with the
  refit narrowing within-channel spread, so the channel explains more of what remains.

## 2. The value-arm pair: same world, `retention_weighs_engagement` off and on

`tools/_c29_retention_engagement_arm.py`, one process per arm, full 2016–2025 window, at
`7a3cdd060`. The arm records every guard decision exactly: the offer's cost, the value with and
without the weight, and the estimate's `prior_strength`. It also records the world's own P(stay) with
and without the offer at each renewal roll. Artefacts are in `docs/reports/c29_arms/`.

| | offers | retention spend | renewal departures | total gross |
|---|---|---|---|---|
| off | 60 | £2,969.31 | 25 | £342,590.90 |
| on | 50 | £2,265.84 | 25 | £342,590.90 (identical to every digit) |

- **Retention cost saved:** £703.48 (24%), across 10 refused offers.
- **Departures added:** 0 realised. Every one of the 155 renewal rows has the same outcome in both
  arms. One roll per refusal is weak evidence, so the expected figure is the one to read:
  Σ(P(stay | offer) − P(stay | none)) over the refusals = **0.050 retentions**. The off arm's 60
  offers buy 0.851 in all. So the weighting drops 6% of what the offers buy, for 24% of their cost.
  At the two rolled refusals' own protected values (£108, £115), the expected loss is about £6
  against £703 saved.
- **`prior_strength == 0` share of the refusals: 0 of 10.** Five guard calls in the whole run rest
  on it, and none was refused. **2 of 10 rest on a different early-book shape:** an estimate of
  exactly 0.0 with `prior_strength` None. The channel rate was fitted on a 2017 book where nobody in
  that channel had yet chosen (`SYN-2016-002`, `SYN-2016-013`, £18 between them). These two are
  also the only refusals the world could have punished. Both are the small-book defect the earlier
  finding filed; the remedy still needs a sourced reason, not a picked minimum.
- `total_net` is identical too. **That is not evidence the spend is free.** `run_phase2b`'s
  `total_net` is `Σ net_margin_gbp` over the billing records, and the retention cost is booked
  only as `retention_cost_events`, netted downstream (`tools/run_frozen_baseline.py` reads it
  separately). So the £703 is a real saving that this headline cannot show.

### What the weighting is actually finding: 8 of its 10 refusals are SVT conversions, which the world gives no exit

8 of the 10 refusals (£685 of the £703) were offers at a term where the household was converting
off the SVT. At those terms the world writes `svt_conversion_event` and gives no roll: P(depart
here) = 0.0 by construction, because the SVT segment before it carries its exit hazard
(`departure_rolled_at_renewal`). An offer there cannot buy anything.

**That set is much larger than the weighting's catch:** 32 of the off arm's 60 offers (£1,764.74,
**59% of all retention spend**) go to such terms. The weighting removes 8 of them, and 24 (£1,079)
survive it. Engagement estimates split along this line: the median is 0.42 at rolled terms and 0.17
at SVT conversions. That split is expected rather than discovered. "Rolled to the default" is
almost the definition the estimate fits, so most of the weighting's value is a noisy
reconstruction of a fact the supplier holds directly: this account is on our SVT.

So the book lift survives (§1), and it is real ranking. But at the guard, the money comes mainly
from a fact the company does not need the estimate for.

## 3. Disposition

- `DecisionPolicy.retention_weighs_engagement` stays **off** on every standing policy. This is not
  because it loses. On this world it wins by about £700 for about £6. Most of that win comes from
  a cheaper rule it only partly reproduces, and switching on the costlier mechanism first would
  credit the method with the SVT fact.
- **Asked of the third side, not built on.** The world says a retention discount offered to a
  household fixing off our SVT buys nothing at that moment. Is that how the industry sees it? The
  alternative is that the offer IS what converts them, or what stops the SVT hazard from firing
  later. If the world is right, the guard should not offer at an SVT conversion at all. That is
  worth £1,765 here, 2.5× the weighting's saving, and the weighting should then be graded on the
  rolled terms only. If the world is wrong, the 59% is a fidelity defect in
  `svt_conversion_event`, and the arms above overstate the weighting. Either answer changes what
  the next arm measures, so it goes to the director before either rule is built.
- **Prediction corrected beside itself:** book lift ~0.35 was filed; 0.268 was measured. The
  direction and the null verdict held; the size did not.

Next, in order: (1) the director's read on the SVT-conversion frame; (2) re-run this pair with
the guard restricted to rolled terms, which isolates the weighting's own value; (3) the small-book
zero-estimate remedy, from a sourced reason.
