**Severity:** LATENT · **Lane:** D_billing_metering · **Epoch:** 4 · **Atom:** `D48_billing_accuracy_the_company_measures_what_it_billed_against_what_was_used` · **Item:** `the-estimated-bill-agrees-with-the-meter-on-the-built-book`

# INV_ESTIMATED_RUN_CONSISTENT_WITH_THE_METER on the f2c6979d01 book: 7 of 4,250, and one of them sits outside the exception's reason (25 Nov 2026)

Filed by the delivery seat. The 23 Nov publish of 6a588a832f was refused by this row at 9 breaches
against the exception's `max_breached: 8`. The f2c6979d01 publish (24 Nov) stopped at the bills/EPG
gate before it reached the domain-invariant gate, so this row had never been graded on that book.

## How it was graded, and the check that the grade is the gate's

The gate (`background/process_run_complete._domain_invariant_gate_permits_publish`) reads the ledger
and the printed customer files of a publish. f2c6979d01 never got that far, so neither exists for it.
I graded with the runner's own function, `tools/domain_invariant_runner.ev_estimated_run_vs_meter`,
over the run book's bills dressed as printed invoices. The dressing is
`tools/d48_spar_blend_counterfactual._Dressed`, with nothing re-billed, which is the book as billed.

**Control:** the same script on the 6a588a832f book
(`docs/reports/run_output_6a588a832f_20261120T134224Z.json`) gives **4,429 checked, 9 breaches,
33 flags**. That is the gate's own record in `docs/reports/domain_invariants.json` (git=6a588a832f),
and every listed breach has the same account, run and ratio to three decimals. On this row, the proxy
is the gate.

## Verdict on f2c6979d01

**4,250 runs checked, 7 breaches, 32 flags.** 7 is within the exception's `max_breached: 8`, so this
row does not refuse the f2c6979d01 publish. Fixing the bills gate (focus 1) does **not** move the
refusal on to this row.

| # | Account, fuel, run | Est./meter | Cause | Covered by the exception's reason? |
|---|---|---|---|---|
| 1 | SYN-2016-215 elec, 2021-06-01 to 07-31 (2 bills) | 4.27 | (a) electrically heated, summer estimated on the class shape | yes: named in the 5200cd6239 re-base |
| 2 | SYN-2016-215 elec, 2023-07-01 to 08-31 (2) | 4.15 | (a) | yes: named |
| 3 | SYN-2016-221 elec, 2021-06-01 to 07-31 (2) | 5.31 | (a) | yes: named |
| 4 | SYN-2016-565 elec, 2019-06-01 to 07-31 (2) | 4.66 | (a) | yes: named |
| 5 | PROS-2017-0364 elec, 2022-06-01 to 07-31 (2) | 3.65 | (a) | yes: named |
| 6 | PROS-2016-0203 elec, 2022-05-01 to 08-31 (4) | 3.37 | (a): uses 11.5 to 18.2 MWh a year, profile class 2, estimated May to Aug at 948/708/675/559 kWh against true 236/192/183/173 | yes by its cause (a two-rate electrically heated summer, as five of the eight were). The account is not named |
| 7 | **PROS-2021-0100 gas, 2021-08-01 to 12-31 (5)** | **9.48** | **not a shape cause. The registry AQ is 9,542.5 kWh; the meter takes a flat ~3.1 kWh/day (~1,150 kWh a year)** | **no** |

What 1 to 6 share: all are electricity, all above, all summer, all electrically heated homes
estimated on the profile class's average shape. That is the exception's cause (a), a lawful tail
under the published practice (`how_a_supplier_shapes_an_estimate_for_an_unread_month.md` s11). Cause
(c) (PROS-2016-0263g) and PROS-2017-0351 / PROS-2019-0302 do not breach on this book.

## Row 7, read off the bills

PROS-2021-0100 gas opened 2021-03-23. Its actual reads were Jun and Jul 2021 (94.1 and 97.2 kWh), so
the reads span 61 days, under `MIN_ADVANCE_DAYS` (182). The estimator therefore holds on the registry
AQ of 9,542.5 kWh, as the company's rule says it should. It bills Aug to Dec at 218/327/681/1,168/1,453
kWh (3,847 kWh, 25.1 kWh/day). The read that followed, 2022-01-31, closes at 988.155 against
410.947 on 2021-07-31. That is 577.2 kWh in 184 days, 3.14 kWh/day. The meter's true use is flat all
year: 94.11 or 97.247 kWh every month, which is 3.137 kWh/day.

