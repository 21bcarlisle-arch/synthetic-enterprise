**Severity:** LATENT · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0 delivery
· **Class:** controls_that_cannot_fail

# RESULT: two more of `fuel_mix`'s contracts die, and the instrument could not see the control until it changed file

**Measured 2026-09-06 BST, isolated worktree on `8a2f11bb3`. Claim
`fuel-mix-M3-to-M10-are-proved-by-nothing`. Instrument
`python3 -m tools.grid_intensity_feed_contract_battery --only M9 M10 M12`, run twice: once at
fingerprint `7edf1af33b37` with `--suites explore_carbon`, once at `aa5ce7785789` with
`--suites fuel_mix_reads_the_cache`. Results
`/var/tmp/grid_intensity_fuel_mix_battery_7edf1af33b37.json` and
`…_aa5ce7785789.json`; logs `/var/tmp/fuel_mix_M9_M10_M12.log` and `…_split.log`. Both exit 0,
subject restored (`git diff` clean on `tools/generate_grid_intensity_feed.py`). Prereg
`docs/staging/records/SEAT_PREREG_CAN_M9_AND_M10_BE_CLOSED_WITHOUT_A_TWIN_MUTATION_2026-09-06.md`.**

## The drawn item's premise is spent, and this is the re-measurement rather than the citation

The item asks for controls killing **M5, M6, M8** and a re-run at fingerprint **`d7eb36a0b901`**.
Both were already answered on this claim before this lane drew it:

- The landed grid `/var/tmp/grid_intensity_fuel_mix_battery_d7eb36a0b901.json` does say what the
  item says — M1, M2 and M11 killed by `test_grid_intensity_feed_and_explore_carbon.py`, M3–M10
  killed by nothing. **It is two hours older than the commits that answered it.** The three
  controls landed at `6965b1ee4` and were graded at `d892342119e8`.
- `d7eb36a0b901` cannot be reproduced: `contract_battery.fingerprint` hashes the engine's field
  list, and fields were added after `03387ff1e`.

So this lane took the increment the last result named as next — **M3, M9 and M10**, whose `DIED`
at `d892342119e8` was `died_by_setup_error_only`: one module-scoped fixture erroring, no control
body run.

## What now dies, and what does not

| row | verdict at `aa5ce7785789` | named by | closed? |
|---|---|---|---|
| **M9** the thermal floor is read from the THERMAL cache | DIED, `died_by_setup_error_only` **false** | `test_the_THERMAL_FLOOR_is_read_from_the_THERMAL_CACHE_and_not_the_OUTTURN_one_beside_it` — the control written for it | **YES** |
| **M12** the biomass rows are FILTERED TO BIOMASS (new row: M10 with a dict, not a list) | DIED, stamp false, 1 failed **1 passed** | `test_the_BIOMASS_ROWS_are_FILTERED_TO_BIOMASS_before_the_ENVELOPE_is_taken_over_them` — the control written for it | **YES** |
| **M10** the same contract with a LIST substituted | DIED, stamp **false** | the THERMAL control — *not its own* | **NO** |
| **M3** the outturn is normalised to settlement periods | not re-run | — | **NO**, and see below |

**M9 did not need a twin, and the reason is that its old kill was an accident of a cache's
contents.** Substituting `load_cached()` for `load_cached_thermal()` raises today because
`sim/cache/elexon_fuelhh.json` is 1,298,444 rows of COAL and nine interconnectors with **no CCGT
or OCGT at all** — measured, not assumed. That refusal is a fact about that file, not about which
cache the floor is read from. Widen the outturn fetch to all fuel types, a one-line change with
its own good reasons, and the same mutation publishes a floor measured off the whole gas fleet
with nothing going red. The control therefore stubs an outturn cache that DOES carry gas: at those
inputs the thermal cache gives a 2020 floor of **3,102 MW** and the outturn cache **20,502 MW**,
and the control asserts the discriminator is live before it asserts the contract.

**M10 needed a twin because three of the four things it guards are equivalences on the real
record.** Measured over 143,057 cached rows: 100% `BIOMASS`, every `settlementDate` already 10
characters, every period inside 1–50, and the 19 duplicate `(date, period)` keys resolve the way a
dict comprehension resolves them. Only the fuel-type filter is left, and the real cache has
nothing to filter — so the control supplies a MIXED cache. Filtered, 2020's envelope is
1,001–1,048 MW; unfiltered it is 20,001–20,048 MW, the CCGT rows entire.

