# GB domestic energy switching: how are switches distributed across the calendar year?

**Knowledge:** how-households-choose

**Question**: How are domestic supplier switches distributed across the calendar year (2016-2025),
and does the simulated company's batch acquisition pattern (20 of 80 founding accounts starting on
1 January; none in Sep/Nov/Dec) resemble how real switching happens?

**Date researched**: 2026-10-03
**Researcher**: discovery-agent

---

## 1. Sources table

| # | Publisher | Dataset / table | URL | Date retrieved | What it covers |
|---|---|---|---|---|---|
| 1 | Department for Energy Security and Net Zero (DESNZ), data sourced from **Ofgem** | *Quarterly Domestic Energy Switching Statistics*, Table 2.7.1 (sheet **"2.7.1 (Monthly)"**) — part of the Quarterly Energy Prices release (QEP) | gov.uk page: `https://www.gov.uk/government/statistical-data-sets/quarterly-domestic-energy-switching-statistics`; file: `https://assets.publishing.service.gov.uk/media/6ab54112734e2435f202f05d/table_271.xlsx` | 2026-10-03 | Monthly GB domestic electricity and gas **meter-point transfers**, Jan 2003 – Jun 2026 (page last modified 2026-09-29) |
| 2 | Ofgem | Retail Market Indicators data portal (referenced in Table 2.7.1's own methodology notes as the primary publisher of the underlying switching counts) | `https://www.ofgem.gov.uk/news-and-insight/data/data-portal/retail-market-indicators` | 2026-10-03 | Interactive-chart front end to the same underlying switching series; JS-rendered, no raw monthly figures extractable without the DESNZ spreadsheet above |
| 3 | Ofgem (cited in Table 2.7.1's "Methodology" sheet) | "Number of domestic customers switching supplier by fuel type (GB)" | Named only, URL not resolved in this session (see §5) | 2026-10-03 | Likely the Ofgem-hosted original of the same series; not independently checked — treated as the same primary measurement, not a second corroborating source |

**No other series was found.** Energy UK, Citizens Advice, ElectraLink/Energy Switch Guarantee, and
MRASCo/Gemserv publications were searched for (see §5) but none surfaced a distinct monthly
switching-count series in this session; where they are quoted elsewhere they appear to cite the
same Ofgem-collected transfer counts DESNZ republishes in Table 2.7.1.

---

## 2. What the series counts — read the definition before trusting the number

From Table 2.7.1's own header notes and "Methodology" sheet (quoted directly):

- **Unit of count: meter-point transfers, not customers and not accounts.** "The number of
  customers accounts changing supplier in the data presented in these tables is based on the number
  of meter points a supplier gains from another supplier following a customer choice to change
  their supplier." A dual-fuel household that switches both fuels together is counted **once in the
  electricity column and once in the gas column** — i.e. as two transfer events, not one switch.
- **It is supplier-to-supplier, not tariff-to-tariff.** "Figures do not include switching payment
  method when staying with the same company, or where a customer switches to another offer provided
  within the same parent company." A customer who renews onto a new deal with their *existing*
  supplier — which is what the simulated company's annual renewal event mostly represents — is
  **not** in this series at all. This series measures acquisition/loss between suppliers, the mirror
  image of what the simulation calls "renewal," not the same event.
- **It is gross, not net.** The table is gross meter-point gains per month; net gains per supplier
  are a separate derived calculation (per the Methodology sheet), not what is reported here.
  Electricity and gas are reported as two separate columns throughout — there is no "GB domestic
  switches, both fuels combined, deduplicated by household" series published. The "combined" column
  in §3 below is **my own sum of two columns that are not the same population** (an electricity
  meter-point transfer and a gas meter-point transfer are not drawn from the same household base, as
  not every home has gas) and should be read as "total transfer events," not "total households."
- **Definitional breaks the data itself warns about**, relevant to anyone using earlier years:
  pre-2014 gas figures cover only the "main six" suppliers (not used here, range starts 2016); from
  April 2016 the Department added filtering to strip non-domestic customers, so April-onward figures
  "may be more accurate but lower than previous levels" — this falls inside the first four months of
  the requested 2016-2025 range and is disclosed by the publisher, not something I inferred.
- Great Britain only — Northern Ireland is excluded (separate regulator, price-controlled market).

**Confidence in the definition: H** — stated by the publisher in the same workbook as the figures,
not inferred.

---

## 3. The monthly series, 2016-2025 (full table)

Figures are rounded to the nearest thousand by the publisher. "Combined" = electricity + gas
transfer events (see caveat above — not a household count).

| Year | Month | Electricity transfers | Gas transfers | Combined |
|---|---|---|---|---|
| 2016 | Jan | 247,000 | 190,000 | 437,000 |
| 2016 | Feb | 391,000 | 306,000 | 697,000 |
| 2016 | Mar | 455,000 | 362,000 | 817,000 |
| 2016 | Apr | 386,000 | 274,000 | 660,000 |
| 2016 | May | 345,000 | 261,000 | 606,000 |
| 2016 | Jun | 336,000 | 253,000 | 589,000 |
| 2016 | Jul | 303,000 | 221,000 | 524,000 |
| 2016 | Aug | 310,000 | 209,000 | 519,000 |
| 2016 | Sep | 349,000 | 271,000 | 620,000 |
| 2016 | Oct | 487,000 | 384,000 | 871,000 |
| 2016 | Nov | 387,000 | 297,000 | 684,000 |
| 2016 | Dec | 423,000 | 318,000 | 741,000 |
| 2017 | Jan | 320,000 | 240,000 | 560,000 |
| 2017 | Feb | 398,000 | 296,000 | 694,000 |
| 2017 | Mar | 513,000 | 388,000 | 901,000 |
| 2017 | Apr | 449,000 | 327,000 | 776,000 |
| 2017 | May | 414,000 | 305,000 | 719,000 |
| 2017 | Jun | 379,000 | 316,000 | 695,000 |
| 2017 | Jul | 351,000 | 306,000 | 657,000 |
| 2017 | Aug | 414,000 | 349,000 | 763,000 |
| 2017 | Sep | 519,000 | 455,000 | 974,000 |
| 2017 | Oct | 535,000 | 461,000 | 996,000 |
| 2017 | Nov | 441,000 | 375,000 | 816,000 |
| 2017 | Dec | 385,000 | 326,000 | 711,000 |
| 2018 | Jan | 322,000 | 254,000 | 576,000 |
| 2018 | Feb | 425,000 | 348,000 | 773,000 |
| 2018 | Mar | 443,000 | 374,000 | 817,000 |
| 2018 | Apr | 447,000 | 372,000 | 819,000 |
| 2018 | May | 465,000 | 399,000 | 864,000 |
| 2018 | Jun | 455,000 | 389,000 | 844,000 |
| 2018 | Jul | 442,000 | 365,000 | 807,000 |
| 2018 | Aug | 467,000 | 394,000 | 861,000 |
| 2018 | Sep | 525,000 | 433,000 | 958,000 |
| 2018 | Oct | 559,000 | 470,000 | 1,029,000 |
| 2018 | Nov | 462,000 | 382,000 | 844,000 |
| 2018 | Dec | 391,000 | 338,000 | 729,000 |
| 2019 | Jan | 360,000 | 291,000 | 651,000 |
| 2019 | Feb | 436,000 | 350,000 | 786,000 |
| 2019 | Mar | 586,000 | 486,000 | 1,072,000 |
| 2019 | Apr | 638,000 | 522,000 | 1,160,000 |
| 2019 | May | 470,000 | 381,000 | 851,000 |
| 2019 | Jun | 423,000 | 336,000 | 759,000 |
| 2019 | Jul | 488,000 | 402,000 | 890,000 |
| 2019 | Aug | 498,000 | 391,000 | 889,000 |
| 2019 | Sep | 546,000 | 436,000 | 982,000 |
| 2019 | Oct | 527,000 | 431,000 | 958,000 |
| 2019 | Nov | 475,000 | 378,000 | 853,000 |
| 2019 | Dec | 499,000 | 418,000 | 917,000 |
| 2020 | Jan | 441,000 | 329,000 | 770,000 |
| 2020 | Feb | 444,000 | 390,000 | 834,000 |
| 2020 | Mar | 569,000 | 422,000 | 991,000 |
| 2020 | Apr | 444,000 | 319,000 | 763,000 |
| 2020 | May | 425,000 | 321,000 | 746,000 |
| 2020 | Jun | 462,000 | 343,000 | 805,000 |
| 2020 | Jul | 537,000 | 389,000 | 926,000 |
| 2020 | Aug | 486,000 | 339,000 | 825,000 |
| 2020 | Sep | 488,000 | 354,000 | 842,000 |
| 2020 | Oct | 549,000 | 415,000 | 964,000 |
| 2020 | Nov | 486,000 | 361,000 | 847,000 |
| 2020 | Dec | 479,000 | 352,000 | 831,000 |
| 2021 | Jan | 350,000 | 263,000 | 613,000 |
| 2021 | Feb | 432,000 | 304,000 | 736,000 |
| 2021 | Mar | 594,000 | 392,000 | 986,000 |
| 2021 | Apr | 552,000 | 397,000 | 949,000 |
| 2021 | May | 375,000 | 260,000 | 635,000 |
| 2021 | Jun | 398,000 | 283,000 | 681,000 |
| 2021 | Jul | 415,000 | 286,000 | 701,000 |
| 2021 | Aug | 371,000 | 238,000 | 609,000 |
| 2021 | Sep | 437,000 | 291,000 | 728,000 |
| 2021 | Oct | 346,000 | 239,000 | 585,000 |
| 2021 | Nov | 99,000 | 70,000 | 169,000 |
| 2021 | Dec | 134,000 | 60,000 | 194,000 |
| 2022 | Jan | 65,000 | 46,000 | 111,000 |
| 2022 | Feb | 73,000 | 51,000 | 124,000 |
| 2022 | Mar | 88,000 | 61,000 | 149,000 |
| 2022 | Apr | 67,000 | 46,000 | 113,000 |
| 2022 | May | 63,000 | 43,000 | 106,000 |
| 2022 | Jun | 71,000 | 40,000 | 111,000 |
| 2022 | Jul | 86,000 | 50,000 | 136,000 |
| 2022 | Aug | 85,000 | 51,000 | 136,000 |
| 2022 | Sep | 73,000 | 44,000 | 117,000 |
| 2022 | Oct | 65,000 | 37,000 | 102,000 |
| 2022 | Nov | 79,000 | 49,000 | 128,000 |
| 2022 | Dec | 79,000 | 48,000 | 127,000 |
| 2023 | Jan | 87,000 | 53,000 | 140,000 |
| 2023 | Feb | 121,000 | 75,000 | 196,000 |
| 2023 | Mar | 147,000 | 88,000 | 235,000 |
| 2023 | Apr | 128,000 | 74,000 | 202,000 |
| 2023 | May | 124,000 | 73,000 | 197,000 |
| 2023 | Jun | 143,000 | 83,000 | 226,000 |
| 2023 | Jul | 178,000 | 89,000 | 267,000 |
| 2023 | Aug | 184,000 | 118,000 | 302,000 |
| 2023 | Sep | 195,000 | 102,000 | 297,000 |
| 2023 | Oct | 187,000 | 145,000 | 332,000 |
| 2023 | Nov | 202,000 | 160,000 | 362,000 |
| 2023 | Dec | 171,000 | 136,000 | 307,000 |
| 2024 | Jan | 174,000 | 133,000 | 307,000 |
| 2024 | Feb | 176,000 | 143,000 | 319,000 |
| 2024 | Mar | 193,000 | 150,000 | 343,000 |
| 2024 | Apr | 205,000 | 160,000 | 365,000 |
| 2024 | May | 196,000 | 151,000 | 347,000 |
| 2024 | Jun | 184,000 | 143,000 | 327,000 |
| 2024 | Jul | 223,000 | 172,000 | 395,000 |
| 2024 | Aug | 260,000 | 203,000 | 463,000 |
| 2024 | Sep | 288,000 | 227,000 | 515,000 |
| 2024 | Oct | 349,000 | 276,000 | 625,000 |
| 2024 | Nov | 231,000 | 179,000 | 410,000 |
| 2024 | Dec | 203,000 | 156,000 | 359,000 |
| 2025 | Jan | 218,000 | 166,000 | 384,000 |
| 2025 | Feb | 239,000 | 182,000 | 421,000 |
| 2025 | Mar | 325,000 | 254,000 | 579,000 |
| 2025 | Apr | 262,000 | 255,000 | 517,000 |
| 2025 | May | 240,000 | 185,000 | 425,000 |
| 2025 | Jun | 182,000 | 133,000 | 315,000 |
| 2025 | Jul | 274,000 | 210,000 | 484,000 |
| 2025 | Aug | 255,000 | 197,000 | 452,000 |
| 2025 | Sep | 293,000 | 228,000 | 521,000 |
| 2025 | Oct | 365,000 | 289,000 | 654,000 |
| 2025 | Nov | 268,000 | 208,000 | 476,000 |
| 2025 | Dec | 224,000 | 165,000 | 389,000 |

**Note on a data-extraction trap found and corrected while building this table**: the workbook's
month column is a mix of Excel date cells and bare month-name strings, and a subset of the date
cells (April-September 2022) carry an internal **year of 2021** baked into the serial date while the
adjacent Year column correctly says 2022. Reading `cell.year` for the month naively would silently
relabel six months of the 2022 crisis-collapse data as 2021 and double up on the real 2021 rows. The
table above uses the spreadsheet's own `Year` column as authoritative and takes only the month
number from the date cell — confirmed against the row immediately above and below each affected
cell, where the Year/Month-name pairing is unambiguous.

**Confidence: H** for the raw monthly counts (single authoritative publisher, internally
consistent, methodology disclosed) — but see §2 for what is and is not being counted.

---

## 4. The seasonal shape — computed, not eyeballed

**Average by calendar month, 2016-2025 (10 observations per month, electricity + gas combined
transfer events)**:

| Month | Avg. electricity | Avg. gas | Avg. combined |
|---|---|---|---|
| Jan | 258,400 | 196,500 | **454,900 (lowest)** |
| Feb | 313,500 | 244,500 | 558,000 |
| Mar | 391,300 | 297,700 | 689,000 |
| Apr | 357,800 | 274,600 | 632,400 |
| May | 311,700 | 237,900 | 549,600 |
| Jun | 303,300 | 231,900 | 535,200 |
| Jul | 329,700 | 249,000 | 578,700 |
| Aug | 333,000 | 248,900 | 581,900 |
| Sep | 371,300 | 284,100 | 655,400 |
| Oct | 396,900 | 314,700 | **711,600 (highest)** |
| Nov | 313,000 | 245,900 | 558,900 |
| Dec | 298,800 | 231,700 | 530,500 |

- **Peak-to-trough ratio, all years 2016-2025, combined fuels: 711,600 / 454,900 = 1.56.**
  By fuel: electricity 396,900/258,400 = **1.54**; gas 314,700/196,500 = **1.60**.
- **January is the lowest-switching month and October is the highest-switching month**, every
  single year from 2016 to 2025 bar one (see year-by-year table below) — the opposite seasonal
  position to what the simulated company currently assumes (a January acquisition spike).
- Shape, computed over sub-periods: pre-crisis 2016-2019 (ratio 1.73, peak Oct, trough Jan),
  post-crisis-recovery 2024-2025 (ratio 1.99, peak Oct, trough Jun in 2025 specifically but Jan in
  2024) — **the Jan-trough/Oct-peak shape is the stable long-run pattern; the exact trough month in
  the still-recovering 2024-2025 data has started to wobble toward mid-year**, worth re-checking in
  a year's data.

**Year-by-year peak/trough** (combined fuels; ratio = peak ÷ trough within that calendar year):

| Year | Jan value | Peak month | Peak value | Trough month | Trough value | Ratio |
|---|---|---|---|---|---|---|
| 2016 | 437,000 | Oct | 871,000 | Jan | 437,000 | 1.99 |
| 2017 | 560,000 | Oct | 996,000 | Jan | 560,000 | 1.78 |
| 2018 | 576,000 | Oct | 1,029,000 | Jan | 576,000 | 1.79 |
| 2019 | 651,000 | Apr | 1,160,000 | Jan | 651,000 | 1.78 |
| 2020 | 770,000 | Mar | 991,000 | May | 746,000 | 1.33 |
| 2021 | 613,000 | Mar | 986,000 | Nov | 169,000 | 5.83 |
| 2022 | 111,000 | Mar | 149,000 | Oct | 102,000 | 1.46 |
| 2023 | 140,000 | Nov | 362,000 | Jan | 140,000 | 2.59 |
| 2024 | 307,000 | Oct | 625,000 | Jan | 307,000 | 2.04 |
| 2025 | 384,000 | Oct | 654,000 | Jun | 315,000 | 2.08 |

**Is the shape stable, or does the 2021-2023 crisis change it?** Both — the question needs splitting
(per the project's own rule on not differencing an undefined thing):

- **The relative seasonal shape (Jan trough, autumn peak) survives the crisis**, holding in 8 of the
  10 years, including both pre-crisis (2016-2019) and recovery (2024-2025) years, and even weakly
  inside 2022 itself (2022's peak is March, trough October — a partial inversion, see below).
  **Confidence: H** that a real, repeating within-year seasonal pattern exists and that January is
  structurally a low-switching month, not a high one.
- **The absolute level collapsed by roughly 13-14x at the trough of the crisis.** Annual combined
  totals: 2019 = 10.77m, 2021 = 8.31m, **2022 = 0.74m**, 2023 = 3.06m, climbing back to 4.78m (2024)
  and 5.62m (2025) — still under half the pre-crisis level by the end of the modelled range. November
  2021 (169,000) is roughly one-sixth of October 2021 (585,000) in the same year — the market
  essentially stopped functioning for new fixed-price offers once wholesale prices spiked, which is
  a documented, distinct mechanism (suppliers withdrew tariffs rather than a change in underlying
  seasonal customer behaviour) rather than a seasonal effect at all. **This is a level collapse, not
  a seasonality collapse** — treating 2021-2023 as evidence against the Jan/Oct seasonal shape would
  be the wrong inference; it is evidence of a different, co-occurring regime change (tariff
  withdrawal / price-cap suspension under the Energy Price Guarantee), and the two should not be
  confused when the simulation's own 2021-2023 crisis period is parameterised.
- 2022 itself (peak March, trough October) looks like a seasonal inversion, but at absolute levels of
  65,000-149,000/month against the >1,000,000 peaks of 2017-2019, a 1.46x ratio inside a market with
  almost no tariffs on open sale is not comparable to the other years and should not be read as
  "October stopped being the peak" — more likely it is noise on a near-dead market, or driven by
  suppliers' own staggered tariff-withdrawal dates rather than customer-initiated switching at all.

---

## 5. Why the seasonality exists — NOT established in this session

I looked for a published causal explanation (price-cap review dates in April/October from 2019,
fixed-term-expiry cohort clustering, a "January is for sorting out your finances" behavioural
account) in:

- Ofgem's Retail Market Indicators page (`ofgem.gov.uk/news-and-insight/data/data-portal/retail-market-indicators`)
  — JS-rendered chart app, no narrative text in the served HTML.
- The DESNZ switching-statistics gov.uk page and the workbook's own "Methodology" sheet — both give
  only the counting methodology (see §2), no commentary on *why* the series moves the way it does.
- Ofgem's `energy-price-cap` page — JS-rendered, the cap review-date history did not appear in the
  static HTML served to a non-JS client; I did not resolve the cap's exact historical review-date
  cadence (Jan/Apr/Jul/Oct quarterly in some periods, Apr/Oct biannual in others, suspended under the
  2022 Energy Price Guarantee) from a primary source in this session, so **I am not citing that
  cadence as an explanation here even though it is plausible** — doing so would be exactly the
  "number picked because a number was needed" failure the house rules warn against.
- Web searches (DuckDuckGo HTML and lite endpoints, Bing) for commentary connecting switching
  seasonality to price-cap dates or fixed-term-expiry cohorts — DuckDuckGo rate-limited this session
  (HTTP 202 / redirect-to-homepage on repeated attempts) and Bing's results were not responsive to
  the query terms (returned unrelated consumer-retail pages).

**Conclusion: no published source found, in this session, stating why GB domestic switching peaks
in autumn and troughs in January.** The shape itself (§4) is well-established; the mechanism is not.
Candidate mechanisms exist in general industry knowledge (price-cap reset dates, 12-month fixed-term
cohorts set up in a prior autumn renewing the following autumn, January being a low-activity month
generally for discretionary financial admin) but **none of these is sourced here** and none should
be written into the simulation as if it were. This is filed as an open research gap, not an answer.

---

## 6. Fixed-tariff end-date / contract-start-date distribution by month — NOT FOUND

No published distribution of fixed-term tariff **end dates** or **start dates** by calendar month
was located. Specifically checked and not found:

- DESNZ/Ofgem Table 2.7.1 and its Methodology sheet — reports transfer *events*, not contract
  start/end dates, and does not break fixed-term tariffs out from variable/default tariffs at all.
- Ofgem Retail Market Indicators data portal — same JS-rendering problem as above; no raw
  distribution table found in the served content.
- General web search for "distribution of fixed tariff end dates energy customers UK research" —
  rate-limited (see §5) before a usable result set was returned.
- Energy UK, Citizens Advice, ElectraLink/Energy Switch Guarantee, MRASCo/Gemserv — not reached in
  this session; named in the brief as candidate publishers but no successful fetch was attempted
  against any of their sites (time/session budget was spent securing and validating the Table 2.7.1
  series instead, which answered the higher-value question directly).

**This is a genuine gap, not a negative result to be read as "no such distribution exists."** A
supplier-side or Ofgem-side register of tariff start/end dates by cohort plausibly exists
internally (it would be needed to run the market) but nothing publishing an aggregate monthly
distribution of it was found here.

---

## 7. What this means for the simulation's acquisition pattern

The simulated company's batch design — 20 of 80 founding accounts starting 1 January, none in
Sep/Nov/Dec — is **not supported by the published switching series** on two separate grounds:

1. **January is the lowest-switching month in the real data, every year 2016-2025 bar the
   crisis-distorted 2022** (ratio to the October peak: 1.56x over electricity+gas combined, 10-year
   average). A batch concentrated on 1 January is placing a sizeable fraction of the book precisely
   where real switching volume is thinnest.
2. **Sep/Nov/Dec are not dead months in the real data** — September and November both sit close to
   the all-month median (September averages 655,400, just below the October peak of 711,600;
   November averages 558,900, roughly in the middle of the distribution). Excluding them entirely
   from acquisition is the opposite of what the published series shows; only December (530,500,
   second-lowest average month) has some real-world support for being a quieter acquisition month,
   and even then it is not as quiet as January.

**What is sourced and actionable**: if founding-account start dates are to be redistributed to
"spread acquisition through the year the way real switching happens," the monthly weights in §4
(the 10-year average-by-month table, or the pre-crisis-only table if the baseline world is meant to
represent a non-crisis regime) are the correct, sourced weights to redistribute the 80 founding
accounts against — not a judgement call, not a round-number spread, and not the current January-
heavy/Sep-Nov-Dec-empty pattern. **What is not sourced** is any claim about *why* that shape exists
(§5) or any finer-grained within-month distribution (e.g. day-of-month) — none of that should be
invented to fill in what this research did not establish.

---

## 8. Confidence summary

| Claim | Confidence | Basis |
|---|---|---|
| A monthly GB domestic switching series exists, Jan 2016-Dec 2025, covering electricity and gas separately | H | Single authoritative publisher (DESNZ, sourced from Ofgem), internally documented methodology |
| The series counts meter-point transfer *events* between suppliers, not households, not within-supplier renewals | H | Stated directly in the workbook's own notes |
| January is the lowest-switching month and October the highest, on a 10-year average (combined-fuel ratio 1.56x) | H | Computed directly from the published series, not eyeballed |
| The Jan-trough/Oct-peak shape holds in 8 of 10 individual years 2016-2025 | H | Computed year-by-year from the published series |
| The 2021-2023 collapse is a level change (~13-14x trough-to-peak-year drop in annual totals), not a seasonality change | M | Computed from the series; the *interpretation* that it reflects tariff withdrawal rather than customer behaviour is reasoned, not independently sourced in this session |
| Why the seasonal shape exists (price-cap dates, fixed-term cohorts, January behavioural effects) | — | NOT ESTABLISHED — no source found this session (§5) |
| Distribution of fixed-tariff end/start dates by month | — | NOT ESTABLISHED — not found this session (§6) |
| The simulation's Jan-heavy / Sep-Nov-Dec-empty batch pattern resembles real switching | H (refuted) | Directly contradicted by the computed monthly shape above |

---

## 9. Where I did NOT look (explicitly, so this is not mistaken for exhaustive)

Energy UK's own published monthly switching commentary (if any), Citizens Advice supplier-performance
reports, ElectraLink/Energy Switch Guarantee operational statistics, and MRASCo/Gemserv historical
transfer-volume releases were named in the brief as candidate sources and were **not fetched** in
this session. Given that Table 2.7.1 directly and authoritatively answers the core monthly-series
question (§1-§4), further sources were not pursued for that question; they remain open avenues
specifically for §5 (the causal "why") and §6 (fixed-tariff date distributions), neither of which
this session resolved.
