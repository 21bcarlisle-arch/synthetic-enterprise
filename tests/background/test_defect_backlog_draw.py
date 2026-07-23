"""R15 both-ways proof of RUNG 4, the DECLARED-DEFECT BACKLOG (director ruling 2026-07-23,
DIRECTOR_RULING_WORK_IS_THE_DEFAULT + NIGHT_ENFORCEMENT):

    A declared fidelity defect that is not in the drawable set is a CONTRADICTION. The draw walks
    a machine-readable register (docs/design/DECLARED_DEFECTS_REGISTER.yaml) as rung 4; any defect
    whose gap is still open is drawable, so rest is illegitimate while one exists.

Before this rung, the spike-tail defect was "declared top priority, untouched five days" -- declared
only in FRAME prose the draw could not see, so `authorized_set_enumeration` read all-empty ->
REST-LEGITIMATE while a top-priority defect sat open. That was the exact state reproduced below.
These tests prove the rung is load-bearing, BOTH ways:

  * test_must_not_rest_with_open_defect         -- a register with an open defect => the draw fires
    (non-None) AND the whole-set enumeration marks defect_backlog drawable. This is the control that
    fires on the exact today-state defect (the R15 "failing test first").
  * test_may_rest_when_all_defects_closed       -- every defect `closed` (gap measured shut) => this
    level offers nothing, so rest is legitimate on it. PASSES.
  * test_rung_is_in_authorized_set_enumeration  -- the level is ACTUALLY wired into the whole-set
    proof (dropping it is what would re-enable the stall) AND into `_is_drained_and_gated`.
  * test_real_register_has_spike_tail_drawable  -- the committed register really does make the
    spike-tail defect drawable RIGHT NOW (the fix is live, not just latent).
  * test_independence_not_a_constant            -- keyed on real parsed content, never a constant
    (R15 independence): closing every defect flips the verdict; a plan_doc alone does NOT close it.
  * test_priority_order_spike_tail_first        -- ties/priority resolve so the oldest top-priority
    defect (the spike tail) is drawn first.
"""
from __future__ import annotations

from pathlib import Path

import background.supervisor as sup

_OPEN_DEFECT = """
defects:
  - id: SPIKE_TAIL_SSP_RESIDUAL
    title: 'SSP spike tail not shaped like reality'
    declared_at: '2026-07-18'
    source: 'FRAME + director ruling'
    priority: 1
    status: open
    evidence: 'model max GBP 574 vs real GBP 4,038; negatives 0.013% vs 2.241%'
    plan_doc: docs/design/proposals/PROPOSE_SPIKE_TAIL_ATTACK_PLAN.md
    closes_when: 'tail re-measured against G4 ledger within tolerance'
"""

# Two open defects, priority 2 declared EARLIER than priority 1 -- proves priority wins over date,
# and the second defect surfaces in the "also open" tail.
_TWO_OPEN = """
defects:
  - id: LATER_BUT_TOP
    title: 'higher priority, newer'
    declared_at: '2026-07-22'
    priority: 1
    status: open
    evidence: 'e'
    plan_doc: null
    closes_when: 'x'
  - id: OLDER_LOWER
    title: 'lower priority, older'
    declared_at: '2026-07-10'
    priority: 2
    status: open
    evidence: 'e'
    plan_doc: null
    closes_when: 'x'
"""

# Every defect closed (gap measured shut) -> this level is empty, rest legitimate ON IT.
_ALL_CLOSED = """
defects:
  - id: SPIKE_TAIL_SSP_RESIDUAL
    title: 'SSP spike tail'
    declared_at: '2026-07-18'
    priority: 1
    status: closed
    evidence: 'gap measured shut'
    plan_doc: docs/design/proposals/PROPOSE_SPIKE_TAIL_ATTACK_PLAN.md
    closes_when: 'done'
"""

# A defect WITH a plan_doc but still open -> a plan does NOT close a defect (the loop must not idle
# beside a still-open gap the instant a plan exists).
_PLANNED_BUT_OPEN = """
defects:
  - id: SPIKE_TAIL_SSP_RESIDUAL
    title: 'SSP spike tail'
    declared_at: '2026-07-18'
    priority: 1
    status: open
    evidence: 'model vs real'
    plan_doc: docs/design/proposals/PROPOSE_SPIKE_TAIL_ATTACK_PLAN.md
    closes_when: 'tail re-measured'
"""


def _write(tmp_path: Path, body: str) -> Path:
    p = tmp_path / "DECLARED_DEFECTS_REGISTER.yaml"
    p.write_text(body, encoding="utf-8")
    return p


