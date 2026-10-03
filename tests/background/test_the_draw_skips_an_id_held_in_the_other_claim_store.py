"""The draw skips an id another writer holds in the OTHER claim store.

Defect this names: `next_item` asked only its own store, so an id held live in
`.seat_work_in_hand.json` was drawn again (`build-the-supplier-dd-stopping-rule`, twice on
2026-10-03, while a scheduled worker was building it).
"""
from __future__ import annotations

import pytest
import yaml

from background import delivery_lane as dl
from background import direction as d
from background import seat_continuation as sc
from background import seat_work_in_hand as claims_mod
from tests.background.test_delivery_lane import NOW_EPOCH, _item, _record


@pytest.fixture()
def lane(tmp_path, monkeypatch):
    direction_path = tmp_path / "DIRECTION.yaml"
    map_path = tmp_path / "maturity_map.yaml"
    map_path.write_text(yaml.safe_dump([{"id": "EP1_real_atom", "level_current": 1}]),
                        encoding="utf-8")
    own = tmp_path / "lane_claims.json"
    other = tmp_path / "seat_claims.json"
    monkeypatch.setattr(dl, "MATURITY_MAP", map_path)
    monkeypatch.setattr(d, "DIRECTION_PATH", direction_path)
    monkeypatch.setattr(sc, "STORE", tmp_path / ".seat_continuation.json")
    monkeypatch.setattr(dl, "_live_holders", lambda: [])
    monkeypatch.setattr(dl, "CLAIMS_FILE", own)
    monkeypatch.setattr(claims_mod, "CLAIMS_FILE", other)
    monkeypatch.setattr(claims_mod, "_last_commit_time_touching", lambda paths: 0.0)
    direction_path.write_text(
        yaml.safe_dump(_record([_item("held-by-the-seat"), _item("free-work")])),
        encoding="utf-8")
    return {"own": own, "other": other}


def test_an_id_held_in_the_other_store_is_not_drawn_and_the_next_free_one_is(lane):
    """Both branches in one control: the held id is skipped AND the walk still reaches a free one.

    MUTATION (must fire): drop the `held_in_other_stores` union from `next_item` -- the draw
    returns `held-by-the-seat`.
    """
    claims_mod.claim("held-by-the-seat", note="a live worker", paths=[], path=lane["other"],
                     now=NOW_EPOCH)

    item = dl.next_item(now=NOW_EPOCH)

    assert item is not None and item["id"] == "free-work"


def test_the_same_id_is_drawable_once_the_other_store_lets_it_go(lane):
    """The skip is a hold, never a ban: with nothing in the other store the head is drawn.

    MUTATION (must fire): make `held_in_other_stores` return every focus id.
    """
    item = dl.next_item(now=NOW_EPOCH)

    assert item is not None and item["id"] == "held-by-the-seat"


def test_a_stale_claim_in_the_other_store_does_not_hold_the_item(lane):
    """A holder past the other store's own deadline no longer holds: the item comes back.

    MUTATION (must fire): drop the `stale` exclusion in `held_in_other_stores`.
    """
    claims_mod.claim("held-by-the-seat", note="a dead worker", paths=[], path=lane["other"],
                     now=NOW_EPOCH - claims_mod.STALE_AFTER_SECONDS - 60)

    item = dl.next_item(now=NOW_EPOCH)

    assert item is not None and item["id"] == "held-by-the-seat"
