**Severity:** LATENT · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — the Lane 0 direction
`capture-the-failing-git-call-so-the-clock-can-refuse-with-its-own-cause`

# The clock can refuse with its own cause, and the instrument that found it was wrong first

**The work is done.** `tools/stale_copy_refusal.py` now distinguishes *the clock looked and has no
complaint* from *the clock could not answer*, and `tools/refresh_to_head.py` renders the second as
its own refusal — `refused_clock_could_not_answer`, naming the git call that failed — instead of as
a content verdict with a clause saying the clock had no objection.

## What was wrong

`judge` and `clock_judge` return `Loss | None`: two values over three states. `_git` is
`check=False` throughout — correctly, because absence is the ordinary answer at both ends of
`blob_at` — so a **failing** git call prints nothing on stdout and every reader turned "nothing"
into its own negative:

| reader | the `None`/`()` it returned | what else that value means |
|---|---|---|
| `last_commit_touching` | `None` | no commit has ever touched this path |
| `committed_at` | `None`, **declared** in its docstring | a `%ct` that came back unparseable |
| `distinctive_lines` | `()` | this landing added no evidence |
| `distinctive_lines` (rev-parse leg) | `()` | this is a root commit, there is no "before" |

All four collapse into one bare `None`, and `judge_copy` read it as **no complaint** at three
separate sites, each spelling the same expression: `"no complaint" if clock is None else
clock.rule`. Right for two states of three. Fail-closed on bytes, fail-**silent** on cause, on a
door whose whole job is discarding bytes.

## What is NOT claimed

The two live refusals of 2026-09-22 that commissioned this — the same enactment refused twice, HEAD
stable either side, the files byte-identical — are **still not attributed to this cause**, by this
work or by any test in it. The handing-off seat could not attribute them and did not pretend to;
neither does this. The claim made and tested here is the narrower one: **the output could not have
told you either way, and now can.**

## What changed

- `stale_copy_refusal.ClockUnanswered` and `_git_answer` — every git call the clock's verdict rests
  on raises with the failing argv and git's own stderr. Stderr is kept from the **front**: git
  prints the cause first (`unable to open loose object <sha>: Permission denied`) and the
  consequence last (`cannot simplify commit <other sha>`), so the tail is the line nobody can act
  on. The first draft tailed it; a leg caught that.
- `stale_copy_refusal.Opinion` / `opinion()` — the three answers, with the cause. It is the **only**
  place `ClockUnanswered` is caught; everywhere else it propagates, so a caller not taught the third
  state gets an exception rather than the flattering branch.
- `stale_copy_refusal.judgement_for` — the `judge`-vs-`clock_judge` suffix dispatch, called rather
  than re-cut. `refresh_to_head` had a second copy of it, hard-coded at two call sites, and had it
  wrong at one of them; that duplication is now gone.
- `committed_at` returns `int` — the declared-`None` is deleted rather than documented. A falsy
  value that a caller can misread is what the docstring had been honestly describing for weeks.
- `violations()` fails closed with rule `clock_could_not_answer`, naming **no door**: both doors this
  module can name are keyed to evidence the clock was supposed to supply, so naming one would be the
  same guess in a louder voice.
- `refresh_to_head.CLOCK_UNANSWERED`, consulted **once**, above every content branch, and whether or
  not `--base-wins` is set. The refusal is not about what the flag may do; it is about what the tool
  may *say*.

**The branch boundary for `--base-wins` did not move.** It still requires `clock.loss` and a rule in
`base_wins_rules(path)`. This changes what a copy is *told*, not what the door is *permitted* to do.

## The instrument was wrong first, and that is the more useful half

The first draft of the controls produced the failing git call by passing a **tree** sha as the base,
on the belief that `git show <tree>:<path>` reads a blob while `git log <tree>` is `fatal: not a
commit`. Measured: `git log -1 --format=%H <tree> -- <path>` exits **0 and prints nothing**. So the
first draft was measuring a different fail-silent from the one it named — and six legs failed,
which is the only reason it was caught rather than banked as evidence.

The working instrument is a genuinely degraded checkout: one loose object made unreadable, which
leaves `git show HEAD:<path>` working and every history walk at rc 128. No stub stands in for git
anywhere in the file.

### The shape left open — a finding, not a gap this work closed

`git log <rev> -- <path>` **exits 0 with empty output** when `<rev>` is a tree rather than a commit.
`last_commit_touching` reads that as *no commit has ever touched this path*, which is the same
collapse this work repaired one layer up — and **no exception can reach it**, because there is no
failure for `_git_answer` to see. Any caller passing a tree-ish base (`surgical_land` computes
result trees; `origin_reconcile` passes refs) gets a silently vouched clock. Not repaired here and
not pretended to be: it needs a positive check that the base resolves to a commit, which is a
different change with a different blast radius.

## Controls

`tests/tools/test_the_clock_could_not_answer_was_read_as_no_complaint.py`, 11 legs. Mutation swept,
six mutations, all six fire:

| mutation | killed by |
|---|---|
| `judge_copy` stops refusing on an unanswered clock | the `.py` and `.json` door legs |
| `opinion()` folds `COULD_NOT_ANSWER` back into `NO_COMPLAINT` (the original defect) | the data-door and `violations` legs |
| `violations()` waves the unanswered path through | the fail-closed leg |
| `_git_answer` tails git's stderr instead of keeping the cause | the cause leg |
| `committed_at` reverts to the tolerant read | the cause leg — see below |
| the new refusal fires on **every** path | `test_a_healthy_clock_still_reaches_every_content_verdict` |

The fifth was **silent on the first sweep**, and it is an equivalence only for the raise: the
`isdigit` guard one line later raises `ClockUnanswered` too. What the two versions do not share is
what the refusal *says* — git's `fatal: bad object` is lost. So it was a missing test, not an
equivalence, and the leg now asserts the cause and not only the raise.

The two partition legs assert **distinctness** (`len(set(...)) == 3`) rather than three
memberships: a per-answer leg passes unchanged if two states collapse, which is the defect.
