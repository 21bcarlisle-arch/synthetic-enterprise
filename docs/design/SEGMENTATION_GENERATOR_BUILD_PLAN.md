# Segmentation generator BUILD plan — verified against live source

**Status:** BUILD-open (director console 2026-07-21). Grounds every step in a code-read verification pass (file:line against live source). Governed by `SEGMENTATION_RECONCILIATION_FRAME.md` (one taxonomy, knee-arbitrated, §0 canonical wall ruling). Additive / zero-blast-radius / wall-honouring.

## 1. Verified inventory reality (the starting point)
The one taxonomy has 12 axes; **only 6 are generated in the sim today**, and the schema's headline attitude/adoption axes are largely absent:

| Generated (SIM truth exists) | How | Absent — NO generator |
|---|---|---|
| tenure | `household_segments.py:196`, independent draw | **cars, nssec, green_stance, price_sensitivity, channel_pref, home_battery** |
| accommodation, heating_fuel | `household.py`, joint-by-mapping off `home_type` | |
| region | `population_draw.py:111` placeholder `UNKNOWN_SYNTHETIC` (synthetic customers) | |
| solar_PV, EV | `household.py` baseline deterministic + `adoption_geography.py` spatially-correlated aggregate | |

**The largest already-wired joint block** (verified live, not doc): the W2_4 affordability spine `household_budget.py:306` and its three coupled consumers — W2_7 ability (`willingness_classification.py:44`), W2_8 self-rationing (`self_rationing.py:281`), W2_10 organisation↔budget 60/40 (`dd_attribution.py:286`). RNG-substream discipline verified (named sha256) on the modern atoms; the older `household_segments.py` axes use `random.Random(f"{name}_{cid}")` (stable but not the named-substream convention — fold carefully). **The tenure→adoption recoupling is NOT wired in code** (a BUILD aspiration, FRAME §5).

## 2. The wall map (§0 canonical ruling) — priors vs discovery
| Public PRIOR (company starts here) | DISCOVER via interaction | NO company observable (hidden-truth only) |
|---|---|---|
| tenure, accommodation, cars, nssec, region (census); heating_fuel (EPC + gas-MPRN — the one Need axis readable per-account) | price_sensitivity (rate-change churn response, `get_churn_estimate`); EV (overnight HH load, `get_settlement_data`); solar (net export/SEG); channel_pref (contact channel used) | green_stance; nudge framing/tone susceptibility (only via A/B outcome experiments, never clustering); CO₂ salience; home_battery (~unobservable) |

## 3. BUILD sequence (additive, wall-honouring — cohort label NEVER crosses `sim_interface.py`)
1. **SIM cohort draw** — `assign_cohort(customer_id, base_seed)` in `population_draw.py` on a NEW named salt of the existing `W2_2_population_draw` substream, **default OFF** so `SyntheticCustomer` output is byte-identical. Sample the observed block from the fused `P(T)P(A|T)P(C|T)P(S|T)`, pin heating_fuel to region, cross the `assumed` axes.
2. **Wire tenure→adoption gating (SIM)** — one canonical cohort `tenure`; `has_solar`/`has_ev`/heat-pump *eligibility* reads it (renter-agency gate). ⚠ **Reconcile the two tenure representations first** (`household_segments.py:196` independent draw vs implicit `home_type` tenure in `household.py`); keep `tenure_for_customer` as fallback for the hand-authored + SYN customers (determinism, 370 test refs). Gating STRENGTH is an R13 call (§5).
3. **Company discovery module (COMPANY)** — new `company/analytics/cohort_discovery.py` clustering the company's OWN inputs into *believed* cohorts: EPC/census priors + interaction observables read ONLY through `sim_interface.py`. MUST NOT import any `simulation.*` trait module. green_stance/susceptibility/CO₂ structurally excluded (no observable).
4. **Harness gap (tools/, outside wall)** — `tools/couple_cohort.py` on the `couple_w2_4_c6.py` template: hold truth cohort (SIM) and believed cohort (company) side by side, compute the §4 worst-cell score, write via `background.gap_metric.write_gap_entry`.
5. **Verifier wall-enforcement + seam check** — extend `tools/epistemic_verifier` (+ a `.claude/rules/` entry) so a company-side read of any SIM segment label/attitude/sensitivity fails; `sim_interface.py` gains NO cohort-label method. Run the verifier to confirm data-flow direction before close.

