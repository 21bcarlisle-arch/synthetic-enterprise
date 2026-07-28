<!-- DISCOVER artefact — P2 (sanity-finding coverage audit). Doc-only. Mint: PLANNER_MINTED_sanity_finding_coverage_audit_2026-07-28. -->
# Sanity-Finding Coverage Map (P2 — every adjudicated-real finding → its remediation atom, or minted residue, 2026-07-28)

**What this is.** The ratified GAP2 method (`DIRECTOR_RULING_GAP_TRIAGE_RATIFIED_2026-07-28`) deferred
P2 — the coverage cross-check of the adjudicated-real sanity findings — to "a future tick." This is that
tick. For **each** finding in `docs/observability/sanity_adjudication_ledger.json` with
`state=adjudicated-real`, a **LAW-C independent read** (does an atom actually touch the finding's
*mechanism*, not merely match its name) yields either `covered_by: <slug + evidence>` or `uncovered`.
Every `uncovered` finding is minted as a remediation atom (named, not self-enacted).

**Scope note (R7 — act on real disk/git state).** The source list enumerated in the mint file was written
from a stale ledger snapshot (`audit:*` / `coldwalk:no_js_fallback` / `test_count_metric` etc.). The
**actual** ledger holds a different 15-key `adjudicated-real` set — audited below. The `open` (3) and
`adjudicated-false-positive` (8) rows are out of scope (they await the adjudicator, not the planner).

**R12/R10 binding.** The covered/uncovered COUNT below is a **diagnostic only** — never a score, never a
target. No finding was reclassified (real→false-positive, or real→covered) to shrink the uncovered count;
a "covered" verdict cites the mechanism the covering atom actually closes. Class closure (where minted)
extends the invariant/obligation library, not a one-instance patch (R10).

---
## Coverage table (15 adjudicated-real findings)

