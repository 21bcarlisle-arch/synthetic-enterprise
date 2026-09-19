**Severity:** LATENT · **Lane:** H_harness · **Epoch:** 3 · **Atom:** (Lane 0 delivery — `the-write-keyed-oracle-cannot-follow-a-path-into-an-instance-attribute`)

# The instance-attribute door is one path wide, the path was already classified generated, and the door that is actually open is a `/` join with a NAME on the right

**Filed 2026-09-15, delivery seat.** Prereg:
`docs/staging/records/PREREG_WHAT_THE_WRITE_KEYED_ORACLE_GAINS_FROM_AN_INSTANCE_ATTRIBUTE_DESTINATION_2026-09-15.md`,
written before any of P1–P6 was run. Third in the sequence after the helper frame (+8) and the
signature default (+9).

---

## 1. The drawn item's stated consequence was false

The item said of `site/data/publish_steps.json`:

> …so that artefact is still classified AUTHORED and `origin_reconcile` still offers to land it.

It is not, and it does not. `background/origin_reconcile._split_generated` reads **both** oracles
and unions them (`for name in ("generated_artefacts", "written_artefacts"): known |= …`). The path
lives under `site/data/`, one of `GENERATED_TREES`, and `background/publish_step_ledger.py:83`
carries `LEDGER_PATH = PROJECT_DIR / "site" / "data" / "publish_steps.json"` — the exact
segment-pair assignment the **tree-keyed** oracle was built to read.

| | |
|---|---|
| In `written_artefacts()` before this change | No |
| In `generated_artefacts()` before this change | **Yes** |
| In the union `origin_reconcile` actually reads | **Yes** |

The half of the premise that was true: the write-keyed oracle genuinely could not follow this
destination. What was false was the consequence — **no consumer was getting a wrong answer about
this path.** This is the same shape as yesterday's `self._write(...)` item (0 instances) one rung
along: a docstring's "still out" list is a prediction about the tree that nobody re-asked, and an
item built on it inherits the staleness.

## 2. The population, measured with the module's own AST helpers rather than a substring probe

Over `tools/ background/ simulation/ saas/ company/`:

| Question | Answer |
|---|---|
| Classes | 2,058 |
| `(class, method)` pairs whose own scope holds a write destination | 8, across 7 classes |
| …whose destination expression **or a local in the same method** touches `self.<attr>` | 2 |
| …whose attribute has exactly ONE `self.X =` store site in the class | **1** |

The one is `PublishStepLedger.write`. The other is `PriceFeed.is_stale`, whose "destination" is the
`'+00:00'` of a `str.replace` — the filter-not-safety case the module already documents — and whose
`self._data` has three store sites, so the rebound guard refuses it independently.

**Eight, then nine, then one.** That curve is the finding, not the path.

## 3. The predictions, each marked

| # | Prediction | Result |
|---|---|---|
| P1 | Raw set grows by exactly 1: `site/data/publish_steps.json`. | **HELD.** 164 → 165, added `['site/data/publish_steps.json']`, removed `[]`. |
| P2 | The union `origin_reconcile` reads does not move — still 234. | **HELD.** 180 tree-keyed ∪ 158 write-keyed = **234**, unchanged. |
| P3 | The addition needs no `WRITTEN_BUT_NOT_REPRODUCIBLE` carve-out. | **HELD, but the REASON given in the prereg was wrong** — see §4. |
| P4 | Guard B removes 0 paths from the pre-change 164. | **HELD.** Removed: `[]`. |
| P5 | Every added path attributable to a named `__init__` assignment and a named method. | **HELD.** `publish_step_ledger.py:128` binds `self.project_dir`; `:213` falls back through it; `process_run_complete.py:3963` constructs with no `project_dir` and `:4525` calls `_ledger.write()` bare. |
| P6 | The largest remaining cluster is a destination that crosses a CALL. | **FALSIFIED** — see §5. |

## 4. P3 held on a reason the prereg got wrong, and the correction belongs beside it

The prereg justified "no carve-out" with *"the next publish rewrites it whole"*. **It does not.**
`PublishStepLedger._read_previous` reads the existing ledger and `_last_ok_stamp` carries
`last_ok_run_stamp` forward for any step that failed this cycle — a read-modify-rewrite, which is
exactly the *append wearing a rewrite's clothes* shape that put three paths on the carve-out list
during the defaults frame.

It still does not earn a carve-out, on a different argument:

- A revert does not destroy the chain, it regresses it. HEAD's copy carries its own, older,
  self-consistent stamps, and the next publish carries forward from whatever is on disk. The cost
  is a ledger **understating** how recently a step was last real — a degraded reading, not an
  unrecoverable purchase like the HaDUK receipt's 10 GB or a person's supplied evidence.
