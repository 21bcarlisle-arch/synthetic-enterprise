**Severity:** LATENT · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0 delivery
· **Class:** controls_that_cannot_fail

# FINDING: a converged helper had three callers, zero test importers, and the refusal was left behind at two of them

**Measured 2026-09-05, delivery seat, from an isolated worktree at `85390f09a`. Pre-registration:
`SEAT_PREREG_WHICH_CALLER_SUITE_IS_EACH_DIRECTION_CONTRACT_STANDING_ON_2026-09-05.md`, filed
before the screen was scored or any battery run. Repaired in the same commit.**

---

## The question this came from

`38871422b` measured one converged mechanism and found the shared module inherits whichever caller
suite happened to be strongest: one contract proved by no suite, two by one. It filed the general
statement LATENT. The drawn direction was to ask that of every *other* converged mechanism.

The screen (method and limits in the pre-registration) put **161** modules at ≥3 first-party
callers, **15** of them with no dedicated suite, and **3** with no test importer at all. This is
the first of those three, and it did not need a mutation battery — the answer is by construction.

## What was true

`background/ops_repo.py` is the only route from this repo to the **private**
`synthetic-enterprise-ops` repo. Three callers converged onto it:

| caller | what it pushes | refusal under a test process |
|---|---|---|
| `background/ntfy_mirror.py` | the director's message mirror | hand-rolled at the call site |
| `background/director_input_log.py` | the director's input log | hand-rolled at the call site |
| `background/backup_company_data.py` | the company databases | **none** |

**Nothing in `tests/` imported `ops_repo` at all.** The callers' suites patch `commit_and_push`
*by name in the caller's namespace*, so the shared function's own body — the `git add`, the
commit, the "nothing to commit" branch, the `git push origin main` — had never been executed by a
test. Its docstring even asserts a claim about tests ("no-ops cleanly … e.g. in tests that don't
mutate content") that no test has ever opened.

**Two callers hand-rolled the same refusal; the third had none.** `backup_once()` reaches
`commit_and_push` with nothing between a test process and a push to the real private remote. It
escaped only because all four of its tests happen to patch the name — safety by convention at
every call site, which is what a choke-point fix exists to replace. That is the same sentence
`background/live_ledger_guard.py` already wrote about its own class in August: *"every … main is
the same shape and only escapes today because no test happens to invoke it."*

**And the two hand-rolled copies are strictly weaker than the primitive that already existed.**
Both key on `os.environ.get("PYTEST_CURRENT_TEST")` alone. pytest leaves that unset during
collection and at module import, so a push at import time walks past both.
`live_ledger_guard.in_test_process()` ORs it with `"pytest" in sys.modules` and fails closed.
`live_ledger_guard` could not cover this by itself — its subject is derived as "any path under
`<PROJECT_DIR>/docs/observability`", and `OPS_REPO_DIR` is a different repository outside the
project directory entirely. **The primitive was shared; the subject was not, so nobody noticed the
subject was uncovered.**

## The shape, stated generally

The low-water case was *convergence moves the code and does not move the evidence*. This is the
harder sibling: **convergence moved the code and left the REPAIR at the call sites.** Two callers
kept a private copy of the guard, the third never had one, and the shared function — the only
place the guard could be complete — had neither the guard nor a single test. A reader counting
call sites sees one helper and three callers and concludes one mechanism, well factored.

## The repair

At the write, not the instance. `commit_and_push` now refuses under a test process, raising
`OpsRepoWriteUnderTest`, and it **calls** `live_ledger_guard.in_test_process()` rather than
copying the callers' spelling. No env-var override — that is a fail-open door set by exactly the
process that must not have it. Real daemon runs are untouched.

`tests/background/test_the_ops_repo_push_had_no_refusal_at_the_choke_point.py` is the module's
first test. Seven mutations on `ops_repo.py`, each applied alone with its target asserted present
exactly once, **all seven caught**: refusal deleted; refusal moved after the `git add`; refusal
made anonymous; no-op branch made to raise; every commit failure swallowed as a no-op; lock
deadline made unreachable; push removed.

The load-bearing leg is `test_the_push_actually_works_when_it_is_not_a_test_process`, which drives
the real body against a real local remote with the guard's single input flipped. Without it a
`commit_and_push` that raised unconditionally would pass every other test in the file — and would
silently disable the ntfy mirror, the input log and the database backup at once.

## A defect found in my own control, kept here because it generalises

Written the obvious way, the lock leg was `pytest.raises(OpsLockTimeout)` around a nested
acquisition. Mutating the deadline branch to `if False:` **did not fail it — it hung it**: the
acquisition loop sleeps for ever. The run was killed at 600s, and it took the restore step of the
mutation harness with it, leaving the module mutated on disk. **A control whose failure mode is an
unbounded hang reports nothing about which leg broke, and under a full gate run it is
indistinguishable from a slow suite.** The leg now runs the second acquirer in a thread with a
join bound, so the same mutation is a named assertion in 10s. Any control over a
blocking-acquire-with-deadline has this shape.

## Not repaired, filed here instead

`commit_and_push` returns early on "nothing to commit" **without pushing**. A commit that landed
locally but whose push failed is therefore never retried by a subsequent identical write — the ops
repo sits ahead of its remote indefinitely, and nothing reports it. Reachable whenever the network
is down at the moment of a push. Left alone deliberately: pushing on the no-op path would add a
network round trip to every unchanged ntfy mirror write, and that trade deserves its own decision
rather than a drive-by.

## What this does not establish

The screen is a proxy: it is blind to callers reached by subprocess or dynamic dispatch, and
"has a dedicated suite" does not mean each contract is proved. The other two zero-importer
modules (`simulation/run_phase3b_recalibration.py`, 6 callers;
`tools/generate_company_data.py`, 4 callers) are **not** examined here — the first is stubbed by
one `monkeypatch` in `tests/sim/test_ssp_tail_model.py` and the second appears in `tests/` only as
a string inside a manifest. Neither is a proof of anything and both remain open.
