# B8 — Discovered price sensitivity + randomised holdout: DISCOVER + FRAME

**Atom:** `B8_discovered_price_sensitivity_holdout` (docs/design/maturity_map.yaml)
**Lane:** B_commercial · **value_stream:** price_to_bill · **epoch:** 3 · **loop_stage:** `idle`
**Stage produced here:** DISCOVER (0→1 work) + FRAME (1→2 work). **No BUILD code was written** — this atom is
epoch-gated (`EPOCH_GATING_AND_ATOM_AUTHORSHIP.md` Rule 1: a parked atom is parked for BUILD only).
**Date:** 2026-07-29
**Coupled world half:** `W2_14_continuous_behavioural_engagement_model` (already registered, `loop_stage: discover`, L0/1).

Every claim below is labelled `observed-with-evidence` (read off disk this tick, file:line quoted) or
`inferred` (R9). Nothing here is copied from the map's own prose without re-checking it against the tree.

---

## PART 1 — DISCOVER: what already exists, and what the real gap is

### 1.1 The company's price-sensitivity beliefs today are ALL asserted constants, never estimated

`observed-with-evidence`. Three separate company/saas modules hold a price-sensitivity number. Not one of
them is fitted to anything the company observed:

| Module | Line | The asserted number | How it was obtained |
|---|---|---|---|
| `company/pricing/price_elasticity.py` | 16–20 | `_PRICE_ELASTICITY_BY_SEGMENT = {"resi": -0.18, "SME": -0.12, "I&C": -0.05}` | Hardcoded, cited to CMA 2016 / Ofgem research in the module docstring (lines 3–5) |
| `company/crm/churn_model.py` | 50–57, 80 | `RATE_SENSITIVITY = 0.8`, `GAS_RATE_SENSITIVITY = 0.6`, `BILL_STRESS_SENSITIVITY = 0.25`, `IC_RATE_SENSITIVITY = 1.5` | Hardcoded population constants applied to every customer in a segment |
| `saas/home_move_win_rate.py` | 47–55 | `PRICE_SENSITIVITY_BY_EPC = {"A": 0.5, … "G": 3.0}` | A deterministic lookup: sensitivity is a **pure function of the customer's EPC band** |

The `home_move_win_rate.py` table is the shape this atom exists to abolish. It is **not** a strict epistemic-wall
violation — an EPC band is a public-register attribute a real supplier genuinely can read, and the module's own
docstring (line 32) truthfully says "No imports from `sim/`". But it is *sensitivity-by-tag*: a customer
attribute is mapped straight onto a behavioural elasticity by a table nobody measured, with no residual, no
uncertainty and no way to be wrong. `inferred`: this is the pattern that would become a real wall breach the
moment the tag chosen is a sim-generated one rather than a public one, and it is the pattern B8 replaces.

**Direct search for a true wall breach — none found.** `observed-with-evidence`: no file under `company/` or
`saas/` imports `simulation.nudge_physics`, `simulation.willingness_classification` or
`simulation.conversation_response`; the F1b estimator states and honours this
(`company/comms/susceptibility_estimator.py:17–26`). The one place a SIM-resolved latent trait *does* cross into
company code is `simulation/run_phase2b.py:1163–1172`, which resolves `engagement_level_for_customer(...)` and
passes the derived float into `company.crm.churn_model.is_active_renewal(...)`. That is the **caller** (a SIM
module) threading a plain float in, and `churn_model.py:118–128` documents exactly this arrangement; the company
module stays import-clean. `inferred`: this is a *seam-shaped* risk rather than a live breach — but it is the
precise coupling point where W2_14's continuous latent propensity would otherwise be handed to the company for
free, and B8's wall test must therefore assert on the *value path*, not only on the *import path*.

### 1.2 Offers and responses exist — but the loop is not closed

`observed-with-evidence`. The observable substrate B8 needs is already in the tree, in four places:

- **Offer chosen and recorded.** `company/policy/decision_policy.py:112–147` — `framing_type_for()` /
  `tone_for()` pick a comms attribute the company itself chose (so it is company-observable by construction),
  with a stable per-offer cohort split hashed on `customer_id + event_date`.
