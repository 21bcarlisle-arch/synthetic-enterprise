**Severity:** RECORDED · **Lane:** W3_industry_systems · **Atom:** `W3_3_the_network_charge_splits_per_unit_and_per_day`

# Pre-registration: what W3_3 moves per domestic electricity account-day, and what it does not (2026-11-18)

Filed by the delivery seat on 18 Nov, in the landing that brings W3_3 onto origin and before any
book carries it. This amends the 9 Nov worker pre-registration
(`docs/staging/records/WORKER_PREREG_W3_3_WHAT_SPLITTING_THE_NETWORK_CHARGE_MOVES_ON_THE_NEXT_RUN_2026-11-09.md`):
that record left the book-level sign conditional on a mean EAC nobody had read. It is read here.
K8: `docs/market_research/network_charges_uk_2016_2024.md` §7d; artefact
`docs/domain_artefact_library/regulatory/ofgem_cap_network_allowance.json` (cap model v1.31).

## Before measuring, what each thing is

- **Network cost per account-day:** the `network_cost_gbp` summed over one domestic electricity
  supply point's 48 settled half-hours in a day, ex-VAT. Old = whole-allowance table x kWh. New =
  cap per-kWh allowance x kWh + cap nil allowance / 365.
- **The carried GBP 0.47-0.60 gap:** NOT a network figure. It is the world's whole electricity
  standing charge per day (ex-VAT, 2022-2026), which `run_deemed_term` and `run_flex_term` never
  book as revenue while `saas/bill_generator.py` bills it
  (`docs/staging/WORKER_FINDING_THE_DEEMED_AND_FLEX_WRITERS_BOOK_NO_STANDING_CHARGE_SO_THE_FIXED_NETWORK_SHARE_HAS_NO_RECOVERY_2026-11-09.md`).
  The two are different quantities and must not be differenced against each other.

## Correction to the direction that drew this item

The focus row says "settlement and the bill disagree on every domestic electricity account-day …
that blocks B12", and reads as if W3_3 closes that. **It does not.** W3_3 changes cost on all three
writers; it changes revenue only on pass-through and flex rows, and books no standing charge on
deemed or flex rows. What W3_3 does fix is the half B12 needs: on the **hedged** writer (every
fixed renewal) the standing charge already recovered the nil column, while network was charged
again per kWh at the whole allowance. After W3_3 the hedged floor carries only the per-kWh part.
The deemed/flex standing-charge gap remains open under its own finding and is a separate world fix
that must not ride on W3_3's book.

## The table at real inputs (printed 18 Nov from this tree before the book)

GBP per account-day, ex-VAT. SC = the world's electricity standing charge; nil = cap NC nil / 365.

| date | SC/day | nil/day | 1,500 kWh/yr | 2,700 | 3,100 | 4,500 |
|---|---|---|---|---|---|---|
| 2019-06 | 0.223 | 0.045 | +0.019 | -0.002 | -0.009 | -0.034 |
| 2021-06 | 0.237 | 0.048 | +0.019 | -0.004 | -0.012 | -0.039 |
| 2022-06 | 0.453 | 0.252 | +0.135 | +0.041 | +0.010 | -0.099 |
| 2023-06 | 0.513 | 0.291 | +0.148 | +0.035 | -0.003 | -0.136 |
| 2024-06 | 0.586 | 0.354 | +0.198 | +0.074 | +0.032 | -0.113 |

The 6af7fd0bfd book's 720 domestic electricity accounts: opening EAC mean 3,635 kWh, median 2,690,
60% below 3,100. Opening EAC is the registry figure, not settled volume (N17 says settled volume
barely moves year to year, so it is a fair proxy, not a measurement).

## Predictions, filed before the book

1. **Hedged and deemed rows, network cost per account-day:** moves exactly by the table above for
   the account's own daily kWh. At the book's mean (about 9.96 kWh/day) that is -0.02 (2019),
   -0.02 (2021), -0.03 (2022-06), -0.05 (2023-06), -0.02 (2024-06). A nil-volume day now costs the
   nil share (0.05 before Apr 2022, 0.25-0.35 after) where it cost 0.
2. **Book level:** `years/<y>/network_cost_gbp` (6af7fd0bfd baseline 2016-2025: 31.4k, 58.5k,
   49.5k, 43.7k, 40.8k, 40.3k, 48.6k, 58.4k, 59.1k, 28.8k). Every day of each year, at the mean
   EAC, prints: 2016 +0.7%, 2017 -2.6, 2018 -2.3, 2019 -3.3, 2020 -5.8, 2021 -4.8, 2022 -4.1,
   2023 -4.7, 2024 -3.5, 2025 -3.3. *(My first draft said "every year falls"; the 2016 row refuted
   that before filing. Kept here as the correction.)* Prediction: 2017-2025 each FALL by 1% to 9%;
   2016 moves within ±3%. **Refuted if** any of 2017-2024 rises, or any year falls by more than 12%. The median account's line RISES after April
   2022 (2,690 kWh sits below the crossover), so a book whose median account falls has charged
   the split wrong.
3. **Flex rows:** revenue falls by (old - per-kWh) x kWh, about 0.28/day at 2,700 kWh in 2024, and
   cost rises by the nil share with nothing recovering it, so each flex account-day's net falls by
   about the nil share (0.25-0.35 after Apr 2022). **The deemed/flex P&L-versus-bill gap therefore
   WIDENS, from the SC (0.47-0.60) to SC plus nil (about 0.72-0.94) per account-day.** That is the
   expected, conservative-direction cost of landing W3_3 alone, and it is the reason the deemed/flex
   standing-charge finding is next in the W3 lane.
