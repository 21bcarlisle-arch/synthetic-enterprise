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
