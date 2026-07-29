# W2_14 — Continuous behavioural engagement model — DISCOVER

**Atom:** `W2_14_continuous_behavioural_engagement_model` (lane W2_customer_generator,
value_stream meter_to_cash, **epoch 4**, level 0→1, loop_stage=discover,
provenance=proposal, depends_on `W2_5_life_event_stream`).
**Provenance:** director standing ask registered in `maturity_map.yaml` and
`docs/staging/done/DIRECTOR_R13_ENGAGEMENT_MIX_RATIFICATION_2026-07-23.md` §3; coupling
hypotheses from `DIRECTOR_SEGMENTS_REVIEW_VERDICTS_2026-07-23.md` §1 entries 2 and 4.
**Date:** 2026-07-29.

> **Director's real-world twin (verbatim, maturity_map):** *"a real household's engagement is not a
> permanent label: a price shock, a bad service episode, or a life event can move a formerly-active
> shopper into disengaged inertia, and the propensity is a distribution across the population, not
> three discrete boxes."*

---

## 0. Scope, and the hard constraint on any build

### 0a. The R13 wall (state it first, because it sizes everything)

The static population shares were **R13-RATIFIED by the director on 2026-07-22**
(commit `9542cdd1b` "R13 engagement-mix ruling applied (director console 2026-07-22)";
`DIRECTOR_R13_ENGAGEMENT_MIX_RATIFICATION_2026-07-23.md`):

```
ENGAGEMENT_POPULATION_SHARE = { ACTIVE 0.45, PASSIVE 0.35, DISENGAGED 0.20 }
```

A latent continuous propensity model **must reproduce those ratified aggregate shares when
bucketed**. It is a **re-representation of the same ratified population, not a re-calibration of
it.** Silently moving those shares would be an R13 breach — the curriculum/baseline is the
director's, never the agent's. §4 shows how to make that preservation an **identity holding for
every customer_id**, not a statistical near-match that could drift.

### 0b. Explicitly OUT of scope (three neighbours this atom is repeatedly confused with)

1. **The regime-timed engagement schedule.** R13 ruling **Q-B** registered a *"regime-timed
   engagement schedule"* as a NAMED candidate **curriculum scenario** — a future epoch-4-class
   **director** lever. It is **not** this atom. This atom is the *within-household continuous*
   model.
2. **Market-state / opportunity modulation.** `docs/design/ENGAGEMENT_MARKET_STATE_RESPONSIVENESS_PROPOSAL_2026-07-22.md`
   proposes that realised switching = **disposition × opportunity**, where *opportunity* (offer
   availability, fixed-vs-SVT spread) collapses in a crisis. That proposal owns the **opportunity**
   factor. **This atom owns the *disposition* factor** — and specifically its shape (distribution,
   not three boxes) and its **movability within one household's life**. The two are complementary
   and must not be built as one thing: conflating them is how a *caused* mechanism turns back into a
   *scripted* one.
3. **Re-levelling the aggregate active-renewal rate.** `household_segments.py:45-52` flags raising
   the ~35% aggregate toward the ~45% recovery regime as a SEPARATE, larger R13 lever, deliberately
   not taken. Unchanged here (R12: the aggregate is a diagnostic, never a target).

---

## 1. JOB 1 — the code read: where the discrete bin enters the churn/renewal path TODAY

Read at this DISCOVER's HEAD. Line numbers are quoted from the working tree.

### 1.1 The definition site — `simulation/household_segments.py`

| Lines | Object | What it is |
|---|---|---|
| 69–72 | `class EngagementLevel(str, Enum)` | The three discrete bins: `ACTIVE` / `PASSIVE` / `DISENGAGED`. **The bounding simplification.** |
| 77–81 | `ENGAGEMENT_POPULATION_SHARE` | **R13-RATIFIED** 0.45 / 0.35 / 0.20 (§0a). Ordered — the order is load-bearing for the cumulative draw at 103–106. |
| 87–91 | `_ACTIVE_RENEWAL_PROBABILITY_BY_ENGAGEMENT` | ACTIVE 0.65 / PASSIVE 0.15 / DISENGAGED 0.02. The docstring (83–86) is explicit that these are **a calibration CHOICE, NOT independently sourced** — tuned so `0.45·0.65 + 0.35·0.15 + 0.20·0.02 ≈ 0.349` reproduces `churn_model.PASSIVE_RENEWAL_RATE = 0.35`. |
| 93 | `assert abs(sum(...) - 1.0) < 1e-9` | The shares-sum invariant. Any re-representation must keep this true. |
| 96–107 | `engagement_level_for_customer(customer_id) -> EngagementLevel` | `rng = random.Random(f"engagement_{customer_id}")`, one `rng.random()` roll, cumulative-share walk, `DISENGAGED` float-rounding fallback. |
| 110–116 | `active_renewal_probability(level) -> float` | Table lookup. Returns a **plain float** so `company/crm/churn_model.py` stays free of any `simulation.*` import (the epistemic wall). |
| 119–123 | `active_renewal_probability_for_customer(cid) -> float` | Convenience composition of the two above. |

