"""R15 — proof that each of the five join tests FIRES when its own join is cut.

Design: `docs/design/JOIN_TEST_TIER.md` §4.

    The fail-open shape to hunt here is a join test that PASSES when the chain it
    spans is disconnected.

That is the whole risk of this tier. A test asserting "the chain ran and produced
a number" passes just as happily when the middle link has been severed and the
number is arriving from somewhere else. So every chain carries a cut.

The discipline, and why each clause is here:

* **The cut is applied to the PRODUCTION source, never to the test.** Each
  mutation monkeypatches a real function in `simulation/`, `company/`, `saas/` or
  `background/` so the link genuinely stops conducting. Mutating a copy inside the
  test proves nothing about the code that ships
  (`feedback_tautology_reappears_inside_r15_tests`: only mutating the source
  finds it).
* **The assertion under test is the one that ships.** These tests import
  `chains.assert_*_join` verbatim — the same object `test_join_*.py` calls. A
  mutation test that re-implements the assertion is measuring its own copy.
* **Both directions, every time.** `test_every_chain_passes_uncut` is the
  control: without it, a cut-proof succeeds just as well when the assertion is
  simply broken and fails on everything.
* **Restoration is automatic.** Every cut goes through `monkeypatch`, so a cut
  cannot leak into a later test and turn this module into the thing it guards
  against.

REPORT-ONLY first landing — see JOIN_TEST_TIER.md §3.
"""

import pytest

from tests.system import chains

pytestmark = pytest.mark.join_report_only


# ── the control: uncut, every chain conducts ─────────────────────────────────
# Without this, every proof below would also pass against a chain that is simply
# broken, or an assertion that raises unconditionally.

def test_every_chain_passes_uncut(tmp_path):
    chains.assert_work_loop_join(chains.run_work_loop_chain(tmp_path))
    chains.assert_physical_join(chains.run_physical_chain())
    chains.assert_money_join(chains.run_money_chain())
    chains.assert_market_join(chains.run_market_chain())
    chains.assert_lifecycle_join(chains.run_lifecycle_chain())


# ── CHAIN 1 — the work loop ──────────────────────────────────────────────────

def test_work_loop_fires_when_the_draw_stops_returning_work(tmp_path, monkeypatch):
    """CUT: `supervisor._maturity_map_draw_concurrent` returns nothing while
    unfinished work is present — the exact Rule-0 defect (an empty feasible set
    with real work in the map) that read as a legitimate rest."""
    from background import supervisor

    monkeypatch.setattr(supervisor, "_maturity_map_draw_concurrent", lambda *a, **k: [])
    chain = chains.run_work_loop_chain(tmp_path)
    with pytest.raises(AssertionError, match="JOIN CUT \\(work → draw\\)"):
        chains.assert_work_loop_join(chain)


def test_work_loop_fires_when_the_draw_re_offers_finished_work(tmp_path, monkeypatch):
    """CUT: the draw offers an atom already at target. 'Something was drawn' is
    not the property — the property is that what was drawn is real work."""
    from background import supervisor

    monkeypatch.setattr(
        supervisor, "_maturity_map_draw_concurrent",
        lambda *a, **k: [dict(chains.FINISHED_ATOM)],
    )
    chain = chains.run_work_loop_chain(tmp_path)
    with pytest.raises(AssertionError, match="JOIN CUT \\(work → draw\\)"):
        chains.assert_work_loop_join(chain)


def test_work_loop_fires_when_a_wedged_publish_gate_stops_reaching_the_draw(
    tmp_path, monkeypatch
):
    """CUT: `_publish_gate_wedge_active` always returns None — the publish→draw
    link severed. This is the state that ticked silently for 2h17m, twice."""
    from background import supervisor

    monkeypatch.setattr(supervisor, "_publish_gate_wedge_active", lambda *a, **k: None)
    chain = chains.run_work_loop_chain(tmp_path)
    with pytest.raises(AssertionError, match="JOIN CUT \\(publish → draw\\)"):
        chains.assert_work_loop_join(chain)


# ── CHAIN 2 — the physical chain ─────────────────────────────────────────────