def test_must_not_rest_with_open_defect(tmp_path: Path) -> None:
    """The control that fires on the exact today-state defect."""
    reg = _write(tmp_path, _OPEN_DEFECT)
    draw = sup._declared_defect_backlog_draw(register_path=reg)
    assert draw is not None
    assert "SPIKE_TAIL_SSP_RESIDUAL" in draw
    # It carries the grounded belief-vs-truth evidence, so the draw is a real work order not a poke.
    assert "574" in draw and "4,038" in draw


def test_may_rest_when_all_defects_closed(tmp_path: Path) -> None:
    reg = _write(tmp_path, _ALL_CLOSED)
    assert sup._declared_defect_backlog_draw(register_path=reg) is None
    assert sup._open_declared_defects(register_path=reg) == []


def test_planned_but_open_still_draws(tmp_path: Path) -> None:
    """A plan_doc does NOT close a defect -- the gap is still open, still drawable, now to ADVANCE."""
    reg = _write(tmp_path, _PLANNED_BUT_OPEN)
    draw = sup._declared_defect_backlog_draw(register_path=reg)
    assert draw is not None
    assert "ADVANCE" in draw and "PROPOSE_SPIKE_TAIL_ATTACK_PLAN" in draw


def test_priority_order_spike_tail_first(tmp_path: Path) -> None:
    reg = _write(tmp_path, _TWO_OPEN)
    defects = sup._open_declared_defects(register_path=reg)
    assert [d["id"] for d in defects] == ["LATER_BUT_TOP", "OLDER_LOWER"]
    draw = sup._declared_defect_backlog_draw(register_path=reg)
    assert draw is not None and "LATER_BUT_TOP" in draw
    assert "OLDER_LOWER" in draw  # surfaces in the "also open" tail


def test_rung_is_in_authorized_set_enumeration() -> None:
    """The level is wired into BOTH the whole-set proof and the drained-gate (dropping either
    re-enables the stall)."""
    enum = sup.authorized_set_enumeration()
    assert "defect_backlog" in enum, "rung 4 missing from authorized_set_enumeration"
    # And the drained-gate consults it: the source names the function.
    import inspect

    src = inspect.getsource(sup._is_drained_and_gated)
    assert "_declared_defect_backlog_draw" in src, "rung 4 not consulted by _is_drained_and_gated"
    refill_src = inspect.getsource(sup._self_refill_draw)
    assert "_declared_defect_backlog_draw" in refill_src, "rung 4 not in the _self_refill_draw ladder"


def test_real_register_backlog_draw_consistent_with_open_defects() -> None:
    """The mechanism's verdict tracks the REAL committed register's live open-defect set (R15 independence
    on the actual file, not a fixture) -- an open defect re-arms the draw, a closed one legitimately empties
    the rung. RECONCILED 2026-07-24: SPIKE_TAIL_SSP_RESIDUAL was measured shut (the intraday-shape fix
    landed -- see the register closed_by / test_forward_intraday_shape.py + test_residual_bites_intraday.py),
    so it must NOT be in the open set, and the draw/enumeration reflect the real remaining open defects
    (whatever they are), never a hard-coded assumption that spike-tail is open."""
    open_defects = sup._open_declared_defects()  # real DECLARED_DEFECTS_REGISTER_PATH
    open_ids = [d.get("id") for d in open_defects]
    draw = sup._declared_defect_backlog_draw()
    enum = sup.authorized_set_enumeration()["defect_backlog"]
    if open_defects:
        assert draw is not None and enum is True, "an open defect must arm the draw + enumeration"
        assert any(oid in draw for oid in open_ids)
    else:
        assert draw is None and enum is False, "no open defect => this rung is legitimately empty"
    # The spike-tail fix is measured-shut, so it is NOT in the open set (a closed defect never re-draws).
    assert "SPIKE_TAIL_SSP_RESIDUAL" not in open_ids, (
        "SPIKE_TAIL_SSP_RESIDUAL is marked closed in the real register but still reads as open"
    )


def test_independence_not_a_constant(tmp_path: Path) -> None:
    """R15 independence: the verdict tracks real parsed content, never a constant. Closing the only
    defect flips must-draw -> may-rest on this level."""
    open_reg = _write(tmp_path, _OPEN_DEFECT)
    assert sup._declared_defect_backlog_draw(register_path=open_reg) is not None
    closed = tmp_path / "closed.yaml"
    closed.write_text(_ALL_CLOSED, encoding="utf-8")
    assert sup._declared_defect_backlog_draw(register_path=closed) is None
    # A missing/unreadable register yields [] (graceful degradation), never a crash or false draw.
    assert sup._open_declared_defects(register_path=tmp_path / "nope.yaml") == []