**The mechanical fact that makes the trait immovable.** `engagement_level_for_customer` has the
signature `(customer_id: str) -> EngagementLevel`. **There is no time argument and no state
argument.** It is a pure function of the customer id alone. A life event, a service episode or a
price shock has **no argument through which it could enter** — the immovability is not a modelling
choice recorded in a constant, it is a *property of the signature*. That is the single most
important thing this code read establishes, and it is what a build must change (additively).

Its docstring (97–99) states the intent plainly: *"stable for the customer's whole tenure (a
persistent behavioural trait, not redrawn per renewal)"*. The atom's ask is precisely to relax the
second half of that sentence without losing the first — engagement should be **persistent but not
permanent**.

### 1.2 Every consumer (exhaustive)

Grep over `--include=*.py` for `engagement_level_for_customer|active_renewal_probability|EngagementLevel`
across the tree (worktrees excluded):

| # | Consumer | Lines | What it consumes |
|---|---|---|---|
| 1 | **`simulation/run_phase2b.py`** | **1163–1172** | **The one live production consumer.** Imports `active_renewal_probability` + `engagement_level_for_customer` (1163–1166), resolves the level on the stable `billing_account` (1167), and passes the float into `company.crm.churn_model.is_active_renewal` (1169–1172). |
| 1b | `simulation/run_phase2b.py` | 1173 | `passive_cap = None if active_renewal else _PASSIVE_CHURN_CAP` — the *downstream consequence*: a passive roller is churn-capped at 0.10. |
| 1c | `simulation/run_phase2b.py` | 1235, 1426, 1432 | `segment_for_churn` branch on `not active_renewal`; stamps `event["is_active_renewal"]` and `event["engagement_level"]` onto the emitted event. |
| 2 | **`company/crm/churn_model.py`** | **118–140** | `is_active_renewal(term_start_str, seed, active_probability=None)`. Receives the archetype **only as an anonymous float** — wall-clean, no `simulation.*` import (docstring 126–129). Defaults to the flat `PASSIVE_RENEWAL_RATE = 0.35` (96) when not threaded. |
| 3 | `tools/generate_customer_sample.py` | 188–189, 210 | Evidence-surface only. Comment at 185–187 marks it SIM-internal ground truth that **"MUST NEVER be read by `company/**` code."** |
| 4 | `tools/generate_dashboard_data.py` | 585 | Reads `ev.get("engagement_level")` off the **emitted event**, not off the module — strictly downstream of consumer 1c. |

**A correction to the atom brief, recorded because it matters for sizing.**
`simulation/switching_propensity.py` is named in the brief as a consumer. **It is not.** The file
contains exactly one occurrence of the string `household_segments` (line 41) and it is a *comment
about TENURE*. `switching_propensity.py` never imports, reads or receives engagement. It is a
**sibling lever on the same churn path**, not a consumer:

- `STRESS_SWITCHING_MULTIPLIER` (19–24): `IncomeStress.LOW 1.10 / MODERATE 0.85 / HIGH 0.65`
- `TENURE_SWITCHING_MULTIPLIER` (45–50): `owner_occupier 1.0 / private_renter 0.80 / social_renter 0.75`
- `adjust_churn_probability(base_prob, income_stress, tenure)` (61–…)

Naming this correctly is load-bearing for §2.3: **`STRESS_SWITCHING_MULTIPLIER` is strictly
monotone in affluence** (least-stressed switch most, 1.10 → 0.85 → 0.65). The registered U-shape
hypothesis' own **refutation condition is stated in the inverse** — *"a source showing engagement is
MONOTONE in affluence … would refute the U-shape"* — so **the code today implements the shape that
the U-shape hypothesis contradicts.** If the U anchors, `switching_propensity.py` is the file that
must change. It is **outside this fork's file scope**, which is itself evidence about build size.

Two further sibling levers sit on the same churn path and are **not** engagement-aware:
- `simulation/satisfaction_churn.py:20–29` — `satisfaction_churn_multiplier(score)`:
  ≥0.80 → 0.85, ≤0.50 → **1.30**. The **service-episode channel already exists**, but it feeds
  *churn magnitude* only, and **only in the direction of more churn**. The director's twin asserts
  the opposite sign is also real (a bad service episode can push a household into *disengaged
  inertia*). That direction is **not representable anywhere in the current model.**
