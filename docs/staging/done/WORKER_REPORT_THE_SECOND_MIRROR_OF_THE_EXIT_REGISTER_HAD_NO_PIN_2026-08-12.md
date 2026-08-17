# [WORKER-REPORT] The second mirror of the exit-code register had no drift pin (2026-08-12)

**Severity:** RECORDED · **Lane:** H_harness
**Drawn as:** PUBLISH-GATE WEDGE self-refill, RUNG 1 (UNWEDGE_PUBLISH_PRIORITY_ZERO 2026-07-23).
Episode: 206 consecutive failures, ~4772 min wedged, no pass at HEAD `b74357282`.

## The red was already repaired before this tick drew it

The alarm's named blocking test —
`tests/background/test_staging_archive_policy.py::test_process_run_complete_still_sees_a_duplicate_after_the_sweep`
— **passes at HEAD**, observed:

```
$ SIM_FAST_MODE=1 python3 -m pytest tests/background/test_staging_archive_policy.py -q
29 passed in 0.13s
```

The repair landed in `83f80e0ce` at **21:59:42 UTC**. The newest recorded failure is at
**21:59:27 UTC** — 15 seconds earlier. All five in-window failures predate the fix:

| failure ts (UTC) | commit | ancestor of HEAD |
|---|---|---|
| 21:09:17 | `ad9d44186` | yes |
| 21:20:03 | `ad9d44186` | yes |
| 21:34:51 | `765246957` | yes |
| 21:48:47 | `1386876c2` | yes |
| 21:59:27 | `ad9d44186` | yes |

**This was NOT the phantom-ancestry class** (`_gate_pass_supersedes_failures`, added earlier the
same day) and that helper was not at fault. The wedge was genuine: `.last_tested_hash` is
`7a9bf56be`, whose pass was stamped at **20:28 UTC**, i.e. genuinely *before* every failure above.
The detector's verdict was correct on the evidence it had. The state simply had not yet seen a
green, because no gate run had completed since the repair — one was in flight at 22:04 UTC at the
fixed HEAD while this tick ran.

## What was actually left open — the class, not the instance

The 19th wedge's cause (`WORKER_REPORT_THE_WEDGES_RED_WAS_A_SIBLING_TESTS_STALE_PIN`) was **a
numeric literal standing in for a property**: a sibling test pinned `assert rc == 0` as a proxy for
"a duplicate is not an error", and nobody updated it when the duplicate path was given its own
exit code `76` that morning. The instance was fixed by asserting the *named register*
(`EXIT_NOTHING_PUBLISHED` / `NO_PUBLISH_EXIT_CODES`).

R10 says an absurdity-class defect may not be closed with an instance fix. Auditing every mirror of
that register found **the class was still open in a second place**:

* `background/background_worker.py` mirrors the codes as literals (deliberately — no import-time
  dependency on the publish stack) and **is** pinned, by
  `test_the_worker_mirror_constant_cannot_drift`.
* `background/sim_runner.py` mirrored the same two codes as **bare inline literals**
  (`if rc == 75:` / `elif rc == 76:`, the constant named only in a trailing comment) and had **no
  pin at all**. Nothing in `tests/` referenced them. A renumber of the register would have left
  sim_runner — the steady-state publisher — silently misclassifying a duplicate as a hard failure
  and feeding a false red into this very wedge detector.

## The fix

* `background/sim_runner.py`: both codes are now named module constants (`EXIT_LOCK_SKIPPED`,
  `EXIT_NOTHING_PUBLISHED`) mirroring the register, and the branch reads them.
* `tests/background/test_a_duplicate_marker_is_not_a_publish.py::test_the_runner_mirror_constants_cannot_drift`:
  the missing pin, sitting beside the worker's. It asserts value equality **and** that the branch
  actually reads the mirror — a literal left inline would satisfy the equality alone while being
  unreachable from it.

**R15, mutation-proven both ways** (observed this tick):

| mutation | result |
|---|---|
| `EXIT_NOTHING_PUBLISHED = 76` → `77` in sim_runner | **FAILED** (line 172) |
| branch reverted to inline `elif rc == 76:` | **FAILED** (line 178) |
| restored | `1 passed` |

Affected suites green together: `test_a_duplicate_marker_is_not_a_publish.py`,
`test_sim_runner_publish_gate_outcome.py`, `test_staging_archive_policy.py` — **52 passed**.

## Cited finding, disposed

`WORKER_FINDING_A_REPO_WIDE_CENSUS_IS_NOT_DECOMPOSABLE_BY_PATHSPEC_2026-08-12.md` was re-frozen by
`b74357282` before this tick, with the provenance note stating it was checked against this episode
and is **not** its cause. Verified in the file; disposition unchanged (QUEUED, LATENT, backlog). It
is not re-drawn here.

## Related

- `feedback_giving_a_door_its_own_exit_code_reds_a_numeric_pin_in_another_file` — the same rule,
  which this closes the remaining half of: assert the named register, never the literal.
- `feedback_a_head_keyed_staleness_check_is_unsatisfiable_and_self_perpetuating` — explicitly
  **excluded** as the cause here, on the ancestry evidence above.