## 4. Worst-cell scoring (proposal; reuses existing machinery)
Reuse `background.gap_metric.belief_gap` (gap = raw_gap / g0, normalised to a blind prior). Per cohort CELL (not per book), compute `belief_gap(truth_cell, belief_cell, prior=national)`; **worst_cell_score = max over cells with support ≥ N_min of gap_cell, among cohorts that CLEAR THE LEARNING-VALUE KNEE** (FRAME §4 — so a sparse pathological cell with no learning value can't dominate). Report the worst-3-mean alongside the single max (redundancy guard, `cohort_schema.json:179`). Write `{worst_cell_id, worst_cell_gap, worst3_mean_gap, n_in_cell}` to the existing ledger — no new format. **Company-scoring dial (flagged, FRAME §3.4):** this "epistemic worst cell" is the default; a lowest-margin/highest-risk *weighting* is a separate company-scoring value, layerable later without changing the primitive.

## 5. Residual R13 curriculum calls — ONE batch (director-reserved; agent must NOT set these)
No external cross-tab exists for these → director-set curriculum (R13). The generator STRUCTURE can be built with these as gated parameters; the VALUES are the director's:
1. green_stance level marginals (engaged/neutral/disengaged incidence) — `cohort_schema.json:86`
2. price_sensitivity level marginals (high/med/low) — `schema:96`
3. channel_pref level marginals (digital/phone/assisted) — `schema:108`
4. **tenure×low_carbon_adoption gating STRENGTH** — the DESNZ tail-lift 6.0 is sourced, but how hard tenure gates adoption in the outcomes (and the exact Cramér's V, which the register refused to fabricate) is the director's dial
5. green_stance × Need-axis fusion (deliberately unfused; no consented source)
6. price_sensitivity × income/tenure (residual unmeasurable, crossed)
7. channel_pref × age (residual unmeasurable, crossed)
8. solar_PV × tenure+dwelling+region (crossed)
9. EV × region+tenure+income (crossed)
10. home_battery co-ownership triple EV×solar×battery (unobservable, crossed)
11. region marginal for synthetic acquisitions (`population_draw.py:54` standing R10 placeholder)

Items 5-10 are already crossed by the conservative fusion gate and need no new value unless the director wants to fuse one; items 1-4 and 11 are the live curriculum inputs the generator needs.

## 6. Prepayment estate — DECIDED requirement on this build (director verdict 2026-07-23)
Source: `DIRECTOR_SEGMENTS_REVIEW_VERDICTS_2026-07-23.md` §2. Spec-006 finding stands — richest company-side payment machinery, **no drawn PPM estate to meet it** (the draw stamps a binary `direct_debit|other`; `high_needs_prepay_proxy` is simultaneously the highest-consequence critical group, mean 3.08, top-decile share .562). When the prepayment estate is drawn it MUST contain **at minimum two sub-populations with OPPOSITE payment reliability**:

- **Debt-mandated PPM** — arrived via the arrears pathway; elevated default / self-disconnection risk; maps to the existing company-side `PaymentMethodSource.DEBT_MANDATED`.
- **Choice PPM / cash-cheque budget-controllers** — pay regularly and consistently; chose prepay for control of incomings/outgoings; **NOT a distress population**. *A build that stamps all PPM as distressed is WRONG and is refuted by this requirement.*

Both sub-populations carry **elevated contact propensity** (prepay calls a lot — practitioner anchor, consistent with the assisted/phone channel skew already in `critical_groups`). Mechanism design is the agent's; **sub-population shares are R13** (director-reserved) unless an Ofgem/EHS anchor is found first — discovery preferred. Couples to the new fusion entry `['payment_method','structural_block']` (§1 of the verdicts doc), which becomes load-bearing the moment this estate exists.

## 7. New coupling hypotheses seeded into the fusion register (verdicts doc §1)
Four generative-coupling hypotheses registered `provenance=assumed / status=hypothesised / coupling_strength=null` (`population_fusion_assumptions_register.json`): `cars_or_vans × ev_adoption_eligibility` (generative coupling — the draw consumes it; NOT a segmentation axis, the frontier finding that cars earns ~zero marginal learning value as an axis is unchanged), `engagement × price_sensitivity` (strength R13), `payment_method × structural_block` (§6), `engagement × affluence` (U-shape, non-monotonic). **These are blocking input to the draw-wiring step specifically** (verdicts doc §3 sequencing constraint) — the register entries must exist before the population draw is wired, or they become retrofits against a shipped draw. Every entry carries an `evidence_route` (discovery pass before any hand-set value) and a `refutation_condition`. Strengths without an external anchor ride the director's R13 batch (adds to §5 above); do not set them here.
