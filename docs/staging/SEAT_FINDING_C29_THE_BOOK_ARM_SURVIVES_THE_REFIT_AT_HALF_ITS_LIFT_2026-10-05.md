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

## Addendum, 2026-10-09: the premise re-read on landed code (`the-retention-discount-concerns-evidence-is-re-read-after-aac535f08`)

The director's open row `does-a-retention-discount-offered-to-a` quotes §2 above: 32 of 60 offers,
59% of spend, GBP 1,765, at a term that gives no exit. Two things have landed since then.
`b922911b7` lets the world answer an offer at its discounted rate. `aac535f08` records that the
discount now enters the decline-or-convert rule.

**Instrument.** I re-joined the newest daemon run on disk, not a fresh one:
`docs/reports/run_output_224e4af02_20261009T171631Z.json`. Its `producing_commit` is `224e4af02`,
which has both `b922911b7` and `aac535f08` as ancestors. Its renewals run from 2016-12-31 to
2025-05-31. Each `retention_log` row joins to exactly one decision-leg event on (customer, date);
208 of 208 joined. For an offer at an SVT conversion, I recomputed the full rate as
offered / (1 − discount) and asked `position_vs_default` whether that rate would have been declined.
Since then only four commits have touched `simulation/` or `company/`, and all of them are
arrears and ledger work. Those can move a few offers through the guard's bad-debt belief, but they
do not change what kind of term an offer lands on. Script: `/var/tmp/retdisc_post.py` (scratch).

**Does `svt_conversion_event` still give P(depart) = 0? Yes.** Its `realized_churn_probability` is
0.0 on every one of the 94 offered conversions. The same holds for every unrolled `declined_fix`.
`departure_rolled_at_renewal` still takes the exit off any term whose previous segment was the SVT.

| kind of term the offer fell on | rolled? | offers | spend | share of spend | what the offer can buy |
|---|---|---|---|---|---|
| fixed-term renewal (`renewal`) | yes | 77 | GBP 2,101 | 31% | a stay: 47 stayed, 30 left despite it |
| fixed-term renewal, declined the fix even at the discount | yes | 26 | GBP 1,121 | 16% | a stay (all 26 stayed, on the SVT) |
| SVT-to-fix conversion | no | 94 | GBP 3,015 | 44% | **a conversion, in 10 of them** |
| SVT anniversary, fix declined even at the discount | no | 11 | GBP 591 | 9% | nothing |
| **all** | | **208** | **GBP 6,828** | | |

- **Offers at a term with no exit: 105 of 208 (50%), GBP 3,607 (53% of spend).** That compares
  with 32 of 60 (53%) and 59% of spend in §2. So the money share is a little lower, but the
  amount is about twice as large, because the book and the run are larger.
- **10 of those 105 now buy something.** At the full rate, those households were above their
  default by between +0.8% and +4.5% and would have declined. The discount (3%, 5% or 8%) puts them
  at or below the default, so they convert. All 10 are domestic credit accounts, and each is billed
  at the offered rate (the logged `unit_rate` equals the offer). They cost GBP 355 together. 7 of
  the 10 fall in 2018, and 3 fall in 2025 H1.
- **95 offers (GBP 3,252, 48% of spend) still buy nothing.** 84 are conversions that would have
  happened at the full rate. 11 are declines that the discount did not reach.

**Does the premise hold?** It holds in part, and the row's wording no longer matches the code.
- *"The world gives the household no exit there" still holds.* No offer at an SVT anniversary can
  prevent a departure.
- *"So the offer cannot buy anything" no longer holds.* On landed code it can buy a conversion
  from the SVT onto a fix, which is the alternative the row itself names. Here it did so in 10 of
  105 cases, about 1 in 10.
- So the director's choice is no longer "offer or don't" over a set where offering is always
  wasted. A blanket stop at SVT anniversaries would give up those 10 conversions to save GBP 3,252.
  A narrower rule would offer at an SVT anniversary only where the full-rate fix sits within the
  discount of the default, and would have kept all 10 for GBP 355. The supplier holds all of the
  facts this rule needs: its own tariff, its own fix and the published default. Whether winning
  the conversion is worth GBP 35 an account is a separate question, not answered here. A household
  on our SVT and the same household on our fix are both still ours, and this world does not yet
  weigh the two terms against each other.
- The figures in the row (32 of 60, 59%, GBP 1,765) are out of date. The current figures are 105 of
  208, 53%, GBP 3,607, of which GBP 355 buys a conversion.

Nothing here edits the direction record. The seat carries this pointer at its next orientation and
decides whether the row is re-worded or withdrawn.

## Addendum, 2026-10-10: the narrower rule, its prediction filed before any run (`an-svt-anniversary-retention-offer-only-where-the-discount-can-win-the-fix`)

