**Severity:** LATENT · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0 delivery
· **Class:** controls_that_cannot_fail

# RESULT: five contracts came back DIED, and the kill was one fixture erroring

**Measured 2026-09-06 BST, shared tree at `6965b1ee4`. Claim
`fuel-mix-M3-to-M10-are-proved-by-nothing`. Instrument
`python3 -m tools.grid_intensity_feed_contract_battery --only M3 M4 M7 M9 M10 --suites
explore_carbon` at spec fingerprint `d892342119e8`. Prereg
`docs/staging/records/SEAT_PREREG_WHAT_THE_FIVE_REMAINING_FUEL_MIX_ROWS_DO_AGAINST_THE_SUITE_THAT_NOW_PUBLISHES_2026-09-06.md`.
BEFORE run `/var/tmp/grid_intensity_fuel_mix_M3_M4_M7_M9_M10_BEFORE_controls_d892342119e8.json`;
AFTER run `…_AFTER_controls_d892342119e8.json`. Subject restored after both.**

## The finding

The drawn item's own work — controls for M5, M6 and M8 — landed at `6965b1ee4`. This lane went on
to the five contracts the same claim still names, and ran them first rather than writing anything,
because the M5/M6/M8 controls had added a module-scoped fixture that publishes off the real caches
and **that fixture was a new execution path through the subject that did not exist when the landed
grid was measured**.

**All five came back DIED. All five named the same node.**

```
M3  DIED (14.4s) [...::test_the_THERMAL_FLOOR_the_MIX_MEASURES_reaches_the_published_feed...]
M4  DIED (27.5s) [...::test_the_THERMAL_FLOOR_the_MIX_MEASURES_reaches_the_published_feed...]
M7  DIED (24.2s) [...::test_the_THERMAL_FLOOR_the_MIX_MEASURES_reaches_the_published_feed...]
M9  DIED (16.1s) [...::test_the_THERMAL_FLOOR_the_MIX_MEASURES_reaches_the_published_feed...]
M10 DIED (15.7s) [...::test_the_THERMAL_FLOOR_the_MIX_MEASURES_reaches_the_published_feed...]
```

Read as a log, that is five of the eight killed-by-nothing contracts closed in one run by work
already landed. **It is nothing of the kind.** Re-running each mutation by hand without `-x`:

| row | what actually happened | mechanism |
|---|---|---|
| M3 | `ERROR at setup` × 3 | `AttributeError: 'list' object has no attribute 'items'` |
| M4 | `ERROR at setup` × 3 | `TypeError: float() argument must be … not 'tuple'` |
| M7 | `ERROR at setup` × 3 | `KeyError: 'usable_fraction'` — in `build()`, not in the subject |
| M9 | `ERROR at setup` × 3 | `FuelOutturnUnavailable: no half hour carried a reading for every thermal fuel type` |
| M10 | `ERROR at setup` × 3 | `AttributeError: 'list' object has no attribute 'items'` |

**Not one control body executed a line.** Each mutation made the shared `real_publish` fixture
raise; a module-scoped fixture that errors errors every test in the module; and `-x` prints the
first red only, so one fixture failure was reported five times as five different contracts being
proved. The three tests it reddens were written for M5, M6 and M8 and assert nothing about any of
these five.

> **One shared fixture can score every contract in a spec, and `died` cannot see it.** `died` is
> `returncode != 0`, which is correct — an ERROR is a red and it is a kill. What it could not say
> is whether a CONTROL fired. The discriminator was available and unread: the landed M5/M6/M8 run
> had each row naming a **different** node; here five rows name one.

## The prediction, and where it was wrong

Filed before the run: *four die, one (M7) survives.* **M7 did not survive.** The prereg reasoned
about `fuel_mix()` alone and missed that `build()` indexes the coverage dict **by name** —
`zero_carbon_must_run_coverage["usable_fraction"]` — so substituting the import coverage raises a
`KeyError` one layer downstream. The mechanism predictions for M3, M4, M9 and M10 were right,
including that M3 and M10 would be wrong-type crashes.

The prereg's decision rule is what this run is being spent under, and it held: a row dying on a
wrong-class exception is not closed.

## What was built

