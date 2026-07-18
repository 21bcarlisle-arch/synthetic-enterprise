"""G10 harden-ability gate on the Rule-0 HARDEN self-refill draw (twin-approved
2026-07-17, route_blocking_decision 'G10_harden_ability_gate_build').

An idle HARDEN draw should spend red-team effort where a control can ACTUALLY fail:
- SKIP-preference atoms with no harden-able surface (FRAME-only level<2, or evidence
  pointing at no runnable test) -- there is nothing to re-verify/mutate on them.
- PREFER harness/safety-control lanes (structural criticality) over settled domain atoms.
- NEVER zero the set (Rule 0): if only non-harden-able atoms exist it still draws one
  (a genuinely-empty draw would false-trip the LOOP_BROKEN transport alarm).
- STRUCTURAL ONLY (twin R12 note): never keyed on bug-history/outcome.

R15 mutation coverage: each gate must be able to FIRE and the guardrail must hold.
"""
from __future__ import annotations

import random

from background import supervisor as S


def _atom(id, lc, lt, lane="X", evidence=None):
    return {"id": id, "level_current": lc, "level_target": lt, "lane": lane,
            "dial_inherited": 1, "evidence": evidence if evidence is not None else []}


# ── unit: the structural predicates ───────────────────────────────────────────────────────
def test_has_harden_surface_predicate():
    # level<2 -> FRAME-only, no surface even with a test listed
    assert S._has_harden_surface(_atom("a", 1, 1, evidence=["tests/x.py"])) is False
    # level>=2 but evidence is docs only -> no runnable test to re-verify
    assert S._has_harden_surface(_atom("b", 3, 3, evidence=["docs/design/x.md"])) is False
    # level>=2 with a test path -> harden-able
    assert S._has_harden_surface(_atom("c", 2, 2, evidence=["tests/background/x.py"])) is True
    assert S._has_harden_surface(_atom("d", 3, 3, evidence=["saas/x.py", "tests/test_x.py"])) is True
    # a test_*.py anywhere also counts
    assert S._has_harden_surface(_atom("e", 3, 3, evidence=["tools/test_thing.py"])) is True


def test_criticality_weight_structural_only():
    assert S._harden_criticality_weight(_atom("h", 3, 3, lane="H_harness")) == 3
    assert S._harden_criticality_weight(_atom("d", 3, 3, lane="C_customer_ops")) == 1


# ── the draw: harden-able preferred over FRAME-only ───────────────────────────────────────
def test_frame_only_atom_is_never_drawn_when_a_hardenable_exists(monkeypatch, tmp_path):
    import yaml
    m = tmp_path / "m.yaml"
    frame_only = _atom("FRAME_ONLY", 1, 1, lane="H_harness", evidence=["tests/x.py"])  # level<2
    hardenable = _atom("REAL", 3, 3, lane="C_customer_ops", evidence=["tests/test_real.py"])
    m.write_text(yaml.safe_dump([frame_only, hardenable]))
    monkeypatch.setattr(S, "MATURITY_MAP_PATH", m)
    ids = {S._rule0_harden_draw(rng=random.Random(i))["id"] for i in range(40)}
    assert ids == {"REAL"}                       # FRAME-only never drawn; the mutation (drop
    #                                              the surface filter) would let it be drawn.


def test_doc_only_evidence_atom_skipped_for_a_tested_one(monkeypatch, tmp_path):
    import yaml
    doc_only = _atom("DOC_ONLY", 3, 3, lane="H_harness", evidence=["docs/design/x.md"])
    tested = _atom("TESTED", 3, 3, lane="C_customer_ops", evidence=["tests/test_x.py"])
    m = tmp_path / "m.yaml"
    m.write_text(yaml.safe_dump([doc_only, tested]))
    monkeypatch.setattr(S, "MATURITY_MAP_PATH", m)
    ids = {S._rule0_harden_draw(rng=random.Random(i))["id"] for i in range(40)}
    assert ids == {"TESTED"}


# ── harness/control lanes preferred (soft, not exclusive) ─────────────────────────────────
def test_harness_lane_preferred_over_domain_but_not_exclusive(monkeypatch, tmp_path):
    import yaml
    harness = _atom("HARN", 3, 3, lane="H_harness", evidence=["tests/test_h.py"])
    domain = _atom("DOM", 3, 3, lane="W3_industry_systems", evidence=["tests/test_d.py"])
    m = tmp_path / "m.yaml"
    m.write_text(yaml.safe_dump([harness, domain]))
    monkeypatch.setattr(S, "MATURITY_MAP_PATH", m)
    picks = [S._rule0_harden_draw(rng=random.Random(i))["id"] for i in range(300)]
    h, d = picks.count("HARN"), picks.count("DOM")
    # 3:1 structural weight -> h ~= 225, d ~= 75. Assert the BIAS is real (h > 2*d), which
    # holds at 3:1 but FAILS at the mutated 1:1 (h ~= d ~= 150, so h > 2*d is false).
    assert h > 2 * d                              # genuinely preferred, not a coin-flip
    assert d > 0                                  # ...but NOT exclusive (soft dial, R12)


# ── the Rule-0 guardrail: never zeroes the set ────────────────────────────────────────────
def test_only_non_hardenable_still_draws_one_never_empty(monkeypatch, tmp_path):
    import yaml
    # every at-target atom is FRAME-only / doc-only -> none harden-able. Must STILL draw one
    # (fall back to the full at-target pool), NEVER return None -> no false LOOP_BROKEN.
    a = _atom("A", 1, 1, lane="H_harness", evidence=["docs/x.md"])
    b = _atom("B", 3, 3, lane="C_ops", evidence=["docs/y.md"])   # level ok but no test evidence
    m = tmp_path / "m.yaml"
    m.write_text(yaml.safe_dump([a, b]))
    monkeypatch.setattr(S, "MATURITY_MAP_PATH", m)
    for i in range(20):
        got = S._rule0_harden_draw(rng=random.Random(i))
        assert got is not None and got["id"] in {"A", "B"}


def test_genuinely_empty_map_returns_none(monkeypatch, tmp_path):
    import yaml
    # no at-target atom (all below target) -> None, the genuine WALL (unchanged behaviour).
    m = tmp_path / "m.yaml"
    m.write_text(yaml.safe_dump([_atom("BELOW", 0, 3, evidence=["tests/t.py"])]))
    monkeypatch.setattr(S, "MATURITY_MAP_PATH", m)
    assert S._rule0_harden_draw(rng=random.Random(0)) is None

# ── Publish-gate scope (R10, 2026-07-18): DAEMON-LIFECYCLE test module ──────────
# Validates pipeline MACHINERY (process/session lifecycle, scheduling, notify transport,
# reconciliation), never a published business surface -- so it must never wedge the live
# publish. The gate runs `-m 'not operational'`. See tests/conftest.py for the marker.
import pytest  # noqa: E402,F811
pytestmark = pytest.mark.operational
