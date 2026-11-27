# Gates judged from the base: what published practice says, and how we will do it

**Knowledge:** none -- this is practice for building the harness, not a market topic. It is published through the reading log (`docs/institutional/reading_log.md`, row of 20 Nov 2026) and read by `tools/base_judged_gates.py`.

**K8 page** for item 1 of the director's steer of 20 Nov,
`docs/staging/advisor/done/DIRECTOR_STEER_GATES_JUDGE_FROM_THE_BASE_PROPERTY_TESTS_FOR_BILLING_AND_DIFF_TRIGGERED_CHECKS_2026-11-20.md`.
The gap was confirmed by a demonstration on 20 Nov:
`docs/staging/records/SEAT_RECORD_A_GATE_IS_JUDGED_BY_ITS_OWN_EDITED_COPY_2026-11-20.md` (bb33b0a629).

## 1. What practice establishes

- **A check that the change can modify is broken.** Anthropic's Code Review reads its rules file
  "from the base or default branch, never from the pull request's changes". This is from Addy
  Osmani, "How the Claude Code team thinks about verification" (17 Nov 2026). It was relayed by the
  director, and the quotation is the advisor's reading.
- **The same rule appears in CI systems as a trust boundary.** GitHub Actions' `pull_request_target`
  runs the workflow file from the base branch, not from the PR. GitHub documents this as the
  protection against a PR rewriting its own checks. This is cited from the documentation and was not
  re-fetched this turn.
- **New gates go off, then observe, then enforce.** This is from the same article. It is also the
  pattern this repo already uses for the size ratchet (`rollout_state=warn`) and the coherence gate
  (`shadow` mode).

## 2. What is true here

The hook runs every gate as `python3 -m tools.<gate>` or `python3 tools/<gate>.py`, with cwd set to
the root of the tree being committed. So the gate that runs, and every module it imports, comes from
the change. Under `surgical_land`, the hook *script* comes from the change too. The steer's question,
"can a weakened gate pass its own change?", was answered **yes** (see the record linked above).

## 3. The design choices, and why

1. **Base = the parent commit (`HEAD`), not the literal `origin/main` ref.** `surgical_land`'s
   extract is a standalone repo with no refs, so `origin/main` does not resolve there. Its HEAD is
   the parent the landing will compare-and-swap onto, which is the trunk tip at landing time. Under a
   plain `git commit`, HEAD is the commit the change is a diff against. In both cases the change cannot
   alter HEAD's blobs, and that is the property the steer asks for.
2. **Code from the base, data from the change.** A shadow tree is built from symlinks to the
   change's root. Only the files in the gate's import closure are replaced with their base copies. A
   gate that finds its project root through `__file__` therefore reads the change's data but runs
   the base's code. The change side is run in an identical shadow built from the change's own copies,
   so any artefact of the shadow itself shows up on both sides and cancels out.
3. **The rerun is limited to what the change touches.** The import closure of each gate is read from
   the base by AST. It covers `import` and `from` statements, plus string literals that name a repo
   module, because a gate that shells out to `-m tools.x` is still built from `tools.x`. A gate is
   rerun only when the change stages a file in its closure, or alters or removes its line in the
   hook. Most commits pay for one closure walk and nothing more.
4. **Observe mode refuses nothing.** It logs every rerun to `base_judged_gates.jsonl` in the real
   git common dir. This is outside the tree, so a log line can never dirty a lane's commit. It also
   prints a stderr line when the base copy refuses what the change's copy passes. Stderr is used
   because `surgical_land` reads the tail of stdout to name a refusing gate.
5. **The observer itself is run from the base:** `git show HEAD:tools/base_judged_gates.py |
   python3 -P -`. The first landing therefore observes nothing. That is the bootstrap rule of
   step 1.3: a gate change takes effect only once landed.

## 4. GAPs (what this does not cover)

- **GAP-1, the data channel.** A change can loosen a baseline or `*.mode` file without touching
  any code. Code is judged from the base; data is not. The log records any staged path that looks
  like gate data (`baseline`, `.mode`, `frozen`), so observe mode measures how often this happens
  before a rule is written.
- **GAP-2, the calling line.** The line that calls the observer lives in the hook script. Under
  `surgical_land` that script is the change's copy, so a change that deletes the line silences the
  observer for that one commit. The enforce step closes this by running the base's hook script
  itself (`git show HEAD:tools/git-hooks/pre-commit | sh`), not by adding a second observer.
- **GAP-3, dynamic imports.** `importlib.import_module(name)` with a computed name is invisible to
  the closure walk. So is a gate that puts `cwd` on `sys.path` itself.
- **GAP-4, `commit-msg`.** Only `pre-commit` is observed in this increment.
- **GAP-5, guarded lines.** The `status_honesty` line inside the `if LATEST.md` block uses
  `|| { ... }`, not `|| exit 1`, and is not parsed. Neither are other conditional lines.
