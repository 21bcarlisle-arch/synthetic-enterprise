"""The hedge-desk seam's contract — and the ways this cut could rot silently.

WHY THIS FILE EXISTS (R15: a control must be able to FAIL on its own named defect)
---------------------------------------------------------------------------------
KNIFE pass 3, `A_composition_lift` step 23, moved the supplier's hedging desk out
of `simulation/run_phase2b.py::main()` into `company/trading/hedge_desk.py`
behind `company/interfaces/hedge_desk.py` — three wall crossings
(`company.trading.forward_book`, `company.trading.hedge_decision`,
`company.risk.hedge_policy`).

The epistemic-wall ratchet polices the STATIC half: a module-scope
`company.trading.hedge_desk -> simulation.*` import is a new class-(a) edge, the
forbidden direction, and reds the suite. Four things it cannot see:

1. **A lazy import.** The ratchet covers static imports only; an in-function
   `import simulation.…` escapes it. The convenience change is real and
   specific here: the desk is handed `price_records` that the world derived from
   a `PointInTimeView`, and the shortest path to "just build the view here" is
   one import away. Control 1 is BEHAVIOURAL — it exercises the real door in a
   clean interpreter and asks which modules the import system actually loaded.
   Its mutation performs the defect on a COPY of the real source and re-runs the
   same detector, so the control is tried rather than trusted (and no repo file
   is edited mid-run, which would corrupt `inspect.getsource` for every other
   test in the session).

2. **THE OVERRIDE ORDERING.** Before the cut the world wrote two adjacent
   statements: assign the model's fraction only if the risk committee has not
   already ruled, THEN compute the realised VaR at whatever fraction survived.
   That ordering is the difference between reporting the risk the desk is
   RUNNING and the risk the model ASKED FOR, and on the majority arm — no
   override — the two are identical, so a swap is invisible on a healthy run.
   Control 2 replicates the PRE-CUT inlined sequence, transcribed from
   `simulation/run_phase2b.py` as it stood at `21ad5aeea` (not from the module
   under test, which would be a mirror), on BOTH arms, and asserts the fraction
   and the whole VaR log entry are identical. Two mutations perform the defect:
   the realised VaR computed at the pre-decision fraction, and the override
   guard dropped entirely.

3. **THE VOLUME/PRICE ARGUMENT SWAP, and the commodity label.** Before the cut
   `eac_kwh`/`aq_kwh` and `company_fwd`/`unit_rate` were locals at the point of
   use and the commodity was a literal inside the dict being built. Now all four
   span a signature, and the electricity and gas call sites differ only in which
   locals they pass. A gas term logged as `"electricity"`, or a unit rate passed
   where a forward belongs, changes every VaR figure on the Trading & Market tab
   and crashes nothing. The parameters are keyword-only and separately named to
   make a swap visible; control 3 is an AST check over the REAL call sites in
   `run_phase2b.py` anyway — both of them, because a control that checks one of
   two sites is the "one of three pairs" defect this project has already
   recorded — with a vacuity guard (a source with no such call would make it
   pass for free) and mutations that perform the swap and the mislabel.

4. **THE BOOK BECOMING TWO BOOKS.** `open_term_hedge`, `settle_period_pnl_gbp`,
   `.book` (marked by the collateral door, §3n) and `.summary()` (the report)
   must all be the SAME `TradingBook`. Before the cut that was self-evident —
   one local named `trading_book`. Behind a class it is an invariant nothing
   static checks, and the failure is silent: the report would show a book with
   contracts and the collateral desk would mark an empty one, or vice versa.
   Control 4 opens a position through the desk and asserts the same contract is
   visible on all four surfaces, with a mutation that hands `.book` a fresh
   `TradingBook`.

Each `test_mutation_*` performs the named defect rather than asserting it is
impossible.

VACUITY, stated once for the whole file. The price fixture is 200 days of DAILY
spot history with real variation (`estimate_price_volatility` floors at
`MIN_VOL_ANNUAL` on fewer than 5 distinct days, and a flat history returns the
floor — either would make the VaR arithmetic constant and every identity control
below compare two floors). Three properties are asserted by
`test_fixture_is_not_vacuous_*` rather than left to the reader: the decided
fraction is strictly ABOVE the mandate floor (else control 2's override arm
compares floor to floor and the ordering defect is undetectable), the realised
VaR is strictly positive (else the two mutations in control 2 both produce
`0.0`), and the two commodities' fixtures produce DIFFERENT VaR figures (else
control 3's argument swap is invisible).
"""

