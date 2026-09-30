# Pre-registration: the HDD leg on the run's own book (W1_14), written 2026-09-30 before measuring

Observed before any change: `sim.weather_hdd.hdd_reading` returns `from_normal=True` for 91 of the
95 GAS_CUSTOMERS `simulation.run_phase2b` settles. Every `SYN-*` id reads the 1991-2020 normal
because `simulation.weather_inputs.cell_weather_for_customer_id` scans only the 18
`registered_supply_points`, while `weather_refusals_for_book(CUSTOMERS)` = 0 of 244: the store
holds their cells, the id door never asks the record that carries the coordinate.

Predictions for the fix (the runner hands the id door its book):
1. from_normal over the 95 gas premises: 91 -> 0.
2. Mean annual HDD (calendar 2022) over the SYN gas premises moves DOWN against the normal's 2,066,
   by 10-30% (the registered points moved -2.5% to -34.5%).
3. Before: every SYN premise's 2018 and 2022 annual HDD are identical. After: none are.
