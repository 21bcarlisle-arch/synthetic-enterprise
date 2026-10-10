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

## The repayment share, knowledge first, and the like-for-like at the shipped 400-founder book

### What the published record holds (searched 2026-10-09)

- **Definition: ESTABLISHED, and already in the knowledge layer.** Ofgem's "in arrears" is quoted in
  `docs/market_research/gb_domestic_bill_payment_failure_and_arrears_prevalence.md` §(d): "not paid
  a bill for longer than 91 days (13 weeks), and there is no formal arrangement to repay the debt.
  It excludes any charges for subsequent consumption." It names no write-off exclusion, so a debt
  the supplier never collects, from a customer still on supply, stays in the count. The triad
  instrument follows that wording. **Explanation 3 above is answered in print, and no director
  concern is needed for it.** Whether suppliers *report* a written-off stayer's balance is still a
  practitioner question, and it is filed below as a named gap.
- **Curve for an ordinary failed bill: NOT ESTABLISHED. This is a named gap.** The following were
  read and none gives a cure curve, or even a single repaid share, for an ordinary failed domestic
  bill:
  - Ofgem's debt and arrears indicators (stocks only).
  - The Social Obligations Reporting template. It collects arrangement entries and breaks (Q3.1 to
    Q3.27), but no cure flow is published
    (`domestic_repayment_plan_take_up_and_keep_rates.md`).
  - Ofgem, *Consumers' experiences of debt and affordability support* (Sep 2024). It is
    qualitative case studies; read in full with `pdftotext`.
  - The 2023 and 2024 debt-related-costs papers, Appendix 2.
  - Energy UK, *Energy debt: Everyone pays* (Feb 2026). It gives recovery rates of 60/56/38% for
    debt under 12 months, but the construction is undisclosed.
  - StepChange (2019 and 2023 responses) and Citizens Advice press material. These cover advice
    clients, a selected population.
  - No DESNZ series was found.

  The one disaggregated real figure is Centrica ARA 2025 Note 17
  (`dd_failure_basis_and_live_arrears_provision_rates.md` C6). It gives the provision on live UK
  residential balances over 90 days old: **DD 7.4%, pay-on-receipt 50.3%**. That is an
  expected-LOSS rate on a balance, one supplier, and it is not a cure curve, so it does not
  replace the constant. It does bound the constant's direction. The world never collects 50% of a
  failed DD bill, while Centrica expects to lose about 7% of its DD balances that are already
  past 90 days. **`LATER_SETTLEMENT_REPAID_SHARE` stays 0.5, and is now marked in code as the
  debt-blocked cohort's share, applied to every failed bill for want of the ordinary one (gap 8).**

### Pre-registration (2026-10-09T15:24Z, written before the run was launched)

**Run.** The same script `/var/tmp/arrears_like_for_like.py`, the same default seed, and the same
2019 quarter-end instrument as the 80-founder reading above. It runs at origin d72c196b3, which
carries `FOUNDER_BOOK.yaml` `founder_accounts: 400` (ad0afe7b3). Worktree:
`/var/tmp/wt_arrears400`. Output: `/var/tmp/arrears_lfl_400.json`.

**Prediction P3.** Founders draw their failures and cures from the same per-account mechanics, so
the per-account stock does not depend on the book's size. It does depend on its age, and 400
founders makes the 2019 book older on average than the 80-founder book. Pooled 2019 electricity
reads **between 9% and 15%**. Its Wilson interval lies wholly above 5.1%, so the verdict is
**NOT MET, HIGH**, at a ratio between 1.8x and 2.9x. The interval is about half as wide as at 80
founders.

**Criterion.** Unchanged from above: met if 5.1% lies inside the pooled Wilson 95% interval.

### Result (2026-10-09T16:05Z): NOT MET, HIGH, 1.67x. P3 refuted on the low side

The run is `longjob-arrears-lfl-400`, at origin d72c196b3 with 400 founders, the default seed and a
`report_end` of 2019-12-31. It took 1,215 s. Output: `/var/tmp/arrears_lfl_400.json`.

**The instrument, corrected first.** The script's own `fuel_of` matches no account id in either
run (ids end in `g`, e.g. `ACC-C1g`), so its `fuel: electricity` rows hold every account and its
gas rows are empty. The figures filed above came from splitting on the `g` suffix (the
`arrears_slice.py` rule). Re-split from each run's `raw` by that rule, the 80-founder output
reproduces the filed figures exactly: 41/370 electricity and 7/165 gas. So the table below is on
the same instrument as the 80-founder table.

