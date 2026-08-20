**Severity:** LATENT · **Lane:** H_harness

# FINDING — the operational-layer signal has its own suite wall, sits at half the tight-band threshold against it, and is the one wall PW3 does not watch — and its timeout branch is fail-silent, not fail-closed

**Found by:** the RUNG 1b operational-layer persistent-red draw, 2026-08-20 ~02:46Z. The draw
itself discharged GREEN — see below — and this is the second-order defect the green run exposed.
**Class:** R15 FAIL-SILENT (an unavailable check is a FAILED check), plus a control whose subject
is narrower than its own stated rationale. Sibling-half of
`PW3_suite_duration_watch`, which closed exactly this shape for the publish gate and stopped there.

## The draw that produced this: DISCHARGED

The RUNG 1b persistent-red is **cleared, by measurement, not by assumption**. Running the exact
argv from `background/process_run_complete.py::operational_layer_pytest_argv`:

```
1148 passed, 26698 deselected, 1 xfailed, 4 warnings in 1496.97s (0:24:56)
```

The four reds' cause was already diagnosed and repaired by the preceding tick — see
`WORKER_FINDING_A_SALVAGE_PARKED_THE_PRODUCER_HALF_AND_LEFT_THE_CONSUMER_HALF_IN_THE_TREE_2026-08-20.md`
(a KNIFE3 step-39 salvage parked the producer `offer_framing_for` and left two importing test
files in the tree, so pytest failed at COLLECTION and a collection error is not scoped by `-m`).
This run confirms that repair **held**: both cited paths are resolved
(`tests/company/interfaces/test_the_run_holds_no_policy.py` is gone from the tree,
`tests/company/policy/test_policy_field_consumption.py` is tracked, clean at HEAD, and passing),
and no test in the marker-selected suite fails. Nothing further was needed at HEAD.

## The one-line defect

The operational-layer signal runs its suite under a hard `timeout=1800`; that suite now measures
**1496.97s**, i.e. **16.8% headroom** — less than half the `TIGHT_HEADROOM = 0.34` band that
`background/suite_duration_watch.py` exists to alarm on — and the watch has exactly one caller,
the publish gate, so this wall is measured by nothing and its crossing would be reported as
neither green nor red.

## Observed, with evidence

Every claim below is `observed-with-evidence` (R9) unless labelled otherwise.

**The ceiling.** `background/process_run_complete.py:616` —
`subprocess.run(argv, cwd=str(PROJECT_DIR), timeout=1800, capture_output=True, text=True)`.
This is the runner used whenever `run_operational_layer_signal` is called without an injected
`runner`, i.e. on every hourly check.

**The measured duration.** 1496.97s, quoted above, from the suite's own trailer.

**The headroom, computed by the project's own function.**

```
>>> from background.suite_duration_watch import headroom
>>> headroom(1496.97, 1800)
0.16835
```

`TIGHT_HEADROOM = 0.34`, `RECOVERED_HEADROOM = 0.45` (`background/suite_duration_watch.py:65-69`).
0.168 is **below half** the tight band. Were this wall watched, it would be paging now.

**Nothing watches it.** `grep -rn "suite_duration_watch\|record_gate_run" background/ tools/`
returns three call sites and no fourth: `process_run_complete.py:1996` (`record_gate_run(elapsed,
GATE_SUITE_TIMEOUT_SECONDS, git_hash, outcome)` — the **publish gate**), and
`daily_self_note.py:436` (a reader). The series file is named for its single subject:
`SERIES_PATH = docs/observability/publish_gate_duration.jsonl`. The operational signal never
records a duration, so there is no series to trend and no ceiling to compare against.

**The crossing would be fail-SILENT, which is the direction PW3 explicitly closed for the gate.**
`subprocess.run(..., timeout=1800)` raises `subprocess.TimeoutExpired`. That raise is caught by
the function's outer handler (`background/process_run_complete.py:698-700`):

