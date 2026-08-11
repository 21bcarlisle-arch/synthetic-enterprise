"""The customer-value seam's contract — and the ways this cut could rot silently.

WHY THIS FILE EXISTS (R15: a control must be able to FAIL on its own named defect)
---------------------------------------------------------------------------------
KNIFE pass 3, `A_composition_lift` step 15, moved the supplier's customer-value
layer out of `simulation/run_phase4c_on_phase2b.py::main()` into
`company/analytics/customer_value_view.py` behind
`company/interfaces/customer_value.py` — four wall crossings
(`saas.cost_to_serve`, `saas.churn_model`, `saas.home_move_win_rate`,
`saas.enterprise_value`).

The epistemic-wall ratchet polices the STATIC half: a module-scope
`company.analytics.customer_value_view -> simulation.*` import is a new class-(a)
edge, the forbidden direction, and reds the suite. Three things it cannot see:

1. **A lazy import.** The ratchet covers static imports only; an in-function
   `import simulation.…` escapes it. The natural convenience change here is for
   the view to reach for the run's own customer list rather than be handed it —
   `_get_all_customers()` is right there in the world module. So control 1 is
   BEHAVIOURAL: it builds a real view in a clean interpreter and asks which
   modules the import system actually loaded.

2. **A silently reordered or dropped builder.** The claim this cut rests on is
   that the five moved calls run with the same arguments as the code they
   replaced. Nothing static sees a builder dropped, and the effect is not a
   crash — it is a different enterprise value. Control 2 replicates the PRE-CUT
   inlined sequence transcribed from the source it was lifted out of (not from
   the module under test, which would be a mirror) and asserts every one of the
   five outputs is identical.

3. **THE CALL-SITE MOVE, and it is the one this cut actually introduces.** Four
   of the five builders were adjacent in `main()`. The fifth,
   `build_cost_to_serve_ledger_events`, was called ~50 lines LATER, just above
   the accounting close. Folding it into the view moves its call site EARLIER.
   That is behaviour-identical only while nothing in between mutates or rebinds
   the record list it reads — today nothing does, but "I read the file" is not a
   control, and a future edit that appends a late-arriving record between those
   two points would silently change the account-6100 schedule while every test
   above stayed green. Control 3 is an AST check over `main()` itself, with a
   vacuity guard (a region of zero statements would make it pass for free) and a
   mutation that performs exactly that append.

Each `test_mutation_*` performs the named defect rather than asserting it is
impossible.
"""

from __future__ import annotations

import ast
import json
import os
import subprocess
import sys
import textwrap

import pytest

from company.analytics import customer_value_view as impl
from company.interfaces import customer_value as door

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
RUN_MODULE_PATH = os.path.join(REPO_ROOT, "simulation", "run_phase4c_on_phase2b.py")

PRICE_DIFFERENTIAL_PCT = 0.0  # the run module's own value, at its own name


# ---------------------------------------------------------------------------
# Fixtures — the smallest input that exercises every moved builder.
#
# `build_churn_risk` needs 12+ months of history before a renewal point exists
# at all (yoy mode), and `build_enterprise_value` excludes accounts with no
# renewal points — so a short book would leave the portfolio EMPTY and every
# identity assertion below would compare {} against {}. Two years of monthly
# records, and the vacuity guard asserts the book is non-empty.
# ---------------------------------------------------------------------------


def _customers() -> list[dict]:
    return [
        {
            "customer_id": "C1",
            "segment": "resi",
            "acquisition_date": "2022-06-15",
            "epc_rating": "C",
        },
        {
            "customer_id": "C2",
            "segment": "SME",
            "acquisition_date": "2022-09-01",
            "epc_rating": "E",
        },
    ]


