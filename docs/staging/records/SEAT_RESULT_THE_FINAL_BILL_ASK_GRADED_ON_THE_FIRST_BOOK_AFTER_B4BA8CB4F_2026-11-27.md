**Severity:** LATENT · **Lane:** D_billing_metering · **Epoch:** 4 · **Atom:** `D48_billing_accuracy_the_company_measures_what_it_billed_against_what_was_used`

# Result: the world's final-bill ask, graded on the first book after b4ba8cb4f (2026-11-27)

Grades the **Still open** section of
`SEAT_PREREG_THE_PAGE_RESOLVES_A_FINAL_BILL_ON_THE_WORLDS_ASK_2026-11-26.md`. The predictions were
written there on 26 Nov, before any of these books existed.

**Books.** The first `run_output` whose sha has b4ba8cb4f as an ancestor is **2100f84f85**
(`run_output_2100f84f85_20261126T194216Z.json`). 76f894811d (15:50) does not descend from it. The two
later books, 601887d76a and d640bd67e4, were run as corroboration. The published page
(`docs/state/billing_ledger.json`) is the 601887d76a book's.

## Graded

1. **`final_month_nets.part_paid_gbp` is at most `ask_gbp`: held.** 0 of 876 rows on 2100f84f85, 0 of
   876 on 601887d76a, 0 of 878 on d640bd67e4. On the 91c32797b3 book OCC-cede70b10116g part-paid 57.23
   against an ask of 3.61. On 2100f84f85 it part-paid 4.14 of 8.52, and on 601887d76a 8.45 of 17.41.
   Only 7 final rows carry any part cash.
2. **No ever-level leg has the world taking more credit than the page netted, except the shapes the
   record names: held, with a residual.** `/var/tmp/rev31/allnet2.py`, pointed at each book
   (`/var/tmp/rev33/allnet_<book>.py`):

   | book | ever-level final rows | disagree | world takes more | legs |
   |---|---|---|---|---|
   | 91c32797b3 (before) | 485 | 26 | 6 | 099, 244, 360g, 139, 6387, cede |
   | 2100f84f85 | 485 | 19 | 2, GBP 96.25 | OCC-6387bf64272a 0.14, OCC-cede70b10116g 96.11 |
   | 601887d76a | 485 | 17 | 4, GBP 139.25 | includes 6387 and cede (92.50) |
   | d640bd67e4 | 485 | 18 | 4, GBP 133.31 | includes 6387 and cede |

   The paid-final legs SYN-2016-099, -244, -360g and -139 have dropped out. The two that remain are
   both **failed on-level finals**. The record did not name this shape: its build netted
   `credit_taken_gbp` on a PAID final only. The residual is filed as
   `docs/staging/SEAT_FINDING_A_FAILED_LEVEL_FINAL_OPENS_A_CASE_ON_CREDIT_THE_WORLD_NETTED_2026-11-27.md`.
   I cannot yet say what the two extra legs on the later books are. Those books carry other
   changes, so the count is not attributed to anything.
3. **The run's own refund log and the page agree on these legs: held for cash, refuted for the
   dunning.** On 601887d76a, OCC-cede70b10116 has a refund log entry of 44.26 with an 8.96 set-off
   against the gas leg. The page prints the same refund (44.26) and set-off (8.96). Both legs close
   at 0.00. But the page's gas final opens an arrears case at **92.50**, with first and second
   notices, where the run closes the gas leg owed 8.96. Same balance, different attribution: the
   SYN-2016-139 shape, now customer-visible. See the finding.
4. **INV_A_CLOSING_REFUND_IS_WITHIN_THE_HOUSEHOLD_CREDIT has no new breach: held.** The 601887d76a
   book has 7 breaches, all of class `other_leg_debt_collected_after_the_refund`, which is the excepted
   class (retired by n29-close-set-off-nets-issued-debt). The last book before that (6af7fd0bfd) had
   24, also all that class. No invariant file was committed for 2100f84f85 itself. Several things
   changed between 6af7fd0bfd and 601887d76a, so the fall from 24 to 7 is not attributed.

## Not graded here

Many failed finals show the page's case differing from the world's `ask - part` (20 of 47 on
601887d76a). In most of them the world's ask includes the scheme debit (`debit_asked_gbp`), and the
page carries that outside the case. The two quantities count different things, so their difference is
not a defect. Only legs where the page is ABOVE the world and the world netted credit are in the
finding: OCC-cede70b10116g, and PROS-2024-0270g (page 54.08, world 13.27, credit 40.81).