## The finding: `-x` plus a shared fixture makes a control unmeasurable, and the cell cannot say so

Both controls were first written **inside** `test_grid_intensity_feed_and_explore_carbon.py`, as
the drawn item asks. Run there at `7edf1af33b37`:

```
M9  DIED (SETUP ERROR -- no control body ran) [...::test_the_TUPLES_ORDER_is_the_contract...]
M12 DIED (27.9s)                              [...::test_the_BIOMASS_ROWS_are_FILTERED...]
```

**M9's control had not run.** `_run_suite` runs every mutation round with `-x`; M9 makes
`fuel_mix()` raise on the real caches; the module-scoped `real_mix` fixture errors; every test in
the module errors with it; `-x` stops at the first node. The cell named a control written for a
different row and reported a kill that proves nothing about either.

> **A control's reachability depends on where in the file it sits, and no care in writing it can
> fix that.** `-x` reports the FIRST red. A module-scoped fixture that the mutation breaks puts a
> red in front of every control in the file. The remedy is not a better assertion; it is a file
> the fixture is not in.

M12 escaped it for a reason worth keeping: **a type-correct mutation does not break the fixture.**
M12 is an equivalence on the real caches, so `real_mix` and `real_publish` succeeded, every
fixture-based test passed, and `-x` reached the control. The property that makes a twin gradeable
is the same one that makes it survive the fixture.

The two controls now live in
`tests/tools/test_fuel_mix_reads_the_cache_each_member_names.py`, a third entry in
`DIRECT_SUITES`. Baseline 0.7s against 28.3s, and — unlike the file they came from — it needs no
`sim/cache/`, so a `git archive HEAD` extract grades it rather than skipping it.

## The second finding: the setup-error stamp does not catch a wrong-class red in a control BODY

M10's cell at `aa5ce7785789` reads `DIED`, `died_by_setup_error_only` **false**, named by a
control. Every discriminator the engine has says a control fired. **It did not.** Measured by hand
— M10 applied to the subject, the suite run with `--tb=line`, subject restored:

```
E   AttributeError: 'list' object has no attribute 'items'
sim/elexon_fuel_outturn.py:845
```

Both controls red on that, in their bodies, before any assertion. The stamp added at `ff2dd516d`
covers `ERROR at setup`; a wrong-class exception raised *inside* a test body is a `FAILED` and is
invisible to it. That is the same false-kill class M11 exists for, arriving through a door the new
stamp does not watch. **No repair is proposed here** — the honest discriminator is the exception
class, the engine currently parses only node ids out of `-q --tb=no` output, and widening that is
a judgement about the instrument rather than a fix anyone should make blind.

## M3 stays open, and the prediction that said so held

Filed before running: *M3's only type-correct twins re-implement `to_settlement_periods` inline,
which grades the twin rather than the subject.* Measured directly on the adapters — the natural
patch, `series = {(r["settlementDate"], r["settlementPeriod"]): r for r in fuel.load_cached()}`:

| adapter | what it does with un-normalised values |
|---|---|
| `imports_by_period` | returns `(0.0, 0.0)` for every half hour — silent |
| `coal_capacity_by_year` | returns `{2020: 0.0}` — silent, and reads as a closed fleet |
| `import_coverage` | **raises** `FuelOutturnUnavailable: no imported MW at all in the series, so coverage is undefined. GB has never gone a year without importing; this is an absence.` |

**This materially reduces M3's exposure and the reduction is not something the battery could
show.** The realistic fail-open patch cannot silently revert: two members go quietly wrong and the
third refuses, by name, one call later. M3 is still proved by no control — but it is fail-closed
by construction at `import_coverage`, which is a different and much smaller thing than the eight
rows the claim opened with.

## What this does NOT establish

- **`survived_all` is `null` on all three rows.** One direct suite was graded by choice, so no
  caller was. The standing finding is untouched: `fuel_mix` has exactly one caller suite that can
  go red for it and that suite proves none of its contracts.
- **M10's own row is not closed** and should not be read as closed however clean its cell looks.
  Its contract is closed by M12, the way M2's is closed by M11.
- **Nothing here re-grades M1–M8 or M11.** The three fingerprints in this document
  (`d7eb36a0b901`, `7edf1af33b37`, `aa5ce7785789`) are three different specs, and only the last
  is live.
