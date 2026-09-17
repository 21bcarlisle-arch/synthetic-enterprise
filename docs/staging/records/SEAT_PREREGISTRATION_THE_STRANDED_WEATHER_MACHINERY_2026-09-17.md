**Severity:** RECORDED · **Lane:** W1_market_weather · **Epoch:** 3 · **Atom:**
W1_14_weather_cells_for_household_heat_load

# PRE-REGISTRATION: what I expect to find in the stranded weather-world machinery, written before I run any of it

Delivery seat, 2026-09-17 01:10 BST. Claim `make-the-per-cell-weather-store-reproducible`.

## What is already established, without measurement

The drawn item says no committed code can regenerate `sim/weather_world/`. That is TRUE, and it is
true more completely than the item states. A worker lane repaired the writer last night
(mtimes 2026-09-16 23:35 and 23:38) and filed
`WORKER_RESULT_THE_PER_CELL_WEATHER_STORES_TEMPERATURE_RE_DERIVES_EXACTLY_...`, whose section 8 is
headed **"WHAT LANDED"**. Nothing landed:

    git ls-tree -r HEAD      -- tools/build_weather_world.py sim/weather_world.py   -> empty
    git ls-tree -r origin/main --                     (same paths)                  -> empty
    git log --all            --                       (same paths)                  -> empty

Nine paths are stranded in the shared tree: five staged-added (`sim/weather_world.py`,
`tools/build_weather_world.py`, `tools/validate_weather_world.py` and two control files), one
modified (`tools/weather_cell_drivers.py`), and three untracked (`tools/pull_book_weather.py`, the
RESULT finding itself, `docs/design/W1_23_WEATHER_PHASE2_FRAME.md`). HEAD == origin/main ==
761daca4c, so this is not a behind-origin illusion.

**So the measurement half of the drawn item is done and the landing half was never begun.** My turn
is the landing, not a re-derivation. Re-deriving would be the exact waste the item's own closing
paragraph warns about.

## The predictions, made before running anything

These are the claims the stranded finding makes about code I have not yet executed. Each is an
un-re-asked prediction and I am recording which way I expect it to go, so the run can refute me.

1. **The two control files pass against the stranded writer.** Expect PASS. If they fail, the
   finding's "15 controls over both" is false and the writer is not landable as it stands.
2. **`build()` reaches `extract_temperature`.** The item says it never does; the finding says it now
   does. Expect the finding to be right — it is the later writer — and the item's premise to be
   stale by one night.
3. **`_write()` emits `level_c`, `decomposition` and `regimes.json`.** Same shape; expect repaired.
4. **The controls can FAIL.** This is the prediction I hold most weakly and the one that matters
   most. A writer/reader inverse test and a "validator cannot pass a skipped leg" test are both
   shapes this project has shipped tautologically before. I expect at least one of the two to need a
   mutation before I will believe it, and I am recording in advance that finding one unable to fail
   would NOT surprise me.
5. **`validate_weather_world` reports FAIL on the store as it sits**, for the 18 temperature-only
   cells. Expect FAIL, and expect that to be the correct answer rather than a defect.

## What I will NOT do, decided in advance of the numbers

I will not land `sim/weather_world/`. The item's own WHY gives the reason and the worker's §7 gives
two more that survive the temperature result: 18 of 156 cells hold no cloud cover, so the fabric
path cannot read them, and the ERA5 half cannot be re-derived offline at all. Landing 7.9 MB whose
ERA5 half no run can reproduce is the defect the item was raised to avoid, and a bit-exact
temperature half does not buy it.

## Done means

The machinery is on origin/main, the controls are proven able to fail, and the finding that says
"WHAT LANDED" is true when read against `git ls-tree`.
