# B4_competitor_field — FRAME (closing DISCOVER/FRAME to L1)

- **id:** B4_competitor_field · **lane:** B_commercial · **value_stream:** wholesale_to_price · **epoch:** 4 · **dial:** 3
- **level:** current 0 → target 1 (this doc closes the FRAME to L1 — a complete FRAME artifact IS the L1 bar for a DISCOVER/FRAME-scoped atom; no BUILD code, no wiring, `loop_stage` stays `idle` until BUILD is opened)
- **depends_on:** `W2_3_competitor_field` (WORLD, currently L1/harden)
- **supersedes/extends:** `docs/design/frame/B4_competitor_field_FRAME.md` (2026-07-16 08:23 pass) — that doc's problem statement, coupled-triad split, and portability notes stand and are not repeated verbatim; this doc adds the concrete competitor-price-setting model, the versioned observable schema, the churn/acquisition wiring shape, and the gap metric definition it left open, then re-states the L1 acceptance and L1+ decomposition as the closing artifact.

## 0. Why this atom exists — the discipline it's missing today

Today the company faces **no market discipline on price**. Grepped the real live pricing pathway
directly: `simulation/renewals.py` (the actual call site that builds the historical replay's renewal
schedule) has zero references to `svt`/`competitor`/`ceiling` of any kind (confirmed unchanged across
three prior DISCOVER/FRAME passes, 2026-07-12/13/15, see `maturity_map.yaml` B4 `simplifications`).
The company could in principle price arbitrarily above cost and lose nothing to a rival, because there
is no rival. Two consequences follow directly from CLAUDE.md's own standing doctrines:

- **Activity-based pricing note:** flat margin already makes some customers net-negative (cost-to-serve
  varies by segment/channel). Without competitive pressure, that mispricing has no corrective force —
  a real supplier that overprices a cheap-to-serve segment loses it to a rival; this company currently
  cannot lose anything to anyone. Competition and cost-to-serve **interact**: the ceiling bites hardest
  on the segments a rival can profitably steal (low cost-to-serve, price-sensitive), which is exactly
  where activity-based pricing already says the company is most exposed.
- **Portability:** a competitor field is inherently market/segment-shaped (rivals differ by geography
  and product), so it must be keyed that way from the start, not hardcoded to "the GB grid" as a
  singleton (§6).

B4 is the **company-side** half of this capability: the belief the company forms about the market and
the decisions that belief touches. The world-side generator is `W2_3_competitor_field` (below).

## 1. Prior art already in the repo (read before building anything)

Two real, non-trivial, real-data-anchored modules already exist and are **both currently orphaned**
(zero non-test callers) — confirmed again this pass via `grep -rn "RenewalPricingEngine\|TariffBenchmarkingRegister" --include=*.py company saas simulation | grep -v test`:

- `company/pricing/renewal_pricing_engine.py` — `RenewalPricingEngine.price_renewal()` computes a
  renewal tariff against **one reference figure**: SVT, capped at `SVT × 1.02`
  (`_RENEWAL_CONVERSION_DECAY_PER_PCT_ABOVE = 0.02`, CMA-2016-calibrated conversion decay per % above
  benchmark). This is a **ceiling-only** mechanism — single benchmark, no rival dispersion.
- `company/market/tariff_benchmarking.py` — `TariffBenchmarkSnapshot`/`CompetitorTariff`/`SupplierRank`
  (CHEAPEST…MOST_EXPENSIVE) models a **multi-competitor snapshot** with named rivals, sourced from real
  public feeds (Ofgem comparison tool, uSwitch, BEIS DUKES). This is the **undercut-pressure** half —
  richer, but keyed to *individual named competitors*.