- **Offer outcome recorded.** `simulation/run_phase2b.py:1435–1437` and `:1590–1592` stamp
  `retention_log[-1]["outcome"]` as `"retained"` / `"churned_despite_offer"`.
- **Renewal decision recorded.** `company/crm/renewal_conversion.py:36–74` — `RenewalRecord` carries
  `offer_date`, `outcome ∈ {ACCEPTED, SWITCHED, LAPSED, PENDING}`, `channel`, `segment`, `decision_date`.
- **A wall-clean estimator pattern already proven.** `company/comms/susceptibility_estimator.py` maintains a
  per-customer Beta belief over each conversational lever from observed responses only, with C-S1/C-S2/C-S5
  discipline stated at lines 27–36. **This is B8's nearest working analogue (R4)** — B8 is the same shape with
  *price* as the lever instead of *framing/tone*.

### 1.3 THE GAP (this is the finding)

**Three defects, each `observed-with-evidence`:**

**(a) The "lift" the company measures is treatment-vs-treatment, never treated-vs-untreated.**
`company/analytics/nudge_discovery.py:42–68` (`compute_framing_lift_by_segment`) skips every log entry whose
`outcome` is not in `("retained", "churned_despite_offer")` — i.e. it reads **only offers that were made**. Both
arms of the A/B are *treated* arms (`loss_framed` vs `gain_framed`, `decision_policy.py:122–128`). There is no
arm that received nothing. So the company can answer "which framing is better?" and **cannot answer "did the
campaign do anything at all?"** — which is precisely the question the atom's own `real_world_twin` names
("because the treated group would partly have stayed anyway").

**(b) There is no untreated denominator to build one from, even observationally.**
`simulation/run_phase2b.py:1453–1464`: `no_offer_churn_log` is appended **only inside
`if event["event_type"] == "churned"`**. Customers who got no offer and *stayed* are never recorded. An untreated
retention rate is therefore not computable from the current logs at all — the numerator exists, the denominator
does not.

**(c) Even with a denominator, the untreated group is selected on the outcome variable.** Offers are gated by
`_retention_discount_for_risk(company_est)` (`simulation/run_phase2b.py:212–223`) — a churn-estimate threshold —
plus an economic guard (`_no_offer_reason = "uneconomical"`, `:1301`); the default no-offer reason is
`"below_threshold"` (`:1146`). So untreated ≙ low predicted churn. A naive treated-vs-untreated comparison is
confounded by the very variable used to assign treatment, and would report the retention campaign as
*negative*-uplift. `inferred`: this is why the fix must be a **randomised** holdout and not a smarter
observational control — no amount of matching removes selection on the assignment score itself.

**The consequence, and the sharpest single line of evidence:**
`company/analytics/counterfactual_retention.py:17` —
```python
ASSUMED_EFFECTIVENESS_PER_DISCOUNT_POINT: float = 0.04
```
The company's entire published counterfactual "value of retention" rests on an assumed constant multiplied by
the discount, via `effectiveness_for_discount()` (`:36–38`). Nothing in the tree ever checks that 0.04 against a
measured outcome. Likewise `company/crm/customer_retention.py:78–81`
(`expected_retention_value_gbp = net_margin − offer_value`) books the **full** margin as saved whenever an offer
is made, i.e. it assumes uplift = 1.0. `observed-with-evidence`: `CustomerRetentionBook` has **no non-test
caller** in the live tree (`grep -rn "CustomerRetentionBook\|generate_offer"` returns only the definition, tests,
and stale worktree copies) — so that particular assertion is currently inert, but the same 1.0-uplift assumption
is live in the counterfactual engine.

### 1.4 What the world half already provides, and what it does not

`observed-with-evidence`. The SIM already holds hidden per-customer behavioural truth and already refuses to let
it cross: `simulation/conversation_response.py:236–256` (`_trust`, `_budget_stress`, `_considering_switch` — the
last is explicitly "a latent propensity to leave … Never crosses the wall"), and
`interface/contracts/conversation_seam.py:251–267` (`FORBIDDEN_TRUTH_FIELDS`, including `true_intent`, `latent`,
`susceptibility`).

What is **missing** world-side is a latent **price** sensitivity: today the world's price response is the
segment-level `_PRICE_ELASTICITY_BY_SEGMENT`-style physics plus
`simulation/market_switching_propensity.py`'s market-level multiplier, and engagement is three discrete lifetime
bins (`simulation/household_segments.py`) — exactly what W2_14 is registered to replace with a continuous,
state-dependent latent.

