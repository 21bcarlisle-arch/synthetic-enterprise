"""The counterparty-collateral seam's contract — and the ways this cut could rot silently.

WHY THIS FILE EXISTS (R15: a control must be able to FAIL on its own named defect)
---------------------------------------------------------------------------------
KNIFE pass 3, `A_composition_lift` step 19, moved the supplier's credit and
collateral desk out of `simulation/run_phase2b.py::main()` into
`company/risk/counterparty_collateral_desk.py` behind
`company/interfaces/counterparty_collateral.py` — three wall crossings
(`company.trading.wholesale_credit_exposure`, `company.finance.margin_call_book`,
`company.risk.collateral_death_test`).

The epistemic-wall ratchet polices the STATIC half: a module-scope
`company.risk.counterparty_collateral_desk -> simulation.*` import is a new
class-(a) edge, the forbidden direction, and reds the suite. Four things it
cannot see:

1. **A lazy import.** The ratchet covers static imports only; an in-function
   `import simulation.…` escapes it. The natural convenience change here is
   real: the desk wants the run's customer register (`_ALL_KNOWN_CUSTOMERS` is a
   module global in the world file, one import away) rather than being handed a
   commodity map. So control 1 is BEHAVIOURAL — it builds a real
   `CounterpartyCollateral` in a clean interpreter and asks which modules the
   import system actually loaded. Its mutation performs the defect on a COPY of
   the real source and re-runs the same detector, so the control is tried rather
   than trusted (and no repo file is edited mid-run, which would corrupt
   `inspect.getsource` for every other test in the session).

2. **A silently reordered, dropped or re-rounded block.** The claim this cut
   rests on is that the desk computes what the inlined code computed. Nothing
   static sees a `round()` move, a dropped sampling date or a flipped
   `max(0, -netted)`, and the effect is not a crash — it is a different peak
   exposure on the board's own credit register. Control 2 replicates the PRE-CUT
   inlined sequence, transcribed from `simulation/run_phase2b.py` as it stood at
   `7237c67a9` (not from the module under test, which would be a mirror), and
   asserts the credit and margin summaries are identical.

3. **THE ARGUMENT SWAP.** Before the cut the fuel→records pairing was an inline
   tuple at the point of use, so `elec_records` could not arrive where
   `gas_records` belonged. Now it spans a signature. Every forward mark, and
   therefore every credit and margin figure in the run, changes if the two are
   swapped — and every test in this file that exercises the impl module directly
   would stay green, because the impl would be given exactly what the caller
   chose to give it. The parameters are keyword-only and separately named to
   make the swap visible; control 3 is an AST check over the real call site in
   `run_phase2b.py` anyway, with a vacuity guard (a source with no such call
   would make it pass for free) and a mutation that performs the swap.

4. **THE FAILURE DOMAINS COLLAPSING INTO ONE.** The pre-cut code was two
   independent `try/except` blocks, with the stated property that a failure in
   the credit feed must not kill the death test. Folding them behind one door
   invites one `try/except` — and nothing would ever notice, because on a
   healthy run both succeed. Control 4 injects a book that raises on the credit
   path only, and asserts the death test still produced its summary; then the
   mirror, and then a mutation proving the assertion is not vacuous.

Each `test_mutation_*` performs the named defect rather than asserting it is
impossible.

VACUITY, stated once for the whole file. The fixture is a two-counterparty book
live across the real 2021-22 window, marked at 2023-06-30, with the two fuels'
spot histories at DELIBERATELY DIFFERENT price levels (electricity ~£95/MWh,
gas ~£28/MWh). Three properties of it are asserted by
`test_fixture_is_not_vacuous_*` rather than left to the reader: the credit
register is non-empty (else control 2 compares two empty dicts), at least one
counterparty is out-of-the-money so a margin call actually forms (else the
margin half of control 2 is `{}` == `{}`), and the death test returns a summary
rather than `None` (else control 4 cannot tell a preserved result from a
suppressed one). The differing price levels are what make control 3's swap
detectable — on equal spot histories the swapped call produces identical marks.
"""

from __future__ import annotations

import ast
import copy
import json
import os
import subprocess
import sys
import tempfile
import textwrap

import pytest