The decisive constraint (found 2026-07-15, re-confirmed this pass by reading `W2_3`'s own registration
in `maturity_map.yaml` line 370-384): `W2_3_competitor_field`'s ground truth today is **one aggregate
scalar per year** — `simulation/market_switching_propensity.py::MARKET_SAVINGS_BY_YEAR` (GBP/yr saving
available from switching to the *best* competitor deal, DESNZ/Ofgem-anchored, 2016-2025) — **not** a
set of individuated rivals with their own tariffs. `tariff_benchmarking.py`'s `SupplierRank` therefore
has **no world-side ground truth to observe today**: wiring it now would mean the company reading a
richer competitor field than the SIM actually generates — a direct epistemic-wall violation, not a
simplification. Confirmed via `.claude/rules/epistemic-wall-company.md`'s own test ("could a real
supplier know this without simulation internals?") — no, because there *is* no simulation internal for
it to correspond to.

**Conclusion carried into this FRAME's L1 scope (§4):** L1 wires the **aggregate ceiling** signal
(reusing `renewal_pricing_engine.py`'s SVT-ceiling *shape*, generalised to a market-reference-plus-
savings signal), and explicitly **defers** `tariff_benchmarking.py`'s named multi-competitor model until
`W2_3` itself reaches L2+ and actually generates individuated rivals for it to observe. Wiring it sooner
would be building a company sense-organ for a nerve that doesn't exist yet.

## 2. The competitor-field model (WORLD side, `W2_3`, ground truth the company must not read directly)

This section specifies what the *world* should generate so the company has something honest to
observe — scoped for `W2_3`'s own eventual L2+, described here because B4's L1 observable (§3) is a
deliberately thin **projection** of it, and the shape of the projection only makes sense against the
richer thing it is a projection of.

- **Population:** GB domestic/SME market realistically has ~8-12 active suppliers at any time
  post-2021 consolidation (down from ~60 pre-2021 collapse) — `W2_3`'s own `real_world_twin` already
  names "~8 active suppliers." Model as N named rival slots (N itself a curriculum parameter, §5), each
  with a tariff-setting policy, not a fixed roster (suppliers enter/exit, matching the real 2021-22
  mass exits).
- **Price-setting per rival, per period:** `rival_price = market_reference_price + rival_spread + noise`,
  where:
  - `market_reference_price` = a wholesale-cost-plus-regulatory-cap composite (the same forward-curve
    and DTCC-derived non-commodity costs the company itself faces, since rivals share the same input
    market) — **not** independently invented per rival, so undercutting is economically meaningful
    (a rival below cost is a real loss-leader, not free noise).
  - `rival_spread` = a per-rival competitive positioning constant (aggressive discounter vs premium/
    green-tariff/service-differentiated) — calibrated to real GB tariff-comparison dispersion. Ofgem's
    own price-cap/comparison-tool publications show typical **cheapest-vs-cap spreads of roughly
    5-20%** in a competitive year (2016-2020) collapsing to **~0% or negative** in the 2022 crisis
    (fixed deals priced *above* the cap floor — the "nowhere cheaper to go" effect already encoded in
    `MARKET_SAVINGS_BY_YEAR[2022] = -200.0`). The dispersion **across rivals**, not just the level, is
    the calibration target: a competitive year needs a real spread of cheapest-to-priciest live tariffs,
    not all rivals clustered on one number.
  - `noise` = small per-period idiosyncratic variation (a rival's own margin call, campaign timing) —
    keeps individual rivals from moving in lockstep, matching real observed tariff-change dispersion.
  - **Regime response to wholesale moves:** rivals should re-price with a **lag** relative to the
    company's own forward-curve exposure (a real rival doesn't instantly reprice the moment wholesale
    moves — tariff review cycles, existing-book protection rules post-2023) — this lag is itself the
    source of transient undercut/overprice windows the company must cope with, not a bug to smooth away.
- **Moves, not just levels:** rivals should be capable of **cut / hold / withdraw** actions (a rival
  pulling a fixed product entirely, matching the real 2021 withdrawal wave) — `W2_3`'s own registration
  already names this as a real, currently-missing L2+ gap ("their own market share, entry/exit,
  per-competitor tariff evolution").
- **This is BASELINE, calibrated to reality (R13):** the price-setting mechanism and its dispersion
  calibration are fidelity questions, decided blind to company P&L, changeable only for
  fidelity-to-reality reasons — never tuned because the company's margin looks wrong under it.

## 3. The OBSERVABLE — what crosses the wall to the company

The company never reads §2's internals (rival cost basis, spread policy, intent, or the RNG substream
generating it). It reads a **typed, versioned message**, in the same style as
`company/interfaces/sim_interface.py`'s existing methods (`get_forward_price`, `get_settlement_data`):

