# ACTIVITY-BASED COST + UTILISATION — see where the machine's resources actually go (P1, director-raised)

**Staged:** 2026-07-16 by advisor, **director-raised**. Disposition: QUEUE-high.
Register as an atom; the daemon builds it. Sibling to G5 (sizing = effort
remaining) and G6 (method lens) — this one = where effort WENT and how much was
wasted. Together they are the forecasting-and-efficiency instrument.

## The question this answers (the one that decides whether this works)
"Is the machine spending its resources on PRODUCT, or on ITSELF?" Right now that
is unanswerable — it's a feeling. This makes it a decomposition. The honest read
of the last week (to be measured, not assumed): the majority of elapsed time went
to SELF-MAINTENANCE (stalls, wedges, transport, daemon launch), not product. If
that ratio persists, the premise fails — and you cannot manage what you cannot
see.

## Two resources, tracked SEPARATELY (they diverge, and the divergence is signal)
- **Elapsed wall-clock time** — the utilisation denominator (where did the hours
  go?). A stall wastes time but few tokens.
- **Token budget** — the COST denominator (the real money/limit constraint). A
  thrashing build wastes both. Track both; they tell different stories.

## Activity taxonomy (the buckets — attribute every unit of both resources)
- **PRODUCTIVE / product** — building/finishing atoms that advance the company.
  The only bucket that is truly "value output."
- **PRODUCTIVE / discovery** — DISCOVER/FRAME passes. Real, but INVESTMENT not
  output — track separately or it flatters the numbers.
- **WASTE / self-repair** — fixing the harness, stalls, wedges, transport,
  daemon/plumbing. This week's dominant cost. Should FALL over time.
- **WASTE / idle** — flag-on-but-nothing-running, between-turns gaps, waiting.
- **WASTE / hit-limit** — blocked on token budget or rate limits.
- **WASTE / rework** — redoing work that failed its gate (the cycle-2 failures).
- **WASTE / idle-waiting-on-director** — productive time lost waiting on a human
  decision. If high, the DIRECTOR is the constraint (ToC) — worth knowing.

## The metrics that fall out (these answer "does this work" and "where's the waste")
- **Productive %** = product-build resource / total. THE headline. 15% = the
  machine mostly serves itself; 60% = it's working. Track for both time & tokens.
- **Cost-of-self-maintenance** — tokens+hours on WASTE/self-repair. Must trend
  DOWN as the harness matures; flat = the harness is a treadmill.
- **Rework rate** — % of turns that failed their gate and redid work.
- **Value-per-problem** — tokens+hours attributed to each problem/atom/epic
  ("800k on the transport bug" vs "120k on the affordability cluster"). Tells you
  where the money actually went and whether it went to things that matter.
- **Idle-waiting-on-director** — how much productive time waits on you.

## Build from data that ALREADY EXISTS (reporting layer, not new instrumentation)
- **git timestamps** — elapsed time per commit; gaps = idle/stall duration.
- **commit-message class** — "fix"/"[build]"/"DISCOVER"/"Register" already tag
  activity type; map them to the taxonomy.
- **daemon token metering** — the 20-turn/window budget already meters per-turn
  tokens; attribute to the turn's drawn atom(s).
- **deadman/health logs** — idle/stall/blocked durations and hit-limit events.
Nobody is AGGREGATING this; the raw data is all there.

## THE GUARDRAIL (non-negotiable — same law as sizing)
**Utilisation is a DIAGNOSTIC, never a TARGET.** The failure mode is optimising
for "100% busy" — which means the machine never stops to think or verify, and you
get fast confident garbage. The goal is not MAXIMUM utilisation; it is maximum
PRODUCTIVE utilisation THAT STAYS VERIFIED. 40% productive-and-correct beats 90%
busy-and-wrong. Never tune the machine to make these numbers look good — that
corrupts the actuals into lies (and breaks the forecasting that depends on them).

## Relationship to forecasting (why this + G5 sizing = the instrument)
- G5 sizing -> EFFORT REMAINING (what's left, in calibrated size-points).
- THIS -> velocity (productive size-points completed per day) + where effort is
  lost. Rolling 7-day productive velocity ÷ remaining sized effort = a real,
  self-updating forecast with error bars. Neither works alone: sizing without
  utilisation over-promises (assumes 100% productive); utilisation without sizing
  can't weight the remaining work.

## Surface it (Method door, live)
A single view: utilisation % (time & tokens), cost-by-activity, waste
breakdown, value-per-problem, rework rate, idle-on-director — updated each cycle.
That one view answers "is this working" better than any narrative, and it makes
"too slow" DIAGNOSABLE (too much self-repair? idle? rework? each has a different
fix) instead of a dead-end feeling.

## DoD
Activity taxonomy defined and mapped to commit-classes/log-events; both resources
(elapsed time + tokens) attributed per activity from existing git/token/deadman
data; the six metrics computed and surfaced on the Method door, updated per cycle;
value-per-problem attributable per atom/epic; the diagnostic-not-target guardrail
recorded in CLAUDE.md; wired to G5 so productive velocity + remaining sized effort
produce a live forecast. A check: the last 7 days' resource split renders, and the
self-repair-vs-product ratio is visible as a single number.
