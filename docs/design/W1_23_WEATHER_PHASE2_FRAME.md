# FRAME — W1_23: the other loads the cells do not carry

**Atom:** `W1_23_weather_phase2_the_other_loads_the_cells_do_not_carry`
(lane `W1_market_weather`, `level_current: 0 → level_target: 3`, `loop_stage: idle`, dial 60)
**Stage:** FRAME only. **No BUILD code was written and none may be** — the atom is
DECIDED, NOT AUTHORISED (weather ruling 2026-09-05 §2 item 2), and its opening condition
("opens when phase 1 lands") is unmet. `EPOCH_GATING_AND_ATOM_AUTHORSHIP.md` Rule 1:
epoch gating gates BUILD, never thought.
**Date:** 2026-09-06, worker tick, LANE 3 DISCOVER/FRAME draw. **First pass on this atom.**
**Measured at HEAD** `e42301c21`, against real disk state (the pull receipt and the tree),
never against the ruling's prose alone.

Everything below is `observed-with-evidence` unless labelled PREDICTION.

---

## 0. What the atom is, in one line

Phase 1 (`W1_14`, bounded into `W1_19`–`W1_22`) cuts GB into weather cells on **heat-load
drivers only** — mean temperature, wind, solar. A cell set that is right for heating is
**unvalidated** for hot water, lighting and summer load. Phase 2 asks whether the *same*
cells carry those three loads, or whether each needs its own cut.

The ruling names the three phase-2 drivers verbatim: *"cold-water / ground temperature
(hot-water load), day length (lighting load and evening shape), summer temperature
(cooling and appliance load; the futures engine needs it)."*

---

## 1. FINDING 1 — the three drivers are three different KINDS of problem, and only one of them is a weather-data problem

Measured against `docs/market_research/haduk_grid_pull_receipt.json` (318 files, 19.85 GB,
`pull_status: complete`, zero failures). The pulled variable set is exactly three:

| variable | normals (mon-30y) | monthly (mon) | daily (day) |
|---|---|---|---|
| `tas` (air temperature) | 1 | 35 | **210** |
| `sfcWind` | 1 | 35 | 0 |
| `sun` (sunshine duration) | 1 | 35 | 0 |

**There is no fourth variable on disk.** Now take the three phase-2 drivers against that:

**(a) Cold-water / ground temperature — NOT IN THE PULL, AND MAY NOT BE IN THE ARCHIVE.**
Nothing in the pulled set is a soil or ground temperature, and nothing in the repo mentions
one: a grep for `cold.?water|inlet temperature|ground temperature` across `simulation/`,
`company/`, `saas/` and `tools/` returns **zero hits**. So this driver has neither data nor
code today. Two routes, and the phase must pick one *and say which*: a published
soil-temperature series (source to be established — HadUK-Grid's 1 km variable list must be
read before assuming it has one), or a **derived** inlet temperature as a damped, lagged
function of annual air temperature. The second route is the industry's usual one and is
cheap, but it is a **Choice-class claim, not a Fact** (knowledge-page canon), and it must be
registered with its source and its named alternative. A lagged-sinusoid coefficient invented
to fill the slot is this project's most expensive recurring defect (CLAUDE.md, knowledge-first).

**(b) Day length — NEEDS NO DATA PULL AT ALL.** Day length is a deterministic astronomical
function of latitude and date. It is not a weather variable; it has no interannual variance,
no measurement error, and no source to license. Its "cell" is a **band of latitude**, and the
whole of its GB spread is computable in one pass today with nothing but the cell centroids
phase 1 produces. This is the cheapest bounded first move in the entire phase and it is
blocked on nothing except the cells existing.

*The load it drives is not deterministic.* Day length sets the *envelope*; lighting and
evening-shape load also depend on occupancy, which is the people axis (`W2_19`), and on cloud,
for which `sun` is already on disk. Phase 2 must not let "day length is deterministic" become
"lighting load is deterministic" — that is the driver/load conflation the ruling's own
property-side exclusion warns about.

**(c) Summer temperature — HALF ON DISK, AND THE MISSING HALF NEEDS A NEW CEDA PULL.**
This is the finding with a cost attached. The 210 daily `tas` files decompose as 35 years ×
6 months, and the six months are, measured from the filenames:

```
{01: 35, 02: 35, 03: 35, 10: 35, 11: 35, 12: 35}
```

**January, February, March, October, November, December.** The receipt states the selection
rule itself: `daily_heating_seasons.definition = "October-March"`. **April to September has no
daily temperature on disk.**

So summer splits cleanly, and phase 2 must split it too:
- **Summer LEVEL** (mean summer temperature per cell, the cooling/appliance *magnitude*):
  answerable today. The 35 monthly `tas` files are whole-year files, so June–August means are
  already on disk.
