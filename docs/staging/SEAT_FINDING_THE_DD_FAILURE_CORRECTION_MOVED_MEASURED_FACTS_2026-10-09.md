**Severity:** LATENT · **Lane:** W2_customer_generator · **Epoch:** unassigned · **Atom:** `unminted`

# The DD failure correction moved measured facts, and the W2_11 harness was pinned rather than re-keyed

## What changed in the world

- `simulation/arrears_engine._DD_FAILURE_PROB`: the LOW tier now reads the register's
  `dd_return_rate_first_presentation` (0.0087). MODERATE and HIGH keep their old ratios to LOW (4x
  and 35/3x), which are still unsourced. The tiers were 3% / 12% / 35% and are now 0.87% / 3.48% /
  10.15%.
- `simulation/payment_behaviour_source.later_settlement_date`: a returned Direct Debit is now
  re-presented. It is collected 14 days after its due date with probability
  `dd_representation_success_share` (0.46), drawn from its own substream (`dd_representation`). The
  bill's record stays `failed`. A bill that is not cured draws exactly the later settlement it drew
  before.

## Facts re-keyed (shape kept)

| Test | Old fact | New fact |
|---|---|---|
| `tests/simulation/test_debt_objection.py::test_a_live_run_cures_some_unpaid_bills_and_leaves_others_unpaid` | every cure lands after day 28 | every cure is either the re-presentation (day 14, DD only) or lands after day 28, and both kinds occur |
| `tests/simulation/test_payment_behaviour_source_later_settlement.py::test_every_branch_is_taken_at_the_published_shares_and_dated_at_its_window_end` | three branches (3 months / 22 months / never) | four branches (re-presented at s, then each of the old three at (1 - s) times its old share). The sample grows from 6000 to 24000, because HIGH now fails 10.15% and the old sample fell under the test's own floor |
| same file, `test_the_cited_rates_and_windows_are_ofgems` | `REPRESENTATION_SUCCESS_SHARE is None` | equals the register's toggle |

## Figures re-pinned (`tests/background/test_live_payment_triad.py::test_q3_EVERY_PUBLISHED_FIGURE_IS_UNCHANGED_BY_THE_NEW_LEGS`)

| Figure | Old | New |
|---|---|---|
| detection | 0.009375 | 0.0192307692 |
| detection latency | 1.549839 | 1.717391 |
| belief | 0.0666666667 | 0.0615384615 |
| population mix | 0.1066666667 | 0.0533333333 |
| ageing | 0.1629183071 | 0.3857259762 |
| ageing, later settlement off | 0.0720759646 | 0.1168776875 |

The test reproduces the old figures exactly when the old tiers are restored and re-presentation is
switched off. A new block in the test holds that.

Re-presentation on its own moves only the ageing figure. At the new tiers, ageing is 0.1427 without
re-presentation and 0.3857 with it.

## The W2_11 harness: pinned, not re-keyed. This decision needs a reader

At the world's new level, 52 tests in `tests/tools/test_couple_w2_11_d5.py` went red. The harness
books are 300-400 accounts, and the corrected level leaves them about 3.4x fewer failures. Many of
the reds are the harness's own anti-vacuity guards firing, for example "the ageing numerator is
EMPTY", "not one dimension moved over the sweep" and "a near-identity permutation". These are not
facts that changed: the tests' populations thinned out or vanished.

The harness measures the company's detection instrument. Its population is declared scaffolding
(`_STRESS_MIX`, "exists only to generate a population with a real mixture of ... DD-failed cases").
So its book now draws at a declared table of its own, `HARNESS_BOOK_DD_FAILURE_PROB`, set to the
pre-correction 3/12/35%. The draw goes through `generate_payment_event(..., dd_failure_prob=...)`,
whose None default is the world's table. With the pin in place no harness fact moves.

The alternative was to re-key about 52 facts. That would also have meant raising n by about 3.4x to
restore the tests' power, and the file already takes about 30 minutes. This was not chosen. The
pre-correction route did let the harness follow the world.

