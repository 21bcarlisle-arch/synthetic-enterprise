# E5_carbon_three_ledger — DISCOVER + FRAME (widened scope, B9)

**Atom:** `E5_carbon_three_ledger` · lane `E_finance_treasury` · epoch 3 · `loop_stage: idle`
**Turn:** Lane-3 DISCOVER/FRAME fork, 2026-07-29. **Doc-only.** No BUILD code; nothing under
`company/`, `saas/`, `sim/`, `simulation/`, `background/` was created or modified
(EPOCH_GATING_AND_ATOM_AUTHORSHIP.md Rule 1).

**Why this doc exists.** A canonical per-atom FRAME already exists at
`docs/design/frame/E5_carbon_three_ledger_FRAME.md` (22,837 bytes, commit `71e204c93`) and covers the
2026-07-20 scope: the three-ledger data model, the counterfactual-method comparison, and the
emissions-factor register. The director's 2026-07-29 re-open (`from_rich_20260729_173731`, BACKLOG
item **B9**) **widened** the scope past it and named two genuinely un-FRAMEd parts:

1. how a **per-household cost-and-carbon trajectory** is derived **from observables only** (the wall);
2. how the site's **£/tCO₂e figure carries its clock/basis (R14)**, plus the plain-language working.

This doc frames those two, and — because a FRAME that rests on a false premise is worse than none —
**corrects a factual error in the existing FRAME that would have caused the exact fail-open this atom
must guard against** (§1.4). It does not re-derive what the prior FRAME already settled; it cites it.

Every claim below is labelled `[observed-with-evidence]` or `[inferred]` per **R9**.

---

## PART 1 — DISCOVER (what already exists, verified against disk)

### 1.1 The rung-1 ledger — built, and it already enforces the basis discipline

`company/carbon/carbon_ledger.py` (167 lines, shipped 2026-07-20) `[observed-with-evidence]`:

| What | Where | Note |
|---|---|---|
| `CarbonEvent` frozen dataclass | lines 69–100 | fields `event_id, ledger, source, tco2e, basis, provenance, as_of` |
| **`basis` is a REQUIRED non-empty field** | lines 93–94 | raises `CarbonEventMalformed("basis must be non-empty (a carbon figure without its basis is a defect)")` |
| `provenance` constrained to an enum | line 55, 95–98 | `estimated_from_data \| assumed \| asserted` |
| Derived-only views | lines 124–138 | `saved()`, `spent()`, `net()` — never stored scalars |
| FAIL-LOUD £/tCO₂e | lines 140–153 | `cost_per_tonne_abated` raises `CarbonAbatementUnavailable` when `net <= 0` |
| Idempotency (C-S2) | lines 113–116 | keyed by `event_id`; re-add is a no-op |
| Arrival-order independence (C-S1) | lines 124–125, 157–159 | sums over a dict, stable `event_id`-sorted view |

**This is the single largest REUSE finding.** The **R14 clock discipline already exists at the event
level** — `basis` and `provenance` and `as_of` are mandatory per event, and construction *fails closed*
without them. The widened-scope work is therefore **not** "invent a carbon clock"; it is **propagate the
per-event basis up into the published aggregate** so a rendered £/tCO₂e cannot lose its basis on the way
to the page (§2.3). `[inferred from the code shape above]`

**Gap in the rung-1 module `[observed-with-evidence]`:** the three derived views
(`saved()/spent()/net()/three_ledger_view()`) return **bare floats and a `{str: float}` mapping**
(lines 127–166) — **the basis does not survive aggregation.** `three_ledger_view()` returns
`{"saved_tco2e": ..., "spent_tco2e": ..., "net_tco2e": ...}` with no basis, no provenance mix, no
`as_of`. A publisher consuming that mapping publishes a basis-less carbon number while every underlying
event carried one. That is the concrete R14 defect to close (§2.3, R15-C1).

### 1.2 The activity-cost mechanism (G11) — the operational denominator already exists

`G11_activity_cost_utilisation` is `level_current: 3`, `loop_stage: idle`
(`docs/design/maturity_map.yaml:1799–1813`) `[observed-with-evidence]`. Live output
`site/data/activity_cost.json` (generated `2026-07-29T18:03:33Z`, git `8fc2a4b5b`):

- **Time attribution** — `time_attribution.by_class_seconds`, 7 PRODUCTIVE/WASTE classes,
  `attributed_seconds: 4,385,104`, `unattributed_seconds: 118,363`, `n_commits: 6,587`. Source: git
  commit clock, inter-commit gap capped at `idle_gap_cap_seconds: 1800`.
- **Token attribution** — `token_attribution.total_tokens: 1,760,127`, `by_class_tokens` over the same
  7 classes. Source: `docs/observability/token-log.md`, parsed by
  `tools/activity_cost.py::parse_token_log` (line 381) on the regex `_TOKENS_RE` (line 378,
  `**Frontier tokens:** <n>`).
- **Guardrail already stated in the artefact:** `guardrail: "DIAGNOSTIC, NEVER A TARGET (R12 / G5 law)"`.

