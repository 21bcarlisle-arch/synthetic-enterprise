**Severity:** LATENT · **Lane:** D_billing_metering · **Epoch:** 4 · **Atom:** `D48_billing_accuracy_the_company_measures_what_it_billed_against_what_was_used`
**Knowledge:** back-billing-and-liability

# A third of direct-debit accounts asked for their balance lose part of it to the 12-month limit, because only the final bill ever asks (2026-10-14)

**Fate (2026-10-14):** ATOM -- company, next week, with the DD engine: the review never asks for the balance (seek_balance_at_review false).

*From D48 Expert Hour, 2026-10-14. Adjudication: `SEAT_FINDING_D48_THE_EXPERT_HOUR_FAILS_ON_THE_CLAIM_NOT_THE_MEASURE_2026-10-14.md`. Not fixed in the turn that found it.*

**The figures:** 153 of 422 DD accounts (36.3%, 95% CI 31.8-40.9%) that met a charge recovery action had money barred, £33,770 gross of VAT in all. `seek_balance_at_review: false`.

**What the reviewer said:** its prior was a few percent, and it held that 21BA does not reach a DD shortfall. The rule half is refuted by the sourced position, "a direct debit statement is not a charge" (`back_billing_and_liability.md` §44). The magnitude half stands.

`back_billing_and_liability.md` already records that `dd_review` "does not seek the balance", and that the shortfall therefore ages out. So the 36% is an artefact of the review never asking. A real supplier's annual DD review normally sets the new amount to clear the shortfall.

**Question for the knowledge layer first (K4):** does published practice (Ofgem's DD guidance, Energy UK, Ombudsman decisions) say the review recovers the balance? If it does, `seek_balance_at_review` defaults to the wrong setting, and the 36% describes a supplier that does not exist.

---

## 2026-10-16: answered, built behind a switch, and both arms read

**The knowledge answer.** Ofgem's DD compliance progress update (2 Feb 2023): "where a consumer
account is in a debit position, suppliers commonly add this amount on to the Direct Debit amount
and smooth the cost over the next 12 months." This is described practice, not a licence rule.
`what_a_supplier_holds_to_size_a_direct_debit.md` §8 gives the source and three GAPs: practice
before 2022, the period for large balances, and credit balances.

**Built.** `company/billing/dd_review.py::REVIEW_SEEKS_BALANCE` (False, unchanged) and
`review_balance_step_up` (a twelfth of the debit left after the bar). The world book reaches them
through the DD-review seam, and its `seek_balance_at_review` now defaults to the company's switch.
Control: `tests/simulation/test_dd_back_billing_at_charge_recovery_actions.py::test_the_company_review_recovers_a_balance_it_seeks_and_loses_one_it_never_asks_for`.
I ran three mutations against it, and all three turn it red: a zero step-up, a step-up that is
computed but never applied, and a book that ignores the company switch.

**Pre-registered before the run:**
`docs/staging/records/SEAT_PREREGISTRATION_THE_DD_REVIEW_SEEKS_THE_BALANCE_ON_THE_2248E3BAF_RUN_2026-10-16.md`.

**Both arms, on `run_output_2248e3baf_20261013T134447Z.json`.** Closed = supply points whose last
bill predates the run's last month. The no-seek arm reproduces the published line exactly. Reviews
are on the default `last_year_spend` rule.

| arm | met a recovery action | barred | share (95% CI) | £ barred (at review / at final bill) | open exposure (unasked, would bar) |
|---|---|---|---|---|---|
| never seeks (today) | 422 | 153 | 36.3% (31.8-40.9) | £33,770 (0 / 33,770) | £50,297 |
| seeks the balance | 610 | 239 | 39.2% (35.4-43.1) | £33,386 (26,771 / 6,615) | £1 |

By year of the bar action. A step-up is the monthly amount the recovery adds to the debit, counted
over reviews that found a debit.

| year | £ barred, never | accts barred, never | £ barred, seeks | accts barred, seeks | reviews stepped up | step-up median £/mo | mean | p90 |
|---|---|---|---|---|---|---|---|---|
| 2017 | 0 | 0 | 0 | 0 | 127 | 4.59 | 7.05 | 12.60 |
| 2018 | 1,061 | 13 | 2,301 | 34 | 169 | 5.24 | 7.67 | 16.12 |
| 2019 | 4,110 | 37 | 2,346 | 76 | 162 | 4.01 | 5.40 | 10.52 |
| 2020 | 8,170 | 30 | 6,372 | 39 | 87 | 2.96 | 5.10 | 11.50 |
| 2021 | 1,260 | 14 | 343 | 10 | 63 | 2.57 | 8.57 | 14.97 |
| 2022 | 789 | 9 | 1,909 | 37 | 179 | 11.97 | 14.54 | 27.92 |
| 2023 | 4,274 | 15 | 17,865 | 150 | 220 | 55.01 | 65.36 | 109.67 |
| 2024 | 11,118 | 25 | 2,250 | 20 | 38 | 9.24 | 15.05 | 36.37 |
| 2025 | 2,988 | 10 | 0 | 0 | 6 | 7.15 | 6.58 | 10.63 |

**The prediction, graded.**

1. At least 600 accounts meet a recovery action: **HELD** (610).
2. The barred share falls to 15% (8-25%): **REFUTED**. It rose to 39.2%.
3. Money barred falls to about £12k (£5k-£22k): **REFUTED**. It was £33.4k.
4. The step-up median is £5-15 a month and largest in 2022-23: **HELD on timing, MISSED on size.**
   In 2023 the median was £55.

What I got wrong: I predicted the barred share and money in isolation and forgot the open book. The
no-seek arm's £33.8k counts only accounts that closed. Its £50.3k of open exposure is money nobody
has asked for yet, which the bar takes the moment anyone does. Seeking turns almost all of that
exposure into collected money: barred plus exposure falls from **£84.1k to £33.4k**. The barred
SHARE rises because 188 more accounts are now asked. A rising share is the denominator growing, not
the review losing more.

**Where the seek arm still loses money: 2023.** The default rule resets the debit to last year's
spend. Through 2022's price rise that under-collects again inside the year, so at the 2023 reviews
a balance has built up that is partly over 12 months old. That one year accounts for £17.9k of the
£26.8k barred at reviews. That is a sizing-rule defect: `consumption_at_rates_in_force` and
`own_forecast_plus_balance` exist for it. It is not a defect of seeking.

**The household's side (M2).** In most years the recovery adds £3-12 a month at the median. In
2023 it adds £55, with a p90 of £110, on top of the 2022-23 price rise. That is the bill shock
under a direct debit, as `what_bill_shock_is.md` defines it. The company keeps £50.7k it would
otherwise lose, and 220 households take a large DD step in one year. Both figures belong on the
page together.

**Should the default flip after the 2026-10-19 publish? Yes.** The reason: the published practice
is to seek the balance over twelve months, and a review that never asks describes a supplier Ofgem
did not find. Two conditions go with it:

- (a) The billing page must publish the open exposure and the step-up beside the barred share. On
  its own the headline moves from 36% to 39%, and that reads as worse when it is better.
- (b) The 2023 step-up is the strongest case for pairing the flip with a review rule that prices at
  current rates. That pairing is a separate decision; this switch does not settle it.

Flipping is a one-line, reversible change to `REVIEW_SEEKS_BALANCE`.

**Not done here, noted.** Under `own_forecast_plus_balance`, `reviewed_standing` already adds the
simple running balance. Seeking on that rule as well would recover a debit twice. Nothing runs that
pair today. Guard it before anyone does.
