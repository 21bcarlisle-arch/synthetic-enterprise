**Severity:** LATENT · **Lane:** D_billing_metering · **Epoch:** unassigned · **Atom:** `unminted`

# Three small exceptions traced on the 209c3350ab book: movers' DDs, held bills, and the revenue row's classes (2026-10-29)

**Item:** `the-small-open-exceptions-get-their-causes` (Lane 0, under
`docs/staging/advisor/DIRECTOR_RULING_CORRECTNESS_BEFORE_THE_NEXT_FEATURE_2026-10-26.md` step 4).

**Book.** The fresh 209c3350ab run (`/var/tmp/fresh-run-out-209c3350ab`, ledger `/var/tmp/wo-grade-209c/ledger.json`).
Its page records were rebuilt in memory with origin 1ba034b9c8's code by the grade script that set these
ceilings (`/var/tmp/fresh-run-0b28-scripts/grade.py`, stopped before `R.run` and pickled). The three rows were then
graded with origin's own evaluators. Probes: `/var/tmp/smallexc/{grade3,p1trace,p1class,p2,p2b,p2c,p3}.py`.

## 1. INV_PAYMENT_RECORD_RECONCILES_TO_COLLECTIONS_DUE: two defects, both a mover's, both fixed

**On origin the row reads 35 on this book, not 6.** dae9f598d9 (one definition of a missed payment: missed from the
day after the due date, not 30 days later) landed after the grade that set the ceiling. So the 6 were the part of a
larger class that the 30-day window hid. Every breach is on the "missed DD without a return" leg: 38 bills on 35
accounts, and **every one of them is a mover's** (`p1class.py`, against `per_customer_behavioral.moved_out_on`):

| class | bills | what happened |
|---|---|---|
| the final bill | 17 | the exit model's PAID_LATE kept its days late (3 to 77) on a DD leg, so a DD was "collected" late with no return |
| the bill before the final | 21 | `LivePaymentTriad.record_period` asked `arrears_engine.mover_final_bill_outcome` with the bill's **due date**, where the rule reads the **period end**. A bill for the month before the move is due in the move month, so it was drawn as an exit too |

The six accounts the exception named are all here. PROS-2016-0042g, PROS-2019-0356g and SYN-2016-603g each have
the bill before the final. PROS-2018-0222g and SYN-2016-390g have both bills. SYN-2016-013 has its final bill
(one bill, due 15 Feb 2016, paid 2 May). **`A_DD_IS_NEVER_LATE` misses one path, the exit model.** Its own
`payment_outcome` is whole. No breach on the row is a stayer's.

**Fixed** (knowledge: `payments_and_direct_debit_2026-10-25.md`, "A DD is never late", amended in the same commit):
- `mover_final_bill_outcome` returns a paid final bill on a DD leg as collected on its date (`days_late` 0). Paid or
  not is unchanged;
- the triad asks the exit model only for the bill whose month reaches the last supplied day's. The due date stays
  the seed key, so the true final bills' draws do not move.

Tests: `tests/simulation/test_a_movers_dd_is_never_late.py`, red on origin, green with the fix. The partition control:
a pay-on-receipt mover does pay late, so the late branch is reachable.

## 2. INV_BILLED_EX_VAT_RECONCILES_TO_REVENUE: the 24 assigned, one class new and one not traced

The R2 note's rule, applied to the 24: each account goes to the month where its page bills (before VAT, plus EPG)
and its settlement revenue part most. Then (b) if estimates follow the last actual read, and (d) if the ledger
holds a bill (`p2.py`, `p2c.py`).

| class | n | accounts |
|---|---|---|
| (a) a catch-up at the actual read that does not net the run back to settlement | 14 | OCC-1a3fe25a0372g, OCC-2e29bf263cb4, OCC-6b934fa268b1, PROS-2016-0349g, PROS-2017-0187g, PROS-2017-0233, PROS-2017-0249g, PROS-2018-0002g, SYN-2016-077, SYN-2016-153g, SYN-2016-304g, SYN-2016-468, SYN-2016-469g, SYN-2016-542g |
| (b) estimates no actual read corrected | 1 | PROS-2017-0117 (5 estimates after its last actual; gap 995.10 on R 3,143.96) |
| (c) a part-month first bill | 2 | PROS-2020-0248, SYN-2016-507g |
| (d) NEW: bills held in the ledger's exception queue | 1 | PROS-2025-0106. April and May are held (cause in 3 below), and June is billed alone |
| (e) NEW: no catch-up on the account, last bill on an actual read, billed kWh 1.5 to 4.7% off settled | 6 | PROS-2016-0370, PROS-2024-0321, SYN-2016-236, SYN-2016-360g, SYN-2016-395g, SYN-2016-477g |