def _records() -> list[dict]:
    """Two years of monthly settled records for two accounts, with a deliberate
    step-change in year 2 for C1 so the yoy bill-shock signal actually fires —
    a book in which no shock ever triggers makes `churn_probability` constant
    and the reorder/drop mutations below unobservable."""
    records = []
    for year, month_scale in (("2023", 1.0), ("2024", 1.6)):
        for month in range(1, 13):
            date = f"{year}-{month:02d}-14"
            for customer_id, base, scale in (
                ("C1", 120.0, month_scale),
                ("C2", 300.0, 1.0),
            ):
                revenue = round(base * scale, 2)
                wholesale = round(revenue * 0.62, 2)
                records.append(
                    {
                        "customer_id": customer_id,
                        "settlement_date": date,
                        "settlement_period": 1,
                        "commodity": "electricity",
                        "revenue_gbp": revenue,
                        "wholesale_cost_gbp": wholesale,
                        "margin_gbp": round(revenue - wholesale, 2),
                        "consumption_kwh": 400.0,
                    }
                )
    return records


@pytest.fixture()
def view():
    return door.build_customer_value_view(
        _records(), _customers(), PRICE_DIFFERENTIAL_PCT
    )


def test_the_fixture_is_not_vacuous(view):
    """Every identity control below compares structures built from this book. If
    the book produced no renewal points, they would all compare empty against
    empty and pass for free — the population-control vacuity shape."""
    assert view.churn_risk, "no accounts scored — the identity controls are vacuous"
    assert any(view.churn_risk.values()), "no renewal points — nothing to value"
    assert view.enterprise_value["portfolio"]["account_count"] > 0
    assert view.cost_to_serve["portfolio"]["cost_to_serve_gbp"] > 0
    assert view.cost_to_serve_ledger_events, "no 6100 postings — control 2 is vacuous"


# ---------------------------------------------------------------------------
# The door
# ---------------------------------------------------------------------------


def test_the_door_re_exports_the_implementation():
    assert door.build_customer_value_view is impl.build_customer_value_view
    assert door.CustomerValueView is impl.CustomerValueView
    assert set(door.__all__) == {"CustomerValueView", "build_customer_value_view"}


def test_the_run_module_reaches_the_view_only_through_the_door():
    """The world imports the seam, not the implementation and not the four
    modules the view was lifted out of."""
    source = open(RUN_MODULE_PATH).read()
    assert (
        "from company.interfaces.customer_value import build_customer_value_view"
        in source
    )
    for forbidden in (
        "company.analytics.customer_value_view",
        "from saas.cost_to_serve import",
        "from saas.churn_model import",
        "from saas.home_move_win_rate import",
        "from saas.enterprise_value import",
    ):
        assert forbidden not in source, f"{forbidden} is reachable from the run module again"


# ---------------------------------------------------------------------------
# CONTROL 1 — the view must not reach back across the wall, statically OR lazily
# ---------------------------------------------------------------------------


_PROBE = textwrap.dedent(
    """
    import json, sys
    sys.path.insert(0, {root!r})
    from company.interfaces.customer_value import build_customer_value_view
    inputs = json.loads(sys.stdin.read())
    build_customer_value_view(inputs["records"], inputs["customers"], inputs["pd"])
    print(json.dumps(sorted(
        m for m in sys.modules
        if m == "simulation" or m.startswith("simulation.")
        or m == "sim" or m.startswith("sim.")
    )))
    """
)


def _run_probe(probe: str) -> list[str]:
    payload = json.dumps(
        {
            "records": _records(),
            "customers": _customers(),
            "pd": PRICE_DIFFERENTIAL_PCT,
        }
    )
    result = subprocess.run(
        [sys.executable, "-c", probe],
        input=payload,
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
        timeout=300,
    )
    assert result.returncode == 0, result.stderr
    return json.loads(result.stdout.strip().splitlines()[-1])


def test_building_the_view_loads_no_world_module():
    """Behavioural, not static: a real build in a clean interpreter, then ask
    which modules the import system actually loaded. An in-function
    `import simulation.…` is invisible to the ratchet and visible here."""
    assert _run_probe(_PROBE.format(root=REPO_ROOT)) == []


