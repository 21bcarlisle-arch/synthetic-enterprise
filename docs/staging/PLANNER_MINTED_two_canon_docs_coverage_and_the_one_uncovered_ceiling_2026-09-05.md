<!-- SUPERVISOR_DRAW: self-drawable -->

**Severity:** RECORDED · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** A49_the_ceiling_comes_before_the_programme_on_r3_and_r4

# [PLANNER-MINTED] Two director canons, nine deliverables: eight already built, one uncovered — and the uncovered one is the ceiling (2026-09-05)

**Source rulings:** `DIRECTOR_CANON_RERANKING_THE_ARC_2026-09-04.md` (5 deliverables) and
`DIRECTOR_CANON_PRODUCT_AND_MACHINERY_2026-09-05.md` (4 deliverables), both WORK THIS CREATES blocks.
**Mint rule applied:** §2+§4 of `DIRECTOR_RULING_WORK_DEFINITION_AND_COHERENCE_2026-07-27` — one atom
per named deliverable, and **a deliverable already covered by a map atom or a landed mechanism is not
re-minted.** Eight of the nine were covered. One atom is minted: `A49`.

---

## Why this document exists rather than nine new atoms

Both canons have been sitting in the staging root being re-drawn every tick, which reads as "nothing
has happened on them". That reading is wrong, and the tick that acts on it would build nine things
that mostly exist. **The work landed without the mint, so the queue could not see it.** This is the
record that closes that gap, deliverable by deliverable, with the evidence checked against disk and
`origin/main` at `48427494a` — not against the doorbell's summary of them.

---

## RERANKING THE ARC (2026-09-04) — 5 deliverables

| # | Deliverable | Status | Evidence (checked this tick) |
|---|---|---|---|
| 1 | Map re-ranked so R1–R5 outrank Epoch 3, in the existing machinery | **COVERED** | `dial_inherited` distribution over 83 live atoms: 11 atoms at **45**, the Epoch-3 adapters at **3**. A change of weights, not of machinery, exactly as §5 required. |
| 2 | R1 and R2 sequenced as one programme in two halves | **COVERED** | `PB4_engagement_separated_from_elasticity` landed at `1fe160dc8`; `PB5_pounds_or_percent_resolved` is dial 45, `loop_stage: build`, L0→L2. Both in `W2_customer_generator`. The two-halves sequencing is recorded in `SEAT_FINDING_R1S_INFERENCE_CEILING_IS_AT_THE_NULL_AND_R2_CANNOT_PAY_UNTIL_R1_LANDS_2026-09-04`. |
| 3 | EP7–EP12 and EP14 unblocked and available, ranked below R1–R5 | **COVERED** | All eight EP7–EP14 atoms now carry `block_reason: None` (the `director-reserved curriculum sequencing (R13)` reservation §4 lifted is gone) and sit at dial 3 — available, and ranked below the 45s. |
| 4 | R5 returned to the director as a curriculum question with its measured cost | **COVERED** | `A46_book_depth_is_a_curriculum_question`, dial 45, L1→L2. Its map note states "RETURNED, NOT DECIDED, as WORK THIS CREATES item 4 requires"; the priced menu is `docs/design/A46_THE_PRICED_MENU_2026-08-30.md` with the letter at `docs/staging/SEAT_TO_DIRECTOR_A46_*`. |
| 5 | Ceiling-before-programme discipline applied to R1–R4 before building | **PARTIAL → MINTED as `A49`** | R1 has `tools/r1_inference_ceiling.py`; R2's bound follows from R1's result. **R3 and R4 have nothing.** See below. |

## PRODUCT AND MACHINERY (2026-09-05) — 4 deliverables

