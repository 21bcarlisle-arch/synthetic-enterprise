**Severity:** INFORMATIONAL (answered 2026-10-26: the duty fires; was LATENT) · **Lane:** D_billing_metering · **Epoch:** 4 · **Atom:** `unminted`

# A third of households go more than a year on estimates without the read duty firing

Defect 4 of the director's Explore steer. Measured on the published 4ae8da9b0f book.

## What is wrong

- **250 of 752** households have at least one bill dated more than 365 days after that fuel's last
  actual read.
- The home page says the supplier "instructs a meter visit when a year passes on estimates, as the
  read duty requires (SLC 21B.4)".
- The published example SYN-2016-587 had 33 estimated bills in a row, with no read from 30 Apr 2021 to
  29 Feb 2024.

## Open question

The run instructs visits (`company/billing/read_duty_register`, `company/policy/decision_policy.py:238`).
So the question is whether the visit is instructed and then fails to produce a read, or is never
instructed for these accounts. That decides whether the capability claim or the record is wrong.
Re-measure it on a run that carries the register.

## Second question, from the same example

SYN-2016-587's catch-up after 33 months of estimates was £7.03. That is too exact. Check whether the
estimate is fed the true consumption. If it is, it breaks the epistemic wall.

## What catches it now

The estimate-trap slot ranks only runs within the read-duty year. This run shows PROS-2017-0264: 12
gas estimates since joining, then a read and a £45.43 credit.

## Answer (delivery seat, 2026-10-26, on the fresh book)

**Correction, beside the claim above:** the duty does fire. "Without the read duty firing" was wrong.
The 250 households were a year on estimates, but that is not a duty unmet. SLC 21B.4 asks for
reasonable steps, not an outcome, and the company took the step on every one of them.

The book is `/var/tmp/mandate-run-out-67a893e749` (arm A, origin 67a893e749). No new run.
Method: bills grouped by (customer_id, commodity). For each leg, find the first bill dated more
than 365 days after its last actual read, then look at the bills in that window.
Script: `/tmp/rd/measure.py`, which is not kept, so the method is set out here.

**Denominator: 279 fuel legs** (279 households) with such a bill.

| branch | legs |
|---|---|
| instructed, visit sent, visit read nothing (`no_read`) | **261** |
| not instructed: electricity prepayment, outside 21B.4 by 21B.3 | **18** |
| not instructed, duty applies | **0** |
| instructed, visit not sent | 0 |

The same answer at bill level, per 12th estimate in a row: **431 duty-applying rows, 431 carry the
instruction**. That is 212 electricity DD, 39 electricity standard credit, 159 gas DD, 21 gas standard
credit, and the 25 gas prepayment rows (UNC M5.9.14). The 30 electricity prepayment rows carry no
instruction, which is correct.

**Which branch fails: neither, as code.** The company instructs (`read_instruction_due`, the 11th
estimate). The world sends the visit. The visit cannot read, because its outcome is
`q6_read_visit_access_failure_rate`, a published GAP left null. Under null, the `register` arm reads no
visit by construction (`simulation/meter_reads.must_read_reads`; first found in
`records/WORKER_RESULT_EVERY_RUN_OF_TWELVE_ESTIMATES_..._2026-10-22.md`). The 115 instructions that
show `actual` are ordinary reads that arrived in the visit month.

**Why the null visit is not the world's error, and why it is not filled.** The world's ordinary read
rate is solved to `q2_no_read_12m_share`: Ofgem's "just over 7%" of domestic credit customers with no
actual-read bill in 12 months (16 Nov 2017), and a median supplier at 5.2–5.6% (5 Mar 2018). That
figure is the outcome of real suppliers' whole read effort, their visits included. Measured on this
book, credit resi legs on supply all year, December snapshots:

| Dec | 2017 | 2018 | 2019 | 2020 | 2021 | 2022 | 2023 | 2024 |
|---|---|---|---|---|---|---|---|---|
| unread 12m | 5.5% | 8.1% | 6.7% | 7.0% | 5.9% | 4.3% | 5.4% | 4.8% |

So the book sits on the published outcome. Giving the visit a read rate as well would count real
visits twice and push the snapshot below the record. "A third of households" is a ten-year *ever*
rate. A 5–8% snapshot produces it, and Ofgem publishes no ever-rate to grade it against.

**What stays open (GAP, not built).** The world spreads reads memorylessly. In reality visits are aimed
at the unread, so real long runs are probably shorter, and the share would be carried by more short
gaps. No published run-length distribution was found beyond Elexon's 30/60/80/97% read at
2/4/7/14 months (`q2_persistent_unread_share`). Whether one visit a year is "all reasonable steps"
or a supplier re-attempts after no access is a practitioner question (q6's own note). It would move
reads only once q6 has a value.

**What changed.** Each 21B.4 row now says whether the step was taken (`step_taken`), and
`read_duty_summary` publishes `rows_without_step` per fuel. On this book it is **0 electricity, 0 gas**.
`tests/company/billing/test_the_company_instructs_a_read_before_the_21b4_year.py::test_a_year_on_estimates_with_no_step_is_counted_and_one_with_a_failed_visit_is_not`
goes red when a leg is left a year on estimates with no step (4 rows counted with instructions off),
and it is mutation-proven three ways. The home page's claim stands, and the test is already on its
`data-test` list.

## Second question: SYN-2016-587's £7.03 — no epistemic-wall breach

- The run is 33 estimates, May 2021 to Jan 2024. It billed **4,986.2 kWh against 5,101.4 kWh true
  (−2.3%)**.
- Monthly errors run from −43.6 to +27.9 kWh. The billed months repeat exactly each year (132.0,
  122.5, 123.4 … kWh): the annualised advance × the seasonal profile
  (`unread_month_estimate.annualised_advance_kwh`, `profile_weight`). It is fed from `register_reads`,
  which `monthly_bill_assembly` appends only on an actual read.
- Truth enters only `_annotate_billing_basis` (grading fields) and the catch-up once an actual read
  arrives, as the module's own epistemic note says.
- The raw catch-up was **£21.03**. SLC 21BA barred 76.6 of the 115.1 kWh (consumption more than 12
  months back, no customer fault), so **£14.00 was written off and £7.03 charged**.
- "Too exact" is a stable household whose own reads predict it to 2%, then cut by two-thirds by the
  back-billing cap. Nothing is BLOCKING.
