# W1 — The COUPLED WEATHER CASCADE (DISCOVER pass, doc-only)

**Status:** DISCOVER, doc-only. Writes **no** `sim/`/`company/`/`harness/` code, edits neither
`maturity_map.yaml` nor any engine, touches only `docs/design/`. Scope is the **coupled cascade** —
how one weather regime propagates as *correlated* shocks through the whole chain
`weather → demand → renewable output → residual demand → price → settlement → company exposure` —
distinct from the per-atom W1 DISCOVER/FRAME passes which model each link in isolation. It is
world/SIM-side framing only; §3 states what the company observes (downstream observables), never the
weather driver. W1 BUILD stays CLOSED (Epoch-3 BUILD-gated per EPOCH_GATING_AND_ATOM_AUTHORSHIP Rule 1);
this is Lane-3 DISCOVER on a parked cluster, allowed now.

**Relationship to the authoritative designs (consolidates, does not re-derive).**
`docs/design/WEATHER_PHYSICS_HIERARCHY_DESIGN.md` §1.4 is authoritative for the L4 five-equation chain
(weather→demand→wind/solar→residual→merit-order price) and states the *crux* — wind, solar and demand
are all functions of the **same** L1 weather draw, so the coherence is structural, not fitted.
`W1_3_NATIONAL_WEATHER_JOINT_REGIME_DISCOVER.md` supplies the measured **entry shock** to the cascade
(the winter cold∧still joint-tail lift: decile **2.34×**, winter temp/wind corr **+0.507**, multi-day
persistence). The individual W1_5 (demand), W1_6 (price), W1_7 (renewable-capacity trend) FRAMEs own
each link's mechanism and its own invariant. **This doc owns the thing none of them own: the
end-to-end *compounding* of correlation down the chain, the single cascade gap the harness measures,
and the cross-link cascade invariant.** Where it cites a number it is a directional anchor from the
committed record or a repo-grounded structural argument; anything resting on the price engine's
calibration is flagged, because that engine already failed its SSP gate (W1_6 FRAME §1) — the cascade's
*direction* is robust to that, its *magnitude* is not.

---

## 0. Repo grounding — the cascade is already half-wired, and where it breaks

- **The chain equations exist** (`WEATHER_PHYSICS_HIERARCHY_DESIGN.md` §1.4, eqs 1–5): national weather
  `X(t)` → `D_national = f_demand(T, day_type, season)` → `G_wind = capacity_wind·power_curve(W)`,
  `G_solar = capacity_solar·clearsky·(1−cloud)` → `RD = D − G_wind − G_solar` → `P =
  gas_floor·(RD/dispatchable_margin)^γ`. The turbine power curve (cut-in 3 m/s, cubic ramp to rated at
  12 m/s) and the merit-order engine (`sim/price_engine.py`) are real code.
