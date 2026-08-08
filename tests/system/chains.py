"""The five chain drivers and their arrival assertions — `AO3_join_test_tier`.

Design: `docs/design/JOIN_TEST_TIER.md`.

Why drivers and assertions live HERE rather than inside each test module
------------------------------------------------------------------------
The R15 fail-open shape this tier has to defend against is *a join test that
passes when the chain it spans is disconnected*. The only proof against it is to
cut the join in the production source and show the assertion fires — and that
proof is worthless unless the mutation test runs **the same assertion that
ships**. A mutation test carrying its own copy of the assertion proves something
about the copy (`feedback_tautology_reappears_inside_r15_tests`: only mutating
the source finds it).

So each chain is a pair:

  run_<chain>_chain(...) -> dict   drives REAL production functions end to end
  assert_<chain>_join(record)      raises AssertionError if propagation is absent

`test_join_*.py` calls the pair on an intact tree. `test_join_cut_mutation.py`
imports the *same* pair, cuts one production link, and asserts the *same*
assertion raises.

Every driver asserts its OWN PREMISE before returning: if the two scenarios it
compares do not actually differ at the input, it raises rather than handing back
a comparison that would pass vacuously
(`feedback_population_control_needs_a_vacuity_guard`).

These helpers deliberately see BOTH sides of the epistemic wall — a test must
see the simulation's truth and the company's belief, or it could never verify the
wall holds at all (JOIN_TEST_TIER.md §2). That is exactly why nothing under
`company/`, `saas/`, `sim/` or `simulation/` may import this module; enforced by
`test_report_only_landing.py::test_no_production_module_imports_the_test_tree`.
"""

from __future__ import annotations

import random
from datetime import date, timedelta

from company.risk import hedge_policy
from company.trading import hedge_decision
from saas import bill_generator

# ── production sources under test — imported at module scope so a monkeypatch
# against the SOURCE module (the R15 cut) is seen by the drivers below ─────────
from simulation import arrears_engine, demand_model, meter_reads, premise_demand, settlement

PERIODS = 48

# ══════════════════════════════════════════════════════════════════════════════
# CHAIN 1 — the work loop: a run completes → publishes → the next draw picks up
#           real work
#
# The advisor singled this one out: "this one alone would have caught most of
# the last fortnight." The property under test is Rule 0's — a state where
# unfinished work exists and NOTHING is drawable is a defect, not a rest — plus
# the publish→draw link that was consumed-not-absorbed twice (a wedged publish
# gate has to CHANGE what the next draw picks up, or the loop ticks happily
# while nothing can publish).
# ══════════════════════════════════════════════════════════════════════════════

#: An unfinished atom: a real level gap, drawable stage, no unmet dependency.
#: `id`s are deliberately unmistakable so a LIVE fork's in-progress set (which
#: `_maturity_map_draw_concurrent` reads from real state, fail-open) can never
#: collide with the fixture and silently empty the candidate list.
UNFINISHED_ATOM = {
    "id": "JOIN_TIER_UNFINISHED_ATOM",
    "title": "an atom with a real gap",
    "lane": "H_harness",
    "level_current": 0,
    "level_target": 2,
    "loop_stage": "build",
    "dial_inherited": 3,
    "depends_on": [],
    "file_scope": ["tests/system/"],
}

#: A finished atom: at target, so it must never be re-offered as work.
FINISHED_ATOM = {
    "id": "JOIN_TIER_FINISHED_ATOM",
    "title": "an atom already at target",
    "lane": "H_harness",
    "level_current": 3,
    "level_target": 3,
    "loop_stage": "build",
    "dial_inherited": 3,
    "depends_on": [],
    "file_scope": ["docs/design/"],
}


def draw_from_map(tmp_path, atoms: list[dict]) -> list[dict]:
    """Run the REAL supervisor draw against an injected map and nothing else.

    Factored out so the opposite-direction control (an all-finished map must draw
    NOTHING) can exercise the same production draw without going through
    `run_work_loop_chain`'s premise guard — that guard exists precisely to stop
    the main comparison being run on a map with no unfinished work, so the
    control cannot be allowed to disable it.

    `MATURITY_MAP_PATH` is restored in a `finally` even on failure: leaking a tmp
    path into a module constant would silently starve every later draw in the
    session.
    """
    import yaml

    from background import supervisor

    map_path = tmp_path / "maturity_map.yaml"
    map_path.write_text(yaml.safe_dump(atoms), encoding="utf-8")
    original = supervisor.MATURITY_MAP_PATH
    try:
        supervisor.MATURITY_MAP_PATH = map_path
        return supervisor._maturity_map_draw_concurrent()
    finally:
        supervisor.MATURITY_MAP_PATH = original