Within (a): on SYN-2016-469g, SYN-2016-153g, PROS-2017-0233 and PROS-2025-0106, billed kWh with the catch-up equals
settled kWh to 0.0%, so their whole £ gap is price. The catch-up's kWh are billed at the catch-up bill's rate, not
at the rates of the months the energy was used (469g: 22,462 kWh caught up in Oct 2018 for use since Oct 2016,
+32.59). On the other (a) accounts, the `catchup_kwh`/`catchup_direction` fields do not reconcile the volume
(OCC-2e29bf263cb4 bills 104% more kWh than settled and less £). **What (e) is, and that (a) volume, are not traced.**
These 7 accounts carry gaps of 1 to 2% of R. The row's ceiling stays at 24.

## 3. INV_CARBON_PANEL_KWH_MATCHES_USAGE_PANEL: bills held and never released

Traced (`p3.py`). All 6 checks are bills the billing ledger holds in `exception_queue` on the 209c book, 7 entries
on these three accounts and no others:
- PROS-2024-0010: Jan and Feb 2024;
- PROS-2025-0106: Apr and May 2025;
- SYN-2016-582: Dec 2016 to Feb 2017.

Each is held by two checks in `company/billing/pre_bill_validation.py`:
- `vat_by_segment`: the load implies a business VAT rate (`check_vat_consistent_with_consumption`);
- `slc_6_7_billing_accuracy`: the load is outside `RESI_CONSUMPTION_ENVELOPE_ELEC_MONTHLY`.

The households use 1,290 to 2,480 kWh a month, about 79 kWh a day, which is electrically heated homes. The usage
panel sums the run's settlement bills (`generate_customer_consumption._monthly_from_bills`, "real settlement
consumption"). The carbon panel sums the bills the ledger issued (`generate_explore_carbon._billed_by_year`). So
a held bill is on one panel and not the other. **The defect is that nothing ever works the queue.** A real supplier
reviews a held bill and issues it. Here it stays unbilled for good. A domestic supply is 5% VAT at any volume (the
de minimis applies to business use), so the VAT hold on a resi account is a mislabel screen that needs a person to
clear it.

**The exception's `retired_by` pointed the wrong way.** The row itself says both panels should count energy used
(CO1). So the usage panel is the right one here, and the remedy is the queue working, not the usage panel reading
issued bills.

**Leg 3, graded for the first time** (from the 209c `site/data/explore_carbon.json`, outside the runner, which does
not carry `full_year`). Of 5,564 billed fuel-legs:
- 1,621 print a `co2e_kg` in a part year (`full_year` false or `months_billed` < 11), each a **breach**;
- 668 part-year legs correctly print none;
- 3,085 full-year legs print a figure, and 190 do not (grid intensity not established).

The year's `total_co2e_kg` is also printed on some part years (C2 2018: 1,681.97 with `full_year` false). Leg 3
is an open defect of the panel. Fixing it is a change to what a public page shows, so it is knowledge-page-first
(K8). It is filed here, not built.

## For the next fresh run (pre-registered)

`docs/staging/records/SEAT_PREREGISTRATION_A_MOVERS_DD_IS_NEVER_LATE_ON_THE_NEXT_FRESH_RUN_2026-10-29.md`.

## What is open after this

1. The exception queue is never worked. That covers 3 accounts here (item 3, and (d) in item 2). This finding
   names it, and no atom is minted.
2. Leg 3 of the carbon row: 1,621 part-year figures. The panel needs its knowledge page first.
3. (e) and the volume side of (a) on the revenue row.

## 2026-10-30: leg 3 of the carbon row built (worker, `worker/carbon-leg3`)

Item 2 above is built. The knowledge page came first: `household_carbon_and_the_measures_that_save_it.md`
§6a. A fuel leg billed for fewer than 12 months now prints its kWh and months, `co2e_kg` null, its own
`full_year` and a reason naming the months; its grid-loss line is null too, and a year with any
part-year leg prints no total. The `Leg` keeps its kg, so nothing that sums a book's emissions moves.
The page renders "no figure for a part year", not "not known". `ev_carbon_matches_usage` grades leg 3: a kg beside
`full_year` false, or beside fewer than 11 months, breaches (a panel from before the field is graded on
its months). Controls: `test_a_part_year_leg_prints_no_figure_and_its_year_no_total` and
`test_leg_three_of_the_carbon_row_breaches_a_part_year_that_prints_a_figure`, each red under its
mutation. **Prediction, filed before the run:** on the next fresh run, leg 3 breaches 0, and the row
stays at the 6 held-bill checks of legs 1 and 2. Item 1 (the queue never worked) is not touched.
The exception's reason in `DOMAIN_INVARIANT_EXCEPTIONS.yaml` still says leg 3 is graded outside the runner.
It was not edited here because the seat's live claim holds that file. Its next edit should take the leg-3 sentence from this section.
