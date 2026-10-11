**Severity:** RECORDED · **Lane:** W_world · **Epoch:** 4 · **Atom:** `unminted` · **Claim:** `world-2022-price-response-on-in-the-settled-book`

# Result: the settled book takes the SERL price response, and the demand digest now sees it

Grades `SEAT_PREREG_THE_SETTLED_BOOK_TAKES_THE_SERL_PRICE_RESPONSE_2026-10-11.md`, committed
(`e0bd5345d`) before the switch was thrown or anything below was run.

## What changed

- `fabric_demand_path.SETTLED_BOOK_PRICE_RESPONSE = True`, passed by `build_fabric_series_for_site`
  (the door `run_phase2b` settles a fabric premise through) and carried in its shared-trace key.
- `premise_trace.comfort_constraint_for` loses its price leg: `_PRICE_ELASTICITY = 0.45` and the
  `unit_price_p_per_kwh` / `reference_price_p_per_kwh` arguments. No production caller passed a
  price, so the term was zero on every settled call. The one unit test that fed it is deleted with it.
- `world_home_identity.home_demand_identity` reads, for each of the 96 probe homes, the gas and
  electricity multipliers the settled book applies on the 1st of every month April 2022 – March 2024,
  or the marker `price_response:off` when the switch is off.

## Grading

| # | predicted | result |
|---|---|---|
| P1 | nothing before 2022-04-01 moves | **Held exactly.** 27,300 of 27,300 premise-days before April 2022 byte-identical on and off, both fuels, n = 60 gas-heated fabric premises of the live book, 2021-01-01 – 2024-03-31. |
| P2 | winter 22/23 gas at the graded distribution, electricity at 6.4% | **Held.** Gas median 10.8%, IQR (0.5, 21.0); electricity 6.4%, IQR (−1.9, 15.0); n = 60. Per premise, the figures equal the graded clean run (`/var/tmp/se-price-2022/run_serl.log`) to every printed digit: C1 gas 26.21 / electricity 18.10, SYN-2016-002 10.51 / 22.23. The door adds nothing to the mechanism. |
| P3 | departure and homes digests unchanged; demand digest moves | **Held.** Departure `cdba75ebb9197b33`, homes `35f8efe8ff02f245`, both unchanged. Demand `c20a2cd403410ed7` → `7d6195c5eb1562ab`. With the switch off it reads `4cb6fa5e7ca02a25`, not the old value: the probe now carries a marker for "off", so no stamp written before today matches either state. That is correct — no arm on disk was measured with the response leg in its stamp. |
| P4 | value arms not re-taken here | **As predicted.** Handed on. |

Run: `/var/tmp/se-price-response/settled_door_on_off.py 60`, toggling only the module constant;
log `/var/tmp/se-price-response/settled_door_run.log`.

The turn that built this ended before landing it; the next turn recovered it from the worktree's
salvage commit `93c2efe0c`, re-ran the four test files (176 passed), re-took both mutations below
(each reds), and re-printed the stamps (same three digests).

## Controls, mutation-proven

- `test_fabric_demand_path.py::test_the_settlement_door_applies_the_2022_price_response` — reds with
  the constant set `False`; its second leg reds if the shared-trace key cannot tell the two apart.
- `test_the_world_demand_digest_moves_with_the_demand.py::test_the_price_response_switch_moves_the_digest`
  — reds with the constant `False`, and reds with the price leg dropped from `_demand_vectors`.

## What it licenses, and what it does not

- The settled book now shows a 2022 demand response on its fabric premises. Year-on-year volumes
  across April 2022 now carry it.
- **Every value-arms artefact on disk was measured in a different demand world**, and
  `_blind_envelope_demand_refusal` now says so with the live digest. The arms are re-taken next.
- The legacy national-shape premises still carry no response (the hook is in the fabric path only),
  and the two filed gaps stand: electricity 2 points short of SERL, calendar 2022 about half of ECUK.