| quarter end | 80 founders (filed above) | 400 founders, shipped |
|---|---|---|
| 2019-03-31 | 9/89 = 10.1% | 23/303 = 7.6% |
| 2019-06-30 | 10/93 = 10.8% | 23/295 = 7.8% |
| 2019-09-30 | 11/93 = 11.8% | 24/283 = 8.5% |
| 2019-12-31 | 11/95 = 11.6% | 28/272 = 10.3% (7.2-14.5%) |
| **2019 pooled, electricity** | **41/370 = 11.1% (8.3-14.7%)** | **98/1153 = 8.5% (7.0-10.3%)** |
| 2019 pooled, gas | 7/165 = 4.2% | 16/202 = 7.9% (4.9-12.5%) |

- **Against 5.1%:** the pooled interval lies wholly above it, so the verdict is **NOT MET, HIGH**,
  at **1.67x** pooled and 2.0x at Q4 2019. The arrears half of the hold on the 3,100 settlement
  raise is still not met.
- **P3 refuted.** I predicted 9-15% and 1.8-2.9x. The reading is 8.5% and 1.67x, below both lower
  bounds. The interval-width half held: 3.3 points against 6.4.
- **I cannot yet say why 400 founders reads lower than 80.** Two things differ: the book's
  composition and the sample. The pooled intervals overlap (7.0-10.3 against 8.3-14.7), so this
  may be noise. The book-age argument I filed predicted the opposite direction. The stock still
  grows with the book's age inside the run: 3.3% at Q1 2017, 5.5% at Q1 2018, 7.7% at Q1 2019 and
  9.9% at Q4 2019, all accounts.
- **Gas** now reads 1.55x, against 0.83x at 80 founders, on 202 account-quarters. That is too
  small to read as a change.

**Where this leaves W2_38.** Both of the item's asks have an answer.

- **The definition** is settled in print (Ofgem, quoted above). The triad instrument follows it.
  No director concern was raised.
- **The curve** is a named gap: gap 8, SELECTION, now in the module. The 2.2x gap is now 1.67x
  at the shipped book. The leading suspect is still the never-repaid half, which is
  the debt-blocked cohort's share applied to every failed bill. The only published bound, Centrica's
  7.4% provision on live DD balances over 90 days old, says that share overstates a DD
  household's loss. The next step needs either Ofgem's unpublished SOR flows or a practitioner's
  answer to one question: *of ordinary failed domestic bills, by payment method, what share is
  eventually collected while the customer stays on supply?* That question is now in
  `for_the_director` with a recommendation.

## The never-repaid share by payment method, at the aged balance (enacting the-world-s-arrears-read-1-67x)

### Pre-registration (2026-10-09, written before any code changed)

**Change.** `later_settlement_date` stops reading the debt-blocked cohort's 0.5 for every failed
bill. The never-repaid share becomes a share by payment method, from Centrica ARA 2025 Note 17's
provision on live UK residential balances over 90 days old: **Direct Debit 7.4%**, and
**pay-on-receipt 50.3%**, which covers standard credit, standing order and card. The world classes
standing order and card as standard credit, and so does Centrica's pay-on-receipt row. Prepayment
has no Centrica row and keeps the Ofgem cohort's 0.5. The repaid remainder keeps Ofgem's 70/30
split between the 3-month and 22-month windows. The draw `u` is unchanged, so for DD the mapping is
deterministic. Of the old never-repaid bills, 29.6% become 3-month, 55.6% become 22-month and 14.8%
stay never. Every old 22-month bill becomes a 3-month bill.

**Where it applies.** Centrica's figure counts a provision on balances already more than 90 days
past invoice. Every failed bill in the world that is not cured on re-presentation (day 14) settles
no earlier than its due date plus 28 days plus 3 months, about day 119. **So every bill that takes
the share has already reached 90 days unpaid**, and applying the share at that draw is the same
as applying it at the 90-day point. No bill is charged the share at the moment it fails.

**Prediction P4.** I re-mapped each bill in `/var/tmp/arrears_lfl_400.json` (the 400-founder run,
d72c196b3) through the rule above, as an expected value per account (`/tmp/predict_nr.py`). The
expected pooled 2019 electricity reading falls from 98/1153 = 8.5% to **66.9/1153 = 5.8%**, a
ratio of **1.14x**. The direction is **down**. Of the 79 DD accounts in the stock, about 48
remain. The pay-on-receipt accounts (19) are unchanged. Debt status feeds renewal and objection
decisions, so the re-run's book will not be the same accounts. I therefore pre-register a band:
pooled **5.0-6.8%**, ratio **1.0-1.33x**. Most likely verdict: **MET** (5.1% inside the pooled
Wilson interval). It is NOT MET, HIGH if the reading is about 6.6% or more.

