**Severity:** LATENT · **Lane:** H_harness · **Epoch:** 3 · **Atom:** (Lane 0 delivery — `the-blocking-tests-record-owes-its-reader-the-divergence-of-the-tree-it-graded`)

# The pre-commit gate selects tests by SUBJECT-MODULE NAME, this repo names them after the DEFECT they close, and the two conventions do not intersect — 153 of 273 background controls cannot be selected by a change to any module they guard

**Filed 2026-09-17, delivery seat.** Found while landing an unrelated Lane 0 item, from the
operational question *"will this red block my commit?"*. **No pre-registration: the first
measurement was run to answer that question, and the sweep below followed from its answer. These
are observations, not predictions, and nothing here should be read as a confirmed forecast.**

---

## 1. The instance

At the start of this turn, at HEAD (`1d9c08f94`), in this worktree:

```
tests/background/test_a_read_modify_write_live_record_reads_and_writes_one_tree.py::
test_a_launch_recorded_from_a_linked_worktree_joins_the_one_book_the_machine_keeps
FAILED — ModuleNotFoundError: No module named 'background.episode_prior'
```

The control builds a stand-in repo and copies `_MODULES` — a hand-kept tuple — into it.
`background/launch_liveness.py` gained `from background.episode_prior import ...` at module level
in `5f6a4f15f`, **earlier the same day**. The tuple was not updated, so the fixture's child
process ImportErrored before a line of its subject ran, and an ImportError stood in for a verdict.

That instance is repaired and landed (`93a085e9e`): `_MODULES` is now the transitive closure of
the roots' module-level `background.*` imports, read by AST off the subject's own source, with a
control keyed to the closure property rather than to today's membership.

**The instance is not the finding.** The finding is why nobody saw it.

## 2. The cause: two naming conventions that do not intersect

`tools/pre_commit_test_gate.tests_for()` maps a changed source file to its tests by **stem**:

```python
matches  = set(ROOT.glob(f"tests/**/test_{p.stem}.py"))
matches |= set(ROOT.glob(f"tests/**/test_{p.stem}_*.py"))
```

So `background/launch_liveness.py` selects `tests/**/test_launch_liveness*.py` and nothing else.

`CLAUDE.md` requires the opposite of every control in this repo: *"every `test_*` naming its own
defect"*. A control named for the defect it closes —
`test_a_read_modify_write_live_record_reads_and_writes_one_tree.py` — shares no stem with
`launch_liveness.py`, `live_ledger_guard.py` or `seat_continuity.py`, which are the three modules
it exists to grade. **The house style makes a control invisible to the gate's own selection.**

`tests_for`'s docstring already records the previous rung of this same class — the exact-stem glob
being *"silently blind to a whole naming convention the repo actively uses"* (`_seam`, `_event_log`,
`_guards`), which cost a ~112-minute publish wedge on 2026-08-09. The suffix half closed the
`test_<subject>_<aspect>.py` case. It cannot reach `test_<the_defect_in_a_sentence>.py`, and that
is now the dominant shape in this tree.

## 3. Measured, not argued

Run in this worktree at `93a085e9e`, using `tools.pre_commit_test_gate.tests_for` and the
always-on `CONTROL_TESTS` list:

| Question | Measured |
|---|---|
| `background/*.py` modules | 154 |
| controls in `tests/background/` | 273 |
| …selectable by a change to **any** of those 154 modules, or always-on | **120** |
| …selectable by a change to **no** module they could be guarding | **153** |

Widened to 1,143 source modules across `background/`, `tools/`, `company/`, `saas/`,
`simulation/`, `site/` against all 1,691 `tests/**/test_*.py`:

| Question | Measured |
|---|---|
| test files reachable from some source module's stem, or always-on | 908 |
| **test files no source-module change can select** | **783** |

**Honest bound on that second table.** The gate has further trigger lists keyed to *non-`.py`*
surfaces — `LEVEL_SENSITIVE_TESTS`, `CANON_SURFACE_TESTS`, `MINT_HYGIENE_TESTS`,
`STORE_CONTRACT_TESTS`, `SITE_SURFACE_TESTS` and `data_surface_tests()` — which reach some of
those 783. The residual after subtracting every one of them was still being computed when this was
filed and is **not established**; it is smaller than 783. The `tests/background/` figure in the
first table already includes the always-on set and needs no such caveat, because none of those
surfaces are `.py` modules under `background/`.

## 4. What this means, stated narrowly

These 153 are not untested files. They are **controls that run only when someone edits the control
itself** — `tests_for` returns a changed test file as its own target. That is precisely backwards:
a control should run when you touch the thing it guards, not when you touch the guard.

The failure mode is the one observed today and it is silent by construction:

1. a module changes;
2. the control that grades it is not in the selection, so the commit gate is green;
3. the control is red at HEAD, and stays red until an unrelated change happens to pull it in — at
   which point it refuses **whoever's** commit did, who did not cause it.

Step 3 is already a filed finding in its own right
(`SEAT_FINDING_A_TIME_BOMBED_FIXTURE_WENT_RED_ON_A_CALENDAR_DATE_AND_THE_REFUSAL_NAMED_WHOEVERS_CHANGE_PULLED_IT_INTO_THE_SELECTION_2026-09-15.md`).
**That finding is the symptom of this one.** It describes the moment of detonation; this describes
why the fuse is long.

## 5. What I am NOT claiming

* **Not** that the selection should be the whole suite. It is a deliberate speed trade-off, stated
  in the gate's own docstring, and `pre_commit_test_gate.py` carries per-entry cost annotations
  (`# background,docs|31|6.82`) showing it was measured.
* **Not** that these 153 never run. Something collects 26,731 tests; this says nothing about what
  a full-suite runner does or how often. *Whether any runner grades HEAD in full, and on what
  cadence, is not established here* — and it is the first thing to establish before sizing a fix,
  because if one exists and is fast enough the remedy is "read its output", not "widen selection".
* **Not** that the naming convention is wrong. Naming a control after its defect is why these
  files are readable, and it is a rule. The *mapping* is what has to change.

## 6. The cheap shape of a remedy, not a recommendation

Recorded so the next reader does not re-derive it — **not costed, and not proposed for action
until §5's open question is settled.** A control's real subjects are already written down in the
control itself, in its imports: `test_a_read_modify_write...` imports
`background.live_ledger_guard` at module level and drives `launch_liveness` and `seat_continuity`
by name in the source it hands its child. The same AST closure that repaired `_MODULES` in
`93a085e9e` inverted — module → tests that import it — would map every one of these 153 to its
subjects without touching a single filename, and would degrade the same way: loudly.

The direction to be careful about is the obvious one. A mapping that reaches more tests makes the
gate slower on every commit; a mapping derived from imports reaches the *transitive* graph, which
for a module like `background/notify.py` is most of the tree. Any remedy has to state its
selection cost against the annotations already in `pre_commit_test_gate.py`, or it will be
reverted by whoever next measures the cadence.
