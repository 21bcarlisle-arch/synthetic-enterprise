"""MC-2 collateral death-test — the run_phase2b WIRING (2026-07-27).

Tests `simulation.run_phase2b._mc2_collateral_death_test`, the helper that runs the MC-2
breaking-strain sweep against a real 2021-22 replay in the live run loop
(DIRECTOR_RULING_MC2_REAL_HISTORY_NOT_DIFFICULTY §2). The sweep MECHANISM itself is tested in
tests/company/risk/test_collateral_death_test.py; this file proves the WIRING — stressed-date
selection anchored to real history, calm-origination vs stressed marking of one fixed book, the
price fan, exposure formation, and the surfaced summary shape.

R15 both-ways (mutations named per test): the teeth test reds if the stressed date is moved off
the real 2021-22 window, and reds if origination is marked at the stressed price (killing the
price MOVE that produces the death). R12 guard is respected — the stressed date is real history,
never chosen to force a death; a pure long book that cannot die is reported as the §4 diagnosis,
not tuned into a death.
"""
from company.trading.forward_book import ForwardContract, TradingBook
from simulation.run_phase2b import _mc2_collateral_death_test


def _book(*contracts):
    b = TradingBook()
    for c in contracts:
        b.open_hedge(c)
    return b


def _fwd(customer_id, counterparty_id, agreed, notional):
    # A forward calendar-live across the 2021-22 crisis window.
    return ForwardContract(
        customer_id=customer_id,
        term_start="2021-01-01",
        term_end="2022-12-31",
        notional_mwh=notional,
        agreed_price_gbp_per_mwh=agreed,
        hedge_fraction=1.0,
        counterparty_id=counterparty_id,
    )


def _price_at(calm=50.0, spike=200.0):
    """Point-in-time forward resolver stub: calm at the origination (2021-01-01) mark,
    spiked at the stressed (2021-12-31) mark — a real gas-crisis shape."""
    def resolve(fuel, date):
        return calm if date == "2021-01-01" else spike
    return resolve


CBY = {"L": "electricity", "S": "electricity"}


def test_teeth_death_by_collateral_while_solvent():
    """A big long name + a moderate SHORT name, both struck at the calm origination price.
    On the spike the long book is deep ITM (P&L survives) while the short leg's variation
    margin overruns the origination-sized facility -> death-by-collateral while solvent: the
    exact 2021-22 shape MC-2 targets. MUTATION: revert stressed-date selection to effective_end
    (a near-empty end-of-run book) and this death vanishes -> test reds."""
    book = _book(_fwd("L", "CP_L", 50.0, 5000.0), _fwd("S", "CP_S", 50.0, -2000.0))
    r = _mc2_collateral_death_test(book, CBY, _price_at(), "2023-01-01")

    assert r is not None
    assert r["stressed_date"] == "2021-12-31"      # real crisis anchor, not effective_end
    assert r["origination_date"] == "2021-01-01"   # earliest live term_start (near-strike baseline)
    assert r["survived"] is False
    assert r["death_dose"] == 1.0                   # survives 0.8x, dies at the REAL 1.0x replay
    assert r["death_cause"] == "collateral_while_solvent"
    assert r["death_while_pnl_survives"] is True
    assert r["any_name_posted_margin"] is True
    # facility book-derived at origination (§3): near-strike origination -> gross ~0 -> the floor.
    assert r["facility_gbp"] == 250_000.0
    assert r["liquidity_headroom_min_gbp"] < 0.0   # liquidity goes negative under the sweep
    # 0.8x survives, 1.0x kills: the breaking strain is between them.
    d08 = next(d for d in r["doses"] if d["dose"] == 0.8)
    d10 = next(d for d in r["doses"] if d["dose"] == 1.0)
    assert d08["is_dead_by_collateral"] is False
    assert d10["is_dead_by_collateral"] is True
    assert d10["book_pnl_gbp"] > 0.0               # solvent on paper at the killing dose


def test_origination_marked_at_stress_removes_the_death():
    """MUTATION of the wiring's load-bearing choice: mark origination at the STRESSED price too
    (no price move). The facility then scales up with the already-large stressed book (§3 is fed
    a big origination), the margin call is flat across doses, and the company SURVIVES. This is
    why the calm-origination mark is load-bearing — a same-price origination cannot produce the
    death, so a mutation that drops the price move reds the teeth test above."""
    book = _book(_fwd("L", "CP_L", 50.0, 5000.0), _fwd("S", "CP_S", 50.0, -2000.0))
    # calm == spike -> origination_exposure == stressed_exposure -> no price move.
    r = _mc2_collateral_death_test(book, CBY, _price_at(calm=200.0, spike=200.0), "2023-01-01")
    assert r is not None
    assert r["survived"] is True
    assert r["facility_gbp"] > 250_000.0           # facility scaled to the large (stressed) book


def test_pure_long_book_cannot_die_reports_diagnosis_not_a_death():
    """§4/R12: a pure long book goes ITM on a spike and posts NO variation margin, so it CANNOT
    die to collateral. That is the honest 'hedge cover masking exposure' diagnosis to REPORT —
    never a cue to shrink the facility to force a death."""
    book = _book(_fwd("L", "CP_L", 50.0, 5000.0))
    r = _mc2_collateral_death_test(book, {"L": "electricity"}, _price_at(), "2023-01-01")
    assert r is not None
    assert r["survived"] is True
    assert r["any_name_posted_margin"] is False    # the §4 diagnosis signal
    assert r["death_while_pnl_survives"] is False
    assert r["peak_margin_call_gbp"] == 0.0


def test_short_run_before_2021_returns_none():
    """A run that never reaches the real 2021-22 stress window yields no death-test (not a
    fabricated one). R12: we do not manufacture a stress the run never saw."""
    book = _book(_fwd("L", "CP_L", 50.0, 5000.0), _fwd("S", "CP_S", 50.0, -2000.0))
    assert _mc2_collateral_death_test(book, CBY, _price_at(), "2020-01-01") is None


def test_no_live_contracts_as_of_stress_returns_none():
    """No positions calendar-live during the stress -> nothing to test -> None (not an empty
    fabricated organ)."""
    early = ForwardContract(
        customer_id="L", term_start="2018-01-01", term_end="2019-12-31",
        notional_mwh=5000.0, agreed_price_gbp_per_mwh=50.0, hedge_fraction=1.0,
        counterparty_id="CP_L",
    )
    assert _mc2_collateral_death_test(_book(early), {"L": "electricity"}, _price_at(), "2023-01-01") is None


def test_deterministic_replay_c_s2():
    """C-S2: the same book + marks reproduce an identical verdict (no clock, no RNG)."""
    def run():
        book = _book(_fwd("L", "CP_L", 50.0, 5000.0), _fwd("S", "CP_S", 50.0, -2000.0))
        return _mc2_collateral_death_test(book, CBY, _price_at(), "2023-01-01")
    assert run() == run()


def test_peak_sample_date_in_window_is_used_as_stress_anchor():
    """When the run's own observed peak-exposure sample falls in 2021-22, it is used as the
    stressed mark (the worst mid-run point during the shock). R12: still real history, not a
    chosen difficulty."""
    book = _book(_fwd("L", "CP_L", 50.0, 5000.0), _fwd("S", "CP_S", 50.0, -2000.0))

    def resolve(fuel, date):
        return 50.0 if date == "2021-01-01" else 200.0
    r = _mc2_collateral_death_test(
        book, CBY, resolve, "2023-01-01", peak_sample_date="2021-06-30"
    )
    assert r is not None
    assert r["stressed_date"] == "2021-06-30"
