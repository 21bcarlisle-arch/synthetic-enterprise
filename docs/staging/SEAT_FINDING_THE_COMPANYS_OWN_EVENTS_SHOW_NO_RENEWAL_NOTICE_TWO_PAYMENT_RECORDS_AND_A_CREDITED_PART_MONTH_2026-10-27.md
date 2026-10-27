**Severity:** LATENT · **Lane:** D_billing_metering · **Epoch:** 2 · **Atom:** `unminted`

# The company's own events show no renewal notice, two payment records, and a credited part-month

This came from giving four of the six ungradeable cold-read rows evaluators on the company's dated
acts (item `the-six-cold-read-rows-read-the-companys-own-events`). The grade and the cause behind
every count are in
`docs/staging/records/SEAT_PREREGISTRATION_THE_SIX_COLD_READ_ROWS_ON_THE_2EEB3F0B3_BOOK_2026-10-27.md`.
Each defect is excepted, capped at its count, in `docs/design/DOMAIN_INVARIANT_EXCEPTIONS.yaml`.

1. **No end-of-fixed-term notice is ever sent.** `company/crm/renewal_notice_register.py` implements
   SLC 22C's 42-49 day window, and nothing in the run calls it. The company's only dated renewal
   act is the retention offer, made on the day the term ends. On the 2eeb3f0b3 book, all 1,338 of
   1,338 fixed terms breach: 163 offers at 0 days, and 1,173 terms with no act at all. This is the
   class behind O6. The fix is to wire the register into the run, so every fixed term gets a dated
   notice 42-49 days before it ends, and to have the offer precede or accompany that notice.
2. **The collections desk and the billing ledger keep two payment records.** On 1,987 of 7,151
   occasions (27.8%), a journey opens on "a bill is unpaid past its due date" where the billing
   ledger shows every bill due by then collected. SYN-2016-356 opens on the 29th each month, while
   its bills fall due on the 14th to the 19th. Which record is wrong is not established. The
   prediction is that the desk reads the DD collection book's schedule. The statute bar's 24
   early write-offs look like the same split: a final bill paid after the account closed restarts
   the six years in the billing ledger, but not, apparently, on the desk.
3. **A joiner's first part-month is credited the EBSS on the named-household path.** Five PROS
   joiners, each traced, were credited for the month they joined mid-way. Guidance 5.4/5.8 gives
   that month's credit only to whoever held the account at 00:00 on the 1st, and the occupier path
   already credits nothing. That is two homes for one rule. The fix is one EBSS eligibility home.

Not done here: the estimate-run check on the generated customer page (point 2 of the source
finding). It is the next increment of the same item.
