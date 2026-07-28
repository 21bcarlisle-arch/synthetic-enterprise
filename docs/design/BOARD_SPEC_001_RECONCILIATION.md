# BOARD SPEC 001 — WHOLESALE & TRADING FUNCTION — line-by-line reconciliation

**What this is.** A line-by-line reconciliation of every scoreable expectation in *BOARD SPECIFICATION 001 —
The wholesale and trading function of a competent mid-size GB domestic supplier*
(`docs/staging/in_progress/BOARD_SPEC_001_WHOLESALE_TRADING_2026-07-22.md`, verbatim blind practitioner
spec) against **(a)** the trading/hedging/collateral machinery as actually built (`sim/hedging_strategy.py`,
`company/trading/*`, `company/market/*`, `company/finance/margin_call_book.py`,
`company/risk/collateral_death_test.py`, `company/pricing/ofgem_price_cap.py`, `company/crm/churn_model.py`,
read this session, 2026-07-28) and **(b)** the WHOLESALE_VALUE_CHAIN steer's planned scope
(`docs/staging/in_progress/DIRECTOR_STEER_WHOLESALE_VALUE_CHAIN_2026-07-22.md`,
`docs/design/WHOLESALE_VALUE_CHAIN_FRAME.md`). This is the **desk that trades** prices — distinct from
`docs/design/BOARD_SPEC_004_RECONCILIATION.md` (the *machinery that makes* the prices); where the two
converge — above all gas-first — the row cites it. Format matches BOARD_SPEC_004/002/005 (id / board_text /
reconciles_to / verdict / evidence / notes rows, section scorelines, a battery table, Director Findings,
summary scoreline).

**Genealogy — this supersedes-by-reformat, not by re-analysis.** A prior reconciliation
(`docs/design/WHOLESALE_TRADING_BOARD_RECONCILIATION_2026-07-22.md`, 2026-07-22) already walked this spec
in full; that analysis is the foundation here. This file (a) re-shapes it into the six specs' common
tabular format (the gap the planner mint named: `BOARD_SPEC_001_RECONCILIATION.md` did not exist under the
naming convention `BOARD_SPEC_00N_RECONCILIATION.md` the other five specs use), and (b) **re-verifies every
citation against the live tree six days later** — one material change was found: the collateral/cash loop
(board §3.6/§7.4) that the 2026-07-22 pass found *unwired* has since been wired
(`company/finance/margin_call_book.py::build_margin_calls_from_mtm`, `company/risk/collateral_death_test.py`,
landed 2026-07-25 under `DIRECTOR_RULING_MC2_REAL_HISTORY_NOT_DIFFICULTY_2026-07-25`). Verdicts below reflect
the current build, not the 2026-07-22 snapshot; where they differ from the prior doc, that is stated.

**Provenance.** proposal · DISCOVER → doc-only · **no level claimed**. Writes no `sim/`/`company/`/`saas/`
code, edits no `maturity_map.yaml`, no engine. No R13 curriculum/generator/baseline value read or moved.
Per the steer, conflicts between board expectation, build and planned VALUE_CHAIN scope are surfaced as
**director findings, not silently resolved** — this document authorises no build.

**Evidence discipline (R9 / R11, no fabrication).** Every row cites a file (and line/anchor where useful)
read this session. Where a mechanism was searched for and not found, the row says "not found after checking
X — grep clean". ABSENT is a first-class, expected verdict — nothing is inflated. Met/partial/absent counts
are a **diagnostic in this document, never a headline or a score (R12)** — the mission is not to raise the
tally.

---

## The four advisor flags — adjudicated up front (per the mint's exit criterion)