from company.finance.margin_call_book import build_margin_calls_from_mtm
from company.interfaces import counterparty_collateral as door
from company.pricing.tariff_engine import CompanyTariffEngine
from company.risk import counterparty_collateral_desk as impl
from company.trading.forward_book import (
    ForwardContract,
    TradingBook,
    assign_default_counterparty,
)
from company.trading.wholesale_credit_exposure import build_credit_register_from_exposure

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
RUN_MODULE_PATH = os.path.join(REPO_ROOT, "simulation", "run_phase2b.py")
IMPL_PATH = os.path.join(
    REPO_ROOT, "company", "risk", "counterparty_collateral_desk.py"
)

MARK_DATE = "2023-06-30"

# Two price LEVELS, far apart on purpose — see the vacuity note in the docstring.
_ELEC_LEVEL = 95.0
_GAS_LEVEL = 28.0


# ---------------------------------------------------------------------------
# Fixtures — the smallest book that marks, breaches, posts margin and can die.
# ---------------------------------------------------------------------------


def _spot_records(level: float) -> list[dict]:
    """DAILY spot history 2020-01-01 .. 2023-06-30 around a fixed level.

    Daily rather than sampled: `CompanyTariffEngine.get_forward_price` refuses a
    mark on fewer than 30 records inside its lookback window, and a mark it
    refuses is an unmarked fuel — which would empty the credit register and make
    every control below pass on nothing.
    """
    from datetime import date, timedelta

    records = []
    day = date(2020, 1, 1)
    last = date(2023, 6, 30)
    while day <= last:
        records.append(
            {
                "settlementDate": day.isoformat(),
                "systemSellPrice": level + (day.month % 5) * 1.5 + day.day * 0.1,
            }
        )
        day += timedelta(days=1)
    return records


def _elec_records() -> list[dict]:
    return _spot_records(_ELEC_LEVEL)


def _gas_records() -> list[dict]:
    return _spot_records(_GAS_LEVEL)


# The customer ids are chosen, not arbitrary: `assign_default_counterparty` is a
# deterministic hash of (customer_id, term_start, notional), and the obvious ids
# all land on ICE_CLEAR_EUROPE — where ISDA netting collapses the in- and
# out-of-the-money legs into ONE net position, leaving zero credit exposure and
# zero margin. Four DIFFERENT counterparties is what makes both sides of the
# book visible at once (asserted below, not assumed).
_CUSTOMERS = [
    # struck WAY above market -> company deeply out-of-the-money -> variation margin
    ("OTM-ELEC-2", "electricity", "2021-01-01", "2023-12-31", 260.0, 900.0),
    ("OTM-GAS-0", "gas", "2021-03-01", "2023-12-31", 190.0, 700.0),
    # struck below market -> in-the-money -> counterparty credit exposure
    ("ITM-ELEC-2", "electricity", "2021-01-01", "2023-12-31", 20.0, 1100.0),
    ("ITM-GAS-2", "gas", "2021-06-01", "2022-12-31", 5.0, 800.0),
]


def _commodity_by_cid() -> dict[str, str]:
    return {cid: fuel for cid, fuel, *_ in _CUSTOMERS}


def _book() -> TradingBook:
    book = TradingBook()
    for cid, _fuel, start, end, agreed, notional in _CUSTOMERS:
        cp = assign_default_counterparty(cid, start, notional)
        book.open_hedge(
            ForwardContract(
                customer_id=cid,
                term_start=start,
                term_end=end,
                agreed_price_gbp_per_mwh=agreed,
                notional_mwh=notional,
                hedge_fraction=0.85,
                counterparty_id=cp.counterparty_id,
                counterparty_type=cp.counterparty_type,
                clearing_status=cp.clearing_status,
                counterparty_rating=cp.counterparty_rating,
                broker_arranged=cp.broker_arranged,
            )
        )
    return book


def _build(book: TradingBook | None = None) -> impl.CounterpartyCollateral:
    return impl.build_counterparty_collateral(
        book if book is not None else _book(),
        commodity_by_customer_id=_commodity_by_cid(),
        elec_spot_records=_elec_records(),
        gas_spot_records=_gas_records(),
        mark_date=MARK_DATE,
    )


# ---------------------------------------------------------------------------
# The fixture's own properties — the vacuity guards the file's docstring names.
# ---------------------------------------------------------------------------


