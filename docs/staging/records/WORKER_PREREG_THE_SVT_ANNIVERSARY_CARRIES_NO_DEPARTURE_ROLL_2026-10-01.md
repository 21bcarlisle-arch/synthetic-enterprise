**Severity:** LATENT · **Lane:** B_commercial (world side: `simulation/`) · **Epoch:** 2 · **Atom:** EP1_clv_three_horizon (upstream world fidelity)
**Answers:** `docs/staging/SEAT_FINDING_THE_PASSIVE_TERM_END_NEEDS_NO_DEPARTURE_ROLL_AND_THE_SVT_ANNIVERSARY_ADDS_A_SECOND_EXIT_ROUTE_2026-10-01.md`

# Pre-registration: the SVT anniversary carries no departure roll

**2026-10-01, autonomous worker, claim `the-svt-anniversary-redraw-is-a-second-exit-route-beside-c1b`.**
This was filed before the world was changed and before any run of the change was read.

## Why nothing in `simulation/` changed in this commit

The item's own gate is: *only after PB4's bill-shock base swap has had its own one-world run on
origin, and never in the same run.* When this was drawn, that gate was live and still protecting a
series in motion. The PB4 lane was 4 minutes into `surgical_land` for the sold-rate repair
(`price-the-opening-dd-at-the-rate-the-supplier-sold-at`). That repair is followed by its
one-world re-run, and then by the swap and the swap's own run. If a churn change landed under that
series, the series would hold two variables. So this commit fixes the prediction and the design,
and leaves the world as it is.

## The change, decided

Choose **remove the roll**. Do not choose *move the re-draw onto the cap calendar*.

- In `run_phase2b`'s renewal block (`term_index >= 1 and commodity == _decision_leg and not
  _indexed_tariff`), skip `roll_lifecycle_event` when the decision leg's **previous** term was an
  SVT segment. Read it from `_last_tariff_type.get(cid)` **before** line ~2278 overwrites it with
  the current term. Gating on the decision leg covers both builders: electricity
  (`renewals.build_renewal_schedule`) and the gas-only account (`_build_gas_renewal_schedule`).
- The anniversary re-draw in the builders **stays**. It is the household's internal conversion
  off the default tariff, and `tools.published_route_split.svt_internal_conversion_floor` requires
  that conversion to exist. Only the exit it carried is removed. After the change, C1b's inertia
  hazard carries every SVT exit, which is what its all-cause band says it does.
- Why not the cap calendar: that would move the *timing* of internal conversion. The record gives
  no evergreen anniversary (SLC 24.7, 31F.5(c)), but it gives no conversion calendar either. That
  is a separate question, and it should not share a run with the exit fix.
- Control: put the predicate in a named function, `departure_rolled_at_renewal(previous_tariff_type)`
  in `simulation/customer_events.py`, beside `roll_lifecycle_event`. Assert over the whole
  partition in one test: a fixed→fixed boundary rolls, a deemed/flex predecessor behaves as it did
  before, and an SVT predecessor does not roll. Mutation: return `True` unconditionally, and the
  SVT leg must go red.
- Out of scope, and named: on that same term, `_rate_shock_counts` still compares the new fixed
  rate against the last **fixed** rate, which can be years old. The bill-shock count belongs to
  PB4's swap, so it is left to it.

## Predictions

Baseline is one world at `aed6bf966`, from the finding: 360.2 SVT account-years, 52 C1b exits
(0.144/yr), 15 anniversary-route exits (0.042/yr), 0.186/yr in total. At SVT anniversaries outside
the FTC window: 28 active-and-stayed, 176 passive, 15 exits. Read with the finding's
`/var/tmp/se-ptm-out/analyse.py` shape. **Before reading the change run, re-run that baseline at
the same base commit.** If PB4's swap has landed by then, `aed6bf966` is no longer the baseline.

| | Prediction | Refuted if |
|---|---|---|
| Q1 | `[CHURN]` exits at a decision-leg term whose predecessor is SVT: **0** | any |
| Q2 | All-route SVT exits per SVT account-year: **0.12–0.17** (C1b alone, centre 0.144) | outside |
| Q3 | Active-and-stayed at SVT anniversaries outside the window: **36–50** (all ~43 active draws now stay) | outside |
| Q4 | Exit rate at fixed ends outside the window: **11–17%** (baseline 13.9%; not touched directly) | outside |
| Q5 | Whole-book departures fall by **8–22** against the same-base baseline | outside |

If Q2 is refuted *high*, C1b is not carrying the band on its own, and the inertia hazard has to be
read before anything is tuned. If Q4 moves outside its band, the change reached fixed→fixed
boundaries, which is a defect in the gate and not a finding about the world.
