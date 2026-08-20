**Severity:** LATENT · **Lane:** H_harness

# FINDING — the operational suite writes fabricated LOOP BROKEN alarms into the live deadman log, and the suite that writes them also blocks the deadman's own cycle for 26 minutes while doing it

**Found by:** the RUNG 1b operational-layer persistent-red draw, 2026-08-20 ~03:00Z. The draw
itself **discharged GREEN** (see below); this is the second-order defect the green run exposed.
**Class:** test isolation — *a test isolates the paths it thought of*
(`WORKER_FINDING_A_TEST_ISOLATES_THE_PATHS_IT_THOUGHT_OF_2026-08-10.md`). New instance, so R10
applies: the closure is the class, not this file.
**Rank requested:** backlog. Nothing here is blocking.

## The draw that produced this: DISCHARGED

The RUNG 1b persistent-red is **cleared, by the signal's own state write, not by assumption**.
`docs/observability/.operational_layer_signal.json` moved, during this tick, from

```json
{"consecutive_green": 0, "consecutive_red": 4, "last_result": "red",   "last_run_ts": 1787189988.275291}
```
to
```json
{"consecutive_green": 1, "consecutive_red": 0, "last_result": "green", "last_run_ts": 1787193610.5650115}
```

That write was made by the **deadman's own hourly run** (`pytest -m "operational or
join_report_only or scale_report_only"`, PID 1441497, child of `deadmans_switch.py` PID 490),
which ran 02:40:10 → 03:06 UTC. Because `consecutive_red` was 4 — at or past
`OPERATIONAL_LAYER_PERSISTENT_RED_THRESHOLD = 2` — the red→green transition took the
`was_persistent_red` branch and paged `[OPERATIONAL LAYER RECOVERED]` itself. **No further NTFY
was sent from this tick**: the recovery page is the transition notice, and a second one would be
exactly the repeat-an-unchanged-status send R5 forbids.

### A note on the doorbell's own instruction (observed, and acted on)

The doorbell said to run `run_operational_layer_signal(force=True)` first. Doing so **started a
second, concurrent 25-minute run of the same suite**: `force=True` bypasses
`_operational_layer_check_due`, which is the only thing standing between two runs, and
`run_operational_layer_signal` takes **no lock at all** (`_run_lock` in that module guards the
heavy publish pipeline at L4923 and is never taken by the signal). Both runs were live
simultaneously — the deadman's PID 1441497 and the forced PID 1478373 — against a hard
`timeout=1800` on a suite that measures 1496.97s, i.e. the **16.8% headroom** named in
`WORKER_FINDING_THE_OPERATIONAL_SIGNAL_HAS_ITS_OWN_WALL_AND_NOTHING_WATCHES_IT_2026-08-20.md`.
Two concurrent runs plus two concurrent non-operational suites is exactly the contention that
crosses that wall — and on a crossing, `TimeoutExpired` falls into the generic handler and
`_write_operational_layer_state` is never reached, so **neither** run records a verdict and the
stale RED stands for another hour. The forced run was therefore **killed**, and the deadman's
in-flight run — the one holding the authority to write the state — was allowed to finish. It did,
and it is what discharged the draw. *The doorbell's re-run instruction should check for an
in-flight run before forcing one.*

## The one-line defect

`tests/background/test_transport_failure_loud.py` is `pytest.mark.operational`, calls the **real**
`deadmans_switch._check_pull_loop_transport()`, and isolates the loud side effects (`send_ntfy`,
`TRANSITIONS_FILE`) but not the quiet one — `log()` — which appends unconditionally to the **live**
`docs/observability/deadmans-switch-log.md`. So every operational suite run injects fabricated
`[LOOP BROKEN]` alarm lines into the one record a human reads to diagnose a broken draw loop.

## Observed, with evidence

Every claim below is `observed-with-evidence` (R9) unless labelled otherwise.

**1. The live log carries LOOP BROKEN lines that no deadman cycle produced.** Verbatim, from
`docs/observability/deadmans-switch-log.md`:

```
- [2026-08-20 02:45 UTC] LOOP BROKEN checked (notify-gated): cannot draw: import failed
- [2026-08-20 02:45 UTC] LOOP BROKEN checked (notify-gated): cannot draw: import failed
- [2026-08-20 03:05 UTC] LOOP BROKEN checked (notify-gated): cannot draw: import failed
- [2026-08-20 03:05 UTC] LOOP BROKEN checked (notify-gated): cannot draw: import failed
```

**2. The transport was healthy the whole time.** Run directly at 03:06 UTC:

```
{"status": "HEALTHY_IDLE", "alarm": false,
 "detail": "scheduled-invocation mode -- external timer/path owns continuity ..."}
```

**3. The string is a test literal, not a diagnosis.** In
`tests/background/test_transport_failure_loud.py::test_deadman_fires_loop_broken_and_is_transition_only`:

```python
monkeypatch.setattr(
    R, "evaluate_pull_loop",
    lambda: {"status": "LOOP_BROKEN", "alarm": True, "detail": "cannot draw: import failed"},
)
D._check_pull_loop_transport()   # ← writes a real log line
...
D._check_pull_loop_transport()   # ← and a second one
```

