**Severity:** BLOCKING · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# SEAT RESULT: the two commit doors run two different gate chains, and now one of them says so

**Severity:** BLOCKING
**Claim:** `core-hookspath-points-at-a-working-copy-so-every-gate-can-be-silently-stale`
**Pre-registration:** `docs/staging/records/PREREG_THE_LIVE_HOOK_CHAIN_DIFFERS_FROM_THE_TRUNKS_BY_MORE_THAN_THE_MARK_2026-09-25.md`

## The premise was NOT spent, and the duplicate claim was my own predecessor

`934343669` is an ancestor of `origin/main`. So is `4157c8d6b`, which the draw's duplicate check
named — and it is **a findings document and nothing else** (one file, 102 lines, `docs/staging/`).
The claim id sat in `docs/observability/.seat_work_in_hand.json` with `"paths": []`, held by that
same invocation, which landed the diagnosis and never built the control. The item's actual ask —
*"the one-leg control that compares the live hook files against the index/origin and says so,
loudly"* — existed in no copy of the tree. Carried on rather than releasing.

## The three predictions, all confirmed

1. **The live chain was missing exactly one invocation, `hook_gate_mark`.** Confirmed: 21 live
   invocations against the trunk's 22. I had flagged this prediction as weak because I had only
   grepped the `python3 -m` form and most of the chain is `python3 tools/X.py`; the full parse
   agreed anyway.
2. **No gate ran live that the trunk had retired.** Confirmed: empty.
3. **`test_every_step_the_hook_runs_is_timed` was RED at `origin/main`.** Confirmed, and this was
   the finding I did not go looking for — see below.

## The sharpest thing measured, which the item did not predict

**There are two doors and they resolve the hook from two different places.**

* `git commit` runs `core.hooksPath` → `/home/rich/synthetic-enterprise/tools/git-hooks/pre-commit`,
  the shared tree's **working copy**. It resolves to that same absolute path from inside every
  linked worktree, so where a lane commits from changes nothing.
* `tools/surgical_land.py::run_gate` runs `checkout / "tools/git-hooks/pre-commit"` — the hook from
  the **extract of the tree being committed**, which is current by construction.

So the careful door has been running the trunk's chain and the cheap door the stale one, and
`surgical_land`'s own comment — *"the tool must face what `git commit` faces"* — has been false for
as long as the checkout has been behind. The correction is now beside that comment rather than
instead of it.

The asymmetry this turns on: for almost any module a stale checkout **delays** a fix; for a gate in
this chain it **deletes** the control. A gate that does not exist does not fail. It returns green
with everything else, and there is no artefact anywhere afterwards that distinguishes the two.

## A live red at `origin/main`, found on the way

`934343669` added `hook_gate_mark --record` to the hook and did not add it to `STEPS` in
`tools/time_the_commit_hook_chain.py`. `test_every_step_the_hook_runs_is_timed` went red on the
trunk and **no commit's selection could reach it**: staging `tools/hook_gate_mark.py` selects that
module's own test by stem, never the timer's. Exactly the class
`GIT_ORACLED_AND_TEST_CORPUS_SUBJECTS` exists for, in a control that is not on that list. Fixed
here, because the parser de-duplication below selects it.

## What landed

* **`tools/live_hook_drift.py`** — the control. Resolves the hooks dir by asking git
  (`rev-parse --git-path hooks`, which honours `core.hooksPath` *and* the worktree case; the naive
  `root/.git/hooks` gives the seat's own empty private dir and would report a permanent all-clear
  from the one place the seat works). Compares **invocations, not bytes**: 805 bytes of difference
  is not 805 bytes of danger, and a control that shouted on comment edits is a control nobody
  leaves on. Three named verdicts — `MISSING` (the trunk declares it and the live chain does not
  run it at all), `ALTERED` (same gate, different argv — `--gate` quietly becoming `--check` is a
  control narrowed without anyone deciding to), `RETIRED`.
* **Fail-closed on its own reading.** An unresolvable reference, an unreadable hook, or a reference
  that parses to no invocations is `undetermined` with the reason named — never green. `clean`
  requires that the comparison was *made*.
* **Two wirings, and neither can cover for the other.** `tools/surgical_land.py` calls the reporter
  from the committing tree on every landing — the channel the outage cannot silence. The hook line
  covers the `git commit` door and **is inert until the shared checkout advances**, which is written
  at the line rather than left to be discovered. A hook-only wiring would have been the liveness
  signal delivered through the channel it monitors: silent on the exact day the gap was real.
* **It reports; it does not refuse.** The remedy is the reconciler advancing the shared checkout,
  which no lane can do from inside its own commit. `--gate` exists for a caller that wants the
  refusal; nothing in the chain passes it.
* **One parser, two subjects.** `tests/tools/test_time_the_commit_hook_chain.py` grew a hook reader
  locally in September; it imports this one now.
* **The timer no longer leaves a mark behind.** `hook_gate_mark --record` writes a mark naming the
  tree the index currently writes out to, so timing it would leave a receipt a later hand-built
  commit over an unchanged index could inherit. Whatever was there before goes back, including
  "nothing".