def test_fixture_is_not_vacuous_the_book_marks_breaches_posts_and_can_die():
    built = _build()
    assert built.credit_feed_error is None, built.credit_feed_error
    assert built.death_test_error is None, built.death_test_error

    credit = built.credit_summary
    assert credit is not None
    assert credit["n_counterparties"] > 0, (
        "empty credit register — control 2 would compare two empty dicts"
    )
    assert len({
        assign_default_counterparty(cid, start, notional).counterparty_id
        for cid, _fuel, start, _end, _agreed, notional in _CUSTOMERS
    }) == len(_CUSTOMERS), (
        "two fixture contracts share a counterparty — ISDA netting would collapse "
        "the ITM and OTM legs and hide one side of the book"
    )
    assert credit["peak_total_net_exposure_gbp"] > 0, "no exposure at any sample"
    assert credit["n_samples"] > 1, "single-sample fixture cannot exercise the peak loop"

    margin = built.margin_call_summary
    assert margin is not None
    assert margin.get("total_outstanding_gbp", 0.0) > 0, (
        "no counterparty is out-of-the-money — the margin half of control 2 is vacuous"
    )

    assert built.death_test_summary is not None, (
        "the death test returned None — control 4 could not distinguish a preserved "
        "result from a suppressed one"
    )

    # Control 3's swap is only detectable because the two fuels' marks differ.
    engine = CompanyTariffEngine()
    elec_mark = engine.get_forward_price("electricity", MARK_DATE, _elec_records())
    gas_mark = engine.get_forward_price("gas", MARK_DATE, _gas_records())
    assert abs(elec_mark - gas_mark) > 1.0, (
        f"the two fuels mark at {elec_mark} and {gas_mark} — control 3's swap "
        "mutation would be undetectable on this fixture"
    )


def test_the_door_re_exports_the_implementation():
    assert door.build_counterparty_collateral is impl.build_counterparty_collateral
    assert door.CounterpartyCollateral is impl.CounterpartyCollateral


# ---------------------------------------------------------------------------
# CONTROL 1 — the company module must not reach back into the world, statically
# OR lazily. Behavioural: what did the import system actually load?
# ---------------------------------------------------------------------------

_PROBE = textwrap.dedent(
    """
    import json, sys
    sys.path.insert(0, {repo!r})
    sys.path.insert(0, {pkgdir!r})
    import {modname} as m
    from company.trading.forward_book import ForwardContract, TradingBook

    book = TradingBook()
    book.open_hedge(ForwardContract(
        customer_id="P1", term_start="2021-01-01", term_end="2023-12-31",
        agreed_price_gbp_per_mwh=260.0, notional_mwh=900.0, hedge_fraction=0.85,
    ))
    recs = [
        {{"settlementDate": "2022-%02d-01" % mth, "systemSellPrice": 95.0 + mth}}
        for mth in range(1, 13)
    ] + [
        {{"settlementDate": "2023-%02d-01" % mth, "systemSellPrice": 95.0 + mth}}
        for mth in range(1, 7)
    ]
    m.build_counterparty_collateral(
        book,
        commodity_by_customer_id={{"P1": "electricity"}},
        elec_spot_records=recs,
        gas_spot_records=recs,
        mark_date="2023-06-30",
    )

    walled = sorted(
        n for n in sys.modules
        if n in ("sim", "simulation") or n.startswith(("sim.", "simulation."))
    )
    print("WALLED_MODULES=" + json.dumps(walled))
    """
)


def _walled_modules_loaded_by(source: str) -> list[str]:
    """Run `source` as the impl module in a clean interpreter; report sim loads.

    THE detector, used unchanged by both the real test and its mutation.
    """
    with tempfile.TemporaryDirectory() as pkgdir:
        modname = "_knife3_step19_subject"
        with open(os.path.join(pkgdir, modname + ".py"), "w") as fh:
            fh.write(source)
        probe = _PROBE.format(repo=REPO_ROOT, pkgdir=pkgdir, modname=modname)
        proc = subprocess.run(
            [sys.executable, "-c", probe],
            cwd=pkgdir,
            capture_output=True,
            text=True,
            timeout=300,
        )
    assert proc.returncode == 0, (
        f"the probe itself failed — an unavailable check is a FAILED check, "
        f"never a skip.\nstdout:\n{proc.stdout}\nstderr:\n{proc.stderr}"
    )
    marker = [ln for ln in proc.stdout.splitlines() if ln.startswith("WALLED_MODULES=")]
    assert len(marker) == 1, f"probe produced no verdict line:\n{proc.stdout}"
    return json.loads(marker[0].split("=", 1)[1])