```python
@dataclass(frozen=True)
class CompetitorFieldObservation:
    """Published-tariff-like observable. Crosses the SIM/company wall — sim_interface.py style.

    Everything here is something a real supplier could read off a comparison site or its own
    switching-in/out flow. Nothing here is a rival's cost stack, margin target, or intent.
    """
    as_of_date: str                     # ISO date — ties to point-in-time discipline
    market_id: str                      # keyed by market/segment, NOT hardcoded (§6)
    segment: str                        # resi / SME / I&C — observable differs by segment
    observed_ceiling_gbp_per_mwh: float # cheapest-visible-tariff-derived reference (was: SVT-only)
    savings_available_gbp_pa: float     # aggregate switching-saving signal (W2_3's real ground truth
                                         # today — MARKET_SAVINGS_BY_YEAR's own figure, generalised)
    market_rank_hint: Optional[str]     # OPTIONAL, coarse (e.g. "below_average"/"above_average"),
                                         # ONLY populated once W2_3 reaches L2+ with real per-rival
                                         # dispersion to rank against — None at L1, not fabricated
    data_regime: str                    # "historical" | "synthetic" — never dropped (epistemic-wall-sim.md)
    schema_version: int = 1
```

Request/response are **separate events in time** (C-S3) — a `CompetitorFieldObservation` is fetched as
of a date, not resolved same-step with the pricing decision that consumes it, matching the real
seconds-to-days latency of an actual comparison-site read. Processing the same observation twice is a
no-op (C-S2 idempotency) and observations may arrive **one at a time, late, or out of order** relative
to renewal dates (C-S1) — the company's consumer must not assume "today's whole field" arrives as one
batch; a single stale-but-valid observation must be tolerable if a fresher one hasn't arrived yet.

## 4. How the observable feeds churn and acquisition/renewal — L1 wiring shape

Two live coupling points, both consuming **only** `CompetitorFieldObservation`, never `W2_3`'s
internals:

- **Ceiling → churn (retention risk):** the probability a customer leaves rises with the company's
  premium to the observed ceiling. Concretely: extend the *existing* company-side churn estimate
  (`company/crm/churn_model.py` / `enriched_churn_estimate.py`, already grepped as real modules with
  competitor-adjacent logic) with a new input — `(company_price − observed_ceiling_gbp_per_mwh) /
  observed_ceiling_gbp_per_mwh` — a positive premium tightens the churn estimate upward. This is a
  **belief-side** adjustment: the company's own churn model reacting to its own inferred premium, not a
  read of `W2_3`'s true churn multiplier.
- **Undercut → acquisition/renewal win-rate:** `RenewalPricingEngine.price_renewal()`'s existing SVT-only
  ceiling (`svt_gbp_per_mwh` param, capped at `×1.02`) generalises to take `observed_ceiling_gbp_per_mwh`
  from the observation instead of (or alongside) SVT — the mechanism (`_estimate_conversion()`'s
  overprice-decay curve) is **already built and already CMA-anchored**; L1's real work is threading a
  live `CompetitorFieldObservation` into the call, not re-deriving the decay curve. `savings_available_
  gbp_pa` gates whether undercut pressure exists at all this year (matching `W2_3`'s own "nowhere
  cheaper to go" 2022 finding — a company should not feel undercut pressure it structurally couldn't
  have suffered).
- **Pricing sanity check:** any renewal/acquisition price that exceeds `observed_ceiling_gbp_per_mwh`
  without a logged reason (e.g. deliberate margin-recovery decision) should be flagged, not silently
  allowed — the ceiling becomes a decision-log-visible constraint, not just a passive number.

## 5. The coupled-triad gap metric

