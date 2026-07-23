# W2_13 — Occupancy → consumption volume & shape — DISCOVER

**Atom:** `W2_13_occupancy_consumption_volume_shape` (lane W2_customer_generator, epoch 3,
level 0→1, loop_stage=discover, `couples_with W1_5_premise_demand_shape`).
**Provenance:** director verdict `DIRECTOR_SEGMENTS_REVIEW_VERDICTS_2026-07-23.md` §3 item 2.
**This is DISCOVER only** — no simulation code changed, no maturity-map level moved. BUILD stays
EPOCH-gated (author now, build when a turn is granted).

## 0. Scope
Occupancy today drives COMPLAINT propensity and a coarse SHAPE tweak; it does **not** change how
much a household *uses* or split the response by people-count / adults-vs-children. This atom
deepens the existing occupancy input from a 3-category shape scalar into a people-count +
composition-driven **volume and shape** response, **folded into** the held HH load-shape lane
(`simulation/demand_model.py::build_demand_shape` / `occupancy_multiplier`, W1_5 premise demand) —
not a new engine.

---

## 1. Job 1 — where occupancy enters the demand path TODAY (code seam, quoted)

**The single attachment point** is `simulation/demand_model.py`. `build_demand_shape()` applies
occupancy at exactly one line (currently ~174–175):

```python
occupancy_pattern = property["occupancy_pattern"]
shape = [s * occupancy_multiplier(occupancy_pattern, p) for p, s in enumerate(shape, start=1)]
```

`occupancy_multiplier(occupancy_pattern, period)` (`simulation/demand_model.py:93`) is:

```python
if occupancy_pattern == "elderly":   # home most of the day — flatter, daytime near peak
    return 1.1 if (morning or evening) else 1.2
if occupancy_pattern == "family":    # out during the day, sharp evening peak
    if evening: return 1.4
    if morning: return 1.1
    return 0.85
# "single" (default): out most of the day, moderate evening peak
if evening: return 1.25
if morning: return 1.0
return 0.75
```

`occupancy_pattern` is a **categorical string** (`"single"|"family"|"elderly"`) set upstream in
`saas/property_model.py` (`build_properties()`, from `OCCUPANCY_PATTERN_BY_CUSTOMER`, flagged
there as a seed estimate "no real data yet").

**What the current mechanism does and does NOT do:**
- It is a **per-period SHAPE multiplier only**. Values hover around 1.0 (0.75–1.4), so it
  *redistributes* load across the day; it does **not** scale a household's **total volume** by
  headcount — a "family" and a "single" home with the same base profile end the day at roughly the
  same daily total, just differently shaped.
- It is keyed on a **3-way category**, not a **people-count**; there is no adults-vs-children
  distinction and no sublinear per-person volume gradient anywhere in the demand path.

**Fold-not-fork attachment (the seam named):** deepen this *one* call site. Two disjoint additions,
both attaching where `occupancy_multiplier` is applied, reusing the existing property record:
1. **VOLUME** — a per-household scalar `occupancy_volume_factor(people_count, composition)` applied
   to the base level (a new multiply alongside the existing shape multiply), following the NEED
   per-adult **sublinear** curve (§2). This is the piece missing today.
2. **SHAPE** — deepen `occupancy_multiplier` so its **daytime (09:00–17:00) window only** responds
   to composition (people-count / pensioner-presence / employment) per EFUS (§3); evening and
   overnight windows stay as-is (near-universal occupancy, no composition signal). The existing
   3-category returns become the coarse fallback when a people-count is unavailable.

No new engine, no new file: the input record gains `people_count` (+ composition where anchorable)
and the one function pair is deepened.

**couples_with W1_5_premise_demand_shape:** the volume factor is a **deterministic per-household
occupancy response** and is *distinct from* W1_5's mean-1 idiosyncratic per-premise noise
(`simulation/premise_demand.py`). They multiply independently — occupancy explains a real
population-structured share of the variance W1_5 currently absorbs as noise; the coupled-triad gap
(company belief vs SIM truth) is measured against W1_5, not re-derived here.

---

## 2. Job 2(a) — VOLUME gradient (ANCHORED, DESNZ NEED 2023, confidence H)

Median kWh/yr **by number of adults**, England & Wales, DESNZ NEED
`Consumption_additional_EW_2023.xlsx` Table A14 (elec) / A13 (gas), parsed direct from the
published `.xlsx` (2026-07-23; full citation in `docs/market_research/occupancy_consumption_volume_shape_w2_13.md` §2):

