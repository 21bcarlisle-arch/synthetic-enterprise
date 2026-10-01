**Severity:** RECORDED · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** `D_opening_dd_seasonal_sizing` — Lane 0 delivery

# The 2025 standing charge is tabled from the cap model, and the tables now have a pin

Claim `add-the-2025-standing-charge-row-from-the-cap-level-model`. The results are graded against
`docs/staging/records/SEAT_PREREGISTRATION_WHAT_THE_2025_STANDING_CHARGE_ROW_MOVES_2026-10-01.md`,
which was written before either arm ran.

**Disposition of the draw's duplicate-work note.** The claim "already held under this very id" was
this draw's own write. The holder was this session (pid 2586229), and there was no rival.

## What changed

- **2025 rows:** electricity **51.23p/day**, gas **29.58p/day**, both ex-VAT. Until now 2025 clamped
  silently to 2024's 57.11p and 28.57p. The v1.31 model carries all four 2025 cap periods. Its
  columns run to October-December 2026 and are empty from January 2027.
- **The method's description was wrong, and the numbers were right.** The comment said "median
  over the regional rows". The 2016-2024 figures reproduce only from the median of all **15**
  Total rows, which includes the model's own "GB average" row. That is the population
  `tools/ofgem_cap_unit_rate_composition` reads (`regions: 15`). Using regions only:
  - electricity differs by up to 0.22p/day in a year, and by 0.5p in 2025;
  - gas is the same either way.

  The comment now states the population that is actually used, and 2025 uses it too.
- **The early-2019 overlap.** The model has a historical column for October 2018 - March 2019 and
  the cap's first column for January-March 2019. They carry identical values. Counting both
  double-weights the quarter (gas 2019 would read 25.03p, not 25.14p).
- **A pin, where there was only a comment.** The new commons artefact
  `docs/domain_artefact_library/regulatory/ofgem_cap_standing_charges.json` carries the per-period
  figures for both fuels and no yearly blend. The model itself is gitignored.
  `tests/simulation/test_standing_charge_reproduces_the_cap_model.py` does the blend and has these
  legs:
  1. every tabled year equals the blend of the artefact's periods;
  2. no year in `SIM_START_YEAR..SIM_END_YEAR` clamps;
  3. the overlap is reachable;
  4. the electricity periods agree with the independent extraction in
     `ofgem_cap_unit_rate_composition.json`;
  5. the artefact equals the cached workbook, run only where the workbook is cached.

  Both tables moved from `_UNVERIFIED_TABLES` to `_PINNED_ELSEWHERE` in
  `test_policy_cost_values_vs_source.py`, and its ratchet went down from 9 to 7.
- **Mutations:**
  - a row changed by +0.01p: red;
  - the gas 2025 row dropped: red;
  - the overlap counted twice: red (2 legs);
  - the earlier overlapping column allowed to win: **green**. This is an equivalence, not a
    missing test, because the two columns are identical in v1.31. The test's docstring says so.

## Results (one default world per arm, same base, run in parallel; n = 319,176 records in both)

| | prediction | result | |
|---|---|---|---|
| P1 | no record before 2025 moves | **12 account-term-years in 2024 moved unit revenue** (net +£0.53); standing charge was identical before 2025 | **MISSED** |
| P2 | 2025 standing charge: elec −£665 ± 10, gas +£91 ± 5 | elec **−£664.79**, gas **+£91.24**, net −£573.55 | holds |
| P3 | revenue ≈ 0.88 × SC change (−£505; band −£460 to −£574) | **−£563.12, 0.98×** | inside the band, off the point |
| P4 | kWh identical on every key | identical on all keys | holds |

**P1 missed, and the miss is a defect, not noise.** Only the two settlement modules read these
tables, so the change cannot reach a 2024 record directly. The 12 moved keys are renewals starting
2024-07-01 and 2024-10-01. Their unit rates moved because the portfolio premium priced them off
realised margins of terms that were still settling in 2025. The world was settling days the company
could not yet have seen. This is filed on its own as
`SEAT_FINDING_THE_PORTFOLIO_PREMIUM_PRICES_A_RENEWAL_OFF_MARGINS_THAT_HAVE_NOT_HAPPENED_YET_2026-10-01.md`.

**P3: I cannot yet say why the feedback here is 2%, not 12%.** Unit revenue moved +£10.43 net:
electricity +£17.81 and gas −£7.38, signs consistent with the premium reading each fuel's margin.
The hypothesis, untested: the change touches only the last five months the world runs, so few
renewals are priced after it. The 12% came from a change spanning every year. A "0.88×" rule for
any standing-charge change is therefore not general. The fraction depends on how much renewal
history follows the change.

## Still open

- The look-ahead above. It is handed on as the next item.
