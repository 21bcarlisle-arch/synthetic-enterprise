# [WORKER FINDING] The disk guard was in PRESSURE and reported "nothing reapable" over 3.4 GB

**Severity:** RECORDED (the hole is closed and the largest lever is fixed; one residual gap named)
**Lane:** H_harness · **Epoch:** 3 · **Atom:** unminted
**Found:** 2026-09-02, tracing the 830-test red the director asked about.

## Class registration

Belongs to `controls_that_cannot_fail`. Not a control with no caller — this one is wired, running,
and correctly alarmed. It fired, did the right thing, and achieved nothing.

## The state file, verbatim, while the box was at 89% of a 12 GB tmpfs

```json
"band": "pressure",
"free_mb": 1286,
"reaped": "nothing reapable (all scratch in use or within TTL)"
```

That last line was not true. In `/tmp` and `/var/tmp` at that moment:

| directory | size | age |
|---|---:|---:|
| `/var/tmp/head-verify-4161726` | 146 MB | **450 h** (19 days) |
| `/tmp/hc2` | 232 MB | 40 h |
| `/tmp/darprobe`, `/tmp/darprobe2` | 465 MB | 118 h |
| `/tmp/chase` | 128 MB | 105 h |
| `/tmp/gt3` | 213 MB | 40 h |

## The cause: an exclusion whose reason was never evaluated

`repo_copy_scratch` skipped any directory containing `.git`:

```python
if (path / ".git").exists():
    continue
```

The stated reason is sound — *"a registered worktree, a clone, or a gate checkout can hold
committed branches or uncommitted edits that exist nowhere else"*. **Nothing ever checked whether it
was true of the directory in front of it.** `/tmp/hc2` and `/var/tmp/head-verify-4161726` both held
`.git` directories with **zero refs and no resolvable HEAD**. An empty `.git` made 378 MB immortal,
indefinitely, and the module reported it had nothing to do.

A control that fires correctly and does nothing is the same family as one that cannot fire, and it
is harder to see: the log line says the control ran.

## And the largest lever was somewhere else entirely

`/tmp` on this box is a **12 GB tmpfs — RAM — on a 24 GB machine**. The census already knows this
and puts its SUBJECT checkout on `/var/tmp` (871 GB, real disk), saying so in a comment. It then ran
pytest with `TMPDIR` unset, so **every one of ~24,000 tests wrote its `tmp_path` into RAM.**

And `tests/background/conftest.py` has four autouse fixtures, each taking `tmp_path`, so every test
in that directory allocates one unconditionally. That is why **820 of the 830 reds were in that one
directory**, all failing at fixture setup, and why 760 were bare `OSError` — a whole directory dying
on an environmental limit, reported as 820 defects.

Measured while investigating: `pytest-of-rich` grew **1.67 GB → 3.36 GB in one hour** under three
concurrent pytest runs.

## What was done

1. **`_git_dir_may_hold_work`** evaluates the exclusion's reason instead of assuming it. A `.git`
   with no refs and no resolvable HEAD holds nothing; every other outcome — refs present, HEAD
   resolves, a `.git` FILE (a linked worktree, whose work belongs to `fork_reconciler`), git
   unavailable, the probe raising — still spares. The module's failure direction is unchanged.
   It found `/var/tmp/head-verify-4161726` on its first run.
2. **The census puts pytest's temp roots on real disk**, where its subject already goes.
3. **1.03 GB reclaimed by hand** (the five directories 40–118 h old, after establishing that none
   held a commit absent from the main repo and none had a live process).

## What is NOT fixed, and is named rather than widened

**A partial repo copy is invisible to this reaper at any age.** `_is_repo_copy` requires ALL FOUR
signature files; `/tmp/chase` was 128 MB — about half a full stem — and 105 hours old, and would
never have been a candidate. Loosening the signature trades a bounded blindness for an unbounded
risk of deleting real work, so it is left alone.

**A `.git` that git cannot READ at all still spares its parent.** Both live victims were
readable-and-empty, so widening past the measured case would be spending the one irreversible
mistake this module can make on a case that has not happened.

**Nothing sweeps session-named scratch.** A dozen directories named `headchk_*`, `omcheck`,
`verifyom`, `recap`, `mutchk`, `anchorjudge`, `atreason` — ~3.4 GB — are `git archive HEAD` clean
stems that sessions create on the director's own advice and never remove. They ARE caught by the
content-based route once past its 6-hour TTL, which is the right mechanism; they had merely never
been reaped because the reaper's other blind spot kept the pressure permanent.

## What I destroyed, and it was evidence

I reclaimed those five directories to protect a box at 90% with three concurrent test runs, which I
would do again — but I did it **before** capturing the reaper's per-directory verdict on each one.
Sizes and ages were snapshotted; the reasons were not. So for `darprobe`, `chase` and `gt3` I can
say they were dead and not why the reaper spared them, and the `.git` explanation is proven only for
the two I could still inspect. Snapshot the control's verdict, not just the symptom, before clearing
the subject.

## And the reproduction failed, which established something else

The census re-run I started to pin the errno **timed out at 3600s** and produced nothing. That is
its own finding:

    last night's real run:  58:57 wall clock
    systemd TimeoutStartSec: 3600s
    margin:                  63 seconds — 1.7%

And `run_suite`'s own timeout was **also 3600**, so it could never fire first: systemd SIGTERMs the
unit at the same instant, killing the census before `subprocess.TimeoutExpired` can be caught. A
slow night therefore produces **no verdict at all**, and no verdict is silent — the one failure mode
a control whose whole purpose is to notice cannot afford.

Fixed: the suite's timeout is 3300s, five minutes inside systemd's, so a run that overruns says
UNPROVEN instead of vanishing. Its partial output is deliberately discarded — `TimeoutExpired`
carries real `FAILED` lines, and publishing a partial red list as the complete one would, through
the register, mark every unreached red as FIXED. An outage booked as progress.

**So the errno behind the 760 `OSError`s is still an inference and is labelled as one.** It is now
also not reproducible on demand: relieving the pressure was the right call for the box and it
removed the condition. The real test is tonight's scheduled census, with `TMPDIR` on real disk — and
the register will record the answer either way, which is the point of having built it.

## What this finding does not claim

Not that `disk_headroom` is badly built — its positive-only identification, its in-use check, its
TTLs and its stated failure direction are all right, and the self-heal was added for exactly this
situation. Not that the tmpfs is misconfigured. And **not that the errno behind the 760 `OSError`s
is proven**: the mechanism is established and the shape reproduced, and the re-run that would have
settled it timed out. The specific errno remains an inference and is written as one everywhere it
appears.
