**Severity:** RECORDED · **Lane:** G_data_learning · **Atom:** `W1_6_physics_price_signal`

# Pre-registration: does the chain's residual decide how much gas runs once demand by year, must-run by year and solar are in? (2026-11-24)

*Autonomous worker, 24 Nov 2026. Item 4 of the weather-to-price steer (BLOCKING finding, G_data_learning).
Filed and landed before the probe runs. The probe is `/var/tmp/mk27/measure_g.py`, sha256
`75553019e77a9cc96e9ee614752617ac33dd14f4d37121eaf3cb8021569212f4`. It will run in a worktree at the origin
commit this lands on. **Nothing in `sim/` changes.***

## Why this arm

The separating arm (`ea6b89ef6`) found the larger term of the post-crisis miss is leg H: the chain's residual
never runs gas below 6 GW, and overstates post-crisis gas running by 3.1 GW. Electricity page §4a (`25886bc99`)
names three terms between the chain's residual and gas running, none of them in the chain: demand held flat,
must-run by year, and embedded solar subtracted twice. This arm adds them one at a time, in §4a's size order,
then asks whether the fitted form of leg H is itself the limiter.

**Disclosed before filing:** §4a's by-year tables were seen before these predictions were written (the chain's
demand miss by year, must-run by year, the solar double count's size). No fit on these inputs has been run.

## Definitions

Arm X inputs and leg P exactly as mk25 (SAP in the call and the refit, real net export in the chain's demand;
leg P fitted once, on PRE days, with real CCGT). c = real daily mean FUELHH CCGT (GW). Regimes as mk25. MAE and
bias are monthly and demand-weighted. Each arm refits only leg H (c_hat = h0 + h1·r + h2·r², PRE days only).

- **G0:** r = the chain's residual. The reproduction of mk25.
- **G1:** G0 + a demand year term. r += (record INDO + net export, mean for the day's year) − (the chain's demand,
  mean for that year). NESO says ND "is equivalent to INDO", so on the record this is ND by year.
- **G2:** G1 + must-run by year. r −= FUELHH NUCLEAR + COAL + BIOMASS + OTHER, mean for the day's year. OTHER is
  in because FUELHH carries biomass under it until late 2017.
- **G3:** G2 + solar out of the residual. r += the chain's solar, because INDO is already net of embedded solar.
- **G4:** G3's inputs in the identity form: c_hat = r − k, slope fixed at 1, k = mean(r − c) on PRE days.
  This changes the form, not an input, and is reported as a separate arm.

Post is also reported without 2025, which is a part year with the renewable fleet clamped to 2024 (§4a).

## Predictions

| # | Prediction |
|---|---|
| Q0 | G0 reproduces mk25: post c_hat − c = +3.12 ± 0.05 GW, composite post bias +11.75 ± 0.05. If it fails, the arm is not comparable and nothing below is read |
| Q1 | G1, post: c_hat − c falls to between +1.5 and +2.6 GW, and the composite post bias falls by at least £2 (to ≤ +9.75) |
| Q2 | G2, post: c_hat − c is higher than G1's (must-run by year works against the overstatement, §4a) |
| Q3 | G3, post: c_hat − c moves by less than 0.5 GW from G2's |
| Q4 | G3, post: c_hat has fewer than 60 days under 6 GW (the record has 241). The fitted quadratic stays flat |
| Q5 | G4, post: \|c_hat − c\| ≤ 1.0 GW, at least 100 days under 6 GW, and composite monthly MAE ≤ 9.0 (G0: 11.92; leg P on real c: 6.97) |
| Q6 | G4, pre: daily R² of c_hat on c is between 0.35 and 0.75 |

## Decision rule, filed now

- **(a) Q1 holds.** The demand year term is a build term. Next is K8 on a forward transmission-demand path
  (NESO's FES and the ND trend), then the term in `demand_from_weather`. The forward path is the director's
  curriculum, carried in a sourced band.
- **(b) Q5 holds.** The fitted leg H is the limiter, not only its inputs. The build is the identity form: gas
  running = residual − must-run − k, with must-run by year on the record and a forward capacity path
  (curriculum, GAP until sourced). The chain is rebuilt on leg P plus that leg in one commit, and its grade
  against the gas-only null is re-run.
- **(a) and (b) can both hold.** Then the build carries both.
- **(c) Q5 fails on the overstatement (> 1.0 GW post).** Something else sits between residual and gas. Report
  it by year, with no build. Read `post_ex2025` first, to separate the 2025 clamp.

Nothing ships from this arm under any outcome. It decides what the build is.

Reverse: delete this record.