- **Summer SHAPE** (heatwave persistence — consecutive-hot-day runs, the exact summer analogue
  of the cold-spell persistence the ruling put in *phase 1* as decision 4): **no data**. The
  210 daily files were pulled for winter persistence and stop at March.

That second pull is ~210 more files and roughly 13 GB, and it needs a live CEDA token. The
ruling records the token as personal and expiring "~3 days from 2026-09-05 mid-morning" —
**already expired as of this FRAME** — with the fallback stated: try the token-minting API,
and if it fails, NTFY the director for a fresh one rather than improvising. The receipt says
`token_source: minted`, so the minting API *did* work on 2026-09-05 after having returned 500
earlier; that is the route to try first, and it is the reason this is a bounded task rather
than a director dependency.

**Do not discover this at BUILD time.** The director's 2026-09-06 complaint against `W1_14`
was precisely "an expensive prerequisite finished, and the work it unblocks not sitting in
the queue as a bounded first move". The inverse — a phase opening and *then* finding its
prerequisite is a 13 GB pull on an expired credential — is the same defect with the sign
flipped, and this paragraph exists so that it is known before the phase opens, not after.

---

## 2. FINDING 2 — phase 2 as written is a PROGRAMME, and that is the defect `W1_14` was already corrected for

`W1_14`'s title was "derive the weather cells". A bounded tick reading it had **no first
move**, so eighteen hours passed with the pull complete and zero commits, and the fix
(commit `3606b21b7`, 2026-09-06) was to mint four successors each with a first move a tick
can take: `W1_19` (drivers per cell), `W1_20` (census household weights), `W1_21` (clustering
and the level curve), `W1_22` (persistence and synchrony). The commit message names it as the
third instance of the shape.

`W1_23` carries the identical defect. "Cold-water/ground temperature, day length, summer
temperature" is three research programmes in one row, with three different blocking
conditions (a source to establish; nothing at all; a 13 GB pull). **A tick that draws this row
for BUILD on the day it opens will have no first move**, exactly as `W1_14` did.

So the principal output of this FRAME is the bounded decomposition below.

### The four bounded successors, with their first moves

| # | Candidate | First move a bounded tick can take | Blocked on |
|---|---|---|---|
| 1 | **Day length per cell, and whether latitude alone cuts it** | Compute sunrise/sunset from the phase-1 cell centroids; report the GB spread in December and June hours; test whether the heat cells are a *refinement* of the day-length bands. | Phase-1 cells only. **No pull.** |
| 2 | **Summer level: does the winter cut carry summer?** | Read June–August means from the 35 monthly `tas` files already on disk; run the phase-1 coverage curve on summer level; report the cell count at 90/95/99%. | Phase-1 method only. **No pull.** |
| 3 | **Inlet temperature: anchor it or declare it** | Establish whether a published GB soil/ground-temperature series exists at usable resolution; if not, register the lagged-air-temperature derivation as a Choice with its alternative named. | A source question. **No pull.** |
| 4 | **Summer shape: heatwave persistence** | Mint the CEDA token via the API; pull daily `tas` for April–September; run `W1_22`'s persistence method on hot spells instead of cold. | **A ~13 GB pull on a credential that has expired.** |

Three of the four need no new data. That is the ordering, and it is not the ordering the
ruling's own sentence implies (it lists cold water first, which is the one with an
unestablished source).

### Why these are NOT minted as map rows today

Deliberate, and recorded so a later reader does not read the omission as an oversight. A
minted row with `loop_stage: idle` is correctly excluded from the BUILD draw — but it is
**included in the DISCOVER/FRAME draw** (`background/supervisor.py::_idle_discover_frame_
draw`). Minting four of them now would put four rows into the idle draw for a phase whose
central question — *do the heat cells carry these loads, or does each need its own cut?* —
**cannot be asked until the phase-1 coverage curve exists** (`W1_21`). Ticks would be drawn
into framing sub-work whose premise is not yet measurable. This atom's own origin note
already carries the sibling of this rule for the knowledge stubs: *"if they are ever minted
here that is duplication, not progress."*

**The minting condition is explicit:** when `W1_21` lands a coverage curve, mint successors
1–4 above from this table. Until then this FRAME is where they live.

---

## 3. PREDICTIONS — filed before the answer, so they can refute me

Recorded per CLAUDE.md ("a prediction filed after the answer is not a prediction"). All three
are unmeasured, and each is refutable by successor 1 or 2 above without any new data.