Per COUPLED_TRIAD (no world atom reaches L3 until the company has been tested against it and the gap
measured; no company capability is complete until it has faced a world that can defeat it), the harness
metric for this pair is:

**`competitor_field_belief_gap` = company's inferred premium/rank vs `W2_3`'s true generated field,
at the same as-of date.**

Concretely, two components (both computable without the company ever reading `W2_3` directly — the
harness sits *outside* the wall and can read both sides for measurement purposes only):

1. **Ceiling gap:** `|observed_ceiling_gbp_per_mwh (as seen by company) − true_cheapest_rival_price
   (W2_3 ground truth, same as_of_date)|` — non-zero whenever the observation is stale, the projection
   from §2→§3 loses information, or a rival's price move hasn't yet propagated through the observation
   lag (§2's regime-response lag is a *deliberate* source of this gap, not noise to eliminate).
2. **Undercut-direction gap:** does the company's win-rate/churn response move in the **correct
   direction** relative to `W2_3`'s true undercut state, even if the magnitude is imprecise? (a company
   that gets the sign wrong — e.g. treats a genuine rival exit as ongoing undercut pressure — is a worse
   failure than one that gets the magnitude approximately right.)

Both are reported per coupled pair each digest, per COUPLED_TRIAD's standing requirement. A **large,
persistent gap is not itself a defect** — it is the expected signature of a real epistemic limit (a
real supplier is genuinely sometimes wrong about where the market sits); a defect is a gap that never
moves in response to new observations, or one the company can silently see-through (a wall leak).

## 6. Portability (market/segment-keyed, not hardcoded)

`CompetitorFieldObservation.market_id` and `.segment` are first-class keys, not decoration — per the
portability design constraints (`PORTABILITY_DESIGN_CONSTRAINTS.md`), a second geography or product
must drop in behind the same seam with its own rival roster, ceiling convention, and switching
mechanics, without a new observation type or a new consumer shape in the company layer. No counterparty
(a specific named rival) is ever hardcoded into a company-side decision path — only the aggregate/
projected fields are, exactly matching the constraint that the obligations register must be keyed by
regime, not by one hardcoded market.

## 7. Scale-readiness (C-S1–C-S5, simplicity guard)

- **C-S1 event-arrival tolerance:** consumer of `CompetitorFieldObservation` must be correct if
  observations arrive one at a time / late / out of order — no "wait for the whole field this tick"
  assumption (§3).
