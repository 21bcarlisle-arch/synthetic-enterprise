**Severity:** LATENT · **Lane:** D_billing_metering · **Epoch:** 4 · **Atom:** `unminted`

# The debt slot's "cleared while still owed" refusal fires on three households on b3ce2a4e73, two of them new (2026-11-04)

**Source.** The 85b044be54 grade predicted "both survive, no new one" (PROS-2020-0191, PROS-2025-0013); graded on the
b3ce2a4e73 book in `docs/staging/records/SEAT_RECORD_THE_B3CE2A4E73_BOOK_GRADED_AGAINST_ITS_FIXES_PREDICTIONS_2026-11-04.md`,
row (e). Of 374 households the debt rule matches, 3 are refused by `CLEARED_WHILE_OWED` ("its story says the debt is
cleared while its own balance at that moment is still owed past due"): **PROS-2020-0191, SYN-2016-066, SYN-2016-380**.
PROS-2025-0013 is no longer one. The slot is still filled (SYN-2016-217), so the page is not wrong; the refusal does
its work. The other refusal in the same fix, "overdue notice dated before the miss" (e28089f99, 2 -> 0), is 0 of 374.

**Why it is a finding.** The refusal is a check that the story's wording agrees with the account's own balance. When it
fires, the page's story generator and the desk's `cured` exit disagree on what "cleared" means: a journey exits
`cured` on "overdue balance cleared on the ledger", while the page balance still shows an amount past due. The 85b044be54
record carried the two older survivors as the same class and no ticket exists for it. **I cannot yet say** whether
the two new ones are the same mechanism as the first two; the book differs (different draw, different weather), so the
set is not comparable one to one. Not traced. The first measurement: for each of the three, the desk's `cured` date,
the ledger balance and overdue amounts that day, and the page's balance that day.

**Reverse:** delete this file.