from __future__ import annotations

import ast
import os
import subprocess
import sys
import tempfile
import textwrap

import pytest

from company.interfaces import hedge_desk as door
from company.risk.hedge_policy import (
    COMPANY_MIN_HEDGE_FLOOR,
    company_evolve_hedge_fraction,
)
from company.trading import hedge_desk as impl
from company.trading.forward_book import TradingBook
from company.trading.hedge_decision import (
    compute_bid_ask_cost,
    compute_realized_var,
    decide_hedge_fraction,
)

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
RUN_MODULE_PATH = os.path.join(REPO_ROOT, "simulation", "run_phase2b.py")
IMPL_PATH = os.path.join(REPO_ROOT, "company", "trading", "hedge_desk.py")

TERM_START = "2022-01-01"
TERM_END = "2022-12-31"
TERM_DAYS = 364

# Two commodity fixtures at DELIBERATELY different levels and volumes — see the
# vacuity note in the docstring.
ELEC_EAC_KWH = 3_100.0
ELEC_FWD = 118.0
ELEC_UNIT_RATE = 205.0

GAS_AQ_KWH = 12_500.0
GAS_FWD = 41.0
GAS_UNIT_RATE = 78.0


def _spot_records(level: float, days: int = 200) -> list[dict]:
    """DAILY spot history with real day-to-day variation.

    Flat history → `estimate_price_volatility` returns MIN_VOL_ANNUAL, which
    would make every VaR figure below a constant. The wobble is deterministic
    (no RNG) so the transcribed-original comparison is exact.
    """
    from datetime import date, timedelta

    start = date(2021, 6, 1)
    out: list[dict] = []
    for i in range(days):
        wobble = 1.0 + 0.11 * ((i % 7) - 3) / 3.0 + 0.04 * ((i % 23) - 11) / 11.0
        out.append(
            {
                "settlementDate": (start + timedelta(days=i)).isoformat(),
                "systemSellPrice": round(level * wobble, 4),
            }
        )
    return out


ELEC_PRICES = _spot_records(ELEC_FWD)
GAS_PRICES = _spot_records(GAS_FWD)


def _decide(desk, *, commodity, accept_decision, current_fraction=0.5):
    if commodity == "electricity":
        volume, fwd, rate, prices = ELEC_EAC_KWH, ELEC_FWD, ELEC_UNIT_RATE, ELEC_PRICES
    else:
        volume, fwd, rate, prices = GAS_AQ_KWH, GAS_FWD, GAS_UNIT_RATE, GAS_PRICES
    return desk.decide_term_hedge(
        customer_id="C-001",
        term_start=TERM_START,
        term_end=TERM_END,
        commodity=commodity,
        volume_kwh=volume,
        forward_price_gbp_per_mwh=fwd,
        unit_rate_gbp_per_mwh=rate,
        price_records=prices,
        term_days=TERM_DAYS,
        current_fraction=current_fraction,
        accept_decision=accept_decision,
    )


# ---------------------------------------------------------------------------
# Vacuity guards — asserted, not assumed.
# ---------------------------------------------------------------------------


def test_fixture_is_not_vacuous_decision_is_above_the_mandate_floor():
    """If the VaR decision returned the floor, control 2's arms are identical."""
    hf = decide_hedge_fraction(
        ELEC_EAC_KWH, ELEC_FWD, ELEC_UNIT_RATE, ELEC_PRICES, TERM_DAYS
    )
    assert hf > COMPANY_MIN_HEDGE_FLOOR, (
        f"fixture decides {hf}, the floor is {COMPANY_MIN_HEDGE_FLOOR} — the "
        "override-ordering controls would compare the floor to itself"
    )
    assert hf < 1.0, "a fully-hedged decision leaves no naked position to price VaR on"


def test_fixture_is_not_vacuous_realized_var_is_positive():
    """A zero VaR makes both control-2 mutations produce the same 0.0."""
    entry = _decide(impl.build_hedge_desk(), commodity="electricity", accept_decision=True)
    assert entry.var_log_entry["var_gbp"] > 0.0
    assert entry.var_log_entry["var_pct_of_term_revenue"] > 0.0


