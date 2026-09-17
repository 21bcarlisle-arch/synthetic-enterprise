**Severity:** LATENT · **Lane:** H_harness · **Epoch:** 3 · **Atom:** (Lane 0 delivery — `thirteen-background-controls-are-red-at-head-and-the-gate-selects-none-of-the-changes-that-broke-them`)

# The machine has lost Playwright, so pixel verification cannot run — and the red control saying so is TRUE, which is why I have not touched it

> ## ⚠ REFUTED 2026-09-17, same day, by the next hand — the title is FALSE
>
> **The machine had lost nothing.** The main worktree had Playwright 1.62.0 throughout, and a real
> `chromium.launch()` renders. The red was measured from a LINKED WORKTREE, where `node_modules/` is
> gitignored and so never exists; `npx --no-install` resolves by walking up from cwd, so it found
> nothing. The truncated `["play....0"]` quoted in §1 below is `["playwright@1.63.0"]`, and it
> reproduces on demand by running the identical probe from a worktree.
>
> **§2's feared expensive outcome did not occur and could not have.** The door suites never used
> Playwright — they drive a Node/`vm` harness needing nothing from `node_modules/`. Measured before
> any restore attempt: **807 passed, 38 skipped, 0 failed, and not one skip browser-related.** No
> close in the window inherits doubt from this cause.
>
> **What §2 got right:** relaxing the control to a skip, or mocking the probe, would have been the
> narrowing move. The repair was neither — the probe is now anchored to the tree that holds the
> dependency, so a genuine loss still reds everywhere.
>
> Full working, mutation proof and the one gap left open:
> `SEAT_RESULT_THE_MACHINE_NEVER_LOST_PLAYWRIGHT_AND_THE_PROBE_WAS_ASKING_WHICH_CHECKOUT_IT_STOOD_IN_2026-09-17.md`.
> Kept beside the claim rather than revised: this is the evidence the question was framed before its
> answer was known.

**Filed 2026-09-17, delivery seat.** Found by the full `tests/background/` run behind the Lane 0
thirteen-reds item. **No pre-registration: this was an observation from a run whose purpose was to
enumerate reds, not to test a hypothesis about the environment.**

---

## 1. The instance

```
tests/background/test_health_check.py::TestCheckPixelVerificationCapability
  ::test_returns_none_when_playwright_available   FAILED

assert 'Pixel-verification (Playwright) unavailable: npm error npx canceled due to
        missing packages and no YES option: ["play....0"]' is None
```

`background/health_check.py::_check_pixel_verification_capability` is **working correctly**. It
probes for Playwright, does not find it, and returns a string saying so. The consumer,
`health_check.py:439`, reads that into `pixel_warn`. Everything downstream of the probe behaves as
designed.

**What is false is the test's premise, and it is a premise about the world rather than about the
code.** Its own comment reads: *"Real invocation — this environment genuinely has Playwright
available (proven 2026-07-11 via a live pixel check on poesys.net)"*. That was true on 2026-07-11
and is not true today. The control is pinned to an ENVIRONMENT FACT with a two-month-old proof.

## 2. Why I left it red

This is the one case where the drawn item's framing — *"a red control is not controlling"* — points
the wrong way, so it is worth saying out loud rather than acting on the framing.

**The red is the true reading.** Relaxing it to a skip, or mocking the probe, would be the
narrowing-for-a-false-positive move: the test would go green and the machine would still have no
pixel verification. The asymmetry is the familiar one — a narrowing added to clear a red can only
ever hide, and the only thing it would hide here is the loss of a capability the project treats as
load-bearing.

`CLAUDE.md` names that capability directly: **"Done means the rendered value changed —
`site/test_*_door.py`, the page's own JavaScript, against the real feed."** A door test that cannot
drive a browser cannot answer the question the door exists to ask. Whether those door tests
currently FAIL or quietly SKIP is the first thing the next hand should establish, because a skip
here is the more expensive outcome: it reads as "nothing to report" on a surface whose whole job is
to refuse that reading.

## 3. Why I have not installed it either

Restoring Playwright is not a code change and is not this item's scope. It downloads browser
binaries onto a shared machine with a bounded cgroup, under a sandbox profile that is
director-console-only, and every lane running in this tree inherits the result. That is a
judgement about the machine rather than a repair to a control, so it is recorded here for the
seat's next orientation rather than taken unilaterally mid-item.

**Recommendation, not a question:** restore Playwright on the next seat turn that owns the
environment, and re-run the door suite to establish whether the doors were failing or skipping
through the outage. If the doors have been SKIPPING, that is a second and larger finding — the
period of the outage is a period in which "done" could not have meant what the rule says it means,
and every close in that window inherits the doubt.

## 4. Scope note

Established this turn, and it bounds how much is owed:

- The full `tests/background/` directory run (5,619 passed, 33m44s) ended with **four** failures,
  not the seventeen an earlier run recorded. Three were the live-tree and pinned-probe causes
  repaired and landed this turn.
- **This is the fourth, and it is the only red left in `tests/background/` that is not a defect in
  the tree.** Everything else that directory names is green.