- The carve-out would be **inert**: the tree-keyed oracle already classifies the path generated and
  the consumer unions, so subtracting it here changes nothing a reader sees — while making the two
  oracles disagree about a path sitting in `site/data/`.

## 5. P6 falsified, and the door that IS open, with a count

Census of every write destination in the scanned trees that resolves to **zero** paths — 364 of
them:

| Shape | Count |
|---|---|
| a bare NAME the resolver could not follow | **174** |
| a string/constant literal (`str.replace` etc. — noise, by design) | 134 |
| an attribute of something other than `self` | 22 |
| a call result | 15 |
| a `/` join on an unresolved base | 15 |
| f-string | 4 |
| **`self.<attr>`, unresolved** | **0** |

Zero unresolved `self.<attr>` destinations remain: the frame is complete for its shape. Splitting
the 174 bare names by where they come from:

| | Count |
|---|---|
| a LOCAL assigned from an expression the resolver declines | **124** |
| a module-level `def`'s parameter with **no** default | 32 |
| a module-level `def`'s parameter whose default resolves to nothing | 14 |
| a module/class-body local | 3 |
| a METHOD parameter with no default | 1 |

And splitting the 124 by the shape of the expression that binds them:

| | Count | Live example |
|---|---|---|
| **a `/` join whose RIGHT operand is a NAME, not a string literal** | **39** | `tools/canon_drift_check.py:554` `out = root / DEFAULT_REPORT` |
| `Path(args.something)` — a CLI argument | 11 | `tools/fold_noise_floor_family.py:310` |
| an attribute of a non-`self` object | 9 | `tools/contract_battery.py:1040` `subject = spec.subject_path` |
| `.with_name(...)` / `.with_suffix(...)` — the atomic-write temp | 11 | `background/seat_continuity.py:182` |
| a choice over a parameter | 4 | `background/head_red_register.py:393` `p = path or REGISTER_PATH` |

**The largest single remaining cluster crosses no call at all.** `_static_paths` accepts only
`ast.Constant` on the right of a `/`:

```python
if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Div):
    right = node.right
    if not (isinstance(right, ast.Constant) and isinstance(right.value, str)):
        return []
```

so `root / DEFAULT_REPORT`, where `DEFAULT_REPORT` is a module-level **string** constant, resolves
to nothing. A string-valued name map is a strictly smaller change than any of the three frames
built so far and has 39 destinations behind it — against this frame's one. P6 predicted a call
shape and was wrong in the direction that matters: **the next door does not need a new frame, it
needs the resolver to read one more kind of constant.**

## 6. What landed

`tools/file_scope_generated_paths.py`

- `_class_self_paths` — `"self.<attr>" -> paths` for one class, from the class body's own
  assignments and from each method's `self.X = <path expression>`, each resolved in the scope
  Python evaluates it in.
- `_static_paths` resolves `ast.Attribute` on the bare receiver `self` against a **dotted** key. A
  dotted key cannot collide with any Python identifier, so the bare-name map is untouched by
  construction rather than by care.
- **Guard A** — an attribute with more than one store site anywhere in the class subtree is dropped
  whole, counting store sites this resolver cannot see (a closure, a `for`, a nested class), so an
  attribute it cannot fully read fails toward silence.
- **Guard B** — the class body's bare names still do not answer a method's bare names. The dotted
  map rides alongside `inherited`, not inside `known`.
- Two guards deliberately **not** built, and both because they measured zero and this project does
  not build a control that cannot fail: a bare-`self` rebinding refusal (0 scopes in the tree store
  `self`) and a nested-class strip as a *measured* guard (0 class-in-class definitions — it is
  written as correctness-by-construction and says so).

`tests/tools/test_a_generated_path_in_an_authored_tree_is_still_generated.py` — five fixtures and a
real-tree poison round, each mutation-proven:

| Mutation | Legs it reds |
|---|---|
| M1 dotted map never handed down | init-binding, local-and-choice, class-body, own-method, real-tree |
| M2 rebound guard removed | rebound-refused-whole |
| M3 guard B undone | class-body dotted-vs-bare |
| M4 flat map over every method | own-method |

The real-tree leg carries **no `len(gained) > 1` floor**, unlike its two neighbours, and says why in
its docstring: asserting a floor of two would be asserting a population this turn measured and
found to be one.

## 7. What is next

1. **The `/`-join-with-a-NAME frame — 39 destinations.** Resolve a `Name` on the right of a `/` to
   a module-level string constant. Same safety rule as every frame here: every added path
   attributed, because an addition is one `origin_reconcile` will advise REVERT on.
2. Before opening it, **re-ask whether each added path is already in the tree-keyed set**. That
   question is what would have retired this item in five minutes, and it was not asked for three
   frames running.
