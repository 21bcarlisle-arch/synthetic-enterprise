**Severity:** LATENT · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# [LAUNCH UNLANDED] 1 file(s) a finished run wrote into this tree are in no commit: arms-rerun-20260910b [artefact]: UNTRACKED -- the job finished and wrote `docs/observability/value

**Filed automatically by `background/alarm_repetition.py`, not by a person.** This alarm has
fired **107 times without its state changing**, over **105.8h**. Under the
director's instruction of 2026-08-20 a repeating alert escalates itself into the draw rather
than being sent again, so this document exists and a 107th page does not.

## The alarm, verbatim

```
[LAUNCH UNLANDED] 1 file(s) a finished run wrote into this tree are in no commit: arms-rerun-20260910b [artefact]: UNTRACKED -- the job finished and wrote `docs/observability/value_cycle_ab_s1_noise_floor_20260910b.json` (its `artefact`), and that file is in no commit and not even staged. The register says this work is done; git says it does not exist. Land it, or say on the record why it is not landable The register says the work is done and git has never seen it. Land them, or record why they are not landable.
```

## What is known without diagnosing anything

- Signature: `deadman_launch_artefact_unlanded` — the alarm text with elapsed times, counters, hashes and timestamps
  normalised away, so this is the same CONDITION recurring, not the same string.
- First seen in this episode: 2026-09-10T21:37:32+00:00
- Repeats before escalation: 107 (threshold `ESCALATE_AFTER_REPEATS`)
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

## Instances seen
- `# file(s) a finished run wrote into this tree are in no commit: arms-rerun-# [artefact]: untracked -- the job finished a` (first seen 2026-09-15)

---

## RESOLVED 2026-09-15 — delivery seat, scheduled tick

The condition is cleared: `docs/observability/value_cycle_ab_s1_noise_floor_20260910b.json` is in
commit `f3d95cc46`, landed with `surgical_land --content` (receipt verified: tree `86bf5b935`,
3 paths, gate-rc 0) and byte-identical to what the finished run wrote.

**It was checked all three ways before landing, not one** — absent from `HEAD`, absent from the
index, and NOT `.gitignore`d. A file can fail "did it reach git" for any of the three and only the
third is silent.

**Why it was landable rather than a refusal to record.** Every other artefact in the dated
noise-floor series is tracked; this one alone was not. It is read by `site/data/delivery.json` and
named in `tests/background/conftest.py:454`, so an untracked copy is the shape where a control
passes on this disk and fails in every clean extract. `site/data/delivery.json` already carried the
remedy verbatim — `surgical_land --content` — which is the route used.

**What it is NOT.** It is a rival floor from a DIFFERENT seed family (seed `111111`, against
`11111` in both committed floors), already established by
`SEAT_FINDING_THE_RIVAL_FLOOR_IS_A_DIFFERENT_SEED_FAMILY_NOT_JUST_A_DIFFERENT_TREE_…_2026-09-10.md`.
Landing it preserves the evidence as a dated sibling. It is **not** promoted to `NOISE_FLOOR` and
nothing here should be read as promoting it.
