**Severity:** LATENT · **Lane:** H_harness · **Epoch:** 3 · **Atom:** (Lane 0 delivery — `the-write-keyed-oracle-cannot-follow-a-path-into-an-instance-attribute`, continued from its own census)

# A `/` join with a NAME on the right is the one door BOTH generated-path oracles were blind to, and the first one whose additions the consumer can see

**Filed 2026-09-15, delivery seat.** Prereg:
`docs/staging/records/PREREG_WHAT_THE_WRITE_KEYED_ORACLE_GAINS_FROM_A_SLASH_JOIN_WITH_A_NAME_ON_THE_RIGHT_2026-09-15.md`,
written before the post-change set was computed. Fourth and last frame in the sequence: helper (+8),
signature default (+9), instance attribute (+1, union unmoved), named segment (**+4, union moves**).

Not a new draw. This door was found by the previous frame's own census, which falsified that
frame's prediction about where the next one would be.

---

## 1. What was wrong

`_static_paths` accepted only a literal on the right of a `/`:

```python
if not (isinstance(right, ast.Constant) and isinstance(right.value, str)):
    return []
```

so `out = root / DEFAULT_REPORT`, where `DEFAULT_REPORT = "docs/observability/canon_drift.json"` is
a module-level **string** constant, resolved to nothing. 39 of the 364 unresolved write destinations
in this tree were that shape — the largest single cluster, and the only one reachable without
crossing a boundary the module has deliberately refused to cross (another module's parse, a second
call frame).

## 2. The predictions, each marked

| # | Prediction | Result |
|---|---|---|
| Q1 | Raw set grows by 14, accepting 6–26. | **FALSIFIED.** It grew by **4** (165 → 169). 39 destinations, 4 artefacts: most of the cluster is several destinations in one module joining onto the same constant, or joining onto a base that is itself a CLI argument. **Destination count is not path count, and I keyed the prediction to the wrong unit.** |
| Q2 | `canon_drift_check.py`'s `root / DEFAULT_REPORT` is in the added set. | **HELD.** |
| Q3 | The union `origin_reconcile` reads MOVES, with ≥3 additions outside the tree-keyed set. | **HELD, and it is the result of the whole sequence.** All 4 additions are outside `generated_artefacts()`. Union **234 → 237** after the carve-out. |
| Q4 | 0 removals from the pre-change 165. | **HELD.** |
| Q5 | Every added path attributable to a named constant and a named write site. | **HELD for all four** — §3. |
| Q6 | At most two additions need a carve-out. | **HELD.** Exactly one, and it matters — §4. |

## 3. The four additions, attributed

| Path | Constant | Write site |
|---|---|---|
| `docs/observability/canon_drift.json` | `tools/canon_drift_check.py:111` `DEFAULT_REPORT = "docs/observability/canon_drift.json"` | `:554` `out = root / DEFAULT_REPORT` → `out.write_text(json.dumps(report))` |
| `docs/staging/reference/HEAD_RED_REGISTER.md` | `background/head_red_register.py:65` `REGISTER_NAME = "HEAD_RED_REGISTER.md"` (`:66` joins it onto the tree) | `:391` `p = path or REGISTER_PATH` → `:393` `p.write_text(render(store, accepted))` |
| `docs/staging/reference/PUBLISH_STANDING_RED_REGISTER.md` | `background/publish_standing_red.py:58` `REGISTER_NAME = …` | `:338` `p = path or REGISTER_PATH` → `:340` `p.write_text(render(ledger, …))` |
| `docs/design/ORPHAN_DISPOSITION_REGISTER.md` | `tools/capability_index.py:905` `DISPOSITION_REGISTER = "docs/design/ORPHAN_DISPOSITION_REGISTER.md"` | `:1288` `path = ROOT / DISPOSITION_REGISTER` → `:1295` `path.write_text(after)` |

The two standing-red registers are rendered whole from a JSON ledger beside them, so a re-run
reproduces them exactly — the cheap-revert property the whole classification rests on.

**`docs/observability/canon_drift.json` is the sharpest of the four**, because it shows the two
oracles going blind to one path for opposite reasons. It lives under `docs/observability`, a
`GENERATED_TREES` member, so the tree-keyed oracle ought to have had it — but that oracle needs
`"docs"` and `"observability"` as **separate** string constants in one assignment, and the module
spells the whole path as a single string. A segment-pair scan and a pathlib-expression scan can each
be blind to the same artefact.

