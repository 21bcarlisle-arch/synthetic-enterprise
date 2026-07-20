# Population Coverage — Stage 1: Source Landscape

**Track:** DIRECTOR_STEER_POPULATION_COVERAGE_DESIGN_2026-07-20 (learning loop, DISCOVER)
**Stage:** 1 of the loop — *"which real datasets carry which dimensions"* (Requirement 1).
**Status:** doc-and-data only. No change to the live population generator. No microdata committed.
**What the director/advisor should do with this:** read it, and steer stage 2 (which sources to
actually fetch, and how hard to push on the fusion problem in §5, which is the crux).

> This stage is deliberately upstream of any fetching. It answers: *for each dimension the director
> named, what is the best open UK source, what does it actually contain, can I download it, and —
> the load-bearing question — does any single source let me observe the JOINT structure between
> dimensions, or must it be fused?* Honest "no good open source" answers are findings, not gaps to paper over.

---

## 0. The dimensions (director-named), grouped by how they cluster in the data

| Group | Dimensions |
|---|---|
| **A. Physical fabric** | house type, built form, floor area, construction age, wall/insulation, energy rating |
| **B. Systems / fuel** | heating system, main fuel, mains-gas connection, smart-meter fitted |
| **C. Tenure & socio-demographic** | tenure, income, household composition, age, socio-economic class, region, fuel-poverty |
| **D. Low-carbon tech** | EV ownership, solar PV, home battery, heat pump |
| **E. Attitudes** | price sensitivity, channel preference, green/environmental stance, smart-meter attitude, trust/satisfaction with suppliers |

The grouping is not cosmetic — it maps almost exactly onto **which source can see which dimensions
jointly**. A single source tends to see one or two groups well and the rest not at all. That is the
whole problem, and it is what §5 is about.

---

## 1. Source catalogue

Access legend: **[open]** direct bulk/API download · **[account]** free login/registration for bulk ·
**[apply]** application-gated microdata (UKDS Special/Safeguarded licence, ONS SRS, etc.) ·
**[aggregate-open]** reports/tables open, unit-record only via [apply].

### A/B — Physical fabric & systems

- **EPC Register — England & Wales** `[account]` — DLUHC/DESNZ.
  ~29.2M domestic certs (2008–2026), ~60% of stock, **transaction-biased** (rented & recently-sold
  over-represented, old unsold stock under-represented). Property type, built form, floor area,
  construction age band, walls description, current rating (A–G / SAP), main fuel, mains-gas flag,
  mainheat description, postcode. *Already researched:* `epc_open_data.md`.
  **Joint reach:** the single richest source for A×B×region *at the dwelling*. No household
  socio-demographics, no tenure (only inferable), no attitudes, no tech beyond heating fuel.
- **Scottish EPC Register** `[account]` — separate portal, same shape, Scotland only.
- **NEED — National Energy Efficiency Data-Framework** `[apply]` (anonymised sample `[open]`) — DESNZ.
  Links measured gas+electricity consumption to EPC fabric + property age + floor area + limited
  household attributes. **Joint reach:** consumption × A × (coarse C). The bridge between fabric and
  actual kWh; the anonymised end-user sample is downloadable, the full linked set is application-gated.
- **English Housing Survey (EHS)** `[apply]` (annual reports `[aggregate-open]`) — DLUHC/DESNZ.
  ~13k dwellings/yr with a *physical surveyor inspection* **and** a household interview. Dwelling type,
  age, fabric, SAP, heating system **jointly with** tenure, income, household composition, and an
  attitudes module. **Joint reach: the best single open-ish source spanning A×B×C together**, and the
  natural spine for fusion. Microdata is [apply] (UKDS Safeguarded/EUL); aggregates are open.

### C — Tenure & socio-demographic

- **Census 2021** `[open]` — ONS (E&W) / NRS (Scotland) / NISRA (NI), via Nomis + Flexible Tables.
  Tenure, dwelling type, central-heating type, occupancy/overcrowding, car-or-van availability, NS-SEC,
  age, household composition, at LSOA and up. **Multivariate cross-tabs are the key asset** — genuine
  joint C×(coarse B) structure, open, small-area. Unit-record only via the Census microdata teaching /
  safeguarded samples `[apply]`. Heating-type field gives a real cross-tab against tenure & dwelling type.
- **Family Resources Survey / HBAI** `[apply]` (`[aggregate-open]`) — DWP. Income, benefits, material
  deprivation, disability — the affordability spine. Coarse dwelling info only.
- **Fuel-poverty statistics (LILEE, sub-national)** `[aggregate-open]` — DESNZ. Fuel poverty by dwelling
  type, tenure, region, efficiency band. Aggregate; underlying is EHS-derived.
- **Understanding Society (UKHLS)** `[apply]` — longitudinal panel, ~40k households. Rich C **plus** an
  energy module, some tech, and some attitudes, tracked over time. **Joint reach: C×E×(some D) in one
  place** — the strongest candidate for the attitudes fusion, but strictly application-gated.

