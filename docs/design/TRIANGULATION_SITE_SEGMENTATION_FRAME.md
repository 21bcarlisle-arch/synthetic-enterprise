# Triangulation extended — the WEBSITE (Spec 005) and SEGMENTATION (Spec 006) (DISCOVER→FRAME)

**Source:** `docs/staging/in_progress/DIRECTOR_STEER_TRIANGULATION_SITE_SEGMENTATION_2026-07-22.md`
(advisor carrying the director's direction). **Type:** [STEER] — extends the Spec-001 triangulation
pattern (blind board expectation × ratified canon × primary DISCOVER) to two further domains: the
site as showcase+director's-window, and segmentation. Mechanism mine; the constructs in the steer are
the **wall**. Tagged by the steer **narrow/reversible** (doc-and-analysis; any site rebuild routes
through the director's Expert-Hour, any generator/schema change through the reserved gate).

**Status:** DISCOVER→FRAME, **doc-only**. Provenance: **proposal**. Writes **no** `sim/`/`company/`/
`site/`/`harness/` code, edits **neither** `maturity_map.yaml` nor any engine, claims **no** level,
edits **no** `DIRECTOR_CANON.md` (director-reserved, Law B) and **no** ratified site/brand canon.
Touches only `docs/design/`. Candidate atoms are *named, not registered* (orchestrator is sole map
writer per THREE_LANES until `H9`). **No network this session** (autonomous run) — every external
fact is flagged **`[recall — verify at BUILD]`**; in-repo files are quoted from the live tree read
this session; **no figure fabricated** (Historical Ground Truth).

**Companion to** `docs/design/TRIANGULATION_WEATHER_DEMAND_PRICE_FRAME.md` (Specs 002/003/004) and the
Spec-001 triangulation. **The board Specs 005/006 have NOT landed** — commissioned blind, in parallel.
This doc is the pre-arrival pass: it fixes the reconciliation STRUCTURE and the canon each spec will be
scored against, so that when a board spec lands the line-by-line reconciliation is mechanical.

---

## 1. Spec 005 — THE WEBSITE (showcase + director's window)

**What the board will specify blind:** what a site must be when it is simultaneously (a) the public
showcase of an autonomous-supplier experiment and (b) the sole operating window for its single human
director. **The novel instruction in this steer** (beyond the 001–004 pattern): the board's
expectations become the **director's standing scoring rubric for axis 1** — his one-line verdicts
("site n/5 — reason") will reference it, so each expectation must be **individually scoreable and
trackable over time**.

### 1.1 Reconcile-against (existing ratified canon — do NOT fork; a conflict is a director finding)

| canon | file | status this session | what it binds |
|---|---|---|---|
| **PURPOSE_PITCH_V4** (the apex) | `docs/design/PURPOSE_PITCH_V4.md` *(ratified)* | cited by both constitutions as the winner on conflict | mission = carbon abatement via personalisation, **£/tCO₂e**; autonomy is the *how*; regulatory reality (a fully autonomous licensed supplier will not be permitted) stated up front |
| **POESYS_SITE_BRIEF** (v4-reconciled) | `docs/design/POESYS_SITE_BRIEF.md` | read; header confirms **v4 reconciliation supersedes v3**; six-doors + private IA survives; Front-Door chart = the £/tCO₂e carbon story | site structure/job, audiences, IA |
| **SITE_CONSTITUTION** (v4-reconciled) | `docs/design/SITE_CONSTITUTION.md` | read; **ratified pitch wins on conflict**; rebuild is director-eye-gated ("propose before rebuilding") | migration order, narrative spine follows the pitch's own §-order |
| **BRAND_CONSTITUTION** | `docs/design/BRAND_CONSTITUTION.md` | read; **sits ABOVE** both site docs on visual/verbal identity; director-ratified 2026-07-13 | palette, wordmark, glyph grammar — wins on any visual-identity conflict |
| operational-window causal-chain | `DIRECTOR_STEER_SITE_REORIENT_TO_PURPOSE_2026-07-19` + the ratified causal-chain structure | the director's own ratified operating-window structure | the (b) "director's window" half of the spec's dual mandate |
| claim-status publication discipline | R11 (`CLAIM_EQUALS_PIXEL`) + the PROVISIONAL/claim-status labels | binding, enforced | every published figure carries its claim status; a claim that counts one side is not a claim |

**Reconciliation tension flagged up front (a director finding, not mine to resolve):** the site has a
**dual audience baked into its constitution** — (a) *public showcase* (CEO/COO/VC/domain-expert must be
convinced of a carbon-abatement thesis) and (b) *sole director's operating window* (dense, honest,
decision-driving). These pull opposite ways on density, polish, and candour. The board's blind Spec 005
will land its own weighting of the two; **where the board's weighting conflicts with the v4 pitch's
"public thesis first" ordering, that is a finding for the director — flag it, do not silently pick a
side** (steer §005 bullet 2, verbatim intent).

### 1.2 The axis-1 scoring rubric — STRUCTURE proposed (the steer's novel ask)

The steer requires each board expectation be **individually scoreable and trackable over time**. Proposed
structure, to be populated line-by-line when the board spec lands (NOT built now — this fixes the shape):

> **`site_axis1_rubric.json`** (proposed artefact, when Spec 005 lands): one row per board expectation,
> each carrying `{expectation_id, board_text (verbatim), reconciles_to (canon file/§ or NEW), current_score
> (n/5), director_verdict_history: [{date, score, one_line}], evidence_surface (live URL/door), status}`.
> The director's "site n/5 — reason" verdicts append to `director_verdict_history`, making axis 1
> **trackable over time** rather than a point-in-time gut score. Each row is a coverage cell: a board
> expectation with **no matching live surface** is a first-class gap (mirrors the Spec-006 coverage test).

**Why a structure, not the rubric itself:** the rubric's ROWS are the board's blind expectations, which
have not landed. Building rows now would be inventing the board's spec — the exact thing the blind design
forbids. The structure is reversible scaffolding; the director ratifies the populated rubric.

**"NOT credible" battery seed (Spec 005) — a site is NOT credible as the dual artefact if:** (a) it argues
the retired v3 go-live thesis rather than the v4 £/tCO₂e carbon thesis; (b) a published figure lacks its
claim status / clock (R11/R14); (c) it counts only the saved side of the carbon three-ledger (saved /
spent-serving / net); (d) the director's operating-window half is decorative — a surface that drives no
decision (the same "useful vs decorative" test Spec 006 raises, applied to a site door); (e) it invents an
argument the ratified pitch does not make. These join the standing practitioner fidelity oracle per the
steer.

---

## 2. Spec 006 — SEGMENTATION

**What the board is asked blind:** what segmentation should *change about how a supplier acts* — which
decisions it drives, what makes it **useful vs decorative**, and which GB domestic segments a veteran
would insist exist. Two binding instructions in this steer: a **coverage test** (board-named segments ×
the data-derived structure), and a **learning-value-leak guard**.

### 2.1 Reconcile-against (existing canon — the one-taxonomy object is already built)

| canon | file | what it binds |
|---|---|---|
| **CANONICAL EPISTEMIC RULING** (wall-class, director console 2026-07-21) | `docs/design/SEGMENTATION_RECONCILIATION_FRAME.md` §0 | ground truth lives ENTIRELY behind the wall; company starts from **EPC + census priors only** and discovers the rest through interaction, scored on the belief-vs-truth gap; **no segment label / attitude / sensitivity ever crosses** |
| the ONE taxonomy | `SEGMENTATION_RECONCILIATION_FRAME.md` §1 — D-SEGMENT folds INTO population-coverage | 12 factor axes (`cohort_schema.json`: tenure, accommodation, cars, nssec, heating_fuel, region, green_stance, price_sensitivity, channel_pref, solar_PV, EV, home_battery), each `observed`/`fused`/`assumed` |
| the joint-structure gate | `population_fusion_assumptions_register.json` | every dimension pair a testable hypothesis with a refutation condition; conservative crossing by default |
| **the learning-value knee (arbiter)** | `learning_value_frontier.json` + `build_learning_frontier.py` | objective = **LEARNING value** (η² / VoI per outcome, equal weight — the ONE declared choice), bad debt a POSITIVE signal, **protection a floor OUTSIDE the ranking**; **supersedes** the earlier P&L-weighted `value_frontier.json` |
| the protected-groups floor | `POPULATION_COVERAGE_NESTED_DESIGN.md` | protection is a floor, not a ranked objective |
| the wall discipline | `company/interfaces/sim_interface.py`; verifier extension named in `SEGMENTATION_RECONCILIATION_FRAME.md` §0 | company-side reads EPC/census + own interaction observables ONLY (R10: the class fails automatically) |

### 2.2 The coverage test — STRUCTURE (the steer's first binding instruction)

When the board names its blind segments, run each against the data-derived structure:

> **`spec006_coverage_matrix.json`** (proposed, when Spec 006 lands): one row per board-named segment,
> `{board_segment (verbatim), maps_to_axes: [cohort_schema axes], present_in_frontier (bool), verdict}`
> where verdict ∈ {**MATCH** (board segment ↔ a data-derived cohort — corroboration), **BOARD-ONLY**
> (board names it, absent from the data-derived structure → a *coverage gap* finding, first-class),
> **DATA-ONLY** (the learning-value route found a cohort no practitioner would name → evidence the data
> route found something practitioners miss, first-class)}. **Both directions are valuable; report both
> honestly** (steer §006 bullet 1, verbatim intent).

### 2.3 The learning-value-leak GUARD (the steer's hard constraint — mechanised note)

The steer is explicit: **do NOT leak the learning-value objective to the board via any channel.** The
board is asked its own practitioner view of "useful vs decorative"; if the board is told the company
already ranks segments by information value (η²/VoI), the board's answer becomes a rubber-stamp of ours
and the triangulation collapses (identical failure mode to DIRECTOR_TWIN Law B — a judge that learns the
answer it is checking is worthless). **FRAME guard for whoever runs the board elicitation:** the board
prompt must describe segmentation in practitioner terms only (what decisions it drives, what a veteran
would insist exists) and must NOT surface `learning_value_frontier.json`, η²/VoI, the equal-weight
choice, or the "which segments teach the company most" framing. This is a wall on the *elicitation
channel*, distinct from the SIM/company data wall.

### 2.4 "Useful vs decorative" as a candidate metric amendment (the steer's third ask)

The steer asks whether the board's "useful vs decorative" test should be folded into the learning-value
metric itself: *a segment that changes no decision has no learning value.* **This already rhymes with the
live objective** — `learning_value_frontier.json`'s objective is "which segments **teach the company
most**," and a segment driving no decision teaches nothing actionable. **Proposed amendment (propose-then-
proceed, not applied here):** add a **decision-linkage gate** to the frontier — a cohort scores learning
value only if at least one company decision (pricing, targeting, contact cadence, credit) is
*conditioned* on membership; a cohort that no decision reads is decorative and scores zero regardless of
its η². This sharpens VoI from "outcome variance explained" to "outcome variance explained *that a
decision can act on*." **Do NOT apply until the board's framing confirms it sharpens ours** (the steer's
own condition) and the director ratifies the metric change (values-adjacent → propose-then-proceed).

