**Severity:** LATENT · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# [DIRECTOR-RULING] Release the reading-token measurement from behind the exit test (2026-11-14)

**Type:** RULING, through the advisor channel. The director's words, from chat on Sat 14 Nov:

- 06:41 GMT: "Is there a way to spend fewer tokens and do less reading or compress and abstract. the information to reduce the token cost of reading irrelevant things?"
- 06:42 GMT, on the advisor's recommendation below: "Yes"

## What the advisor found (check it)

- Three steers on reading cost were staged on 7 and 9 Nov. All three sit under `held_behind_the_exit_test` in `docs/direction/priority_order.yaml`, so none has run:
  - `DIRECTOR_STEER_MEASURE_WHERE_READING_TOKENS_GO_BEFORE_SPLITTING_ANY_FILE_2026-11-07.md`
  - `DIRECTOR_STEER_ABSTRACTION_IS_ONE_RESEARCH_FAMILY_AND_A_CENSUS_OF_OUR_DESCRIPTIONS_2026-11-07.md`
  - `DIRECTOR_STEER_MEASURE_WHAT_COMMITTED_GENERATED_DATA_COSTS_US_2026-11-09.md`
- The correctness stretch's own `holds:` comment says "Correctness and harness work is never held here -- a blanket hold would starve the draw." The first steer is a measurement of harness cost and builds no feature.

## The ruling

1. **Release the first steer only:** `MEASURE_WHERE_READING_TOKENS_GO_BEFORE_SPLITTING_ANY_FILE`. Remove it from `held_behind_the_exit_test` and draw it as harness work, at the stretch's normal priority, measurement only. It splits no file, moves no rule out of CLAUDE.md and builds no index.
2. **The other two stay held** until the exit test or until this measurement names them. If the measurement shows generated data or missing module summaries are a top cost, say so and propose releasing the matching steer.
3. **The result must rank the candidate cuts by measured share**, so the next decision is aimed:
   - the always-loaded context (CLAUDE.md and the rules);
   - repeat reads of the same files within a session and across seats;
   - whole-file reads where an excerpt would do;
   - generated data swept into reads and searches;
   - search and census work done in an Opus context instead of a Haiku or Sonnet sub-agent.

   Use `tools/tick_burn_rate.py` and the transcripts it already reads; add to it rather than writing a new tool.
4. **State the uncertainty.** The plan's usage meter's weighting of cache reads against fresh input and output is not published. Report shares in tokens by class (fresh input, cache write, cache read, output), not as a percentage of the allowance. Do not estimate the allowance: that mechanism stays mothballed by his ruling ("better to hit the limit").

## Risk

Touches: `priority_order.yaml` (one list entry) and a read-only measurement over transcripts.
Blast radius: none to runs.
Probable failure mode: a measurement keyed to one heavy day. Cover a full week, every seat kind, and say which week.

Proportionality: doc-and-measurement only. Implement directly.

— Director ruling, 14 Nov 2026, his words above; the reading and drafting are the advisor's.

## Done

(worker tick, Sat 14 Nov.) Item 1: `DIRECTOR_STEER_MEASURE_WHERE_READING_TOKENS_GO_BEFORE_SPLITTING_ANY_FILE_2026-11-07.md`
is removed from `held_behind_the_exit_test` in `docs/direction/priority_order.yaml`, with this
ruling cited beside the list. Nothing in code reads that list, so the release is the edit itself.
The measurement is ranked as harness work in the 16 Nov balance proposal (§5 item 10, about 0.9
points). It is measurement only and extends `tools/tick_burn_rate.py`. Item 2: the generated-data
and abstraction steers stay held. Items 3 and 4 are the measurement's own done-criteria, and the
proposal restates them: rank the five cuts by measured share, report tokens by class, cover a
full week and every seat kind, and never estimate the allowance.
