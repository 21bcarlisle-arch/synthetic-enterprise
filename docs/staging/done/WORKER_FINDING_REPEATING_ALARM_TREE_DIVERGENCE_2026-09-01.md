**Severity:** LATENT · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# [TREE DIVERGENCE — 28.2x OVER] 272 source files diverge from HEAD (threshold 15); the oldest has sat 112.7h (threshold 4.0h): docs/staging/done/WORKER_FINDING_REPEATING_ALARM_CONSI

**Filed automatically by `background/alarm_repetition.py`, not by a person.** This alarm has
fired **3 times without its state changing**, over **0.8h**. Under the
director's instruction of 2026-08-20 a repeating alert escalates itself into the draw rather
than being sent again, so this document exists and a 3th page does not.

## The alarm, verbatim

```
[TREE DIVERGENCE — 28.2x OVER] 272 source files diverge from HEAD (threshold 15); the oldest has sat 112.7h (threshold 4.0h): docs/staging/done/WORKER_FINDING_REPEATING_ALARM_CONSISTENCY_GATE_FAILED_GIT_DASHBOARD_TOTALS_AND_EXEC_SUMMARY_INSIGHTS_2026-08-25.md. 18.1x the file line (272 vs 15) and 28.2x the age line (112.7h vs 4.0h). By lane: unattributed:docs (233 files, oldest 112.7h); unattributed:tests (19 files, oldest 69.27h); H_harness (8 files, oldest 38.39h). Report only — the publish gate's subject is HEAD, so this blocks nothing. Walk it by lane and land what is finished; a sweep that only makes the count fall is the same defect wearing a smaller number.
```

## What is known without diagnosing anything

- Signature: `tree_divergence` — the alarm text with elapsed times, counters, hashes and timestamps
  normalised away, so this is the same CONDITION recurring, not the same string.
- First seen in this episode: 2026-09-01T22:11:19+00:00
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
- **2026-09-02** — still live. 3 repeats over 1.0h without the state changing. No second document filed: this condition already has one.
- **2026-09-03** — still live. 8 repeats over 2.1h without the state changing. No second document filed: this condition already has one.
- **2026-09-04** — still live. 14 repeats over 12.9h without the state changing. No second document filed: this condition already has one.
- **2026-09-05** — still live. 17 repeats over 14.7h without the state changing. No second document filed: this condition already has one.
- **2026-09-06** — still live. 18 repeats over 13.2h without the state changing. No second document filed: this condition already has one.
- **2026-09-07** — still live. 3 repeats over 2.3h without the state changing. No second document filed: this condition already has one.
- **2026-09-08** — still live. 10 repeats over 7.1h without the state changing. No second document filed: this condition already has one.
- **2026-09-09** — still live. 3 repeats over 3.8h without the state changing. No second document filed: this condition already has one.
- **2026-09-10** — still live. 9 repeats over 9.2h without the state changing. No second document filed: this condition already has one.
- **2026-09-11** — still live. 5 repeats over 3.4h without the state changing. No second document filed: this condition already has one.
## Instances seen
- `# source files diverge from head (threshold #); the oldest has sat #h (threshold #h): docs/staging/done/worker_finding_r` (first seen 2026-09-01)
- `# source files diverge from head (threshold #); head is # commit(s) behind origin/main (and # ahead), so this count is m` (first seen 2026-09-02)
- `# source files diverge from head (threshold #); the oldest has sat #h (threshold #h): docs/staging/done/run_complete_#t#` (first seen 2026-09-03)
- `# source files diverge from head (threshold #); the oldest has sat #h (threshold #h): tools/test_generate_regulatory_dat` (first seen 2026-09-05)