def test_fixture_is_not_vacuous_the_two_commodities_differ():
    """Equal fixtures would make control 3's argument swap undetectable."""
    e = _decide(impl.build_hedge_desk(), commodity="electricity", accept_decision=True)
    g = _decide(impl.build_hedge_desk(), commodity="gas", accept_decision=True)
    assert e.var_log_entry["var_gbp"] != g.var_log_entry["var_gbp"]


# ---------------------------------------------------------------------------
# The door re-exports the implementation, and nothing else.
# ---------------------------------------------------------------------------


def test_the_door_exposes_the_desk_the_mandate_and_the_term_hedge():
    assert door.HedgeDesk is impl.HedgeDesk
    assert door.HedgeMandate is impl.HedgeMandate
    assert door.TermHedge is impl.TermHedge
    assert door.build_hedge_desk is impl.build_hedge_desk
    assert door.hedge_mandate is impl.hedge_mandate


def test_the_mandate_states_the_naked_fraction_rather_than_the_world_deriving_it():
    """`1 - floor` was the world's arithmetic before this cut; now it is the desk's."""
    mandate = door.hedge_mandate()
    assert mandate.minimum_hedged_fraction == COMPANY_MIN_HEDGE_FLOOR
    assert mandate.opening_hedge_fraction == COMPANY_MIN_HEDGE_FLOOR
    assert mandate.naked_fraction == pytest.approx(1.0 - COMPANY_MIN_HEDGE_FLOOR)


# ---------------------------------------------------------------------------
# CONTROL 1 — read direction, behavioural.
# ---------------------------------------------------------------------------

_READ_DIRECTION_PROBE = """
import datetime, json, sys
sys.path.insert(0, {root!r})
sys.modules.pop("simulation", None)
import company.interfaces.hedge_desk as door
_start = datetime.date(2021, 6, 1)
_prices = [
    {{
        "settlementDate": (_start + datetime.timedelta(days=i)).isoformat(),
        "systemSellPrice": 100.0 + (i % 9),
    }}
    for i in range(120)
]
desk = door.build_hedge_desk()
desk.decide_term_hedge(
    customer_id="C-001", term_start="2022-01-01", term_end="2022-12-31",
    commodity="electricity", volume_kwh=3100.0,
    forward_price_gbp_per_mwh=118.0, unit_rate_gbp_per_mwh=205.0,
    price_records=_prices,
    term_days=364, current_fraction=0.5, accept_decision=True,
)
desk.open_term_hedge(
    customer_id="C-001", term_start="2022-01-01", term_end="2022-12-31",
    volume_kwh=3100.0, forward_price_gbp_per_mwh=118.0,
    hedge_fraction=0.9, term_days=364,
)
world = sorted(
    m for m in sys.modules
    if m == "simulation" or m.startswith("simulation.")
    or m == "sim" or m.startswith("sim.")
)
print("WORLD_MODULES=" + json.dumps(world))
"""


def _run_probe(root: str) -> list[str]:
    with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False) as fh:
        fh.write(_READ_DIRECTION_PROBE.format(root=root))
        probe = fh.name
    try:
        res = subprocess.run(
            [sys.executable, probe],
            capture_output=True,
            text=True,
            timeout=180,
            cwd=root,
        )
        assert res.returncode == 0, f"probe failed:\n{res.stdout}\n{res.stderr}"
        line = [
            ln for ln in res.stdout.splitlines() if ln.startswith("WORLD_MODULES=")
        ]
        assert line, f"probe produced no verdict:\n{res.stdout}"
        import json as _json

        return _json.loads(line[-1].split("=", 1)[1])
    finally:
        os.unlink(probe)


def test_control_1_exercising_the_door_loads_no_world_module():
    assert _run_probe(REPO_ROOT) == []


