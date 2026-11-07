**Severity:** LATENT · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# The shared tree's fork with origin has been open for 60 minutes (6 behind, 0 ahead) and the reconciler cannot close it alone. Newest refusal: NOT_ADVANCED -- [origin's reconciler @

<!-- counts:begin -->
**Filed automatically by `background/alarm_repetition.py`, not by a person.** This condition
has been **observed to hold on 13 separate day(s)**, between **2026-10-23** and **2026-11-07**,
and **1 member(s)** of the family `fork_open_streak` have fired. Both counts are DERIVED from
this document's own dated lines every time the alarm fires again, so they age with the document
rather than with its first firing.

This condition's observer calls `escalate()` directly rather than through `notify()`, so no
consecutive-firing count exists for it and `ESCALATE_AFTER_REPEATS` (= 3) was never applied.
That absence is stated rather than filled with a placeholder count.
<!-- counts:end -->

## The alarm, verbatim

```
The shared tree's fork with origin has been open for 60 minutes (6 behind, 0 ahead) and the reconciler cannot close it alone. Newest refusal: NOT_ADVANCED -- [origin's reconciler @5b838d596] origin is 6 commit(s) ahead, this machine has NOTHING to land, and the shared tree will not fast-forward. Refused by 15 path(s): docs/design/DOMAIN_INVARIANTS.yaml (modified here, and origin changes it too); docs/direction/priority_order.yaml (modified here, and origin changes it too); docs/staging/SEAT_FINDING_THE_B3CE2A4E73_BOOK_FAILS_THE_DOMAIN_INVARIANT_GATE_ON_SEVEN_ROWS_2026-11-04.md (modified here, and origin changes it too); docs/staging/SEAT_FINDING_THE_EIGHTH_COLD_READ_FINDS_METERED_ELECTRICITY_USE_BARELY_MOVES_FROM_ONE_YEAR_TO_THE_NEXT_2026-11-04.md (modified here, and origin changes it too); docs/staging/advisor/done/DIRECTOR_EVIDENCE_WHAT_HAPPENS_TO_UNPAID_DOMESTIC_ENERGY_DEBT_2026-11-07.md (modified here, and origin changes it too); docs/staging/advisor/done/DIRECTOR_EVIDENCE_WHAT_HOUSEHOLDS_DO_AFTER_A_PAIN_POINT_2026-11-07.md (modified here, and origin changes it too); docs/staging/advisor/done/DIRECTOR_STEER_ABSTRACTION_IS_ONE_RESEARCH_FAMILY_AND_A_CENSUS_OF_OUR_DESCRIPTIONS_2026-11-07.md (modified here, and origin changes it too); docs/staging/advisor/done/DIRECTOR_STEER_MEASURE_WHERE_READING_TOKENS_GO_BEFORE_SPLITTING_ANY_FILE_2026-11-07.md (modified here, and origin changes it too); docs/staging/advisor/done/DIRECTOR_STEER_OFFICIAL_PLUGINS_EARN_THEIR_PLACE_AGAINST_OUR_OWN_NUMBERS_2026-11-07.md (modified here, and origin changes it too); docs/status/SEAT_STRETCH_LOG.md (modified here, and origin changes it too); tests/tools/test_the_domain_invariant_runner_reads_only_the_raw_export_and_every_evaluator_can_fire.py (modified here, and origin changes it too); tools/domain_invariant_runner.py (modified here, and origin changes it too) -- and 3 further path(s) not listed here. THE STEP IS TO LAND OR REVERT THOSE PATHS, NOT TO RE-RUN THIS MODULE: it clears a blocking path only when the path's bytes ALREADY equal what origin brings, so a second run on this tree returns this same refusal. Specifically, the 12 MODIFIED path(s) are this tree's uncommitted work and clear by LANDING or reverting them here -- `python3 tools/isolate_hunks.py --survey <path>` lists the hunks and `python3 -m tools.surgical_land --content <path>=<isolated> <path>` lands your bytes without swapping the shared worktree; and the 3 UNTRACKED path(s) are orphan drafts of files ORIGIN ALREADY BRINGS, so landing one REPLACES origin's copy rather th. The door: resolve each named path in an isolated worktree with `python3 -m tools.surgical_land --merge origin/main --resolve <path>=<file-outside-the-repo>` after reading both sides, then push as `background/origin_reconcile` does. Every daemon runs from the shared tree, so until this closes they run code that origin has replaced.
```

## What is known without diagnosing anything

- Signature: `fork_open_streak` — the alarm text with elapsed times, counters, hashes and timestamps
  normalised away, so this is the same CONDITION recurring, not the same string.
- First seen in this episode: 2026-11-07T16:31:00+00:00
- Repeats before escalation: **not measured**. This condition's observer calls `escalate()` directly rather than through `notify()`, so there is no transition store to count a streak against and `ESCALATE_AFTER_REPEATS` (= 3) was never applied to it. What the document can establish about itself is counted at the top; this is a stated absence, not a zero.
- Paging for this signature is now SUPPRESSED. It resumes automatically the moment the
  underlying state changes — including when it clears.

