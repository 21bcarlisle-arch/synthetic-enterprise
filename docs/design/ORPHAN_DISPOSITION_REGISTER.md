# The orphan disposition register

**Atom:** `KNIFE4_orphan_disposition` (lane `H_harness`, epoch 3, L0→L2)
**Serves:** KNIFE pass 4 of 4 — `docs/design/KNIFE_HOTSPOT_PASSES.md` §4
**Source of the population:** `python3 tools/capability_index.py --orphans` (AO1). The index is
the SOURCE — what is unwired. This register is the RULING — what we decided about it.
**Enforced by:** `python3 tools/capability_index.py --dispositions`
**Written:** 2026-08-09, from a measured walk of `main`

---

## 0. Why a ruling and not just a list

`--orphans` has been able to answer *what is unwired* since AO1 landed. It cannot answer *and what
did we decide about it*, and a standing list nobody has ruled on decays into wallpaper. That decay
has a price already paid: the no-caller class census (2026-08-09) found **13 instances in 13 days,
8 of them discovered by accident**. This register is that class's standing disposition — and per
MAKE_IT_STICK it is a mechanism, not an exhortation: a company-side orphan with no row here fails
`--dispositions`, and so does a row whose subject stopped being an orphan.

**There is deliberately no generator.** A new orphan must be ruled on by a judgement. Auto-stamping
each one with a default class would empty the ruling of content while leaving the count complete —
the exact fail-open shape this register exists to prevent.

---

## 1. The pass's own premise, and how the measurement refuted it

