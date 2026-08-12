# WORKER FINDING — a seam control mutated the side it was not about, and the walk could not tell

**Severity:** LATENT · **Lane:** H_harness

**Filed** 2026-08-12, from the H27 Expert Hour #22 landing (atom D38, `H27_payment_belief_gap`).
**Class** control-that-cannot-fail (R15) — wrong-subject sub-class: a mutation applied to one
side of a seam, read as proof about the other.
**Rank requested** backlog. Nothing published rests on it; no epsilon and no figure moved.

## 1. The correction to a filed cause — observed-with-evidence

`docs/staging/done/WORKER_FINDING_A_MUTATION_THAT_PATCHES_BOTH_SIDES_OF_ITS_SEAM_2026-08-12.md`
(instance 2) attributed the isolation failure of
`test_a_composer_that_stops_carrying_a_renderers_string_fires` to the `pair._PUBLISHED_BOOKS`
cache: run alone the cache is empty, so "the books are composed *after* the patch, both sides
use the mutated renderer". The failure it quotes is real. **The cause is not.**

Re-derived this tick, in a fresh interpreter with an EMPTY cache each time:

| composer module imported before the patch? | `renderer_in_note` |
|---|---|
| yes (`import background.live_payment_triad` first) | `False` — the control fires |
| no (first import happens inside `_publish_one_book`) | `True` — the control cannot fire |

The composer binds its renderers with `from background.gap_metric import format_ageing_summary`
**at its own import time**. Patching `gap_metric` after that import does not move the composer's
binding — the divergence exists and the cache is irrelevant. Patching it *before* that import
means the composer binds the patched object, both sides move together, and no divergence can
arise. The operative variable is the **import graph state**, not the book cache; the cache
mattered only because populating it forces the composer's import.

This matters practically: the repair the cache story implies (pre-seed the books) does not fix
the control when the composer module is imported late, which is exactly the condition a
single-test run creates.

## 2. The defect underneath, and what landed

The control patched the **walk's** renderer and read the resulting divergence as the
**composer's** defect. Even where it fired, its subject was the swap, not the seam — the same
shape as Hour #20 at the ledger seam and Hour #21 in `has_door_carrier` (a value test doing
provenance work), here one level down in the module system.

Landed in `tools/couple_w2_11_d5.py` + `tests/tools/test_couple_w2_11_d5.py`:

* each published book now records the renderer **object** the composer's own module namespace
  held when it wrote the note (`composer_renderers`, resolved by name and then by `__name__`,
  because the composer imports one of them under an alias);
* the walk reports `renderer_provenance` per figure, and `check_reader_render_sites` refuses
  every state but `the_composers` — a walk that executed somebody else's renderer, or a book
  that recorded no binding at all, is an unmeasured seam and therefore a failed check (R15);
* the composer-defect sentence is **withheld** unless the provenance carries it, so a divergence
  is never attributed to the wrong side;
* the seam control now mutates the composer (a `write_gap_entry` wrapper that reformats the note
  it is handed, renderer identity untouched) and asserts its own one-sidedness;
* the old walk-side mutation survives as its own named control, asserting the refusal fires and
  that the composer is *not* blamed.

Five source mutations, each firing a named test: refusal removed; composer sentence made
unconditional; `unrecorded` made fail-open; the alias fallback dropped; the provenance
re-resolved through the walk's own path instead of the composer's.

## 3. The class that is NOT closed — queued, not fixed

Both controls now self-check their one-sidedness, so *these two* cannot silently invert again.
The general class is untouched: **a control whose subject depends on which modules an earlier
test happened to import**. Nothing in this repo measures that. The cheapest honest mechanism is
a meta-control that re-runs each named mutation control alone, in a fresh interpreter, and
requires it to still fire — which means a nested pytest process, and this project has already
been bitten twice by nested pytest inside a gated run (`feedback_a_fixtures_neutralise_list_
rots_when_the_callee_gains_a_check`, `feedback_wedge_payload_is_contaminated_by_nested_pytest_
output`). **Recommended, and what I would take next:** a `tools/` entrypoint, run outside the
publish gate, that takes a list of mutation-control node ids and asserts each fails when its
source mutation is applied and passes when it is not — the R15 pass made re-runnable rather
than a per-Hour manual ritual. Not taken this tick (SELF_INTERRUPT_DISCIPLINE): it is new
tooling on a shared path and nothing is blocked by queueing it.

## 4. Reported, not acted on: H27 has held at L2 for twenty-two consecutive Hours

Level 2, `level_target` 3, and every Hour since 2026-08-09 has found a real defect in the
instrument — so the hold is honest each time, and the atom is not the OPS2 shape (a criterion
the hardware cannot satisfy). But nothing states what would END the streak, which is the half of
the OPS2 lesson that generalises. **Recommended promotion criterion, written into the record
this tick so the next Hour can act on it rather than re-derive it:** an Hour that finds no defect
requiring a source change to the instrument promotes H27 to L3 on the spot, citing the Hours
whose findings are closed. A streak with no stated exit is a criterion nobody re-asks.
