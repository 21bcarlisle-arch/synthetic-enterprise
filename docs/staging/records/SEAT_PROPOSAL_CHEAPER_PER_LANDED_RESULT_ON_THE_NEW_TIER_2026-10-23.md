**Severity:** BLOCKING · **Lane:** A_strategy_governance · **Epoch:** unassigned · **Atom:** `unminted`

# SEAT PROPOSAL: a cheaper landed result on the new tier, by route, with what was enacted (2026-10-23)

This answers two advisor files: `DIRECTOR_READING_THE_NEW_TIER_IS_A_QUARTER_OF_THE_OLD_2026-10-23.md` and
`DIRECTOR_STEER_CHEAPER_PER_LANDED_RESULT_SCRIPTS_TIERS_AND_EFFORT_2026-10-23.md`. Both are now in `advisor/done/`.
Every figure below is weighted USD at Anthropic's list prices, and every one was printed by
`python3 -m tools.tick_burn_rate --routes FROM TO`. That command is new in this commit, so the breakdown now costs no tokens.

## 1. The headline, and a correction to the target

- **One point now costs about USD 7.9 weighted.** That comes from one interval: 06:55 to 09:45 BST, 4 points. At ±0.5 point of reading resolution the band is USD 6.9 to 9.0.
- **The old tier cost USD 23.4 a point**, from Tue 17:37 to Thu 14:52, 15 points. So a point now buys about a third of what it did. The advisor expected about USD 6 to 7. The fit is a little above that and inside its own band.
- **Correction: the cut needed is 1.3 to 1.7 times, not 4 times.** "Plan for a quarter of last week's throughput" assumes last week used the whole old allowance. It did not:
  - Last week cost USD 991, from Fri 16 Oct 06:55 to Fri 23 Oct 06:55 BST. That is about 42 points of the old tier.
  - On the new tier the same week would be about 125 points. Landing at the 94% reserve line needs a cut of about **25%** (1.34x cheaper per landed result).
  - At last week's weekday pace, Mon to Thu at about USD 177 a day, the cut needed is about **40%** (1.67x).
  - At today's pace, USD 10.2 an hour under the site-steer load, it is about **57%**.
- **This weekend is fine without a width change.** From 06:55 BST to now has cost about 8.5 points. The 62 hours to the Monday 04:00 BST reset add 46 points at last week's average, or 80 points at today's rate. That ends the window at 55% to 88%, under 94% either way.

## 2. Spend by route, last week (old tier, Fri 16 to Fri 23 Oct 06:55 BST)

| route | weighted $ | share | sessions | landed | $ per landed | cost mix: output / 1h cache write / read |
|---|---|---|---|---|---|---|
| worker tick | 481.0 | 48.5% | 187 | 149 | 3.23 | 21% / 36% / 43% |
| seat executor, map and lane-0 draws | 295.7 | 29.8% | 112 | 93 | 3.18 | 22% / 36% / 42% |
| seat executor, advisor items | 96.3 | 9.7% | 22 | 21 | 4.59 | 20% / 28% / 51% |
| delivery seat (orientation, every 3 h) | 70.3 | 7.1% | 41 | 2 | n/a (it orients; others land) | 20% / 57% / 22% |
| forks and subagents | 34.6 | 3.5% | 16 | — | — | mostly 5-minute writes and reads |
| director's console | 13.5 | 1.4% | 1 | 1 | — | — |

- **What a turn costs, and why.** A median executor turn costs USD 2.6 and sends about 55 messages.
  - Every message re-reads the whole context, so about 43% of the spend is cache reads.
  - About 35% is writing new context into the 1-hour cache.
  - About 21% is output, thinking included.
  - Input tokens round to 0%.
- **Advisor items cost 44% more per landed result than map draws.** That is USD 4.59 against 3.18. The turns run longer: reads are 51% of their cost against 42%.
- **The fixed opening context.** Measured today with `claude -p` probes on Haiku 5.5 sending one word:
  - Claude Code itself is about 28,000 tokens.
  - The account's MCP connectors add about 2,500.
  - This repository adds about 21,600: `CLAUDE.md`, the 36.5 KB memory index (24.4 KB is loaded, the rest is cut off), and the session hooks.
  - Each 1,000 tokens of opening context costs about USD 0.018 a turn: one write, then about 50 re-reads. Across about 360 turns a week that is about **USD 6.5 a week per 1,000 tokens, roughly 0.66% of spend**.

## 3. What a deterministic script could answer, and its share

| mechanical work | evidence | share of spend it would remove |
|---|---|---|
| the weekly breakdown by route (this item) | it took a full Opus turn by hand | under 1%, now enacted |
| landing, waiting, status and census commands inside turns | about 15% of tool-result bytes in last week's worker and executor turns | at most about 3%, and most are already scripts |
| reading code (`sed`, `cat`, `grep`, `Read`, `git show`) | about 50% of tool-result bytes | 0%. This is the work itself. |
| the HEAD-red register as the worker tick's lead reason | it heads 240 of 250 worker doorbells | unknown. The next measurement is whether each tick re-derives the register. |

