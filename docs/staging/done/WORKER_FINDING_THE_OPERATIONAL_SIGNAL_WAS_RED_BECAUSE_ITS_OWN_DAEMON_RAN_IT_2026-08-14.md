# [WORKER-FINDING] The operational-layer signal was RED for 9 hourly checks because the daemon that runs it flushes a digest the suite's own tests capture (2026-08-14)

**Severity:** BLOCKING · **Lane:** H_harness · **Status:** diagnosed and repaired in this tick —
class pin landed at directory scope, R15 proven both ways.

**Discharged:** `tests/background/test_deadmans_switch.py::test_the_digest_pin_fires_when_it_is_bypassed`

The RUNG-1b doorbell drew this as PRIORITY ZERO: `pytest -m operational` red for 8 (then 9)
consecutive hourly checks, past paging, so paging had not fixed it.

## The measurement, `observed-with-evidence`

Ran the exact signal (`background/process_run_complete.py::operational_layer_pytest_argv`):

```
python3 -m pytest tests/ -q --tb=short -m "operational or join_report_only or scale_report_only"
1135 passed, 25451 deselected, 1 xfailed, 4 warnings in 614.17s
```

**Green by hand, rc=0** — while `.operational_layer_signal.json` read
`{"consecutive_red": 8, "last_result": "red"}` and the daemon's 14:49 check logged a ninth red.
So the red was never a daemon-lifecycle regression. Every one of the 22 failures the digest named
(`docs/observability/sim-runner-log.md:167083`) is in one file,
`tests/background/test_deadmans_switch.py`, which passes standalone in 0.35s — under the daemon's
own environment too (checked against `/proc/483/environ`; not a PATH or env difference).

## The mechanism

`deadmans_switch.run_cycle()` ends with `_flush_notification_digest()` → `notification_digest.
maybe_flush()`, which reads the **real** append-only `docs/observability/ntfy_digest_queue.jsonl`
and sends via `background.ntfy_utils.send_ntfy` — the exact symbol ~27 tests in that file
monkeypatch to capture into a list they then assert is empty. `test_deadmans_switch.py`'s
`_isolate` fixture neutralises six other `run_cycle` checks *by name* and never grew a seventh
entry when the digest landed (G-N4, 2026-08-12).

Reproduced deliberately, forcing only the condition "digest due with something pending" and
touching no real state:

```
27 failed, 27 passed in 0.35s
```

— a superset of the 22 the daemon reported.

**Why the daemon sees it and a hand run does not.** `DIGEST_INTERVAL_SECONDS` is 6h and the
high-water mark advances **only on a confirmed delivery** (G-N5), so the queue is due for a short
window a day — and stays due indefinitely if that send is dropped or rate-limited. The daemon
spawns this pytest from *inside* `run_cycle`, at line 743, **before** its own flush at line 745:
for the whole ~10-minute subprocess the pending entries are still there for the child's tests to
flush. This is the "a control that must win a race has the weather as its subject" class, and it
is why the signal flapped (red 02:31, green 03:36, red from 06:42) before sticking.

## The repair — class, not instance

The pin is the **eighth** instance of a class `tests/background/conftest.py` already fixes seven
times (publish-gate wedge, director axes, blocked mints, operational signal, gap ledger, product
interleave, stall tracker). Fixing it inside `test_deadmans_switch.py::_isolate` would have been
the instance fix and would have gone stale again at the ninth check, so `QUEUE_FILE` and
`STATE_FILE` are pinned at absent tmp paths for the **whole directory**: empty queue ⇒ `pending()`
empty ⇒ `flush()` returns None without sending, whatever the clock says.
`test_notification_digest.py`'s own `store` fixture sets both paths in its body, which runs after
this one and therefore still wins — the digest's own R15 tests are untouched (88 passed).

**R15, both directions**, in `test_deadmans_switch.py`:
- `test_a_due_digest_does_not_leak_into_this_files_ntfy_assertions` — clock forced fully due
  (asserted, not assumed), `run_cycle` still silent.
- `test_the_digest_pin_fires_when_it_is_bypassed` — restore a due clock over a non-empty queue and
  the digest reaches `send_ntfy` through `run_cycle`. If this ever passes green *without* the
  bypass, the pin has stopped being load-bearing and the silent test proves nothing.

## What this cost, and the generalisable bit

Nine hourly pages, ~9h of a PRIORITY-ZERO lane outranking every product lane, over a suite that
was green the whole time. **A signal whose runner is also its subject can page on its own
side effects.** The deadman runs the suite that tests the deadman, from inside the cycle the
suite calls — the one arrangement where the instrument's mid-flight state is visible to the
measurement. Worth a standing question at any new always-on check: *does anything this daemon
does between spawning the suite and finishing its own cycle appear in that suite's assertions?*
