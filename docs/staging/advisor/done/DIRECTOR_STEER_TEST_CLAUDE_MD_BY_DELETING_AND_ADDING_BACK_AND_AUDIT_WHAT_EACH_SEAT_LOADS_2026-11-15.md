**Severity:** LATENT · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# [DIRECTOR-STEER] Test CLAUDE.md by deleting and adding back, and audit what each seat loads (2026-11-15)

**Type:** STEER, through the advisor channel. It amends trial (e) of `DIRECTOR_STEER_A_STANDING_TRACK_FOR_USAGE_EFFICIENCY_STARTING_WITH_QUICK_WIN_TRIALS_AFTER_THE_16_NOV_RESET_2026-11-15.md` and runs inside that track, after the Mon 16 Nov 03:00 GMT reset. The director's words, from chat on Sun 15 Nov:

- 06:57 GMT, sharing https://code.claude.com/docs/en/code-mode with no comment.
- 06:59 GMT: "Also, what is latest advice on size of claude.md etc. I thought Boris was now saying make it really small? Is ours small? Are we following best practice in what drives wasteful token burn"
- 07:01 GMT, on the advisor's recommendation below: "Yee" (yes)

## What the advisor found (check it)

**Ours is not small.** `CLAUDE.md` is 366 lines and 23,892 characters, about 9,900 tokens at the measured 0.416 tokens per character. It was 9.8% of all context tokens in the 7–14 Nov week, and it is part of the ~36k fixed context each subagent call pays.

**The current advice (secondhand; the advisor found no primary transcript):**
- **Boris Cherny, Y Combinator podcast, 27 Jul 2026.** His team cut more than 80% of Claude Code's own system prompt when Opus 5 shipped, and the agent did better: "A lot of the stuff in the system prompt was correcting for these behaviors that the model should have known." His method: delete the whole prompt, then add lines back one at a time, measuring each.
- **arXiv 2602.11988 (ETH Zurich).** Context files did not generally improve task success and raised inference cost by over 20%.
- **arXiv 2607.27250** (288 runs, 17 tasks). Context strategy did not measurably change correctness.
- Both studies are on ordinary coding tasks, not a governance-heavy autonomous project, so transferability is unproven. That is why this is a trial, not a cut.
- **The rule of thumb that follows.** Keep facts the model cannot find in the repo: commands, prohibitions, costly risks, conventions with no in-repo signal. Treat as suspect lines that try to raise capability, especially corrections written for older models.