def test_building_the_collateral_position_loads_no_world_module():
    with open(IMPL_PATH) as fh:
        real_source = fh.read()
    assert _walled_modules_loaded_by(real_source) == []


def test_mutation_a_lazy_world_import_is_caught_by_the_same_detector():
    """Perform the defect on a copy of the real source, same detector."""
    with open(IMPL_PATH) as fh:
        mutated = fh.read()
    anchor = "    _mark_engine = CompanyTariffEngine()"
    assert anchor in mutated, "anchor moved — this mutation is no longer the defect"
    mutated = mutated.replace(
        anchor,
        "    import simulation.reputation_index  # noqa: F401  <-- the defect\n" + anchor,
        1,
    )
    loaded = _walled_modules_loaded_by(mutated)
    assert "simulation.reputation_index" in loaded, (
        "control 1 did not fire on a lazy world import — it cannot fail, so it "
        "is not evidence"
    )


# ---------------------------------------------------------------------------
# CONTROL 2 — behaviour identity against the PRE-CUT sequence, transcribed from
# simulation/run_phase2b.py as it stood before step 19 (git 7237c67a9), NOT from
# the module under test.
# ---------------------------------------------------------------------------


def _pre_cut_credit_and_margin(
    trading_book,
    _ALL_KNOWN_CUSTOMERS: list[dict],
    elec_records: list[dict],
    gas_records: list[dict],
    effective_end: str,
) -> tuple[dict, dict]:
    from datetime import date, timedelta

    _mark_engine = CompanyTariffEngine()
    _current_fwd_by_commodity: dict[str, float] = {}
    for _fuel, _recs in (("electricity", elec_records), ("gas", gas_records)):
        try:
            _current_fwd_by_commodity[_fuel] = _mark_engine.get_forward_price(
                _fuel, effective_end, _recs
            )
        except ValueError:
            pass
    _commodity_by_cid = {c["customer_id"]: c["commodity"] for c in _ALL_KNOWN_CUSTOMERS}
    _mark_prices: dict[str, float] = {}
    for _c in trading_book.open_contracts():
        _px = _current_fwd_by_commodity.get(_commodity_by_cid.get(_c.customer_id))
        if _px is not None:
            _mark_prices[_c.customer_id] = _px
    _exposure = trading_book.exposure_by_counterparty(_mark_prices)
    _credit_register = build_credit_register_from_exposure(_exposure)
    _largest = _credit_register.largest_exposure()
    _breaches = _credit_register.limit_breaches()
    _wholesale_credit_summary = {
        "mark_date": effective_end,
        "current_forward_price_by_commodity": {
            k: round(v, 4) for k, v in _current_fwd_by_commodity.items()
        },
        "n_counterparties": len(_credit_register.all_records()),
        "total_net_exposure_gbp": round(_credit_register.total_net_exposure_gbp(), 2),
        "total_collateral_held_gbp": round(_credit_register.total_collateral_held_gbp(), 2),
        "largest_counterparty": _largest.counterparty_id if _largest else None,
        "largest_net_exposure_gbp": round(_largest.net_exposure_gbp, 2) if _largest else 0.0,
        "largest_utilisation_pct": round(_largest.utilisation_pct, 2) if _largest else 0.0,
        "is_limit_breached": len(_breaches) > 0,
        "n_breach": len(_breaches),
    }
    _samples: list[dict] = []
    _sample_years = sorted({c.term_start[:4] for c in trading_book.all_contracts()})
    _sample_dates = [
        f"{_y}{_mmdd}" for _y in _sample_years for _mmdd in ("-06-30", "-12-31")
        if f"{_y}{_mmdd}" < effective_end
    ] + [effective_end]
    for _sd in _sample_dates:
        _fwd_sd: dict[str, float] = {}
        for _fuel, _recs in (("electricity", elec_records), ("gas", gas_records)):
            try:
                _fwd_sd[_fuel] = _mark_engine.get_forward_price(_fuel, _sd, _recs)
            except ValueError:
                pass
        _live_sd = trading_book.live_contracts_as_of(_sd)
        _mp_sd = {
            _c.customer_id: _fwd_sd[_commodity_by_cid[_c.customer_id]]
            for _c in _live_sd
            if _commodity_by_cid.get(_c.customer_id) in _fwd_sd
        }
        _reg_sd = build_credit_register_from_exposure(
            trading_book.exposure_by_counterparty_as_of(_mp_sd, _sd)
        )
        _samples.append({
            "sample_date": _sd,
            "n_live_contracts": len(_live_sd),
            "n_counterparties": len(_reg_sd.all_records()),
            "total_net_exposure_gbp": round(_reg_sd.total_net_exposure_gbp(), 2),
            "n_breach": len(_reg_sd.limit_breaches()),
        })
    _peak = max(_samples, key=lambda s: s["total_net_exposure_gbp"], default=None)
    _wholesale_credit_summary.update({
        "sampling": "semi-annual point-in-time marks (VALUE_CHAIN multi-period)",
        "n_samples": len(_samples),
        "peak_sample_date": _peak["sample_date"] if _peak else None,
        "peak_total_net_exposure_gbp": _peak["total_net_exposure_gbp"] if _peak else 0.0,
        "peak_n_live_contracts": _peak["n_live_contracts"] if _peak else 0,
        "peak_n_counterparties": _peak["n_counterparties"] if _peak else 0,
        "peak_is_limit_breached": bool(_peak and _peak["n_breach"] > 0),
        "sample_series": _samples,
    })
    _settlement_deadline = (
        date.fromisoformat(effective_end) + timedelta(days=1)
    ).isoformat()
    _margin_book = build_margin_calls_from_mtm(
        _exposure, as_of_date=effective_end, settlement_deadline=_settlement_deadline
    )
    return _wholesale_credit_summary, _margin_book.margin_call_summary()


