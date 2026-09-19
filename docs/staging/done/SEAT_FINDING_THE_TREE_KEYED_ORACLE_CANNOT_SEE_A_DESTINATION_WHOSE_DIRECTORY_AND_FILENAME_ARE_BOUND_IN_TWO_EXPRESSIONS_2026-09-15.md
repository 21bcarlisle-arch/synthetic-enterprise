**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 3 · **Atom:** (Lane 0 delivery — `the-tree-keyed-oracle-cannot-see-a-destination-whose-directory-and-filename-are-bound-in-two-expressions`)

*Filed and **RECORDED 2026-09-15**, same day — §4 is the result and no work is owed. §6 names what
is still open and it is smaller than what was closed.*

# A destination bound in TWO expressions was invisible to the tree-keyed oracle, and the +12 it recovers is worth +2 at the only consumer that reads it

**Filed 2026-09-15, delivery seat.** Prereg:
`docs/staging/records/PREREG_WHAT_THE_TREE_KEYED_ORACLE_GAINS_FROM_CROSS_EXPRESSION_NAME_RESOLUTION_2026-09-15.md`,
written before the population was counted.

This is the **last of the three gaps found on 2026-09-15** on
`tools/file_scope_generated_paths.py`. The hard-join fabrication (`683a86222`) and the glob pattern
(`6cc48c6ca`) are closed and recorded; both findings named this one explicitly as a *different
mechanism* rather than folding it in.

---

## 1. The defect

`generated_artefacts()` resolved a `/`-chain **inside one assignment and no further**. A module that
binds its output directory once and its files beside it was invisible:

```python
# tools/scale_probe_10k.py:119-121
ARTEFACT_DIR             = PROJECT / "docs" / "observability" / "scale_probe_10k"
REPORT_PATH              = ARTEFACT_DIR / "report.json"
PREDICTION_REGISTER_PATH = ARTEFACT_DIR / "prediction_register.json"
```

Line 119 is under a declared tree and carries no artefact suffix. Lines 120–121 are
artefact-suffixed and their head is an opaque `ast.Name`, so the tail alone is what gets matched and
it starts with no declared prefix. **Neither expression alone is both**, so neither oracle saw the
producer at all.

**`report.json` was nevertheless a member — and not because of its producer.**
`simulation/premise_population.py:1190` happens to spell the whole chain in one expression, as a
*reader*. So AO12's two tracked outputs were covered by an accident of how a third module reads one
of them, and `prediction_register.json`, which no reader spells whole, was in **neither oracle** and
was therefore being handed to `origin_reconcile._split_generated` as somebody's **WORK** — whose
refusal leads with how to **LAND** it. On a producer's output. That is the exact harm this module
exists to prevent, and it was live.

## 2. The repair

`_chain_segments` now takes a **name map** and returns **alternatives** (`list[list[str]] | None`),
the way `_static_paths` returns a list on the write-keyed side — a name rebound to a second
destination is still a destination. `_scope_chain_names` threads that map in source order, the
tree-keyed twin of `_scope_path_names`.

**The unit is the one thing the two halves do not share, and that is why it is a second function.**
`_scope_path_names` resolves to absolute `Path` objects because the write-keyed oracle starts from
`Path(__file__)` and can say where it is. This half never resolves a head at all — `PROJECT`,
`base`, `Path(__file__).resolve().parents[1]` all just stand where the repo root does — so its unit
is a **relative segment list** and its evidence is that a declared tree stands at the head of it.
Merging them would make one of them lie about what it knows.

**A name the map does not hold still falls back to the empty prefix**, which is the opaque-head
asymmetry the ordered reconstruction already rests on. It degrades the safe way: the tail alone
starts with no declared prefix, so the chain is dropped rather than fabricated. The resolution can
therefore only ADD; it can never move an existing member onto a different path.

## 3. Whether the machinery could be borrowed without its defect — the question the item asked

`_own_scope`'s docstring records what a flat, module-wide name map did to the write-keyed oracle: a
one-letter `p` bound to `DIRECTOR_AXES.md` in one function answered a `p.write_text(...)` in
another, and the gate **reported the director's own axes as a generated artefact** — in a set whose
consumer's remedy is `git show HEAD:<path> > <path>`.

**Measured rather than argued: a flat module-wide map over the five scanned trees adds ZERO members
beyond the scoped one.** The scoping stays anyway, and the zero is the reason to be careful rather
than a reason to drop it — this half only emits a chain whose head is a declared tree, a far
narrower target than a write site, so today it is safe by **accident**. That is precisely how
`WRITTEN_BUT_NOT_REPRODUCIBLE` was safe until `("docs", "status")` was declared and the accident
ended in one commit.

**The control therefore had to be a fixture, and its two scopes had to use the SAME name.** A
scope-leak control whose scopes bind different names passes with the defect fully installed —
nothing in the flat map can answer for anything else, so it measures the fixture and not the
mechanism. Both fixture functions bind `OUT_DIR`, and the assertion is equality, because the leak
that matters is one-directional: `site/data` answering the axes join emits
`site/data/DIRECTOR_AXES.md`, a path that does not exist, under a declared tree. The other direction
is dropped by the prefix test either way and proves nothing.

