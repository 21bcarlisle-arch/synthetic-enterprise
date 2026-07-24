# FRAME — VALUE_CHAIN counterparty-resolution — the margin-conduct coupled triad

**Provenance.** PRODUCT-FIRST item 3 (VALUE_CHAIN first organs, `docs/PRIORITIES.md`;
`DIRECTOR_RULING_PLANNER_MINT_WAIVED_2026-07-24.md` item 2). The observation-window credit cap
(`company/trading/wholesale_credit_exposure.py`) is LIVE but honestly **DORMANT**: it erodes a
counterparty's credit line only when fed observed settle/dispute/default conduct, and *nothing produces
that conduct stream yet*. The `PLANNER_MINTED_value_chain_observation_window_cap` mint's step-3 note named
this world-half as **"a walled coupled atom, gated on its own side of the wall — NOT a bare company-side
worker-tick action."** This is that atom's FRAME artefact. It **opens no BUILD atom and moves no map
level** — the build proposal in §10 returns through the twin/director gate (F1 precedent).

**Why a FRAME and not a build:** *whether* a counterparty settles/disputes/defaults reflects its **true
default propensity, which lives behind the wall**. A company-side model that *decides* counterparty
defaults would be a Tier-1 epistemic violation. So this must be authored as a coupled SIM/world atom and
faces world-atom gating (COUPLED_TRIAD: no world atom reaches L3 until the company has been tested against
it and the gap measured) — not an autonomous company-side increment.

**DISCOVER basis.** `docs/market_research/uk_supplier_hedge_counterparty_distribution_2026-07-24.md`
(rating bands public/wall-safe; true default probability sim-internal; Oxera 2021-failures review — the
margin/collateral death-loop is real at the generator/major-trader level, **distinct** from the domestic
under-hedging failure mode) + 4 rows in `ASSUMPTIONS.md`. Consumer-seam reconciliation:
`company/trading/wholesale_credit_exposure.py` (the COMPANY half is **already built** — see §3b).

---

## 1. What this atom is & real-world grounding

A real supplier's counterparty credit line is not a static dict — it is *earned and eroded* by how the
counterparty actually honours margin calls over time. The observation-window cap already models the
COMPANY side of that erosion; what is missing is the **world that produces the conduct to observe**:
counterparties who, under wholesale stress, settle / dispute / default on the margin they owe, at rates
governed by their true (hidden) credit quality. This atom builds that producer, wall-correctly, so the
cap's erosion physics has real blood.

