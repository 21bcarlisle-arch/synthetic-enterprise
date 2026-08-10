"""RUNG-4b STALE PUBLISHED GAP MEASUREMENT draw -- R15 both-ways proof (2026-08-10).

The mechanism: a coupled-gap ledger row whose PRODUCING CODE has changed since the measurement was
taken is a number on a public door produced by a program nobody runs. `gap_ledger_reconciler`
already detects that (report-only, G-R3) and pages through `reconcile_watch` -- but nothing could
ACT on it, so five consecutive worker ticks cleared the drift set BY HAND. That is the same shape
as the overnight operational-red incident one rung up: an alarm with no draw rung behind it.
`supervisor._stale_gap_row_draw()` is the rung; it is wired into `_self_refill_draw` below the
declared-defect backlog and mirrored in `_is_drained_and_gated`. Ownership rationale and the
alternatives rejected: `docs/design/GAP_TOOL_RERUN_OWNERSHIP.md`.

R15 requires a control that can FAIL. Proven BOTH ways here:
  * MUST FIRE: refreshable rows present -> the detector returns a draw naming the row and the
    command, `_self_refill_draw` returns it with every lane above it empty, and
    `_is_drained_and_gated` refuses rest.
  * MUST STAY SILENT: no refreshable rows (the clean state the fifth tick actually reached for the
    two fabric rows) -> None, and rest stays available. A rung that can only fire is a wedge.
  * MUST NOT WEDGE: `never_landed` / `never_measured` entries are not refreshable by any re-run,
    so they must not reach this rung -- otherwise it draws forever on work that cannot drain.

Every test injects its own work list; none reads the live ledger or live git
(feedback_new_draw_rung_needs_fixture_isolation).
"""
from background import gap_ledger_reconciler as glr
from background import supervisor


def _work(**over):
    w = {"item": "W2_4_household_budget", "status": "stale",
         "runners": ["tools/couple_w2_4_c6.py"],
         "command": "python3 -m tools.couple_w2_4_c6 --write-ledger",
         "no_runner": False, "detail": "1 commit(s) touched tools/couple_w2_4_c6.py since abc"}
    w.update(over)
    return w


def _lanes_above_are_empty(monkeypatch):
    """Neutralise every rung ABOVE 4b so a draw/rest decision is attributable to THIS rung."""
    monkeypatch.setattr(supervisor, "_publish_gate_wedge_active", lambda *a, **k: None)
    monkeypatch.setattr(supervisor, "_operational_red_persistent_draw", lambda *a, **k: None)
    monkeypatch.setattr(supervisor, "_maturity_map_draw_concurrent", lambda *a, **k: [])
    monkeypatch.setattr(supervisor, "_site_lane_draw_concurrent", lambda *a, **k: [])
    monkeypatch.setattr(supervisor, "_idle_discover_frame_draw_concurrent", lambda *a, **k: [])
    monkeypatch.setattr(supervisor, "_open_campaign_draw", lambda *a, **k: None)
    monkeypatch.setattr(supervisor, "_declared_defect_backlog_draw", lambda *a, **k: None)
    monkeypatch.setattr(supervisor, "_actionable_backlog_item", lambda *a, **k: None)
    monkeypatch.setattr(supervisor, "log", lambda *a, **k: None)


def _reconciler_says(monkeypatch, work):
    """Patch the module the rung lazily imports, so the rung's OWN code path runs end to end."""
    monkeypatch.setattr(glr, "reconcile", lambda *a, **k: [])
    monkeypatch.setattr(glr, "refresh_work", lambda *a, **k: list(work))


# ─────────────────────────────── MUST FIRE (a stale public number) ────────────────────────────

def test_fires_on_a_stale_row_and_names_the_command_that_would_clear_it():
    msg = supervisor._stale_gap_row_draw(work=[_work()])
    assert msg is not None
    assert "STALE-GAP-ROW" in msg
    assert "W2_4_household_budget" in msg
    assert "python3 -m tools.couple_w2_4_c6 --write-ledger" in msg


def test_the_draw_states_the_acceptance_test_is_the_row_reading_current_not_that_it_ran():
    """A command that ran is not evidence: the tools take arguments this rung does not model, so
    the acceptance test has to be the independent reconcile verdict."""
    msg = supervisor._stale_gap_row_draw(work=[_work()])
    assert "ACCEPTANCE is not that the command ran" in msg
    assert "CURRENT" in msg


def test_overflow_is_stated_never_silently_dropped():
    """The summary caps how many rows it spells out; a cap that hid the rest would under-report the
    work (no silent caps)."""
    many = [_work(item=f"W_row_{i}") for i in range(supervisor._STALE_GAP_SUMMARY_CAP + 3)]
    msg = supervisor._stale_gap_row_draw(work=many)
    assert f"{len(many)} published coupled-gap measurement(s)" in msg
    assert "+3 more" in msg


def test_a_row_with_no_invocable_producer_is_drawn_as_a_worse_defect_not_hidden():
    """A published number nobody can re-take is worse than a stale one. It must reach the tick as
    a defect to file, not vanish because there is no command to print."""
    msg = supervisor._stale_gap_row_draw(
        work=[_work(runners=[], command=None, no_runner=True, item="W9_orphan")])
    assert "NO INVOCABLE PRODUCER" in msg
    assert "W9_orphan" in msg
    assert "wants a\nfinding" in msg or "wants a finding" in msg


def test_self_refill_draw_returns_the_rung_when_every_lane_above_it_is_empty(monkeypatch):
    """WIRING, not assertion: the rung is in the real ladder. Its absence is the five-hand-re-run
    state this atom recorded on five consecutive ticks."""
    _lanes_above_are_empty(monkeypatch)
    _reconciler_says(monkeypatch, [_work()])
    out = supervisor._self_refill_draw()
    assert out is not None
    assert "STALE-GAP-ROW" in out


def test_is_drained_and_gated_refuses_rest_while_a_stale_row_is_refreshable(monkeypatch):
    _lanes_above_are_empty(monkeypatch)
    _reconciler_says(monkeypatch, [_work()])
    assert supervisor._is_drained_and_gated() is False


# ────────────────────────── MUST STAY SILENT (the rung can drain) ─────────────────────────────

def test_silent_when_nothing_is_refreshable():
    """The fifth tick genuinely reached this state for both fabric rows. A rung nobody has seen
    return None is indistinguishable from one that cannot
    (feedback_always_red_detector_is_as_ignored_as_a_blind_one)."""
    assert supervisor._stale_gap_row_draw(work=[]) is None


def test_self_refill_draw_falls_through_when_the_ledger_is_clean(monkeypatch):
    _lanes_above_are_empty(monkeypatch)
    _reconciler_says(monkeypatch, [])
    out = supervisor._self_refill_draw()
    assert out is None or "STALE-GAP-ROW" not in out


def test_a_broken_reconciler_never_invents_a_hold(monkeypatch):
    """FAIL-OPEN on its own error, matching the rungs above it: an unavailable reconcile falls
    through to lower rungs rather than wedging the ladder with a draw it cannot substantiate."""
    def _boom(*a, **k):
        raise RuntimeError("git unavailable")
    monkeypatch.setattr(glr, "reconcile", _boom)
    assert supervisor._stale_gap_row_draw() is None
