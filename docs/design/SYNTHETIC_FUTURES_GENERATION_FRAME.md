# FRAME — Synthetic Futures Generation (W1_2_generate_futures)

**Atom:** `W1_2_generate_futures` — "Synthetic future market generation beyond real 2016-2025
history" · lane `W1_market_weather` · dial 4 · epoch 3 · `level_current: 0` → `level_target: 2` ·
`depends_on: [W1_reveal_over_time]` (currently `level_current: 3`, `loop_stage: harden` — the
dependency is met on the map's own "loop_stage idle-or-harden counts as met" rule).
**Stage:** DISCOVER/FRAME only. No product code, no `maturity_map.yaml` edit, no `git`. This
supersedes nothing in `docs/design/frame/W1_2_generate_futures_FRAME.md` — it is read and cited
below — but **corrects one load-bearing factual claim** that prior FRAME pass made (§1) using code
this pass read directly rather than from memory.

---

## 1. Problem, and the correction to prior art

**Why this atom exists (unchanged from the prior FRAME):** the baseline world is one realised path
— real 2016-2025 Elexon/NESO settlement history. A company that survives the replayed past has
survived exactly one draw from the distribution of possible worlds. The Epoch-4 evolutionary
tournament needs the company tested against **unseen** futures, including regimes with no
historical analogue, or it will overfit to the one crisis (2021-22) and one calm run (2016) that
actually happened. This is the SIM enriching the world, not the company gaining anything — the
company should get a harder world to survive, never new information.

**Correction to the record:** the existing `docs/design/frame/W1_2_generate_futures_FRAME.md` and
the DISCOVER note it cites (`docs/market_research/synthetic_future_generation_w1_2.md`) both assert
this atom is *"genuinely greenfield at the mechanism level... the actual stochastic engine... does
not exist anywhere in `sim/` today."* Reading the actual code (not summarising from memory, per this
project's own R4 discipline) shows this is **not true**:

- `sim/scenario/bimodal_generator.py` ("Phase 35a") already implements a **regime-switching Markov
  chain** stochastic price generator — two Gaussian regimes (gas-marginal upper mode, renewable-
  suppressed lower mode), a first-order Markov transition matrix solved so the long-run regime split
  matches a target fraction, plus negative-price-day and Dunkelflaute-spell overlays — for 2026-2030+
  electricity prices.
- `sim/scenario/gas_scenario_generator.py` ("Phase 35b") is the coupled gas-price counterpart, regime-
  conditioned on the same electricity Markov state (gas price rises when electricity is in the
  gas-marginal upper mode) — i.e. **cross-commodity coupling already exists**, not a future TODO.
- Both are calibrated against real external research
  (`docs/market_research/price_distribution_high_renewables_2027.md`, June 2026: Ember Energy 2025/
  2026 GB market data, arXiv 2501.10423 causal merit-order analysis, Cambridge EPRG WP2503), each
  parameter confidence-rated H/M/L against a named source — genuine fidelity anchoring, not invented
  numbers.
- Both are **already wired end-to-end**: `simulation/run_scenario.py` (Phase 36a) concatenates
  historical + generated records and runs the *full* historical replay pipeline
  (`run_phase2b.main()`) through them; `simulation/scenario_comparison.py` (Phase 38a) runs all five
  named scenario presets and reports company KPIs (net margin, treasury, churn) side by side;
  `saas/reporting/annual_report.py` already reads scenario output for reporting.

**What this means for the FRAME:** the mechanism/content split in the prior notes is real and still
the right lens, but the "mechanism does not exist, build from scratch" conclusion is wrong — a
working, calibrated, coupled two-regime stochastic generator **already exists and already runs the
company through it**. The real remaining gap is not "build a generator" — it is three concrete,
narrower defects this FRAME identifies below (§4), plus the genuinely-missing piece: a
**director-facing, versioned scenario-authorship boundary** (§5) and **substream discipline** (§6),
neither of which exist today. This FRAME reduces the atom's scope considerably versus the prior
pass's "greenfield" framing — most of the *statistical machinery* is done; what remains is wall-
discipline around it.

## 2. The overfit risk this removes

Without this atom, the Epoch-4 tournament (`A5_tournament_fitness_mortality`, which
`depends_on: [W1_2_generate_futures, A4_sim_approver]`) has only the real 2016-2025 record to score
company variants against — a single historical draw, reused across every generation. A
search/selection process run against one fixed history will converge on strategies fitted to that
history's specific idiosyncrasies (e.g. a hedge policy tuned to exactly when the 2021-22 gas crisis
happened), not to the underlying *distribution* of UK energy markets. `sim/scenario/` already
supplies five named regimes that are qualitatively different draws from that distribution
(`central_2027`, `stress_dunkelflaute_2027`, `low_renewables_2027`, `battery_saturation_2029`,
`baseline_2025`); running a company variant across all five and requiring survival across the set,
not just the mean, is what prevents single-path overfitting.

