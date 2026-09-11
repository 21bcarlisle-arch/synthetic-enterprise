<!-- SUPERVISOR_DRAW: self-drawable -->

**Severity:** RECORDED · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** W2_19_who_lives_where_money_and_composition

# [PLANNER-MINTED] The ruling and the canon: nine deliverables, seven already minted — and six of the seven exist only in the working tree (2026-09-07)

**Source rulings:** `DIRECTOR_RULING_SUPPLIER_USE_CASE_REGISTER_AND_SIM_FIDELITY_2026-09-06.md`
(4 deliverables) and `DIRECTOR_CANON_THE_DEMAND_VECTOR_2026-09-07.md` (5 deliverables), both from
their WORK THIS CREATES blocks.

**Mint rule applied:** §2+§4 of `DIRECTOR_RULING_WORK_DEFINITION_AND_COHERENCE_2026-07-27` — one
atom per named deliverable, and **a deliverable already covered by a map atom is not re-minted.**
Seven of the nine are covered. Two are minted here.

Machine-readable coverage (one line per deliverable, the form `named_but_unminted` reads):

- Source: `DIRECTOR_RULING_SUPPLIER_USE_CASE_REGISTER_AND_SIM_FIDELITY_2026-09-06.md`, deliverable 1 — MINTED here as `A50`
- Source: `DIRECTOR_RULING_SUPPLIER_USE_CASE_REGISTER_AND_SIM_FIDELITY_2026-09-06.md`, deliverable 2 — COVERED (`W2_25`, `W2_26`, `W2_31`), with a stated limit
- Source: `DIRECTOR_RULING_SUPPLIER_USE_CASE_REGISTER_AND_SIM_FIDELITY_2026-09-06.md`, deliverable 3 — COVERED (`G14`, `G15`)
- Source: `DIRECTOR_RULING_SUPPLIER_USE_CASE_REGISTER_AND_SIM_FIDELITY_2026-09-06.md`, deliverable 4 — MINTED here as `A51`
- Source: `DIRECTOR_CANON_THE_DEMAND_VECTOR_2026-09-07.md`, deliverable 1 — COVERED (`W2_29`)
- Source: `DIRECTOR_CANON_THE_DEMAND_VECTOR_2026-09-07.md`, deliverable 2 — COVERED (`W1_28`)
- Source: `DIRECTOR_CANON_THE_DEMAND_VECTOR_2026-09-07.md`, deliverable 3 — COVERED (built: `tests/architecture/test_a_coverage_claim_declares_what_it_reduces_over.py`)
- Source: `DIRECTOR_CANON_THE_DEMAND_VECTOR_2026-09-07.md`, deliverable 4 — COVERED (`W2_30`)
- Source: `DIRECTOR_CANON_THE_DEMAND_VECTOR_2026-09-07.md`, deliverable 5 — COVERED (`W2_31`)

---

## Why this document exists, and the thing it found on the way

The doorbell drew both documents as unminted and listed all nine deliverables. **Seven of them were
already minted.** That is the same shape as `PLANNER_MINTED_two_canon_docs_..._2026-09-05`: work
landed, the mint record did not, and the queue therefore re-drew the whole thing every tick.

But the reason the queue could not see it this time is a **defect in the machinery, not a missing
document**, and it is the more valuable half of this tick. `background/primary_state_scan.py` is
LAW C's second, independent read of primary state — the source that is supposed to contradict the
supervisor when the supervisor is wrong. Its parser had drifted from the supervisor's in two
places, both silently, both in the fail-open direction:

1. **The heading parser.** The supervisor gained an optional section-number group on 2026-09-05
   (`## 5. WORK THIS CREATES`), with a comment recording that on the day it was found *"EVERY §4
   defect report in the tree was false"*. The mirror never gained it. Measured today: the supervisor
   parsed **4** deliverables from the ruling, the mirror parsed **0**.
2. **The document vocabulary.** The supervisor widened to admit `[DIRECTOR-CANON]` and gave its
   prefix tuple one home, with a comment naming the exact failure it was fixing — *"how a vocabulary
   widened in one place stays narrow in the other"*. It then happened again, across the module
   boundary, to this mirror. A **BLOCKING** director canon naming five deliverables was a mint source
   to the doorbell and invisible to LAW C.