4. **Renewal floors (B12's question):** the domestic per-MWh network a floor reads drops from
   49 to 42 (2021/22), 66 to 37.5 (2022/23), 69 to 31 (2024/25), as the 9 Nov record says. The 9 Nov
   prediction "fewer than half of held electricity renewals sit on the floor to the penny" stands
   unamended.
5. **Not predicted:** churn and book net. Lower floors make our renewals keener and the rival's too
   (both read the same function); the net retention move needs the one-variable run.

## What would make me wrong

- A book-level rise (prediction 2): the settled volume per account-day is lower than the registry
  EAC says, which would itself be news for N17.
- Void rows: `as_void_row` still zeroes network, so void-heavy years understate the nil share.
  Expected small; named so a surprise there is attributed to it first.

## Graded on 67d454905c (book `docs/reports/run_output_67d454905c_20261119T184502Z.json`, built 19 Nov 20:36Z)

Graded 19 Nov by the worker holding `w3-3-the-standing-charge-fix-is-graded-on-67d454905c`. The book
carries c71d2521d **and** other world landings since 6af7fd0bfd (W2_30 OCC gas legs, the stock
prepayment meters, KNIFE3 moves, s.12f off). So W3_3 does not read alone here, book against book.
Each grade below is therefore taken **within this one book** wherever it can be, so the population is
held fixed.

1. **Held.** On hedged domestic electricity account-months, `(network_cost_gbp − cap per-kWh × kWh) /
   (cap nil / 365 × days)` has median 1.000 in every year 2016–2025. 98–99% of account-months
   fall within 5% in 2017–2024. The 2016 and 2025 tails (84%, 82%) are part-months at the edges of the
   book. The split is charged exactly as written.
2. **Held, but only as a one-variable reading.** Book against book, network cost *rises* in
   2016–2019 and 2022–2024 against the 6af7fd0bfd baseline (+4.0, +0.2, +0.1, +1.9, −0.8, −1.6, +2.3,
   +0.2, +1.0, −6.6%). Taken at face value, that refutes the prediction. It cannot be attributed,
   because the population moved too. On this book's own account-months, W3_3 against the old
   whole-allowance rule (the year table, still served for `segment="SME"`, × the same kWh) gives:
   2016 +3.0%, 2017 −2.3, 2018 −3.1, 2019 −3.6, 2020 −5.8, 2021 −5.3, 2022 −2.0, 2023 −3.8, 2024 −2.7,
   2025 −8.3. Predicted: 2017–2025 each fall by 1–9%, and 2016 within ±3%. Every year holds. 2016 sits
   at the edge of its band and 2025 near the bottom of its band. The static counterfactual ignores
   any behaviour the floors feed back; that is named rather than corrected. The median-account
   sub-claim was not read.
3. **Vacuous on this book: there are no flex rows, and no deemed rows either.** `run_deemed_term`
   is reached only through `deemed_gap_days > 0`, and `run_flex_term` only through `tariff_type ==
   "flex"`. Both are set only on the I&C demo accounts in `saas/customers.py` (C_IC1, C_IC2 deemed;
   C_IC4 flex). No `C_IC*` account is in this book, and no account-state row has a tariff type other
   than `fixed` or `svt`. **The measured deemed/flex standing-charge gap per domestic electricity
   account-day is GBP 0.00, against the GBP 0.47–0.60 carried (0.72–0.94 predicted after W3_3).** That
   is not because the writers were fixed. The code still books no `standing_charge_gbp` on either
   writer. It is because no domestic account settles through them. "Settlement and the bill disagree
   on every domestic electricity account-day" was wrong as a statement about the book. It is a latent
   defect in two writers that the current population never reaches.
4. **Not graded here** (the renewal-floor per-MWh). It is a property of the function, which
   c71d2521d's control already pins.

**The void half, measured.** `as_void_row` still zeroes `network_cost_gbp`, because it is in
`_VOLUME_FIELDS`. The book has 140 electricity bills that carry a void owner's charge, covering
1,939 void account-days in total. The fixed network share those days omit, at the cap nil column, is
**GBP 202.53 over ten years**: GBP 8–15 a year to 2021, then 31.82 / 35.03 / 59.34 / 8.90 in
2022–2025, about 0.05/day before April 2022 and 0.19–0.34 after. That is at most 0.1% of any year's
network cost. It runs in the flattering direction, as the "what would make me wrong" line expected,
and it is small.

**The other ~SC cluster, named so nobody reads it as deemed.** 255 domestic account-months show a
bill-minus-settlement revenue of about one standing charge a day, and only 56 of them fall within 2%.
All 255 are `billing_basis: estimated`, where the bill is set from the estimate rather than the
settled volume. 10,084 estimated months fall outside both clusters. This is the estimated-billing
spread. It is not a missing standing charge.

**What this means for B12.** B12's renewal floor reads the hedged writer, and (1) shows that writer
carries the split exactly. The settlement-versus-bill row no longer blocks B12. The deemed/flex/void
fix is still a true world fix, and it stays open as a latent defect, but it is not on B12's path.

Graded: 67d454905c -- P1 held, P2 held on the within-book one-variable reading (book-vs-book refuted by population change, unattributable), P3 vacuous (0 deemed/flex rows; measured gap GBP 0.00/account-day vs 0.47-0.60 carried), P4 not graded; void omission GBP 202.53 over 1,939 void-days. Probes: /tmp scripts reading the book's per_customer_monthly, bills, account_state_log, home_move_outs.
