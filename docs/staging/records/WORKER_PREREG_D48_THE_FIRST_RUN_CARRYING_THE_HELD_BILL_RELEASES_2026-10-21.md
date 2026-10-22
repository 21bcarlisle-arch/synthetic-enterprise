**Knowledge:** unbilled-energy-and-revenue-assurance

# D48: the first run carrying the held-bill releases, graded (pre-registration, 2026-10-21)

*Worker, 2026-10-21, written at 07:20Z before any held-bill figure was read from the run.*

Three D48 follow-ons each ended "the next run settles it":
`SEAT_FINDING_D48_THE_UNBILLED_ACCRUAL_IS_THE_ENERGY_THE_PRE_BILL_GATE_HELD_2026-10-20.md`, items 2
(066fd2300), closed account (7a266cb76) and founder homes (032b3dec2). The shared tree's plain
`docs/reports/run_output_latest.json` is unpublished, and was drawn at **9ca972774**, which has all
three as ancestors. It does not carry ab3baa0b0 (the K1 dating fix). The committed gz (ad8afadc5)
carries none of them. So this run is the first that can grade them. The book is the 400-household
founder book (8927e9345), not the 44a21e3e8 book the follow-ons measured, so counts are not
comparable to theirs; only the properties below are.

**Instrument.** The run's own bills. The held set is `company.interfaces.bill_assembly.held_bills`
at HEAD, which is the issuance door's own reading. The in-run `billing_accuracy` block is read beside
it. A closed account is one whose bills carry `final_bill`.

**Predictions.**
1. Held **actual-read** bills: 0 in total, so 0 at every month end of the run's
   `K1_unbilled_accrual`. (Item 2 releases an occupier's held actual once the listing answers; the
   founder-homes fix gives the founders a listing.)
2. No resi electricity bill carries `premise_council_tax_listed` None. (Founder homes, prediction 3:
   "holds by construction", not yet measured.)
