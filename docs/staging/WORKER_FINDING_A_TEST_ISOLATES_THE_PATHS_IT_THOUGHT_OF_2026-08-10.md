# [WORKER-FINDING] A test isolates the state paths it thought of, so every new one re-opens the leak (2026-08-10)

**Severity:** LATENT · **Lane:** H_harness

**Class:** test-isolation-by-enumeration. **Status:** one instance fixed in passing (it was in the
drawn atom's blast radius); the CLASS is unfixed and wants a mechanism. **Not fixed on sight** per
SELF-INTERRUPT DISCIPLINE.

## Observed, with evidence

While building `H42_wedge_suspect_list_rederived_from_the_red`, the publish-gate recorder gained a
second state path (`docs/observability/.wedge_suspect_hit_rate.json`). Running
`tests/background/test_episode_monotonic_guard.py` immediately wrote it **into the live tree**:

```
$ git status --porcelain docs/observability/.wedge_suspect_hit_rate.json
?? docs/observability/.wedge_suspect_hit_rate.json
$ cat docs/observability/.wedge_suspect_hit_rate.json
{"episodes": [{"blocking_tests": ["FAILED tests/tools/test_interim_bypass_retirement.py::..."],
  "closed_at": 2000.0, "hit": true, "suspects": 1}]}
```

`closed_at: 2000.0` is a test clock. The file was written by
`test_a_drained_queue_does_close_the_episode`, which drives the REAL
`record_publish_gate_success`. It had isolated `PUBLISH_GATE_STATE_FILE` and `STAGING_DIR` — and
nothing else, because those were the two the test needed at the time it was written.

Worse than a dirty tree: the leaked entry read back as a genuine measurement. A live
`suspect_hit_rate_phrase()` call reported `SUSPECT HIT RATE: 1/1` off a row no episode produced.
**A test manufactured the evidence a control reports on.**

## Why it is a class and not an instance

Isolation is written as an ENUMERATION of the paths a test happened to need, so it is correct only
against the code as it stood the day the test was written. Every state path added to a recorder
later silently escapes every test that drives it. The same shape is latent anywhere a test drives a
real writer: `.publish_gate_state.json`, `.last_gate_blocking_tests.json`,
`.operational_layer_signal.json`, `.run_marker_sweep_state.json`, `action_needed_register.json` all
have tests that drive their writers directly.

It is the fail-open direction of test isolation: the test still PASSES while leaking, so nothing
reports it. It surfaced here only because a human ran `git status` on an unrelated question.

## The candidate fix, and the recommendation

1. **Keep enumerating, more carefully.** Rejected — that is the thing that just failed.
2. **RECOMMENDED: a conftest-level autouse guard that FAILS any test which creates or modifies a
   file under `docs/observability/` (or any tracked state path) during the test.** Mechanism, not
   exhortation: it catches the NEXT new state path with no author having to think of it, and it
   fails loudly instead of leaking quietly. Needs a narrow, named allowlist for the handful of
   tests that legitimately assert on a live artefact, each with a reason — the same shape as the
   self-clearing-alarm dispositions.
3. A pre-commit check on untracked `docs/observability/` dotfiles — weaker: it catches the leak
   after the fact and only when someone commits.

R15 on the guard itself: a mutation that lets a write through must kill a named test, and the guard
must be shown firing on the real 2026-08-10 leak reproduced from git history.

## Instance already closed

`tests/background/test_episode_monotonic_guard.py` now carries an autouse fixture covering every
path the recorder is known to touch, and the leaked file was deleted. That closes the instance and
nothing else — the next state path added to any recorder re-opens the class.
