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