**(a) §1 gas-first — the largest single re-prioritisation, verified and NARROWED.** The board's opening
claim — a GB domestic supplier is *predominantly a gas business* by energy delivered (~4× kWh gas vs
electricity; typical dual-fuel figures ~2,700 kWh elec / ~11,500 kWh gas) — is correct, and the build, the
director's own steer, and the `WHOLESALE_VALUE_CHAIN_FRAME.md` are all **power-led**: the FRAME names gas a
"second commodity" footnote, not a co-equal book. Verified against the live tree: gas *market plumbing* is
in fact **not thin** — a 7-tenor forward curve with confidence bands and a crisis flag
(`company/trading/gas_forward_curve.py::GasTenorBand`, L29-46, day-ahead through Cal+2), an OTC trade book
with seasonal exposure (`company/market/gas_otc_book.py::GasOTCBook`, L80-148), an SBP/SSP gas imbalance
cash-out ledger (`company/market/gas_imbalance_ledger.py`, L19-80, premium/discount + a £100/MWh crisis
threshold), and a real ingested NBP-proxy series feeding `sim/gas_prices_history.py` (per BOARD_SPEC_004
§1.GAS.STOCKFLOW). What **is** thin: `simulation/gas_settlement.py` — retail gas is settled as **pass-through
with `hedge_fraction` an explicit input that PRODUCTION callers set to 0.0**
(`tests/simulation/test_gas_pass_through_hedge.py`, "Phase 56: Gas pass-through customers must have
hedge_fraction = 0"), while retail power carries an evolving hedge fraction bounded in [0.85,1.0]
(`sim/hedging_strategy.py`). **So gas-first is not "build a gas market from scratch" — the market machinery
exists; the correction is that the retail gas book is priced/settled as spot pass-through while the retail
power book is actively hedged, and the WVC FRAME's own framing subordinates gas to a footnote.** This is a
scope/sequencing finding for the director (F1 below), not self-enacted here.

**(b) §3.6 / §7.4 collateral-as-cause-of-death — status UPGRADED since the last pass, verified.** The
2026-07-22 reconciliation found rich cash-consequence *ledgers* (variation margin, additional calls, MtM-vs-
collateral netting, a finite facility) but an **unwired** price-move → margin-call causal loop. That gap is
now closed: `company/finance/margin_call_book.py::build_margin_calls_from_mtm` (added 2026-07-24, L150-211)
derives variation-margin calls directly from a counterparty's netted mark-to-market — `max(0, -netted_mtm)`,
the CSA out-of-the-money party posts collateral — with **no hand-supplied loss figure**. The committed
facility is **book-derived at origination and held fixed** (`book_scaled_credit_facility_gbp`,
`DIRECTOR_RULING_MC2_REAL_HISTORY_NOT_DIFFICULTY_2026-07-25` §3, closing a named defect — a hardcoded £5m
facility that nothing could kill). `company/risk/collateral_death_test.py::breaking_strain_sweep` runs a
real-price-replay dose sweep (0.8×/1.0×/1.2×/1.5×) and **distinguishes `collateral_while_solvent` (dead on
cash, solvent on paper — the actual 2021–22 failure shape) from `collateral_insolvent`** — exactly the
board's "2021–22 was a liquidity event wearing a price event's clothes." Mutation-proven both ways:
`tests/company/risk/test_collateral_death_test.py::test_teeth_death_by_collateral_while_pnl_survives` (the
positive case) and `test_pure_long_book_cannot_die_to_collateral_the_section4_diagnosis` (the negative
control — a pure long book cannot die to collateral, so `any_name_posted_margin=False` is a diagnosis
signal, not a softened test) both exist and are cited by name. **Verdict: MET for the causal mechanism and
the disqualifying-signature avoidance; PARTIAL for the desk-pack surfacing** (the weekly collateral-and-
credit page, board §3.6, is not yet a rendered artefact — the mechanism exists below the surface).

**(c) §7.3 look-ahead & §7.5 demand–price joint tail — claimed MET only with the cited proof.**
§7.3 (any look-ahead in hedging inputs): **MET**, cited proof —
`tests/interfaces/test_observable_trace.py::test_blindfold_gate_MUTATION_future_record_not_served` (a
genuine mutation test: removing the `if oa > as_of: continue` gate makes a future record leak and the test
fails) plus the PreToolUse enforcement hook `.claude/hooks/block_point_in_time_read.py` (live, last touched
2026-07-28, flags `run_settlement(`/`all_records` patterns with no `as_of`/`bisect` bound in new
company/saas code). §7.5 (demand and price independent): **MET**, cited proof —
`sim/weather_tail_demonstration.py` (W1_3, HARDEN-passed 2026-07-28, `53b201ef6`) scores Dunkelflaute
severity as the **product** of cold-intensity × still-intensity (never two marginals) over a real-vs-
synthetic envelope; `background/weather_price_triad.py` + `background/weather_demand_triad.py` demonstrate
one shared weather draw drives both legs. Caveat carried forward honestly: this is a **structural** proof
(the joint tail is demonstrably co-occurring in the engine), not a replay of the named 2018 cold-snap event
specifically — no citation inflates that gap.

**(d) §7.10 profitable-desk-is-an-alarm — convergence recorded, NOT yet a control.** The board's law
("a domestic desk that reliably beats the market is leakage or unauthorised risk, not skill") is one
independent derivation of this project's own **degenerate-emergent-behaviour law** and of **R12** (margin is
a diagnostic, never a target) and R0's "cost flows forward into price, price never backward into cost."
Two independent arrivals at the same law is worth recording as a convergence. But — verified again this
session, `grep -rn "degenerate.emergent\|profit.centre" company saas sim` — **no code enforces it**: the
law exists only as prose (this document, the prior reconciliation, and CLAUDE.md's R12/R0). **Verdict:
ABSENT as a control, MET as a converged doctrine** — a genuine finding for the director (F3 below), not
smoothed into a false MET.

---

## §1 — The products actually traded, and their conventions

| id | board_text (short) | reconciles_to | verdict | evidence | notes |
|---|---|---|---|---|---|
| 1.GASFIRST | "gas comes first" — ~4× kWh vs power; a power-first trading function has misread the book | `simulation/gas_settlement.py` (retail) vs `sim/hedging_strategy.py` (retail power) vs FRAME framing | **PARTIALLY MET** | Gas *market* machinery is deep (see flag (a) above); retail gas is spot pass-through (`hedge_fraction=0` in production per `test_gas_pass_through_hedge.py`) while retail power is actively hedged (`hedging_strategy.py` floor 0.85). `WHOLESALE_VALUE_CHAIN_FRAME.md` §1 names gas a "second commodity" footnote | **Advisor flag (a), the headline finding — see F1.** Re-prioritisation, not a build-from-scratch |
| 1.GASCONV | NBP p/therm, gas day 05:00–05:00, near-far ladder to seasons (Summer Apr-Sep / Winter Oct-Mar), OTC via brokers + ICE, liquidity to ~2-3 seasons | `company/trading/gas_forward_curve.py` `GasTenorBand` | **PARTIALLY MET** | 7-tenor band enum DAY_AHEAD→CAL_PLUS_2 with confidence intervals widening 3%→50% (L29-46) mirrors the board's near-far structure and season/quarter/month granularity; `gas_otc_book.py::Season` splits Apr-Sep/Oct-Mar (L40-48) matching the board's Summer/Winter split exactly. **Not found:** an explicit 05:00-05:00 gas-day convention or p/therm as the working unit (curve stores £/MWh) — a unit-convention gap, not a structural one | Structure is closer to the board's spec than flag (a) implies; the pence/therm unit and gas-day boundary are the specific missing pieces |
| 1.POWERCONV | baseload/peak power blocks, seasons→quarters→months→weeks→DA auction (N2EX/EPEX)→within-day→imbalance cash-out; thin GB liquidity, 5-10MW clips | `company/trading/shape_risk_book.py::ShapeBand` + DA/intraday books | **PARTIALLY MET** | Baseload/peak distinction exists (`ShapeBand`); imbalance cash-out via `company/market/imbalance.py` (per BOARD_SPEC_004 cross-ref). **Not found:** explicit N2EX/EPEX auction naming, or a clip-size/depth limit anywhere in the book (bid-offer spread exists in `hedge_decision.py` L24-28,87-94, widening by tenor, but no volume-depth constraint) — matches battery item 9 below | Silos exist per product but the unified ladder (seasons→...→imbalance as one instrument family) is the WVC FRAME's planned, not-yet-built, unification |
| 1.SHAPE | the shape residual — not baseload+peak but a half-hourly morning/evening-ramp, winter-skewed shape; shape/imbalance premium is a real cost line, near-zero = broken | `company/trading/shape_risk_book.py` + WVC FRAME §3.1 (shaped benchmark) | **PARTIALLY MET** | A shape-risk book exists (baseload/peak bands), but an **explicit shape/imbalance premium as a rendered cost line versus the baseload price** is FRAME-planned (WVC_1, "the annualised shaped energy cost is the benchmark... everything the trading function buys must roughly add up to this number") and not yet built — grep of `company/trading/` finds no `shape_premium_pct`-shaped output | The board's own diagnostic ("if the model's shape premium is near zero, it is broken") cannot yet be evaluated because the line does not exist to inspect |
| 1.OBLIGATIONS | REGOs, RO/CfD, capacity market charges, transmission/distribution loss factors gross up volume | `company/regulatory/llf_register.py` (losses) + `company/regulatory/uig_allocation_register.py` | **PARTIALLY MET** | Line-loss factors to 1.12 and monthly UIG allocation are built and R15-proven (per BOARD_SPEC_004-sibling evidence, `llf_register.py` L41-62, `uig_allocation_register.py` L19-43) — the *losses* half is solid. REGO/RO/CfD/capacity-market charges as an explicit stack line riding on wholesale volume: not found as a rendered cost-stack component (`grep -riE "REGO|capacity.market.charge"` company/ = no hits) | Losses MET; the policy-obligation lines (RO/CfD/CM) are the FRAME's own under-weighted gap (F4 of the prior pass, carried forward) |

**§1 scoreline: 0 MET · 5 PARTIALLY MET · 0 ABSENT.**

---

## §2 — Hedge policy by tariff type

| id | board_text (short) | reconciles_to | verdict | evidence | notes |
|---|---|---|---|---|---|
| 2.FIXED.B2B | fixed book back-to-back at acquisition (weather-normalised, profiled, netted for attrition); managed thereafter as residuals (churn/forecast/weather); ±5% tolerance band | `sim/hedging_strategy.py` (fraction) + `company/trading/hedge_decision.py` | **PARTIALLY MET** | An evolving hedge fraction bounded [0.85,1.0] approximates "mostly covered, breathing inside a band" (battery item 12 partner), and residual management exists via VaR (`hedge_decision.py`). **Not found:** a tariff-type-specific hedge LOGIC split — one policy governs the book generally, not "fixed = back-to-back at acquisition" as a distinct rule, and no explicit ±5%-of-forecast-volume tolerance band is named as such | Present in spirit (bounded, not naked), absent as the board's specific mechanism (acquisition-triggered lock + named tolerance band) |
| 2.FIXED.CORR | the fixed book's poison: cold snap raises demand exactly when prices spike → short precisely when covering is most expensive | joint weather→demand→price mechanism (W1_3/triads) | **MET** (mechanism) / **PARTIALLY MET** (as a hedge-policy consequence) | The causal mechanism is proven (flag (c) above — demand and price move together from one weather draw). But whether the FIXED BOOK specifically is shown going short and expensive-to-cover at exactly that moment (a hedge-adequacy consequence, not just the price/demand correlation) is not separately demonstrated — no test found tying book coverage ratio to the joint-tail event | The underlying physics the board's warning depends on is real and proven; the specific "the fixed book's poison" narrative (coverage draining exactly when cover is dearest) is not yet an isolated, named result |
| 2.SVT.CAP | SVT book replicates the cap: buy in tranches mirroring Ofgem's observation window; deviation = a sized/authorised/stop-lossed speculative position | `company/pricing/ofgem_price_cap.py` | **ABSENT** | `ofgem_price_cap.py` (L1-52) is a **static annual £/MWh dict** (2019-2025 hand-set values, `_ELEC_CAP_FALLBACK`/`_GAS_CAP_FALLBACK` beyond) — no observation window, no quarterly reset, no achieved-cost-vs-allowance tracking, therefore no mechanical cap-tracking hedge ladder can exist on top of it | Matches battery item 8 (FAIL) below — this is the load-bearing absence beneath 2.SVT.CAP |
| 2.LADDER | written policy: target ratio by horizon, tolerance bands, delegated dealing authority, stop-loss/escalation, no naked shorts in delivery months; desk shows actual-vs-policy any morning | `sim/hedging_strategy.py` floor + `company/trading/wholesale_position_report.py` | **PARTIALLY MET** | A floor (0.85) prevents naked shorts by construction (battery item 12); WAPP reporting (`wholesale_position_report.py`) gives an actual-position view. **Not found:** delegated dealing authority by tenor/size, stop-loss triggers, or an explicit policy-ladder-vs-actual rendered comparison (the WVC FRAME's planned "cover fan" is this exact artefact, not yet built) | Governance controls (authority, stop-loss) are a genuine gap distinct from the mechanical floor |

**§2 scoreline: 1 MET · 2 PARTIALLY MET · 1 ABSENT.**

---

## §3 — The weekly desk pack

The board's 7-item pack is not separately built as a rendered weekly artefact; each item is assessed against
whether the *underlying data* exists to construct it.

| id | board_text (short) | reconciles_to | verdict | evidence | notes |
|---|---|---|---|---|---|
| 3.1.POSITION | hedge ratio by month/fuel vs policy ladder + tolerance band; net open volume | `wholesale_position_report.py` | **PARTIALLY MET** | WAPP report gives a position view; ladder-vs-actual as a rendered comparison is FRAME-planned (WVC "cover fan"), not built | Data exists; the comparison artefact does not |
| 3.2.COST.ALLOW | WACOG vs curve MtM, and vs the SVT book's accruing cap wholesale allowance (= the default book's gross margin) | `ofgem_price_cap.py` (static, no allowance mechanics) | **ABSENT** | Cannot construct — the cap has no observation-window/allowance mechanics to accrue against (2.SVT.CAP) | Downstream of the 2.SVT.CAP absence |
| 3.3.DEMAND | weather-normalised forecast vs prior week; actual-vs-forecast error; churn/acquisition vs plan; EAC movements | `company/crm/churn_model.py`, `eac_drift_assessor.py` (per BOARD_SPEC_004-sibling) | **PARTIALLY MET** | Forecast-error and EAC-drift machinery exists; a rendered weekly demand page combining all four is not found as one artefact | Components exist scattered; the weekly-pack assembly does not |
| 3.4.RISK | VaR/equivalent on open position; named weekly stress scenarios (2021-style rally, 1-in-20 cold, demand-price joint stress) with cash+P&L consequence | `company/trading/hedge_decision.py` (VaR) + `company/risk/collateral_death_test.py` (MC-2 sweep) | **PARTIALLY MET** | VaR exists (`hedge_decision.py`). The MC-2 breaking-strain sweep (flag (b)) is effectively a named stress scenario with a **cash** consequence (`liquidity_headroom_min_gbp`, `collateral_cover_min`) run around a real price replay — close to the board's ask. **Not found:** this run as a *standing weekly* re-run artefact, or a "1-in-20 cold winter" scenario named as such | MC-2 is real substance for this row but is a director-gated measurement tool today, not a weekly pack page |
| 3.5.IMBALANCE | imbalance volume % + cost/MWh vs DA reference; shape cost achieved vs assumption | `company/market/imbalance.py`, `gas_imbalance_ledger.py` | **PARTIALLY MET** | Imbalance charge mechanisms exist for both fuels (electricity NIV/SSP per BOARD_SPEC_004-sibling; gas SBP/SSP `gas_imbalance_ledger.py` L19-80); "shape cost achieved vs assumption" is the FRAME's WVC_1 output, not yet built | Imbalance MET at the mechanism level; the shape-vs-assumption comparison is planned, not built |
| 3.6.COLLATERAL | collateral/credit sits IN the trading pack: margin posted, Elexon credit cover, facility headroom, projected call under ±30% moves | `company/finance/margin_call_book.py` + `company/trading/wholesale_credit_exposure.py` + `collateral_death_test.py` | **PARTIALLY MET** | The mechanism is now real (flag (b) — the MC-2 sweep literally runs a ±dose price-move-to-collateral-call chain, `DEFAULT_DOSES=(0.8,1.0,1.2,1.5)` brackets a ±30-50% move). Elexon-specific credit cover not found by name (`wholesale_credit_exposure.py` is counterparty MtM exposure generally, not Elexon-specific). **The rendered "in the trading pack, not a finance annex" surfacing is absent** — this data lives in `company/finance/` and `company/risk/`, not a desk-pack page | Upgraded from the 2026-07-22 pass's "PARTIAL, unwired loop" — the loop is wired; the desk-pack *page* is the remaining gap |
| 3.7.BACKDROP | week-on-week curve moves, gas storage and LNG, volatility — one page context | none found | **ABSENT** | No storage/LNG state exists to report on (matches BOARD_SPEC_004 §1.GAS.STORAGE/1.GAS.LNG ABSENT); no volatility-term-structure page found | Downstream of the storage/LNG absence documented in BOARD_SPEC_004 |

**§3 scoreline: 0 MET · 5 PARTIALLY MET · 2 ABSENT.**

---

## §4 — Where trading creates or destroys value

| id | board_text (short) | reconciles_to | verdict | evidence | notes |
|---|---|---|---|---|---|
| 4.COSTCENTRE | desk is a risk-management cost centre, not a profit centre; reliably "beating the market" should alarm | R12 (doctrine) + no code control | **PARTIALLY MET (doctrine MET, control ABSENT)** | See flag (d) — the law is doctrine (R12, R0, CLAUDE.md) but has no enforcing code | Duplicate of battery item 10 / F3 |
| 4.EXEC.VS.LADDER | execution vs the mechanical policy ladder, cumulatively | not found as a built comparison | **ABSENT** | No mechanical-policy-benchmark-vs-actual-execution comparison found; requires the ladder itself (2.LADDER, PARTIAL) to exist first | Downstream dependency |
| 4.FORECAST.ATTR | forecast error × price-at-correction = a cash cost; MAPE by horizon | `company/*/eac_drift_assessor.py` (component) | **PARTIALLY MET** | Forecast-error tracking exists in pieces (EAC drift); a forecast-error-to-cash-cost attribution line is not found assembled | Components present, attribution not assembled |
| 4.SHAPE.MGMT | shape/imbalance cost vs a naive buy-everything-day-ahead counterfactual | none found | **ABSENT** | No counterfactual-benchmark comparison found — this is the FRAME's planned value-add ledger (WVC_4), not yet built | FRAME-planned |
| 4.DISTRESSED | avoiding distressed trades — forced buys from breached tolerance/exhausted collateral; measured in the negative, ideally zero | `collateral_death_test.py` (measures the failure) | **PARTIALLY MET** | The death-test measures WHEN forced distress (collateral exhaustion) occurs (death_dose, death_cause) — this is measuring the failure mode directly, which is close to the board's "count of forced trades, ideally zero" in spirit, though it is a stress-sweep instrument, not a running production counter | Real substance; not the specific production metric the board names |
| 4.PNL.ATTRIB | monthly P&L attribution: price / volume / shape / timing / imbalance | none found assembled | **ABSENT** | No five-way P&L decomposition found; WAPP report gives an aggregate position/cost view, not a price/volume/shape/timing/imbalance split | The board: "if the attribution cannot be produced, the desk does not know where its result came from" — currently cannot be produced |

**§4 scoreline: 0 MET · 3 PARTIALLY MET · 3 ABSENT.**

---

## §5 — Benchmarks, ratios, the annual cost stack

| id | board_text (short) | reconciles_to | verdict | evidence | notes |
|---|---|---|---|---|---|
| 5.STACK.CONSTRUCT | 6-step annual shaped-cost stack: shape → shape-weighted curve incl. peak/shape premium & winter-gas → gross up losses/UIG → shaping/imbalance allowance → RO/CfD/CM → wholesale line above networks/policy/opex/margin | `WHOLESALE_VALUE_CHAIN_FRAME.md` §1 (WVC_1, planned) | **ABSENT (build) / MET-IN-PLAN (scope)** | This IS the FRAME's stated spine ("the annualised shaped energy cost is the benchmark... everything the trading function buys must roughly add up to this number") — independently specified by the board, corroborating the FRAME. Not yet built: no `maturity_map.yaml` entry for WVC_1-5, no code implementing the 6-step construction found | The clearest case of the board's spec independently validating an already-planned (not yet built) construct |
| 5.RATIOS | achieved-vs-cap-allowance; shape premium as % of baseload (near-zero = broken); winter/summer spreads; forward premium over realised spot (mid-single to low-double-digit %); imbalance cost/MWh vs DA; forecast error by horizon | none rendered | **ABSENT** | None of these ratios are computed as standing sanity bands today; they depend on 5.STACK.CONSTRUCT existing first | The board explicitly proposes these as sanity DIAGNOSTICS (R12-compatible framing: "external sanity checks... should be routine") — a genuine, adoptable addition once WVC_1 lands |

**§5 scoreline: 0 MET · 1 PARTIALLY MET (scope-corroborated, build-absent) · 1 ABSENT.**

---

## §6 — How the wholesale stack should drive retail prices

| id | board_text (short) | reconciles_to | verdict | evidence | notes |
|---|---|---|---|---|---|
| 6.FIXED.PRICE | fixed = shaped/lossed forward cost + explicit risk premia (volume, weather, shape, **churn free-option**, credit) + margin, off a **live curve**; stale quote = a free option written to the public | `sim/forward_curve.py::generate_forward_price` (per BOARD_SPEC_004 §4.FWD.BELIEF) | **PARTIALLY MET** | A live, re-computed forward exists (`spot_ewma × seasonal × (1+term_premium)`) — not a stale static quote. **Not found:** an explicit churn-free-option premium line, or a stale-quote guard/re-price-frequency control | The live-curve half is real; the explicit risk-premia decomposition (esp. the churn option) is the gap |
| 6.SVT.CONSTRAINED | SVT commercial question is not price (cap sets ceiling) but whether the hedge tracks the allowance | `ofgem_price_cap.py` (static, no tracking) | **ABSENT** | No allowance-tracking exists because the cap itself has no observation-window mechanics (2.SVT.CAP) | Same root cause as 2.SVT.CAP / battery item 8 |
| 6.GOVERNANCE | cost flows forward into price; price never backward into cost; margin is an output, not a target; pricing committee separate from trading | R12 (doctrine) | **MET (doctrine)** | R12 states exactly this ("margin... is a DIAGNOSTIC, never a target... never tuned because company results look wrong") and is a standing, cited project law, not merely aspirational — R13's baseline/curriculum split enforces the same discipline structurally | The one clean MET in §6 — genuine doctrinal alignment, independently arrived at |

**§6 scoreline: 1 MET · 1 PARTIALLY MET · 1 ABSENT.**

---

## §7 — The credibility battery (12 disqualifiers) — standing practitioner fidelity oracle

Verdict convention (matching BOARD_SPEC_004): **MET** = disqualifier avoided (credible) · **PARTIALLY MET**
= partly avoided · **ABSENT** = the disqualifier's failure mode is present in the build.

| # | Disqualifier (board §7) | verdict | evidence / anchor |
|---|---|---|---|
| 1 | Gas missing or subordinate | **PARTIALLY MET** | Gas market plumbing is deep (7-tenor curve, OTC book, SBP/SSP cash-out — flag (a)), but retail gas is spot pass-through (`hedge_fraction=0` production default) while retail power is actively hedged, and the WVC FRAME's own framing subordinates gas → **F1** |
| 2 | No shape residual | **PARTIALLY MET** | Baseload/peak distinction exists (`shape_risk_book.py::ShapeBand`); an explicit shape/imbalance premium as a rendered cost line (board: near-zero = broken) is FRAME-planned, not built (1.SHAPE) |
| 3 | Any look-ahead in hedging inputs | **MET** | Genuine mutation test `test_blindfold_gate_MUTATION_future_record_not_served` + live PreToolUse hook `.claude/hooks/block_point_in_time_read.py` (touched today, 2026-07-28) — flag (c), claimed with cited proof per the board's own caveat ("test for it adversarially, not by inspection") |
| 4 | No collateral physics | **MET** | `build_margin_calls_from_mtm` derives calls purely from netted MtM (no hand-supplied loss); `collateral_death_test.py::breaking_strain_sweep` produces `collateral_while_solvent` — the 2021-22 shape — mutation-proven both ways (`test_teeth_death_by_collateral_while_pnl_survives`, `test_pure_long_book_cannot_die_to_collateral_the_section4_diagnosis`) — flag (b), **UPGRADED from the 2026-07-22 pass's PARTIAL/unwired verdict**. Caveat: the weekly-pack *surfacing* (3.6) remains PARTIAL |
| 5 | Demand and price independent | **MET** | Joint-tail structurally proven from a shared weather draw (W1_3 `weather_tail_demonstration.py`, HARDEN-passed 2026-07-28; `weather_price_triad.py`/`weather_demand_triad.py`) — flag (c). Caveat: structural proof, not a replayed named 2018 event |
| 6 | Churn uncorrelated with market | **PARTIALLY MET** | SVT-swells-on-spike is present (`market_conditions.py::MARKET_SWITCHING_MULTIPLIER_BY_YEAR`, e.g. 2022=0.44 reflecting suppliers withdrawing fixed deals — matches the board's own §6 note on 2022 fixed-deal withdrawal exactly). **"Fixed customers leave when the market falls below their own locked rate" is ABSENT**: `churn_model.py` keys churn off `rate_increase_pct` (the customer's OWN rate change vs their prior rate) and the published year-level switching-multiplier, not a live wholesale-price-vs-locked-rate in/out-of-money comparison — `grep -n "in_money\|out_of_money\|below_fix"` in `churn_model.py` = no hits |
| 7 | Benign imbalance, always | **MET** | Imbalance cash-out spikes on both fuels: electricity NIV/SSP stress premium (per BOARD_SPEC_004-sibling evidence), gas `gas_imbalance_ledger.py` `_CRISIS_SBP_THRESHOLD_GBP_PER_MWH=100.0` (L21) flags crisis pricing | Not a benign fiction — genuine cash-out sensitivity on both books |
| 8 | Cap mechanics absent/hand-waved | **ABSENT** | `ofgem_price_cap.py` L25-52 is a static per-year dict — no observation window, no quarterly reset, no achieved-cost-vs-allowance tension. Verified unchanged since the 2026-07-22 pass (`git log` shows last touch 2026-06-24, before this steer) |
| 9 | Infinite liquidity | **PARTIALLY MET** | Bid-offer spread modelled, widening by tenor, bought at ask not mid (`hedge_decision.py` L24-28,87-94); no clip-size/market-depth limit anywhere — `grep -riE "clip.size|market.depth"` company/ = no hits | Spread yes, depth no |
| 10 | A profitable desk (no alarm) | **ABSENT (control)** | The law exists only as prose (R12, R0, this document, the prior reconciliation) — no code enforces or flags a persistently-profitable desk. Verified again this session, `grep -rn "degenerate.emergent\|profit.centre"` company/saas/sim = no code hits → **F3** |
| 11 | No losses, no UIG, no consumption-estimate error | **MET** | Line-loss factors to 1.12, monthly UIG allocation, EAC drift, billed-vs-metered reconciliation all exist and are R15-proven (per BOARD_SPEC_004-sibling evidence — `llf_register.py`, `uig_allocation_register.py`, `eac_drift_assessor.py`, `back_billing.py`) |
| 12 | Everything exactly 100% hedged, always | **PARTIALLY MET** | Power book breathes: floor 0.85, bounded evolution in [0.85,1.0], population 0.80-0.90 (`sim/hedging_strategy.py`) — not pinned at 100%. But it is a hedge-*fraction* floor, not an explicit ±% volume tolerance band (board §2), and retail gas is 0% hedged (pass-through), which is its own — different — disqualifier-relevant fact (item 1) |

**Battery scoreline: 5 MET (3,4,5,7,11) · 5 PARTIALLY MET (1,2,6,9,12) · 2 ABSENT (8,10).**

**Change from the 2026-07-22 pass:** item 4 (collateral physics) moves **PARTIAL → MET** — the price-move
→ margin-call loop that was the single hardest gap six days ago is now wired and mutation-proven. This is
the one place this reconciliation's tally materially differs from its predecessor, and it is a real build
delta, not a re-reading of the same evidence.

**Recommendation (endorsing the board's own §7 framing and the prior pass):** register these 12 as a
**standing R15-failable practitioner fidelity oracle**, peer to the regulatory oracle and to
BOARD_SPEC_004's 12-item machinery battery — items 6, 8, 10 have concrete, directly-checkable build
dependencies (churn in/out-of-money logic; cap observation-window mechanics; a desk-profit alarm) that a
control can test for directly, not merely narrate.

---

## Director findings — where the board's expectation refines or conflicts with the built design and planned scope

**F1 — Gas-first is real, but narrower than the board's framing implies (advisor flag a, CONFIRMED).**
The board's headline claim (predominantly a gas business by kWh) is correct, and the WVC FRAME's own
framing is power-led — a genuine correction. But the verification shows the gas *market* plumbing (curve,
OTC book, imbalance cash-out) is comparably deep to power's; the actual gap is **retail gas priced/settled
as spot pass-through (`hedge_fraction=0`) while retail power carries an active, evolving hedge.** **For the
director:** does making retail gas an actively-hedged book (mirroring power's hedge-fraction mechanism),
and re-weighting the WVC atoms to lead with the larger fuel rather than append it, become an Epoch-2
re-prioritisation via the steer's propose-then-proceed gate? This reconciliation does not self-enact it.

**F2 — Collateral is now a modelled cause of death, closing the board's §7.4 disqualifier — but the desk-pack
surfacing (§3.6) has not caught up.** The mechanism landed 2026-07-25 under `DIRECTOR_RULING_MC2_REAL_HISTORY_NOT_DIFFICULTY_2026-07-25`,
independently of this reconciliation and after the board spec was drafted — a case of the build catching up
to the board's expectation on its own. **For the director:** the remaining gap is presentational, not
structural — should the MC-2 sweep's outputs (`liquidity_headroom_min_gbp`, `collateral_cover_min`,
`death_cause`) be promoted from a director-gated measurement tool into the standing weekly desk-pack page
the board specifies (§3.6, §3 item 4's named weekly stress-scenario re-run)?

**F3 — "A profitable desk is an alarm" (§7.10) converges with the project's own degenerate-emergent-
behaviour law and R12/R0 — two independent derivations, still zero enforcement.** Both this reconciliation
and its 2026-07-22 predecessor find the same thing: real doctrinal convergence, no code. **For the
director:** is a desk-profit-alarm control (R15-failable — mutation-test that it actually fires on a
synthetically-inserted persistent-profit case) worth minting as its own atom, given the convergence
strengthens the case that this is a load-bearing law rather than a stylistic preference?

**F4 — The board's §5 six-step cost-stack construction independently re-derives the WVC FRAME's planned
spine (WVC_1) and sharpens it with three lines the FRAME under-weighted: losses/UIG grossing-up (already
built, BOARD_SPEC_004-sibling evidence), an explicit shape/imbalance premium over baseload (not yet built —
1.SHAPE), and the wholesale-riding obligations RO/CfD/CM (not yet built — 1.OBLIGATIONS).** **For the
director:** when WVC_1 is opened for BUILD, fold these three lines into its stack decomposition rather than
treating them as separate atoms — carried forward unchanged from the 2026-07-22 pass, still true.

**F5 — Churn's market-correlation is real on the SVT side, absent on the fixed side — the board's own §7.6
test resolved honestly, not smoothed.** `market_conditions.py`'s published year-level switching multiplier
(2022=0.44) genuinely captures "rivals withdrew fixed deals, so even large rate rises don't drive
switching" — matching the board's own narrative almost verbatim. But the board's sharper claim — a fixed
customer churns when the market falls *below their own locked rate* (an in/out-of-money trigger, not a
year-level published multiplier) — has no code anywhere. **For the director:** this is one of the two named
"risk correlations" (with F2/collateral) the board's Chair says is where a believable trading function's
excitement should live — a candidate for the next WVC-adjacent atom, distinct from and additional to the
churn-model's existing mechanisms.

---

## Summary scoreline

**27 scoreable expectations (§1-6) + 12 battery items (§7) = 39 rows · 7 MET · 22 PARTIALLY MET · 10 ABSENT
· 0 N/A.**

By section (MET / PARTIAL / ABSENT): §1 products 0/5/0 · §2 hedge policy 1/2/1 · §3 desk pack 0/5/2 ·
§4 value 0/3/3 · §5 cost stack 0/1/1 · §6 retail price 1/1/1 · §7 battery 5/5/2.

**This is a diagnostic, not a scorecard (R12) — read as follows.** The strongest area is the **credibility
battery's hard disqualifiers**: look-ahead is genuinely blocked (mutation-proven), the demand-price joint
tail is genuinely coupled (structurally proven), collateral is now a genuine cause of death
(mutation-proven, landed independently of this document), and losses/UIG/estimate-error are real. The
weakest areas are exactly where the board predicted the excitement should live and mostly does not yet:
**the two risk correlations (F2's remaining surfacing gap and F5's fixed-book churn trigger)**, **the
cost-stack/benchmark spine (§5, F4)** — independently re-derived by the board but still unbuilt — and **the
gas-first re-weighting (F1)**, which the verification narrows from "gas market missing" to "retail gas
unhedged and the framing subordinates it." The one genuine doctrine-vs-code gap is **§7.10/F3**: a law two
independent parties have arrived at, enforced nowhere.

**The 3 most material findings for Movement 3:**
1. **Gas-first re-weighting (F1)** — the largest single re-prioritisation the advisor flagged, confirmed
   but narrowed to: hedge retail gas actively (not build gas machinery from scratch) and lead the WVC
   atoms with the larger fuel.
2. **The two named risk correlations are half-built** — collateral-as-cause-of-death (F2) is now
   mechanism-complete and needs only desk-pack surfacing; churn-vs-locked-rate (F5) has no mechanism yet at
   all. The board's Chair names these as precisely where a believable trading function's excitement lives.
3. **The cost-stack/benchmark spine (§5/F4) and the profitable-desk alarm (§7.10/F3)** are both
   independently re-derived by the board from a blind read of the industry, corroborating already-planned
   or already-declared project constructs that remain unbuilt — the board is not inventing new requirements
   so much as independently confirming the FRAME's and R12's judgement.

*All scope changes route through the WHOLESALE_VALUE_CHAIN steer's propose-then-proceed (2h veto); this
reconciliation is analysis and authorises nothing to build. The 12-item battery is recommended as a
standing R15-failable practitioner fidelity oracle, peer to BOARD_SPEC_004's machinery battery and the
regulatory-rules oracle.*
