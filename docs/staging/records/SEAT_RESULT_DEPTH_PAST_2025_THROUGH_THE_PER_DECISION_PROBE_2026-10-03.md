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

## Correction, 2026-10-03 (later the same day)

**Every margin above was scored on the OFFER, and a stayer offered a fix above its default does not
pay it.**

The world's decline-and-stay rule is live (`DECLINE_A_FIX_ABOVE_THE_DEFAULT`). A household that
stays refuses any fix above its default and is billed the default. The probe credited the offer.

The value rule priced above the default on 68-74 of 77-82 decisions per path; the level rule at the
value median did so on 59-67. Re-scored offline with the world's own rule, value - level on the
four 2025 paths:

| path | was | now (SNR) |
|---|---|---|
| default | -2,668 | -1,184 (1.25) |
| 61001 | -3,046 | -1,482 (1.69) |
| 61002 | -2,146 | -1,019 (1.43) |
| 61003 | -2,827 | -1,560 (1.79) |

value - flat roughly halves (e.g. 7,250 -> 3,663).

**The direction of every conclusion here holds; the sizes do not.** The probe now records
`stayer_pays_gbp_per_mwh` and scores on it. See
`SEAT_PREREG_A_STAYER_PAYS_THE_DEFAULT_SO_THE_VALUE_RULE_SHOULD_NOT_PRICE_ABOVE_IT_2026-10-03.md`.

**The 2029 run, re-scored the same way:**
- value - level: -3,083 -> **-1,418, SNR 1.29**, against the default path's 1.25 to 2025;
- value - flat: 8,787 -> 4,946;
- 94 of 103 value offers sit above the default.

The re-score read the default outside the forward-world scope, so past 2025 it takes whatever
the SVT series returns there. It is approximate for the 21 decisions past the record, and exact once
the probe re-runs with the column inside the world. **Depth is an even weaker lever than reported:
four more years buy SNR +0.04.**