So `named_but_unminted()` returned **no residue at all** for either document. The §0 failure class —
a ruling names work that was never minted — was invisible in the one source built to catch it, for
every numbered ruling and every canon. Residue went **37 → 46** when both were repaired; the nine new
entries are exactly these two documents.

**The drift guard that should have caught it could not.** `test_local_parser_agrees_with_supervisor_parser`
existed, imported both parsers, and passed — because all five of its fixtures head the block with the
bare phrase. It never fed the parsers the one shape the 2026-09-05 repair was made for, and it only
ever compares *text in, list out*, so it was structurally blind to the vocabulary half. Both gaps are
now closed by controls keyed to the property rather than to today's answer, each proven by a poison
round: mutating the section-number group out reds two tests, mutating `CANON` out reds one.

---

## The ruling — 4 deliverables

| # | Deliverable | Status | Evidence (checked this tick, against disk and `HEAD`) |
|---|---|---|---|
| 1 | Use-case register published to Capabilities, external register, status per item | **UNCOVERED → MINTED as `A50`** | `site/data/capabilities.json` parses to `{generated_at, git_commit, phase, cards}`. Case-insensitive counts over the whole serialised document: `use case` **0**, `use_case` **0**, `register` **0**, `status` **0**. Nothing on that surface is the register. |
| 2 | Scope additions to People P1 (allocation rules; going-cold), Housing/People P1 (per-asset usage decomposition with a sum-to-total control), People P2 (lever/nudge/game responses; consent to control; channel behaviour) | **COVERED, with a stated limit** | `W2_25_people_phase2_shape_and_attitudes` (dial 50) carries the P2 subject and its `block_reason` names the people ruling 2026-09-05 §2 item 1 *and* the amendment that pulled scope forward — "THE SCOPE IS THE AMENDED ONE". `W2_26_people_phase3_the_residual_and_the_change` and `W2_31` carry the rest. **LIMIT, stated rather than glossed:** I verified the *atoms* exist and are scoped to these phases; I did **not** verify each of the six named sub-items (allocation rules, going-cold, per-asset decomposition, the sum-to-total control, consent to control, channel behaviour) has a home. That check is `A50`'s first dependency and is named there rather than assumed here. |
| 3 | Two data assets: half-hourly carbon intensity; forward-curve/hedge-cost series | **COVERED** | `G14_half_hourly_grid_carbon_intensity_aligned_to_settlement` (lane `G_data_learning`, dial 45) and `G15_forward_curve_series_to_backtest_hedging_by_physics` (lane `E_finance_treasury`, dial 45). Both `loop_stage: build`, both `block_reason: None`, and — unlike the canon's rows — **both present at `HEAD`**. |
| 4 | One plain-English report to the director: the register as published, the gaps folded, the two pulls landed, the envelope decision awaiting him | **UNCOVERED → MINTED as `A51`** | No `SEAT_TO_DIRECTOR_*` document exists for this ruling. It cannot be written before item 1, because three of its four sections describe the register. |

## The canon — 5 deliverables

| # | Deliverable | Status | Evidence (checked this tick, against disk and `HEAD`) |
|---|---|---|---|
| 1 | Coverage re-measured against the demand vector, weighted distributional acceptance test, dominant term named, both N figures | **COVERED** | `W2_29_the_coverage_is_re_measured_against_the_demand_vector`, lane `W2_customer_generator`, dial 50, `loop_stage: build`, `block_reason: None`. **Not at `HEAD`.** |
| 2 | The weather partition re-opened as a joint question over a stock with varying fabric | **COVERED** | `W1_28_the_weather_partition_is_joint_over_a_stock_with_varying_fabric`, lane `W1_market_weather`, dial 60, `loop_stage: build`. **Not at `HEAD`.** |
| 3 | A control refusing any coverage, ceiling or sufficiency claim that does not declare the dimension it reduces over | **COVERED — built, not just minted** | `tests/architecture/test_a_coverage_claim_declares_what_it_reduces_over.py`, **14 passed**. Its docstring names this canon and this item as the defect it owns, and states why nothing went red before: *"Both figures were correct arithmetic on the quantity they named."* **The file is UNTRACKED (`??`).** |
| 4 | Per-household half-hourly electricity shape and seasonal gas shape as the demand deliverable | **COVERED** | `W2_30_per_household_half_hourly_electricity_and_seasonal_gas_shape`, dial 50, `loop_stage: build`. **Not at `HEAD`.** |
| 5 | People phase 1 re-cut so the physical layer stands alone, commercial correlated rather than merged | **COVERED** | `W2_31_people_phase1_the_physical_layer_stands_alone`, dial 50, `loop_stage: build`; and commit `bf35fde11` *"W2_19 physical layer: the postcode explains nine per cent of who lives there"* is the measurement behind it. **The row is not at `HEAD`.** |