- `simulation/sim_satisfaction.py:64–69` — `sim_satisfaction_score(bill_shock_count, tenure_years,
  income_stress, payment_channel, customer_id)`. Note it already carries `bill_shock_count`: **the
  price-shock signal a movable propensity needs is already computed**, it simply never reaches
  engagement.

### 1.3 THE SEAM (name it — fold, do not fork)

> **The seam is `simulation/household_segments.py:96–107` — `engagement_level_for_customer` — which
> must become a PROJECTION of a continuous latent variable rather than the primitive that defines
> it. The call seam is `simulation/run_phase2b.py:1167`.**

Concretely, fold by adding *beneath* the existing function, never around it:

```
engagement_propensity_for_customer(customer_id) -> float in [0,1]     # NEW: the latent
engagement_level_from_propensity(p: float)      -> EngagementLevel    # NEW: the projection
engagement_level_for_customer(customer_id)      -> EngagementLevel    # UNCHANGED signature
```

bound by the **exact refinement identity**

```
engagement_level_from_propensity(engagement_propensity_for_customer(cid))
    == engagement_level_for_customer(cid)      for EVERY customer_id, ALWAYS
```

**This is not an invented pattern — it is this codebase's own established precedent for exactly this
problem.** `simulation/population_draw.py:417–467` faced the identical situation (a finer 4-level
cohort tenure must not disturb the existing 3-level `tenure_for_customer` relied on by 370+ test
references) and solved it by making the fine representation a **strict refinement of the coarse
one**, guaranteeing

```
collapse_cohort_tenure(cohort_tenure_for_customer(cid, seed)) == tenure_for_customer(cid)   # always
```

(`population_draw.py:428–431`, `collapse_cohort_tenure` at 463–467). Adopting the same shape here
means the **R13 shares are preserved by construction, not by a statistical test** — a far stronger
guarantee, and the one an R13 wall deserves. A population test that merely checks 0.45/0.35/0.20
within a tolerance is a *weaker* control that could drift; the identity cannot.

**Why the call seam needs no new plumbing.** `run_phase2b.py:1169–1172` already has
`term_start_str` in hand at the point it resolves the archetype. A time- or state-dependent
propensity therefore reaches the seam through an argument that is **already there** — no new data
path, no new event type, no threading through intermediate layers.

### 1.4 The structural finding that actually sizes this atom

**There are two population representations in the SIM, and they never meet.**

| | `simulation/household_segments.py` | `simulation/population_draw.py::Cohort` (684–695) |
|---|---|---|
| Keyed on | `customer_id` only | `(customer_id, base_seed)` |
| RNG | `random.Random(f"engagement_{cid}")` (100) | `_cohort_substream(cid, base_seed, axis)`, stable-sha256 (390–401) |
| Carries | engagement, payment_channel, fuel_poverty, tenure(3), occupancy | tenure(4), accommodation, cars, nssec, heating_fuel, region, green_stance, **price_sensitivity**, channel_pref |

**`Cohort` has no engagement field.** Therefore **neither registered coupling is expressible in the
code today**:

- **engagement × price_sensitivity** — `price_sensitivity` is drawn at `population_draw.py:737` via
  `_draw_curriculum_axis`, inside a block whose own header comment (570–574) reads: *"green_stance /
  price_sensitivity / channel_pref — **CROSSED (independent)** … No basis to fuse these onto the
  block (fusion register: residual unmeasurable → cross, the enforced `FUSION_BAR_RESIDUAL_v1`
  gate)."*
- **engagement U-shape by affluence** — the affluence proxy (`nssec`, drawn at 723–726) is a
  `Cohort` field.

**And the sharpest finding of this DISCOVER.** `docs/design/segmentation_curriculum_v1.json:16–21`:

```json
"price_sensitivity_marginals": {
  "value": {"high": 0.30, "medium": 0.45, "low": 0.25},
  "basis": "GB retail-energy switching/engagement segmentation (Ofgem consumer engagement work):
            an active-switcher minority, a disengaged 'stuck' minority, a middle majority.
            PROVISIONAL."
}
```

That basis names **the same real-world construct, from the same cited body of work, in the same
three-bin shape** (an active minority, a stuck minority, a middle) as the engagement mix. **The
model therefore draws one latent construct twice** — two independent RNG streams, in two modules,
with two different shapes (0.30/0.45/0.25 vs 0.45/0.35/0.20) — **and then crosses them
independently.** Today a household can be `ACTIVE` engagement × `low` price_sensitivity, which under
the shared basis is close to a contradiction.

