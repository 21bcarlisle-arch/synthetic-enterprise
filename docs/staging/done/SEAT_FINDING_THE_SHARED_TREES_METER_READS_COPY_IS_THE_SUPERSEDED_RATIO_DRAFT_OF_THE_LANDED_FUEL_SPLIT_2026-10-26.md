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

## Done

*2026-10-27, delivery seat, under `the-shared-checkout-runs-the-code-origin-holds`.* The shared
tree's `simulation/meter_reads.py` and `tests/simulation/test_meter_reads.py` were preserved
byte-for-byte at `refs/preserved/origin-reconcile-superseded-live/seat-judged-7db1e2c4af-2026-10-27`
(commit `c1098dc3ab`, read back clean) and restored for the fast-forward onto origin/main, so
the odds form is what the box runs. The same ref holds seven other copies, each judged by
reading it against origin rather than by any tool's grade:

- `docs/design/maturity_map.yaml`: its only difference is B13's row at L2. b7b17b8bf3 moved
  that row to `maturity_map_closed.yaml`, so the copy would have put a closed atom back on the
  live map.
- `docs/market_research/unbilled_energy_and_revenue_assurance.md`: this copy held the one piece of
  real unlanded work, the K8 section for c77a181fa's fuel split. It described the plain ratio,
  so it landed corrected to the odds form, with the correction beside the claim (see that commit).
- `SEAT_FINDING_EXPLORES_CAST_...`, `..._BLIND_INVARIANT_SUITE_...`, `..._DEFAULT_BOOK_SHIPS_...`,
  `..._TERM_RATE_AGAINST_ITS_WHOLESALE_FLOOR_...` and `..._PRINTED_RATE_...`: each copy's mtime
  is earlier than origin's last commit to that path. The lines only the copy holds are the text
  origin's later edit replaced: a BLOCKING severity that origin regraded LATENT, an "owed" stub
  since filled, and a GAP that origin struck through and answered.

Recover any of them with `git show <ref>:<path>`.

The shared checkout is level with origin/main at `f0d04dd72`, and `units_lacking_origin` is empty.
`deploy_restart --apply` restarted six daemons whose loaded code was behind disk. Among them is
`supervisor.service`, which rebooted at `f0d04dd72`, so cd59b84f9's refusal now runs in it:
`correctness_stretch_refusals()` names EP16, SPINE_1, C4 and W1_10. Twenty-seven other blockers
were cleared by `origin_reconcile.advance_shared_tree` under its own hash and three-way proofs.
