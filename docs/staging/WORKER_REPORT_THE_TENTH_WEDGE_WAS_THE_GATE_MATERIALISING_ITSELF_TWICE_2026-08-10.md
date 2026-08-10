# WORKER REPORT — the episode-4 wedge at HEAD `88181441a` was the gate materialising its own subject a second time, on RAM

**Drawn:** 2026-08-10, scheduled worker tick, RUNG 1 / PRIORITY ZERO (publish-gate wedge self-refill).
**Failing test, named from the log rather than inferred (R9):**
`tests/background/test_publish_gate_head_checkout_is_a_repo.py::test_the_checkout_is_either_reused_or_removed_never_leaked`
(`docs/observability/sim-runner-log.md:140583`, the 12:29 UTC cycle, `-x` so it stopped the suite at
`1 failed, 792 passed, 1 skipped, 1107 deselected`).

## The cause, measured — `observed-with-evidence` unless labelled

**Observed.** The captured stdout of the failing test carries the whole diagnosis:

```
- [12:26 UTC] Publish gate: the reused HEAD checkout is held by another publisher
              -- using a throwaway checkout for this cycle (correct, but cold).
- [12:29 UTC] Publish gate: could not make the HEAD checkout a git repo:
              Command '['git', 'read-tree', '70d23b088...']' timed out after 120 seconds
```

`_make_checkout_a_repo` returned False → `_head_checkout()` yielded None → `assert path is not None`
failed. **The fail-closed branch worked exactly as designed** (R15: an unavailable check is a failed
check). Nothing here says a test of HEAD's content failed, and nothing says HEAD is unpublishable.

**Observed — why a 0.02s operation took >120s.** The gate's checkout root is `tempfile.gettempdir()`
= `/tmp`, which on this machine is **tmpfs, i.e. RAM**. At the failure:

| measurement | value |
|---|---|
| `/tmp` (tmpfs) | 7.8G size, **5.5G used**, 2.4G free |
| RAM | 15.9G total, **3.0G available** |
| swap | **4074 / 4096 MB used — 21MB free** |
| live full pytest suites | **2** (pids 2721519, 2727777) + `run_annual_report` |
| publish-gate checkouts resident in tmpfs | 2 × 190M |

**Observed — the structural part, and the actual defect.** When this module runs *inside* the publish
gate, the gate itself holds the reuse lock, so `_head_checkout()` can only take the **throwaway**
branch. Confirmed live at 12:38 UTC while writing this: an independent call logged
`the reused HEAD checkout is held by another publisher`. So every gate cycle paid **two** further full
190MB extractions of HEAD — the module fixture's, and this test's — on top of the 190MB it was already
running from, on RAM, with swap exhausted. The second `git read-tree` is the one that blew its timeout.

**Inferred (not fixed here):** the `HEAD_CHECKOUT_MIN_FREE_MB = 400` pre-flight reads *filesystem*
free space. On tmpfs that number is not the binding constraint — memory is — so the pre-flight passed
(2.4G free) while the machine had 21MB of swap left. That is the resource-headroom class already flagged
in `ADVISOR_FLAG_RESOURCE_HEADROOM_GOVERNOR_2026-08-09.md`, and the misclassification of this timeout as
`kind="test_regression"` is `WORKER_FINDING_AN_OOM_KILL_IS_RECORDED_AS_A_TEST_REGRESSION_2026-08-10.md`.
Both are queued, not fixed on sight (SELF_INTERRUPT_DISCIPLINE) — neither blocks publishing once the
second materialisation is gone.

## What was NOT done, and why

**Not deselected.** Taking `@pytest.mark.operational` to stop this blocking is precisely the fail-open
channel the containment guard exists to prevent (`feedback_deselecting_a_marker_orphans_the_tier` §3).
The property is real and belongs in the content gate; its *cost* was the defect.

**Not a raised timeout.** 120 → 300s is repairing the threshold, not the statistic. The operation is
measured at 0.02s when the machine is not thrashing; a timeout that has to absorb swap exhaustion is
not a timeout.

## The fix — landed

`test_the_checkout_is_either_reused_or_removed_never_leaked` stubs `_materialise_head_into` to a bare
directory. The property under test is the **contextmanager's lifecycle** — sweep, disk pre-flight, SHA,
lock, `mkdtemp`, `finally: rmtree`, and the reused-vs-throwaway naming branch — and none of that is a
property of the extracted tree. The whole branch and cleanup path stays real; only the 190MB copy goes.
The module fixture still pays **one** real materialisation, which is what the tree-shaped assertions
(`rev-parse`, `blame`, `status --porcelain`) genuinely need.

**Result:** the four fixture-free tests in the module run in **1.27s** (`4 passed, 5 deselected`); the
timeout-prone second `read-tree` no longer exists in a gate cycle, and the gate's tmpfs high-water
drops by 190MB per cycle.

**R15, the control still fires on its own defect.** Mutation — neuter the `shutil.rmtree` in
`_head_checkout`'s `finally`, keeping the stub:

```
throwaway: /tmp/publish-gate-head-kdiwmon0 still exists after exit -> True
MUTATION CAUGHT (test would fail)
```

The test also now asserts the stub was *used*, so a silent regression back to the expensive form
cannot pass unnoticed.

## Honest residue

- The module fixture's single remaining materialisation can fail the same way under the same memory
  pressure; the exposure is halved, not closed. Closing it is the headroom-governor work above, which
  is the right home for it — a gate that cannot tell "the machine is out of RAM" from "HEAD is red"
  will keep producing this shape.
- This report closes the tenth wedge cause of episode 4. It does not claim the gate is green: the next
  cycle's full suite is the only thing that can say that, and it had not completed when this was
  written.
