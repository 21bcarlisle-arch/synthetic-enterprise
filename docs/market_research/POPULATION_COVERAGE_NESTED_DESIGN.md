# Population Coverage — Stage 3: The Nested Worst-Cell Design

**Track:** DIRECTOR_STEER_POPULATION_COVERAGE_DESIGN_2026-07-20 (learning loop, DISCOVER)
**Stage:** 3 of the loop — *nested worst-cell coverage design, built on the committed stage-2 numbers.*
**Authority:** the director's stage-3 direction (proceed as recommended; gate on tail lift; nested greedy;
first-class worst cells; mechanise the fusion bar; threshold is the director's dial).
**Status:** DESIGN + committed structure only. **No generator change** (that is the later, director-reserved
step). **No new fetch. No microdata.** Everything below derives from the stage-2 committed numbers.

> Committed machine-readable structure (all in `docs/market_research/`):
> `population_coverage/cohort_schema.json` (the permutation space + provenance),
> `population_coverage/nested_design.json` (the 1000 nested cohorts + worst-cell scores + marginal gains),
> `population_coverage/threshold_sensitivity.json` (the design rebuilt at 1.3 / 1.5 / 1.75 / 2.0),
> and the **enforced fusion gate** now mechanised in `population_fusion_assumptions_register.json`.
> The build is deterministic and hash-independent (verified identical under `PYTHONHASHSEED` 0 and 1).

---

## 0. Headline for the director (read this first)

1. **The design reaches complete coverage at N=200.** Worst-cell coverage crosses 0 → 1.0 between N=100
   and N=200 — i.e. by N=200 *every* target tuple that matters is hit at least its required number of
   times. N=500 and N=1000 do not add *new* coverage; they add **statistical mass** (redundancy) on the
   rare cells, which is what a learner needs to *learn* a worst cell rather than merely contain one
   household in it. **§4.**
2. **The tail-lift threshold is NOT material between 1.3 and 2.0 — with one honest caveat.** Rebuilt
   end-to-end at all four thresholds: coverage-to-complete (N=200), population composition (agrees to
   ≤0.6 percentage points), and the identity of the worst cells are **identical**. The *only* measurable
   effect is at the largest N: the lower thresholds (1.3/1.5, which *couple* `tenure × region`) buy about
   **10% more redundancy on the rare cells at N=1000** (named cells hit 31× vs 28×) than the higher
   thresholds. So the dial is yours by right, the band is immaterial for *what gets built*, and if
   anything the evidence mildly favours the **low** end (deeper tail redundancy). **§2 and §4.**
3. **Mechanising the fusion bar bit.** Encoding "fuse only with positive evidence" as an enforced,
   machine-checkable gate *reclassified four entries* stage-2 had optimistically called `fused`
   (EV×income, solar×tenure, price-sensitivity×income, channel×age) down to `assumed` (crossed) — because
   their residual is unmeasurable, which the gate treats as *no evidence*. There are now **zero permitted
   fusions**; every non-observed pair is crossed. The design already crossed them; the gate makes the
   register honest too. **§3.**

---

## 1. The cohort schema (the permutation space)

Twelve factor axes, each tagged with provenance (`observed` / `fused` / `assumed`) exactly as a published
figure carries its claim status. Full detail: `cohort_schema.json`.

| Group | Factor | Levels | Provenance | Note |
|---|---|---|---|---|
| **Coupled block** (spine = tenure) | tenure | 4 | observed | Census RM003/TS054 |
| | accommodation | 5 | observed | incl. caravan (a real fabric worst-cell) |
| | cars/van | 3 | observed | affluence / EV-adjacency proxy |
| | NS-SeC class | 4 (banded from 9) | observed | open income/class proxy; true income FRS-gated |
| **Fabric/fuel** | heating fuel | 7 (banded from 12) | observed | **pinned to region** (its only open joint) |
| **Geography** | region | 10 | observed | 9 English regions + Wales |
| **Attitudes (E)** | green stance | 3 | **assumed** | never jointly observed with fabric/tech → crossed |
| | price sensitivity | 3 | **assumed** ¹ | gate-reclassified from *fused* |
| **Engagement (E)** | channel preference | 3 | **assumed** ¹ | gate-reclassified from *fused* |
| **Low-carbon tech (D)** | solar PV | 2 | **assumed** ¹ | gate-reclassified from *fused* |
| | EV | 2 | **assumed** ¹ | gate-reclassified from *fused* |
| | home battery | 2 | assumed | co-ownership tail unobservable |

