**Severity:** LATENT · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# [OPERATIONAL LAYER RED] The independent-cadence operational-layer signal (`pytest -m operational`, deselected from the content publish gate so it can never wedge the live site) has

**Filed automatically by `background/alarm_repetition.py`, not by a person.** This alarm has
fired **3 times without its state changing**, over **2.1h**. Under the
director's instruction of 2026-08-20 a repeating alert escalates itself into the draw rather
than being sent again, so this document exists and a 3th page does not.

## The alarm, verbatim

```
[OPERATIONAL LAYER RED] The independent-cadence operational-layer signal (`pytest -m operational`, deselected from the content publish gate so it can never wedge the live site) has been RED for 4 consecutive check(s) (rc=1). This does NOT affect the published site/report -- it is a daemon-lifecycle test regression. Failing tests:
FAILED tests/system/test_join_cut_mutation.py::test_every_chain_passes_uncut
FAILED tests/system/test_join_cut_mutation.py::test_work_loop_fires_when_the_draw_stops_returning_work
FAILED tests/system/test_join_cut_mutation.py::test_work_loop_fires_when_the_draw_re_offers_finished_work
FAILED tests/system/test_join_work_loop.py::test_the_work_loop_join_conducts
```

## What is known without diagnosing anything

- Signature: `operational_layer_signal` — the alarm text with elapsed times, counters, hashes and timestamps
  normalised away, so this is the same CONDITION recurring, not the same string.
- First seen in this episode: 2026-09-06T20:56:56+00:00
- Repeats before escalation: 3 (threshold `ESCALATE_AFTER_REPEATS`)
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
- **2026-09-07** — still live. 3 repeats over 2.2h without the state changing. No second document filed: this condition already has one.
## Instances seen
- `the independent-cadence operational-layer signal (`pytest -m operational`, deselected from the content publish gate so i` (first seen 2026-09-06)

## RESOLVED 2026-09-07 — condition cleared, archiving

Drawn as RUNG 1b at 5 consecutive reds. **Note the alarm text above names a spent episode**: the
four `test_join_cut_mutation` / `test_join_work_loop` failures it quotes were already green. The
live failure was one test —
`tests/background/test_supervisor.py::test_live_fork_ceiling_matches_its_dated_fence_and_expires_with_it`
— whose post-expiry leg had never been run and asserted a sentence the width-1 fast path has never
emitted. There was a SECOND defect underneath it, which no local run could see: the dial's restore
edited the working tree and was never committed, so HEAD carried `MAX_CONCURRENT_FORKS = 2` hours
after the window closed. The landing gate found it; the working-tree signal structurally could not.
Both are fixed here. Diagnosis, correction and poison round:
`SEAT_FINDING_THE_FENCED_DIAL_RESTORED_ITSELF_AND_ITS_GUARDS_POST_EXPIRY_LEG_HAD_NEVER_BEEN_RUN_2026-09-07.md`.

Signal re-run whole: **1240 passed, 1 xfailed, 0 failed.** Paging resumes automatically on the next
state change.