**What is not established:** whether any published W2_11 figure is read anywhere as a statement
about how often the world's households fail. If one is, the pin makes that reading wrong, and the
figure should carry the harness's own failure density as its basis.

## Not changed, and still named

- Every domestic credit method (DD, standing order, card, standard credit) fails at the one
  DD-derived tier. Only a DD is re-presented.
- The billing-ledger path (`arrears_engine._resolve_bills`, `tools/generate_billing_ledger.py`,
  `dd_collection_book`) reads the new first-presentation tiers but has no re-presentation, so it
  overstates failures there by about 1/(1 - 0.46).
- A re-presentation collection crosses as `ARREARS_REPAYMENT` in the live triad, not as a DD
  collection.
- `simulation/payment_timing.py` keeps its own copy of 3/12/35% (`_DD_FAILURE_PROBABILITY`). This
  is a second implementation, not migrated here.

## Re-reading the arrears like-for-like on origin (pre-registered 2026-10-09T07:30Z, before any run)

The director's hold on the 3,100 settlement raise and the 400-founder run has two halves. The
departure half is met (c38c97622). The arrears half was "about 2x once matched" (32acb3ea1), but it
was read on a world whose lowest DD tier failed 3% a month. This re-reads it on origin after
54dbd5650 (this correction), c9fd63f82 (voids) and d00cf9dc2 (headcount given dwelling size).

**What is measured.** At each 2019 quarter end: the share of domestic electricity accounts billed
in that month that hold a bill unpaid for more than 91 days. That covers a failed bill not yet
settled, and a bill paid more than 91 days late but not yet paid. It is read from the payment
triad's truth records, by the same rule as `debt_objection.WorldDebtBook` but at 91 days. The
denominator includes prepayment accounts, because Ofgem's does.

**Comparator, unchanged.** Ofgem Q4 2019: arrears 2.45% plus debt on an arrangement 2.6%, giving
**5.1%** for electricity. The world's arrangements do not shrink the sum, so the sum is the
like-for-like figure.

**Run.** Default seed, 80 founders, `run_phase2b(report_end="2019-12-31")`. Script:
`/var/tmp/arrears_like_for_like.py`.

**Predictions.**
- P1, the instrument. At 54dbd5650^ (before the correction) this script reads the 2019 electricity
  quarter ends within 2 points of 54dbd5650's own 8.7 / 9.6 / 11.6 / 10.2%. If it does not, my
  matching is not the commit's, and both readings are reported on this instrument.
- P2, the world. On origin, every 2019 electricity quarter end reads at most 3%. Pooled over the
  four quarter ends it reads at most 2%, a ratio to 5.1% of 0.4 or less. Two things lower it from
  54dbd5650's 0.0 / 1.2 / 0.0 / 1.1%: the triad no longer bills the named household for occupier
  debt (c9fd63f82), and a smaller household pays a smaller bill (d00cf9dc2). The second does not
  move a count of unpaid bills, so I expect little movement overall.

**Criterion, fixed now.** The arrears half is **MET** if 5.1% lies inside the Wilson 95% interval
of the pooled 2019 electricity reading. That pooled n counts each account once per quarter end. It
overstates independence, so the interval is too narrow, and Q4 2019 alone is reported beside it.
It is **NOT MET, HIGH** if the interval lies wholly above 5.1%, and **NOT MET, LOW** if it lies
wholly below. A world far below the comparator is as much a like-for-like gap as one 2x above it,
only in the other direction.

### Result (2026-10-09T08:05Z): NOT MET, HIGH, about 2.2x. Both predictions were refuted

Electricity accounts with a bill unpaid more than 91 days at the quarter end. Same instrument, same
default seed, 80 founders, `report_end` 2019-12-31. Origin is 8f6237b6f and the control is
54dbd5650^ (7d5259c7b).

| quarter end | before the correction (54dbd5650^) | origin |
|---|---|---|
| 2019-03-31 | 33/90 = 36.7% | 9/89 = 10.1% |
| 2019-06-30 | 35/94 = 37.2% | 10/93 = 10.8% |
| 2019-09-30 | 36/94 = 38.3% | 11/93 = 11.8% |
| 2019-12-31 | 39/96 = 40.6% (31-51%) | 11/95 = 11.6% (6.6-19.6%) |
| **2019 pooled** | **143/374 = 38.2% (33-43%)** | **41/370 = 11.1% (8.3-14.7%)** |

