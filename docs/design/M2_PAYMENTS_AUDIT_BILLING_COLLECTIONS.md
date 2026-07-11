# M2 Payments Maturity Audit — Billing / Collections / Arrears / Metering cluster

Expert Hour simulation under a payments-operations veteran persona (estimated
billing, catch-up rebilling, back-billing law, arrears escalation, debt
referral, meter-read validation/disputes), run against 22 `company/billing/`
modules per `docs/design/THE_VALUE_CYCLE_FRAMING.md`'s M2 entry gate. A
parallel fork audited the DD/Bacs-rails-specific modules separately.

**Headline finding, more important than any single module verdict:** of the
22 modules audited, only **4** have any call site outside their own file and
tests (`get_collections_queue`, `calibrate_eac`, `validate_bills`,
`DualFuelBillBook` — via `company/portal/app.py` or
`tools/generate_billing_ledger.py`). The remaining **18** are real,
well-designed, correctly-cited register classes that are **completely
unwired** — never invoked by the actual simulation pipeline or any live
surface. This is "paper compliance": the code correctly models the real
Ofgem SLC/statutory regime in isolation, but none of it actually constrains
or reacts to what the simulation does. This is the single largest gap this
audit found, larger than any individual module's own maturity gap.

## Module table

| Module | One-line summary | Classification | Maturity verdict |
|---|---|---|---|
| `back_billing.py` | Ofgem SLC 31A 12-month back-billing cap, pro-rata write-off calc | RAILS-PHYSICS (statutory cap) | Correct cap math, real citation. **Wired** (referenced by `smart_meter_reconciliation.py`, `obligations_register.py`, `billing_dispute.py`, `account_adjustment_register.py`) but never actually invoked from the live billing/simulation pipeline itself — those are cross-references, not call sites from real data. |
| `collections.py` | SQLite-backed overdue-invoice aging queue (30/60/90+ tiers) | RAILS-PHYSICS (mechanical aging) | Simple, correct aging logic. **Wired** via `company/portal/app.py`. No escalation *action* linkage (doesn't itself trigger notices/referral) — by design, a pure query layer. |
| `debt_referral.py` | Mandatory debt-advice referral above a £200 threshold (SLC 27A-style) | COMPANY-LOGIC (policy threshold) + statutory trigger | Well-modeled. **Unwired** — no caller outside itself/tests. |
| `breathing_space_register.py` | Debt Respite Scheme (SI 2020/1311): 60-day standard + open-ended MH crisis moratorium | RAILS-PHYSICS (statutory timing) | Best-cited module in the set (real SI number, correct MH-crisis asymmetry, correct "interest resumes, not cancelled" behaviour). **Unwired.** |
| `winter_moratorium.py` | Nov-Mar domestic disconnection prohibition + PSR year-round protection | RAILS-PHYSICS (statutory calendar) | Correct year-wraparound month logic (`month>=11 or month<=3`). **Unwired.** |
| `disconnection_warning.py` | 3-warning + 28-day-notice mandatory sequence before disconnection | RAILS-PHYSICS (statutory sequence) | Correctly gates `can_disconnect()` on the full sequence + notice period. **Unwired.** |
| `capacity_to_pay.py` | Affordability assessment → repayment plan / PPM / write-off recommendation | COMPANY-LOGIC (policy engine) | **Domain-sense finding:** recommends `PPM_CONVERSION` for vulnerable customers in fuel poverty — this is the *opposite* of the real 2023 regulatory direction (Ofgem tightened forced-PPM rules for vulnerable customers specifically, following well-publicised harm cases; PPM self-disconnection risk is a fuel-poverty *harm*, not a *remedy*). Also conflates "energy debt as % of annual income" with the real fuel-poverty definition (energy *spend* as % of income) — a specific, checkable metric mismatch, not vague hand-waving. **Unwired.** |
| `payment_deferral.py` | Hardship/COVID/job-loss payment deferral book with repayment tracking | COMPANY-LOGIC (discretionary) | Clean, no named regulatory citation (deferrals are supplier-discretionary, appropriately). **Unwired.** |
| `meter_read_validation.py` | Reversal/transposition/outlier detection on a single read pair | RAILS-PHYSICS (data-quality rules) | **No meter-rollover handling** — a mechanical meter rolling from e.g. 99999→00000 would be flagged as `REVERSAL` (a real, common false-positive class in actual billing ops). **Unwired.** |
| `meter_dispute.py` | Customer meter-read dispute lifecycle (open/review/resolve) | COMPANY-LOGIC (process) | No SLA/deadline modeling for resolution (real MPAS/ECOES-adjacent disputes have expected timeframes) — register-only. **Unwired.** |
| `metering_exception.py` | No-read/consecutive-estimate/objection exception tracking, SLC 22/22.3 | RAILS-PHYSICS (BSC/SLC rules) | Correctly models the 2-consecutive-estimate trigger and 4-month objection window. **Unwired.** |
| `eac_calibration.py` | Recalibrates EAC from billing history vs acquisition-time estimate | COMPANY-LOGIC (estimation) | **No seasonal weighting** — a linear `total_kwh/days*365.25` annualisation is biased if the lookback window happens to sample mostly summer or winter months; real EAC calibration needs a full annual cycle or seasonal adjustment. **Wired** via `company/portal/app.py`. |
| `pre_bill_validation.py` | Tier-1 pre-issue bill gate (VAT-by-segment, consumption plausibility) | COMPANY-LOGIC (validation gate) | Mature, self-documents its own known follow-up gap (no auto-retry/GSOP trigger for held bills) rather than silently omitting it. **Wired** via `tools/generate_billing_ledger.py`. |
| `invoice.py` | SQLite invoice artefact engine (schema, create, retrieve, payment status) | RAILS-PHYSICS + COMPANY-LOGIC (mixed) | `issue_date = period_end` (same-day dispatch) — real supplier billing has a read→calculate→dispatch lag of several days, not same-day. `PAYMENT_TERMS_DAYS=14` is short vs common 14-28-day UK practice (not wrong, just worth naming as a specific assumption). **Wired** (the invoice DB backing `collections.py`/`eac_calibration.py`). |
| `dual_fuel_bill.py` | Unified dual-fuel statement aggregating elec+gas invoices by period | COMPANY-LOGIC (presentation) | Correct SME VAT threshold logic (33 kWh/day, 5%/20% split). **Wired** via `company/portal/app.py`. |
| `annual_statement.py` | SLC 31B annual statement (consumption/cost/tariff summary + saving estimate) | RAILS-PHYSICS (statutory annual duty) | Correct citation, correct year-over-year mechanics. **Unwired.** |
| `tariff_variation.py` | SLC 23.1 30-day rate-change notice tracking, fee-free switch window | RAILS-PHYSICS (statutory notice) | Correct notice-period math. **Unwired.** |
| `renewal_engine.py` | Standalone renewal-quote generator (1yr/2yr fixed, SVT) from a spot price | COMPANY-LOGIC (pricing) | **Fully orphaned** — hardcodes its own margin targets/standing charges completely independent of the REAL renewal pricing path (the VaR-hedge-driven logic in `simulation/run_phase2b.py` + `company/trading/hedge_decision.py`). Two parallel, disconnected renewal-pricing implementations exist in this codebase; only one is ever used. |
| `switching.py` | Supplier-switch request tracking, 10-working-day objection window | RAILS-PHYSICS (DTN/MPAS process) | **Docstring says "10 working days," constant is `_OBJECTION_WINDOW_DAYS = 14`** (calendar, not working days) — a real, checkable mismatch between the documented rule and the code. Also calls `date.today()` directly inside `is_objectable` rather than accepting an `as_of` parameter — a point-in-time-blindfold risk pattern (see below). **Fully orphaned.** |
| `account_closure.py` | Final-bill/deposit/debt-referral closure pipeline, SLC 21B 42-day deadline | RAILS-PHYSICS (statutory deadline) | Correct citations (SLC 21B final bill, SLC 12 deposit return). `closure_summary()` calls `dt.date.today()` internally instead of accepting `as_of` — same point-in-time pattern as `switching.py`. **Unwired.** |
| `account_adjustment_register.py` | Goodwill/back-billing/redress one-off adjustments with tiered approval | COMPANY-LOGIC (approval workflow) | Well-designed, cites Consumer Duty 2023 correctly, cross-references its own siblings by name. **Unwired.** |
| `billing_dispute.py` | Formal dispute lifecycle, SLC 18.7 (3-day ack) / SLC 18.9 (8-week final response) | RAILS-PHYSICS (statutory deadlines) | Correctly gates disconnection during genuine disputes. Properly accepts `as_of` everywhere (no wall-clock anti-pattern). **Unwired.** |

## Simplifications register

- **The 18-of-22 unwired-module gap** (headline finding above) — every
  module below is additionally affected by this; listed once here rather
  than repeated per row.
- `capacity_to_pay.py`: recommends PPM conversion for vulnerable
  fuel-poverty customers, contradicting the real 2023 regulatory direction
  restricting forced PPM for vulnerable customers.
- `capacity_to_pay.py`: `energy_share_of_income_pct` computes debt-to-income,
  not the real fuel-poverty definition of energy-spend-to-income.
- `meter_read_validation.py`: no meter-rollover detection (a 5-digit
  mechanical meter wrapping 99999→00000 reads as a false REVERSAL).
- `eac_calibration.py`: linear annualisation with no seasonal weighting —
  biased if the lookback window doesn't span a full year.
- `invoice.py`: `issue_date = period_end` (no real read→calculate→dispatch
  lag); `PAYMENT_TERMS_DAYS=14` is on the short side of common UK practice.
- `renewal_engine.py`: fully orphaned, duplicate renewal-pricing logic
  disconnected from the real VaR-hedge-driven pricing path.
- `switching.py`: docstring/constant mismatch (10 working days vs 14
  calendar days); uses `date.today()` instead of an `as_of` parameter.
- `account_closure.py`: `closure_summary()` uses `date.today()` instead of
  an `as_of` parameter — same point-in-time anti-pattern class the Epoch-2
  framing's "as-of interfaces" work exists to eliminate, found here outside
  the pricing/hedging path it was originally scoped to.
- No SLA/deadline modeling in `meter_dispute.py` (real disputes have
  expected resolution timeframes; this register tracks status only).

## Verdict on M2 shape

**HARDEN-EXISTING, do not rebuild — but "harden" here means "wire in," not
"improve the modules themselves."** The individual modules are, module for
module, some of the most carefully regulatory-cited code in this codebase —
real SLC numbers, real statutory instrument citations, correct edge-case
handling (MH-crisis moratorium asymmetry, winter-period year-wraparound,
back-billing pro-ration). Rebuilding them would waste real, correct domain
modeling. The actual M2 gap is integration, not design: 18 of 22 modules are
call-site-less. M2's real work is threading live simulation events (arrears
accrual, meter reads, closures, disputes) into these already-built registers
— the same "sim loop drains events, not steps" primitive M1 is building for
the pricing/hedging path applies here too, and this cluster is arguably a
*cheaper* place to prove that event-driven pattern first, since the
compliance logic already exists and only needs a live event source. The two
`date.today()` instances (`switching.py`, `account_closure.py`) should be
fixed to accept `as_of` as part of the same M1 as-of-interface generalisation,
not left for later — they're small, mechanical, and exactly the bug class
the framing is trying to eliminate everywhere.
