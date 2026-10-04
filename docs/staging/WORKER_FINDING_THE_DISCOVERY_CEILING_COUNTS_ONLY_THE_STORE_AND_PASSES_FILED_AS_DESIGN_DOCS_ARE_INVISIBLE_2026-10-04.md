**Severity:** LATENT · **Lane:** W4_the_wall · **Epoch:** 3 · **Atom:** `EP14_adapter_published_cost_stack`

# The discovery ceiling counts only the note store, so passes filed as design docs are invisible to it

Draw: LANE 3 DISCOVER/FRAME on `EP14_adapter_published_cost_stack`, worker tick 2026-10-04.
**No sixth investigation was run.** The draw's useful act was to find that it should not have
been offered.

## 1. EP14 had taken five passes and the ceiling read one

`tools/discovery_pass_ceiling.py` counts passes from `docs/design/simplifications/<atom>.yaml`
only. EP14's passes 2 to 5 (`docs/design/EP14_PUBLISHED_COST_STACK_{DISCOVER,BATTERY}_2026-08-14.md`,
`..._SOURCE_CHECK_2026-08-17.md`, `..._RO_SOURCE_CHECK_2026-08-19.md`) each say in their header
that they were *deliberately* left out of the store, because appending there obliges a map
`simplifications_count` edit and the map carried another lane's hunk. Measured before this
change: `survey()` gave EP14 `passes 1, saturated False`. So the atom stayed in the idle
discovery draw for six weeks past the point where the 2026-08-19 ruling should have removed it.
This draw is the result.

**Remedy landed (instance):** four dated pointer notes, one per doc pass, appended to the store,
and the map's `simplifications_count` set 1 → 5. Now `survey()` gives `passes 5, saturated True`.
`decisions()` lists EP14 as "promote to build, or close it".

## 2. The class: at least one more atom has the same shape

I matched design docs whose header names `**Atom:**` and DISCOVER against `survey()`:
`EP5_settlement_true_ups` has 1 store pass and 4 DISCOVER docs. Others have 1 to 6 docs beside
their store passes. **I cannot yet say how many of those docs are also store notes**, which
would make them double-counted rather than missing. This census did not check overlap, so it
proves only the EP14 instance (confirmed by its own headers).

## 3. Recommendation

- **EP14's decision: promote to BUILD when the seat ranks it.** The block was lifted on
  2026-09-04 (`MATURITY_MAP.md`, the EP adapter block lift). The frame is complete: pass 1
  finding 4 names the build as adapter → the already-written, uncalled
  `company/pricing/ncc_forecast_register.py` → pricing path, with `simulation/policy_costs.py`
  kept as truth. The decision row has `exit_criterion: None`. Pass 1 finding 1 already proposes
  the criterion: per period, the parsed build-up reconciles to the cap-annex allowance within
  materiality, or every divergence carries a named driver. `total_gap_gbp` is explicitly
  excluded, because it *is* the stack total.
- **Class:** check EP5 the same way, by reading each doc's header for "store not edited", and
  backfill if so. Do not teach the ceiling to read `docs/design/*.md`: where a doc and a note
  record the same pass, that would double-count. The store is the pass register, and a pass
  that skips it is the defect.
