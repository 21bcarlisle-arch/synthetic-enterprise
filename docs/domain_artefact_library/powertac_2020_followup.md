# PowerTAC 2020 follow-up — rate-type taxonomy & lifecycle state machine vs actual code

**Status:** follow-up pass, completes the two ADAPT-verdict comparisons `powertac_2020.md` registered
but did not start ("Follow-up registered, not started this pass"). Read-only research; no code
changed. R9: every claim below is a direct file:line citation checked in this pass (either read
directly, or surfaced by a supporting Explore-agent pass whose specific citations were then
independently spot-checked by re-reading the cited files).

**What was compared:** PowerTAC's two ADAPT-verdict items (`powertac_2020.md` lines 62-71) —
(1) the tariff rate-type taxonomy (tiered / ToU / weekday-weekend / two-part / variable-with-notice /
sign-up-incentive / early-withdrawal-penalty) and (2) the tariff lifecycle state machine
(created→published→active→modified→expiring→revoked/KILLED) — against `company/billing/contract.py`
and the rest of this project's real tariff/contract-lifecycle code in `company/` and `saas/`
(and `simulation/renewals.py`, which directly feeds `saas/tariff_pricing.py`).

---

## Part A — Rate-type taxonomy

`company/billing/contract.py` itself (76 lines total) does not model rates at all — it is pure
date arithmetic on a `_CONTRACT_YEARS` dict (`fixed_1yr`, `fixed_2yr`, `variable`, `svt`, `flex`,
`hh`, lines 12-19) producing `contract_end_date`/`days_until_renewal`/`is_in_notice_window`. None
of PowerTAC's rate-type distinctions live in this file. But most of them exist elsewhere in the
codebase, reachable from the real pricing/billing call path:

| PowerTAC rate type | Present? | Evidence |
|---|---|---|
| Two-part (standing charge + unit rate) | **Yes, ubiquitous** | `saas/bill_generator.py:116-150` (`generate_bill`, `standing_charge_gbp`); `saas/non_commodity.py:108-149` (`standing_charge_rate`); `company/billing/dual_fuel_bill.py:34-53` (`FuelBillSection`); `company/billing/contract_manager.py:41-42`; `company/billing/economy7.py:53-83` |
| Time-of-use (rate varies by hour) | **Yes** | `saas/tariff_pricing.py:108-129` (`price_tou_tariff`, `TOU_PEAK_MULTIPLIER=1.50`/`TOU_OFFPEAK_MULTIPLIER≈0.786`, lines 111-112); `company/market/tou_periods.py:1-28` (`is_peak_period`: morning 07:00-11:00 + evening 16:00-20:00, settlement periods 15-22/33-40); `company/portal/app.py:193-199` (`_tou_band`); `company/pricing/tou_rate_card.py:29-62` (Octopus-Go-style overnight/standard/peak bands); Economy 7 day/night register (`company/billing/economy7.py:9-11,18-25,86-102`) is a real UK ToU variant already fully modelled with year-indexed rate tables |
| Weekday/weekend differentiation | **Yes, explicit** | `company/market/tou_periods.py:26-27` (`if dt.weekday() >= 5: return False` — weekends always off-peak); `company/portal/app.py:197` (`d.weekday()>=5  # weekends always off-peak`) |
| Variable rate with notice-of-change interval | **Yes, extensively modelled** — more thoroughly than PowerTAC's single `noticeInterval` field | `company/billing/tariff_variation.py` (full file: `NOTICE_DAYS=30` per Ofgem SLC 23.1 line 8, `VariationReason`/`VariationOutcome` enums lines 11-24, `is_adequate_notice()` line 48-49, `has_no_exit_fee_window()` line 51-53); `company/billing/tariff_change_log.py` (full file: SVT 30-day vs fixed-term 42-day notice split, lines 24-26); `company/crm/renewal_notice_register.py` (full file: SLC 22, 42-49 day window, `NoticeOutcome` enum lines 32-38 — `PENDING`/`SENT_ON_TIME`/`SENT_LATE`/`SENT_EARLY`/`NOT_REQUIRED`/`FAILED`); `company/pricing/price_transparency_register.py:50-51` (`_MIN_NOTICE_DAYS_ON_RATE_CHANGE = 30`); `simulation/renewals.py:33-36,108-110` (`NOTICE_DAYS = 42`, company prices 42 days before term start — the notice interval is load-bearing in the actual pricing mechanism, not just a compliance record) |
| Early-withdrawal / exit penalty | **Yes** | `company/billing/exit_fee.py` (full file: `calculate_exit_fee()` lines 39-79, waived within 42-day notice window or after contract expiry, `ExitFeeWaiveReason` enum lines 9-15 including `SUPPLIER_BREACH`/`CUSTOMER_DEATH`/`PROPERTY_EMERGENCY`); referenced by `company/crm/renewal_notice_register.py:52` (`exit_fee_gbp` field) and `company/pricing/price_transparency_register.py:64` |
| Sign-up incentive (welcome discount) | **No** | Not found anywhere in `company/` or `saas/`. `company/crm/onboarding_journey.py`'s "welcome" hits are the regulatory *Welcome Pack* document (SLC 14.2), not a price discount. No `welcome_discount`/`signup_bonus`/`introductory_rate` code exists. |
| Tiered / block usage rate (first-N-kWh priced differently from the rest) | **No** | All "tier" hits in the codebase are unrelated concepts: `company/crm/clv_calculator.py` margin tiers, `company/crm/customer_profitability_scorecard.py` PLATINUM/GOLD customer-value tiers, `company/billing/seg_portfolio.py` SEG export-tariff tiers (export-rate structure, not consumption-volume tiering). `saas/bill_generator.py:198-200` explicitly flags the adjacent gap in its own comment: *"the tariff engine has no multi-rate-per-day concept at all yet — registered separately, not attempted here"* — and even that (full ToU) is a bigger gap than block tiering, which doesn't exist at all. |

