**Severity:** LATENT · **Lane:** D_billing_metering · **Epoch:** 4 · **Atom:** `unminted`

# The level-DD J1 leg reads a household's journey against one fuel leg's returns (2026-11-16)

*LATENT: a scratch instrument (J1) counted the wrong object, which understated a pre-registered leg. No gate row,
published figure or control verdict reads it, and the household reading is given below. The 13 openings it leaves
belong to the level-DD finding's open rows.*

**Why this was audited.** 367378cb7 showed that `/var/tmp/grade-desk-bacs/grade.py` matched an account-level
desk journey against one fuel leg's bills: every next-Bacs-day opener it counted was a sibling leg's debt. This
audit asks the same question of every other reading of a desk opener against bills or collections.

## The audit (read from the code, before any measurement)

| Reading | Where | Unit of the journey | Unit of the bills/returns it reads | Same object? |
|---|---|---|---|---|
| INV_OVERDUE_WITHIN_BALANCE | `ev_overdue_within_balance` | household (`_households`, `_journeys`) | any leg owes (`_leg_owes` over every leg) | **yes** |
| INV_COLLECTIONS_EVENTS_ORDERED | `ev_collections_ordered` | household | none (event order only) | yes |
| INV_PLAN_REOFFER_FOLLOWS_A_MISSED_BILL | `ev_reoffer_follows_a_missed_bill` | household | `_bills_missed` + `_instalments_missed` over every leg | yes |
| INV_OVERDUE_WITHIN_PAGE_BALANCE | `ev_overdue_within_page_balance` | household's steps, deduplicated | sum of every fuel page's balance | yes |
| INV_NO_ARREARS_NOTICE_WHILE_THE_HOUSEHOLD_IS_IN_CREDIT | `ev_no_arrears_notice_while_in_credit` | each page's notice | sum of every fuel page's balance | yes |
| INV_HOUSEHOLD_PAGE_MISSED_BILL_WAS_NOT_SETTLED | `ev_page_missed_bill_unsettled` | household tally | `_unsettled_by` over every leg | yes |
| Working-day opener baseline (2,459 / 9 / 10) | `/var/tmp/grade-desk-bacs/grade.py` | account | **one leg's bills** | **no** (367378cb7) |
| **J1** and **J2** | `/var/tmp/grade-e50e/level_legs.py` | account (the same journey sits on `X` and `Xg`) | **one leg's level returns**; "all-level" decided per leg | **no** |

The gate's rows all group by `_households`, which keys on `billing_account_id` and falls back to the leg's own id.
A book that lost the id would make every dual leg its own household and bring the defect into the gate; that is
a property to hold, not a defect seen.

J1's script, read: for each ledger leg with any level collection it takes `fails` from **that leg's** payments,
and every journey in **that leg's** `collections_desk_journeys`. The desk's journey is the account's, so a dual
household's journey appears on both legs. An opening caused by the gas leg's return, or by the gas leg's
per-bill bill, is counted as an "off-return opening" on the electricity leg, and the same journey is counted
twice. The off-return samples it printed already show this: `PROS-2016-0067` and `PROS-2016-0067g` both open on
2019-10-17 at £34.97, each decided "a bill is unpaid past its due date".

## Pre-registration (seat executor, 16 Nov 2026, written before the household re-grade is run)

Re-grade J1 on e50e7b8f68's ledger (`/var/tmp/grade-e50e/ledger.json`, where 159 of 655 was filed) and on
8a300fa561's (`/var/tmp/grade-c915/ledger_8a30.json`), with the household as the unit: legs `X` and `Xg` are
one household; its journeys are deduplicated by (opening date, decision, overdue); its returns are the union of
both legs' failed level collections; "all-level" means every DD on every leg is level.

- **P1.** On e50e7b8f68 the deduplicated household openings are **at most 75%** of the 655 per-leg openings
  (dual households counted twice).
- **P2.** Household J1 on all-level households reads a **higher share than 159/655 (24%)**, but **below 95%**.
  The per-leg reading cannot be the whole of the 29 unexplained off-return openings named in the level-DD finding.
- **P3.** Of the 496 per-leg off-return openings, **at least 30%** sit on households that the household
  reading does not call all-level (a sibling leg is per-bill or mixed), so they leave J1's population.
- **Refuted if** the household reading moves J1 by less than 5 points: then the leg/household mismatch is not
  what keeps J1 low, and the cause is the desk's opener itself.

## Graded (seat executor, 16 Nov 2026, after the pre-registration above)

Scripts and output: `/var/tmp/grade-j1hh/` (`j1_household.py`, `residual.py`, `out.txt`). The per-leg reading is
reproduced exactly first (159 of 655 on e50e7b8f68), so the two readings run on the same bytes.

| | e50e7b8f68 | 8a300fa561 |
|---|---|---|
| J1 per leg, as filed | 159 of 655 (24%) | 89 of 269 (33%) |
| household openings, deduplicated (P1: ≤ 75% of per-leg) | 285 (**43.5%**) | 132 (49.1%) |
| J1 per household, all-level households (P2: above 24%, below 95%) | 146 of 285 (**51%**) | 82 of 132 (62%) |
| per-leg off-return openings that leave J1's population (P3: ≥ 30%) | 107 of 496 (**21.6%**) | 27 of 180 (15%) |
| household off-return openings after the household's last level collection | 97 of 139 | 37 of 50 |
| **J1 on openings inside the level span** (the leg as defined: "a level leg's journey") | **146 of 188 (78%)** | **82 of 95 (86%)** |

