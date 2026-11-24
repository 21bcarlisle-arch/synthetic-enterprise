**Severity:** RECORDED · **Lane:** G_data_learning · **Atom:** `W1_6_physics_price_signal`

# Pre-registration: is the chain's 2025 gas-running miss the basis of the fleet it is clamped to? (2026-11-24)

*Autonomous worker, 24 Nov 2026. Item 4 of the weather-to-price steer (BLOCKING finding, G_data_learning):
"R's 2025 residual against the AGWS windows finding", owed since the annual-mean arm. Filed and landed
before the probe runs. Probe `/var/tmp/r2025/probe.py`, sha256 `bc4d8129f667a174…`. It is the wind-target
arm's probe (`/var/tmp/wtp_worker/measure_w.py`, sha256 `0847aa93…`) with two arms added after W1 and a
2025 row added to the output. **Nothing in `sim/` changes.***

## What is known before the run

- **W1** (the wind-target result) mean-matches the chain's wind to FUELHH by year with
  `s_y = FUELHH ÷ AGWS` over each year's own record days. After the crisis its gas running is +0.71 GW,
  and −0.02 GW without 2025. So 2025's 158 days carry about +3.25 GW. That result put two candidates
  beside it and attributed neither: AGWS running above FUELHH in 2025 (s = 0.812), and the fleet
  clamped to 2024.
- **The end-year clamp arm** showed 2025 cannot take its own AGWS fleet (0.717 × DUKES). It gets 2024's
  instead. 2024's fleet is fitted on AGWS and depressed by the May-October 2024 window, and 2025's
  January-June town wind is calm (3.23 m/s, against 3.91-4.71 in 2017-24).

**The hypothesis.** W1 scales 2025 by **2025's** ratio (0.812). The wind it scales comes from **2024's**
fleet, which sits on 2024's AGWS basis (s = 1.221). The scale and the fleet come from different years.
If the fleet carried its own year's basis, 2025 would be scaled by 1.221, which is 1.50× W1.

## Arms (each changes 2025 only; k is fitted on pre-crisis days, so pre and crisis rows cannot move)

| Arm | 2025 scale |
|---|---|
| W1 (control) | s_2025 = 0.812, as published |
| **Y1** | s_2024 = 1.221: the 2024 fleet carries its own basis |
| **Y2** | set so the chain's 2025 wind mean equals 2025's FUELHH mean. An in-sample oracle on the level, keeping the chain's daily shape |

## Predictions

| # | Prediction |
|---|---|
| Y-P0 | W1 reproduces the published W1 to every printed figure |
| Y-P1 | Y1's 2025 c_hat − c is in [+0.8, +2.2] GW, so the basis fix takes 30-75% of the miss |
| Y-P2 | Y2's 2025 c_hat − c is in [−0.8, +0.8] GW |
| Y-P3 | Y1's post-crisis c_hat − c is in [+0.15, +0.55] GW |
| Y-P4 | Pre and crisis rows are identical across W1, Y1 and Y2, and so is post without 2025 (7.33 / +5.83) |
| Y-P5 | Y1's post-crisis composite bias is £0.4-1.5 below W1's +8.29 |
| Y-P6 | Y2 runs gas under 6 GW on 10-48 of 2025's days (record 48; W1 0) |

## Decision rule

- **(a)** If Y-P1 holds, or Y1 takes at least half the miss: build rule. **A clamped year inherits its source
  year's fleet and basis together.** Whatever Y1 leaves is the calm-year curve, and the build reports it
  beside the number.
- **(b)** If Y1 takes under 30% and Y2 closes (Y-P2 holds): the miss is the fleet's level beyond the basis.
  2025 needs a fleet from a source independent of AGWS (DUKES or the capacity path). On record years the
  build reports 2025's miss beside the number.
- **(c)** If Y2 does not close (|2025 c_hat − c| > 0.8 GW): the wind level is not the term. Demand, solar or
  must-run in 2025 is filed unattributed.

Reverse: delete this record.