def test_mutation_a_lazy_world_import_inside_the_view_is_caught():
    """Perform the defect: reach for the world's customer list from inside the
    view, the way a convenience default would. The static ratchet stays green;
    control 1 fires."""
    mutated = _PROBE.format(root=REPO_ROOT).replace(
        "from company.interfaces.customer_value import build_customer_value_view",
        "from company.interfaces.customer_value import build_customer_value_view as _b\n"
        "def build_customer_value_view(*a, **k):\n"
        "    import simulation.meter_reads  # noqa: F401  <- the defect\n"
        "    return _b(*a, **k)",
    )
    loaded = _run_probe(mutated)
    assert loaded, "the lazy world import was not observed — control 1 is blind"
    assert any(m.startswith("simulation") for m in loaded)


# ---------------------------------------------------------------------------
# CONTROL 2 — the moved composition is the composition that was lifted
# ---------------------------------------------------------------------------


def _pre_cut_sequence(records, customers, price_differential_pct):
    """The inlined customer-value layer EXACTLY as
    `simulation/run_phase4c_on_phase2b.py::main()` ran it before step 15 —
    transcribed from that source, not from the module under test, which is what
    makes this a characterization and not a mirror.

    Note the two call sites are reproduced in their PRE-CUT order, with the
    ledger-event call last, where it sat.
    """
    from saas.churn_model import build_churn_risk
    from saas.cost_to_serve import build_cost_to_serve, build_cost_to_serve_ledger_events
    from saas.enterprise_value import build_enterprise_value
    from saas.home_move_win_rate import build_home_move_win_rates

    cost_to_serve = build_cost_to_serve(records, customers)
    churn_risk = build_churn_risk(records, customers)
    home_move_win_rates = build_home_move_win_rates(
        churn_risk, customers, price_differential_pct
    )
    enterprise_value = build_enterprise_value(
        churn_risk, cost_to_serve, customers, price_differential_pct
    )
    # ... ~50 lines of printing in between, then:
    cost_to_serve_ledger_events = build_cost_to_serve_ledger_events(records, customers)
    return {
        "cost_to_serve": cost_to_serve,
        "churn_risk": churn_risk,
        "home_move_win_rates": home_move_win_rates,
        "enterprise_value": enterprise_value,
        "cost_to_serve_ledger_events": cost_to_serve_ledger_events,
    }


def test_the_view_is_identical_to_the_sequence_it_replaced(view):
    expected = _pre_cut_sequence(_records(), _customers(), PRICE_DIFFERENTIAL_PCT)
    assert view.cost_to_serve == expected["cost_to_serve"]
    assert view.churn_risk == expected["churn_risk"]
    assert view.home_move_win_rates == expected["home_move_win_rates"]
    assert view.enterprise_value == expected["enterprise_value"]
    assert view.cost_to_serve_ledger_events == expected["cost_to_serve_ledger_events"]


def test_mutation_dropping_the_home_move_adjustment_is_caught(view):
    """Perform the defect: value the book on RAW churn instead of home-move
    adjusted churn — the single most plausible wrong simplification when
    recomposing these four, and one that produces a perfectly plausible number.
    Control 2 fires on the enterprise value."""
    from saas.clv_model import build_clv

    unadjusted = build_clv(view.churn_risk, view.cost_to_serve, n_draws=500, random_seed=42)
    wrong = {
        "by_customer": unadjusted,
        "portfolio": {
            "enterprise_value_gbp": sum(e["clv_gbp"] for e in unadjusted.values()),
            "account_count": len(unadjusted),
        },
    }
    assert wrong != view.enterprise_value, (
        "raw and home-move-adjusted churn produce the same enterprise value on "
        "this fixture — the control cannot discriminate and the book needs a "
        "non-zero churn probability"
    )


def test_mutation_price_differential_is_actually_read(view):
    """A parameter threaded through a seam and then ignored is the donated-
    residual shape: the signature says the run controls its market position, and
    nothing checks that it does. Move it and the view must move."""
    moved = door.build_customer_value_view(_records(), _customers(), 0.10)
    assert moved.home_move_win_rates != view.home_move_win_rates
    assert moved.enterprise_value != view.enterprise_value


# ---------------------------------------------------------------------------
# CONTROL 3 — the call-site move is only safe while the record list is untouched
# ---------------------------------------------------------------------------