### 1.5 The precedent to copy wholesale

`observed-with-evidence`. The `W2_7 ↔ C9` pair is the fully-built template for everything B8 needs:
- world-side hidden 2×2 answer key (`simulation/willingness_classification.py:1–70`) with its own named seeded
  substream (`:118`, `:265`) per C-S2;
- company-side observable-only classifier that is *allowed to be wrong* (`saas/arrears_classifier.py:59, :266`);
- harness runner that is the **only** layer holding truth and belief side by side, living in `tools/` so the
  epistemic verifier does not scan it (`tools/couple_w2_7_c9.py:1–48`);
- an explicit **asymmetric misclassification cost**: `R = 8:1`, signed
  (`saas/arrears_classifier.py:36, :41`; `tools/couple_w2_7_c9.py:29–35, :240–243, :279`), scored through
  `background/gap_metric.py::harm_cost` / `::classification_gap`, normalised to a no-skill baseline.

B8 is the same triad with a continuous latent instead of a 2×2, and `background/gap_metric.py::belief_gap`
(`:295`) + `::bootstrap_gap_ci` (`:531`) + `::write_gap_entry` (`:572`) are the metric functions already
available for a continuous truth-vs-belief comparison.

---

## PART 2 — FRAME: the design (nothing built)

### 2.1 Purpose, in one sentence

Give the company a **per-customer price-sensitivity belief that it estimated from its own offer→response
history**, plus a **randomised holdout** that makes the sentence "this segment justifies its treatment" a
*measurement with a confidence interval* rather than an assertion — and a **misclassification cost** so being
wrong is expensive in the direction it is really expensive.

### 2.2 The observable-only discovery path, and where the seam sits

The company may read exactly four things, all of which it either chose itself or received as an event:

1. **What it offered** — the price/discount it put in front of the customer, and when
   (company-owned: `decision_policy.py` chooses it, `retention_log` records it).
2. **What came back** — `ACCEPTED / SWITCHED / LAPSED / PENDING` plus the latency to decision
   (`renewal_conversion.RenewalRecord`), and the conversation-level action/channel/latency already carried by
   `ConversationResponse`.
3. **Its own price moves** — the rate change it applied at renewal, and the observed switch-away that followed.
4. **Public attributes** it could genuinely look up (segment, EPC band, tariff type). These may enter as
   **priors**, never as the answer — the estimator must be able to move away from the prior on evidence, and the
   residual must be reportable.

The seam is **unchanged and typed**: a new `price_offer_seam` contract in `interface/contracts/`, modelled
byte-for-byte on `conversation_seam.py` — a `PriceOffer` going out, a separate-in-time `OfferResponse` coming
back matched by `responds_to`, with a `FORBIDDEN_TRUTH_FIELDS` tuple that must include
`price_sensitivity`, `elasticity`, `wtp`, `willingness_to_pay`, `reservation_price`, `latent`, `true_*`. Per the
typed-flow-seam preference this is a new adapter, not a widening of an existing call. C-S3 is satisfied
structurally: an `OfferResponse` with `latency <= 0` must be rejected at construction, as
`conversation_seam.py` already does.

**The estimator itself** (`company/pricing/discovered_price_sensitivity.py`, the atom's declared `file_scope`)
is the `susceptibility_estimator` pattern with price as the lever: a per-customer posterior over "probability of
accepting at price delta *d*", shrunk toward a segment-level pooled posterior when the customer's own *n* is
small (a customer sees ~1 renewal a year — per-customer data is desperately thin, and honest shrinkage is the
difference between a belief and a coin flip). Its output is a **distribution with an interval**, never a point
estimate, and it carries `n_observations` so a consumer can see how little it rests on.

### 2.3 The holdout

**Assignment.** At the moment the retention/pricing policy decides a customer is *eligible for treatment*, a
fraction *h* is diverted to **no treatment** — the offer is withheld, the outcome is still recorded. Assignment
is a deterministic function of `(customer_id, campaign_id)` hashed through this subsystem's **own named seeded
substream**, `B8_holdout::assignment::<base_seed>` (C-S2, the `simulation/population_draw.py:143` /
`willingness_classification.py:118` `_substream` pattern), so:
- a re-run reproduces the identical assignment (deterministic replay);
- adding the holdout draw can **never** shift any sibling subsystem's random sequence (the 01:09Z shared-RNG
  incident is structurally impossible);