**"NOT credible" battery seed (Spec 006) — a segmentation is NOT credible if:** (a) any segment label /
attitude / sensitivity crosses the wall to the company directly (R10 class-fail); (b) the company's
discovered belief is not *scored* against SIM ground truth (no coupled-triad gap); (c) a board-named
veteran segment is silently absent with no coverage-gap finding; (d) segments drive no decision yet are
published as insight (decorative); (e) protection is treated as a ranked objective rather than a floor.

---

## 3. Candidate atoms (NAMED, not registered — orchestrator is sole map writer)

Each is DISCOVER/FRAME-workable NOW (doc-only); any BUILD touching `site/**` returns via the director's
Expert-Hour, any touching the segmentation generator returns via the reserved gate (both per the steer's
own risk tag).

- **`SPEC005_site_reconcile`** — line-by-line MATCH/CONFLICT of board Spec 005 vs the v4 canon stack when
  it lands; **builds `site_axis1_rubric.json`** (§1.2) so axis 1 is scoreable + trackable. *DISCOVER now
  (structure); populate when the board spec lands.*
- **`SPEC006_coverage_matrix`** — the board-segments × data-derived-cohorts coverage test (§2.2), both
  directions reported. *DISCOVER now (structure); populate when the board spec lands.*
- **`SPEC006_decision_linkage_metric`** — the "useful vs decorative" → decision-linkage-gate amendment to
  the learning-value frontier (§2.4). *FRAME now; metric change is values-adjacent → propose-then-proceed,
  director-ratified.*

---

## 4. Process (per the steer, unchanged from Specs 001–004)

1. **Primary/literature DISCOVER need not wait on the board** — this doc is the in-repo + structure pass.
   External practitioner-segmentation and site-craft anchors are `[recall — verify at BUILD]` (no-network
   autonomous run).
2. **When board Specs 005/006 land** — reconcile line-by-line (board / this doc / canon); every
   disagreement is a finding; each spec's "NOT credible" battery (§1.2 / §2.4 seeds) joins the standing
   practitioner fidelity oracle. The axis-1 rubric and the coverage matrix get populated then.
3. **Findings → proposals** via propose-then-proceed — **no silent scope changes.** DISCOVER/FRAME and
   the reconciliation structures are reversible and proceed; the site rebuild (director's Expert-Hour),
   the generator/schema change (reserved), and the learning-value metric amendment (values-adjacent) come
   back as named proposals.

**The steer stays in `docs/staging/in_progress/` — genuinely open sub-item:** board Specs 005/006 have
NOT landed (commissioned blind, in parallel); the line-by-line reconciliation, the populated axis-1
rubric, the coverage matrix, and the metric-amendment decision are pending their arrival.
