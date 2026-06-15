# Latest Status (mobile snapshot)

This file is served by `/ui/status` on the file API for quick mobile checks.
For full detail see `STATUS.md` at the repo root.

**Share with Claude.ai**: paste this URL into a claude.ai chat and Claude
will fetch the live content directly — no copy/paste needed, always
up to date with the latest push to `main`:
https://raw.githubusercontent.com/21bcarlisle-arch/synthetic-enterprise/main/docs/status/LATEST.md

Last updated: 2026-06-15T11:52:48Z

**Phase 6a complete — HH smart meter customers (2026-06-15)**: added three
half-hourly (smart meter) residential customers, C7 (London, single
occupant), C8 (Manchester, family), C9 (Glasgow, elderly) — `eac_kwh: None`,
`"metering": "HH"` in `saas/customers.py`. New `simulation/hh_consumption.py`
loads real per-half-hour consumption from `sim/hh_data/{C7,C8,C9}.csv`
(synthetic, generated once via `tools/generate_hh_data.py` from the existing
PC1 GAD shape run through `simulation.demand_model.build_demand_shape()` with
real Open-Meteo weather for each customer's location — reusing C1/C2/C3's
London/Manchester/Glasgow weather data, so no new weather pulls needed).
`run_phase2b.py`'s new `EFFECTIVE_EAC_KWH` dict is the single source of truth
for hedging-volume sizing: profile-class customers (C1-C6, C1g-C4g) keep
their static `eac_kwh`; HH customers derive an effective annual figure from
real consumption (`estimate_annual_kwh`). C1-C6/C1g-C4g settlement is
unaffected — same shape_fn path as before. 11 new tests (283 total), lint
clean.

Full 2016-2025 re-run (13 accounts: 9 electricity incl. C7-C9 + 4 gas):
**SURVIVED full window**, final treasury £29,846.19 ->
£53,524.74 (net margin **£23,678.55**, gross £27,525.43, capital cost ratio
**14.0%** of gross), 168 Context Handshake wake-ups, 1,434 bills (avg clarity
0.878, service quality score 0.920), enterprise value £12,801.58 across 9
billing accounts, cost to serve £8,878.73 (net margin after cost to serve
£18,646.70). Contrary to the original plan's expectation, C7-C9's 4b/4c
metrics (cost-to-serve, CLV/enterprise value, bills, bill-shock) all computed
correctly — no "Not available" placeholders were needed for the new
customers; the existing data architecture handled the mixed profile-class +
HH portfolio without any gaps.

