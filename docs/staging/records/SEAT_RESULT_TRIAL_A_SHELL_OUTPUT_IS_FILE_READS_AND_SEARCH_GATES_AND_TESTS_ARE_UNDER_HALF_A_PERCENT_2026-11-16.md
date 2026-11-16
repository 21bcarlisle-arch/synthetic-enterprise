**Severity:** LATENT · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# Trial (a) result: shell output is file reads and search; gates and tests are under half a percent (2026-11-16)

*Seat executor, Mon 16 Nov 2026, about 03:45 GMT. Pre-registration:
`SEAT_PREREG_TRIAL_A_SHELL_OUTPUT_BY_COMMAND_FAMILY_2026-11-16.md`. It was written to disk before the
run, as git blob `739e92b34a1d` (hashed before the run started), and landed in the same commit as
this result. Backlog row: `docs/operations/EFFICIENCY_BACKLOG.md` E-a.*

## Result

Families are disjoint and sum to all shell output. Shares are of all context tokens (fresh input +
cache write + cache read).

| Family | 7–14 Nov (record window) | 9–16 Nov (the allowance week) | Share of shell output |
|---|---|---|---|
| File read (cat/head/tail/sed/awk) | **16.3%** | **15.7%** | 42% |
| Search/census (grep/find/ls/wc/git log…) | **12.2%** | **11.5%** | 31% |
| Python run (a tool, daemon or inline script) | 4.5% | 4.3% | 12% |
| Other shell | 3.8% | 3.8% | 10% |
| Git write/sync | 1.3% | 1.3% | 3.5% |
| **Gate run** (commit/land/promote/pre-run gate) | **0.3%** | **0.3%** | 0.8% |
| Test run (pytest) | 0.2% | 0.1% | 0.4% |
| *All shell output* | *38.6%* | *37.2%* | |

- 22,150 and 21,254 calls. 0.411 and 0.406 tokens per character, measured from the transcripts.
- The record window gives 38.6% here against 39.1% on 14 Nov. The tokens-per-char fit moved from 0.416
  to 0.411, because more transcripts now reach back into the window.
- **The 9–16 Nov window is the "before" for every later trial this week.** On it, the first call's
  whole context is 39.1%, CLAUDE.md 10.0%, and the opening prompt 5.0%.

## Predictions

| | Prediction | Result |
|---|---|---|
| P1 | File reads lead, at 14% or more and over a third of shell output | **Held** (16.3%, 42%) |
| P2 | Search/census is second, at 8–13% | **Held** (12.2%) |
| P3 | Gate runs are under 5% | **Held, by far** (0.3%) |
| P4 | Pytest is under 4% | **Held** (0.2%) |

**What I did not predict: how small gates are.** I expected them to be a few percent. Three
explanations, ranked by evidence:
1. **Commits run in the background** (CLAUDE.md says to), so their hook output goes to a file. The
   session reads only the notification, plus a `tail` that counts as a file read.
2. **Gate output read through `tail`/`grep` on a log** is counted in file read or search. So "gate
   output" is undercounted, but by at most the part of 16% that is log tails. I cannot yet say how
   much that is: the tool does not yet tell a log file from a source file.
3. The family regexes might miss gate verbs. Checked against nine sample commands; see the test
   `test_a_commit_or_landing_is_a_gate_run_not_a_python_or_git_run`.

## What it aims

- **Trial (b) as the steer drafted it (quiet gates and tests) can reach at most about 0.5%.**
  Recommendation: drop that form. Even under explanation 2, its ceiling is the share of file reads
  that are log tails, so **measure that first** (b0 in the backlog) before building any quiet mode.
- **The levers are file reads (16%) and search (12%).** Both are content a session asked for. They are
  costly because a result is re-read by every later call: it costs its size times the calls that follow
  it. So the saving is in asking for smaller excerpts, or reading earlier and fewer times, not in hiding
  output. Whether a smaller excerpt would have done is a judgement this tool does not make.
- **The first call's context (39%) is still the largest single class.** Trials (c) and (e), the opening
  prompt and CLAUDE.md, aim at it.

## Also found: the plan's usage percentage is machine-readable (steer item 3)

Every headless `claude -p --output-format stream-json --verbose` call emits a `rate_limit_event`. It has
`unifiedWindows.five_hour.utilization` and `unifiedWindows.seven_day.utilization`, as fractions to two
decimals, with each window's `resetsAt`. Read at about 03:45 GMT, after the reset, from one Haiku call:
`five_hour 0.02` (resets 08:00Z) and `seven_day 0` (resets **Mon 23 Nov 03:00Z**, which matches the
director's weekly reset). A 15 Nov transcript shows the same event with `five_hour 0.41`.

- **So the meter test does not need four readings from the director.** The machine can read the
  weekly figure before and after each test session. Its resolution is one point of the week, so each
  test session must move several points, or the test reads the five-hour window instead.
- **What this is for.** By his words, it is for understanding the cost, never for pacing. Nothing reads
  it on a schedule, and nothing is keyed to it.