**Run.** Same script, default seed, `report_end` 2019-12-31, 400 founders (`FOUNDER_BOOK.yaml`), and
the same 'g'-suffix fuel split. It runs at origin with this change, through `launch_long_job`.

### Result (2026-10-09T18:01Z): MET, 0.85x. P4 refuted on the low side

The run is `longjob-arrears-lfl-400-never-repaid-by-method`, at origin 63f429536 plus this change,
with 400 founders, the default seed, a `report_end` of 2019-12-31 and the 'g'-suffix split. Output:
`/var/tmp/arrears_lfl_400_nr.json`. The denominators match the 1.67x run exactly, so this is the
same book.

| quarter end | 400 founders, flat 0.5 (1.67x run) | 400 founders, share by method |
|---|---|---|
| 2019-03-31 | 23/303 = 7.6% | 12/303 = 4.0% |
| 2019-06-30 | 23/295 = 7.8% | 10/295 = 3.4% |
| 2019-09-30 | 24/283 = 8.5% | 12/283 = 4.2% |
| 2019-12-31 | 28/272 = 10.3% | 16/272 = 5.9% (3.7-9.3%) |
| **2019 pooled, electricity** | **98/1153 = 8.5% (7.0-10.3%)** | **50/1153 = 4.3% (3.3-5.7%)** |
| 2019 pooled, gas | 16/202 = 7.9% | 8/202 = 4.0% (2.0-7.6%) |

- **Against 5.1%:** 5.1% lies inside the pooled Wilson interval, so the verdict is **MET**, at
  **0.85x** pooled. Q4 2019 alone reads 1.16x and its interval also contains 5.1%. **The arrears
  half of the director's hold on the 3,100 settlement raise is met on this instrument.** The
  departure half was already met (c38c97622).
- **P4 refuted, low.** I predicted 5.0-6.8% (point 5.8%, 1.14x). The reading is 4.3%. The
  direction held. The never-repaid DD bills fell from 37 to 3, against 5.5 expected. The DD stock
  fell from 79 to 35 account-quarters, against about 48 expected. The 4 `standard_credit`
  account-quarters left the stock. The pay-on-receipt stock (standing order and card, 15) did not
  move, as predicted. The shortfall against the expected value sits in where this book's fixed
  draws fell. It is one seed, so whether the world lands below or at 5.1% on average is **not
  established**. A second seed would settle it.
- **What still leans high, unchanged:** the provision is a stock rate read as a flow share (it
  overstates never-repaid), and gaps 2, 4 and 7. **What now leans low:** nothing new. A reading
  below 5.1% on more seeds would point at those gaps being smaller than the provision's slack, or
  at the 22-month dating.
- **Controls:** `test_the_never_repaid_share_is_one_suppliers_aged_balance_provision_by_method`
  and the re-keyed partition test. Each reds under the matching mutation: a flat 0.5 reds the DD
  partition, and the DD share for every method reds the card leg. A flat 0.5 is equivalent on the
  card leg (0.503). `test_q3` re-pinned: only ageing moves (0.3857 -> 0.3516), and a flat 0.5
  reproduces it exactly. The `W2_11` harness (623 tests) does not move.
- The three reds in `test_a_vacated_home_stands_void_for_its_tenure.py` and
  `test_the_company_ledger_bills_the_months_revenue.py` are red at origin 63f429536 without this
  change too (run in a clean worktree). They are not this change.

### Addendum (2026-10-10, worker): the two-seed re-take, written before it runs

**The grader is tracked.** `tools/grade_world_debt_against_ofgem.py` is the `/var/tmp` capture
script plus `arrears_slice.py`, and it counts the same things. It reproduces both readings above
exactly from their captures: 98/1153 = 8.5%, NOT MET, HIGH; and 50/1153 = 4.3% (3.3-5.7%), MET.
Its control is `tests/tools/test_grade_world_debt_against_ofgem.py`. Three mutations each red it:
admitting a bill paid inside 91 days, dropping the matched denominator, and a grader that never
says MET. The tool's own focus item, `the-arrears-like-for-like-is-a-tracked-tool`, was refused
at draw time by a FALSE hold. The holder is worktree `.claude/worktrees/agent-a5cc99fa24f34feed`,
owned by pid 2197437: a worker seat started 14 days ago that idles at bring-up. Its HEAD is
a52651e29 (2026-10-05). Its only work is an untracked copy of `debt_and_collections.md` from
2026-10-05 03:39, written before the 10-09 result existed. It is not the tool. This lane built the
tool, because this item cannot move without it.

