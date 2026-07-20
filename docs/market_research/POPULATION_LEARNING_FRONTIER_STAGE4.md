# Population Learning-Value Frontier — Stage 4 REFRAMED (2026-07-20)

**Track:** `DIRECTOR_STEER_SEGMENTATION_LEARNING_VALUE_REFRAME_2026-07-20`
**Supersedes the objective of:** `POPULATION_VALUE_FRONTIER_STAGE4.md` (the P&L-weighted "value frontier").
**Status:** DISCOVER/FRAME — analysis only, doc-and-data, reversible. **The population-generator wiring stays director-reserved (a wall). This reframes the analysis; it does not authorise wiring.**
**Loop position:** one iteration of an explicitly iterative learning loop. The director reacts and refines; no single output is final.

---

## 0. What the director corrected

The stage-4 "value frontier" optimised **value of the customer** (signed £ P&L contribution). The director caught the conflation, verbatim:

> **"Value makes no sense. Bad debt is negative value but working out how to deal with them is really valuable."**

Two different things were collapsed into one signed scalar:
1. **Value of the customer** — margin contribution. A fuel-poor household in arrears is *negative* here.
2. **Value of MODELLING that segment well** — how much the business learns from understanding it. Arrears, vulnerability and collections are *high* here precisely because they are hard, costly, and where regulatory + mortality risk concentrate.

The old build maximised (1). The director wants (2). Concretely, in the old objective **bad debt entered with a minus sign and a guessed 0.20 weight**, so a high-arrears segment scored *low-value* and got demoted — backwards. And the fixed weights (margin 0.40 / retention 0.25 / bad-debt 0.20 / carbon 0.15) were "a guess dressed as precision"; the director's deeper instruction: *"let the data guide us rather than just guess."*

## 1. The reframed objective — learning / information value

Optimise for **which segments teach the company the most.** A segment ranks high when it is:
- **behaviourally distinct** (acts differently in ways that change a decision), OR
- **commercially consequential in EITHER direction** (large positive *or* large negative P&L — arrears/default count as HIGH-consequence, not low-value), OR
- **regulatorily/vulnerability-critical** — handled as a **floor outside the ranking**, not a term inside it.

### Three data-derived criteria (no hand-assigned outcome weights)
Values-call file: `population_coverage/learning_value_model.json`. The outcome MODEL (effects/base) is re-used **unchanged** from `value_outcome_model.json` — same physics; only the objective over it is reframed, which keeps the knee-delta clean.

1. **Consequence magnitude (unsigned, either direction)** — `sqrt(Σ z_k²)` over the four standardized outcomes. A household extreme on *any* outcome, **including bad debt**, is high-consequence. This is the "either direction" fix in one number.
2. **Learning value / value-of-information** — between-segment η² of each *standardized* outcome. Under a quadratic-loss decision the between-group variance **is** the value of information (gain from acting per-segment vs pooled), so η² is a VoI measure, not a proxy. **Bad-debt η² now counts positively.**
3. **Distinctness** — marginal learning value of a dimension *given those already chosen* ("not predictable from the others"). A redundant dimension adds ≈0 and earns no segment.

### The one declared choice (chosen, declared, sensitivity-tested)
The four guessed weights are **withdrawn**. The only unavoidable residual choice is **equal weight on the four standardized outcomes** when aggregating — the *maximum-entropy / least-committed* prior (no outcome presumed more important before the data speaks). Segment ranking then comes from *measured* η², not the weight. Sensitivity-tested against margin-led, bad-debt-led and net-zero tilts (§5) — same discipline as the 1.5× tail-lift threshold.

### Protection is a floor OUTSIDE the ranking
`critical_group_bonus` is **removed** from the score (it was 0.05). Protected groups are covered by **carve-out construction**. **No metric — learning value included — can demote a regulatorily-significant group (vulnerability, fuel poverty, prepayment, priority-services, debt) below full-fidelity modelling.** The director invited this set to *widen* if anything; see `critical_groups.json`.

---

## 2. Dimension ranking by learning value (equal-standardized default)

