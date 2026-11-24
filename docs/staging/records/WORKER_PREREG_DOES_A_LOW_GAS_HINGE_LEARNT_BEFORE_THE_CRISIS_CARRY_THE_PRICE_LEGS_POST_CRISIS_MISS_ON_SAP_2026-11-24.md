**Severity:** RECORDED · **Lane:** G_data_learning · **Atom:** `W1_6_physics_price_signal`

# Pre-registration: does a low-gas hinge learnt before the crisis carry the price leg's post-crisis miss, on SAP? (2026-11-24)

*Autonomous worker, 24 Nov 2026. Item 4 of the weather-to-price steer (BLOCKING finding, G_data_learning):
"the price-leg shape arm on low-gas days (§1b), now the largest post-crisis term in every year", named
next by the 2025 arm. Filed and landed before the probe runs. Probe `/var/tmp/shape_sap/probe.py`, sha256
`053d6857a305b9c1…`. It is the 2025 arm's probe (`/var/tmp/r2025/probe.py`, sha256 `bc4d8129…`) unchanged,
with the shape arms added after it. **Nothing in `sim/` changes.***

## What is known before the run, and what was seen

- **Leg P** (the separating arm's price leg, as the 2025 arm runs it, on SAP) is
  price = floor × (b0 + b1·c + b2·max(0, c − 14)), with c the real daily mean FUELHH CCGT GW, fitted on
  pre-crisis days. Its coefficients are 0.7893 / 0.0233 / 0.0200. On real c its monthly MAE / bias is
  3.06 / −0.30 pre, 9.44 / −1.78 crisis, 6.97 / +6.16 post (6.45 / +5.79 without 2025).
- **Seen before this was written:** the electricity page's §1b table of SSP ÷ floor by fixed 2 GW CCGT band.
  Post-crisis it reads 0.57 at 0-4 GW (90 days) and 0.80 at 4-6 GW (151). Pre-crisis it has no day under
  4 GW and 0.84 at 4-6 GW (59). Leg P gives about 0.86 at 3 GW and 0.91 at 5 GW [calc]. The knot at 6 GW and
  the size of every prediction below come from that table. These are informed predictions, not blind ones.
- **Not seen:** any fit with the hinge, or any score of it.
- **Basis caveat carried from the shape arm:** the TTF-basis shape arm (`8e2faf1a3`) found "a level, not a
  shape". The leg-inputs arm showed that level was the proxy's. This arm is the shape question on SAP.

## Arms (one added term: h = max(0, 6 − c))

| Arm | Leg P design | Fitted on |
|---|---|---|
| S0 (control) | 1, c, max(0, c − 14) | pre-crisis days |
| **S1** | S0 + h | pre-crisis days only (62 days under 6 GW, none under 4) |
| **S2** | S0 + h | every record day except the scored calendar year (leave one year out) |
| S3 (oracle) | S0 + h | every record day, in sample |

Each arm is scored on real c and on the chain's own gas running with the 2025 basis rule (Y1's c_hat,
which runs under 6 GW on 197 post-crisis days).

## Predictions

| # | Prediction |
|---|---|
| H-P0 | S0 reproduces the 2025 arm's leg-P-on-real rows to every printed figure, and its Y1 composite rows |
| H-P1 | S1's hinge coefficient is negative, in [−0.12, −0.03] per GW |
| H-P2 | S1 on real c: post bias in [+1.0, +4.5] (from +6.16); post MAE in [4.5, 6.5] (from 6.97) |
| H-P3 | S1 on real c: pre MAE within ±0.15 of 3.06 |
| H-P4 | S1 on real c: crisis bias falls (more negative) by £0.5-3.5 from −1.78 |
| H-P5 | S2 on real c: post bias within ±£2.5, and post MAE no higher than S1's |
| H-P6 | S3's hinge coefficient is more negative than S1's |
| H-P7 | S1 on Y1's c_hat: post composite bias falls by £1.0-4.0 from +7.04 |

## Decision rule

- **(a)** If S1's post bias on real c is within ±£3 and its pre MAE is no more than £0.20 worse than S0's:
  the low-gas depth is a stable multiple of the floor, learnable from the pre-crisis record. It is a build
  term for the price leg, fitted on the whole record.
- **(b)** If S1 misses (a) but S2's post bias is within ±£3: the depth is stable across years but too thin
  before the crisis to learn. The build fits it on the whole record, and the leave-one-year-out figure is
  stated beside every forward number.
- **(c)** If neither: the price on low-gas days is not a multiple of the gas floor. The next arm is a price
  setter that does not scale with gas (§1b: an import at the neighbour's cost, or subsidised output), K8 first.

Reverse: delete this record.
