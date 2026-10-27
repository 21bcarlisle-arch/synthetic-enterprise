**Severity:** LATENT · **Lane:** D_billing_metering · **Epoch:** 4 · **Atom:** `unminted`

# The first cold read finds page arithmetic that does not reconcile, and a margin nobody defined

These are the first cold read's objections that are **not a range checkable on every household**
(record: `docs/staging/records/SEAT_RECORD_THE_FIRST_COLD_READ_ON_THE_4AE8DA9B0F_PAGES_2026-10-27.md`,
run 4ae8da9b0f). The range-shaped ones went to `DOMAIN_INVARIANTS.yaml`. The reader saw only the
rendered page. Quotes are the page's own text.

## Wrong in the world, or on the page as a fact

- **O25, an undefined "gross margin".** Gross is 41–66% of revenue on all six random accounts,
  where GB pass-through puts it at about 10–20%. "Net after cost to serve" is not gross less cost to
  serve: for OCC-f6813bf9f05e, £4,776.92 − £477.25 ≠ £854.29. **Say what "gross" counts before
  anything differences it.** It is likely revenue less wholesale only, with network and policy
  unnamed in between. Same class as *net margin* in CLAUDE.md.
- **O13, a bill with nothing owed.** PROS-2025-0022's first bills total £186.20 with "0 payments"
  and "Nothing owed". Balance ≠ billed − paid.
- **O26, "Paid in total" equals "Revenue billed".** It does so on every account, where stage 5's
  ledger shows less collected (OCC-52fbc3104c5f: collected £4,747.99 against paid £5,062.23).
- **O27, frozen balances never chased.** A balance owed is held flat for two years with no debt
  stage (OCC-f6813bf9f05e at £399.99). Payments equal each invoice 14 days later, which is pay on
  bill, while the page says "a flat monthly amount".
- **O8, true churn at exactly 0.0%.** This is on the world side. PROS-2017-0049 and SYN-2016-031
  show 0.0% at fix ends. Home moves alone make it non-zero. The "CONTENT" household also sits at
  86.2%. The floor is a world question (GAP: no commons rate for moves).
- **O30, a first part-year too low.** OCC-f6813bf9f05e's first quarter is 750 kWh of gas for a
  9,600 kWh/yr home. The Xoserve ALP share is not in the commons (GAP), so this is not yet a row.
- **O4, SVT electricity below the cap.** Feb–Mar 2025 electricity bills sit about 6% under the cap
  while gas sits on it. This is lawful under the cap, but it reads as missing VAT. Whether SVTs were
  priced at the cap is for `svt_rates_active_passive_2016_2025.md` to settle.

## Misleading or cosmetic page copy

- O7: the renewal EV of £26.15 = £113.18 − £87.03, and never applies the 85%. Also, 8% costing £87
  implies a term bill of about £1,088 for a home billing about £2,400 a year.
- O9: a 2024 moment labelled "at the 25 Jan 2019 renewal". O11: a "renewal" on an SVT account, and
  "off by 5.0%" given for percentage points.
- O12: "Three months in" is two months in. O15: "£45.43 credited" against the bill's "£33.57
  credit", with the electricity leg still estimated on the same read date.
- O20, O21: life events after supply ended, a 2024 customer page for a household gone since 2018,
  and "Income stress low" beside 40 missed payments.
- O23: "use did not explain the change" when use rose 18%. O24: a 2021 payment line repeated in
  2022.
- O28: the account header's bill count is one fuel's count. O29: gas–weather r is computed over
  part-years, giving r = −0.30 beside "heating-dominated".
- O32: electricity day-clock text on gas-only smart accounts. O33: three book sizes (752, 707, 1291)
  with no units. O34: bill lines split energy from "Network & environmental", which no GB bill
  does. O35: one p/kWh averaged across both fuels.
- O37: the mover slot's "What closes it" reads as if already done.

## What closes it

O25 first, because it is a definition: write what gross, net and cost to serve each count on the
page that prints them. O13, O26 and O27 are one ledger reading and can likely become an
`INV_BALANCE_IS_BILLED_LESS_PAID` row once the export carries a dated balance. The copy items are
one pass over the cast and stage generators.

## O26, O13, O27 and O25: causes and fixes (2026-10-27, delivery lane)

**The ledger was right about payment and the page was wrong.** On all 1,291 published accounts the
invoices sum to the ledger's raised amounts, and the ledger's balance is the sum of its entries.

