**Severity:** LATENT · **Lane:** H_harness · **Epoch:** 3 · **Atom:** (Lane 0 delivery — `the-tree-keyed-generated-oracle-is-blind-to-a-path-spelled-as-one-whole-string`)

# The tree-keyed oracle could not read a path spelled as ONE STRING — and the consequence was in the RECONCILER, not in the gate the draw named

**Filed 2026-09-15, delivery seat.** Prereg, written before the population was counted or the
matcher changed:
`docs/staging/records/PREREG_WHAT_THE_TREE_KEYED_ORACLE_GAINS_FROM_A_PATH_SPELLED_AS_ONE_WHOLE_STRING_2026-09-15.md`.

First frame on the **tree-keyed** oracle. The four before it were on its write-keyed sibling
(helper +8, signature default +9, instance attribute +1, named segment +4) and this door was found
in passing by the last of them.

---

## 1. What was wrong

`generated_artefacts()` matched a `(parent, child)` **segment pair** — `docs` and `observability`
as separate string constants inside one assignment, which is how a generator usually builds a path:
`PROJECT / "docs" / "observability" / "canon_drift.json"`. A module that spells the whole thing as
one string was invisible:

```python
DEFAULT_REPORT = "docs/observability/canon_drift.json"   # tools/canon_drift_check.py:111
```

The artefact sits squarely inside a `GENERATED_TREES` member and the matcher could not name it.
**Eleven** artefacts in this tree are spelled that way.

## 2. The predictions, each marked

| # | Prediction | Result |
|---|---|---|
| Q1 | `WHOLE` (every whole-string match in an assignment) has 14 members, accepting 5–30. | **FALSIFIED.** 33. Excluding the oracle's own source — an exclusion that did not exist when the prediction was written, see §4 — it is 29, inside the band. Marked falsified on the terms actually written. |
| Q2 | `WHOLE − generated_artefacts()` is 9, accepting 3–20. | **HELD.** 15 raw, **11** after the self-exclusion. Both inside the band. |
| Q3 | `docs/observability/canon_drift.json` is in the difference. | **HELD.** |
| Q4 | The gate verdict does not move, and *cannot*: `offends()` decides by tree PREFIX and every member the oracle can return is under one, so `s in generated` is subsumed. | **HELD, and it is the most useful answer here.** `gate_violations() == []` before and after; **0 of 191** members escape the prefix test. See §3. |
| Q5 | The union moves, by strictly fewer than Q2, with ≥2 paths neither oracle had. | **HELD.** Union **237 → 247**. `canon_drift.json` was already in the union via `written_artefacts`, so 11 additions to the oracle bought 10 to the union. |
| Q6 | 0 additions need a `WRITTEN_BUT_NOT_REPRODUCIBLE`-shaped carve-out. | **HELD.** Every addition is inside a generated tree, where a photograph of a run is the premise. |
| Q7 | Widening to every string constant (not only assignments) adds ≤3 further. | **FALSIFIED.** It adds 10. The breakdown is what makes the scope a decision rather than an inheritance — §5. |

## 3. The drawn item's stated consequence was FALSE, and that is the finding

The draw said: *"a path it cannot see is a file_scope entry that silently starves its atom — the
exact eight-day G13 defect."* It is not. `offends()` is:

```python
bare = s.rstrip("/")
return bare in prefixes or any(bare.startswith(p + "/") for p in prefixes)
```

— a PREFIX test over `site/data`, `docs/observability`, `docs/market_data`, taken without
consulting the generated set at all. Every path `generated_artefacts()` can return is under one of
those prefixes by construction, so the membership test `s in generated` is **subsumed**: no
widening of this oracle can change `gate_violations()`, and none did.

The consumer that reads **exact membership** is `origin_reconcile._split_generated`, where a path
in neither oracle is classified as somebody's WORK and the refusal leads with how to **land** it —
on a producer's output, when the correct remedy is revert. That is the `value_arms.json` defect of
2026-09-09 and the `orphan_baseline.json` defect of 2026-09-15, and ten more paths were standing in
it. The gate half is safe by a different mechanism than the one the draw credited; the advisory
half was the one actually wrong.

`test_the_gate_half_is_SUBSUMED_by_the_prefix_test_and_the_docstring_says_so` keys that to the
property: if a `GENERATED_TREES` entry or `offends` ever changes so membership stops being
subsumed, it goes red and says the frozen debt list must be re-measured against the wider set.

## 4. The unpredicted one: the gate read its own freeze list as evidence

Four of the fifteen raw matches came from `tools/file_scope_generated_paths.py` itself. `FROZEN` is
a set of `(atom_id, file_scope_entry)` pairs **copied out of the maturity map** — the declarations
this gate exists to judge — and a whole-string matcher reads the path halves of those pairs as
producer evidence.

That is circular. An atom's own `file_scope` entry would become the proof that the ground it names
is generated, so `violations()` would agree with the map by construction and a frozen entry would
help keep itself alive. The paths happen to be real artefacts, but the *evidence* is the map
talking to itself, and nothing else in the scanned trees names them.

The module now skips its own source, under a module-level `_SELF` so the skip is reachable by a
test rather than being a `__file__` branch no fixture can enter. Both legs are driven in
`test_MUTATION_the_gates_OWN_freeze_list_is_not_evidence_about_itself`: with `_SELF` pointed
elsewhere the fixture's freeze path **is** read, so the control cannot pass by the fixture simply
missing the matcher.

