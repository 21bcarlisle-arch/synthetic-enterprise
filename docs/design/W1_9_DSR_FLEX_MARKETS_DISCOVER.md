# W1_9_dsr_flex_markets — DISCOVER pass: demand-side response / flexibility markets

**Status:** DISCOVER-stage research only. NO SIM/COMPANY CODE CHANGED — atom is `epoch: 3`,
`loop_stage: idle`, so BUILD is gated; DISCOVER/FRAME is workable now per
`EPOCH_GATING_AND_ATOM_AUTHORSHIP.md`. This pass does not move `level_current` (stays 0).
File scope for this pass: `docs/design/` only.

## What was checked

Grepped `company/`, `sim/`, `simulation/` for `flex|DSR|demand-side|capacity market|aggregator|DFS|
balancing` before writing anything, per the standing instruction that DISCOVER passes on this
W1 cluster (see `W1_3_national_weather_signal`'s 2026-07-15 finding) have repeatedly turned up
**built-but-uncredited capability** against atoms registered `level_current: 0`/`provenance:
proposal`. Same pattern here, and it is large.

## Finding 1 — extensive company-side DSR/flexibility revenue modelling already exists

Nine modules in `company/market/`, ~1,300 lines, with fourteen matching test files, already wired
into a real simulation run path:

| Module | Covers |
|---|---|
| `capacity_market.py` | CM unit registration (CCGT/OCGT/battery/DSR/interconnector/pump storage), T-4/T-1 auction types, a `_CM_CLEARING_PRICE_GBP_PER_KW_PER_YEAR` table by delivery year 2016-2025 |
| `capacity_market_register.py` | CM obligation (levy on consumption) vs CM revenue (contracted flex) as a net position |
| `dsr_book.py` | DSR participant enrolment (contracted MW, status lifecycle) and dispatch result recording |
| `dsr_portfolio.py` | DSR event management — grid stress / frequency response / triad avoidance / capacity-market-dispatch / voluntary event types, curtailment compliance status |
| `flexibility_potential.py` | Screens the customer portfolio (EV/ASHP/battery flags) for flex kW potential and DFS/CM revenue eligibility |
| `flexibility_revenue_book.py` | Realises annual CM (2016+) and DFS (2022+) revenue per enrolled customer |
| `ic_flexibility_revenue.py` | I&C (industrial/commercial) demand-response enrolment via aggregators — process flexibility (chillers/compressors/HVAC), aggregator commission |
| `dso_flexibility_tender_register.py` | DNO/DSO **local** flexibility tender rounds and bids — peak avoidance, constraint management, voltage support, fault restoration, frequency response, keyed by `gsp_name` |
| `flexible_asset.py` | Battery/pump-storage dispatch intervals (charge/discharge/standby) with round-trip efficiency, SoC tracking, revenue realisation — docstring says "for BM and triad avoidance" |

Callers/consumers found: `company/pricing/ncc_forecast_register.py`, `company/regulatory/
remit_book.py`, and — importantly — `simulation/run_phase2b.py` (a live run path), plus
`tests/company/test_phase_jd_coverage_expansion.py`. This is not dead/orphaned code; it
participates in real simulation runs and dashboard/reporting flow already (`tests/saas/
test_phase_ny_flex_dashboard.py`, `tests/saas/reporting/test_phase_ag_flex_revenue.py`).

**This atom's own registration (`level_current: 0`, `provenance: proposal`, `evidence: [.../
WEATHER_PHYSICS_HIERARCHY.md]`) does not reflect any of the above** — same shape of gap as
W1_3's DISCOVER finding. Flagging, not self-fixing: per THREE_LANES / sole-map-writer discipline
this DISCOVER pass makes no `level_current` change and does not edit `maturity_map.yaml`; a
re-level is the orchestrator/director's call, informed by the gap analysis below (the build is
real but the *specific target this atom names* is not the same thing as the accounting modules
that exist — see Finding 2).

## Finding 2 — what's built is company-side REVENUE ACCOUNTING on ASSUMED constants, not a SIM-side market

Reading past the module list to what each one actually *does*: every rate, every event count, and
every dispatch cadence is a **hardcoded constant**, not an output of any world/SIM process:

- `_DFS_RATE_GBP_PER_MWH = 4.5` and `_DISPATCH_EVENTS_PER_YR = 20` (`flexibility_potential.py`,
  `ic_flexibility_revenue.py`) — DFS is assumed to deliver exactly 20 evenly-distributed winter
  events every year at one flat rate. No linkage to any actual system-stress or price-spike signal.
- `_CM_CLEARING_PRICE_GBP_PER_KW_PER_YEAR` (`capacity_market.py`) is a fixed lookup table by
  calendar year — reasonable as a stand-in for real published T-4/T-1 clearing prices, but it is
  *read*, never *derived* from anything the SIM produces.
- `DSOFlexibilityTenderRegister` (`dso_flexibility_tender_register.py`) has a full tender/bid
  lifecycle (open → close → award, submit → accept/reject) but tenders are created by direct
  method calls with a caller-supplied `capacity_required_mw` and `gsp_name` string — there is no
  underlying model of *why* a DNO would need that MW at that location (i.e., no regional network
  constraint physics to originate a genuine tender from).
- `FlexibleAsset.dispatch()` (`flexible_asset.py`) takes `price_gbp_per_mwh` as a bare argument
  from the caller — there's no BM bid-offer stack, no imbalance/system-price mechanism generating
  that number; it's supplied by whatever test or run script calls it.

**Confirmed via `company/interfaces/sim_interface.py`: zero mentions of flex/DSR/capacity-market
anywhere in the SIM/company seam.** Nothing in any of the above nine modules is discovered by the
company through an observable world interface the way meter reads or market price feeds are —
it's company-authored constants applied directly. That is the real gap against this atom's own
lane (`W1_market_weather`, i.e. a *world* capability) and against the epistemic wall's own
standard ("could a real UK supplier know this, or is it a fact the code was simply handed?").
Right now the honest answer is: handed, not discovered.

This also explains the `depends_on: [W1_6_physics_price_signal]` in the map entry, which is
physically correct even though W1_6 is itself unbuilt (`level_current: 0`): in reality, DSR/DFS/
BM dispatch frequency and price is *driven by* system tightness — the same cold-and-still,
low-margin conditions that W1_3/W1_6 are trying to model mechanistically, not a flat calendar
rate. Building this atom before W1_6 exists would mean hardcoding the exact assumption
(independent, non-stress-linked event rate) that the physics-hierarchy work is meant to replace.

## Real UK DSR/flexibility market structure (grounding; figures below are structural/qualitative
unless stated as already-embedded-and-cited in code — this DISCOVER pass had no live network
access to independently re-verify point figures against NESO/Elexon/Ofgem publications this
session; anything not already cited in existing code comments is flagged **UNVERIFIED**)

1. **Balancing Mechanism (BM).** Run by NESO (National Energy System Operator; took over the
   system-operator function previously badged National Grid ESO). Real-time balancing via
   Bid-Offer Acceptances (BOAs) issued to registered BM Units, gate closure roughly one hour
   ahead of each half-hour settlement period. Historically the preserve of large generators/
   suppliers with registered BMUs; access reforms over the 2017-2021 period (BSC modification
   process) progressively opened participation to smaller flexibility providers and independent
   (non-supplier) aggregators. Settlement/BM data (Bid-Offer Data, BOALF, system/imbalance
   price) is published via Elexon's Insights Solution — the same data family this repo already
   ingests for wholesale settlement, which is the natural real-world anchor if this atom is ever
   built (an *independent* validator anchor per the anti-marking-own-homework rule, distinct
   from whatever generates the SIM's own price series).
2. **Ancillary/frequency response services.** Firm Frequency Response (FFR) historically, with
   Dynamic Containment / Dynamic Moderation / Dynamic Regulation products introduced ~2020-21;
   battery storage is a heavy participant. Not represented in any module found above beyond the
   bare `FrequencyResponse` enum value in `dsr_portfolio.py`/`DSOFlexibilityTenderRegister`.
3. **Capacity Market (CM).** Electricity Market Reform (2014) mechanism; T-4 (four-years-ahead)
   and T-1 (one-year-ahead top-up) auctions. DSR/battery participate as Capacity Market Units,
   commonly pooled by aggregators to clear minimum size thresholds; DSR typically carries a lower
   de-rating factor than firm thermal generation, reflecting delivery-risk uncertainty
   (**UNVERIFIED** precise de-rating figures — not present in code, not checked this session).
   The existing `_CM_CLEARING_PRICE_GBP_PER_KW_PER_YEAR` table's individual year values are
   **UNVERIFIED** against the actual published T-4/T-1 auction results this session — worth an
   independent discovery-agent pass against NESO's published auction reports before this atom's
   BUILD stage, since the code comments assert them as real without a citation.
4. **NESO Demand Flexibility Service (DFS).** Voluntary domestic/small-business turn-down scheme,
   first live-tested winter 2022/23 in response to 2022 security-of-supply concerns; has
   continued in subsequent winters. **UNVERIFIED / genuinely uncertain, flag explicitly**: whether
   DFS continues as a standing annual scheme going forward is a live policy question, not a
   settled multi-decade mechanism — a SIM-side model should represent it as a *dateable, possibly
   discontinued* scheme (matching `domain_invariants.py`'s `effective_from`/`effective_to`
   convention), not bake in "20 events/year forever" as the current code does. The code's
   `_DFS_RATE_GBP_PER_MWH = 4.5` average and `_DISPATCH_EVENTS_PER_YR = 20` are also
   **UNVERIFIED** this session against NESO's own published DFS settlement reports (which show
   materially different average clearing prices across individual events — some public reporting
   describes wide event-to-event variance, not a flat rate); recommend a discovery-agent pass.
5. **DNO/DSO local flexibility markets.** Distribution Network Operators, transitioning toward a
   Distribution System Operator role under Ofgem/ENA's Open Networks Programme, run **locational**
   flexibility tenders (peak avoidance, constraint management, voltage support) at individual Grid
   Supply Points/primary substations — several DNOs use or have used a shared marketplace platform
   (**UNVERIFIED** which specific platform names are current) rather than one national clearing
   price. This is structurally what `dso_flexibility_tender_register.py` models (correctly, as a
   per-GSP tender/bid register) — the gap is that nothing originates a *real* tender from network
   conditions; it's caller-driven today.
6. **Aggregator route.** Both licensed suppliers and independent (licence-exempt) aggregators pool
   small/behind-meter flexible assets to meet BM/CM/DFS/DSO minimum bid sizes. Ofgem access reforms
   (from ~2018) progressively enabled independent aggregator access to the Balancing Mechanism
   without requiring the customer's own supplier's sign-off — relevant because `ic_flexibility_
   revenue.py`'s `_AGGREGATOR_FEE_PCT = 0.20` models the company routing I&C customers through an
   aggregator rather than bidding directly; the 20% figure is **UNVERIFIED** this session.
7. **Triad avoidance and its decline.** Historically, avoiding the three winter system-peak
   half-hours minimised a customer's TNUoS (transmission) charge — a real economic driver behind
   battery/DSR dispatch timing (`is_evening_peak` in `flexible_asset.py` gestures at this).
   Ofgem's Targeted Charging Review has been moving transmission residual charges toward a fixed
   basis, structurally reducing the future value of pure triad-avoidance behaviour
   (**UNVERIFIED** current implementation timeline/status) — a SIM/company model that treats
   triad avoidance as a permanent, undiminishing revenue stream would be building in a fact that
   is actively changing in the real regime; worth a time-indexed treatment if this is built.

## What the SIM/world layer would concretely need to ADD (not built now — Epoch 3, BUILD-gated)

Given Finding 2, the genuine remaining scope for this atom is **not** "build DSR/flex market
accounting" (that exists) but specifically:

- **A. A system-stress signal the company discovers, not is handed.** Extend the SIM/company seam
  (`company/interfaces/sim_interface.py`) with an observable — e.g. a residual-demand-margin or
  price-spike-severity feed — that DFS/BM dispatch probability and DSO tender frequency can key
  off, replacing the flat `_DISPATCH_EVENTS_PER_YR` constant. This is the natural consumer of
  W1_6's derived price signal once that exists — cold-and-still conditions (W1_3) → tight margin →
  price spike (W1_6) → DSR/DFS dispatch trigger, one coherent causal chain instead of an
  independent calendar draw.
- **B. Locational grounding for DSO tenders.** Tie `capacity_required_mw`/`gsp_name` tender
  creation to whatever regional weather/demand field W1_4 eventually produces, so a tender exists
  because a *modelled* regional constraint exists, not because a test/run script invented one.
- **C. Stress-responsive price formation**, at least qualitatively — real DFS/BM prices can be an
  order of magnitude above baseline during genuine tight periods; a flat per-event rate can't
  represent that, and currently doesn't try to.
- **D. Time-indexed scheme lifecycle** for DFS specifically (dateable start, no assumed
  indefinite continuation) per the regulation-commons doctrine's `effective_from`/`effective_to`
  convention already used in `domain_invariants.py`.

None of A-D is greenfield in the sense of "no code exists" — they are extensions/rewirings of the
nine already-built modules to receive a SIM-originated signal instead of a caller-supplied
constant. The company-side accounting, enrolment, and revenue-realisation logic in those nine
modules looks like it would mostly survive unchanged; what's missing is the upstream signal.

## Open questions (explicit, for the record — not resolved by this pass)

1. Should the re-level conversation (Finding 1) treat this atom as "L1/L2 already reached" on the
   strength of the existing accounting modules, with L3 reserved for the stress-linkage in
   Finding 2 — or is "discovered vs handed" (Finding 2) itself the bar for *any* level above 0
   under this project's epistemic-honesty standard? This DISCOVER pass surfaces the question,
   doesn't answer it (level changes are not this pass's call).
2. Every UNVERIFIED figure flagged above (DFS rate/event count, CM clearing-price table, 20%
   aggregator fee, current DNO flexibility platform names, TCR/triad reform timeline, CM DSR
   de-rating factors) should get a `discovery-agent` pass against a primary published source
   (NESO DFS settlement reports, NESO/EMR Delivery Body CM auction results, Ofgem TCR decision
   documents, Elexon Insights Solution) before any BUILD work leans on them as calibration inputs.
3. Whether DFS should be modelled as possibly-discontinued (per its short, policy-contingent
   real history) is a director-level curriculum question (R13's baseline/curriculum split) as
   much as a technical one — the *baseline* fact of "DFS existed 2022-currently, uncertain
   continuation" is fidelity-to-reality and belongs on the baseline side; whether/when the
   *company* correctly anticipates a scheme ending is squarely a company-capability test (COUPLED
   TRIAD — the world can defeat a company that over-relies on it).

## Evidence for this pass

- `company/market/{capacity_market,capacity_market_register,dsr_book,dsr_portfolio,
  flexibility_potential,flexibility_revenue_book,ic_flexibility_revenue,
  dso_flexibility_tender_register,flexible_asset}.py` — read directly, this session.
- `company/interfaces/sim_interface.py` — checked directly for flex/DSR mentions (none found).
- Fourteen matching test files under `tests/company/market/`, `tests/company/regulatory/`,
  `tests/company/`, `tests/saas/`, `tests/saas/reporting/`, `tests/simulation/` (listed by name
  in Finding 1's table context; not individually re-read line-by-line this pass).
- `simulation/run_phase2b.py` confirmed as a live caller via grep.
- `docs/design/maturity_map.yaml` entries for `W1_9_dsr_flex_markets`, `W1_6_physics_price_signal`,
  `W1_3_national_weather_signal` — read, not edited (file_scope for this pass is `docs/design/`
  minus the map itself, per task scope).