## Controls

Ten mutations run, not annotated; each fired the test written for it, green restored between each.
Anti-vacuity guard removed → `test_a_reference_that_parses_to_no_gates_is_undetermined_and_NOT_clean`
(without the guard the verdict is `clean is True`, which is the exact failure). `clean` returned
True unconditionally, `missing`/`retired`/`altered` each forced to `[]`, `live_hooks_dir` replaced
by a hand-built `.git/hooks`, `invocation_subject` returning `""` instead of raising, the `MISSING`
loop dropped from the report, the `land()` call deleted, the hook's `|| true` dropped.

The partition is asserted by **one** control over all three verdicts in a single comparison, not a
leg per branch: a builder returning three empty lists would pass every single-branch test that only
asks `not d.retired`.

**The controls grade the DETECTOR on synthetic hook texts, never the live checkout's current
state.** A control pinned to "the shared tree is 49 behind today" would go green the moment somebody
ran the reconciler and could never go red again for the right reason — and would meanwhile red every
lane for something no lane can fix. One test reads the real hook, and it reads it for reachability
(does the parser find gates in real bytes at all), not for a verdict.

## What is NOT closed

The shared checkout is still 7 ahead / 49 behind, and this work cannot advance it. The ahead leg
remains unpromotable for the reason `4157c8d6b` recorded: `6a422ea0f` carries neither a receipt nor
a mark, and one receipt-less commit makes the whole leg unpromotable. Until the checkout advances,
every ordinary `git commit` in the shared tree still runs a chain missing `hook_gate_mark` — and now
also missing `live_hook_drift` itself, which is the honest self-demonstration and will be the first
thing the reporter says about itself once this lands.

## Landed at `bfa285755`, on `origin/main`

Seven paths: `tools/live_hook_drift.py`, `tests/tools/test_live_hook_drift.py`,
`tools/surgical_land.py`, `tools/time_the_commit_hook_chain.py`,
`tests/tools/test_time_the_commit_hook_chain.py`, `tools/git-hooks/pre-commit`,
`docs/observability/substring_source_scan_baseline.json`.

## Three defects the GATE found that my own run did not, and all three were mine

My local run of the affected suites was green each time. What made the difference is that the gate
runs the whole tree against the tree the commit would create, in a standalone extract.

1. **`test_a_control_reads_python_as_code` refused the caller test, correctly.** It read
   `tools/surgical_land.py` as TEXT — and that file now explains this whole mechanism in a comment
   beside `HOOK_REL`, so `"live_hook_drift" in source` was satisfied by the **prose** and deleting
   the call would have left the control green. The exact fail-open that census exists for, walked
   into inside the commit that adds a control about controls. Routed through
   `python_code_text.searchable()`.
2. **`drift()` read the reference before the subject.** In the extract there is no `origin/main`,
   so the reference leg fired first and masked the leg under test. Both are `undetermined` so
   nothing was hidden, but only one is actionable by the reader. Subject first now.
3. **And the fix for (2) was wrong in the same way.** The tests still called `drift(root=ROOT)` and
   asserted on whichever reason came back. The extract is a standalone repo with its own empty
   `.git/hooks` *and* no `origin/main`, so **both** refusal legs were reachable there and each test
   passed on the other one's reason — green in the worktree, red in the gate, and green for the
   wrong cause had the order differed. Both tests now build a repository whose hooks dir and
   committed hook are under the test's own control, with a third arm over the same builder
   asserting a **clean** verdict: without it, a broken fixture would make every refusal leg green.

Two census rows were frozen by hand with their reasons in the row (`compare` and the hook-shape
test read `/bin/sh`; `python_code_text` parses Python). A third was refused rather than frozen, and
that refusal was right — it is (1).

## The reporter's first live reading after its own landing

```
[live-hook] the hooks git will run live at /home/rich/synthetic-enterprise/tools/git-hooks/pre-commit, which is a WORKING COPY, and it differs from origin/main.
[live-hook] GATES THE TRUNK DECLARES THAT DO NOT RUN -- these controls do not exist for any commit made through `git commit` here, and a green gate does NOT mean they passed:
[live-hook]   MISSING  live_hook_drift
```

It names itself, which is the honest self-demonstration and was predicted above.

**And the reading changed in a way worth recording.** `hook_gate_mark` is no longer reported
missing — the live `pre-commit` now contains it and `tools/hook_gate_mark.py` is on disk there —
**while the shared checkout has not advanced**: it reads 8 ahead / 50 behind, further from
`origin/main` than the 7/49 measured at the top of this record. So those two files arrived in the
working copy by some route other than the checkout moving, and the shared tree's `tools/git-hooks/`
is now a **mixture** rather than a snapshot of any commit. That is strictly harder to reason about
than being uniformly behind, and it is precisely the state that has no other witness. I have not
established which lane wrote them or how, and I am not inferring it: the observation is that the
gap closed for one gate without the checkout moving.
