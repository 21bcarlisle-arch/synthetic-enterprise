**Severity:** BLOCKING · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0 delivery
· **Class:** controls_that_cannot_fail

# The status board published a wiped roster, and the failing agent did not go stale — it vanished

Filed 2026-09-05 by the delivery seat under the Lane 0 claim
`ask-the-remaining-32-benign-census-rows-the-loader-question-2026-09-04`. **Fixed and landed in the
same commit.** Pre-registration filed before the deciding measurements:
`SEAT_PREREGISTRATION_WHETHER_THE_STATUS_BOARDS_LOST_ROSTER_AND_THE_IDLE_COUNTERS_RAISE_ESCAPE_THEIR_CALLERS_2026-09-05.md`.

## Why these two, and why the row's own reasoning is the finding

Ranked as the direction asks — by what the carrier's WRITER does. `agent_status.json` is the
largest read-modify-write left on the census: `update_agent_status` loads the whole roster, appends
one entry and writes the whole file back, and `update_sim_metrics` does the same one function away.
It is also the only carrier in this sweep whose corruption reaches a **published** surface.

The census row justified `benign` like this, and it is a good argument:

> Staleness is measured as now MINUS last_heartbeat, so a failing agent that stops writing makes
> the number WORSE, not better — the opposite of the self-clearing shape.

**That holds only while the agent's ROW still exists.** Measured against a live prior of two
agents, one of them eight days stale, in `error`, carrying an anomaly:

| prior | `_load` | `update_agent_status` | roster after | published mirror |
|---|---|---|---|---|
| **live control** | 2 agents | ok | supervisor, sim-runner, +1 | same |
| missing file | default | ok | +1 only | same |
| empty file | default | ok | **all lost** | **wipe published** |
| truncated | default | ok | **all lost** | **wipe published** |
| `{"other": 1}` | `{'other': 1}` | ok | **all lost** | **wipe published** |
| `null` | `None` | **RAISED** AttributeError | — | — |
| `[1, 2, 3]` | `[1,2,3]` | **RAISED** AttributeError | — | — |
| `{"agents": [1, 2]}` | as written | **RAISED** TypeError at `a["name"]` | — | — |

The stale `sim-runner` in `error` **did not go stale on the board. It vanished from it.** And
absent reads as *not part of this system*, which is the opposite of the alarm the row relies on.
`SITE_STATUS_FILE.write_text` is two lines below `STATUS_FILE.write_text`, in the same call, under
the same lock — so the wipe reaches the published board in the same breath as the register.

The three raises are inside the `flock`, on the function every daemon calls after every meaningful
action. **19 of 28 call sites across 11 modules have no enclosing try**, and `supervisor.main()`
calls it as its **first act, outside the `while` and outside every try** — so an unreadable status
file stopped the escalation watchdog starting.

`.supervisor_idle_turn_count.json` is the same `json.loads(...).get` shape.

## The predictions, and the one that was half wrong

Q1 (call sites unguarded), Q2 (roster wiped and published), Q3 (a dead agent vanishes rather than
going stale) all held. **Q4 did not.** I predicted the idle counter's raise would kill the
supervisor's tick. It escapes `run_cycle` — no try covers the call — but `main`'s loop catches every
`Exception`, so the supervisor does **not** die: it logs `Supervisor cycle error` every two minutes
forever and the tick never completes. Alive, warm, doing nothing, on exactly the branch that exists
to make an idle machine visible. The correction is recorded beside the claim in the loader's
docstring and in the census row, not quietly revised.

## The repair, and the third defect the repair itself surfaced

Both write sites go through `episode_prior` — **both**, because this module's own comment records a
previous repair that guarded `update_agent_status` and not `update_sim_metrics`, and 32 refusals
survived it unchanged. On an unreadable prior the bytes are preserved and the file carries
`roster_rebuilt_from_unreadable`: a board showing three agents because three exist and one showing
three because it forgot the rest are otherwise the same bytes, and that is the one thing a reader
cannot recover for themselves.

Preservation uses a new `keep_original=True` on the shared helper. The default **moves** the file,
and this caller holds an `fcntl` lock on that inode — a move would drop the rebuild at a path
nothing was holding while every other daemon writes it. Move-versus-copy is a per-carrier property,
so it is a flag on the seam rather than a sixth hand-rolled loop.

**A third defect, found by measuring the repair rather than reasoning about it.** After the fix,
every *first-ever* board announced that it had lost a roster it never had and wrote a `.unreadable`
copy of nothing. Cause: `open(STATUS_FILE, "a+")` **creates** the file, so by the time `_load` looks,
a fresh run has a zero-length file — which is UNREADABLE, correctly. The loader's ABSENT branch was
right and simply **unreachable from its only caller**, because the lock acquisition one line above
manufactured the file. Existence is now captured before the lock.

The idle counter gets the crash fix and **deliberately not** an alarm: absent and unreadable both
start from 0, the reset is genuinely cheap (all-time count, consumers are a log line and
`naive_organ`'s evidence reference, nothing reads it for severity), and inventing an escalation
nobody chose is what the census's own scope note forbids.

## Two of my own controls could not fail, and what they taught

Mutation-proving found **two survivors**, both tautologies rather than equivalences:

- `keep_original` dropped → survived. The leg asserted `board.exists()` after the call, which is
  true either way because the rebuild writes the path back. **Re-keyed to the inode**: on a move,
  the original inode goes into the `.unreadable` copy and the path holds a new one — which is
  exactly the inode the flock is no longer on.
- The second write site's repair reverted → survived. The leg asserted `phase == 9`, satisfied by
  any body that does not raise — and the crash was already fixed inside `_load`. **Re-keyed to what
  is actually left to that site**: preserve the bytes, and say on the file that the roster was
  rebuilt.

Both now fire. All seven mutants fire: 10, 1, 1, 1, 6, 3, 1 legs respectively.

## What this leaves

26 `benign` census rows still carry no `loader` field, down from 31 at the start of this claim.
`agent_status.json` also sits on a whole-tree ratchet that is **already red at HEAD** (83 unguarded
observability writers against a bound of 74) — pre-existing, verified by re-running it against
HEAD's own copies of both files, and not this lane's to move.