def run_work_loop_chain(
    tmp_path,
    *,
    atoms: list[dict] | None = None,
    wedge_age_seconds: float = 2 * 60 * 60,
    wedge_failures: int = 5,
) -> dict:
    """Drive run-completes → publish state → next draw, twice: once with a clean
    publish gate and once with a wedged one, over the SAME unfinished work.

    Every path is injected (`tmp_path`), so the chain reads no production state
    and writes none. The draw itself is the real
    `supervisor._maturity_map_draw_concurrent`, resolved as a module attribute at
    call time so an R15 cut applied to the supervisor module is seen here.
    """
    import json

    import yaml

    from background import supervisor

    atoms = list(atoms if atoms is not None else [UNFINISHED_ATOM, FINISHED_ATOM])
    unfinished = [a for a in atoms if a.get("level_current", 0) < a.get("level_target", 0)]
    if not unfinished:
        raise AssertionError(
            "driver premise violated: the fixture map contains no unfinished work, so "
            "'unfinished work exists and nothing is drawable' cannot be observed"
        )

    clean_state = tmp_path / "publish_gate_clean.json"
    clean_state.write_text(json.dumps({"failures": []}), encoding="utf-8")

    now = 1_700_000_000.0
    wedged_state = tmp_path / "publish_gate_wedged.json"
    wedged_state.write_text(
        json.dumps(
            {
                "failures": [
                    {"ts": now - wedge_age_seconds, "reason": "a red test wedged the gate"}
                    for _ in range(wedge_failures)
                ],
                "wedge_since": now - wedge_age_seconds,
            }
        ),
        encoding="utf-8",
    )
    last_tested = tmp_path / "last_tested_hash"
    last_tested.write_text("0000000000000000000000000000000000000000", encoding="utf-8")

    # link 1+2 — the publish outcome reaches the wedge detector
    clean_verdict = supervisor._publish_gate_wedge_active(
        now=now, head="deadbeefdeadbeefdeadbeefdeadbeefdeadbeef",
        state_path=clean_state, last_tested_path=last_tested,
    )
    wedged_verdict = supervisor._publish_gate_wedge_active(
        now=now, head="deadbeefdeadbeefdeadbeefdeadbeefdeadbeef",
        state_path=wedged_state, last_tested_path=last_tested,
    )

    # link 3 — the map's unfinished work reaches the draw
    drawn = draw_from_map(tmp_path, atoms)

    return {
        "unfinished_ids": sorted(a["id"] for a in unfinished),
        "finished_ids": sorted(
            a["id"] for a in atoms
            if a.get("level_current", 0) >= a.get("level_target", 0)
        ),
        "drawn": drawn,
        "drawn_ids": sorted(a.get("id") for a in drawn if isinstance(a, dict)),
        "clean_verdict": clean_verdict,
        "wedged_verdict": wedged_verdict,
    }


def assert_work_loop_join(chain: dict) -> None:
    """Unfinished work must be drawable, finished work must not be re-offered,
    and a wedged publish gate must change what the next draw sees."""
    # link 1+2 — the publish outcome reached the wedge detector, BOTH ways. A
    # detector that always says "wedged" is as broken as one that never does.
    assert chain["clean_verdict"] is None, (
        "JOIN CUT (publish → draw): a CLEAN publish gate was reported wedged — "
        f"{chain['clean_verdict']!r}"
    )
    assert chain["wedged_verdict"] is not None, (
        "JOIN CUT (publish → draw): a publish gate wedged for hours did not reach the "
        "draw ladder at all — this is the exact state that ticked silently for 2h17m twice"
    )
    assert "PUBLISH-GATE WEDGE" in chain["wedged_verdict"], (
        "JOIN CUT (publish → draw): the wedge draw carries no diagnostic payload (R5)"
    )

    # link 3 — Rule 0: unfinished work present ⇒ something is drawable. This is
    # the assertion that would have caught most of the last fortnight.
    assert chain["drawn"], (
        "JOIN CUT (work → draw): unfinished work exists "
        f"({chain['unfinished_ids']}) and the draw returned NOTHING — an empty feasible "
        "set with real work present is a defect in the dials, never a rest (Rule 0)"
    )
    assert set(chain["drawn_ids"]) <= set(chain["unfinished_ids"]), (
        "JOIN CUT (work → draw): the draw offered work that is not unfinished — "
        f"drew {chain['drawn_ids']}, unfinished is {chain['unfinished_ids']}"
    )
    for finished in chain["finished_ids"]:
        assert finished not in chain["drawn_ids"], (
            "JOIN CUT (work → draw): the draw re-offered an atom already at target "
            f"({finished}) — re-verification is not real work"
        )


