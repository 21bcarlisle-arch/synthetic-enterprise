**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# RESULT — the `-` on the units' `ExecStartPre` costs NO detection, because systemd records the failing exit under `ignore_errors=yes` anyway; so the second leg of the drift item is refuted, not deferred

Class: `controls_that_cannot_fail`. Written 2026-09-25 while holding
`boot-sha-drift-reads-zero-stale-over-one-resolvable-daemon`. **Not a finding:** nothing is
broken. What is recorded here is a remedy the delivery seat has carried for four stretches,
now measured and dropped.

## What the item asked for

> *"Once a unit demonstrably stamps, strip the `-` prefix from that ONE unit's `ExecStartPre` in
> `background/generate_units.py:53` and prove a deliberately broken stamper command makes its
> start FAIL. One unit, not twelve."*

and its stated reason for the four deferrals was **outage risk** — "the risk of a second outage
while the publisher was dark". That reason was never the load-bearing one, and treating it as
load-bearing is why the leg survived four stretches instead of being settled in ten minutes.

## Measured, on this box, just now

A transient user unit with a `-`-prefixed `ExecStartPre` that exits 7:

```
$ systemd-run --user --unit=se-stamper-probe-N \
      --property="ExecStartPre=-/bin/sh -c 'exit 7'" /bin/sleep 3
$ systemctl --user show se-stamper-probe-N.service -p ExecStartPre --value
{ path=/bin/sh ; argv[]=/bin/sh -c exit 7 ; ignore_errors=yes ;
  start_time=[Fri 2026-09-25 21:40:12 BST] ; stop_time=[Fri 2026-09-25 21:40:12 BST] ;
  pid=789383 ; code=exited ; status=7 }
$ systemctl --user show se-stamper-probe-N.service -p ActiveState --value
active
```

**`status=7` is recorded, in full, WITH `ignore_errors=yes`, and the unit still started.**

## Why that settles it

`loaded_code_drift`'s fifth rule (`stamper-failed`, landed 2026-09-25) reads exactly that
`status` field, through `unit_stamper_run` → `stamper_record` → `parse_exec_records`. So:

| | detection of a stamper exiting non-zero | cost |
|---|---|---|
| `ExecStartPre=-…` (today) | `unresolved: stamper-failed` | none |
| `ExecStartPre=…` (the ask) | `unresolved: stamper-failed`, **and** the daemon does not start | one outage per stamper bug |

The strip is **strictly dominated**. It adds no information the fifth rule does not already
have; it only converts a recorded status into a dead daemon.

And it would not have caught the defect it was minted for. The twenty-day outage
(2026-09-04 → 2026-09-24, `3ecf355d8` deleting `boot_sha.__main__`) **exited 0 throughout** —
`python3 -m background.boot_sha <session>` on a module with no `__main__` imports and returns 0.
A fail-closed `ExecStartPre` passes a command that exits 0 and writes nothing exactly as an
ignore-errors one does. The `-` was never what hid it; the absence of any check that RAN the
declared command was, and `test_the_units_own_declared_stamp_command_stamps` is that check.

## And the first leg is what makes the second unnecessary

Before today, a `stamper-failed` row landed in `unresolved` and `stale` stayed `[]`, so the
fleet still read `stale 0` — which is the case for wanting a refusal loud enough to be an
outage. With the denominator published (this stretch's landing), a failed stamper now shrinks
`graded`: the headline reads `0 stale of 10 graded, 11 observed` and the reader can see the
hole. **The honest denominator is the remedy the `-` strip was a proxy for.**

## What was built instead

One control, in `tests/background/test_boot_sha_deployment.py`, keyed to the property the
refutation rests on rather than to today's systemd: two transient units running the REAL
declared stamper command, one with a deliberately broken argument and one with a valid session,
both `-`-prefixed, graded through the production `unit_stamper_run`. If a future systemd stops
recording `status` under `ignore_errors`, that control reds and this decision is re-opened by
the machine rather than by someone remembering.

## The prediction, filed beside its result

The item predicted *"one unit refuses to start on a broken stamper"* as the finish line. It is
wrong, and it was wrong when written: the finish line it was reaching for is *"a broken stamper
is visible to a reader"*, and that is reached without any unit refusing anything. Kept here
rather than quietly revised.
