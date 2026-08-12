# [PLANNER-MINTED / GOVERNANCE] — The household page becomes a two-sided wall exhibit; the bill prints its catch-up line (2026-08-12)

**Provenance:** processing `DIRECTOR_RULING_THE_PORTAL_IS_A_WALL_EXHIBIT_2026-08-12.md` as a mint
source, per §2+§4 of `DIRECTOR_RULING_WORK_DEFINITION_AND_COHERENCE_2026-07-27`.

## The defect this mint is also reporting, not silently absorbing

This ruling has **no formal `WORK THIS CREATES` block** — the pattern §4 of
`DIRECTOR_RULING_WORK_DEFINITION_AND_COHERENCE_2026-07-27` requires every ruling/steer to carry so a
mint has a named deliverable list to work from, rather than a mint author inferring one from prose.
Per that ruling's own instruction for exactly this case: **mint what work can be identified from the
body, and request the missing block from the author — do not silently absorb it.** This document does
the first half; this paragraph is the second half of that request. The ruling's own "Requirements" and
"Non-negotiables" sections under each Part were detailed enough to derive two atoms from directly, but
a future ruling of this shape should carry the block so a mint is not reconstructing deliverables from
narrative prose.

## Coverage checked before minting

`grep` for `portal|wall exhibit|catch-up.*render|catchup.*render` over `docs/design/maturity_map.yaml`
returns only the pre-existing `D_printed_figure_rederivation` (a sibling, not a duplicate — it covers
re-derivation-vs-carry-through generally; it does not print the catch-up line, fix the pence rounding,
or touch the portal's naming/framing) and `D_money_boundary_reconciliation` (owns `BILL_FOOTS`, does
not touch the renderer). No existing atom and no existing `PLANNER_MINTED_*` document covers either
Part. **Both mints below are NEW; neither is a re-mint.**

## Part → atom

| Part | Deliverable (ruling's own Requirements/Non-negotiables) | Atom | Lane | Epoch | Level |
|---|---|---|---|---|---|
| 1 | Catch-up line printed on-screen + PDF, footing to the penny, pounds-and-pence rendering, value carried not re-derived | `D36_bill_render_footing_and_pence` | D_billing_metering | 1 | 0 → 2 |
| 2 | Rename/re-home the page as a structurally-enforced two-sided wall exhibit | `SITE2_two_sided_wall_exhibit` | H_harness | 3 | 0 → 3 |

Both are `provenance: director_ruling`, `loop_stage: build`, `dial_inherited: 1` (matching the
OPS9–14 mint precedent from the same day). `SITE2` couples with `D36` (same file,
`site/customers/index.html`) — the ruling's own "Part 2's redesign must not undo Part 1's fix" is
carried as `D36` being one of `SITE2`'s own exit criteria (criterion 7), not a `depends_on` edge,
since the ruling explicitly leaves ordering ("whether Part 1 ships ahead of Part 2 or inside it") open
to the builder.

`SITE2`'s `level_target` is 3, not 2 like `D36` and the OPS atoms: this is a live, public-facing wall
exhibit whose whole point is customer/company/SIM attribution being *trustworthy*, which this project's
own maturity ladder reserves for an Expert-Hour "this is real" verdict (`docs/design/MATURITY_MAP.md`
§3), not a mechanically-real happy path.

## Value-stream classification

Both filed under `close_to_learn`. Neither prices, bills, meters or settles anything: `D36` changes
how a correct, already-footing figure is *displayed*, not what it *is*; `SITE2` changes how the wall
represents itself on a public page, not what any figure is or what anyone pays. `meter_to_cash` /
`price_to_bill` would each claim a revenue flow neither atom touches. `tests/design/
test_maturity_map_facets.py::REVIEWED_CLOSE_TO_LEARN` gained one new entry (`SITE2`; `D36`'s stream,
`price_to_bill`, needed no entry — it's a bona fide billing-render fix, unlike `SITE2`).

## Registration

Two atoms appended to `docs/design/maturity_map.yaml`. `tests/design/test_maturity_map_contract.py` +
`test_maturity_map_facets.py`: 36 passed. Map size after the append: 400,337 bytes against the 409,600
ceiling — `tools/size_ratchet_gate.py` unaffected.

## What this mint does NOT do

- It does not fix the printed bill. That is `D36`'s own build — a real render-layer change to
  `site/customers/index.html` (add the fifth line, switch the bill path off the zero-decimal `gbp()`),
  not a side-effect of registering the atom.
- It does not rename or re-home the page, nor build the per-panel side-declaration mechanism. That is
  `SITE2`'s own build.
- It does not disposition the parent ruling beyond recording that its deliverables now have atoms —
  see the defect note above; the missing block itself is still open.

— Planner mint, from `DIRECTOR_RULING_THE_PORTAL_IS_A_WALL_EXHIBIT_2026-08-12`, 2026-08-12.