Brackets are Wilson 95% intervals. The pooled n counts an account once per quarter end, so its
interval is too narrow.

- **Against 5.1%:** the pooled interval on origin lies wholly above the comparator. By the
  criterion filed above, the arrears half of the hold is **NOT MET, HIGH**. The ratio is **2.2x**
  pooled and 2.3x at Q4 2019. The earlier gap was "about 2x" (32acb3ea1).
- **P1 refuted: the instrument is not the one 54dbd5650 used.** Before the correction this
  instrument reads 37-41%, not the commit's 8.7 / 9.6 / 11.6 / 10.2%. So the "~10%" in 32acb3ea1,
  and 54dbd5650's "10% -> about 1%", were read on a different "ledger" instrument, and I could not
  find or reproduce it. On the triad's truth the correction moved the stock 38% -> 11%. That is a
  factor of 3.5, in line with the factor of about 3.4 by which it cut failures. On this instrument
  the pre-correction gap was 7.5x, not 2x. **The two "about 2x" figures are on different
  instruments and must not be read as "unchanged".**
- **P2 refuted:** I predicted at most 3% at every quarter end and at most 2% pooled. The reading is
  10-12%.
- **The stock grows with the book's age.** Origin reads 2.3% (Q1 2017), then 3.3% (Q1 2018), then
  10.1% (Q1 2019), so a 2025 reading would be higher again. Gas pooled 2019 is 7/165 = 4.2%
  (2.1-8.5%).

**What holds the stock up (origin, Q4 2019, the 11 accounts):**
- 10 of the 11 hold a bill the world **never** settles (`later_settlement_date` returns None),
  while the account stays on supply and is billed.
- Only 3 of the 11 are behind because of a bill older than 22 months. Wiring the unwired
  `q3_debt_repaid_after_22_months_share` (0.15 a year; no `.py` reads it) could at most remove
  those 3, which leaves 8/95 = 8.4%. **It does not close the gap.**
- The other 8 owe a bill between 91 days and 22 months old. That is the body of
  `LATER_SETTLEMENT_REPAID_SHARE = 0.5` (only half of failed bills are ever repaid, 70% of those
  within 3 months). It is read at its floor from Ofgem IA July 2016 §1.39. That cohort is
  **customers blocked from switching by debt**, a selected population, and here it is applied to
  every failed domestic bill.

**Explanations, ranked by the evidence:**
1. **Selection in the repayment share.** The 50% is the debt-blocked switchers' share, applied to
   every first failure. Evidence: 8 of 11 are inside its window, and the stock tracks failures by
   the factor the tiers moved. This is the next place to look, knowledge first. It needs a
   published repayment curve for an ordinary failed domestic bill, or a practitioner's answer.
2. **Gaps 4 and 7 of the same module** (each bill is drawn alone, and leavers repay at the
   stayer's rate). They push in opposite directions; their size is not measured.
3. **The definition.** Is a debt the supplier never collects, from a customer still on supply,
   in Ofgem's count until it is written off? The triad says yes, matching Ofgem's own words. The
   unknown instrument behind 54dbd5650 evidently says no. **This is a practitioner question**, and
   it decides which instrument the hold is graded on.
4. **Sample size.** Small, but the pooled interval excludes 5.1%, and Q4 2019 alone sits at 2.3x.

**Consequence.** The 3,100 settlement raise stays held. It is not filed as a continuation, because
only the departure half is met. 54dbd5650's commit message ("falls from about 10% to about 1%")
reads as the world's arrears level. On the triad's truth it is 38% -> 11%, and that correction
belongs beside the claim. Scripts: `/var/tmp/arrears_like_for_like.py`,
`/var/tmp/arrears_slice.py`. Outputs: `/var/tmp/arrears_lfl_{now,pre}.json`.
