# How the Energy Bills Support Scheme reached a household's bill (Oct 2022 to Mar 2023)

**Knowledge:** debt-and-collections

**Asked by** the crisis bad-debt finding
(`docs/staging/SEAT_FINDING_THE_CRISIS_BAD_DEBT_CONTROL_HAS_SKIPPED_SINCE_THE_RUN_WENT_GZIP_AND_THE_PUBLISHED_RUN_SHOWS_NO_STEP_UP_2026-10-14.md`),
whose 2026-10-23 section found that the £400 reaches neither the world nor any billing path. This is
next step (i) there, and the K8 page that must come before the build. Researched 2026-10-23. No code
changes in this commit.

## What the scheme required

- **Who.** Every GB domestic household with a domestic electricity supply. It was paid per domestic
  electricity account, not per household. Gas accounts got nothing. Non-domestic supply was covered
  by the separate Energy Bill Relief Scheme, not EBSS.
- **How much and when.** £400, in six monthly instalments, October 2022 to March 2023, each of £66
  or £67. The constants are already carried in `company/regulatory/energy_bill_support.py`
  (`EBSS_MONTHLY_CREDIT_GBP = 66.67`, `EBSS_MONTHS`). That module uses an even £66.67. The
  published split is £66 in October and November and £67 from December to March, and those six add
  up to the £400. **GAP (small):** the module's even split is £0.02 off the total. Use the
  published split when the credit is built.
- **Who paid.** Government funded it. The supplier applied the credit and reclaimed it. The
  supplier's charge for the energy is unchanged. What changes is what the household owes. **The
  credit is a receivable from government, not lost revenue and not a discount.**

## How it reached the account, by payment route

| route | how the £66/£67 arrived | did the household have to act? |
|---|---|---|
| direct debit | credited to the account each month. Some suppliers offered it as a refund instead. | no |
| pay on receipt (standard credit) | credited to the account, shown on the bill | no |
| smart prepayment | added to the meter as credit | no |
| traditional prepayment | a voucher each month, by text, email or post, redeemed at a PayPoint or Post Office | **yes** |

Source: the scheme's consumer guidance, as summarised by ii.co.uk, "Energy Bills Support Scheme
takes some of sting out of soaring bills" (2022). That is a secondary source. **GAP:** the BEIS
guidance itself was not fetched for this page.

## What the published record says about take-up

Only the traditional-prepayment route depended on the household acting, so it is the only route
with a take-up figure.

- **71%** of vouchers had been redeemed since launch, as of the January 2023 government release (up
  from 65%).
- **76%** of January's vouchers had been redeemed, per the February 2023 release: 1.7m used, around
  1.9m still unredeemed.
- **About 20%** of vouchers expired without being redeemed (press reading of the final figures, LBC).
- By supplier, the January 2023 rates ran from about 85% at the best to the low end at Scottish
  Power, Good Energy and Utilita. By region, 26% were unclaimed in Scotland and 32% in London.

Sources: current-news.co.uk, "Good Energy, Utilita and Scottish Power rank amongst lowest for EBSS
voucher redemption, says BEIS"; which.co.uk, "Thousands missing out on energy support"; End Fuel
Poverty Coalition, "Poorest constituencies missing out"; lbc.co.uk, "Nearly 20% of energy support
vouchers expire without being redeemed". All are secondary readings of BEIS or DESNZ releases.
**GAP:** the final DESNZ EBSS statistics, which give the end-of-scheme redemption rate, were not
fetched. The range above, 0.71 to 0.82, is the published bracket until they are.

## Why it matters to the run

Ofgem attributes the fall in the arrears count from Q2 2022 to Q1 2023 (894,732 to 663,189) to EBSS
and the Energy Price Guarantee (`debt_and_collections.md`). The world has the EPG through the cap.
It does not have the £400. So from October 2022 to March 2023, every world electricity bill is £66
to £67 a month too high, in exactly the window where the world's failed share of billed pounds
peaks (6.7% in January 2023).

## What the code does today (discovery, 2026-10-23, on origin/main `7a777030e9`)