## What this document is asking for

The repetition is the finding. Something is failing the same way on a loop and nothing is
converging on it, which is the shape the director named as "a symptom, not an event". Draw
this, diagnose the condition named above, and either fix it or record why the alarm is wrong.

Archive to `docs/staging/done/` when the condition is resolved. While this document is live
-- here or in `in_progress/` -- a continuing condition APPENDS a dated line below rather than
filing a second document (2026-08-24). A condition that returns AFTER this has been archived
files a fresh document, because that is a new episode and an R3 two-strike signal.

A REPEATING FAILURE IS ONE OF THE THREE TRIGGERS FOR THE END-TO-END CHECK (director,
2026-10-04): before fixing the instance, write the section below -- the loop may be the world,
the maths, the canon or the frame, not the code that is alarming.

## End-to-end check

_Template -- replace this paragraph with the check itself._ Read the canon (`docs/design/DIRECTOR_CANON*.md`, `docs/staging/DIRECTOR_CANON_*`, `docs/design/THE_MODEL_ON_A_PAGE.md`, `CLAUDE.md`), the logic, and the work and findings in question TOGETHER, as hypotheses under test, stated and unstated. For each surprise, list every explanation the evidence allows -- the world wrong, the maths wrong, the director wrong, it not being that simple, something none of us has thought of -- ranked by evidence, not convenience. Raise each resulting concern with `python3 -m background.director_concerns --raise --kind ... --what ... --proposal ...` and carry on; it never blocks the work.

- 

## Still live
- **2026-10-23** — still live. The condition was observed to hold on this date. Restored from `.alarm_repetition_state.json` when this document was re-derived; the observation is that date's, not today's.
- **2026-10-24** — still live. The condition was observed to hold on this date. Restored from `.alarm_repetition_state.json` when this document was re-derived; the observation is that date's, not today's.
- **2026-10-25** — still live. The condition was observed to hold on this date. Restored from `.alarm_repetition_state.json` when this document was re-derived; the observation is that date's, not today's.
- **2026-10-26** — still live. The condition was observed to hold on this date. Restored from `.alarm_repetition_state.json` when this document was re-derived; the observation is that date's, not today's.
- **2026-10-27** — still live. The condition was observed to hold on this date. Restored from `.alarm_repetition_state.json` when this document was re-derived; the observation is that date's, not today's.
- **2026-10-28** — still live. The condition was observed to hold on this date. Restored from `.alarm_repetition_state.json` when this document was re-derived; the observation is that date's, not today's.
- **2026-10-29** — still live. The condition was observed to hold on this date. Restored from `.alarm_repetition_state.json` when this document was re-derived; the observation is that date's, not today's.
- **2026-10-30** — still live. The condition was observed to hold on this date. Restored from `.alarm_repetition_state.json` when this document was re-derived; the observation is that date's, not today's.
- **2026-10-31** — still live. The condition was observed to hold on this date. Restored from `.alarm_repetition_state.json` when this document was re-derived; the observation is that date's, not today's.
- **2026-11-01** — still live. The condition was observed to hold on this date. Restored from `.alarm_repetition_state.json` when this document was re-derived; the observation is that date's, not today's.
- **2026-11-02** — still live. The condition was observed to hold on this date. Restored from `.alarm_repetition_state.json` when this document was re-derived; the observation is that date's, not today's.
- **2026-11-03** — still live. The condition was observed to hold on this date. Restored from `.alarm_repetition_state.json` when this document was re-derived; the observation is that date's, not today's.
## Instances seen
- `the shared tree's fork with origin has been open for # minutes (# behind, # ahead) and the reconciler cannot close it al` (first seen 2026-10-23)

## Re-asked
- **2026-11-07** — re-asked: **still_holds**. observed 2026-11-07, within the 3-day bar.

## Done (delivery seat, 2026-11-07 21:20 GMT): the fork closed at 21:00 UTC

- **Cleared.** reconcile-watch fast-forwarded the shared tree 20 commits, fa915ac0d7 to f248d5ffa, at 21:00 UTC
  (`FAST_FORWARDED [settled]`). The fork had been open since 16:31.
- **Every refusing path was superseded by origin.** The only real unlanded writing was three orientation entries in
  the stretch log, and they landed in f248d5ffa. The per-path disposition is in
  `docs/staging/done/SEAT_FINDING_TWO_HOUSEHOLD_PAGE_ROWS_ARE_STRANDED_UNCOMMITTED_ON_THE_SHARED_TREE_SINCE_THE_OUTAGE_2026-11-07.md`.
- **The detector worked: it filed this document at 17:31, 60 minutes into the streak.** The advisor asked for a
  "behind origin for more than N hours" check. That check exists, and it is this one. The 3.5 hours between this
  filing and the fix were not the detector's.
  - This file was written untracked onto the shared tree, the same tree whose pin it reports. The 18:22 orientation
    record does not mention it.
  - Whether the draw ranks an untracked filing on the shared tree is not established here. It is handed on as one
    question, and no second detector is built for it.
