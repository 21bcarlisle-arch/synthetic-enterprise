**Severity:** RECORDED · **Lane:** C_customer_ops · **Atom:** `C29_decisions_stop_being_lookup_tables` · **Direction item:** `grade-the-retention-guard-netting-the-companys-own-bad-debt-belief`

# Pre-registration: the retention guard netting its own bad-debt belief, on the contribution guard

Written 21 Oct 2026 at about 09:35Z, before either arm ran. No code changes. The default of
`DecisionPolicy.retention_nets_bad_debt` stays `False` in this item.

## Correction to the item's premise

The item says the netting "has been built and unmeasured". **It was measured, on 2026-10-07**
(`SEAT_RESULT_THE_RETENTION_GUARD_NETS_BAD_DEBT_AND_ON_THE_CHOSEN_BOOK_IT_WITHDRAWS_NOTHING_2026-10-07.md`,
beside this file). The two arms came out identical: 73 offers each, and a guard that refused nothing,
with value protected running 4.9x to 15.7x the offer's cost. That reading has since been overtaken.
`c61d8b608` (2026-10-20) values the guard on the term's **contribution**, not the spread over
wholesale. On the shared tree's latest run (`9ca972774`, 2026-10-21 02:54Z, unpublished), the
guard's value-to-cost ratio over its 113 offers is 1.13 at the minimum, 2.10 at the lower quartile
and 2.78 at the median. Expressed as a share of the term's energy billing, headroom (value minus
cost) is 2.0% at p10, 3.2% at p25 and 5.3% at the median. The company's bad-debt prior is 2.0% of
billing (`company/pricing/default_belief.py:75`). **So the netting can now bind, which it could not
on 10-07.** That is why the pair is worth re-running.

## The pair

- `off`: `CURRENT_POLICY`. `net`: `dataclasses.replace(CURRENT_POLICY, retention_nets_bad_debt=True)`.
  This is the one variable.
- Full 2016–2025 window, default book and seed, at origin `1ac35d918`, in a locked worktree
  (`/var/tmp/se-retnet/wt`). Each arm runs in its own process.
- Probe: `/var/tmp/se-retnet/probe.py`. It is out of tree because `tools/_c29_retention_engagement_arm.py`
  would crash on the contribution guard's `None` value. The probe wraps the run's
  `retention_value_protected` and records each guard verdict once. Each record carries the payment
  behaviour score the churn belief read, the margin, the billing, the belief rate, the netted
  charge, and whether the un-netted value would have offered.
- Launched by the unit `relaunch-driver-retnet-1021`. It is queued behind
  `relaunch-driver-scopex-1021` and `relaunch-driver-baddebt-1021`, and runs through
  `background.launch_long_job` (`longjob-retention-nets-bad-debt-arms-1ac35d918`). When the job ends,
  it files the grade continuation `grade-the-retention-netting-arms-1ac35d918`.

## What the reasoning rests on

The belief is keyed on **arrears state**, not payment method. Each arrears cell starts at the 2.0%
prior, with one account-year of weight (`PRIOR_ACCOUNT_YEARS`). 93 of the 113 offers fall in
2017–2018, before many outcomes have resolved. So most offers net close to 2% of billing,
whatever the account's score. A flat 2% charge applied to the 9ca972774 offers withdraws 11 offers
(£640 of £2,838). Of those, 6 were retained and 5 churned despite the offer. At 3% it withdraws 24
(£846). Netting only ever lowers the value, so to first order no offer can be added. Any `net`-arm
offer that is absent from `off` is path divergence, and is counted as such.

## Predictions (on the difference, net minus off)

- **P1, offers withdrawn.** Offers fall by 6–25 (point estimate 11), and retention spend falls by
  £250–£1,100 (point estimate £640). *Refuted* if offers fall by fewer than 4 or more than 35.
- **P2, who loses them. This is the decisive one.** Withdrawals are **not** concentrated on
  debtors. Take the share of withdrawn offers whose renewal read a POOR or CRITICAL score. It sits
  within 10 points of POOR/CRITICAL's share of `off`-arm offers (expected 10–20%). *Refuted* if the
  withdrawn POOR/CRITICAL share is at least twice their `off`-arm offer share. If P2 holds, the
  netting as built trims thin-headroom offers across the whole book. It does not stop the debtor
  transfer the item's WHY names, so making it the default would rest on a different argument
  (that it is the correct valuation) and not on that one.
- **P3, the belief itself.** The median `belief_rate` over `net` guard rows lies in [0.015, 0.030].
  The median for POOR/CRITICAL rows is under 1.5x the median for GOOD/EXCELLENT rows. *Refuted* if it
  is 2x or more. That would mean the arrears-state cells had learned enough to separate debtors.
- **P4, churn.** Renewal departures move by 0 to +4, and churned billing accounts by −2 to +6. Only
  11 or so offers are withdrawn, and the world credits a 1–8% cut with a small change in P(stay).
  *Refuted* if departures fall, or rise by more than 6.
- **P5, retained margin net of bad debt.** `total_net` moves by £0 to +£1,000: spend is saved, and
  the few extra leavers had median contribution around £9. `total_bad_debt` moves by less than
  £500. *Refuted* if `total_net` falls. If `total_net` moves by more than £3,000 in either
  direction, the pair is dominated by path divergence and cannot be read as one variable at this
  book size; that is reported as such, not graded as a pass.

## What each outcome would change

- **P1 and P2 hold:** keep the field off as the debtor fix. Raise the debtor transfer as its own
  mechanism. One option is an arrears-state belief that can separate debtors; the other is a guard
  rule on accounts in arrears. That second option is a policy choice and goes to the director with
  a recommendation.
- **P2 refuted (withdrawals land on debtors):** propose flipping the default, with the
  `total_net` and departures figures beside it.
- **P1 refuted low (nothing withdrawn):** the contribution guard's headroom is not where the
  9ca972774 log puts it at 1ac35d918. Find out why before anything else.
