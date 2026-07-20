# Population Coverage — Stage 2: Fetched Joint Structure

**Track:** DIRECTOR_STEER_POPULATION_COVERAGE_DESIGN_2026-07-20 (learning loop, DISCOVER)
**Stage:** 2 of the loop — *fetch the ungated open sources; commit structure not microdata.*
**Authority:** `docs/staging/done/DIRECTOR_STEER_COVERAGE_STAGE2_FUSION_CALL_2026-07-20.md`
**Status:** doc-and-data only. No generator change. No personal microdata. Raw responses cached
outside the repo (`~/.cache/se_coverage/`), aggregates only committed.

> This stage answers Requirement 2 with **real fetched numbers**: per-dimension marginals, the
> pairwise cross-tabs we could observe jointly, an association matrix (Cramér's V), and the
> load-bearing plain-language note on what is genuinely orthogonal vs coupled. Committed structure:
> `population_coverage/marginals.json`, `.../crosstabs.json`, `.../association_matrix.json`, and the
> extended `population_fusion_assumptions_register.json`.

---

## 0. What was actually fetched (honest inventory)

| Source | What | Access | Got it? | Contributes |
|---|---|---|:--:|---|
| **Census 2021 RM003** (Nomis NM_2103_1) | Accommodation × central-heating(has/not) × tenure — a real **3-way** joint | open | ✅ | accom×tenure, accom×CH, CH×tenure |
| **Census 2021 RM138** (NM_2238_1) | Tenure × NS-SeC (class) | open | ✅ | tenure×class |
| **Census 2021 RM131** (NM_2231_1) | Tenure × car/van availability | open | ✅ | tenure×cars |
| **Census 2021 TS046** (NM_2064_1) | Heating **fuel type** (13-cat) × region | open | ✅ | fuel×region |
| **Census 2021 TS054** (NM_2072_1) | Tenure × region | open | ✅ | tenure×region |
| **DfT VEH0135** | Licensed plug-in vehicles by LSOA, quarterly to 2026 Q1 | open | ✅ | EV marginal only |
| MCS install dashboard | PV / heat-pump / battery install counts | open | ⚠️ deferred | marginal only — see §5 |
| DESNZ smart-meter stats | penetration by region/fuel | open | ⚠️ deferred | marginal only |
| DESNZ fuel-poverty (LILEE) | fuel-poverty × tenure/dwelling | aggregate-open | ⚠️ deferred | a real cross-tab — see §5 |
| PAT / Ofgem consumer | attitudes × coarse demographics | aggregate-open | ⚠️ deferred | E×coarse-C, marginal for our purposes |
| EHS / Understanding Society microdata | the two rich A×B×C / C×E×D spines | **apply-gated** | ⛔ boundary | **not fetched by rule** |

The ⚠️ items are **open and locatable** (URLs/collections identified) but are **marginal-only for the
joint-structure question** — by the stage-1 finding they cannot add an *observed cross-group joint*, so
they were not parsed this pass. They matter for **generator anchoring** (real marginal shares), not for
the orthogonality decision that gates stage 3. Recorded as an honest deferral, not a data gap. The
⛔ items are the two richest joint sources and are deliberately **not obtained** — the pitch's public
"no household data entered the system" claim depends on that, and it holds.

---

## 1. The association matrix (real numbers)

Cramér's V, whole England-&-Wales population (n ≈ 24.78M households). Bands:
`orthogonal <0.10 · weak 0.10–0.20 · moderate 0.20–0.35 · strong >0.35`.

| Pair | Cramér's V | Aggregate band | Tail max lift | Provenance |
|---|:--:|:--:|:--:|:--:|
| tenure × cars/van | **0.303** | moderate | 2.1× | observed |
| accommodation × tenure | **0.273** | moderate | 2.3× | observed |
| tenure × NS-SeC (class) | **0.229** | moderate | 3.3× | observed |
| heating **fuel** × region | **0.070** | orthogonal | 3.8× | observed |
| tenure × region | **0.066** | orthogonal | 1.6× | observed |
| accommodation × central-heating(has/not) | **0.063** | orthogonal | 2.8× | observed |
| central-heating(has/not) × tenure | **0.045** | orthogonal | 1.6× | observed |

**The single most important result:** every pair came in **weaker than the stage-1 priors assumed**.
The priors called tenure↔fabric and fuel↔region "strong"; measured, they are **moderate (0.27)** and
**orthogonal-in-aggregate (0.07)**. The design must not have inherited the "strong" priors — it would
have over-collapsed the space and *under*-sampled the tails.

---

## 2. THE load-bearing finding — aggregate V is the wrong lens for a worst-cell design

Heating-fuel × region scores V = 0.070 ("orthogonal"). But look at the tail:

| Fuel (national share) | most-concentrated region | least |
|---|---|---|
| **Oil only** (3.5%) | Wales **7.83%** (2.2× nat) | London **0.12%** (0.03× nat) |
| Electric only (8.5%) | London 12.6% (1.5×) | North East 5.1% (0.6×) |
| Tank/bottled gas (1.0%) | Wales 2.05% (2.0×) | London 0.61% (0.6×) |

Oil-only ranges **~65× across regions** while the pair reads "orthogonal." Why? The table is dominated
by the 73.8% mains-gas mass; Cramér's V is a mass-weighted average, so a strong association confined to a
small tail is diluted to near-zero. **The coverage design's objective is the worst *cell* — the off-gas,
all-electric, fuel-poor tail is exactly where the money and the mortality live — so the aggregate V is
the wrong statistic to decide what to cross vs collapse.** Both layers are committed in
`association_matrix.json` (`aggregate_band` **and** `tail_max_lift`); stage 3 must gate on the tail
structure, not the headline V.

Corollary: the same is true of the **moderate** pairs. tenure×NS-SeC reads 0.229 but its sharpest cell is
full-time-students × private-rented at **3.3× lift** — the coupling is real and concentrated, not smeared.

---

## 3. Orthogonal vs coupled — the crossing decision, per pair

**Effectively orthogonal in aggregate AND tail (cross them — they multiply the space, cheaply):**
- **central-heating (has/not) × everything** — V ≤ 0.06 and the variable is a **near-constant**: 96%+ of
  E&W households have central heating. *Finding:* "has central heating" is **not a real design dimension**
  — it carries almost no information. The informative variable is **fuel type**, which is only openly
  observed jointly with **region** (TS046), never with tenure/fabric at national level (a coverage gap —
  the 2021 open cross-tabs dropped the fuel-type×tenure table the 2011 census had).
- **tenure × region** (V 0.066, tail 1.6×) — tenure mix is fairly stable across regions (London's higher
  private-rent share is the main deviation). Safe to cross.

**Coupled — must be respected, NOT crossed as independent:**
- **tenure × cars/van** (0.303) and **accommodation × tenure** (0.273) — the strongest real couplings.
  Owner-occupiers skew to houses and to ≥1 car; social-rented skews to flats and no-car. Collapsing these
  saves N honestly.
- **tenure × NS-SeC** (0.229) — moderate, tail-sharp. Class and tenure move together.
- **heating-fuel × region — coupled IN THE TAIL only.** Cross the *bulk* (mains-gas is ~everywhere) but
  the design must *pin the off-gas tail to region* (oil→Wales/SW/East, electric→London), or it will
  scatter oil boilers into London where they essentially do not exist.

**Not observable — deferred to the register as fusion/assumption (unchanged from stage 1, now with
measured shared-key strength):**
- **anything × attitudes (E)** and **anything-household × low-carbon-tech (D)** — no open joint exists.
  EV is observable **per-area** (LSOA) but never per-household-with-attributes. These stay `fused`
  (only where shared-key evidence exists) or `assumed` (crossed), per the register.

---

## 4. Coverage-matrix update — which cells moved gap → observed

Relative to stage-1 §2 (which rated whole *sources*), these **dimension-pairs** are now **observed with
real numbers** (previously only asserted from priors):

| Pair | Stage 1 | Stage 2 |
|---|---|---|
| accommodation × tenure | prior "strong" | **observed, V=0.273** |
| tenure × NS-SeC | prior (income proxy) | **observed, V=0.229** |
| tenure × cars | — | **observed, V=0.303** |
| heating-fuel × region | prior "strong" | **observed, V=0.070 + tail map** |
| tenure × region | — | **observed, V=0.066** |
| accom × central-heating, CH × tenure | — | **observed (CH ≈ constant)** |

Still **gap** (confirmed, not closed — honest): fuel-type × tenure/fabric (dropped from 2021 open
tables); all D×household; all E×(A/B/D). Income itself stays FRS-gated — **NS-SeC is the open proxy**
committed here.

---

## 5. Sources I could NOT get openly (findings, not failures)

1. **Fuel-type × tenure/fabric at national level** — the 2021 open cross-tabs give heating *fuel* jointly
   only with **geography** (TS046) and with occupancy/age (RM141), **not** with tenure or dwelling type.
   The 2011 census had DC4402 (accom×central-heating×tenure with fuel detail); the 2021 open equivalent
   (RM003) collapses heating to **binary has/has-not**. So the fabric↔fuel joint that a supplier most
   wants is **weaker in 2021 open data than in 2011** — a genuine, citable coverage regression.
2. **EHS / Understanding Society aggregate cross-tabs** — the report *pages* do contain published
   A×B×C and C×E cross-tabs (allowed), but they are embedded in PDF report annexes rather than a
   machine table endpoint; extracting them reliably is a scraping/parse job deferred to stage 3, where
   they become the fusion bridge for the C↔E link. Flagged, not done.
3. **MCS / smart-meter / fuel-poverty ODS tables** — open but ODS-embedded; marginal-only for our
   question, deferred to the generator-anchoring pass. Fuel-poverty × tenure is a real cross-tab worth
   pulling *then* (affordability spine), not needed for the crossing decision now.

None of these change the §3 crossing decision. They change stage-3 *anchoring* precision.

---

## 6. Recommendation for stage 3 (the nested worst-cell design)

1. **Gate crossing decisions on TAIL lift, not aggregate V.** Concretely: a pair is "collapsible" only if
   it is weak in aggregate **and** its max tail lift < ~1.5×. By that rule, fuel×region is **NOT**
   collapsible despite V=0.07 — the off-gas tail must be pinned to region.
2. **Drop "has central heating" as a dimension** (near-constant); replace with **fuel type**, carried on
   the **region** key (its only open joint).
3. **Use NS-SeC as the open class/income axis**; keep true income as a stage-3 fusion onto NS-SeC×tenure
   with the CI assumption declared in the register.
4. **Nesting N=100→200→500→1000:** the required N is driven by the pairs that must be **crossed**
   (CH-as-constant now removed helps; the real cost is the D and E dimensions that are all `assumed`).
   Seed the worst-cell greedy build from the **coupled** structure (tenure↔accom↔cars↔class as one
   correlated block) and cross the `assumed` D/E dimensions against it — that is where N is spent, and it
   is spent honestly (we know we don't know).
5. **Instrument the tails as first-class worst cells:** oil-fuel-poor-rural, all-electric-flat-London,
   solar-EV-battory owner-occupier. The first two are now anchored to real region×fuel structure; the
   third stays `assumed` (crossed) per the ruling until a consented source exists.

---

## 7. Push-back on the ruling (as invited)

Two small ones, both endorsing the direction:

- **"Fusion only with positive evidence for the conditional structure" needs a measurable bar, or it
  will decay to a judgement call.** I propose the operational test: a fusion is permitted only if the
  shared keys explain the pair's association to within a stated tolerance in a source where *both* the
  keys and the target are seen (e.g. within Census, does tenure+region account for the tenure×fuel
  association, or is there residual?). Where we cannot even measure the residual (the D/E gaps), the
  answer is automatically "no evidence → cross," which is what the ruling wants — but now it's a
  mechanism, not an exhortation (per MAKE_IT_STICK). Recorded as a refutation-style bar in the register.
- **The aggregate-V-understates-tails finding slightly reframes the director's "where there is no
  correlation you can cover without spiralling size" premise.** There is *low aggregate* correlation in
  several pairs, but not *low tail* correlation — so "cover the orthogonal pairs freely" must read
  "cover the pairs that are orthogonal *in the tail that matters*," which is a stricter and smaller set
  than the aggregate matrix suggests. Net effect on N: slightly larger than a naive aggregate reading,
  but honestly so. Flagging because it moves the sizing.

---

*Stage 2, autonomous worker in isolated worktree, 2026-07-20. Committed structure + this note; not
pushed. Advisor/director read & steer stage 3.*
