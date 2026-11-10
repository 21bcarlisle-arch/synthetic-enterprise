**Severity:** LATENT · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# [DIRECTOR-STEER] Test Fable 5.2 against Opus 5.5 on our own work, and say how models are picked (2026-11-10)

**Type:** STEER, through the advisor channel. The director's words, from chat on Tue 10 Nov:

- 05:43 GMT: "Also I note fable 5.2 is released and is better and more token efficient for some activities. We should do some research and some tests to see if it can be helpful to us in some circumstances versus opus 5.5 and how we pick models."

**When:** the research now. The tests are sized against the weekly allowance under P12, and they do not displace the correctness exit test.

## What the advisor established (10 Nov; check it)

- **Released 9 Nov 2026.** Model id `claude-fable-5-2`. 1M context, 128K output.
- **Effort and thinking:** adaptive thinking is always on, and default effort is `high`, against Opus 5.5's `medium`. There is a fast mode at premium pricing.
- **API price is double Opus 5.5:** $8/$40 per MTok against $4/$20, with cache reads at $0.20. We run on a subscription allowance, so what matters is how fast each model draws the allowance per unit of finished work. Neither price nor token count alone tells us that.
- **Anthropic positions it for** "demanding reasoning and long-horizon agentic work". The docs page gives no guidance on choosing between Fable and Opus.
- **Fable carries extra safeguards** (biology, cyber, LLM R&D) with classifier refusals and a fallback to another model ([Refusals and fallback](https://platform.claude.com/docs/en/build-with-claude/refusals-and-fallback)). Some of our harness work concerns agents, evals and model routing, and could plausibly touch the LLM R&D line. That is a thing to measure, not assume.
- **Our routing today** (`background/model_tier.py`): Opus is the default and the fallback. Sonnet is reachable only by enumerated pilot classes, data-driven by `docs/observability/model_tier_pilot.yaml`. This rests on his 12 Aug asymmetric loss: "I'd rather spend the tokens than get shallower work."

## The questions

1. **Research:** read the announcement, the system card and the refusal-and-fallback page. What does Fable 5.2 do better than Opus 5.5, by Anthropic's own evidence, and on which kinds of task? Grade the evidence. Record it in the reading log.
2. **Test on our work, not on benchmarks.** Choose a small set of real, already-labelled tasks from our own record, where we know the right answer. Candidates:
   - the reading-review trial's known-bad and clean commits;
   - a design read whose defects were confirmed;
   - a diagnosis we closed (the naive organ's loop, for example);
   - a routine measurement tick.

   Run Opus 5.5 and Fable 5.2 blind, at comparable effort. Report four numbers separately, without blending: quality (confirmed against the known answer), tokens used, allowance drawn, and time. Also report any refusal or fallback on Fable, with the task that triggered it.
3. **How models are picked.** From those results, recommend whether `model_tier.py` gains a Fable class, and for which work. Say what default and fallback each class should have. The asymmetric loss still governs, so a cheaper or faster model needs evidence that quality holds. Fable is a candidate where depth compounds (diagnosis, design reads, end-to-end checks), not a new default by assumption. If a refusal could stall unattended work, the fallback must be proven to fire.

## Not wanted

- No change to the default model before the test reports.
- No benchmark-only conclusion.
- No new gate.

## Also: one reading-log row for you to append

The advisor's own commit of this row was refused by the site lane. The live door test cannot reach poesys.net from the advisor's container (403 at the proxy), and that failure is correct and fail-closed. Append this row to `docs/institutional/reading_log.md` and regenerate the feed (`tools/reading_log_feed.py --write`) from Skynet, where the door test can run. Add the 9 Nov Fable 5.2 research to the log too, once item 1 above is done.

| 10 Nov | An AI-written research summary the director shared: "AI delegation fails from uncurated context", citing Ehsani et al. (arXiv 2601.15195), Microsoft's delegation-failure taxonomy, a "verification scarcity" paper and the Glean Work AI Index | Silent, low-noticeability failures burn the overseer's attention; agent PR failures spike across module boundaries; the bottleneck is verification, not generation. Four rules: distil sub-agent output, map code before writing, deterministic hard gates, machine-readable boundaries | Mixed: Ehsani and the Microsoft taxonomy are real; the "verification scarcity" paper (26.3% corrective rate) and the Glean figures could not be found or verified | Already have | All four rules exist: helpers return summaries; the reuse index, knowledge-before-build and design reads before build; about 21 mutation-proven gates, with the standing-red ledger as "break the loop after two"; CLAUDE.md, path rules and the wall. Silent failure is our no-caller and drift classes. One use: test "touches several areas at once" as a reader-selector predictor at the 11 Nov calibration | Independent review |

## Risk

Touches: a bounded test spend, `model_tier.py` and its pilot file later, and the reading log.
Blast radius: allowance spend this week. A later routing change affects every unattended route.
Probable failure modes:
- A comparison confounded by effort level or caching, because Fable defaults to high effort and Opus to medium. Hold effort equal, or report both settings.
- A Fable classifier refusal on harness work silently stalling a tick. Prove the fallback.

Proportionality: reversible and narrow — just do it.

— Director steer, 10 Nov 2026, his words above; the research and drafting are the advisor's.