3. On a closed account, every held bill in its closing run is one SLC 21BA bars at the final bill
   (some part over 12 months before the final bill's date). No other held bill sits in a closing run.
4. The in-run `billing_accuracy` and a HEAD recompute over the same bills differ in
   `K1_year_end_grades` only (ab3baa0b0), at no more than three year ends, and the accrual
   `month_ends` are identical.

**Refutation lines.** Any held actual refutes 1. Any None listing on a resi electricity bill refutes 2.
A held closing-run bill not barred by 21BA refutes 3. Any accrual month-end difference refutes 4.

## Graded (2026-10-21, same tick)

All four held. 53,314 bills; 854 final bills stamped.

1. **CONFIRMED.** 40 bills held, all estimates. Held actuals: 0 in total and 0 at every one of the
   10 accrual month ends in the run's own block.
2. **CONFIRMED.** No resi electricity bill has a None listing. The 24 None listings are the SME
   founders C5 and C6 (12 each), which are not domestic.
3. **CONFIRMED.** 2,734 closing-run bills, of which none is held.
4. **CONFIRMED.** Every block is identical except `K1_year_end_grades`, which differs at one year
   end: electricity 2017-12, open bills 1,373 -> 1,372 and open kWh -3,120.35 (GBP -419.79). That is
   the same single closing-run interim ab3baa0b0 moved on the 44a21e3e8 book.

**What the grade turned up, which the predictions did not ask.** The 40 held estimates are five
accounts, and 32 of them are **PROS-2017-0336**, a listed dwelling whose meter reads 2,500-5,000 kWh
a month. Each of its estimates is over the population ceiling, so each waits for an actual read.
From 2019-04 to 2020-05 it was sent **no bill at all**, then a single catch-up of GBP 5,067 for 14
periods at 2020-06-30. SLC 21B.5 asks for a bill at least twice a year. The catch-up itself is
right: `read_true_up_billed_kwh` is 0 and `catchup_unbilled_periods` equals the held count, so no
energy is lost. It is billed late and all at once.

**Counterfactual, printed before any build.** 31 of the 40 are at or under a daily rate the same
meter had already measured at an earlier read (read-to-read, using only bills before this one). The
other 9 are on accounts with no read yet. Measuring by month instead of read-to-read gives the same
31.

**Built from this:** `pre_bill_validation.release_on_measured_rate`, asked by both the issuance
door and the assembly's catch-up. Knowledge first: `unbilled_energy_and_revenue_assurance.md` §4d.
Re-validating these bills with it holds 9 and releases 31. Those bills' catch-ups were assembled
under the old rule, so this count says which bills are released and nothing about money. The next run settles the money.
**Prediction for that run, filed now:** held estimates fall to those with no earlier read or above
every rate measured (single digits on this book). PROS-2017-0336 gets a bill every month, and
its largest catch-up falls below GBP 1,000.

## Beside the prediction above: what HEAD's gate already says about it (worker, 2026-10-21, 08:10Z)

This is a re-validation, not a run. HEAD's `validate_bills` (4d6d5ab91) was run over the same 53,314
bills. It holds 9 bills on four accounts, all resi electricity estimates over the domestic ceiling
on accounts with no earlier actual read. The longest stretch of consecutive held periods is **3**
(SYN-2016-582, 2016-12 to 2017-02). The others are PROS-2017-0336 2 (2017-12, 2018-01),
PROS-2024-0010 2 and PROS-2025-0106 2. Each stretch ends at the account's first actual read. So no
account on this book goes six months without a bill, and SLC 21B.5 is met.

**Corrected beside the claim:** "PROS-2017-0336 gets a bill every month" is too strong as written.
HEAD still holds its 2017-12 and 2018-01 estimates, because it had no read yet. The prediction the
next run grades is therefore "no gap over two months on PROS-2017-0336, and none over three on the
book", together with the GBP 1,000 catch-up bound, which is unchanged. The 9 that stay held are what
§4d intends the screen to hold.

**The run that grades the filed prediction (worker, 2026-10-21, 14:45Z).** It is the retention-netting pair's OFF arm: CURRENT_POLICY on the full book in /var/tmp/se-retnet/wt at **1ac35d918**, which carries 4d6d5ab91 (`git merge-base --is-ancestor 4d6d5ab91 1ac35d918` exits 0). The arm is not started yet: it is queued behind scopex and baddebt, with no `status` and no `off.log` at 14:40Z. After off.json, /var/tmp/se-retnet/probe.py now rebuilds the bills with phase4c's own `build_monthly_bills` and writes the bills (`billing_basis`, `final_bill`, `period_end`), `held_bills` and `billing_accuracy` (K1 month ends; the DD money line is left out, because it needs phase4c's balance book) to /var/tmp/se-retnet/off_bills.json.gz. If that step fails, it writes off_bills.error and exits 0. run_both.sh then files `grade-d48-held-bill-releases-on-the-retnet-off-arm`, held until that file exists. Both edits were proven on a 40-household 2016 sub-book in a scratch worktree at 1ac35d918: 4,793 bills, 47 final, 0 held, and the handoff was filed into a temp store with its path hold read back. **Found and fixed on the way:** the probe could not import `simulation` as launched. A script's sys.path[0] is its own directory, and the unit sets no PYTHONPATH, so both retnet arms would have died at import. probe.py now puts its cwd, the locked worktree, first on the path.

## Graded on the retnet off arm (worker, 2026-10-21, 21:50Z)

Read from /var/tmp/se-retnet/off_bills.json.gz: arm `off`, CURRENT_POLICY, head 1ac35d918 (carries
4d6d5ab91), read instruction on. 53,314 bills, 854 final bills, 9 held. No off_bills.error. The DD
money line is omitted by design. A "gap" here means consecutive months whose bill the pre-bill gate
held, so the customer was sent nothing for them.

1. **Held estimates in single digits, only those with no earlier read or above every measured
   rate: HELD.** 9 held, down from 40, all resi electricity estimates. None has a measured
   read-to-read rate before it: SYN-2016-582 (3), PROS-2024-0010 (2) and PROS-2025-0106 (2) have no
   earlier actual read at all, and PROS-2017-0336 (2, 2017-12 and 2018-01) has one actual read
   (2017-11), which is not enough to measure a rate. It is the same 9 that HEAD's re-validation
   named at 08:10Z.
2. **No gap over two months on PROS-2017-0336, none over three on the book: HELD.** PROS-2017-0336's
   longest gap is 2 months, and the book's is 3 (SYN-2016-582, 2016-12 to 2017-02). The 2019-04 to
   2020-05 gap is gone. PROS-2017-0336 has 93 bills from 2017-10 to 2025-06 with no month missing.
3. **PROS-2017-0336's largest catch-up under GBP 1,000: REFUTED.** Its only held-bill catch-up is
   the 2018-02-28 bill for 2 periods: GBP 1,809.12 in total, of which the catch-up adjustment is
   GBP 1,171.79. It is above GBP 1,000 on either measure. The earlier figure was GBP 5,067 for 14
   periods, so the catch-up fell by about 64% but did not get under the bound. The prediction
   priced two held months at an ordinary bill, but this meter uses 4,000-5,000 kWh a month, so two
   months of its energy alone is over GBP 1,000. The bound was wrong for this account, while the
   mechanism behaved as §4d intends.

**What the grade turned up, which the predictions did not ask.**
- **Held energy is billed at the first actual read, not at the next bill that is sent.**
  SYN-2016-582 gets bills again from 2017-03 as estimates, but its 3 held periods are not charged
  until the actual read on 2017-07-31, seven months after the first held month. Each of the 4
  catch-ups works this way (PROS-2024-0010: held 2024-01 and 02, charged 2024-05). SLC 21B.5 is
  still met, but the unbilled accrual carries that energy for longer than the gap in bills shows.
- **PROS-2017-0336's largest bill is a read true-up, not a held catch-up.** On 2023-03-31 it is
  billed GBP 6,036.85, which includes a GBP 4,224.94 undercharge after 21 consecutive estimates
  (8,351 kWh trued up). That is the book's largest catch-up. It falls under the read-instruction
  and estimate-accuracy question, not the pre-bill gate's.

## Re-graded on a HEAD full-window run (seat, 2026-10-22, 12:20 BST)

This is the run that `run_annual_report` writes, not a probe rebuild. `head-crisis-989ce4f1c2` at
**989ce4f1c2**, `/var/tmp/se-head-crisis-out/run_output.json`. It carries 4d6d5ab91, the
post-departure gas fix 2b81e1466 and the gas-PPM read instruction c6c09641e. `held_bills` is
recomputed over the run's own `bills`. 53,110 bills, 204 fewer gas bills than 76a29bd92. 147 of those are
the post-departure bills 2b81e1466 removes; the other 57 are not traced (see the crisis bad-debt
finding). 852 final bills.

1. **Held estimates in single digits, only those with no measured rate: HELD again.** 9, all
   estimates, the same four accounts and counts as the retnet off arm: SYN-2016-582 3,
   PROS-2017-0336 2, PROS-2024-0010 2 and PROS-2025-0106 2. Held actuals are 0 at every month end of
   the run's own `K1_unbilled_accrual`.
2. **No gap over two months on PROS-2017-0336, none over three on the book: HELD again.**
   PROS-2017-0336 has 93 bills from 2017-10 to 2025-06.
3. **PROS-2017-0336's largest catch-up under GBP 1,000: REFUTED again,** for the reason already
   given. The 2018-02-28 bill for 2 held periods totals GBP 1,812.93 (GBP 1,809.12 on the retnet
   arm).

So the probe rebuild and the run's own bills agree. The gas-PPM read instruction and the
post-departure fix move none of the held set.