This is the real prize of the atom, and it reframes coupling entry 2. The fusion register
(`docs/market_research/population_fusion_assumptions_register.json`, entry `["engagement",
"price_sensitivity"]`) currently states the coupling as *"co-vary as one structural bundle …
currently drawn independent"* with `coupling_strength: null` and the note *"strength is R13
director-reserved (no external anchor)"*. **The code read suggests a stronger and cheaper reading:
the right answer may not be a correlation coefficient bolted between two three-box draws at all, but
two PROJECTIONS of one continuous latent.** A projection needs **no R13 coupling-strength dial** —
which is exactly why the continuous representation is worth having. Recorded here as a proposed
sharpening of that register entry; the register is not this fork's to edit.

**But:** `population_draw.py` and `segmentation_curriculum_v1.json` are the curriculum/R13 surface
and outside this fork's file scope. So the *unification* half of the prize cannot be built here.

### 1.5 An MC-1-shaped override already sitting in the path (flagged, not this atom's to fix)

`company/crm/churn_model.py:100–101` and `137–138`:

```python
CRISIS_PASSIVE_YEARS = frozenset({"2022"})
...
year = term_start_str[:4]
if year in CRISIS_PASSIVE_YEARS:
    return False
```

Two observations, both labelled honestly:

- **`observed-with-evidence`:** the short-circuit runs **before** the per-household
  `active_probability` is consulted (137–139), so in 2022 *every* household is forced passive
  regardless of its archetype. Structurally this is **already** `disposition × opportunity` — the
  exact shape `ENGAGEMENT_MARKET_STATE_RESPONSIVENESS_PROPOSAL_2026-07-22.md` proposes — but with
  opportunity as a **hardcoded year literal** and a **hard zero**.
- **`inferred`:** by *representation* this is the MC-1 scripted class the same proposal explicitly
  forbids (a date-keyed constant written because we know how the year turned out). It is
  point-in-time *defensible* (a real 2022 supplier genuinely knew no fixes were on sale), so this is
  **not** asserted as an established wall breach. It belongs to the sibling market-state proposal
  (§0b item 2), not here. Registered as a lead, not actioned.

---

## 2. JOB 2 — real-world anchoring

**Method note (honesty bar).** Findings below are separated into (a) figures held in this repo's own
market-research register from earlier fetches, cited to their register file and their original
source, and (b) figures fetched fresh this session. Every unfetched source is named explicitly in
§2.5 rather than paraphrased from memory. No citation or number in this document was generated
without a named source.

### 2.1 Is engagement three boxes, or a distribution? — the direct evidence AGAINST three boxes

The strongest available evidence is that **Ofgem's own published segmentation of the same population
does not use three bins, and does not treat "default" as "disengaged".**

From `docs/design/ENGAGEMENT_MIX_RECONCILIATION_2026-07-22.md` §1 (Ofgem Retail Market Indicators
data portal, *"Number of domestic customer accounts by supplier … on default tariffs"* panel, as of
**October 2025**, non-prepayment domestic; fetched 2026-07-08, held in the register — **not
re-fetched this session**):

| | Actively-chosen | On default tariff | of which held **3+ yr** | of which held **<3 yr** |
|---|---|---|---|---|
| Electricity | 45.1% | 54.9% | **20.3%** | **34.6%** |
| Gas | 45.4% | 54.6% | 23.1% | 31.5% |

The reconciliation doc's own reading (§1, verbatim): *"Ofgem **does not equate 'default' with
'disengaged'**: it splits the 54.9% default majority into a **clearly-disengaged** 3+-year tail
(20.3%) and a **churning middle** (34.6%, <3 yr) that defaulted recently — post-fix rollers, SoLR
placements, price-crisis fallbacks."*

**This is a *tenure-on-tariff* continuum, not a categorical typology.** Ofgem's discriminator is
"how long have you sat there" — a **duration**, which is continuous, arbitrarily binnable, and
exactly the observable a latent propensity would generate. The 3-year cut is a reporting convenience
Ofgem chose; nothing in the source asserts a natural three-way kind. **Confidence H that the source
is a duration split; confidence M (inferred) that this implies an underlying continuum** rather than
a mixture of three genuinely distinct types — the data are equally consistent with a two- or
three-component mixture, and no fetched source resolves that. Recorded as inferred, not established.