**What the carbon ledger REUSES:** the **activity denominators** — elapsed operating time and frontier
tokens, already classified, already attributed, already fail-honest. E5's SPENT ledger must **consume
`site/data/activity_cost.json` (or `tools/activity_cost.py`'s pure functions), never re-instrument.**
`[inferred — the design decision, stated so a BUILD fork cannot accrete a second meter]`

**What it must NOT duplicate:** the classification taxonomy, the git-clock attribution, the token-log
parse. G11 owns those at L3 with a hand-labelled accuracy control
(`tests/tools/test_activity_cost_accuracy.py`, coarse 0.938 / fine 0.859).

**Inherited weaknesses that become CARBON weaknesses (this is the important half) `[observed-with-evidence]`:**

- `token_attribution.n_entries: 25`, **`n_parsed: 7`, `n_unparsed: 18`.** Only **7 of 25** token-log
  sessions parse. `attribute_tokens` (line 448) excludes unparsed entries from the numerator and
  surfaces `n_unparsed` — fail-honest, never fabricated — but it means the token denominator covers a
  **minority of sessions**. A SPENT ledger reading `total_tokens` as *the* token spend would understate
  it, and understating SPENT **inflates NET**, which **flatters** the mission metric. This is a
  self-flattering direction and must be labelled on the published figure, not buried.
- G11's own registered, still-open fail-opens apply transitively: the **fork-churn blindness**
  (2026-07-18 note — killed forks that commit nothing are invisible, `WASTE/rework` read 0 tokens
  while ~190k fork tokens were actually burned) and the **harden-of-harness / same-level-arrow**
  self-flattering classifier holes (2026-07-27 notes #2 and #3, both pinned `xfail(strict)`). Carbon
  SPENT built on G11 inherits every one of them. `[observed-with-evidence, from the map entries]`

### 1.3 Carbon-intensity data — more exists on the company side than the prior FRAME credited

`[observed-with-evidence]`

- **`company/sustainability/carbon_intensity_register.py`** — a real, shipped company module:
  `_CARBON_INTENSITY_G_CO2_PER_KWH` per-fuel factors (lines 44–56: gas 394, coal 820, nuclear 12,
  wind 11/12, solar 41, hydro 24, biomass 230, imports 300, other 200) **and
  `_GRID_AVERAGE_INTENSITY`, a per-year 2016→2025 UK grid-average table** (lines 57–68: 350 → 165
  gCO₂/kWh). Its docstring cites NESO Annual Fuel Mix, Elexon BSC FMD, DESNZ, REGO.
- **`company/regulatory/fuel_mix_disclosure.py`** — the company's own SLC/Disclosure-Regulations fuel-mix
  and blended-intensity computation (`carbon_intensity_gco2_per_kwh`, lines 82, 106, 175, 186).
- **`sim/generation_demand_history.py`** — real Elexon Insights half-hourly demand (`/demand/outturn`)
  and wind+solar generation (`/generation/actual/per-type/wind-and-solar`), key-free, Historical Ground
  Truth. **SIM-side**: the company may not import it (the wall). The company's legitimate route to the
  same information is the *published* feed (regulation-commons doctrine: published data is readable by
  every lane) — NESO/DESNZ published intensity, not the SIM's module.
- **`docs/market_data/`** holds only `price_feed.json` and `consumption_feed.json` — **there is no
  carbon-intensity feed file today.** `[observed-with-evidence]`

**Consequence for the FRAME:** the SPENT-side compute factor does **not** need a new register invented.
`_GRID_AVERAGE_INTENSITY` (2016–2025, annual) is a **usable, already-shipped, source-cited** grid-average
factor. What it lacks is (a) `effective_from`/`effective_to` dataclass dating in the
`company/compliance/domain_invariants.py` shape, (b) any half-hourly resolution, and (c) any
marginal-vs-average declaration — all three of which are **director values-calls**, unchanged (§4).
`[inferred]`

### 1.4 CORRECTION — the `RESOURCE_AWARE_SCHEDULING` sensor **does not exist**

`[observed-with-evidence]` The existing FRAME
(`docs/design/frame/E5_carbon_three_ledger_FRAME.md` lines 61, 102, 137) lists as an *observable input*:
"**compute kWh** and **token counts** from the `RESOURCE_AWARE_SCHEDULING` sensor (sensor available
CC 2.1.215)". The 2026-07-20 map entry (`maturity_map.yaml:2074`) makes the same claim.

`grep -rn "RESOURCE_AWARE" --include=*.py` over the whole tree returns **zero hits**. The only
occurrences are in prose: `docs/design/RESOURCE_AWARE_SCHEDULING_PROPOSAL.md` (a **proposal**),
`SCHEDULED_BOUNDED_INVOCATIONS_DESIGN.md:186`, `SELF_MEASUREMENT_UNIFIED_DESIGN.md:95,143`,
`PARALLEL_LANES_PROPOSAL.md:1`, the maturity map, and the FRAME itself.

**There is no token sensor and no compute-power sensor.** The nearest real thing is
`background/ntfy_responder.py::_gpu_summary` (lines 291–305), which shells `nvidia-smi
--query-gpu=utilization.gpu,memory.used,memory.total` for a **point-in-time status string** for an NTFY
digest — it is **not integrated over time, not logged to any timeseries, and not a kWh meter**.

**Why this matters more than a citation nit.** A BUILD fork reading the prior FRAME would wire the SPENT
emitter to a nonexistent sensor. Absent input → zero events → `spent() == 0.0` → `net() == saved()` →
the mission metric reads its **best possible value because the feed is missing**. That is the textbook
FAIL-OPEN this atom's own constraint doc names, reached through a stale premise rather than a coding
error. **Corrected here; the R15 control in §5 is written specifically to catch it.**

### 1.5 The observables that DO exist for the customer side

`[observed-with-evidence]`

- **`docs/market_data/consumption_feed.json`** — `published_at`, `records`: 288 rows of
  `{customer_id, date, period, kwh, hour}`. **Per-customer, half-hourly, settlement-period-keyed
  consumption.** This is the raw observable a baseline-trajectory model is fit to.
- **`docs/reports/run_output_latest.json::per_customer_lifetime.<id>.cost_to_serve_gbp`** — real
  per-customer cost-to-serve already computed (C1 £274.94, C2 £505.43, C3 £219.95, … C_IC1 £4,218.12),
  alongside `net_margin_after_cost_to_serve_gbp`. **The first half of the £/tCO₂e numerator already
  exists at the per-customer grain.**
- **`company/crm/customer_profitability_scorecard.py:60`, `company/compliance/fair_value_assessment_register.py:63`**
  — `cost_to_serve_gbp` is first-class company vocabulary, not a new concept.

### 1.6 The R14 gate, and where a carbon figure would slip past it

`[observed-with-evidence]` `tools/generate_dashboard_data.py`:
- `_BASIS_REQUIRED_PORTFOLIO_KEYS = ("net_margin_gbp", "enterprise_value_gbp")` (line 1691)
- `_check_basis_labels_present(portfolio)` (line 1694) → `basis_ok` folded into the publish gate
  (lines 1586–1588); failure raises `"BASIS-LABEL GATE FAILED: headline figure(s) missing a basis
  label"` (line 1710).
- The basis entries carry `"clock": "settled"` (lines 259, 270).

**No carbon key is in `_BASIS_REQUIRED_PORTFOLIO_KEYS`.** A published `£/tCO₂e` or `net_tco2e` today
would pass the gate **by not being checked** — the R15 FAIL-SILENT shape (a checker that is simply
never invoked on the value). Extending that tuple is the concrete, small, named mechanisation (§2.3).

### 1.7 The site's honest current state

`[observed-with-evidence]`
- `site/assets/model-on-a-page.svg:216` renders "Carbon ledger designed, not yet instrumented".
- `docs/design/THE_MODEL_ON_A_PAGE.md:61` — "designed ledger (SAVED/SPENT/NET), honestly *not yet
  instrumented* — the site says so".
- `site/test_home_door.py:70–75` **asserts** the front door carries
  `"carbon abatement through personalisation"`, `"273/tCO&#8322;e (2025)"`,
  `"per tonne of CO&#8322;e saved"`, **and** the literal disclaimer `"designed, not yet instrumented"`.

This is a **good** existing gate: the disclaimer cannot be removed silently — a test fails. Per the
director's re-open, it comes off **only** when the LIVE rendered figure is asserted (**R11**).

### 1.8 No coupled-triad carbon twin exists

`[observed-with-evidence]` `background/coupled_triad.py::_AUTHORITATIVE_COUPLING` (lines 52–77) holds
`W2_7→C9, W2_8→C10, W2_5→C7, W2_4→C6, W2_10→C12, W2_6→C8, W2_9→C11, W2_11→D5, W1_5→C13, W1_6→C13`.
`grep -i "carbon\|E5"` over the file returns nothing. Unchanged from the prior FRAME's finding; not
self-registered here (registering a coupling is a BUILD/director act).

---

## PART 2 — FRAME (design, not build)

### 2.0 The one-line design decision

> **The carbon ledger measures nothing itself. It is a *derivation layer* over meters that already
> exist — G11's activity attribution for SPENT, the half-hourly consumption feed for SAVED — and its
> only original contribution is (a) carrying each figure's basis intact from event to pixel, and
> (b) refusing to produce a number when an input is absent.**

Everything below follows from that. The corollary is the anti-accretion rule: **E5 adds no new meter.**
If a quantity is not measured today, E5 does not invent an instrument for it — it either models it with a
stated factor and an `assumed` provenance, or it **omits the term and says so on the face of the figure**.

### 2.1 The three ledgers, precisely

The taxonomy is SAVED / SPENT / NET (settled by the prior FRAME §0; GHG scopes 1/2/3 are an *orthogonal
boundary label inside SPENT*, not a third ledger). Restating each with **denomination**, **measurement
basis**, and **source** — the three things a basis-less carbon number is missing:

| | **SAVED** (customer) | **SPENT** (operational) | **NET** |
|---|---|---|---|
| **Denomination** | tCO₂e, non-negative magnitude, `ledger=saved` | tCO₂e, non-negative magnitude, `ledger=spent` | tCO₂e, **signed**, derived |
| **Grain** | per household, per intervention, per period | per activity class, per period | portfolio, per period |
| **Measurement basis** | **MODELLED** counterfactual × **published** intensity factor | **MEASURED** activity × **ASSUMED/published** emissions factor | derived; inherits the worse of the two |
| **Source (today)** | `docs/market_data/consumption_feed.json` (half-hourly per-customer kWh) + intensity factor | `site/data/activity_cost.json` (seconds + tokens) + intensity/energy factors | `carbon_ledger.py::net()` |
| **Exists today?** | inputs YES, baseline model **NO** | inputs PARTIAL (time+tokens yes, **kWh no**) | mechanism YES, feeds NO |
| **Honest provenance tag** | `estimated_from_data` | `estimated_from_data` (time), `assumed` (energy-per-token, kWh) | mixed — must be surfaced, see §2.3 |

**The decomposition of SPENT, term by term, with what each really is:**

| Term | Activity source | Factor | MEASURED / MODELLED / ASSUMED |
|---|---|---|---|
| Compute electricity | *(none — no kWh meter, §1.4)* | grid intensity, `_GRID_AVERAGE_INTENSITY` | **ASSUMED end-to-end.** Would be `utilisation × TDP × hours`, all three modelled. Hardware is known (i5-13400F + RTX 3060, CLAUDE.md) so a nameplate-TDP model is *defensible*, but it is a model, not a meter. |
| Frontier tokens | `activity_cost.json::token_attribution.total_tokens` | energy-per-token × grid intensity | activity **MEASURED but incomplete** (7/25 sessions parse); factor **ASSUMED** (published estimates span an order of magnitude) |
| Local model (Ollama/qwen3) | *(not attributed anywhere today)* | GPU-hours × TDP × intensity | **UNMEASURED — a named omission.** Local inference is deliberately the volume path (CLAUDE.md model routing), so omitting it **understates SPENT**, which **flatters NET**. Must be declared, not silently dropped. |
| People | headcount = 1 (director), own record | DESNZ per-FTE | **ASSUMED**; small relative to compute `[inferred]` — candidate to scope out **with a stated boundary**, never silently |

### 2.2 The per-household cost-and-carbon trajectory, from observables only (director item 1)

This is the SAVED side's missing input and the sharper of the two widened items, because it is where the
epistemic wall bites.

**What it must be:** for each household, a **projected path** of (cost £, carbon tCO₂e) over a forward
horizon, under (i) the status quo and (ii) each intervention the company could offer. `SAVED` is the
delta between the two paths, realised against actuals as they arrive.

**Derived from observables ONLY — the permitted input set:**

| Input | Observable? | Source |
|---|---|---|
| Household's own half-hourly kWh history | **YES** — it is the company's own meter read | `docs/market_data/consumption_feed.json` shape (`customer_id/date/period/kwh`) |
| Household's tariff, standing charge, unit rate | **YES** — the company's own contract | company billing |
| Published grid carbon intensity by half-hour / by year | **YES** — published in reality (regulation-commons) | NESO/DESNZ; `_GRID_AVERAGE_INTENSITY` today (annual) |
| Weather / temperature | **YES** — published | Open-Meteo; C13's HDD/CDD normalisation is the existing precedent |
| EPC band, census-derived priors | **YES** — public data a real supplier can obtain | the D-segment wall ruling permits exactly these |
| The intervention record (what we offered, when, whether accepted) | **YES** — the company's own contact log | company CRM |
| Household's true propensity / green stance / segment label | **NO — WALL** | SIM-internal. `.claude/rules` D-segment ruling: *"No segment label, attitude, or sensitivity ever crosses the wall directly."* **Do not invent a proxy for `green_stance`.** |
| The SIM's ground-truth counterfactual (CRN A/B) | **NO — WALL** | harness-side truth only; §2.6 |

**The construction (three named layers, each with its own honesty tag):**

1. **Observed layer** — the household's realised half-hourly kWh. `MEASURED`. Point-in-time bounded
   (`company/interfaces/point_in_time_view.py`); a trajectory must never read beyond `as_of`.
2. **Normalisation layer** — weather-normalise the history to separate *behaviour* from *weather*.
   `MODELLED`. **Reuse C13's HDD/CDD normalisation** (built observables-only, epistemic PASS) rather
   than authoring a second normaliser — and inherit its **measured failure mode**: the coupled-triad gap
   found C13 is *harmful in summer* (worst cell 1.040). A summer-shifted carbon claim therefore rests on
   a normaliser known to be wrong in summer, and must carry that caveat.
3. **Projection layer** — extend the normalised path forward under status quo vs intervention.
   `MODELLED`, and this is where **all** the attribution risk lives (§2.5).

**The counterfactual, honestly (the attribution problem — director item 1's hard core).**
"Customer carbon SAVED" means: *the CO₂e this household would have emitted, but did not, **because of**
something we did.* Three candidate baselines:

| Baseline | What "would have happened" means | Defensible? |
|---|---|---|
| **B — own pre-intervention trajectory** (weather-normalised) | this household, continuing its own observed path | **The company's only wall-legal option.** It is what a real supplier's carbon desk actually does. **Named simplification (R10):** it attributes to the intervention *everything* that changed — including autonomous behaviour change, price response, appliance replacement, and mean reversion. It is an **upper bound on attribution**, and the bias direction is **toward over-claiming**. |
| **C — matched control** (similar households not offered) | a peer group's path | Wall-legal in principle (uses only observables) and **strictly better on attribution** than B, because it differences out common shocks (weather, price, season). Requires enough population to match on — currently N≈19 active customers `[observed-with-evidence: site/shadow]`, so **not viable at current scale**; becomes viable as population grows. **Register as the intended upgrade path, not as today's method.** |
| **A — same-household CRN A/B** | the SIM re-run, contacted vs not | **NOT a company observable — WALL.** It is the *harness's* truth, used to score the company's belief (§2.6). A company reading method-A output into its own SAVED ledger has read SIM ground truth. |

**Design decision: B is the company's belief; C is the registered upgrade; A is the harness's truth and
never enters `company/carbon`.** The baseline is defensible *as a named, bias-declared simplification* —
not as a correct measurement. It must be published as such (§2.3), and the direction of its bias
(over-claiming) must be stated on the face of the figure, because it is the direction that flatters.

**Which counterfactual defines the published headline, and whether behaviour-persistence decays, remain
director values-calls** (unchanged — carbon is the mission, category 6).

### 2.3 The clock: R14 for carbon (director item 2)

**R14 for money:** every published financial figure carries its clock — settled / billed / banked.
**The analogue for carbon is not one field but three,** because carbon has three independent axes on
which a number can be silently wrong:

| Axis | Carbon values | What it answers | Money analogue |
|---|---|---|---|
| **CLOCK** — how settled is the underlying activity? | `metered` (actual reads / actual token counts in) · `estimated` (period open, read estimated) · `reconciled` (settlement-final, factor final) | *Will this number move?* | settled / billed / banked |
| **BASIS** — which factor convention? | `grid_average` · `grid_marginal` · `activity_based`; plus the **scope boundary** (which of 1/2/3) and the **factor vintage** (`effective_from`/`effective_to`) | *Against what was it converted?* | the accounting basis |
| **PROVENANCE** — how do we know? | `estimated_from_data` · `assumed` · `asserted` (the enum already in `carbon_ledger.py:55`) | *Measured, modelled, or assumed?* | — (carbon-specific; money is mostly measured, carbon mostly is not) |

**A basis-less carbon number is a defect, exactly as a clock-less financial figure is.** Concretely:
"we saved 4.2 tonnes" without its triple is unfalsifiable — 4.2 tonnes against *which* baseline, at
*which* grid intensity, of *which* vintage, counting *which* scopes, from *measured* or *assumed*
activity? Every one of those choices can move the number by a factor of two or more, and every one of
them can move it in the flattering direction. **The number without its triple is not a weak claim; it is
not a claim at all** — which is the same argument the atom already makes for reporting NET alongside
SAVED.

**Mechanisation — three concrete, small steps, in dependency order:**

1. **Make the basis survive aggregation.** `three_ledger_view()` (`carbon_ledger.py:164–166`) must
   return, alongside each magnitude, the **basis set** of the events that composed it (the distinct
   `basis` values), the **provenance mix** (share of tCO₂e by provenance kind), the **as_of window**
   (min/max), and an explicit **`omitted_terms`** list naming what is *not* counted (local-model
   inference, scope-3, people — §2.1). A view that returns a bare float is the defect.
2. **Extend the publish gate.** Add the carbon headline keys to
   `_BASIS_REQUIRED_PORTFOLIO_KEYS` (`tools/generate_dashboard_data.py:1691`) so
   `_check_basis_labels_present` (line 1694) fails the publish gate on a basis-less carbon figure —
   reusing the existing R14 mechanism rather than building a parallel one. **This is the whole R14
   mechanisation: one tuple entry and the view change above.**
3. **The plain-language working, rendered next to the figure.** Not a footnote — the *derivation*, in
   sentences a non-specialist can check:

   > "Over 2016–2025 we estimate we helped customers avoid **X tonnes** of CO₂e. That is our own
   > estimate, not a measurement: we compared each household's actual metered use against what its own
   > weather-normalised history said it would have used — so anything else that changed their usage is
   > credited to us too, and the number is more likely too high than too low. We converted kWh to CO₂e
   > using the published UK grid **average** intensity for each year (350 g/kWh in 2016 falling to
   > 165 g/kWh in 2025). Running the company cost **Y tonnes** — that counts our frontier-model tokens
   > and our machine's electricity; it does **not** yet count local-model inference, so Y is
   > understated. Net: **X − Y tonnes**. At £Z of cost to serve and persuade, that is **£Z/(X−Y) per
   > tonne**. The UK government's own appraisal value is £273/tCO₂e (2025) — we show it so you can
   > judge our number, not because we are trying to hit it."

   Every sentence names its basis, and **each of the two honest admissions points the wrong way for us**
   (SAVED likely over-claimed, SPENT understated). That is the test of whether the working is honest:
   *if the plain-language version contains no statement against interest, it is marketing.*

4. **The disclaimer comes off last.** `site/test_home_door.py:75` asserts "designed, not yet
   instrumented". It is removed **only** when the LIVE rendered figure is fetched and asserted (**R11**),
   and the same commit must replace that assertion with one on the rendered value *and its basis triple*
   — never delete a gate without its successor (no orphan transition).

### 2.4 The derived metric — £/tCO₂e, input by input

```
£ per tonne CO₂e  =  (cost to serve  +  cost to persuade, incl. compute)  /  carbon abated
```

| Input | Exists today? | Where / what is missing |
|---|---|---|
| **cost to serve** (£) | **YES** | `run_output_latest.json::per_customer_lifetime.<id>.cost_to_serve_gbp` — per-customer, real (C1 £274.94 … C_IC1 £4,218.12) |
| **cost to persuade** (£), marketing/contact | **PARTIAL** | acquisition/retention costs exist in the CAC/CLV layer; **no per-intervention "cost to persuade" line item** is aggregated today `[inferred]` |
| **cost to persuade — compute** (£) | **NO** | requires £ per token and £ per compute-hour. Token *counts* exist (7/25 sessions); the **£ conversion does not exist anywhere** |
| **carbon abated** (tCO₂e) = NET | **NO** | needs both feeds: SAVED (needs the trajectory, §2.2) and SPENT (needs the factor values-call + a compute-energy model) |
| **the £273/tCO₂e comparator** | **YES, on the site** | `site/test_home_door.py:73` — already rendered as a **yardstick**, correctly framed |

**Inputs that do not exist yet, ranked by what unblocks them:** (1) *carbon abated* — the largest, gated
on a director values-call **and** the trajectory build; (2) *compute £* — small, but needs a per-token
and per-kWh price, which touches real-money figures; (3) *cost to persuade* — an aggregation over
existing data, the cheapest of the three. **Three of the five inputs do not exist. A £/tCO₂e figure is
therefore not near-term, and any interim publication must say so** (which the site already does, §1.7).

### 2.5 Why this structurally cannot be goal-sought (R12)

R12 says the metric is a diagnostic, never a target. `CARBON_NOT_A_TARGET_CONSTRAINT.md` already forbids
it entering the fitness function, any reward/selection/ranking path, or being tuned toward the £273
benchmark. **That is policy. The question this FRAME must answer is what makes it *mechanically*
un-tunable** — because per MAKE_IT_STICK, prose-only rules evaporate.

**Four structural properties. Each is a property of the construction, not a rule someone must obey:**

**(a) The import wall — already built, must be EXTENDED as a class (R10).**
`tests/company/test_carbon_not_a_target.py` is an **AST** grep-guard: no decision surface (fitness
register, atom draw, risk committee, pricing/personalisation reward path) may `import company.carbon`.
Mutation-proven both directions at rung 1. **A metric a decision surface cannot import is a metric it
cannot optimise** — this is the strongest of the four because it is a *reachability* property, not a
behavioural one. **Class obligation:** every new decision surface must be added to the forbidden-importer
set, or the class silently reopens.

**(b) Separation of the numerator's owner from the denominator's owner.** The £ numerator comes from
the billing/cost-to-serve chain (`run_output_latest.json`), the tCO₂e denominator from the carbon event
stream, and the emissions **factors** from a register whose values are **director-authored** (§4). **No
single component can move the ratio**, and the one component that would move it most — the factor set —
is not the agent's to write. This is the same architecture as R13's baseline/curriculum split, and for
the same reason: *the agent sits on both sides of the wall, so the definitional half must face the
director.*

**(c) Fail-loud instead of fail-soft, everywhere a tune would hide.** `cost_per_tonne_abated` **raises**
on `net <= 0` (`carbon_ledger.py:148–152`) rather than returning 0 or ∞. `CarbonEventMalformed` rejects
a missing `basis` or an out-of-enum `provenance` at construction. **The directions a goal-seeker would
push are exactly the directions that raise**: suppress SPENT → NET rises → but the omission shows in
`omitted_terms` and the provenance mix; drop a feed → events vanish → §5's non-empty control fires;
inflate SAVED → the basis set and the over-claiming caveat travel with it to the page.

**(d) Adversarial reporting — NET is mandatory and the caveats point against us.** `net()` is
always reported, including negative. The plain-language working (§2.3) is required to contain the two
statements against interest. **A metric whose published form is obliged to disclose the ways it is
flattering is one whose flattery is self-defeating.**

**How would anyone NOTICE if it were being tuned? — the detection design (this is the part usually left
out).** Four independent signals, none of which the tuner controls:

1. **The factor register is director-authored and versioned.** A change to a factor is a *diff in a
   file the agent does not own*. Silent parameter drift — R13's named failure — is therefore visible as
   a commit, in the one place it would have to happen.
2. **Provenance mix is published and trendable.** If the `assumed` share of tCO₂e falls while accuracy
   claims rise, or if `omitted_terms` shortens without a corresponding build landing, something moved
   that should not have. A tuner must either lie in the provenance mix (a second, detectable act) or
   leave a trail.
3. **The £273/tCO₂e external anchor is *external*.** It is not derived from anything the company
   computes, so it cannot be co-moved. Convergence toward it over time — with no mechanism change
   explaining the convergence — is itself the alarm. Per R12, that triggers **R4 (diagnose the
   mechanism)**, never a tune.
4. **The coupled-triad gap (§2.6) is the real detector.** A company that tunes its SAVED belief upward
   moves *away* from the harness's CRN truth, so the **gap widens**. This is the one signal that is
   genuinely independent of the company's own accounting — the belief is scored against a truth the
   company cannot see or influence. **This is why the triad coupling is the L3 gate and not optional
   polish.**

**The honest residual:** properties (a)–(d) prevent *automated* goal-seeking and make *deliberate*
goal-seeking leave evidence. They cannot prevent a human choosing a flattering factor set — which is
precisely why the factor set is a director values-call rather than an agent decision. The mechanism
does not remove the values judgement; it **relocates it to the only party who can legitimately make it,
and makes the choice visible.**

### 2.6 The coupled-triad shape (unchanged, restated for completeness)

SIM adds the world (true per-household carbon under CRN) → COMPANY forms a belief through the wall
(method B, allowed to be wrong) → HARNESS measures the gap. Belief `b` = company SAVED; truth `θ` = the
SIM's method-A CRN counterfactual; `g0` = a no-skill baseline (zero abatement, or a naive flat-factor
guess). **No world twin exists and none is registered here** (§1.8) — registering a coupling is a
BUILD/director act. **Per COUPLED_TRIAD doctrine E5 cannot reach L3 until it has faced that world and the
gap is measured.**

---

## 3. R15 — the named defects and the mutations that must go RED (for whenever BUILD opens)

Every control names **the defect it fires on** and **the concrete mutation that must turn it red**. The
FAIL-OPEN family is listed first because §1.4 proved it is the live risk here, not a hypothetical.

### FAIL-OPEN controls (a zero-emissions reading because a feed is absent — the classic shape)

| # | Named defect | Control | **Mutation that must go RED** |
|---|---|---|---|
| **C1** | **The absent-feed zero.** The SPENT source is unavailable/empty/unparsable → zero SPENT events → `spent()==0.0` → `net()==saved()` → £/tCO₂e reads its **best possible value because the feed is missing**. (Exactly §1.4's `RESOURCE_AWARE_SCHEDULING` scenario.) | A SPENT ledger with **zero events** must NOT read as "zero emissions". `spent()` must be distinguishable from *unknown*: `three_ledger_view()` returns a **status** (`ok` / `no_source` / `insufficient_data`), and any £/tCO₂e computed on a non-`ok` SPENT **raises**. | Point the SPENT emitter at a **missing file**, an **empty list**, and a **malformed record**. Each must produce a non-`ok` status and a raise — **not** `0.0`. Then **delete the status check** and prove the test fails. |
| **C2** | **Partial-feed silent understatement.** The feed exists but covers a minority — G11 parses **7 of 25** token sessions (§1.2). A total computed over 7/25 reads as *the* total. | The SPENT view must carry **coverage** (`n_parsed`/`n_entries`, `unattributed_*`) and must **refuse to publish** a headline below a declared coverage floor, rather than publishing a small number confidently. | Feed a fixture with 1 of 100 entries parsed. The view must report low coverage and block the headline. Mutation: **remove the coverage floor** → the test must fail. |
| **C3** | **The omitted term.** Local-model inference is unmeasured (§2.1). Omitting it understates SPENT and flatters NET. | `omitted_terms` is **non-empty-by-default** and travels with the figure to the page; a published figure with an empty `omitted_terms` must be proven exhaustive, not assumed. | Remove a known term from `omitted_terms` without adding its measurement → a control asserting every SPENT term is either *measured* or *declared-omitted* must go RED. |
| **C4** | **The basis-less publish.** A carbon figure reaches the dashboard without clock/basis/provenance — passing the R14 gate **by never being checked** (§1.6). | Add the carbon keys to `_BASIS_REQUIRED_PORTFOLIO_KEYS` (`generate_dashboard_data.py:1691`); `_check_basis_labels_present` fails the publish gate. | Publish a carbon headline with `basis` omitted → the gate must fail the build. Mutation: **remove the carbon key from the tuple** → the test that proves the gate fires must itself go RED. |
| **C5** | **Non-finite laundering — EXECUTED AND CONFIRMED LIVE THIS TURN, not hypothetical.** `CarbonEvent.__post_init__` guards `not isinstance(tco2e,(int,float)) or tco2e < 0` (`carbon_ledger.py:89`), but `NaN < 0` is `False` and `NaN` *is* a float, so **`NaN` and `inf` are both accepted**. `NaN` then propagates through `_sum()` → `net()` returns `nan` → **`net <= 0` is `False`, so the fail-loud guard at line 148 is BYPASSED** → `cost_per_tonne_abated` **returns `nan` instead of raising**. A `nan` rendered to a page is the exact "reads as free/great" failure the constraint doc forbids, reached through the project's own registered `comparison_guards_are_nan_blind` class. `[observed-with-evidence: run directly against the shipped module this turn — NaN accepted, net()=nan, net<=0 False, cost_per_tonne_abated returned nan; inf likewise accepted]` | Reject non-finite **first**, before any comparison, in `CarbonEvent.__post_init__` **and** in `cost_per_tonne_abated` (both the ledger's own value and the incoming `cost_gbp`). | Construct `CarbonEvent(tco2e=float("nan"))` and `float("inf")` → both must raise `CarbonEventMalformed`; a ledger containing one must make `cost_per_tonne_abated` **raise**, never return `nan`. Mutation: **remove the `isfinite` check** → all three tests go RED. **This is a live defect in shipped code today, is factor-agnostic and values-call-free, and is therefore the single cheapest genuinely-unblocked increment (§5).** |

### TAUTOLOGY controls (the checked value must not derive from the source it checks)

| # | Named defect | Control | **Mutation that must go RED** |
|---|---|---|---|
| **C6** | SPENT reconciliation reads back the stored `tco2e` and "confirms" it. | Recompute `activity × factor(as_of)` via an **independent** path from the raw activity source and the register; never read the stored value. | Make the control read `event.tco2e` instead of recomputing → a fixture with a **corrupted stored `tco2e`** must still be caught; if it is not, RED. |
| **C7** | Anachronistic factor — 2025 grid intensity applied to a 2016 event (a real risk: `_GRID_AVERAGE_INTENSITY` spans 350→165, a **2.1× swing**, §1.3). | Assert `effective_from <= as_of < effective_to` for every event's cited factor. A missing/expired factor **fails loud**, never defaults to nearest-or-zero. | Apply the 2025 factor to a 2016 event → RED. Mutation: replace the fail-loud with a nearest-year fallback → the anachronism test must go RED. |

### FAIL-SILENT controls (an unavailable checker is a FAILED checker)

| # | Named defect | Control | **Mutation that must go RED** |
|---|---|---|---|
| **C8** | The `CARBON_NOT_A_TARGET` AST grep-guard cannot resolve a decision-surface file (moved/renamed) and **passes vacuously**. | The guard asserts its **expected surface set is non-empty and every named surface resolves**; an unresolvable surface is a FAILED check, not a skip. | Rename a decision-surface file → the guard must go RED (not silently pass). Mutation: remove the resolve-check → RED. |
| **C9** | The wall breach: a SAVED event sourced from method-A CRN truth (§2.2). | `tools.epistemic_verifier` + a test that no `company/carbon` module imports `simulation.*`/`sim.*` or reads a SIM counterfactual. | Add a synthetic `from simulation... import` to a `company/carbon` module → RED. |

**Plus the three already proven at rung 1** — idempotency (C-S2), arrival-order independence (C-S1),
fail-loud `net <= 0` — which must be re-proven, not assumed, on every new rung.

---

## 4. Unchanged director values-calls (category 6 — carbon is the mission)

Restated, not decided, and **not** widened by this FRAME:

1. **Grid marginal vs average** intensity (affects both SAVED and SPENT).
2. **The scope boundary** (which of GHG scopes 1/2/3 SPENT counts).
3. **Time-of-use resolution** — annual (`_GRID_AVERAGE_INTENSITY` today) vs half-hourly.
4. **Token energy-per-unit source**, or defer the token term to metered-compute-only.
5. **Which counterfactual defines "abated"** (§2.2's B / C / A), and whether behaviour-persistence decays.
6. **Whether carbon ever enters the Epoch-4 fitness function** — explicitly reserved by
   `CARBON_NOT_A_TARGET_CONSTRAINT.md`; a one-way door.

**Newly surfaced by this FRAME, and also the director's:** whether the published SAVED headline uses the
**over-claiming** method-B baseline at all before method C is viable at population scale — i.e. whether a
knowingly-upper-bound abatement figure should be published with its caveat, or withheld until the matched
control exists. That is a values question about what the company is willing to claim, not a technical one.

---

## 5. Disposition

- **DISCOVER: complete for the widened scope.** Existing mechanisms inventoried with file:line; one
  material factual correction made (§1.4).
- **FRAME: complete for the widened scope** — the observables-only trajectory (§2.2) and the carbon
  clock/basis + plain-language working (§2.3), plus the un-goal-seekability design (§2.5) and the R15
  control set (§3).
- **Level: HELD at 0.** Rung 1 is genuinely built and is **L1-quality**, but no
  `LEVEL_UP_PROPOSED`/`LEVEL_UP_TWIN` entry for `E5_carbon_three_ledger` exists in
  `docs/observability/gate_authorizations.jsonl` `[observed-with-evidence: grep returns nothing]`, and
  **R16** makes the ledger the sole authority — the agent never self-bumps. **L1 is PROPOSED**, pending
  ratification. Analysis alone certainly does not reach L2 (the L2 bar is *mechanically real AND
  mutation-tested*). This follows the `H29_import_time_env_capture_test_isolation` precedent: every
  DISCOVER/FRAME entry there closes with "level_current unchanged (R16 — no self-bump)" while closing
  saturation via the marker.
- **Remaining path: BUILD only**, gated on the §4 values-calls, the trajectory build, and the
  coupled-triad twin. **No honest FRAME output remains** — hence `frame_saturated: true`, which
  auto-clears when `loop_stage` flips off `idle` and the atom re-enters via the BUILD draw.
- **The cheapest genuinely-unblocked increment**, if BUILD opens with no values-call: **C5** (reject
  non-finite `tco2e`) — a live fail-open in shipped code, factor-agnostic, values-call-free.

---

*Sources read directly this turn: `company/carbon/carbon_ledger.py`,
`company/sustainability/carbon_intensity_register.py`, `company/regulatory/fuel_mix_disclosure.py`,
`tools/activity_cost.py`, `site/data/activity_cost.json`, `tools/generate_dashboard_data.py`,
`background/coupled_triad.py`, `background/ntfy_responder.py`, `background/gate_authorization.py`,
`background/supervisor.py`, `sim/generation_demand_history.py`, `docs/market_data/consumption_feed.json`,
`docs/reports/run_output_latest.json`, `site/test_home_door.py`, `site/assets/model-on-a-page.svg`,
`docs/design/CARBON_NOT_A_TARGET_CONSTRAINT.md`, `docs/design/frame/E5_carbon_three_ledger_FRAME.md`,
`docs/design/maturity_map.yaml`. Prior-stage docs cited, not re-derived:
`CARBON_THREE_LEDGER_DISCOVER.md`, `E5_EMISSIONS_FACTOR_REGISTER_DISCOVER.md`.*
