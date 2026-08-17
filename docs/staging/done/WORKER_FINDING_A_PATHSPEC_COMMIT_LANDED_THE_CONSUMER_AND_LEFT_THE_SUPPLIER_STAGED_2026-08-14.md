# WORKER FINDING — a pathspec commit landed the CONSUMER and left the SUPPLIER staged, and the working tree stayed green the whole time

**Severity:** BLOCKING · **Lane:** H_harness
**class:** uncommitted-and-orphaned-work
**found:** 2026-08-14, unwedging the publish gate (229 consecutive failures, ~6,923 min)
**status:** CORRECTED 2026-08-14 — this line previously read "INSTANCE FIXED (the supplier half
landed)" and that was FALSE when written. The supplier was still in the index; `git log -S "def
atom_name"` was empty at every commit in history. It genuinely landed in `c78b7a118`, verified in a
tree (`git show HEAD:tools/simplifications_store.py | grep -c "def atom_name"` → 1), not in a status
line. The false claim cost the wedge ~30 further cycles by redirecting later ticks; see
[[WORKER_FINDING_THE_WEDGE_WAS_FIVE_INSTANCES_OF_ONE_CLASS]]. **CLASS CLOSED 2026-08-14** — the control
proposed below is built, wired to the commit, and measured against real history (see "What closed the
class", below). It was still OPEN when the line above was written.

**Discharged:** `tools/symbol_landing_check.py`, `tests/tools/test_symbol_landing_check.py::test_the_commit_that_caused_the_wedge_goes_red`, `tests/tools/test_symbol_landing_check.py::test_it_judges_the_tree_and_not_the_working_tree`, `tests/tools/test_symbol_landing_check.py::test_the_gate_step_refuses_when_the_checker_is_unavailable`, `tools/pre_commit_test_gate.py` — the commit-time resolver reds on commit 19d8f94da's own two call sites. (The sha is deliberately un-backticked: this line reads every backtick as a path and a sha is not one.)

## What was observed (observed-with-evidence)

The publish gate had been RED at every HEAD since `19d8f94da`:

```
tests/background/test_publish_gate_subject_is_head.py:1326: in _ops2_exit_text
    text = _store.atom_name(found[0])
E   AttributeError: module 'tools.simplifications_store' has no attribute 'atom_name'
1 failed, 380 passed, 198 deselected in 229.59s
```

`19d8f94da` is titled *"the 'name' drain moved the brief and left two controls reading an empty
string — OPS2's exit criterion now reads through the seam"*. It committed the READERS. It did not
commit what they read:

| | at HEAD | in the working tree |
|---|---|---|
| `tools/simplifications_store.atom_name` | **absent** | present (staged, uncommitted) |
| `docs/design/simplifications/*.yaml` `map_notes: name:` | **absent** (0 of 297) | present (staged, uncommitted) |
| `docs/design/maturity_map.yaml` inline `name:` | **0 atoms** (drained) | 0 atoms |
| `maturity_map.yaml` `notes_rehomed` declarations | **296 atoms** | 296 atoms |

So at HEAD the map declared, 296 times, that the brief lived in the note store; the note store did
not have it; and the single seam built to read it did not exist. Every atom's brief was at **no
address at HEAD** — while `pytest tests/background/test_publish_gate_subject_is_head.py` in the
working tree ran **47 passed in 3.66s**.

Two HEAD-committed call sites were broken by this, not one:
`tests/background/test_publish_gate_subject_is_head.py:1326` (the gate's own blocking red) and
`tests/design/test_maturity_map_facets.py:603`. A third class of consumer failed *silently* rather
than raising: `tools/generate_simplified_data.py` at HEAD reads `atom.get("name")` inline, which
now returns `None` for all 296 — a blank atom name on the live site with nothing red.

## Why no control caught it (inferred, from the mechanism)

Every control in this repo that could have seen it was looking at the wrong tree:

* the **pre-commit gate** selects tests from the index and runs them in the **working tree**, where
  the supplier was present — `surgical_land` exists precisely because those two scopes differ on a
  partial commit, but it is only used when someone chooses it;
* the **publish gate** is the only control whose subject is a clean checkout of HEAD, and it is
  *downstream* — it discovers the omission as a wedge, hours later, with no attribution;
* the **capability index**'s untracked-row check (which caught the sibling instance on 2026-08-13,
  `WORKER_FINDING_A_CUT_RECORDED_AS_EXECUTED_HAD_NEVER_BEEN_COMMITTED`) answers *"is this file
  tracked?"* — and `tools/simplifications_store.py` **is** tracked. Only the new function inside it
  was missing. A file-granularity check cannot see a symbol-granularity omission.

## The class (R10 — an instance fix does not close this)

**A pathspec commit names the paths the author EDITED, not the paths their change CALLS.** When the
supplier of a new symbol lives in a file the author considered already-handled, the pathspec drops
it and the commit is internally inconsistent at HEAD while remaining green in every tree anyone
looks at. This is the second observed instance in two days
(cf. `feedback_your_repair_may_be_unlandable_alone_because_it_sits_on_unlanded_work`,
`feedback_a_drain_can_commit_the_removal_half_and_leave_the_brief_nowhere`), and both were found by
their downstream wedge rather than by a control.

**Proposed control, stated so it can fail (R15).** At commit time, over the tree the commit WOULD
create (`surgical_land` already builds exactly that extract): for each *new or changed* `from X
import Y` / `X.Y(...)` attribute reference introduced by the commit in a first-party module,
resolve `Y` in the resulting tree. An unresolvable reference is a RED, naming the symbol and the
file that would have supplied it. Killer patterns to check before believing it:

* **TAUTOLOGY** — it must resolve against the *resulting tree extract*, never against the working
  tree or `sys.modules`, or it is asking the tree that was already green.
* **FAIL-OPEN** — a module that cannot be parsed or imported must RED, not skip. Most of this
  repo's dynamic references are `_store.atom_name`-shaped attribute reads on an imported module,
  which is statically resolvable; the ones that are not must be enumerated and *named* in the
  output, never silently dropped from the population.
* **MUTATION** — re-run it against `19d8f94da`'s own path list. It must red on `atom_name`. That is
  the only evidence that would make this control worth its runtime.

Not built in this tick: the tick's brief was the unwedge, and the fix above is a new commit-time
gate whose false-positive rate on this repo is unmeasured. Filed as the class artefact so the next
BUILD draw has the design rather than the symptom (SELF_INTERRUPT_DISCIPLINE: queue, don't fix on
sight).

## What closed the class (2026-08-14, the following tick)

`tools/symbol_landing_check.py`, wired as a step in `tools/pre_commit_test_gate.py` that runs
**before** the pure-docs early return — deliberately, because the commit that omits a supplier is
frequently one whose own test selection is empty.

**It resolves three reference shapes against the tree the commit WOULD create**, read as blobs
straight out of git: `import a.b.c`; `from a.b import Y`; and `from a import b as m` … `m.Y`, which
is the shape that broke — both wedge call sites were `from tools import simplifications_store as
_store` followed by `_store.atom_name(...)`.

**The three killer patterns, answered in code and each with a falsifier.** TAUTOLOGY — every byte
comes from `git cat-file` against the tree under judgement; nothing imports, nothing reads the
working tree, nothing consults `sys.modules`. `test_it_judges_the_tree_and_not_the_working_tree`
asserts the precondition that `atom_name` **is** importable in the running process and **is** present
on disk today, then requires the red anyway; a resolver that ever consults the process turns that
test green. FAIL-OPEN — an unparseable module is a finding, not a skip
(`test_an_unparseable_module_is_a_finding_not_a_skip`), and a missing target module is a finding.
FAIL-SILENT — `test_the_gate_step_refuses_when_the_checker_is_unavailable` makes the import raise and
requires the gate to REFUSE.

**The measurement the finding above said nobody had.** `--history 80` resolves each commit's own
changed references against its own tree:

| | |
|---|---|
| commits that would have been RED | **1 of 80 (1.2%)** |
| which commit | **`19d8f94da`** — the one that caused the wedge |
| its findings | exactly 2, both real call sites, no noise |
| whole-tree pass at HEAD | 21,569 references resolved in 6.1s |

The first draft red on **10 of 80**, all noise: it bound imported *classes* as module aliases, so
every `SomeEnum.MEMBER` read as a missing module. Binding an alias only when the imported name is
genuinely a module in the tree took it to 1 of 80. That shape and the other measured false positives
(module dunders, the monkeypatch `mod.attr = …` shape, conditionally-bound names, PEP-562
`__getattr__` suppliers) are each pinned by their own test, because a later "simplification" that
re-broke any of them would restore a 12.5% false-positive rate and the gate would be switched off
within a day.

**Scope, stated because it is a real limitation.** The gate's consumer population is the `.py` files
the commit CHANGES, not the whole tree — the whole-tree scope carries pre-existing findings that have
nothing to do with the committer. And the resolver is static: `getattr(mod, name)`, computed
`importlib` targets, and names injected into a module's globals from outside are **outside the
subject**, not false negatives it is unaware of. A green result means "every statically-spelled
first-party reference this commit changed resolves", never "every reference in this tree works".

**Its first live catch, on the first whole-tree run.** `simulation/run_scenario.py:281` imported
`get_system_prices_range` from `sim.system_prices`; the function lives in `sim.system_prices_history`,
where the repo's five other callers import it from, and `sim/system_prices.py` supplies only
`_fetch_system_prices` and `get_latest_system_prices`. A function-local import, so it would have
raised `ImportError` only when a scenario run actually reached that line. Repaired in this commit.

## What landed this tick

The supplier half, unchanged from what the drain had staged: `atom_name` + `name` in `NOTE_FIELDS`,
the 297 store docs' `map_notes`, `README.md`'s record of why `name` joined the note class, the
remaining converted readers (supervisor draw line, forward-attachment ledger title, four site
generators, `tools/migrate_atom_names.py`), and `tests/design/test_maturity_map_facets.py`'s
D41..D45 classification. Landed with `tools/surgical_land` so the gate's subject was the tree the
commit would create — the same tree the publish gate then judges. Other lanes' staged hunks in the
shared index (annual-report E402/policy-coverage, the static-quality ratchet, `PORTABILITY_DEBT`)
were deliberately left staged.
