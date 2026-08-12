"""RUNG 1c -- BLOCKING FINDING LANE PRECEDENCE -- R15 both-ways proof.

Atom `OPS12_blockers_ahead_of_disposition` (DIRECTOR_RULING_FINDING_SEVERITY_AND_INTERLEAVE
2026-08-12, clause 3): "a BLOCKING finding draws ahead of the general disposition queue, ahead of
latent findings, and ahead of new feature work in its own lane; the drain proceeds around it."

The mechanism: `supervisor._blocking_lane_draw()` reads OPS9's severity parse
(`background.finding_severity`) over the staging root and returns the set of lanes carrying a live
BLOCKING finding. `_self_refill_draw()` uses that set to exclude SAME-LANE BUILD/SITE/DISCOVERY
candidates from the cycle and to prepend the blocker's own name to whatever it returns; when
nothing else is left to draw in the cycle, the blocker alone outranks the campaign/declared-defect/
stale-gap/backlog/propose-half/forward-discovery/HARDEN rungs beneath it. `_is_drained_and_gated`
mirrors the same check so a live blocker can never ground a "rest" verdict.

Per this file's own established convention for rungs embedded in `background/supervisor.py`
(`test_publish_gate_wedge_draw.py`, `test_operational_red_persistent_draw.py`,
`test_stale_gap_row_draw.py`): supervisor.py is too large to safely clone+exec per test
(`feedback_editing_a_source_file_mid_pytest_run_corrupts_inspect_getsource` — the class this
project already filed against literal source mutation of huge modules), so "R15 both ways" is
proven BEHAVIOURALLY against the real function with injected fixtures, not via a source-mutated
copy. Each direction below is named for the mutation it would catch:

  * test_a_blocked_lane_atom_is_excluded_from_the_draw -- kills a mutation that DROPS the
    `lane not in blocked_lanes` filter (restoring plain arrival/recency order: the blocked-lane
    atom would draw again as if nothing were wrong).
  * test_an_unblocked_lane_atom_still_draws_the_same_cycle -- kills a mutation that turns the
    per-lane filter into a global one (a blocker in lane L silently starving every OTHER lane too,
    the "naive global priority" exit criterion 2 explicitly forbids).

Every test injects its own staging root + maturity map (`feedback_new_draw_rung_needs_fixture_
isolation`); none reads the live `docs/staging/` or `docs/design/maturity_map.yaml`.
"""
from __future__ import annotations

from pathlib import Path

import pytest

from background import finding_severity as fs
from background import supervisor

BLOCKING_DOC = """# [WORKER-FINDING] An instrument in H_harness cannot be trusted

**Severity:** BLOCKING · **Lane:** H_harness

## The claim
Body text naming the untrustworthy control.
"""

LATENT_DOC = """# [WORKER-FINDING] A cosmetic defect

**Severity:** LATENT · **Lane:** H_harness

## The claim
Body text.
"""

_TWO_LANE_MAP_YAML = """\
- id: H1_test_atom
  name: "Test atom in the blocked lane"
  lane: H_harness
  dial_inherited: 1
  level_current: 0
  level_target: 2
  loop_stage: build
  file_scope: []
- id: B1_test_atom
  name: "Test atom in an unaffected lane"
  lane: B_commercial
  dial_inherited: 1
  level_current: 0
  level_target: 2
  loop_stage: build
  file_scope: []
"""

_ONE_LANE_MAP_YAML = """\
- id: H1_test_atom
  name: "Test atom in the blocked lane, the only candidate this cycle"
  lane: H_harness
  dial_inherited: 1
  level_current: 0
  level_target: 2
  loop_stage: build
"""


def _staging_with(tmp_path: Path, *docs: tuple[str, str]) -> Path:
    root = tmp_path / "staging"
    root.mkdir()
    for name, text in docs:
        (root / name).write_text(text, encoding="utf-8")
    return root


def _neutralise_rungs_above_and_below(monkeypatch, *, site=(), discovery=()):
    """Silence every rung this test isn't about, so a draw/rest decision is attributable to
    RUNG 1c alone -- same convention as test_stale_gap_row_draw.py::_lanes_above_are_empty."""
    monkeypatch.setattr(supervisor, "_publish_gate_wedge_active", lambda *a, **k: None)
    monkeypatch.setattr(supervisor, "_operational_red_persistent_draw", lambda *a, **k: None)
    monkeypatch.setattr(supervisor, "_site_lane_draw_concurrent", lambda *a, **k: list(site))
    monkeypatch.setattr(supervisor, "_idle_discover_frame_draw_concurrent", lambda *a, **k: list(discovery))
    monkeypatch.setattr(supervisor, "log", lambda *a, **k: None)


# ─────────────────────────── _blocking_lane_draw itself ───────────────────────────

