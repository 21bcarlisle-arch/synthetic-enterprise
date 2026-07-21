# D-SEGMENT joint-structure DISCOVER pass — what cohort structure already exists, what external evidence supports it

**Serves:** Step 1, `docs/design/SEGMENTATION_WIRING_PLAN.md` (Part 2 of DIRECTOR_STEER_LEGIBILITY_AND_SEGMENTATION_2026-07-20).
**Status:** DOC-ONLY. No generator/simulation code read or changed. Discovery-agent pass, 2026-07-21.

## 0. A hard scope note the dispatching agent should read first

The discovery-agent role this pass runs under carries an explicit, "critical" constraint: *read
only external published sources and `docs/market_research/`; never read `sim/`, `simulation/`,
`company/`, `saas/`, or derive values from simulation outputs.* That wall is designed to stop
market-research findings being contaminated by circular reference to the very system they exist
to validate (the same anti-tautology logic as R15's "checked value derived from the same source
it checks").

The plan's Deliverable 1 asks for a trait inventory sourced by reading `simulation/household.py`,
`household_demand.py`, `premise_demand.py`, `demand_model.py`, `nudge_physics.py`,
`household_segments.py`, `arrears_engine.py`, and `adoption_geography.py` directly. **That is
outside this role's epistemic wall and this pass did not do it.** What follows instead is a trait
inventory **reconstructed from existing `docs/market_research/` DISCOVER documents** — prior
passes by agents who did have code access, writing structured findings about those same modules.
Every row below cites the specific prior doc it comes from, not the code itself. This is a real
limitation, flagged honestly (R9) rather than silently worked around: **a companion pass by an
agent with code-read permission (FRAME lane) should confirm exact function names, line numbers,
and RNG substream identifiers against the live source before FRAME finalises the clustering
design.** Where a prior doc's own stated atom status ("DISCOVER only, BUILD gated") appears to
conflict with the plan's claim that a coupling is already live in code, that conflict is flagged
below rather than resolved — resolving it needs a code read this pass cannot do.

Deliverables 2 and 3 are within the role's normal scope and are the more load-bearing sections
below.

---

## 1. Deliverable 1 — repo-side trait inventory, reconstructed from prior DISCOVER docs

### 1a. Need (house physics + occupancy)

| Trait | Where (per prior doc) | Independent or correlated? | RNG substream | Provenance of this row |
|---|---|---|---|---|
| EPC band / thermal efficiency | `household.py` (per ASSUMPTIONS.md "Household Physical Property Attributes") | Not stated as correlated to anything else in the docs read; ASSUMPTIONS.md logs it against EHS 2022-23 marginals only | Not stated | ASSUMPTIONS.md L86-99 |
| Property type / build era | `household.py` | Independent marginal draws per ASSUMPTIONS.md; no cross-tab wiring described | Not stated | ASSUMPTIONS.md L91-92 |
| Heating system (gas boiler / heat pump %) | `household.py` | Independent marginal | Not stated | ASSUMPTIONS.md L93 |
| Occupancy / household size | Implied in `household.py`/`household_demand.py` per Phase 2 registration | ASSUMPTIONS.md logs occupancy as its own Census-anchored marginal (TS017), not cross-tabbed to tenure/EPC in any doc found | Not stated | ASSUMPTIONS.md L109-110 |
| Tenure | `household.py` (property-attribute layer) | ASSUMPTIONS.md logs tenure split (EHS) as its own marginal | Not stated | ASSUMPTIONS.md L111 |
| Solar PV / EV adoption (asset ownership) | `household.py` property layer + W1_10 `adoption_geography.py` | **Correlated — geography.** The most recent build commit (`ca546f5cf`, this session's own git log, not code content) states W1_10 landed "regional adoption field (a_{k,r}=a_k·m_{k,r}), spatial-correlation Cholesky" — i.e. adoption propensity is explicitly modelled as spatially correlated across regions via a Cholesky factor, not an independent per-household draw. This is a genuine already-built joint structure (adoption × geography). | Not stated (commit message only) | git log (commit subject line, not code read) + ASSUMPTIONS.md L94-95 |
| Smart meter penetration | `household.py` / Phase 50 model | Time-varying population-level rollout curve (10%→75%, 2016-2025), not described as per-household-correlated to anything | Not stated | ASSUMPTIONS.md L96 |
| Premise demand shape | W1_5 (`premise_demand.py` implied) | Named in the plan itself as a precedent for additive, ground-truth-preserving extension (`premise_demand_shape`) — not independently confirmed here | n/a | SEGMENTATION_WIRING_PLAN.md L33 |

**Honest gap:** the plan's own framing ("EPC/thermal... heating type, occupancy pattern") implies
`demand_model.py` is where these combine into an actual load shape, but no prior market-research
doc describes that combination directly — this pass found marginal anchors for each trait
individually, not the internal joint structure the generator uses to combine them. That is
precisely the kind of thing only a direct code read (or a FRAME-lane companion pass) can confirm.

### 1b. Attitudes & values

| Trait | Where (per prior doc) | Independent or correlated? | RNG substream | Provenance |
|---|---|---|---|---|
| FramingSusceptibility, ToneSusceptibility (hidden traits) | `nudge_physics.py` | NUDGE_PHYSICS_BENCHMARKS.md states the project's own population-anchoring convention: "sample each customer's susceptibility from a distribution across the published range rather than a fixed constant" — this describes an **independent per-customer draw** from a benchmark range; no correlation to Need or Engagement axes is described anywhere in that doc | Not stated | NUDGE_PHYSICS_BENCHMARKS.md L23-24 |
| Willingness-to-pay / can't-pay-won't-pay classification (W2_7) | `simulation/` (module not named in its own DISCOVER doc; W2_7 registration text implies a dedicated classifier) | Not describable — the atom's own DISCOVER doc (`willingness_classification_incidence.md`) states the atom is **"DISCOVER only... BUILD stays gated pending epoch sequencing"** and that no whole-population incidence split was found even after two search passes. **This conflicts with the SEGMENTATION_WIRING_PLAN's own claim that "W2_7 ability couples byte-identical to W2_4 budget — a real joint structure already present."** Flagged, not resolved — needs a direct check of current `maturity_map.yaml`/code state, since the DISCOVER doc may simply predate a later BUILD. | Unknown | willingness_classification_incidence.md; SEGMENTATION_WIRING_PLAN.md L22 |
| Bill-shock aversion / trust-reassurance need | Not located in any prior doc under a specific filename | No evidence found either way | Unknown | — (gap) |
| CO₂/mission salience | Plan itself calls this "new, thin today" | n/a — plan's own admission, not this pass's finding | n/a | SEGMENTATION_WIRING_PLAN.md L16 |

### 1c. Engagement capacity & behaviour

| Trait | Where (per prior doc) | Independent or correlated? | RNG substream | Provenance |
|---|---|---|---|---|
| Engagement archetype (ACTIVE 48% / PASSIVE 23% / DISENGAGED 29%) | `household_segments.py`, Phase 2 Layer 1 (built 2026-07-08 per ASSUMPTIONS.md) | Calibrated to reproduce `company/crm/churn_model.py`'s existing ~35% flat churn rate in aggregate — i.e. it is a **population-level calibration constraint**, not a stated per-household correlation to Need/Attitude axes. ASSUMPTIONS.md separately flags the underlying Ofgem anchor (2018 SVT-tenure survey, 48/23/29%) is now stale against Ofgem's Oct-2025 data (45%/55% actively-chosen/default) — a director recalibration decision explicitly deferred, not actioned. | Not stated | ASSUMPTIONS.md L116 |
| Payment channel (`payment_channel_for_customer()`) | `household_segments.py` | Exists as its own archetype field; ASSUMPTIONS.md L136 explicitly notes it is **not yet wired into** `sim_satisfaction.py` even though a real satisfaction-by-payment-method anchor exists (a genuine, named, currently-unexploited joint-structure opportunity) | Not stated | ASSUMPTIONS.md L114, L136 |
| Payment method segmentation (resi/SME/I&C) | `arrears_engine.py::payment_method()` | Described as "segment-aware... but not archetype-aware within resi" (ASSUMPTIONS.md L114) — i.e. varies by customer class (resi/SME/I&C) but not by the resi engagement archetype above; a stated **gap between two related traits that should plausibly be linked but currently are not** | Not stated | ASSUMPTIONS.md L114 |
| `organisation` latent (W2_10, DD-attribution confound) | `simulation/dd_attribution.py` | **Explicitly, precisely correlated — the clearest already-built joint structure found this pass.** Per `dd_attribution_confound_w2_10.md`: the hidden `organisation` latent blends "an idiosyncratic conscientiousness draw (60%, own substream...) with the affordability signal (income decile) read from `simulation.household_budget` (W2_4, 40%)." Organisation then drives BOTH DD-adoption AND arrears risk — a genuine common-cause/back-door structure (a textbook confound), not accidental correlation. This is the plan's cited example, and it checks out against the prior doc's own text. | **Yes — "own substream" stated for the 60% idiosyncratic component**; the 40% component reads directly from the W2_4 module rather than drawing its own randomness | dd_attribution_confound_w2_10.md L56-63 |
| Income stress tier | `simulation/sim_satisfaction.py` consumes a 3-tier income-stress signal; W2_4 `household_budget` names income band/essential-cost floor/discretionary margin/savings buffer/priority-of-debts as five hidden components | W2_4's own DISCOVER doc states its status as **"DISCOVER only... BUILD stays gated"** — same discrepancy noted for W2_7 above: the dd_attribution doc (W2_10) describes W2_4 as already a live, readable module (`simulation.household_budget`), while W2_4's own doc describes itself as not yet built. One of the two is stale; cannot resolve without a code read. | Not stated | household_budget_w2_4.md header; dd_attribution_confound_w2_10.md L59-60 |
| Budget margin (W2_4) × savings buffer | W2_4 (household_budget) | **External evidence says this SHOULD be a joint distribution, not independent** — see Deliverable 2 (FCA Financial Lives finding) — but the DISCOVER doc records this as a design recommendation for the (not-yet-built, per its own status line) atom, not a confirmed built correlation | n/a | household_budget_w2_4.md L69-70 |
| Self-rationing propensity (W2_8) | Named in the plan, no dedicated prior DISCOVER doc found in this pass's search of `docs/market_research/` | No evidence found | Unknown | — (gap) |
| Adoption journey / friction-vs-reward-responsiveness traits (C4) | `simulation/` adoption-journey module (unnamed in its own doc) | adoption_physics_c4.md: friction sources are "genuine STRUCTURAL... not purely attitudinal" and explicitly separated from "reward responsiveness" as two distinct trait axes already in the atom's own trait list — i.e. the atom's own design already treats these as separate, not fused, axes | Not stated | adoption_physics_c4.md L26-35 |

### 1d. Counts and the headline structural finding

| Family | Trait axes inventoried | Already-correlated (per prior docs) | Independently drawn (per prior docs) | Status unclear / discrepancy flagged |
|---|---|---|---|---|
| Need | 9 | 1 (adoption × geography, W1_10 Cholesky) | 7 | 1 (demand_model combination logic — no doc found) |
| Attitudes & values | 4 | 0 confirmed built | 1 (nudge susceptibilities — independent by stated convention) | 3 (W2_7 status conflict; bill-shock/trust trait not located; CO₂ salience admitted thin) |
| Engagement & behaviour | 8 | 1 confirmed built (`organisation`, W2_10, byte-adjacent to W2_4) + 1 recommended-but-unconfirmed (budget×savings, W2_4) | 3 (engagement archetype, payment channel, arrears payment_method — each independently anchored, not cross-linked to each other) | 3 (W2_4 status conflict; W2_8 not located; the archetype↔`sim_satisfaction.py` non-wiring gap) |

**The headline finding for FRAME:** across 21 trait axes reconstructed from prior docs, only
**2 are described as already jointly-structured in a way this pass could confirm** — W1_10's
spatial adoption correlation, and W2_10's `organisation` latent (which itself only half-exists,
since it reads from a W2_4 module whose own DISCOVER doc says it isn't built yet). **The default
state of the existing trait vector, as far as `docs/market_research/` evidences it, is
independent draws per axis, calibrated individually against a real marginal but not against each
other.** This directly supports the plan's own diagnosis ("today the population carries its
factors one axis at a time") — the joint structure the plan wants clustered largely does not yet
exist to be clustered; FRAME needs to decide whether the cohort layer imposes it going forward, or
whether generator changes (a separate, gated BUILD step) are needed first to create genuine joint
variance for a clustering pass to find.

---

## 2. Deliverable 2 — external joint-structure anchors

### 2.0 A directly relevant sibling artefact found first (not this pass's own fetch, but decisive)

Before any new fetch, this pass found `docs/market_research/POPULATION_COVERAGE_NESTED_DESIGN.md`
and `POPULATION_COVERAGE_JOINT_STRUCTURE.md` — a **separate, already-landed DISCOVER/DESIGN track**
(`DIRECTOR_STEER_POPULATION_COVERAGE_DESIGN_2026-07-20`) that did exactly this pass's Deliverable 2
job already, for a 12-axis cohort schema, with real fetched Census/DfT joint data (Cramér's V +
tail-lift, n≈24.78M households), committed to `docs/market_research/population_coverage/*.json`.
**This is the single most load-bearing finding of this pass** — not a new number, but a discovery
that D-SEGMENT's Deliverable 2 substantially already exists and should be reconciled with, not
duplicated (see Deliverable 3 §3b).

Headline reusable results from that track (full citation trail already in that doc, not re-derived
here):
- **tenure × cars/van**: Cramér's V 0.303 (moderate), tail lift 2.1× — coupled, Census RM131.
- **accommodation × tenure**: V 0.273, tail lift 2.3× — coupled, Census RM003.
- **tenure × NS-SeC (class)**: V 0.229, tail lift 3.3× — coupled, Census RM138.
- **heating fuel × region**: V 0.070 (aggregate "orthogonal") but tail lift **3.8×** (oil-fuel
  concentration in Wales vs London) — the doc's own headline finding that aggregate association
  measures are the wrong lens for a worst-cell design; must gate on tail lift, not aggregate V.
- **Attitudes (green stance, price sensitivity), Engagement (channel preference), and low-carbon
  tech (solar/EV/battery)** are ALL currently classified `assumed` (crossed as independent) in that
  design's schema — an enforced fusion gate reclassified four previously-optimistic `fused` entries
  down to `assumed` because "fuse only with positive evidence" could not be met. **This is the same
  finding as Deliverable 1's headline above, arrived at independently by a different track**:
  Attitude/Engagement/tech-adoption axes have no measured joint structure against Need in the
  existing evidence base.

### 2.1 New fetch this pass — DESNZ Public Attitudes Tracker, Spring 2026 (a genuinely disjoint validator for the Attitudes family)

**domain**: other (household attitudes/adoption-propensity segmentation)
**assumption_tested**: whether attitude/adoption-likelihood traits (the plan's "Attitudes &
values" family) show real cross-tab structure against Need axes (tenure, age) independent of the
Census-based generator anchors already used for the Need family — i.e. a genuinely disjoint
validator, not the same survey re-cited.
**benchmark_value**: Net Zero heating-change knowledge: 42-48% (age 45+) vs 26-31% (age 16-44);
45% (owner-occupied) vs 25% (rented). Heat-pump knowledge: air-source 33% (owner-occupied) vs 17%
(rented); ground-source 28% vs 15%. Heat-pump install-likelihood: 42% of renters say "not my
decision to make" vs 7% of owner-occupiers (both heat pump types) — a real, quantified,
tenure-gated **structural adoption blocker**, not merely an attitude gap.
**confidence**: H (official DESNZ accredited statistics release, live fetch)
**source**: DESNZ Public Attitudes Tracker: Heat and Energy Use in the Home, Spring 2026, UK.
gov.uk/government/statistics/desnz-public-attitudes-tracker-spring-2026/... — fetched live
2026-07-21 (published 2026-07-02, fieldwork n≈3,386-3,389).
**date**: 2026-07-21
**finding**: This is a methodologically distinct survey instrument (DESNZ attitudes tracker) from
the Census data underpinning the population-coverage Need-axis work — a genuine disjoint validator
per the plan's anti-marking-own-homework requirement. It directly **challenges** the
population-coverage register's "assumed" (independent) classification of the tech-adoption/green
attitude axes: tenure and age both show real, large, consistent attitude/adoption-likelihood gaps
(15-20 percentage points), and — decisively — the "not my decision" renter finding shows the
adoption gap is not purely attitudinal but **structurally gated by tenure** (a landlord-decision
constraint), which is exactly the kind of real joint structure the plan is looking for. Action
warranted: FRAME should treat tenure (already a Need-axis Census anchor) as a real coupling key for
at least one Attitudes/adoption trait, rather than accepting the population-coverage register's
current "assumed"/crossed treatment as final for this specific pair.

### 2.2 Reused anchors (already fetched by prior passes, cited not re-fetched, each already [L]/H-tagged in their source docs)

- **Ofgem/Citizens Advice satisfaction Wave 20 (Jan 2025)**: satisfaction by payment method — DD
  82%, prepayment 80%, standard credit 76% (ASSUMPTIONS.md L136). A real Engagement-family
  cross-tab (payment channel × satisfaction), independently sourced from the Census/DESNZ material
  above — usable as a disjoint validator for the Engagement family specifically.
- **FCA Financial Lives**: savings buffer strongly co-varies with income band (<£15k: 22% no
  savings, >1/3 <£1,000; >£50k: majority hold >£10,000) (household_budget_w2_4.md L68-70). A real,
  disjoint (FCA, not Census/DESNZ) anchor for the Engagement/hardship family's internal joint
  structure (income × savings buffer), supporting the plan's coupling intuition for W2_4 even
  though W2_4 itself is not yet confirmed built.
- **StepChange client data (2023-24)**: 41-55% of debt-advice clients with energy-bill
  responsibility carry arrears; of those, 47% have a negative budget (willingness_classification_incidence.md
  L32-42) — real evidence the can't-pay/won't-pay split skews toward ability constraints, but from a
  self-selected (distressed) sub-population, explicitly not a whole-population incidence figure.
- **Nesta consumption-pattern clusters**: "tech-affluent" household profiles show 30-40% ToU
  adoption vs 2.8-9% population average (adoption_physics_c4.md L18-24) — the plan's own named
  example anchor, confirmed present and real, but the underlying archetype definitions were "not
  investigated in depth" by that prior pass — a genuine open item this pass also did not close
  (would need Nesta's primary report, not just the summary already in `docs/market_research/`).

### 2.3 What this pass could NOT verify (honest — R9)

- No published cross-tab was found (this pass or reused) linking **FramingSusceptibility/
  ToneSusceptibility** (nudge traits) to any demographic or Need axis. NUDGE_PHYSICS_BENCHMARKS.md
  itself flags most of its evidence base as cross-domain imports (retail pricing, tax debt, savings
  products) rather than UK-energy-specific, so even the marginal ranges carry only M/L confidence on
  magnitude — a joint-structure claim here would be materially weaker still. **[UNVERIFIED — genuine
  gap, not a network failure]: no external source located this pass evidencing attitudinal-nudge-
  susceptibility correlated with any other axis.**
- The whole-population (not self-selected/distressed-only) can't-pay/won't-pay split (W2_7) remains
  unresolved after three independent search attempts across two DISCOVER passes (the prior pass's
  two, plus a check this pass did not re-attempt given the prior pass's own conclusion that it is
  "confirmed genuinely un-anchorable via this method"). This stays an R13 director-curriculum
  candidate, not a research gap to keep re-searching.
- Network access WAS available this pass (unlike the "no network in autonomous runs" caution in
  standing memory) — curl to gov.uk, DuckDuckGo HTML, and Nesta all returned 200s. So absence of a
  finding above is a genuine "not found," not an access failure.

---

## 3. Deliverable 3 — gaps & FRAME hand-off

### 3a. Evidenced vs asserted, by combination

**EVIDENCED (real cross-tab exists, estimable — a clustering pass can be validated against these):**
1. tenure × accommodation × cars/van × NS-SeC class (Census, coupled block, population_coverage track)
2. heating fuel × region, specifically the off-gas tail (Census, tail lift 3.8×)
3. tenure × Net-Zero/heat-pump attitude & adoption-likelihood, INCLUDING the renter "not my decision"
   structural gate (DESNZ PAT Spring 2026 — new this pass)
4. age × attitude/adoption-likelihood (DESNZ PAT Spring 2026 — new this pass)
5. payment channel × satisfaction (Ofgem CSAT Wave 20)
6. income band × savings buffer (FCA Financial Lives) — evidenced externally, not yet confirmed
   wired into the (possibly-not-yet-built) W2_4 module
7. `organisation` latent × (DD adoption, arrears risk) — the one genuinely-built internal joint
   structure this pass found (W2_10 ↔ W2_4), assuming the W2_4-not-yet-built status flag is stale

**ASSERTED (no cross-tab found; must become a named R10/R13 simplification, not a silent parameter):**
1. green stance × any Need axis (population-coverage register: `assumed`, gate-enforced)
2. price sensitivity × income/class (population-coverage register: `assumed`, was `fused`, downgraded)
3. channel preference × age (population-coverage register: `assumed`, was `fused`, downgraded)
4. solar PV / EV / battery co-ownership × tenure/income (population-coverage register: `assumed`)
5. FramingSusceptibility / ToneSusceptibility × any other axis (no anchor found, this pass, §2.3)
6. engagement archetype (ACTIVE/PASSIVE/DISENGAGED) × Need axes (no cross-tab found; only
   anchored to its own stale SVT-tenure marginal)
7. willingness-to-pay whole-population can't-pay/won't-pay split (confirmed un-anchorable, W2_7's
   own doc, R13 candidate already flagged there)
8. self-rationing propensity (W2_8) × anything (no prior doc located at all)

### 3b. Open questions for FRAME (top 3, plus 2 more flagged for completeness)

1. **Reconcile-or-diverge from `POPULATION_COVERAGE_NESTED_DESIGN.md`'s cohort schema.** That
   track already built a 12-axis schema with a mechanised collapsibility rule (cross if weak in
   BOTH aggregate Cramér's V and tail lift; couple otherwise) and a fusion gate that reclassifies
   optimistic `fused` claims down to `assumed` when the residual is unmeasurable. FRAME must decide:
   is D-SEGMENT's per-customer trait-vector clustering the SAME object as that cohort schema (in
   which case reuse its schema/gate/register rather than re-deriving one — the plan's own "cluster
   real structure, don't invent a parallel taxonomy" principle applies here first), or is it a
   genuinely different object (e.g. that track sizes a *training/coverage* population while
   D-SEGMENT clusters the *live customer-book* generator's trait vector)? This is the single
   highest-leverage open question — get it wrong and the project builds two competing taxonomies.
2. **Clustering method and the mixed-type problem.** The existing traits span continuous (budget
   margin, savings buffer), ordinal (income band, EPC), categorical (tenure, heating fuel,
   engagement archetype), and hidden-continuous (organisation latent, susceptibility scores) types.
   Plain k-means needs a defined distance (Gower or similar) or a latent-class/mixture model — and
   given §2.0's collapsibility-rule precedent already exists and is mutation-testable (R15), FRAME
   should evaluate reusing THAT mechanism (cross weak/weak pairs, couple the rest, worst-cell-scored)
   rather than introducing a second clustering methodology.
3. **The coupled-triad gap needs an observable-proxy map before it can be built.** Per
   ARCHITECTURAL LAW, the company must discover cohort structure from **observables only** — never
   read the SIM trait vector. Several axes inventoried in Deliverable 1 have NO plausible real-world
   observable proxy at all (green stance, framing/tone susceptibility, CO₂ salience — a real
   supplier cannot directly observe these). FRAME must state, per trait, what observable a real
   supplier COULD use as a proxy (payment history for `organisation`; smart-meter usage shape for
   Need; complaint/switching behaviour for engagement) — traits with no plausible proxy either stay
   permanently hidden-truth-only (never part of a company-discoverable cohort) or need a different
   scope decision, not a clustering-method decision.
4. **Worst-cell metric shape is a company-scoring-frame decision, not a market-research one** — this
   pass cannot resolve whether "worst cell" means smallest-N-populated, lowest-margin, or
   highest-risk; couples directly to Atom A's scoring frame (SEGMENTATION_WIRING_PLAN.md L28) and
   should be decided there, not inferred from external benchmarks.
5. **Resolve the W2_4/W2_7 build-status discrepancy.** Two prior DISCOVER docs describe these atoms
   as not-yet-built (BUILD gated); the W2_10 doc and the SEGMENTATION_WIRING_PLAN both describe W2_4
   as already live and read from. A direct code/maturity-map check (outside this role's wall) is
   needed before FRAME assumes either state.

---

*Discovery-agent pass, 2026-07-21. Deliverable 1 reconstructed from `docs/market_research/` prior
docs only (epistemic wall — no `simulation/` code read, flagged §0). Deliverables 2-3 within normal
scope; network access confirmed available (§2.3). No fabricated figures; every external claim
above carries a cited, fetched, or previously-committed source.*