`cannot draw: import failed` is hardcoded there. The test calls the check **twice** (to assert
transition-only paging), which is why the live log shows each fake alarm **doubled** — the
signature that distinguishes the pollution from a real cycle, and the only reason it was
identifiable at all.

**4. The marker puts it in the hourly suite.** `tests/background/test_transport_failure_loud.py:323`:
`pytestmark = pytest.mark.operational`. So this fires once per operational run — hourly.

**5. There is no seam to isolate.** `deadmans_switch.log()` (L131) writes to
`LOG_FILE = PROJECT_DIR / "docs" / "observability" / "deadmans-switch-log.md"` (L75) — an absolute
path resolved at import, opened `"a"`, no injectable sink. The test could not have isolated it
without monkeypatching `LOG_FILE`, and nothing signals that it needs to.

**6. The timestamps line up with the suite, not with the deadman.** Both fake pairs (02:45, 03:05)
fall strictly inside the suite's 02:40:10 → 03:06 UTC window.

## The second half: the deadman goes dark while the suite runs

`run_cycle()` is strictly sequential and single-threaded, and
`_check_operational_layer_signal()` is **7th of 9**, ahead of `_check_content_publishing()` and
`_flush_notification_digest()`. It calls `subprocess.run(..., timeout=1800)` inline. So the whole
safety net stops for as long as the suite takes:

| time (UTC) | what the log shows |
|---|---|
| 02:40 | `FORK ORPHANS`, `WORKTREE UNDECLARED` — then the cycle stops mid-way |
| 02:45, 03:05 | *(fake lines from the suite — not cycles)* |
| 02:50, 02:55, 03:00 | **nothing — no cycle ran** |
| 03:06 | `Work queued (105 file(s)) but commit recent (16min ago) -- not blocked` |

That last line is the late-cycle commit-clock check, and it lands the instant the suite exits: the
02:40 cycle was blocked at check 7 for **26 minutes**. Every prior cycle in the log (00:24 → 02:35,
unbroken at 5-minute spacing) carries that same late line; the 02:40 cycle is the first that does
not.

**Why this only starts now, and why that is the interesting part.** For the four RED checks the
suite failed at *collection* — seconds, not minutes — so the signal returned almost immediately
and the loop stayed responsive. The 01:39:48 UTC run shows exactly that: cycles at 01:40, 01:45,
01:50, 01:55, 02:00, 02:05, all complete. **The repair that turned the operational suite green is
what made the dead-man's switch go dark**, because a green run is a 25-minute run. The blocking
was invisible for precisely as long as the suite was broken.

`POLL_INTERVAL_SECONDS = 300` is a declared 5-minute safety net. Once an hour it is now a
26-minute one, and on a `timeout=1800` crossing it would be a 30-minute one.

## Why this matters (and the cost it already imposed)

The deadman log is diagnostic, not a published surface, so nothing customer-facing is wrong — hence
LATENT. But it is the record consulted when the loop is suspected broken, and it now contains
alarm lines byte-identical in format to real ones, written by the same function, differing only in
that they arrive in pairs. **This tick was itself misled by them**: on seeing a live
`cannot draw: import failed` at 03:05, effort went into diagnosing a broken draw path that has
never existed. That is the concrete cost — the pollution is not inert, it actively produces
misdiagnosis, and it did so within an hour of being written.

It also interacts badly with the blocking half: the suite writes fake *loop-broken* alarms into the
log during the exact window in which it has genuinely stalled the loop that writes that log.

## Disposition — QUEUED, not fixed (SELF-INTERRUPT DISCIPLINE)

Not fixed on sight, deliberately, and not only on principle: two non-operational suites (PIDs
1368026, 1432381) were in flight against this shared tree throughout, and mutating a shared test
module mid-suite is the failure this project has already recorded. Doc-only this tick.

**Candidate closure — class-level, per R10.** The instance fix (monkeypatch `LOG_FILE` in this one
test) is exactly the instance fix R10 refuses. The class is *"an operational test calls a real
daemon function whose logging writes to a live observability artefact."* Two shapes worth costing:

1. **A conftest-level autouse redirect** for the operational marker: point every daemon module's
   `LOG_FILE` at `tmp_path` for the duration of a marked test. Closes the class in one place,
   including the writers nobody has enumerated yet.
2. **A guard that the live logs do not move during a test run** — snapshot the mtime/length of
   `docs/observability/*.md` around the suite and fail if a marked test grew one. This is the R15
   shape: it can fail, it names the offender, and it catches producers 1 would miss if a module
   resolves its path some other way.

1 is the fix; 2 is the control that proves 1 stayed true. Neither is a production behaviour change.

**Separately, and smaller:** the RUNG 1b doorbell should not instruct a bare `force=True` re-run
while the deadman may already be running the same suite — it should skip if a run is in flight, or
the signal should take a lock so a forced run joins rather than duplicates. Recorded here rather
than as its own file because it is the same 26-minute suite and the same wall.

## What this does NOT claim

- Not that the pull-loop transport is broken. It is healthy (§2); that was the misdiagnosis.
- Not that any NTFY was falsely sent. The test isolates `send_ntfy`, so no fake page left the
  machine — the pollution is confined to the log file.
- Not that the deadman's *alarms* were wrong during the dark window, only that they did not run.
  Whether anything needed alarming between 02:40 and 03:06 is unknown and unknowable from here.
