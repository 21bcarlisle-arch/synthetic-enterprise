# BATTERY CONVERSION — turning purchased judgement into standing checks

**Atom:** `AO8_board_batteries_executable` (lane H_harness, director programme
`DIRECTOR_PROGRAMME_ARCHITECTED_OUT_2026-08-05.md`).
**Built:** 2026-08-08.

## Why this exists

Eight advisor scope briefs each end in a **disqualification battery** — a list of
things that, if true of our treatment, mean the treatment is incomplete. That is
external judgement, already bought, written from the domain by someone who
deliberately had not read our code.

Left as prose it cannot fail. It sits in `docs/staging/`, it reads as covered
because someone once read it, and the company can drift arbitrarily far from it
without anything going red. The director's own justification for this atom is
the whole point: *external judgement already paid for stops sitting inert.*

## What it is

Three pieces, deliberately separate:

| Piece | File | Job |
|---|---|---|
| The oracle | `tests/domain/battery_register.py::parse_battery_lines` | Reads each battery **out of the brief itself** |
| The register | `tests/domain/battery_register.yaml` | Our disposition of every line (generated) |
| The control | `tests/domain/test_battery_register_integrity.py` | Puts the two against each other |

Plus `tests/domain/test_battery_checks.py`, which holds the lines that are
actually mechanised, and `tools/build_battery_register.py`, which regenerates the
register from the briefs.

**The separation is the design.** The oracle derives from the source documents;
the register is a different file. If both were derived from the same place their
agreement would prove nothing — the TAUTOLOGY pattern R15 names. Because the
brief is the authority, a battery line cannot be quietly dropped, reworded, or
marked done.

### Dispositions

Every line carries exactly one, and each has a rule that can fail:

- **`mechanised`** — a standing check runs with the suite. The register names it
  `module::function`, and integrity **resolves it by import**. A check that was
  renamed or deleted fails the suite instead of continuing to read as covered.
- **`not_mechanisable`** — the line is a judgement no assertion can carry.
  Requires a reason. Two lines qualify, and both are argued in the register.
- **`pending_capability`** — testable in principle; the capability it would test
  does not exist. Requires a reason **naming the blocker**. This is a REPORTED
  GAP, not a pass.

There is deliberately **no `skip` disposition**, and integrity forbids
`pytest.skip`/`skipif`/`xfail` anywhere in the battery checks. This is the
failure shape the atom's own origin note names: *a battery line converted into a
check that silently skips when its data is absent is worse than leaving it as
prose, because it reads as covered.* Absent data must make a check FAIL.

## Status

<!-- BEGIN GENERATED STATUS -- regenerate with tools/build_battery_register.py -->
| Brief | Lines | Mechanised | Pending capability | Not mechanisable |
|---|---:|---:|---:|---:|
| CARB | 12 | 0 | 11 | 1 |
| CFD | 9 | 0 | 8 | 1 |
| COT | 7 | 0 | 7 | 0 |
| ELEC | 12 | 1 | 11 | 0 |
| GAS | 12 | 1 | 11 | 0 |
| IND | 10 | 0 | 10 | 0 |
| NCS | 7 | 1 | 6 | 0 |
| PPM | 7 | 0 | 7 | 0 |
| **All** | **76** | **3** | **71** | **2** |

**3 of 76 battery lines run with the suite.** 71 name a blocker; 2 are judgements no assertion can carry.
<!-- END GENERATED STATUS -->

## The delta, reported not hidden

**73 of 76 lines are not yet mechanised, and that is the honest headline.** The
mechanism is complete; the coverage is a beginning. Reporting it this way is the
deliverable — the register turns 76 pieces of prose into 76 addressable, drawable
items with named blockers, where before there were eight documents nobody could
act on incrementally.

Three findings worth carrying forward:

1. **`ELEC-2` is the highest-leverage single gap.** The tree has settlement and
   forward series but no distinct day-ahead or within-day series. That one
   absence blocks `ELEC-2`, `ELEC-11` and `CFD-1` outright, and weakens `ELEC-9`.
   One capability closes four battery lines.

