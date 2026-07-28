<!-- SUPERVISOR_DRAW: self-drawable -->
# [PLANNER-MINTED] — P2: coverage audit of the 15 adjudicated-real sanity findings → mint the uncovered residue (2026-07-28)

**Source:** `docs/design/FIRST_RANKED_GAP_LIST.md` §2 product-lane row **P2** and §4 ("the
already-remediated sanity findings → **verify-then-mint only the uncovered ones later** (no
duplication)"), which the ratified GAP2 method (`DIRECTOR_RULING_GAP_TRIAGE_RATIFIED_2026-07-28.md`)
put on the ranked backlog but explicitly deferred to "a future tick." This is that tick.

**Why this and not a rest-with-proof:** the RUNG-7 rest premise is FALSE while any un-minted,
non-walled ratified-goal next-step exists. P2 is exactly that — a ranked mint-set row that is neither
minted nor walled: the ranked list minted its cheap/net-new rows (M1, M5, P3, M2, M3-delta) and left
P2 as named-but-uncovered work. So the honest action is MINT, not rest.

**Provenance:** RUNG-7 planner mint from the ratified backlog's own deferred disposition. No existing
atom performs the coverage cross-check (`grep` of staging/design finds none). Distinct from each
individual remediation atom: this atom audits the *set* of 15 for silent gaps, then mints the residue.

**Serves:** DIRECTOR_AXES v1 **#3 Believability** (a supplier carrying adjudicated-real billing/margin
defects fails the 20-year-veteran smell test) and **#2 Segmentation/customer truth**
(cost-to-serve cross-fuel, unit-rate-vs-cap-band are per-customer truth defects). Also the
coupled-triad law "the gap is the score": an adjudicated-real finding with no remediation atom is an
unmeasured gap masquerading as handled.

**Fidelity gained (one sentence):** a proven-complete map from every adjudicated-real customer/billing
defect to its remediation atom — closing the route by which a real, practitioner-visible defect sits
adjudicated-real yet silently un-worked.

---
## The 15 adjudicated-real findings (from `docs/observability/sanity_adjudication_ledger.json`, state=`adjudicated-real`)
```
audit:gas-kwh-unit                              coldwalk:margin_reconciliation:portfolio_vs_ledger
audit:high-consumption                          coldwalk:no_js_fallback_rendering
audit:vat-mismatch                              coldwalk:no_privacy_policy_page          [P3 — BUILT, privacy page live]
bill_to_ledger_linkage_2026_07_12               coldwalk:payment_channel_dd_fail_contradiction
coldwalk:bad_debt_implausibly_low_through_2021_22_crisis   coldwalk:supplier_failure_count_inconsistent_2021_22
coldwalk:bill_shock_c1_2018_annual_vs_monthly_scale_mismatch   coldwalk:test_count_metric_self_contradiction
coldwalk:c1_2_successor_acquisition_date_mismatch   population:unit_rate_vs_cap_band:C1g:2019
coldwalk:c2_tariff_vs_svt_extreme_yoy_swing     population:unit_rate_vs_cap_band:C4:2024
coldwalk:cost_to_serve_cross_fuel_mismatch_same_household
```
(The 3 `open` rows are NOT in scope — they await the adjudicator, not the planner. The 8
`adjudicated-false-positive` rows are NOT in scope.)

## Known-covered (do NOT re-mint — verify the linkage holds, then record it)
- `no_privacy_policy_page` → **P3, BUILT** (privacy page live, R11-verified).
- `margin_reconciliation:portfolio_vs_ledger` → **E2 revenue-reconciliation** (hardened, R15 both-ways).
- `payment_channel_dd_fail_contradiction` → **payment grid SOURCE 1+2** (regime detection + expected-collection recon).
- `bad_debt_implausibly_low_through_2021_22_crisis` → **dunning/debt reconciliation bridge** (RUNG-1 minted).
- `E1 ledger double-entry` family → **D5 ledger non-finite / E1** hardened family.
- `unit_rate_vs_cap_band:*` → **population coverage** infra (region R10 closed).

## Exit criteria (DISCOVER, doc-only)
- A coverage table: **each of the 15** → `{covered_by: <atom/mint slug + evidence>, OR uncovered}`.
  "Covered" means an atom exists whose scope demonstrably addresses the finding's mechanism — a
  LAW-C independent read (not a name match; the atom must actually touch the defect).
- For every **uncovered** finding: mint a remediation atom **autonomously** (a defect fix is a
  mint-direction move — GAP2 §2, autonomous), ranked among product-lane atoms per the ratified method,
  each carrying its finding-key and the mechanism it closes. Name them, do not self-enact closures.
- **R12/R10:** the covered/uncovered COUNT is a diagnostic only — never a score, never a target; and
  no finding may be reclassified (real→false-positive, or covered) to shrink the uncovered count.
  Closure of an uncovered *class* extends the invariant/obligation library, not a one-instance patch (R10).

## Walls untouched
- **R13:** no baseline/curriculum value moved. A finding whose closure needs a director scope/curriculum
  call is tagged `blocked-on-director` and escalated as `[ACT]`, never worked around.
- **PRODUCT-FIRST:** minted residue ranks among product atoms; never outranks a live product item on composite alone.
- **No red-retirement to close:** an honest red left open with a better-measured bound is a legitimate
  `not-worth-the-complexity` outcome (credited), not a silent closure (§3 claim-status defect).

## Lane / level / deps
- **Lane:** `L3 DISCOVER` (doc-only audit → `docs/design/SANITY_FINDING_COVERAGE_MAP.md`; residue mints to `docs/staging/`).
- **Deps:** none blocking — the ledger and the atom map are both present now. Self-drawable.