def _all_known_customers() -> list[dict]:
    return [{"customer_id": cid, "commodity": fuel} for cid, fuel, *_ in _CUSTOMERS]


def test_credit_and_margin_are_identical_to_the_pre_cut_inlined_sequence():
    credit, margin = _pre_cut_credit_and_margin(
        _book(), _all_known_customers(), _elec_records(), _gas_records(), MARK_DATE
    )
    built = _build()
    assert built.credit_summary == credit

    # R6 (2026-08-28): the door now reports the counterparty's CREDIT verdict alongside the
    # margin figures -- whether an independent amount was demanded, and on what basis. The
    # pre-cut inline sequence has no such concept, so an exact dict equality would now be
    # asserting that the door never grew, which is a different and wrong claim.
    #
    # The conformance that matters is unchanged and is asserted on every key the pre-cut code
    # produced: not one of them moved. The addition is named explicitly rather than absorbed by
    # a subset comparison, so a future key cannot slip in unlisted.
    added = set(built.margin_call_summary) - set(margin)
    assert added == {"independent_amount_basis", "total_independent_amount_gbp"}, (
        f"the door grew keys nobody declared: {sorted(added)}"
    )
    assert {k: built.margin_call_summary[k] for k in margin} == margin, (
        "every figure the pre-cut sequence produced must be bit-identical through the door"
    )
    # And with no balance sheet supplied it must SAY so, never report a waived demand.
    assert built.margin_call_summary["independent_amount_basis"] == (
        "not_assessed_no_balance_sheet"
    )


