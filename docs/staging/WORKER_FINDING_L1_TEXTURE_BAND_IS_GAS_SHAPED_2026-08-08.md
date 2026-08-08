# [WORKER-FINDING] W1_12 stays L2: the last red cell is a heat-pump home, and the band judging it was derived from gas homes (2026-08-08)

**Drawn work:** `W1_12_premise_trace_generator`, L2 -> L3 (lane `W1_market_weather`, dial 3).
**Outcome: the level did NOT move. W1_12 remains at L2**, on a measured red cell, not on a hunch.
**Every number below is `observed-with-evidence`** — re-measured this tick at HEAD `e492096d4`
via `python3 tools/couple_fabric.py --write-ledger`, not read from the previous ledger row.

---

## 1. The draw was live, and the stale-cell check was the reason to look

The doorbell named W1_12 at level 2 -> 3. The atom's own park reason (simplifications register,
2026-08-03) said the L2->L3 step was blocked because "the company twin `C14_thermal_parameter_inference`
is still L0". **That block is dead** — C14 is `level_current: 2` in the map today, and
`H_GAP_fabric_belief_truth_gap` is L2 with the measuring tool (`tools/couple_fabric.py`) built and
wired. This is the known "park reason may name a dead mechanism" class: the blocker cleared and the
park text did not.

The gap ledger's W1_12 row was stamped `run_git_commit: 381b0f2c`, **2026-08-03** — five days and one
generator change stale. Commit `46422b0d6` (2026-08-08) adopted the persistent household clock and
the two-state lighting/electronics model. Re-verifying rather than re-stamping the cell is the whole
finding: the stale row said two cells were red, and it was wrong about one of them.

## 2. What the re-measurement changed — L2 closed on its own

| | ledger @ `381b0f2c` (2026-08-03) | ledger @ `e492096d4` (this tick) |
|---|---|---|
| `failed_levels` | **`['L1', 'L2']`** | **`['L1']`** |
| L1.1 half-hourly texture | 0.1213 **fail** | 0.1248 **fail** |
| L2.3 timing diversity | 0.4073 **fail** (thr 0.5) | **1.0223 pass** |
| L1.2 day-to-day shape r | 0.3789 pass | 0.3295 pass |
| L2.1 smoothing ratio | 0.3439 pass | 0.3389 pass |
| L2.2 between-home r | 0.0653 pass | 0.0604 pass |

**Level 2 is now green.** The adopted household-clock work did exactly what it was adopted to do:
giving each premise a persistent `routine_offset_periods` took the population sd of each home's mean
evening-peak period from 0.407 to 1.022 against a 0.5 threshold. That cell needed no new work this
tick — it needed someone to re-run the measurement and notice.

The smoothing curve is worth quoting because it is the coupled leg working as designed:
`{1: 14.4, 3: 8.3, 5: 7.18, 10: 4.9}` — peak÷mean falls monotonically with N. The original defect
this suite was built to catch was "5.9 at N=3 vs 5.7 at N=1 — aggregation smooths nothing".

## 3. The one remaining red cell, diagnosed rather than patched (R4)

`L1.1_half_hourly_texture` = **0.1248**, threshold **0.15** (`at_least`), verdict FAIL, worst home **H10**.

The cell is a WORST-HOME statistic, so one home fails it for the whole population. Per-home values:

| home | heating | L1.1 texture |
|---|---|---|
| F8 | gas | 0.2931 |
| T5 | gas | 0.2425 |
| F1 | gas | 0.2403 |
| T2 | gas | 0.2221 |
| S3 | gas | 0.2186 |
| S6 | gas | 0.2179 |
| D4 | gas | 0.2064 |
| S9 | gas | 0.1915 |
| D7 | gas | 0.1804 |
| **H10** | **heat pump (ASHP)** | **0.1248** |

**Nine of ten homes pass comfortably, inside the 20–40% domain expectation the band's own anchor text
cites. The single failing home is the panel's only electrically-heated home** (`PANEL` entry H10,
`HeatingSystem.HEAT_PUMP_AIR`; every other entry is `GAS_BOILER_COMBI`).

**The mechanism is arithmetic, and it was measured, not inferred.** Decomposing H10's electricity into
its behavioural (appliance) stream and its heat-pump stream:

```
H10:  texture(full electricity)   = 0.1248    mean = 0.3150 kWh/hh
      texture(behavioural only)   = 0.2130    mean = 0.1608 kWh/hh
      heat-pump share of electricity = 49.0%
S3 (gas):  texture(electricity) = texture(behavioural) = 0.2186   mean = 0.1430 kWh/hh
F8 (gas):  texture(electricity) = texture(behavioural) = 0.2931   mean = 0.0891 kWh/hh
```

**H10's appliance behaviour is as spiky as everyone else's — 0.2130, mid-pack among the gas homes.**
The generator is not producing a smooth home. Texture is `median |x[t] − x[t−1]| ÷ mean(x)`; the heat
pump is 49% of H10's electricity and roughly doubles the denominator while contributing very little
period-to-period movement, being a thermally-driven, slowly-varying load. 0.2130 × (0.1608/0.3150)
= 0.109, and the observed 0.1248 sits just above that — the heat pump contributes a little movement
of its own. **The whole of H10's deficit is accounted for by the denominator.**

## 4. What this means, and what I am deliberately NOT doing (R12)

The band's own `anchor_source` reasons from a gas-heated premise in as many words: *"a kettle is 2.8 kW
for three minutes on a ~0.7 kWh half-hour"*. It is `AnchorStatus.DOMAIN_KNOWLEDGE`, threshold 0.15,
and it is applied as **one national floor to every home regardless of heating system** — which is
structurally the same defect this atom exists to remove (one national constant), reappearing in the
CONTROL rather than in the generator. A real ASHP home's half-hourly electricity genuinely is smoother
in *relative* terms than a gas home's, because a large steady load sits underneath the same spikes.

**I have not touched the threshold, and I recommend nobody does on this evidence.** Relaxing a band
because the thing it judges fails it is precisely the goal-seek R12 forbids, and this suite already
carries a tuning detector for the neighbouring case (L1.1 passing while L1.5 fails prints
"SOMEONE TUNED THE NUMBER"). Marking H10 `UNVALIDATED` would turn the suite green and unblock L3 in one
edit, which is exactly why it is not a call to make as a side-effect of a build tick.

**Checked before recommending:** there is **no anchor for heat-pump half-hourly load texture anywhere
in `docs/domain_artefact_library/`** (grep: zero files mention heat pumps). So a heat-pump band cannot
be set tonight without inventing a number, and an invented threshold is unfalsifiable — the thing R15
exists to prevent.

**Recommendation (one atom's worth of DISCOVER, needs a real source, not a decision):** condition L1.1
on heating system and anchor the electrically-heated band to published evidence — the BEIS/DESNZ
Electrification of Heat demonstration project and SERL's heat-pump subsample are the obvious
candidates, both of which publish half-hourly ASHP load data. Until an anchor exists, the honest
treatment of an unanchored band is `UNVALIDATED` (measured, not judged) — the same standing L1.4 and
L2.4 already have in this very suite — **but that reclassification should land with the anchor, not
before it**, because it is the edit that moves the level.

## 5. Consequences recorded

- **W1_12 stays `level_current: 2`.** Its exit test is "must pass the two-level test" and the suite is
  RED. No level was moved, no map edit made.
- **The gap ledger row is now current** (`measured_at` 2026-08-08T20:54:49Z, `run_git_commit` `e492096d4`),
  replacing the 2026-08-03 row. `failed_levels` `['L1','L2']` -> `['L1']`.
- The coupled-triad L3 gate (`background.coupled_triad.world_l3_blocked`) would now return *unblocked*
  for W1_12 — twin C14 is at L2 and the gap IS measured. **The gate is satisfied and the atom still
  should not move**, because the gate tests the coupling, not the atom's own exit test. Worth saying
  plainly: passing the L3 gate is necessary, not sufficient.
- Diagnostic, not a target (R12): `inference improvement` is **−0.0277** — C14's posterior is *worse*
  than the EPC register on raw HLC error (0.2325 vs 0.2049). On the money consequence it is better
  (misrank 0.000 vs 0.100, £0 vs £83 forgone). Reported as measured; the company is allowed to be wrong.

## 6. Verification

`python3 -m pytest tests/simulation/test_premise_trace.py tests/harness/test_premise_two_level.py
tests/tools/test_couple_fabric.py -q` -> **145 passed, 1 xfailed in 21.29s** at HEAD before any change
this tick. The only file changed by this tick's measurement is the ledger JSON.

— Worker tick, 2026-08-08.