**Conclusion: scripts are a small lever here, at most about 4%.** The tokens go into reading code and writing reasoning. The large levers are the per-turn fixed context, which model each turn runs on, and how long turns run.

## 4. The levers, each with its estimated saving and its measure

Savings are a share of the week's weighted spend at constant throughput. Each is measured by `--routes` over matched windows (USD per landed result, by route) and by the first message's `cache_creation_input_tokens`.

| # | lever | estimated saving | status | how to reverse |
|---|---|---|---|---|
| E1 | `--strict-mcp-config` on the worker-tick, seat-executor and delivery-seat spawns (`model_tier.HEADLESS_FLAGS`). No unattended turn called an MCP tool in the week; 0 calls. | about 1.6% (2,500 tokens a turn) | **enacted** | empty `HEADLESS_FLAGS` in `background/model_tier.py` |
| E2 | `tick_burn_rate --routes`, prices for Sonnet 5.5 and Fable 5.1, and the 09:45 reading in `POINT_READINGS` | under 1% directly; makes every other measure free | **enacted** | revert the commit |
| P1 | Cut the repository's 21,600-token opening context by about half: bring the memory index back under its own limit and move detail into topic files | about 7% | **enacted 23 Oct**: 21,517 → 10,721 tokens (−50%), see below | memory: copy `MEMORY_index_before_the_2026-10-23_cut.md` back over `MEMORY.md`; `CLAUDE.md`: revert the commit |
| P2 | Sonnet 5.5 (exactly half Opus 5.5 on every token class) for routine draws, piloted against a concurrent Opus control | up to about 15% if about a third of turns move and land at the same rate | **blocked, see F1**; pilot designed below | the pilot file's `enabled: false` |
| P3 | Delivery-seat orientation every 6 h instead of 3 h. Each of its turns opens on about 91,000 tokens. | about 3.5% | proposed, not enacted: the seat is the only place the whole is held (director, 30 Aug) | `tick_mode` |
| P4 | Subagents for search, census and log reading on Haiku 5.5 or Sonnet 5.5. This is already in `CLAUDE.md`. | at most about 2% (all subagents are 3.5% of spend) | standing rule | n/a |
| P5 | 5-minute cache writes instead of 1-hour. 1-hour writes are 35% of spend, and a 5-minute write is priced at 62.5% of one. | up to about 13%, **GAP** | research only | n/a |
| P6 | Medium effort for routine turns | 0%: **already in force**. This executor turn's environment carries `CLAUDE_EFFORT=medium`, and nothing sets effort in the spawns or settings. | no move to low proposed | n/a |
| P7 | Narrower width | linear in throughput, so it does not cut cost per landed result | not this weekend. From Monday, only if the first two readings project above 94% after E1, P1 and P2. | `tick_mode` |

**What P5's GAP is made of.** Three things are not established:
- whether the CLI lets a subscription session choose the TTL;
- whether the allowance meters the TTL the way list price does;
- whether 10-minute gate waits would make a 5-minute cache re-write and cost more.

**The projected week on the new tier.** E1 plus P1 plus P4 come to about 10%. P2, if it passes its rule, takes that to about 25%, or 1.34x. That matches last week's average throughput at 94% and falls short of the weekday pace. Holding the weekday pace would also need P3, or a P5 result that is not yet known.

**Recommendation for the director:** stay on the new tier. The case for the bigger tier is not made on this evidence. Read again at Wednesday's reading. This is raised in `for_the_director`.

## 5. Findings

**F1: the Sonnet routing in `model_tier` cannot be reached from the worker tick.**
- All 250 worker-tick doorbells logged since 16 Oct in `docs/observability/model_tier_log.jsonl` went to Opus, all 250 with reserved classes `finding_disposition` and `level_move`.
- The cause: the tick's doorbell joins the reactive reasons (the HEAD-red register on 240 of them) with the drawn item. A reserved marker anywhere forces Opus, so no drawn item can ever be classed as routine.
- The pilot window also expired on 19 Aug. Re-enabling it would therefore save exactly nothing.
- Before P2 can run, the classifier must grade the drawn item apart from the reactive reasons, and a control must assert that the Sonnet branch CAN be taken.
- **Fixed 23 Oct.** `model_tier.classify` now grades the drawn item (after `; ALSO -- `) apart from the reactive reasons. If only the drawn item is cheap, the Sonnet turn is handed only the drawn item, and the reactive reasons wait for the next Opus tick. `test_the_sonnet_branch_can_be_taken_on_a_real_worker_doorbell` holds both legs on the 23 Oct doorbell shape.
- **What this does not change.** The worker tick's drawn item is almost always a maturity-map BUILD draw, which is a level move and stays Opus by the director's 12 Aug rule. Its pilot classes also expired on 19 Aug. So the worker tick is now reachable but still all Opus. P2's saving rides on the executor pilot below.