#: A flat 48-period base consumption shape (kWh). Flat on purpose: any structure
#: the chain produces is then attributable to the chain, not to the fixture.
FLAT_BASE_SHAPE = [0.2] * PERIODS

#: An all-electric premise with storage heating — the heating_system key
#: `demand_model.ELEC_HEATING_KWH_PER_DEGREE_DAY` actually responds to, so the
#: weather link genuinely conducts.
HEATED_PREMISE = {
    "premise_id": "JOIN-PREMISE-1",
    "heating_system": "electric_storage",
    "occupancy_pattern": "family",
    "assets": {},
}


def assert_no_wall_crossing(paths: list[str]) -> None:
    """Assert no company-side participant in this chain reads simulation internals.

    "Feed real input at one end, assert the outcome at the other, AND assert
    nothing crossed the wall on the way" — this is the third clause, applied to
    the chain's own participants rather than to a whole-repo diff.

    Uses `tools.epistemic_verifier.scan`, the same checker the phase-close
    verifier runs, so a chain cannot be judged clean by a private standard.
    FAIL-CLOSED on an unavailable checker: an unavailable check is a FAILED
    check (R15 fail-silent), so an ImportError raises rather than skipping.
    """
    from tools import epistemic_verifier

    passed, violations = epistemic_verifier.scan(paths)
    assert passed, (
        "WALL CROSSED by a chain participant — the company layer read simulation "
        f"internals: {violations}"
    )


def _price_records(dates: list[str], price_gbp_per_mwh: float) -> list[dict]:
    """System-price records in the exact shape settlement looks up by
    (settlementDate, settlementPeriod)."""
    return [
        {
            "settlementDate": d,
            "settlementPeriod": p,
            "systemSellPrice": price_gbp_per_mwh,
        }
        for d in dates
        for p in range(1, PERIODS + 1)
    ]


def _dates(start: str, days: int) -> list[str]:
    d0 = date.fromisoformat(start)
    return [(d0 + timedelta(days=i)).isoformat() for i in range(days)]


# ══════════════════════════════════════════════════════════════════════════════
# CHAIN 2 — the physical chain: weather → premise demand → settlement → book
# ══════════════════════════════════════════════════════════════════════════════

def run_physical_chain(
    *,
    warm_temp_c: float = 16.0,
    cold_temp_c: float = 1.0,
    regional_deviation_c: float = -1.5,
    price_gbp_per_mwh: float = 60.0,
    days: int = 3,
    start: str = "2023-01-09",
) -> dict:
    """Drive weather → premise demand → settlement → book, twice: once on a warm
    national temperature and once on a cold one, everything else held identical.

    Returns both ends of both runs so the arrival assertion can check the change
    propagated AND arrived at the right magnitude.
    """
    if not cold_temp_c < warm_temp_c:
        raise AssertionError(
            "driver premise violated: the cold scenario must be colder than the warm one "
            f"(cold={cold_temp_c} warm={warm_temp_c}) — otherwise the comparison is vacuous"
        )

    dates = _dates(start, days)
    prices = _price_records(dates, price_gbp_per_mwh)
    customers = [
        {
            "customer_id": "JOIN-CUST-1",
            "acquisition_date": dates[0],
            "unit_rate_gbp_per_mwh": 140.0,
        }
    ]

    def _leg(national_temp_c: float) -> dict:
        # link 1 — weather → premise demand (the premise's LOCAL temperature)
        shape = premise_demand.premise_demand_shape(
            FLAT_BASE_SHAPE,
            national_temp_c,
            regional_deviation_c,
            "electricity",
            HEATED_PREMISE,
        )
        # link 2 — premise demand → settlement
        records = settlement.run_settlement(
            customers, dates[0], dates[-1], lambda _d: shape, prices
        )
        # link 3 — settlement → the book
        return {
            "national_temp_c": national_temp_c,
            "local_temp_c": premise_demand.local_mean_temp_c(
                national_temp_c, regional_deviation_c
            ),
            "shape_kwh": shape,
            "daily_kwh": sum(shape),
            "settled_records": len(records),
            "settled_kwh": sum(r["consumption_kwh"] for r in records),
            "wholesale_cost_gbp": sum(r["wholesale_cost_gbp"] for r in records),
            "revenue_gbp": sum(r["revenue_gbp"] for r in records),
            "margin_gbp": sum(r["margin_gbp"] for r in records),
        }

    return {
        "warm": _leg(warm_temp_c),
        "cold": _leg(cold_temp_c),
        "price_gbp_per_mwh": price_gbp_per_mwh,
        "expected_records": len(dates) * PERIODS,
    }


