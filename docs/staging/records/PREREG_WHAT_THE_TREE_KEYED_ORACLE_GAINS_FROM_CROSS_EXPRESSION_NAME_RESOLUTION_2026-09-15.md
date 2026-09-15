# PREREG — what the TREE-keyed oracle gains when a destination is bound in TWO expressions

**Written 2026-09-15 by the delivery seat, BEFORE the population was counted or the matcher
changed.** Lane 0, claim
`the-tree-keyed-oracle-cannot-see-a-destination-whose-directory-and-filename-are-bound-in-two-expressions`.

This is the **seventh** frame on `tools/file_scope_generated_paths.py` and the **fourth** on the
tree-keyed half. The three before it paid **+8** (helper reach), **+9** (signature defaults), **+1**
(instance attribute) on the write-keyed half, and the tree-keyed half's own frames paid **+11**
(whole-string spelling), **-6** (ordered reconstruction, a subtraction), **-1** (glob patterns,
a subtraction). **The curve is the point**: each frame reaches further and each reaches less. A
frame that pays nothing is a result, not a failure, and this file exists so that result cannot be
rewritten afterwards.

---

## 1. The defect, stated so it can be wrong

`generated_artefacts()` resolves a `/`-chain **inside ONE assignment and no further**.
`_chain_segments` reads the chain in source order and stops at whatever stands at its head: a head
it cannot read is treated as the repo root and the literal tail is what gets matched.

That is exactly right for `PROJECT / "docs" / "observability" / "canon_drift.json"`. It is blind to
a module that splits the same destination across two statements:

```python
# tools/scale_probe_10k.py:119-121
ARTEFACT_DIR            = PROJECT / "docs" / "observability" / "scale_probe_10k"
REPORT_PATH             = ARTEFACT_DIR / "report.json"
PREDICTION_REGISTER_PATH = ARTEFACT_DIR / "prediction_register.json"
```

Neither expression alone names a path that is both under a declared tree AND an artefact:

- line 119 reconstructs to `docs/observability/scale_probe_10k` — under a declared tree, **no
  artefact suffix**, declined;
- lines 120–121 reconstruct to `report.json` / `prediction_register.json` — artefact-suffixed,
  **head is an opaque `ast.Name`**, so the tail is all there is and it does not start with a
  declared prefix, declined.

**MEASURED, not asserted** (this tree, 2026-09-15, before any change):

```
docs/observability/scale_probe_10k/prediction_register.json | tree-keyed: False | write-keyed: False
docs/observability/scale_probe_10k/report.json              | tree-keyed: True  | write-keyed: False
tree-keyed 215 · write-keyed 160 · union 253
```

**And `report.json`'s `True` is not this module's doing.** `tools/scale_probe_10k.py` — the actual
producer — contributes **nothing** to either oracle. `report.json` is in the union only because
`simulation/premise_population.py:1190` happens to spell the whole chain in one expression, as a
*reader*. So AO12's two tracked outputs are covered by an accident of how a third module reads one
of them, and the one no reader spells whole is offered a LANDING by
`origin_reconcile._split_generated`. That is the harm, and it is live.

## 2. What I am measuring

Thread a **name → segment-chain** map through `generated_artefacts()`, in source order, with
per-scope isolation, the way `_scope_path_names` already does it for the write-keyed half. Then
count:

- **N_add** — members added to `generated_artefacts()`.
- **N_tracked** — of those, how many `git ls-files` knows.
- **N_union** — the change in the union `origin_reconcile._split_generated` reads.
- **N_gate** — the change in `gate_violations()`.
- **N_flat** — members a FLAT (module-wide, unscoped) name map would add *beyond* the scoped one.
  This is the axes-defect probe: `_own_scope`'s docstring records that a module-wide map read a
  one-letter `p` from one function against a `p` bound to `DIRECTOR_AXES.md` in another and reported
  the director's own axes as generated. The item drawing this work asked explicitly whether the
  tree-keyed half can borrow the machinery without inheriting that defect. **N_flat is the number
  that answers it**, and it is measured rather than argued.

## 3. Predictions, written before the count