| adults | elec (kWh/yr) | Δ vs prior | gas (kWh/yr) | Δ vs prior |
|---|---|---|---|---|
| 1 | 1,993 | — | 8,546 | — |
| 2 | 2,867 | **+43.8%** | 10,624 | +24.3% |
| 3 | 3,318 | +15.7% | 11,576 | +9.0% |
| 4 | 3,772 | +13.6% | 12,734 | +10.0% |
| 5+ | 4,129 | +9.5% | 14,486 | +13.8% |

**Shape of the response is the anchor, not one number:** electricity jumps hardest on 1→2 adults
(+43.8%, a large shared fixed base — lighting/fridge/standby/cooking — that a 2nd adult adds little
marginal draw to) then flattens (+15.7/+13.6/+9.5%). Gas is smaller on 1→2 (+24.3%) and steadier
(space heating tracks dwelling size, already modelled elsewhere; hot-water/cooking gas tracks
people). The same monotonic-sublinear shape holds every year back to 2005 — not a one-year
artefact. **A build follows this per-adult decay curve, not a flat linear per-person scalar.**

---

## 3. Job 2(b) — SHAPE driver: daytime-window occupancy by composition (ANCHORED, EFUS 2017, H)

DESNZ/BRE Energy Follow-Up Survey (EFUS) 2017 heating-patterns-&-occupancy report (n≈1,167–1,179 GB
households; `docs/market_research/…w2_13.md` §4):
- Weekday **daytime (09:00–17:00) "someone home all day"** swings **~30pp by composition**: single
  37% vs 5+-person 67%; no-pensioner 34% vs pensioner-present 63%; someone-employed 35% vs
  all-unemployed 60%.
- **Evening (88%) and overnight (94%)** are near-universally occupied **regardless of composition**
  — consistent with the existing Elexon PC1 evening-peak / overnight-baseload shape in
  `sim/profile_class_1.py`.

→ **Concentrate the composition-driven shape adjustment on the 09:00–17:00 window only.** The
occupancy-**rate** inputs are H-confidence; converting an occupancy rate into an exact kWh
half-hourly weight is a build-time modelling choice → **R10-DISTRIBUTION-CANDIDATE** for that
conversion magnitude.

---

## 4. What stays R10 (sample from a distribution, never a point estimate)

1. **Adults vs children decomposition** — NEED's variable is **adults-only**; no located NEED table
   splits adults vs children jointly. EFUS water-use corroborates a *children-present dampening on
   per-person intensity* (71% vs 38% of households under 1 wash/person/day with vs without
   children). So do **not** assume a child contributes the same marginal volume as an adult — a
   distinct child increment is unanchored; sample it and state the gap in the build docstring.
2. **The occupancy-rate → kWh-shape-weight conversion** (§3).
3. **Cooking fuel split & overnight device/standby load by composition** — genuinely not found this
   session; named unfetched follow-up lead: `efus-light-appliances-smart-tech.pdf` (fetch before
   treating as permanently unanchorable).

---

## 5. DISCOVER-COMPLETE

- **Seam named:** `simulation/demand_model.py::build_demand_shape` at the `occupancy_multiplier`
  call site (line ~174–175) + the `occupancy_multiplier` function (line 93). Fold, do not fork —
  the property record gains `people_count` (+ composition where anchorable); the one function pair
  is deepened; no new engine.
- **What an L1 build adds (2–3 concrete things):**
  1. A **volume factor** on total level, following the NEED per-adult sublinear curve (§2) — the
     genuinely missing piece today.
  2. A **daytime-window (09:00–17:00) composition shape response** deepening `occupancy_multiplier`
     (§3); evening/overnight unchanged. Category returns become the no-people-count fallback.
  3. Both keyed on a **people-count** derived input, replacing the hand-set 3-way category as the
     primary key (category retained as fallback).
- **Stays R10:** child-vs-adult marginal increment; the rate→shape-weight conversion; cooking
  fuel / overnight device load. A build samples these from distributions and states the gap.
- **couples_with W1_5** — volume factor is deterministic and distinct from W1_5's idiosyncratic
  noise; the belief-vs-truth gap is measured against W1_5.
- **Level:** L1 **PROPOSED** (this log). `level_current` held at 0 — the cell move is the
  director's per the level-promotion gate (R16). BUILD stays EPOCH-gated.

**Sources (full citations):** `docs/market_research/occupancy_consumption_volume_shape_w2_13.md`
(Job 2, DESNZ NEED 2023 + EFUS 2017, fetched/parsed 2026-07-23) and its appended
`docs/market_research/ASSUMPTIONS.md` section. Job 1 code seam quoted from
`simulation/demand_model.py` at this DISCOVER's HEAD.

— W2_13 DISCOVER, 2026-07-23. Job 1 (code seam) by the orchestrator; Job 2 (real-world anchoring)
by discovery-agent, disjoint-scope fork.