def assert_physical_join(chain: dict) -> None:
    """Cold weather must arrive at the book, at the volume×price magnitude."""
    warm, cold = chain["warm"], chain["cold"]

    # the chain actually ran end to end — an empty book is not a passing book
    assert warm["settled_records"] == chain["expected_records"], (
        f"settlement did not settle the whole window: {warm['settled_records']} "
        f"records, expected {chain['expected_records']}"
    )
    assert cold["settled_kwh"] > 0, "no volume reached the book at all"

    # link 1 — weather reached demand
    assert cold["daily_kwh"] > warm["daily_kwh"], (
        "JOIN CUT (weather → premise demand): a "
        f"{warm['national_temp_c'] - cold['national_temp_c']:.1f}C colder day produced "
        f"no more demand ({cold['daily_kwh']:.4f} vs {warm['daily_kwh']:.4f} kWh)"
    )

    # link 2 — demand reached settlement
    delta_kwh = cold["settled_kwh"] - warm["settled_kwh"]
    assert delta_kwh > 0, (
        "JOIN CUT (premise demand → settlement): extra demand did not reach settled volume "
        f"({cold['settled_kwh']:.4f} vs {warm['settled_kwh']:.4f} kWh)"
    )

    # link 3 — settled volume reached the book, at the right MAGNITUDE, not merely
    # in the right direction. This is the assertion a "it ran and returned a
    # number" test would miss.
    delta_cost = cold["wholesale_cost_gbp"] - warm["wholesale_cost_gbp"]
    expected_delta_cost = delta_kwh / 1000.0 * chain["price_gbp_per_mwh"]
    assert abs(delta_cost - expected_delta_cost) < 1e-9, (
        "JOIN CUT (settlement → book): the wholesale cost moved by "
        f"GBP{delta_cost:.6f} but the settled volume change implies "
        f"GBP{expected_delta_cost:.6f}"
    )


# ══════════════════════════════════════════════════════════════════════════════
# CHAIN 3 — the money chain: meter read → bill → payment → arrear → recovery
# ══════════════════════════════════════════════════════════════════════════════

def run_money_chain(
    *,
    customer_id: str = "JOIN-MONEY-1",
    period_end: str = "2023-02-28",
    true_consumption_kwh: float = 900.0,
    trailing_actuals_kwh: tuple[float, ...] = (300.0, 320.0, 310.0),
    unit_rate_gbp_per_mwh: float = 140.0,
    price_gbp_per_mwh: float = 60.0,
    stress: str = "severe",
    method: str = "direct_debit",
) -> dict:
    """Drive meter read → bill → payment → arrears → recovery/write-off.

    The customer's true consumption is deliberately far above their trailing
    actuals, so an ESTIMATED read (which can only see the trailing actuals — the
    company side of the wall) under-reads badly. That gap is what has to survive
    all the way to the bill.
    """
    if not true_consumption_kwh > max(trailing_actuals_kwh) * 1.5:
        raise AssertionError(
            "driver premise violated: true consumption must dominate the trailing actuals, "
            "otherwise an estimated read and an actual read produce indistinguishable bills"
        )

    # link 1 — the meter read. Both branches of the REAL arrival model, so the
    # chain is exercised on the estimate path the company actually bills from.
    forced_actual = meter_reads.simulate_read(
        customer_id, period_end, "smart", true_consumption_kwh,
        list(trailing_actuals_kwh), 0,
    )
    estimated = meter_reads.simulate_read(
        customer_id, period_end, "traditional", true_consumption_kwh,
        list(trailing_actuals_kwh),
        meter_reads.MAX_CONSECUTIVE_ESTIMATED_PERIODS - 1,
    )

    def _billed_kwh(event) -> float:
        if event.status == "actual":
            return event.true_consumption_kwh
        return event.estimated_consumption_kwh

    # link 2 — read → bill. One settlement record per period carrying the READ
    # volume (what the company can see), priced at the contracted rate.
    def _bill(event) -> dict:
        kwh = _billed_kwh(event)
        per_period = kwh / PERIODS
        records = [
            {
                "customer_id": customer_id,
                "settlement_date": period_end,
                "settlement_period": p,
                "consumption_kwh": per_period,
                "revenue_gbp": per_period / 1000.0 * unit_rate_gbp_per_mwh,
                "wholesale_cost_gbp": per_period / 1000.0 * price_gbp_per_mwh,
            }
            for p in range(1, PERIODS + 1)
        ]
        return bill_generator.generate_bill(customer_id, records, "fixed")

    actual_bill = _bill(forced_actual)
    estimated_bill = _bill(estimated)

    # link 3 — bill → payment. A seeded RNG so the chain is deterministic; the
    # OUTCOME still comes from the real production model, not from the fixture.
    rng = random.Random(20260808)
    outcome, days_late = arrears_engine.payment_outcome(method, stress, rng)

    # link 4 — payment → arrears. The arrears case is opened for the BILL's own
    # amount: the number that has to survive the whole chain.
    arrears_gbp = round(estimated_bill["total_amount_gbp"], 2)
    due = date.fromisoformat(period_end) + timedelta(days=14)
    stages = arrears_engine.arrears_stages(
        arrears_gbp, due, eventually_resolved=False,
        archetype="PERSISTENT", method=method,
    )

    # link 5 — arrears → recovery / write-off
    recovered_gbp = arrears_engine.dca_recovered_amount(arrears_gbp, "PERSISTENT")

    return {
        "actual_event": forced_actual,
        "estimated_event": estimated,
        "true_consumption_kwh": true_consumption_kwh,
        "actual_billed_kwh": _billed_kwh(forced_actual),
        "estimated_billed_kwh": _billed_kwh(estimated),
        "actual_bill": actual_bill,
        "estimated_bill": estimated_bill,
        "payment_outcome": outcome,
        "days_late": days_late,
        "arrears_gbp": arrears_gbp,
        "stages": stages,
        "recovered_gbp": recovered_gbp,
        "method": method,
    }