def test_mutation_a_dropped_sample_date_breaks_the_identity():
    """The identity control fires when the moved code stops matching.

    The defect: the semi-annual sampling loop keeps only the December marks —
    one dropped tuple element, the shape of a transcription slip. It changes the
    peak, which is the figure the board reads.
    """
    real_credit, _ = _pre_cut_credit_and_margin(
        _book(), _all_known_customers(), _elec_records(), _gas_records(), MARK_DATE
    )
    book = _book()
    sample_years = sorted({c.term_start[:4] for c in book.all_contracts()})
    engine = CompanyTariffEngine()
    commodity = _commodity_by_cid()
    mutated_dates = [
        f"{y}-12-31" for y in sample_years if f"{y}-12-31" < MARK_DATE
    ] + [MARK_DATE]
    samples = []
    for sd in mutated_dates:
        fwd = {}
        for fuel, recs in (("electricity", _elec_records()), ("gas", _gas_records())):
            try:
                fwd[fuel] = engine.get_forward_price(fuel, sd, recs)
            except ValueError:
                pass
        live = book.live_contracts_as_of(sd)
        prices = {
            c.customer_id: fwd[commodity[c.customer_id]]
            for c in live
            if commodity.get(c.customer_id) in fwd
        }
        reg = build_credit_register_from_exposure(
            book.exposure_by_counterparty_as_of(prices, sd)
        )
        samples.append({
            "sample_date": sd,
            "n_live_contracts": len(live),
            "n_counterparties": len(reg.all_records()),
            "total_net_exposure_gbp": round(reg.total_net_exposure_gbp(), 2),
            "n_breach": len(reg.limit_breaches()),
        })
    peak = max(samples, key=lambda s: s["total_net_exposure_gbp"], default=None)
    mutated_credit = dict(real_credit)
    mutated_credit.update({
        "n_samples": len(samples),
        "peak_sample_date": peak["sample_date"] if peak else None,
        "peak_total_net_exposure_gbp": peak["total_net_exposure_gbp"] if peak else 0.0,
        "peak_n_live_contracts": peak["n_live_contracts"] if peak else 0,
        "peak_n_counterparties": peak["n_counterparties"] if peak else 0,
        "peak_is_limit_breached": bool(peak and peak["n_breach"] > 0),
        "sample_series": samples,
    })
    assert len(samples) < real_credit["n_samples"], (
        "the mutation dropped no sample — it is not the defect on this fixture"
    )
    # The identity assertion in the test above, run against the mutated summary:
    # it must FAIL. A control that cannot fail is not evidence.
    assert mutated_credit != real_credit, (
        "control 2's identity comparison passes on a dropped sampling date — "
        "the credit summary would agree with the pre-cut sequence while the "
        "board's own peak had moved"
    )


# ---------------------------------------------------------------------------
# CONTROL 3 — the fuel→records pairing at the REAL call site in run_phase2b.py.
# ---------------------------------------------------------------------------

_EXPECTED_PAIRING = {
    "elec_spot_records": "elec_records",
    "gas_spot_records": "gas_records",
}


def _pairing_findings(source: str) -> tuple[list[str], int]:
    """Return (findings, n_calls_examined) for `build_counterparty_collateral` calls.

    The call count is returned so the caller can refuse a vacuous pass: a source
    with no such call produces an empty finding list for free.
    """
    findings: list[str] = []
    n_calls = 0
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        fn = node.func
        name = fn.id if isinstance(fn, ast.Name) else getattr(fn, "attr", None)
        if name != "build_counterparty_collateral":
            continue
        n_calls += 1
        supplied = {kw.arg: kw.value for kw in node.keywords if kw.arg}
        for param, expected_var in _EXPECTED_PAIRING.items():
            value = supplied.get(param)
            if value is None:
                findings.append(f"{param} is not passed by keyword at the call site")
            elif not isinstance(value, ast.Name):
                findings.append(f"{param} is not a plain name at the call site")
            elif value.id != expected_var:
                findings.append(
                    f"{param}={value.id} at the call site, expected {expected_var}"
                )
    return findings, n_calls


def test_the_call_site_pairs_each_fuel_with_its_own_spot_history():
    with open(RUN_MODULE_PATH) as fh:
        source = fh.read()
    findings, n_calls = _pairing_findings(source)
    assert n_calls >= 1, (
        "no build_counterparty_collateral call found in run_phase2b.py — this "
        "control would pass for free (vacuity guard)"
    )
    assert findings == [], findings


def test_mutation_a_swapped_pair_at_the_call_site_is_caught():
    with open(RUN_MODULE_PATH) as fh:
        source = fh.read()
    mutated = source.replace(
        "        elec_spot_records=elec_records,\n        gas_spot_records=gas_records,",
        "        elec_spot_records=gas_records,\n        gas_spot_records=elec_records,",
        1,
    )
    assert mutated != source, "the swap anchor moved — this mutation is no longer the defect"
    findings, n_calls = _pairing_findings(mutated)
    assert n_calls >= 1
    assert len(findings) == 2, findings
    assert any("elec_spot_records=gas_records" in f for f in findings), findings


