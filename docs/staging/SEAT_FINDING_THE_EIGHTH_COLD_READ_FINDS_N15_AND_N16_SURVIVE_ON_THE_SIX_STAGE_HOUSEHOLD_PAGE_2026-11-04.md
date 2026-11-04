**Severity:** LATENT · **Lane:** D_billing_metering · **Epoch:** 4 · **Atom:** `unminted`

# Two classes fixed on the cast still print on the six-stage household page: the tariff label (N16) and a bill tally that counts credit-settled bills as missed (N15) (2026-11-04)

**Source.** Reader objections O4, O33 and O34 in the eighth cold read
(`records/SEAT_READING_THE_EIGHTH_COLD_READ_ON_THE_B3CE2A4E73_BOOK_2026-11-04.md`), confirmed by the seat on the
b3ce2a4e73 pages. These are not new classes. Each fix covered one surface, and the page has another.

**N16 on the household page (O33, O34).**
- The reader read "one supplier's SVT moves like a monthly tracker". It cited 10.11p in June 2016, 11.44p in
  April 2016 and 13.33p in November 2016.
- PROS-2016-0187 and SYN-2016-185 are billed on **fixed** terms (`term_tariff_type: fixed` on every bill read).
  SYN-2016-185's is a prepayment statement.
- Both pages carry `tariff_name: "Standard Variable (Electricity)"`. That is an account-level name, not the term
  in force.
- d14ff599e made the Explore cast print the billed term. The six-stage page still prints the account's name.
- Unconfirmed: SYN-2016-185's "fixed" prepayment rate moves from 6.24p to 7.15p (energy) between April 2016 and
  April 2017, with no renewal on record.

**N15 on the page's bill tally (O4).**
- The renewal slot prints "Direct debit … 76 of 83 bills paid, 0 returned, 7 missed". The estimate trap prints
  "19 of 22 bills paid, 0 returned, 3 missed".
- SYN-2016-592's record has one failed payment. Its other non-PAID bills are CREDITED (credit bills) or
  SETTLED_BY_CREDIT (paid down by an earlier credit).
- The page counts those as "missed". That is N15's cause: a bill settled by credit read as unpaid. ba868134c fixed
  it in the desk, and the page's tally still carries it.

**The rows these owe (ruling step 6).**
- Blind from the tariff pages: the tariff a household page prints at a date agrees with the billed term at that
  date. That is the N16 row widened from `explore_cast.json` to the household pages.
- Blind from `company_debt_management.md`: a bill counted as missed on a page has neither a payment nor a credit
  that settled it in its window.

**Reverse.** Delete this file. Nothing outside `docs/staging/` was touched.