### D — Low-carbon tech

- **MCS Data Dashboard** `[open]` — solar PV, heat pump, battery-storage install counts by month and
  region/postcode-area. Counts, not households; no socio-demographic join.
- **DfT/DVLA EV statistics (VEH0 series)** `[open]` — licensed plug-in vehicles by LSOA/LA/region.
  Geography + marginals; no household join.
- **BEIS/DESNZ Solar PV & FIT deployment stats** `[open]` — installed capacity/counts by band & region.
- **Smart-meter statistics (DESNZ, quarterly)** `[open]` — smart-meter penetration by region, fuel,
  domestic/non-domestic. Marginal only.
- **Honest gap:** there is **no good open source giving household-level joint of D with C or A/B**.
  EV × PV × battery co-ownership at the household is essentially unobservable openly — it lives in
  commercial panels or must be *modelled* from regional marginals + plausible conditional structure.
  This is a first-class finding and directly stresses the director's correlation question: some of the
  most valuable cells (solar-EV-battery household) sit exactly where the open joint data is thinnest.

### E — Attitudes

- **DESNZ Public Attitudes Tracker (PAT)** `[aggregate-open]` (microdata `[apply]`) — quarterly.
  Climate concern, energy-saving behaviour, smart-meter attitudes, heat-pump awareness/willingness,
  crossed with coarse demographics (age, region, tenure, working status). **Joint reach: E × coarse C.**
- **Ofgem Consumer Survey / Consumer Perceptions of the Energy Market** `[aggregate-open]` — trust,
  satisfaction, switching behaviour, ability to pay, vulnerability. *Related repo research:*
  `willingness_classification_incidence.md`, `churn_price_elasticity.md`.
- **Smart Energy GB research** `[aggregate-open]` — smart-meter attitudes/segments.
- **Understanding Society** — see C; the one place E is jointly observed with real behaviour + rich C.
- **Honest gap:** attitudes are **never openly observed jointly with dwelling fabric (A/B) or tech (D)**.
  They are keyed to coarse demographics only. Price sensitivity and channel preference in particular
  have *no* clean open UK microdata source — they must be **inferred** (elasticity proxies already in
  `churn_price_elasticity.md`) or fused on demographic keys, with the conditional-independence
  assumption stated explicitly.

---

## 2. Coverage matrix — which source sees which group jointly

`●` sees it richly & jointly · `◐` partial / coarse · `○` marginal-only or absent

| Source | A fabric | B systems | C socio-dem | D tech | E attitudes | Access |
|---|:--:|:--:|:--:|:--:|:--:|---|
| EPC register | ● | ● | ○ | ○ | ○ | account |
| NEED | ● | ● | ◐ | ○ | ○ | apply/open-sample |
| **EHS** | ● | ● | ● | ◐ | ◐ | apply / aggregate-open |
| Census 2021 | ◐ | ◐ | ● | ○ | ○ | open |
| **Understanding Society** | ○ | ◐ | ● | ◐ | ● | apply |
| FRS/HBAI | ○ | ○ | ● | ○ | ○ | apply |
| MCS / EV / PV / smart stats | ○ | ◐ | ○ | ●(marginal) | ○ | open |
| PAT / Ofgem consumer | ○ | ○ | ◐ | ○ | ● | aggregate-open |

**The load-bearing reading:** no row is `●` across the board. EHS and Understanding Society are the two
spines (one dwelling-anchored, one household-panel-anchored); everything else is either fabric-only
(EPC), geography-marginal (Census, MCS/EV), or attitude-only (PAT/Ofgem). **So the joint structure the
design needs cannot be read from one table — it must be assembled.** That assembly is §5.

---

## 3. What is openly downloadable *right now* vs gated

- **Fetch without gates (stage 2 candidates):** Census 2021 cross-tabs (Nomis/Flexible Tables),
  MCS dashboard, DfT EV stats, solar/FIT stats, smart-meter stats, PAT & Ofgem aggregate tables,
  DESNZ fuel-poverty tables, NEED anonymised sample.
- **Free but account-gated:** EPC bulk (GOV.UK One Login) — already known to work (`epc_open_data.md`).
- **Application-gated (NOT stage 2; flag & stop per steer boundary):** EHS/Understanding Society/FRS/
  Census microdata unit records. These require a UKDS licence application and carry human-subject
  terms — **do not attempt to obtain or hold personal microdata.** Use their *published aggregates and
  cross-tabs* only; that is enough to estimate the marginals and pairwise associations we need.

This matters for honesty: the two richest *joint* sources (EHS, Understanding Society) are precisely the
gated ones. The design must therefore lean on **published cross-tabs from the gated sources + open
micro/aggregate from the ungated ones**, not on holding raw personal records.

---

## 4. What "commit structure not microdata" means concretely (sets up stage 3)

