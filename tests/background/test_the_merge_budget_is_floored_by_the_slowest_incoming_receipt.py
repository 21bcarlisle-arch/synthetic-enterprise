"""The reconciler's merge may run as long as its base PLUS the slowest incoming receipt's test leg.

The defect (2026-09-29): `f997f8bf7` landed with a 1570 s test leg, and the merge that closes the
fork carries its subject, so a fixed 25-minute limit killed every cadence's merge and the shared
tree fell 24 -> 37 behind origin with the log reading only `ERROR: TimeoutExpired`.
"""
from __future__ import annotations

import subprocess
from pathlib import Path

from background import origin_reconcile as o

RECEIPT = ("the value-cycle artefact carries each account's arrears lines\n\n[surgical-land receipt]\n"
           "gate-rc: 0\ntests: 1427 passed, 2 skipped in 1570.17s (0:26:10)\n")
QUICK = "a small landing\n\n[surgical-land receipt]\ntests: 1221 passed, 2 skipped in 228.29s (0:03:48)\n"


def _log(*entries: tuple[str, str]) -> str:
    return "".join("{}\x00{}\x01".format(sha, body) for sha, body in entries)


def test_the_budget_can_extend_and_can_stay_at_the_base():
    """Both branches are reachable: a slow receipt extends it, no receipt leaves the base."""
    extended, why = o.merge_budget(Path("."), log_fn=lambda: _log(("f997f8bf7", RECEIPT)))
    plain, plain_why = o.merge_budget(Path("."), log_fn=lambda: _log(("abc", "no receipt here\n")))
    assert extended > o.MERGE_TIMEOUT_SECONDS and plain == o.MERGE_TIMEOUT_SECONDS
    assert extended == o.MERGE_TIMEOUT_SECONDS + 1570
    assert "f997f8bf7" in why and "no incoming receipt" in plain_why


def test_the_slowest_receipt_sets_the_floor_not_the_last_or_the_first():
    budget, why = o.merge_budget(Path("."), log_fn=lambda: _log(
        ("quick1", QUICK), ("f997f8bf7", RECEIPT), ("quick2", QUICK)))
    assert budget == o.MERGE_TIMEOUT_SECONDS + 1570 and "f997f8bf7" in why


def _diverged(**kw):
    return o.reconcile(
        Path("."), worktree=Path("/nonexistent-reconcile-wt"), state_fn=lambda p: (37, 3),
        gate_fn=lambda p: False, make_worktree=lambda p, w: (True, ""),
        drop_worktree=lambda p, w: None, **kw)


def test_the_production_merge_is_handed_the_budget(monkeypatch):
    """The chain, not the helper: the default runner receives what `merge_budget` computed."""
    seen = {}

    def fake_run_merge(worktree, timeout=o.MERGE_TIMEOUT_SECONDS):
        seen["timeout"] = timeout
        raise subprocess.TimeoutExpired("surgical_land", timeout)

    monkeypatch.setattr(o, "_run_merge", fake_run_merge)
    _diverged(budget_fn=lambda p: (3070, "base 1500s + 1570s (f997f8bf7's receipt)"))
    assert seen["timeout"] == 3070


def test_a_timed_out_merge_names_its_budget_and_the_receipt_behind_it():
    def runner(worktree):
        raise subprocess.TimeoutExpired("surgical_land", 3070)

    out = _diverged(runner=runner, budget_fn=lambda p: (3070, "base 1500s + 1570s (f997f8bf7's receipt)"))
    assert out["status"] == o.ERROR and out["pushed"] is False
    assert "3070s" in out["detail"] and "f997f8bf7" in out["detail"]