def test_mutation_control_1_fires_on_a_lazy_world_import():
    """Perform the defect on a COPY of the repo's impl, never the repo file."""
    with tempfile.TemporaryDirectory() as tmp:
        # A minimal shadow tree: copy the packages the desk actually needs by
        # symlinking the repo and overlaying one mutated module.
        shadow = os.path.join(tmp, "repo")
        os.symlink(REPO_ROOT, shadow)
        mutated_root = os.path.join(tmp, "overlay")
        os.makedirs(os.path.join(mutated_root, "company", "trading"))
        source = open(IMPL_PATH, encoding="utf-8").read()
        assert "def open_term_hedge(" in source
        mutated = source.replace(
            "        tenor_years = term_days / 365.25",
            "        import simulation.run_phase2b  # noqa: F401  <-- THE DEFECT\n"
            "        tenor_years = term_days / 365.25",
            1,
        )
        assert mutated != source, "mutation did not apply — the anchor moved"
        # The overlay needs the whole import path, so run the probe against the
        # real root but with the mutated module shadowing it on sys.path.
        for pkg in ("company", os.path.join("company", "trading")):
            init = os.path.join(mutated_root, pkg, "__init__.py")
            real_init = os.path.join(REPO_ROOT, pkg, "__init__.py")
            with open(init, "w", encoding="utf-8") as fh:
                fh.write(
                    open(real_init, encoding="utf-8").read()
                    if os.path.exists(real_init)
                    else ""
                )
                fh.write(
                    "\nimport os as _os\n"
                    f"__path__.append(_os.path.join({REPO_ROOT!r}, {pkg!r}))\n"
                )
        with open(
            os.path.join(mutated_root, "company", "trading", "hedge_desk.py"),
            "w",
            encoding="utf-8",
        ) as fh:
            fh.write(mutated)

        probe = _READ_DIRECTION_PROBE.format(root=REPO_ROOT).replace(
            f"sys.path.insert(0, {REPO_ROOT!r})",
            f"sys.path.insert(0, {REPO_ROOT!r})\nsys.path.insert(0, {mutated_root!r})",
            1,
        )
        path = os.path.join(tmp, "probe.py")
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(probe)
        res = subprocess.run(
            [sys.executable, path],
            capture_output=True,
            text=True,
            timeout=300,
            cwd=REPO_ROOT,
        )
        assert res.returncode == 0, f"mutated probe failed:\n{res.stdout}\n{res.stderr}"
        import json as _json

        line = [
            ln for ln in res.stdout.splitlines() if ln.startswith("WORLD_MODULES=")
        ][-1]
        loaded = _json.loads(line.split("=", 1)[1])
        assert loaded, (
            "the read-direction control did NOT fire on a lazy world import — "
            "it cannot fail, so it is not evidence (R15)"
        )
        assert any(m.startswith("simulation") for m in loaded)


# ---------------------------------------------------------------------------
# CONTROL 2 — the override ordering, against the transcribed PRE-CUT sequence.
# ---------------------------------------------------------------------------


def _pre_cut_decide(
    *,
    cid: str,
    term_start_str: str,
    term_end_str: str,
    commodity: str,
    volume_kwh: float,
    company_fwd: float,
    unit_rate: float,
    price_hist: list[dict],
    term_days_count: int,
    hf: float,
    overridden: bool,
) -> tuple[float, dict]:
    """The inlined block from `simulation/run_phase2b.py` at 21ad5aeea.

    Transcribed from the WORLD file as it stood before the cut — NOT from
    `company/trading/hedge_desk.py`, which would make this a mirror of the thing
    it is checking (R15: tautology).
    """
    _var_hf = decide_hedge_fraction(
        volume_kwh, company_fwd, unit_rate, price_hist, term_days_count
    )
    if not overridden:
        hf = _var_hf
    _realized_var = compute_realized_var(
        volume_kwh, company_fwd, unit_rate, price_hist, term_days_count, hf
    )
    entry = {
        "customer_id": cid,
        "term_start": term_start_str,
        "term_end": term_end_str,
        "commodity": commodity,
        "hedge_fraction": round(hf, 4),
        **_realized_var,
    }
    return hf, entry


@pytest.mark.parametrize("overridden", [False, True])
@pytest.mark.parametrize("commodity", ["electricity", "gas"])
def test_control_2_the_desk_reproduces_the_pre_cut_sequence_on_both_arms(
    commodity, overridden
):
    if commodity == "electricity":
        volume, fwd, rate, prices = ELEC_EAC_KWH, ELEC_FWD, ELEC_UNIT_RATE, ELEC_PRICES
    else:
        volume, fwd, rate, prices = GAS_AQ_KWH, GAS_FWD, GAS_UNIT_RATE, GAS_PRICES

    expected_hf, expected_entry = _pre_cut_decide(
        cid="C-001",
        term_start_str=TERM_START,
        term_end_str=TERM_END,
        commodity=commodity,
        volume_kwh=volume,
        company_fwd=fwd,
        unit_rate=rate,
        price_hist=prices,
        term_days_count=TERM_DAYS,
        hf=0.5,
        overridden=overridden,
    )
    got = _decide(
        impl.build_hedge_desk(),
        commodity=commodity,
        accept_decision=not overridden,
        current_fraction=0.5,
    )
    assert got.hedge_fraction == expected_hf
    assert got.var_log_entry == expected_entry