**1. The engine can now say which kind of kill it measured** — `tools/contract_battery.py`.
`_run_suite` records `errored` (pytest's `ERROR` nodes) beside the existing `failed` (which unions
`FAILED` and `ERROR` deliberately, and must keep doing so — both are reds and both must be
deselected from the baseline). `_score` stamps `died_by_setup_error_only` where every red was a
setup error, and prints `(SETUP ERROR -- no control body ran)`.

It is a **stamp, not a demotion**: `survived_all` is untouched and a setup error is still a kill.
Refusing to count one would be wrong — M9's is an honest fail-closed refusal that names its own
reason, and it arrives by exactly this route. **This is a RESULT field, not a spec field: it is
not in the hashed payload and it moves no fingerprint in the family.**

Its control is `tests/tools/test_a_kill_by_setup_error_is_not_a_control_firing.py`, three tests
over the whole partition (setup-error kill / assertion kill / survivor, plus the mixed red where a
body *did* run). **Mutation-proven, all three mutations applied and reverted:** `_ERRORED` widened
to the union → 3 failed; the stamp fired on any error → 1 failed; the stamp fired on any death →
2 failed. Two fakes of `_run_suite` in neighbouring suites were narrower than the real thing and
were widened to match — a fake that omits a field the scorer reads grades the fake.

**2. The fixture is split, so the tuple can be graded before the publish crashes** —
`tests/tools/test_grid_intensity_feed_and_explore_carbon.py`. `real_mix` stops at `fuel_mix()`;
`real_publish` depends on it and adds `generate()`. Two of the five do not break `fuel_mix()`
itself, and they are now closed by controls that assert:

| row | the contract | the control |
|---|---|---|
| M4 | the tuple's ORDER is the contract | `test_the_TUPLES_ORDER_is_the_contract_and_each_member_is_a_DIFFERENT_SHAPE` |
| M7 | must-run coverage is its own measurement | `test_the_MUST_RUN_COVERAGE_measures_the_MUST_RUN_BLOCK_and_not_the_IMPORTS_beside_it` |

Printed at real inputs before either was written: member 0 is 175,212 entries keyed
`(date, period)` with `(MW, t/MWh)` pairs, member 1 is 10 entries keyed by integer year with float
values — so M4 is a contract and not an equivalence, and the control asserts that distinguishability
explicitly rather than assuming it. Member 5 reports 544 / 6,013 / 9,831 MW over 175,156 usable
half hours, and **every one of those is re-derived here from member 4**, which
`zero_carbon_must_run_coverage` never sees: two independent reductions of the same rows agreeing is
the tie, and `import_coverage` cannot satisfy it at any value.

## The grid, at `d892342119e8`

Baseline `rc=0 failed=0` in **26.7s** (the data-present timing; this file is under a second with no
`sim/cache/`). Poison: the suite reaches the subject in 0.8s, both control suites stayed green.
Null round: `behaviour only`.

| row | verdict | stamp | named by |
|---|---|---|---|
| M3 | DIED | **SETUP ERROR — no control body ran** | (the first test in the module) |
| M4 | DIED | — | `test_the_TUPLES_ORDER_…` — the control written for it |
| M7 | DIED | — | `test_the_MUST_RUN_COVERAGE_…` — the control written for it |
| M9 | DIED | **SETUP ERROR — no control body ran** | (the first test in the module) |
| M10 | DIED | **SETUP ERROR — no control body ran** | (the first test in the module) |

## What this does NOT establish

- **M3, M9 and M10 are still proved by nothing, and the run says so on the cell.** All three raise
  *inside* `fuel_mix()`, so no control that calls it can assert past them. The remedy is the one
  this spec already set for M2: a **type-correct twin mutation** — the substitution a real
  fail-open patch would actually write, leaving the subject returning a value a control can grade —
  plus the control that kills it. That is the next increment on this claim and it moves the
  fingerprint, as M11 did. **Three of `fuel_mix`'s eleven contracts remain closed by nothing.**
- **`survived_all` is `null` on all five rows.** One suite was graded by choice, so no caller was.
  Nothing here changes the standing finding that `fuel_mix` has exactly one caller suite that can
  go red for it and that suite proves none of its contracts.
- **The stamp is not retroactive.** Every landed results file in this family predates the field and
  none of them carries it. The landed M5/M6/M8 grid is sound on the *other* discriminator — each of
  its three rows named a different node, and each named the control written for it — but that was
  read by a human, and any earlier grid in this family where one node killed several rows should be
  re-read before it is cited.