```python
    except Exception as exc:
        log_fn("Operational-layer signal check error (swallowed): {}".format(exc))
        return {"ran": False, "reason": "error", "error": str(exc)}
```

`_write_operational_layer_state` is never reached. So on a timeout the signal writes **no state at
all**: `consecutive_red` does not advance, `consecutive_green` does not advance, `last_run_ts` is
not refreshed. The last recorded verdict stands unchanged and unaged, indefinitely, while the
check is in fact no longer completing. A reader of
`docs/observability/.operational_layer_signal.json` cannot distinguish "green, checked an hour
ago" from "hasn't completed a check since".

**This is a named regression of a closed defect, in a sibling.** `suite_duration_watch.py`'s own
header records the original: *"The publish-gate suite reached 612.94s against a 600s timeout. The
timeout branch returned 'passed', so the gate could not pass — it could only time out and publish
unverified. That fail-open is closed (1fd85cb27: a timeout now BLOCKS)."* The gate's ceiling has
since been re-derived **five** times (600 → 1800 → 2600 → 2900 → 3600, per the comment block at
`process_run_complete.py:2151-2161`). The operational signal's ceiling is still the **1800** of
that second re-derivation, and its suite has grown underneath it the same way.

**Inferred (labelled):** that the four reds ran to completion rather than timing out is consistent
with the recorded digests — they were 8.70s collection errors, which is why the streak advanced at
all. A *slow* red, unlike a *broken* red, would have gone mute instead of paging. I have not
observed a timeout occurring; the claim here is about the branch's behaviour if it does, read from
the code, not from an incident.

## Why the existing control does not cover it

Not an oversight in PW3 so much as a scope statement that outlived its subject. PW3 was minted
from a publish-gate wedge and its whole vocabulary is the gate's: the series path, the caller, and
the `note_line` reader all say "publish gate". The operational-layer signal was *deliberately
decoupled* from the publish gate — its docstring is emphatic that it "never runs
`publish_gate_pytest_argv()`, never reads/writes `PUBLISH_GATE_STATE_FILE`, and its result cannot
reach `commit_and_push_if_changed`". That decoupling is correct and is the reason the signal
cannot wedge the live site. It also, silently, decoupled the signal from the one control that
watches suites approaching walls. **The independence that protects the site is the same
independence that lost the instrumentation.**

## What this argues for

Queued, not built — SELF-INTERRUPT DISCIPLINE: this is my own finding, the machine is not blocked
(the suite is green and the signal will self-clear on the next hourly check), so it goes on the
queue rather than being fixed on sight. Three things, cheapest first:

1. **Make the timeout fail CLOSED, not silent.** Catch `subprocess.TimeoutExpired` distinctly from
   the generic handler and record it as a **red** with a digest naming the timeout — an
   unavailable check is a failed check (R15). This is the smallest change and it is
   mutation-testable both ways: stub a runner that raises `TimeoutExpired`, assert
   `consecutive_red` advances and the digest names the ceiling.

2. **Give the signal's wall the watch that already exists.** `suite_duration_watch.record()` takes
   `(duration, ceiling, git_hash, outcome)` and is already subject-agnostic in its arithmetic —
   only `SERIES_PATH` and the caller are gate-specific. A second series keyed to the operational
   signal costs one call site and one path constant, and reuses the bands, hysteresis and R15
   tests unchanged. Note the R12 clause in that module applies with full force here: a tight
   headroom is a signal to raise the ceiling **with the measurement behind it**, never to deselect
   or re-tier tests to make the number green.

3. **Then re-derive 1800.** At 1496.97s the ceiling is 1.20x the measured runtime; the gate's own
   convention is 3x. That is a number to set from a cold-checkout measurement, after (1) and (2)
   make its approach visible — deriving it now, from one warm run, would repeat the guess that has
   already been re-made five times on the sibling.

Doing (3) without (1) and (2) would be the exact error the sibling's header describes: moving the
wall while nothing watches the approach, so the next crossing is discovered rather than planned.
