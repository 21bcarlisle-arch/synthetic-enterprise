**Severity:** BLOCKING · **Lane:** B_commercial · **Epoch:** 4 · **Atom:** `unminted`

# N18. Every 2017 gas standard variable bill is priced 30% under 2016 and 2018, and under the cheapest region's pass-through cost, while the published default bill rose (2026-11-04)

**Source.** The eighth cold read's named check (a), price between wholesale and cap. The seat ran it over all
1,292 page files of the b3ce2a4e73 book (`records/SEAT_READING_THE_EIGHTH_COLD_READ_ON_THE_B3CE2A4E73_BOOK_2026-11-04.md`).
Scripts: `/var/tmp/eighth-read/scripts/a_split.py` and `svt_precap.py`.

**What the record shows.** These are domestic single-register gas SVT bills. The all-in rate is energy plus
network and policy, ex-VAT, standing charge excluded. Medians by quarter:

| | 2016 | 2017 | 2018 |
|---|---|---|---|
| gas SVT all-in, p/kWh | 3.81 (every quarter) | **2.67** (every quarter) | 3.57 (every quarter) |
| electricity SVT all-in, p/kWh | 13.33 | 13.33 | 14.52 |
| against Ofgem's back-cast cap level (median region, DD) | 1.32 | **0.86** | 1.09 |

- 1,304 bills in 2017 carry it. Example: C2g's April 2017 bill (C2g-INV45) is 2.67p all-in. Ofgem's back-cast
  pass-through cost for April–September 2017 (DF+CM+NC+PC, the **lowest** region) is 2.73p
  (`docs/domain_artefact_library/regulatory/ofgem_cap_unit_rate_composition.json`). So a default tariff sits
  under the cost of energy, network and policy in the cheapest region, before any operating cost.
- At the benchmark consumption (3,100 kWh electricity, 12,000 kWh gas), the default dual-fuel unit cost **falls
  about 16%** from 2016 to 2017, from £870 to £733 before standing charges.
- The published default dual-fuel bill **rose 4%**: £1,071 in 2016, £1,117 in 2017 and £1,175 in 2018 (Ofgem
  RMI large-legacy SVT average, `docs/market_research/cheapest_fix_against_the_default_tariff_gb_2016_2025.md`
  §2, ESTABLISHED).

**Why the gate cannot see it.** `INV_UNIT_RATE_SVT_GAS_PRE_CAP` (`docs/design/DOMAIN_INVARIANTS.yaml`) bounds the
term's energy rate below by the back-cast DF+CM floor (1.673p from April 2017). It has no ceiling, and it reads
neither the all-in rate nor the pass-through floor. An energy line of about 1.7p passes it.

**The likely source, a candidate, not an attribution.** `docs/market_research/svt_rates_active_passive_2016_2025.md`
§1 gives 2017 gas SVT as "~2.1–3.5 (Q4 low: 2.07p)" and says "Gas fell to 2.07p/kWh Q4 2017 then recovered". Its
own label: "back-derived from BEIS QEP bills + Ofgem SVT league tables; treat as ±15%". The same page's §1a says
the per-fuel pre-cap default is a GAP that Ofgem never published. BEIS QEP averages every tariff, fixes included.
**I cannot yet say** whether the world's or the company's pre-cap gas SVT reads that row. Its flat 2.67p for all
of 2017, against 3.81p in every 2016 quarter, has the shape of one annual figure from a table, not a priced tariff.

**What a fix needs (K8, knowledge page first).** The pre-cap default per fuel has to be split from the published
dual-fuel series, with the split stated as a belief with a range. Then the "2.07p" row should be corrected or
withdrawn on its page.

**The row this owes (ruling step 6).** It must be written blind from the RMI series and the composition artefact.
A pre-cap domestic SVT's all-in rate sits at or above the lowest-region pass-through cost of its period. At the
benchmark consumption, the default dual-fuel annual cost moves year to year in the direction of the published
default bill, within a stated band.

**Reverse.** Delete this file. Nothing outside `docs/staging/` was touched.