def assert_money_join(chain: dict) -> None:
    """The read's error must reach the bill; the bill's amount must reach the
    arrears case; the case must resolve to a write-off that reconciles."""
    # link 1 — the two read paths genuinely diverge (the estimate is a belief,
    # the actual is the truth). If they don't, the wall isn't being crossed.
    assert chain["actual_event"].status == "actual", (
        "JOIN CUT (meter read): the communicating-smart path did not produce an actual read"
    )
    assert chain["estimated_event"].status == "estimated", (
        "JOIN CUT (meter read): the traditional path did not produce an estimated read"
    )
    assert chain["estimated_billed_kwh"] < chain["true_consumption_kwh"], (
        "JOIN CUT (meter read): the estimate did not under-read the truth "
        f"({chain['estimated_billed_kwh']} vs {chain['true_consumption_kwh']} kWh)"
    )

    # link 2 — the read error arrived at the bill
    est_total = chain["estimated_bill"]["total_amount_gbp"]
    act_total = chain["actual_bill"]["total_amount_gbp"]
    assert est_total < act_total, (
        "JOIN CUT (read → bill): an under-reading estimate did not produce a smaller bill "
        f"(estimated GBP{est_total:.2f} vs actual GBP{act_total:.2f})"
    )
    assert chain["estimated_bill"]["total_consumption_kwh"] == chain["estimated_billed_kwh"], (
        "JOIN CUT (read → bill): the bill's consumption is not the volume that was read"
    )

    # link 3 — the payment decision is a real outcome, not a default
    assert chain["payment_outcome"] in {"success", "failed", "dispute"}, (
        f"JOIN CUT (bill → payment): unrecognised outcome {chain['payment_outcome']!r}"
    )

    # link 4 — the bill's amount arrived at the arrears case
    assert chain["arrears_gbp"] == round(est_total, 2), (
        "JOIN CUT (bill → arrears): the arrears case does not carry the bill's amount "
        f"(GBP{chain['arrears_gbp']:.2f} vs GBP{est_total:.2f})"
    )
    notes = " ".join(s["note"] for s in chain["stages"])
    assert ("%.2f" % chain["arrears_gbp"]) in notes, (
        "JOIN CUT (bill → arrears): the arrears correspondence never states the amount owed"
    )
    stage_names = [s["stage"] for s in chain["stages"]]
    assert "WRITTEN_OFF" in stage_names, (
        f"JOIN CUT (arrears → write-off): an unresolved case never wrote off — {stage_names}"
    )

    # link 5 — recovery reconciles against the written-off amount. Money cannot
    # be recovered that was never owed.
    assert 0.0 <= chain["recovered_gbp"] <= chain["arrears_gbp"], (
        "JOIN CUT (write-off → recovery): recovered GBP"
        f"{chain['recovered_gbp']:.2f} is not within the GBP{chain['arrears_gbp']:.2f} owed"
    )