- **Two amount paths reach the world. Both are gross of EBSS.**
  1. The household's payment decision. `simulation/run_phase2b.py` sums a leg's month of
     settlement `revenue_gbp` into `held["amount_gbp"]` and hands it to
     `live_payment_triad.record_period`. Behind `household_budget.BUDGET_DECIDES_PAYMENT`, that
     decides whether the household's margin can cover the bill.
  2. The pounds that fail. The arrears engine (`arrears_engine._resolve_bills`) takes each issued
     bill's `total_amount_gbp` from the company's bill assembly. `world_payment_truth` keeps "the
     amounts the issued bills'" by design.
- `company/regulatory/energy_bill_support.py` and `ebss_register.py` are reached only by tests and
  `tools/generate_dashboard_data.py`.

## The design choices the build makes, and why

1. **The supplier applies the credit. It is not world income.** That is how the scheme worked, and
   a real supplier knew every term of it (published law), so the wall allows it. It enters as a
   credit line on the domestic electricity bill, months 2022-10 to 2023-03, at the published
   £66/£66/£67/£67/£67/£67.
2. **One credit, both paths.** The defect class here is the VAT rule's: one requirement, two homes.
   The household's held amount (path 1) and the issued bill's `total_amount_gbp` (path 2) must net
   the same pounds, from one function. A control asserts the two agree on every credited leg-month.
3. **Revenue does not move.** The P&L books the credit as recoverable from government. Margin is
   unchanged, and what falls is what the household owes. A build that lowers `revenue_gbp` would be
   wrong in the other direction.
4. **Traditional prepayment carries take-up as a stated belief.** The range is 0.71 to 0.82, drawn
   per voucher, and an unredeemed voucher credits nothing. The world currently says "no meter is
   changed for debt" and keeps a PPM channel. If that channel cannot tell smart from traditional,
   the build says which it assumes and labels it.
5. **Prediction, filed before the run.** Netting £66 to £67 off the October to March bills lowers the
   world's failed share in winter 2022-23, and with it the too-steep 2023 the finding names. It does
   not create the 2022 step the validator asks for. That step is the company's overlay (finding,
   point 1). If the build's run shows a 2022 step-UP, this page's reasoning is wrong and says so
   here.

## Choice 5's grading run, fixed before either arm finished (2026-10-23, 19:55Z)

**The run.** Two full-window arms at origin `aed6ba8517`, which carries the build (d8129f3f6) and
not yet the EPG carve another lane is landing. *On* is that commit as it stands. *Off* differs in
one line: `bill_assembly.owed_after_scheme_credit` returns the gross amount. Long jobs
`ebss-grade-on-aed6ba851` and `ebss-grade-off-aed6ba851`, artefacts in `/var/tmp/se-ebss-out/`.
The grader is `/var/tmp/se-ebss-out/grade.py`. Run on the pre-EBSS run 989ce4f1c2, it reproduces
the finding's table A to within 0.05 pt (2022 2.91% against 2.87%, January 2023 6.68% against 6.7%).

**What each figure counts.** *Billed* is the issued bills' `total_amount_gbp`, the charge, which
EBSS does not move. *Failed, gross* is the charge on bills the world's payment truth records as
unpaid. That is table A's basis, and it moves only if fewer households fail. *Failed, owed* is what
actually failed: the charge less the EBSS credit, less any part payment. *Winter* is bills with a
period ending October 2022 to March 2023.

**The predictions, sized now.** The credit is about 17% of winter's billed pounds (GBP 87.6k of
505k on 989ce4f1c2).
- **P1.** Winter's failed-owed share is lower on *on* than on *off*, by a ratio of 0.60 to 0.90.
  Above 0.90 means the netting reaches almost no failing bill. Below 0.60 means it moved more than
  the credit's pounds can, through incidence.
- **P2.** Winter's count of failed bills on *on* is no higher than on *off*. More failures with
  less owed refutes the budget path.
- **P3, the page's "no 2022 step-up".** The 2022 failed-owed share on *on* is not above *off*'s,
  and the IFRS 9 step-up ratio on *on* is not above *off*'s by more than 0.05.
