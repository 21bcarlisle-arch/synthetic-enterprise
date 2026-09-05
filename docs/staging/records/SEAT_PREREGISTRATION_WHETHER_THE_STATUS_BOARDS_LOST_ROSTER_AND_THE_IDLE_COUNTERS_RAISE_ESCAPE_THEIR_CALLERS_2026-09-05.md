**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0 delivery
· **Class:** controls_that_cannot_fail

# Pre-registration: whether the status board's lost roster and the idle counter's raise escape their callers

Filed 2026-09-05 by the delivery seat under the Lane 0 claim
`ask-the-remaining-32-benign-census-rows-the-loader-question-2026-09-04`, continuing the sweep after
the inbound-channel increment landed (38f94a7e8).

## What has already been measured, and what has not

**Stated plainly so the record is honest:** the loader partition below was run as part of *ranking*
the remaining rows, before any prediction was filed. Those results are therefore observations, not
predictions, and are not claimed as either:

| carrier | loader | `null` | `[1,2,3]` | mapping without the key |
|---|---|---|---|---|
| `.supervisor_idle_turn_count.json` | `supervisor._load_idle_turn_count` | **RAISED** AttributeError | **RAISED** AttributeError | 0 |
| `agent_status.json` | `agent_status._load` → `update_agent_status` | **RAISED** AttributeError | **RAISED** AttributeError | OK |
| `agent_status.json` | `{"agents": [1, 2]}` | **RAISED** TypeError: `'int' object is not subscriptable` | | |

Both loaders are `json.loads(...)` followed by `.get(...)` under `except (json.JSONDecodeError,
OSError)` — the exact shape `episode_prior`'s own docstring enumerates, one level up, in two
carriers nobody had asked.

## What is NOT yet measured, and what I predict

These are the questions whose answers decide the severity, and none of them has been run.

**Q1 — does `update_agent_status`'s raise escape its callers?** It raises *inside* the `flock`,
after the `try:` whose `finally:` releases the lock, so I predict **no deadlock** — the lock is
released and the exception propagates. Every daemon in this repo calls this function on every
meaningful action. Prediction: **at least one call site has no enclosing try**, and there a corrupt
`agent_status.json` takes that daemon down on its own heartbeat. `ntfy_responder`'s call is inside
`check_once` and therefore inside `main`'s blanket `except Exception`, so I predict that one
survives — but the message is staged *before* the status update, so even there the harm is a log
line rather than a lost message.

**Q2 — does an unreadable status file WIPE the roster rather than raise?** For the members that do
not raise, `_load` returns the default `{"agents": []}`, `update_agent_status` appends exactly one
entry, and writes the whole file. Prediction: **every other agent's row is destroyed**, and the
board then reports fewer agents than exist. This is the read-modify-write harm the direction ranks
first, on a register that is **mirrored to `site/data/agent_status.json` and published**. Prediction:
**the wipe reaches the published mirror in the same call**, because `SITE_STATUS_FILE.write_text` is
two lines below `STATUS_FILE.write_text` with nothing between them that could fail selectively.

**Q3 — does a daemon that has stopped writing DISAPPEAR from the board, or go stale on it?** This
is the one that decides whether Q2 is cosmetic or not. The board's whole job is to say which agents
are alive, and staleness is measured as *now minus `last_heartbeat`* — which the census row itself
cites as the reason this carrier is `benign` ("a failing agent that stops writing makes the number
WORSE, not better"). That argument holds only while the ROW EXISTS. Prediction: **after a wipe, a
dead agent is not stale on the board, it is absent from it** — and absent reads as "not part of this
system", which is the opposite of the alarm the row is relying on. If that prediction holds, the
`benign` verdict is still correct on the episode question and the loader answer is severe.

**Q4 — does `_record_idle_turn`'s raise escape the supervisor tick?** The call is at
`supervisor.py:6421`, on the `map_exhausted` branch. Prediction: **it escapes**, killing the tick
that was about to report the map exhausted — i.e. the raise happens exactly on the branch that
exists to make an idle machine visible, so the instrument for "nothing to do" is destroyed by the
state it keeps its own count in. Secondary prediction: the reset is real but cheap — `count` is an
all-time counter whose only consumer is a log line and `naive_organ`'s evidence reference, so
losing it costs a number in a log, not a decision.

## What would refute this

Q1 refuted if every call site is inside a try. Q2 refuted if some path re-reads the file before
writing. Q3 refuted if the dashboard renders a roster from somewhere other than this file's `agents`
list. Q4 refuted if the supervisor's tick wraps `find_work`'s result handling.

## What done means

Both carriers tell ABSENT from PRESENT-BUT-UNREADABLE, no partition member raises out of either
loader, the roster is not destroyed by a read it could not perform, both census rows carry a
`loader` field, and each control has a reachability leg proving a live prior reaches a third answer.