- assignment is *stable per campaign* but *rotates across campaigns*, so no customer is permanently untreated —
  which is both the ethical position and the way real suppliers run it.

**The critical property: assignment must be randomised WITHIN the eligible set, after the threshold.** Holding
out a random slice of everyone (including the ineligible) reproduces defect 1.3(c). The holdout answers "among
customers we would have treated, what did treating them buy?" — that is the only question the campaign's
economics actually turn on.

**Reporting.** The measured quantity is the difference in retention rate between the treated and held-out arms
of the *same* eligible cohort, reported **with a confidence interval and the arm sizes**, per segment and per
sensitivity band. `background/gap_metric.py::bootstrap_gap_ci` (`:531`) already provides the CI machinery.

**How large must it be to say anything.** Two-proportion power arithmetic, stated so the build cannot skip it.
For a baseline treated retention rate p ≈ 0.80 and equal-sized arms, detecting an absolute uplift Δ at 80% power
and α = 0.05 needs roughly n ≈ 2·(1.96·√(2·p̄(1−p̄)) + 0.84·√(2·p̄(1−p̄)))² / Δ² per arm — i.e.
**Δ = 10pp → ~250/arm; Δ = 5pp → ~1,000/arm; Δ = 2pp → ~6,300/arm**. The design consequence is blunt and must be
written into the build: **at plausible book sizes and one renewal per customer per year, a 2pp effect is not
detectable in a single campaign.** The honest response is (i) report the CI and let it be wide, (ii) pool across
campaigns and years where the treatment is unchanged, (iii) **report "underpowered — no claim" as a first-class
verdict**, and never a point estimate presented as a finding. An uplift number printed without its interval and
its *n* is a defect of the same class as R14's basis-less financial figure.

**What it costs.** The holdout is *deliberate lost margin*: `h × n_eligible × (true uplift) × margin_per_customer`
customers who would have been retained and were not. That cost must be **booked and published** — a line in the
campaign result reading "holdout cost: £X (Y customers withheld)" — because the whole point of the mechanism is
that the company can see what it paid for the knowledge. `inferred`: h ≈ 5–10% of the eligible set is the range
real retail practice sits in; the exact value is a company *policy* parameter, not a world parameter, so it is
the company's to set and get wrong.

**R12 wall on this mechanism:** measured uplift is a **diagnostic**. A treatment is never tuned to make uplift
look better, the holdout fraction is never shrunk because the number came out badly, and a campaign is never
re-cut post-hoc to find a segment where the effect happens to be significant.

### 2.4 The misclassification cost model

Two errors, and they are **not symmetric**:

| Error | What the company does | What it costs |
|---|---|---|
| **False-sensitive** (treat a price-*insensitive* customer as sensitive) | Gives a discount to someone who would have stayed anyway | Pure margin give-away: `discount × annual_consumption`, on ~100% of the mistaken group. High-frequency, low-severity, and **invisible without a holdout** — it looks like a retention success. |
| **False-insensitive** (treat a price-*sensitive* customer as insensitive) | Withholds the offer, or raises their price | Loses the customer: `remaining_CLV + reacquisition_cost (CAC)`. Low-frequency, high-severity. |

The signed harm ratio is `R_B8 = cost(false-insensitive) / cost(false-sensitive)`, derived from the company's
**own** CLV and CAC figures (`company/crm/` already holds both) rather than declared as a magic number — but
`inferred`: on typical UK domestic economics (CLV in the low hundreds of £, discount give-away in the low tens)
R lands in the **5:1–15:1** range, i.e. the same order as the C9 ability-axis 8:1 and for the same structural
reason (the expensive error is the one that destroys the relationship, not the one that shaves the margin).

Two second-order costs must be named or the model is dishonest:
- **Consumer-Duty asymmetry.** "Insensitive" correlates with *disengaged*, and disengaged correlates with
  *vulnerable*. A model that learns "don't bother discounting the disengaged" is learning to charge the
  vulnerable more. `nudge_discovery.assess_framing_consumer_duty()` (`:71`) is the existing precedent for
  policing your own discovered nudges; B8's equivalent check is **mandatory, not optional**, and its verdict
  belongs beside the uplift number.
