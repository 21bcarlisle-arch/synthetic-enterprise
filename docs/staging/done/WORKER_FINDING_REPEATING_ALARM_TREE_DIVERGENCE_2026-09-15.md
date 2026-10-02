**Severity:** LATENT · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# [TREE DIVERGENCE — 105.9x OVER] 748 source files diverge from HEAD (threshold 15); HEAD is 35 commit(s) behind origin/main (and 40 ahead), so this count is measured against a stale

<!-- counts:begin -->
**Filed automatically by `background/alarm_repetition.py`, not by a person.** This condition
has been **observed to hold on 14 separate day(s)**, between **2026-09-15** and **2026-09-28**,
and **4 member(s)** of the family `tree_divergence` have fired. Both counts are DERIVED from
this document's own dated lines every time the alarm fires again, so they age with the document
rather than with its first firing.

Separately, the observer that last filed reported **16 consecutive firing(s) without a state
change**, over **36.7h**. That is `notify()`'s streak counter, which resets; it is not a total
and does not combine with the two counts above.
<!-- counts:end -->

## The alarm, verbatim

```
[TREE DIVERGENCE — 105.9x OVER] 748 source files diverge from HEAD (threshold 15); HEAD is 35 commit(s) behind origin/main (and 40 ahead), so this count is measured against a stale base: 4 of the 748 are byte-identical to the trunk and are not uncommitted work; the oldest has sat 423.51h (threshold 4.0h): docs/staging/done/run_complete_20260828T071155Z.md; 6 of the 748 diverging file(s) hold an OLDER COMMITTED VERSION and are armed to silently revert HEAD on the next pathspec commit that includes them -- restore to HEAD, do not land: docs/design/orphan_baseline.json (would revert to 8dd060194 selecting a control by what it scans is the always-run list spelled differently,), docs/design/simplifications/A49_the_ceiling_comes_before_the_programme_on_r3_and_r4.yaml (would revert to 992a037fc the map pair sat seven bytes under its ceiling, and the prose that filled it bel), docs/institutional/knowledge_map.md (would revert to 8369a541e the shift response is established as a function, and the constraint turns out to). 49.9x the file line (748 vs 15) and 105.9x the age line (423.51h vs 4.0h). By lane: unattributed:docs (668 files, oldest 423.51h); unattributed:tests (32 files, oldest 390.02h); unattributed:tools (18 files, oldest 359.14h). Report only — the publish gate's subject is HEAD, so this blocks nothing. Walk it by lane and land what is finished; a sweep that only makes the count fall is the same defect wearing a smaller number.
```

## What is known without diagnosing anything

- Signature: `tree_divergence` — the alarm text with elapsed times, counters, hashes and timestamps
  normalised away, so this is the same CONDITION recurring, not the same string.
- First seen in this episode: 2026-09-10T20:54:30+00:00
- Repeats before escalation: 12 (threshold `ESCALATE_AFTER_REPEATS`)
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

## Still live
- **2026-09-16** — still live. 5 repeats over 7.8h without the state changing. No second document filed: this condition already has one.
- **2026-09-17** — still live. 7 repeats over 4.7h without the state changing. No second document filed: this condition already has one.
- **2026-09-18** — still live. 16 repeats over 12.2h without the state changing. No second document filed: this condition already has one.
- **2026-09-19** — still live. 10 repeats over 5.8h without the state changing. No second document filed: this condition already has one.
- **2026-09-20** — still live. 3 repeats over 4.5h without the state changing. No second document filed: this condition already has one.
- **2026-09-21** — still live. 12 repeats over 36.1h without the state changing. No second document filed: this condition already has one.
- **2026-09-22** — still live. 3 repeats over 4.3h without the state changing. No second document filed: this condition already has one.
- **2026-09-23** — still live. 11 repeats over 7.8h without the state changing. No second document filed: this condition already has one.
- **2026-09-24** — still live. 4 repeats over 6.8h without the state changing. No second document filed: this condition already has one.
## Instances seen
- `# source files diverge from head (threshold #); head is # commit(s) behind origin/main (and # ahead), so this count is m` (first seen 2026-09-15)
- `# source files diverge from head (threshold #); the oldest has sat #h (threshold #h): docs/staging/done/run_complete_#t#` (first seen 2026-09-15)
- `# source files diverge from head (threshold #); the oldest has sat #h (threshold #h): tests/tools/test_settlement_ceilin` (first seen 2026-09-16)
- `# source files diverge from head (threshold #); the oldest has sat #h (threshold #h): tests/background/test_health_check` (first seen 2026-09-17)

## Re-asked
- **2026-09-24** — re-asked: **still_holds**. observed 2026-09-24, within the 3-day bar.
- **2026-09-25** — re-asked: **still_holds**. observed 2026-09-24, within the 3-day bar.
- **2026-09-26** — re-asked: **still_holds**. observed 2026-09-25, within the 3-day bar.
- **2026-09-27** — re-asked: **still_holds**. observed 2026-09-26, within the 3-day bar.
- **2026-09-28** — re-asked: **still_holds**. observed 2026-09-27, within the 3-day bar.
- **2026-09-29** — re-asked: **still_holds**. observed 2026-09-28, within the 3-day bar.
- **2026-09-30** — re-asked: **still_holds**. observed 2026-09-28, within the 3-day bar.
- **2026-10-01** — re-asked: **still_holds**. document last annotated 2026-09-28, but `tree_divergence` fired 68.1h ago in the notify transition store, which contradicts the silence.
- **2026-10-01** — re-asked: **cleared**. no observation since 2026-09-28, past the 3-day bar; `tree_divergence` last fired 72.0h ago; and the machinery observed other conditions on 2026-10-01, so the silence is the observers running and not seeing it.

## Re-asked and cleared, 2026-10-01

Archived by `background/alarm_repetition.reask()`, not by a person, and not because anybody diagnosed it.

- **What was asked:** has the condition behind `tree_divergence` been observed to hold since it was last annotated?
- **Last observation:** 2026-09-28
- **The answer, and what carried it:** no observation since 2026-09-28, past the 3-day bar; `tree_divergence` last fired 72.0h ago; and the machinery observed other conditions on 2026-10-01, so the silence is the observers running and not seeing it.
- **What this does NOT claim:** that the condition was fixed, or why it stopped. Only that nothing has observed it for 3 days while the observers were demonstrably running. If it returns it files a FRESH document — `escalate()` does not search `done/` — and that fresh document is an R3 two-strike signal worth more than this one was.

