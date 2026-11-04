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

## Progress (worker, 2026-11-04): the source is attributed and the world row is corrected; BLOCKING stands

- **Attribution, now settled.** The world reads that row. `simulation/svt_rates._SVT_GAS_PRECAP_PENCE_PER_KWH[2017]`
  was 2.80p inc VAT, the midpoint of "~2.1–3.5". 2.80 / 1.05 = 2.67p ex VAT, which is the flat 2.67p on every
  2017 bill. The 2016 row (4.00 → 3.81) and the 2018 row (3.75 → 3.57) match their medians in the same way.
- **K8, knowledge first.** `docs/market_research/svt_rates_active_passive_2016_2025.md` §1b withdraws the row. It
  names three records against it: the RMI default dual-fuel bill rose, the back-cast pass-through floor rose,
  and the suppliers' 2016 gas cuts and 2017 electricity-only rises. It replaces the row with a belief of
  ~3.8–4.2p inc VAT, the 2016 band.
- **Build.** 2017 is now 4.00p inc VAT, so 3.81p ex VAT, above the 2.73p / 2.71p floors.
  `tests/simulation/test_svt_rates.py::test_pre_cap_gas_is_never_under_the_cheapest_regions_pass_through_cost`
  reads the commons for every pre-2019 period in the record. It fires on the old 2.80 (mutation run).
- **Not attributed with it, on purpose:** the 2017 electricity row and the 2018 gas row. Both are logged as gaps
  in §1b.
- **Still owed before this closes.**
  - (1) A fresh book shows the 2017 gas SVT at about 3.81p ex VAT, and every published figure that moves is
    marked.
  - (2) The blind `DOMAIN_INVARIANTS.yaml` row named above. It has to be written by a reader who has not seen this
    code, so this worker did not write it.