- **The couplings are NOT yet all live.** Today (per the FRAMEs): W1_3's regime trigger keys on
  **wind-residual alone**, not the joint cold∧still condition (so the entry shock is under-populated);
  demand, wind and price are in places **separately sourced** rather than all-descendants-of-one-draw
  (§1.4's own "replacing today's separately-sourced demand/renewable series" admission); and
  `sim/price_engine.py` **failed its SSP calibration ~10×** and was superseded (W1_6 FRAME §1). So the
  cascade is a *design target with a real precursor*, not a working pipeline — exactly the state that
  makes a DISCOVER pass on its coupling worthwhile before BUILD.
- **The coupled-triad plumbing exists** (`background/coupled_triad.py`, `coupled_gap_ledger.json`, the
  Proof-door `_coupled_gaps` panel) but `_AUTHORITATIVE_COUPLING` currently registers only the W2
  affordability cluster + `W2_11↔D5`. **No weather-cascade pair is registered** — the gap this doc names
  has no ledger entry yet; that wiring is a BUILD act (§6).

---

## 1. The cascade chain, explicit — each link, its coupling, where correlation compounds

The cascade is one weather regime hitting **every** link at once, in the **same direction**, for
**several days**. Read top to bottom; the right column is the load-bearing part — *what couples this
link to the driver, and whether the coupling adds to or amplifies the tail*.

| # | Link | Mechanism (repo) | What couples it to the weather regime — and the compounding |
|---|---|---|---|
| A | **Weather regime** (national + regional joint tail) | W1_3 national `X(t)`; W1_4 regional field `X_r(t)` | The **entry shock**. Cold∧still is a *joint* winter tail — measured **2.34×** fatter than independent (W1_3 §1.2). Regionally it is worse where it matters: a blocking high hits the Scotland/North-Sea wind fleet harder than a 4-point national mean (W1_3 §5.1), and a book concentrated in a cold region takes more than the national-average hit (W1_4). |
| B | **National demand** ↑ | `D = f_demand(T, day_type, season)`, convex-below-threshold heating | Demand rises because temp is in the **cold** tail. Same driver as A — not an independent demand shock. Persistence (A's 2–7 day spells) makes it a *sustained* demand plateau, not a spike that mean-reverts overnight. |
| C | **Renewable output** ↓ | `G_wind = cap·power_curve(W)`; `G_solar = cap·clearsky·(1−cloud)` | Wind gen collapses because wind is in the **still** tail — the *same* weather event as B. The power curve is **convex** near cut-in: below ~5 m/s a small wind drop is a large output drop (cubic ramp), so the "still" tail translates to an *amplified* generation tail. Blocking-high cloud can also suppress solar. **B and C move in opposite MW directions but the SAME residual direction.** |
| D | **Residual demand** ↑↑ | `RD = D − G_wind − G_solar` | **First compounding point.** `RD` = (a term that rises in cold) − (a term that falls in still). Because cold and still co-occur (corr +0.507 in winter), both moves push `RD` **up together**. `RD`'s upper tail is therefore fatter than either `D`'s tail or `(−G_wind)`'s tail alone, **and fatter than if D and G_wind were independent** — the additive combination of two positively-tail-dependent terms. This is where W1_3's weather-only 2.34× stops being "a weather statistic" and becomes a *system-tightness* statistic. |
| E | **Wholesale price** ↑↑↑ | `P = gas_floor·(RD/dispatchable_margin)^γ`, γ≈1.5–2.5 | **Second compounding point — convex amplification.** Price is a **convex power** of the tightness ratio `RD/margin`. A fat-tailed `RD` pushed through `(·)^γ` produces a *fatter-still* price tail: roughly, a proportional move in `RD` near full dispatch produces a ~γ× proportional move in `P` (and the margin denominator *shrinks* exactly when `RD` peaks, so the ratio moves more than `RD` alone). The cold∧still corner is where the price spike **mechanistically appears without being drawn** (§1.4's proof-of-closure). |
| F | **Settlement / imbalance** ↑↑↑ | System Sell/Buy price, cash-out on the company's imbalance volume | The company is **short** in exactly this regime (its metered book consumed more than its hedged/forecast position, because demand plateaued high) **at the same time** as cash-out prices spike (E). Volume-error and price-error are **positively correlated** — the classic imbalance double-hit: you are most short when being short is most expensive. Persistence means this recurs each settlement period across a multi-day spell, compounding the cash drain. |
| G | **Company hedge / capital exposure** | hedge book P&L, VaR, capital buffer draw | Terminal link. A hedge sized for *independent* demand and price risk is under-hedged against the *joint* tail; the residual open position is realised at spiked prices → capital drawdown. Because the shock persists (A), a buffer sized for a one-period stress is drained over a multi-period one. **This is the £ the cascade actually costs.** |

**The one-line physics:** a single blocking-high winter regime is *not* one shock to one variable — it is
a **correlated multi-shock** that moves demand up, wind down, residual up-up, price up-up-up, and
imbalance up-up-up, **simultaneously and for days**, because every link reads the same upstream weather
draw. The correlation does not merely *survive* the chain; it **compounds** at D (additive co-movement)
and again at E (convex amplification), then persists across F.

---

## 2. The compounding-correlation insight — the cascade's joint tail is fatter than the product of marginals

**The core thesis, chained.** W1_3 proved that modelling temperature and wind *independently* under-populates
the supplier-killing corner by ~half to two-thirds (2.34× decile lift). The cascade insight is that this is
the **first** of several compounding steps, not the whole error:

1. **At the weather entry (A):** joint cold∧still lift ≈ **2.34×** vs independent (measured, W1_3 §1.2,
   4-point proxy — a plausible *lower* bound; capacity-weighted GB output concentrates wind geographically,
   so the true lift is likely ≥ this).
2. **At residual demand (D):** two positively-tail-dependent terms are **added** (D↑, −G_wind↑). The
   residual's upper-tail lift over "D and G_wind drawn from independently-fit marginals" is *at least* the
   weather lift and generally larger, because the power curve's convexity near cut-in **stretches** the
   wind term's tail before it is added. Directional, not yet quantified — the exact residual lift needs the
   capacity-weighted series + the fitted `f_demand` (BUILD).
3. **At price (E):** a convex transform `(·)^γ` of a fat-tailed input yields a fatter-tailed output. For
   γ≈2 a proportional tail move in the tightness ratio roughly **squares** into the price tail; the
   shrinking margin denominator adds to this. So the *price*-corner mass in cold∧still is amplified again
   over the residual-corner mass.
4. **At imbalance (F):** volume-short and price-high are positively correlated, so the *cost* (volume ×
   price) has a tail fatter than the product of the volume tail and the price tail — a third compounding.

**Net:** model each link's marginal behaviour independently and you **under-state the terminal (capital)
tail by a factor that is the *product* of the per-link lifts, not any single one of them.** The honest,
repo-grounded claim is directional and strong: the cascade's end-to-end joint tail is **materially fatter
than the product of independently-fit marginals**, with the weather entry (2.34×) the only link currently
measured and the residual/price/imbalance amplifications argued structurally (convex power curve, convex
merit-order γ, positively-correlated cash-out) pending BUILD calibration. **Quantifying the end-to-end
multiplier is the single biggest BUILD measurement (§6.1)** — and R12 binds: it is a *diagnostic to
surface*, never a target to tune.

*(Caveat carried forward: the price engine's γ is currently mis-calibrated ~10× (W1_6 FRAME §1). That
breaks the **magnitude** of link E, not its **direction** — convexity amplifies the tail whatever the
calibrated γ. The cascade invariant (§4) is written on tail-dependence *shape*, which survives a wrong γ;
the *level* of the price spike is explicitly a BUILD calibration output, not asserted here.)*

---

## 3. The coupled-triad framing — the GAP (the company sees downstream, never the driver)

**The wall, kept.** The company never reads the SIM weather engine, the regime label, `f_demand`, the
power curve, γ, or the residual calc. Per the epistemic wall it observes only **downstream consequences**:
its own metered book volume, the published wholesale/imbalance (SSP/SBP) prices it is charged, published
weather outturns/forecasts a real supplier could buy, its own bills and settlement. It sees the cascade's
**exhaust** (prices, volumes, cash-out), not its **driver** (the correlated weather regime).

**What the company MISbelieves (the gap).** A real supplier — and the company, allowed to be wrong —
that calibrates demand risk and price risk **separately**, or on data pooled across seasons (where the
temp/wind coupling washes to ≈0, W1_3 §1.3), sees demand shocks and price shocks as **two independent
noise sources**. During a cascade it therefore MIS-attributes a *single correlated weather driver* to
*independent* volume and price noise, **under-hedges the joint tail** (hedges the marginals, misses their
co-movement), and takes a capital hit when the correlation it didn't price shows up all at once. It is
structurally blind to the compounding of §2 because the compounding lives **upstream of the wall**.

**The candidate gap metric — the cascade co-movement gap.** Per COUPLED_TRIAD (gap = realised truth vs
belief, normalised to a no-skill baseline):

> **`gap_cascade` = |VaR_realised − VaR_believed| / VaR_believed**, where `VaR_believed` is the company's
> pre-spell tail-loss expectation on its hedge+imbalance book computed under its **observable-only,
> marginals-independent** model of (demand, price), and `VaR_realised` is the SIM's actual tail loss over
> an **injected cold∧still cascade spell** (harness reads the SIM ground-truth cascade; the company never
> does). Equivalently reported as a **co-movement gap**: `corr_realised(book-short-volume, cash-out-price)`
> in the joint tail minus the company's **assumed** correlation (≈0 for a marginals-independent model).

Reading (COUPLED_TRIAD convention): `gap→0` = company fully priced the cascade correlation (structurally
near-unreachable through the wall — reaching it means an observable leaked the weather driver, a wall
defect not a triumph); `gap→1` = no better than a blind marginals-independent hedge; `0<gap<1` = the
company learned *some* of the co-movement (the honest steady state). **Trend is the story:** a company
whose cascade gap **falls** over successive injected spells is learning to hedge the joint tail; a
**static** gap is the finding "not adapting to correlated weather risk." Per COUPLED_TRIAD's binding rule,
**no W1 world atom in the cascade reaches L3 until this gap has been measured against an injected spell** —
the cascade is the archetypal weather-cluster coupled pair, and its natural company twin is the
demand-forecast + hedge/capital-posture capability (the W1_3 gap already names this; C13 owns the
weather-normalisation sub-part).

---

## 4. Candidate INVARIANT(s) — cross-link tail dependence (R10 class-failing, R15-failable, no code)

The generated cascade must **preserve and compound** cross-link tail dependence end-to-end. Stated as
testable invariants in the R10 library style (each fails a *class*, not an instance):

> **INVARIANT W1-CASC1 (cross-link tail dependence is non-vanishing along the whole chain).**
> Over a generated multi-year run, restricted to the winter joint cold∧still corner (temp ≤ winter-p10 ∧
> wind ≤ winter-p10, per W1_3), the tail dependence must hold at **every** link, not just the weather
> entry: `corr(residual_demand, price)` in the joint tail ≥ `ρ_min`, **and** the corner must carry
> co-moving demand-up ∧ gen-down ∧ residual-up ∧ price-up (sign-consistent, per-period). A run whose price
> tail is *decoupled* from its residual tail (price high in cold∧still by luck, not by mechanism) fails.

> **INVARIANT W1-CASC2 (the cascade joint-tail lift ≥ the product-of-marginals — compounding does not wash
> out).** Let `L_end` = the end-to-end joint-tail lift of the terminal quantity (imbalance cost, or price)
> in the cold∧still corner vs the same corner under **independently-fit marginals** (demand, wind, price
> each drawn from its own fitted marginal with cross-coupling removed). Then `L_end ≥ L_A` (the weather
> entry lift, directional anchor 2.34×) — i.e. the chain **amplifies** the tail, it must not *thin* it.
> A `L_min` floor is a stated, real-data-anchored constant (BUILD-calibrated against the capacity-weighted
> series + real SSP), never a difficulty dial (R13).

> **INVARIANT W1-CASC3 (persistence propagates — the spell is multi-day at every link).** The
> consecutive-day spell length of the *terminal* stress (price/imbalance above its own tail threshold)
> must track the weather-entry spell distribution (W1_3 §1.4: mean ≈ 2 d, max ≥ ~5 d) — the cascade must
> not collapse a 5-day weather spell into a one-period price spike. A memoryless price tail fails.

**R15 — the invariant must be able to FAIL (mutation direction, designed not coded):**
- **The killer mutation is "break one link's coupling."** Replace `G_wind = cap·power_curve(W)` with an
  **independent** wind draw (or draw price independently of `RD`, or draw demand independently of `T`, or
  decouple the regional field from the national regime). W1-CASC1/CASC2 **must fire**: the corner's
  cross-link correlation drops toward 0 and `L_end` collapses toward 1.0 (or below). This is the direct
  mechanised guard against the exact regression the whole atom exists to prevent — a code path that samples
  any downstream variable independently of the weather driver (§1.4's forbidden anti-pattern).
- **TAUTOLOGY guard:** the checker must recompute the corner masses / correlations **independently** from
  the generated series and compare against an **independent** anchor (the historical weather record; the
  BUILD capacity-weighted GB output series; real SSP) — never read back a stored "designed lift/correlation"
  parameter, which would always pass.
- **FAIL-OPEN guard:** an empty winter subset, an all-equal series, a NaN, or a zero-margin division must
  **fail loud**, never pass on a degenerate run.
- **FAIL-SILENT guard:** if the real-record anchor or the generated series is unavailable, the check is a
  **FAILED** check, never skipped-and-green (an unavailable check is a failed check).

These sit *above* the per-link invariants (W1_3-JT1 weather, W1_5-I2 demand reconciliation, W1_6 price-is-
derived, W1_7 outturn-consistency) — those guard each link; **W1-CASC1/2/3 guard the *seams between*
them**, which no single-atom invariant covers. The cascade is exactly where "each link is individually
correct but the chain is decoupled" hides, so it needs its own cross-link control.

---

## 5. Wall / curriculum (R13) + portability (C-S)

- **R13 — the cascade PHYSICS is baseline; the SEVERITY/scenario is director curriculum.** The
  *existence, sign, shape and compounding* of the cascade — that cold co-occurs with still, that residual
  and price co-move in the joint tail, that the tail compounds down the chain and persists for days — is
  **baseline**: calibrated to reality, decided **blind to company P&L**, changed only for fidelity reasons
  (R12/R13). If the company loses money in a faithfully-severe cascade winter, that is a **finding**, never
  a licence to soften any link. **Which** cascade the company lives through — "a 2010-style two-week
  February blocking high", a stress ensemble of back-to-back dunkelflaute spells — is **director-authored,
  named, versioned curriculum**, never silent parameter drift and never agent-tuned toward a gap number.
  The generator supplies the *capability* to run a severe cascade faithfully; the director chooses the
  *diet*. `L_min`, `ρ_min` and the spell floors are baseline-fidelity constants, **not** difficulty dials.
  Note the double wall: the agent controls both the SIM (that makes the cascade) and the company (that
  copes) — so the cascade *severity* must face the director, exactly because the agent could otherwise tune
  both sides.
- **Portability — percentile-keyed, no hardcoded GB constants.** Every corner threshold is a **tail
  quantile of the realised winter distribution** (winter-p10 temp/wind), so a second geography or a
  shifted-climate future world re-derives its own cold∧still corner without hardcoded °C/m/s. "Winter =
  DJF" is a Northern-Hemisphere convention → the cold-season months are a configurable parameter
  (portability debt if hardcoded). The cascade is keyed by *function* (weather→demand→gen→residual→price),
  not by GB fuel names, so a second market's fleet/tariff fits behind the same seam.
- **C-S2 — per-substream RNG + deterministic replay (load-bearing for the cascade specifically).** Each
  stochastic link draws from its **own named, seeded substream** (`national_regime`, `regional_field`,
  `premise_noise`, `price`, per the hierarchy design §7) — the 01:09Z shared-RNG lesson. This is what lets
  the cascade be **replayed identically**: the injected cold∧still spell (§3) and the end-to-end
  tail-lift measurement (§4) are only reproducible if adding/altering a draw in one link cannot shift
  another link's path. Critically, the cascade's *coupling* must live in the **deterministic** structure
  (each link a function of the shared weather draw), **not** in a shared RNG stream — coupling-via-shared-
  RNG is the anti-pattern C-S2 forbids and would make the tail dependence an untestable side effect.
- **C-S5 — time-scale invariance declaration.** The cascade statistics here are **daily** (joint-tail
  corner, spell length, autocorrelation). The daily-regime → half-hourly-diurnal coupling (heating shape,
  solar clear-sky, settlement period) is **not** fully time-scale invariant; any L3 claim must register it
  as a named simplification (R10). The cascade invariant is stated on the daily series and must declare
  that basis.

---

## 6. Open questions / what BUILD needs (unresolvable without network or a director call)

1. **The end-to-end tail multiplier (biggest measurement).** §2 argues the cascade compounds the 2.34×
   weather lift through residual (additive co-movement) and price (convex γ) into a materially fatter
   terminal tail, but the *number* needs: the capacity-weighted GB wind-output series (not the 4-point
   proxy), the fitted `f_demand`, and a **recalibrated** price engine (the current one fails SSP ~10×,
   W1_6 FRAME §1). Requires a real data pull (no network in this fork) and the W1_6 recalibration to land
   first. The direction is robust; the magnitude is a BUILD output, reported not tuned (R12).
2. **Price-engine calibration is a hard upstream blocker for link E's magnitude.** The cascade's *price/
   imbalance* tail cannot be trusted until `sim/price_engine.py` passes its SSP gate with the residual-
   demand/dispatchable-margin ratio form (W1_6 FRAME §3.1). Until then the cascade invariant is asserted
   on tail-dependence *shape* (γ-robust), and the price-spike *level* is flagged provisional.
3. **`ρ_min` / `L_min` / spell floors — a calibration + values call.** The exact cross-link correlation
   floor, end-to-end lift floor, and spell-length tolerances are BUILD calibration decisions against the
   capacity-weighted series + real SSP; whether any is a promotion *gate* is the director/twin's BUILD-open
   call (Epoch 3). They are baseline-fidelity constants (R13), not difficulty dials.
4. **Which company twin(s) the cascade couples to, and registering the pair.** The natural twin is the
   demand-forecast + hedge/capital-posture capability; C13 owns the weather-normalisation sub-part. BUILD
   must register the cascade pair(s) in `background/coupled_triad.py::_AUTHORITATIVE_COUPLING` (currently
   **no** weather-cascade entry) and add a `coupled_gap_ledger.json` row so the Proof-door panel renders
   it. Whether the gap is asserted at national level only or also propagated as a **regional-basis** stress
   (W1_4) and a **zonal/locational** price stress (W1_8) is a cross-atom sequencing question for the
   orchestrator, not resolved here.
5. **Injected-spell design (the harness scenario).** The gap (§3) needs a *named* injected cold∧still
   cascade spell to measure against — its severity/duration is **director curriculum** (R13), not an
   agent-chosen stress. BUILD needs the director's first named cascade scenario (or a default "faithful
   worst historical spell" pulled from the record) before the gap can be scored.
6. **External anchors (recall — verify at BUILD).** NESO's loss-of-load-expectation / capacity-market
   "low wind + cold" stress characterisations and documented GB winter blocking-high events are the natural
   **independent** validator anchors for the cascade tail (anti-marking-own-homework: fit on the weather/
   output record, validate on independent published stress-period statistics). Cited from **recall only —
   flag: verify against primary source at BUILD** (no network here; Historical Ground Truth forbids
   fabricating a specific date/figure in a DISCOVER doc).

---

*Sources (all read/computed this pass, no network): `docs/design/WEATHER_PHYSICS_HIERARCHY_DESIGN.md`
§1.4 (the L4 five-equation cascade chain, the same-weather-draw crux, the cold-still→spike proof-of-closure
+ forbidden independent-draw anti-pattern — read directly, not re-derived); `docs/design/
W1_3_NATIONAL_WEATHER_JOINT_REGIME_DISCOVER.md` (the measured entry shock: 2.34× decile lift, +0.507 winter
corr, 2–7 day persistence); `docs/design/frame/W1_5_premise_demand_shape_FRAME.md` (link B, the demand
decomposition + I2 reconciliation), `W1_6_physics_price_signal_FRAME.md` (links D/E, residual-demand/
margin ratio, the ~10× SSP calibration failure + R13 baseline/curriculum split), `W1_7_renewable_capacity_
trends_FRAME.md` (link C, time-varying capacity); `docs/design/COUPLED_TRIAD_DESIGN.md` (the gap-metric
family, normalisation to no-skill baseline, digest + Proof-door reporting); `background/coupled_triad.py`
(`_AUTHORITATIVE_COUPLING` — confirmed no weather-cascade pair registered yet). External NESO/blocking-high
characterisations in §6.6 are **recall only, flagged for BUILD-time verification**. R10/R12/R13/R15,
COUPLED_TRIAD, C-S2/C-S5, Historical Ground Truth, and the epistemic wall referenced inline.*