**Assessment:** this project already covers 5 of PowerTAC's 7 rate-type distinctions in real,
tested code, several (variable-notice, exit penalty) modelled in more UK-regulatory depth than
PowerTAC's generic version. The two genuine absences are sign-up incentives and consumption-tiered
(block) rates. Of those two, block/tiered domestic rates are not standard practice in the current
GB retail market (inclining-block tariffs were largely phased out; the live UK pattern is flat
unit rate, Economy 7 day/night, or ToU/Agile-style time bands — all three of which this project
already has) — so this is a low-value adoption candidate, not a real gap against UK reality. A
sign-up incentive/welcome-discount mechanism is a more plausible real-world gap (UK suppliers do
run these), but it is a **pricing/marketing feature**, not a rate-*type* distinction, and nothing
in the fetched PowerTAC source (`powertac_2020.md` lines 27-30) describes its mechanics beyond the
one word "incentives" — too thin to adopt a specific shape from; noted as a possible future
CRM/acquisition-pricing item, not a PowerTAC-derived one.

---

## Part B — Tariff lifecycle state machine

PowerTAC's lifecycle (`powertac_2020.md` lines 51-58): created → published → active/unexpired →
modified (`VariableRateUpdate`) → expiring (`TariffExpire`) → revoked (`TariffRevoke` → immediate
`KILLED`, subscribers must call `getRevokedSubscriptions()`/`handleRevokedTariff()` to migrate to
a successor or default tariff, fee if subscribers were still active).

**`company/billing/contract.py` itself has no state machine at all** — no status field, no enum,
no transition method. It computes `contract_end_date`/`days_until_renewal`/`is_in_notice_window`
purely from `acquisition_date` + `contract_type` + calendar arithmetic (lines 22-61). This is the
central finding of this comparison: the module this follow-up was asked to check is not "missing
a state or two" relative to PowerTAC — it doesn't model state at all, by design (it's a pure
date-math helper, not a lifecycle object).