**The stock-vs-disposition seam must be honoured** (`ENGAGEMENT_MIX_RECONCILIATION_2026-07-22.md`
§0, and repeated in the fusion-register entry's `seam` field): Ofgem RMI measures a **point-in-time
stock** ("is this account on a chosen tariff today"); the SIM's archetype is a **behavioural
disposition** ("does this household shop ~every renewal"). *A household can be Ofgem-active today
and a PASSIVE archetype; an ACTIVE archetype sitting between fixes shows up as Ofgem-default.* Any
build must not treat the Ofgem stock split as a direct read of disposition. **This is the single
easiest way for a continuous-propensity build to go wrong.**

### 2.2 TRANSITIONS — can a household MOVE? (the highest-value question)

**(a) The population demonstrably moved, year on year, in the pre-crisis steady state.** From
`docs/market_research/svt_rates_active_passive_2016_2025.md` §2 (register-held, sourced to the Ofgem
Consumer Engagement Surveys):

- **Ofgem Consumer Engagement Survey 2018:** 29% on SVT 3+ years; 23% on SVT under 3 years; **60%+
  switched once or never.** (register confidence H)
- **Ofgem Consumer Engagement Survey 2019:** **49% never switched or switched once (down from 61%
  the prior year).** (register confidence H)

**A 12-percentage-point movement out of the never/once-switched bucket in a single year is direct
evidence that engagement is not a fixed lifetime trait.** Under the current SIM model this
transition is *impossible by construction* — `engagement_level_for_customer(cid)` returns the same
value forever. **This is the cleanest single justification for the atom, and it comes from the
project's own register.** (Caveat, `inferred`: these are repeat cross-sections, not a panel, so they
show the *population* moved, not that *identified households* moved. A panel source would be needed
to prove household-level transition; none is held in the register — named as an unfetched lead in
§2.5.)

**(b) The 2021–22 price shock — and the honest distinction that must not be lost.** Register §2–3:

| Year | Electricity switches (accounts) |
|---|---|
| 2016 | ~4.82 m |
| 2017 | ~3.84 m |
| 2018 | ~5.54 m |
| 2019 | ~5.88 m (pre-crisis peak) |
| 2020 | ~6.39 m |
| 2021 | ~5.06 m (collapsed H2) |
| 2022 | **near zero** |

(register: *"Source: Energy UK / DESNZ quarterly switching statistics"*, confidence not individually
stamped; treat as M pending re-fetch — named in §2.5.)

**The critical interpretive point, stated because getting it wrong would corrupt the whole atom:**
the 2022 collapse was a **SUPPLY-side withdrawal, not a demand-side disengagement.** Register §3:
*"Suppliers withdrew fixed tariffs — wholesale costs exceeded the Ofgem price cap ceiling so no
viable fixed product could be offered … Customers did not voluntarily churn: no competitive fixed
alternatives existed."* By Apr 2023, ~29 m customers on SVT (~90%) vs ~3 m on fixed (~10%) — a
complete inversion. **This is an *opportunity* collapse and belongs to the market-state proposal
(§0b item 2), NOT to this atom's disposition model.** A build that moves *disposition* to reproduce
the 2022 switching collapse would be modelling the wrong thing and would additionally be
goal-seeking against a known outcome (R12).

**(c) Did the shock leave a scar? — the highest-value number for this atom, and it is NOT anchored.**
The question that *is* this atom's (did households forced onto SVT in 2022 **stay** disengaged after
fixed deals returned in 2023–25, versus resume shopping?) is **not answered by anything in the
register.** The register's §3 closing line — *"Post-2023 recovery: ~one-third of customers on fixed
deals by Jul 2025 (Ofgem State of the Market, Jan 2026). **Closely matches pre-crisis 35% engaged
proportion.**"* — is **evidence of aggregate RECOVERY, i.e. weak or no persistent population-level
scarring**, which is a genuine and useful finding: it argues *against* a large permanent
shock-induced disengagement term. But it says nothing about *which* households returned. **The
persistence/scarring magnitude is UNANCHORED → R10** (§3).

**(d) SoLR — ~4 m customers moved involuntarily.** Register §3: *"29 energy suppliers failed Jul
2021–May 2022, displacing ~4 million customers into SoLR. All placed on SVT."* An involuntary
transition of ~14% of the domestic market into the default bucket, with **no engagement change
implied by the mechanism** — these households' *dispositions* did not change, only their *stock*
did. This is the cleanest real-world illustration of why the stock/disposition seam (§2.1) matters,
and it is a concrete falsifier for any build that infers disposition from tariff state.

**(e) Service episodes.** The SIM already has the channel (`satisfaction_churn.py`, §1.2) but only
in the **more-churn** direction. No fetched source in the register quantifies the **opposite**
direction the director asserts (bad service → *disengaged inertia*, i.e. withdrawal rather than
switching). **UNANCHORED → R10**, and named as an unfetched lead in §2.5.

