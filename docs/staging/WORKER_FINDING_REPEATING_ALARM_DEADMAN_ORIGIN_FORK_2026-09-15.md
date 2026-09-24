**Severity:** LATENT · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# [ORIGIN FORK] REFUSED_CONFLICT: between e097212cd and 33b78a519 -- 6 conflicted path(s), nothing was committed:

**Filed automatically by `background/alarm_repetition.py`, not by a person.** This alarm has
fired **46 times without its state changing**, over **101.9h**. Under the
director's instruction of 2026-08-20 a repeating alert escalates itself into the draw rather
than being sent again, so this document exists and a 46th page does not.

## The alarm, verbatim

```
[ORIGIN FORK] REFUSED_CONFLICT: between e097212cd and 33b78a519 -- 6 conflicted path(s), nothing was committed:
  docs/staging/records/SEAT_PREREGISTRATION_WHAT_CHOOSING_THE_SETTLED_SAMPLE_FOR_DIFFERENCE_MOVES_2026-09-11.md
  docs/staging/reference/CLASS_UNCOMMITTED_AND_ORPHANED_WORK_2026-08-12.md
  simulation/net_new_acquisition.py
  site/data/value_arms.json
  tests/tools/test_generate_value_arms_data.py
  tools/pre_commit_tes — origin is 35 commit(s) ahead and the fork could NOT be closed automatically, so landings and publishing stay blocked until someone reconciles.
```

## What is known without diagnosing anything

- Signature: `deadman_origin_fork` — the alarm text with elapsed times, counters, hashes and timestamps
  normalised away, so this is the same CONDITION recurring, not the same string.
- First seen in this episode: 2026-09-11T01:30:18+00:00
- Repeats before escalation: 46 (threshold `ESCALATE_AFTER_REPEATS`)
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

- **2026-09-15, delivery seat, scheduled tick.** Drawn and converged on, not cleared. All **six**
  conflicted paths now have a named resolution and the merge is mechanically complete (no markers,
  parses, 246 top-level defs with zero duplicates, both sides' work preserved). The fork is **not**
  blocked on knowing how to merge it. It is blocked on ONE control, for one named reason: the
  merged page's headline publishes verbatim a sentence the same feed's `withdrawn_claim` block
  records as withdrawn on 2026-08-29. Attributed in clean extracts (clean HEAD green, clean origin
  green, merged 2 red) with the regeneration confound separated out. One of 09-11's three reds is
  genuinely fixed by `9c2234e2c`, so this is converging: 3 red → 2 red. Full diagnosis, the six
  resolutions and the ordered remedy:
  `SEAT_FINDING_THE_MERGE_OPENS_THE_SIGN_GATE_AND_THE_HEADLINE_COMPOSER_REPUBLISHES_A_WITHDRAWN_SENTENCE_2026-09-15.md`.
- **2026-09-16** — still live. 3 repeats over 0.3h without the state changing. No second document filed: this condition already has one.
- **2026-09-17** — still live. 3 repeats over 0.2h without the state changing. No second document filed: this condition already has one.
- **2026-09-18** — still live. 5 repeats over 2.2h without the state changing. No second document filed: this condition already has one.
- **2026-09-19** — still live. 3 repeats over 0.2h without the state changing. No second document filed: this condition already has one.
- **2026-09-20** — still live. 16 repeats over 2.0h without the state changing. No second document filed: this condition already has one.
- **2026-09-21** — still live. 169 repeats over 30.7h without the state changing. No second document filed: this condition already has one.
- **2026-09-22** — still live. 7 repeats over 2.2h without the state changing. No second document filed: this condition already has one.
- **2026-09-23** — still live. 3 repeats over 1.5h without the state changing. No second document filed: this condition already has one.
- **2026-09-24** — still live. 6 repeats over 1.0h without the state changing. No second document filed: this condition already has one.
## Instances seen
- `refused_conflict: between # and # -- # conflicted path(s), nothing was committed: docs/staging/records/seat_preregistrat` (first seen 2026-09-15)
- `not_advanced: the merge gated clean and was pushed, but the shared tree did not advance and is still # commit(s) behind.` (first seen 2026-09-15)
- `not_advanced: origin is # commit(s) ahead, this machine has nothing to land, and the shared tree will not fast-forward. ` (first seen 2026-09-15)
- `refused_conflict: between # and # -- # conflicted path(s), nothing was committed: tests/background/test_the_liveness_sur` (first seen 2026-09-17)
- `refused_conflict: between # and # -- # conflicted path(s), nothing was committed: docs/design/orphan_baseline.json tests` (first seen 2026-09-17)
- `error: could not build an isolated worktree: another writer holds /var/tmp/se-origin-reconcile (owner marker live, or th` (first seen 2026-09-17)
- `refused_gate: on the resulting tree (rc=#). this is the tree the commit would create, not the working tree -- a working ` (first seen 2026-09-18)
- `refused_conflict: between # and # -- # conflicted path(s), nothing was committed: docs/staging/records/prereg_the_publis` (first seen 2026-09-18)
- `refused_conflict: between # and # -- # conflicted path(s), nothing was committed: tests/background/test_a_window_that_cl` (first seen 2026-09-18)
- `refused_conflict: between # and # -- # conflicted path(s), nothing was committed: docs/staging/records/seat_result_a_car` (first seen 2026-09-24)

## Re-asked
- **2026-09-24** — re-asked: **still_holds**. observed 2026-09-24, within the 3-day bar.
