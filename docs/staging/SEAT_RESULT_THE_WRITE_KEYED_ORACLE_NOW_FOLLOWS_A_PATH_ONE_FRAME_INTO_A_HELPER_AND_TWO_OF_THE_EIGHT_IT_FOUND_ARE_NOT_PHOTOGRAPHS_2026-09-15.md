**Severity:** LATENT · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0 delivery, the
generated-path oracle

# The write-keyed oracle now follows a path one frame into a helper, and two of the eight it found are not photographs

**Filed 2026-09-15 by the delivery seat**, holding
`teach-the-write-keyed-oracle-to-follow-a-path-into-a-helper`. It closes the gap that
`SEAT_RESULT_THE_GENERATED_PATH_ORACLE_NOW_KEYS_ON_WRITING_A_PATH_AND_NOT_ON_NAMING_ONE_2026-09-15.md`
named in its own docstring on the day it landed.

Prediction filed before the measurement:
`docs/staging/records/SEAT_PREREGISTRATION_WHAT_ONE_FRAME_OF_INTERPROCEDURAL_REACH_ADDS_TO_THE_WRITE_KEYED_ORACLE_2026-09-15.md`.

## What was wrong

`written_artefacts()` demands a write SITE the constant reaches — that asymmetry is what stops a
naming-keyed classifier marking a register generated and advising a lane to REVERT its real work.
But the scan could only see a write in the same scope the constant resolves in, so it said of
itself:

> THE NAMED GAP. A path handed to a helper (`_write_json(BASELINE_PATH, data)`) and written one
> frame down is NOT found.

Every producer that factors its write into a `_write`-shaped helper was therefore still classified
**authored**, and `origin_reconcile._split_generated` still led its refusal with the recipe for
LANDING that producer's output — the exact defect the write-site key was built to end, surviving in
whatever fraction of producers use a helper. It degrades in the SAFE direction, so nothing reported
it and nothing would have.

## What was done

`_module_helpers` records every module-level `def` that writes; a call binds its arguments to those
parameters by position and by keyword, and the helper's write destination is re-resolved under that
binding by the same `_scope_path_names` + `_static_paths` the helper's own scope already gets. So
`path.write_text(...)`, `Path(path).write_text(...)`, `(path / "f.json").write_text(...)` and
`dest = path / "f.json"` all follow without enumerating the write shapes twice.

**Four things stay out, each on purpose rather than by omission:** a helper in another module; a
helper reached through two frames (the binding does not travel, so this is structural, not a depth
counter); a method called as `self._write(...)`; and a parameter **rebound** inside the helper,
because after `path = DEFAULT` the write no longer goes where the caller said and following it
anyway *manufactures* a path. All four degrade the way the whole gap used to.

One place is deliberately **stricter** than the scan around it. A write destination is structurally
a path expression, so walking it for any known name is safe; an **argument** is an arbitrary
expression, and walking `_save(derive(REGISTER))` for names would report a register this module only
reads — the naming-keyed misclassification arriving one frame down instead of at the top. Arguments
are resolved by `_static_paths` alone. Missing a path costs a warning; claiming one costs a lane's
work.

## The measurement

| | before | after |
|---|---|---|
| raw write-reached | 147 | **155** |
| carve-out (`WRITTEN_BUT_NOT_REPRODUCIBLE`) | 2 | **4** |
| `written_artefacts()` — what the reconciler consumes | 145 | **151** |
| residue the tree-keyed oracle cannot see | — | 50 |

**Eight paths added, zero removed** — inside the predicted 2–40 band, and the prediction that the
addition would be small held. Seven producers, every one of them factoring its write into a helper:

| added path | producer | helper | verdict |
|---|---|---|---|
| `docs/observability/run_rotation_cursor.json` | `background/run_rotation.py` | `_write_index` | generated |
| `docs/observability/.resource_headroom_episode.json` | `background/resource_headroom.py` | `_write_json` | generated |
| `docs/observability/.heavy_job_reservations.json` | `background/resource_headroom.py` | `_write_json` | generated |
| `docs/observability/gate_x_premium_rss.json` | `tools/sample_gate_rss_premium.py` | `_write` | generated |
| `docs/observability/.tree.lock` | `background/tree_lock.py` | `_acquire_flock` | generated (untracked) |
| `docs/reports/c2_departure_factors.json` | `tools/capture_departure_factors.py` | `main(out_path)` | generated |
| `docs/market_research/ASSUMPTIONS.md` | `background/discovery_agent.py` | `_update_last_checked` | **NOT a photograph** |
| `docs/observability/naive_organ_log.jsonl` | `background/naive_organ.py` | `_rewrite_log` | **NOT a photograph** |