**Revenue capture (Open Questions #1/#5)**: `saas/reporting/annual_report.py`
now captures `total_revenue_gbp` (sum of `revenue_gbp` across all settlement
records) and reports **net margin as % of revenue: 12.6%** in the executive
summary (industry benchmark for a retail energy supplier: 2-5% — flagged as
an open question about pricing realism, see REPORTING_BACKLOG item 17). The
mandate-comparison section also reports this metric, falling back to "Not
available" for the pre-5c snapshot (which has no revenue figure).

**Other Open Questions actioned**: idle-detector false positives (#4,
`AUTOLOOP_IDLE_CHECKS` 5->10, i.e. 10 minutes) and two CLAUDE.md gaps (#6,
non-blocking concurrency + ~5hr session window) fixed directly. Forward-curve
realism (#2) and cost-to-serve depth (#3) are larger, propose-before-build
items — proposed approaches documented in `docs/reports/REPORTING_BACKLOG.md`
items 16-17, awaiting Rich's steer before any implementation.

283 tests passing, lint clean. Report:
https://21bcarlisle-arch.github.io/synthetic-enterprise/reports/ANNUAL_REPORT.md

**Phase 5c complete — minimum hedge mandate (2026-06-15)**: redesigned the
hedging philosophy from "speculative book with a risk governor" to "supply
obligation first, active position second", matching how real suppliers
(e.g. EDF) operate. `sim/hedging_strategy.MIN_HEDGE_FLOOR = 0.85` — every
contract term now starts at least 85% hedged; the risk committee's
`evolve_hedge_fraction()` operates only in `[0.85, 1.0]`, managing the
~15% active position rather than deciding whether to hedge at all. Capital
cost was already charged on the unhedged (naked) portion of volume, so
raising the floor to 0.85 caps that exposure — and the capital charge
derived from it — at 15% of volume by construction, with no separate
capital-cost code change needed.

Re-ran the full 2016-2025 simulation under the new mandate:
treasury £21,829.17 -> £37,953.15, net margin £16,123.98 (gross £18,970.93,
**capital cost ratio 15.0%**, down from 41.0% under the old reactive
model). **2021 net margin £632.78** (was £-1,096.43 under the old reactive
model) — the business was largely protected going into the crisis rather
than scrambling to hedge after the fact. Whole-run hedging cost £17,352.21
vs. a fully naked book (actual £16,123.98 vs. naked £33,476.19) — more than
the old model's £6,696.63, reflecting the cost of carrying the mandate
through calm years; the new `ANNUAL_REPORT.md` section "Hedging Mandate —
Before/After Phase 5c" lays out the full mandate-vs-old-reactive-vs-naked
comparison for Rich's review.
99 Context Handshake wake-ups, 1,101 bills (avg clarity 0.918, bad debt
£2,639.69), enterprise value £10,496.28 across 6 billing accounts, SURVIVED
full window. Report:
https://21bcarlisle-arch.github.io/synthetic-enterprise/reports/ANNUAL_REPORT.md
273 tests passing, lint clean.

**Two-way NTFY command channel (2026-06-14)**: Rich can now send a short
message from the ntfy app on his phone (topic `skynet-synthetic`) and the
agent will act on it and reply via NTFY — no staging required. New shared
helper `background/ntfy_utils.py` records the id of every outgoing
notification; `session_watchdog.py`'s existing 60s loop now also polls
`ntfy.sh/skynet-synthetic/json?poll=1&since=...`, skips messages it sent
itself (via the recorded ids), and relays anything else into the `claude`
tmux session with an instruction to reply concisely via NTFY (deferring if a
permission prompt is showing). The watermark persists to
`docs/observability/.ntfy_command_since.json` so it survives restarts.
Staged instruction `docs/staging/FIX_NTFY_TWO_WAY.md` actioned and moved to
`docs/staging/done/`. 265 tests passing, lint clean.

**Phase 5b complete — report data pipeline (2026-06-14)**: the combined
2b+4b+4c run (`python3 -m simulation.run_phase4c_on_phase2b --save-json`)
now runs Phase 2b once and feeds the same settlement records through the
4b customer-value builders and 4c billing-experience builders, persisting
the reduced output to `docs/reports/run_output_latest.json` (+ a versioned
copy stamped with git commit and timestamp). `ANNUAL_REPORT.md` regenerates
from this JSON with real customer-book, pricing/margin, and VaR-ratio data
where it exists; remaining "Not available" placeholders are limited to
genuinely-unbuilt mechanics (roster churn events, regulatory threshold
tracking — see REPORTING_BACKLOG.md). A new "Hedge Effectiveness" section
(whole-run + per-year) answers whether the risk committee's hedging actually
made money: across the full 2016-2025 run, hedging **cost** £6,696.63 vs. a
fully naked book (actual net £26,779.56 vs. naked net £33,476.19). Final
figures: treasury £21,829.17 -> £48,608.72, net margin £26,779.56 (gross
£45,417.31, capital cost ratio 41.0%), 130 Context Handshake wake-ups, 1,101
bills (avg clarity 0.918, avg bill shock 12.7%, bad debt £2,639.69),
enterprise value £32,018.72 across 6 billing accounts, SURVIVED full window.
`make publish-report` pushes `ANNUAL_REPORT.md` to a public Gist:
https://gist.github.com/21bcarlisle-arch/84943fc547781e6389e0561691ee5b4b
252 tests passing, lint clean, pushed (`c56e6e8` + this run's commit).

**Usage-pause fix #2 (2026-06-14)**: the soft 90%-usage self-pause never
fired because `/usage` was embedded mid-instruction in
`USAGE_PAUSE_CHECK_INSTRUCTION` — a slash command is only recognised when
it's the entire input, so Claude never actually ran it. Fixed:
`background/session_watchdog.py`'s `check_session_usage()` now sends a
standalone `/usage`, captures and parses the pane itself
(`parse_usage_pane()`), and writes `.usage_pause.json` directly if usage is
>= 90% — no Claude-side action needed. 5 new tests (252 total), lint clean,
pushed (`a31caa1`).

**Weather-effects re-run completed cleanly with Ollama caps (2026-06-14)**:
the restarted run (num_predict=2048 cap + 60s timeout on all Ollama calls,
see `sim/risk_committee_agent.py`/`tools/delegate_ollama.py`) finished the
full 2016-2025 window with no timeout/runaway-loop issues. Final figures
(slightly different from the earlier interrupted attempt below, due to LLM
non-determinism in the risk committee's responses): net margin **£25,666.60**
(gross £42,889.16, capital cost ratio 40.2%), treasury £21,829.17 →
£47,495.77, electricity net £22,191.09 / gas net £3,475.50, 1,101 bills (avg
clarity 0.918, avg bill shock 12.7%, bad debt £2,639.69), 161 Context
Handshake wake-ups, SURVIVED full window.

**Watchdog fix (2026-06-14)**: `background/session_watchdog.py`'s
`check_autoloop` checked `REVIEW_GATE_PATTERN`/`PERMISSION_PROMPT_PATTERN` on
every poll regardless of pane activity. Claude's own prose mentioning
"REVIEW_GATE" while actively working (e.g. discussing a staged instruction's
gate requirements) could sit in the captured pane tail and get treated as a
deliberate stop on every poll — suppressing `AUTOLOOP_INSTRUCTION` (and its
soft 90%-usage self-check) for hours, until the hard 100% usage-limit path
caught it instead. Fixed: these patterns are now only checked once the pane
has been idle (unchanged) for `AUTOLOOP_IDLE_CHECKS` consecutive polls. 34
watchdog tests updated and passing.

**Phase 5a complete — annual report generated, REVIEW_GATE (2026-06-14)**:
the bootstrap run of `python3 -m saas.reporting.annual_report` finished
(net margin £26,173.89, gross £44,682.49, capital cost ratio 41.4%,
treasury £21,829.17 → £48,003.06, 122 Context Handshake wake-ups, 1,101
bills, SURVIVED full window — figures differ slightly from the weather-effects
re-run above due to LLM non-determinism in risk-committee responses).
`docs/observability/phase4c_report_data.json` now holds the persisted run
output, and `docs/reports/ANNUAL_REPORT.md` (10 year sections, 2016-2025) was
generated from it. `docs/reports/REPORTING_BACKLOG.md` (15 prioritised items)
is also ready. **Awaiting Rich's review of both and prioritisation of the
backlog before any further reporting work.**

**Phase 4c complete, including the weather-effects re-run (2026-06-14)**:
`simulation/run_phase2b.py` now applies 4c-2 (weather-driven demand) and 4c-3
(weather→price sensitivity) directly to the settlement run, closing the last
item in Phase 4c's integration backlog:
- `simulation/weather_inputs.py` (new) maps each customer to a C1-C4 weather
  CSV by shared location (C5/C1, C6/C2, C1g-C4g/C1-C4) and provides
  lookback-window mean temperatures.
- Electricity consumption shapes now run through 4c-2's
  `build_demand_shape()` per customer (real daily weather + 4c-1 property
  records; SME C5/C6 use `DEFAULT_PROPERTY`).
- Forward prices (both elec and gas renewal schedules) now pass the
  lookback-window temperatures through to 4c-3's
  `weather_sensitivity_multiplier()` via a new optional `lookback_temps_fn`
  on `simulation.renewals.build_renewal_schedule` and
  `_build_gas_renewal_schedule`.
- 6 new tests (243 total), lint clean, pushed (`91847d0`).

**Full 9.5-year re-run with weather effects live — headline figures**:
- Net margin **£25,470.20** (up from £13,646.21 without weather effects,
  +£11,823.99) — gross margin £42,613.51, capital costs £17,143.31
- Treasury £21,829.17 → £47,299.37; capital cost ratio 40.2% of gross (down
  from 51.3%)
- Electricity: gross £37,712.40 / net £21,994.69. Gas: gross £4,901.12 / net
  £3,475.50
- Billing layer: 1,101 bills, avg clarity 0.918 (was 0.923), avg bill shock
  12.7% (was 10.9%), bad debt £2,639.69 (was £2,016.30), **service quality
  score 0.935** (was 0.941)
- OUTCOME: SURVIVED — full 2016-2025 window completed, 161 Context Handshake
  wake-ups (was 160)
- See `docs/observability/PHASE_4c_SUMMARY.md` ("Follow-up — Full Re-run with
  4c-2/4c-3 Weather Effects Live") for the per-account table and open
  questions (clarity/bad-debt move slightly worse with weather effects live —
  expected, since 4c-2/4c-3 are exactly the volatility and price-shock 4c-4/
  4c-6 were built to penalise).

This closes Phase 4c's integration backlog entirely. With Phase 4b and 4c
both complete, Phase 4's "core value drivers" prerequisite for Phase 5 is
satisfied. Phase 4a remains an undesigned placeholder. **Open question for
Rich**: Phase 4a (fully synthetic ecosystem bootstrap, run forward beyond
2025) or Phase 5 (smart tariff innovation) design next?

Current phase: Phase 2b (gas dual fuel) COMPLETE. Full 9.5-year re-run
finished with active Context Handshake (160 wake-ups, routed through local
Ollama `qwen3:14b`, now live as the standard coder/committee model). Headline
figures: net margin **£13,970.60** (electricity £10,850.17 + gas £3,120.43)
over 2016-2025; treasury grew £21,829.17 → £35,799.77. Capital cost ratio
50.9% of gross. See `docs/observability/PHASE_2b_SUMMARY.md` for full detail.

`make check` passes — 142 tests, lint clean.

Live status page: https://21bcarlisle-arch.github.io/synthetic-enterprise/status/
(renders this file, auto-refreshes every 2 minutes).

Phase 4a (Fully Synthetic Ecosystem Bootstrap, per MASTER_BACKLOG) remains a
placeholder. The customer value layer, **Phase 4b**, is now **complete**
(all five sub-phases): 4b-1 cost to serve, 4b-2 churn model, 4b-3 CLV
(Shifted-BG via PyMC-Marketing), 4b-4 home move win rate, 4b-5 enterprise
value function.

- **4b-1 (cost to serve) — done**: `saas/cost_to_serve.py` + 5 tests added
  (89 total). See `docs/observability/PHASE_4b_SUMMARY.md`.
- **4b-2 (churn model) — done**: `saas/churn_model.py` + 7 tests added
  (96 total). Builds on Phase 3a's `score_experience_signals()`.
- **4b-3 (CLV via Shifted-BG) — done**: `saas/clv_model.py` + 9 tests added
  (109 total). Uses `pymc-marketing`'s `ShiftedBetaGeoModelIndividual` with
  method-of-moments priors (the portfolio's 6 accounts are all
  right-censored with 0 observed churns, making a direct MCMC `.fit()`
  numerically unstable — see Open Questions in `PHASE_4b_SUMMARY.md`).
- **4b-4 (home move win rate) — done**: `saas/home_move_win_rate.py` + 14
  tests added (132 total). Builds on 4b-2's `build_churn_risk()` output —
  "inverse of churn": when an account doesn't renew, the property's new
  occupant either stays with us (win) or switches (loss).
  `effective_retention_probability` combines churn and win probability per
  renewal point. See `docs/observability/PHASE_4b_SUMMARY.md`.
- **4b-5 (enterprise value function) — done**: `saas/enterprise_value.py` +
  10 tests added (142 total). Re-runs 4b-3's CLV projection on an
  "effective" churn probability (`churn_probability * (1 -
  win_probability)`, from 4b-4) — portfolio-wide sum of the result is
  `enterprise_value_gbp`. See `docs/observability/PHASE_4b_SUMMARY.md`.

**Phase 4b — fully complete, including full-portfolio re-run (2026-06-13)**:
`simulation/run_phase4b_on_phase2b.py` ran the full 9.5-year Phase 2b
settlement once and fed it through all five 4b modules. Portfolio-level
results: cost to serve £5,732.08, net margin post cost-to-serve £21,941.36,
enterprise value (sum of CLV, 6 accounts) £17,569.06. See "Follow-up — Full
Portfolio Re-run" in `docs/observability/PHASE_4b_SUMMARY.md` for the
per-account table and open questions (notably C3's low CLV relative to its
peers). `make check` passes (155 tests, lint clean).

**Two-way NTFY (2026-06-13)**: NTFY messages now carry priority/tags
(default+✅ for done, high+⚠️ for needs-input), and REVIEW_GATE notifications
include tap-to-reply "Approve, proceed"/"Hold" buttons (via Tailscale Funnel
+ `POST /respond`, single-use gate tokens) that relay your decision straight
into the session. See `docs/instructions/NTFY_TWO_WAY_PROTOCOL.md`.

Session watchdog: now auto-resumes on Claude Code usage-limit messages
without a "YES" confirmation (waits up to 6h, retrying every 15min) — only
crash/exit still requires confirmation. It also queues two tasks for the
independent background-worker (local Ollama, GPU) during the wait: a
forward-prep draft of 4b-4 (qwen3:14b) and an observability/housekeeping
digest (qwen2.5:7b) — both land as review-only drafts under
`docs/observability/`. See `background/session_watchdog.py`.

**Autonomous main loop — live**: the watchdog now detects when this Claude
Code session goes idle (pane unchanged for 5 minutes) and sends a
continuation instruction — check `MASTER_BACKLOG.md` for the next
incomplete (sub-)phase and `docs/staging/` for new instructions, proceed
autonomously. It pauses (NTFY only, no nudge) if the pane shows a
`REVIEW_GATE` or a permission prompt — those need Rich. Capped at 6
continuations/hour. This closes the loop: usage-limit pauses auto-resume,
crashes need a "YES", and now ordinary task-to-task handoffs no longer need
a prompt from Rich either.

`docs/staging/TASK_AUTOSTART.md` — complete, registered manually by Rich.
Cleared from staging.

**Phase 4c-1 (property and asset model) — done (2026-06-13)**: new
`saas/property_model.py` (`build_properties()`) gives each resi customer
(C1-C4) a physical property record: property type (mapped from
`home_type` — flat/semi/detached), EPC rating and bedroom count (from
`saas/customers.py`), heating system (`gas_boiler` for the four current
dual-fuel customers, `electric_storage` otherwise), occupancy pattern
(single/family/elderly), and an asset mix (EV/solar/smart meter). Occupancy
pattern and asset mix are seed-estimate constants pending the
`customer-archetype-data-enrichment` background task. 10 new tests (166
total), lint clean.

**Autoloop pane-capture debounce (2026-06-13)**: fixed a false-positive
pattern in `background/session_watchdog.py`'s `check_autoloop` — a
REVIEW_GATE/permission-prompt "waiting" state now requires
`AUTOLOOP_IDLE_CHECKS` consecutive non-matching pane captures before
clearing, so a one-off tmux viewport shift (cursor blink, redraw) can't
cause a duplicate notification when the same gate text reappears. Also added
a "Standard Completion Protocol" to `CLAUDE.md`: after NTFY + LATEST.md
update, always check `docs/staging/` and `MASTER_BACKLOG.md` before going
idle.

Open gates:
- **Phase 4b — REVIEW_GATE**: all five sub-phases (4b-1 through 4b-5) plus
  the full-portfolio re-run complete. See `docs/observability/PHASE_4b_SUMMARY.md`
  for full detail and open questions across the layer (seed-estimate
  constants throughout, point-estimate CLV prior, C3's low relative CLV).
  Awaiting Rich's review and direction on next steps — Phase 5 is currently
  a placeholder per MASTER_BACKLOG ("do not design in detail until Phase 4
  is complete").
**Phase 4c-2 (weather-driven demand) — done (2026-06-13)**: new
`simulation/demand_model.py` (`build_demand_shape()`) adjusts a base PC1/PC3
shape with heating/cooling degree days (UK 15.5C/22C bases, gas boiler vs
electric storage vs heat pump heating rates), an occupancy-pattern time-of-day
multiplier (single/family/elderly), and asset adjustments (EV overnight
charging block, solar generation netted off daytime demand via
`solar_generation_shape()`, floored at 0). Pure module — takes a daily mean
temperature and optional half-hourly irradiance as plain inputs rather than
importing `sim.weather_engine` directly, so existing weather-engine output
slots straight in. 20 new tests (186 total), lint clean. Not yet wired into
`simulation/settlement.py` — that integration (replacing the population-average
PC1/PC3 shape with `build_demand_shape()` per customer) is the natural next
step, either as part of 4c-2's wrap-up or folded into 4c-4 (bill generation).

Open gates:
- **Phase 4b — REVIEW_GATE**: all five sub-phases (4b-1 through 4b-5) plus
  the full-portfolio re-run complete. See `docs/observability/PHASE_4b_SUMMARY.md`
  for full detail and open questions across the layer (seed-estimate
  constants throughout, point-estimate CLV prior, C3's low relative CLV).
  Awaiting Rich's review and direction on next steps — Phase 5 is currently
  a placeholder per MASTER_BACKLOG ("do not design in detail until Phase 4
  is complete").
**Phase 4c-3 (weather -> wholesale price influence) — done (2026-06-13)**: new
`sim/weather_price_sensitivity.py` (`weather_sensitivity_multiplier()`)
applies a `COLD_SPELL_PRICE_MULTIPLIER` (1.10x, seed estimate) to the
synthetic forward price when the *lookback window's* average heating-degree-days
exceeds `COLD_SPELL_HDD_THRESHOLD` — Point-in-Time-safe, since it reads only
the same lookback window `sim/forward_curve.py` already uses for its
base/volatility calculation. `generate_forward_price()` gains an optional
`lookback_daily_mean_temps_c` parameter (defaults to `None` = no change,
fully backward compatible). Note: real Elexon SSP data already covers
2016-2025 per Historical Ground Truth law — there was no synthetic
historical curve to "replace"; this sub-phase's scope was the forward-price
sensitivity layer only. 6 new tests (192 total), lint clean.

**Per Rich's 2026-06-13 instruction** (now in `CLAUDE.md`): Phase 4c
REVIEW_GATEs are informational-only — NTFY each milestone, continue
automatically unless a genuine blocker or one-way-door decision arises.

**Phase 4c-4 (bill generation) — done (2026-06-13)**: new
`saas/bill_generator.py` (`generate_bill()`) aggregates a customer's monthly
settlement records into total consumption, total amount due, average unit
rate, and a clarity score in [0,1]. Clarity is reduced by consumption
volatility within the month (coefficient of variation of daily kWh — a
cold-spell-driven spike from 4c-2/4c-3 makes a flat-rate bill harder to
reconcile) and by "bill shock" (% change vs the previous month's total,
capped at 100% for the penalty). All current `fixed_1yr` contracts start at
clarity 1.0; unknown/future tariff types (e.g. ToU) default to 0.7. 9 new
tests (201 total), lint clean.

**Phase 4c-5 (payment behaviour) — done (2026-06-13)**: new
`saas/payment_behaviour.py` (`build_payment_behaviour()`) replaces
`saas/cost_to_serve.py`'s flat 2%/1% `BAD_DEBT_RATE` with a per-customer
credit-risk segment (low/medium/high/vulnerable), each with its own bad-debt
provision rate (0.5%-8% of revenue) and payment-timing delay (5-45 days
after bill period-end). C1-C4 seeded as low/medium/vulnerable/low (seed
estimates). Not yet wired into `cost_to_serve.py`/`portfolio_pnl.py` — same
"standalone, ready for integration" pattern as 4c-2's `demand_model.py`. 9
new tests (210 total), lint clean.

**Phase 4c-6 (contact and complaints) — done (2026-06-13), Phase 4c complete**:
new `saas/contact_model.py` (`build_contact_model()`) computes, per bill from
`saas/bill_generator.py`, a `contact_probability` driven by low
`clarity_score` and high `bill_shock_pct`, and a `complaint_probability` —
modelling `COMPLAINT_ESCALATION_DAYS = 14` as a fixed
`UNRESOLVED_AFTER_14_DAYS_RATE` applied to contact probability (no
per-contact resolution-date data exists yet to track an actual 14-day
clock). Portfolio-level `avg_complaint_probability` feeds a
`service_quality_score` in [0,1]. 12 new tests (222 total), lint clean. This
closes Phase 4c (physical simulation layer) — all six sub-phases (4c-1
property/asset model, 4c-2 weather-driven demand, 4c-3 weather→wholesale
price sensitivity, 4c-4 bill generation, 4c-5 payment behaviour, 4c-6
contact/complaints) are done. See `docs/observability/PHASE_4c_SUMMARY.md`
for full detail, integration status, and open questions.

Open gates:
- **Phase 4b — REVIEW_GATE**: all five sub-phases (4b-1 through 4b-5) plus
  the full-portfolio re-run complete. See `docs/observability/PHASE_4b_SUMMARY.md`
  for full detail and open questions across the layer (seed-estimate
  constants throughout, point-estimate CLV prior, C3's low relative CLV).
  Awaiting Rich's review and direction on next steps — Phase 5 is currently
  a placeholder per MASTER_BACKLOG ("do not design in detail until Phase 4
  is complete").
- **Phase 4c — REVIEW_GATE (informational)**: all six sub-phases (4c-1
  through 4c-6) complete. See `docs/observability/PHASE_4c_SUMMARY.md` for
  full detail and seed-estimate caveats. With 4b and 4c both complete,
  Phase 4's "core value drivers" prerequisite for Phase 5 is satisfied —
  Phase 4a remains a placeholder ("do not design in detail until Phase 3 is
  complete" — likely now satisfied too, but undesigned). Awaiting Rich's
  direction: Phase 4a, or Phase 5 design.

**Phase 4c full-portfolio re-run — done (2026-06-13)**:
`simulation/run_phase4c_on_phase2b.py` ran the full 9.5-year Phase 2b
settlement (10 accounts: 6 electricity + 4 gas) once, grouped settlement
records into 1,101 monthly bills via `build_monthly_bills()` (chronological,
per-customer bill-shock tracking), then fed them through 4c-5 (payment
behaviour) and 4c-6 (contact/complaints). Portfolio results: average clarity
0.923, average bill shock 10.9%, total bad-debt provision £2,016.30, avg
complaint probability 0.030, **service quality score 0.941**. Phase 2b
financials re-confirmed (net margin £13,646.21, treasury £21,829.17 →
£35,475.37 — a different point estimate from earlier re-runs, consistent
with the stochastic-trajectory caveat). 3 new tests (231 total), lint clean.
4c-2/4c-3 (which modify settlement inputs rather than consume its output)
remain the only items in the integration backlog — see "Follow-up — Full
Portfolio Re-run" in `docs/observability/PHASE_4c_SUMMARY.md` for the
per-account table and open questions (notably C5/C6's lower clarity, and
C5/C6/Cxg falling back to default credit-risk/property seed estimates).