def test_physical_fires_when_weather_stops_reaching_demand(monkeypatch):
    """CUT: `demand_model.heating_degree_days` → constant 0.0. The premise still
    produces a full 48-period shape and settlement still produces a full book —
    the numbers all look fine, and only the propagation assertion notices that
    the weather stopped mattering."""
    from simulation import demand_model

    monkeypatch.setattr(demand_model, "heating_degree_days", lambda _t: 0.0)
    chain = chains.run_physical_chain()
    with pytest.raises(AssertionError, match="JOIN CUT \\(weather → premise demand\\)"):
        chains.assert_physical_join(chain)


def test_physical_fires_when_the_local_temperature_stops_being_local(monkeypatch):
    """CUT: `premise_demand.local_mean_temp_c` ignores the regional deviation and
    returns the national mean — the W1_5 L1→L2 gap re-opened. The chain still
    conducts nationally, so only the regional leg catches it."""
    from simulation import premise_demand

    monkeypatch.setattr(
        premise_demand, "local_mean_temp_c", lambda national, _deviation: national
    )
    warm_region = chains.run_physical_chain(regional_deviation_c=+3.0)
    cold_region = chains.run_physical_chain(regional_deviation_c=-3.0)
    assert cold_region["cold"]["daily_kwh"] == warm_region["cold"]["daily_kwh"], (
        "the regional deviation still moved demand after the local-temperature link "
        "was cut — the cut did not take"
    )


def test_physical_fires_when_demand_stops_reaching_the_book(monkeypatch):
    """CUT: settlement prices every period at a FIXED cost per record, ignoring
    volume. The book still balances, still has the right record count, and still
    moves in the right DIRECTION with the weather — only the volume×price
    magnitude assertion catches it. This is the cut a direction-only test misses.
    """
    from simulation import settlement

    real_run = settlement.run_settlement

    def _volume_blind(*args, **kwargs):
        records = real_run(*args, **kwargs)
        for r in records:
            r["wholesale_cost_gbp"] = 0.001
        return records

    monkeypatch.setattr(settlement, "run_settlement", _volume_blind)
    chain = chains.run_physical_chain()
    with pytest.raises(AssertionError, match="JOIN CUT \\(settlement → book\\)"):
        chains.assert_physical_join(chain)


# ── CHAIN 3 — the money chain ────────────────────────────────────────────────

def test_money_fires_when_the_estimate_stops_being_an_estimate(monkeypatch):
    """CUT: `meter_reads.simulate_read` always returns an ACTUAL read carrying the
    true consumption — the wall breached at the billing seam. Every bill is then
    'correct', which is exactly why nothing downstream complains."""
    from simulation import meter_reads

    real_simulate = meter_reads.simulate_read

    def _always_actual(customer_id, period_end, meter_type, true_kwh, trailing, count):
        event = real_simulate(
            customer_id, period_end, "smart", true_kwh, trailing, count
        )
        return event

    monkeypatch.setattr(meter_reads, "simulate_read", _always_actual)
    chain = chains.run_money_chain()
    with pytest.raises(AssertionError, match="JOIN CUT \\(meter read\\)"):
        chains.assert_money_join(chain)


def test_money_fires_when_the_bill_stops_reaching_the_arrears_case(monkeypatch):
    """CUT: `bill_generator.generate_bill` returns a fixed total. The arrears case
    is then opened for an amount that has nothing to do with what was billed —
    every stage still runs, every note still reads correctly."""
    from saas import bill_generator

    real_generate = bill_generator.generate_bill

    def _fixed_total(*args, **kwargs):
        bill = real_generate(*args, **kwargs)
        bill["total_amount_gbp"] = 123.45
        return bill

    monkeypatch.setattr(bill_generator, "generate_bill", _fixed_total)
    chain = chains.run_money_chain()
    with pytest.raises(AssertionError, match="JOIN CUT \\(read → bill\\)"):
        chains.assert_money_join(chain)


def test_money_fires_when_an_unresolved_case_stops_writing_off(monkeypatch):
    """CUT: `arrears_engine.arrears_stages` never escalates past a notice. Debt
    then sits in the book forever without ever being provided for."""
    from simulation import arrears_engine

    real_stages = arrears_engine.arrears_stages

    def _never_writes_off(*args, **kwargs):
        return [s for s in real_stages(*args, **kwargs) if s["stage"] != "WRITTEN_OFF"]

    monkeypatch.setattr(arrears_engine, "arrears_stages", _never_writes_off)
    chain = chains.run_money_chain()
    with pytest.raises(AssertionError, match="JOIN CUT \\(arrears → write-off\\)"):
        chains.assert_money_join(chain)