- **Control (can the comparison fail?).** 2016-2021 lie before the credit. If their failed shares
  differ between arms by more than 0.2 pt, the arms are not paired, and P1 to P3 are not graded.

## Choice 5, graded: all three predictions hold (2026-10-23, 21:55Z)

Both arms finished. Each `producing_commit` is `aed6ba8517`. **Pairing control: held.** 2016-2021
match exactly, bill for bill, between the arms (0.00 pt apart), so P1 to P3 are graded.

| figure | off (no credit) | on (credit netted) | on / off |
|---|---|---|---|
| winter 22-23, failed-owed share of billed | 5.06% | **4.18%** | **0.83** |
| winter 22-23, failed-gross share (incidence) | 5.06% | 4.84% | 0.96 |
| winter 22-23, failed bills | 107 of 2,457 | **98** | |
| 2022, failed-owed share | 3.06% | **2.62%** | |
| 2023, failed-owed share | 6.03% | 5.55% | |
| IFRS 9 crisis share / step-up | 0.692% / x0.95 | **0.593% / x0.81** | |

- **P1: HELD.** The ratio is 0.83, inside 0.60 to 0.90. Of the 0.88 pt fall, about 0.22 pt is
  incidence: nine fewer winter bills fail. The other 0.66 pt is the credit netted off bills that
  still fail.
- **P2: HELD.** 98 failed bills against 107.
- **P3: HELD, and the step-up falls.** EBSS lowers the 2022 failed share and creates no step. The
  validator moves *further* from passing: the crisis share goes from 0.69% to 0.59% against the 1%
  floor, and the step-up from x0.95 to x0.81. That is the direction this page expected. The £400
  was real relief, and the 2022 step the validator asks for is the company's overlay (the finding's
  step ii), not the world's.

**What the prediction did not ask, and the grade shows.** The page said the credit would ease "the
too-steep 2023". It eases only January to March 2023. From April 2023 the arms run within 0.7 pt of
each other, and they are identical from August. The world's failed share stays at 4.9-6.8% every
month of 2023 after the credit ends, 1.5 to 2 times its 2016-19 level of 3.2-3.8%. So EBSS does not explain the
too-steep 2023. That question stays with the finding's steps (ii) and (iii).

**The base.** These arms predate the EPG carve (another lane, landing as this is written), which
lowers default-tariff bills in the same winter. With smaller bills the credit is a larger share of
each one, so the size of P1 will move on the next run. The direction should not.

## How the billing record carries it (2026-10-27)

The table above says the credit was applied to the account, not paid by the household. The billing
ledger did not record it that way. A bill the credit settled in full was written as a payment of the
whole bill with no method, and its status was `overdue`: 218 bills on 4ae8da9b0f.

- The ledger now gives such a bill the method `scheme_credit` and the status `paid`.
- The raw export treats it as an **adjustment**: money credited to the account, with that reason.
  It is not a payment.
- A bill the credit covered only in part was still recorded as the household paying the whole
  bill. That was next step (b) of the blind-suite finding's export section; the section below
  closes it.

## A bill the credit covered in part (2026-10-27)

**What published practice says.** The credit went onto the account balance, not onto a payment.
- *Pay on receipt (standard credit).* The credit was added to the account balance in the first week
  of each month, October to March. The bill that followed showed it. The household paid the
  balance, so it paid the bill less the credit.
- *Direct debit.* Practice varied by supplier. OVO credited the account and then refunded the credit
  to the customer's bank account 3 to 5 working days after the direct debit cleared. Other suppliers
  left it on the account as credit, or lowered the direct debit.
- *Every route.* The credit was the government's money, reclaimed by the supplier. It was never a
  payment by the household.

Sources: OVO Energy, "Energy Bills Support Scheme" (ovoenergy.com/energy-bills-support-scheme);
The Star, "Energy bills: How £400 government discount will be paid to you, according to your
supplier" (2022); the HMG fact sheet for the scheme as republished by CPCT.

