# [WORKER-REPORT] OPS3: the wedge was repaired fourteen hours before the live surface said so, and the counter that measures it was writable by the gate's own tests (2026-08-13)

**Severity:** LATENT · **Lane:** H_harness · **Atom:** `OPS3_first_post_ruling_publish` (level stays 0)

**Status:** one exit criterion delivered and R15-proven, two verified as already met, one left
IN FLIGHT and not claimed. The level does NOT move — criterion (1) is executing as this is
written and criterion (4)'s counter has not returned to zero. R16: nothing recorded in
`gate_authorizations.jsonl`, because nothing was promoted.

---

## R9 — the measured cause of the wedge this publish closes

`observed-with-evidence`. `.publish_gate_state.json` cites one blocking test:
`tests/background/test_staging_archive_policy.py::test_process_run_complete_still_sees_a_duplicate_after_the_sweep`.

The cause was **a stale sibling assertion in a test file, not a regression in the publish path.**
The duplicate-marker path was given its own exit code that morning — `EXIT_NOTHING_PUBLISHED`
(76), so that "published nothing" stopped reading as "published successfully" — and this test
still pinned that path at `rc == 0`. It went red for being right about yesterday.

Repaired at `83f80e0ce` (surgical-land receipt, gate-rc 0, 260 passed), committed
**2026-08-12T21:59:42Z — fifteen seconds after the last failure it caused** (`ad9d44186`,
21:59:27Z). Verified at HEAD this tick: `1 passed in 0.05s`.

This is the memory class *a new refusal relocates a sibling assertion behind it*: giving a path
its own exit code is a two-file change, and the second file was in a different directory.

## The part that was not the wedge

**Publishing was never down.** `grep "Committing and pushing" docs/observability/sim-runner-log.md`
shows a real publish every ~40–60 minutes straight through `2026-08-13 11:24 UTC`. The 206 in
`episode_failures` is not 206 outages.

The counter cannot come down because **`record_publish_gate_success()` has not been reached since
2026-08-11 07:50 UTC** — 198 "Publish gate recovered" lines in the log, none after that. The
outcome router takes the `unproven` branch instead: `_green_is_on_record_for(git_hash)` is False
whenever the marker's hash parses as `unknown`, and the router then leaves the streak "exactly as
it was found". Correct by design (PW2: publishing nothing is not evidence of health) — but it
means the counter measures router bookkeeping, not the outage it is read as measuring.

## THE DEFECT FOUND AND FIXED — criterion (4)'s "never by hand" was defeated by the gate's own suite

`observed-with-evidence`. The **live** `docs/observability/sim-runner-log.md` carries, at
11:26–11:29 UTC while a real publish cycle was mid-flight, lines no live publisher could have
written:

| live log line | why it cannot be the publisher |
|---|---|
| `no suite PASS is recorded for git=abc1234` | `abc1234` is a test fixture hash (`tests/conftest.py:94` names it by name) |
| `could not make the HEAD checkout a git repo: git is not installed` | git is installed |
| `` `git init` in the HEAD checkout failed rc=128 -- fatal: cannot mkdir `` | a sandbox repo, not this one |
| `run_complete_20260813T112620Z.md exited 0` (×3, same minute) | that marker exists nowhere on disk — not in `docs/staging/`, not in `done/` |

Those are gate-suite tests driving the **live** `record_publish_gate_outcome`. Neither
`docs/observability/.publish_gate_state.json` (the counter) nor
`docs/observability/.last_tested_hash` (the suite-pass stamp the episode close rests on) was in
`tests/conftest.py::_PROTECTED_WRITE_PATHS`, so the suite could move the counter in **either**
direction — inflate it through `record_publish_gate_failure`, or zero it through
`record_publish_gate_success`. OPS3 exit (4) requires the counter return to zero "through a real
pass, never by hand"; a gate-suite test able to stamp `.last_tested_hash` *is* a hand.

**This is the SAME CLASS as `WORKER_REPORT_THE_GATES_OWN_TESTS_WERE_WRITING_THE_ALARMS_EVIDENCE_2026-08-10`,
instances three and four.** That report added `.last_gate_blocking_tests.json` to the tuple and
filed the log-file case as too-large blast radius. It did not reach these two, and neither did
anything since — which is the class's own point: each instance is found one file at a time
because the guard is a list. The honest read is that the list will keep leaking until something
DERIVES the protected set from "what does a live daemon read to make a control decision"; that is
a bigger change than this draw, and is filed here rather than attempted.

