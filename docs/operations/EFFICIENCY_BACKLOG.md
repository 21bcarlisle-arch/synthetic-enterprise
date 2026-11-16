# Efficiency backlog: what the work costs against the weekly allowance

*The one standing list of efficiency ideas, trials and results. The director's steer, 15 Nov 06:45 GMT:
"a continuous track of weekly allowance usage optimisation and efficiency measures, ideas and
backlog". `docs/staging/advisor/DIRECTOR_STEER_A_STANDING_TRACK_FOR_USAGE_EFFICIENCY_..._2026-11-15.md`.
The Friday review's burn section (`background/weekly_rhythm.py::_burn_section`) reads this file and
proposes next week's trials here. There is no gate and no daemon.*

**Rules.**
- **One variable at a time.** Pre-register each trial before it runs.
- **Before and after from `python3 -m tools.tick_burn_rate --reading FROM TO`,** keyed to token share,
  and to usage points once the meter test (E-3) reports.
- **A trial that hides something a session needed is reverted,** and that is its result.
- **The allowance is understood, not policed.** Nothing throttles on the percentage.

**Baseline ("before"), 9 Nov 03:00 to 16 Nov 03:00 UTC.** 21,254 calls. Shares of context tokens:
- the first call's whole context: 39.1%
- CLAUDE.md: 10.0%
- the opening prompt: 5.0%
- all shell output: 37.2%
  - file reads: 15.7%
  - search/census: 11.5%
  - python runs: 4.3%
  - gate runs: 0.3%
  - pytest: 0.1%

Source: `docs/staging/records/SEAT_RESULT_TRIAL_A_..._2026-11-16.md`.

| Id | Idea | Source | Expected saving, on which tokens | Trial and result | Status |
|---|---|---|---|---|---|
| E-a | Split shell output by command family | Steer 2a | None itself: it aims the rest | Families added to `--reading` 16 Nov. **File reads 16%, search 12%, python 4%, gates 0.3%, pytest 0.1%.** All 4 predictions held | **KEEP** (instrument) |
| E-b | Quiet-by-default gate and test output, full log to a file | Steer 2b | Was guessed at several %; **measured ceiling ~0.5%** of context | Not run. Trial (a) shows gates and tests are 0.4% | **DROP** in that form, unless E-b0 finds log tails are large |
| E-b0 | How much of the 16% file-read share is tails of logs (gate, run and daemon logs), not source | E-a's explanation 2 | Unknown; the ceiling for any quiet-output trial | To do: class shell reads by path, `/tmp/` and `*.log` against repo files | NEXT |
| E-b1 | Smaller excerpts and fewer re-reads in file reads and search (the 28%) | E-a | Part of 28% of context; a result costs its size times the calls after it | Not designed. Needs a judgement of what excerpt would have done, which the tool cannot make. Within-context re-reads were 2.9% (14 Nov) | IDEA |
| E-c | Opening prompt carries the drawn item and a pointer, not the whole staging list | Steer 2c | Up to 5.0% of context (all opening prompts) | Not run | QUEUED |
| E-d | Delegate only large, read-once censuses (a subagent pays ~36k fixed context); amend CLAUDE.md's routing sentence | Steer 2d; 14 Nov record | Search in Opus contexts is 12%; a small grep moved out costs more than it saves | Not run. CLAUDE.md wording is trial E-e's subject, so this waits for it, one variable at a time | QUEUED after E-e |
| E-e | CLAUDE.md: delete, then add back measured lines (minimal file in a worktree, sample turns of each kind against the full one) | Steer 2e as amended by the second steer (Boris Cherny, YC 27 Jul; arXiv 2602.11988, 2607.27250) | Up to 10.0% of context (CLAUDE.md), and 77% fixed load for the delivery seat | Not run. Load audit E-f goes first | QUEUED |
| E-f | Audit what each headless seat loads (system prompt, tool, skill, plugin and MCP listings) and switch off the unused | Second steer, item 2 | Part of the ~21% the system prompt and listings carry | First look, 16 Nov: one headless Haiku call (CLI 2.1.319, cwd `/tmp`) loaded **14 plugins, 42 MCP servers (Gmail, Slack, Snowflake, Notion and others from the operations, design, legal, finance and data plugins), 103 skills and 34 tools**. Not yet measured: their token share and whether any seat used one in the week | NEXT (before E-e) |
| E-3 | Meter weighting: two short sessions of known mix (cache-read heavy, output heavy), usage read before and after each | Steer 3 | None itself: it turns token shares into usage points | **The machine can read the meter**: `claude -p --output-format stream-json --verbose` emits `rate_limit_event` with `seven_day.utilization` (0.01 resolution) and `resetsAt`. No readings are needed from the director. Not yet run. Needs a quiet window | QUEUED |
| E-cm | Claude Code Code Mode: scripts filter tool output before the model reads it | Director share, 15 Nov 06:57 (CLI 2.1.323) | Aimed at the 37% shell output | Interactive only; every seat is `claude -p`. **Revisit when it supports `-p` or headless sessions; re-check each Friday.** Build nothing now | WAITING (re-check each Friday) |

**Friday, each week.**
- Read each trial's after-window against the baseline.
- Set its status.
- Re-check E-cm against the CLI changelog (`~/.claude/cache/changelog.md`).
- Propose the next week's trials in this file.
