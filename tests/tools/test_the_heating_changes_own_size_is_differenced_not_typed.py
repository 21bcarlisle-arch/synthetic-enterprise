"""W2_20's own effect on the published control arm is differenced from two artefacts, never typed.

The current-world sentence named the heating change with no size beside it, and a change named
without a size is read as zero. `_w2_20_own_effect` now differences the published run against the
same code with `81732ffe2` reverted. These legs hold that the figures come from the artefacts, and
that every refusal is reachable alongside the sized branch.
"""
from __future__ import annotations

import copy
import json

import pytest

from tools import generate_value_arms_data as g


@pytest.fixture(scope="module")
def pair():
    published = json.loads(g.CURRENT_WORLD_THREE_ARM_PATH.read_text(encoding="utf-8"))
    reverted = json.loads(g.W2_20_REVERTED_CONTROL_PATH.read_text(encoding="utf-8"))
    return published, reverted


def test_the_size_is_the_difference_of_the_two_artefacts(pair):
    published, reverted = pair
    out = g._w2_20_own_effect(published, reverted)
    assert out["available"], out.get("why_not")
    gas = (published["book_identity"]["control_arm"]["with_a_gas_leg"]
           - reverted["book_identity"]["control_arm"]["with_a_gas_leg"])
    net = published["control_arm"]["total_net_gbp"] - reverted["control_arm"]["total_net_gbp"]
    assert out["gas_legs"] == gas
    assert out["net_gbp"] == round(net, 2)
    assert str(abs(gas)) in out["sentence"]
    assert "One draw" in out["sentence"]


def test_the_generator_reads_the_committed_reverted_run_as_a_stamped_source(tmp_path):
    data = g.generate(out_path=tmp_path / "value_arms.json")
    assert data["current_world"]["w2_20_own_effect"]["available"]
    rel = g.W2_20_REVERTED_CONTROL_PATH.relative_to(g.PROJECT).as_posix()
    assert rel in json.dumps(data[g.provenance_stamp.STAMP_KEY])


def test_moving_the_reverted_book_moves_the_published_size(pair):
    """A literal sentence would survive this; a differenced one cannot."""
    published, reverted = pair
    fewer = copy.deepcopy(reverted)
    fewer["book_identity"]["control_arm"]["with_a_gas_leg"] = (
        published["book_identity"]["control_arm"]["with_a_gas_leg"] - 3)
    out = g._w2_20_own_effect(published, fewer)
    assert out["gas_legs"] == 3 and out["sentence"].startswith("On its own, the heating change adds 3")


def test_the_sized_branch_and_every_refusal_are_reachable(pair):
    published, reverted = pair
    other_commit = copy.deepcopy(reverted)
    other_commit["producing_commit"]["commit"] = "0" * 40
    other_world = copy.deepcopy(reverted)
    other_world["world_identity"]["digest"] = "ffffffffffffffff"
    no_margin = copy.deepcopy(reverted)
    del no_margin["control_arm"]["total_net_gbp"]
    outcomes = {
        "sized": g._w2_20_own_effect(published, reverted),
        "commit": g._w2_20_own_effect(published, other_commit),
        "world": g._w2_20_own_effect(published, other_world),
        "itself": g._w2_20_own_effect(published, published),
        "unreadable": g._w2_20_own_effect(published, None),
        "no_published": g._w2_20_own_effect(None, reverted),
        "no_margin": g._w2_20_own_effect(published, no_margin),
    }
    assert outcomes.pop("sized")["available"]
    for name, out in outcomes.items():
        assert out["available"] is False, name
        assert "heating change" in out["why_not"], name
    assert "000000000" in outcomes["commit"]["why_not"]