Each was checked by reading the helper and the call site, not by trusting the resolver — prediction
(3). No path the tree authors was added by a new route; `maturity_map.yaml`, `DIRECTOR_CANON.md` and
`WALL_CROSSING_DISPOSITION_REGISTER.md` are all absent from the addition — prediction (4).

## The finding the frame surfaced: writing is still not sufficient, twice over

Six of the eight are photographs of a run. **Two are not, and they are a class the mode check cannot
see.**

`background/discovery_agent._update_last_checked` reads `ASSUMPTIONS.md`, regex-substitutes ONE date
line, and writes it back. The file says of itself: *"Updated by discovery agent and manually when
phases change assumptions."* A daemon touching one line does not make the hand-written anchor rows
below it reproducible.

`background/naive_organ._rewrite_log` rewrites the answered-question ledger **whole** — so it passes
`WRITING_MODE_CHARS` where an `"a"` append would have been excluded. But the exclusion of append was
never about the mode; it is about *a record no run can reproduce*, and this is that record:
`answer_organ_question` stores an answer and its fetchable evidence refs, supplied by a person and
refused if empty. **A read-modify-rewrite of an accumulated ledger is an append wearing a rewrite's
clothes, and the mode check cannot tell them apart.** `WRITTEN_BUT_NOT_REPRODUCIBLE` is where that
distinction actually gets made, and it now has four members instead of two.

Neither path was write-reached before this change, so neither could have been carved out before it.
The frame found them; the judgement about them is a separate question from finding them, and both
are held on the safe side — classified authored, offered a landing.

## Controls

Eight new legs in `tests/tools/test_a_generated_path_in_an_authored_tree_is_still_generated.py`,
every one with its partner on the naming side of the boundary. Mutation-proven, not assumed:

| mutation | legs that go red |
|---|---|
| frame removed entirely | 9, incl. the pre-existing carve-out leg |
| rebound-parameter check removed | rebound leg |
| argument bound to parameter 0 instead of its position | position leg |
| helper inherits the CALLER's names | scope leg |
| arguments resolved by name-walk as well | strictness leg |
| keyword binding removed | keyword leg |

Two legs needed repairing before they were controls at all, and both are recorded in the test file
beside the leg rather than quietly fixed:

- **the scope leg passed with the leak installed.** The call bound nothing, so the resolver took its
  `if not bound: return` exit and never consulted the inherited map on *either* side of the
  mutation — a control measuring an early return. It needed a second parameter that *does* bind, so
  the leak is reached and the colliding name can fire. (The same R15 shape as the class-body leg
  above it: *the names must meet*.)
- **the two-frames leg would have passed with the whole frame dead.** Both halves now live in one
  fixture — `SHALLOW` goes one frame and must be found, `DEEP` goes two and must not — and `_outer`
  is a real helper, so the question asked is "does the frame recurse" rather than "is `_outer` a
  helper at all".

`test_the_helper_frame_is_LOAD_BEARING_in_the_REAL_tree` is the poison round: it removes the frame
from the live scan and measures what disappears, keyed to the property rather than to today's count,
so a producer later refactored to write its constant directly turns it green on a smaller set rather
than red on a number.

## What is next

- **The method door is the biggest one left.** `self._write(...)` is not followed, and this tree has
  class-shaped producers. The binding machinery is now there; what it needs is resolving the callee
  within the enclosing `ClassDef` — and the class-body scoping rule right above it says exactly why
  that cannot be done by adding methods to the module-level table.
- **Cross-module helpers** need another module's parse and name resolution. Larger, and out until
  something shows it matters.
- **Is the carve-out's boundary the right one?** Four members now, two found in one afternoon, and
  the rule that separates them from the other 151 is prose in a comment rather than a predicate. If
  a fifth arrives the same way, that is the signal to ask whether "reproducible by a run" can be
  made checkable instead of enumerated.
