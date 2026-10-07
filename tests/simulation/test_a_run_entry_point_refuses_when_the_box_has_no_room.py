"""A run entry point refuses to start when MemAvailable is below the run's budgeted peak.

The director's ask, 2026-10-07, after the box fell to 1.6 GB of 24 GB free at 11:52Z with two runs
started by `setsid` around `launch_long_job`'s admission door. So the refusal is asserted at the
entry points themselves: `python3 -m simulation.run_phase2b` and `tools.run_value_cycle_ab`'s
ordinary A/B. Each side is tested at the live price +/- 1 MB, so the control follows the curve and
the budget rather than a number copied out of them today.
"""
from __future__ import annotations

import ast
import inspect

import pytest

from simulation import run_phase2b
from tools import run_value_cycle_ab as rvca


def _box(available_mb):
    return lambda: {"available_mb": available_mb, "total_mb": 24032.1, "swap_free_mb": 0.0}


def _price():
    peak, basis = run_phase2b.budgeted_run_peak_mb()
    assert peak is not None, f"the run's peak could not be priced: {basis}"
    return peak


def _main_block_calls():
    """The calls the module's `if __name__ == "__main__":` block makes, by name."""
    tree = ast.parse(inspect.getsource(run_phase2b))
    block = next(node for node in tree.body if isinstance(node, ast.If)
                 and "__main__" in ast.unparse(node.test))
    return {ast.unparse(call.func) for node in block.body for call in ast.walk(node)
            if isinstance(call, ast.Call)}


def test_the_phase2b_entry_point_REFUSES_below_the_budgeted_peak(monkeypatch):
    """Fires on: the check removed from `cli`; `__main__` calling `main()` around `cli`; or the
    comparison keyed to anything looser than the budgeted peak. The default sampler is the one
    patched, so the production read is the one exercised."""
    import background.resource_headroom as rh

    monkeypatch.setattr(rh, "sample", _box(_price() - 1))
    started = []
    assert run_phase2b.cli(main_fn=lambda: started.append(True)) == 2
    assert started == []
    calls = _main_block_calls()
    assert "cli" in calls and "main" not in calls, (
        f"`python3 -m simulation.run_phase2b` must start through cli(); its block calls {calls}")


def test_the_phase2b_entry_point_STILL_STARTS_with_room():
    """Fires on a guard that refuses everything, or one keyed above the budgeted peak."""
    started = []
    rc = run_phase2b.cli(main_fn=lambda: started.append(True), sample_fn=_box(_price() + 1))
    assert (rc, started) == (0, [True])


def test_an_unpriced_run_is_refused_and_says_why():
    reason = run_phase2b.entry_headroom_refusal(
        sample_fn=_box(10**6), peak_fn=lambda: (None, "no curve on disk"))
    assert reason and "no curve on disk" in reason


class _Started(Exception):
    pass


def _ab(monkeypatch, tmp_path, available_mb):
    monkeypatch.setattr(rvca, "_headroom_sample", _box(available_mb))
    monkeypatch.setattr(rvca, "running_floor_legs", lambda: [])

    def started(**kwargs):
        raise _Started

    monkeypatch.setattr(rvca, "run_value_cycle_ab", started)
    return rvca.main(["--level-arm", "--out", str(tmp_path / "ab.json")])


def test_the_ordinary_ab_REFUSES_below_its_measured_peak(monkeypatch, tmp_path):
    """Fires on: the ordinary A/B branch losing its check (it had none until 2026-10-07)."""
    assert _ab(monkeypatch, tmp_path, rvca.FLOOR_RUN_PEAK_MB - 1) == 2


def test_the_ordinary_ab_STILL_STARTS_with_room(monkeypatch, tmp_path):
    with pytest.raises(_Started):
        _ab(monkeypatch, tmp_path, rvca.FLOOR_RUN_PEAK_MB + 1)
