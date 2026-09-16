**Severity:** LATENT · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# [ORIGIN FORK] NOT_ADVANCED: origin is 1 commit(s) ahead, this machine has NOTHING to land, and the shared tree will not fast-forward: error: The following untracked working tree fi

**Filed automatically by `background/alarm_repetition.py`, not by a person.** This alarm has
fired **3 times without its state changing**, over **0.2h**. Under the
director's instruction of 2026-08-20 a repeating alert escalates itself into the draw rather
than being sent again, so this document exists and a 3th page does not.

## The alarm, verbatim

```
[ORIGIN FORK] NOT_ADVANCED: origin is 1 commit(s) ahead, this machine has NOTHING to land, and the shared tree will not fast-forward: error: The following untracked working tree files would be overwritten by merge:
	docs/staging/SEAT_FINDING_A_SECOND_DRAW_RE_OFFERED_A_RECONCILIATION_ALREADY_LANDED_UNDER_A_DIFFERENT_CLAIM_ID_2026-09-. Nothing was committed and nothing was pushed -- a merge with no work of ours in it would only widen the fork it claims to close. The tree advances when the lane holding those files lands or reverts them. — origin is 1 commit(s) ahead and the fork could NOT be closed automatically, so landings and publishing stay blocked until someone reconciles.
```

## What is known without diagnosing anything

- Signature: `deadman_origin_fork` — the alarm text with elapsed times, counters, hashes and timestamps
  normalised away, so this is the same CONDITION recurring, not the same string.
- First seen in this episode: 2026-09-03T14:58:22+00:00
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
- **2026-09-04** — still live. 3 repeats over 0.1h without the state changing. No second document filed: this condition already has one.
- **2026-09-05** — still live. 3 repeats over 0.2h without the state changing. No second document filed: this condition already has one.
- **2026-09-06** — still live. 8 repeats over 1.0h without the state changing. No second document filed: this condition already has one.
- **2026-09-07** — still live. 3 repeats over 0.4h without the state changing. No second document filed: this condition already has one.
- **2026-09-08** — still live. 3 repeats over 0.5h without the state changing. No second document filed: this condition already has one.
- **2026-09-09** — still live. 3 repeats over 0.1h without the state changing. No second document filed: this condition already has one.
- **2026-09-10** — still live. 6 repeats over 1.2h without the state changing. No second document filed: this condition already has one.
- **2026-09-11** — still live. 24 repeats over 5.8h without the state changing. No second document filed: this condition already has one.
## Instances seen
- `not_advanced: origin is # commit(s) ahead, this machine has nothing to land, and the shared tree will not fast-forward: ` (first seen 2026-09-03)
- `not_advanced: origin is # commit(s) ahead, this machine has nothing to land, and the shared tree will not fast-forward. ` (first seen 2026-09-04)
- `refused_conflict: between # and # -- # conflicted path(s), nothing was committed: background/origin_reconcile.py tests/b` (first seen 2026-09-05)
- `refused_conflict: between # and # -- # conflicted path(s), nothing was committed: background/origin_reconcile.py docs/de` (first seen 2026-09-05)
- `refused_gate: on the resulting tree (rc=#). this is the tree the commit would create, not the working tree -- a working ` (first seen 2026-09-05)
- `not_advanced: the merge gated clean and was pushed, but the shared tree did not advance and is still # commit(s) behind.` (first seen 2026-09-05)
- `refused_conflict: between # and # -- # conflicted path(s), nothing was committed: site/data/delivery.json site/data/valu` (first seen 2026-09-08)
- `refused_conflict: between # and # -- # conflicted path(s), nothing was committed: site/capabilities/index.html site/data` (first seen 2026-09-09)
- `error: timeoutexpired: command '['/usr/bin/python#', '-m', 'tools.surgical_land', '--merge', 'origin/main', '-m', "merge` (first seen 2026-09-10)
- `refused_conflict: between # and # -- # conflicted path(s), nothing was committed: site/data/value_arms.json a conflict i` (first seen 2026-09-10)
- `refused_conflict: between # and # -- # conflicted path(s), nothing was committed: docs/staging/records/seat_preregistrat` (first seen 2026-09-11)
