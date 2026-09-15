# PREREG — what the write-keyed oracle gains from a `/` join whose RIGHT operand is a NAME

**Written 2026-09-15 by the delivery seat, BEFORE the post-change set was computed.** Lane 0,
continuing under claim `the-write-keyed-oracle-cannot-follow-a-path-into-an-instance-attribute`
because this door was found by that claim's own census, not by a new draw.

Fourth in the sequence: helper frame (+8), signature default (+9), instance attribute (+1, union
unmoved), and now this.

---

## 1. Why this one and not another

The instance-attribute turn ran a census of every write destination in
`tools/ background/ simulation/ saas/ company/` that resolves to ZERO paths — 364 of them — and the
result falsified that turn's own P6. The largest single cluster crosses no call frame at all:

| Shape | Count |
|---|---|
| **a `/` join whose RIGHT operand is a NAME, not a string literal** | **39** |
| a module-level `def`'s parameter with no default (needs cross-module reach) | 32 |
| `Path(args.something)` — a CLI argument, unknowable statically | 11 |
| `.with_name(...)` / `.with_suffix(...)` — the atomic-write temp | 11 |
| an attribute of a non-`self` object | 9 |

`_static_paths` accepts only `ast.Constant` on the right of a `/`:

```python
if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Div):
    right = node.right
    if not (isinstance(right, ast.Constant) and isinstance(right.value, str)):
        return []
```

so `out = root / DEFAULT_REPORT` (`tools/canon_drift_check.py:554`), where `DEFAULT_REPORT` is a
module-level **string** constant, resolves to nothing. This is the only remaining cluster the
resolver could reach without crossing a boundary it has deliberately refused to cross.

## 2. Baseline, measured before the change

- `_write_reached_paths()` — **165**.
- `written_artefacts()` — **158**.
- `generated_artefacts()` — **180**.
- The union `origin_reconcile` reads — **234**.

## 3. The change under test

A module-level (or scope-level) assignment whose value is a **string** `Constant` is recorded under
a dotted key `"str.<NAME>"` in the same `known` map, holding `Path(<the string>)`. The `/` branch of
`_static_paths` then accepts a `Name` on the right and joins each recorded relative path.

Dotted keys cannot collide with identifiers, which is the same property the instance-attribute
frame relies on, so the bare-name path map is untouched by construction.

**The existing refusals are unchanged.** The write SITE is still the key: a string constant is only
ever a right-hand segment, never a destination on its own, so a register a module merely names
cannot become a write.

## 4. Predictions, recorded before running any of them

| # | Prediction | Falsified by |
|---|---|---|
| Q1 | The raw set grows by **14, and I will accept 6–26**. Fewer than the 39 destinations because several resolve to the same artefact and several sit in modules whose base is itself unresolved. | A delta outside 6–26. |
| Q2 | `tools/canon_drift_check.py`'s report destination (`root / DEFAULT_REPORT`) is in the added set. | Absent. |
| Q3 | **The union DOES move this time** — unlike the instance-attribute frame, whose one path was already tree-keyed. At least 3 added paths are outside `generated_artefacts()`. | Fewer than 3 additions outside the tree-keyed set. |
| Q4 | Removals from the pre-change 165: **0**. This change only widens what resolves. | Any path present before and absent after. |
| Q5 | Every added path is attributable to a named module-level string constant and a named write site — **no addition is a path the module only reads**. | Any added path whose module never writes it. |
| Q6 | **At most two** additions need a `WRITTEN_BUT_NOT_REPRODUCIBLE` carve-out. | Three or more. |

Q5 is the rule, as in every prereg in this sequence: an addition is a path `origin_reconcile` will
start advising REVERT on, so a false positive costs a lane its work while a miss costs a warning.
**If Q5 fails the change does not land.** Q3 is what decides whether this frame was worth opening —
the previous one added a path and moved no consumer's answer, and that outcome is now a known
possibility rather than a surprise.

## 5. What done means

Every added path enumerated in the finding with its constant and its write site, each prediction
marked held or falsified beside itself, and — if Q5 fails on any path — the frame narrowed or
dropped rather than the prediction rewritten.