- **P1 held.** More than half of the per-leg openings were the same journey counted on both legs.
- **P2 held.** The household reading moves J1 by 27 points (24% to 51%), so the "refuted if under 5 points" leg does not fire.
- **P3 refuted.** Mixed households explain only 21.6%, not 30%. Most of the rest of the gap was not mixed legs. It was
  **openings after the household left level DD** (97 of 139; 37 of 50). J1 is about a level leg's journey, so those
  openings are outside it. They are D5's ground, the scheme's debit after leaving (`docs/design/LEVEL_DD_AREA_MAP.md`).
- **What J1 really reads.** On openings while the household was paying level, J1 is 78% on e50e7b8f68 and 86% on
  8a300fa561. That is still below the 95% filed, but the gap is 13 openings, not 180. Every one is decided "a bill is
  unpaid past its due date", and they sit on four households: PROS-2016-0374 (7), SYN-2016-525 (3), SYN-2016-048 (2)
  and SYN-2016-215 (1). That is the desk opening a level household on a bill's due date. The knowledge page says a level
  bill's due date is not an opener. These 13 are the J1 residual worth reading next. Use the household reading.

## What this changes

- **No gate row moves.** Every domain-invariant row that reads a desk journey against bills, returns or balances
  already groups by household (table above). INV_OVERDUE_WITHIN_BALANCE was the row named as suspect, and it reads
  "any leg owes" over every leg.
- **Two scratch instruments counted the wrong object**: the working-day opener baseline (367378cb7) and J1/J2 here.
  J2 ("journeys ≤ level returns per account") carries the same defect: it counts per leg, so a dual household's journey
  is set against one leg's returns. It was not re-graded, because nothing now pre-registers against it.
- **The class, for the next grader.** The desk's journey is the billing account's, and the ledger has no household key.
  A leg `X` and its sibling `Xg` are one household, so strip the `g` and deduplicate before you count. The runner's
  `_households` is the reference reading. A new grader should import it rather than re-derive it.

## Pre-registration: reading the 13 (seat executor, 16 Nov 2026, before any of the 13 is opened)

Each opening carries `days_overdue`, so the date its debt fell overdue is `on − days_overdue`. J1 calls an opening
"on a return" only if a failed level collection sits on the day before the opening.

- **Q1.** At least 7 of the 13 have a failed level collection on the household within 5 days of `on − days_overdue`:
  the desk opened on a return's debt, at a later step, and the error is J1's one-day window, not the desk.
- **Q2.** At most 3 of the 13 open on a bill whose household had no failed level collection in the 60 days before
  the opening: those are the desk opening a level household on a bill's due date, which the knowledge page forbids.
- **Refuted if** Q1 finds fewer than 4: then most of the 13 are not return-driven and the desk itself is the cause.

## The 13, read (seat executor, 16 Nov 2026, after the pre-registration above)

Reader: `/var/tmp/grade-j1hh/read13.py` on 8a300fa561's ledger. It prints each household's payments by method and its
bills' due dates in the 75 days before each opening.

- **Q1 refuted, Q2 held.** None of the 13 has a failed level collection within 5 days of `on − days_overdue`, so J1's
  one-day window is not the cause. But they are not the desk opening a level household on a level bill either.
- **12 of 13: J1's population is wrong, and the desk is right.** At the opening, one fuel leg of each household paid
  **by standard credit, not by level DD.** PROS-2016-0374g has been on standard credit since 2017-04-14 (7 openings;
  the first, on 2017-03-22, sits after that leg's last DD was returned on 2017-01-17 and none followed).
  SYN-2016-525g has been on standard credit since 2021-01-23 (3). SYN-2016-048's electricity leg has been on standard
  credit since 2023-10-29 (2). A standard-credit bill unpaid past its due date is the right opener. `residual.py`
  and `j1_household.py` both called these households "all-level". Their test asks whether every *direct debit* is
  level and whether every leg has *any* level DD ever. A leg that left DD for cash, and a leg that left in 2017, both
  pass. The household-level fix to J1 from earlier in this finding inherited that test, so its 82 of 95 counts these 12
  as failures. **Rightly scoped, J1 inside the level span on 8a300fa561 is 82 of 83.**
- **1 of 13: the desk opened on a return that the page does not print.** SYN-2016-215 is single-fuel and on level DD
  throughout. Its 2020-07-15 instalment of £162.80 has **no payment row** in the ledger. The desk opened on 2020-07-16
  with £144.07 overdue at 1 day, and the household repaid £162.80 on 2020-07-29, which the page hangs on the *June*
  collection as "repayment of a returned collection". That month's bill (33407) is a credit bill (−£56.33).
  `tools/generate_billing_ledger.py` (credit-bill branch, "returned, nothing crossed and the bill owes nothing, so no
  case opens") prints a level collection on a credit bill only when it succeeded. The desk and the household both
  acted on a return that the page dropped. Filed as its own finding:
  `SEAT_FINDING_A_LEVEL_RETURN_ON_A_CREDIT_BILL_MONTH_IS_DROPPED_FROM_THE_PAGE_THE_DESK_OPENED_ON_2026-11-16.md`.

**Done.** The J1 residual is spent. After both instrument corrections (household unit; a household is level only
while every leg it has is paying by level DD), the desk opened on a level bill's due date **zero** times on
8a300fa561. The one opening left is return-driven and invisible to J1 because the page dropped the return. No desk
change is indicated. The next grader should take "level" from the leg's payment method at the opening date, not
from whether the leg has ever had a level DD.