**A new reading, from the same two captures.** No prepayment account is behind in either stock:
0 of 98 and 0 of 50, against 87 prepayment accounts among the run's 667. So the 0.30-0.88 toggle
moves only credit accounts on this book. That fits PPM debt (P4 in `debt_and_collections.md` §7)
being absent from the world.

**"Two seeds besides the default" has two meanings, and one is not ours to run.**
- **A book seed** draws a different cast of households. That is `EP17_varied_population_draw`,
  which is curriculum and the director's alone. `tools/book_seed_authorisation.py` refuses it
  until `docs/design/curriculum/varied_population_draw_activation.json` exists, and it does not.
- **A payment-dice seed** keeps the cast, weather and prices, and re-draws only each bill's
  outcome. That is the stream `simulation/arrears_engine.bill_substream(base_seed, customer_id,
  period_end, ...)`, rebound the way `run_value_cycle_ab.noise_floor` rebinds the elasticity and
  churn-roll draws. The default run does not move. **Recommended, and it needs no ruling:** it
  answers "is 4.3% this book's dice or this book?", and that is the question that decides whether
  the MET can carry the re-takes. A book-seed spread would also need the director's EP17 record.
- **Correction, same day.** The payment draws the triad records come from
  `simulation/payment_behaviour_source`, not from `arrears_engine.bill_substream`. Every per-bill
  draw there goes through `_period_substream`: the outcome, its reason, a DD re-presentation and a
  later settlement. The household's method uses `_substream` directly. So `capture OUT END
  DICE_SEED` now salts `_period_substream` alone (`dice_seeded`). It refuses if the salt reached
  no draw. Its control reds on a no-op salt and on a salt that leaks onto the method.
- **The launch:** `python3 -m tools.grade_world_debt_against_ofgem capture OUT 2019-12-31 <seed>`,
  seeds 1 and 2, serially, through `launch_long_job`. Then `grade` the three captures together.
  It waits for `/var/tmp/m_scale.py` to leave the box. That file was still there at 2026-10-10,
  with no process running it.

**Prediction P5, filed before any second seed is run (payment-dice seeds, same 400-founder book,
`report_end` 2019-12-31):**
- Each new seed reads **3.0-7.0%**, 2019 pooled electricity. The default's 4.3% sits low among
  them, because P4 expected 5.8% from this book's own bills and the dice fell short of it.
- Pooled over the three seeds (n about 3,459): **4.2-5.8%**, point **4.9%**, ratio **0.82-1.14x**.
  Verdict **MET** (about 60%). Otherwise **NOT MET, LOW** (about 35%). NOT MET, HIGH is unlikely.
- **Prepayment share of the accounts behind: 0** on every seed. One prepayment account behind on
  any seed refutes this. It would mean the world can put a PPM account behind 91 days, and the
  reading above would then be a property of this seed's dice.

**In flight (2026-10-10, worker).** `/var/tmp/m_scale.py` has left the box. Dice seeds 1 and 2
run serially, at origin 820a2f31b, in one unit, `longjob-arrears-dice-seeds-1-2`
(`/var/tmp/dice_seeds_run.sh`). Admission refused it beside the nightly HEAD-green census
(11.2 GB, about 2h45m), so it waits on that pid. It then grades the default capture
(`arrears_lfl_400_nr.json`) pooled with both seeds into `/var/tmp/arrears_dice_pooled.txt`. The
reading goes here, under P5, unchanged.

**Re-drawn 2026-10-10 05:37, premise spent, nothing launched.** The unit is alive and still
waiting on the census pid (2h06 in). A second launch would run the same seeds twice. Writing the
grade here is handed on as `the-arrears-pooled-grade-under-p5`, not to be drawn before 10:30.

### Result (2026-10-10T09:45Z, seat): 6.1%, 1.19x, NOT MET, HIGH on the grader. P5 refuted, high

The unit `longjob-arrears-dice-seeds-1-2` ended cleanly at 07:28 (3h50m wall, 4.6 GB peak). Its
worktree `/var/tmp/wt_dice_seeds` is at 820a2f31b, which contains 95c1193cb (the share by method).
So seed 1's 99/1153 sits beside the old flat-0.5 98/1153 by chance, not because the code was stale.
Each capture below was graded alone with `grade_world_debt_against_ofgem grade <one capture>`, and
the pooled line is `/var/tmp/arrears_dice_pooled.txt` unchanged.

| 2019, electricity | Q1 | Q2 | Q3 | Q4 | year | Wilson | verdict |
|---|---|---|---|---|---|---|---|
| default dice | 12/303 | 10/295 | 12/283 | 16/272 | 50/1153 = 4.3% | 3.3-5.7% | MET, 0.85x |
| dice seed 1 | 25/303 | 26/295 | 25/283 | 23/272 | 99/1153 = 8.6% | 7.1-10.3% | NOT MET, HIGH, 1.68x |
| dice seed 2 | 19/305 | 15/297 | 16/284 | 12/273 | 62/1159 = 5.3% | 4.2-6.8% | MET, 1.05x |
| **pooled** | | | | | **211/3465 = 6.1%** | **5.3-6.9%** | **NOT MET, HIGH, 1.19x** |

Gas, pooled: 40/610 = 6.6% (4.9-8.8%), 1.29x, MET (per seed: 4.0%, 6.9%, 8.7%). P5 set no gas band.
**Prepayment share of the accounts behind: 0 on every seed.** That is 0 of 50, 0 of 99 and 0 of 62,
against 134 prepayment account-quarters billed per seed. The dice move the book slightly: seed 2
bills 341 accounts against 339. Debt feeds renewal, as noted under P4.

**P5, band by band:**
- Each new seed 3.0-7.0%: seed 1, 8.6%, **miss** (high). Seed 2, 5.3%, **hit**.
- The default's 4.3% sits low among them: **hit**. It is the lowest of the three.
- Pooled n about 3,459: 3,465, **hit**.
- Pooled 4.2-5.8%, point 4.9%: 6.1%, **miss** (high).
- Ratio 0.82-1.14x: 1.19x, **miss** (high).
- Verdict MET (about 60%): the grader says NOT MET, HIGH. P5 called that outcome unlikely.
  **Miss.**
- Prepayment 0 on every seed: **hit**. No seed puts a PPM account behind 91 days. So "PPM debt is
  absent from the world" is a property of the world, not of one seed's dice.

**The grader's interval is too narrow, so the verdict above overstates what is known.** The Wilson
interval treats each account-quarter as independent. But an account that is behind stays behind:
the 50, 99 and 62 account-quarters are 22, 35 and 29 distinct accounts, about 2.3 quarters each.
- **Resampling accounts instead** (cluster bootstrap within each seed, 4,000 draws, pooled):
  **4.7-7.5%**. That interval contains 5.1%, so on it the verdict is MET.
- **Treating each seed as one observation:** the mean is 6.1%, the sd is 2.2pp, and the t(2) 95%
  interval is 0.6-11.6%.
- **The seeds also spread more than resampling accounts predicts.** The between-seed sd is 2.2pp,
  against a within-seed cluster sd of 1.1-1.5pp. Three seeds cannot establish that excess.
- **The 10-09 MET's 3.3-5.7% was too narrow the same way.**

**What this means downstream.**
- **The 10-09 MET at 0.85x was the low draw of three. It does not stand as a MET.**
- **The three-seed point leans high: 1.19x.** On the honest interval, whether the world over-holds
  debt is **not established**. It is not shown to be low, and it is not shown to be high.
- **The baseline, retention and value-arms re-takes assumed "the world does not over-hold debt".**
  That is now "about 1.2x, and we cannot tell", not "met". They can go ahead, but they should carry
  this as an open fidelity caveat.
- **What still leans high is unchanged:** the provision is a stock rate read as a flow share, and
  gaps 2, 4 and 7.
- **Seed 1's excess is almost all direct debit:** 70 DD account-quarters behind, against 35 on the
  default dice and 50 on seed 2. Card and standing order sit at 9 and 16.
- **Do not vary the book seed (EP17).** It was not varied here.

**Owed, and handed on:** the grader should publish and grade on an account-clustered interval, not
account-quarter Wilson. Then a verdict cannot read MET or NOT MET on a bound its sample has not
earned. Handed on as `the-arrears-grader-grades-on-an-account-clustered-interval`.
