# WORKER FINDING — an absent checkout was reported as a rotted declaration, and widened the gate 28 times

**Filed:** 2026-08-12 · **Lane:** H_harness · **Class:** R15 wrong-subject / publish wedge
**Status:** FIXED and R15-proven both ways this tick (`background/publish_scope.py`,
`background/process_run_complete.py`)

## The claim

`observed-with-evidence` — Between 2026-08-10 18:15Z and 2026-08-12 02:11Z the publish gate
resolved its blocking scope against a tree that was **not a checkout of this repo** on 28
cycles, against 64 that resolved normally — **30% of every gate cycle**. Each one was logged
as *"the declaration has rotted; blocking on the FULL suite until it is repaired"*. The
declaration had not rotted, and repairing it was never possible, because nothing was wrong
with it.

## The evidence

The trigger, from `sim-runner-log.md` at 02:04Z — the checkout failed to materialise:

```
[process_run] Publish gate: could not make the HEAD checkout a git repo: git is not installed
[process_run] Publish gate: `git init` in the HEAD checkout failed rc=128 -- fatal: cannot mkdir
[process_run] Publish gate scope: 6 declared publish-path source(s) do not exist
  (background/process_run_complete.py, saas/reporting/annual_report.py,
   simulation/publish_consumption_data.py, simulation/publish_market_feed.py,
   tools/generate_dashboard_data.py, tools/generate_insights.py)
  -- the declaration has rotted; blocking on the FULL suite until it is repaired.
```

All six exist, in the working tree **and** in HEAD at that SHA (`git cat-file -e HEAD:<path>`
→ present, six for six). So the message named the one subject that was provably healthy.

Reproduced directly against today's code, before the fix:

```
REAL ROOT : full_suite=False | 134 tests | 6 publish-path source(s) -> 134 blocking test files
EMPTY ROOT: full_suite=True  | "6 declared publish-path source(s) do not exist ... has rotted"
NO ROOT   : full_suite=True  | "6 declared publish-path source(s) do not exist ... has rotted"
```

Frequency, `grep -c` over `sim-runner-log.md`: **28** rot verdicts vs **64** successful
resolutions, first 2026-08-10 18:15Z, last 2026-08-12 02:11Z.

## Why it wedged publishing

The direction was never wrong — an unresolvable scope must widen, and it did. The **cost** is
that widening is the pre-decoupling gate: 134 scoped files become the whole tree, which is
exactly the *"publish iff everything is green, i.e. publish never"* condition
`publish_scope.py` was built to end (its own module docstring). So on 30% of cycles the
decoupling silently switched itself off, and the log explained it with a subject that could
not be acted on. Six ticks were sent after a declaration needing no repair.

Same shape the sibling already records for `git is not installed`
(`process_run_complete.py:935-996`): an environment fault printed as a code fault, at exactly
the moment a reader is hunting for a red test.

## The mechanism

`resolve_scope` asked one question — "do the declared sources exist under `root`?" — and had
one answer for both causes. But they are trivially distinguishable and the distinction was
simply never drawn: **a declaration rots one entry at a time** (somebody moves one module),
so some sources resolve and some do not. **A root that is not this repo resolves none of
them.**

## The fix (built, landed this tick)

1. `publish_scope.ROOT_REPO_MARKER` + `_root_holds_the_repo()` — the discriminator is
   `tests/`, deliberately **not** drawn from `PUBLISH_PATH_SOURCES`. Asking the declared list
   whether the declared list is trustworthy is the tautology shape R15 names first
   (`feedback_tautology_reappears_inside_r15_tests`); `tests/` is the positional every
   full-suite fallback argv carries, so its absence answers the operative question exactly —
   *can the suite this is about to fall back to even run here?*
2. A missing declaration **plus** a missing marker → `root_unavailable: True` and a reason
   naming the ROOT. A genuine partial rot still says the declaration rotted.
