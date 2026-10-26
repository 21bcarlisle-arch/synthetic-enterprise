# The shared tree's meter_reads.py copy is the superseded ratio draft of the landed fuel split

**Severity:** LATENT · **Lane:** W2_customer_generator · **Epoch:** 4 · **Atom:** `W2_36_unbilled_energy_arises_the_way_it_does_in_reality`

## What landed

c77a181fa (on origin/main) splits `q6_smart_not_in_smart_mode_share` by fuel at the DESNZ Q4 2024
domestic shares. Electricity has 1.4m of 20.5m smart meters in traditional mode, which is 6.83%.
Gas has 2.2m of 15.5m, which is 14.19%. Both together are 3.6m of 36.0m, the register's 0.10.
The source is `docs/market_research/meter_read_latency_estimation_2026.md` s.1, and it holds:
19.1m + 1.4m and 13.3m + 2.2m are the smart stocks in its own table.

The landed form holds each fuel's **odds ratio** to the blend. The stranded diff on the shared
tree (mtime 03:10Z, no claim) held a **plain ratio**. That form breaks at the row's ends. At 1.0,
which is how `force_estimated_reads` pins every smart meter out of mode, it left electricity 68%
out of mode and sent gas past 1. Two tests in `tests/simulation/test_run_phase4c_on_phase2b.py`
went red under it: `test_an_estimated_run_past_12_months_is_not_forced_...` and
`test_billing_accuracy_finds_the_barred_energy_...`. Under the odds form they are green, and so is
every file that imports `meter_reads` (741 passed).

## What is left, and why the seat did not do it

`/home/rich/synthetic-enterprise/simulation/meter_reads.py` still holds the ratio draft. It
differs from origin/main by 5 insertions and 17 deletions.
`tools.refresh_to_head --base origin/main --base-wins` refused it as
`[predates_landing_carrying_some]`. The flag needs the clock to establish that the copy is the
older draft, and here it was only the seat's word. The refusal is deliberate, so it was not forced.

The judgement is made: **the odds form wins.** The copy adds no name except
`SMART_MODE_FUEL_RATIO`, which the odds form replaces. Whoever holds the shared tree can drop the
copy to origin's bytes. Nothing in it is unlanded work.

**Do not** land it with `isolate_hunks` + `surgical_land --content`. That would replace the odds
form with the ratio and turn the two phase4c tests red on origin.

## What stays open in W2_36

The two legs of one home draw their smart-mode state from their own ids. A lost comms hub would
take both fuels, and that is not modelled. Nobody publishes the joint rate, so this is a GAP and
not a number to pick.
