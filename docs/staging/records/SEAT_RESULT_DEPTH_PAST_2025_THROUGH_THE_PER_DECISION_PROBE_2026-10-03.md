# Depth past 2025, measured through the per-decision probe

**Severity:** RECORDED · **Lane:** W1_market_weather · **Epoch:** 3 · **Atom:** `SPINE_1_scenario_world_state`

The director's depth question ("wire SPINE_1 and run past 2025 ... say where the curve lands"),
answered on the per-decision instrument rather than the book-level A/B. The default book, its
renewals priced decision by decision, lived to 2029 inside `neso_central`:
- prices from the spine and scenario generators, from the day after the record;
- weather by analogue years;
- the domestic cap held at its last published window (December 2026), stamped on the run.

| Window | decisions | value - flat | value - level at its median | O_full headroom |
|---|---|---|---|---|
| 2016-2025 (record) | 82 | +7,250, SNR 6.8 | -2,668, SNR 2.2 | +2,952 |
| 2016-2029 (neso_central) | 103 (21 past the record) | +8,787, SNR 6.9 | -3,083, SNR 2.4 | +2,848 |

**Where the curve lands.** Four more years add a quarter more decisions and move the selection
signal from 2.2 to 2.4. The sign and the cause do not change: the choosing still loses against a
flat price at its own median, and the headroom is still about 3k. Depth is a weak lever here next
to the churn belief (`SEAT_PREREG_WHICH_BELIEF_THE_CHOOSING_LOSES_ON_2026-10-03.md`).

Cost: 53 min, 6.0 GB, one book, every rule. The held book-level depth legs would have cost about
20 machine-hours and stay held. The forward world settled to 2029-12 with no refusal, and a run past
the record without a named world refuses, as 18c3ecb8c built.

Caveat, carried from the world's stamp: the cap past December 2026 is held, not modelled, so
forward wholesale moving under a frozen cap is in these 21 decisions.