def test_mutation_control_2_fires_when_var_is_computed_at_the_pre_decision_fraction():
    """The defect: report the risk the model ASKED FOR, not the one being RUN."""
    volume, fwd, rate, prices = GAS_AQ_KWH, GAS_FWD, GAS_UNIT_RATE, GAS_PRICES
    _, expected_entry = _pre_cut_decide(
        cid="C-001",
        term_start_str=TERM_START,
        term_end_str=TERM_END,
        commodity="gas",
        volume_kwh=volume,
        company_fwd=fwd,
        unit_rate=rate,
        price_hist=prices,
        term_days_count=TERM_DAYS,
        hf=0.5,
        overridden=True,
    )
    # Now perform the defect: VaR at the model's fraction while the committee's stands.
    decided = decide_hedge_fraction(volume, fwd, rate, prices, TERM_DAYS)
    mutated_var = compute_realized_var(volume, fwd, rate, prices, TERM_DAYS, decided)
    mutated_entry = {**expected_entry, **mutated_var}
    assert mutated_entry != expected_entry, (
        "the mutation changed nothing — control 2 could not fail on it"
    )


def test_mutation_control_2_fires_when_the_override_guard_is_dropped():
    """The defect: the model's fraction overwrites the committee's ruling."""
    got = _decide(
        impl.build_hedge_desk(),
        commodity="electricity",
        accept_decision=False,
        current_fraction=0.5,
    )
    assert got.hedge_fraction == 0.5, "the committee's fraction must survive"
    dropped_guard = decide_hedge_fraction(
        ELEC_EAC_KWH, ELEC_FWD, ELEC_UNIT_RATE, ELEC_PRICES, TERM_DAYS
    )
    assert dropped_guard != got.hedge_fraction, (
        "the mutation changed nothing — the fixture's decision equals the "
        "committee's fraction, so the guard control is vacuous"
    )


# ---------------------------------------------------------------------------
# CONTROL 3 — the real call sites, BOTH of them.
# ---------------------------------------------------------------------------


def _decide_calls(source: str) -> list[ast.Call]:
    tree = ast.parse(source)
    out = []
    for node in ast.walk(tree):
        if (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and node.func.attr == "decide_term_hedge"
        ):
            out.append(node)
    return out


def _kwargs(call: ast.Call) -> dict[str, ast.AST]:
    return {kw.arg: kw.value for kw in call.keywords if kw.arg}


def test_control_3_both_call_sites_exist_and_are_wholly_keyword():
    """Vacuity guard first: a source with no such call must not pass for free."""
    source = open(RUN_MODULE_PATH, encoding="utf-8").read()
    calls = _decide_calls(source)
    assert len(calls) == 2, (
        f"expected the electricity AND gas call sites, found {len(calls)} — "
        "a control that checks one of two sites is the census defect this "
        "project has already recorded"
    )
    for call in calls:
        assert not call.args, "positional arguments make a swap invisible"
        assert {
            "customer_id",
            "term_start",
            "term_end",
            "commodity",
            "volume_kwh",
            "forward_price_gbp_per_mwh",
            "unit_rate_gbp_per_mwh",
            "price_records",
            "term_days",
            "current_fraction",
            "accept_decision",
        } <= set(_kwargs(call))