**The choices the build makes, and why.**
1. **The household pays the bill less the credit.** That is how the pay-on-receipt route worked. It
   is also what the arrears engine and the DD collection book already ask of every route
   (`owed_after_scheme_credit`). The ledger now records the same figure as the payment.
2. **The credit is recorded beside the payment as `scheme_credit_gbp`.** The raw export reads it as
   an adjustment, and the household's account ledger shows it as a credit that lowers the balance
   and is not counted as collected. Billed = collected + scheme credit + balance + written off.
3. **No more credit than the bill on that bill.** What is left over stays on the account. The
   engine nets it from the next bill on that fuel (`credits_applied`).

**What is unknown.**
- **GAP:** the rule for a bill smaller than the month's credit. No published source fetched for
  this page says whether the rest had to carry forward or could be refunded. Ofgem's "Energy Bills
  Support Scheme: Guidance for Electricity Suppliers" should say; it was not fetched.
- **GAP:** for direct debit, the world nets the credit from the month's collection. A supplier that
  kept collecting the fixed amount and refunded the credit, as OVO did, moved the same pounds by a
  different route. The account balance comes out the same either way. The cash flow by day does
  not, and that difference is not modelled.

## An occupier's deemed account (2026-10-27)

**What the rules require.** BEIS, "Energy Bills Support Scheme: guidance for electricity
suppliers" (22 Sep 2022, withdrawn after the scheme closed and still published at
assets.publishing.service.gov.uk/media/661eb96a90095817cebd3dc7/withdrawn-ebss-guidance-for-electricity-suppliers.pdf):
- **5.1:** payments "are applied to primary domestic supply contracts (or deemed contracts)".
- **5.3:** eligibility is "only one contract (or deemed contract) per domestic premises".
- **5.4:** a customer with a domestic supply contract "or a deemed contract at 00:00 hours on the
  qualifying date" is eligible for that month. The qualifying date is the 1st of each month from
  October 2022 to March 2023 (5.8).
- **Annex C, "Occupier Accounts":** a household with no named account holder on the qualifying date
  is still counted as eligible. As a last resort, the supplier credits the "Owner/Occupier" account
  on the bill for direct debit, credit and smart prepayment customers.
- **Annex C, "Vacant Properties":** a property found empty on the qualifying date, with no
  eligible customer, is an exception. No payment is made.

**What the code did.** The world books energy used in the change-of-tenancy window, before the
incoming occupant is named, as `occupier_debt_gbp`. The amount was the window's whole revenue,
including in the crisis winter. No credit was applied to it, and the ledger recorded the occupier
as paying the bill in full. On 4ae8da9b0f that was 22 `OCC-` bills on seven accounts. Twelve of
them, covered in part, overstated the occupier's payment by £804.

**The choices the build makes, and why.**
1. **An unnamed occupier's account takes the credit for a month only if it held the account on the
   1st.** That is guidance 5.4 read against the world's own window. If the home was still void on
   the 1st, the month falls under the vacant exception and gets no credit. So does an occupant who
   arrived after the 1st, because nobody held the account at 00:00.
   (`simulation/run_phase2b.occupier_scheme_credit`).
2. **The credit is netted from the occupier's debt, not booked as revenue.** The government paid
   it. So the supplier's loss on the window is the revenue less the credit, capped at the debt.
   Any credit beyond the debt is a balance owed to the occupier, not a gain.
3. **One credit per account per month.** The bill carries `occupier_scheme_credit_gbp`. The arrears
   engine, the household's held month and the ledger then give no second credit to a payer named
   later that month (5.3).

**What is unknown.**
- **GAP:** a named account opened after the 1st still has the month's credit netted by
  `owed_after_scheme_credit`, which does not read the qualifying date. Under 5.4 that is a credit
  the supplier could not have claimed. Not measured on any book yet.
- **GAP:** whether a supplier's "reasonable steps" for an occupier account (Annex C) ended in a
  credit or an exception in practice. This page assumes a credit, which is the last-resort route
  the guidance names for credit and DD accounts.