- **GAP-6, cost.** This is unmeasured until observe mode has run on real commits. The log records
  each rerun's duration and, from 20 Nov, one line for EVERY commit with `observer_seconds`. Until
  then it wrote only on a rerun, so five commits after it landed had left no log at all, and that
  silence could not be told from an observer that never ran. One probe on the real tree with
  nothing to rerun: 3.55 s.
  **First reading, 20 Nov (9 commits over 56 minutes, `--report`):** 0 would-refuse, 4 deferred,
  0 commits staging gate data, median observer cost 3.86 s. The maximum was 1,117 s, from one
  commit that touched `tools/pre_commit_test_gate.py`. Its base rerun alone took 537 s and the
  change rerun 568 s, so observe mode more than doubles the cost of any commit that touches the
  test gate or one of its direct imports. Enforce does not carry this cost, because it runs the
  base copy *instead of* the change's copy, not beside it. It is a cost of observing only.
  `--report` now prints these counts and `ready`. `ready` is true only once the logged commits
  span 7 days, because a busy afternoon is not a week. `--report --raw` prints the log itself.

## 5. The week's reading (27 Nov, `--report`), and the enforce flip

**The reading.** 872 commits from 20 Nov 12:31Z to 27 Nov 13:00Z (7.02 days). 281 of them reran at
least one gate from the base. **0 would-refuse.** In 18 test-gate reruns the base copy returned rc 1,
and in 15 of those the change's copy also returned rc 1: the commit was red on both sides and was
refused by the chain anyway. The remaining three disagreed only because one side hit the 1,200 s
observe bound (`rc None`), never because one side passed and the other refused. Per gate: size
ratchet 281 reruns; test gate 27 reruns and 254 deferred; site-lane gate 24 reruns and 257 deferred.
Observer cost per commit: median 4.15 s, p90 13 s, max 2,362 s (a commit that touched the test gate,
run on both sides). No legitimate gate fix was seen being deadlocked.

**What "deferred" is.** The 511 deferred results are commits that touched the *deep* closure of the
two pytest gates and not their own code. The top paths were `simulation/run_phase2b.py` (118 per gate),
`company/interfaces/growth_desk.py` (30), `background/live_payment_triad.py` (29) and
`simulation/gain_registration.py` (25). These files are the **code under test, not the gate**. Running
them from the base would test the old code and not the change, so they stay deferred under enforce.
This is a scope decision, not a hole that was missed. Its residue is **GAP-7**: a test gate weakened
through a module it reaches only indirectly is still judged by the change's copy.

**GAP-1, decided from the log: data stays the change's.** 29 commits staged gate data. 22 of them were
`docs/design/orphan_baseline.json`, 4 were `substring_source_scan_baseline.json` and 3 were
`wall_channel_census_baseline.json`. The orphan baseline is changed in the same commit *by design*: the
hook's own comment names `orphan_ratchet.py --freeze` in the same commit as the sanctioned way to
record a dormant module. Judging that data from the base would refuse the sanctioned route on every
one of those 22 commits. So data is not judged from the base. A loosened baseline is a diff a reviewer
can read, and the ratchets that own the files refuse growth themselves.

**Enforce, as landed 27 Nov.** The hook line is `git show HEAD:tools/base_judged_gates.py | python3 -P -
--enforce || exit 1`. For each affected gate it runs HEAD's copy only, with no timeout, because the
chain runs the gate itself unbounded. A base refusal exits 1, and the last line on stdout names the
gate, which is the line `surgical_land` quotes. The gate's own line in the chain then runs the change's
copy, so **a gate change must pass both**: the old gate, because a change cannot judge itself, and the
new gate, so a gate cannot land if it refuses its own landing commit. Cost: the same as the observe week
on affected commits, because a test-gate edit still runs that gate twice. Every other commit pays the
~4 s closure walk. A gate fix that the old gate refuses is split, or raised with a recommendation. It is
never bypassed.

**A crash of the judge fails open, loudly.** It prints `JUDGE FAILED` on stderr and logs a
`judge_failed` record. This is the one place fail-closed is wrong. The judge runs from HEAD, so a
refusing crash would also refuse the commit that repairs it, and no lane could clear that.

**Bootstrap.** The landing commit is judged by HEAD's observe-mode copy, which ignores `--enforce`.
Enforce starts on the next commit.

**Still open.** **GAP-2** is closed for `surgical_land` (27 Nov): `run_gate` runs HEAD's blob of
`tools/git-hooks/pre-commit` (the extract's HEAD is the base), written to a temp file outside the
checkout, and refuses when the base has no such blob. A change that deletes the enforce line is
judged by it on its own landing
(`tests/tools/test_a_landing_is_gated_by_the_base_chain_not_its_own.py`, mutation-proven). Two costs
follow. A new line added to the chain first runs on the commit after the one that adds it. A gate
module cannot be deleted in the same commit as its hook line, because the base's line still calls
it; that takes two landings. The `commit-msg` chain followed the same day: `run_message_gate` runs
HEAD's blob of `tools/git-hooks/commit-msg` through the same `_base_hook`, and refuses when the base
has none, so a change cannot delete its own REUSE or `NEXT:` line on its landing (same test file,
mutation-proven). The gate modules both hooks call are still the extract's copies. Still open: the
plain `git commit` door runs the shared tree's working copy (`core.hooksPath`). First live reading
of enforce (27 Nov 13:12Z): 1 enforce record, 0 refusals, 0 judge_failed. GAP-3, GAP-4 and GAP-5 are
unchanged. **GAP-8:** a gate that passes its landing but refuses everything afterwards, including
its own repair, cannot be repaired through the door, because enforce judges the repair by the broken
copy. The remedy is the director's console. The week showed none.