**The remedy already existed and was unwired.** `_PROTECTED_WRITE_PATHS` is the G-T2 guard, and
its own comment states the doctrine: *"a guard list only protects the paths somebody thought of,
so the answer to finding a hole in it is to fill the hole, not to isolate the caller."* These two
paths were guarded only by ~10 per-test `monkeypatch.setattr` calls — the pattern that comment
rejects. `tests/background/conftest.py` neutralises the **supervisor's** copies of both constants
(the read side) and not `process_run_complete`'s (the write side), which is why the
directory-scoped fixture never covered it. Same class as memory's *a fixture's neutralise-list
rots when the callee gains a check*.

**Fixed** by adding both paths to the tuple. Both are written through `Path.write_text`
(`process_run_complete.py:1844` and `:3573`), which is the guard's intercept point — not an
`os.replace` atomic write that would have slipped past it, checked before claiming coverage.

**R15 both ways**, `tests/test_isolation_guards.py::test_gt2_blocks_forging_the_suite_pass_stamp_and_the_wedge_counter`:
green with the entries present (9 passed); with `.last_tested_hash` removed from the tuple the
test fails `DID NOT RAISE`. The read side is asserted still open, because the live router and the
supervisor's RUNG-1 draw both read these files and a guard that blocked reads would break the
pipeline it protects.

**Cost paid, and worth stating.** Running that mutation against the live tree made the first write
land for real: the test stamped `deadbeef` over the live `.last_tested_hash`. Restored to the
observed prior value `ed4da96a0` (written by the real 11:24Z gate pass; `git checkout --` was the
wrong instrument — it returns the last *committed* hash, `a0d003108`, a staler number).
`.publish_gate_state.json` was untouched: the test aborted before reaching it. The test's docstring
now says mutate-against-a-copy so the next person does not repeat it.

## Exit-criterion census, measured not asserted

| # | criterion | verdict |
|---|---|---|
| 1 | one publish cycle green, gate's subject a clean HEAD checkout, `.last_tested_hash` names that commit | **IN FLIGHT, NOT CLAIMED.** PID 2221699 on `run_complete_20260813T113731Z.md` (git `1cf30581b`), gate started 11:46Z on a throwaway HEAD checkout, 139 blocking test files. Owned by that process; this tick did not race it and wrote nothing in its path. |
| 2 | backlog DRAIN-SUPERSEDED, not bulk-archived, each naming its superseder | **DELIVERED.** 366 of 457 archived `run_complete_*.md` carry `## Superseded (not published)` naming the run that overtook them (newest: `20260812T134414Z`). Mechanism: `background_worker.retire_superseded_marker()`, which appends the reason before the rename precisely so R10 is not satisfied by deletion. Backlog now 1 — the in-flight marker. |
| 3 | candidate baseline printed on the live surface, R11-verified **by fetching it**, figure + clock basis (R14) | **MET.** Fetched `https://poesys.net/data/dashboard.json` this tick: `portfolio.net_margin_gbp = 1526252.39` — the £1,526,252.39 candidate baseline — with `portfolio.basis.net_margin_gbp = {"clock": "settled", "provisional": true}`. Rendered value and its clock, off the live surface, not the file on origin. |
| 4 | counter returns to zero through a real pass, never by hand | **NOT MET — but no longer forgeable.** 206 at tick end. The "never by hand" half is now mechanised and mutation-proven; the "returns to zero" half needs the in-flight cycle. |

## What criterion 3's fetch also showed, and it is not a defect

The live surface serves the **01:00Z** render while HEAD has been committing £1,559,116 since
06:56 UTC. That is the publish-decoupling ruling working, not staleness: live
`publish_provenance.json` reports `verification_state: "verified"`, `showing_run == last_verified`
(`433718889`), and a `paused_reason` naming the blocking test — the site keeps serving the last
VERIFIED run and says so, publishing no unverified figure.

One thing there **is** worth naming: that `paused_reason` still cites
`test_process_run_complete_still_sees_a_duplicate_after_the_sweep` at `git=ad9d44186`, a red
repaired at `83f80e0ce` fourteen hours before this tick read it. The public pause reason has no
path back to "actually, that one is fixed" other than a green cycle — so a repaired wedge keeps
publishing its own obituary. Filed as an observation, not fixed on sight
(SELF_INTERRUPT_DISCIPLINE); the in-flight cycle is its natural test.

## Not claimed

No level move. No publish forced. No counter reset by hand — the point of the fix was to make
that impossible, and doing it here would have been the defect wearing the repair's clothes.
`docs/status/LATEST.md` was not touched: a live publisher owned it for this tick's duration.