**The rule.** At a term the world does not roll (the previous segment was our SVT), the guard
offers only where the full-rate fix sits above the published default and the offered rate does
not: `position_vs_default(full) > 0` and `position_vs_default(offered) <= 0`. Those are exactly
the two inequalities the world's dominance rule (`renewal_outcome`) applies, and every input is
the supplier's own: its fix, its discount tier, and the published default. Rolled terms are left
as they were. Where either position is unknown at an unrolled term, the guard makes no offer and
logs that as the reason. It is a standing-policy field, on in `current` and every arm built from
it, and off in `naive`.

**Prediction on run 224e4af02's book, written before any run carrying the rule:**
1. On the same book, the rule removes exactly the 95 offers (GBP 3,252) the 2026-10-09 table
   names as buying nothing: 84 that converted at the full rate, and 11 that the discount did not
   reach. It keeps the 10 conversions (GBP 355). This part is arithmetic, since the rule is the
   table's own split.
2. In a fresh run carrying the rule, the book drifts, because a household converting at the
   full rate is now billed more and the treasury moves. Grading bands:
   - Offers at unrolled terms: **8 to 14**, against 105.
   - Spend on those offers: **GBP 250 to 500**, against GBP 3,607.
   - Discount-bought conversions: **8 to 14**, against 10.
   - Offers at rolled terms: **within ±10 of 103**.
   - Total offers: **about 113 (103 to 125)**, against 208.
   - Total spend: **about GBP 3,580 (GBP 3,200 to 4,000)**, against GBP 6,828.
   A result outside a band refutes the claim that the rule moved only what it targets.

**Prediction 1 graded (2026-10-10 02:30 BST): held exactly.** I ran the landed function
`growth_desk.retention_offer_can_buy_anything` over every offer on run 224e4af02's book, with each
position re-read through `position_vs_default` at the full and the offered rate. It keeps the 10
unrolled conversions (GBP 354.72) and drops 95 offers: 84 conversions that the full rate already
won (GBP 2,660.43) and 11 declines that the discount did not reach (GBP 591.44), GBP 3,251.87 in
all. All 103 rolled-term offers are kept. The join instrument first reproduced the 2026-10-09
table to the penny: 208 offers, GBP 6,828.20, no row unjoined. Scratch scripts:
`/var/tmp/retdisc_post.py` and `/var/tmp/svtann_rule_on_book.py`. Prediction 2 is graded on the
run `longjob-svtann-retention-rule-run`. That run started at 01:15 BST from a worktree whose three
rule files are byte-identical to `9efdb1493`, and its output goes to `/var/tmp/svtann_run.json`.

**Prediction 2 graded (2026-10-10 02:45 BST): every band held.** Run `longjob-svtann-retention-rule-run`
ended `success` at 02:29 BST after 1h14m. Output: `/var/tmp/svtann_run.json` (scratch, not
promoted). It was joined the same way as above, and no row was left unjoined. Script:
`/var/tmp/svtann_grade_p2.py`.

| | band filed before the run | 224e4af02 | this run | verdict |
|---|---|---|---|---|
| offers at unrolled terms | 8 to 14 | 105 | **10** | held |
| spend on them | GBP 250 to 500 | GBP 3,607 | **GBP 354.84** | held |
| discount-bought conversions | 8 to 14 | 10 | **10** | held |
| offers at rolled terms | 93 to 113 | 103 | **102** | held |
| total offers | 103 to 125 | 208 | **112** | held |
| total spend | GBP 3,200 to 4,000 | GBP 6,828 | **GBP 3,797.99** | held |

- **The 10 conversions are the same 10 households on the same dates as on 224e4af02** (10 of 10
  shared by customer and date). The rule kept exactly what the money had won.
- **Both branches are reached in the run itself.** Across all 314 unrolled-term events, 10 were
  offered, 94 were withheld with `the_discount_cannot_win_the_fix` stamped on the event, and 210
  were below the guard's threshold before the rule was asked.
- Rolled-term spend rose from GBP 3,222 to GBP 3,443 on one fewer offer. That is book drift on
  the terms the rule does not touch, and it sits inside the total-spend band.
- **Caveat on the instrument.** The run's `producing_commit` reads `6a7a35721`, which is the
  worktree's base. The rule was uncommitted on top of that base when the run started. Before
  grading, I checked that the three rule files in `/var/tmp/se-svtann-run` are byte-identical to
  `9efdb1493`. The stamp alone would not show that this run carried the rule.

**What this settles.** Retention spend falls by about 44% (GBP 6,828 to GBP 3,798) and every
conversion the discount bought is kept. That answers the premise of the director's row
`does-a-retention-discount-offered-to-a` in code: the offers that bought nothing are no longer
made, and none of the offers that bought something were given up. Whether a conversion is worth
about GBP 35 an account is still the open question from the 2026-10-09 addendum. The seat should
carry the row as answered-in-code at its next orientation.
