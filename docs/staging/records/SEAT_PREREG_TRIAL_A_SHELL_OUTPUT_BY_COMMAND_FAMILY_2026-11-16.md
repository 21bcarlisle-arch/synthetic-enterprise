**Severity:** LATENT · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# Pre-registration: trial (a), the 39% shell output split by command family (2026-11-16)

*Seat executor, Mon 16 Nov 2026, about 03:30 GMT, after the reset. Written before the split was run.
The steer is `docs/staging/advisor/done/DIRECTOR_STEER_A_STANDING_TRACK_FOR_USAGE_EFFICIENCY_..._2026-11-15.md`,
item 2a. The backlog row is `docs/operations/EFFICIENCY_BACKLOG.md` E-a.*

## The question

Of the shell (Bash) output that was 39.1% of context tokens in the week of 7 to 14 Nov, which command
family carries the most? The answer decides where trial (b), quiet-by-default output, goes first.

## What changed in the instrument

`tools.tick_burn_rate.bash_kind` already classed each shell call by its first verb. Gate output was
hidden inside the "python run" and "git write" kinds. Commits and landings print every hook's output,
and the hand pre-runs print the cheap gates. A new kind, **gate run**, now comes ahead of those two:
`git commit`, `surgical_land`, `promote_worktree_landing`, `ruff`, the write-time, document and level
gates, and the finding-class, severity, staging-room and CLAUDE.md-integrity checks. `--reading` now
prints the families as one disjoint table that sums to all shell output.

## Predictions (filed before the run)

The 14 Nov record gives shell file reads 16.6% and python runs 4.9%. Bash search/census is inside the
12.5% Opus search share, which also counts the Grep and Glob tools.

- **P1. File reads (cat/head/tail/sed) lead,** at 14% or more of context tokens and over a third of shell
  output.
- **P2. Search/census is second,** at 8 to 13%.
- **P3. Gate runs are under 5% of context tokens.** The gates are long, but commits are few per session,
  and a landing that refuses is short.
- **P4. Pytest is under 4%.**
- **Consequence, stated now.** If P1 and P3 hold, quieting gate and test output (the steer's example
  for b) can reach at most 9%. The top family would then be file reads, which are content a session
  asked for, not noise. So trial (b) would move to "read an excerpt, not the file" in the shell-read
  family, or stop at the small gate-and-test share. Neither is decided here.

## Windows

- **Primary:** 7 Nov 06:00 to 14 Nov 06:00 UTC, the same window as the 14 Nov record, so the families
  reconcile with its 39.1%.
- **Second:** 9 Nov 03:00 to 16 Nov 03:00 UTC, the allowance week just closed. This is the "before"
  reading for every later trial this week.

Run: `python3 -m tools.tick_burn_rate --reading 2026-11-07T06:00 2026-11-14T06:00`, then the second window.