Per Requirement 3, stage 3 will commit, in readable form:
- **Marginals** per dimension (distribution of each on its own).
- **Pairwise cross-tabs** for every pair we can observe jointly (from EHS/Census/PAT published tables).
- **Association matrix** with the *right* measure per pair type: Cramér's V for categorical×categorical,
  correlation ratio (η) for categorical×continuous, Pearson/Spearman for continuous×continuous — a
  single "correlation matrix" would be wrong across mixed types and would mislead the design.
- **A plain-language orthogonality note:** which pairs are effectively independent (must be crossed —
  they multiply the space) vs strongly coupled (collapse the space). *Prior expectations to test, not
  assert:* tenure↔fabric strong; heating-fuel↔region strong; EV↔income moderate; PV↔tenure (owner)
  strong; green-stance↔age/income moderate; price-sensitivity↔income strong; channel-preference↔age
  moderate. The design's required N is driven by the **independent** pairs, so this note is what sizes it.

---

## 5. The crux — the fusion / joint-structure problem (for director & advisor to steer)

The director's framing ("*where there is no correlation you can cover without spiralling size*") requires
the joint structure **before** the design. But §2 shows no single open source carries the full joint.
So the honest methodological situation is:

1. **Within-group joints are directly observable.** A×B×region from EPC; C×B from Census; C×E-coarse
   from PAT; C×A×B from EHS aggregates. These give real, defensible pairwise structure.
2. **Cross-group joints spanning A/B ↔ E, and anything ↔ D-at-household, are NOT openly observable.**
   They can only be reached by **statistical fusion**: match records/marginals across sources on shared
   keys (region, tenure, dwelling type, income band, age). Fusion's price is a **conditional-independence
   assumption** — it assumes the two unlinked dimensions are independent *given the shared keys*. That
   assumption is exactly a correlation claim, and it is often the wrong one (e.g. green-stance and PV
   ownership are surely correlated beyond what income+tenure explain).
3. **Therefore the design must declare, per cross-group pair, one of:** (a) observed jointly → use it;
   (b) fused under stated conditional-independence → use it *and flag the assumption as a fidelity risk*;
   (c) no basis → treat as independent-by-necessity and let the coverage design cross it (safe, costs N).

**This is the decision I want the director/advisor's steer on for stage 2:** how aggressively to pursue
fusion for the high-value tails (the solar-EV-battery household, the prepayment fuel-poor all-electric
flat) where the open joint data is thinnest and the money/mortality lives — vs conservatively crossing
those dimensions and paying the N cost. Both are defensible; it is a values/curriculum-adjacent call
about where to spend fidelity budget, so it is yours, not mine to settle.

---

## 6. Method note (candidates from the steer & advisor ideas, evaluated not adopted)

The steer's math candidates map cleanly onto §4's orthogonality split, and I agree with the direction:
- **Covering arrays / pairwise (t-wise) coverage** — right primitive for the categorical dimensions
  (A/B/C/E-as-bands): guarantees every *pair* of levels appears, N grows ~logarithmically in factor
  count. This is the natural fit for "cover the space without spiralling size."
- **Space-filling (Latin hypercube / maximin)** — right for the genuinely continuous dimensions (floor
  area, income, consumption), layered on top of the categorical covering array.
- **Orthogonal-array / fractional-factorial (advisor §D2)** — applicable where main-effects additivity
  holds; useful for the *curriculum-dial* crossing, less so for the population itself where interactions
  (the tails) are the point.
- **Worst-cell scoring (advisor §C5, steer Req 4b)** — adopted as the coverage objective: score the
  least-covered *cell that matters*, not the average. Consistent with the fidelity grid.
- **NESTED sizing (steer Req 4a)** — each of N=100→200→500→1000 contains the previous, so each increment
  is a controlled experiment and its marginal fidelity gain (Req 5) is measurable. This constrains the
  covering-array construction to a *greedy incremental* build (add the cells that most raise the worst-cell
  score), not an independently-optimal design per size.

None of this is built here — it is the stage-4 design, gated on the stage-3 joint structure, gated on
this stage's fetch plan. Stated now only so the director/advisor can redirect the method early.

---

## 7. Next actions (proposed — awaiting steer)

1. **Stage 2 (fetch, network-capable session):** pull the ungated open sources in §3 bullet 1, cache raw
   on the box outside the repo, and pull published cross-tabs from the gated sources' report pages. No
   personal microdata.
2. **Stage 3 (structure):** compute & commit marginals + pairwise cross-tabs + mixed-type association
   matrix + the plain-language orthogonality note (§4), in readable form.
3. **Stage 4 (design):** nested worst-cell covering-array populations at N=100/200/500/1000 + marginal-gain
   report (§6).

Each stage reports back in prose + committed structure before the next, per the loop. Brief expected to
change between stages — that is intended.

— Stage 1, autonomous worker, 2026-07-20. Owned by the build lane; advisor/director read & steer.