- **C-S2 idempotency + deterministic replay:** re-processing the same observation is harmless; the
  world-side rival price-setting RNG (§2's `noise` term) draws from its **own named seeded substream**
  (matching the population/life-event precedent from the 01:09Z incident) so adding rival noise can
  never shift any other subsystem's draw sequence.
- **C-S3 asynchronous wall contract:** already the observation's own shape (§3) — fetch is a separate
  event from the pricing decision that consumes it.
- **C-S4 persistence behind an interface:** observation history (if retained) goes through the existing
  append-only event-log abstraction, not a bespoke store.
- **C-S5 time-scale invariance:** the churn/undercut coupling (§4) should not assume a fixed settlement
  cadence — declare this explicitly at BUILD time if any half-hourly-specific shortcut is taken (R10
  simplification, not silent).
- **Simplicity guard:** no repository-pattern cathedral for one dataclass and two call-site edits — the
  wall (`sim_interface.py`) already provides the seam; L1 adds one method + one field thread-through,
  not new architecture.

## 8. Curriculum / director gates (R13) — unchanged from the prior FRAME pass, restated for completeness

**Competitor aggressiveness (rival count N, spread dispersion, whether a price war or a fixed-deal
withdrawal wave occurs) is director-authored CURRICULUM, never agent-tuned.** The baseline calibration
(§2's real-anchored spread/dispersion figures) may only change for fidelity-to-reality reasons, decided
blind to company P&L (R13). Open director-gate questions, unchanged and still open:
1. Canonical competitor-field scenario set + default (calm / challenger price-war / 2022-crisis-style).
2. Whether the observable includes comparison-site *ranking* (`market_rank_hint`) pre-emptively or only
   once `W2_3` reaches L2+ with real per-rival dispersion to rank against (this FRAME recommends: wait
   for L2+, per §1's epistemic-wall finding — populating a rank hint from an aggregate scalar would be
   fabricating precision the world doesn't generate).
3. Whether the Ofgem price cap is its own regulatory-ceiling atom or folded into this competitive
   ceiling (recommend: cap stays separate; B4's ceiling is the *competitive* one, tighter than or equal
   to the cap, never looser).

## 9. L0→L1 acceptance (this FRAME) and L1+ BUILD decomposition

**L0→L1 acceptance (satisfied by this document):**
- [x] Problem named: no market discipline on price today (§0), confirmed via direct grep of the live
  call site, not assumed.
- [x] Prior art read and reconciled, not re-invented (§1) — both orphaned modules' real shapes
  understood, the epistemic-wall constraint on `tariff_benchmarking.py`'s multi-rival model identified
  and carried forward as an explicit L1 exclusion, not silently dropped.
- [x] WORLD-side model specified to the depth B4's observable needs to make sense against (§2), with
  real GB tariff-dispersion anchors named (Ofgem cap/comparison-tool spread, 2022 crisis inversion).
- [x] COMPANY-side observable specified as a concrete typed/versioned dataclass (§3), epistemic-wall
  compliant (no rival internals, `data_regime` field retained).
- [x] Concrete churn + acquisition/renewal wiring points named against **real existing code** (§4) —
  not a hypothetical "some churn model somewhere."
- [x] Coupled-triad gap metric defined operationally (§5), not just referenced.
- [x] Portability + C-S1–C-S5 constraints applied at design time (§6-7).
- [x] Curriculum gates named for director sign-off before BUILD-open widens scope (§8).

**L1+ BUILD decomposition (epoch-gated, NOT opened by this FRAME — for the eventual BUILD pass):**
1. **B4-a (small):** add `CompetitorFieldObservation` dataclass + a `SimInterface.get_competitor_field()`
   method (stub returning the generalised-SVT reference today, real `W2_3` wiring once its own
   aggregate signal is exposed through the interface rather than imported directly).
   `file_scope: ["company/interfaces/sim_interface.py"]`
2. **B4-b (small):** generalise `RenewalPricingEngine.price_renewal()`'s SVT-only param to accept
   `observed_ceiling_gbp_per_mwh` from the observation (backward-compatible default keeps SVT behaviour
   if no observation supplied). `file_scope: ["company/pricing/renewal_pricing_engine.py"]`
3. **B4-c (small):** thread the premium term into one existing churn estimator
   (`company/crm/churn_model.py` or `enriched_churn_estimate.py` — BUILD-time pick, not decided here).
   `file_scope: ["company/crm/churn_model.py"]` or `["company/crm/enriched_churn_estimate.py"]`
4. **B4-d (medium, gated on `simulation/renewals.py` wiring):** the actual live call-site wiring —
   `simulation/renewals.py`'s `_route_pricing_move()`/`build_renewal_schedule()` currently take no
   competitor/svt/ceiling parameter at all (confirmed unchanged, three passes running); this is the
   step that makes the whole chain live in a real run, not just unit-testable in isolation.
   `file_scope: ["simulation/renewals.py"]`
5. **B4-e (harness, parallel to B4-d):** the gap-metric computation (§5) as a measurable harness
   artifact, reading both `W2_3` ground truth and the company's belief for the same as-of date.
   `file_scope: ["company/compliance/"]` (new module, naming TBD at BUILD time) — mirrors the existing
   `crisis_bad_debt_validator.py` pattern (harness-side honest-gap measurement, expected-failing until
   the mechanism closes it).

None of steps 1-5 are opened by this document — BUILD-open for this atom remains DIRECTOR_TWIN's call
per `EPOCH_GATING_AND_ATOM_AUTHORSHIP.md` §3a, and `W2_3` itself would need to reach the richer
per-rival L2+ state (§1) before B4-a's stub could be upgraded to a real multi-rival read without
re-violating the epistemic wall this FRAME just closed.