# ══════════════════════════════════════════════════════════════════════════════
# CHAIN 4 — the market chain: price → hedge → settlement → P&L
# ══════════════════════════════════════════════════════════════════════════════

def run_market_chain(
    *,
    base_price: float = 55.0,
    calm_swing_ratio: float = 1.10,
    volatile_swing_ratio: float = 1.16,
    spike_price: float = 400.0,
    eac_kwh: float = 4000.0,
    unit_rate_gbp_per_mwh: float = 90.0,
    fwd_price_gbp_per_mwh: float = 60.0,
    term_days: int = 180,
    history_days: int = 120,
    start: str = "2022-08-01",
) -> dict:
    """Drive price → hedge decision → hedged settlement → P&L.

    Two price histories (calmer and more volatile) reach the SAME real hedge
    decision function; the resulting hedge fractions are then settled against the
    SAME spiking spot prices, so the only difference downstream is the hedge the
    price history bought.

    Fixture calibration matters here and is not arbitrary. `decide_hedge_fraction`
    clamps to `COMPANY_MIN_HEDGE_FLOOR` whenever the VaR constraint does not bind,
    so a *flat* calm history and a wild one both return the floor — a comparison
    that would pass vacuously in one direction and be unfalsifiable in the other.
    Both legs are therefore placed inside the range where the constraint actually
    binds (a term long enough that `vol_term` exceeds
    `unit_rate / (fwd_price × z95)`), which is what makes the hedge fraction a
    live function of the price history rather than a constant.
    """
    if not volatile_swing_ratio > calm_swing_ratio > 1.0:
        raise AssertionError(
            "driver premise violated: the volatile history must swing harder than the calm "
            f"one and both must swing ({calm_swing_ratio} / {volatile_swing_ratio})"
        )

    def _history(swing_ratio: float) -> list[dict]:
        return [
            {
                "settlementDate": d,
                "settlementPeriod": 1,
                "systemSellPrice": base_price * (swing_ratio if i % 2 else 1.0),
            }
            for i, d in enumerate(_dates(start, history_days))
        ]

    calm_history = _history(calm_swing_ratio)
    volatile_history = _history(volatile_swing_ratio)
    calm_vol = hedge_decision.estimate_price_volatility(calm_history)
    volatile_vol = hedge_decision.estimate_price_volatility(volatile_history)
    if not volatile_vol > calm_vol:
        raise AssertionError(
            "driver premise violated: the volatile history must be measurably more volatile "
            f"than the calm one (vol {volatile_vol:.6f} vs {calm_vol:.6f})"
        )

    # link 1 — price history → hedge decision
    calm_hf = hedge_decision.decide_hedge_fraction(
        eac_kwh, fwd_price_gbp_per_mwh, unit_rate_gbp_per_mwh, calm_history, term_days
    )
    volatile_hf = hedge_decision.decide_hedge_fraction(
        eac_kwh, fwd_price_gbp_per_mwh, unit_rate_gbp_per_mwh, volatile_history, term_days
    )
    # VACUITY GUARD: if either leg has clamped to the policy floor the VaR
    # constraint is not binding, and the hedge fraction has stopped being a
    # function of the price history at all — the comparison downstream would then
    # be comparing two constants. Raise here rather than hand back a result whose
    # assertion could only ever pass or only ever fail.
    floor = hedge_policy.COMPANY_MIN_HEDGE_FLOOR
    if calm_hf <= floor or volatile_hf <= floor:
        raise AssertionError(
            "driver premise violated: a hedge fraction clamped to the policy floor "
            f"({floor}) — calm={calm_hf:.6f} volatile={volatile_hf:.6f}; the VaR "
            "constraint is not binding, so the price→hedge link cannot be observed"
        )

    # link 2+3 — hedge fraction → settlement → P&L, both settled against the
    # same spike so the hedge is the only live variable.
    term_dates = _dates(start, term_days)
    spike_prices = _price_records(term_dates, spike_price)
    daily_kwh = eac_kwh / 365.0
    shape = [daily_kwh / PERIODS] * PERIODS

    def _settle(hedge_fraction: float) -> dict:
        from simulation import hedged_settlement

        records = hedged_settlement.run_hedged_term(
            "JOIN-MARKET-1",
            term_dates[0],
            term_dates[-1],
            unit_rate_gbp_per_mwh,
            fwd_price_gbp_per_mwh,
            hedge_fraction,
            0.0,
            lambda _d: shape,
            spike_prices,
        )
        return {
            "hedge_fraction": hedge_fraction,
            "records": len(records),
            "wholesale_cost_gbp": sum(r["wholesale_cost_gbp"] for r in records),
            "margin_gbp": sum(r["margin_gbp"] for r in records),
            "net_margin_gbp": sum(r["net_margin_gbp"] for r in records),
            "hedged_kwh": sum(r["hedged_volume_kwh"] for r in records),
            "unhedged_kwh": sum(r["unhedged_volume_kwh"] for r in records),
        }

    return {
        "calm_volatility": calm_vol,
        "volatile_volatility": volatile_vol,
        "calm_hedge_fraction": calm_hf,
        "volatile_hedge_fraction": volatile_hf,
        "spike_price": spike_price,
        "fwd_price_gbp_per_mwh": fwd_price_gbp_per_mwh,
        "settled_at_calm_hf": _settle(calm_hf),
        "settled_at_volatile_hf": _settle(volatile_hf),
        "settled_unhedged": _settle(0.0),
        "settled_fully_hedged": _settle(1.0),
    }