2. **The merit-order reconstruction is nearly load-bearing but not yet asserted.**
   `sim/merit_order_reconstruction.py` (W1_6b) is the mechanism that would make
   `ELEC-3`, `ELEC-8`, `ELEC-12` and `GAS-1` checkable — *raising wind must change
   which unit is marginal, not subtract from price*. These four are marked
   pending because the assertion is unwritten, not because the capability is
   missing. This is the cheapest next atom in the register.

3. **Two lines were marked pending specifically to avoid double-counting an
   existing control as new coverage** (`IND-2`, the Point-in-Time Blindfold, and
   `IND-7`/`IND-9`, which are really assertions belonging to `NCS-B1`/`NCS-B2`).
   Claiming them would have inflated the mechanised count with work already done
   elsewhere. The count is meant to measure this conversion, not re-bank the past.

### What the three mechanised lines found

- **`GAS-8`** (therm conversion) — the tree spells the constant **five** ways
  across five modules: `29.3071`, `29.307`, `29.31`, `29.3`, `0.02931`. All agree
  to within 0.03%, so nothing is materially wrong today; nothing stopped the
  sixth from being wrong. Now pinned to the published 29.3071 kWh/therm.
- **`NCS-B3`** (fuel purity) — currently clean. `simulation/gas_settlement.py`
  reaches only gas levies; `simulation/hedged_settlement.py` only electricity
  ones. Checked structurally at the assembler rather than on a sampled bill,
  because a sampled bill only proves the sample.
- **`ELEC-4`** (negative prices) — the generator does reach negative prices, but
  the first version of this check was worthless and the mutation pass caught it.
  It asserted "some price is below zero" and **passed with the generator's
  negative-price overlay disabled**, because `lower_mode_mean=50, std=18` throws
  the occasional sub-zero draw unaided. Rewritten as a **differential** with a
  control arm (`negative_days_per_year=0`) and a depth threshold, and the control
  arm asserts its own premise so the test says so if the ordinary distribution
  ever widens far enough to reach that depth by chance.

  This is the atom's own lesson in miniature: three of the five mutations
  confirmed a working guard, and the fourth revealed that a green test was
  measuring nothing. A battery line converted into a check nobody has watched
  fail is not converted.

## Known limits of this control

Stated rather than discovered later:

- **Coverage is measured per *registered* brief.** A brief added to the tree but
  never registered would be invisible, so `test_every_brief_is_registered`
  discovers briefs from the filesystem instead — but only under the four roots in
  `BRIEF_SEARCH_ROOTS`. A brief filed elsewhere is still invisible.
- **The commit gate does not fire on brief edits.** `docs/` is not in
  `CODE_PREFIXES` in `tools/pre_commit_test_gate.py`, so editing a brief's battery
  will not run this control at commit time. The integrity test is in
  `CONTROL_TESTS`, so it runs on any *code* change, and the full suite catches it
  per integration. Widening `CODE_PREFIXES` to all of `docs/` would slow every
  commit for one control; the gap is accepted and recorded here rather than
  papered over.
- **`GAS-8`'s scan is line-based**, so a conversion split across two lines is not
  seen. It also skips `sim/gas_prices_history.py`'s `0.29307` (a combined
  pence-and-unit conversion that does not normalise cleanly). Bounded on purpose:
  the first version of the guard matched `therm` inside `thermal_lag_hours` and
  fired on a daylight calculation, and a guard that cries wolf gets deleted.

## How to extend it

1. Build the capability a `pending_capability` line names.
2. Write the check in `tests/domain/test_battery_checks.py`.
3. Change the disposition in `tools/build_battery_register.py` to `mechanised`
   with `module::function`, and re-run it.
4. Integrity will refuse the claim if the check does not resolve.

Never hand-edit `battery_register.yaml`: the `text` fields are parsed from the
briefs so the register cannot drift from the purchased judgement.
