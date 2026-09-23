# The operational layer was blind to one stale copy, and the draft it carried is not the feature HEAD built

**Severity:** RECORDED · **Lane:** H_harness

The operational-layer signal is green and its episode is closed. It had failed to run for four
consecutive hourly checks, and the cause was one stale working copy of `tools/run_value_cycle_ab.py`
shadowing a constant that has been at HEAD since 20:06.

Paths: `tools/run_value_cycle_ab.py`.

## The doorbell's diagnosis was wrong, and the one-variable control is what says so

The item named two test files and a cause: *"a half-landed rename or a salvage that parked a
producer and left its consumers is the usual cause — `git status` these paths first"*.

`git status` on both paths is **empty**. Both are clean at HEAD, and neither was ever the subject:

- `tests/tools/test_the_paired_floor_leg_runs_alone_in_its_own_process.py` — clean
- `tests/tools/test_the_paired_size_term_floor_cannot_report_a_contrast_it_never_ran.py` — clean

The collection error names the real subject three frames down. Both files import
`tools.size_term_paired_floor` (also clean at HEAD), which at line 129 does
`from tools.run_value_cycle_ab import PAIRED_FLOOR_LEG_PEAK_MB`. **HEAD defines that constant.
The working copy does not.** One dirty file, in neither of the two the item named.

This is the shape the memory already carries as *"reds naming a subject far from your change are a
stale working copy"* — and the item's own remedy sentence would have sent a lane hunting a rename
that does not exist.

## The copy is six days stale, and it is NOT a plain revert

`tools/run_value_cycle_ab.py` had mtime `13:33` against a last commit to its path of `20:06`
(`b1b3cb922` — the memory-ceiling work). Scanning the file's whole history for the blob nearest the
working copy puts its base at **`c9bd2eae7`, 09-17 16:20** — six days back, and still 356 lines
apart. It is not a fork of anything recent.

**But it is not discardable either, and `refresh_to_head` is what established that**, not my
reading. It refused:

```
tools/run_value_cycle_ab.py  [refused_supplies_names_head_lacks]
    this copy SUPPLIES 2 name(s) HEAD does not have, so it is not a copy HEAD supersedes
      + arm_population_instrument
      + arm_population_pair
```

Neither override applies, and both refusals are correct: `--superseded` requires that *no* supplied
name can run against the base (both of these can), and `--base-wins` requires that *no* landable
hunk exists (hunk 19 is landable). The tool named its own door and I took it.

## Why the feature could not be grafted whole

`isolate_hunks --survey` reports 32 hunks. The `arm_population` feature spans hunks 19, 21, 23 and
31 — but **only hunk 19 adds without deleting anything HEAD carries**. The hunks holding its call
sites also delete HEAD's memory-ceiling landing:

| hunk | what the stale copy would revert |
|---|---|
| 24 | `#: WHAT ONE LEG OF THAT PAIR COSTS -- NOW MEASURED, AND IT WENT UP` |
| 25 | the `--seeds` → `--leg-only` correction of 2026-09-23 |
| 26 | `def _peak_provenance` |

So the choice was never "keep the draft or keep HEAD". Landing the draft's call sites lands the
revert that OOM-killed the paired floor in the first place. **Landed `HEAD + hunk 19`**: the
constant is HEAD's, and the draft's two functions are preserved in the tree rather than in a ref
nobody reads.

Verified before writing: AST-parses, `PAIRED_FLOOR_LEG_PEAK_MB` is bound at module level, both
functions present, `ruff --select I001` clean, and the file contributes **zero** F401.

## The residue, filed as its own instance — `no_caller_and_never_runs`

**The two functions have no caller.** That is a real instance of the class and it is mine, created
deliberately and with the alternative being the destruction of unlanded work.

What a lane taking this must NOT do is assume it is merely dead. **The draft is not superseded by
`same_book_across_arms`, and I nearly recorded that it was.** That function compares *served
segments* and says in as many words that it is *"NOT compared on account counts"* — it deliberately
excludes the realised, priced population. `arm_population_pair` measures exactly what
`same_book_across_arms` declines to. Different subjects; the flattering reading was that HEAD had
already built this.

**The open question is the draft's own premise, and it is six days old.** The draft's warrant is
that `level_arm_decision_shape` was *"reported, not raised on, and then reported to nothing: no
artefact on disk carried it"*. Since that was written, `a08752789` landed a roster for the declined
renewals. At HEAD, `level_arm_decision_shape` is bound at line 4970 and `FOLD_MUST_AGREE` at 5622.
**Whether the fold now reads it is a question to run, not to inherit** — and it decides whether
these two functions get wired or deleted. Neither answer should be taken from this document.

## Two things found in passing, neither mine to sweep

**The static quality ratchet is red in the shared worktree and it is not this change.** `F401`
stands at 269 against a baseline of 264. Attributing per dirty file against each file's own HEAD
blob puts all five on `tools/refresh_to_head.py` (work=5, head=0, mtime 05:54 — fifteen hours
before this tick, and not caused by the survey run above).

**CORRECTION, beside the claim: I first wrote that this "reds that gate for every lane until its
holder lands or drops it". That is wrong, and my own commit is the one-variable control that
refutes it** — `224ca2b0a` landed with `gate-rc 0` while the worktree read 269. The ratchet is
measured per-file against `git show HEAD:` and the gate runs a `git archive HEAD` extract, so
another lane's *dirty* file is invisible to it. The red is **worktree-local**: it costs any lane
that runs the suite in the shared tree a false red and an investigation, and it blocks no commit.
That is a smaller and differently-shaped problem than the one I published, and the difference is
exactly the shared-worktree-vs-extract locality this project already banks as a class.

**The build figure in `CLAUDE.md` is stale again.** It reads 36,838; collection is now **37,048**,
clean, zero errors. Correct it at the next phase close, per the rule on that line.

## Evidence

- `pytest tests/ -q --collect-only` → `37048 tests collected`, no errors.
- `run_operational_layer_signal(force=True)` →
  `{'ran': True, 'green': True, 'episode_closed': True, 'rc': 0, 'consecutive_red': 0, 'blocked_by': (), 'consecutive_green': 1, 'paged': True}`
- Prior state: `consecutive_red: 4`, `blocked_by` naming exactly the two test files.
- The pre-repair working copy is preserved at `~/.cache/se-armpop/run_value_cycle_ab.WORKING.py`
  (outside the shared tree), in addition to hunk 19 being landed.