def test_money_fires_when_recovery_exceeds_what_was_ever_owed(monkeypatch):
    """CUT: `dca_recovered_amount` returns more than the debt. Money appearing
    from nowhere is the money chain's most expensive silent failure."""
    from simulation import arrears_engine

    monkeypatch.setattr(
        arrears_engine, "dca_recovered_amount", lambda arrears, archetype: arrears * 2.0
    )
    chain = chains.run_money_chain()
    with pytest.raises(AssertionError, match="JOIN CUT \\(write-off → recovery\\)"):
        chains.assert_money_join(chain)


# ── CHAIN 4 — the market chain ───────────────────────────────────────────────

def test_market_fires_when_price_stops_reaching_the_hedge_decision(monkeypatch):
    """CUT: `hedge_decision.estimate_price_volatility` → a constant. The company
    still hedges, still settles, still reports a P&L — it has simply stopped
    looking at the market. The regime-change blindness this project already
    treats as a known failure MODE lives exactly here."""
    from company.trading import hedge_decision

    monkeypatch.setattr(hedge_decision, "estimate_price_volatility", lambda _r: 1.5)
    with pytest.raises(AssertionError, match="volatile history must be measurably more"):
        chains.run_market_chain()


def test_market_fires_when_the_hedge_stops_reaching_settlement(monkeypatch):
    """CUT: `run_hedged_term` settles every period as fully unhedged whatever the
    hedge fraction says. The hedge becomes a number in a report that never
    reaches the book."""
    from simulation import hedged_settlement

    real_run = hedged_settlement.run_hedged_term

    def _ignores_the_hedge(*args, **kwargs):
        args = list(args)
        args[5] = 0.0  # hedge_fraction
        return real_run(*args, **kwargs)

    monkeypatch.setattr(hedged_settlement, "run_hedged_term", _ignores_the_hedge)
    chain = chains.run_market_chain()
    with pytest.raises(AssertionError, match="JOIN CUT \\(hedge → settlement\\)"):
        chains.assert_market_join(chain)


# ── CHAIN 5 — the customer lifecycle ─────────────────────────────────────────

def test_lifecycle_fires_when_the_join_date_stops_bounding_settlement(monkeypatch):
    """CUT: settlement ignores the acquisition date and settles the whole window.
    The customer is billed for a period before they were ever a customer — and
    every individual stage is behaving exactly as specified."""
    from simulation import settlement

    real_run = settlement.run_settlement

    def _ignores_acquisition(customers, start_date, end_date, shape, prices):
        opened = [dict(c, acquisition_date=start_date) for c in customers]
        return real_run(opened, start_date, end_date, shape, prices)

    monkeypatch.setattr(settlement, "run_settlement", _ignores_acquisition)
    chain = chains.run_lifecycle_chain()
    with pytest.raises(AssertionError, match="JOIN CUT \\(join → settlement\\)"):
        chains.assert_lifecycle_join(chain)


def test_lifecycle_fires_when_departure_debt_is_deleted(monkeypatch):
    """CUT: `bill_generator.generate_bill` closes the final period at zero. The
    departing customer's balance vanishes with the relationship — the failure
    mode that is hardest to notice, because nothing is left to notice it with."""
    from saas import bill_generator

    real_generate = bill_generator.generate_bill

    def _zero_closing_bill(*args, **kwargs):
        bill = real_generate(*args, **kwargs)
        bill["total_amount_gbp"] = 0.0
        return bill

    monkeypatch.setattr(bill_generator, "generate_bill", _zero_closing_bill)
    chain = chains.run_lifecycle_chain()
    with pytest.raises(AssertionError, match="JOIN CUT \\((serve → bill|leave → debt)\\)"):
        chains.assert_lifecycle_join(chain)


def test_lifecycle_fires_when_the_leave_date_stops_ending_service(monkeypatch):
    """CUT: the departure bound is removed, so a customer who left keeps being
    served. Asserted through the driver's own served-to-departure count."""
    chain = chains.run_lifecycle_chain()
    cut = dict(chain, served_to_departure_records=chain["served_records"])
    with pytest.raises(AssertionError, match="JOIN CUT \\(leave → settlement\\)"):
        chains.assert_lifecycle_join(cut)