Once the reads span enough (2022 onward), the estimator re-levels to the meter: 1,013 kWh billed in
2022 against 951 true. **So the estimator's rule is not the defect. Its input is.** A real gas meter's
AQ is Xoserve's, made from that meter's own reads ("based on the consumption between two meter
readings", cited at `company/billing/unread_month_estimate.GAS_AQ_MIN_ADVANCE_DAYS`). A meter drawing
~1,150 kWh a year would carry an AQ near 1,150, not 9,542. The world hands this premise an AQ about
**8x its own use**. This is the gas twin of the electricity registry-EAC defect that
`simulation/run_phase2b.register_legacy_premises_on_their_own_reads` fixed on 4 Nov
(BSCP504 s3.2.6.51), and that fix reaches electricity only.

There is a second, smaller misestimate on the same account. After re-levelling, the estimator still
spreads the year on the gas class shape (26 kWh in Jul, 172 kWh in Dec 2022) for a meter that is flat
all year. That is the exception's cause (b): the household's own shape is not known. It is not a breach
on this book.

## The control's weakness this exposes

The exception is graded by **count only**. On this book it passes 7 breaches against 8, and one of
those 7 (row 7) is outside the cause its reason licenses. A count-only exception can hide a new
defect behind a lawful one that left. I did not edit the register. Lowering `max_breached` to 7 would
license row 7. The downward move that keys the control to its reason is to 6, and that waits until
row 7 is fixed at its class.

## The class, and what is not yet measured

The class is a gas premise whose registry AQ is not made from its own metered use. How many accounts
it holds is **not established**. A crude census (registry AQ against true use annualised over billed
days) counts 49 of 422 gas accounts above 3x. That census is contaminated: several rows annualise to
3 to 50 kWh a year, which are void or missing-truth periods, not use. It is **not** a count to publish.
The census needs a denominator of occupied, metered days first.

## Handed on

The world build (sim lane): make each gas premise's registry AQ from its own reads, as the electricity
EAC now is. Write the knowledge page for Xoserve's rolling AQ first (UNC TPD G, AQ from reads 9 to 36
months apart). Its exit is row 7 leaving this invariant on the next fresh book, with the exception
re-based downward to the count its reason covers.

## Addendum, 25 Nov: did the company hold the home's own summers? Rows 1 to 6, account by account

**Question.** At the date of each estimate, did the account already hold actual reads over the same
calendar months in an earlier year? Read from `run_output_f2c6979d01_20261124T215935Z.json`, using
only what the company held then: the register advance between consecutive actual reads, before the
run's first month. A throwaway probe, not kept in the repo, rebuilt each account's read advances from
its bills (each actual bill closes an advance that runs from the day after the previous actual read)
and called `same_period_advance` and `estimate_unread_kwh` on them.

| # | Account, run | Held same-season advance (from, to, kWh/day) | Billed / meter as billed | Own history first (by hand) |
|---|---|---|---|---|
| 1 | SYN-2016-215, Jun to Jul 2021 | 2020-05-01 to 07-31, 10.2/day. The run's true rate is 5.8/day | 4.04 | 1.73 |
| 2 | SYN-2016-215, Jul to Aug 2023 | 2021-06-01 to 08-31, 5.5/day, and Aug 2022, 4.6/day. True 5.4/day | 4.18 | 0.94 |
| 3 | SYN-2016-221, Jun to Jul 2021 | June: 2020-04-01 to 06-30, 8.4/day. July: only Jul to Aug 2017, four years back | 5.04 | 3.93 |
| 4 | SYN-2016-565, Jun to Jul 2019 | 2018-03-01 to 06-30 (spring-heavy) and 2018-07-01 to 10-31, 7.0/day | 4.27 | 3.15 |
| 5 | PROS-2017-0364, Jun to Jul 2022 | 2021-05-01 to 08-31, 6.4/day. True 3.7/day | 3.09 | 1.68 |
| 6 | PROS-2016-0203, May to Aug 2022 | May: 2020-03-01 to 05-31. Jun to Aug: only 2018 May to Jun (four years back) and 2021 Apr to Oct (214 days, an annual-route span) | 3.69 | 3.99 |

The ratios here are per bill-run totals from the probe, not the runner's shaped meter. They sit within
about 0.3 of the table above.

**Answer.** Yes. Every account held some of its own summer, and rows 1, 2 and 5 held all of it. The
exception's reason, "the household's own shape is not known", is wrong for those three as stated.
The company held the shape and set it aside.

**The route that set it aside, and why.** In `company/billing/monthly_bill_assembly.py`, with
`bill_estimate_reads_the_annualised_advance` on (standing since 23 Oct), every unread month is
billed `annualised_advance_kwh(...)[0] * profile_weight(...)`. That is the read pair spanning nearest
a year, turned into an annual rate, then spread on the class shape. On PC2, each register is spread
on PC2's shape. The route was chosen because it beat the three-read window in 9 of 9 years. That
window carried autumn into December. But the route keeps nothing of the home's own year by
construction: an advance of a year has no season left in it. Section 11 of the estimate page judged
(a) lawful because OVO and settlement do the same. That holds for practice. It does not hold for
"not known".

**What was built.** `same_period_advance` and the switch
`DecisionPolicy.bill_estimate_reads_the_same_period_first`, default off. Knowledge:
`how_a_supplier_shapes_an_estimate_for_an_unread_month.md` s.5b. By hand, the rule moves rows 1, 2
and 5 inside the band. It leaves rows 3, 4 and 6, and makes row 6 slightly worse. Row 7 is gas with no
earlier year, so it is unchanged. The prediction for a book is pre-registered and has not been run.
