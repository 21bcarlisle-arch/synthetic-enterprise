# W1_10 — EV + Heat-Pump Adoption Geography (FRAME)

**Atom:** `W1_10_ev_heatpump_geography` (`docs/design/maturity_map.yaml`), `level_current: 0`,
`level_target: 3`, `loop_stage: idle` (Epoch-3 BUILD-gated), `dial_inherited: 3`,
`file_scope: [docs/design]` (this FRAME gives BUILD a concrete scope; no code written here).
**Depends on:** `W1_5_premise_demand_shape` (the per-premise demand response this modifies) and
— added by this FRAME — `W1_4_regional_weather_field` (heat-pump load is a function of *regional*
temperature `T_{r(i)}(t)`, so the adoption layer cannot sit above only the national signal).
**Sources:** `docs/design/WEATHER_PHYSICS_HIERARCHY_DESIGN.md` (the W1_3→W1_4→W1_5 hierarchy this
extends; §1.3 premise attributes already list `solar/battery/EV` as *static* flags — this FRAME
makes them a *spatially-and-temporally-varying adoption process*), `company/market/network_charges.py`
(the DNO-area partition already in the repo), `sim/weather_engine.py` (the region calibration set),
`company/crm/property_model.py` / `property_discovery.py` (premise attributes), CLAUDE.md WALLS
(epistemic wall, Historical Ground Truth, anti-marking-own-homework), C-S1..C-S5, R10/R12/R15,
COUPLED_TRIAD, portability constraints.

**What was out of scope, and why** (G3 Finding-2 discipline): this FRAME does **not** design the
*price* consequence of regional load growth (that is the merit-order / W1_2 futures work), does not
design the DNO network-reinforcement cost feedback (a later B/commercial slice), and writes no code —
Epoch-3 BUILD stays gated. It scopes only the **adoption process and its load signature on the demand
hierarchy**, because that is the physics W1_10 owns and the layer W1_5 sits under.

---

## 1. The gap this fills

WEATHER_PHYSICS_HIERARCHY_DESIGN.md builds coherent demand physics — national signal (W1_3),
aggregation-consistent regional field (W1_4), premise-level weather-driven demand (W1_5). But its
premise demand model treats EV/heat-pump ownership as a **fixed per-premise attribute**. In reality
these are the two fastest-moving structural drivers of GB demand *shape and level*, and both are
**spatially uneven** and **growing on an S-curve through the 2016–2025 window and beyond**:

- **Heat pumps** add *temperature-correlated* winter electrical load that is **coincident with the
  system peak** — so heat-pump geography reshapes the regional peak, not just annual volume. Uptake
  skews to **off-gas-grid, rural, higher-income, higher-EPC** properties (MCS install data, DESNZ
  sub-national stats): Scotland, SW England, rural Wales lead; dense urban gas-connected areas lag.
