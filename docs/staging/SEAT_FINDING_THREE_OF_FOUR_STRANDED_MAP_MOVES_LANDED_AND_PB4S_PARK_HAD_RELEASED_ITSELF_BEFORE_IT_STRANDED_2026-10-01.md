**Severity:** LATENT · **Lane:** H_harness · **Epoch:** 3 · **Atom:** `H49_an_untracked_copy_of_an_earlier_origin_revision_is_cleared_like_a_twin`

# Of the four stranded map moves, three landed and PB4's was already dead: its park had released itself before it was stranded

**2026-10-01, delivery seat, claim `land-h47-l3-and-three-stranded-map-moves-from-the-preserved-ref`.**
Source: `refs/preserved/unwedge-ff-2026-10-01/{maturity_map.yaml,gate_authorizations.jsonl}`, diffed
against `e196d0937`, and the shared tree's dirty companions
(`WORKER_FINDING_THE_SHARED_TREE_WAS_HELD_29_BEHIND_BY_FOUR_LANES_STRANDED_LEVEL_MOVES_2026-10-01.md`).

## What landed

- **H47 L2→L3**, in one commit. That commit carries the map hunk, the original jsonl line (its
  original ts, in ts order), the blind-review ledger line, the simplifications entry, and
  `_verdict_cell` with its control. The 5 mutations the record names were re-run and all 5 went red.
  **One more was missing.** If `_verdict_cell` is un-wired from `_render_figures`, every control stays
  green and the published row goes back to a bare `AGREES`. That is a missing test, not an
  equivalence. It is now controlled by
  `test_the_published_table_carries_the_qualified_cell_not_the_bare_verdict`, which goes red under
  that mutation.
- **W2_28 L1→L2.** The row set its own condition: "Level 2 needs that debt paid". I re-measured it
  today. `OUTSTANDING` is `{}`. `tools.reduction_dimension --undeclared` exits 0 with 0 outstanding.
  The control plus `test_weather_cell_siting.py` give 30 passed. The preserved ref held **no ledger
  line** for this move, so the level gate would have refused it. I recorded one through
  `record_level_up_self_certified`.
- **SP2_2 build→idle**, simplifications 6→8 (the stranded entry plus my re-read). The park still holds in substance. The AB lineage's next
  step is EP17's book-varying pilot, which waits on the director's ruling (`32c04d778`). Its
  replicate-to-the-penny comparisons are exactly what a world-wide re-seed would break. I added one
  line to its store that restates the release.

## What did not land, and why

**PB4 build→idle.** I dropped it on purpose. The park note was written 2026-09-29 at 13:53Z. It says:
"return it to `build` when he answers or when PB6 reaches L2". PB6 reached L2 at 14:35Z the same day
(`gate_authorizations.jsonl`, the PB6 level-2 line), forty minutes later. DIRECTION.yaml
(2026-10-01) also names PB4 as an active focus item, and its EAC work is landing on origin
(`3bf64c4e7`). Landing `idle` would park a row that its own rule had already released. The row stays
`build` at HEAD. The PB4 store's dirty note recorded NTFY `9kuLLifpjEiV` as put to the director. That record
is landed in a follow-up commit, with the release written beside it. The shared copy was then
refreshed to HEAD (preserved first), so it cannot wedge the next fast-forward that touches PB4.

## The class

A level or park written into the shared map and stranded is a **prediction about the row's
conditions at the moment it was written**. One day later, one of the four was false. A preserved ref
cannot be replayed verbatim: each hunk's own release condition has to be re-asked before it lands.