**(f) Life events.** `W2_5_life_event_stream` is this atom's registered `depends_on` and is built
(`simulation/life_events.py`; `LifeEventType` = BIRTH/DEATH/MARRIAGE/DIVORCE/JOB_LOSS/JOB_GAIN/
RETIREMENT/SERIOUS_ILLNESS/MOVE_IN/MOVE_OUT/BENEFIT_CHANGE). The **home move** is the strongest
a-priori engagement trigger (it forces a supply decision), and the sibling atom `W2_12` has already
mapped that path. **Per-event-type engagement shift magnitudes are UNANCHORED → R10.**

### 2.3 Coupling 2 — engagement × price_sensitivity

See §1.4. The code read supplies something the fusion register did not have: the two axes are
**cited to the same source and the same three-bin shape**
(`segmentation_curriculum_v1.json:16-21`). That is not an external anchor for a *coupling strength*
— it remains true that **no external cross-tab is known**, so a *strength* stays R13
director-reserved exactly as the register says. What it does supply is an argument that a **strength
dial may be the wrong instrument**: two projections of one latent need no dial. Offered as a
proposed sharpening of the register entry; **not** a claim that the coupling is now anchored.

### 2.4 Coupling 4 — the U-shape by affluence

**Status from this session: NOT ANCHORED — and the current code implements the shape that would
refute it.**

The register entry's refutation condition is *"a source showing engagement is MONOTONE in affluence
(rising or falling throughout, no interior peak) would refute the U-shape."*
`simulation/switching_propensity.py:19–24` implements `LOW stress 1.10 > MODERATE 0.85 > HIGH 0.65`
— **strictly monotone**, i.e. today's SIM asserts the refuting shape. (Caveat: `IncomeStress` is a
*stress* axis, not an affluence axis; they are directionally aligned but not identical, so this is
`inferred`, not proof that the SIM contradicts the hypothesis.)

The register's own evidence route — *"Ofgem Consumer Engagement Survey / DESNZ attitude tracker
demographic splits — discovery pass BEFORE hand-setting"* — is precisely what this DISCOVER
attempted. **No demographic cross-tab establishing an interior peak was obtained.** The U-shape
therefore remains `assumed`/`hypothesised`, and **must not be hand-set**: per the register it
CONSTRAINS coupling entry 2 if anchored, so hand-setting it would silently propagate.

**Also binding (director, register `note`):** *"the schema carries no age axis and this does NOT
admit one; whether age becomes a dimension is a generator-side ask reserved to the director. Do not
add an age axis unilaterally."* Honoured — no age axis is proposed anywhere in this document.

### 2.5 UNFETCHED LEADS — named plainly, not paraphrased

None of the following was obtained this session. They are named so a later pass can go straight to
them, and so that nothing below is mistaken for an anchor:

1. **A PANEL (not repeat cross-section) source on household-level engagement transition** — the only
   thing that would prove *identified households* move, rather than the population aggregate moving
   (§2.2a). Nothing in the register is a panel.
2. **Ofgem Consumer Survey, 2021/2022/2023/2024/2025 waves** — the register holds only the 2018 and
   2019 Consumer Engagement Surveys. The post-crisis waves are the ones that would carry the
   scarring answer (§2.2c).
3. **Ofgem "Consumer Impacts of Market Conditions"** — named in the atom brief; not fetched.
4. **CMA Energy Market Investigation Final Report (24 June 2016), the disengagement/inertia
   appendices** — the register holds only the headline *"70%+ Big Six domestic customers on SVT"*
   figure (§2), not the survey-based engagement segmentation appendix that would answer §2.1's
   "is there a published >3-bin typology" question directly.
5. **Citizens Advice consumer research / supplier star-ratings work, and Ombudsman Services energy
   complaints data** — the route to §2.2e (service failure → subsequent engagement), entirely
   unfetched.
6. **Ofgem RMI switching datasets 2023–2025** — the register's switching series stops at 2022 ("near
   zero"); the recovery-side series would sharpen §2.2c.
7. **DESNZ Public Attitudes Tracker demographic splits** — the register's named evidence route for
   the U-shape (§2.4), unfetched.
8. **Re-fetch of the 2016–2022 switching-volume series** (§2.2b) — held in the register sourced to
   "Energy UK / DESNZ quarterly switching statistics" without a per-row confidence stamp; treat as M
   until re-fetched.

---

## 3. What is ANCHORED vs what stays R10

### 3.1 Anchored (a published figure, cited, held in the register)

