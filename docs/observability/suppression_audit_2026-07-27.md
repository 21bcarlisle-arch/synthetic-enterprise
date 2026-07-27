# R10 Suppression Sweep — 14-day audit by failure direction (2026-07-27)

**Authority:** `docs/staging/in_progress/DIRECTOR_RULING_FAILURE_BIAS_LAWS_2026-07-27.md`
**Mint:** `PLANNER_MINTED_failure_bias_r10_suppression_sweep_2026-07-27.md`
**Machine-readable register:** `docs/observability/suppression_register.json`
**Standing gate (mutation-proven):** `background/suppression_register.py::validate_suppression_register` — R15 both-ways in `tests/background/test_suppression_register.py` (6 passed).

## What this is

The director's diagnosis: five independent defences failed in the same direction (toward
silence) because every one had been added to suppress a *false positive*. A week of optimising
against noise made quiet the failure mode. This sweep enumerates **every gate / throttle /
suppression / fold introduced in the trailing 14 days** (`git log --since=2026-07-13 -- background/**`),
classifies each by **failure direction**, and assigns a remediation to every silence-biased one:
**LAW A** (time-bound + re-arm), **LAW B** (per-cluster lane isolation), or **LAW C** (independent
counterpart). This is the R10 *class fix* — the three law-mints are the per-instance mechanisms.

## The table

| # | Mechanism | Commit | Fails toward | Remediation | Status |
|---|-----------|--------|:------------:|:-----------:|:------:|
| 1 | Pending-batch mint gate (rest-with-proof over all-blocked batch) | `1a46bd447` / `b55981046` | **silent** | LAW A + LAW B | landed_partial |
| 2 | Deadman proven-rest fold (suppress [STALL] on self-declared rest) | pre-window; `b55981046` | **silent** | LAW A + LAW C | **landed** |
| 3 | Drained-and-gated quiet wait (stop HARDEN treadmill while blocked) | `f9b57a209` | **silent** | LAW A | open |
| 4 | HARDEN cooldown / rotation (`.harden_cooldown.json`) | `7582b9ed1` | silent | — | **compliant** (re-arms 6h+sha) |
| 5 | BUILD planner REST-WITH-PROOF marker | `14ea5514a` | **silent** | LAW A | **landed** (2h age-cap) |
| 6 | Authorized-set enumeration (tick self-publishes 'set empty') | `eaffdb81e` | **silent** | LAW C | open |
| 7 | Daily self-note R17 **status** line | daily_self_note.py | **silent** | LAW C | open |
| 8 | Self-verifying push throttle (release unless origin verified) | `de8e5fa2d` | noisy | — | **compliant** (model example) |
| 9 | Publish-gate surgical scope partition | `6667672ae`/`d1458f8dc`/`2ddf71272` | silent | LAW C | **compliant** (H23 indep. signal) |
| 10 | External-blocked atom exclusion (draw skips `blocked_on`) | `6effd0343`/`15414e6c4` | **silent** | LAW B | open_partial |
| 11 | BUILD-IN-PROGRESS guard (don't re-offer a live fork's atom) | `aee1e9853` | noisy | — | **compliant** (fail-open→work) |
| 12 | Frame-saturation draw guard | `d2f1b420a`/`af8863f47` | silent | LAW C | **compliant** (self-staleness re-exec) |

## Verdicts

**Already remediated (do NOT re-file — prevents the re-work the EIGHTH-CLASS memory ledger warns of):**
rows 2, 4, 5, 8, 9, 11, 12. The deadman's un-suppressible OPEN-MINT `[ACT]` + 6h `HARD_REST_CAP`
(row 2) and the 2h rest-proof age cap (rows 1, 5) are the EIGHTH-CLASS fix, live and R15-proven.

**Still open — assigned to the three law-mints (drawable now):**
- **LAW A** → row 3 (drained-and-gated quiet wait needs its own explicit re-arm; today it is
  only bounded indirectly by the deadman 6h cap and the always-drawable R17 lane).
- **LAW B** → rows 1 (pending-batch gate is still *global*, not per-cluster) and 10 (external-blocked
  exclusion must not leak across sibling lanes).
- **LAW C** → rows 6 (enumeration) and 7 (daily note reports **status**, not **effect**). These are
  the failure-#3 / failure-#5 pair: the watchdog and the note must derive from primary state.

## The standing consequence — mechanised

Every registered suppression now carries a non-empty **`what_still_pages`** field: the independent
check that fires if the underlying condition is real. `validate_suppression_register` fails-closed on
any registered suppression that names no pager, or that is silence-biased with no remediation and no
`compliant` proof. **Scope honesty (R9):** the gate enforces the *declaration* on every *registered*
suppression; forcing a newly-written suppression to be registered remains a convention backed by this
ruling. The mechanised, mutation-tested half is the declaration requirement.

— R10 sweep, RUNG-7 refill worker tick, 2026-07-27.
