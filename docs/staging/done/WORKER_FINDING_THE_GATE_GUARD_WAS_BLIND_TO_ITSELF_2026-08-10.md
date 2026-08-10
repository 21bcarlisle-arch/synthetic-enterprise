# [WORKER-FINDING] The occupancy guard skipped the one occupant that mattered — itself (2026-08-10)

**Class:** R3 (second false completion on the same component), R15 (a control that could not fire
on its own named defect). **Landed:** the guard fix + its mutation-proven test.

## The observation (observed-with-evidence)

`ModuleNotFoundError: No module named 'tools.test_execution_metric'` wedged the publish gate at
18:25Z. A fix — `process_run_complete._reused_checkout_is_in_use` — landed **19:08 UTC**
(`349f5ac48`). The identical red then came back **twice more**, at **20:18Z** and **20:47Z**.

The module is not missing. It is tracked at every SHA involved, `git archive` exports it, and the
conftest import that fails is correct at HEAD:

```
ab8d19b37  module=PRESENT  conftest imports it
1f9d1a787  module=PRESENT  conftest imports it
22e849600  module=PRESENT  conftest imports it
d5d92ff83  module=PRESENT  conftest imports it
```

**The traceback is the proof of what actually happened.** The line number of that import differs
per commit, so it fingerprints which commit's `conftest.py` was on disk when the traceback
rendered:

| commit | import at line |
|---|---|
| `ab8d19b37`, `1f9d1a787` (the SHAs the failing runs were *recorded against*) | **219** |
| `22b097a1b` | **250** |
| `f42c7f901`, `03f9a5257`, `22e849600` | **265** |

The 20:18Z traceback rendered **line 250**; the 20:47Z traceback rendered **line 265**. Both runs
*started* at a 219 commit. The suite's own source files were replaced, mid-run, with a **later
commit's** content. Nothing here is about any test.

## Why (observed, then closed)

`HEAD` moves every ~5 minutes (the publisher commits provenance banners and derived-artefact
repairs), while one gate suite takes ~20 minutes. The chain:

1. `sim_runner` SIGKILLs the publisher at its deadline (`Auto-process timed out after 1200s`).
2. The gate's pytest is a **grandchild** — it survives, cwd still inside
   `/tmp/publish-gate-head-reused`, and the dead parent's `flock` is **released**. (Already known;
   it is why the guard was written.)
3. That orphaned suite reaches `tests/background/test_publish_gate_head_checkout_is_a_repo.py`,
   whose module-scoped fixture calls `prc._head_checkout()` against the **real**
   `HEAD_CHECKOUT_ROOT` — unlike the sandboxed modules, it does not redirect it — and which is
   **inside the gate's own blocking scope**.
4. The reuse lock is now free, so the call reaches the guard.
5. **The guard skipped `os.getpid()`.** The caller *is* the occupant. It answered `False` about
   itself, and `_refresh_checkout_to` ran `read-tree -u --reset <newer HEAD>` on the directory the
   suite was executing from.

Demonstrated directly, nothing mocked:

```
my cwd           : /tmp/selfblind_probe
guard says in-use: False
```

The 19:08Z fix closed the *next publisher's* half and left the *orphan's own* half open — the half
that fires whenever the publisher is killed, which is the common case here.

## The fix

`_reused_checkout_is_in_use` now treats **self-occupancy as the strongest sighting, not an
exclusion**, and reads it via `os.getcwd()` (no procfs needed, so that half survives a box where
/proc cannot be enumerated). Subdirectory occupancy counts too — a suite's cwd sits below the
checkout root, not on it.

## R15, both directions (mutation, not assertion)

* **With the fix:** 3 occupancy tests pass; the full module is **34 passed**;
  `test_process_run_complete.py` **62 passed**.
* **Mutation** — restore `if pid == os.getpid(): continue`, the exact pre-fix code:
  `test_the_caller_standing_in_the_checkout_is_itself_an_occupant` **FAILS**, while both
  pre-existing occupancy tests still **PASS**. That is precisely why the red survived the 19:08Z
  fix: the controls in place could not see this defect. Source restored, sha256-verified.

## Still open (queued, not fixed on sight — SELF_INTERRUPT_DISCIPLINE)

`test_publish_gate_head_checkout_is_a_repo.py` operates on the **live shared** reused checkout
while `test_publish_gate_subject_is_head.py` redirects `HEAD_CHECKOUT_ROOT` into a sandbox. With
the guard fixed this is now *safe* — it takes the throwaway branch — but it still pays a **190MB
extraction with cold bytecode on every publish cycle**, and it remains a test that mutates
machine-wide state its siblings isolate. Isolating it (without weakening its claim, which is
genuinely about the real subject) is a separate atom, not tonight's fix.