Reproduce: `python3 population_coverage/build_learning_frontier.py` → `population_coverage/learning_value_frontier.json`.

| rank | dimension | learning value | margin η² | churn η² | **bad-debt η²** | carbon η² |
|---|---|---|---|---|---|---|
| 1 | price_sensitivity | 0.226 | 0.28 | 0.576 | 0.050 | 0.00 |
| 2 | **tenure** | 0.220 | 0.214 | 0.091 | **0.512** | 0.063 |
| 3 | channel_pref | 0.167 | 0.338 | 0.262 | 0.067 | 0.00 |
| 4 | **nssec** | 0.166 | 0.090 | 0.025 | **0.545** | 0.004 |
| 5 | accommodation | 0.114 | 0.046 | 0.007 | 0.091 | 0.313 |
| 6 | heating_fuel | 0.106 | 0.012 | 0.001 | 0.060 | 0.350 |
| 7 | EV | 0.060 | 0.100 | 0.007 | 0.000 | 0.133 |
| 8 | green_stance | 0.049 | 0.000 | 0.024 | 0.000 | 0.173 |
| 9 | cars | 0.029 | — | — | 0.077 | — |
| 10 | solar_PV | 0.011 | — | — | — | 0.035 |
| 11 | home_battery | 0.002 | — | — | — | — |
| 12 | region | 0.002 | — | — | 0.001 | 0.005 |

**The reframe working, made visible:** `tenure` and `nssec` rank #2 and #4 **because bad-debt variance is now a positive learning signal** (η² 0.51 and 0.55 — the highest single-outcome cells in the table). Under the old signed objective these dimensions were *penalised* for the same arrears that here makes them high-learning-value. This is exactly "working out how to deal with [bad debt] is really valuable" expressed as a metric.

## 3. The reframed frontier and its knee (greedy by distinctness)

| step | +dim | segments | learning value | ΔLV | consequence η² | critical coverage |
|---|---|---|---|---|---|---|
| 1 | price_sensitivity | 3 | 0.226 | +0.226 | 0.064 | 0.064 |
| 2 | tenure | **12** | 0.447 | +0.221 | 0.248 | 0.210 |
| 3 | channel_pref | 36 | 0.617 | +0.170 | 0.377 | 0.379 |
| 4 | heating_fuel | 252 | 0.724 | +0.107 | 0.495 | 0.736 |
| **5** | **nssec** | **934** | **0.817** | **+0.094** | 0.702 | 0.928 |
| 6 | accommodation | 3069 | 0.883 | +0.066 | 0.761 | 0.997 |
| 7 | EV | 4070 | 0.942 | +0.059 | 0.910 | 1.000 |
| 8+ | green/solar/battery/cars/region | → 38k | →1.000 | ≤+0.046 | →1.000 | 1.000 |

**Value knee (reframed):** **~5 dimensions** (LV 0.817, gap-above-chord 0.401) is the dimension-count knee — the point past which each further dimension buys <0.07 learning value while multiplying segment count. The classic **12-segment point** (price_sensitivity × tenure) now captures **0.447** of the *broader* learning value (vs 78% of the narrower P&L variance in the old build) — because learning value now spans bad-debt and carbon signal that a two-dimension commercial core does not reach.

> Note on the "by-segment-count" knee (4070): segment count grows multiplicatively so that axis is a poor ruler — the **dimension-count knee (5)** and the **hybrid design (§4)** are the legible answers. Reported both for honesty.

## 4. How the knee MOVED vs the withdrawn P&L-signed objective

| | old (P&L-signed, WITHDRAWN) | new (learning value) |
|---|---|---|
| leading 3 dims | price_sensitivity, tenure, **accommodation** | price_sensitivity, tenure, **channel_pref** |
| #4 | — | **nssec rises** |
| dim-count knee | (deeper cross) | **5 dims** |

