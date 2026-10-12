<!-- SUPERVISOR_DRAW: self-drawable -->

# [WORKER-MINTED] Trial Sonnet 5.5 + Opus advisor on the worker ticks (2026-10-12)

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
