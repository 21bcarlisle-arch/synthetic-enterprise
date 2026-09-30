# W1_14: the HDD leg read the monthly normal for 91 of the 95 gas premises the run settles

**Graded against** `PREREG_THE_HDD_LEG_ON_THE_RUNS_OWN_BOOK_2026-09-30.md`, written before the
measurement.

## What was wrong
`sim.weather_hdd.get_hdd(date, customer_id)` resolves a sky through
`weather_inputs.cell_weather_for_customer_id`, which scanned only the 18 `registered_supply_points`.
`run_phase2b` settles 95 gas premises: 76 `PROS-*` and 15 `SYN-*` of them are drawn households no
roster entry holds, so every one read the 1991-2020 England & Wales monthly normal. Their 2018 and
2022 were the same number. Meanwhile `weather_refusals_for_book` over the same records said
0 refused: it is handed the record, the id door was not. The 2026-09-21 step-3 claim "16/18 read
their own cell" was true of the roster and said nothing about the book.

A second thing: the runner half of steps 1 and 3 (`adopt_shared_world`, the store handed to the
shape and price legs, the `weather_refusal_by_customer` record) was **in no commit**. It was only in
the shared working copy of `simulation/run_phase2b.py`. The build_note's "LANDED" covered
`weather_inputs.py` and `weather_hdd.py` only. It lands here, isolated from another lane's hunks in
the same file.

## Fix
`weather_inputs.adopt_book(customers)` is the id door's record source, and the runner calls it
next to `adopt_shared_world`. Adopting a premise also drops its cached sky, so a refusal cached
before adoption does not survive it.

## Measured (one process, before and after)
| | prediction | result |
|---|---|---|
| gas premises on the normal | 91 -> 0 | **91 -> 0** |
| mean 2022 annual HDD, the 91 | down 10-30% | **2,086 -> 1,744 (-16.4%)**; per premise -35.7% to +10.4%, median -16.4% |
| premises with 2018 == 2022 | all -> none | **15/15 -> 0/15** (SYN subset checked) |

All three held. The +10.4% tail was not predicted: some cells are colder than the England & Wales
normal (northern cells).

## Controls
- `test_a_drawn_gas_premise_reads_its_cell_once_the_runner_adopts_its_book` is one partition. Before
  adoption the premise must read the normal, after adoption it must not, and a roster premise is
  unaffected either way.
- `test_the_runner_adopts_the_gas_book_it_settles` walks the AST, not the text, so the comment
  beside the call cannot satisfy it.
- Mutations: dropping the `_BOOK` lookup, the cache pop, and the runner call each red exactly one
  leg.
- Also fixed a pre-existing red: `"7.4 km" in basis` was pinned to today's answer. The store grew,
  Birmingham now sits 5.5 km out, and the control is now keyed to the property.

## Not done
- Level stays 1. Its measured reason is now false (two I&C premises remain, both named), so the
  level judgement is owed. It was not taken in this landing.
- Birmingham's cell (step 2) and the drawn-frame judgement (step 3) are still open.