def assert_market_join(chain: dict) -> None:
    """A price move alone must change the hedge decision, and that hedge must
    change the P&L when the spike arrives."""
    # link 1 — the price history reached the hedge decision
    assert chain["volatile_hedge_fraction"] > chain["calm_hedge_fraction"], (
        "JOIN CUT (price → hedge): a measurably more volatile price history bought no more "
        f"hedge (volatile hf {chain['volatile_hedge_fraction']:.6f} vs calm hf "
        f"{chain['calm_hedge_fraction']:.6f})"
    )

    # the chain actually settled
    unhedged = chain["settled_unhedged"]
    fully = chain["settled_fully_hedged"]
    assert unhedged["records"] > 0 and fully["records"] > 0, "nothing settled at all"

    # link 2 — the hedge fraction reached the settled volumes
    assert unhedged["hedged_kwh"] == 0.0 and unhedged["unhedged_kwh"] > 0, (
        "JOIN CUT (hedge → settlement): a zero hedge fraction still settled hedged volume"
    )
    assert fully["unhedged_kwh"] == 0.0 and fully["hedged_kwh"] > 0, (
        "JOIN CUT (hedge → settlement): a full hedge fraction still settled unhedged volume"
    )

    # link 3 — the hedge reached the P&L. With spot spiking far above the
    # forward, being hedged must cost strictly less.
    assert chain["spike_price"] > chain["fwd_price_gbp_per_mwh"], (
        "driver premise violated: the spike must exceed the forward price"
    )
    assert fully["wholesale_cost_gbp"] < unhedged["wholesale_cost_gbp"], (
        "JOIN CUT (settlement → P&L): the spike cost a fully-hedged book "
        f"GBP{fully['wholesale_cost_gbp']:.2f}, no less than an unhedged "
        f"GBP{unhedged['wholesale_cost_gbp']:.2f}"
    )
    assert fully["net_margin_gbp"] > unhedged["net_margin_gbp"], (
        "JOIN CUT (settlement → P&L): the hedge did not reach the reported result "
        f"(hedged GBP{fully['net_margin_gbp']:.2f} vs unhedged "
        f"GBP{unhedged['net_margin_gbp']:.2f})"
    )

    # and the decision the PRICE bought is worth more than the one it didn't
    assert (
        chain["settled_at_volatile_hf"]["net_margin_gbp"]
        > chain["settled_at_calm_hf"]["net_margin_gbp"]
    ), (
        "JOIN CUT (price → hedge → P&L): the hedge the volatile history bought was worth "
        "nothing when the spike actually arrived"
    )


# ══════════════════════════════════════════════════════════════════════════════
# CHAIN 5 — the customer lifecycle: join → bill → serve → leave
# ══════════════════════════════════════════════════════════════════════════════

