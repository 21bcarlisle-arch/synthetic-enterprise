# [DIRECTOR-STEER][ADVISOR-STAGED] Backlog: trial Sonnet 5.5 + Opus advisor on worker ticks (2026-10-11)

**Status:** BACKLOG. Not urgent. Do not start before the weekly allowance resets, and do not let it displace supplier work in the current priority order. Draw it when a stretch has room.

**Proportionality:** reversible / narrow. A launch-flag change on one unit, switched off by removing the flag. Just do it once drawn, and report the result.

## What the director wants

A measured trial of Claude Code's advisor tool (experimental): a cheaper main model doing routine turns, with a stronger model consulted at decision points. Docs: https://code.claude.com/docs/en/advisor

- **Trial unit:** the worker ticks only. They are bounded jobs (draw, do, land, exit), so they suit a cheaper main model with an advisor on call.
- **Pairing:** main model Sonnet 5.5, advisor Opus (an accepted pairing per the docs table: Sonnet 5.5 main accepts Opus 5 or later as advisor).
- **Unchanged:** the delivery seat orientation and the interactive window stay on Opus 5.5 with no advisor. Those are where the judgment calls live.

## Why

Most of this week's expensive mistakes were judgment slips at decision points: asking the director questions that published rules answer, choosing a design without grounding it in the knowledge page, stalling instead of repairing self-caused breakage, and treating memory before asking what runs were for. The advisor is meant for exactly those moments. Separately, routine worker turns may not need Opus throughout, and the weekly allowance is the binding constraint.

## How to judge it

Run for a few days against the current set-up (Opus 5.5, no advisor), on comparable work, and report in the stretch log:

1. share of worker turns that land work;
2. allowance used per landed change (the run-cost log and usage figures);
3. landings later corrected or reverted, and findings found by accident rather than by a control;
4. how often the advisor was called, and on what kind of decision;
5. any refusal or unavailability of the advisor (see risks).

Pre-register what result would make us keep it, extend it to other units, or drop it, before the first trial tick.

## Risks and mitigations

- **Touches:** the worker tick's launch command only (the `--advisor` flag and the main model for that unit). No change to canon, the seam, or any other unit.
- **Blast radius:** worker-tick output quality for the trial period.
- **Probable failure modes:**
  - Sonnet lands less or lands worse work, so the saving is lost to rework. *Mitigation:* the measures above, and a stop rule pre-registered before the trial.
  - Advisor calls re-read the full transcript uncached, so long turns could cost more than they save. *Mitigation:* worker ticks are short by design; report calls and cost per call.
  - The advisor silently doesn't attach. Per the docs it needs feature-flag fetching, and is off if a variable like `DISABLE_TELEMETRY` is set. A refused pairing is dropped without an error. *Mitigation:* confirm on the first tick that the advisor actually ran (the transcript shows an `Advising` line) before counting any results.
  - Fallback models in `.claude/settings.json` (Sonnet 5, Haiku) could swap in mid-trial and invalidate the comparison. *Mitigation:* record which model actually served each trial turn.
- **Not independent review:** the advisor sees the whole conversation, so it is a second opinion, not the separate-agent check required for high-stakes work. Don't count it as that.

## Done when

The trial has run, the results are in the stretch log against the pre-registered stop rule, and you've proposed keep, extend or drop. Extending it to the seat or the interactive window is the director's call.