**External grounding (all independent of SIM ground truth, DISCOVER-cited):**
- **Rating→default is public and quantified:** agency (S&P/Moody's/Fitch) published historical
  one-year default and transition rates by letter band are the SIM's calibration target — investment
  grade sub-0.5%/yr rising steeply through sub-investment grade. These are **public** (a supplier reads
  them) → wall-safe as the SIM's *calibration anchor*, never as a company-side read of a specific
  counterparty's truth.
- **The death-loop is real but channel-specific (Oxera):** the acute margin/collateral drain sits at the
  **generator/major-trader** counterparty level (Uniper/Fortum ~$29bn 2022), **not** the domestic
  under-hedging failure (`MIN_HEDGE_FLOOR`). MC-2 must be a **distinct** failure channel — this FRAME
  keeps them separate (see §9).
- **Stress raises dispute/default jointly:** a wholesale price shock both inflates the margin owed and
  degrades counterparty liquidity → resolution outcomes worsen exactly when exposure peaks (the
  multi-period feed already captures the peak-£786k-at-2021-crisis exposure this conduct would bite).

---

## 2. The central mechanism — resolution is a function of stress × hidden quality

> **resolution = f( margin_call_size, counterparty_true_credit_quality, market_stress_state )
> → {SETTLED, DISPUTED, DEFAULTED} + latency**

where `true_credit_quality` is a hidden per-counterparty latent (calibrated so its *band-average* matches
the published agency default rate for the counterparty's public rating band). The company never sees the
latent; it sees only the typed `CounterpartyResolutionOutcome`. That asymmetry is the whole atom — a
company that inferred the latent directly would be an intent-leak (§3c control).

---

## 3. The three components

### 3a. SIM — the counterparty-resolution model (behind the wall, allowed to hold truth)
- **Inputs:** a typed `MarginCallOwedToCompany{counterparty_id, amount_gbp, rating_band, deadline}` event
  (the *owed-to-us* leg — the credit-exposure side, NOT the company-owes liquidity leg; see §3b note).
- **State per counterparty:** hidden `true_default_propensity` + `dispute_propensity` latents (independent
  named draws; band-average pinned to published agency default rates — a fidelity anchor, not a P&L knob),
  plus a `market_stress` coupling that raises both under a wholesale shock. None crosses the wall.
- **Output:** a typed `CounterpartyResolutionOutcome{call_id, counterparty_id, resolution ∈
  {SETTLED, DISPUTED, DEFAULTED}}` — **the exact type the COMPANY consumer already consumes** (§3b).
- **Discipline:** own **named RNG substream** (C-S2 — a resolution draw never shifts another subsystem's
  outputs; forced by the shared-RNG-incident precedent); resolution is a **separate event in time** from
  the call (C-S3 async — a deadline then an outcome, never same-step); typed-flow seam (the wall IS the
  go-live seam — swap for a real counterparty's actual conduct behind the unchanged type).

### 3b. COMPANY — credit-observation + cap erosion (in front of the wall, **already built**)
The company half exists and is R15-proven (`company/trading/wholesale_credit_exposure.py`, mint ticks 3+6):
- `CounterpartyResolutionOutcome` / `MarginResolution` — the **typed consumer contract** the §3a producer
  plugs into (typed-flow-seam-first: the consumer shape was defined before the producer).
- `observed_behaviour_from_resolutions(outcomes)` — a **pure, order-invariant, idempotent** fold
  (C-S1/C-S2) aggregating observed outcomes into `ObservedCounterpartyBehaviour`; it **aggregates, never
  decides** (epistemic-verifier PASS on its diff).
- `observation_window_credit_limit(rating, behaviour)` — the rating-band **prior** eroded monotonically by
  `adverse_score` toward the floor (one-directional: conduct can only erode, never earn a line above the
  band). The company's belief is explicitly permitted to diverge from truth — that divergence is the score.
- **Wall note (a real fork this FRAME preserves):** the sixth-tick seam deliberately types the
  *owed-to-us* credit leg **distinct** from the company-owes liquidity leg (`build_margin_calls_from_mtm`),
  so the SIM producer cannot wire the sign-inverted side by accident. §3a emits ONLY the owed-to-us leg.

### 3c. HARNESS — the gap (the score)
Two measured gaps + one adversarial control:
1. **Belief-vs-truth credit gap** per counterparty: the company's eroded-cap belief (its
   `observation_window_credit_limit` given observed conduct) vs the SIM's true default propensity — the
   coupled-triad GAP, reported per digest in `coupled_gap_ledger.json` (no `WVC_*` pair exists there yet).
2. **Did the cap protect the book:** realised credit loss under the eroded cap vs a static-dict control —
   the cap earns its keep only if a deteriorating counterparty's line tightened *before* the default.
3. **R15 credit-leak control (mandatory):** a company whose cap correlates with the true latent **beyond
   what its observed resolutions justify** is a leak — a named defect the harness must *catch*. Mutation
   test: inject a company variant that peeks at `true_default_propensity`; the control must fire. Without
   that test the wall is theatre (R15 doctrine).

---

## 4. COUPLED TRIAD — the gap is the score (A6 binding rules)

| loop | owns | allowed to |
|---|---|---|
| **SIM** | true default/dispute propensity, resolution physics, stress coupling | be realistic; never expose internals |
| **COMPANY** | conduct observation, cap erosion *belief* | **be wrong** — learn only from observed outcomes |
| **HARNESS** | belief-vs-truth credit gap + loss-protection + credit-leak control | measure, never help either side |

Binding: no SIM/world part reaches L3 until the company has been tested against it and the gap measured;
no company capability is complete until it has faced a counterparty that can defeat it (the cap is only
proven once a real default has eroded a line it should have). The gap is reported per digest.

---

## 5. Level decomposition (target L2 first; L3 director-reserved)

- **L1** — types + one counterparty end-to-end: SIM emits a resolution stream for one bilateral name under
  a benign path, COMPANY folds it and the cap holds at the prior (no adverse conduct → honest no-erosion),
  HARNESS logs a zero gap. Propensity sampled from the published band default rate.
- **L2** — the full 5-type counterparty set (CCP-cleared + bilateral bank/trader/generator + broker flag);
  stress-coupled resolution (dispute/default rise under a wholesale shock); the belief-vs-truth gap + the
  loss-protection score; the **credit-leak control with its passing mutation test**.
- **L3** (director-reserved) — the **MC-2 collateral death-test** as a *distinct* channel (§9): a crisis
  curriculum world whose margin-call spike drains liquidity past the facility so the company *can die* to
  collateral, R15 both-ways (survives benign, dies MC-2). Gated because the crisis *difficulty* is
  director-curriculum (R13), never agent-tuned.

---

## 6. Dependencies & sequencing
- **Reuses** the built consumer seam (§3b — do NOT re-draw it), the multi-period exposure feed
  (`exposure_by_counterparty_as_of`, peak-mid-run mark), the counterparty-attribution taxonomy on
  `ForwardContract`, the typed-flow seam, the event-log.
- **New** only: the SIM resolution producer + its two latents + stress coupling (§3a), and the three
  harness scores (§3c). No new billing/risk engine, no new RNG framework.
- **Does not depend on** any unresolved upstream question (the company half is done, the exposure feed is
  live) → passes the two-way-door filter. The one gate is the world-atom gating itself (director/twin).

## 7. Scale-readiness lenses (C-S1..C-S5)
Async call→resolution (C-S3) and named RNG substream (C-S2) are load-bearing: resolutions arrive singly,
late, out of order (C-S1 — the consumer fold is already order-invariant + idempotent by `call_id`), and
processing a resolution twice must be harmless (C-S2, already proven consumer-side). Persistence via the
event-log abstraction (C-S4). Time-scale invariance (C-S5): the call→resolution lag is a declared
parameter, not a hardcoded step.

## 8. Portability lens
Product-first: the resolution type keys on counterparty + call, not on any GB-specific construct — a second
market's counterparties fit the same 5-type taxonomy behind the unchanged seam. No counterparty
hardcoding (the producer keys on rating band + type, not a named bank). Any GB-specific calibration
(agency default rates) is config, not baked. Debt logged, not fixed speculatively (PORTABILITY_DEBT.md).

## 9. Curriculum note (R13 — baseline/curriculum split)
The **baseline** — rating-band-conditioned default/dispute propensities calibrated to published agency
default rates — may change only for fidelity-to-reality reasons, decided **blind to company P&L**. **Which
crises the company must face** — the MC-2 collateral-death scenario's spike magnitude/shape — is the
**director's curriculum**: named, versioned, never tuned toward a company outcome, and never adjusted
because the belief-gap or a survival rate looks wrong. The resolution rates are a **diagnostic, never a
target** (R12). **MC-2 must stay a DISTINCT failure channel from the domestic under-hedging
`MIN_HEDGE_FLOOR` mechanic** — the Oxera evidence attaches the collateral death-loop to the
generator/major-trader level; conflating them would misattribute the UK-specific evidence.

---

## 10. The build proposal (returns through the gate — no atom opened here)

Proposed as a **coupled triad**, disjoint file_scopes (the COMPANY leg is already delivered):

| candidate atom | lane / scope | exit test (the gate) |
|---|---|---|
| `WVC_Ra_sim_counterparty_resolution` | SIM/world (`sim/**` or `company/interfaces` seam side) | typed call→resolution over the wall; own RNG substream proven independent (C-S2 mutation); band-average default rate matches the published agency anchor within tolerance; stress raises dispute/default jointly |
| `WVC_Rb_company_credit_observation` | COMPANY (`company/**`) | **ALREADY BUILT** (`observed_behaviour_from_resolutions` + `observation_window_credit_limit`, R15-proven ticks 3+6) — the gate here is only that the belief never reads the true latent (epistemic-verifier PASS, already holds) |
| `WVC_Rc_harness_credit_belief_gap` | HARNESS (`tests/`/harness) | reports belief-vs-truth credit gap + loss-protection-vs-static-cap + **credit-leak control fires on its mutation** (R15 — a peeking company variant is caught); registers a `WVC_R` pair in `coupled_gap_ledger.json` |

**Definition of done (triad):** the gap is reported per digest; the credit-leak mutation test passes; no
epistemic-wall violation on the SIM diff; the cap demonstrably tightens a deteriorating line *before* its
default in at least one coupled scenario (the "cap earns its keep" proof).

**Open values-calls for the director (do not block FRAME; needed before L3):**
1. **Curriculum:** the MC-2 collateral-death scenario — spike magnitude/shape/which counterparty channel
   (default proposal: a benign steady-state resolution curriculum at published base default rates, with
   **no** adversarial margin-spike world until the director authors MC-2). This is the one director-reserved
   value; the mechanism + a benign default is all the agent may build.
2. **The agency-anchor calibration source** — which published default-rate table (S&P/Moody's/Fitch) is the
   canonical baseline anchor. A fidelity (R13) decision, director-facing since it defines the baseline world.

**What this FRAME explicitly does NOT do:** open any atom, write any BUILD code, or touch the maturity
map. The triad above is a proposal for the twin/director gate. The COMPANY leg being already built is the
typed-flow-seam-first pattern working as intended — the consumer contract stabilised before the producer.
