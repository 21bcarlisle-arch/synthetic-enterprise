# FRAME — W1_2_generate_futures

**Atom:** `W1_2_generate_futures` — Synthetic future market generation beyond real 2016-2025 history
**Lane:** `W1_market_weather` · **dial:** 4 · **level_current:** 0 → **level_target:** 2
**depends_on:** `W1_reveal_over_time`
**Stage:** FRAME/DISCOVER (doc-only). BUILD is gated — this artifact does not move the level.

---

## 1. What this atom is & why

The baseline world is the real UK half-hourly settlement history 2016-2025 (Elexon/NESO), replayed
through externally-calibrated generators. That history contains exactly one realised path: one
2021-22 gas crisis, one COVID demand collapse, one 2016 calm year. A company that survives the
replayed past has survived *one* draw from the distribution of possible worlds — it has not been
stress-tested against worlds that plausibly *could* have happened but didn't.

`W1_2_generate_futures` generates plausible **synthetic future market paths** — prices (wholesale
day-ahead / imbalance / forward curve) and volatility regimes — that extend beyond the end of the
real record. The purpose is adversarial: give the SIM the ability to run the company forward through
2026+ worlds it has never seen, including regimes with no historical analogue (a price war, a
sustained high-vol plateau, a demand shock), so the harness can measure how the company's hedging,
pricing, and capital models cope when the future is genuinely unknown.

This is a **SIM-depth** atom: it enriches the world, not the company. The company gains nothing it
can read directly — only a harder world to survive.

## 2. The R13 wall this atom MUST respect (central design constraint)

R13 (`MARGIN_REALISM.md`) splits the world in two, and this atom sits astride the split:

- **BASELINE** (real 2016-25 history + externally-calibrated generators): may change **only for
  fidelity-to-reality reasons**, decided **blind to company P&L**. Never tuned because company
  results look wrong.
- **CURRICULUM** (which worlds the company lives through): the **DIRECTOR'S**. Difficulty changes
  are **named, versioned, director-authored artefacts** ("Scenario: 2027 price war"), never silent
  parameter drift, and **never adjusted by the agent in response to company outcomes**.

**Synthetic futures are CURRICULUM artefacts, full stop.** The generator's *statistical machinery*
(what makes a path "plausible UK" — return distributions, seasonality, vol clustering) is calibrated
to reality and is fidelity-owned, blind to P&L. But every *choice of which scenario to run and how
hard it is* — regime mix, shock magnitude, start conditions, seed set — is a director-authored
curriculum decision. The agent MUST NOT:

- pick or tune scenario parameters because the company is winning too easily or losing too hard;
- add a "harder" regime in response to a good P&L, or soften one after a bad run;
- treat margin as a target the curriculum steers toward (that is R12 anti-goal-seek too).

The agent MAY: author candidate scenarios as `provenance: proposal` (DISCOVER/FRAME), calibrate the
fidelity machinery to external data blind to P&L, and mechanise the *published, versioned* scenario
the director selects. The wall is enforced structurally: scenario definitions live as versioned,
named files facing the director; the generator reads a scenario spec, it does not invent one. A
missing scenario spec is a hold-for-director, not an agent default.

## 3. Method options for synthetic path generation

Each method must reconcile to fidelity anchors from real UK data. **All anchors: benchmark required
(source: Elexon/NESO)** — no numbers are fabricated here; calibration is a BUILD-time step against the
real record.

| Method | Mechanism | Fidelity anchors it must reconcile to |
|---|---|---|
| **Block bootstrap** of historical returns | Resample contiguous blocks of real day-ahead/imbalance returns to preserve short-run autocorrelation & vol clustering | Marginal return distribution, block-length vs autocorrelation decay, seasonality of blocks — *benchmark required (source: Elexon/NESO)* |
| **Regime-switching / Markov** | Hidden-state model (calm / stressed / crisis), transition matrix drives regime, within-regime process draws prices | Regime frequencies & persistence, transition probabilities estimated from 2016-25, per-regime vol/mean — *benchmark required (source: Elexon/NESO)* |
| **Calibrated stochastic process** | Mean-reverting (e.g. OU / jump-diffusion) with seasonal drift + stochastic vol for spikes | Mean-reversion speed, seasonal shape, jump frequency/size, vol-of-vol — *benchmark required (source: Elexon/NESO)* |

Selection criteria: block bootstrap is highest-fidelity for "more of the same" but cannot produce a
regime with no historical precedent; regime-switching and calibrated processes can extrapolate to
*unseen* regimes (the whole point of stress testing) at the cost of parametric assumptions. A likely
L2 shape is block-bootstrap as the fidelity-faithful default, with regime-switching as the
director-selectable curriculum knob for no-precedent worlds. **Calibration is blind to P&L** (R13);
the *choice of which extrapolation to run* faces the director.

Reconciliation is a hard gate: any synthetic path population must pass a distributional sanity check
against the real record (vol, seasonality, spike statistics within plausibility bands anchored to
Elexon/NESO) — a generator that produces implausible UK prices is a fidelity defect regardless of
what scenario it serves.

## 4. Point-in-Time Blindfold

