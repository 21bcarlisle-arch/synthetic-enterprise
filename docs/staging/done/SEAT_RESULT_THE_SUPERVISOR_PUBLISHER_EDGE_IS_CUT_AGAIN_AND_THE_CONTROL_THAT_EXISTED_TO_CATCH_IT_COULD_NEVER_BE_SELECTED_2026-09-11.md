**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0 delivery

**Knowledge:** none — this is a harness/selection state, not domain understanding.

# The supervisor→publisher edge is cut again, and the control written to catch it could never have been selected

Closes the Lane 0 item *"the supervisor imports the publisher again and it is the only red"*
(claim `the-supervisor-imports-the-publisher-again-and-it-is-the-only-red`).

The defect is repaired. The more expensive fact is the second half of the item's question, and it
has a definite answer: **the control was correct, was present, and was structurally unreachable by
the gate that should have run it.**

---

## 1. The premise was live, and the defect is LOCAL-ONLY

Checked before touching anything, because a drawn premise can read as live only because the tree is
behind origin:

| | state |
|---|---|
| `rev-list --count HEAD..origin/main` | **31** behind, **25** ahead — the trees have diverged |
| `59a91d4a2` (the commit that re-cut the edge) | **not an ancestor of `origin/main`** |
| `origin/main:background/supervisor.py` | carries **no** top-level `process_run_complete` import |
| the test at HEAD, in a clean `git archive` extract | **FAILED**, naming the chain |

So origin never received this defect. It is not something a fast-forward clears, and the merge
would have *carried it to origin* — which is what the item's check against merge tree `818eacc75`
already said. It had to be repaired here, on its own.

The reproduction, on clean HEAD bytes rather than the shared dirty tree:

```
E  Failed: the supervisor reaches a publish-path source, so every test that imports the
E  supervisor now blocks publishing:
E      background/supervisor.py -> background/process_run_complete.py
```

## 2. What it cost, measured rather than asserted

`publish_scope.resolve_scope()` on the same bytes, with and without the edge:

| | blocking test files |
|---|---|
| HEAD, edge present | **275** |
| edge cut | **239** |

**36 test files** — the draw ladder, the executor daemon and governor, the harden gates, forward
discovery, the mint, blocked-atom visibility. Exactly the 36 that `92e5b380a` removed on
2026-08-21, back again. None of them can make a published figure wrong, which is
`PUBLISH_PATH_SOURCES`'s own membership test; they were in the gate because of an import.

And it was the whole of `total_red: 1` in `.publish_gate_state.json`, so it blocked **every lane's**
publish for ~19 hours, not only the lane that wrote it.

## 3. The repair

The instinct in `59a91d4a2` was *right* — import the contract, never mirror it; that is what its own
comment says and the comment is correct. It was pointed at the wrong module. So the contract moved
rather than being duplicated or re-implemented:

- `operational_layer_timeout_named_a_test` and the three parenthesised "cannot tell" phrases move to
  `background/publish_gate_blocking_read.py`, the stdlib-only leaf cut for exactly this purpose.
- `process_run_complete` imports them back and stays their only **writer** —
  `operational_layer_timeout_subject` reads a dead subprocess's output and has no business in a leaf.
- `background/supervisor.py` asks the leaf.

The phrases travelled *with* the predicate deliberately: the convention they share is "a cannot-tell
answer is parenthesised, a real nodeid is not". Splitting them would leave that convention implicit
in one module and asserted in another, free to drift silently — the mirror class this repo refuses.

`tests/background/test_publish_scope.py`: **1 failed / 27 passed → 30 passed, 1 skipped.**

## 4. THE REGRESSION QUESTION — why the control did not stop it

`tests/background/test_publish_scope.py` is **not** in the commit gate's test selection, and no
rename or reorganisation could put it there.

