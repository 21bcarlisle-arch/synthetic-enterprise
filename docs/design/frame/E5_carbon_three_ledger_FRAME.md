# E5_carbon_three_ledger — FRAME (canonical per-atom, doc-only)

**Atom:** `E5_carbon_three_ledger` · lane `E_finance_treasury` · value_stream `close_to_learn` ·
epoch **3** · `level_current: 0` → `level_target: 3` · `loop_stage: idle` (BUILD epoch-parked +
values-call/trajectory-gated) · `provenance: proposal` · `frame_saturated: true` ·
`file_scope: [company/carbon, tests/company/test_carbon_ledger.py, tests/company/test_carbon_not_a_target.py]`
· `depends_on: []`.

**Turn:** Lane-3 FRAME (doc-only, no BUILD code — EPOCH_GATING Rule 1; no map edit — F1; no level
change — a FRAME is not a build). Advances the idle backlog per DIRECTOR_DIRECTIVE_KEEP_BUILDING
(2026-07-21). This is a **COMPANY-layer** atom (`file_scope: company/carbon`) — the epistemic wall
governs every line below.

---

## Why this doc exists (and why it is NOT churn)

E5 has accumulated two real DISCOVER-stage findings —
`docs/design/CARBON_THREE_LEDGER_DISCOVER.md` (the three-ledger data model + counterfactual-method
comparison) and `docs/design/E5_EMISSIONS_FACTOR_REGISTER_DISCOVER.md` (the SPENT-side factor
register) — plus a shipped **rung-1** (`company/carbon/carbon_ledger.py` + its two tests, L0→L1
PROPOSED, 2026-07-20). It had **no canonical per-atom FRAME terminus**. This doc **consolidates**
(does not re-derive) those inputs into one build-ready design with a single stated BUILD-unblock gate,
so the intrinsic saturation guard reads E5 as frame-saturated and the idle draw yields to genuinely
un-FRAMEd work (SELF_INTERRUPT_DISCIPLINE — the treadmill H23 exists to stop). It **resolves** the
open questions a FRAME can resolve (the ledger-taxonomy ambiguity, the belief-vs-truth split, the
reconciliation invariants) and hands the rest — the emissions-factor *set* and the counterfactual
*method* — to the director as the values-calls they are (`CARBON_NOT_A_TARGET_CONSTRAINT.md`: carbon
is the mission, so its definition is cat-6 director-reserved).

---

## 0. Ledger-taxonomy resolution (the ambiguity the prompt flagged, RESOLVED here)

The atom's **"three ledger"** is, per `CARBON_THREE_LEDGER_DISCOVER.md §1` and the shipped
`carbon_ledger.py` docstring, a **carbon P&L**:

| Ledger | What it records | Sign discipline |
|---|---|---|
| **SAVED** (customer) | CO₂e a household would have emitted but did **not**, *because of* an intervention — a **counterfactual**, and the company's own **estimate** of it | non-negative magnitude, tagged `ledger=SAVED` |
| **SPENT** (operational) | CO₂e **emitted** serving customers: people, compute, tokens | non-negative magnitude, tagged `ledger=SPENT` |
| **NET** | SAVED − SPENT, **always reported** (a claim that counts one side is not a claim) | derived, may be negative — never omitted |

It is **NOT** GHG-Protocol scopes 1/2/3, and it is **NOT** generation/supply/customer. **GHG scopes
1/2/3 are an *orthogonal* accounting-boundary dimension that lives *inside* the SPENT ledger** (compute
electricity is scope 2; embodied hardware + upstream cloud is scope 3; a ~1-human company has little
scope 1) — the scope boundary is director values-call #2 (§4). This FRAME uses SAVED/SPENT/NET
throughout and treats "which scopes SPENT counts" as a boundary label on each SPENT event's `basis`,
never a third ledger. This resolves the taxonomy question the task raised.

---

## 1. The epistemic wall (this is the load-bearing part — a COMPANY atom)

