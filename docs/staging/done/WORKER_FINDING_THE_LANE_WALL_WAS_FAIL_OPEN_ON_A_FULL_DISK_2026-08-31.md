**Severity:** BLOCKING · **Lane:** H_harness · **Epoch:** 3 · **Atom:** `OPS1_process_manifest_reconstruction`

# The lane wall enforced denials only while it could write its diary — an unwritable log turned every denial into an allow

**Found:** 2026-08-31, by a control written to check something else. While isolating 72 tests that
were writing the live denial log, I added `SE_LANE_DENIAL_LOG` to redirect it, and wrote a leg
asserting the obvious safety property: **moving the log cannot change a verdict.** It could.

## What the wall did

`.claude/hooks/lane_wall_hook.py` is the development-time lane wall — it denies a `Read`/`Glob`/
`Grep` that would cross from the supplier lane into `simulation/`, or the other way. It denies by
exiting **2**. Claude Code blocks a tool call on exit 2 and does not block on exit 1.

Every one of the four `return 2` sites in `main()` is preceded by `_log_denial(...)`, and that
function was:

```python
def _log_denial(lane, tool_name, path) -> None:
    DENIAL_LOG.parent.mkdir(parents=True, exist_ok=True)
    ...
    with DENIAL_LOG.open("a") as f:
        f.write(json.dumps(entry) + "\n")
```

No `try`. An `OSError` propagates out of `main()`, the process dies with a traceback and **exit 1**,
and the call it was refusing goes through.

## Measured, not argued

With `SE_LANE=supplier` and the payload `Read sim/forward_curve.py` — a call the wall exists to
refuse:

| `SE_LANE_DENIAL_LOG` | exit code | effect |
|---|---|---|
| a writable path | **2** | DENIED |
| unset (the real log) | **2** | DENIED |
| `/proc/definitely/not/writable.jsonl` | **1** | **ALLOWED** |

The allowed call is identical in every respect except whether a *diary entry* could be written.

## The conditions that reach it, none of them exotic — and one of them happened the same evening

**`/tmp` on this machine filled while this finding was being written.** Three test suites running
concurrently exhausted a 12 GB tmpfs, and for several minutes every process on the box that tried to
write a file failed with ENOSPC. That is precisely the state in which a control whose refusal path
writes a log stops refusing. It is not a scenario; it is Monday evening.

## The conditions that reach it, none of them exotic

A read-only mount. A full disk — and `background/disk_headroom.py` exists because this machine has
run out of space before. A permissions change on `docs/observability/`. A `docs/` that has not been
created yet in a fresh checkout. In each case the wall reports nothing and stops working, and the
only artefact is a traceback on a hook's stderr.

## Why it survived

**It is the fail-closed rule inverted, and the inversion is what made it invisible.** This project
audits controls that *refuse on input they could not read* — that class was found three times in one
day in August. Nobody had asked the mirror question: which controls **depend on a write succeeding
in order to enforce**? A refusal is the product; the log is a note about it, and the note was
load-bearing.

The 73 tests over this hook all ran with a writable log, so none of them could see it. The leg that
found it was not about logging at all — it was checking that a new env var could not become a
fail-open door. It found the fail-open door that was already there.

## Fixed

`_log_denial` now wraps the write and, on `OSError`, writes one line to **stderr** — the channel the
user is already reading, because the denial message itself follows one line later. The wall enforces;
the audit trail records a gap in itself.

`tests/tools/test_lane_wall_hook.py::TestLaneWallHook::test_the_denial_log_redirect_cannot_change_a_verdict`
holds it, across three settings and both a denied and an allowed payload. Mutation: remove the
`try` and it fires.

## A SECOND INSTANCE, found the same hour, in a completely different control

`background/process_run_complete.record_publish_gate_success` — the function that clears the
publish-gate wedge after a clean publish — had the identical shape:

```python
if episode_closed and had_state:
    _measure_suspect_list(prev, ...)          # writes .wedge_suspect_hit_rate.json
_write_publish_gate_state({...})              # <- the actual clear, one line later
```

`_measure_suspect_list` writes a **diagnostic** about how good this pipeline's guesses were. It sat
un-wrapped inside the function's outer `except`, so a failure to write that side-file abandoned the
whole function and the clear never ran. The observable behaviour of *"the hit-rate file is
unwritable"* was **the publish gate stays wedged**, with `episode_failures` still standing and a
swallowed log line as the only trace.

Found because three publish-gate tests began reporting *"a clean publish must CLEAR the wedge
streak"* once the test-isolation sink started refusing that write. The tests were right, and they
had been describing a real failure mode nobody had reached yet.

## The census, run rather than filed

The obvious next move was to write "a census of this class is owed" and stop. It is cheap enough to
just do, so it was done: an AST pass over `.claude/hooks/`, `background/`, `tools/`,
`company/compliance/` and `saas/` for functions that can REFUSE (return a non-zero rc, or raise a
`*Refused`/`*Blocked`/`*Violation`) and contain a **file** write outside any `try`.

| | |
|---|---|
| refusing functions with an unguarded file write | **32** |
| …of those, inside a HOOK (blocks a tool call by exit code) | **0** |
| …inside a gate / ratchet / guard | 4, and all four are false positives |

The four are two `str.replace` calls the scanner could not tell from `os.replace`, and two report
tools whose artefact IS their product — a census tool that cannot write its census should fail
loudly, and does.

**So the class is real and small, and its two live instances were the two already found.** That is
worth more than the open-ended census I was about to file: the answer is *"two, both fixed"*, not
*"unknown, someone should look"*.

What the scanner cannot see, and is therefore still owed as judgement rather than as a sweep: a
write hidden behind a helper the refusing function calls (`_log_denial` itself would have been
invisible to this pass — it was found by a test, not by a scan). The heuristic bounds the shallow
form of the class; it does not close it.