- **Holdout cost is a third cost**, not part of either error — it is the price of knowing, and it belongs on the
  same page so the trade is visible.

The cost model is scored through `background/gap_metric.py::harm_cost` / `::classification_gap` with `R_B8`
substituted for `HARM_RATIO_R`, normalised to a no-skill baseline exactly as `couple_w2_7_c9.py` does — so a
company that classifies everyone as the majority class scores zero skill, not a flattering number.

### 2.5 Coupled-triad framing

This atom is the **COMPANY** half. The triad:

- **SIM must supply (W2_14):** a continuous, per-customer, state-dependent latent price sensitivity — movable by
  life events, service episodes and price shocks — replacing the three discrete engagement bins. It must respond
  to a price delta so that treatment genuinely changes the outcome (otherwise the holdout measures a true zero
  and proves nothing). It must live behind the wall, in its **own** named substream, and appear on no seam
  payload. It must be calibrated blind to company P&L (R13 baseline).
- **COMPANY discovers (B8, this atom):** a per-customer sensitivity posterior from offer→response history only,
  a randomised holdout inside the eligible set, a published uplift-with-CI, and the asymmetric misclassification
  cost. **Allowed to be wrong** — that is the point.
- **HARNESS measures (`tools/couple_w2_14_b8.py`, new, in `tools/` so the verifier does not scan it):** three
  numbers, entered in the gap ledger via `gap_metric.write_gap_entry("W2_14", "B8", …)`:
  1. **`belief_gap`** — the company's per-customer sensitivity posterior mean vs W2_14's true latent
     (`gap_metric.py:295`), the headline belief-vs-truth score.
  2. **`misclassification_harm`** — the `R_B8`-weighted cost of the sensitive/insensitive call
     (`gap_metric.py::harm_cost`), normalised to no-skill.
  3. **`uplift_honesty`** — the harness's own check that the company's *published* uplift bracket contains the
     **true** uplift, which only the harness can compute (it can simulate both arms against the true latent).
     A company that publishes a confident number outside the true bracket scores badly *even if the number
     flatters it*. `inferred`: this third metric is the one that makes the atom about epistemics rather than
     about retention.

**R15 independence (binding):** the harness's observable-generation model and the company's estimator must be
parameterised **independently**, as `couple_w2_7_c9.py:37–46` states for its pair. If the harness generates
responses using the same functional form the estimator fits, the gap is a tautology and measures nothing.

**Coupled-triad rule:** W2_14 may not reach L3 until B8 has been tested against it and the gap measured; B8 is
not complete until it has faced a world whose latent can defeat it (e.g. a sensitivity that *moves* mid-tenure —
a stationary estimator will be confidently wrong, and should be).

### 2.6 R15 — what must be true when BUILD opens

Three controls, each with its **named defect** and the **concrete mutation that must go RED**. A control that
cannot be shown to fire is not evidence.

