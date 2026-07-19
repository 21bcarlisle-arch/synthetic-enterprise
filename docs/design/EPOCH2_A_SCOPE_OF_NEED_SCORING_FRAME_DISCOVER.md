# EPOCH-2 ATOM A — the SCOPE-OF-NEED SCORING FRAME (DISCOVER, doc-only)

**Status:** DISCOVER/FRAME, doc-only. `provenance: proposal`; **no level claimed.** Writes only
under `docs/design/`; edits neither `maturity_map.yaml`, `supervisor.py`, `coupled_triad.py`,
`CLAUDE.md` nor any engine — those are the orchestrator's/BUILD's landing acts. This is
requirement 1 of the Epoch-2 coupled-world campaign
(`docs/staging/DIRECTOR_CAMPAIGN_EPOCH2_COUPLED_WORLD_2026-07-19.md`), **defined FIRST because it
defines what "good" means for every atom built after it.** W1 BUILD stays CLOSED.

**What this doc is.** The director's requirement, verbatim intent: *define the grid you will be
scored against — customer archetypes × market regimes, chosen to span the RANGE OF NEED, not
frequency; the cases that STRESS DIFFERENT PHYSICS; and the fidelity score is the
WORST-EXPLAINED CELL of that grid, not the population average.* This doc delivers that grid, the
worst-cell scoring rule tied to the existing belief-vs-truth gap metric, and the frame's wall /
portability / simplifications. It is a **scoring instrument**, not a population model — §1.4 draws
the load-bearing line between "in the frame for scoring" and "population weight."

**Confidence tagging.** Where a boundary, weight, or penetration is asserted rather than derived
from data it is flagged inline and registered as a simplification in §5 (R10). External anchors
are tagged *"recall — verify at BUILD"* (no network in this fork; Historical Ground Truth forbids
fabricating a specific figure in a DISCOVER doc).

---

## 0. The one-paragraph idea