def test_control_3_each_call_site_passes_its_own_commodity_and_its_own_locals():
    source = open(RUN_MODULE_PATH, encoding="utf-8").read()
    by_commodity = {}
    for call in _decide_calls(source):
        kw = _kwargs(call)
        label = kw["commodity"]
        assert isinstance(label, ast.Constant), "the commodity label must be a literal"
        by_commodity[label.value] = kw
    assert set(by_commodity) == {"electricity", "gas"}

    elec = by_commodity["electricity"]
    gas = by_commodity["gas"]
    assert isinstance(elec["volume_kwh"], ast.Name) and elec["volume_kwh"].id == "eac_kwh"
    assert isinstance(gas["volume_kwh"], ast.Name) and gas["volume_kwh"].id == "aq_kwh"
    for kw in (elec, gas):
        assert isinstance(kw["forward_price_gbp_per_mwh"], ast.Name)
        assert kw["forward_price_gbp_per_mwh"].id == "company_fwd"
        assert isinstance(kw["unit_rate_gbp_per_mwh"], ast.Name)
        assert kw["unit_rate_gbp_per_mwh"].id == "unit_rate"
    assert isinstance(elec["price_records"], ast.Name)
    assert elec["price_records"].id == "_elec_price_hist"
    assert isinstance(gas["price_records"], ast.Name)
    assert gas["price_records"].id == "_gas_price_hist"


def test_mutation_control_3_fires_on_a_swapped_forward_and_unit_rate():
    source = open(RUN_MODULE_PATH, encoding="utf-8").read()
    mutated = source.replace(
        "                        forward_price_gbp_per_mwh=company_fwd,\n"
        "                        unit_rate_gbp_per_mwh=unit_rate,",
        "                        forward_price_gbp_per_mwh=unit_rate,\n"
        "                        unit_rate_gbp_per_mwh=company_fwd,",
        1,
    )
    assert mutated != source, "mutation did not apply — the anchor moved"
    calls = _decide_calls(mutated)
    swapped = [
        c
        for c in calls
        if _kwargs(c)["forward_price_gbp_per_mwh"].id == "unit_rate"
    ]
    assert swapped, "control 3 did not see the swap — it cannot fail (R15)"


def test_mutation_control_3_fires_on_a_gas_term_labelled_electricity():
    source = open(RUN_MODULE_PATH, encoding="utf-8").read()
    # The anchor carries the decide-call's own indentation. A bare
    # `commodity="gas",` is NOT unique in this file and stopped being the first
    # occurrence when KNIFE step 24 (§3s) put a gas forward-estimate ask above
    # it — the mutation then landed on an unrelated call and this control
    # silently could not fire. A positional `replace(..., 1)` has the file's
    # line order as its subject, which is not the thing being tested.
    anchor = '                        commodity="gas",'
    assert source.count(anchor) == 1, (
        "the gas decide-call anchor is no longer unique — this mutation cannot "
        "be aimed at the site it claims"
    )
    mutated = source.replace(anchor, '                        commodity="electricity",', 1)
    assert mutated != source, "mutation did not apply — the anchor moved"
    labels = {
        _kwargs(c)["commodity"].value
        for c in _decide_calls(mutated)
        if isinstance(_kwargs(c)["commodity"], ast.Constant)
    }
    assert labels != {"electricity", "gas"}, (
        "control 3 did not see the mislabel — it cannot fail (R15)"
    )


def test_control_3_the_world_no_longer_imports_the_three_cut_modules():
    source = open(RUN_MODULE_PATH, encoding="utf-8").read()
    tree = ast.parse(source)
    imported = {
        node.module
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module
    }
    for gone in (
        "company.trading.forward_book",
        "company.trading.hedge_decision",
        "company.risk.hedge_policy",
    ):
        assert gone not in imported, f"{gone} is back — the cut regressed"
    assert "company.interfaces.hedge_desk" in imported


# ---------------------------------------------------------------------------
# CONTROL 4 — one book, four surfaces.
# ---------------------------------------------------------------------------


def _open_one(desk) -> None:
    desk.open_term_hedge(
        customer_id="C-001",
        term_start=TERM_START,
        term_end=TERM_END,
        volume_kwh=ELEC_EAC_KWH,
        forward_price_gbp_per_mwh=ELEC_FWD,
        hedge_fraction=0.9,
        term_days=TERM_DAYS,
    )


