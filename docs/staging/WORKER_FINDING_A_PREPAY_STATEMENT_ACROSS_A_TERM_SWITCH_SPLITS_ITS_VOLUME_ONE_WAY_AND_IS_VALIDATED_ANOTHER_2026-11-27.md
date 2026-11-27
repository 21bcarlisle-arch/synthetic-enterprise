**Severity:** LATENT · **Lane:** D_billing_metering · **Epoch:** 4 · **Atom:** `D48_billing_accuracy_the_company_measures_what_it_billed_against_what_was_used`

# A prepayment statement that spans a term switch splits its volume one way, and is validated another

*Autonomous worker, 2026-11-27. Found by `python3 -m background.post_publish_readers --run` on the live
book 601887d76a (04:07Z, 45 files, `rc=1`). That run was the first grade of this book: the store's last
run had graded 6af7fd0bf.*

## Measured

There is one red: `tests/tools/test_the_validator_checks_the_printed_rate_against_the_contracted_tariff.py::test_the_published_book_charges_its_contracted_tariff`.
Every other `unit_charge_at_contract_gbp` claim on the book agrees. One disagrees:

- **PROS-2023-0135, prepayment statement 19569, electricity, 2025-06-01 to 2025-06-07** (7 days, 38.9 kWh).
  Its `contracted_terms` are an SVT term at 24.949 p/kWh until 2025-06-05, then a fixed term at
  19.6518 p/kWh from 2025-06-05.
- The validator says £8.81, from 22.0 kWh × 24.949 + 16.9 kWh × 19.6518.
- The biller printed £8.61, a difference of −£0.20. The tolerance is £0.065.
- The two sides agree on both rates and on the total volume. They disagree only on **how the volume
  is split across the term boundary.** £8.61 needs roughly 18.2 kWh on SVT and 20.7 kWh on fixed. A
  pro-rata split by days (4/7 and 3/7) gives about £8.82, which is the validator's side.
- May 2025 on the same account agrees to £0.01, on a single term.

## What is not yet known

I cannot yet say which side is right. The biller may split on interval reads, which would be the
real consumption either side of the switch. The validator may split on a day-weighted or
read-estimated basis. Either way, the two readers answer "how much was used before the switch" by
different routes, and the control is keyed to one of them. Before deciding, answer two questions:

1. What does each side's split rest on?
2. Can a supplier observe that split? (A prepayment meter with a smart register can. A traditional
   one cannot.)

A count of the class is the cheap first step: every bill on the book whose `contracted_terms` holds
more than one term. Only one such bill disagrees today, but a split defect would show only where the
usage either side of the boundary is uneven, so most of the class would agree by chance.