| # | finding_key (ledger) | verdict | covered_by / mechanism closed |
|---|---|---|---|
| 1 | `bill_to_ledger_linkage_2026_07_12` | **COVERED** | **E2 revenue-reconciliation** (`project_e2_revenue_reconciliation_hardened`) + **R14 basis-labels gate** (`generate_dashboard_data.py`). The finding *is* the settlement-basis (`total_net_gbp`) vs bill/ledger-basis (`derive_pnl`) divergence — its own evidence names it as the SAME divergence as row 5. R14 forces each figure to carry its clock (settled/billed/banked); E2 added the bidirectional lockstep (discovered⊆EXPECTED) over the /proof + /now net-margin doors. |
| 2 | `coldwalk:bad_debt_implausibly_low_through_2021_22_crisis` | **COVERED** | **W2 affordability charter** (`docs/design/CHARTER_W2_AFFORDABILITY.md`) + **dunning/debt reconciliation bridge** (RUNG-1 minted, `project_dunning_debt_provisioning_steer`) + harness measurement **`company/compliance/crisis_bad_debt_validator.py`** (live xfail, R12-clean: measures the gap, does not tune toward benchmark). Director-decided REAL (`AFFORDABILITY_AS_SIM_PHYSICS.md`): arrears must EMERGE from budget-meets-shock — the mechanism is charted + measured. |
| 3 | `coldwalk:c1_2_successor_acquisition_date_mismatch` | **UNCOVERED → MINT** | No atom touches the `acquisition_date` **semantic overload**. `grep` of staging/design/map finds none. The billing-anchor use is deliberate+correct; the *defect* is that `company/crm/customer_registry.py:133` writes `acquisition_date` straight into a column literally named `supply_start`, stamping a successor's real relationship-start 5y early. → **`PLANNER_MINTED_supply_start_semantic_separation_2026-07-28`**. |
| 4 | `coldwalk:cost_to_serve_cross_fuel_mismatch_same_household` | **COVERED** | Instance FIXED (`cost_to_serve_for_period()` takes a `commodity` param, divides by the correct per-fuel cadence) **AND** class-guarded by regression test **`tests/saas/test_cost_to_serve.py::test_gas_commodity_uses_gas_cadence_divisor`** (l.197, carries the finding key l.189) — a gas record no longer recovers only 365/17,520 of annual overhead. R10 class closure present (per-commodity cadence enforced, not a one-off). |
| 5 | `coldwalk:margin_reconciliation:portfolio_vs_ledger` | **COVERED** | **E2 revenue-reconciliation** (same as row 1). The three disagreeing net-margin figures are the commodity-only vs full double-entry bases; R14 basis-labels + E2 lockstep close the "no label distinguishing basis" gap. |
| 6 | `coldwalk:no_privacy_policy_page` | **COVERED** | **P3 — privacy policy page BUILT + live** (`project_privacy_policy_page_built`, poesys.net/privacy/, R11-verified, `a094c87b8`). |
| 7 | `coldwalk:payment_channel_dd_fail_contradiction` | **UNCOVERED → MINT** | LAW-C **name-match ≠ mechanism-match**: the payment-grid SOURCE 1+2 work SENSES aggregate collection gaps (regime detection + expected-collection recon) — it does **not** enforce the specific cross-generator invariant this finding names (a `standard_credit` customer cannot carry `dd_failed`). `grep` for any channel↔dd-fail consistency invariant returns empty. Two independently-dispatched generators (`household_segments.payment_channel_for_customer` vs `arrears_engine.payment_outcome`) were never cross-referenced. → **`PLANNER_MINTED_payment_channel_dd_consistency_invariant_2026-07-28`**. |
| 8 | `coldwalk:supplier_failure_count_inconsistent_2021_22` | **COVERED** | Instance FIXED (all 5 live-site mentions standardised to the hedged "around 30") **AND** single-source-guarded by **`tests/tools/test_generate_shadow_html.py::test_2021_22_crisis_supplier_failure_count_is_single_sourced`**. |
| 9 | `expert_hour:E1_ledger_double_entry` | **COVERED** | The LEGIBILITY gap (corp-tax triplet computed but never downstream) is **closed at the data surface**: `corporation_tax` + `profit_for_year` now in `site/data/company.json`; `corporation_tax`+`profit_before_tax`+`profit_for_year` in `site/data/dashboard.json` (grep-confirmed — zero occurrences when the 2026-07-11 finding was written). Class-level mechanism = **`SITE_evidence_pages_behind_nodes`** (map atom, evidence-on-business-surface, BUILD blocked_on director front-open). |
| 10 | `expert_hour:W3_1_price_cap_binding` | **UNCOVERED → MINT** | The atom (`W3_1_price_cap_binding`, L2, HARDEN-saturated) closes cap-*binding*; the Expert-Hour REAL GAP — cap table is **annual granularity** while the real Ofgem Default Tariff Cap moves 2–4×/yr and jumped ~54% at Apr-2022 mid-crisis — is **neither covered nor a declared simplification** (its own W3_1 `simplifications:` list records only the build + HARDEN re-verifies, not this intra-year gap; the finding explicitly distinguishes it from the accepted year-on-year ballpark). Net-new capability (sub-annual cap table), not a W3_1 duplicate. → **`PLANNER_MINTED_intra_year_price_cap_granularity_2026-07-28`**. |
| 11 | `harden_sweep:live_site:B3_hedge_tariff_alignment` | **COVERED** | The "verified in code, never on a customer surface" gap is closed at the data surface: `hedge`/`hedge_fraction`/`hedge_frac` fields now present in `site/data/customers/*.json` (grep-confirmed — zero matches when the finding was written). Class mechanism = **`SITE_evidence_pages_behind_nodes`**. |
| 12 | `harden_sweep:live_site:D1_bill_correctness` | **COVERED** | A rendered invoice view now exists on the public site (`site/customers/index.html` — VAT rendered, 5 occurrences; invoice content present) where the 2026-07-11 finding found none. Class mechanism = **`SITE_evidence_pages_behind_nodes`**. (Residual: `site/shadow/customers/` still renders 0 VAT — a narrower surface gap folded into the SITE-evidence atom, not a new mint.) |
| 13 | `harden_sweep:live_site:F3_obligations_register` | **COVERED** | Register content is live+substantive already; the two gap sub-parts are each on an existing track: per-row evidence/freshness passport → **`SITE_evidence_pages_behind_nodes`** + **`SURFACE_FRESHNESS_CLASS_FIX`** (staging/in_progress); cross-page test-count disagreement → the surface-freshness/single-sourcing class. |
| 14 | `population:unit_rate_vs_cap_band:C1g:2019` | **COVERED** | **RESOLVED** in the finding's own evidence (2026-07-11 standing-charge double-count fix): traced to a real defect — `bill_generator.py` re-added a second flat standing charge on top of the settlement-folded one, inflating the apparent per-kWh rate in low-consumption months exactly as flagged. |
| 15 | `population:unit_rate_vs_cap_band:C4:2024` | **COVERED** | Same root + same fix as row 14 (standing-charge double-count) — the finding's evidence marks it RESOLVED, shared mechanism with C1g. |

**Tally (diagnostic only, not a score — R12):** 12 covered, 3 uncovered → 3 remediation atoms minted.

---
## Minted residue (the 3 uncovered → remediation atoms, named not self-enacted)

1. **`PLANNER_MINTED_supply_start_semantic_separation_2026-07-28`** — finding_key `coldwalk:c1_2_successor_acquisition_date_mismatch`. Separate the term-schedule anchor (deliberate, keep) from the real relationship-start date so `customer_registry.supply_start` reflects actual supply start, not the predecessor's anchor.
2. **`PLANNER_MINTED_payment_channel_dd_consistency_invariant_2026-07-28`** — finding_key `coldwalk:payment_channel_dd_fail_contradiction`. A cross-generator consistency invariant (R10 class): a customer's `payment_channel` and its arrears-engine `dd_failed` events must be mutually consistent (non-DD channel ⇒ no DD-failure events).
3. **`PLANNER_MINTED_intra_year_price_cap_granularity_2026-07-28`** — finding_key `expert_hour:W3_1_price_cap_binding`. A sub-annual (quarterly / 6-monthly) Ofgem cap table so a Jan–Mar 2022 deemed customer clamps against the real period cap, not the full-year blend — OR, if the builder judges it not-worth-the-complexity, a **declared + measured-bound** simplification (no silent closure).

**Walls untouched.** R13: no baseline/curriculum value moved. PRODUCT-FIRST: the minted residue ranks among product atoms, never outranking a live product item on composite alone. No red retired to close — where a mint could resolve to `not-worth-the-complexity`, that stays a credited, argued, measured-bound outcome (§3 claim-status), never a silent closure.
