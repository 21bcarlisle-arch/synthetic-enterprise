"""R15 both-ways proof of the SEVENTH CLASS (director ruling 2026-07-23,
DIRECTOR_RULING_CAMPAIGN_CONTINUATION_AND_SITE_VERDICT):

    An OPEN campaign in PRIORITIES with unfinished items IS drawable work --
    finishing surface N rolls directly into surface N+1, no doorbell required.

A seventh rest-while-work-exists class is an R10 breach of R17; the fix is to
R17's enumeration, not a special case. Before this fix the SITE_V5 campaign lived
only as a comment block in PRIORITIES.md whose "<-- NEXT" marker the draw could not
see, so at 14:03Z the tick RESTED with surfaces 2-5 drawable. These tests prove the
rung is now load-bearing, BOTH ways:

  * test_must_not_rest_with_open_campaign      -- an open campaign with an open item
    => `_open_campaign_draw` draws (non-None) AND the whole-set enumeration marks
    open_campaign drawable. This is the control that fires on the exact 14:03Z defect.
  * test_may_rest_when_all_items_landed        -- every item `landed` (or campaign
    `closed`) => this level offers nothing, so rest is legitimate on it. PASSES.
  * test_rung_is_in_authorized_set_enumeration -- the level is ACTUALLY wired into the
    whole-set proof (dropping it is what would re-enable the stall).
  * test_real_register_has_site_v5_drawable    -- the committed register really does
    make SITE_V5 surfaces 2-5 drawable RIGHT NOW (the fix is live, not just latent).
  * test_independence_not_a_constant           -- keyed on real parsed content, never a
    constant (R15 independence): landing every item flips the verdict.
"""
from __future__ import annotations

from pathlib import Path

import background.supervisor as sup

_OPEN_CAMPAIGN = """
campaigns:
  - id: SITE_V5
    title: 'Site rebuild -- five-surface IA'
    status: open
    items:
      - id: surface_1_front_door
        title: 'Front door -- the pitch'
        status: open
      - id: surface_2_the_world
        title: 'The World -- walkable causal chain'
        status: open
"""

# Surface 1 landed, surfaces 2-5 still open -> the 14:03Z state exactly (campaign open,
# one item done, the rest drawable). Must NOT rest.
_ONE_LANDED_REST_OPEN = """
campaigns:
  - id: SITE_V5
    status: open
    items:
      - id: surface_1_front_door
        title: 'Front door'
        status: landed
      - id: surface_2_the_world
        title: 'The World'
        status: open
"""

_ALL_LANDED = """
campaigns:
  - id: SITE_V5
    status: open
    items:
      - id: surface_1_front_door
        status: landed
      - id: surface_2_the_world
        status: landed
"""

_CAMPAIGN_CLOSED = """
campaigns:
  - id: SITE_V5
    status: closed
    items:
      - id: surface_1_front_door
        status: open
"""

_EMPTY = "campaigns: []\n"


def _write(tmp_path: Path, body: str) -> Path:
    p = tmp_path / "CAMPAIGN_REGISTER.yaml"
    p.write_text(body, encoding="utf-8")
    return p


def test_must_not_rest_with_open_campaign(tmp_path):
    reg = _write(tmp_path, _OPEN_CAMPAIGN)
    msg = sup._open_campaign_draw(register_path=reg)
    assert msg is not None, "an open campaign with open items MUST be drawable (the 14:03Z defect)"
    assert "SITE_V5" in msg
    assert "surface_2_the_world" in msg


def test_one_landed_rest_open_must_not_rest(tmp_path):
    """The exact 14:03Z ledger state: surface 1 landed, the rest open. The tick must NOT rest."""
    reg = _write(tmp_path, _ONE_LANDED_REST_OPEN)
    items = sup._open_campaign_items(register_path=reg)
    ids = {i[1] for i in items}
    assert "surface_2_the_world" in ids
    assert "surface_1_front_door" not in ids, "a landed item is not drawn again"
    assert sup._open_campaign_draw(register_path=reg) is not None


def test_may_rest_when_all_items_landed(tmp_path):
    reg = _write(tmp_path, _ALL_LANDED)
    assert sup._open_campaign_items(register_path=reg) == []
    assert sup._open_campaign_draw(register_path=reg) is None, "all landed -> this level permits rest"


def test_closed_campaign_leaves_the_drawable_set(tmp_path):
    reg = _write(tmp_path, _CAMPAIGN_CLOSED)
    assert sup._open_campaign_draw(register_path=reg) is None, "a closed campaign forbids nothing"


def test_empty_or_absent_register_permits_rest(tmp_path):
    assert sup._open_campaign_draw(register_path=_write(tmp_path, _EMPTY)) is None
    assert sup._open_campaign_draw(register_path=tmp_path / "does_not_exist.yaml") is None


def test_rung_is_in_authorized_set_enumeration():
    """The whole-set proof (director ruling §2) MUST count open_campaign as its own level --
    dropping it is what would let a lane-scoped proof ground the 14:03Z rest again."""
    enum = sup.authorized_set_enumeration()
    assert "open_campaign" in enum, "open_campaign must be an enumerated level of the authorized set"


def test_real_register_has_site_v5_drawable():
    """The committed register still makes SITE_V5 drawable NOW (live, not latent): surface 2 is
    landed (2026-07-23), but surface 1 (front door, deployed-but-FAILED) and surfaces 3-5 remain
    open, so the campaign must-draw persists."""
    items = sup._open_campaign_items()  # real CAMPAIGN_REGISTER_PATH
    ids = {i[1] for i in items}
    assert "SITE_V5" in {i[0] for i in items}
    # surface 2 has landed -> it is no longer in the drawable set...
    assert "surface_2_the_world" not in ids
    # ...but at least one of the still-open surfaces is, so the campaign draws.
    assert ids & {"surface_1_front_door", "surface_3_the_company",
                  "surface_4_proof", "surface_5_director_window"}
    assert sup._open_campaign_draw() is not None


def test_independence_not_a_constant(tmp_path):
    """R15 independence: the verdict tracks real content, never a constant -- landing every item
    flips must-draw to may-rest through the SAME function."""
    assert sup._open_campaign_draw(register_path=_write(tmp_path, _OPEN_CAMPAIGN)) is not None
    assert sup._open_campaign_draw(register_path=_write(tmp_path, _ALL_LANDED)) is None
