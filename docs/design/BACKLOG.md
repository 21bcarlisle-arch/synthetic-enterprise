# THE BACKLOG — agent-owned, ordered, with definitions of done

**Status:** LIVING. **Authored:** 2026-07-29 by the worker tick.
**Provenance / authority:** `THE_STANDARD.md` §7.3 ("turn each Timeframe-2 item into real work
with a definition of done") + the **YOU OWN THE BACKLOG** amendment ("propose your own backlog
and your own ordering… publish it… notify once, then begin — no approval step; silence is
agreement"). Source material: `THE_MODEL_ON_A_PAGE.md` Timeframe-2, plus the gap/simplification
registers the standard names as "the backlog's raw material."

**Why this file exists (plain):** the loop kept running out of *real* work and falling back to
re-verifying already-finished atoms (HARDEN rest-churn). `THE_STANDARD.md` §6 forbids that as
day-filler. Timeframe-2 is "months of work" that "has never been work" because it was prose, not
a backlog. This turns it into work. When this is stocked and wired, `_rule0_harden_draw` gets
demoted below it and then mothballed (`MOTHBALL_2026-07-29.md` row 2).

**How an item graduates from this list into the loop:** each item below is a *candidate atom*
(`provenance: proposal`). Authoring candidates + DISCOVER/FRAME on them is allowed autonomously
now (CLAUDE.md "Epoch gating gates BUILD, never thought"). Wiring the top items into
`maturity_map.yaml` as real atoms is the follow-on to this doc — done a few at a time, not in one
wide-blast pass (the map is a shared, gate-guarded surface).

**Reading rule (inherits `THE_MODEL_ON_A_PAGE.md`):** everything here is **Timeframe-2 = not yet
true.** Stating any of it as present tense on the public site is a claim-status defect. "Definition
of done" is the exit test, never a target to tune toward (R12).

---

## Ordering — and why (the reasoning is part of showing the working, §4)

Ordering principle, in priority order:
1. **Compounding first** (`COMPOUNDING_WORK_FIRST.md`): work that shortens the feedback loop or
   is the substrate many other items sit on comes before linear work.
2. **The mission must become measurable** (`THE_MODEL_ON_A_PAGE.md` score = Survive/Earn/**Abate**):
   carbon is the headline the company is *for*, and today it is designed-not-instrumented. Making
   the score real unlocks judging everything else.
3. **Coupled-triad law** (CLAUDE.md): no world/SIM deepening reaches L3 until the company has been
   tested against it and the belief-vs-truth gap measured. World items therefore pull their
   company counterpart with them, not ahead of them.
4. **Product-first** (`PRODUCT_FIRST` ruling) + §4: prefer items that produce a *visible, explained*
   capability on the site over pure internal machinery.

Resulting wave order (rationale per item below):

**Wave A (substrate + mission-measurable):** B1 scenario spine · B9 carbon instrumented (E5).
**Wave B (the crisis the world exists to pose, coupled):** B2 gas storage inversion + B6 collateral→cash death loop (one coupled pair) · B3 forecast-error layer.
**Wave C (market realism so pricing has an opponent):** B4 traded product ladder + B5 shaped-cost benchmark · B10 competitors.
**Wave D (customer depth, discovered not tagged):** B7 the state layer · B8 continuous engagement + discovered price-sensitivity + holdout uplift.
**Wave E (endgame):** B11 the evolutionary tournament — depends on A–D existing to be worth running.

---

## The items

### B1 — Scenario spine (World; **Wave A, compounding substrate**)
**Plain:** the company should live through *named, director-authored* worlds (NESO-central,
crisis-replay, glut), sampled tail-heavy with each world's true probability tagged, not just the
single real 2016–25 record.
**Why here:** it is the substrate the forecast layer, the death loop and the endgame tournament all
rerun over. Highest compounding return; build it first. Extends `sim/scenario/` (FRAME already done —
see [[project_scenario_spine_frame]], wall = import-direction).
**Definition of done:** ≥3 named scenario worlds selectable by a committed, director-facing config
(R13 curriculum: named + versioned, never silent drift); each carries a true-probability tag; a run
can be launched against any of them and the manifest records which; a test asserts scenario choice
changes the world the company sees without touching baseline ground truth.
**Wiring status (2026-07-29):** REGISTERED into `maturity_map.yaml` as `SPINE_1_scenario_world_state`
(`provenance: proposal`, `loop_stage: idle`, `level_current: 0`, `blocked_on: director_build_open`) —
the world-selection MECHANISM half of B1. The named-world VALUES half is the FRAME's `SPINE_2_launch_worlds`
(director-ratified R13 curriculum), still named-not-registered per FRAME section C, as are SPINE_3–SPINE_5.

**MECHANISM BUILT (2026-07-29, on the director's "start the hardest item, not a frame" warning
`DIRECTOR_WARNING_QUIET_BUSYWORK_2026-07-29.md`, which overrides the `director_build_open` gate — "no
one-way doors"):** `sim/scenario/spine.py` — the immutable, version-pinned `ScenarioSpine` value object +
curriculum registry (`sim/scenario/curriculum/*.yaml`) + Blindfold-clean `paths_as_of(t)` accessor + the
R13 ratification gate. The `history_replay` default selects NO overrides (byte-identical/dormant, FRAME
§A.5). The three FRAME-proposed worlds (`neso_central`, `crisis_2021_22`, `supply_glut`) are committed as
`ratified: false, in_rotation: false` PROPOSAL artefacts — the mechanism sees them, but none can enter
rotation until the director ratifies (R13 wall held; `rotation_set()` is empty today). 15 exit tests green
(`tests/sim/test_scenario_spine.py`), incl. the FRAME §R15 failable controls: **W1** the epistemic wall
(no `company/**`/`saas/**` import — mutation-proven both ways), **W2** baseline dormancy, **W3** the
fail-closed ratification guard (`ratified:true` without a record is REJECTED). **Level stays a proposal
(`level_current: 0`) — I built it, I do not self-promote it (levels are proposals; the director moves them).**
**Still open (honest):** SPINE_1 is not yet WIRED INTO price formation / the runner (the integration that
makes a chosen world change what the company sees — the next real increment); the launch-world VALUES await
director R13 ratification (`SPINE_2`); a site page showing this working is a follow-on (claim-status: the
spine is Timeframe-2 machinery, dormant, NOT a present-tense capability).

### B2 — Gas storage stock-and-flow that can *produce* a 2022 inversion (World; Wave B, coupled w/ B6)
**Plain:** model gas storage as a stock that fills and draws, so a supply shock endogenously
produces the winter-2022 price inversion rather than it being scripted.
**Definition of done:** a storage state variable drives wholesale gas such that a defined shock
scenario reproduces an inversion of the observed 2021–22 shape within a stated tolerance, verified
blind to company P&L (R13); registered as a scenario in B1's spine.
**Wiring status (2026-07-29):** REGISTERED into `maturity_map.yaml` as `SPINE_3_gas_storage_crisis_regime`
(`provenance: proposal`, `loop_stage: idle`, `level_current: 0`, `depends_on: [SPINE_1_scenario_world_state]`,
`blocked_on: director_build_open`) — the world half of the Wave-B coupled pair. Shock magnitude + target
inversion shape are R13 director curriculum, not agent-set.

### B3 — Forecast layer at multiple horizons, error shrinking to delivery (World→Company, Wave B)
**Plain:** the company should receive *published forecasts with realistic error* at several horizons,
the error narrowing as delivery approaches (the wall on the future, per MOAP).
**Definition of done:** a typed inbound forecast feed exposes ≥2 horizons; forecast error is
non-zero and monotonically shrinks toward delivery by a calibrated schedule; the company's naive
120-day belief is measured against it and the gap is reported per the coupled triad.

### B6 — Collateral → cash death loop (Company; Wave B, coupled w/ B2)
**Plain:** a 2021–22 replay must be able to kill the company *by collateral* — margin calls draining
cash faster than the P&L looks bad — with the P&L surviving on paper as it dies on cash.
**Why coupled to B2:** the death loop needs a world that can defeat it (B2's inversion); neither
reaches L3 without the other (coupled-triad law).
**Definition of done:** a hedge book posts variation margin against a moving forward; a defined
crisis scenario produces a cash-exhaustion mortality event while accounting P&L stays positive;
the mortality is recorded by the survival score; a test proves it can both kill and be survived.
**Wiring status (2026-07-29):** REGISTERED into `maturity_map.yaml` as `B6_collateral_cash_death_loop`
(`provenance: proposal`, `loop_stage: idle`, `level_current: 0`, `depends_on: [SPINE_3_gas_storage_crisis_regime]`,
`blocked_on: director_build_open`) — the company half of the Wave-B coupled pair (coupled-triad: neither
it nor SPINE_3 reaches L3 without the other).

### B4 — Traded product ladder with moving contango/backwardation (Market; Wave C)
**Plain:** seasons/quarters/months/day-ahead as real tradable products with a moving term structure,
not one synthetic curve.
**Definition of done:** ≥4 tenor buckets priced with a term structure that can invert
(contango↔backwardation) across scenarios; the company can hedge in named products; a test asserts
the ladder moves independently of spot.

### B5 — Shaped annual cost as the benchmark + trading value-add ledger (Market; Wave C, w/ B4)
**Plain:** the honest benchmark for "did trading add value?" is the shaped annual cost of the book;
the trading value-add must be reported *net of day-one friction*.
**Definition of done:** shaped-cost benchmark computed per run; a value-add ledger reports
trading P&L net of modelled friction against it; friction is non-zero and sourced; reported as a
diagnostic, never a target (R12).

### B7 — The customer state layer (Customers; Wave D)
**Plain:** customers change: house moves (credit exit + two deemed entries), births/deaths/divorce,
income shocks — driving switching, arrears and consumption.
**Definition of done:** a state-transition layer emits these as first-class events on named RNG
substreams (C-S2 discipline); each has a downstream effect the company observes only through
behaviour (never a tagged trait); replay is deterministic; a test asserts a move produces the
credit-exit + two deemed-entry pattern.

### B8 — Continuous engagement + discovered price-sensitivity + holdout uplift (Customers; Wave D)
**Plain:** replace the three engagement bins with a continuum; let price-sensitivity and attitudes be
*discovered through conversations and offers*, never tagged; prove "this segment justifies its
treatment" with a holdout, not an assertion.
**Definition of done:** engagement is continuous; the company estimates price-sensitivity from
observed responses only (epistemic wall held); a holdout group exists and measured uplift is
reported so a treatment claim is proven, not asserted; misclassification cost is modelled.

### B9 — Carbon instrumented — E5, £/tCO₂e on the front page (Carbon; **Wave A, mission-measurable**)
**Plain:** NESO grid intensity × every half-hourly meter read → per-customer CO₂e trajectories →
**£ per tonne saved** as the headline the company is judged on.
**Why so early:** it is the mission (`THE_MODEL_ON_A_PAGE.md` score = Abate) and today it is
designed-not-instrumented — the site says so plainly. Until it is real, the fitness function it
feeds cannot judge anything. High compounding + §4 (the primary visible output).
**Definition of done:** intensity × HH read wired into the existing SAVED/SPENT/NET ledger;
per-customer tCO₂e trajectories produced from observables; a £/tCO₂e figure derived and shown on the
site with its clock/basis (R14) and a plain-language explanation of the working (§4); the "not yet
instrumented" disclaimer removed only when the live rendered figure is asserted (R11).
**Reconciliation (2026-07-29): B9 IS the existing map atom `E5_carbon_three_ledger`, NOT a new atom.**
E5 already exists (`provenance: proposal`, `loop_stage: idle`, rung-1 DATA MODEL + CARBON_NOT_A_TARGET
grep-guard BUILT, `level_current: 0`). B9's definition of done above is precisely E5's remaining
L1→L3 work: the live SAVED feed (per-household cost-and-carbon trajectory, unbuilt), NESO intensity ×
HH read wiring, and the on-site £/tCO₂e figure. E5 is BUILD-blocked on two director VALUES-calls
(emissions-factor set + counterfactual method, carbon = the mission = cat-6) plus the trajectory build —
so "carbon instrumented" advances by unblocking E5, NOT by authoring a duplicate. B9 here is the
site-facing framing of that same work; do not register a second atom.

### B10 — Competitors (Market; Wave C)
**Plain:** other suppliers, so the company's pricing meets opposition instead of pricing into a void.
**Definition of done:** ≥1 competitor prices tariffs the population can switch to; switching responds
to relative price; the company's win/loss is observable only through acquisition/churn (wall held);
a test asserts a competitor price change moves the book.

### B11 — The evolutionary tournament (Endgame; Wave E)
**Plain:** rerun the whole company across the scenario worlds to death or endpoint — EV is fitness,
mortality is selection.
**Why last:** it is only worth running once A–D give it worlds to die in and organs to select on.
**Definition of done:** a harness reruns a company configuration across B1's scenario set, scores each
on Survive/Earn/Abate, and ranks; mortality removes configurations; results published as a finding.

### Carry-overs already registered (not re-authored here, tracked in their own docs)
- **Spike-tail 10× gap** — declared simplification, see [[project_parked_campaign_blindspot_and_spike_tail]] (SPIKE_TAIL closed) / spine.
- **Retail gas actively hedged** — folds into B4/B6 plumbing; gas-wholesale page shipped (k-pilot).
- **Cost-to-serve & opex, VAT/CCL tax cycle, cannot-pay/will-not-pay collections** — company-deepen
  items; queue behind B6 (same treasury lane) as B6a/B6b when B6 lands.

---

## WIRED INTO THE MAP — all eleven, 2026-07-29 (director instruction, verbatim)

> "Your backlog is in a document but the thing that picks your next job reads the map. That's why you
> keep saying there's no work. Put all eleven backlog items into the map as real unfinished work items
> now, so you can never again say 'nothing below target' while your own list has months on it."
> — `docs/staging/from_rich_20260729_173731.md`

**He was right, and here is the measurement, not the assurance.** Before this pass, the picker's
DISCOVER/FRAME pool (`supervisor._idle_discover_frame_draw`) was **empty**: 31 idle atoms with a real
level gap → 6 externally blocked, 29 FRAME-saturated, **0 drawable**. The backlog contributed
**nothing**, for three separate reasons, all of them the same shape (real work wearing a status that
hides it):

1. **`blocked_on` hides an atom from EVERY lane, not just BUILD.** B1/B2/B6 were registered earlier
   the same day with `blocked_on: director_build_open`, intending only to hold BUILD.
   `supervisor._is_externally_blocked` drops a blocked atom from the idle DISCOVER/FRAME draw too — so
   "BUILD is director-gated" silently became "this atom does not exist". **CLEARED** on all three; the
   BUILD wall is now held by the *correct* mechanism (`loop_stage: idle` + the `fronts.yaml`
   `stage_advance` gate: idle→build is a director console act), which gates BUILD *without* gating
   thought, exactly as CLAUDE.md's "Epoch gating gates BUILD, never thought" intends.
2. **A sibling's FRAME doc silently saturates a brand-new atom.** `_atom_has_frame_doc` marks an atom
   FRAME-saturated on *any* `evidence` entry under `docs/design/` with `FRAME` in its filename, and H23
   then **hard-skips** it. Citing `SCENARIO_SPINE_AND_TRADING_FRICTION_FRAME.md` /
   `COMPETITOR_FIELD_FRAME.md` / `A5_TOURNAMENT_FITNESS_MORTALITY_FRAME.md` as background on six atoms
   therefore made six *unframed* atoms read as fully framed and vanish from the draw. Fail-**silent**:
   nothing errored, the atoms just weren't there. The mechanism's own docstring names the assumption
   that broke — *"every non-canonical `*_FRAME.md` is owned by exactly ONE atom"*. Fixed by keeping
   those references in prose and out of `evidence`. **Standing rule: `evidence` lists THIS atom's own
   artefacts; a sibling's FRAME doc goes in the prose.**
3. **B9 was in the map and still invisible** — `E5_carbon_three_ledger` carried
   `frame_saturated: true`, honest for the scope framed on 2026-07-20 but not for the scope B9 widened
   it to. Re-opened with the two genuinely-unframed parts named (trajectory-from-observables; the
   site £/tCO₂e figure's clock/basis).

**Result, measured after the change — 11/11 registered, 10/11 drawable:**

| # | Map atom | State |
|---|---|---|
| B1 | `SPINE_1_scenario_world_state` | held — FRAME complete + mechanism BUILT; next step is **BUILD** (wire into price formation), needs the idle→build stage advance |
| B2 | `SPINE_3_gas_storage_crisis_regime` | DRAWABLE |
| B3 | `B3_published_forecast_error_horizons` | DRAWABLE (new) |
| B4 | `B4_traded_product_ladder` | DRAWABLE (new) |
| B5 | `B5_shaped_cost_benchmark_value_add` | DRAWABLE (new) |
| B6 | `B6_collateral_cash_death_loop` | DRAWABLE |
| B7 | `B7_customer_state_layer_moves_and_shocks` | DRAWABLE (new) |
| B8 | `B8_discovered_price_sensitivity_holdout` | DRAWABLE (new) |
| B9 | `E5_carbon_three_ledger` | DRAWABLE (re-opened, **not** duplicated) |
| B10 | `B10_competitor_switching_response` | DRAWABLE (new) |
| B11 | `B11_evolutionary_tournament_harness` | DRAWABLE (new) |

**Four of the eleven were NOT minted as new atoms** — they were reconciled to work already in the map,
because a duplicate row is worse than no row: **B9** = `E5_carbon_three_ledger` (as this doc already
said). **B7** is scoped to the *remainder* of the customer state layer — house moves (credit exit + two
deemed entries) and income shocks — because `W2_5_life_event_stream` already emits job loss / illness /
divorce / retirement / new child and is at target. **B8** registers only the **company** half
(discovered price-sensitivity + holdout uplift); the world half is the existing
`W2_14_continuous_behavioural_engagement_model`. **B10** registers only the missing **switching
response**; `W2_3_competitor_field` (at target) and `B4_competitor_field` already exist and were left
untouched — levels are proposals, not mine to move (R16).

**What is still director-reserved, unchanged by this pass** (registering work is not authorising it):
the idle→build stage advance on any of these; B1's named-world VALUES and their true probabilities, B2's
shock magnitude and target inversion shape, B10's price-war aggressiveness (all R13 curriculum); B9's
emissions-factor set and counterfactual method (category 6, carbon is the mission); B11's fitness
function and mortality rules (`A5_tournament_fitness_mortality`, the `values_decisions` gate). Every
level here stays at 0 — built things get proposed, never self-promoted.

## Keeping it stocked (the amendment's standing duty)
This list is not a one-off. As items land, pull their carry-overs up, and mine the gap/simplification
registers (`coupled_gap_ledger.json`, the simplification register) for the next candidates **before**
the list runs low — an empty backlog is a failure to *create* work, not a clean finish
(YOU OWN THE BACKLOG, test of compliance). Re-rank on evidence; log deviations (LAW A: the plan is a
diagnostic, never a target).