**F2: a headless `claude -p` in the repository is captured as the director's console words.**
- Measuring the opening context, a one-word `claude -p` probe run in this worktree (it inherited `SE_SEAT_EXECUTOR=1`) was written to `docs/staging/DIRECTOR_CONSOLE_2026-10-23.md` as a verbatim director turn.
- The cause: `.claude/hooks/capture_director_console.py` asks only `is_resident_seat()` and the text classifier `is_director_prompt`, and a short plain prompt passes both.
- It was caught in the isolated worktree and deleted unlanded. The shared tree has no copy.
- Until it is fixed, run probes with `SE_SEAT=foreign`. The fix is for the hook to refuse when any seat marker (`SE_SEAT_EXECUTOR`, `SE_SBI_WORKER`, `SE_DELIVERY_SEAT`) is set.
- **Fixed 23 Oct.** The hook now refuses when any of `_seat.SEAT_SPAWN_MARKERS` is set. `tests/hooks/test_seat_guard.py::TestCaptureDirectorConsoleGuard` holds the whole partition, and it reds both when the guard is removed and when it refuses everything.
- **Not fixed, same shape:** `log_director_input.py` also guards only on `is_resident_seat()`. It hands the prompt to a classifier rather than filing it verbatim, so it was left alone.

## 6. The P2 pilot, pre-registered before launch

- **Design.** One executor turn in four, chosen by a hash of the work id, runs on Sonnet 5.5, but only when the drawn item carries no reserved marker. The other three are the concurrent Opus control, drawn from the same pool.
- **Switch-on rule** (machine's under the 23 Oct ruling; a dated exception is recorded, per G17). After at least 20 turns in each arm, Sonnet 5.5 stays on for that class only if all three hold:
  - its landed share is within 10 points of the control;
  - rework is no higher than the control's (a fix commit to the same paths within 72 h);
  - it costs at least 25% less per landed result.
- **Revert rule.** Otherwise it reverts, and the result is said beside this rule.
- **Prediction, written now:** it lands about 10 points below the control at about 45% lower cost per landed result, which passes. The 12–14 Oct trial (33% against 74%) was Sonnet 5 with an advisor, not Sonnet 5.5, and this prediction may be wrong for that reason.
- **Opened 23 Oct**, as designed above: `model_tier.executor_arm`, declared in `docs/observability/executor_tier_pilot.yaml` (one in 4; window 23 Oct to 6 Nov; fails closed to Opus outside it). Reserved items are excluded before the hash. Over the 860 work ids the executor has ever run, the hash puts 214 (24.9%) in the Sonnet arm. Each decision is logged to `model_tier_log.jsonl` with `route: seat_executor`, its arm and its work id. A Sonnet turn is not handed the advisor channel's rung zero, which carries director steers; the next Opus turn reads it. `SE_EXECUTOR_MODEL`, if set, overrides the pilot.
- **Not yet built:** the grader for the switch-on rule. It joins the log's arm to `seat-executor-log.md`'s outcome by work id, and cost comes from `tick_burn_rate --routes`. It is due before 20 turns accumulate in each arm, about 6 Nov.

## 7. P1 result, 23 Oct

**Prediction, written before measuring:** the repository adds about 21,000 tokens. Of that, the memory index is about 7,000 and `CLAUDE.md` about 6,500.

**Method.** A one-word `claude -p` on Haiku 5.5 with `--strict-mcp-config` and `SE_SEAT=foreign`. Opening tokens are cache write plus cache read plus input. Each component is measured by ablation: a scratch directory holding only that component, and the worktree with `CLAUDE_CODE_DISABLE_AUTO_MEMORY=1`.

| | before | after |
|---|---|---|
| empty directory (Claude Code itself; the control) | 25,626 | 25,626 |
| this repository | 47,143 | 36,347 |
| **the repository's addition** | **21,517** | **10,721** |
| of which the memory index | 12,068 | about 1,300 |
| of which `CLAUDE.md` | 8,468 | about 8,000 |
| of which `.claude/` (agents, skills, hooks) | about 960 | unchanged |

**The prediction was wrong on the split.** The memory index cost nearly twice what I predicted. Its long underscore filenames tokenise at about 2 characters a token, against about 3 for `CLAUDE.md`'s prose.

**What changed.**
- **Memory.** `MEMORY.md` went from 36.5 KB to 2.5 KB. It now holds seven topic-file pointers and fifteen every-turn rules. Before the cut, the 154 entries that existed only in `MEMORY.md` were appended verbatim to their sections' `index_*.md` files, and all 163 links in the old index were checked as reachable from a topic file.
- **`CLAUDE.md`.** About 1,300 characters of machine-written anecdote were shortened: the bill-shock elaboration, the competitor-model drafts, the three-doors story, the £55 story, the qwen history and the Build line's history. No director quote, rule or pointer was removed.

**Worth:** about 10,800 tokens a turn, about USD 70 a week, about 7% of spend.