**But the codebase does model tariff/contract state — just not in one place, and not wired to
`contract.py`.** At least three independently-valued `ContractStatus`-style enums exist:

1. `company/billing/contract_manager.py:10-15` — `ContractStatus`: `ACTIVE`, `IN_NOTICE`,
   `EXPIRED`, `CANCELLED`, `RENEWED`. Transitions: `serve_notice()` (lines 95-99, → `IN_NOTICE`),
   `expire_contract()` (lines 101-104, → `EXPIRED`). **`CANCELLED` and `RENEWED` are declared
   (lines 14-15) but no method in the file ever sets them** — confirmed by grep: each name
   appears exactly once, at its own declaration. Dead states, closest PowerTAC analogue to
   `KILLED`/successor-migration, unimplemented.
2. `company/crm/contract_exposure_register.py:31-36` — a second, differently-valued
   `ContractStatus`: `FIXED_TERM`, `STANDARD_VARIABLE`, `OUT_OF_CONTRACT`, `DEEMED`,
   `PENDING_RENEWAL`. Its own docstring (lines 1-23) explicitly narrates the real UK
   equivalent of PowerTAC's revocation/migration idea: *"On contract expiry, customers roll onto
   SVT... or Default Tariff Cap rate by operation of licence (SLC 22, 23)... until... the
   company agrees to transfer the customer to SoLR (Ph321)."*
3. `company/crm/customer_registry.py:88,153-160` — a third, SQLite-backed status column:
   `status TEXT NOT NULL DEFAULT 'active'`, validated in `update_status()` (lines 153-164) against
   exactly `("active", "churned", "pending")` — a narrower 3-value model again.

Plus event-level (not contract-level) status enums that partially cover PowerTAC's
`modified`/`expiring` transitions: `company/billing/tariff_variation.py:19-24` `VariationOutcome`
(`PENDING`/`ACCEPTED`/`REJECTED_SWITCHED_AWAY`/`REJECTED_STAYED`); `company/crm/renewal_notice_register.py:32-38`
`NoticeOutcome`; `company/crm/renewal_conversion.py` `RenewalOutcome` (`ACCEPTED`/`SWITCHED`/
`LAPSED`/`PENDING` — `LAPSED` is glossed *"Contract expired, no action — became deemed"*);
`company/pricing/price_transparency_register.py:43-47` `UpdateStatus`
(`PUBLISHED`/`PENDING`/`STALE`/`WITHDRAWN` — a *publication*-status enum, closest naming match to
PowerTAC's published/active/`KILLED` axis, but scoped to the comparison-site feed, not the
customer's actual contract).

**None of these five-plus enums share a vocabulary, and none is called from the other four.**
Checked by grep for cross-references (`contract_manager`, `contract_exposure_register`,
`price_transparency_register`, `renewal_notice_register`, `tariff_variation`,
`tariff_change_log`) across `company/`, `saas/`, `simulation/`, `tools/`, `background/`, and
`company/portal/`: **every one of these status-bearing modules is imported only by its own
dedicated unit-test file** (e.g. `tests/company/billing/test_contract_manager.py`,
`tests/company/crm/test_phase_co_contract_exposure.py`,
`tests/company/pricing/test_price_transparency_register.py`,
`tests/company/crm/test_renewal_notice_register.py`,
`tests/company/billing/test_tariff_variation.py`) — none is invoked from the actual live pricing
path (`simulation/renewals.py` → `saas/tariff_pricing.py` → `saas/bill_generator.py`, or the
portal, or `tools/generate_billing_ledger.py`). The one exception is
`customer_registry.update_status()`, which **is** called from `tools/generate_billing_ledger.py`
and its own test — the only one of these six modules with a real, non-test call site, and it uses
the narrowest 3-value model of all of them.

**Assessment:** this is not "PowerTAC has state X, we're missing it" — it's the opposite failure
mode. This project has *more* lifecycle-state machinery than PowerTAC's single `Tariff` object,
spread across at least six independent, mutually-unaware modules, most of which are standalone
regulatory-obligation registers (each correctly modelling one real SLC requirement) that were
never wired into the pipeline that actually prices and bills customers. The live pipeline itself
(`contract.py` + `simulation/renewals.py`) tracks no status at all — only a `tariff_type` string
per term and computed dates. PowerTAC's contribution here isn't a missing enum value; it's a
concrete existence proof that *one* small, closed state machine (5-6 states) can cover the whole
lifecycle a real tariff object needs, which is a genuinely useful design template for
consolidating this project's scattered status vocabulary — see the adoption candidate below.

---

## Concrete adoption candidate

**Adopt PowerTAC's small closed lifecycle (active → in-notice/expiring → renewed | revoked-with-migration)
as the target shape for consolidating this project's tariff/contract status representation**,
rather than adopting any single missing state in isolation. Concretely, a future phase should:

- Give the *live* pricing path (`simulation/renewals.py` / `company/billing/contract.py`) an
  actual status field for the first time — today it has none, only inferred dates — using
  `company/billing/contract_manager.py`'s `ContractStatus` vocabulary (`ACTIVE`/`IN_NOTICE`/
  `EXPIRED`/`CANCELLED`/`RENEWED`) as the starting point since it is the closest of the three
  existing enums to PowerTAC's shape, **but first implementing its two currently-dead states**
  (`CANCELLED`, `RENEWED` — declared at lines 14-15, never set by any method) so the enum's
  members are all actually reachable, matching PowerTAC's requirement that `KILLED` is a real,
  driven transition (`TariffRevoke`), not a decorative value.