def run_lifecycle_chain(
    *,
    window_start: str = "2023-03-01",
    window_days: int = 40,
    join_offset_days: int = 10,
    leave_offset_days: int = 30,
    unit_rate_gbp_per_mwh: float = 140.0,
    price_gbp_per_mwh: float = 60.0,
    daily_kwh: float = 9.6,
) -> dict:
    """Drive join → bill → serve → leave through the REAL contract-window logic
    in `settlement.run_settlement`, then carry the departing customer's unpaid
    balance out of the relationship.
    """
    if not 0 < join_offset_days < leave_offset_days < window_days:
        raise AssertionError(
            "driver premise violated: the customer must join AFTER the window opens and "
            "leave BEFORE it closes, or the window bounds are never actually tested"
        )

    dates = _dates(window_start, window_days)
    prices = _price_records(dates, price_gbp_per_mwh)
    shape = [daily_kwh / PERIODS] * PERIODS

    join_date = dates[join_offset_days]
    leave_date = dates[leave_offset_days]

    # link 1 — join: the acquisition date bounds settlement's start
    joiner = {
        "customer_id": "JOIN-LIFECYCLE-1",
        "acquisition_date": join_date,
        "unit_rate_gbp_per_mwh": unit_rate_gbp_per_mwh,
    }
    served = settlement.run_settlement(
        [joiner], window_start, dates[-1], lambda _d: shape, prices
    )

    # link 2 — leave: served only up to the departure date. Settlement's own
    # contract window is a 365-day term, so a mid-window departure is applied
    # here the way the company applies it — by ending the served period.
    served_to_departure = [r for r in served if r["settlement_date"] < leave_date]
    settled_dates = sorted({r["settlement_date"] for r in served})

    # link 3 — serve → bill
    bill = bill_generator.generate_bill(
        joiner["customer_id"], served_to_departure, "fixed"
    ) if served_to_departure else None

    # link 4 — leave with debt: the closing balance does not vanish with the
    # relationship, it becomes an arrears case dated from departure.
    closing_balance_gbp = round(bill["total_amount_gbp"], 2) if bill else 0.0
    final_stages = arrears_engine.arrears_stages(
        closing_balance_gbp,
        date.fromisoformat(leave_date) + timedelta(days=14),
        eventually_resolved=False,
        archetype="NEUTRAL",
        method="direct_debit",
    )

    return {
        "window_dates": dates,
        "join_date": join_date,
        "leave_date": leave_date,
        "settled_dates": settled_dates,
        "served_records": len(served),
        "served_to_departure_records": len(served_to_departure),
        "bill": bill,
        "closing_balance_gbp": closing_balance_gbp,
        "final_stages": final_stages,
        "expected_served_days": window_days - join_offset_days,
        "expected_days_to_departure": leave_offset_days - join_offset_days,
    }


def assert_lifecycle_join(chain: dict) -> None:
    """Arrival and departure must bound the relationship exactly, and debt must
    survive the departure."""
    assert chain["served_records"] > 0, "the customer was never served at all"

    # link 1 — the join date reached settlement: nothing before acquisition
    assert min(chain["settled_dates"]) == chain["join_date"], (
        "JOIN CUT (join → settlement): settlement began "
        f"{min(chain['settled_dates'])}, not at the acquisition date {chain['join_date']}"
    )
    assert chain["window_dates"][0] < chain["join_date"], (
        "driver premise violated: the window must open before the customer joins"
    )
    assert len(chain["settled_dates"]) == chain["expected_served_days"], (
        "JOIN CUT (join → settlement): served "
        f"{len(chain['settled_dates'])} days, expected {chain['expected_served_days']}"
    )

    # link 2 — the leave date reached the served period
    assert max(d for d in chain["settled_dates"] if d < chain["leave_date"]) < chain["leave_date"]
    served_days_to_departure = chain["served_to_departure_records"] / PERIODS
    assert served_days_to_departure == chain["expected_days_to_departure"], (
        "JOIN CUT (leave → settlement): served "
        f"{served_days_to_departure} days to departure, expected "
        f"{chain['expected_days_to_departure']}"
    )

    # link 3 — the served period reached the bill
    assert chain["bill"] is not None, "JOIN CUT (serve → bill): no bill was produced"
    assert chain["bill"]["total_amount_gbp"] > 0, (
        "JOIN CUT (serve → bill): a served customer was billed nothing"
    )

    # link 4 — the debt survived the departure
    assert chain["closing_balance_gbp"] > 0, (
        "JOIN CUT (leave → debt): the closing balance vanished with the relationship"
    )
    stage_names = [s["stage"] for s in chain["final_stages"]]
    assert "WRITTEN_OFF" in stage_names, (
        f"JOIN CUT (leave → debt): departure debt never reached a resolution — {stage_names}"
    )
    notes = " ".join(s["note"] for s in chain["final_stages"])
    assert ("%.2f" % chain["closing_balance_gbp"]) in notes, (
        "JOIN CUT (leave → debt): the closing arrears case does not carry the closing balance"
    )
