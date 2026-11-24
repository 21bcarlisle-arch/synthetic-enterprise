**Severity:** RECORDED · **Lane:** G_data_learning · **Atom:** `W1_6_physics_price_signal`

# Result: a demand year term takes about half of the chain's gas-running miss, and the identity form still leaves 1.9 GW unexplained after the crisis (2026-11-24)

*Autonomous worker, 24 Nov 2026. Item 4 of the weather-to-price steer (BLOCKING finding, G_data_learning).
Pre-registered in `docs/staging/records/WORKER_PREREG_DOES_THE_CHAINS_RESIDUAL_DECIDE_HOW_MUCH_GAS_RUNS_ONCE_DEMAND_MUST_RUN_AND_SOLAR_ARE_IN_2026-11-24.md`
(`f616ad94e`). Probe `/var/tmp/mk27/measure_g.py`, sha256 `75553019...` (unchanged), run in a worktree at
`f616ad94e`. Output `/var/tmp/mk27/out_g.json`. **Nothing in `sim/` changes.***

**Disclosure on order.** The pre-registration was committed through the full gate as `f616ad94e` before the
probe ran. It was promoted to origin only *after* the run: `surgical_land` from a worktree does not push, and
I had not run `promote_worktree_landing`. The bytes on origin are the bytes gated before the run, so the
predictions are unchanged. But the record said "landed before its probe runs", and on origin that was not true.

## Outcomes (post = Jul 2023 on; c_hat − c in GW; composite bias in £/MWh, monthly, demand-weighted)

| Arm | Post c_hat − c | Post days < 6 GW (record 241) | Post composite MAE / bias | Crisis composite bias | Pre daily R² |
|---|---|---|---|---|---|
| G0, the chain's residual | +3.12 | 0 | 11.92 / +11.75 | −1.09 | 0.437 |
| G1, + demand year term | **+1.73** | 0 | **9.37 / +8.44** | **−6.19** | 0.466 |
| G2, + must-run by year | +3.19 | 0 | 12.09 / +11.90 | −0.70 | 0.426 |
| G3, + solar out | +2.57 | 4 | 11.11 / +10.81 | −0.80 | 0.493 |
| G4, G3's inputs, identity form (k = −0.61) | +1.86 | 79 | 10.79 / +10.39 | +1.67 | 0.493 |

For reference, leg P on real gas running: post 6.97 / +6.16. Arm X: 10.38 / +8.23. Without 2025, G4's post
miss is +1.62 GW, so the 2025 renewable clamp is not what is left.

| # | Prediction | Outcome |
|---|---|---|
| Q0 | G0 reproduces mk25 (+3.12 GW, +11.75) | **Held.** +3.12, +11.75 |
| Q1 | G1 post miss in [+1.5, +2.6] and composite bias falls by at least £2 | **Held.** +1.73, and the bias fell £3.31 |
| Q2 | G2 post miss above G1's | **Held.** +3.19 |
| Q3 | G3 moves less than 0.5 GW from G2 | **Wrong.** It moved 0.62. With solar out, the fit's linear coefficient on r rose from 0.17 to 0.79 (the quadratic term fell from +0.014 to −0.005), so the term changed the fit, not just its level |
| Q4 | G3 post days under 6 GW below 60 | **Held.** 4 |
| Q5 | G4 post \|miss\| ≤ 1.0, ≥ 100 days under 6 GW, MAE ≤ 9.0 | **Wrong** on all three: +1.86, 79, 10.79 |
| Q6 | G4 pre daily R² in [0.35, 0.75] | **Held.** 0.493 |

## What the rule says

- **(a) fires (Q1).** The demand year term is a build term. It halves the post-crisis gas-running miss. On its
  own it is the best post-crisis composite of the five arms. But it costs the crisis: bias goes from −1.09 to
  −6.19, because 2022's −1.37 GW demand term is priced at crisis gas. The term cannot ship alone without
  that cost being stated beside it.
- **(b) does not fire.** The identity form is not enough by itself.
- **(c) fires (Q5 fails on the miss).** Something else sits between the chain's residual and gas running.

**By year, post hoc** (rule (c) asks for it; not pre-registered; `/var/tmp/mk27/by_year.py`, output
`by_year.txt`). G4's gas-running miss is +0.06 to +0.87 GW in 2017-2022, then +1.67 (2023), +1.62 (2024) and
+2.69 (2025). G1 alone misses by +0.87 (2023) and +2.12 (2024). The step comes in 2023, and must-run by year
makes it worse in every post-crisis year.

## Candidates for what is left, not attributed

- **The wind leg's target.** §4a measured AGWS wind below FUELHH wind by 0.89 GW (crisis) and 0.36 GW (post).
  The chain's wind is mean-matched to AGWS, so after the crisis it under-counts the wind that displaces gas.
  The sign is right. On the post-crisis mean, 0.36 GW is about a fifth of the 1.86 GW left, so it cannot be all of it.
- **Fuels outside the must-run sum.** Hydro, pumped storage, OCGT and oil are not in G2's term, and neither
  is the steady identity gap that station load fits. Each is small on a daily mean.
- **The chain's demand inside each year.** The year term moves the level only. The chain's temperature-only
  demand (R² about 0.55) is still what varies the residual day to day.

## Next

1. **K8 on a forward transmission-demand path** (rule (a)): NESO's FES and the ND trend. It must be sourced
   before any year term enters `demand_from_weather`, and the forward path is the director's curriculum.
2. **The one-variable arm on the wind leg's target**: the chain's wind mean-matched to FUELHH wind instead of
   AGWS, on G4's inputs. Pre-register it first.

Reverse: delete this record.
