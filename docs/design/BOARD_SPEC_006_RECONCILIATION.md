# BOARD SPEC 006 — SEGMENTATION: line-by-line reconciliation

**What this is.** The mechanical, evidence-first reconciliation of the blind practitioner spec
`docs/staging/BOARD_SPEC_006_SEGMENTATION_2026-07-22.md` (Poesys Board, Practitioner Specification 006)
against the segmentation / population-coverage model **as actually built in this repo**, plus the
canonical epistemic wall ruling. It executes the reconciliation STRUCTURE already fixed pre-arrival in
`docs/design/TRIANGULATION_SITE_SEGMENTATION_FRAME.md` §2 (coverage matrix, ~12-knee arbiter,
learning-value objective, protected-groups floor, the canonical wall ruling) — that structure is used,
not re-invented.

**Provenance.** proposal · DISCOVER→FRAME · **doc-only** · **NO level claimed**. This doc edits **no**
`sim/`/`simulation/`/`company/`/`saas/`/`site/` code, **no** `maturity_map.yaml`, **no** canon file
(`DIRECTOR_CANON.md` / `SEGMENTATION_RECONCILIATION_FRAME.md` are director-reserved / ratified — read
only). It touches only `docs/design/`. Not committed by this session.

**The battery joins the oracle.** Spec 006's 12-item "NOT credible" battery (§6) joins the standing
practitioner fidelity oracle, alongside the Spec 005 seed and the earlier Specs 001–004 batteries.

**Model evidence was read from the LIVE TREE this session — no fabricated figures.** Files quoted below
were opened this session (autonomous, no-network run; every external benchmark cited *inside those
files* is theirs, carried verbatim, not re-fetched):

- Ground-truth generator / SIM: `simulation/population_draw.py`, `simulation/willingness_classification.py`,
  `simulation/household.py`, `simulation/household_segments.py`, `simulation/household_budget.py`,
  `simulation/life_events.py`, `simulation/lifecycle_tracker.py`, `simulation/meter_reads.py`,
  `simulation/self_rationing.py` (referenced by C10).
- The one taxonomy (design): `docs/market_research/population_coverage/cohort_schema.json`,
  `.../learning_value_frontier.json`, `.../value_frontier.json`, `.../build_learning_frontier.py`,
  `docs/market_research/population_fusion_assumptions_register.json`,
  `docs/market_research/POPULATION_COVERAGE_NESTED_DESIGN.md`.
- Company-side discovery twins (behind the wall): `saas/arrears_classifier.py`,
  `company/crm/affordability_inference.py`, `company/crm/self_rationing_detector.py`,
  `company/crm/vulnerability_index.py`, `company/crm/vulnerability_register.py`,
  `company/crm/priority_services.py`, `company/billing/payment_method_register.py`,
  `company/billing/prepayment.py`, `company/billing/ppm_debt_loading.py`,
  `company/finance/bad_debt_provision.py`.
- The wall verifier: `tools/epistemic_verifier.py` (seam-file segment-label guard).
- Canon: `docs/design/SEGMENTATION_RECONCILIATION_FRAME.md` (§0 canonical ruling, §4 the knee).

**Discipline note.** ABSENT and PARTIAL are used honestly. A segment *designed but not wired into the
live population draw* is **PARTIAL**, and which side is missing is named. No figure is invented; where a
number appears it is quoted from the file that holds it.

---

## COVERAGE TEST — §2's ten board-named segments vs the built model

Verdict key: **YES** = represented as a first-class trait in the built model (SIM draw and/or company
twin); **PARTIAL** = present on one side only, or designed-not-wired, or a coarser proxy; **ABSENT** =
not found after checking the named files. Direction of any gap is flagged.