Generated futures are the **SIM's ground truth**. They are constructed and held entirely inside the
world layer. The company never receives the synthetic path; it receives only **realised
observations** as sim-time advances — the same observable interfaces a real supplier has (settled
market data feeds, its own bills/reads, published forward curves *as of the current sim-time*).

Concretely: the generator produces the full future path up front (deterministic given seed — see §8),
but the SIM/company seam (`company/interfaces/sim_interface.py`) exposes only the slice of that path
that has *already occurred* at the company's current clock. Future half-hours of the synthetic path
are as invisible as tomorrow's weather is to a real supplier. This is where `W1_reveal_over_time`
(the dependency) does the work: reveal-over-time is the mechanism that gates the pre-generated path
behind sim-time, so a generated future cannot leak backward through the wall. **The wall test**: at
any sim-time T, the company's observable set must be a function only of path values at times ≤ T,
never > T — a company model whose output depends on a not-yet-revealed value is a blindfold breach.

## 5. COUPLED TRIAD framing

Per COUPLED_TRIAD_DESIGN (A6) — the gap is the score:

- **SIM adds depth:** the ability to run the company through synthetic 2026+ worlds, including
  regimes with no historical analogue. World becomes capable of *defeating* a company tuned to the
  replayed past.
- **COMPANY copes through the wall:** its hedging / pricing / capital models meet a future they
  cannot see and were not fitted to. It is *allowed to be wrong* — mis-forecasting a synthetic
  regime is the expected, informative outcome, not a bug to patch.
- **HARNESS measures the belief-vs-truth gap:** company's forward belief (hedge ratios, price
  forecasts, VaR) vs the SIM's realised synthetic path. The gap per synthetic scenario is the
  reported score each digest / Proof door. Binding triad rules: this SIM atom does not reach L3 until
  the company has been tested against a generated future and the gap measured.

## 6. Level decomposition

- **L1** — A single synthetic path generator (one method, likely block bootstrap) produces a
  fidelity-checked future price series beyond 2025, held as SIM ground truth, revealed only via the
  blindfold seam. Distributional sanity check against the real record passes. Draws from a named
  seeded RNG substream (§8). No scenario library yet; one default path.
- **L2 (target)** — Multiple named, director-authored curriculum **scenarios** (e.g. calm
  continuation / high-vol plateau / price-war), each a versioned spec the generator reads (never
  invents). Regime-switching available as the no-precedent knob. Each scenario reconciles to Elexon/
  NESO fidelity anchors and carries its provenance (director-authored vs agent-proposal). Company can
  be run through any scenario; harness reports the belief-vs-truth gap per scenario. R13 wall
  structurally enforced (generator reads spec, missing spec → hold-for-director).
- **L3+ (not this atom's target)** — gap measured across the scenario library, time-scale-invariance
  declared, promotion only after a company has faced a world that can defeat it.

## 7. Dependencies, BUILD unblock, open director gates

- **depends_on `W1_reveal_over_time`:** the reveal mechanism is the blindfold enforcer for a
  pre-generated path (§4). Until reveal-over-time exists and is tested, a generated future cannot be
  safely held without risking leakage — so BUILD stays gated on it.
- **What unblocks BUILD:** (a) `W1_reveal_over_time` at a level that gates a pre-generated path
  behind sim-time; (b) a director-authored scenario spec format / at least one named baseline-
  continuation scenario to build against (curriculum authorship is the director's — §2); (c)
  DIRECTOR_TWIN BUILD-open within the open epoch.
- **Open director gates:** (1) the initial scenario library — *which* named worlds exist and their
  difficulty is a curriculum/values decision (one-way-door category 6-adjacent); (2) sign-off that
  the fidelity-calibration step is genuinely blind to P&L; (3) confirmation of the plausibility bands
  used for the distributional sanity check (anchored to Elexon/NESO, not to company results).

## 8. Portability & scale-readiness

- **C-S2 deterministic replay + RNG SUBSTREAM discipline (directly load-bearing):** the future-market
  generator MUST draw from its **own named, seeded RNG substream** — never the shared world RNG. This
  is exactly the law proven necessary by the 01:09Z life-event incident: adding a new stochastic
  subsystem to a shared stream silently shifts every downstream draw. A synthetic-future generator is
  a large new source of draws; on a shared stream it would perturb weather, churn, and every other
  stochastic subsystem, destroying replay determinism and cross-run comparability. Own substream ⇒
  regenerating the same scenario+seed reproduces the identical path (deterministic replay), and the
  scenario can be added/changed without disturbing any other subsystem's outputs.
- **C-S5 time-scale invariance:** an L3+ claim must declare whether path generation is time-scale
  invariant (HH vs daily granularity) or register the granularity as a named simplification (R10).
- **Portability (second market/product):** the scenario spec and generator must be keyed by
  market/commodity, not hardcode UK-power specifics into the path logic — a second geography or a gas
  scenario should fit the same generator behind a typed boundary (no hardcoded settlement granularity
  or monetary treatment). Log as portability debt if the L1/L2 build hardcodes; do not build a second
  market now.
- **SIMPLICITY GUARD:** satisfy the above with the simplest construct — a named seeded substream and a
  versioned scenario file, not a scenario-engine cathedral.
