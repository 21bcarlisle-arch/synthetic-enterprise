**Severity:** BLOCKING · **Lane:** H_harness · **Epoch:** 3 · **Atom:** H27_payment_belief_gap

# RESULT — the live-ledger guard is blind from a linked worktree, and a fixture id was steering the delivery lane

*A test process could write the measurement of record, and the write actually observed was
changing which work the delivery seat was handed.*

*Lane 0, claim `lane-0-consulted-the-focus-list-zero-times-in-three-hours`. 2026-09-17.
Pre-registration:
`docs/staging/records/PREREG_DOES_THE_IMPORT_ERROR_FIXTURE_ACTUALLY_RAISE_AND_DOES_ITS_TEST_WRITE_THE_LIVE_DRAW_LEDGER_2026-09-17.md`,
written before any of the measurements below.*

---

## The drawn item's diagnosis is refuted, and I am recording that beside the result

The item named a suspect in `delivery_lane.record_draw` and asked me to confirm it **by counting,
not by reading**. The count refutes it on three claims:

| The item said | The ledger says |
|---|---|
| `background/.delivery_lane_claims.draws.json` | No such file. The live ledger is `docs/observability/.delivery_lane_claims.draws.json`, 359 rows. |
| "eight consecutive rows stamped `source: continuation` / `source_self_issued: False`" | `(continuation, False)` occurs **11** times in 359 rows and **never consecutively**. The eight `self_issued: False` rows it means are stamped `source: **focus**` — they are focus draws. Today's continuation run is stamped `self_issued: **True**`. |
| "the limit was never reached" | Replaying `_self_issued_chain` at each of today's draws: 03:05→0, 04:29→1, 04:38→2, 05:06→**3**, 06:07→0, 06:38→1, 07:04→2, 07:36→**3**, 08:24→**4**, 08:39→**5**. It crossed `SELF_HANDOFF_CHAIN_LIMIT = 3` twice and kept climbing. |

**The chain counter works and the swap fires.** `record_draw` is not the defect. The symptom the
item describes is real; its named cause is not, and nothing in `delivery_lane.py` was changed.

## What was actually wrong

**`live_ledger_guard` is structurally blind to the shared tree's live records when imported from a
linked worktree, and there are five linked worktrees on this machine.**

The two halves of one doctrine disagreed about where the record lives:

* `LIVE_RECORD_DIR` is `PROJECT_DIR / "docs" / "observability"`, and `PROJECT_DIR` comes from
  `__file__`. A module imported out of a linked worktree binds the whole published record to
  **that worktree**.
* The claim writers do not write there. `delivery_lane.CLAIMS_FILE` resolves through
  `seat_continuation.shared_tree_dir()` — the **shared** tree.

So the guard was handed a shared-tree live path, found it outside its own room, and returned it
**unchanged**. Measured directly from `/var/tmp/se-seat-executor`:

```
guard LIVE_RECORD_DIR  : /var/tmp/se-seat-executor/docs/observability
shared_tree_dir()      : /home/rich/synthetic-enterprise
ledger path written    : /home/rich/synthetic-enterprise/docs/observability/.delivery_lane_claims.draws.json
is_live_record_path()  = False        <-- the guard is blind
```

`seat_work_in_hand._save` **did** call `guard_live_ledger_write`. The wiring was never missing;
the guard's *subject* was one room wide. This is the R15 shape where a control is keyed to the
tree it was imported from rather than to the property.

**The read side already knew.** `shared_tree_live_record` has resolved live *reads* into the
shared tree since 2026-09-16, and its docstring reasons about exactly this `__file__` rebinding.
Only the *write* guard's subject had not been given the same answer.

## What it cost — a fixture id was steering the delivery lane

The live draw ledger carried a row whose id is **`some-id`**. That is not work; it is a fixture id
appearing exactly once in the repository, at
`tests/background/test_dispatch_is_the_claim.py:200`. It was first written 2026-09-06 and
re-stamped **2026-09-17 08:39**, `source: focus`, with no authorship flag.