- Fill the one genuine structural gap this comparison found relative to PowerTAC: **a
  supplier-initiated tariff-withdrawal-with-forced-successor-migration mechanism does not exist
  anywhere in `company/` or `saas/`.** `company/billing/tariff_products.py:26,140-151`
  (`withdrawal_date`) and `company/pricing/price_transparency_register.py:43-47`
  (`UpdateStatus.WITHDRAWN`) both only remove a product from the sales catalogue / comparison
  feed — neither migrates already-signed customers to a successor tariff, unlike PowerTAC's
  `TariffRevoke` → `getRevokedSubscriptions()`/`handleRevokedTariff()` pair. This project's own
  docstrings (`company/crm/contract_exposure_register.py` lines 1-23) already reference the real
  UK analogue (SoLR transfer, Ph321) as existing elsewhere in the codebase, so this is a
  domain-relevant gap, not a PowerTAC-only concern — worth registering as a named follow-up for
  whichever future phase builds supplier-initiated product withdrawal or SoLR-adjacent handling,
  rather than treated as closed by the catalogue-level `withdrawal_date` that already exists.

This is registered as a **candidate for a future phase**, not started here — per the task scope,
no code was changed in this pass.

## Provenance tag

**`generator-anchor`** only (per `powertac_2020.md`'s own tag, carried forward — this remains a
SIM/company-side tariff-generation design reference, not a company-observable fact, and per the
mutual-exclusivity rule cannot also serve as a `validator-anchor`).

## What this pass did not do

Did not touch `company/compliance/`, `docs/design/maturity_map.yaml`, or
`docs/observability/sanity_adjudication_ledger.json` (owned by concurrent agents). Did not assess
`company/crm/churn_model.py`/`churn_analytics.py`/`enriched_churn_estimate.py`/
`payment_churn_model.py`/`saas/churn_model.py` in depth (flagged by the supporting research pass
as out of this follow-up's scope — churn *modelling* is a different question from tariff/contract
*lifecycle state*). Did not re-attempt the SSRN PDF fetch `powertac_2020.md` flagged as blocked
(HTTP 403) — this pass's comparison used only the wiki-sourced lifecycle/rate-type detail already
cited in `powertac_2020.md`, which was sufficient for both comparisons above.
