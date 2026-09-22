**Severity:** LATENT · **Lane:** H_harness · **Epoch:** 3 · **Atom:** (Lane 0 delivery — wire the live-record readers through the shared-tree resolver)

# Two implementations answer "where is the shared tree", they disagree about method, and a circular import is why the second one exists

**2026-09-16, scheduled tick, worker seat.** Found while wiring the live-record readers, which is
the work that has to call one of them. Filed rather than fixed: the fix is a module-graph change
and this turn's claim was the wiring.

## The two

| | `seat_continuation.shared_tree_dir(project_dir)` | `live_ledger_guard.shared_tree_live_record(path)` |
|---|---|---|
| asks | reads the `.git` FILE pointer and walks its parents | `git rev-parse --git-common-dir` in a subprocess |
| returns | the shared tree's DIRECTORY | the shared tree's copy of one PATH |
| cost | none | one subprocess per call, 10s timeout |
| redirects | unconditionally | only when the shared copy EXISTS |
| side | built for the WRITE side (claim stores) | built for the READ side (live records) |
| callers | 4 modules + tests | 2 before this turn, 6 after |

Both fail closed to the caller's existing behaviour, and both are individually well-reasoned and
mutation-proven. This is not a defect in either. It is one rule with two implementations, which is
the shape the VAT rule taught this project to look for: a defect fixed in one of them is still
live in the other, and nothing can notice.

## Why it happened, which is the part worth keeping

`seat_continuation` imports `guard_live_ledger_write` from `live_ledger_guard` at module level. So
`live_ledger_guard` **cannot** import `seat_continuation` at top level — the obvious convergence
(have the resolver delegate its "where is the shared tree" question to the function that already
answers it) is a circular import.

That is a real constraint and it explains the duplication honestly. It does not excuse it: the
answer is to move `shared_tree_dir` DOWN into `live_ledger_guard` beside its twin and have
`seat_continuation` import it from there, which is the direction the module graph already runs.
Not attempted here.

## The measurable consequence, not an aesthetic one

`shared_tree_live_record` spawns a git subprocess on **every** call whose path is inside the live
record room — which is every call its callers make. Its own docstring flags this ("this is called
per read") as the reason it keeps a behaviourally-subsumed early-out. `shared_tree_dir` answers the
same question by reading one small file, with no subprocess at all.

Wiring four more readers through it this turn raised the per-tick subprocess count. The readers
wired are all low-frequency (a supervisor cycle, a launch check, a verdict record), so this is not
urgent — but it scales with exactly the wiring the Lane 0 item asks for, and the cheaper
implementation is already in the tree.

## What NOT to do

Do not memoise `shared_tree_live_record` at module level as a shortcut. The tree a process runs in
is fixed, so it looks safe, and it is — but it would freeze the answer for the test fixtures that
monkeypatch `PROJECT_DIR` and `LIVE_RECORD_DIR` to drive the real-git two-tree fixture, and those
are the only controls proving the redirect branch is reachable at all. Converge on
`shared_tree_dir` instead; it is cheap without needing a cache.