def test_no_blocking_finding_is_silent(tmp_path):
    root = _staging_with(tmp_path, ("LATENT_ONLY.md", LATENT_DOC))
    reason, blocked = supervisor._blocking_lane_draw(staging_dir=root)
    assert reason is None
    assert blocked == frozenset()


def test_a_blocking_finding_names_itself_and_its_lane(tmp_path):
    root = _staging_with(tmp_path, ("WORKER_FINDING_THE_THING.md", BLOCKING_DOC))
    reason, blocked = supervisor._blocking_lane_draw(staging_dir=root)
    assert reason is not None
    assert "WORKER_FINDING_THE_THING.md" in reason  # exit criterion 3: audit from the string alone
    assert "H_harness" in reason
    assert blocked == frozenset({"H_harness"})


def test_fail_open_on_unreadable_index_says_so_and_falls_back_visibly(tmp_path, monkeypatch):
    """Exit criterion 5. An unreadable severity index must be DISTINGUISHABLE from a clean
    zero-blocker read: `reason` is non-None (visible) but `blocked_lanes` is empty (no silent
    exclusion -- the ordinary draw order gets a fair chance below this rung)."""
    def _raise(*a, **k):
        raise RuntimeError("simulated unreadable staging root")
    monkeypatch.setattr(fs, "scan_staging_root", _raise)
    reason, blocked = supervisor._blocking_lane_draw(staging_dir=tmp_path / "staging")
    assert reason is not None
    assert "UNREADABLE" in reason
    assert blocked == frozenset()


# ─────────────────────────── wired into _self_refill_draw ───────────────────────────

def test_a_blocked_lane_atom_is_excluded_from_the_draw(tmp_path, monkeypatch):
    """MUST FIRE + exit criterion 1: the blocked-lane atom (H1) never appears this cycle.
    A mutation that drops the `lane not in blocked_lanes` filter (restoring plain arrival/
    recency order) makes H1 reappear and kills this test."""
    _neutralise_rungs_above_and_below(monkeypatch)
    staging = _staging_with(tmp_path, ("WORKER_FINDING_THE_THING.md", BLOCKING_DOC))
    monkeypatch.setattr(supervisor, "STAGING_DIR", staging)
    monkeypatch.setattr(supervisor, "MATURITY_MAP_PATH", tmp_path / "maturity_map.yaml")
    supervisor.MATURITY_MAP_PATH.write_text(_TWO_LANE_MAP_YAML)

    msg = supervisor._self_refill_draw()

    assert msg is not None
    assert "H1_test_atom" not in msg
    assert "BLOCKING FINDING" in msg
    assert "WORKER_FINDING_THE_THING.md" in msg


def test_an_unblocked_lane_atom_still_draws_the_same_cycle(tmp_path, monkeypatch):
    """MUST FIRE + exit criterion 2 (NON-BLOCKING ELSEWHERE): the SAME cycle that excludes H1
    still draws B1 (a different lane) -- 'the drain proceeds around it'. A mutation that turns
    the per-lane filter into a global one (blocking ALL lanes, not just H_harness) drops B1 from
    this message too and kills this test."""
    _neutralise_rungs_above_and_below(monkeypatch)
    staging = _staging_with(tmp_path, ("WORKER_FINDING_THE_THING.md", BLOCKING_DOC))
    monkeypatch.setattr(supervisor, "STAGING_DIR", staging)
    monkeypatch.setattr(supervisor, "MATURITY_MAP_PATH", tmp_path / "maturity_map.yaml")
    supervisor.MATURITY_MAP_PATH.write_text(_TWO_LANE_MAP_YAML)

    msg = supervisor._self_refill_draw()

    assert msg is not None
    assert "B1_test_atom" in msg


def test_no_blocker_message_is_byte_identical_to_the_pre_ops12_format(tmp_path, monkeypatch):
    """Backward-compat: when nothing is blocking, the lone-BUILD-atom short message is untouched
    -- existing NTFY/log parsing depends on this exact string."""
    _neutralise_rungs_above_and_below(monkeypatch)
    monkeypatch.setattr(supervisor, "STAGING_DIR", tmp_path / "staging_empty")
    monkeypatch.setattr(supervisor, "MATURITY_MAP_PATH", tmp_path / "maturity_map.yaml")
    supervisor.MATURITY_MAP_PATH.write_text(_ONE_LANE_MAP_YAML)

    msg = supervisor._self_refill_draw()

    assert msg is not None
    assert msg.startswith("self-refill from maturity map (dial-weighted): H1_test_atom")
    assert "BLOCKING FINDING" not in msg