**Where the selection is decided:** `tools/pre_commit_test_gate.py` — invoked from
`tools/git-hooks/pre-commit` (`core.hooksPath` = `tools/git-hooks`) as
`python3 tools/pre_commit_test_gate.py`. It selects by **filename stem**: `tests_for(path)` globs
`tests/**/test_<stem>.py` and `tests/**/test_<stem>_*.py`, plus the always-on `CONTROL_TESTS` list.

Proved by calling it rather than by reading it:

```
tests_for('background/supervisor.py')
  = ['tests/background/test_supervisor.py',
     'tests/background/test_supervisor_blocker_precedence.py']

select_targets(['background/supervisor.py', 'background/process_run_complete.py'])
  -> 20 targets;  'test_publish_scope.py' in them?  False
```

**Why no stem can ever reach it.** This control's subject is an **edge between two modules**. It has
no implementation file of its own, so there is no stem for a stem selector to match. It is the same
structural class as the three entries already on `CONTROL_TESTS` for this reason (the ruff ratchet,
the segment-case guard, the child-stderr guard) — each a control whose subject is repo-wide or
relational, each invisible to per-file selection.

Note the near-miss that makes this worth writing down: the *publish* gate's own selector,
`tools/select_impacted_tests.select()`, **does** select this file for the same change (150 impacted
files, `test_publish_scope.py` among them) — because it walks the import graph and the test does
import `process_run_complete` inside a function. Two selectors, one repo, opposite answers; the
cheap one guards the commit and the thorough one guards the publish. So the defect landed green and
surfaced only when the publish gate ran, by which time it was blocking everyone.

**The repair to the class**, in the same change: `tests/background/test_publish_scope.py` is added
to `CONTROL_TESTS`, with two mutation-proven legs in `tests/tools/test_pre_commit_test_gate.py`
mirroring the ratchet idiom already there — one asserting a supervisor commit now selects it (and
that the stem selector still cannot), one dropping the entry and proving the selection goes away.
Cost: ~21s per code commit, 3.5% of the 600s budget the lint entry cites.

Had that entry existed on 2026-09-10, `59a91d4a2` could not have landed.

## 5. LIVE RESIDUAL — the next lane to land `supervisor.py` will be refused, and that is correct

`background/supervisor.py` is uncommitted-modified in the shared tree right now by another lane
(+101 lines: the `_idle_discover_frame_draw_concurrent` pass ceiling, paired with edits to
`tests/background/test_publish_gate_wedge_draw.py`). Their hunk **re-cuts this same edge**: it adds
`PUBLISH_GATE_WINDOW_SECONDS` to the very `from background.process_run_complete import (...)`
statement this change removes.

Their work was not touched. This landed via `surgical_land --content` against clean HEAD bytes, so
their working copy is intact — but their commit will now be **refused by the commit gate**, which is
the mechanism working rather than a new problem.

**The remedy for that lane, so it is not a puzzle:** move `PUBLISH_GATE_WINDOW_SECONDS` into
`background/publish_gate_blocking_read.py` on the same footing as the vocabulary moved here, and
import it from the leaf in both `process_run_complete` and `supervisor`. Identity is preserved, so
`test_publish_gate_wedge_draw.py`'s
`assert supervisor.PUBLISH_GATE_WINDOW_SECONDS is process_run_complete.PUBLISH_GATE_WINDOW_SECONDS`
continues to hold. It was deliberately **not** moved pre-emptively here: at HEAD that constant has no
supervisor-side consumer, and moving a publisher policy constant for a caller that does not yet exist
would have been speculative work landing in another lane's file.

## 6. What is next

- The 31/25 divergence with origin is untouched by this and remains the larger open item
  (`SEAT_FINDING_TWENTY_ONE_GATED_COMMITS_NEVER_REACHED_ORIGIN_AND_THE_TREES_HAVE_DIVERGED_2026-09-11.md`).
  This repair must reach origin for the merge to stop carrying the defect.
- The two selectors disagreeing (§4) is a class, not an instance: any control whose subject is
  relational is reachable by `select_impacted_tests` and invisible to the commit gate. The list is
  the current instrument; whether the commit gate should consult the import graph for
  `background/**` is a real question and is *not* settled here.
