**Severity:** LATENT · **Lane:** H_harness · **Epoch:** 3 · **Atom:** `unminted` (lane-0 `the-memory-weights-drift-both-ways`)

# The sim_run weight was checked in one direction, so an over-declared figure read clean

**2026-09-30.** `background/resource_headroom.weight_drift` set `drifted = peak > declared`. A
declared weight twice the observed peak therefore read `drifted=False`, and
`CLASS_WEIGHTS_MB["sim_run"] = 13824` has stood since 2026-08-24 against a job the record says now
peaks near 6.3 GB.

## Pre-registration (written BEFORE reading the journal)

- P1. `weight_drift("sim_run")` over the default `-24h` window, through the module's own reader,
  returns an observed peak in **[5,500, 7,500] MB**, i.e. roughly half the declared 13,824.
- P2. With a long job declaring 11,200 MB resident, `admit("sim_run")` on this box DEFERS at the
  current 13,824 weight AND still defers at a re-derived ~6.5 GB weight (budget ≈ total − 1,024;
  11,200 + 6,500 + whatever else is reserved vs ~22.9 GB is close — I expect it to be near the
  line, so this is the one that could refute me).

## Results

- **P1 held.** Through `oom_watch.read_unit_memory_peaks_mb` (weight_drift's own reader): `-24h`
  8 runs, max 6.2G = 6,349 MB; the whole retained journal (2026-09-19..09-30, 82 runs, `-14d`
  through `-60d` identical) max 6.9G = 7,066 MB on 09-27. The 6,317 MB quoted in the record was
  not used.
- **P2 WAS WRONG, and I could not have seen it by thinking harder.** I expected the re-derived
  weight to still defer beside an ab6 pass "near the line". It does not come near:
  11,200 + 7,066 = 18,266 against a 23,008 MB budget admits with 4.7 GB spare, and the measured
  leg admits too while the long job is still growing. The deferral held ONLY because 13,824 MB
  pushed any long job declared over 9,184 MB past the budget. Re-deriving the weight alone would
  have silently removed the protection the item asked to keep.

## What landed

1. `weight_drift` is two-directional. `direction` is `"under"` (peak > declared, no tolerance:
   fail-open) or `"over"` (declared − peak > `OVER_DECLARED_TOLERANCE_MB`), and the alarm names
   them differently (`OUTGROWN` / `OVER-RESERVED`). The tolerance is the budget's own
   `RESERVE_FOR_UNDECLARED_MB` (1,024) — no new number was picked.
2. `CLASS_WEIGHTS_MB["sim_run"] = 7066`, the retained-journal maximum, with its origin in the
   comment. Budgeted at the retained max rather than the 24h max because under is the fail-open
   side; 7,066 − 6,349 = 717 MB sits inside the tolerance, so live `weight_drift("sim_run")`
   reads **matched** (`drifted=False, direction=None`). At 13,824 it would read `over`.
3. The protection is now a stated rule, not an accident: `sim_runner.cycle_admission` defers a
   cycle whenever `admit()` reports a resident long job, even when the arithmetic fits, with a
   reason naming the unit and pids. The 19:07Z death needed a third, undeclared 5.2 GiB
   resident that no declared arithmetic sees; a cycle is the cheap thing to defer.

## Controls (each mutation run, each red)

| mutation | reds |
|---|---|
| drop the `over` leg | `test_drift_reads_in_both_directions[over…]` |
| tolerance 0 | matched leg, re-derived-constant control, matches-the-record control |
| drop the yield in `cycle_admission` | 19:07Z deferral test, yield test at weights 1,024 and 7,066 |
| restore 13,824 | `test_the_re_derived_constant_matches_the_record_it_was_derived_from` |

`test_denies_when_the_budget_is_exhausted…` was re-keyed to the weight (it pinned 13,824 via a
24,000/16,000 box that admits at 7,066) so it keeps proving budget-only refusal at any weight.

## For the next orientation

The `wrong` row "weight_drift checks one direction only … protection correct by accident of a
stale figure" (decisions.jsonl, 2026-09-30) can be marked `corrected: true` with this file as its
evidence. Residual, not fixed here: `subject_cost`, `publish_gate` and `census` still have no unit
and so no independent re-derivation — unchanged, and reported `UNVERIFIED` as before.