| # | Quantity | Prediction | Why |
|---|---|---|---|
| P1 | **N_add** | **2–12, point estimate 5** | The idiom needs a directory bound to a chain *under a declared tree* and re-joined elsewhere. `OBS = PROJECT / "docs" / "observability"` then `OBS / "x.json"` needs no sub-directory and feels common; the six-frame curve says the tail is thin. |
| P2 | **N_tracked** | **1–6, point estimate 3** | Past frames ran roughly 55–75% fictional (222→216 removed six, *all six* fictional; 167 of 222 on disk). A cross-expression destination is more likely to be a real one than a hard-joined one, so I expect a HIGHER hit rate here — but off a smaller base. |
| P3 | **N_gate** | **exactly 0** | Not a guess. `offends()` decides by tree PREFIX and every member this function can return is under one, so `s in generated` is subsumed. An ADDITION cannot move a subsumed test. If this is not 0 the subsumption claim in the docstring is false and that is the finding, not this one. |
| P4 | `prediction_register.json` in the additions | **yes** | It is the measured instance. If it is not, the mechanism I built is not the mechanism that blinds it. |
| P5 | **N_flat** | **≥1, ~50/50** | Genuinely uncertain. The write-keyed half hit the defect on one-letter names at *write sites*; the tree-keyed half only ever emits a path that starts with a declared prefix, which is a much narrower target for a fabrication. I will not know until I measure both. |
| P6 | `report.json` gained by the PRODUCER | **yes** | Today it arrives via a reader in `simulation/`. After this it should also arrive via `tools/scale_probe_10k.py` itself. It cannot move the count (already a member) — it is a claim about the *reason*, checkable and worth checking. |

## 4. What would refute the frame entirely

**N_add = 0.** Then the cross-expression idiom is not how this tree binds destinations under
declared trees, `prediction_register.json` is a singleton rather than a class, and the honest
outcome is to record that and NOT ship a resolver — a mechanism whose whole population is one path
is a mechanism nobody will maintain correctly. In that case the remedy is the one already in the
module's own vocabulary: name the path in the write-keyed oracle's terms, or accept it and say so.

**N_flat ≥ 1 with no scope fix available.** Then borrowing the machinery costs a fabrication and
the correct answer is to decline the borrow and say why, in the module, beside the code.

## 5. Done means

1. `generated_artefacts()` resolves a name bound to a `/`-chain in an earlier assignment **in the
   same scope**, with the same opaque-head/opaque-middle asymmetry `_chain_segments` already holds.
2. `docs/observability/scale_probe_10k/prediction_register.json` is in the oracle, therefore out of
   the reconciler's "somebody's WORK" half.
3. A control that goes **red** when cross-expression resolution is removed (mutation-proven, and the
   mutation named).
4. A control on the **scope isolation** whose fixture names **COLLIDE** — a scope-leak control
   passes with the defect installed unless the names are the same in both scopes.
5. Every number in §3 measured and written back **beside** the prediction, wrong or right.

---

## 6. THE RESULT, written back beside the predictions (2026-09-15, same day)

Full record:
`docs/staging/SEAT_FINDING_THE_TREE_KEYED_ORACLE_CANNOT_SEE_A_DESTINATION_WHOSE_DIRECTORY_AND_FILENAME_ARE_BOUND_IN_TWO_EXPRESSIONS_2026-09-15.md`.

| # | Predicted | **Measured** | |
|---|---|---|---|
| P1 | `N_add` 2–12, point 5 | **+12** (215 → 227) | in range, at the ceiling |
| P2 | `N_tracked` 1–6, point 3 | **8 of 12** | over |
| P3 | `N_gate` exactly 0 | **0** (0 → 0) | ✅ |
| P4 | register recovered | **yes** | ✅ |
| P5 | `N_flat` ≥1 | **0** | ❌ refuted |
| P6 | producer reaches its own outputs | **yes**, both | ✅ |

**AND EVERY ROW ABOVE IS THE WRONG QUANTITY, WHICH IS THIS FILE'S REAL RESULT.** §2 listed
`N_union` and then §3 predicted none of it — the table plotted the six-frame membership curve
instead. **The union moved 253 → 255: +2**, because ten of the twelve were already in the
write-keyed oracle on better evidence (they bind the directory and then WRITE through the name). One
of the remaining two is untracked dotfile state that never reaches the reconciler. **The whole harm
removed is ONE tracked file — `docs/observability/scale_probe_10k/prediction_register.json`, the
instance the frame was drawn for.**

§4 said `N_add = 0` would refute the frame. It did not fire, and a stricter version of it should
have: **`N_union` ≤ 2 was the refutation condition worth writing**, and on it this frame is exactly
at the line. It shipped because the one path it recovers is a tracked producer output that was being
offered a LANDING, which is the harm the module exists to prevent — not because twelve was a large
number.

P5's refutation is kept live rather than closed: zero flat-map fabrications today means the
tree-keyed half is safe by **accident**, not by construction, so the scoping is held by a fixture
whose two scopes bind the SAME name. A census over the live tree would be green with the scoping
deleted. The class-body variant of the same leak **was** real in the first draft of this commit and
its control caught it — also at zero cost on the live tree.
