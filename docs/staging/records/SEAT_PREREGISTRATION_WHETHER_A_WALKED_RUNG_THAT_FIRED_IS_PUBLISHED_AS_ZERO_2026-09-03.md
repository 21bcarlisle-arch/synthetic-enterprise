**Severity:** RECORDED · **Lane:** D_billing_metering · **Epoch:** 3 · **Atom:** `D_opening_dd_seasonal_sizing`

# Pre-registration — whether a walked rung that fired is published to the reader as zero

*Delivery seat, 2026-09-03, lane-0. Written BEFORE the repaired split was computed. Continues
`SEAT_PREREGISTRATION_WHETHER_THE_OPENING_DD_ESTIMATE_REACHES_ANY_PUBLISHED_NUMBER_2026-09-03.md`
and the finding it produced,
`SEAT_FINDING_THE_OPENING_DD_ESTIMATE_WORKS_AND_NOTHING_PUBLISHED_CAN_SEE_IT_2026-09-03.md`, whose
§7 item 3 is what this grades.*

---

## What I already measured, and am therefore not predicting

These are established, not forecast, and are stated here so the predictions below cannot be read as
covering them:

* `simulation/live_population.live_population()` returns 257 supply points. **3 of them carry no
  `eac_kwh`/`aq_kwh`** — `C7` (elec, 2016-01-01), `C8` (elec, 2016-04-01), `C9` (elec, 2016-07-01).
* All three resolve through `estimate_annual_consumption` to basis **`TDCV_TYPICAL`**. The rung
  fires. It is not an unreachable branch.
* All three then get `opening_monthly_amount(...) is None`, because
  `get_cap_unit_rate_for_date` holds no published GB rate before the price cap began in
  January 2019 and all three were acquired in 2016. **A different refusal, at a later stage, for an
  unrelated reason.**
* `tools/dd_opening_arms.py:351` builds `basis_split` by iterating `est_open` — the accounts that
  came out with an **amount**. So a rung that fired and then lost its amount downstream contributes
  nothing to the split.
* The live feed `site/data/dd_opening_arms.json` therefore publishes
  `basis_precedence.walked = [registry_eac: 142, tdcv_typical: 0]`, and
  `site/capabilities/index.html` renders **"Ofgem's published typical values — 0"** to a reader.

The internal key is honestly named — `basis_split_of_estimated_accounts` — and `publish_view`
renames it to `basis_split` and hands it to `basis_precedence_view`, which is documented as the
split of *the precedence*. The name that reached the reader is not the name of the quantity.

## Why this is the same defect the last commit fixed, not a new one

`28865ab63` abolished a rendered `our own meter reads 0` on the ground that **a rendered zero is a
MEASUREMENT: it says the supplier looked and found none.** It fixed that for the two rungs in
`NOT_REACHABLE_AT_OPENING` and left the identical falsehood standing on the third. `tdcv_typical 0`
tells a reader no account needed Ofgem's fallback. Three did, and used it. This is the catalogued
shape *"the fix mechanises one disclosure and asserts the rest in prose"*.

## Predictions, filed before the repaired split was computed

**R1 — the repaired `tdcv_typical` resolution count is non-zero and the amount count stays zero.**
I predict the two counts separate for exactly this rung: resolutions ≥ 3, accounts-with-an-amount
**0**. If both come out non-zero I have mis-traced the rate refusal and must say so.

**R2 — `registry_eac`'s resolution count is strictly greater than the 142 published today**, because
142 counts survivors and the refusals are dominated by pre-2019 acquisitions that resolved an EAC
perfectly well. I predict it lands near `N_asked − 3 − n_unavailable`. I do **not** know
`N_asked`: `run()` measures `live_population() + successor_supply_points()` and I have measured only
the first term. If `registry_eac`'s resolution count comes back at 142 the population is not what I
think it is.

**R3 — `unavailable` is 0.** Every account carries either an EAC/AQ or the MEDIUM band, and the
band always resolves. If any account resolves to `UNAVAILABLE` there is a fourth outcome nobody has
named and it is its own finding.

**R4 — no run-output key moves.** This repair touches the published VIEW only; the organ, the two
arms and the three DD keys are untouched. I predict `whole_run_output_diff` is byte-identical
before and after, still naming exactly `annual_dd_review`, `dd_balance_book`,
`dd_level_collection_book`, and that every figure in the finding's §4 is unchanged to the penny. If
a drift or opening figure moves, the repair has reached the organ and must be reverted.

**R5 — the existing door control does not catch this and will still be green after a mutation that
reinstates it.** `test_every_information_source_reaches_the_reader_and_a_zero_is_never_a_zero`'s
walked-rung leg asserts `str(row["n_accounts"]) in rendered`, which `"0"` satisfies — and `"0"`
occurs in almost any rendered money string, so the assertion is close to a tautology for the zero
case. I predict that reverting `basis_split` to the survivors-only count leaves the whole existing
site suite **green**. That is the mutation that proves the new control is worth having, and if the
suite goes red without a new control then this prediction is refuted and the control already existed.

## What must NOT happen

1. **The two counts must never be summed, differenced into one number, or presented as one.** "The
   rung fired" and "the account got a direct debit" are two different events about two different
   populations. A single number covering both is the recurring failure CLAUDE.md names.
2. **No count is invented for a rung that did not fire.** If `tdcv_typical` had genuinely resolved
   for nobody, `0` would be the honest answer and would stay.
3. **The organ is not touched.** R4 is the check on this.
4. **No new published figure without its clock.** The split is on the billed-clock section that
   already carries one; it inherits it and does not get a second.

## How I will know I was wrong

If R1 fails, the three accounts do not reach the split for some reason other than the one I traced,
and the repair is aimed at the wrong line. If R4 fails, the change is not a view change and the
whole increment is unsafe. If R5 fails, this defect was already controlled and the finding is not a
finding.