**And the class-body leak was real, in this commit, written by me.** The first draft tested
`isinstance(nested, ast.ClassDef)` — the **child** — which reads plausibly and does the exact
opposite of what it says: it lends a class body's names to its own methods, so a method's bare
`OUT_DIR` resolved to the class attribute beside it and the oracle emitted a path the code would
`NameError` on. `test_a_CLASS_BODY_does_not_lend_its_names_to_its_methods` went red on its author.
It cost **zero members on the live tree** (227 / union 255 with the defect and without), so a census
would have been green on it.

## 4. The numbers, beside the predictions, wrong ones kept

| # | Quantity | Predicted | **Measured** | |
|---|---|---|---|---|
| P1 | `N_add` (oracle membership) | 2–12, point **5** | **+12** (215 → 227) | in range, at the ceiling |
| P2 | `N_tracked` | 1–6, point **3** | **8 of 12** tracked | over |
| P3 | `N_gate` | **exactly 0** | **0** (0 → 0 violations) | ✅ |
| P4 | `prediction_register.json` recovered | yes | **yes** | ✅ |
| P5 | `N_flat` (flat-map fabrications) | **≥1**, ~50/50 | **0** | ❌ refuted |
| P6 | `report.json` reached by its PRODUCER | yes | **yes** — both outputs, from `tools/scale_probe_10k.py` alone | ✅ |

**AND THE PREREG ASKED THE WRONG QUESTION, WHICH IS THE FINDING WORTH MORE THAN ANY ROW ABOVE.**

Every quantity I pre-registered is a fact about `generated_artefacts()` membership. **The consumer
is the UNION**, and the union moved **253 → 255: +2.**

**Ten of the twelve were already in the write-keyed oracle.** `generate_capabilities_door`,
`fetch_weather_data`, `self_clearing_alarm_census` and the rest bind the directory in one statement
and then *write through the name* — so the write scan had them all along, on better evidence than a
declaration. The tree-keyed half was blind to ten paths that were never at risk. Of the two
genuinely new to the union, one (`.origin_race_episode.json`) is untracked dotfile state that never
arrives at the reconciler.

**So the entire harm this frame removes is ONE tracked file:
`docs/observability/scale_probe_10k/prediction_register.json`** — the instance the item was drawn
for, and the only one.

This is this project's own recurring shape, caught on myself: *before dividing or differencing two
numbers, say what each one counts.* I plotted the six-frame curve (+8, +9, +1, +11, −6, −1) and
predicted the seventh point on it — and that series was measuring **how much the two oracles
overlap** at least as much as it was measuring reach. On the union the curve never broke: it is a
steady approach to zero, and this frame contributes +2.

**The honest conclusion is that this door is now nearly shut**, and the next frame on this module
should be made to predict its **union** delta before it is worth starting.

## 5. Controls, each mutation-proven with a distinct mutation

| Control | Mutation that reddens it | Verified |
|---|---|---|
| `test_MUTATION_a_destination_bound_in_TWO_expressions_is_generated` | delete the `ast.Name`/`known` branch in `_chain_segments` | ✅ red |
| `test_MUTATION_a_name_does_not_leak_ACROSS_scopes` | replace the scoped walk with one flat `ast.walk(mod)` map | ✅ red |
| `test_a_CLASS_BODY_does_not_lend_its_names_to_its_methods` | hand `known` instead of `inherited` in the `ClassDef` branch | ✅ red |

Each was run in a clean HEAD extract with the mutation applied, not reasoned about. The first
control carries a **third leg** — a chain joined onto a name the scope never binds must NOT appear —
because asserting only the two recovered paths would pass with a fabrication sitting beside them.
Every join in every fixture is an **`Assign`**, never a `return`: both halves of the matcher are held
to `Assign`/`AnnAssign`, and this file has already been caught once by a fixture the scanner never
visited, which passed for lack of a subject.

## 6. What is still open, counted rather than left as an unasked question

1. **An alias binds nothing.** `B = A` where `A` is a resolved chain does not seed `B`: seeding
   requires the assignment's value to **be** one whole chain (identity against `node.value`), so that
   `PAIRS = (P / "a" / "x.json", P / "b" / "y.json")` cannot bind `PAIRS` to a path it is not.
2. **A name as the RIGHT operand is still declined.** `OUT_DIR / NAME` with `NAME =
   "prediction_register.json"` is an opaque *middle* and is refused whole — correctly, by the rule
   that a missing middle fabricates. The write-keyed half resolves this through its separate `"str."`
   namespace; this half has no counterpart. A different door, not this one.
3. **No `self.` reach.** `_class_self_paths` gives the write-keyed half instance-attribute
   resolution. This half has none and does not fake one.
4. **The evidence here is still a DECLARATION, not a write site**, and the resolution widens what
   that stands for. `tools/generate_case_study_recommender.py:60` reaches
   `site/data/customers/_index.json` through a **read** (`json.loads((CUSTOMERS_DIR /
   "_index.json").read_text())`). The classification is right — `site/data` is generated ground — but
   the site is a reader. This is the pre-existing property of the tree-keyed half, unchanged in kind
   and wider in reach, and it is the reason `written_artefacts` exists beside it.

Given §4, none of these is worth a frame on its own. Each would be worth starting only with a
**union-delta** prediction attached.
