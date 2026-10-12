<!-- SUPERVISOR_DRAW: self-drawable -->

# [WORKER-MINTED] Trial Sonnet 5.5 + Opus advisor on the worker ticks (2026-10-12)

**Fate (2026-10-12, clear-the-decks):** ATOM -- fresh director-steer-derived mint; a model-tiering conflict was found before any build, trial embargoed until the weekly allowance resets (P2)

**Source:** `DIRECTOR_STEER_ADVISOR_TRIAL_BACKLOG_2026-10-11.md` (moved to `in_progress/` beside
this). The steer carries no `WORK THIS CREATES` block; its `## Done when` and `## How to judge it`
name the work, so the deliverables below are minted from those sections. Requesting a block from
the director for a steer that already says what done is would be ceremony on his path, so this
mint does not.
**Lane:** A_strategy_governance · **Embargo (his words):** "Do not start before the weekly
allowance resets, and do not let it displace supplier work in the current priority order." The
seat does not estimate the allowance; draw this only once the reset has happened.

## A conflict found before any build — read first

The trial cannot be run as written through the existing tiering, and the reason is measured.

`background/model_tier.py` (director rule of 2026-08-12: "Diagnosis, science, level moves and wall
decisions stay Opus") forces Opus whenever any RESERVED marker is in the doorbell. Over the 14 days
to 2026-10-12, `docs/observability/model_tier_log.jsonl` holds **586 SPAWNED worker ticks; 586 were
Opus, 0 carried no reserved marker**. `unprocessed staging --` alone fired on 584 of them, because
the staging root is never empty. So:

- built as a `model_tier_pilot.yaml` class, the trial is **inert** (0 of 586 ticks would qualify);
- built as a launch-flag override in `worker_tick.py`, it **sets aside the 2026-08-12 rule** on
  every tick, with the Opus advisor as the only judgment cover.

Which of those is intended is canon intent, so it was raised to `for_the_director` with a
recommendation (see the commit that landed this file). Until he answers, nothing below is built.

**Answered (director, 2026-10-12):** "I set aside my 12 August reserved-marker rule for the worker
ticks only, for the trial's duration (at most seven days), using a dated launch flag, with the
pre-registered stop rule as the way back." Built as the launch-flag override:
`docs/observability/advisor_trial.yaml` (2026-10-12 to 2026-10-19; a wider window is refused in
code), read by `model_tier.advisor_trial()` and applied in `worker_tick.apply_advisor_trial()`.
**Sonnet 5, not 5.5:** Claude Code 2.1.282 has no `claude-sonnet-5-5`. Opus 5.5 as advisor to
Sonnet 5 was probed and attached.

## The stop rule (pre-registered 2026-10-12, before the first trial tick)

**Baseline:** the Opus-only worker ticks of the 7 days to 2026-10-12, read by
`python3 -m tools.tick_burn_rate --days 7` after its double-count fix (one usage per message id):
**207 turns, 74% landed, median $2.44 weighted, $568.93 total = $3.71 per landed turn.** Rework:
`tools/model_tier_report.py`'s `rework_rate` over the same 7 days, read at the first report.

**Prediction, written before the answer:** landed share 65-75%; $ per landed turn $1.50-2.50
(Sonnet's list is half Opus 5.5's on fresh tokens and equal on cache reads, which dominate; each
advisor call re-reads the conversation uncached at Opus rates, about $0.40 at a 100k context).

**Advisor attached** is a precondition, not a measure: until a worker-tick transcript shows an
`advisor_message` iteration, no trial turn counts. If the first 10 trial ticks show none, the trial
is off (`enabled: false`) and the cause is fixed before it reopens.

**STOP at once (`enabled: false`, then say so)** on any of:
1. after at least 40 trial ticks, landed share below **64%** (ten points under the baseline);
2. $ per landed turn at or above the baseline **$3.71** after 40 ticks (no saving to buy);
3. a trial landing reverted for a correctness defect, or a red at HEAD opened by a trial commit,
   at a rate above the baseline's `rework_rate`;
4. a trial turn crossing a wall (the reserved markers it no longer routes on are the reason to watch).

**Propose KEEP** (and extension to other units, which is his) if, at the window's end, landed share
is at least 70%, $ per landed turn is at most **60% of baseline ($2.23)**, and rework is no higher.
Anything between is reported as inconclusive with the numbers, and the trial lapses on 2026-10-19.

**Measured per turn:** the serving model and the advisor's calls and tokens, from each transcript
(`tick_burn_rate`: `model`, `advisor_calls`, `advisor_tokens`, the advisor priced at its own list);
the tier and the advisor named at dispatch in `model_tier_log.jsonl` (`tier: advisor_trial`).
What each call was about is read from a sample of transcripts at the report, not counted.

## Deliverables

1. **Pre-register the stop rule** before the first trial tick, in this file, against the five
   measures the steer names (landing share; allowance per landed change; landings later corrected
   or reverted, and findings found by accident; advisor calls and on what; advisor refusal or
   absence). Baseline = the Opus-only worker ticks in the same number of days immediately before.
2. **The launch change**, on the worker-tick unit only: `background/worker_tick.py`'s spawn argv
   (`[claude_bin, "-p", ..., "--model", model, prompt]`) takes the trial main model and the advisor
   flag, gated by a dated window in a committed file so it lapses by itself (the shape
   `model_tier_pilot.yaml`'s `ends:` already uses). Record per turn which model actually served
   it — `.claude/settings.json` fallbacks can swap mid-trial.
3. **First-tick proof the advisor attached**: the transcript's `Advising` line, before any result
   counts. A refused pairing or a set `DISABLE_TELEMETRY` drops the advisor without an error.
4. **Report** in the stretch log against the stop rule, and propose keep / extend / drop.
   Extending to the seat or the interactive window is his.

## Not this

The advisor sees the whole conversation; it is a second opinion, not the separate-agent check that
high-stakes work requires. Do not count it as one.