| Quantity | Value | Source | Conf |
|---|---|---|---|
| Population shares of the three bins | 0.45 / 0.35 / 0.20 | Ofgem RMI Oct-2025 default-tariff panel → **R13-RATIFIED by the director**, commit `9542cdd1b`. **Not the agent's to move.** | H (and *ratified*, which is stronger than anchored for this purpose) |
| Ofgem's own split of the default majority | 20.3% held 3+ yr / 34.6% held <3 yr (elec) | Ofgem RMI Oct-2025 | H |
| The population's engagement composition CHANGES year-on-year | 61% → 49% never/once-switched, 2018→2019 | Ofgem Consumer Engagement Surveys 2018, 2019 | H |
| Switching collapsed to ~zero in 2022 and it was SUPPLY-side | ~5.9 m (2019 peak) → ~0 (2022); ~90% SVT by Apr 2023 | Energy UK / DESNZ quarterly switching statistics; register §3 | M–H |
| Aggregate engagement RECOVERED post-crisis to ≈ its pre-crisis level | ~⅓ on fixed by Jul 2025 vs ~35% pre-crisis | Ofgem State of the Market, Jan 2026 | H |
| ~4 m customers moved involuntarily to SVT via SoLR | 29 supplier failures, Jul 2021–May 2022 | register §3 | H |

### 3.2 Stays R10 — MUST be sampled from a distribution, never a point estimate, with the gap stated in the build docstring

1. **The SHAPE of the latent propensity distribution within each ratified bin.** No source gives a
   within-bin density. A build must state the shape it assumes and why, and must not present it as
   anchored. (The *bin boundaries* are fixed by the ratified shares; the *density between them* is
   not.)
2. **Whether the underlying construct is truly continuous or a 2–3 component mixture** (§2.1) — the
   Ofgem duration split is consistent with both.
3. **Post-price-shock persistence / "scarring" magnitude** — the atom's highest-value unknown
   (§2.2c). The one directional constraint available is that **aggregate recovery to pre-crisis
   levels argues for a SMALL persistent term**; a build must not choose a large one, and must sample.
4. **Service-episode → engagement shift, magnitude AND sign** (§2.2e). The existing satisfaction
   channel only points one way; the director asserts the other way exists. Entirely unanchored.
5. **Per-life-event engagement shift magnitudes** (§2.2f), including the home move.
6. **Any engagement × price_sensitivity coupling STRENGTH** — R13 **director-reserved** (fusion
   register, explicit). Not R10-samplable by the agent: it is a curriculum dial, not an uncertainty.
7. **The U-shape by affluence: existence, position of the interior peak, and depth** (§2.4).
   Must not be hand-set — it constrains item 6.
8. **Mean-reversion / decay rate** — if propensity moves, does it drift back? Nothing anchors a
   half-life. Directly coupled to item 3.

### 3.3 An R13 question this DISCOVER surfaces that only the DIRECTOR can answer

**Is `ENGAGEMENT_POPULATION_SHARE = 0.45/0.35/0.20` an ENTRY distribution or a STEADY-STATE
distribution?**

The ratification (`9542cdd1b`) does not say, because with an immovable trait **the two are
identical** — the question could not arise. **A movable propensity forces the distinction:**

- If **steady-state**: the movement mechanism must be **stationarity-preserving** — transitions in
  both directions balanced so the long-run distribution equals the ratified mix. Buildable, but it
  is a real design constraint that must be *proven*, not assumed, and it forbids any net drift.
- If **entry/cohort-entry**: the shares hold at acquisition, and the book's *observed* composition
  legitimately drifts away from 0.45/0.35/0.20 over time.

**These give materially different books, and choosing between them is an R13 curriculum call — the
director's, never the agent's.** This is the principal reason the *movement* half of this atom
cannot be built in this fork (§5). It is raised here as a recommendation, not a bare ask:
**recommended default = STEADY-STATE with a stationarity proof**, because it is the reading that
cannot silently move a ratified number, and because §2.2's evidence (population composition moves
year to year, then *recovers* to its pre-crisis level after the largest shock in the market's
history) is more consistent with a stationary distribution with churn between states than with an
entry distribution that drifts.

---

## 4. What an L1 build would add — three concrete things, at the named seam

All three are **additive** to `simulation/household_segments.py`. **No existing public function
changes signature or behaviour** (three sibling subsystems import from this module).

1. **`engagement_propensity_for_customer(customer_id) -> float` in [0,1]** — the latent. Drawn from
   its **own named seeded substream** (C-S2), following this codebase's established
   `_substream(base_seed, name)` stable-sha256 pattern (`simulation/sme_distress.py:170–197`,
   `simulation/household_budget.py:36–47`, `simulation/population_draw.py:390–401`) so the new draw
   can **never** shift `engagement_{cid}` or any sibling subsystem's sequence. This matters more here
   than almost anywhere: `household_segments.py` is imported from all over the tree.