def _main_body() -> list[ast.stmt]:
    tree = ast.parse(open(RUN_MODULE_PATH).read())
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name == "main":
            return node.body
    raise AssertionError("run_phase4c_on_phase2b.main() not found")


def _statements_between_the_view_and_the_close(body: list[ast.stmt]) -> list[ast.stmt]:
    """The region of `main()` the ledger-event call was moved ACROSS: from the
    `build_customer_value_view(...)` call down to the `close_the_books(...)`
    call that consumes its 6100 schedule."""
    start = end = None
    for index, statement in enumerate(body):
        names = {
            n.func.id
            for n in ast.walk(statement)
            if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)
        }
        if start is None and "build_customer_value_view" in names:
            start = index
        elif start is not None and "close_the_books" in names:
            end = index
            break
    assert start is not None, "the view call was not found in main()"
    assert end is not None, "the close call was not found after the view call"
    return body[start + 1 : end]


def _record_list_mutations(statements: list[ast.stmt]) -> list[str]:
    """Every statement in the region that could change what `all_records` holds:
    a method call that mutates it in place, an item/slice assignment into it, or
    a rebinding of the name itself."""
    mutating_methods = {"append", "extend", "insert", "pop", "remove", "clear", "sort", "reverse"}
    found = []
    for statement in statements:
        for node in ast.walk(statement):
            if (
                isinstance(node, ast.Call)
                and isinstance(node.func, ast.Attribute)
                and isinstance(node.func.value, ast.Name)
                and node.func.value.id == "all_records"
                and node.func.attr in mutating_methods
            ):
                found.append(f"line {node.lineno}: all_records.{node.func.attr}()")
            if isinstance(node, (ast.Assign, ast.AugAssign, ast.For)):
                targets = node.targets if isinstance(node, ast.Assign) else [node.target]
                for target in targets:
                    if isinstance(target, ast.Name) and target.id == "all_records":
                        found.append(f"line {node.lineno}: all_records rebound")
                    if (
                        isinstance(target, ast.Subscript)
                        and isinstance(target.value, ast.Name)
                        and target.value.id == "all_records"
                    ):
                        found.append(f"line {node.lineno}: all_records[...] assigned")
    return found


def test_the_region_the_ledger_call_moved_across_is_not_empty():
    """VACUITY GUARD. Control 3 checks a REGION of `main()`; if that region were
    empty the check would pass for free and stop being evidence of anything. It
    is not empty today (the printing block sits there), and if a future refactor
    empties it, this fails loudly and control 3 should be retired rather than
    left as decoration."""
    region = _statements_between_the_view_and_the_close(_main_body())
    assert len(region) > 5, (
        f"only {len(region)} statements between the view and the close — control 3 "
        "no longer has a region to police"
    )


def test_nothing_between_the_view_and_the_close_touches_the_record_list():
    """The identity claim for moving `build_cost_to_serve_ledger_events` EARLIER
    is that its inputs are the same at both points. This is that claim as a
    check rather than a reading of the file."""
    region = _statements_between_the_view_and_the_close(_main_body())
    assert _record_list_mutations(region) == []


def test_mutation_a_late_record_append_between_the_two_points_is_caught():
    """Perform the defect: a record arriving after the view is built but before
    the close. Pre-cut, the 6100 schedule would have included it; post-cut it
    would not — and no other test in this file, or in the suite, would notice."""
    source = open(RUN_MODULE_PATH).read()
    anchor = "    cost_to_serve_ledger_events = "
    if anchor not in source:
        anchor = "    books = close_the_books("
    assert anchor in source, "no injection point found — the mutation cannot be performed"
    mutated = source.replace(
        anchor,
        "    all_records.append({'customer_id': 'C_LATE'})  # <- the defect\n" + anchor,
        1,
    )
    tree = ast.parse(mutated)
    body = next(
        node.body
        for node in tree.body
        if isinstance(node, ast.FunctionDef) and node.name == "main"
    )
    region = _statements_between_the_view_and_the_close(body)
    found = _record_list_mutations(region)
    assert found, "the injected append was not detected — control 3 is blind"
    assert any("append" in f for f in found)
