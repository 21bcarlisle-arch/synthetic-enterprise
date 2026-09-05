"""R1: the payment observable reaches a LIVE DECISION, not just the belief function.

Each test names the defect it exists to catch.

THE DEFECT THIS FILE EXISTS FOR, and it was reported to the director as done when it was not.
`99d2befb4` gave `enriched_churn_estimate` a `payment_method` argument and proved the belief moves
with it. The live path -- `tools/run_live_decisions._retention_ev`, the only production caller --
never passed one, so `payment_method_engagement_factor(None)` returned 1.0 on all 145 accounts and
the observable stopped dead at the wall it had just crossed. "Reachable is not chosen" applied to a
seam rather than to the draw.
"""
from __future__ import annotations

from tools import project_portfolio_to_2026 as portfolio
from tools.run_live_decisions import _retention_ev

_ARGS = dict(segment="resi", fuel="electricity", expected_margin=50.0,
             clock_date_str="2026-09-05")


def _customer(**over):
    base = {"cid": "PROS-2017-0130", "commodity": "electricity",
            "eac_kwh_per_year": 3000.0, "hedge_fraction": 0.8}
    base.update(over)
    return base


def test_the_live_decision_moves_with_the_payment_method():
    """THE DEFECT. Measured on the real book at the time of writing: prepayment churn 0.1101 ->
    0.0644 (0.58x), direct debit 0.1116 -> 0.1179. All 145 accounts moved."""
    ppm, _ = _retention_ev(400.0, 420.0, _customer(payment_method="prepayment"), **_ARGS)
    dd, _ = _retention_ev(400.0, 420.0, _customer(payment_method="direct_debit"), **_ARGS)

    assert ppm is not None and dd is not None
    assert ppm < dd * 0.75, (
        f"prepayment ({ppm}) must read as materially less likely to leave than direct debit "
        f"({dd}) once the observable reaches the decision -- Ofgem CIM w6 puts the annual "
        f"switching rates at 3.1% and 5.6%"
    )


def test_a_record_without_the_observable_is_bit_for_bit_unchanged():
    """The branch that protects every account whose payment method cannot be established. Without
    it the factor could apply a blanket shift to the whole book and the test above still passes."""
    absent, _ = _retention_ev(400.0, 420.0, _customer(), **_ARGS)
    explicit_none, _ = _retention_ev(400.0, 420.0, _customer(payment_method=None), **_ARGS)

    assert absent == explicit_none


def test_the_crm_record_carries_the_payment_method_and_it_varies():
    """A field written as a constant would satisfy "does it reach the decision" while making every
    decision identical -- the same failure the seam test guards one layer up."""
    seam = portfolio._live_seam()
    assert seam is not None, "the approved seam must be constructible in this tree"

    got = {portfolio._payment_method(seam, f"PROS-2017-{i:04d}", "electricity")
           for i in range(300)}

    assert got == {"direct_debit", "standard_credit", "prepayment"}, got


def test_an_unavailable_seam_yields_none_and_never_the_majority_channel():
    """FAIL-SAFE DIRECTION, and it is deliberately the OPPOSITE of the seam's own fallback --
    asserted here because the two look inconsistent side by side and a later reader would
    "fix" one of them.

    `LiveSimInterface.get_payment_method` falls to direct_debit: its argument is a broken CRM
    record for a customer the supplier is still billing. THIS falls to None: the question is
    whether the observable is available at all, and answering direct_debit for a portfolio the
    seam could not be built for would apply the direct-debit engagement factor to every account
    in the book while looking exactly like a measurement.
    """
    assert portfolio._payment_method(None, "PROS-2017-0130", "electricity") is None
    assert portfolio._payment_method(portfolio._live_seam(), "", "electricity") is None


def test_the_seam_is_reachable_when_the_generator_runs_AS_A_SCRIPT():
    """THIRD INSTANCE OF THIS DEFECT IN ONE SESSION, and the one that would have shipped silently.

    `python3 tools/project_portfolio_to_2026.py` puts `tools/` on `sys.path[0]`, not the repo root,
    so `_live_seam`'s `from company.interfaces.sim_interface import ...` raises ModuleNotFoundError.
    Measured before the guard: all 145 accounts written with `payment_method: None` by the real
    script, while the identical call answered correctly under pytest. The siblings were
    `tools/next_step_gate.py` and `tools/generate_project_state.py`.

    Every control was green in all three cases and structurally had to be: pytest fixes `sys.path`
    before any test can import the module, so no test that imports it can ever fail this way.
    `sys.path[0] = "tools"` reproduces script semantics; a plain `-c` leaves the CWD on the path and
    would pass with or without the guard.
    """
    import os
    import subprocess
    import sys as _sys

    from tools.project_portfolio_to_2026 import PROJECT

    done = subprocess.run(
        [_sys.executable, "-c",
         "import sys; sys.path[0] = 'tools';"
         "import runpy;"
         "m = runpy.run_path('tools/project_portfolio_to_2026.py', run_name='probe');"
         "print(m['_payment_method'](m['_live_seam'](), 'PROS-2017-0130', 'electricity'))"],
        cwd=str(PROJECT), capture_output=True, text=True, timeout=180,
        env={**os.environ, "PYTHONPATH": ""},
    )

    assert done.returncode == 0, done.stderr
    assert done.stdout.strip() in ("direct_debit", "standard_credit", "prepayment"), (
        f"the seam was unreachable when run as a script (got {done.stdout.strip()!r}); every "
        f"account would be written with payment_method: None. stderr: {done.stderr!r}"
    )


def test_the_generated_portfolio_actually_carries_the_field(tmp_path, monkeypatch):
    """END TO END through the real generator, because every test above could pass while
    `generate()` never wrote the key -- which is precisely how the argument came to exist with no
    caller in the first place."""
    import json

    from tools.project_portfolio_to_2026 import RUN_OUTPUT, generate

    if not RUN_OUTPUT.exists():
        import pytest
        pytest.skip("no run output in this tree")

    out = tmp_path / "live_portfolio.json"
    generate(out_path=out)
    got = json.loads(out.read_text())["customers"]

    assert got, "no customers generated"
    assert all("payment_method" in c for c in got)
    methods = {c["payment_method"] for c in got}
    assert len(methods) > 1, f"every account got the same payment method: {methods}"