- **O26: the page read the wrong field.** `stageJudged` summed each leg's `revenue_gbp`, which is
  the supplier's ex-VAT settlement revenue, and printed it as "Paid in total". It now reads the
  payment ledger (`judgedFigures` in `site/explore/index.html`): billed (VAT included), paid,
  government credit, write-off, and what is owed on the ledger's date. The rows foot.
- **O25: two clocks were mixed and one row was missing.** "Gross margin" was the household's two
  legs, but "Cost to serve" and "Net after cost to serve" were the electricity leg's alone. Nothing
  printed net. Now every figure is summed over every leg, and the column reads: revenue before VAT,
  less wholesale energy, gross margin, less network, policy and capital, net margin, less cost to
  serve, net after cost to serve. The page says what each one counts. Gross is revenue less
  wholesale only (`simulation/hedged_settlement.py`), which is why it runs at 41–66%.
  **Still open:** cost to serve is charged per leg, so a dual-fuel home carries two. The page now
  says so. Whether that is right belongs to B13.
- **O13: two clocks for one bill.** The invoice is dated at its period end, and the ledger raises
  it on issue a few days later. The cast read the balance from the ledger alone, so at a first-bill
  moment it showed the bills and "Nothing owed". `_owed` in `tools/generate_explore_cast.py` now
  takes the bills the page shows, less every other ledger movement known that day. On the published
  book, 7 of the cast's 18 balance rows change. One is `shock_2022` on 2021-12-31, which moves from
  "£0.01 owed" to £311.09.
- **O27: the ledger dropped part of the EBSS credit.** The engine gives the month's whole credit to
  the account, caps the bill's share at the bill, and carries the rest as account credit that later
  bills draw on (`credit_applied_gbp`). `tools/generate_payment_ledger_data.py` posted only the
  capped share, so the bills that the carried credit settled stood owed for ever. On
  OCC-f6813bf9f05e, £400 of credit appeared as £399.99 owed under the old ledger, then £92.19 owed
  under 9d7bd4a5c's. The page ledger now posts `scheme_credit_month_gbp`, as 9d7bd4a5c made the raw
  export do. On the 13a6e5e71d book, accounts whose ledger balance disagrees with the engine's own
  outstanding fell from 182 to 133. The 133 that remain:
  - 76 are bills due after the book date. They are owed on that date, so these are correct.
  - 33 are in credit beyond the engine, and 13 of those are new. They are credit the old ledger
    dropped, for example a £67 January credit on a £6.61 final part-month bill. **GAP:** no refund
    of a credit balance at exit is modelled.
  - 20 owe more for some other reason, and 4 owe more while holding a write-off. One of those
    leaves £19.16 after writing off less than the bill (OCC-87206d346f15g). These are not chased
    here.
  "Payments equal each invoice 14 days later" is the DD collected on the due date. It is not pay
  on bill. Not changed.
- **Life events (4d7f6021a's residue).** Each life event in the supplier's timeline now carries
  `seen_by: "world"`. No route in the run tells the supplier of one.
- **INV_BALANCE_IS_BILLED_LESS_PAID was not added.** The raw export deliberately carries no balance
  (`company/billing/raw_account_export.py`, "nothing derived"). The row would have to rebuild the
  balance from the raw movements. That is for the suite's blind author to judge.

**Reconciled on a regenerated book.** The 2eeb3f0b3 run exists only as a pickled arm, which has no
`per_customer_lifetime` and so cannot drive the page generators. The pages were therefore rebuilt
in `/var/tmp/cust-reconcile-13a6e5e71d` from the full 13a6e5e71d run, which descends from 2eeb3f0b3,
using current ledger code. The page's own `stageJudged()` was then driven over the eleven
cold-read households. On all eleven, paid equals what the ledger collected, billed equals paid +
credit + write-off + owed to the penny, and the column for us foots within a penny. The published
site changes at the next publish.

**Tests that go red on the old code:**
- `site/explore/test_the_judged_stage_reconciles.py`: 752 households printed a paid figure the
  ledger did not collect.
- `tests/tools/test_generate_explore_cast.py::test_the_cast_balance_is_billed_less_paid_on_every_moment`
- `tests/tools/test_generate_payment_ledger_data.py::test_the_months_whole_scheme_credit_is_posted_so_the_bills_it_later_settles_are_not_owed`

The rest of this finding stays open: O8, O30, O4 and the copy items.
