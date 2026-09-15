# PREREG — what the write-keyed oracle gains from following a destination into an INSTANCE ATTRIBUTE

**Written 2026-09-15 by the delivery seat.** Lane 0, claim
`the-write-keyed-oracle-cannot-follow-a-path-into-an-instance-attribute`.

Third in the sequence that began with
`SEAT_PREREGISTRATION_WHAT_ONE_FRAME_OF_INTERPROCEDURAL_REACH_ADDS_TO_THE_WRITE_KEYED_ORACLE_2026-09-15.md`
(the helper frame, +8) and continued with
`PREREG_WHAT_THE_WRITE_KEYED_ORACLE_GAINS_FROM_A_DEFAULTED_DESTINATION_PARAMETER_2026-09-15.md`
(the signature default, +9).

**What was measured BEFORE this file was written, and is therefore stated as baseline and not as a
prediction:** the three set sizes below, and the instance-attribute population census. **What was
NOT known when this file was written:** every prediction in the table, and the residual-shape census
in §5. The structural population count is cheap and unfalsifiable-by-me once run, so it is recorded
honestly as a measurement rather than dressed as a forecast.

---

## 1. The drawn item's stated consequence is FALSE, and that is the first finding

The item says of `site/data/publish_steps.json`:

> …so that artefact is still classified AUTHORED and `origin_reconcile` still offers to land it.

Asked of the tree at `c9769d426`:

| Question | Answer |
|---|---|
| `written_artefacts()` — the write-keyed oracle — contains it? | **No** |
| `generated_artefacts()` — the tree-keyed oracle — contains it? | **YES** |
| `origin_reconcile._split_generated` reads which of the two? | **BOTH, unioned** (`for name in ("generated_artefacts", "written_artefacts")`, `known |= …`) |
| So is it classified authored, and offered a landing? | **No. It is classified generated already.** |

The path lives under `site/data/`, which is one of `GENERATED_TREES`, and
`background/publish_step_ledger.py:83` carries a module-level
`LEDGER_PATH = PROJECT_DIR / "site" / "data" / "publish_steps.json"` — exactly the segment-pair
assignment the tree-keyed oracle was built to read. The write-keyed oracle misses it; the union
does not.

The half of the premise that IS true: the write-keyed oracle genuinely cannot follow this
destination, for exactly the reason given, and the "STILL OUT" list in `written_artefacts`'s
docstring names it as an open door. What is false is the consequence attached to it. **No consumer
is getting a wrong answer about this path today.**

## 2. The population, measured

Over `tools/ background/ simulation/ saas/ company/`, using the module's own `_own_scope` and
`_write_destinations` rather than a substring probe:

| Question | Answer |
|---|---|
| Classes | 2,058 |
| `(class, method)` pairs whose own scope holds a write destination | **8**, across **7** classes |
| …of those 8, pairs where the destination expression OR a local assigned in the same method touches `self.<attr>` | **2** |
| …of those 2, pairs where the attribute has exactly ONE `self.X = …` store site in the class | **1** |

The one: `PublishStepLedger.write`, where `target = Path(path) if path else (self.project_dir /
"site" / "data" / "publish_steps.json")` and `__init__` binds
`self.project_dir = Path(project_dir) if project_dir else PROJECT_DIR`.

The other: `PriceFeed.is_stale`, whose "destination" is the `'+00:00'` of a `str.replace` — the
filter-not-safety case the module already documents — and whose `self._data` has three store sites,
so the rebound guard refuses it independently.

Five of the remaining six pairs are the same `str.replace` shape. The sixth,
`PublishStepLedger._commit_state`, writes `state_path`, which its ENCLOSING method binds from
`self._state_path()` — a method CALL, a different door, and recorded in §5 rather than built here.

**So the frame under test has exactly one live instance.** Not zero, which is what stopped the
`self._write(...)` frame being built yesterday; and not the eight or nine of the two frames before
it. This prereg exists because "one" is the number that decides whether to build, and it should be
on the page before the result is.

## 3. Baseline, measured before the change

- `_write_reached_paths()` — **164** repo-relative paths.
- `written_artefacts()` (after the `WRITTEN_BUT_NOT_REPRODUCIBLE` carve-out) — **157**.
- `generated_artefacts()` — **180**.
- The union the consumer actually reads — **234**.

## 4. The change under test

1. `_static_paths` resolves an `ast.Attribute` whose value is the bare name `self`, against a map
   keyed `"self.<attr>"`. A dotted key cannot collide with any Python identifier, so the existing
   bare-name map is untouched by construction.
2. That map is built per `ClassDef` from the class body's own assignments and from each method's
   `self.X = <path expression>`, each resolved against what the CLASS inherited (module scope) —
   never against a sibling method's locals.
3. **Guard A, a REBOUND attribute is refused.** An attribute with more than one `self.X` store site
   anywhere in the class subtree is dropped, for the reason `_module_helpers` and
   `_default_destinations` refuse a rebound parameter: after a second binding the write need not go
   where the first one said.
4. **Guard B, the class body's bare names still do not reach a method.** The dotted map is handed
   down where `handed_down = inherited if isinstance(node, ast.ClassDef) else known` already runs;
   the bare-name half of that line is unchanged. A nested `ClassDef` starts a fresh dotted map, and
   a nested scope that shadows `self` in its own signature loses the dotted keys — the same
   shadow-stripping leg that landed with the defaults frame, extended to the dotted half.

## 5. Predictions, recorded before running any of them

| # | Prediction | Falsified by |
|---|---|---|
| P1 | The raw set grows by **exactly 1**: `site/data/publish_steps.json`. | Any other count, or any other path. |
| P2 | The **union that `origin_reconcile` reads does not move at all** — still 234. This change makes the write-keyed oracle more honest and changes no consumer's answer on today's tree, and that is stated here so the result cannot later be read as a fix to a live defect. | The union changing size. |
| P3 | The addition needs **no** `WRITTEN_BUT_NOT_REPRODUCIBLE` carve-out: `publish_steps.json` is a per-cycle report of which publish steps refreshed which artefacts, and the next publish rewrites it whole. | The path being a record a run cannot reproduce. |
| P4 | Guard B removes **0** paths from the pre-change 164. | Any path present before and absent after. |
| P5 | Every added path is attributable to a named `__init__` assignment and a named method — **no addition is a path the module only reads**. | Any added path whose module never writes it. |
| P6 | A census of write-destination expressions that resolve to ZERO paths will show the **largest single remaining cluster is a call to something that is not a same-module writing `def`** — a method call (`self._state_path()`), an imported helper, or a factory — rather than any further NAME-resolution shape. | The largest cluster being a name/attribute shape the resolver could reach without crossing a call. |

P5 is still the one that matters: an addition is a path `origin_reconcile` will start advising
REVERT on. P2 is the one that decides what this turn is worth.

## 6. What done means

- The frame is built with both guards, or it is not built and the census in §5/P6 is the
  deliverable instead.
- P1–P5 are answered in a landed finding, each marked held or falsified beside the prediction.
- The "STILL OUT" list in `written_artefacts`'s docstring no longer names the instance attribute as
  an open door, and the docstring says what the door was actually worth.
- The census (P6) names the next frame **with a count**, so the next session is not told to open a
  door on a prediction nobody re-asked. That is the failure this sequence has now hit twice: the
  `self._write(...)` door (0 instances) and this item's stated consequence (already classified).
