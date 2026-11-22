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
- **Every trial records the model and the CLI version it ran on** (director steer, 17 Nov,
  `advisor/done/DIRECTOR_STEER_EVERY_CLAUDE_MD_RULE_CARRIES_ITS_LINEAGE_..._2026-11-17.md`). A result
  read on one model is a prediction on the next. Backfilled only where the record already said;
  "not in the record" means the row was run or written without it.

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

| Id | Idea | Source | Expected saving, on which tokens | Trial and result | Model, CLI version | Status |
|---|---|---|---|---|---|---|
| E-a | Split shell output by command family | Steer 2a | None itself: it aims the rest | Families added to `--reading` 16 Nov. **File reads 16%, search 12%, python 4%, gates 0.3%, pytest 0.1%.** All 4 predictions held | not in the record | **KEEP** (instrument) |
| E-b | Quiet-by-default gate and test output, full log to a file | Steer 2b | Was guessed at several %; **measured ceiling ~0.5%** of context | Not run. Trial (a) shows gates and tests are 0.4% | not in the record | **DROP** in that form, unless E-b0 finds log tails are large |
| E-b0 | How much of the 16% file-read share is tails of logs (gate, run and daemon logs), not source | E-a's explanation 2 | Unknown; the ceiling for any quiet-output trial | To do: class shell reads by path, `/tmp/` and `*.log` against repo files | not in the record | NEXT |
| E-b1 | Smaller excerpts and fewer re-reads in file reads and search (the 28%) | E-a | Part of 28% of context; a result costs its size times the calls after it | Not designed. Needs a judgement of what excerpt would have done, which the tool cannot make. Within-context re-reads were 2.9% (14 Nov) | not in the record | IDEA |
| E-c | Opening prompt carries the drawn item and a pointer, not the whole staging list | Steer 2c | Up to 5.0% of context (all opening prompts) | Not run | not in the record | QUEUED |
| E-d | Delegate only large, read-once censuses (a subagent pays ~36k fixed context); amend CLAUDE.md's routing sentence | Steer 2d; 14 Nov record | Search in Opus contexts is 12%; a small grep moved out costs more than it saves | Not run. CLAUDE.md wording is trial E-e's subject, so this waits for it, one variable at a time | not in the record | QUEUED after E-e |
| E-e | CLAUDE.md: delete, then add back measured lines (minimal file in a worktree, sample turns of each kind against the full one) | Steer 2e as amended by the second steer (Boris Cherny, YC 27 Jul; arXiv 2602.11988, 2607.27250) | Up to 10.0% of context (CLAUDE.md), and 77% fixed load for the delivery seat | Pre-registered 16 Nov (`docs/staging/records/SEAT_PREREG_TRIAL_E_E_..._2026-11-16.md`): draft `docs/operations/EFFICIENCY_E_E_MINIMAL_CLAUDE_MD_DRAFT.md`, 9,052 of 23,803 characters; seat executor Opus turns split by salted work-id hash, 21–28 Nov (after E-f's Friday read), 25 per arm Amended 17 Nov (director steer): the decider is a ten-task golden set run twice per arm (`docs/operations/EFFICIENCY_E_E_GOLDEN_SET.yaml`, `tools.claude_md_golden_set`); a line comes back if its absence fails a task in either run; real turns are the secondary check. Handoff inventory and tool count: `SEAT_RESULT_E_E_EVERY_HANDOFF_MARKED_AND_THE_TOOL_COUNT_2026-11-17.md` | Real turns: Opus, version not in the record. Golden set: `claude-opus-5-5` (the set's `model:`); each run row records the model and CLI that ran | **WIRED, opens 21 Nov; golden runs before then** |
| E-f | Audit what each headless seat loads (system prompt, tool, skill, plugin and MCP listings) and switch off the unused | Second steer, item 2 | Part of the ~21% the system prompt and listings carry | **Run 16 Nov.** Haiku probe in the repo, CLI 2.1.319: 34 tools, 42 MCP servers, 14 plugins, 107 skills, 12 agents; **40,612** opening-context tokens. The live seats (worker_tick, delivery_seat, seat_executor) already pass `--strict-mcp-config`: **38,135**. Turning off the 10 non-builtin plugins with `--settings` gives **34,224 (-3,911, about -10% of the fixed load)**. In the week to 16 Nov 03:00, 574 transcripts used 0 MCP tools and 0 plugin skills. The skills used were the project's own cold-eyes-walk and phase-close (2 calls each), which stay. The PreToolUse wall hooks still fire with the plugins off. **Switched off** in `background/model_tier.py::HEADLESS_FLAGS`; delete the `--settings` pair to reverse. build_executor and autonomous_runner have no live unit and were left unchanged. After-window: the first call's context share against 39.1%, read on Friday | Haiku probe, CLI 2.1.319; model version not in the record | **TRIAL RUNNING** (re-probe each Friday: a newly synced plugin is not on the list) |
| E-f2 | `--disallowedTools` for the 11 tools no live seat called in 447 turns (CronCreate, CronDelete, CronList, DesignSync, EnterWorktree, ExitWorktree, NotebookEdit, PushNotification, RemoteTrigger, ReportFindings, Workflow) | E-f per-seat census (`SEAT_RESULT_E_F_LOAD_AUDIT_..._2026-11-16.md`) | ~2,800 tokens per call (Haiku probe, 37,427 to 34,584) | Not run. After E-e, one variable at a time | Haiku probe; CLI not in the record | QUEUED |
| E-f3 | build_executor and autonomous_runner spread `HEADLESS_FLAGS` | Same census | ~6,400 per turn if either runs (MCP and plugins); 0 turns in the week | Consistency only | not in the record | IDEA |
| E-3 | Meter weighting: two short sessions of known mix (cache-read heavy, output heavy), usage read before and after each | Steer 3 | None itself: it turns token shares into usage points | **The machine can read the meter**: `claude -p --output-format stream-json --verbose` emits `rate_limit_event` with `seven_day.utilization` (0.01 resolution) and `resetsAt`. No readings are needed from the director. Not yet run. Needs a quiet window | not in the record | QUEUED |
| E-r | Cost per result (staging closed, level move, steer done; never summed) and rework rate (code commits with a line changed on the trunk within 14 days) | Director steer 17 Nov (`advisor/done/DIRECTOR_STEER_COST_PER_RESULT_AND_REWORK_RATE_..._2026-11-17.md`) | None itself: it shows where work gets dearer or less reliable | **Run 17 Nov:** results cost about 0.2 points each; 86% of the week's spend is in sessions that landed no result (an upper bound, see E-r2); rework is 48% of code commits (40–55%) but 6% of lines, flat for four weeks. Friday section `_results_section`; `python3 -m tools.work_cost_estimate --results`. Rule: where a class's rework rises for two read weeks with non-overlapping bounds, add verification there before widening its autonomy | not in the record | **KEEP** (instrument) |
| E-r2 | Attribute a long job's landing to the session that launched it (`launch_long_job` records the launcher; the job's `landed <sha>` joins back) | E-r's no-result share | None itself: it removes the largest known under-count from E-r, so the no-result share means what it says | Not built | not in the record | NEXT |
| E-cm | Claude Code Code Mode: scripts filter tool output before the model reads it | Director share, 15 Nov 06:57 (CLI 2.1.323) | Aimed at the 37% shell output | Interactive only; every seat is `claude -p`. **Revisit when it supports `-p` or headless sessions; re-check each Friday.** Build nothing now | CLI 2.1.323 is the feature's release, not a run | WAITING (re-check each Friday) |
| E-p0 | **Speed track step 1: profile three workloads** (run, gate chain, suite), time and peak memory, ranked by share of the whole | Director steer 22 Nov (fast-anything) | None itself: it ranks every speed fix after it | **Run 22 Nov** on a contended day: `docs/operations/PROFILE_THREE_WORKLOADS_2026-11-22.md`. Gate chain and suite done. The book run was queued 22 Nov 13:30Z as declared long job `profile-book-run-cprofile` (peak 11,200 MB, writes `/var/tmp/profile-book-run/out/cprofile.json`) with P1 to P5 pre-registered in (a). The tracemalloc leg is sized from its measured peak | Opus 5.5 (`claude-opus-5-5`), CLI 2.1.319 | **KEEP** (instrument); (a) book run OWED |
| E-p1 | Control set: the Friday and Monday step tests in `test_weekly_rhythm.py`, starting with `work_cost_estimate.render_results` (14,711 `git` subprocesses, one per commit per question; 146 s of the 178 s test) | E-p0 | `test_weekly_rhythm` is 489 s of the 778 s control set: **58% of every code commit's chain**, about 36 h of gate time a week over 167 code commits | Not run. Python first: one batched `git log`. Write the prediction, replay recorded inputs and outputs of `render_results` for identical text, time the whole control set interleaved | profile: Opus 5.5, CLI 2.1.319 | **NEXT** |
| E-p2 | Site gate: three whole-site render tests at ~115 s each (empty-field, sideways-scroll, door-element) | E-p0 | ~350 s of a 694 s `site/` run: **23% of a site-data commit's ~1,540 s chain** | Not run. First find out whether they render the same pages three times; one shared render is the candidate | Opus 5.5, CLI 2.1.319 | QUEUED after E-p1 |
| E-p3 | Rest of the control set: `test_publish_scope` 57 s, `test_a_control_reads_python_as_code` 27 s, `test_isolation_guards` 24 s | E-p0 | 7%, 3% and 3% of a code commit | Not run | Opus 5.5, CLI 2.1.319 | IDEA |
| E-p4 | The suite runs serially on 16 cores (no pytest-xdist); the nightly census has not finished since before 4 Nov (bound 17,400 s, 26–29k of ~33.6k tests reached, 12–17 GB peak) | E-p0 | Tests per change and a census that finishes. The bound is memory: per-worker RSS against the 12 GB serial peak | Not run. Needs an install (a proposal, not a step-1 action) and the per-file profile (E-p5) to shard by | Opus 5.5, CLI 2.1.319 | IDEA |
| E-p5 | Instrument: `tools/head_census_progress.py` writes `report.duration` per test, so every nightly census ranks the suite by file at no extra run | E-p0 | None itself: it supplies (c)'s whole-suite per-file ranking, which a 6 h+ serial run would otherwise have to buy | Not built (step 1 changes no code) | Opus 5.5, CLI 2.1.319 | NEXT (instrument) |
| E-p6 | Gate verdict reuse when the files a gate read are unchanged (google/abfs; the 20 Nov base-judged work) | Steer item 5 | Only the control set (93% of a code commit) and the site gate (45% of a site commit) are worth reusing; the 22 other steps total ~62 s | Not designed | Opus 5.5, CLI 2.1.319 | IDEA |

**Friday, each week.**
- Read each trial's after-window against the baseline.
- Set its status.
- Read E-r's two lines (the Friday section *Cost per result and rework rate*) and act on a class whose rework rises.
- Re-check E-cm against the CLI changelog (`~/.claude/cache/changelog.md`).
- Propose the next week's trials in this file.