- **EVs** add *charging* load, concentrated evening/overnight and **tunable by smart-charging tariffs**
  (this is where the company's own ToU products bite — `company/pricing/tou_product_launch.py`). Uptake
  skews to **higher-income suburban with off-street parking**; dense inner-London (on-street-parking
  friction) lags on private charging despite high registration counts.

A model with static, spatially-uniform EV/HP shares will **mis-shape regional load growth** and
therefore mis-forecast peak, hedging volume, and network cost — the exact fidelity the atom exists to
add. The adoption geography is a first-class **stochastic subsystem with its own RNG substream**
(`adoption_field`, C-S2), layered *between* W1_4 (regional weather) and W1_5 (premise demand).

---

## 2. Construction — three levels (mirrors the weather hierarchy's national→regional→premise shape)

Let `𝓡` be the GB region partition BUILD chooses (reuse the existing partition rather than invent one:
the `network_charges.py` DNO areas or the `weather_engine.py` calibration regions — named, not
hardcoded per portability constraint; the adoption process is keyed by `region_set`, not "GB DNOs").

### L1 — national adoption S-curves per technology (`level 1`)
For each technology `k ∈ {ev, heat_pump}`, a logistic diffusion curve `a_k(t)` giving the national
share of eligible premises adopted at time `t`, **calibrated to real published history**
(DVLA/DESNZ EV registrations; MCS/DESNZ heat-pump installs) over 2016–2025 and extrapolated on the
fitted curve beyond. Monotonic non-decreasing (no un-adoption). RNG: none for the mean curve
(historical fit); a national timing jitter uses the `adoption_field` substream only.

### L2 — regional adoption field, aggregation-consistent (`level 2`, the W1_4 analogue)
Each region `r` gets a share `a_{k,r}(t) = a_k(t) · m_{k,r}(t)` where `m_{k,r}` is a **regional
multiplier** driven by observable regional covariates (off-gas-grid fraction, rural/urban, income/EPC
proxy) with **spatial correlation** (neighbouring regions covary — a distance-keyed field, reusing
W1_4's Cholesky machinery). The multipliers satisfy the **aggregation-consistency invariant** exactly
as W1_4's I1 does, so the layer cannot drift off national truth:

> **I(adopt):**  `Σ_r w_r · a_{k,r}(t) = a_k(t)`  ∀ `k, t`, where `w_r` is region `r`'s eligible-premise
> weight (`Σ_r w_r = 1`). Enforced by a **weighted-mean projection** on the raw multipliers (the same
> structural device W1_4 uses for weather), not a fudge.

### L3 — premise asset assignment + load signature into W1_5 (`level 3`, the target)
Each premise `i` in region `r(i)` is assigned EV / heat-pump flags by a draw consistent with its
region's rate `a_{k,r(i)}(t)` **and** premise eligibility (a flat with no off-street parking is a low-
probability EV private-charge premise; a gas-connected terrace is a low-probability heat-pump premise —
so the within-region assignment is covariate-weighted, not uniform). The flags then modify W1_5's
premise demand:

```
D_i(t) = base_i · seasonal(t)
       + heating_i · g_heat( T_{r(i)}(t), thermal_i, heating_type_i )   # W1_5, now heating_type ∈ {…, heat_pump}
       + hp_flag_i(t)  · g_hp_load( T_{r(i)}(t), thermal_i )            # NEW: temp-correlated, peak-coincident
       + ev_flag_i(t)  · g_ev_charge( t, smart_tariff_i )              # NEW: evening/overnight, tariff-tunable
```

`g_hp_load` is keyed to **regional** temperature (so a cold spell in one region lifts *that* region's
heat-pump load — the whole point of sitting above W1_4). `g_ev_charge` is time-of-day shaped and
responds to the premise's tariff, giving the company's smart-charging products a real lever.

---

## 3. WALL / epistemic honesty

- **Adoption is COMPANY-KNOWABLE at the aggregate.** Regional EV registration and MCS heat-pump
  install statistics are genuinely published; the company also directly observes **its own customers'**
  assets. So L1/L2 outputs and the company's own book sit on the **public side of the wall**. What the
  company must *not* read is the SIM's per-premise ground-truth assignment for non-customers — it
  infers the rest from published regional rates + its own sample, and is **allowed to be wrong** (the
  gap, §5).
- **Anti-marking-own-homework (carried from the REGISTERED note, binding):** the **GENERATOR** anchors
  to the fitted historical adoption series; the **VALIDATOR** must use a **different source** —
  independent published **sub-national** EV/heat-pump statistics (DESNZ sub-national energy consumption,
  MCS regional install counts, regional degree-day-adjusted consumption) **not used in the generator
  fit** — checking the L2 field's demand-weighted aggregate and the L3 premise aggregate reproduce real
  regional adoption *shares* and the real load-growth gradient. Never validate against SIM truth.
- **Historical Ground Truth (WALL):** the 2016–2025 national curves are fit to real history, not tuned
  to make company P&L look right (R12/R13 — this is BASELINE-world fidelity, decided blind to P&L).

---

## 4. Invariants (mutation-testable, R15 — a control that cannot fail is worse than none)

| # | Invariant | Enforced by | Mutation that must make it FAIL |
|---|---|---|---|
| A1 | regional → national adoption: `\|Σ_r w_r a_{k,r}(t) − a_k(t)\| ≤ tol` ∀ k,t | weighted-mean projection on multipliers | offset one region's multiplier by ε≫tol; swap the weight vector |
| A2 | monotone adoption: `a_{k,r}(t+1) ≥ a_{k,r}(t)` ∀ k,r | cumulative-diffusion construction | inject a decrement in one region-year |
| A3 | premise ↔ regional consistency: `\|(Σ_{i∈r} flag_{k,i}(t))/|r| − a_{k,r}(t)\| ≤ tol` | covariate-weighted assignment normalised to the rate | bias the per-premise draw high in one region |
| A4 | heat-pump load is peak-coincident & temp-driven: winter-peak Δload correlates with `T_r` and with `a_{hp,r}` | `g_hp_load(T_{r(i)}, …)` | flatten `g_hp_load` to a constant → correlation collapses |

**Fail-open guards forbidden (R15 FAIL-OPEN/FAIL-SILENT doctrine):** a missing region, an empty weight
vector, a malformed adoption series, or an unavailable validator source is a **FAILED** check, not a
pass — the invariant fails closed, and the mutation harness proves it by removing each input in turn.
The checker recomputes against the **independently held** national series / published stats, never the
value it is checking (R15 TAUTOLOGY guard, mirroring W1_4 I1's design).

---

## 5. The gap is the score (COUPLED_TRIAD)

**Coupled pair:** SIM adds spatially-varying EV/HP adoption → COMPANY forecasts regional load growth
from its own book + published regional stats (allowed to misread — e.g. under-weighting off-gas-grid
heat-pump acceleration) → HARNESS measures **gap = |company regional-load-growth forecast − SIM regional
outturn|** per region, reported each digest. Binding per COUPLED_TRIAD: W1_10 does not reach L3 until the
company has been tested against an adoption-geography world and the gap measured; and the company's
regional load-forecast capability is not "complete" until it has faced a geography that can defeat a
spatially-uniform assumption. The gap is the fidelity delta, not a number to minimise (R12).

---

## 6. Cross-cutting constraints (cheap now, brutal to retrofit)

- **C-S2 (RNG substream + deterministic replay):** all adoption stochasticity draws from a single named
  `adoption_field` substream — adding it must not shift any other subsystem's draws (the 01:09Z
  shared-RNG incident precedent). Replaying a history reproduces identical assignments.
- **C-S1 (event-arrival tolerance):** regional covariates / adoption updates may arrive incrementally
  and out of order; the projection is a pure function of the current field, order-independent.
- **C-S5 (time-scale invariance):** the diffusion curve is expressed in real time, not step count —
  register any half-hourly-step assumption as a named R10 simplification.
- **Portability:** keyed by `region_set` and technology-generic (`k ∈ {ev, heat_pump}` extensible to a
  third technology, e.g. battery/V2G, with no new engine) — no GB-DNO hardcoding in the logic.

---

## 7. Level definitions & BUILD task list (`level_target: 3`)

- **L1** — national EV & heat-pump adoption S-curves calibrated to real 2016–2025 published history;
  monotone; `adoption_field` substream wired; determinism test green.
- **L2** — regional adoption field with spatial correlation and the **A1 aggregation-consistency**
  invariant enforced + mutation-tested; regional gradient (off-gas-grid / income proxies) calibrated.
- **L3 (TARGET)** — premise asset assignment (A3) consistent with regional rates + eligibility; the
  `g_hp_load` / `g_ev_charge` signatures wired into W1_5 premise demand (A4); VALIDATOR (independent
  published sub-national stats) green; **COUPLED_TRIAD gap measured** against a company regional-load
  forecast; R10 simplifications registered.

**Ordered BUILD steps (Epoch-3, when opened):** (1) fit + register national curves from published
history; (2) add the `adoption_field` substream; (3) regional multiplier field + A1 projection reusing
W1_4's Cholesky machinery; (4) premise covariate-weighted assignment + A3; (5) `g_hp_load`/`g_ev_charge`
into the W1_5 demand sum + A4; (6) VALIDATOR against the held-out published source; (7) COUPLED_TRIAD
gap measurement + digest wiring. Proposed BUILD `file_scope`: `[sim/weather_engine.py or a new
sim/adoption_geography.py, sim/*, tests/sim]` — **disjoint from W1_2/W1_3/W1_4** at the file level
(shares only the region-set constant), so it can run concurrently once its dependencies (W1_4, W1_5)
have landed at L2+.

**Open questions for BUILD (not blocking FRAME):** (a) exact region partition — DNO areas vs
`weather_engine.py` calibration regions vs GSP groups (BUILD picks the one W1_4 adopts, for a shared
weight vector); (b) heat-pump eligibility rule (off-gas-grid + EPC threshold) — calibrate to MCS data;
(c) whether V2G/battery export is a W1_10 technology or a later atom (lean: later, keep `k` extensible).

BUILD-ready; Epoch-3 gated. Twin can open when W1_4/W1_5 reach L2.
