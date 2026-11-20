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

## 5. Enforce

The flip comes after observe mode has seen at least one week of real commits. The steps are:
the hook script itself is read from the base, and a base refusal becomes `exit 1`. A legitimate gate
change that the old gate refuses is split so that the old gate passes it, or it is raised with a
recommendation. It is never bypassed.