3. **Wired, because a reported state is not a control**
   (`feedback_reported_state_is_not_a_control`): `_run_gate_in` now returns the existing
   `_checkout_unavailable_verdict()` on `root_unavailable`. Reused verbatim rather than
   restated, so there stays ONE answer to "the gate has no subject". It blocks (R15: an
   unavailable check is a FAILED check), does **not** stamp `LAST_TESTED_HASH_FILE`, and
   deliberately skips `_log_gate_failure_payload` — there are no failing tests to name, and
   naming some anyway is the defect the previous tick filed
   (`WORKER_FINDING_THE_WEDGE_ALARM_NAMED_TESTS_THE_GATE_NEVER_RAN`).

`run_fast_tests` already refused a `None` checkout. What it could not see is a checkout that
was **created and then not populated** — directory present, `head_dir` not None, contents
absent. That is the hole this closes.

## R15 — proven both ways, on the real source

Mutation arms run by extracting HEAD to a throwaway tree (under `HEAD_CHECKOUT_PREFIX`, per
this repo's own convention) and copying only the NEW tests over the OLD source:

| arm | old source | new source |
|---|---|---|
| `test_an_absent_root_is_reported_as_an_absent_root_not_a_rotted_declaration` | FAIL | pass |
| `test_a_genuinely_rotted_declaration_still_says_so` (over-fire guard) | FAIL | pass |
| `test_the_root_marker_is_independent_of_the_declaration_it_adjudicates` | FAIL | pass |
| `test_a_root_unavailable_scope_stops_the_gate_instead_of_running_it` (wiring) | FAIL | pass |
| `test_the_unavailable_root_verdict_does_not_stamp_the_tested_hash` (wiring) | FAIL | pass |

The two wiring arms were mutated separately, against a tree holding the NEW `publish_scope.py`
and the OLD `process_run_complete.py` — i.e. the flag present but unread. Both fail there,
which is what makes them a test of the wiring rather than of the flag.

`tests/background/test_publish_scope.py`: **27 passed** on the fix.

## A second finding, surfaced while verifying this one

`observed-with-evidence` — **an uncommitted, daemon-written observability record silently reds
10 tests in the working tree**, and it is not this change.

`tools/measure_publish_gate_subject_cost.py` computes `PHASE_CEILING_IS_SUFFICIENT` at IMPORT
time from `docs/observability/publish_gate_subject_cost.json`. That file is daemon-written and
currently modified-uncommitted:

```
demand floor from WORKTREE record: 10240   -> needs 10240*1.2 = 12288MB ceiling
demand floor from HEAD     record:  8192   -> needs  8192*1.2 =  9830MB ceiling
box safe cap                     : 11816
```

So in the working tree the phase is `_Unbounded` and 10 tests refuse; against HEAD they pass.
This cost most of this tick's diagnosis: an A/B that ran HEAD in a clean checkout and the
change in the dirty worktree attributed all 10 to the change. The controlled cell — the change
copied onto a clean HEAD tree — is **114 passed, 1 failed**, and that 1
(`test_the_sampler_reads_this_scopes_own_high_water_mark_from_the_kernel`) fails identically on
unmodified HEAD. The change is innocent.

Worth its own atom: the publish gate runs against a HEAD checkout so it never sees this, but
every worker running tests locally does, and will misattribute exactly as this tick did.
Class: `feedback_gate_lints_working_tree_so_uncommitted_wedges_everyone`, with the twist that
the working-tree file here is written by a daemon rather than by a lane.

## Related

- `WORKER_FINDING_THE_WEDGE_ALARM_NAMED_TESTS_THE_GATE_NEVER_RAN_2026-08-12.md` — the previous
  tick's finding; that one is about the payload naming wrong tests, this one about the scope
  naming the wrong subject. Same episode, different organ.
- `WORKER_FINDING_THE_SCOPE_IS_RESOLVED_AGAINST_A_DIFFERENT_TREE_THAN_THE_GATE_RUNS_IN_2026-08-10.md`
  — the fix for that made the scope resolve against `run_root`, which is correct and is what
  makes THIS failure mode reachable: the run root can be a tree that does not exist.
- `WORKER_FINDING_AN_OOM_KILL_IS_RECORDED_AS_A_TEST_REGRESSION_2026-08-10.md` — sibling: a
  resource failure recorded as a test regression.
- `feedback_a_bare_head_extract_is_not_the_gates_subject`
