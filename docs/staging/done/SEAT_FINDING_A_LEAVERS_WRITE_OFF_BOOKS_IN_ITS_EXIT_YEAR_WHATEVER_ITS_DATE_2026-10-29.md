**Severity:** LATENT · **Lane:** D_billing_metering · **Epoch:** 4 · **Atom:** `unminted`

# A leaver's write-off books in its exit year in the P&L, whatever date it carries

Measured on two fresh books on 2026-10-29 that differ by one variable, the world's
`WRITE_OFF_DATE_CONVENTION`: `fresh-run-0b2879ef7d` (`final_bill_due_date`) and
`fresh-run-209c3350ab` (`company_closed_account_write_off`, a year after the final bill, from
2b70102f9e).

## What is measured

- `p2b__arrears_lines_by_customer`: identical on every key for all 1,293 customers.
- `management_accounts[*].income_statement.bad_debt_gbp`: identical in every year 2016–2025.
- `bad_debt_gbp` summed per (customer, settlement year) over `p2b__all_records`: 0 of the pairs differ.

So moving every leaver's close write-off a year later moves nothing in the P&L. 2b70102f9e says the
page, the P&L and the desk all read the one date. On this evidence the P&L does not.

## Likely mechanism (not established)

`simulation/arrears_engine._row_for` books a (customer, year) figure dated after the account's last
settlement year on that account's last record. A leaver has no records after it leaves, so its
write-off books in its exit year under either convention. Its docstring calls this deliberate,
because dropping the figure was silent. `BAD_DEBT_BASIS` is "write-offs only, no provision", so
booking a write-off before the company takes it is in effect a provision under a write-off's name.

## Open

Which is right is a knowledge question before it is a code one (K8). Either the P&L recognises the
write-off in the year the company takes it, which needs a row to book on after exit, or it
recognises the expected loss at exit and says so (a provision basis, `debt_and_collections.md`).
The next step is to read `_row_for`'s callers and the provisioning section of the knowledge page,
then state which one the P&L means. Probe: `/var/tmp/wo-attr-0b28-scripts/attr.py`. Record:
`docs/staging/records/SEAT_PREREGISTRATION_ONE_WRITE_OFF_DATE_FOR_A_LEAVERS_DEBT_ON_A_FRESH_RUN_2026-10-29.md`.

## Done (2026-10-29)

Established, one probe (`/var/tmp/wo-year-probe/probe.py`, both books): `_row_for` is why
`bad_debt_gbp` is identical. All 143 leavers with a close write-off (£11,866.17) are dated after
their exit year under the company's date, and all 143 book in it. Under the final-bill due date,
12 (£455.42) were already after it and booked there too. The recovery (£1,447.60, 12.2%) is also
dated later, so it books in the exit year. The net charge is 87.8% of the closing balance, which is
Centrica's final-bill coverage.

Decided: the P&L books an **expected loss at close** (a provision, which is IFRS 9 practice and
Ofgem's charge basis). The write-off date derecognises the balance, and only the page and the
desk read it. Stated in `docs/market_research/debt_and_collections.md` s.7.4. Section 7.3's
sentence saying the P&L reads the date is corrected beside the claim. `BAD_DEBT_BASIS` no longer
says "write-offs only". No P&L figure moves: the behaviour was right and its name was wrong.