The atom named three dispositions and expected the population to divide between them: **wired** (a
caller existed and was missing), **retired-to-archive** (superseded — name the superseder), and
**kept-and-explained** (a library or entry point the index cannot see, which is a defect in the
index's caller detection and gets logged as one).

Before ruling on anything, that expectation was tested — because the third class is an accusation
against the index, and an accusation is worth measuring before it is acted on. Four independent
ways the index could be blind to a real caller, each checked against the tree:

| Blindness hypothesis | How it was tested | Result |
|---|---|---|
| Dotted-name string references (`importlib.import_module("company.x.y")`, a registry, `-m company.x.y`) | every non-orphan production module's full text searched for each of the 258 dotted names | **1 hit**, and it is a docstring EXAMPLE in `tools/internal_seam_verifier.py`, not a call |
| Dynamic loading (`walk_packages` / `iter_modules` / `__import__`) sweeping a package | grep across `company/ saas/ simulation/ sim/ tools/ background/ interface/` | **0** — every hit is inside the two verifiers that *detect* dynamic imports |
| Reference from a tracked NON-Python file (Makefile, config, template, JSON) | all 6,226 tracked non-`.py` files searched for each orphan's path and dotted name | **258 hit — and all of them are documentation.** `site/data/phases.json`, `docs/PROJECT_OVERVIEW.md`, `PRIORITIES.md`. A doc that mentions a module is not a caller |
| An entry point the `if __name__ == "__main__"` probe misses (a `main()` with no guard) | AST scan of all 258 | **0 define `main()`** |

**The index is not blind. The orphans are real.** `kept-and-explained` — the class that would have
carried the volume — is empty, and it is empty by measurement rather than by assumption.

The other two classes are near-empty for the same reason:

- **`wired`** requires a caller that *existed and was missing*. For these modules there is no
  consumer at all to have been missing one import.
- **`retired`** requires a named superseder. A symbol-overlap scan of all 258 against every wired
  or entry-point company module found exactly **one** pair above 50%:
  `company.market.imbalance_analytics` vs the wired `company.market.imbalance_ledger`. They share
  `ImbalanceDirection` and `ImbalanceRecord` — and the analytics module adds systematic-bias
  detection the ledger does not have. That makes it a **consolidation candidate, not a superseded
  copy**, and the atom's own wall is explicit that retirement may never be inferred from orphan
  status alone. It is ruled `unhooked` with the finding recorded on its row, and the consolidation
  is owed to `AO6_consolidation_rhythm`.

So the three named classes are kept — they are the right classes, and future orphans will land in
them — but they describe **0, 0 and 0** of today's population.

### The fourth class, and why it is not an escape hatch

What all 258 actually are: **real, tested capability with no consumer, because the consumer that
would drive it was never built.** They are `Phase XX` domain registers — Breathing Space
moratoria, Fair Value Assessments, SEG registers, theft risk scoring — carrying real regulatory
content, real dataclasses, and **258 of 258 carrying test evidence, across 334 distinct test
files**. Not one is untested dead code.

That is a fourth class, `unhooked`, and the honest thing is to name it rather than to force 258
modules into three boxes that do not fit them. The danger of a fourth class is obvious: it is the
box everything goes in, and a box everything goes in is a label. So **`unhooked` is falsifiable per
row** — it must nominate the consumer that would drive it, and `--dispositions` refuses:

- a nominated consumer that does not exist (`ABSENT REFERENT`);
- a nominated consumer that imports **nothing** from the orphan's own package
  (`DECORATIVE REFERENT`) — the nomination has to touch the package somewhere real;
- a `none:<package>` claim (below) for a package that turns out to have a consumer after all
  (`REFUTED REFERENT`).

The nomination is derived, not invented: it is the module that reaches the most **wired** modules
in the orphan's own package today. `company.billing` is driven by `company.portal.app`,
`company.regulatory` by `tools.generate_regulatory_data`, `company.crm` and `company.trading` by
`simulation.run_phase2b`. Those are the doors these registers would come through.

**Two packages have no door at all.** `company.carbon` (1 module) and `company.sustainability`
(4 modules) have **zero** external consumers — every module in them is an orphan, so there is no
wired sibling to nominate from. Those five rows carry `none:<package>`, which is a claim about the
tree and not an exemption: the check verifies the package really has no external consumer and
fires the moment one appears.

---

## 2. The count did not fall, and forcing it would have been the defect

The atom's exit reads: *every orphan carries a disposition; the count falls; nothing is deleted.*
The first and third clauses are met. **The second is not, and this pass declines to meet it.**

Given the measurement above, there are exactly three ways to make 258 fall today: delete (a
director wall — ARCHIVE, NEVER DELETE), archive without a superseder (forbidden by this atom's own
method — *retirement may never be inferred from orphan status alone*), or manufacture an import
that no consumer actually needs. All three are defects, and the third is the worst: it would move
the measurement rather than the code, which is the failure KNIFE pass 1 explicitly refused when it
declined to route a dependency through a package the walker does not walk.

R12 governs: the orphan count is a **diagnostic, never a target**, and driving it down to satisfy a
forecast is goal-seeking an output metric. LAW A says the same in the other direction: if an exit
criterion and the evidence disagree, **the criterion is wrong**. This is the second time in one day
that a KNIFE pass's own measurement has corrected the plan that scheduled it — §3a of
`KNIFE_HOTSPOT_PASSES.md` records the first — and it is recorded here rather than quietly smoothed
for the same reason as that one.

What this pass therefore delivers is the ruling and the mechanism that keeps it true: 258 rulings,
each with a falsifiable referent, and a check that fails on the 259th orphan the day it appears.
**The count falling is owed to the consumers being built** — which is what the nominated referent
column is *for*: it is a work list addressed to `AO6_consolidation_rhythm` and to whichever atom
builds each door, sorted by the door it would come through.

### Where the fall would come from, largest door first

| Nominated consumer | Orphans behind it | Packages |
|---|---|---|
| `simulation.run_phase2b` | 82 | `company.crm` 52, `company.trading` 20, `company.risk` 10 |
| `tools.working_day_guard` | 59 | `company.market` 59 |
| `tools.generate_regulatory_data` | 42 | `company.regulatory` 42 |
| `company.portal.app` | 33 | `company.billing` 33 |
| `saas.reporting.annual_report` | 20 | `company.finance` 20 |
| `background.fabric_gap_ledger` | 10 | `company.pricing` 10 |
| `simulation.churn_journey` | 4 | `company.core` 4 |
| `background.sanity_daemon` | 3 | `company.compliance` 3 |
| *no consumer exists* (`none:`) | 5 | `company.sustainability` 4, `company.carbon` 1 |

One line in that table is worth reading twice. **`tools.working_day_guard` is the largest single
door and it is not a business surface** — it is the module that reaches the most wired
`company.market` modules today, which is what makes it the derived nomination, and it is a *guard*.
That is a finding about `company.market`, not about the guard: a package of 59 unwired modules
whose most connected reader is a lint-style checker has no business consumer at all, and the
nomination is honest about naming the only thing that touches it. The same reading applies more
weakly to `background.fabric_gap_ledger` over `company.pricing`.

---

## 3. Nothing was deleted

No file was removed, moved or archived by this pass. The third exit clause is met trivially and
honestly: the measurement produced no justified retirement, so there was nothing to archive.

---

## 4. The register

`module | class | referent | reason`. The referent is the caller (`wired`, `explained`), the
superseder (`retired`), or the consumer that would drive it (`unhooked`).

<!-- ORPHAN-DISPOSITIONS
company.billing.annual_statement | unhooked | company.portal.app | no docstring; 1 test(s); no importer
company.billing.billing_dispute | unhooked | company.portal.app | Billing Dispute Resolution Book (Phase FC).; 2 test(s); no importer
company.billing.breathing_space_register | unhooked | company.portal.app | Debt Respite (Breathing Space) Register (Phase FY).; 2 test(s); no importer
company.billing.capacity_to_pay | unhooked | company.portal.app | Capacity-to-Pay (CtP) affordability assessment for customers in arrears.; 4 test(s); no importer
company.billing.contract_manager | unhooked | company.portal.app | Supply contract lifecycle management: terms, break clauses, price protection.; 2 test(s); no importer
company.billing.credit_balance_control | unhooked | company.portal.app | Undischarged credit-balance control (SLC 14 / Ofgem DD Market Compliance Review).; 1 test(s); no importer
company.billing.economy7 | unhooked | company.portal.app | no docstring; 2 test(s); no importer
company.billing.exit_fee | unhooked | company.portal.app | no docstring; 1 test(s); no importer
company.billing.fit_legacy_register | unhooked | company.portal.app | Feed-in Tariff (FiT) Legacy Register.; 2 test(s); no importer
company.billing.ic_invoice_dispute_register | unhooked | company.portal.app | I&C Invoice Dispute Register (Phase GE).; 1 test(s); no importer
company.billing.meter_assets | unhooked | company.portal.app | Meter asset management.; 1 test(s); no importer
company.billing.meter_dispute | unhooked | company.portal.app | no docstring; 1 test(s); no importer
company.billing.meter_points | unhooked | company.portal.app | Meter Point Administration Number (MPAN) and Meter Point Reference Number (MPRN) management.; 1 test(s); no importer
company.billing.moa_charges | unhooked | company.portal.app | Meter Operator Agent (MOA) charge management.; 1 test(s); no importer
company.billing.payment_behaviour | unhooked | company.portal.app | Customer payment behaviour analytics: timing, DD failure rates, lateness scoring.; 2 test(s); no importer
company.billing.payment_deferral | unhooked | company.portal.app | no docstring; 1 test(s); no importer
company.billing.payment_method_register | unhooked | company.portal.app | Payment Method Register — tracks how each account pays.; 1 test(s); no importer
company.billing.payment_plan | unhooked | company.portal.app | no docstring; 1 test(s); no importer
company.billing.payment_plan_adequacy | unhooked | company.portal.app | Payment plan adequacy: Ofgem Ability to Pay (ATP) compliance assessment.; 1 test(s); no importer
company.billing.ppm_warrant_register | unhooked | company.portal.app | PPM Installation Warrant Register (Phase FX).; 1 test(s); no importer
company.billing.prepayment | unhooked | company.portal.app | Prepayment meter (PPM) management.; 1 test(s); no importer
company.billing.renewal_engine | unhooked | company.portal.app | Renewal pricing engine.; 2 test(s); no importer
company.billing.revenue_protection_visit_register | unhooked | company.portal.app | Revenue Protection Visit Register — GS(SS)5 site investigation obligation.; 2 test(s); no importer
company.billing.seg_portfolio | unhooked | company.portal.app | Smart Export Guarantee (SEG) and domestic battery storage analytics.; 1 test(s); no importer
company.billing.seg_register | unhooked | company.portal.app | Smart Export Guarantee (SEG) Register.; 2 test(s); no importer
company.billing.smart_export | unhooked | company.portal.app | no docstring; 1 test(s); no importer
company.billing.smart_meter_analytics | unhooked | company.portal.app | Smart meter half-hourly consumption analytics: peak detection, seasonal profiling.; 1 test(s); no importer
company.billing.switching | unhooked | company.portal.app | Supplier switching request tracking.; 1 test(s); no importer
company.billing.tariff_change_log | unhooked | company.portal.app | Tariff change notification (TCN) management.; 1 test(s); no importer
company.billing.tariff_variation | unhooked | company.portal.app | no docstring; 1 test(s); no importer
company.billing.theft_indicator | unhooked | company.portal.app | Energy theft / loss indicator.; 1 test(s); no importer
company.billing.theft_risk_scoring_register | unhooked | company.portal.app | Energy Theft Risk Scoring Register (Phase GH).; 2 test(s); no importer
company.billing.whd_register | unhooked | company.portal.app | no docstring; 1 test(s); no importer
company.carbon.carbon_ledger | unhooked | none:company.carbon | E5 — the carbon three-ledger: the company's carbon P&L (SAVED / SPENT / NET).; 1 test(s); no importer
company.compliance.board_meeting_register | unhooked | background.sanity_daemon | Board Meeting Minutes Register (Phase DR).; 2 test(s); no importer
company.compliance.consumer_duty_board_report | unhooked | background.sanity_daemon | Consumer Duty Annual Board Report Register (Phase FW).; 1 test(s); no importer
company.compliance.fair_value_assessment_register | unhooked | background.sanity_daemon | Consumer Duty Fair Value Assessment Register (Phase GP).; 3 test(s); no importer
company.core.account_intelligence | unhooked | simulation.churn_journey | Account Intelligence Report (Phase EI).; 1 test(s); no importer
company.core.adr_register | unhooked | simulation.churn_journey | Architectural Decision Record (ADR) Register (Phase EE).; 1 test(s); no importer
company.core.event_ledger | unhooked | simulation.churn_journey | Event Ledger Core (Phase DZ).; 1 test(s); no importer
company.core.three_horizon_clv | unhooked | simulation.churn_journey | no docstring; 1 test(s); no importer
company.crm.acquisition_cohort | unhooked | simulation.run_phase2b | Customer acquisition cohort CLV analysis: cohort tracking, payback period.; 2 test(s); no importer
company.crm.acquisition_journey | unhooked | simulation.run_phase2b | no docstring; 1 test(s); no importer
company.crm.acquisition_strategy_book | unhooked | simulation.run_phase2b | Acquisition Strategy Intelligence Book.; 2 test(s); no importer
company.crm.ancillary_products | unhooked | simulation.run_phase2b | Smart home product bundle and ancillary revenue tracker.; 3 test(s); no importer
company.crm.behaviour_segment | unhooked | simulation.run_phase2b | Customer behaviour segmentation model.; 1 test(s); no importer
company.crm.campaign_tracker | unhooked | simulation.run_phase2b | Outbound contact campaign tracker: retention, renewal, and collections campaigns.; 2 test(s); no importer
company.crm.channel_roi | unhooked | simulation.run_phase2b | no docstring; 2 test(s); no importer
company.crm.churn_analytics | unhooked | simulation.run_phase2b | Churn waterfall and reason code analysis.; 1 test(s); no importer
company.crm.clv_calculator | unhooked | simulation.run_phase2b | Customer lifetime value (CLV) calculator.; 2 test(s); no importer
company.crm.clv_cohort_book | unhooked | simulation.run_phase2b | no docstring; 2 test(s); no importer
company.crm.clv_sensitivity_model | unhooked | simulation.run_phase2b | CLV Sensitivity Model (Phase DW).; 1 test(s); no importer
company.crm.complaint_root_cause_analyser | unhooked | simulation.run_phase2b | Customer Complaint Root Cause Analyser (Phase DS).; 1 test(s); no importer
company.crm.contact_centre_metrics | unhooked | simulation.run_phase2b | no docstring; 2 test(s); no importer
company.crm.contact_journey | unhooked | simulation.run_phase2b | Customer contact preferences and multi-channel communication management.; 2 test(s); no importer
company.crm.contact_log | unhooked | simulation.run_phase2b | no docstring; 2 test(s); no importer
company.crm.contract_exposure_register | unhooked | simulation.run_phase2b | Contract Exposure Register — tracks regulatory supply obligations.; 2 test(s); no importer
company.crm.conversation_log | unhooked | simulation.run_phase2b | no docstring; 2 test(s); no importer
company.crm.cos_process | unhooked | simulation.run_phase2b | no docstring; 2 test(s); no importer
company.crm.credit_assessment_register | unhooked | simulation.run_phase2b | Customer Credit Assessment Register (Phase DU).; 1 test(s); no importer
company.crm.credit_scoring | unhooked | simulation.run_phase2b | Customer credit scoring and risk tier classification.; 2 test(s); no importer
company.crm.customer_comm_preferences | unhooked | simulation.run_phase2b | Customer Communication Preference Register.; 2 test(s); no importer
company.crm.customer_profitability_scorecard | unhooked | simulation.run_phase2b | Customer Profitability Scorecard (Phase FK).; 1 test(s); no importer
company.crm.customer_retention | unhooked | simulation.run_phase2b | Customer Retention Offer Book — Phase AE.; 1 test(s); no importer
company.crm.decarb_recommender | unhooked | simulation.run_phase2b | no docstring; 2 test(s); no importer
company.crm.eep_book | unhooked | simulation.run_phase2b | no docstring; 4 test(s); no importer
company.crm.energy_profile | unhooked | simulation.run_phase2b | no docstring; 1 test(s); no importer
company.crm.fuel_poverty | unhooked | simulation.run_phase2b | no docstring; 1 test(s); no importer
company.crm.life_event_impact | unhooked | simulation.run_phase2b | no docstring; 1 test(s); no importer
company.crm.marketing_budget | unhooked | simulation.run_phase2b | no docstring; 2 test(s); no importer
company.crm.marketing_campaign_register | unhooked | simulation.run_phase2b | Direct Marketing Campaign Register (Phase DT).; 1 test(s); no importer
company.crm.microbusiness | unhooked | simulation.run_phase2b | no docstring; 1 test(s); no importer
company.crm.neighbourhood_comparison | unhooked | simulation.run_phase2b | no docstring; 1 test(s); no importer
company.crm.notification_prefs | unhooked | simulation.run_phase2b | Customer notification and communication preferences.; 1 test(s); no importer
company.crm.occupancy_register | unhooked | simulation.run_phase2b | no docstring; 1 test(s); no importer
company.crm.portal_analytics | unhooked | simulation.run_phase2b | no docstring; 4 test(s); no importer
company.crm.portfolio_repricing | unhooked | simulation.run_phase2b | Portfolio Repricing Action Book — Phase AC.; 2 test(s); no importer
company.crm.porting_loss_register | unhooked | simulation.run_phase2b | Porting Loss Register (Phase FL).; 1 test(s); no importer
company.crm.priority_services | unhooked | simulation.run_phase2b | no docstring; 1 test(s); no importer
company.crm.property_improvement | unhooked | simulation.run_phase2b | Property improvement event tracker.; 1 test(s); no importer
company.crm.renewal_conversion | unhooked | simulation.run_phase2b | Renewal Conversion Rate Book.; 1 test(s); no importer
company.crm.renewal_notice_register | unhooked | simulation.run_phase2b | Renewal Notice Register (Phase DQ).; 1 test(s); no importer
company.crm.renewals_book | unhooked | simulation.run_phase2b | no docstring; 4 test(s); no importer
company.crm.solr_intake | unhooked | simulation.run_phase2b | no docstring; 3 test(s); no importer
company.crm.solr_register | unhooked | simulation.run_phase2b | Supplier of Last Resort (SoLR) Register: tracks customer transfers from failed suppliers.; 1 test(s); no importer
company.crm.switch_analytics | unhooked | simulation.run_phase2b | no docstring; 5 test(s); no importer
company.crm.switching_cba | unhooked | simulation.run_phase2b | Switching Friction Cost-Benefit Analyser (Phase EJ).; 1 test(s); no importer
company.crm.switching_cost_model | unhooked | simulation.run_phase2b | Switching Cost Model (Phase DK).; 1 test(s); no importer
company.crm.switching_report | unhooked | simulation.run_phase2b | Customer gain/loss switching analytics: market share movement, churn tracking.; 2 test(s); no importer
company.crm.tariff_notification | unhooked | simulation.run_phase2b | Tariff change notification system: 42-day advance notice per Ofgem SLC 25B.; 3 test(s); no importer
company.crm.tpa_register | unhooked | simulation.run_phase2b | Third Party Authority (TPA) Register: customer-designated account representatives.; 1 test(s); no importer
company.crm.tpi_conduct_register | unhooked | simulation.run_phase2b | TPI Conduct Compliance Register (Phase GY).; 2 test(s); no importer
company.crm.vulnerability_index | unhooked | simulation.run_phase2b | Fuel poverty vulnerability index: scored triage for Ofgem obligations.; 2 test(s); no importer
company.finance.annualised_revenue_report | unhooked | saas.reporting.annual_report | Annualised Customer Revenue Report (Phase EU).; 1 test(s); no importer
company.finance.board_dashboard | unhooked | saas.reporting.annual_report | Integrated board KPI dashboard: the monthly view an energy supplier board reviews.; 2 test(s); no importer
company.finance.board_kpis | unhooked | saas.reporting.annual_report | no docstring; 2 test(s); no importer
company.finance.cash_flow_forecast | unhooked | saas.reporting.annual_report | no docstring; 2 test(s); no importer
company.finance.company_pl | unhooked | saas.reporting.annual_report | no docstring; 2 test(s); no importer
company.finance.corporation_tax | unhooked | saas.reporting.annual_report | Corporation tax provision: UK CT rates 2016-2025 and annual provision calculation.; 1 test(s); no importer
company.finance.credit_facility | unhooked | saas.reporting.annual_report | no docstring; 3 test(s); no importer
company.finance.credit_limit_book | unhooked | saas.reporting.annual_report | no docstring; 1 test(s); no importer
company.finance.customer_lifetime_revenue | unhooked | saas.reporting.annual_report | Customer Lifetime Revenue Register (Phase FN).; 1 test(s); no importer
company.finance.debt_age_analysis | unhooked | saas.reporting.annual_report | Debt Age Analysis Register (Phase FO).; 1 test(s); no importer
company.finance.payroll | unhooked | saas.reporting.annual_report | Staff headcount and payroll cost model: operational cost driver for company P&L.; 2 test(s); no importer
company.finance.period_reconciliation | unhooked | saas.reporting.annual_report | Period-end financial reconciliation: revenue-cost matching, settlement variances.; 2 test(s); no importer
company.finance.pnl | unhooked | saas.reporting.annual_report | Company Layer — P&L from Ledger Events.; 2 test(s); no importer
company.finance.portfolio_dashboard | unhooked | saas.reporting.annual_report | Customer Portfolio Profitability Dashboard (Phase EG).; 1 test(s); no importer
company.finance.portfolio_margin_sensitivity | unhooked | saas.reporting.annual_report | Portfolio margin sensitivity analyser — five-factor sensitivity table.; 2 test(s); no importer
company.finance.revenue_accruals | unhooked | saas.reporting.annual_report | Revenue accruals ledger: billed vs unbilled accrual for month-end close.; 5 test(s); no importer
company.finance.segment_profitability | unhooked | saas.reporting.annual_report | Customer Segment Profitability Analysis (Phase ES).; 1 test(s); no importer
company.finance.trade_finance | unhooked | saas.reporting.annual_report | Trade finance instrument registry: letters of credit, bank guarantees, parent guarantees.; 3 test(s); no importer
company.finance.treasury | unhooked | saas.reporting.annual_report | FI3 -- Treasury management: cash position, working capital, MCR headroom, and forward cash fl...; 1 test(s); no importer
company.finance.working_capital | unhooked | saas.reporting.annual_report | Working capital daily cash position: inflows, outflows, headroom monitoring.; 1 test(s); no importer
company.market.agreed_capacity_register | unhooked | tools.working_day_guard | Agreed Capacity Register (Phase GS).; 2 test(s); no importer
company.market.bsuos_ledger | unhooked | tools.working_day_guard | no docstring; 1 test(s); no importer
company.market.capacity_market | unhooked | tools.working_day_guard | Capacity Market participation: CM unit registration, auction, and obligations.; 2 test(s); no importer
company.market.capacity_market_register | unhooked | tools.working_day_guard | Capacity Market Revenue Register (Phase EX).; 1 test(s); no importer
company.market.cfd_levy | unhooked | tools.working_day_guard | CfD (Contracts for Difference) levy tracker.; 1 test(s); no importer
company.market.curve_monitor | unhooked | tools.working_day_guard | Wholesale forward curve anomaly detection.; 2 test(s); no importer
company.market.dadc_contract_register | unhooked | tools.working_day_guard | Data Aggregator / Data Collector (DA/DC) Contract Register.; 2 test(s); no importer
company.market.day_ahead_book | unhooked | tools.working_day_guard | no docstring; 1 test(s); no importer
company.market.dno_network_charge_dispute_register | unhooked | tools.working_day_guard | no docstring; 2 test(s); no importer
company.market.dso_flexibility_tender_register | unhooked | tools.working_day_guard | DSO Flexibility Tender Register.; 2 test(s); no importer
company.market.dsr_book | unhooked | tools.working_day_guard | no docstring; 5 test(s); no importer
company.market.dsr_portfolio | unhooked | tools.working_day_guard | Demand side response (DSR) event management: grid stress, customer curtailment.; 2 test(s); no importer
company.market.dtn_log | unhooked | tools.working_day_guard | Data Transfer Network (DTN) message log.; 1 test(s); no importer
company.market.duos_ledger | unhooked | tools.working_day_guard | no docstring; 1 test(s); no importer
company.market.embedded_network_register | unhooked | tools.working_day_guard | Embedded Network Supply Register (Phase DO).; 1 test(s); no importer
company.market.ev_demand_forecast | unhooked | tools.working_day_guard | EV Charging Demand Forecaster (Phase FS).; 1 test(s); no importer
company.market.flexible_asset | unhooked | tools.working_day_guard | Flexible asset dispatch: battery/pump storage for BM and triad avoidance.; 2 test(s); no importer
company.market.gas_imbalance_ledger | unhooked | tools.working_day_guard | no docstring; 1 test(s); no importer
company.market.gas_interruption | unhooked | tools.working_day_guard | Gas supply interruption risk: interruptibility, UK gas emergency, IGEM procedures.; 4 test(s); no importer
company.market.gas_network_ledger | unhooked | tools.working_day_guard | no docstring; 1 test(s); no importer
company.market.gas_otc_book | unhooked | tools.working_day_guard | Wholesale gas OTC trading book (NBP market).; 1 test(s); no importer
company.market.gas_storage | unhooked | tools.working_day_guard | Gas storage position: seasonal injection, withdrawal, and storage optimisation.; 1 test(s); no importer
company.market.grid_connection_queue_register | unhooked | tools.working_day_guard | Grid Connection Queue Register.; 2 test(s); no importer
company.market.hedge_performance | unhooked | tools.working_day_guard | no docstring; 3 test(s); no importer
company.market.hedging_schedule | unhooked | tools.working_day_guard | Commodity hedging schedule: forward delivery vs open position by month.; 5 test(s); no importer
company.market.hh_data_quality | unhooked | tools.working_day_guard | Half-hourly (HH) meter data quality checker.; 1 test(s); no importer
company.market.imbalance | unhooked | tools.working_day_guard | Imbalance price risk model.; 1 test(s); no importer
company.market.imbalance_analytics | unhooked | tools.working_day_guard | Settlement imbalance analytics: cash-out cost tracking, systematic bias detection.; 1 test(s); no importer; NEAREST DUPLICATE IN THE TREE - shares ImbalanceDirection and ImbalanceRecord with the wired company.market.imbalance_ledger (50% symbol overlap, the highest measured), but adds bias detection the ledger does not have, so it is not a superseded copy; consolidation is owed to AO6_consolidation_rhythm
company.market.interconnector_monitor | unhooked | tools.working_day_guard | Interconnector cross-border price exposure: NEMO, BritNed, IFA1/2, VikingLink.; 2 test(s); no importer
company.market.interconnector_monitor_register | unhooked | tools.working_day_guard | Wholesale Energy Market Interconnect Quality Register (Phase DP).; 1 test(s); no importer
company.market.interruptible_supply_register | unhooked | tools.working_day_guard | Interruptible Gas Supply Contract Register.; 2 test(s); no importer
company.market.intraday_book | unhooked | tools.working_day_guard | Intraday electricity trading book.; 1 test(s); no importer
company.market.llf_register | unhooked | tools.working_day_guard | Line Loss Factor (LLF) Register (Phase GL).; 1 test(s); no importer
company.market.load_forecast | unhooked | tools.working_day_guard | no docstring; 1 test(s); no importer
company.market.map_contract_register | unhooked | tools.working_day_guard | Meter Asset Provider (MAP) Contract Register (Phase GJ).; 2 test(s); no importer
company.market.market_report | unhooked | tools.working_day_guard | Ofgem domestic market report data.; 1 test(s); no importer
company.market.market_share_estimator | unhooked | tools.working_day_guard | Market Share Estimator — estimates supplier position in each segment.; 2 test(s); no importer
company.market.market_share_intelligence | unhooked | tools.working_day_guard | Market Share Intelligence (Phase EK).; 1 test(s); no importer
company.market.metering_contracts | unhooked | tools.working_day_guard | Metering services: Meter Operator (MOP) and Data Collector (DC) contracts.; 2 test(s); no importer
company.market.mpan_register | unhooked | tools.working_day_guard | no docstring; 1 test(s); no importer
company.market.mpas_registry | unhooked | tools.working_day_guard | MPAS supply point registry: MPAN/MPRN registration, gain/loss and objections.; 1 test(s); no importer
company.market.mprn_register | unhooked | tools.working_day_guard | no docstring; 1 test(s); no importer
company.market.network_charge_ledger | unhooked | tools.working_day_guard | Network charge pass-through ledger: TNUoS, DUoS, BSUoS tracking.; 2 test(s); no importer
company.market.network_charges | unhooked | tools.working_day_guard | Network Use of System (UoS) charges.; 1 test(s); no importer
company.market.portfolio_position | unhooked | tools.working_day_guard | no docstring; 1 test(s); no importer
company.market.ppa_book | unhooked | tools.working_day_guard | Power Purchase Agreement (PPA) book: long-term renewable offtake contracts.; 1 test(s); no importer
company.market.price_monitor | unhooked | tools.working_day_guard | Wholesale energy price monitor: alerts on spot/forward prices vs trigger levels.; 2 test(s); no importer
company.market.prosumer_balance_register | unhooked | tools.working_day_guard | Prosumer Balance Register (Phase EH).; 1 test(s); no importer
company.market.seasonal_demand | unhooked | tools.working_day_guard | Seasonal demand forecast: portfolio-level load profile for hedging decisions.; 1 test(s); no importer
company.market.settlement_reconciler | unhooked | tools.working_day_guard | M1 -- Elexon settlement interface: receive and reconcile settlement statements.; 2 test(s); no importer
company.market.shipper_code_register | unhooked | tools.working_day_guard | Xoserve Shipper Code Register.; 2 test(s); no importer
company.market.smart_meter_programme_register | unhooked | tools.working_day_guard | Smart Meter Installation Programme Register (Phase GI).; 2 test(s); no importer
company.market.smart_meter_rollout | unhooked | tools.working_day_guard | no docstring; 1 test(s); no importer
company.market.switch_governance | unhooked | tools.working_day_guard | Switching cooling-off and objection management: 14-day right, ET resolution.; 4 test(s); no importer
company.market.tariff_benchmarking | unhooked | tools.working_day_guard | Tariff Benchmarking Register (Phase EZ).; 1 test(s); no importer
company.market.tnuos_ledger | unhooked | tools.working_day_guard | no docstring; 1 test(s); no importer
company.market.tpi_commission_book | unhooked | tools.working_day_guard | Third-Party Intermediary (TPI) commission tracking for I&C customers.; 2 test(s); no importer
company.market.triad_notification_book | unhooked | tools.working_day_guard | Triad Notification Book — proactive I&C demand reduction for TNUoS Triad avoidance.; 3 test(s); no importer
company.market.uig_allocation_register | unhooked | tools.working_day_guard | Unidentified Gas (UIG) Allocation Register (Phase GN).; 2 test(s); no importer
company.pricing.break_even_assessor | unhooked | background.fabric_gap_ledger | Break-Even Tariff Assessor.; 1 test(s); no importer
company.pricing.ncc_forecast_register | unhooked | background.fabric_gap_ledger | Non-Commodity Cost (NCC) Forecast Register (Phase GW).; 2 test(s); no importer
company.pricing.price_elasticity | unhooked | background.fabric_gap_ledger | Price Elasticity Estimator — models customer churn response to tariff changes.; 2 test(s); no importer
company.pricing.price_transparency_register | unhooked | background.fabric_gap_ledger | Price Transparency Publication Register (Phase DL).; 1 test(s); no importer
company.pricing.renewal_pricing_engine | unhooked | background.fabric_gap_ledger | Renewal Pricing Engine — compute optimal renewal tariff for each customer.; 2 test(s); no importer
company.pricing.segment_profitability | unhooked | background.fabric_gap_ledger | Tariff Segment Profitability Book.; 1 test(s); no importer
company.pricing.standing_charge_assessor | unhooked | background.fabric_gap_ledger | Standing Charge Fairness Assessor (Phase FP).; 1 test(s); no importer
company.pricing.tariff_smoothing | unhooked | background.fabric_gap_ledger | no docstring; 1 test(s); no importer
company.pricing.tou_product_launch | unhooked | background.fabric_gap_ledger | ToU Product Launch Decision Engine -- Phase X.; 1 test(s); no importer
company.pricing.tou_rate_card | unhooked | background.fabric_gap_ledger | EV ToU Rate Card Optimiser -- Phase Y.; 1 test(s); no importer
company.regulatory.annual_obligations | unhooked | tools.generate_regulatory_data | Annual regulatory obligations report packaging ECO4, WHD, GSOP and Ofgem returns.; 3 test(s); no importer
company.regulatory.capacity_market | unhooked | tools.generate_regulatory_data | Capacity Market (CM) obligation management.; 1 test(s); no importer
company.regulatory.cca_verification_register | unhooked | tools.generate_regulatory_data | Climate Change Agreement (CCA) Verification Register (Phase GT).; 1 test(s); no importer
company.regulatory.cfd_levy_register | unhooked | tools.generate_regulatory_data | Contract for Difference (CfD) Levy Register (Phase FJ).; 1 test(s); no importer
company.regulatory.consumer_vulnerability_register | unhooked | tools.generate_regulatory_data | Consumer Vulnerability Duty Action Register (Phase DG).; 1 test(s); no importer
company.regulatory.desnz_returns | unhooked | tools.generate_regulatory_data | DESNZ supplier data returns and exception reporting.; 2 test(s); no importer
company.regulatory.ebrs_register | unhooked | tools.generate_regulatory_data | Energy Bill Relief Scheme (EBRS) Register.; 1 test(s); no importer
company.regulatory.ebss_register | unhooked | tools.generate_regulatory_data | Energy Bills Support Scheme (EBSS) Register.; 1 test(s); no importer
company.regulatory.eco_tracker | unhooked | tools.generate_regulatory_data | Energy Company Obligation (ECO) tracker.; 1 test(s); no importer
company.regulatory.ee_obligation_tracker | unhooked | tools.generate_regulatory_data | Energy efficiency obligation referral tracker: ECO4, GBIS, WHD, BUS.; 3 test(s); no importer
company.regulatory.energy_bill_support | unhooked | tools.generate_regulatory_data | no docstring; 1 test(s); no importer
company.regulatory.epg_reconciliation_register | unhooked | tools.generate_regulatory_data | Energy Price Guarantee (EPG) Reconciliation Register (Phase GC).; 1 test(s); no importer
company.regulatory.ets_registry | unhooked | tools.generate_regulatory_data | UK Emissions Trading Scheme (UKETS) allowance registry: purchase, allocation, surrender.; 2 test(s); no importer
company.regulatory.fuel_poverty | unhooked | tools.generate_regulatory_data | Fuel Poverty Indicator: customer fuel poverty risk assessment.; 1 test(s); no importer
company.regulatory.green_gas_levy_register | unhooked | tools.generate_regulatory_data | Green Gas Levy (GGL) Register (Phase FV).; 2 test(s); no importer
company.regulatory.ico_breach_register | unhooked | tools.generate_regulatory_data | ICO Data Breach Notification Register.; 1 test(s); no importer
company.regulatory.licence_application_register | unhooked | tools.generate_regulatory_data | Licence Application and Variation Register.; 2 test(s); no importer
company.regulatory.licence_monitor | unhooked | tools.generate_regulatory_data | Standard Licence Condition (SLC) monitoring.; 1 test(s); no importer
company.regulatory.licence_renewal_tracker | unhooked | tools.generate_regulatory_data | Supplier Licence Renewal Tracker (Phase EP).; 1 test(s); no importer
company.regulatory.network_code_modification_register | unhooked | tools.generate_regulatory_data | Network Code Modification Register (Phase GU).; 1 test(s); no importer
company.regulatory.ofgem_redress_register | unhooked | tools.generate_regulatory_data | Ofgem Redress Payment Register (Phase FZ).; 1 test(s); no importer
company.regulatory.ofgem_scorecard | unhooked | tools.generate_regulatory_data | Ofgem Supplier Performance Scorecard (Phase EF).; 1 test(s); no importer
company.regulatory.penalty_provision | unhooked | tools.generate_regulatory_data | Regulatory Penalty Provision Book (Phase EL).; 1 test(s); no importer
company.regulatory.price_cap_tracker | unhooked | tools.generate_regulatory_data | Price Cap Pass-Through Tracker (Phase EM).; 1 test(s); no importer
company.regulatory.priority_services_register | unhooked | tools.generate_regulatory_data | Priority Services Register (PSR) — consumer vulnerability tracking.; 2 test(s); no importer
company.regulatory.regulatory_breach_log | unhooked | tools.generate_regulatory_data | Regulatory Breach Log.; 2 test(s); no importer
company.regulatory.regulatory_dashboard | unhooked | tools.generate_regulatory_data | Phase 300 milestone: Regulatory Compliance Dashboard.; 1 test(s); no importer
company.regulatory.remit_book | unhooked | tools.generate_regulatory_data | no docstring; 1 test(s); no importer
company.regulatory.remit_surveillance_register | unhooked | tools.generate_regulatory_data | REMIT Market Abuse Surveillance Register (Phase GF).; 1 test(s); no importer
company.regulatory.renewable_obligation | unhooked | tools.generate_regulatory_data | no docstring; 1 test(s); no importer
company.regulatory.reporting_calendar | unhooked | tools.generate_regulatory_data | Regulatory reporting calendar: submission deadlines and overdue detection.; 2 test(s); no importer
company.regulatory.rggo_register | unhooked | tools.generate_regulatory_data | Renewable Gas Guarantee of Origin (RGGO) Register (Phase GV).; 1 test(s); no importer
company.regulatory.sar_register | unhooked | tools.generate_regulatory_data | Data Subject Access Request (SAR) Register.; 1 test(s); no importer
company.regulatory.seg_export_estimator | unhooked | tools.generate_regulatory_data | SEG Export Estimator — Phase R.; 1 test(s); no importer
company.regulatory.sfr_book | unhooked | tools.generate_regulatory_data | Supplier Financial Resilience (SFR) framework.; 1 test(s); no importer
company.regulatory.slc_compliance_tracker | unhooked | tools.generate_regulatory_data | Standard Licence Condition (SLC) compliance tracker.; 2 test(s); no importer
company.regulatory.solr | unhooked | tools.generate_regulatory_data | Supplier of Last Resort (SoLR) risk assessment.; 1 test(s); no importer
company.regulatory.solr_exposure | unhooked | tools.generate_regulatory_data | Supplier of Last Resort (SoLR) exposure: competitor failure, customer transfer pricing.; 2 test(s); no importer
company.regulatory.solr_levy_register | unhooked | tools.generate_regulatory_data | SoLR Levy Reconciliation Register (Phase ER).; 1 test(s); no importer
company.regulatory.statutory_accounts_register | unhooked | tools.generate_regulatory_data | Statutory Annual Accounts Register (Phase DJ).; 1 test(s); no importer
company.regulatory.supplier_fitness_register | unhooked | tools.generate_regulatory_data | Supplier Fitness and Propriety Assessment Register.; 3 test(s); no importer
company.regulatory.vulnerable_customer_register | unhooked | tools.generate_regulatory_data | Vulnerable Customer Register (Phase FA).; 1 test(s); no importer
company.risk.annual_board_pack | unhooked | simulation.run_phase2b | Annual Board Pack synthesiser — aggregates company-level risk signals.; 2 test(s); no importer
company.risk.capital_adequacy | unhooked | simulation.run_phase2b | Regulatory Capital Adequacy Assessment (Phase EV).; 2 test(s); no importer
company.risk.financial_resilience | unhooked | simulation.run_phase2b | Financial Resilience Assessment (FRA): Ofgem mandatory quarterly framework post-2022.; 1 test(s); no importer
company.risk.gas_procurement_policy | unhooked | simulation.run_phase2b | Gas Procurement Policy Book — Phase 309.; 1 test(s); no importer
company.risk.hedge_effectiveness | unhooked | simulation.run_phase2b | Hedge Effectiveness Assessment: IFRS 9 hedge accounting (80-125% band).; 1 test(s); no importer
company.risk.liquidity_stress_test | unhooked | simulation.run_phase2b | Liquidity Stress Test Book — models the combined cash drain from margin calls.; 3 test(s); no importer
company.risk.risk_appetite | unhooked | simulation.run_phase2b | no docstring; 5 test(s); no importer
company.risk.risk_committee_ledger | unhooked | simulation.run_phase2b | Risk Committee Decision Ledger — tracks and assesses risk committee interventions.; 2 test(s); no importer
company.risk.supplier_resilience_scorecard | unhooked | simulation.run_phase2b | Supplier resilience scorecard — Ofgem post-2022 financial fitness assessment.; 2 test(s); no importer
company.risk.var_monitor | unhooked | simulation.run_phase2b | no docstring; 1 test(s); no importer
company.sustainability.carbon_intensity_register | unhooked | none:company.sustainability | Carbon Intensity Register (Phase FD).; 1 test(s); no importer
company.sustainability.decarbonisation_score | unhooked | none:company.sustainability | no docstring; 1 test(s); no importer
company.sustainability.environmental_impact | unhooked | none:company.sustainability | Environmental Impact Register — Scope 3 downstream gas emissions.; 2 test(s); no importer
company.sustainability.tcfd_climate_risk | unhooked | none:company.sustainability | TCFD Climate Risk Financial Assessment (Phase DX).; 1 test(s); no importer
company.trading.credit_limits | unhooked | simulation.run_phase2b | Counterparty credit limit management.; 2 test(s); no importer
company.trading.credit_rating_book | unhooked | simulation.run_phase2b | Supplier credit rating model: wholesale counterparty assessment for trading.; 4 test(s); no importer
company.trading.forward_curve_confidence | unhooked | simulation.run_phase2b | Forward Curve Confidence Band (Phase ET).; 1 test(s); no importer
company.trading.gas_forward_curve | unhooked | simulation.run_phase2b | Wholesale Gas Forward Curve (Phase FR).; 1 test(s); no importer
company.trading.gas_market_monitor | unhooked | simulation.run_phase2b | Wholesale Gas Market Monitor (Phase FF).; 2 test(s); no importer
company.trading.imbalance_cashflow | unhooked | simulation.run_phase2b | Imbalance Cash Flow Register (Phase FT).; 1 test(s); no importer
company.trading.imbalance_charge_register | unhooked | simulation.run_phase2b | Imbalance Charge Register (Phase EN).; 1 test(s); no importer
company.trading.initial_margin_register | unhooked | simulation.run_phase2b | Initial Margin Register for OTC and cleared energy derivatives.; 2 test(s); no importer
company.trading.interconnector_booking | unhooked | simulation.run_phase2b | Interconnector Capacity Booking Register (Phase FQ).; 1 test(s); no importer
company.trading.net_open_position_register | unhooked | simulation.run_phase2b | Net open position register — tracks hedged vs unhedged retail commitment.; 2 test(s); no importer
company.trading.otc_margin_book | unhooked | simulation.run_phase2b | OTC derivative variation margin call tracking (ISDA CSA mechanism).; 2 test(s); no importer
company.trading.power_auction_monitor | unhooked | simulation.run_phase2b | Wholesale Power Auction Monitor (Phase FM).; 1 test(s); no importer
company.trading.risk_limits | unhooked | simulation.run_phase2b | Wholesale trading risk limits and position governor.; 1 test(s); no importer
company.trading.shape_risk_book | unhooked | simulation.run_phase2b | Wholesale Shape Risk Book (Phase EO).; 1 test(s); no importer
company.trading.trade_blotter | unhooked | simulation.run_phase2b | Wholesale trading journal (trade blotter).; 1 test(s); no importer
company.trading.trade_confirmation_register | unhooked | simulation.run_phase2b | Wholesale Market Trade Confirmation Register (Phase GR).; 1 test(s); no importer
company.trading.triad_exposure_register | unhooked | simulation.run_phase2b | Triad Exposure Register (Phase FG).; 1 test(s); no importer
company.trading.triad_response_book | unhooked | simulation.run_phase2b | Triad Demand Response Book (Phase FU).; 1 test(s); no importer
company.trading.wholesale_position_report | unhooked | simulation.run_phase2b | Wholesale Market Position Monthly Report (Phase DV).; 1 test(s); no importer
company.trading.wholesale_trading_mandate_register | unhooked | simulation.run_phase2b | Wholesale Trading Mandate Register.; 1 test(s); no importer
ORPHAN-DISPOSITIONS -->
