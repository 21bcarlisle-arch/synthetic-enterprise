**Severity:** LATENT · **Lane:** D_billing_metering · **Epoch:** 4 · **Atom:** `unminted`

# The collections desk never ran on five households the ledger dunned, one of them owing GBP475.32 past due (2026-11-03)

**Source.** Residual from `the-last-two-notices-before-the-miss-traced`, on the 0a6391d186 book. The method
and the change it followed are in `docs/market_research/company_debt_management.md`, "Where the desk runs,
its silence is a decision".

**What the published pages hold.** After the ledger's letters yield on every account the desk runs,
6 ledger letters (FIRST/SECOND_NOTICE) are left on the reaction chains of 752 households. All 6 are on
accounts where the desk has no journey at all, so the ledger is the only narrator there:

| household | ledger | home owed past due on the letter's date |
|---|---|---|
| PROS-2024-0010 (electricity) | DD returned 17 Jan 2025, GBP475.32; first notice 24 Jan; second notice 14 Feb | GBP475.32 |
| PROS-2023-0325 (gas leg) | DD returned 18 Jun 2025; first notice 25 Jun; repaid 2 Jul | GBP29.37 |
| PROS-2024-0012 (electricity) | DD returned 20 May 2025; first notice 27 May; repaid 3 Jun | in credit (GBP-474.75) |
| PROS-2025-0013 (electricity) | first notice 30 Jun 2025 | GBP9.74 |
| PROS-2025-0042 (electricity) | first notice 30 Jun 2025 | GBP18.05 |

All five are `PROS-*` accounts, but the desk does run on other `PROS-*` accounts (PROS-2018-0137 has journeys), so the prefix alone does not explain it.

**Not established:** why the desk opened no journey on PROS-2024-0010 while GBP475.32 was owed past due
for at least four weeks. The candidates are:
- the desk's walk stopped before the book's ledger clock;
- the account is not in the desk's ledger book (a prospect-cohort account billed by another path);
- a plan or a credit on another account the desk reads.

A desk that stays silent on a real debt is an SLC 27 contact duty not discharged. A ledger letter
sent over a home in credit (PROS-2024-0012) is the class already fixed on desk-run accounts.

**Probe.** Run from the repo root: load `tools.generate_explore_cast` households, and for each
`arrears_first_notice`/`arrears_second_notice` left on a reaction chain with no `collections_` event,
print `_owed_past_due(ev, date)`.

**Done means:** each of the 6 is traced to the desk's own walk, and either the desk opens where it
should (with a test that reds today) or the account is shown not to be the desk's, with the cause
recorded on the knowledge page.