## 5. Why the match is held to an ASSIGNMENT, with the cost counted

Widening to every string constant adds ten:

| | |
|---|---|
| 2 | **PROSE.** `"site/data/customers.json + site/data/dashboard.json"` is a real constant in `tools/generate_capabilities_door.py`, and `tools/generate_world_data.py` has a sentence ending in a `.md` citation. |
| 6 | Already found by the segment match. |
| 2 | **Real paths this therefore misses** — `site/data/knowledge_topics.json` and `knowledge_price_cap.json`, in a `for rel in (...)` tuple in `knowledge_layer_gate.orphan_research`, which `read_text`s them. |

So the scope is a real trade and not a free one, and the two missed paths are recorded as a counted
gap in the code rather than left as an unasked question. The distinction it draws: an **assignment**
is where a module names its own destination; a loose constant is where it names somebody else's
artefact in order to read it. Both missed paths are the second kind. They degrade the safe
direction — classified authored, offered a landing, never reverted.

## 6. The eleven, and where each is spelled

| Path | Named in | New to the union? |
|---|---|---|
| `docs/observability/canon_drift.json` | `tools/canon_drift_check.py:111` | no — `written_artefacts` had it |
| `docs/observability/.run_marker_sweep_state.json` | `background/background_worker.py:75` | **yes** |
| `docs/observability/projections.sqlite` | `tools/build_projections.py:76` | **yes** |
| `docs/observability/renewal_churn_belief_grade.json` | `tools/grade_renewal_churn_belief.py:92` | **yes** |
| `docs/observability/settlement_choice_probe.json` | `tools/settlement_choice_probe.py:62` | **yes** |
| `docs/observability/settlement_per_axis_gain.json` | `tools/settlement_per_axis_gain.py:100` | **yes** |
| `docs/observability/value_cycle_ab_s1_three_arm_20260829.json` | `tools/generate_value_arms_data.py:4787` | **yes** |
| `docs/observability/value_cycle_ab_chase_off_2026-08-28.json` | `:4790` | **yes** |
| `docs/observability/value_cycle_ab_resi_renewal_fixed.json` | `:4793` | **yes** |
| `docs/observability/value_cycle_ab_resi_only.json` | `:4796` | **yes** |
| `site/data/moap_node_atoms.json` | `tools/moap_coherence_gate.py:81` | **yes** |

Two shapes the segment match structurally cannot reach are visible here: a `Path("…")` built from
one literal (`background_worker`, `build_projections`, `settlement_*`), and a path named in a
**data row** rather than a destination expression — the four `value_cycle_ab_*` artefacts are
historical run records cited by `generate_value_arms_data`'s own history table. The second kind is
never write-reached, so the write-keyed sibling cannot find them either. They are photographs of
runs inside a generated tree, which is exactly what `GENERATED_TREES` asserts about its members.

## 7. The controls, each proven against the mutant it names

Four mutants, run against the four new controls. Each control fails on exactly the defect it is
written for, and the specificity is the evidence — a control that goes red on every mutant is
measuring the fixture, not the defect.

| Mutant | Which controls went red |
|---|---|
| **A** — segment pair only (the defect restored) | `..._ONE_WHOLE_STRING_is_generated`, plus the two controls whose fixtures reach the matcher through it |
| **B** — widened to every string constant, not only assignments | `..._loose_constant_naming_SOMEBODY_ELSES_artefact_is_not_swept` **and that one alone** |
| **C** — `_SELF` skip removed | `..._the_gates_OWN_freeze_list_is_not_evidence_about_itself` **and that one alone** |
| **D** — `offends()` prefix branch removed | `..._the_gate_half_is_SUBSUMED...` **and that one alone** |

Mutant B is also how the assignment scope was shown to be a decision and not a preference: it is
the only mutant that makes the oracle *wider* and it is still caught, so the narrowing has a
failing case of its own rather than being an unexamined default. (It is 75× slower, too — the
all-constants scan walks every node of every assignment, which is quadratic. Not a reason to keep
the scope, but worth writing down beside one.)

## 8. Where the sequence stands

| Frame | Oracle | Paths added | Union moved? |
|---|---|---|---|
| helper, one frame down | write-keyed | +8 | — |
| signature default | write-keyed | +9 | — |
| instance attribute | write-keyed | +1 | **no** |
| named segment | write-keyed | +4 | yes, 234 → 237 |
| **whole string** | **tree-keyed** | **+11** | **yes, 237 → 247** |

## 9. What is next

1. **The cross-module frame** — 32 destinations are a module-level `def`'s parameter with no
   default, reachable only from a call site in another module. Still the largest remaining cluster
   on the write-keyed side, and still a real piece of work rather than a widening.
2. **The two loose-constant paths in §5**, if a second instance of the shape ever appears. One
   module's read-list is not a class.
3. **Ask the same question of `offends()`'s prefix list that was just asked of the matcher.**
   `GENERATED_TREES` is three trees. Whether a fourth generated tree exists that nobody has
   declared is a separate, uncounted question — and unlike this one, an addition there *would*
   move the commit gate, which is why it needs its own prereg and its own re-measurement of the
   frozen debt list rather than being folded in here.