¹ See §3 — the enforced fusion gate forces these to `assumed` because their residual is unmeasurable.

**"Has central heating" is dropped as a dimension** (near-constant at 98.5% of E&W households — it carries
almost no information). The informative variable is **fuel type**, which open 2021 data publishes jointly
only with **region** (see the open-data-degradation finding, §5.1).

**Two structural moves distinguish this from a naive full cross** (which would be ~3.1M cells):

- **The block is collapsed to its realistic joint.** tenure/accom/cars/class are sampled from
  `P(T)·P(A|T)·P(C|T)·P(S|T)` (tenure as the correlating spine — a stated conditional-independence
  simplification, logged). This prunes **39 of 240** block combinations as implausible (e.g. social-rented
  detached with 2+ cars and a higher-managerial HRP), leaving **201 realistic block cells**. *Collapsing
  saves N honestly* — we never spend a cohort on a household that essentially does not exist.
- **Fuel is pinned to region.** We use `P(fuel|region)`, so oil lands in Wales/SW/East (never London),
  electric and heat-networks concentrate in London. **7 of 70** fuel×region combinations are pruned as
  off-support (oil×London among them). This is the load-bearing stage-2 finding turned into design.

---

## 2. The collapsibility rule (gate on the tail, not the aggregate)

> **A dimension-pair may be CROSSED as independent (space multiplies cheaply) IFF it is weak in
> aggregate (Cramér's V < 0.10) AND its `tail_max_lift` < THRESHOLD. Otherwise it is COUPLED**
> (respect the joint / pin the tail).

Applied to the measured pairs (default threshold **1.5×**):

| Pair | V (aggregate) | tail lift | Decision @1.5× | Why |
|---|:--:|:--:|:--:|---|
| accommodation × tenure | 0.273 | 2.3× | **couple** | aggregate not weak |
| tenure × cars | 0.303 | 2.1× | **couple** | aggregate not weak |
| tenure × NS-SeC | 0.229 | 3.3× | **couple** | aggregate not weak |
| **heating fuel × region** | 0.070 | **3.8×** | **couple** | orthogonal in aggregate but tail 3.8× → **pin the off-gas tail** |
| tenure × region | 0.066 | 1.6× | **couple** | tail 1.6× ≥ 1.5× — *the only pair that flips in the sweep* |
| accom × central-heating(bin) | 0.063 | 2.8× | (moot — CH dropped) | |
| central-heating(bin) × tenure | 0.045 | 1.6× | (moot — CH dropped) | |

The director's fixed point holds mechanically: **fuel × region is never collapsible** in the whole
1.3–2.0 band, because its 3.8× tail sits far above the band. The off-gas tail is pinned to region at every
threshold — so the worst cells that depend on it (oil-rural, electric-London) are threshold-invariant.

The threshold (1.5×) is tagged **CHOSEN** — a director dial, not a derived constant. Sensitivity in §4.

---

## 3. The mechanised fusion bar (STEP 2 — now an enforced gate, not an exhortation)

Encoded in `population_fusion_assumptions_register.json` as `FUSION_BAR_RESIDUAL_v1`:

> **provenance may be `fused` IFF `residual_measurable == true` AND the within-cell residual association
> (after conditioning on the shared keys, in a source where keys AND target are jointly observed) is
> ≤ tolerance (0.10). IF the residual is UNMEASURABLE (the pair is never jointly observed), there is by
> definition no positive evidence → the gate FORCES `assumed` (cross).** Directly-observed pairs are
> `observed` and not subject to the gate.

This is the director's ruling ("fusion only with positive evidence for the conditional structure") turned
into the actual rule the design applies — per MAKE_IT_STICK, a rule lives as enforced code or it decays to
a judgement call. Each register entry now carries its **gate verdict**, its **residual test**, and its
**refutation observation**.

**The gate bit.** Four entries stage-2 had labelled `fused` on prior belief have unmeasurable residuals
(no open source ever observes them jointly with their keys), so the gate reclassified them to `assumed`:

| Entry | was | now | gate verdict |
|---|---|---|---|
| EV_ownership × income | fused | **assumed** | cross_forced (residual unmeasurable) |
| solar_PV × tenure | fused | **assumed** | cross_forced |
| price_sensitivity × income | fused | **assumed** | cross_forced |
| channel_preference × age | fused | **assumed** | cross_forced |
| green_stance × solar_PV | assumed | assumed | *promotable* if a consented source shows residual ≤ tol |
| EV × solar_PV × home_battery (the high-value triple) | assumed | assumed | *promotable* likewise |

Net effect: **there are currently zero permitted fusions** — every non-observed pair is crossed. That is
the asymmetric-error ruling working as designed (a confident false CI fusion mis-locates the tail and
everything downstream learns it as true; an honest cross is recoverable). The register keeps each as a
scheduled experiment: the `refutation_condition` states what a consented shadow-billing check or a
counterfactual twin would have to show to *promote* it to a real fused entry with explicit structure.
The tolerance (0.10) is tagged **CHOSEN** — a second director dial, sibling to the tail-lift threshold.

---

## 4. Nested worst-cell scores + the sensitivity result (STEP 3 & 4)

**Objective:** the worst cell — `min` over all targets of (coverage count ÷ required redundancy), never
the average. **Targets (1067 total):** 1-wise (every level of every factor appears) + pairwise t=2
(crossed pairs → all combos; coupled pairs → realistic combos only; fuel×region → pinned combos only) +
the **3 named worst cells** at redundancy 3. **Nesting:** one greedy-incremental sequence; N=100 ⊂ 200 ⊂
500 ⊂ 1000 by prefix, so each +N is a controlled experiment.

### The nested design at the default threshold 1.5×

| N | worst-cell coverage | Δ (marginal gain) | fraction covered ≥1 | meets required redundancy | named worst-cell hits (oil-rural / electric-London / solar-EV-batt) |
|---:|:--:|:--:|:--:|:--:|:--:|
| 100 | 0.00 | — | 0.886 | 0.883 | 1 / 1 / 1 |
| 200 | **1.00** | +1.00 | **1.000** | **1.000** | 4 / 4 / 4 |
| 500 | 4.00 | +3.00 | 1.000 | 1.000 | 13 / 13 / 13 |
| 1000 | 10.00 | +6.00 | 1.000 | 1.000 | 31 / 31 / 31 |

Reading it: **N=200 is the completeness knee** — worst-cell coverage reaches 1.0 (every target hit at
least its required count) and stays complete. The compounding-vs-linear split the director cares about is
visible: 100→200 buys *completeness* (the big fidelity jump, the cell now *exists*); 200→1000 buys
*redundancy / statistical mass* on the rare cells (+3.0 then +6.0 on the worst-cell count), a real but
different kind of value for a worst-cell learner.

### The sensitivity table — is the threshold material? (his explicit question)

Design rebuilt end-to-end at each threshold (`threshold_sensitivity.json`):

| threshold | `tenure×region` | worst-cell @100 | @200 | @500 | **@1000** | named cells @1000 | composition vs 1.5× |
|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|
| **1.3×** | coupled | 0.00 | 1.00 | 4.00 | **10.00** | 31 / 31 / 31 | — |
| **1.5×** | coupled | 0.00 | 1.00 | 4.00 | **10.00** | 31 / 31 / 31 | (base) |
| **1.75×** | crosses | 0.00 | 1.00 | 4.00 | **9.00** | 28 / 28 / 28 | ≤ 0.6 pp |
| **2.0×** | crosses | 0.00 | 1.00 | 4.00 | **9.00** | 28 / 28 / 28 | ≤ 0.6 pp |

**Verdict: NOT material for what gets built.** Through N=500 the design is *identical* at all four
thresholds — same completeness (N=200), same worst cells, same composition. The population composition at
N=1000 agrees to **≤ 0.6 percentage points** on every level of fuel/region/tenure. The *only* measurable
effect is a **~10% difference in redundancy depth at N=1000**: coupling `tenure × region` (the lower
thresholds) tells the design to spend marginally more attention respecting that pair's realistic joint,
which propagates to slightly deeper redundancy on the rare cells by the largest N (31× vs 28× on the named
cells; global worst-cell min 10 vs 9).

**Why so small (the mechanism, so the immateriality is shown not asserted):** for the threshold to move
the design, a *measured* pair would need `tail_max_lift` **inside** (1.3, 2.0) **AND** a realistic support
that differs materially from its full cross. Exactly one measured pair has a tail lift in that window —
`tenure × region` at 1.6× — and it is **near-orthogonal** (V = 0.066): every region contains every tenure
at a non-trivial share, so its realistic support ≈ its full cross, and coupling vs crossing it changes
only *how much greedy attention* it draws, not *which* cells are targets. Meanwhile the *decisive*
coupling — `fuel × region` at 3.8× — sits far above the entire band and never flips, so the tail pinning
that defines the worst cells is constant.

**What I'd flag to the director:** the threshold *would* become genuinely your dial the moment a future
association matrix contains a pair whose tail lift lands in 1.3–2.0 **and** whose realistic support is
materially sparser than its cross (a moderately-coupled pair with a mid-strength tail). The sensitivity
artifact rebuilds on every data refresh and will surface that automatically. Today's data does not contain
such a pair, so: **leave it at 1.5×; the band is immaterial; if you want maximum tail redundancy, prefer
the low end.**

---

## 5. First-class findings (kept, per the director)

### 5.1 Open data is getting *worse* — the 2021 census dropped the fuel×tenure cross-tab (STEP 5)

**The 2011 Census published `DC4402EW` — accommodation × central-heating × tenure with fuel detail.**
The 2021 open equivalent (`RM003`, Nomis `NM_2103_1`) **collapses heating to a binary has/has-not**, and
fuel type (`TS046`, `NM_2064_1`) is published jointly only with **geography** and occupancy/age — **never
with tenure or dwelling type**. So the fabric↔fuel joint a supplier most wants is **weaker in 2021 open
data than it was in 2011**: a genuine, citable regression. Consequence for the design: the fabric↔fuel
joint cannot be observed at household level in 2021 open data — it must be crossed (assumed) or fused via
region only. Recorded as a first-class finding in the register `_meta.open_data_degradation_finding` with
its citations, and in `POPULATION_COVERAGE_JOINT_STRUCTURE.md` §5.1.

### 5.2 The three first-class worst cells (instrumented, STEP 3)

Each is a must-hit target at redundancy 3; the greedy seeds from them (they are cohorts #1–3):

1. **oil-fuel-poor-rural** — oil fuel · Wales · social-rented · detached · never-worked/unemployed HRP.
   Anchored to real region×fuel structure (oil 7.83% Wales vs 0.12% London). *This is where the fuel
   poverty and the winter mortality live.*
2. **all-electric-flat-London** — electric-only · flat · London · private-rented. Anchored to real
   region×fuel structure (electric-only peaks in London at ~2× national).
3. **solar-EV-battery-owner** — PV + EV + battery co-ownership · owner-occupier · detached · higher class
   · green-engaged. Stays **assumed (crossed)** per the ruling — household co-ownership is unobservable in
   open data, and a confident false fusion here would systematically misrepresent the high-value tail.

By N=1000 each is populated ~31× (30/29/29–31/31/31 depending on threshold) — enough statistical mass for a
downstream model to *learn* the cell, not merely contain one household in it.

---

## 6. Push-back / what I'd surface

- **"N=200 is enough" is coverage-completeness, not fidelity-completeness.** N=200 guarantees every
  target *appears*; it does not guarantee the population's *marginals* match reality — the greedy spreads
  coverage roughly uniformly across levels (each fuel ≈ 14% of cohorts), which is deliberately **not**
  population-proportional (a worst-cell design over-weights rare cells on purpose). If the generator later
  needs population-representative marginals *as well as* worst-cell coverage, that is a second objective
  (importance weights / a re-weighting layer at draw time), not a bigger N. Flagging so the headline isn't
  over-read.
- **The block CI simplification (spine = tenure) is itself an assumption**, logged in the schema. It is
  the cheapest defensible block joint from pairwise-only open data (we never obtained the 4-way). A
  published 3-way (e.g. tenure×accom×cars) should replace it if one appears; until then it is a declared,
  refutable simplification, not a settled fact.
- **The immateriality of the threshold is a property of *this* association matrix, not a general law.**
  I would not let it harden into "the threshold never matters" — the sensitivity artifact must be rerun
  whenever the association matrix is refreshed. Built that way; noted here so it isn't forgotten.
- **NS-SeC banded 9→4 for tractability.** The banding preserves the tail cell that matters
  (unemployed/student), but a downstream model wanting the full 9-way class resolution should carry it;
  the design is band-agnostic (levels are a schema field, not hard-coded into the algorithm).

---

*Stage 3, autonomous worker in isolated worktree, 2026-07-20. Design + committed structure; **not pushed**.
Director/advisor read & steer stage 4 (the generator change — director-reserved).*
