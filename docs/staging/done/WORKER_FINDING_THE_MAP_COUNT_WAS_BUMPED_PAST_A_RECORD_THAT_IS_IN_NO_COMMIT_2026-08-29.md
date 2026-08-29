# [WORKER-FINDING] The map's simplification count was bumped past a record that is in no commit, so `tests/design/` is red at HEAD and green in every working tree (2026-08-29)

**Severity:** BLOCKING · **Lane:** H_harness · **Status:** measured, not repaired — filed per
`SELF_INTERRUPT_DISCIPLINE`. This tick's draw was the Lane 0 founder-book landing ("code is in
HEAD and its controls are not"); this is the SAME CLASS one surface over, found while
pre-gating that landing, and repairing it on sight would have been the self-serving move.

## Class registration

Belongs to `uncommitted_and_orphaned_work`. Declared rather than left to the title regex, for
the reason that class's own docstring records: a document whose title says "in no commit"
carries none of the `uncommitted`/`orphan`/`untracked` tokens the net matches on, and the
previous instance of exactly that shape sat live and unlisted for six passes with `--check`
green. The declaration is the fix; a wider net would not be.

## What is true at HEAD

    docs/design/maturity_map.yaml         SPINE_1_scenario_world_state: simplifications_count: 3
    docs/design/simplifications/SPINE_1_scenario_world_state.yaml   2 records

    tests/design/test_simplifications_store.py::test_counts_match_file_contents
      → SPINE_1_scenario_world_state: map simplifications_count=3 != store file count=2

Reproduced in a clean extract (`git archive HEAD | tar -x -C /tmp`), 1 failed in 0.56s, with no
uncommitted work of any lane present.

## Why nobody has seen it

**It is green in the working tree.** The third record EXISTS there, uncommitted. So every seat
that runs `pytest tests/design/` locally — which is CLAUDE.md's own recommended cheap pre-gate —
gets a pass, and only a resulting-tree gate (`tools.surgical_land`) or a fresh checkout sees the
red. This is the identical shape as
`WORKER_FINDING_298_SIMPLIFICATION_FILES_SIT_UNCOMMITTED_AND_THREE_ALREADY_DESYNC_THE_MAP_2026-08-14`,
which is the reason to treat the class as live rather than closed.

## How it got there, and the part worth generalising

The map's own committed comment says:

> 2026-08-29: the store file carried a third note ("CONSUMED -- the spine is now READ by a
> generator on a live run path") and this count was left at 2, so `test_counts_match_file_contents`
> was red for every lane in the tree. Bumped to match the register rather than the register
> trimmed to match it: **the note is real work another lane landed.**

The last clause is false at HEAD, and the error is not carelessness — it is a **census taken
against the wrong tree**. The author read the working tree, counted 3, and concluded the record
was landed. It was not, and neither is the work it describes:

| Artefact the record cites | State |
|---|---|
| `sim/scenario/gas_scenario_generator.py :: generate_gas_scenario_prices(spine=...)` | In HEAD **without** a `spine` parameter — signature is `(year_from, year_to, scenario, seed)` |
| `tests/sim/test_scenario_spine_consumption.py` (the record's 10 tests) | **Untracked** (`??`) — in no commit |
| `run_scenario.build_extended_price_feeds(world_id=)` | `world_id` appears nowhere in HEAD's `run_scenario` |

So a count was committed to describe content that was not. **A count is a claim about a
population, and it inherits the tree the population was counted in** — that is the durable
lesson, and it is the same one as the drawn item this was found under.

## Both obvious repairs are wrong, which is why this is filed rather than fixed

1. **Land the third record** (makes count=3 true). This would put into HEAD a record asserting
   "the spine is now READ by a generator on a live run path" while HEAD's generator has no such
   parameter and the tests are untracked. That is publishing a false claim to unwedge a gate —
   strictly worse than the red.
2. **Trim the map to 2** (also makes the counts agree, and IS true at HEAD — §0 refuses
   unauthorised `level_current` increases, not a count edit, so this was available). But the
   working tree holds 3 records, so trimming greens HEAD and turns the SHARED TREE red for the
   seat actively working that lane, and for everyone running the cheap pre-gate. It moves the
   wedge onto a live seat rather than removing it.

**The repair belongs to the spine lane and is one commit: the generator change, its 10 tests,
and the record, landed together.** That is the only move that makes the count true and the claim
true at the same time. Until then the count is ahead of its content in HEAD.

## Blast radius, measured rather than assumed

Not every lane. `tools/pre_commit_test_gate.tests_for` selects `tests/design/` only for pathspecs
whose name-stems reach it — this tick's own founder-book pathspec (8 paths across
`docs/design/` and `tests/simulation/`) selects only its own three test files and landed
unaffected. The wedge falls on any pathspec that DOES pull `tests/design/` in, which is how the
2026-08-14 instance was found: a commit of two unrelated orphaned files was refused by it.

## DISCHARGED 3ef0f6ecc (2026-08-29) — by the third repair, the one this finding named

`tests/design/` in a clean extract of HEAD: **1 failed, 113 passed → 114 passed.** The prediction
above was made before the answer and held: the repair was the spine lane's one commit — generator,
its tests, and the record, landed together — and neither rejected repair was used. The map was not
edited at all; `simplifications_count=3` was already in HEAD and became TRUE rather than being
trimmed to match a smaller store.

**What made it landable was the expiry of this finding's own premise, not a change of mind about
its reasoning.** Repair 2 was rejected because trimming "turns the SHARED TREE red for the seat
actively working that lane". The store file's mtime was 2026-08-28 14:47 — thirty-two hours before
the discharge. There was no seat actively working that lane, so holding the repair for its owner
was holding it for nobody, and a wedge with no owner is just a wedge. **The check worth repeating
is the mtime, not the argument:** "this belongs to another lane" has a shelf life, and this one had
expired without anything announcing it.

One thing this finding got right by luck rather than method, worth naming so the next pass does it
deliberately: it asserted the record's wiring claim was false at HEAD. It is — but a first grep for
`world_id` in `sim/scenario/run_scenario.py` returned nothing *because the module is
`simulation/run_scenario.py`*, a different package. Had that grep been the evidence, the conclusion
would have been right for the wrong reason and repair 1 would have looked correct (a record making
a claim no tree satisfied). The claim is satisfied in the working tree. **Two packages named
`sim/scenario/` and `simulation/` sit one letter apart here; a negative grep across them is not
evidence until the symbol is located positively somewhere.**

`tools/run_frozen_baseline.py` was left uncommitted on purpose — a different lane's
`figures_on_a_superseded_clock` repair, claimed by no line of the spine record.
