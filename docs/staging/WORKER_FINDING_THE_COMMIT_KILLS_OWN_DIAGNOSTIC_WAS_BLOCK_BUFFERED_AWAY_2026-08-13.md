# [WORKER-FINDING] The commit kill's own diagnostic was block-buffered away — seven timeouts named the chain, never the link (2026-08-13)

**Severity:** RECORDED · **Lane:** H_harness · **Status:** the diagnostic is repaired and
landed in this tick; the un-derived deadline it exposes is QUEUED, stated below.
**Discharged:** `tests/background/test_process_run_complete.py::test_the_kills_diagnostic_survives_the_kill_only_when_the_hooks_are_unbuffered`, `tests/background/test_process_run_complete.py::test_the_commit_runs_its_hook_chain_unbuffered`

## How it was found

Drawing `OPS3_first_post_ruling_publish` — "get one publish cycle green". The publish gate
was not the blocker. **The gate passed.** Observed, not inferred
(`docs/observability/sim-runner-log.md`, 2026-08-13):

- `01:04 UTC` gate starts, throwaway HEAD checkout, scope resolves to **138 blocking test
  files** from 6 publish-path sources;
- `01:25 UTC` marker `run_complete_20260813T005523Z.md` moved to `done/`, provenance
  `Verified 2026-08-13T01:25:10Z`, `.last_tested_hash` written (mtime `01:25:10 UTC`) naming
  `433718889` — the commit that was HEAD when the gate started;
- `01:25 UTC` `Committing and pushing (net=£1,526,252)`;
- `01:30 UTC` **`Commit TIMED OUT after 300s (TimeoutExpired) -- the pre-commit hook chain
  outran its deadline. Nothing committed`**.

So the cycle died at `git commit`, on a **stopwatch, not a red**. Meanwhile
`.publish_gate_state.json` still carries `episode_failures: 206` and cites
`test_process_run_complete_still_sees_a_duplicate_after_the_sweep` as the blocking test —
which passes standalone in **0.13s** (29 passed). The cited test is not the cause and has
not been for some time.

## The defect

The timeout handler has promised, since H30, to print
`hook output before the kill (names the SLOW hook)`. **It has never once delivered it.** All
seven commit timeouts in the log (1 on 08-03, 1 on 08-11, 3 on 08-12, 2 on 08-13) took the
fallback branch: `hook output: nothing captured before the kill`.

The capture was not the problem. `subprocess.run(capture_output=True, timeout=N)` *does*
populate `TimeoutExpired.stdout/.stderr` on this platform, and
`child_diagnostics.stderr_tail` already decodes the bytes it hands back undecoded. Measured
directly on this box (python 3.14.4), a child that prints and then hangs:

```
default                -> exc.stdout = None
PYTHONUNBUFFERED=1     -> exc.stdout = b'HOOK: pre_commit_test_gate starting\n'
```

Every link in the chain is `python3 tools/<gate>.py`. Python block-buffers stdout when it is
a pipe rather than a tty, so each hook's progress sat in **that hook's own userspace buffer**
and died with it — the bytes were never on the wire for the kill path to collect. A
diagnostic that exists only on a tty is a diagnostic that is absent from every autonomous
run, which is all of them. This is the R15 FAIL-SILENT pattern one level down from the usual
one: not a control that passes when unavailable, but a control whose *evidence* is
unavailable by construction while the control itself reads healthy.

## The fix that landed

`git commit` is now given an explicit environment carrying `PYTHONUNBUFFERED=1`
(`process_run_complete._commit_hook_env`). git passes its environment to its hooks, so one
call reaches every link. Unbuffering can only make output arrive EARLIER; it cannot change a
hook's verdict, so getting it wrong costs a slightly slower write, never a wrong commit.

R15, both controls proven to FAIL on their own named defect:

- remove `env=_commit_hook_env()` from the `git commit` call → the wiring test fails
  (`git commit must be given an explicit environment`);
- remove `env[GIT_COMMIT_HOOK_ENV_UNBUFFERED] = "1"` from the builder → **both** fail,
  including the real-platform one. That second kill is what makes the platform test not a
  tautology: it drives a real child through real buffering rather than asserting against a
  mock's `stdout` attribute — a mock passes either way, which is exactly why nothing caught
  this for seven kills.

## What is QUEUED, not fixed (self-interrupt discipline)

**`GIT_COMMIT_HOOK_TIMEOUT_SECONDS` is a number of our own, and it has now drifted twice.**
Its own comment records the first drift (30s → 300s, 2026-08-03) in the same words: "the cap
was set when the hooks were trivial and quietly became a publish-blocker as the suite grew:
the deadline is now a property of how many tests exist, not of whether the commit is
healthy." That is the identical class this project already closed one level up, where
`background_worker`'s independent `timeout=900` had drifted below the publisher's own
declared budget and was replaced by `_publisher_deadline_seconds()` — "NOT A NUMBER OF OUR
OWN".

Measured this tick, on a publish-shaped index (130 changed `site/**` + `docs/**` paths):
**`pre_commit_test_gate.select_targets` enlists 119 test files**, and that is before
`site_lane_gate`'s broad branch (`pytest site/`, 27.3s measured) and four further gates. 300s
is at the edge of that, which is exactly why the kill is intermittent and accelerating
(1, 1, 3, 2 per day).

**The fix, when drawn:** derive the commit deadline from the hook chain's own declared cost
the way `_publisher_deadline_seconds()` derives the publisher's, so suite growth moves both
together and no comment has to be trusted to keep them in step. Raising the literal to 600
would buy a week and re-create the defect. **Do not draw this before the unbuffered tail has
named the slow hook on a real kill** — the fix needs to know which link to size against, and
until this tick there was no instrument that could tell us.
