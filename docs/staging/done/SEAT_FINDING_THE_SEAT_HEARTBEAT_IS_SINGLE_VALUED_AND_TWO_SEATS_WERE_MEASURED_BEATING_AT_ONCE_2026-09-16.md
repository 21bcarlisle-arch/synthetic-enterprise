**Severity:** LATENT · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# [SEAT] the seat heartbeat is single-valued and two seats were measured beating at once

Drawn as *"decide the WRITE side of `.launch_records.json`, then wire the read; same question for
`seat_continuity.note_activity`"* — the one row the 09-16 live-record survey
(`SEAT_FINDING_THE_LIVE_RECORD_RESOLVER_WAS_NOT_EVEN_WIRED_INTO_THE_OTHER_TWO_READERS_OF_THE_FILE_IT_WAS_NAMED_FOR_2026-09-16.md`)
left **UNDECIDED**, because both subjects are read-modify-writes over a TRACKED live record and
resolving the READ without the WRITE loses the write instead of staling the read.

**The two were decided OPPOSITE ways, on measurement.** One is delivered. The other is a refusal,
and the refusal uncovered the finding this document is named for.

## The premise was NOT spent

`e9ad946cd` is an ancestor of `origin/main`, as the draw said. It is the commit that *filed* this
as owed; it did not do it. Neither module resolved either side at HEAD before this turn.

## `.launch_records.json` — REDIRECTED to the shared tree, both sides

Measured in `/var/tmp/se-seat-executor` against `/home/rich/synthetic-enterprise`, same commit,
same code, two trees:

| | the worktree's checkout | the shared tree's live book |
|---|---|---|
| records | **4** | **12** |
| `noise-floor-20260910` | `live` | `finished` |
| `arms-rerun-20260910b` | `live` | `finished` |

So from a delivery turn: `check()` re-asks two claims the machine settled six days earlier,
`unregistered_live_units()` grades systemd's real units against a book missing eight of them, and
`record()` — reached in production by `launch_long_job` — writes a launch nothing else will ever
read.

**The subject decides it.** A record's subject is a `systemctl --user` unit, and there is ONE user
manager per machine. The register describes machine state, not tree state; two books is not a
tolerable divergence but two answers to a question that has one. `load()` and `save()` are the only
functions in the module that touch the path, so wiring both covers every caller and no future one
can resolve half of it.

**A hole the redirect itself opens, closed in the same commit (R15).**
`guard_live_ledger_write` refuses on `is_live_record_path`, whose room is derived from *this* tree's
`LIVE_RECORD_DIR`. A path already redirected to the shared tree is **outside** that room — so a
`save()` that resolved first and guarded second would hand a test process the real launch register
with the guard still called, still passing, and permanently unreachable for exactly the callers the
redirect applies to. The guard is therefore asked about the path the caller named, before the
redirect moves it.

**Accepted cost, named rather than discovered later:** `--check` run from a worktree now settles
verdicts in the shared tree's copy of a tracked file. That is correct — it is the one book — and it
is already the standing condition for every live record the daemons write. A lane committing
`docs/observability/` by pathspec will sweep it, as it would any of them.

## `.seat_heartbeat.json` — REFUSED, and this is the finding

Measured 2026-09-16T14:20Z. The two trees did **not** hold one live seat and one stale checkout.
They held **two live seats**:

| tree | session | pid | beat age | tool count |
|---|---|---|---|---|
| `/var/tmp/se-seat-executor` | `f4c65996` | 3399771 | 0.1 s | 16 |
| `/home/rich/synthetic-enterprise` | `53b48707` | 3394062 | 76 s | 196 |

**The record is single-valued and the population is not** — this project's most expensive recurring
shape, and the reason to say what a thing is before measuring it. Merging the beats onto the shared
tree does not yield one honest answer; it yields the **survivor's**. When one of two concurrent
seats dies, the other keeps the shared beat warm, `state()` never reaches `SILENT_AFTER_SECONDS`,
`sweep()` never fires, and the dead seat's uncommitted work is orphaned in silence — the exact
outcome `seat_continuity` exists to prevent, reintroduced by its own repair. That is a FAIL-SILENT,
and it is worse than the staleness it would fix: a stale beat over-reports death, which is noisy and
self-correcting, and is why the 09-16 survey already graded this reader NOT FLATTERING.

The per-tool-call `git` subprocess is real (a fresh hook process outlives no cache) but it is not
the reason. It would be worth paying for a correct answer.

### The gap, named rather than papered over

`sweep()` only ever reads the tree it was imported from. **A seat that dies in a linked worktree is
swept by nobody**, unless a tick happens to run in that same worktree — and the seat executor
mandates that delivery turns run in linked worktrees. The handoff mechanism is therefore blind to
the population it was built for, in the direction that files nothing.

The fix is a sweeper that enumerates `git worktree list` and a store holding **one record per
seat** — keyed, not single-valued. **It is not built.** A redirect onto a single-valued record
would look like an answer and would remove the only signal the dead seat still has.

## Pre-registration, written before the control was run

> Unwiring EITHER side of `launch_liveness` fails the launch-register leg and not the heartbeat
> one; adding a resolver to EITHER side of `seat_continuity` alone fails the heartbeat leg and not
> the launch one; swapping the guard and the redirect in `save()` fails only the ordering leg. A
> mutation that fires nothing means the leg is a tautology; one that fires everything means the
> legs grade one thing while claiming three.

### The result, kept beside the prediction: CONFIRMED, 4 of 4 mutations fired exactly their own leg

| mutation | fired | predicted |
|---|---|---|
| `load()` unresolved | launch-register leg only | ✓ |
| `save()` unresolved | launch-register leg only | ✓ |
| `seat_continuity._read()` resolved alone | heartbeat leg only | ✓ |
| guard and redirect swapped in `save()` | ordering leg only | ✓ |

## What the control is keyed to, and what it is deliberately NOT keyed to

`tests/background/test_a_read_modify_write_live_record_reads_and_writes_one_tree.py` asserts **the
two sides agree**, not **both are redirected**. Keyed to "both redirect" it would be keyed to
today's answer and would go red on the day the heartbeat is correctly repaired with a keyed store —
the backwards direction CLAUDE.md names. Keyed to agreement it fires on the defect and stays green
through either honest repair.

The launch leg additionally asserts the redirect is **taken** (the record lands in the shared book
and the worktree's copy is untouched), because a module that redirected nothing round-trips
local-to-local perfectly and would satisfy the agreement clause on its own.

No mocks: the fixture builds a real git main tree and a real linked worktree, copies the real
modules in, and drives them from a real **non-test** interpreter with `PYTEST_CURRENT_TEST`
stripped. So `guard_live_ledger_write` behaves as it does in production instead of being faked
away, and `git rev-parse --git-common-dir` is answered by git about a worktree git actually made.

## What landed

- `background/launch_liveness.py` — `load`/`save` resolve through
  `live_ledger_guard.shared_tree_live_record`; `save` gains `guard_live_ledger_write` **before**
  the redirect.
- `background/seat_continuity.py` — the refusal and its measurement, recorded at
  `note_activity`. No behaviour change.
- `tests/background/test_a_read_modify_write_live_record_reads_and_writes_one_tree.py` — new.

## What is still owed

The per-seat keyed heartbeat store and the cross-worktree sweeper described above. Nothing in this
commit closes it and nothing in this commit hides it.