| # | Board segment (§2) | Present? | Where (file / schema path) or "not found after checking X" | Notes / which side is thin |
|---|---|---|---|---|
| 1 | **Payment method: DD / standard credit / prepayment** — "the cap itself differs by payment method"; prepayment "nearly a different business" | **PARTIAL** | Company side full: `company/billing/payment_method_register.py` (3-way enum incl. `PREPAYMENT_METER`, + `PaymentMethodSource.DEBT_MANDATED` / `VULNERABILITY_PROTECTION`), `company/billing/prepayment.py`, `ppm_debt_loading.py`, `ppm_emergency_credit_register.py`, `ppm_warrant_register.py`, `self_rationing_detector.py`. SIM draw thin: `simulation/population_draw.py:249-250` stamps **binary** `payment_method="direct_debit"|"other"` from `DD_SHARE_ELEC=0.72`/`DD_SHARE_GAS=0.75` — **prepayment is NOT drawn as a distinct estate**, it is folded into "other". | The economics machinery is built and rich; the **generated population does not carry a first-class prepayment cohort** (no ~10–15% PPM estate, no self-rationing physics wired at draw time). Cap-differs-by-method is asserted in docstrings, not confirmed wired into the draw. **Board-named, half-missing on the SIM side.** |
| 2 | **Vulnerable / PSR households** — carry BOTH the flag AND the inference (registered ⊂ actually-vulnerable) | **PARTIAL (strong)** | Flag: `company/crm/vulnerability_index.py` (scored indicators → bands), `vulnerability_register.py`, `priority_services.py`, `company/regulatory/consumer_vulnerability_register.py`, `warm_home_discount.py`. Inference: `affordability_inference.py`, `self_rationing_detector.py` (raises `PPM_SELF_DISCONNECTED` from a consumption drop, proactively). | Both a declared-flag path AND a proactive-inference path exist — the two halves the board demands. What was **not confirmed** this session: an explicit reconciliation that the *registered* set is a modelled minority of the *actually-vulnerable* set with a scored registered-vs-actual gap. The pieces are present; the "registered ⊂ actual" gap as a first-class measured quantity is not evidenced → PARTIAL. |
| 3 | **Financially stressed / in arrears** (the cannot-pay book) | **YES** | SIM answer key: `simulation/willingness_classification.py` (hidden ABILITY×WILLINGNESS 2×2, ability derived from `household_budget.discretionary_margin_monthly`, not an independent draw). Company twin: `saas/arrears_classifier.py`, `company/billing/arrears_engine.py`, `affordability_inference.py`, `company/finance/bad_debt_provision.py`, `debt_collection.py`. | The strongest-built segment — a full coupled triad (SIM truth → company inference through the wall → gap). |
| 4 | **Disengaged default-tariff loyalists — "the majority of any real book"** | **PARTIAL** | `simulation/household_segments.py`: `EngagementLevel.DISENGAGED` archetype with population share **0.29** (`_INTENSITY... DISENGAGED: 0.29`), PASSIVE 0.23, ACTIVE 0.48. | The archetype EXISTS and is a durable per-tenure trait (not re-drawn each renewal). But the distribution is an **active plurality (0.48)**, not the disengaged MAJORITY the board insists on; the file's own recalibration flag notes real active share may be ~45%. **This is the §6-item-9 realism check firing — see Director Findings.** |
| 5 | **Engaged switchers** (fixed-tariff-cycling minority) | **YES** | `simulation/household_segments.py` `ACTIVE` archetype (0.48), `simulation/switching_propensity.py`, `market_switching_propensity.py`, `simulation/satisfaction_churn.py`, `churn_journey.py`. | Present and wired to churn. (See #4 — the ACTIVE/DISENGAGED *ratio* is the finding, not the presence.) |
| 6 | **Electric-heating households** (no gas; storage heaters, Economy 7) | **YES (PARTIAL on legacy metering specifics)** | `cohort_schema.json` `heating_fuel` axis has `electric` (region-pinned, off-gas tail modelled); `simulation/household.py` `HeatingSystem`; `population_draw.py` `_HEATING_FUEL_*` tables (London electric tilt 1.3). | Electric-heat cohort is first-class and region-pinned. **Economy 7 / storage-heater legacy-metering specifics** (the distinct shape + tariff) are not confirmed as a separate trait — noted PARTIAL on that sub-point. |
| 7 | **Smart vs legacy meter** ("a *data* trait that gates what the company can know") | **YES** | `simulation/meter_reads.py` (`meter_type: "smart"|"traditional"`, `meter_type_for_customer()`, `SMART_METER_NOT_COMMUNICATING_RATE=0.10`), `has_smart_meter` on the household, `saas/smart_meter_rollout.py` (`is_tou_eligible` gate), DCC/SMETS modelled. `self_rationing_detector.py` explicitly loses its baseline for non-smart/recently-switched accounts — the data-trait gating the board describes. | Treated correctly as a data trait that gates observability, not a customer trait. |
| 8 | **Low-carbon-tech adopters** (EV, solar, heat pump, battery) | **YES** | `cohort_schema.json` axes `solar_PV`, `EV`, `home_battery`; `simulation/household.py` `has_ev`/`has_solar`; `household_demand.py` asset dict (`ev`/`solar`/`smart_meter`); tenure×adoption recoupling (`SEGMENTATION_RECONCILIATION_FRAME.md` §2, DESNZ 42% renters). | Present and shape-distorting via the demand model. Heat-pump as a distinct axis level is thinner than EV/solar/battery (noted). |
| 9 | **Renters vs owner-occupiers** | **YES (PARTIAL on void-property)** | `cohort_schema.json` `tenure` (4-level: own_outright/own_mortgage/private_rent/social_rent); `population_draw.py` tenure spine + `_ACCOMMODATION/_CARS/_NSSEC_TILT_BY_TENURE`; `simulation/household.py` `TenureType`; tenure→adoption recoupling (`REFUTED_ASSUMPTION_RECOUPLED`). | Tenure is the observed-block SPINE and the single most-developed structural axis. **Void-property problem** the board names is not confirmed as modelled → PARTIAL on that sub-point. |
| 10 | **High-consumption large homes vs low-consumption flats** (volume/margin split) | **YES** | `cohort_schema.json` `accommodation` (detached…flat…caravan); `simulation/household.py` `PropertyType`+`BuildEra`+EPC-calibrated base consumption; TDCV bands (`domain_invariants.py`); cost-to-serve at customer level (activity-based pricing, per CLAUDE.md). | The crude volume split is present and drives base consumption / margin. |

### Absences in the OTHER direction (built-but-not-board-named — DATA-ONLY findings, first-class)

| Data-derived axis (in `cohort_schema.json`) | Board §2 names it? | Note |
|---|---|---|
| **region** (10-region axis) | No (implicit only) | Data-derived; pins heating-fuel off-gas tail. A cohort dimension no practitioner would list first, yet load-bearing — DATA-ONLY corroboration. |
| **nssec** (4-band income/class proxy) | No | Open income proxy (true income FRS-gated). Board treats income as INFERRED (§5) — the model uses NS-SeC as a *prior*, consistent. |
| **cars** (0/1/2+) | No | Observed-block member (tenure×cars V=0.303, the strongest measured pair) — a genuine data-derived axis outside the board's list. |
| **green_stance** (attitude) / **channel_pref** (engagement) | Partially (channel ≈ service/channel §1) | `assumed`-provenance attitude axes crossed independently — the board would call these INFERRED, and the model keeps them behind the wall (never crosses to company). |
| **home_battery** as a standalone axis | Folded into #8 | Separated from solar/EV — finer than the board's single "low-carbon-tech" bucket. |

---

## RECONCILIATION — §1, §3, §4, §5, §6 battery

Verdict key: **MET** / **PARTIALLY MET** / **ABSENT** / **N/A**.

### §1 — What segmentation must CHANGE (decisions that differ by segment)

| id | board_text (short verbatim) | reconciles_to | verdict | evidence (file/schema checked) | notes / what would advance it |
|---|---|---|---|---|---|
| S1-collections | "The fundamental split is *cannot pay* versus *will not pay*… treatment paths radically different" | model (coupled triad) | **MET** | `simulation/willingness_classification.py` (2×2 answer key), `saas/arrears_classifier.py` (Bayes gate, R=8:1 signed harm cost, PURSUE iff p>8/9), `affordability_inference.py`, `company/finance/debt_collection.py` | The best-realised claim in the spec — split, treatment divergence, regulatory-breach asymmetry all present. Involuntary-PPM / disconnection restrictions modelled (`ppm_warrant_register.py`, `winter_moratorium.py`, `disconnection_warning.py`). |
| S1-service-channel | "Digital-capable → self-serve; offline/low-capability held on human channels… cost-to-serve differs several-fold" | model | **PARTIALLY MET** | `channel_pref` axis (digital/phone/assisted) in `cohort_schema.json`; `company/crm/channel_roi.py`, `onboarding_journey.py` | Channel trait + cost-to-serve exist; a *segment→channel-routing decision wired to a live cost-to-serve differential* is not fully confirmed. Advance: show the routing decision reads the channel segment and prices cost-to-serve. |
| S1-pricing-acq | "segmentation's pricing role is mostly upstream: which segments to *acquire*… which *tariff structures*… never price the same product worse to the vulnerable or captive" | model + canon | **PARTIALLY MET** | `company/pricing/*` (`price_transparency_register.py`, `standing_charge_assessor.py`, `fair_value_assessment_register.py`), ToU/EV eligibility via smart-meter gate (`smart_meter_rollout.py`) | Cap-constrained pricing + fair-value present; loyalty-penalty guard present in spirit (fair-value register). Acquisition-targeting BY segment (consumption/cost-to-serve/churn-priced premia) is thinner. Battery item 12 (licence-forbidden use) → see below. |
| S1-comms | "Frequency, channel, reading level, tone by segment; *timing by state*… event-triggering layered on top" | model + §4 | **PARTIALLY MET** | `company/analytics/nudge_discovery.py`, `crm/campaign_tracker.py`; state layer via `life_events.py` | Comms-by-segment partial; the *timing-by-state* layer the board separates out is DESIGNED-DEFERRED (see §4 row). |
| S1-carbon | "intersection of three maps: physical headroom, financial ability, behavioural willingness… ECO-type obligations" | model + canon | **PARTIALLY MET** | headroom (EPC/fabric in `household.py`), ability (`affordability_inference.py`), willingness (`green_stance` behind wall); mission = £/tCO₂e (`PURPOSE_PITCH_V4`) | The three maps exist as separate objects; their *intersection as an abatement-targeting decision* is not confirmed wired. ECO-type scheme eligibility not confirmed as a modelled obligation. |
| S1-forecast-hedge-prov | "Segment-level consumption shapes feed shape cost… bad-debt provisioning by payment segment; churn forecasting by engagement segment" | model | **PARTIALLY MET** | shape via `household_demand.py`; bad-debt by segment `bad_debt_provision.py`; churn by engagement `household_segments.py`+`churn_journey.py` | Each leg exists. The board's test is that segmentation *reaches trading/finance*; bad-debt-by-payment-segment and churn-by-engagement are wired; segment-shape → **shape cost in the hedge book** is the thinnest leg. |

### §3 — Useful vs decorative (the four properties)

| id | board_text | reconciles_to | verdict | evidence | notes |
|---|---|---|---|---|---|
| S3-pairwise | "for any two segments, name one decision the company takes differently… if none, merge them" | proposed metric amendment (NEW) | **PARTIALLY MET** | `TRIANGULATION_...FRAME.md` §2.4 proposes a **decision-linkage gate** on the learning frontier (a cohort scores VoI only if a decision is conditioned on it) — NOT YET APPLIED | The board's Child-test *is* the proposed decision-linkage gate, independently derived. Advance: director ratifies the metric amendment (values-adjacent, propose-then-proceed). |
| S3-assignable | "every customer maps to a segment from data the company actually holds… unassignable honestly parked" | canon (wall) + model | **MET** | company twins start from EPC/census priors + own observables only (`affordability_inference.py` docstring: "missing signals simply absent — no opinion, not a zero", C-S1) | Unassignable handled as "no opinion" not forced — matches the board's "honestly parked". |
| S3-wired | "each segment routes to a concrete treatment in a live system, not a persona document" | model | **PARTIALLY MET** | collections (`arrears_classifier`→pursue/forbear), vulnerability (`priority_services`), PPM (`ppm_*`) are wired; comms/carbon/acquisition thinner (see §1) | Strongest for collections/vulnerability; weakest for carbon-targeting and acquisition. |
| S3-measured | "the differential response… estimated with **holdouts**, not asserted; a segment whose uplift has never been measured is a hypothesis wearing a name" | not found | **ABSENT** | searched company/saas for holdout / control / uplift discipline — no holdout-measured-uplift machinery found | **Material gap.** The coupled-triad measures belief-vs-truth *gap*, but there is no A/B holdout that measures *treatment uplift per segment*. Battery item 8 fails on the same point. |
| S3-dynamic | "customers migrate… model must move them on **trigger events**, not annual refresh" | model | **MET** | `simulation/life_events.py` (job_loss/income_stress HIGH→LOW transitions, W2_5 stream), `lifecycle_tracker.py`, `life_event_detector.py`, `life_event_impact.py`; arrears in/out via `arrears_engine.py` | Trigger-event migration is genuinely built (life-event stream + arrears transitions). |

### §4 — Granularity: coarse traits, fine states

| id | board_text | reconciles_to | verdict | evidence | notes |
|---|---|---|---|---|---|
| S4-knee | "fineness pays while (differentiation × uplift × population) exceeds cost… stops at three walls" | canon (the knee arbiter) | **MET** | `learning_value_frontier.json` + `build_learning_frontier.py`: dimension-knee at 5 dims, segment-knee at 4070; "a segment is included iff it clears the re-derived knee; completeness never justifies a segment" (`SEGMENTATION_RECONCILIATION_FRAME.md` §4) | The board's economics-of-fineness is the live learning-value knee. Independent corroboration (Advisor flag (a)). NOTE the objective differs — board uses treatment-uplift×population; canon uses η²/VoI (learning value). Convergent, not identical — see Director Findings. |
| S4-coarse-traits-fine-states | "coarse traits, fine states… ten to fifteen durable cells… + an event and state layer doing timing and tone" | canon + model | **PARTIALLY MET** | Coarse traits: the 12-axis `cohort_schema.json` + the ~12-segment value knee — the "10–15 durable cells" the board names, independently arrived at. State layer: `life_events.py` exists but is **deliberately deferred** as the *fine-timing* layer per the FRAME. | **The convergence the Advisor flag (a) predicts is real**: 10–15 coarse cells AND a deferred state layer, both sides landing on the same architecture. PARTIAL because the state layer is designed/partially-built, not fully wired as the timing-and-tone engine on top of the coarse cells. |

### §5 — KNOWN vs INFERRED (the epistemic wall)

| id | board_text | reconciles_to | verdict | evidence | notes |
|---|---|---|---|---|---|
| S5-known-set | "Known: address→property data, meter type/reads, payment method/history/arrears, tariff/switching, contact history, disclosed facts" | model observables | **MET** | company twins read exactly these: EPC/census priors + payment behaviour + arrears + metered kWh + contact + disclosure (`affordability_inference.py`, `arrears_classifier.py` observable lists) | The KNOWN set matches the board's list closely. |
| S5-inferred-only | "income/affordability, occupancy, attitudes/willingness, appliance holdings, undisclosed vulnerability — inferred, only ever probabilistically" | canon (wall) + model | **MET** | income never observed → NS-SeC/postcode proxy; attitudes (`green_stance`) stay behind wall; undisclosed vulnerability inferred by `self_rationing_detector.py` / `affordability_inference.py` | Each inferred quantity is inferred, not read. |
| S5-disqualifying-inversion | "The disqualifying inversion is a model where the company simply *reads* income, attitudes, or vulnerability as attributes" | **CANONICAL RULING + verifier** | **MET (wall enforced)** | Ruling: `SEGMENTATION_RECONCILIATION_FRAME.md` §0 (director console 2026-07-21, wall-class). Verifier: `tools/epistemic_verifier.py` seam-file segment-label guard — bans `green_stance`, `price_sensitivity`, `channel_pref`, `cohort_label`, `true_cohort`, `segment_label` crossing the seam (lines 79–123, "always runs" L413). SIM code (`willingness_classification.py`, `population_draw.py`) MUST NOT import `company.*`/`saas.*`. | Per Advisor flag (b): the disqualifying inversion is **structurally prevented** by a running verifier, not just declared. This is the strongest MET in the spec. **BUT** — see next row. |
| S5-misclassification-cost | "the inference error is part of the physics — misclassification, and its costs, must exist in the model" | model (partial) | **PARTIALLY MET** | The 8:1 signed harm cost in `arrears_classifier.py` IS a misclassification cost *for the collections decision*. A general **misclassification-cost physics across all inferred segments** is not built. | Per Advisor flag (b), explicitly: **misclassification-cost physics is the part NOT built** beyond the collections cell. Advance: a general cost-of-being-wrong applied wherever an inferred segment drives a decision. |

### §6 — The battery (12 items: a segmentation is NOT credible if…)

| item | board_text (short) | verdict (does the model AVOID the failure?) | evidence | notes |
|---|---|---|---|---|
| 6-1 | No decision differs by segment | **MET (avoided)** for collections/vuln; **PARTIAL** overall | `arrears_classifier.py` pursue/forbear; but §3-measured absent | Decisions differ where wired; the decision-linkage gate (S3-pairwise) is the proposed guarantee. |
| 6-2 | Segmentation on unknowable data (income/attitudes/vuln read as observed) | **MET (avoided)** | wall ruling §0 + `epistemic_verifier.py` seam guard | Structurally prevented. |
| 6-3 | No payment-method split / prepayment absent / prepayment on DD economics | **PARTIALLY MET** | company side 3-way + PPM economics built; **SIM draw is binary DD\|other** (`population_draw.py:249`) | Prepayment economics exist but the **population does not carry a prepayment estate** — the failure is half-present. Material gap. |
| 6-4 | No vulnerability layer / only self-declared / no collections constraint by segment | **MET (avoided)** | `vulnerability_index.py` + proactive inference + `winter_moratorium.py`/`ppm_warrant_register.py` regulatory constraints | Both declared and inferred vulnerability + regulated collections constraints present. |
| 6-5 | Cannot-pay and will-not-pay undistinguished | **MET (avoided)** | `willingness_classification.py` 2×2 + `arrears_classifier.py` | The flagship coupled triad. |
| 6-6 | Perfect assignment / no unassignable residue / no misclassification cost | **PARTIALLY MET** | "no opinion when signal absent" (`affordability_inference.py`); 8:1 cost in collections | Unassignable handled; but general misclassification-cost physics not built (S5-misclassification-cost). |
| 6-7 | Static segments / no migration / no trigger reassignment | **MET (avoided)** | `life_events.py` transitions, `lifecycle_tracker.py`, arrears in/out | Genuinely dynamic. |
| 6-8 | Asserted uplifts / no holdout or control discipline | **ABSENT (failure present)** | no holdout/uplift machinery found (S3-measured) | **The model currently fails this item.** Coupled-triad gap ≠ treatment-uplift holdout. Material gap. |
| 6-9 | A book of rational actors / engagement distribution inverted | **PARTIALLY MET** | `household_segments.py` DISENGAGED 0.29 / PASSIVE 0.23 / ACTIVE 0.48 | Engagement is a durable trait (good), but ACTIVE 0.48 is a **plurality, not a disengaged majority** — leans toward the "rational shoppers" country the board warns against. See Director Findings (c). |
| 6-10 | Independent draws (fuel poverty/housing/payment/digital/cost uncorrelated) | **PARTIALLY MET** | observed block IS correlated (tenure spine → accommodation/cars/nssec, `population_draw.py:454-505`, real Cramér's V 0.273/0.303/0.229; fuel pinned to region); BUT **green_stance/price_sensitivity/channel_pref/tech axes are CROSSED (independent)** by the enforced fusion gate | The board's compound-hardship household is **partially** modelled: the structural block correlates, but the attitude/digital/tech axes draw independently. This is the tail-aware coupling ruling (Advisor flag (d)) — recorded as convergent. Advance: consented-residual measurement to fuse the attitude/tech legs. |
| 6-11 | Micro-precision theatre (segments below measurable size) | **MET (avoided)** | the knee (`build_learning_frontier.py`) caps fineness at measurable size; "completeness never justifies a segment" | The knee is precisely the anti-theatre mechanism. |
| 6-12 | Segmentation used where licence forbids (worse prices for captive/vulnerable, supply refused) | **PARTIALLY MET** | `fair_value_assessment_register.py`, `price_transparency_register.py`, cap constraints; supply-refusal not modelled (no customers refused) | Fair-value guard present; a *test that the pricing engine cannot price the vulnerable/captive worse by segment* is not confirmed. Advance: an R10 class-invariant that fails any segment-conditioned price penalty on protected groups. |

---

## DIRECTOR FINDINGS (conflicts / convergences — flagged, not silently resolved)

**F1 — Advisor flag (a): coarse-traits/fine-states convergence is REAL and worth recording.** The board
independently arrived at "10–15 durable trait cells + a deferred event/state layer for timing." The built
model has exactly this shape: the 12-axis `cohort_schema.json` + the ~12-segment value knee as the coarse
cells, and `life_events.py` as a **deliberately deferred** state/timing layer (`SEGMENTATION_RECONCILIATION_FRAME.md`
§4). Two blind routes, one architecture. **Latent conflict to surface:** the board's fineness objective is
`differentiation × treatment-uplift × population`; the ratified arbiter's objective is η²/VoI **learning
value** (equal-weight, the one declared choice, `learning_value_frontier.json`). These *rhyme* (a segment
driving no decision teaches nothing) but are **not identical** — the proposed **decision-linkage gate**
(§2.4) is exactly the bridge, and it is a **values-adjacent metric change requiring director ratification**,
not to be applied by the builder. Do not silently fold the board's objective into the canon.

**F2 — Advisor flag (b): §5 wall is MET and enforced; misclassification-cost physics is NOT built.** The
"disqualifying inversion" (company reads income/attitudes/vulnerability as attributes) is structurally
prevented by the **canonical epistemic ruling** (`SEGMENTATION_RECONCILIATION_FRAME.md` §0, director console
2026-07-21, wall-class) AND a **running verifier** (`tools/epistemic_verifier.py` seam-file segment-label
guard, which bans the attitude/sensitivity/label tokens from crossing the seam and "always runs"). That is a
genuine MET with a control that can fire (R15). **The honest gap the flag predicts:** misclassification-cost
physics exists **only** for the collections cell (the 8:1 signed harm ratio in `arrears_classifier.py`).
There is **no general cost-of-being-wrong** applied wherever an inferred segment drives a decision. This is
the part not built — flag it as such, do not claim §5 fully MET without this caveat.

**F3 — Advisor flag (c): the honest coverage gaps, confirmed against the tree.**
- **Prepayment economics as a first-class SIM estate — HALF-MISSING.** Company-side PPM machinery is rich
  (`payment_method_register.py` 3-way + debt-mandated source, `prepayment.py`, `ppm_debt_loading.py`,
  `self_rationing_detector.py`), but the **population draw stamps binary `direct_debit|other`**
  (`population_draw.py:249-250`) — there is no ~10–15% prepayment estate with self-disconnection/self-rationing
  physics *drawn at population level*. The cap-differs-by-payment-method claim is in docstrings, not confirmed
  wired. **Most material single coverage gap.**
- **Cannot-pay/will-not-pay split — FULLY MET** (the flagship coupled triad). No gap.
- **PSR registered-vs-actually-vulnerable inference gap — PARTIAL.** Both a declared-flag path and a
  proactive-inference path exist, but an explicit modelled "registered ⊂ actual" set with a scored gap
  between them was not evidenced this session. The physics the regulator expects (proactively identify the
  undisclosed) is present in mechanism (`self_rationing_detector.py`); the *registered-minority quantity*
  is not.
- **Holdout-measured uplift — ABSENT.** No A/B holdout / control machinery found. The coupled-triad gap
  measures belief-vs-truth, **not treatment uplift**. Battery item 8 currently fails. Material gap.
- **Disengaged-loyalist MAJORITY realism — PARTIAL / leaning wrong.** `household_segments.py` has
  DISENGAGED 0.29 vs ACTIVE 0.48 — an **active plurality**, closer to the "book of rational actors" the
  board (§6-9) warns is a different country. The file's own recalibration flag already notes this tension
  (real active ~45% per a 2025 Ofgem series it declines to adopt unilaterally). Director call: is the ~48%
  active share a curriculum choice or a fidelity defect? (R13 — curriculum is director-reserved.)

**F4 — Advisor flag (d): battery item 10 (independent draws ≠ a GB book) is our tail-aware coupling
ruling, independently derived — recorded, with a caveat.** The board's "compound hardship households
travel together" is the coupled-observed-block design: `population_draw.py` correlates tenure→accommodation/
cars/nssec using the **real measured Cramér's V** (0.273/0.303/0.229) from the fusion register, and pins
heating-fuel to region. **Caveat (honest):** the *attitude/digital/tech* legs the board specifically names
(fuel poverty × digital capability × payment method) are **crossed independently** by the enforced fusion
gate (`FUSION_BAR_RESIDUAL_v1`, residual unmeasurable → cross). So the compound household is **partially**
modelled — the structural block coheres, the attitude/tech/payment legs do not yet. Convergent ruling,
partial realisation.

**F5 — objective mismatch to keep on the director's desk.** The board never sees the learning-value
objective (the §2.3 elicitation-channel wall held — this reconciliation confirms the board spec contains
no η²/VoI framing). Good: the triangulation did not collapse into a rubber-stamp. The board's practitioner
objective (treatment-uplift economics) and the canon's learning-value objective are therefore **genuinely
independent** and their agreement on the ~12-cell architecture is real evidence, not leakage.

---

## SUMMARY SCORELINE

**Battery (§6, 12 items — "does the model AVOID the failure?"):**
- MET (avoided): **5** — items 1(partial-overall but met where wired), 2, 4, 5, 7, 11 → counting strict MET: **6-2, 6-4, 6-5, 6-7, 6-11** = **5 MET**.
- PARTIALLY MET: **6** — 6-1, 6-3, 6-6, 6-9, 6-10, 6-12.
- ABSENT (failure present): **1** — 6-8 (holdout-measured uplift).
- N/A: 0.

**Coverage test (§2, ten named segments):** YES **6** (#3, 5, 7, 8, 9, 10) · PARTIAL **4** (#1, 2, 4, 6) ·
ABSENT **0**. Plus **5 DATA-ONLY** axes built but not board-named (region, nssec, cars, green_stance/
channel_pref, home_battery) — evidence the data route carries structure practitioners under-name.

**Full reconciliation rows (§1+§3+§4+§5, 19 expectation rows):** MET **8** · PARTIALLY MET **9** ·
ABSENT **2** (S3-measured holdouts; and the acquisition-targeting leg of S1-pricing counted within its
PARTIAL) · N/A **0**.

**The 3–5 most material gaps (director attention):**
1. **Holdout-measured uplift is ABSENT** (battery 6-8, S3-measured). The company measures belief-vs-truth
   gap but never treatment uplift per segment. Every "this segment justifies its treatment" claim is
   currently asserted, not measured.
2. **Prepayment is not a first-class SIM estate** (battery 6-3, coverage #1). Rich company-side PPM
   machinery sits on a population draw that only knows `direct_debit|other` — no ~10–15% prepayment cohort,
   no drawn self-rationing physics.
3. **Misclassification-cost physics is built only for collections** (F2, S5-misclassification-cost,
   battery 6-6). The 8:1 harm ratio is real but local; no general cost-of-being-wrong where other inferred
   segments drive decisions.
4. **Disengaged-loyalist share leans to an active plurality** (0.48 active vs 0.29 disengaged; battery
   6-9). A director curriculum call, not a silent fix (R13).
5. **Compound-hardship coupling is only half-realised** (battery 6-10, F4). Structural block correlates on
   real Cramér's V; attitude/digital/tech/payment legs draw independently pending consented-residual
   measurement.

**Convergences worth banking (blind board ↔ ratified canon, independently derived):** coarse-traits/
fine-states ↔ the ~12-cell knee + deferred state layer (F1); the disqualifying-inversion ↔ the canonical
wall ruling + running verifier (F2); independent-draws-≠-GB-book ↔ the tail-aware coupled-block design (F4).
Three blind agreements — the triangulation did its job.