A fidelity harness that scores itself on the **population average** rewards nailing the
comfortable middle — which is also the most numerous, so it dominates the average — and lets the
model explain **nothing** at the edges while still reporting a good number. That is precisely the
failure the director names: *"a model that nails the comfortable middle and explains nothing at
the edges has failed, however good its average fit."* The fix is structural, not exhortational:
**score against a fixed grid of cases chosen to span the range of NEED (each cell stressing a
different physics / failure mode), and take the fidelity score to be the WORST-explained cell, not
the average.** Frequency decides population weight (how often the SIM draws each case); it must NOT
decide scoring weight (how much a cell's gap counts toward the score) — otherwise the rare-but-
catastrophic edge is averaged into invisibility. This is the same logic the campaign applies at
the physics level (requirement 4: *"the joint tail matters more than the marginal"*), lifted to the
scoring level: **the worst cell is the joint tail of the fidelity surface.**

---

## 1. The ARCHETYPE axis — chosen for scope of NEED, not numerosity

### 1.1 The design rule for the axis

An archetype earns a place on this axis iff it **stresses a physics or failure mode that no other
archetype on the axis stresses to the same degree** — it can *defeat* a model that is correct
everywhere else. Numerosity is irrelevant to inclusion (a self-generating prosumer household may
be 2% of the book and still be on the axis; the comfortable-DD-payer may be 60% of the book and be
on the axis only as the *reference*, see A5). The axis is deliberately **small** — one clean
representative per distinct physics — because every archetype added is a cell multiplied across
every regime, and a grid too large to measure honestly per-cell defeats the worst-cell rule
(unmeasured cells fail the score, §3.4).

The existing SIM cast (`simulation/segments.py`: `resi_standard`, `resi_smart`, `sme_standard`,
`sme_smart`, `gas_resi`) is a **frequency/population** partition — five cohorts chosen for book
realism, all sitting near the comfortable middle on the *need* dimension (all direct-debit,
all-paying, none exporting, none in acute distress). It is the right population model and the
**wrong scoring frame**: it spans the middle densely and the edges not at all. The scope-of-need
axis is a **cross-cut** over that population, keyed by the physics each case stresses. Some
archetypes map onto existing cohorts (A5 ⊇ `resi_standard`/`resi_smart`/`gas_resi`; A4 ⊇
`sme_standard`/`sme_smart`); others (A1 prepayment/arrears, A2 unusual-shape, A3 export/self-gen)
are **new scoring cases** the current cast does not populate — flagged as simplifications in §5.

### 1.2 The archetypes

| # | Archetype | Physics it STRESSES (that others don't) | Why in the frame — the model it can defeat | Diff from the comfortable middle |
|---|---|---|---|---|
| **A1** | **Affordability-stressed / prepayment (PPM) household** — low/volatile income, thin discretionary margin, may be on PPM or in arrears | **Collections & affordability physics:** arrears as the *output* of a hidden budget meeting a shock (W2_4); can't-pay vs won't-pay under uncertainty (W2_7); self-rationing invisible in payment data (W2_8); priority-of-debts, forbearance, cash-lag. The **direction** of a price move *bites hardest here* (bill shock → arrears → self-disconnect). | A hedge/pricing model that is perfect on cash-collecting DD payers is **blind** to the customer whose consumption *collapses below the TDCV floor while paying perfectly* — a vulnerability with no signal in the payment stream. Nails the middle, explains nothing here. | Middle pays in full on time via DD; A1's cash arrives late, partial, or not at all, and its *consumption* carries the distress signal the payment stream hides. |
| **A2** | **Unusual-consumption-shape household** — electrified heat (heat pump / electric storage) + EV, or an atypical occupancy pattern | **Demand-shape & weather-coupling physics:** a load profile that is **winter-peaked, temperature-convex, and evening-spiked** rather than flat PC1; the customer whose volume deviates *most* from the hedged EAC exactly in the cold∧still cascade (W1 §3, the volume channel of requirement 3's hypothesis). Cost-to-serve is shape-driven, not level-driven. | A cost/price-discovery model calibrated on the smooth average PC1/PC3 shape **mis-forecasts A2's volume in the tail** and mis-attributes its cost-to-serve — the model that "explains consumption" on the aggregate profile explains this customer's peaks not at all. | Middle tracks the standard settlement profile; A2's peaks land in the most expensive half-hours and its winter volume overshoots the hedge when incremental energy is dearest. |
| **A3** | **Export & self-generation prosumer** — domestic solar PV ± battery, net-metered / SEG feed-in | **Net-settlement & sign-flip physics:** import volume is *reduced and volatile*, occasionally **net-export** (negative import); self-consumption is a hidden decision behind the wall; feed-in payment is a *cash outflow* from the supplier; the customer's response to price/weather runs opposite to a pure consumer. | A billing/settlement and value-ranking model built assuming *volume ≥ 0, supplier always the seller* breaks on the customer who is sometimes a **counterparty who sells to you**. The model that ranks value by consumed kWh mis-ranks the exporter entirely. | Middle is a monotone importer; A3's meter can run backwards, its cost-to-serve and CLV logic must handle a two-sided flow and a feed-in liability. |
| **A4** | **Pass-through commercial (I&C half-hourly, flex / pass-through contract)** | **Where a price move bites — and doesn't (requirement 3):** on a pass-through/flex contract the **wholesale price risk sits with the customer, not the supplier** — a price spike that devastates a fixed-price domestic book *doesn't bite the supplier here at all*, only the customer's bill moves. Plus discrete SME/I&C **failure** physics (W2_6): bad debt **and a lost supply point**, a step-change signature, not the household's gradual slide. | A cost/margin model that treats every customer's price exposure identically (the naive "a spike hurts us everywhere") is **wrong in the opposite direction here** — it over-states supplier exposure on the pass-through book and mis-reads a slow-payer as a failing one. The requirement-3 discovery lives or dies on this cell. | Middle is a fixed-price domestic account where the supplier carries the price risk; A4 inverts the risk-holder and fails discretely, not gradually. |
| **A5** | **The comfortable middle (reference)** — stable DD-paying domestic (⊇ existing `resi_standard`/`resi_smart`/`gas_resi`) | **The calibration anchor / anti-archetype.** Stresses *no* edge physics by design — it is on the axis so the frame can **measure the gap between middle and edge explicitly**: a large spread between A5's cell gaps and the worst cell is itself the "explains the middle, not the edges" pathology made numeric. | A model is *supposed* to explain A5 well; A5 being the only well-explained column while A1–A4 are red is the exact signature the worst-cell rule is built to catch. A5 alone green ≠ pass. | It *is* the middle — included precisely so "good on the middle" cannot masquerade as "good." |

**Named-stressor coverage check (director's list).** affordability & collections → **A1**; unusual
consumption shape → **A2**; export & self-generation → **A3**; pass-through commercial → **A4**;
crisis vs calm regimes → the **regime axis (§2)**, orthogonal to archetype. All five of the
director's named stressors are covered; A5 is the only addition, justified as the reference anchor
the worst-cell rule needs (without it, "great on the middle" has nothing to be measured *against*).

**Merges considered and rejected.** (i) *Gas-seasonal-heating household* folds into A2 (unusual
shape = the same demand-shape/weather-coupling physics; commodity is a facet, not a distinct
failure mode). (ii) *Won't-pay strategic defaulter* stays **inside** A1 rather than as its own
archetype — it is the *classification* stress within the affordability cell (W2_7's other
quadrant), not a distinct physics; splitting it would double a cell without adding a failure mode.
Keeping the axis at **five** honours "small set, one physics each."

### 1.3 What each archetype couples to (reuse, don't invent)

The archetypes deliberately line up with couplings the harness **already scores**, so the frame is
implementable against existing gap plumbing rather than new machinery:

- **A1** ⇄ the affordability cluster already in the ledger: `W2_4`⇄`C6` (budget/affordability
  belief-error, live: tv≈0.30), `W2_7`⇄`C9` (can't/won't classification), `W2_8`⇄`C10`
  (self-rationing detection), `W2_11`⇄`D5` (payment-behaviour detection, live: gap≈0.297).
- **A2** ⇄ the weather cascade pair (W1 §3, `gap_cascade` — the volume channel) + cost-to-serve.
- **A3** ⇄ a **new** export/self-gen coupling BUILD must register (none in
  `coupled_triad.py::_AUTHORITATIVE_COUPLING` today) — §5 simplification + §6 open question.
- **A4** ⇄ `W2_6`⇄`C8` (SME distress/credit) + `W2_10`⇄`C12` (attribution, live: gap≈0.516) +
  the requirement-3 cost/price-incidence discovery.
- **A5** ⇄ the same pairs, evaluated on the comfortable band — the low-need reference reading.

### 1.4 Scoring frame vs population weight — the load-bearing distinction

Two different weights, kept strictly separate:

- **Population weight `π(archetype)`** — how often the SIM draws this case into the book. Frequency.
  Realistic (A5 large, A3 small). Lives SIM-side; feeds P&L and the population-draw atom (W2_2).
  **It does NOT enter the fidelity score.**
- **Scoring presence** — a cell is either **in the grid or not**, and every in-grid cell counts
  **equally** for the worst-cell rule regardless of `π`. A3 at 2% of the book and A5 at 60% get the
  *same* standing in the max (§3). The rare edge cannot be averaged away.

The one place `π` legitimately re-enters is **requirement 2 (VALUE)**, a *separate* arbiter: which
gap to *close first* is ranked by exposure = `π × harm-per-unit × gap`, so a cheap rare wrongness
can be deprioritised for *fixing* — but never for *scoring*. **Scoring says how wrong we are
everywhere; value says which wrongness to buy down first.** Conflating them is the anti-pattern
this whole doc exists to prevent (§4). This frame owns scoring only; it hands `π` to requirement 2
untouched.

---

## 2. The REGIME axis — small, orthogonal, stresses the archetypes differently

A regime is a **market/weather macro-state** the whole book lives through. The axis is kept to
**three** regimes chosen to be mutually orthogonal on the two dimensions that actually move
supplier physics — **price level (chronic)** and **correlated tail (acute)** — plus the calm
baseline. Adding a fourth that is a blend of these would be collinear and dilute the grid.

| # | Regime | Macro-state | Physics it stresses (orthogonal axis) | Real-world anchor (recall — verify at BUILD) |
|---|---|---|---|---|
| **G1** | **Calm / soft market** | Low, stable wholesale; competitive, thin acquisition margins; price war | **Retention/pricing & value-ranking under thin margins** — the regime where cost-to-serve differences *decide* profitability (activity-based pricing), and where being wrong is *cheap* (requirement 2's "correct to be more wrong here"). Low-and-flat. | 2019–early-2020 soft market / periodic GB retail price wars. *Recall.* |
| **G2** | **Crisis / sustained price spike** | High wholesale for a *sustained* period; hedge exhaustion, SoLR events, supplier failures; bill shock | **Chronic level-shift physics:** where the fixed-vs-flex cost wall (requirement 3) bites hardest — a fixed book's supplier eats the spike, a pass-through book's customer does; affordability collapses (bill shock → arrears → A1 amplified); capital/hedge stress. **Level, sustained.** | 2021–22 gas crisis (the campaign's own named case). *Recall — the qualitative shape (sustained high, ~29 GB supplier failures) is well-attested; exact figures verify at BUILD.* |
| **G3** | **Acute correlated tail (cold∧still / dunkelflaute)** | A short (days-long) joint weather tail; demand↑, wind↓, residual↑↑, price↑↑↑, imbalance↑↑↑ **simultaneously** | **Acute co-movement physics (the joint tail):** the volume-price double-hit (W1 cascade §1 link F); the demand-forecast error that lands exactly when incremental energy is dearest (A2 amplified); distinct from G2 in being **acute + correlated + mean-reverting**, not a level shift. | W1_3 measured entry shock: cold∧still decile lift **2.34×**, winter temp/wind corr **+0.507**, 2–7 day persistence (committed repo record). |

**Orthogonality argument.** G1 = low & flat; G2 = high & *sustained* (a level shift that persists
across many settlement periods); G3 = *acute & correlated & short* (a tail event that mean-reverts
in days). A model can be right in one and wrong in another for *unrelated* reasons — G2 tests the
cost-pass-through wall over time, G3 tests correlated-tail hedging over days. That non-overlap is
what makes them a useful axis rather than three points on one severity dial.

**R13 wall (curriculum, not baseline).** These regimes are the *capability to run* faithfully-
severe macro-states; **which** regimes the company actually lives through, and at what severity, is
**director-authored, named, versioned curriculum** — never agent-tuned toward a gap number, never
softened because company P&L looks bad (a loss in a faithfully-severe G2/G3 is a **finding**). The
frame supplies the grid; the director chooses the diet. The regime *thresholds* (what counts as the
G3 cold∧still corner) are **tail quantiles of the realised distribution** (winter-p10), baseline-
fidelity constants, **not** difficulty dials.

---

## 3. THE GRID + the WORST-CELL scoring rule

### 3.1 The grid

`Grid = {A1..A5} × {G1,G2,G3}` = **5 × 3 = 15 cells.** Each cell `(a, g)` is *one archetype living
through one regime*, and it inherits the coupled-pair gap(s) relevant to that archetype (§1.3),
**evaluated on the sub-population in that archetype under that regime.** Not every cell stresses
every physics equally — that is intended: the grid's job is to guarantee that **each distinct
physics is stressed in at least one cell**, and that no cell is silently unmeasured (§3.4).

```
             G1 calm/soft        G2 crisis/sustained   G3 acute cold∧still
   A1 afford  collections@thin   bill-shock→arrears     self-ration in a spell
   A2 shape   shape cost-to-serve tariff mismatch        volume overshoot @ peak price   ← typically the worst row×col
   A3 export  feed-in economics   export value in crisis  negative-load in the tail
   A4 passthr slow-payer vs fail  who-eats-the-spike      I&C flex in the tail
   A5 middle  REFERENCE (low need across the row — the anchor the worst cell is measured against)
```

### 3.2 "Explained", operationally — tie to the existing gap metric

A cell is **explained** to the degree its coupled belief-vs-truth **gap** is small, using the
metric already in the codebase (COUPLED_TRIAD_DESIGN §1, live in `coupled_gap_ledger.json`):

```
gap(cell) = raw_gap(cell) / g0(cell)          # dimensionless, per COUPLED_TRIAD §1.2
```

where `raw_gap` is the per-cell divergence between the SIM's hidden truth `θ` and the company's
observable-only belief/action `b` (the specific `loss(·)` is the one the cell's physics dictates —
classification for A1@can't/won't, detection for A1@self-ration, attribution for A4@confound,
belief-error/TV for shape/book-mix, VaR-ratio for A2/A3 in G3), and `g0` is that cell's **no-skill
baseline** (predict-majority / assume-independence / flag-nobody). Because every cell is a fraction
of *its own* no-skill baseline, **cells are directly comparable** — a gap of 0.6 on A1@G2 and 0.6
on A3@G3 mean the same *kind* of thing (60% of the way from blind to perfect), which is exactly
what makes a MAX across heterogeneous physics well-defined. Reading convention (unchanged): `0` =
perfect (structurally unreachable through the wall — reaching it is a **leak**, a defect not a
triumph); `1` = no better than blind; `>1` = **worse than blind**.

### 3.3 The worst-cell score

```
FIDELITY_SCORE(frame) = MAX over all in-grid cells  gap(cell)
```

— **the single worst-explained cell, not the mean.** Lower is better; a good frame score means
*even the worst edge* is explained. The companion diagnostics travel alongside it (never replace
it): `argmax` (which cell is worst — the thing to fix), the **middle-to-edge spread**
`MAX(edge cells) − mean(A5 cells)` (the "explains the middle not the edges" pathology, numeric),
and the full per-cell surface for the Proof door.

**Why MAX, not mean or a quantile.** The mean lets a blind edge hide behind a well-explained bulk
(the exact failure). A high quantile (p90) is the mean's disease in slower motion — with 15 cells,
p90 still discards the single worst. **MAX is the only aggregation under which a model blind at one
edge scores badly no matter how good it is everywhere else** — which is the property the director
requires. (Softening note for BUILD: if per-cell noise at small cast makes the raw MAX jumpy, the
honest smoother is a **small top-k mean of the worst cells with the count declared**, never a
downweighting of the worst — and it must degrade to MAX as noise falls. R4/R12: read the actual
per-cell variance from a real run before choosing k; don't tune it to flatter the score.)

### 3.4 Unmeasured cells FAIL — the frame is a control that can FAIL (R15)

The worst-cell rule is a **control**, and per R15 it must be able to fire on its own defects:

- **FAIL-OPEN guard (the critical one).** An **unmeasured** cell (no coupled gap yet — e.g. A3
  today, no export coupling registered) does **NOT** drop out of the MAX. It is scored as
  **`gap = untested` and treated as ≥ the worst measured cell** for the headline (rendered as an
  explicit amber "untested edge", never silently omitted). *A frame that quietly skips the cell it
  can't measure would let "great on 14 cells, blind on the 15th" pass — the precise thing forbidden.*
  So the headline is `MAX(measured gaps ∪ {untested-cells count as top-severity})`, and a frame with
  **any** untested in-grid cell cannot report a clean score.
- **TAUTOLOGY guard.** Each cell's `gap` recomputes `θ` and `b` from **independent** sources (SIM
  answer-key vs observable-only company output) — never reads back a stored "designed" gap. A cell
  whose `b` can see `θ` is a wall leak (`gap→0`), flagged red, not celebrated (§3.2).
- **FAIL-SILENT guard.** If the SIM answer-key or the company output for a cell is **unavailable**,
  that cell's check is a **FAILED** check (top severity), never skipped-and-green — an unavailable
  check is a failed check.
- **The killer mutation (designed, not coded here).** Construct a model that drives 14 cells' gaps
  →0.1 (near-perfect middle-and-most-edges) but leaves **one** edge cell at gap≈0.95 (blind). A
  **mean** score reads ≈0.16 → looks great (the bug). The **worst-cell** score reads ≈0.95 → **FAIL**.
  That divergence *is* the R15 proof that the control fires on its named defect ("nails the middle,
  blind at an edge"); BUILD must ship it as the frame's mutation test. Symmetric mutation: mark one
  cell "untested" and confirm the headline refuses a clean score (FAIL-OPEN guard fires).

### 3.5 R14 basis note

A gap is a **ratio**, not a financial figure, so it carries no settled/billed/banked clock — but
each cell **states its measurement basis** (which sub-population, which run/as-of date, which
regime injection) so a falling worst-cell trend cannot be an apples-to-oranges artefact of a
changed population or a re-drawn regime. Trend (`Δ worst-cell` over runs) is the story, per
COUPLED_TRIAD: falling = the company is learning to explain its hardest edge; static = a finding;
rising = regression.

---

## 4. Why this is EPOCH-2-FIRST

**The frame determines what every downstream atom optimises toward.** Requirement 1 is defined
before the physics deepens because the scoring rule is the **objective function** the whole
campaign is graded by:

- **Cost / price discovery (requirement 3)** — if scored on the average, a discovery model
  optimises the aggregate cost curve and can be arbitrarily wrong on A4's pass-through incidence
  (who *actually* eats a spike) because A4 is few. Scored worst-cell, the requirement-3 discovery
  is *forced* to get the fixed-vs-flex incidence right, because A4@G2 is a scored cell that will be
  the max if it doesn't.
- **Correlations / joint tail (requirement 4)** — the worst-cell rule at the *scoring* level is the
  same doctrine as "joint tail > marginal" at the *physics* level. A model calibrated to average
  correlation erases the coincidences that kill suppliers; the worst cell (A2/A3 @ G3) is where
  that erasure shows, so scoring worst-cell *makes* the correlation work face its own tail.
- **Billing physics (event delays, true-ups, meter→cash lag)** — the affordability edge (A1) and
  the export sign-flip (A3) are where billing physics is hardest; worst-cell scoring keeps billing
  honest at those edges rather than on the clean DD middle.
- **Value-ranking (requirement 2)** — value ranks which gap to *close*; but "how wrong are we,
  per cell" (this frame) is the **input** value consumes. Value cannot rank exposure without a
  per-cell gap surface to weight. So the frame is upstream of value, and value is Epoch-2 itself.

**The anti-pattern it prevents (stated so BUILD can guard it).** *Optimising the population average
and erasing the edges.* Every downstream atom, graded on an average, has a gradient that points
toward the numerous middle and *away* from the rare-but-catastrophic edge — it will, if left to a
mean, quietly learn to be excellent on A5 and blind on A1/A3. The worst-cell rule removes that
gradient: there is no score credit for improving an already-good cell while a worse cell stands.
Defining the frame first is what makes this the objective from atom one rather than a correction
bolted on after a mean-optimised model has already erased the edges.

---

## 5. Portability / wall / simplifications (R10)

### 5.1 Portability — the frame is archetype-and-regime keyed

- **Keyed by physics/function, not by GB specifics.** Archetypes are named by the *failure mode*
  they stress (affordability, consumption-shape, export/self-gen, pass-through, reference), not by a
  GB tariff or fuel — a second market's cast fits behind the same five slots (a second geography has
  its own affordability-stressed and its own prosumer). Regimes are keyed by *macro-state shape*
  (low-flat / high-sustained / acute-correlated-tail) with thresholds as **tail quantiles of the
  realised distribution**, so a second market re-derives its own corners without hardcoded £/°C/m·s⁻¹.
- **Product as a facet, not a new axis.** Gas vs electricity vs (future) a second product is a
  *facet* of an archetype (A2 covers electrified-heat; a gas archetype folds into shape), so a new
  product adds event types inside the frame, not a new scoring engine — honouring the portability
  lens *"would a second product fit inside this brain."*
- **The worst-cell aggregation is product/market-agnostic** — MAX over whatever cells the grid
  holds; adding a market multiplies cells, never changes the rule.

### 5.2 The wall, kept (requirement 5)

The frame scores the company's **observable-based beliefs `b`** against the SIM's **hidden truth
`θ`**; the harness is the only layer that holds both. The company never sees `θ`, never sees its own
cell gaps, never sees the archetype/regime labels — a real supplier gets no labelled answer key for
who was really can't-pay, which household self-rationed, or which regime it is standing in. The
**randomness** (which archetype is drawn, which regime the curriculum runs, the stochastic shocks)
lives **behind the curtain** (requirement 5); the company infers structure from observables,
imperfectly, and the measured per-cell gap *is* the point. A cell whose gap reaches 0 is a **leak**,
not a triumph (§3.2/§3.4).

### 5.3 Simplifications asserted here (R10 — register + what BUILD needs to ground them)

| # | Asserted (not yet data-derived) | What BUILD needs to ground it |
|---|---|---|
| S1 | **The 5-archetype partition itself** — that these five spans "the range of need." Asserted from domain reasoning + the director's named list, not from a data-driven clustering of the real book. | A data-driven needs-clustering (e.g. over affordability band × load shape × generation × contract type) to confirm five is enough and no distinct physics is unrepresented. Network + real segmentation data. |
| S2 | **A1's affordability-band boundaries** (comfortable/managing/stretched/negative — inherited from the live W2_4 ledger). | Calibration of band cut-offs to a real income/essential-cost distribution (recall: Ofgem affordability / ONS — verify at BUILD). |
| S3 | **A2 unusual-shape & A3 export/self-gen are not populated by the current SIM cast** (`segments.py` has no PPM-arrears, heat-pump/EV, or PV/battery cohort). | SIM-side archetype generators for A1(PPM/arrears sub-cohort), A2(electrified-heat/EV load), A3(PV±battery net-export) — Epoch-2/3 BUILD; today they are *scoring slots awaiting a population*. |
| S4 | **A3's export/self-gen coupling is unregistered** — no entry in `coupled_triad.py::_AUTHORITATIVE_COUPLING`, no gap formula for net-export sign-flip / feed-in liability. | BUILD registers the A3 pair + defines its `loss(·)`/`g0` (a net-settlement belief-error or feed-in mis-attribution gap); until then A3 cells are **untested** and score top-severity per §3.4. |
| S5 | **Regime real-world anchors** (G1 soft-market dates, G2 2021-22 magnitudes/failure counts) are **recall**, and regime *severity/naming* is director curriculum. | Verify anchors against primary sources at BUILD (no network here); the director authors the named, versioned regime scenarios (R13). |
| S6 | **Cell equal-weighting in the MAX** and the **top-k smoother's `k`** (§3.3) are asserted defaults. | A real run's per-cell noise floor (R4) to set `k` honestly; confirm equal-weighting is the right null (vs a director-authored harm weight, which is *value* not *scoring*, and would be R13 curriculum if introduced). |

---

## 6. Open questions / what BUILD needs (unresolvable here — network / data / director)

1. **A3 export/self-gen gap formula.** The one genuinely new coupled metric (§5.3 S4): does the
   net-export sign-flip score as a **belief-error on net-position** (TV / MAE over the import↔export
   distribution) or as a **feed-in-liability mis-attribution** (attribution-style, mirroring W2_10)?
   Needs the SIM export generator's shape before the `loss(·)` can be fixed. BUILD + a sign-flip
   design call.
2. **Small-cast statistical power.** At the current ~31-account cast, several cells (A3 especially,
   A1 sub-quadrants) may have **too few entities** for a stable per-cell gap — the same limiter
   COUPLED_TRIAD §6 flags. Until the population-draw atom (W2_2) lands, worst-cell gaps are
   **directional, labelled provisional**, and the top-k smoother (§3.3) may be needed. The real fix
   is population volume, not a scoring tweak (R12).
3. **The top-k smoother's `k` (§3.3).** Needs a real run's per-cell variance to set honestly (R4);
   ship MAX (k=1) first and only widen if the measured noise floor demands it, with `k` declared.
4. **Cell equal-weighting vs a harm-weighted worst-cell.** Should every cell count equally in the
   MAX, or should a director-authored **harm weight** (vulnerable-edge > reference) shape which cell
   is "worst"? This is a **values/curriculum** call (R13) — a harm weight is *value* entering
   scoring, which the frame deliberately keeps out (§1.4). **Flag for director sign-off**; ship
   equal-weight first, do not invent a weight (mirrors the COUPLED_TRIAD harm-matrix open question).
5. **Regime curriculum authorship.** G1/G2/G3 as *capabilities* are baseline; the **named, versioned
   scenarios** the company actually faces (severity, duration, sequencing) are the director's (R13,
   requirement 5's curriculum wall). BUILD needs the director's first named Epoch-2 regime diet
   before any cell can be scored *in that regime*.
6. **Grid completeness audit.** Is any distinct supplier-killing physics **unrepresented** by these
   5×3 cells (e.g. a settlement/true-up-lag stress, a switching/erroneous-transfer stress)? S1's
   data-driven needs-clustering should be run at BUILD to confirm the frame spans the need before it
   is frozen as the objective the whole campaign optimises toward.

---

*Sources (all read/computed this pass, no network): `docs/staging/DIRECTOR_CAMPAIGN_EPOCH2_COUPLED_
WORLD_2026-07-19.md` (the five requirements, esp. req 1 worst-cell + req 2 value/frequency split +
req 4 joint-tail doctrine); `docs/design/COUPLED_TRIAD_DESIGN.md` (the gap metric family,
`gap=raw_gap/g0` normalisation, no-skill baseline, digest + Proof-door reporting, R15-failable
control pattern); `docs/design/W1_COUPLED_WEATHER_CASCADE_DISCOVER.md` + `W1_3` (G3 anchor: cold∧
still 2.34× decile lift, +0.507 winter corr, 2–7 day persistence; the volume-price double-hit);
`docs/observability/coupled_gap_ledger.json` (live gaps: W2_4/C6 tv≈0.30 with comfortable/managing/
stretched/negative bands, W2_10/C12 attribution≈0.516, W2_11/D5 detection≈0.297 — the affordability
cluster A1 couples to); `simulation/segments.py` (the existing frequency/population cast — the frame
is a scope-of-need cross-cut over it); `background/coupled_triad.py::_AUTHORITATIVE_COUPLING`
(registered couplings — confirmed no export/self-gen pair yet). External regime anchors (G1 soft-
market, G2 2021-22 crisis) are **recall only, flagged for BUILD-time verification**. R10/R12/R13/
R14/R15, COUPLED_TRIAD, MAKE_IT_STICK, EPOCH_GATING, portability + C-S constraints, and the
epistemic wall referenced inline.*