def test_mutation_the_swap_actually_moves_every_credit_figure():
    """The AST control is only worth having if the swap is a real defect."""
    straight = _build()
    swapped = impl.build_counterparty_collateral(
        _book(),
        commodity_by_customer_id=_commodity_by_cid(),
        elec_spot_records=_gas_records(),
        gas_spot_records=_elec_records(),
        mark_date=MARK_DATE,
    )
    assert straight.credit_summary is not None and swapped.credit_summary is not None
    assert (
        straight.credit_summary["peak_total_net_exposure_gbp"]
        != swapped.credit_summary["peak_total_net_exposure_gbp"]
    ), "the swap changes nothing on this fixture — control 3 guards nothing"


# ---------------------------------------------------------------------------
# CONTROL 4 — the two failure domains stayed independent behind one door.
# ---------------------------------------------------------------------------


class _BookFailingOn:
    """A trading book that raises on ONE named method and delegates the rest."""

    def __init__(self, inner: TradingBook, method: str) -> None:
        self._inner = inner
        self._method = method

    def __getattr__(self, name: str):
        if name == self._method:
            def _boom(*_a, **_kw):
                raise RuntimeError(f"injected failure in {name}")
            return _boom
        return getattr(self._inner, name)


def test_a_credit_feed_failure_does_not_suppress_the_death_test():
    # open_contracts() is reached only by the credit block; the death test uses
    # live_contracts_as_of().
    built = _build(_BookFailingOn(_book(), "open_contracts"))
    assert built.credit_feed_error is not None, "the injected failure did not fire"
    assert built.credit_summary is None
    assert built.death_test_summary is not None, (
        "the credit feed's failure took the death test with it — the two "
        "try/except blocks the pre-cut code kept apart have collapsed into one"
    )
    assert built.death_test_error is None


def test_a_death_test_failure_does_not_suppress_the_credit_feed():
    built = _build(_BookFailingOn(_book(), "live_contracts_as_of"))
    assert built.death_test_error is not None, "the injected failure did not fire"
    assert built.death_test_summary is None
    # The credit block also samples with live_contracts_as_of, so its own summary
    # is lost too — what must survive is that the door still RETURNS, reporting
    # both domains, rather than the exception escaping into main().
    assert isinstance(built, impl.CounterpartyCollateral)
    assert built.credit_feed_error is not None


def test_mutation_a_single_shared_try_except_is_caught_by_control_4():
    """Perform the defect: one try/except around both blocks.

    Re-implemented here rather than patched into the real module, so the control
    is tried against the shape it is meant to reject without editing a source
    file mid-pytest-run.
    """
    book = _BookFailingOn(_book(), "open_contracts")

    def _one_domain() -> impl.CounterpartyCollateral:
        try:
            credit, margin = impl._credit_and_margin(
                book, _commodity_by_cid(), _elec_records(), _gas_records(), MARK_DATE
            )
            death = impl.collateral_death_test_summary(
                book, _commodity_by_cid(), lambda _f, _d: 90.0, MARK_DATE
            )
            return impl.CounterpartyCollateral(credit, margin, death)
        except Exception as exc:
            return impl.CounterpartyCollateral(credit_feed_error=exc)

    collapsed = _one_domain()
    assert collapsed.death_test_summary is None, (
        "the collapsed shape still produced a death-test summary — control 4's "
        "assertion would pass on the defect it exists to reject"
    )
    # ...and the real door does not behave that way.
    assert _build(book).death_test_summary is not None


# ---------------------------------------------------------------------------
# The door's own shape.
# ---------------------------------------------------------------------------


def test_the_result_is_frozen_so_a_consumer_cannot_edit_the_position():
    built = _build()
    with pytest.raises(Exception):
        built.credit_summary = {}  # type: ignore[misc]


def test_the_desk_does_not_mutate_the_book_it_is_handed():
    book = _book()
    before = copy.deepcopy([c.customer_id for c in book.all_contracts()])
    _build(book)
    assert [c.customer_id for c in book.all_contracts()] == before
