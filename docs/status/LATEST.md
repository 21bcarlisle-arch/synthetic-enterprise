# Latest Status (mobile snapshot)

This file is served by `/ui/status` on the file API for quick mobile checks.
For full detail see `STATUS.md` at the repo root.

**Share with Claude.ai**: paste this URL into a claude.ai chat and Claude
will fetch the live content directly — no copy/paste needed, always
up to date with the latest push to `main`:
https://raw.githubusercontent.com/21bcarlisle-arch/synthetic-enterprise/main/docs/status/LATEST.md

Last updated: 2026-06-14T00:25:00Z

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