| # | Deliverable | Status | Evidence (checked this tick) |
|---|---|---|---|
| 1 | The distinction expressed where work is chosen, not only where it is described | **COVERED** | `background/supervisor.py::_product_priority_ids` (:5637) — the enumeration the selector reads, not a doc. |
| 2 | The selector changed so product work can win against machinery work | **COVERED** | `_drop_lane_blocked` (:5656) now exempts product-priority atoms from the RUNG 1c blocking-finding lane exclusion, keyed against `_priority_zero_active` (:5733) as the canon's own test for essential machinery. Plus RUNG 1e, an unread director document preempting self-filed findings. |
| 3 | The split measured and visible, with a bad ratio filing itself | **COVERED** | `tools/product_machinery_split.py`, and the ratio filed itself as `SEAT_FINDING_THE_PRODUCT_SHARE_IS_ZERO_AND_THE_SELECTOR_NOT_THE_DIAL_IS_WHY_2026-09-05` (BLOCKING) — the mechanism working, first time out. |
| 4 | The floor: a stretch with no product progress is a finding | **COVERED** | `_product_starvation_stretch` (:5697), read at :5395. Keyed to a product atom being **named in a commit**, not to `file_scope` — the finding records that a scope-keyed version was written first and would have been fail-open (123 file-touches inside product scopes over 20 hours with zero product commits). |

---

## The one uncovered deliverable, and why it is the expensive one

`grep` over `tools/` returns six ceiling instruments: five are EP13's (`ep13_input_ceiling`,
`ep13_ccgt_swap_ceiling`, `ep13_ccgt_level_ceiling`, plus the per-fuel and biomass bounds) and one is
R1's. **Neither R3 (the score, £/tCO₂e) nor R4 (products beyond price) has any bound on what it could
be worth if it worked perfectly** — and R4 is the largest unbuilt programme on the map, with §2's own
statement that the mission is unreachable without it.

**The cost of skipping this is measured, not asserted, and EP13 is the measurement.** That atom ran
twelve passes without leaving L2. The ceiling discipline arrived at pass seven and then retired *five*
candidate programmes — the outage model, the within-day axis, a publishable within-day CCGT proxy,
biomass dispatch, and (honestly) left the daily-gas-level rung **undecided rather than falsely
retired**, because the control that would have licensed the retirement was itself fail-open. Every one
of those would otherwise have been built first and bounded afterwards.

`A49` carries one lesson forward that EP13 paid two passes to learn: an instrument must state whether
it is a true **CEILING** (perfect knowledge of the quantity a real method approximates — a negative
retires the candidate outright) or a handicapped **FLOOR** (bounds from below — a negative retires
nothing). EP13's tenth pass conflated them and its eleventh corrected it.

**Not machinery about machinery** (PRODUCT_AND_MACHINERY §4): both instruments measure the world and
the book, which is product under the canon's own test.

---

## Two drawn items that were already done, recorded so the next tick does not redo them

- **Lane 0, the five-path fork with `origin/main`.** Resolved by another lane. `HEAD == origin/main ==
  48427494a`, and all five named commits (`88d493ac9`, `7b3134f86`, `5b4e5602e`, `f459f9895`,
  `aab6fb990`) are ancestors of `origin/main` by `merge-base --is-ancestor` — the check that survives
  `surgical_land` never pushing. Nothing to decide.
- **LANE 1 BUILD, `EP13_adapter_carbon_intensity` at level 2→3.** The drawn brief is the mint-time one
  and is stale: it says the adapter feeds "`E5_carbon_three_ledger`, which today has no real feed
  behind it", but `sim/neso_carbon_intensity.py` has existed since 2026-08-26 and the atom's own
  30,261-byte level-hold note says so. All three defects E5's FRAME queued as "the cheapest genuinely
  unblocked increment" are also already repaired: non-finite rejection at `carbon_ledger.py:105-113`,
  label survival through aggregation via `LedgerRow`, and the R14 basis gate, whose fix was promoted
  from E5's instance to a derived class rule on 2026-08-22 (it had been a two-name allowlist hiding
  five unclocked figures). **LAW A: the drawn 2→3 is a diagnostic, never a target.** A thirteenth pass
  was not taken, and the reason is recorded here rather than left for the next tick to rediscover.

— Delivery seat, 2026-09-05.