## 3. Generative model recommendation

Per the prior FRAME's own selection criteria (block bootstrap is fidelity-faithful for "more of the
same" but cannot extrapolate to a no-precedent regime; regime-switching/calibrated processes can):
**recommend keeping and hardening the existing regime-switching Markov mechanism
(`bimodal_generator.py`/`gas_scenario_generator.py`)** rather than building a second, competing
stochastic engine. Reasons:

1. It already satisfies the "extrapolate to unseen regimes" requirement that block bootstrap
   structurally cannot (a bootstrap of 2016-2025 blocks can never produce a regime with no
   historical analogue, e.g. 70%-renewables negative-price-dominated pricing).
2. It is already calibrated against named, dated, confidence-rated real sources — not a fresh
   calibration exercise.
3. It already has cross-commodity coupling (gas regime tied to electricity regime), which the prior
   FRAME's 2026-07-15 DISCOVER note flagged as a **missing** feature ("a synthetic FUTURE market must
   be DRIVEN BY weather physics... building W1_2 as an independent SSP path generator would reproduce
   the exact naive-decoupling error"). That note was written without reading `gas_scenario_generator.py`
   — the electricity↔gas coupling already exists. The **actual remaining coupling gap** is weather:
   neither generator reads `sim/weather_engine.py`/`W1_3_national_weather_signal` output at all; the
   "renewable-suppressed lower mode" and "Dunkelflaute" regimes are today driven purely by a scheduled
   Markov state, not by an actual generated weather series. This is real portability debt (§7), not
   fixed here.
4. Reuse avoids two divergent calibration surfaces (one anchored to reality, one improvised) — a
   direct R13 risk if a second engine's parameters were chosen without the same external-benchmark
   discipline.

**What still needs building (BUILD-stage, not this doc):** a thin **block-bootstrap fidelity-check
mode** — resampling real 2016-2025 daily returns as a *sanity baseline* the regime-switching output
must not statistically diverge from on shared moments (mean, autocorrelation decay, seasonal shape)
where the two are expected to agree (i.e. the `baseline_2025`-style scenario). This is the "reconcile
to real distributional moments" gate the prior FRAME named (§8 below), using block bootstrap as the
*reference*, not as a second generator to maintain.

## 4. Concrete defects found reading the existing wiring

Three real, load-bearing gaps, found by reading the actual code paths, that BUILD must close before
this atom can honestly claim L1/L2:

