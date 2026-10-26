"""A publish landing fast-forwards onto origin right before each attempt (2026-10-26).

The defect: a shared tree one commit behind origin with nothing of its own was admitted by
`_divergence_refusal` as disjoint, so no fast-forward ran, and `surgical_land` refused the landing
because a primary checkout behind origin may not commit. The Monday publish of run 4ae8da9b0f ended
`commit_refused`, and nothing was gated.

MUTATION: delete either `_level_with_origin_before_landing(...)` call in `_land_publish_commit`;
the ordering assertion below goes red for that attempt.
"""
from background import process_run_complete as prc


def test_each_landing_attempt_is_preceded_by_the_wait_and_then_the_advance(monkeypatch):
    from tools import surgical_land

    events = []

    class Lost(Exception):
        parent, observed = "a" * 40, "b" * 40

    def fake_land(root, paths, message, attempts=None, on_lost=None, **kw):
        events.append("land")
        on_lost(1, Lost())          # attempt 1 lost the compare-and-swap
        events.append("land")
        return "f" * 40

    monkeypatch.setattr(prc, "log", lambda *a, **k: None)
    monkeypatch.setattr(prc, "_record_commit_hook_duration", lambda *a, **k: None)
    monkeypatch.setattr(prc, "_wait_for_a_quiet_tree",
                        lambda *a, **k: (events.append("wait"), {"waited_seconds": 0})[1])
    monkeypatch.setattr(prc, "_advance_to_origin_or_say_why",
                        lambda *a, **k: (events.append("advance"),
                                         {"advanced": True, "reason": "ff"})[1])
    monkeypatch.setattr(surgical_land, "land", fake_land)

    out = prc._land_publish_commit([str(prc.PROJECT_DIR / "site" / "data" / "dashboard.json")],
                                   "msg", "abc1234")
    assert out["sha"] == "f" * 40, out
    assert events == ["wait", "advance", "land", "wait", "advance", "land"], (
        "the fast-forward must sit between the quiet-tree wait and EACH landing attempt: origin "
        "moves during the wait, and a primary checkout behind origin is refused by the door")