**A rough read of ours against that test (the advisor's judgement):**
- **Clearly kept:** the walls, hook-bypass, commit mechanics, map headroom, the mission and canon quotes, and "Where the rules live".
- **Suspect:** most of "How to behave when no rule applies", about a third of the file. Those habits were learned on this project, but nobody has tested whether Opus 5.5 still needs them stated.
- **Shrinkable to pointers:** the operating model's mechanics, which are enforced in code.

**Two other things we don't know:**
- **What each headless seat loads.** About 21% of all context tokens is Claude Code's own system prompt plus tool, skill, plugin and MCP listings. Nobody has checked which MCP servers, plugins and skills each headless seat loads, or whether it uses them.
- **Code Mode** (CLI 2.1.323, 13 Nov, experimental). Claude writes JavaScript that calls its tools and returns only the output it needs, which targets the 39% shell-output share. It is interactive-terminal only: not `-p`, the Agent SDK or cloud sessions. Every machine seat is headless `claude -p` (`background/delivery_seat.py`, `build_executor.py`, `autonomous_runner.py`), so it is unavailable to us now. In auto mode the classifier reviews the script, not run-time values; PreToolUse hooks still apply to each call.

## The outcome wanted

1. **Trial (e) becomes delete-and-add-back.** Draft a minimal `CLAUDE.md`: the walls, commit mechanics, map headroom, the mission and canon quotes, and pointers. Run a sample of real seat turns of each kind on the minimal file against the full one, in a worktree; the live file is unchanged until the result. Compare:
   - gate refusals;
   - wall-hook denials;
   - G5 and one-way-door refusals;
   - landed work and its later reverts or corrections;
   - tokens per turn from `tick_burn_rate`.

   Pre-register the prediction. Add back only lines whose absence shows in those measures, and name the evidence for each one kept. The 35,000-character cap is unchanged.
2. **Audit what each seat loads.** For each headless seat kind, list the system prompt size, tool and skill listings, plugins and MCP servers loaded, and which were used in the measured week. Switch off what a seat never uses, as a reversible trial with a before and after.
3. **Add Code Mode to the efficiency backlog:** "revisit when it supports `-p` or headless sessions; re-check each Friday". Build nothing for it now.

## Reading-log entries to append

| Date | Source | Shared by | What we took | Verdict |
|---|---|---|---|---|
| 2026-11-14 | iulio/RoCast (MIT, 0 stars): Romanian solar and wind 15-minute probabilistic forecasting (SEVIRI, Earth-2, pvlib, quantile regression), one two-day test window | Director | The world replays GB outturn, and the company needs only customer-scale PV. Two touch points: pvlib clear-sky for the PV knowledge page, and range scoring (CRPS, pinball loss, coverage) for the Timestral benchmark; its 80% band covered 90%. | NOT FOR US |
| 2026-11-15 | Graphify-Labs/graphify (Apache/MIT, ~145k stars): a code and docs knowledge graph via tree-sitter, run as a skill | Director | "Cut token spend by 80%" is marketing for the paid cloud product, and its benchmarks measure memory recall, not code navigation. It targets file reading, which is small for us (no file over 0.89%). | NOT FOR US |
| 2026-11-15 | Claude Code Code Mode (2.1.323, experimental), via clauding.de, developersdigest.tech and dev.classmethod.jp; the official page could not be fetched | Director | Scripts that filter tool output before Claude reads it, aimed at our 39% shell output, but interactive only; our seats are all `-p`. | BACKLOG (revisit when headless) |
| 2026-11-15 | Boris Cherny on cutting the system prompt (YC podcast, 27 Jul), via bestagent.dev and news.ainauten.com; arXiv 2602.11988; arXiv 2607.27250 | Director | Delete and add back, measured per line; context files change behaviour more than they change correctness. | TRIAL (trial e) |

## Rules

- **The walls are enforced in code**, so the risk in the trial is behaviour, not safety. Keep the walls' text in the minimal file anyway.
- **One variable at a time.** The CLAUDE.md trial and the load audit run separately.
- **Never trade correctness for tokens.** A dropped line that raises refusals, reverts or corrections goes back in.

## Risk

Touches: a worktree copy of CLAUDE.md, seat configuration (MCP servers, plugins), the efficiency backlog.
Blast radius: the trial's sample turns only. Seat configuration changes are reversible.
Probable failure modes:
- **A small sample hides a rare failure** that a dropped habit prevented. Name the sample size and the bound it earns. A habit tied to a named past incident needs stronger evidence to drop.
- **Switching off a tool a seat uses rarely but critically.** Use a measured week, not a guess, and give each switch-off a reversal.

Proportionality: harness, reversible. Implement within the efficiency track after the reset.

— Director steer, 15 Nov 2026, his words above; the reading and drafting are the advisor's.

## Done

Seat executor, Mon 16 Nov 2026, 06:50 GMT. All three items and the reading log had already landed in e390e0da71 and 9554dcf49f; this commit only files the steer.
- **1. Trial (e) is delete-and-add-back:** pre-registered in `docs/staging/records/SEAT_PREREG_TRIAL_E_E_MINIMAL_CLAUDE_MD_AGAINST_THE_FULL_ONE_2026-11-16.md` (minimal draft 9,052 of 23,803 characters; 25 Opus seat-executor turns per arm, 21–28 Nov; the bound 25 turns earns is stated). The live `CLAUDE.md` and its cap are unchanged. Backlog row E-e.
- **2. Load audit (E-f):** run 16 Nov; ten unused plugins switched off for headless seats (-3,911 opening tokens, reversible in `background/model_tier.py::HEADLESS_FLAGS`); 11 never-called tools queued as E-f2, after E-e, one variable at a time.
- **3. Code Mode:** backlog row E-cm, "revisit when it supports `-p` or headless sessions; re-check each Friday". Nothing built.
- **Reading log:** the four rows are in `docs/institutional/reading_log.md`.
