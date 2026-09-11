**Severity:** RECORDED · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** H45_the_queue_is_chained_to_the_map

# The six rulings were already minted. The seven gaps are almost all the reader-facing half

**Audited 2026-09-07**, delivery seat, scheduled tick, against the doorbell's mint instruction
(§2+§4 `DIRECTOR_RULING_WORK_DEFINITION_AND_COHERENCE` 2026-07-27). **Method:** every named
deliverable in each ruling's `WORK THIS CREATES` block, checked against `maturity_map_store`
(both halves), `docs/design/simplifications/`, `site/knowledge/` and `site/data/`.

---

## The headline

The doorbell asked for **one atom per named deliverable across six rulings** — 30 deliverables.
**Twenty-three are already minted.** The map carries 14 live rows and 8 closed rows with
`provenance: director_ruling` that trace to these six documents. Re-minting them was the instruction's
own named failure mode, and this is the "state which are already covered" half of it.

**Nothing was minted this tick from the rulings.** One atom, `W2_27`, was closed during it — but it
was another lane's, and my attempt to mint it produced a duplicate I then had to remove
(`4fcf171ed` → `1c97ed54e`, and the finding beside this one).

## Deliverable by deliverable

**Weather cells, phase 1** (2026-09-05) — 4 named, 4 covered.

| deliverable | where |
|---|---|
| knowledge page (full depth) + four stubs | `site/knowledge/weather-cells/` |
| research/analysis pass, §3.2–3.3 | `W1_19`, `W1_20`, `W1_21`, `W1_22`, `W1_25`, `W1_27` (closed); `W1_14` (L1, build) |
| phases 2 and 3 registered as decided-not-authorised | `W1_23`, `W1_24` — both `idle`, both `depends_on: W1_14` |
| plain-English report to the director | not an atom; director-facing |

**Housing value ceiling and sample, phase 1** (2026-09-05) — 7 named, 5 covered.

| deliverable | where |
|---|---|
| premise joint extended, anchored, marginals-preserving | `W2_21` |
| space-filling sample, output-similarity test, two coverage curves, N | `W2_22`; **N answered by `W2_27`, closed today at 13 cases** |
| per-house ceilings on the seven levers, current-settings draw, house-driven CLV | `W2_18` |
| **knowledge page (full depth) + two stubs** | **GAP** |
| register rows and research docs | `docs/market_research/`, populated |
| phases 2 and 3 registered | `W2_23`, `W2_24` |
| **plain-English report to the director** | **GAP** |

The knowledge-page gap is not my inference — it is declared in the project's own record. Two research
docs carry the header *"the housing knowledge page is deliverable 4 of the housing ruling and is not
yet written"*, and both say the figure they publish stands in for it.

**People, money and who they are, phase 1** (2026-09-05) — 8 named, 5 covered.

| deliverable | where |
|---|---|
| layer-one joint on small-area geography, conditioned on house | `W2_19` |
| **independence register for un-joined pairs** | **GAP** — no file, no row, no mention outside the ruling |
| layer-two anchored residuals; curriculum-slot register | `W2_25` frame + `W2_19` simplification |
| per-household hidden truth, people-driven usage, credit and payment propensities | `W2_19` |
| coverage curves and N for the axis; the crossed curve | crossed curve is `W2_27`; the people axis curve is not separately evidenced |
| **knowledge page (full depth) + two stubs** | **GAP** |
| phases 2 and 3 registered | `W2_25`, `W2_26` |
| **report to the director, including the slots awaiting his values** | **GAP, and it is the one that blocks him** |

**July steers reconciled, parked audit** (2026-09-05) — 3 named, 3 covered.
The three document dispositions and the re-homed open item are document actions, not atoms. The
amendment against the people ruling *is* the amendment ruling of the same date. The parked-documents
audit is `H48`.

**Amendment: merit order, people phases, practice books** (2026-09-05) — 4 named, 1 covered.

| deliverable | where |
|---|---|
| People P1 scope extended; phases 2–3 re-scoped | recorded on the `W2_19` / `W2_25` frames |
| **move emitter wired to the change-of-tenancy register; deemed contracts on move-in** | **GAP** (below) |
| **four practice books added to the run-mix proposal for ratification** | **GAP** — "practice book" appears nowhere outside the two rulings |
| **fidelity-effort ordering recorded and cited by each phase-1 report** | **PARTIAL** — recorded in one simplification file; the "cited by each report" leg has no control |

On the move emitter: the design side exists (`B7_CUSTOMER_STATE_MOVES_AND_SHOCKS_FRAME.md`,
`W2_12_CHANGE_OF_TENANCY_DEBT_PHYSICS_DISCOVER.md`) and `B7_customer_state_layer_moves_and_shocks` is
on the map — but at `provenance: proposal`, so **it does not descend from this ruling**, and its
`file_scope` names `sim/customer_state_layer.py`, **which does not exist**. Both `sim/` and
`simulation/` are real directories here, so this is not a stale-prefix rename that a grep would
surface; it is a level-0 row pointing at nothing, which is the class
`SEAT_FINDING_TWENTY_EIGHT_OF_THIRTY_FOUR_LEVEL_ZERO_ROWS_NAME_NO_CONTROL` already counted.

**Supplier use-case register and sim fidelity** (2026-09-06) — 4 named, 2 covered.

| deliverable | where |
|---|---|
| **use-case register published to Capabilities, external register, status per item** | **GAP** |
| scope additions to People P1, Housing/People P1, People P2 | `W2_19` simplification carries per-asset usage and the sum-to-total control |
| two data assets: half-hourly carbon intensity; forward-curve/hedge-cost series | `G14`, `G15` |
| **report to the director** | **GAP** |

The Capabilities door is live and generated, but from the maturity map: `capabilities_door.json` holds
`world`, `supplier`, `go_live`, `typed_seams`, `wall`, `scale`, `gaps`. There is **no use-case
register key**, so the register the ruling asked to publish has no home on the page it named.

## What this says

**Seven gaps, and five of them are the reader-facing half of work that is otherwise done.** Two
knowledge pages, three director reports, one published register. The measuring got minted; the
telling did not. That is a legible pattern and not a coincidence — a bounded tick can pick up
"extend the premise joint" and cannot pick up "one plain-English report", so the deliverables that
are not code accumulate.

The two gaps that are *not* that shape are the **independence register** (people, deliverable 1) and
the **four practice books** (amendment, deliverable 3). Both are single named artefacts with no
trace anywhere in the tree.

## What is next

1. **Mint the seven.** I did not, deliberately: both map halves were mid-collision for this whole
   tick, and adding seven level-0 rows to a file two lanes were already contending would have been
   the wrong second act after the duplicate. They are enumerated above in mint-ready form — lane,
   parent ruling, and what would close each — and the next tick that holds the map cleanly should
   take them.
2. **The director reports are his, and three are outstanding**, one of which (people) is explicitly
   *"including the slots awaiting his values"* — so a ratification is parked behind a report nobody
   has written. That is the item with a person waiting at the end of it.
3. `B7_customer_state_layer_moves_and_shocks` should be repointed at a real path and re-provenanced
   to the amendment ruling, or the move-emitter deliverable minted separately. As it stands the
   ruling's deliverable looks covered from the lane index and is not.