def test_blocker_draws_alone_ahead_of_the_general_disposition_queue(tmp_path, monkeypatch):
    """Exit criterion 1: with every candidate in the blocked lane excluded and no other-lane
    work this cycle, the blocker draws ALONE -- it must outrank the campaign/declared-defect/
    stale-gap/backlog/propose-half/forward-discovery/HARDEN rungs beneath it, every one of which
    is armed here to prove the short-circuit is real (not merely 'nothing else happened to fire')."""
    _neutralise_rungs_above_and_below(monkeypatch)
    staging = _staging_with(tmp_path, ("WORKER_FINDING_THE_THING.md", BLOCKING_DOC))
    monkeypatch.setattr(supervisor, "STAGING_DIR", staging)
    monkeypatch.setattr(supervisor, "MATURITY_MAP_PATH", tmp_path / "maturity_map.yaml")
    supervisor.MATURITY_MAP_PATH.write_text(_ONE_LANE_MAP_YAML)  # only the blocked-lane atom exists
    monkeypatch.setattr(supervisor, "_open_campaign_draw", lambda *a, **k: "CAMPAIGN ITEM SHOULD NOT WIN")
    monkeypatch.setattr(supervisor, "_declared_defect_backlog_draw", lambda *a, **k: "DEFECT SHOULD NOT WIN")
    monkeypatch.setattr(supervisor, "_stale_gap_row_draw", lambda *a, **k: "STALE GAP SHOULD NOT WIN")
    monkeypatch.setattr(supervisor, "_actionable_backlog_item", lambda *a, **k: "BACKLOG SHOULD NOT WIN")

    msg = supervisor._self_refill_draw()

    assert msg is not None
    assert "BLOCKING FINDING" in msg
    assert "SHOULD NOT WIN" not in msg


def test_fail_open_does_not_suppress_the_ordinary_draw(tmp_path, monkeypatch):
    """Exit criterion 5, second half: an unreadable index falls back to the ordinary draw order
    VISIBLY -- it must not accidentally exclude the very lane the (unreadable) index would have
    named. Single-atom map so `MAX_CONCURRENT_FORKS=1` (SERIAL BY DEFAULT) can't turn this into a
    coin flip about which of two atoms survives the fork-budget truncation -- the only question
    this test asks is "does H1 (in the lane a real blocker WOULD have named) still draw when the
    index can't be read", and a real filter-on-empty-blocked_lanes bug would make it disappear."""
    _neutralise_rungs_above_and_below(monkeypatch)
    monkeypatch.setattr(supervisor, "STAGING_DIR", tmp_path / "staging_absent")
    monkeypatch.setattr(supervisor, "MATURITY_MAP_PATH", tmp_path / "maturity_map.yaml")
    supervisor.MATURITY_MAP_PATH.write_text(_ONE_LANE_MAP_YAML)

    def _raise(*a, **k):
        raise RuntimeError("simulated unreadable staging root")
    monkeypatch.setattr(fs, "scan_staging_root", _raise)

    msg = supervisor._self_refill_draw()

    assert msg is not None
    assert "UNREADABLE" in msg
    assert "H1_test_atom" in msg  # not excluded -- the fail-open path never filters


# ─────────────────────────── mirrored in _is_drained_and_gated ───────────────────────────

def test_is_drained_and_gated_refuses_rest_while_a_blocker_is_live(tmp_path, monkeypatch):
    """A live BLOCKING finding is real work by the ruling's own words -- rest is never
    legitimate while one sits unrepaired, even if every OTHER lane happens to be genuinely
    empty (the exact 'lane-scoped proof grounds rest' shape this mirror exists to forbid)."""
    monkeypatch.setattr(supervisor, "_publish_gate_wedge_active", lambda *a, **k: None)
    monkeypatch.setattr(supervisor, "_operational_red_persistent_draw", lambda *a, **k: None)
    staging = _staging_with(tmp_path, ("WORKER_FINDING_THE_THING.md", BLOCKING_DOC))
    monkeypatch.setattr(supervisor, "STAGING_DIR", staging)
    monkeypatch.setattr(supervisor, "MATURITY_MAP_PATH", tmp_path / "maturity_map_absent.yaml")

    assert supervisor._is_drained_and_gated() is False


def test_blocking_lane_draw_itself_is_silent_so_this_mirror_adds_nothing_on_a_clean_index(tmp_path):
    """MUST STAY SILENT counterpart, scoped to this rung's own contribution (matching
    `test_operational_red_persistent_draw.py`'s convention of proving the FALSE direction against
    `_is_drained_and_gated` and the None/silent direction against the detector itself, rather than
    re-neutralising every other rung's real-file reads just to exercise the True branch end to end):
    with no blocking finding anywhere, `_blocking_lane_draw` itself returns nothing that could flip
    the predicate."""
    reason, blocked = supervisor._blocking_lane_draw(staging_dir=tmp_path / "staging_empty")
    assert reason is None
    assert blocked == frozenset()