The company's carbon ledger must be assembled from **observables only** — what a real UK supplier can
actually know. The critical seam:

| Company CAN observe (through the wall) | Company CANNOT observe (SIM-internal — a wall violation to read) |
|---|---|
| Its **own metered volumes** (customer kWh/therms, from meter reads) | The SIM's ground-truth per-household emissions |
| Its **own compute/token usage** (`RESOURCE_AWARE_SCHEDULING` sensor, sensor available CC 2.1.215) | The SIM's true generation mix behind the published number |
| **Published grid carbon intensity** (NESO/DESNZ, §3) — a public feed, law/data published in reality | The counterfactual carbon a household *didn't* emit, computed by re-running it under CRN (method A) |
| **Published fuel-mix / REGO / Elexon generation-by-fuel** (its own SLC-19A disclosure basis) | Any household's true churn/behaviour propensity |
| Its own procurement/settlement records | VaR/weather-engine/price-chain internals |

**The single sharpest wall risk, RESOLVED here → §5.** The SAVED ledger is a **counterfactual**, and
`CARBON_THREE_LEDGER_DISCOVER.md §2` named three methods. Method **A (same-household CRN A/B)** — run
the simulated household twice, contacted vs not — is a **SIM/harness operation, not a company
observable**; a company that reads method-A output into its own SAVED ledger has read SIM ground truth
(a Tier-1 wall breach). So the FRAME **splits** it: the company's SAVED is a **BELIEF** estimated by
method **B (baseline-trajectory)** from its own observed meter history + published factors (what a real
supplier's carbon desk actually does); method **A is the HARNESS truth** against which that belief is
measured (§5, the coupled-triad gap). This split is the resolution — it was latent in the DISCOVER
doc's "recommended for the SIM" phrasing and is made explicit here.

---

## 2. The three ledgers, built from observables

### SAVED (customer) — a belief, not a read
- **Definition:** avoided CO₂e attributable to an intervention (a ToU nudge, a DER offer, a tariff
  shift that moved consumption to a cleaner half-hour or reduced it).
- **Observable inputs:** the household's **own metered consumption** before and after the intervention
  (meter reads through the wall); the **published grid carbon intensity** at the affected half-hours
  (§3); the intervention record (the company's own contact/offer log).
- **Published-source anchor:** NESO/National Grid Carbon Intensity feed (§3) for the gCO₂e/kWh applied
  to the avoided/shifted kWh.
- **Computation:** `SAVED = Σ (baseline_kWh(hh,t) − actual_kWh(hh,t)) × intensity(t)` where
  `baseline_kWh` is the company's **modelled** counterfactual (method B — a baseline-trajectory model
  fit to the household's pre-intervention observed reads). Emitted as `CarbonEvent(ledger=SAVED,
  provenance="estimated_from_data", basis=<intensity basis>)`.
- **Honest simplifications (R10):** (a) the baseline is a **model**, so attribution to the intervention
  is *weaker than* a true CRN isolation — named, not hidden (this is exactly why §5 measures the gap);
  (b) behaviour-**persistence decay** (does a shifted habit stick, or revert?) is a director values-call
  (§4), defaulted to *no decay* with the decay curve a named open parameter; (c) SAVED **depends on the
  unbuilt per-household cost-and-carbon trajectory** (personalisation) for the baseline — until that
  lands, SAVED has no live feed (this is the L2→L3 gate, §7).

### SPENT (operational) — metered activity × published factor
- **Definition:** CO₂e emitted operating the company: compute electricity, token/inference energy,
  people (office/commute).
- **Observable inputs:** **compute kWh** and **token counts** from the `RESOURCE_AWARE_SCHEDULING`
  sensor (the company meters its own machine — fully observable, no wall issue); **headcount** (its own
  record).
- **Published-source anchor:** per the register (§3) — NESO/DESNZ grid intensity for compute kWh;
  published ML-inference energy-per-token estimate (a *range*, contested) for tokens; DESNZ GHG
  conversion factors for per-FTE.
- **Computation:** `SPENT = Σ activity_i × factor_i(as_of)`, each term an independent
  `CarbonEvent(ledger=SPENT, provenance="estimated_from_data"|"assumed",
  basis="grid_marginal"|"grid_average"|"activity_based")`. The factor is time-indexed (§3).
- **Honest simplifications (R10):** (a) the **token energy-per-unit** spans an order of magnitude in
  published estimates — register a *range + source*, never a point, and consider deferring the token
  term to metered-compute-only until a defensible factor is a director pick (§4.4); (b) **scope-3**
  (embodied hardware, upstream cloud) is a boundary decision (§4.2) — a stated boundary label on each
  event, not a fabricated inclusion; (c) people-emissions for a ~1-human+AI company are small vs
  compute — candidate to scope-out with a *stated boundary*, not silently drop.

### NET — the honest headline
- `NET = SAVED − SPENT`, a **derived view** (never a stored scalar), **always** reported including when
  negative. Already implemented (`carbon_ledger.py::net()`). `£/tCO₂e = cost / NET` is the mission
  DIAGNOSTIC (`cost_per_tonne_abated`), **FAIL-LOUD on NET ≤ 0** (raises `CarbonAbatementUnavailable` —
  a 0/inf would read as "free/great", the fail-open the constraint forbids).

---

## 3. The emissions-factor register (time-indexed, R10-anchored, no fabricated numbers)

Consolidated from `E5_EMISSIONS_FACTOR_REGISTER_DISCOVER.md`. **No autonomous network → no current
published value is asserted; each row names the SOURCE + SHAPE, and any specific value is flagged
`UNVERIFIED — needs <source>` for a discovery-agent pass at BUILD.** Every factor carries
`effective_from`/`effective_to` — grid intensity declined materially 2016→2025 as coal retired and
wind grew, so a single flat factor across the window is itself a defect.

| Activity (observable) | → tCO₂e via | Published source (real) | Effective-dating | Status |
|---|---|---|---|---|
| Compute electricity (kWh) | grid carbon intensity gCO₂e/kWh | **NESO / National Grid Carbon Intensity** (`carbonintensity.org.uk`, key-free, half-hourly actual + forecast); **DESNZ** GHG conversion factors (annual grid-electricity factor) | per-year (DESNZ) or per-half-hour (NESO) — declines across 2016→2025 | value **UNVERIFIED — needs NESO/DESNZ fetch**; source + shape fixed |
| Tokens / inference | energy-per-token (kWh) × grid intensity | published ML-inference energy estimates (contested, order-of-magnitude spread); **usage** from `RESOURCE_AWARE_SCHEDULING` sensor | energy-per-token is the uncertain half | value **UNVERIFIED — needs a cited estimate + range**; candidate: defer to metered-compute-only |
| People (headcount) | per-FTE operational emissions | **DESNZ / GHG-Protocol** conversion factors (office, commute) | annual | value **UNVERIFIED**; candidate: small named constant or scoped-out with a stated boundary |
| Generation mix (for grid intensity derivation, if not taking NESO's published number directly) | fuel-mix share × per-fuel factor | **Elexon** generation-by-fuel (BMRS/Insights); **REGO** / supplier fuel-mix disclosure (the company's own SLC-19A basis) | per-period | source cited; values **UNVERIFIED** |
| £/tCO₂e sanity anchor | — | **£273/tCO₂e (2025, 2022 prices, ±50%)**, UK government appraisal (DESNZ carbon values / Green Book supplementary guidance) | 2025 vintage | **cited**; a sanity band (R12), **never a target** (§6) |

---

## 4. The director values-calls this FRAME surfaces (not decided — cat-6, mission-defining)

Per `CARBON_NOT_A_TARGET_CONSTRAINT.md` the emissions-factor *set* and the counterfactual *method*
define the mission metric and are the director's, exactly like the A/D/G values-calls and the R13
curriculum. This FRAME states them crisply so a single director pass unblocks the SPENT emitter:

1. **Grid marginal vs average intensity.** Average understates incremental consumption; marginal is
   higher and time-varying. Affects BOTH SPENT (compute) and SAVED (avoided). *Recommendation surfaced,
   not chosen: marginal for SAVED avoided-emissions (it is incremental), stated per-event via `basis`.*
2. **The accounting boundary (GHG scopes).** Which of scope 1 / 2 / 3 the SPENT ledger counts — the
   headline-moving boundary. *Recommendation: state the boundary explicitly on every published figure,
   like the R14 clock.*
3. **Time-of-use resolution.** Flat annual grid intensity vs half-hourly. The sim already settles
   half-hourly, so a ToU factor is feasible and matters (cold-still tail = dirtier grid).
4. **Token energy-per-unit source** — which published estimate (order-of-magnitude spread), *or* defer
   the token term to metered-compute-only until a defensible factor exists.
5. **Which counterfactual defines "abated"** (method A/B/C) — and whether behaviour-persistence
   **decays** the SAVED claim over time. §5 resolves the *architecture* (B = company belief, A = harness
   truth); *which* the published SAVED headline uses, and the decay shape, stay the director's.

---

## 5. Coupled-triad framing (belief-vs-truth) — a candidate twin, PROPOSED not registered

E5 is a **COMPANY-side belief** atom, and its SAVED ledger is precisely a belief a real supplier forms
without ground truth. That makes it a natural coupled-triad **company leg**:

- **Belief `b`** = the company's SAVED estimate (method B baseline-trajectory, §2), computed only from
  observed meter history + published factors.
- **Hidden truth `θ`** = the SIM's **actual** counterfactual carbon — method A (same-household CRN A/B,
  the fidelity-ablation discipline) run in the SIM: the household simulated twice under common random
  numbers, contacted vs not, the delta priced at the SIM's *true* grid intensity (drawing on
  `W1_7_renewable_capacity_trends`' time-varying generation mix). This is a **harness/SIM-side**
  quantity, never a company observable (§1).
- **`raw_gap`** = a measure of how far the company's SAVED belief sits from the CRN truth (over- or
  under-claiming abatement); **`g0`** = a no-skill baseline that attributes zero abatement (or a naive
  flat-factor guess). Exact loss + `g0` are genuine BUILD-time judgement, named open here.

**No WORLD twin atom currently exists** for the SIM's ground-truth carbon counterfactual, and **no
coupling is registered** in `background/coupled_triad.py::_AUTHORITATIVE_COUPLING` (checked directly:
the table holds W2_*↔C*/D5 pairs only; there is no carbon/emissions world atom in the map —
`W1_7_renewable_capacity_trends` supplies the *generation mix* but is not itself E5's truth twin).
**This FRAME does NOT self-register the coupling** (that is a BUILD/director act, and self-registering
would be marking-own-homework). It **flags a proposed follow-on**: author a WORLD/HARNESS atom that
computes the CRN counterfactual carbon truth (leaning on W1_7's mix + the method-A ablation), then
register `E5 ↔ <that atom>` at BUILD. **Per COUPLED_TRIAD doctrine, E5 does not reach L3 until it has
faced that world-truth and the belief-vs-truth gap is measured** — this is the L2→L3 gate (§7).

---

## 6. The anti-goal-seek guardrail (R12 / CARBON_NOT_A_TARGET) — already mechanised, must be EXTENDED

`£/tCO₂e` and every derived metric is a **DIAGNOSTIC**: measured, reported, inspected — **never
optimised**, never a reward/selection/ranking input. Three mechanisms, all already shipped in rung 1
and **binding on every future rung**:

- **The grep-guard: `tests/company/test_carbon_not_a_target.py`** (AST-based). **Invariant it must
  encode:** *no decision surface imports `company.carbon`* — the forbidden-importer set is the fitness
  function, the atom draw, the risk committee, and any pricing/personalisation reward path. Rung 1
  mutation-proved it **both directions** (fires on a synthetic import, quiet on a clean tree — R15).
  **R10 class-fix obligation:** as new decision surfaces are added, the forbidden-importer set MUST be
  extended so the *class* stays closed — a new reward path that imports carbon must red this test, not
  slip through. This is the "extend the invariant, don't instance-fix" rule made concrete for E5.
- **No optimisation surface in the module** — `carbon_ledger.py` exposes measurement/reporting only; no
  "improve carbon" method, nothing a selection loop could call.
- **FAIL-LOUD** — an unavailable/zero/negative abatement RAISES (`CarbonAbatementUnavailable`), never
  reads as 0/inf/"great" (fail-open forbidden). The £273/tCO₂e appraisal value is an **external-benchmark
  sanity band (R12)**, a flag that triggers R4 (diagnose the mechanism), never a number to tune toward.

---

## 7. Reconciliation invariants the BUILD must mutation-test (R15)

The eventual BUILD (SPENT emitter + SAVED feed) must add — and mutation-prove firing on its own named
defect — at least these. Each names its **independence guard** (R15 tautology doctrine: the check must
recompute via an *independent* path, never read back the same stored value):

| # | Invariant | Named defect it must catch | Independence / fail-open guard |
|---|---|---|---|
| R15-1 | **NET = SAVED − SPENT exactly**, from derived views not a stored scalar | a stored-scalar shortcut that drifts | recompute from the event stream, not from a cached total |
| R15-2 | **SPENT reconciliation:** each SPENT event's `tco2e` == `activity × factor(as_of)` | a SPENT tco2e that doesn't trace to observed activity × its cited factor | recompute activity×factor via an independent path — do **not** read back the stored `tco2e` (else tautology) |
| R15-3 | **Factor time-index validity:** every event's cited factor satisfies `effective_from ≤ as_of < effective_to` | an anachronistic factor (2025 grid intensity applied to a 2016 event) | the register lookup is the independent oracle; a missing/expired factor **FAILS LOUD**, never defaults to the nearest or to zero |
| R15-4 | **Idempotency (C-S2)** — same `event_id` twice = no double count | a re-add / replay double-counting | keyed by `event_id`; already held in rung 1 |
| R15-5 | **Arrival-order independence (C-S1)** — views identical under any insertion order | an order-dependent aggregation | shuffle-and-compare; already held in rung 1 |
| R15-6 | **FAIL-LOUD on NET ≤ 0** — `cost_per_tonne_abated` raises | a 0/inf that reads as "free/great" | already held in rung 1; extend to any new £/tCO₂e surface |
| R15-7 | **SAVED belief provenance** — every SAVED event is `provenance="estimated_from_data"` and carries no SIM-internal source | a SAVED event sourced from method-A CRN truth (a wall breach) | epistemic_verifier + a test that no `company/carbon` code imports/reads SIM counterfactual internals |

The **"scope totals reconcile to metered volume × factor"** invariant the task named is **R15-2 +
R15-3** together: SPENT reconciles to (metered activity × time-valid factor), independently recomputed,
fail-loud on a missing factor.

---

## 8. Definition-of-Done and the remaining level gaps

- **L0→L1 ("built in any form") — ALREADY MET, held at L0.** Rung 1 shipped 2026-07-20
  (`company/carbon/carbon_ledger.py`: append-only `CarbonEvent` stream; derived SAVED/SPENT/NET +
  £/tCO₂e views, never stored scalars; C-S1/C-S2; FAIL-LOUD cost-per-tonne) + the `CARBON_NOT_A_TARGET`
  grep-guard (R15, both directions). **58 tests green, epistemic PASS.** It is **factor-agnostic** (tCO₂e
  handed in) so the emissions-factor set and the counterfactual method stay director values-calls. Level
  is **L1 PROPOSED**, `level_current` held at 0 pending director level-up — a FRAME never moves a cell,
  and the agent never self-promotes (levels are proposals; the LEVEL gate reverts a self-bump).
- **L1→L2 — the SPENT emitter.** Real activity→`CarbonEvent` using the `RESOURCE_AWARE_SCHEDULING`
  compute/token sensor × the director-chosen factor set (§3/§4), with the time-indexed register (R15-3)
  and the reconciliation invariant (R15-2). **Unblocked by one director values-call:** (a) marginal-vs-
  average, (b) scope boundary, (c) token-energy source (or defer tokens). No trajectory dependency —
  SPENT is buildable the moment factors are chosen.
- **L2→L3 — the SAVED live feed + the coupled-triad gap.** Requires (i) the **unbuilt per-household
  cost-and-carbon trajectory** (personalisation) for the method-B baseline; (ii) the director's
  counterfactual-method + persistence-decay values-call (§4.5); (iii) the **coupled-triad twin**
  authored and `E5 ↔ <twin>` registered, and the belief-vs-truth gap **measured** — E5 does not reach
  L3 until it has faced that world (COUPLED_TRIAD doctrine, §5). NET is derivable the moment either side
  has one real event.

---

## 9. The single BUILD-unblock gate (epoch-sequencing intelligence — HELD at L0)

| Atom | Epoch | Level (held) | Single BUILD-unblock gate | Gate class |
|------|-------|---------------|---------------------------|------------|
| `E5_carbon_three_ledger` | 3 | **0 (→3)** | **(1) Director values-calls** (§4): the emissions-factor SET (marginal-vs-average, scope boundary, ToU, token source) unblocks the **SPENT** rung; the counterfactual METHOD + persistence decay unblocks the **SAVED** headline. **(2)** the unbuilt **per-household cost-and-carbon trajectory** (personalisation) lands, feeding SAVED's method-B baseline. **(3)** a **coupled-triad world/harness twin** (CRN counterfactual carbon truth, leaning on `W1_7`) is authored + `E5 ↔ twin` registered, for the L3 gap. **(4) Epoch-3 BUILD-open** (director/TWIN, within the open epoch, per `EPOCH_GATING_AND_ATOM_AUTHORSHIP.md` Rule 1). | DIAL (director values-call + trajectory dependency + epoch sequencing) — **not** a wall; empty feasible set here is a correct hold on a values-call, not a Rule-0 defect |

**Disposition:** level **HELD at 0** (`loop_stage: idle`; rung-1 built = **L1 PROPOSED**, FRAME complete
≠ built; SPENT is values-call-gated, SAVED is trajectory-gated + L3 is coupled-triad-gated;
EPOCH_GATING Rule 1). This FRAME is E5's canonical terminus — the next idle draw reads E5 as
frame-saturated and yields to genuinely un-FRAMEd work. **No BUILD code, no map edit (F1), no level
change, no self-registered coupling.**

---

*Sources consolidated (not re-derived): `docs/design/CARBON_THREE_LEDGER_DISCOVER.md` (three-ledger
data model, counterfactual-method comparison, values-calls), `docs/design/E5_EMISSIONS_FACTOR_REGISTER_
DISCOVER.md` (the SPENT-side factor register), `docs/design/CARBON_NOT_A_TARGET_CONSTRAINT.md` (the
binding diagnostic wall), `company/carbon/carbon_ledger.py` + `tests/company/test_carbon_not_a_target.py`
(the shipped rung-1 data model + grep-guard, read directly), `docs/design/maturity_map.yaml`'s own E5
`simplifications` (2026-07-20 DISCOVER/BUILD registration), `background/coupled_triad.py`
(`_AUTHORITATIVE_COUPLING` — confirmed no carbon twin registered), `docs/design/frame/
W1_7_renewable_capacity_trends_FRAME.md` (the generation-mix source the CRN truth would lean on) and
`docs/design/PURPOSE_PITCH_V4.md §9` (the mission this atom measures). The proposed coupled-triad twin
is named, never self-registered — that is a BUILD/director act.*