## 4. One addition would have done real harm, and attribution is what caught it

`docs/design/ORPHAN_DISPOSITION_REGISTER.md` passes the write-site test honestly —
`path.write_text(after)` is a real write. It is still a **human ruling**. The document says so of
itself, in bold:

> **There is deliberately no generator.** A new orphan must be ruled on by a judgement.

`render_dispositions`'s own docstring: it rewrites ONE derived consumer column, *"never adds a row
and never removes one"*. The remedy a consumer applies to a generated path is REVERT, and a revert
would drop whatever rulings another lane wrote — on a document the director reads. It is carved out
into `WRITTEN_BUT_NOT_REPRODUCIBLE` with that reasoning beside it, and
`test_a_HUMAN_RULING_a_tool_renders_ONE_COLUMN_of_is_not_a_photograph_of_a_run` reds if anyone
deletes the entry because the scan "obviously" found a write.

This is the `ASSUMPTIONS.md` shape arriving through a new door, and **it is the first addition in
four frames that would have destroyed work rather than merely over-warned.** Q5 — attribute every
added path, every time — is the only thing between this frame and that outcome, and it is why every
prereg in this sequence makes it the rule that decides landing.

## 5. What landed

`tools/file_scope_generated_paths.py`

- `_scope_path_names` records a **string** constant under a `"str.<NAME>"` key; `_static_paths`
  accepts a `Name` on the right of a `/` and joins each recorded segment.
- **The namespaces are separate in the direction that matters, and the other direction is recorded
  as an equivalence rather than dressed as a guard.** A `"str."` key is consulted ONLY as a
  right-hand segment, so a module's `REGISTER_REL = "docs/design/SOMETHING.md"` can never become a
  destination on its own — that asymmetry is the oracle. Merging the maps so a PATH-valued name
  could stand as a segment would change nothing the scan reports, because every path
  `_static_paths` produces is absolute and `p / <absolute>` is that absolute path. Established by
  trying to write the mutation and failing to make it fire.
- The `ClassDef` entry now drops only the `self.` half of the dotted map. A segment constant is a
  module global and a method sees it as any function beside it does; stripping it would make a
  class's methods blinder than the module around them — blind in the direction that HIDES a
  generated path, which is the failure nothing ever goes red for.

`tests/tools/test_a_generated_path_in_an_authored_tree_is_still_generated.py` — two fixtures and
two real-tree legs, each mutation-proven:

| Mutation | Legs it reds |
|---|---|
| N1 named segments never read | all four |
| N2 the `ClassDef` entry strips the segment map too | the class-survival leg only |
| N3 the human-ruling carve-out deleted | the carve-out leg only |

## 6. Where the sequence now stands

| Frame | Paths added | Union moved? |
|---|---|---|
| helper, one frame down | +8 | — |
| signature default | +9 | — |
| instance attribute | +1 | **no** |
| named segment | +4 | **yes, 234 → 237** |

**What is left, with counts rather than a prediction**, from the census in the previous finding:

1. **32** destinations are a module-level `def`'s parameter with **no** default — reachable only
   from a call site in another module. That is the cross-module frame the docstring has refused
   three times, and it is now the largest remaining cluster. It needs the other module's parse and
   its name resolution; it is a real piece of work, not a widening.
2. **11** are `Path(args.something)` — a CLI argument, unknowable statically. Not a door.
3. **11** are `.with_name(…)` / `.with_suffix(…)` — the atomic-write temp file, which is the
   destination's *neighbour* and not the destination. Resolving them would add `.tmp` siblings, not
   artefacts.
4. **9** are an attribute of a non-`self` object (`spec.subject_path`) — needs the other object's
   type, which this resolver does not track.

**And a door outside the write-keyed oracle entirely, found in passing:** the TREE-keyed oracle
misses any artefact whose path is spelled as one whole string rather than a segment join.
`canon_drift.json` is one live instance; nobody has counted the rest. That is a cheaper fix than
the cross-module frame and it is in the gate-blocking oracle rather than the advisory one.