---

## The finding in the coverage itself: six of the seven covering rows are not at `HEAD`

`git grep` for each atom id against `HEAD -- docs/design/` returns hits for `G14` and `G15` and
**nothing** for `W2_29`, `W2_30`, `W2_31` and `W1_28`. Those four rows live only in the shared working
tree's `docs/design/maturity_map.yaml`, which carries **207 uncommitted insertions** from another
lane. The canon's item-3 control is untracked outright.

So the honest statement of coverage is two-tier, and conflating them would be the
`CLASS_UNCOMMITTED_AND_ORPHANED_WORK` shape exactly:

- **Durable:** the ruling's deliverable 3 (`G14`, `G15`).
- **At risk:** the canon's five, all of them. A `reset --hard`, a mixed reset onto a moved origin, or
  a whole-file rewrite of the map by any lane deletes four map rows and one test file, and the
  coverage claimed above evaporates with them. This has already happened once in this tree this week
  (`462af9439`).

**This is not a thing to fix by editing the map.** A pathspec commit of `maturity_map.yaml` stages
the *working-tree copy* and would carry the other lane's 207 lines inside this lane's commit. The
correct move is that the lane holding those rows lands them; this document's job is to make the
exposure visible rather than to reach across it. That is why `A50` and `A51` below are specified in
full here and deliberately **not** written into the map by this tick.

---

## The two atoms minted

### `A50_the_supplier_use_case_register_is_published_with_a_status_per_item`

- **Lane:** `A_strategy_governance`
- **Target level:** L0 → L2
- **Deps:** the six named sub-items of the ruling's deliverable 2 must first be located or declared
  missing (see the limit stated above) — the register's "status per item" cannot be truthful until
  each use case's SIM-fidelity dependency has a home or an explicit gap.
- **Exit criteria:**
  1. Every use case in the ruling appears in the register with a status drawn from a closed
     vocabulary, and each status is *derived* from map/tree state, never hand-set.
  2. The register reaches a reader: it renders on Capabilities, and a door test asserts the **lifted**
     value changed, not a feed the test itself built.
  3. A use case whose SIM fidelity is not established publishes that as a named gap — an honest
     `None` with a reason, not an omission and not a plausible status.
  4. A control that reds when a use case is added to the ruling and not to the register.

### `A51_the_plain_english_report_on_the_use_case_register_reaches_the_director`

- **Lane:** `A_strategy_governance`
- **Target level:** L0 → L1
- **Deps:** `A50` (three of its four sections describe the register); the two data pulls `G14`/`G15`.
- **Exit criteria:** one document covering the register as published, the fidelity gaps folded into
  existing phases, the two pulls landed, and the envelope decision stated as awaiting him — sent on
  NTFY, carrying a recommendation rather than a bare ask.

---

## What this tick did and did not do

**Did:** repaired both halves of the LAW-C parser drift, with two controls proven by poison round;
re-derived the residue (37 → 46); checked all nine deliverables against disk and `HEAD`; minted the
two that were genuinely uncovered.

**Did not:** write `A50`/`A51` into `docs/design/maturity_map.yaml`, for the contention reason above;
verify the six sub-items of the ruling's deliverable 2, which is named as `A50`'s dependency rather
than assumed either way.

— Delivery seat, 2026-09-07.