2. **`engagement_level_from_propensity(p) -> EngagementLevel`** — the projection, with the bin
   boundaries derived from the **ratified** `ENGAGEMENT_POPULATION_SHARE` cumulative walk (so the
   boundaries move if and only if the director moves the shares; there is no second copy of the
   ratified numbers to drift). Together with (1), constrained by the **exact refinement identity**
   of §1.3 — R13 preservation *by construction*.

3. **The movement interface, as a pure function with no call sites yet** —
   `engagement_propensity_after(base_propensity, ...) -> float`, sampling every shift magnitude from
   an R10 distribution (§3.2 items 3–5) rather than a point estimate, with the gap stated in the
   docstring. **This third item is where L1 stops and the atom's real cost begins** (§5).

**What a build must NOT do:** touch `ENGAGEMENT_POPULATION_SHARE` (R13); infer disposition from
tariff stock (§2.1); hand-set the U-shape (§2.4); reproduce the 2022 collapse by moving *disposition*
(§2.2b, R12); introduce an age axis (§2.4, director-reserved); or unify engagement with
`price_sensitivity` inside `population_draw.py` / `segmentation_curriculum_v1.json` (R13 curriculum
surface, out of scope).

---

## 5. Build-size verdict, and disposition

**Verdict: the atom does NOT fit in one L1 fork. Items 1–2 of §4 do; item 3 does not.**

The honest split:

- **Items 1–2 (the re-representation) ARE small, additive and share-preserving.** Two pure
  functions, one exact identity, one named substream; the identity makes the R13 guarantee
  structural. This delivers the *first* half of the director's ask — *"the propensity is a
  distribution across the population, not three discrete boxes."*
- **Item 3 (movability) is NOT L1-in-one-fork**, for four independent reasons, any one of which is
  sufficient:
  1. **An unresolved R13 question blocks it** — entry vs steady-state (§3.3). Building either
     reading before the director rules risks silently moving a ratified number. This is a wall, not
     a dial.
  2. **Its magnitudes are entirely unanchored** (§3.2 items 3–5) and the most valuable one — post-
     shock persistence — has an explicitly named unfetched evidence route (§2.5 items 1, 2, 6). A
     build now would be sampling from invented distributions across the atom's whole substance.
  3. **The registered couplings are structurally inexpressible** (§1.4): `Cohort` has no engagement
     field, and unifying engagement with `price_sensitivity` requires `population_draw.py` and
     `segmentation_curriculum_v1.json` — the R13 curriculum surface, outside this fork's file scope.
  4. **If the U-shape anchors, `switching_propensity.py` must change** (§2.4) — also outside this
     fork's file scope.
- **What it would take:** (a) a director R13 ruling on §3.3; (b) a real evidence pass against §2.5
  items 1, 2, 5 and 6 (the post-crisis Ofgem Consumer Survey waves and a panel/scarring source);
  (c) a single-fork build spanning `household_segments.py` + `population_draw.py` +
  `switching_propensity.py` + `segmentation_curriculum_v1.json`, which is a coordinated multi-file
  atom, not an L1 increment.

**Therefore this fork builds §4 items 1–2 only** — the share-preserving continuous substrate — and
stops deliberately short of item 3, leaving `engagement_level_for_customer` and every consumer
byte-for-byte unchanged in behaviour. That is a genuine capability (the distribution now exists and
is provably the same population) and it is the substrate item 3 will need, with **zero** risk to the
ratified mix.

**Level:** L1 **PROPOSED** (this log). `level_current` stays 0 in the map — the cell move is the
orchestrator's/director's per R16; this fork is not the map writer.

---

**Evidence.** Job 1 code seam read directly from the working tree at this DISCOVER's HEAD
(`simulation/household_segments.py`, `simulation/run_phase2b.py`, `company/crm/churn_model.py`,
`simulation/switching_propensity.py`, `simulation/satisfaction_churn.py`,
`simulation/population_draw.py`, `docs/design/segmentation_curriculum_v1.json`,
`docs/market_research/population_fusion_assumptions_register.json`, `tools/generate_customer_sample.py`,
`tools/generate_dashboard_data.py`). Job 2 anchors from
`docs/market_research/svt_rates_active_passive_2016_2025.md`,
`docs/design/ENGAGEMENT_MIX_RECONCILIATION_2026-07-22.md`, and
`docs/market_research/continuous_behavioural_engagement_w2_14.md` (this session's research pass).
R13 ratification verified against commit `9542cdd1b` in git, not against a commit message claim (R16).