**Control 1 — THE WALL (the atom's whole point).**
- *Named defect:* the estimator reads W2_14's true latent price sensitivity instead of inferring it.
- *Test:* `tests/company/test_discovered_price_sensitivity.py::test_estimator_never_reads_the_latent` — asserts
  (a) no `simulation.*` / `sim.*` import anywhere in the estimator's module graph, and (b) the
  `OfferResponse` payload carries no field whose name matches `FORBIDDEN_TRUTH_FIELDS` (structural, per
  `conversation_seam.py:251`), and (c) **the value path**: a customer whose true latent is high and one whose is
  low, but whose *observed* offer→response histories are identical, must receive **identical** estimates.
- *Mutation that must go RED:* import `simulation.household_segments` (or W2_14's successor) in the estimator and
  return the true latent as the estimate. Test (a) fires on the import, and — crucially — test (c) fires **even
  if the import is laundered** through a caller-supplied float, closing the `run_phase2b.py:1163–1172` seam-shaped
  hole found in DISCOVER §1.1. Leg (c) is the one that must exist; (a) alone is fail-open against a value path.

**Control 2 — THE HOLDOUT IS REAL AND RANDOMISED.**
- *Named defect:* the "holdout" is not randomised within the eligible set (it degenerates to the untreated
  below-threshold population — defect 1.3(c)), or is empty and the code silently reports uplift anyway.
- *Test:* `test_holdout_is_randomised_within_eligible_only` — the held-out arm's distribution of *predicted churn
  score* must be statistically indistinguishable from the treated arm's (balance check), and an empty/degenerate
  holdout must raise, never return a number.
- *Mutations that must go RED:* (i) assign the holdout **before** the eligibility threshold instead of after —
  balance check fires; (ii) set `h = 0` and have the uplift function return a value — the empty-arm guard fires
  (this is the FAIL-OPEN killer pattern: passes on empty); (iii) replace the named substream with a shared/global
  RNG — the determinism/isolation test fires (the C-S2 leg, exactly as
  `tests/simulation/test_conversation_response.py` does for F1a).

**Control 3 — NO UPLIFT CLAIM WITHOUT ITS INTERVAL AND ITS n.**
- *Named defect:* a point-estimate uplift is published from an underpowered arm — the R14 "figure without its
  clock" defect transposed onto an experimental claim.
- *Test:* `test_uplift_claim_carries_interval_and_power_verdict` — any published uplift result must carry
  `ci_low`, `ci_high`, `n_treated`, `n_holdout`, and a `verdict ∈ {significant, underpowered}`; a result whose CI
  spans zero must be labelled `underpowered` and must **not** be quotable as a proven treatment.
- *Mutation that must go RED:* return the raw rate difference with the interval fields set to `None` — the test
  must fire on `None`/missing, not pass through it (FAIL-OPEN: passes on missing/zero/empty). Second mutation:
  make the significance verdict derive from the same rate difference it is judging — the TAUTOLOGY pattern; an
  independence assertion must fire.

### 2.7 Scale + portability constraints this design commits to

- **C-S1** — offer responses arrive singly, late, out of order; the estimator folds each in independently (the
  Beta-counts-commute property `susceptibility_estimator.py:31–33` already relies on). No batch-completeness
  assumption anywhere.
- **C-S2** — idempotent on `response_id`; holdout assignment from its own named seeded substream; replay
  reproduces identical beliefs *and* identical arm membership.
- **C-S3** — offer and response are separate events in time; `latency <= 0` unrepresentable.
- **C-S4** — the offer→response history persists only through the append-only event-log abstraction.
- **C-S5** — latency is an abstract step count; the campaign window is a declared parameter, never a hardcoded
  wall-clock duration.
- **Portability** — "price sensitivity" is keyed by *product*, not by *fuel*; the seam carries a price delta and
  a response, so a second market or a second product fits behind it unchanged.
- **SIMPLICITY GUARD** — no experimentation *framework*. One assignment function, one uplift function with a CI,
  one cost function. The seam already exists as a pattern; this adds discipline, not architecture.

### 2.8 Level

**`level_current` held at 0.** The L1 bar is "been BUILT in any form" and L2 is "mechanically real AND
mutation-tested" (`docs/design/MATURITY_MAP.md:49–52`). **Nothing is built here** — BUILD is epoch-gated for this
atom and this fork wrote no code. Claiming L1 or L2 for analysis alone would be an unearned level. Saturation via
this artefact, not a level bump, is what correctly stops the re-draw — the same disposition
`H29_import_time_env_capture_test_isolation` took on 2026-07-29.

### 2.9 What BUILD would do first, in order

1. The typed `price_offer_seam` contract with its `FORBIDDEN_TRUTH_FIELDS` (smallest, unblocks everything).
2. Record the **untreated denominator** — close defect 1.3(b) by logging no-offer *retained* outcomes, not only
   no-offer churns.
3. Holdout assignment (own substream) + the balance check.
4. The estimator, shrunk to segment, distribution-valued.
5. Uplift-with-CI + the power verdict.
6. The cost model, with R_B8 derived from the company's own CLV/CAC.
7. `tools/couple_w2_14_b8.py` — but only once W2_14 supplies a latent that actually moves with price; until then
   the harness has nothing true to compare against.

`inferred`: steps 1–2 are the ones with real leverage, because step 2 alone converts a currently-unanswerable
question into an answerable one, and it is the cheapest item on the list.