**P1. Day length will need FEWER cells than heat, and its cells will be a coarsening of the
heat cells, not a crossing.** Day length is monotone in latitude with no orographic, coastal
or continentality term, so its variation is one-dimensional where heat's is at least three.
*Refuted if* the day-length coverage curve needs more cells than the heat curve at the same
threshold, or if any heat cell spans more day-length variation than the 95% band allows.

**P2. Summer temperature will need cells that are NOT a refinement of the winter cells.** The
winter cut should be dominated by altitude and latitude (cold is high and north); the summer
cut should pick up an **east–west continentality axis** (inland England warm, Atlantic coasts
cool) that winter suppresses. If so, the two cut GB along different axes and one cell set
cannot carry both without loss — which is the phase's whole question answered in the
affirmative. *Refuted if* the summer 95% cell set is a strict refinement or coarsening of the
winter one.

**P3. Cold-water temperature will need the fewest cells of the three.** Ground temperature at
mains depth is a heavily damped, lagged annual mean; damping destroys exactly the short-run
variance that makes cells necessary. *Refuted if* its coverage curve is steeper than day
length's.

**P1 and P2 cannot both be about "granularity" in the same sense.** P1 is about *level*; P2 is
about the *axis of variation*. The ruling's decision 5 already forces level and shape to be
computed separately for heat; phase 2 inherits that split and must not average across it.

---

## 4. Level definitions and exit criteria (so `level_target: 3` is checkable)

The row carries `level_target: 3` and no level definitions anywhere. Proposed, for
ratification when the phase opens:

- **L1 (DISCOVER)** — for each of the three drivers: its source established or its derivation
  registered as a Choice with a named alternative; the data either on disk or its pull scoped
  with a byte count and a credential path. *Exit:* successor 3 lands a source finding, and
  successor 4 lands either the pull or a stated refusal with its reason.
- **L2 (FRAME/BUILD)** — a coverage curve per driver, household-weighted from the censuses
  (never from the SIM's drawn population — the ruling's decision 9), on the same method as
  `W1_21`, with the 90/95/99% cell sets named. *Exit:* three curves and three cell sets,
  rendered from the pipeline, never static.
- **L3 (the target)** — the phase's actual question answered: **one cell set or four?** A
  stated figure for the fidelity cost of forcing all four loads onto the phase-1 heat cells,
  and, if that cost is material, the merged cell set with its own coverage figure. Comparators
  (LDZ, GSP, SAP-21) overlaid afterwards, never fitted to. *Exit:* the knowledge page's
  expected-shape block states the answer falsifiably, and the phase-2 stubs `W1_14` minted are
  filled in place with both clocks.

**Proposed `file_scope`** (currently `[]`, which is checked by nothing — a level-0 row's
`file_scope` can name a control no build ever wrote): `docs/market_research/`,
`docs/institutional/knowledge_map.md`, `site/knowledge/`, and a phase-2 sibling of
`tools/generate_weather_cells_data.py`. Not written here; a `file_scope` naming a module no
build has written is the defect, so this stays a proposal until the first successor lands.

---

## 5. What would make this phase wrong

- **Re-cutting cells the phase-1 curve has not yet justified.** The question is whether the
  heat cells *carry* these loads. Cutting four cell sets before measuring the loss on one is
  answering a question nobody asked, at four times the cost.
- **A fabricated conversion.** HadUK publishes **sunshine duration, not irradiance** (the
  ruling says so, and the pull confirms `sun` is what landed). Any daylight-to-lighting-load
  or duration-to-irradiance coefficient must trace to a source or be registered as a Choice.
  The same applies with more force to the inlet-temperature lag.
- **Household weights from the SIM's own population.** Forbidden by decision 9, and the
  circularity would be invisible in the output — the coverage curve would become a statement
  about our draw rather than about Britain.
- **Treating summer as winter with a sign flip.** Cooling load is not heating load negated:
  it is threshold-triggered, it has almost no GB appliance base today, and its persistence
  behaviour (heatwaves) is not the mirror of cold snaps. The futures engine is the stated
  consumer, and it needs the summer *distribution*, not a reflected winter one.
- **Starting it.** The phase is registered, not authorised. This document is the whole of what
  is permitted until `W1_14`'s successors land.

---

## 6. What this pass did not establish

- Whether HadUK-Grid v1.3.2 publishes any soil or ground temperature variable at 1 km. The
  pulled set does not contain one; the archive's full variable list was **not** read this
  pass (it is a network read, and `company/`/`saas/` may not open a socket — this is a
  `tools/`-side pull and belongs to successor 3, not to a FRAME).
- Whether the CEDA token-minting API still works. The receipt proves it worked once, on
  2026-09-05. Whether it works today is successor 4's first move and is not assumed here.
- Any figure for how much variation the phase-1 cells leave unexplained on the phase-2 loads.
  That number does not exist yet and this document does not invent one.