**Why it moved:** `accommodation` (carbon-driven, η² 0.31) fell out of the top-3 because the old objective's explicit 0.15 carbon weight lifted it; under equal-standardized learning value the **bad-debt-bearing dimensions (nssec, and tenure's bad-debt half) rise** and `channel_pref` (a cost-to-serve + collections proxy) overtakes it. The movement *is* the information the director asked for: the segments worth modelling shift from "where margin/carbon vary" toward "where arrears and cost-to-serve vary."

### Recommended hybrid designs — learning-value core + protected floor
| design | core dims | segments | learning value | critical coverage |
|---|---|---|---|---|
| **lvcore2_OVERLAY** | price_sensitivity × tenure + cross-cutting protected overlay | **31** | 0.522 | **1.00** |
| lvcore3_OVERLAY | + channel_pref | 53 | 0.625 | 1.00 |
| lvcore2_INTERSECT | protected carved within each core cell | 83 | 0.547 | 1.00 |

The **~31-segment overlay** (12-cell commercial core + protected groups pulled into one cross-cutting group-segment, the way a real supplier runs a PSR/fuel-poor list) remains the honest minimum-segment recommendation: full protection at ~zero extra variance cost. The two objectives still do **not** co-move — learning is bought by coarse main-effect splits; protection by targeted conjunctive carves.

## 5. The inverted-bell thesis, made measurable (consequence tail)

Population mean consequence = **1.87**. Every protected group sits well above it and is over-represented in the top consequence decile:

| protected group | mean consequence | share in top consequence decile | n (of 60k) |
|---|---|---|---|
| high_needs_prepay_proxy | **3.08** | 0.562 | 1549 |
| electric_flat_renter | **2.99** | 0.553 | 886 |
| fuel_poor_offgas | **2.93** | 0.522 | 2010 |
| offgrid_rural_low_income | **2.86** | 0.481 | 539 |
| vulnerable_assisted | **2.72** | 0.398 | 3598 |

This is the director's thesis as evidence: value (of understanding) concentrates at the difficult edges. The groups the *old* objective scored as low-value are, on the reframed axis, the **highest-stakes** cohorts — which is why protection is a floor, not a scored bonus.

## 6. Sensitivity to the one declared choice

Rebuilding under each outcome-importance tilt:

| tilt | leading dims | dim-count knee LV |
|---|---|---|
| equal (default) | price_sensitivity, tenure, channel_pref, nssec | 0.942 @ step-7 boundary |
| margin_led | price_sensitivity, tenure, channel_pref, nssec | 0.966 |
| bad_debt_led | **tenure, nssec**, price_sensitivity, channel_pref | 0.902 @ 934 segs |
| net_zero_tilt | tenure, heating_fuel, price_sensitivity, accommodation | 0.907 |

**The top-2 (price_sensitivity, tenure) are robust across equal / margin / bad-debt tilts;** only the carbon-heavy net-zero tilt reshuffles by lifting `heating_fuel`. So the reframed knee is robust to the declared choice, and only the fine ordering past the knee is tilt-dependent. The director's real lever is the *tilt direction*, not a four-number weight vector.

## 7. What stays reserved (the wall)

Unchanged from stage 4: **building this structure into the population generator is the director's gate.** This reframe changes the *analysis* only. The two values-calls now take their reframed shape:
- **(a) business-value weighting** → **withdrawn as a fixed weight**, replaced by the data-derived learning-value metric. The one surviving director-set parameter is the *equal-vs-tilt* choice (§1, §6), marked ASSERTED and sensitivity-tested.
- **(b) critical/protected set** → **stays, and should if anything widen.** Protection is a floor outside the ranking; `critical_groups.json` carries a widening invitation.

**Next in the loop:** the director reacts to this reframed ranking + knee. Bring the generator wiring back as **[ACT]** only after that — nothing here touches the live generator.

---

*Epistemic note:* built from committed stage-2 census marginals + crosstabs (population-representative, volume-weighted), same joint structure as stage-3. Deterministic (seed 20260720), no microdata, no network. Outcomes are DIAGNOSTICS used to *rank* segments (R12); no effect size was tuned — bad debt lifts a dimension because its variance is genuinely informative, not because it was weighted to. No SIM internals read; no company-layer code touched.
