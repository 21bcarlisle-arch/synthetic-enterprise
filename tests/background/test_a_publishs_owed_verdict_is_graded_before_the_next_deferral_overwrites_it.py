"""The defect: one failed push held the public banner at "PUBLISHING IS FAILING" through six
successful publishes (2026-09-25 17:10Z to 2026-09-26 05:54Z).

The deferral file holds ONE outstanding delivery. Each cycle's publisher wrote its own commit into
it before the router's `grade_outstanding_delivery` ran, so the router graded a commit one second
old (ABSORBING, nothing written), and the previous commit, which the reconciler had delivered, was
never graded REACHED. `episode_clean_publishes` stayed 0 and the failure was never cleared.
"""
from __future__ import annotations

import ast
import functools
import json
from pathlib import Path

from background import process_run_complete as prc
from background import publish_delivery_deferral as pdd

WINDOW = 2700.0


def _run(tmp_path, monkeypatch, *, previous_reached):
    p = tmp_path / "deferral.json"
    p.write_text(json.dumps({"ts": 1000.0, "sha": "PREVIOUS", "git_hash": "g", "evidence": "x"}))
    monkeypatch.setattr(prc, "PUBLISH_DELIVERY_DEFERRAL_FILE", p)
    monkeypatch.setattr(prc, "_record_push_time", lambda *a, **k: None)
    monkeypatch.setattr(prc, "_record_content_published", lambda *a, **k: None)
    calls = {"success": 0}
    grade = functools.partial(
        prc.grade_outstanding_delivery, now=1100.0, fetch_fn=lambda: None,
        remote_head_fn=lambda: "TIP", ancestor_fn=lambda a, b, **k: previous_reached,
        benign_fn=lambda: WINDOW,
        success_fn=lambda: calls.__setitem__("success", calls["success"] + 1),
        failure_fn=lambda *a, **k: None)
    status = prc._grade_the_owed_delivery_before_it_is_overwritten(grade_fn=grade)
    return status, calls


def test_the_previous_commit_is_graded_before_its_record_is_replaced_both_ways(tmp_path, monkeypatch):
    """Partition in one control: REACHED records the clean publish, ABSORBING records nothing.
    A helper that recorded nothing, or recorded unconditionally, fails one leg."""
    reached, reached_calls = _run(tmp_path, monkeypatch, previous_reached=True)
    absorbing, absorbing_calls = _run(tmp_path, monkeypatch, previous_reached=False)
    assert (reached, reached_calls["success"]) == (pdd.REACHED, 1), (reached, reached_calls)
    assert (absorbing, absorbing_calls["success"]) == (pdd.ABSORBING, 0), (absorbing, absorbing_calls)


def test_a_grading_error_never_costs_the_current_cycle_its_deferral():
    def boom():
        raise RuntimeError("remote unreadable")
    assert prc._grade_the_owed_delivery_before_it_is_overwritten(grade_fn=boom) is None


def test_the_grading_sits_directly_before_the_only_write_that_can_lose_the_verdict():
    """ORDER IS THE WHOLE REPAIR. Mutation: move the call after `record(...)`, or delete it, and
    this reds -- the write would replace the previous commit before anything asked about it."""
    tree = ast.parse(Path(prc.__file__).read_text())
    found = 0
    for node in ast.walk(tree):
        body = getattr(node, "body", None)
        if not isinstance(body, list):
            continue
        for i, stmt in enumerate(body):
            if isinstance(stmt, ast.If) and "publish_delivery_deferral.record(" in ast.unparse(stmt.test):
                found += 1
                prev = ast.unparse(body[i - 1]) if i else ""
                assert prev.strip() == "_grade_the_owed_delivery_before_it_is_overwritten()", prev
    assert found == 1, f"expected exactly one deferral write in process_run_complete, found {found}"