def test_control_4_open_settle_book_and_summary_are_the_same_book():
    desk = impl.build_hedge_desk()
    assert desk.summary()["contract_count"] == 0, "vacuity: the book starts empty"
    _open_one(desk)

    # .book — the surface the collateral door (§3n) marks.
    assert desk.book.contract_count == 1
    contracts = desk.book.all_contracts()
    assert contracts[0].customer_id == "C-001"

    # .summary() — the surface the report publishes.
    assert desk.summary()["contract_count"] == 1

    # settle — must find the contract just opened, i.e. non-zero P&L off spot.
    pnl = desk.settle_period_pnl_gbp("C-001", TERM_START, 1_000.0, ELEC_FWD - 20.0)
    assert pnl == pytest.approx(20.0 * (1_000.0 / 1000.0) * 0.9)
    assert desk.book.total_pnl_gbp == pytest.approx(pnl)
    assert desk.summary()["total_hedge_pnl_gbp"] == pytest.approx(round(pnl, 2))


def test_mutation_control_4_fires_when_the_book_surface_is_a_second_book():
    """The defect: `.book` returns a fresh TradingBook, so the collateral desk
    marks an empty book while the report shows a full one."""
    desk = impl.build_hedge_desk()
    _open_one(desk)
    assert desk.book.contract_count == 1

    class _SplitBrainDesk(impl.HedgeDesk):
        @property
        def book(self):  # <-- THE DEFECT
            return TradingBook()

    mutated = _SplitBrainDesk()
    _open_one(mutated)
    assert mutated.summary()["contract_count"] == 1
    assert mutated.book.contract_count == 0, (
        "the mutation did not split the book — control 4 could not fail on it"
    )


def test_control_4_the_execution_arithmetic_matches_the_pre_cut_inlined_block():
    """Notional, bid-ask and rounding, transcribed from run_phase2b.py at 21ad5aeea."""
    hf = 0.9
    tenor_years = TERM_DAYS / 365.25
    notional_mwh = (ELEC_EAC_KWH / 1000.0) * hf
    bid_ask = compute_bid_ask_cost(ELEC_FWD, tenor_years) * notional_mwh

    desk = impl.build_hedge_desk()
    contract = desk.open_term_hedge(
        customer_id="C-001",
        term_start=TERM_START,
        term_end=TERM_END,
        volume_kwh=ELEC_EAC_KWH,
        forward_price_gbp_per_mwh=ELEC_FWD,
        hedge_fraction=hf,
        term_days=TERM_DAYS,
    )
    assert contract.notional_mwh == notional_mwh
    assert contract.agreed_price_gbp_per_mwh == ELEC_FWD
    assert contract.hedge_fraction == hf
    assert contract.bid_ask_cost_gbp == round(bid_ask, 4)
    assert bid_ask > 0.0, "vacuity: a zero spread would make the rounding check free"


def test_mutation_control_4_fires_when_the_notional_ignores_the_hedge_fraction():
    """The defect: hedge the whole EAC rather than the hedged share of it."""
    hf = 0.9
    correct = (ELEC_EAC_KWH / 1000.0) * hf
    mutated = ELEC_EAC_KWH / 1000.0
    desk = impl.build_hedge_desk()
    contract = desk.open_term_hedge(
        customer_id="C-001",
        term_start=TERM_START,
        term_end=TERM_END,
        volume_kwh=ELEC_EAC_KWH,
        forward_price_gbp_per_mwh=ELEC_FWD,
        hedge_fraction=hf,
        term_days=TERM_DAYS,
    )
    assert contract.notional_mwh == correct
    assert mutated != correct, "vacuity: hf=1 would make the mutation a no-op"


# ---------------------------------------------------------------------------
# The roll — the backward-looking arm of the same desk.
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "current, naked_net, actual_net",
    [
        (0.90, 100.0, 400.0),   # hedge beat naked → raise
        (0.95, 400.0, 100.0),   # naked beat hedge → trim, floored at the mandate
        (0.90, 100.0, 102.0),   # within tolerance → hold
    ],
)
def test_the_roll_reproduces_the_pre_cut_call(current, naked_net, actual_net):
    expected = company_evolve_hedge_fraction(current, naked_net, actual_net)
    got = impl.build_hedge_desk().roll_hedge_fraction(current, naked_net, actual_net)
    assert got == expected


def test_the_roll_never_falls_below_the_mandate_floor():
    desk = impl.build_hedge_desk()
    hf = 1.0
    for _ in range(20):
        hf, _reason = desk.roll_hedge_fraction(hf, 10_000.0, 0.0)
    assert hf == pytest.approx(COMPANY_MIN_HEDGE_FLOOR)
    assert hf == pytest.approx(desk.mandate.minimum_hedged_fraction)