**(a) Epistemic-wall violation, already flagged and unresolved.**
`docs/staging/done/Sim_boudary_audit.md` (`docs/architecture/sim_boundary_audit_20260630.md`) found
that `saas/reporting/annual_report.py` imports `sim.scenario.bimodal_generator` **directly** — a
company/SaaS-layer reporting module reading SIM-internal scenario machinery, not going through
`company/interfaces/sim_interface.py`. The audit names the fix explicitly ("source scenario/segment
composition from what the company has actually observed and recorded, not sim internals") and it has
been open, unaddressed, since it was filed. This is the exact epistemic-wall class this atom's own
Point-in-Time Blindfold requirement exists to prevent — **flagged, not fixed here** (out of scope for
a doc-only FRAME); BUILD must close it as part of reaching L1, not defer it further.

**(b) No `data_regime` tagging on the generated+historical concatenation.**
`.claude/rules/epistemic-wall-sim.md` states: *"every record should carry `historical` or
`synthetic`... do not drop this field when adding new record types."* `run_scenario.py::
build_extended_price_feeds()` concatenates `historical_elec + elec_hh` with **no `data_regime` field
on either half** — the combined list is structurally indistinguishable historical-vs-synthetic once
built. Contrast `simulation/population_draw.py`, which does carry `data_regime: str = "synthetic"` on
its own generated records. This is a real, fixable gap, not a design question — BUILD adds the field
to both halves of the concatenation.

**(c) Bulk injection bypasses the reveal seam this atom `depends_on`.**
`run_scenario.py` builds the **entire** future price series up front and hands it whole to
`run_phase2b.main()`, the same historical-replay engine used for the real record. This is safe for
*producing* the SIM's ground truth (the future path is not company-visible data, it's the world's own
new history), but it means the generated path never actually passes through
`W1_reveal_over_time`'s machinery (`PointInTimeView`/`BitemporalEventLog`) — the very mechanism this
atom's `depends_on` names as its blindfold enforcer. Today's company-side reads
(`estimate_price_volatility()` et al., per `W1_reveal_over_time`'s own build history) are protected by
their own backward-looking windowing regardless of whether the underlying feed is historical or
scenario-generated, so there is **no live leak** currently — but the design intent (§ the prior
FRAME's §4, "a company model whose output depends on a not-yet-revealed value is a blindfold breach")
is not yet *structurally* enforced for the scenario path the way it is enforced for the real 2016-2025
path. BUILD's job at L1/L2 is to route scenario-generated records through the same as-of/bitemporal
gate real records already get, not to add a second, parallel, ungated future-data channel.

## 5. R13 wall, made concrete

R13 (`MARGIN_REALISM.md`) splits BASELINE (real history + externally-calibrated generators, may only
change for fidelity-to-reality reasons, blind to company P&L) from CURRICULUM (which worlds the
company lives through — the director's own instrument, named/versioned, never silent drift, never
tuned to company outcomes). Applied concretely to what already exists:

- **The generator's statistical machinery is BASELINE-adjacent and fidelity-owned.** The Markov
  transition solver, the Gaussian regime draws, the Dunkelflaute/negative-price overlay mechanics —
  these are calibration MECHANISM, validated against Ember/arXiv/EPRG sources blind to any company
  P&L number. This part may keep evolving for fidelity reasons (e.g. a better weather-coupling term,
  §3 point 3) without director sign-off, same as any other baseline generator.
- **The five named presets (`baseline_2025`, `central_2027`, `stress_dunkelflaute_2027`,
  `low_renewables_2027`, `battery_saturation_2029`) are CURRICULUM CONTENT, and were authored by the
  agent (Phase 35a, before R13 existed as a written rule, 2026-07-10) without director selection.**
  This is a genuine, honest gap this FRAME surfaces rather than glosses over: R13 requires curriculum
  choices to be "named, versioned, director-authored artefacts," and these five names/parameter sets
  were chosen unilaterally, calibrated to real research but never presented to the director as a
  scenario-selection decision. **This does not mean the presets are wrong** — the parameters trace to
  real sources — but their STATUS as tournament-difficulty content has never been director-ratified.
  Two ways to close this cleanly at BUILD, either is acceptable, neither decided here (R13 reserves
  the choice to the director, not this FRAME): (i) retroactively present the five existing presets to
  the director as a scenario-library ratification decision (fast — the calibration work is already
  done and real); or (ii) treat the five presets as *agent proposals* (`provenance: proposal`, per
  `EPOCH_GATING_AND_ATOM_AUTHORSHIP.md` Rule 2 — DISCOVER/FRAME-workable, never tournament-load-
  bearing until opened) until the director names which subset (if any) the tournament actually runs.
- **Structural enforcement (the actual wall, not a policy statement):** the generator function
  (`generate_scenario_prices`) already takes a `scenario: str | ScenarioParams` argument rather than
  hardcoding a single path — i.e. it already "reads a spec, does not invent one," the shape the prior
  FRAME's §2 called for. The missing piece is that `SCENARIOS: dict[str, ScenarioParams]` lives as a
  Python literal inside the SIM module, not as an external, versioned file the director owns and
  diffs against. BUILD should externalise it (e.g. `sim/scenario/scenario_library/*.yaml`, one file
  per named scenario, each carrying `provenance: director-authored | proposal`,
  `ratified_by`/`ratified_at` fields, and a citation back to its calibration source) so a new curriculum
  entry is a reviewable file diff, not a code change — the same "versioned, named artefact" pattern
  R13 requires elsewhere (`docs/design/DIRECTOR_CANON.md`-style). A missing/unratified scenario spec
  at tournament-run time is a **hold-for-director**, never an agent default (per the existing FRAME's
  §7 open item 1).

## 6. RNG substream discipline (C-S2)

Current state: `generate_scenario_prices()`/`generate_gas_scenario_prices()` seed via
`random.Random(f"{seed}_{year_from}_{year_to}_{scenario_name}")` — a private, ad hoc string-seeded
generator local to the function, not touching the shared world RNG or any other subsystem's stream.
This is **not currently a leak** (no shared state), but it does not follow the project's own
established substream pattern (`simulation/population_draw.py::_substream()`,
`simulation/life_events.py::_substream()`): a **stable SHA-256 digest of `(base_seed, name)`**,
guaranteed process-independent, versus Python's built-in string-seeding of `random.Random`, which is
deterministic within a given CPython version but is not a documented cross-version stability
guarantee the way an explicit `hashlib.sha256` digest is.

**Recommendation for BUILD:** refactor both generators onto the same named-substream helper already
proven at `simulation/population_draw.py::_substream()` / `simulation/life_events.py::_substream()`
— ideally by **factoring it into one shared utility** (e.g. `simulation/rng_substream.py`) both
existing call sites and the new one import, rather than a third independent reimplementation (DRY,
and it closes the "is this really stable across processes" question with the same proof
(`test_substream_isolation_*`) the other two subsystems already carry). Named substreams for this
atom, one per generator/degree of freedom that can independently vary:

- `future_market.electricity.regime_switch` — the Markov state sequence draw.
- `future_market.electricity.regime_price` — the within-regime Gaussian price draw.
- `future_market.electricity.dunkelflaute` — event scheduling + multiplier draw.
- `future_market.electricity.negative_price` — negative-day scheduling + magnitude draw.
- `future_market.gas.regime_price` — the coupled gas-price draw (reads, never re-draws, the
  electricity regime state — coupling must be a value dependency, not a second independent RNG for
  "which regime," or the two commodities silently decouple).

Keyed by `(base_seed, scenario_name, year_from, year_to)` so **adding a new named scenario, or
extending an existing scenario's year range, can never perturb any other scenario's, or any other
subsystem's (weather/churn/life-events), draws** — the identical proof obligation the 01:09Z
life-events incident established as necessary (CLAUDE.md C-S2). Deterministic replay requirement:
regenerating the same `(scenario, seed, year range)` must reproduce byte-identical output — already
true today given the ad hoc string seed; the refactor preserves this property, it does not introduce
it.

## 7. Point-in-Time Blindfold and reveal-seam integration

Generated futures are SIM ground truth exactly as the prior FRAME's §4 states — held inside the world
layer, revealed to the company only as sim-time advances past each half-hour. Concretely, once §4(c)
is closed at BUILD:

- The generator still produces the full path up front (a deterministic function of scenario+seed —
  this is a property of the world, not a leak; a real future weather/price path also "exists" in full
  before it is observed, the blindfold is about what the *company* can read, not about when the world
  computes it).
- Every generated record is appended to the same bitemporal store real records populate
  (`company/interfaces/bitemporal_event_log.py`), tagged `data_regime: "synthetic"`, with
  `valid_time` = the settlement date/period the scenario places it at and `transaction_time` set no
  earlier than that date becomes "current" in sim-time — i.e. exactly the same construction
  `W1_reveal_over_time`'s L3 fix already applies to real records (`transaction_time` = midnight of
  `valid_date + 1`, closing the same-day leak its own Expert Hour found). A generated future gets no
  special-cased earlier visibility than a real one.
- `PointInTimeView.get_price_history_as_of()` then serves both historical and synthetic records
  identically — a company-side reader cannot distinguish "am I in the real replay or a scenario run"
  from the interface shape, only from the (masked, per §4a) `data_regime` field if it is ever exposed
  at all, which it should not be to the company (a real supplier never learns "this market segment is
  synthetic").
- **The wall test, restated for this atom specifically:** at any sim-time T inside a scenario run, the
  company's observable set (forward prices, spot history, volatility estimates) must be a function
  only of generated-path values at settlement time ≤ T. A scenario run where a company-side hedge
  decision's output changes when future (not-yet-revealed) scenario prices are altered, holding
  everything ≤ T fixed, is a blindfold breach — this is a literal, runnable mutation test (§8).

## 8. Validation & mutation-test plan

Two independent obligations, per R15 (a control that cannot fail is worse than none — every claim
below must be backed by a test that can be shown to catch its own named defect):

**(A) Fidelity/statistical reconciliation** (validates the BASELINE-adjacent machinery, §5):
1. Generate a `baseline_2025`-preset path and assert its annualised mean, coefficient of variation
   (same statistic `calculate_sigma_recent()` already computes), and month-of-year seasonal shape
   fall within a plausibility band anchored to the real 2016-2025 Elexon/NBP record (matching this
   atom's own real_world_twin framing and R12's "plausibility bands are diagnostic, anchored to
   external sources, never tuned to output"). A **mutation test proving this control can fail**: feed
   the checker a deliberately-broken generator (e.g. one with `lower_mode_fraction=1.5`, an invalid
   probability) and assert the reconciliation check actually FAILS — not merely that the real
   parameters pass (a tautology risk named by R15 directly: "checked value derived from the same
   source it checks").
2. Block-bootstrap reference check (§3): resample real daily log-returns and assert the regime-
   switching generator's *baseline* preset does not diverge on autocorrelation decay / vol-clustering
   beyond a stated band from the bootstrap reference — this is the "more of the same" fidelity floor;
   stress presets (`stress_dunkelflaute_2027` etc.) are explicitly exempt (they are meant to diverge —
   that is the point of a no-precedent regime) but must still reconcile on things that shouldn't
   change under any regime (e.g. `settlementPeriod` structure, no negative electricity price below the
   real historical spike ceiling times a stated multiplier, not an unbounded blow-up).

**(B) Blindfold mutation test** (validates the wall, §7): construct a scenario run, then **deliberately
leak** a future scenario value into a company-side read (e.g. monkeypatch `get_price_history_as_of()`
to include one record with `valid_time > current sim-time`) and assert the existing/extended
detector — `.claude/hooks/block_point_in_time_read.py` and/or a new
`test_structurally_excludes_future_scenario_dates` test mirroring
`W1_reveal_over_time`'s own `test_structurally_excludes_future_dates` — **catches it**. Per R15, a
blindfold check that only ever runs against already-correct code proves nothing; this test must be
shown red-then-green (fails against the deliberately-broken injection, passes once removed) before
this atom can claim the wall is enforced, not merely designed.

**(C) Substream isolation test** (validates §6): mirror
`simulation/population_draw.py`'s existing `test_substream_isolation_*` pattern — assert that adding a
new named future-market substream, or changing one scenario's parameters, does not change a single
byte of another subsystem's (weather/life-events/population-draw) or another scenario's output, given
the same top-level seed.

## 9. L1 → L2 decomposition and file_scope

**L1 target ("a single synthetic path generator... produces a fidelity-checked future price series
beyond 2025, held as SIM ground truth, revealed only via the blindfold seam... draws from a named
seeded RNG substream," per the prior FRAME's §6 — narrowed here to concrete BUILD steps):**

1. Fix §4(a): remove `saas/reporting/annual_report.py`'s direct `sim.scenario.bimodal_generator`
   import; source scenario/company-observed composition through `company/interfaces/sim_interface.py`
   or an equivalent company-observed record, per the existing `Sim_boudary_audit.md` finding.
2. Fix §4(b): add `data_regime` tagging (`"historical"` / `"synthetic"`) to both halves of
   `run_scenario.py::build_extended_price_feeds()`'s concatenation.
3. Fix §4(c)/§7: route generated records through the same bitemporal/as-of construction real records
   use (`build_price_bitemporal_log`-style, `transaction_time = valid_date + 1`), so a scenario run's
   company-side reads are wall-enforced identically to the real replay, not via a separate ungated
   path.
4. Refactor §6: introduce (or extend) a shared named-substream helper and re-seed both existing
   generators onto it, one substream per named draw.
5. Ship §8(A)/(B)/(C) as real, executed tests, including the mutation-test halves (red-then-green),
   not assertions alone.

**File scope this BUILD phase would touch (declared here for the orchestrator's disjointness check
per H9/L1 BUILD serialisation rules — not written by this FRAME pass):**
- `sim/scenario/bimodal_generator.py`, `sim/scenario/gas_scenario_generator.py` (substream refactor,
  `data_regime` tagging)
- `simulation/run_scenario.py` (data_regime tagging, bitemporal routing)
- `simulation/rng_substream.py` (new, shared substream helper — or extend
  `simulation/population_draw.py`'s existing one if the orchestrator prefers no new file)
- `saas/reporting/annual_report.py` (remove direct sim-internal import — same fix
  `Sim_boudary_audit.md` already named, narrower than a fresh discovery)
- `company/interfaces/bitemporal_event_log.py` / `point_in_time_view.py` (no interface change
  expected — reuse, confirm no new method needed once §4(c) is attempted)
- `tests/sim/test_bimodal_generator.py`, `tests/sim/test_gas_scenario_generator.py`,
  `tests/simulation/test_run_scenario.py` (new/extended tests per §8)
- New, if (i) in §5 is chosen: `sim/scenario/scenario_library/*.yaml` + a small loader.

**L2 target (multiple named, director-authored curriculum scenarios, versioned specs, R13
structurally enforced — per the prior FRAME's §6, unchanged as a target):** externalise `SCENARIOS`
into versioned files per §5's structural-enforcement point; resolve the five-existing-presets
ratification question (§5, either path (i) or (ii)); regime-switching remains the no-precedent
extrapolation knob. Not this FRAME's job to choose (i) vs (ii) — that is exactly the director gate
the prior FRAME's §7 already named ("the initial scenario library... is a curriculum/values
decision").

## 10. Open director gates (unchanged in kind from the prior FRAME, sharpened in content)

1. **Ratify or reclassify the five existing presets** (§5) — the one concrete, actionable decision
   this FRAME adds precision to; everything else here is BUILD-executable without further director
   input.
2. Sign-off that the fidelity-calibration step (§8A) stays genuinely blind to company P&L, per R13.
3. Confirmation of the plausibility bands used for the distributional sanity check (anchored to
   Elexon/NESO/Ember/arXiv sources already cited, not to company results) — largely already satisfied
   by the existing `price_distribution_high_renewables_2027.md` research, needs director awareness
   rather than fresh work.

## 11. Portability & scale-readiness (unchanged from prior FRAME, confirmed against real code)

- **C-S2** — addressed concretely in §6 (was abstract in the prior FRAME).
- **C-S5 time-scale invariance** — both existing generators work in whole calendar days, then expand
  to half-hourly via flat replication (`_expand_daily_to_hh()` repeats one price across all 48
  periods) — an explicit, already-named simplification (no intraday shape in the synthetic path,
  unlike the real record's genuine HH variation). Register this at BUILD as a stated L3+ exception,
  not fixed by this FRAME.
- **Portability (second market/product)** — `ScenarioParams`/`GasScenarioParams` are named per fuel
  (`electricity_n2ex`-style implicit assumption via `sim/data/seasonal_calibration.json` reuse
  elsewhere in `sim/forward_curve.py`) but the scenario generators themselves take no explicit
  market/commodity key beyond a fixed two-fuel (elec/gas) shape — a second geography would need a
  third generator module, not a parameterisation of the existing two. Log as portability debt at
  BUILD if untouched; not fixed here.
- **SIMPLICITY GUARD** — the recommendation throughout this FRAME is *reuse and harden*, not build a
  second engine; this is the simplest construct available given what already exists.
