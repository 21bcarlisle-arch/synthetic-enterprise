"""The director-reserved site mirror must be unreachable from a test, INCLUDING the one
redirection idiom this module's own docstring tells tests to use.

THE DEFECT THIS NAMES (2026-09-04). `action_needed.save_register` mirrored the register to
`site/data/director_reserved.json` behind:

    if path == REGISTER_PATH:

and a test controls BOTH SIDES of that comparison. `_resolve_path`'s docstring instructs tests to
redirect the register with `monkeypatch.setattr(action_needed, "REGISTER_PATH", tmp_path)`; after
that, `path` IS `REGISTER_PATH` -- both the tmp path -- so the guard read True and wrote the
fixture register into the real site feed. It stopped only the callers that passed `path=`
explicitly, which are the ones that were never the risk.

Measured consequence, not hypothesised: the shared tree's `director_reserved.json` held a fixture
alarm ("wedged since 1970-01-01T00:00 UTC", `git=dead`) where HEAD held the director's real
one-way-door escalation awaiting his PIN. The mirror REPLACES the item list, so the fixture evicted
his item rather than joining it, and the publish daemon commits `site/`.

WHY THE POSITIVE LEG IS HERE AND WHAT IT COSTS. A guard that mirrors NOTHING would satisfy every
negative assertion below, and the site feed would silently stop updating -- the fail-silent that
this project keeps paying for. So `test_the_mirror_still_fires_for_the_real_register` is the
reachability control: it points BOTH the frozen constant and the register at tmp, which is the only
way to exercise the true branch without writing the real file the rest of this module forbids
touching.
"""
from __future__ import annotations

import json

import pytest

from background import action_needed


@pytest.fixture
def site_feed(tmp_path, monkeypatch):
    """Redirect the mirror's OUTPUT so a fired mirror is observable but harmless."""
    feed = tmp_path / "site" / "director_reserved.json"
    monkeypatch.setattr(action_needed, "SITE_RESERVED_PATH", feed)
    return feed


def _register(item_id="fixture-item"):
    return {item_id: {"item_id": item_id, "what": "w", "how": "h", "why": "y",
                      "first_asked_at": "2026-09-04T00:00:00+00:00", "resolved": False}}


def test_the_mirror_still_fires_for_the_real_register(tmp_path, monkeypatch, site_feed):
    """REACHABILITY / null control -- assert the guarded branch CAN be taken.

    Without this, a guard that refused every caller would pass every other test in this file
    while quietly freezing the director's window. Both `REGISTER_PATH` and `_REAL_REGISTER_PATH`
    are pointed at one tmp file, which is what "this IS the real register" means to the guard.
    """
    real = tmp_path / "register.json"
    monkeypatch.setattr(action_needed, "REGISTER_PATH", real)
    monkeypatch.setattr(action_needed, "_REAL_REGISTER_PATH", real)

    action_needed.save_register(_register("director-item"), path=real)

    assert site_feed.exists(), "the mirror never fired -- the site feed can no longer update"
    payload = json.loads(site_feed.read_text())
    assert payload["open_count"] == 1
    assert payload["items"][0]["item_id"] == "director-item"


def test_monkeypatching_the_register_path_does_not_reach_the_site_feed(tmp_path, monkeypatch,
                                                                      site_feed):
    """THE DEFECT ITSELF: the documented idiom, which used to fire the mirror open.

    `_REAL_REGISTER_PATH` is deliberately NOT patched -- that is the whole point. A test may move
    `REGISTER_PATH`; it may not move what the guard compares against.
    """
    monkeypatch.setattr(action_needed, "REGISTER_PATH", tmp_path / "register.json")

    action_needed.save_register(_register())

    assert not site_feed.exists(), (
        "monkeypatching REGISTER_PATH reached the director's site feed -- the guard is comparing "
        "two values the test controls")


def test_an_explicit_tmp_path_does_not_reach_the_site_feed(tmp_path, site_feed):
    """The case the original guard did stop. Kept so the fix cannot regress it."""
    action_needed.save_register(_register(), path=tmp_path / "register.json")
    assert not site_feed.exists()


def test_the_frozen_constant_is_not_the_mutable_one(monkeypatch, tmp_path):
    """The two names must be independently rebindable, or the fix is cosmetic.

    If `_REAL_REGISTER_PATH` were re-derived from `REGISTER_PATH` at call time, this would fail
    and the guard would be exactly as defeatable as before.
    """
    original = action_needed._REAL_REGISTER_PATH
    monkeypatch.setattr(action_needed, "REGISTER_PATH", tmp_path / "moved.json")
    assert action_needed._REAL_REGISTER_PATH == original
    assert action_needed.REGISTER_PATH != action_needed._REAL_REGISTER_PATH


def test_the_real_site_feed_is_untouched_by_this_module(tmp_path, monkeypatch):
    """The whole-file control: run the defect's exact reproduction with the mirror output NOT
    redirected, and assert the real file on disk is byte-identical afterwards.

    Every other test here redirects `SITE_RESERVED_PATH`, so none of them can observe the actual
    harm. This one can. It reads the real path deliberately.
    """
    real_feed = action_needed.SITE_RESERVED_PATH
    before = real_feed.read_bytes() if real_feed.exists() else None

    monkeypatch.setattr(action_needed, "REGISTER_PATH", tmp_path / "register.json")
    action_needed.save_register(_register("would-have-evicted-the-director"))

    after = real_feed.read_bytes() if real_feed.exists() else None
    assert after == before, (
        "a test rewrote the director's own reserved-items surface at "
        f"{real_feed} -- this is the eviction measured on 2026-09-04")
