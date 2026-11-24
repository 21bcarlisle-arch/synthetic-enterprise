**Severity:** LATENT · **Lane:** W1_market_weather · **Epoch:** unassigned · **Atom:** `unminted`

# The SAP splice was decided, its only hold lapsed on 19 Nov, and its handoff expired untaken

Found by the worker, 24 Nov 2026, while checking what the weather-to-price chain's build still waits on
(`WORKER_FINDING_THE_WEATHER_TO_PRICE_CHAIN_STEER_IS_HALF_ANSWERED_AND_ITS_REST_HAD_NO_WORK_ITEM_2026-11-24.md`, item 4).

## What the tree says

- **The decision is made.** On 18 Nov, blind to company results, the delivery seat decided **"Splice"**: the world's
  gas baseline takes GB daily SAP from 2018-01-01 in place of the monthly TTF proxy
  (`docs/staging/records/SEAT_RESULT_SPLICING_DAILY_SAP_INTO_THE_WORLDS_GAS_BASELINE_FROM_2018_2026-11-18.md`,
  "Decision"). The proxy is 29% too high on 2022's monthly mean and 30-44% too high on the forward from June to
  December 2022.
- **The switch was not made, on purpose.** The same section reads: "DIRECTION.yaml `not_now` holds it until skip1 and
  skip0 have read. It is handed on gated on skip0's output file." The loader landed
  (`sim.gas_prices_history.load_gas_baseline_spliced`). No runtime reader calls it. Only
  `tests/sim/test_gas_prices_history.py` does.
- **The hold has lapsed, and the handoff expired untaken.** The `not_now` row ("The world gas switch to spliced
  daily SAP (continuation world-gas-baseline-switch-readers-to-spliced-sap) ... correctly held on both skip control
  files") is in DIRECTION.yaml up to `4cd09c6ceb` (18 Nov 18:05). It is gone from `7852dd77ff` (18 Nov 18:53) and from
  every revision since. skip1 was graded in `a2c848965` and skip0 in `9a361e3562`. Both gate files exist:
  `/var/tmp/vts-out-skip1/control_11111_22222.json` (18 Nov 23:53) and `/var/tmp/vts-out-skip0/...` (19 Nov 10:31).
  The continuation that carried the switch, `world-gas-baseline-switch-readers-to-spliced-sap`, now lists as
  **EXPIRED, "written and never taken (window closed)"** in `python3 -m background.seat_continuation --list`. No work
  item, live continuation or focus row carries it.
- **The switch census leaves it out.** `docs/staging/records/SEAT_RECORD_THE_DEFAULT_OFF_SWITCHES_AND_THE_ORDER_THEY_FLIP_IN_2026-11-24.md`
  lists ten built, default-off switches. The splice is an eleventh. It is a world-fidelity change of the same kind as
  that record's #3 and #9, and it is decided and built. It has no flag: it is a reader repoint.
- **Downstream still cites the hold.** Five weather-to-price records say the chain's build waits on "the DIRECTION
  `not_now` hold" on SAP: the inputs-arm prereg, the net-export prereg and result, and the build-terms rerun prereg
  and result. That row left DIRECTION.yaml on 18 Nov, and its condition was met on 19 Nov.

## What the switch touches

The expired continuation's own reader list is: `simulation/run_phase2b.py:1959` (every gas run);
`company/interfaces/sim_interface.py:636` (the company's forward curve, which is the seam, so the interface steward);
`simulation/gas_settlement.py`; `simulation/publish_market_feed.py` (it reads `sim/gas_data/nbp_sap.csv` directly, at
line 23); `sim/weather_price_chain.py:149`; and `run_scenario`'s historical patch (`simulation/run_scenario.py:313-335`).
The phase-3b calibration scripts, `simulation/run_merit_order_reconstructibility.py` and `tools/run_segments.py` also
call `load_nbp_history`. Its done-means: "Every world gas reader reads the spliced record on origin/main. A test asserts
that the world's gas record from 2018-01-01 equals SAP and that the proxy is reachable only by name. The book that
follows names the switch's sha in background/next_book_requires.yaml."

The chain is the one reader that cannot switch alone. On SAP with no net-export term, its monthly MAE is
4.77 / 20.88 / 13.00 against the shipped 6.50 / 17.20 / 8.19 (`8be76e9495`). It needs SAP plus the annual
net-export level plus demand by year (`d2a4630783`: 4.22 / 16.81 / 6.18). On record years, that form uses each
year's real level, so it can ship for the record without waiting on a forward band.

## What is not decided here

Where the switch goes in the order. The switch-order record's rule is "one change per book" and "world fidelity
first on standing books", and rankq is running now. The order is the delivery seat's to set. It is not this
worker's to place around rankq.

## Close when

The splice is placed in the switch order, with its own one-variable book named, and then taken. Or it is ruled out
with a reason that answers the 18 Nov decision.

Reverse: delete this file.
