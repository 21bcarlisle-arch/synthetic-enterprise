**Severity:** LATENT · **Lane:** D_billing_metering · **Epoch:** 4 · **Atom:** `unminted`

# A level return's repayment line names a bill not yet issued on 58 rows (2026-11-12)

**Source.** Fix 1 of `docs/design/LEVEL_DD_AREA_MAP_2026-11-11.md` s.9, graded in s.9.1 on the 6fe7827ab2 run.
Ledgers and readers are in `/var/tmp/f1118` (`f45.py`, `f45.txt`).

**What the page holds.** The no-case level-return branch of `tools/generate_billing_ledger.py` now dates the
household's repayment on its cash day. On 58 rows that day is **before the receiving bill was issued**. The walk
(`simulation/arrears_engine.py`, `resolved_settlement`) netted older cash against a later return. One example:
OCC-6387bf64272ag's 2017-12-18 cash of 28.22 sits on a 2019-04-03 return. The page prints "Payment received
towards a returned collection" on 2017-12-18 under invoice 2965, a bill of 2019.

**What it is not.** It is not a balance defect: no balance moves at the book date (s.9.1 F5), and money in is now
on its day. Before fix 1 the same 58 rows were dated at the netting day, up to eight years late (SYN-2016-488g, 2017 cash
dated 2025-05-17). The defect is the label: which bill the money is said to pay.

**The fix (fix 1b).** At the no-case branch, cash whose `credit_period_end` predates the receiving bill's issue date
is neither appended nor added to `repaid_posted`. The catch-up loop then posts it once, on its cash day, on the
payment for the bill of its `settles_month`. Prediction to file before the build: rows before their bill 58 → 0, with
F1 to F6 of s.9.1 unmoved and the catch-up's rows +58 or fewer (same-day cash merges).

**Resolved (fix 1b, seat, 2026-11-12).** Built and graded in `docs/design/LEVEL_DD_AREA_MAP_2026-11-11.md` s.9.2:
rows dated before their return 58 → 0; no balance and no repayment total moved. The cut is the return's
`payment_date`, not the issue date written above. A level DD can be collected before its bill is issued, and
all 58 predate both.