`_self_issued_chain` walks newest-first and stops at the first row without a truthy
`source_self_issued`. The phantom row took the live chain from **5 to 0** — postponing the
delivery seat's own focus list by another three draws. That is the item's symptom, produced by a
test.

## Why nothing caught the test either — it could not fail

`test_a_lane_that_cannot_import_does_not_take_the_tick_down` monkeypatches `builtins.__import__`
to raise for `name == "background.delivery_lane" or name.endswith("delivery_lane")`. But
`from background import delivery_lane` calls `__import__("background", ..., fromlist=("delivery_lane",))`
— the submodule never appears as `name`. Measured:

```
P1 RESULT: import SUCCEEDED -- _boom did not fire
names _boom was asked about: [('background', ('delivery_lane',)), ...]
```

So the `except` arm in `_claim_dispatched` was **never entered**. The test's own stated mutation
("drop the `try/except` and this reddens") could not fire, and its assertion
`outcome == "SPAWNED"` was true on both sides of the branch it claimed to test. It then took the
*real* path — which is how a fixture id reached the live ledger. Its `_isolate` fixture redirects
only `worker_tick.*` attributes; it never redirects `delivery_lane.CLAIMS_FILE`.

## The repair

1. **`background/live_ledger_guard.py`** — `is_live_record_path` now answers for **both** rooms:
   this tree's `docs/observability` and the shared tree's, the latter found with
   `git rev-parse --git-common-dir` (the same question `shared_tree_live_record` already asks),
   hoisted into `_shared_record_dir()` and cached so the per-read path keeps no subprocess. The
   widening **cannot narrow**: every path refused before is refused now, and in the main tree the
   second room does not exist, so the predicate is exactly the old one.
2. **`tests/background/test_dispatch_is_the_claim.py`** — `_boom` now also matches the fromlist
   spelling, and the test asserts the simulated failure **actually fired** before asserting what
   it does. It now grades the branch it names.
3. **The phantom row is gone.** `some-id` removed from the live ledger (358 rows). Reversible —
   its exact contents are recorded above.

## The controls, and both fire

`test_the_live_record_room_is_both_trees_when_this_one_is_a_linked_worktree` stands where a
worktree-imported module stands and makes **one assertion over the whole partition** rather than a
leg per branch, so a guard that refuses *everything* fails it too:

```python
assert refused_local and refused_shared and not permitted_scratch
```

| Mutation | Result |
|---|---|
| drop the shared room from `is_live_record_path` | **RED** — `assert (True and False)` |
| restore the name-only `_boom` | **RED** — "the simulated ImportError never fired" |

`test_the_shared_room_is_absent_in_the_main_tree_so_this_is_the_old_predicate` holds the other
direction — the widening must not invent a second room where there is none. It **skips** rather
than asserts when the suite itself runs in a linked worktree, because a test keyed to where it was
checked out is keyed to today's answer rather than to the property.

Suites green: `tests/background/test_live_ledger_guard.py` +
`tests/background/test_dispatch_is_the_claim.py` — 23 passed.

## What this does NOT establish, and what is still owed

* **The population is wider than the one row I found.** Any live record under
  `docs/observability/` written from a worktree test process was equally unguarded for as long as
  worktrees have existed. I removed the one contaminated row I could *prove* was a fixture,
  because its id appears nowhere else. **Nobody has censused the rest**, and a row polluted by a
  test whose fixture id looks like real work would be invisible to the method I used. That census
  is the follow-up this finding owes.
* I did not establish *which* worktree run wrote `some-id`, only that a main-tree run cannot (the
  main tree's guard already refused it, silently, inside `record_draw`'s `except`).
* The delivery lane's focus-starvation symptom should now be watched rather than declared fixed:
  the phantom reset is removed and the guard is closed, but three hours of continuation draws had
  more than one contributor and I have attributed only this one.
