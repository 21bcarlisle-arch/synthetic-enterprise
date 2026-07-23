> **[CC PROCESSING STATUS -- 2026-07-23, parked in in_progress/]**
> DONE this tick: **item 1** -- publish gate UNWEDGED. R9 cause (NOT the suspected R16 level-surface
> class): the commit-time level-surface gate's LEVEL_SENSITIVE_TESTS omitted
> `tests/design/test_maturity_map_facets.py`, so F1c's value_stream-hygiene violation
> (`close_to_learn` not on the reviewed allowlist, registered f27a06a39) passed at commit and only
> the full publish gate caught it. Instance fix: F1c reviewed onto REVIEWED_CLOSE_TO_LEARN. R10 class
> fix: facets test added to the commit-time level-surface gate so the whole class is now
> structurally uncommittable. Full publish gate GREEN (18672 passed). **item 2** -- axis-3 weather
> verdicts recorded in `docs/observability/director_axis_verdicts.jsonl`. **item 3(c)** -- weather
> steer consumed -> `docs/design/WEATHER_SIM_PURPOSE_FRAME.md`; W1_6/F2 lane implication surfaced as
> director findings F-i/F-ii/F-iii, not silently resolved.
>
> OPEN (blocking sub-items -> next tick/lane): **3(a)** F1c harness-gap BUILD leg (under the existing
> F1 waiver -- a separate BUILD atom). **3(b)** F1a/F1b L1/L2 level moves = the TWIN's ledger-backed
> call; no self-claim on any surface until the twin's entry exists (not mine). **3(d)** the R13
> ratification's stale-pin sweep result -- one line in today's daily note (needs the sweep result;
> not fabricated here). Unblocks when: the F1 BUILD lane draws F1c; the twin logs F1a/F1b level
> entries; the R13 stale-pin sweep runs.

---

# [DIRECTOR-RULING] — Unwedge the publish gate (R16 class); axis-3 weather verdicts RATIFIED; sequencing (2026-07-23)

**Type:** [DIRECTOR-RULING] via advisor bridge. Three parts.

## 1. Publish gate wedged — diagnose and unwedge FIRST (priority over all queued work)

Three consecutive publish-gate failures (alerts 08:24Z), no tick commits since F1a at 07:51Z. Diagnose the root cause with evidence (R9). If it is the R16 class again — a level-quality claim unbacked by the ledger (the fresh F1a/F1b "BUILT to L2 exit test" surfaces are the obvious suspects) — then: fix the instance, AND answer why the commit-time level-surface gate (built 2026-07-22 precisely for this class) did not catch it before publish. If the commit-time gate has a bypass path, that is the class fix (R10), not the unwedge. Report cause in one line before proceeding.

## 2. Axis-3 weather verdicts — RATIFIED as director scores (from the weather review, director's endorsement carried verbatim)

Record in the axes ledger for the twin's prediction loop:
- **Still-and-cold compound: MET** — winter D1 decile lift 2.875 inside the real CI [1.54, 3.38], mutation-proven. Caveat F2 recorded: one national wind series serves both demand and generation; part of the spike may be inherited from that collapse.
- **Seasonal normalisation skill: PARTIAL** — genuine winter skill (0.863 vs blind), worse-than-blind in summer (1.039, worst cell). The negative CWV wind-chill coefficient (−23.1) stands as correct physics (GB cold spells are anticyclonic/still), not a defect.
- **Persistence: PARTIAL** — real Dec-2022 worst-week depth reachable (1.75 vs 1.45) but only in 12–32% of seeded sims; no multi-week blocking regime exists.
- **Warming trend: ABSENT** — stationary climatology on fixed 1991–2020 normals; consequence named: systematic volume-forecast-high bias into hedge sizing (feeds VALUE_CHAIN as a finding).

## 3. Sequencing after the unwedge

(a) Complete **F1c** (harness-gap leg) — the triad's remaining scope under the existing waiver. (b) F1a/F1b level moves: **twin's call at L1/L2 per standing authorization, ledger-backed** — no self-claims on any surface until the twin's entry exists. (c) Consume the weather-purpose steer (fc461e105) — its W1_6 lane implication surfaces as a director finding per its own text, not silently resolved. (d) The R13 ratification's stale-pin sweep result: one line in today's note.

**Risk & proportionality:** unwedge = diagnosis + instance fix + possible R10 on the commit gate's bypass — evidence first, own commits. Verdict recording = ledger entries. Tag: **unwedge priority; verdicts narrow/reversible; F1c proceeds under existing waiver.**

— Advisor bridge, carrying the director's verdicts and priority, 2026-07-23.
