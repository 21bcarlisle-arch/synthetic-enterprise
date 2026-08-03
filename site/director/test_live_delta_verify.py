#!/usr/bin/env python3
"""R15 both-ways proof for site/director/live_delta_verify.py.

A control counts as evidence only if a MUTATION TEST proves it fires on its own named
defect (R15). This suite runs the verifier against a FAKE live host assembled from the
repo's real door HTML and real feed payloads, so the baseline is a genuine end-to-end
render through the door's own boot path -- then breaks one thing at a time.

The three killer patterns R15 names are each executed here, not asserted:
  TAUTOLOGY   -- test_deployed_version_defect_is_caught is the whole reason this module
                 exists: the generic verifier derives its expectations from the live
                 page, so an OLD page passes it. D1 does not.
  FAIL-OPEN   -- a 404 feed, an unparseable feed, an empty payload and a missing key
                 each FAIL rather than resolving to a quiet empty dict.
  FAIL-SILENT -- an unreachable host FAILS. There is no skip verdict.
"""
from __future__ import annotations

import json
import re
import shutil
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
SITE = HERE.parent
REPO = SITE.parent
sys.path.insert(0, str(SITE))
sys.path.insert(0, str(HERE))

import live_delta_verify as ldv  # noqa: E402
from live_pixel_verify import CANONICAL_HOST, LiveCheckUnavailable  # noqa: E402

DOOR_URL = CANONICAL_HOST + ldv.DOOR
DATA = SITE / "data"

pytestmark = pytest.mark.skipif(
    shutil.which("node") is None,
    reason="the live render harness is a node program; without it this control cannot run",
)


def _door_html() -> str:
    return (SITE / "director" / "index.html").read_text(encoding="utf-8")


def _feed_bytes(name: str) -> bytes | None:
    p = DATA / name
    return p.read_bytes() if p.exists() else None


class FakeHost:
    """A stand-in for the deployed host, served from the repo's real artefacts.

    Deliberately NOT a hand-written fixture: the door HTML and the feed payloads are
    the real ones, so the baseline exercises the door's actual render path. A fixture
    that hand-rolls a tiny page would prove only that the verifier can read a page it
    was handed, which is the failure mode this whole module is about.
    """

    def __init__(self, html: str | None = None, overrides: dict | None = None):
        self.html = _door_html() if html is None else html
        self.overrides = overrides or {}

    def __call__(self, url: str) -> tuple[int, bytes]:
        if url in self.overrides:
            value = self.overrides[url]
            if isinstance(value, Exception):
                raise value
            return value
        if url == DOOR_URL:
            return 200, self.html.encode("utf-8")
        name = url.rsplit("/", 1)[-1].split("?")[0]
        body = _feed_bytes(name)
        if body is None:
            return 404, b""
        return 200, body


def _url(feed: str) -> str:
    return ldv._resolve(ldv.DOOR, feed)


# --------------------------------------------------------------------------------
# BASELINE -- the control must be able to PASS, or every red below is meaningless
# --------------------------------------------------------------------------------

def test_baseline_passes_against_a_healthy_live_surface():
    res = ldv.verify_delta(fetcher=FakeHost())
    assert res.ok, res.failures
    assert res.deployed_version is True
    # The state is NOT pinned: 'quiet' and 'changed' are both legitimate depending on
    # whether anything actually moved since the recorded look. Pinning either would
    # turn an honest interval into a false alarm (the anti-pin half of R15).
    assert res.rendered_state in ldv.HEALTHY_STATES


# --------------------------------------------------------------------------------
# D1 -- TAUTOLOGY: the defect the generic verifier passed on
# --------------------------------------------------------------------------------

def test_deployed_version_defect_is_caught():
    """The exact 2026-08-03 live state: door 200, feeds healthy, feature ABSENT.

    This is the mutation that matters most. `live_pixel_verify --door /director/`
    returned PASS on precisely this input.
    """
    stale = _door_html().replace(ldv.DELTA_FEED, "../data/director_twin.json")
    res = ldv.verify_delta(fetcher=FakeHost(html=stale))
    assert not res.ok
    assert res.deployed_version is False
    assert any("D1" in f for f in res.failures), res.failures


def test_door_not_serving_200_fails():
    res = ldv.verify_delta(fetcher=FakeHost(overrides={DOOR_URL: (404, b"")}))
    assert not res.ok
    assert any("D1" in f and "200" in f for f in res.failures), res.failures


# --------------------------------------------------------------------------------
# D2 -- FAIL-OPEN: a missing/empty/malformed feed must FAIL, never resolve to {}
# --------------------------------------------------------------------------------

@pytest.mark.parametrize("feed", [ldv.DELTA_FEED, ldv.STAMP_FEED])
def test_feed_404_fails(feed):
    res = ldv.verify_delta(fetcher=FakeHost(overrides={_url(feed): (404, b"")}))
    assert not res.ok
    assert any("D2" in f and feed in f for f in res.failures), res.failures


@pytest.mark.parametrize("payload", [b"{}", b"", b"not json at all", b"null"])
def test_empty_or_malformed_delta_feed_fails(payload):
    """FAIL-OPEN is the enemy: an empty payload is not a quiet delta, it is no delta."""
    res = ldv.verify_delta(fetcher=FakeHost(overrides={_url(ldv.DELTA_FEED): (200, payload)}))
    assert not res.ok
    assert any("D2" in f for f in res.failures), res.failures


@pytest.mark.parametrize("missing", ldv.DELTA_REQUIRED_KEYS)
def test_delta_feed_missing_a_required_key_fails(missing):
    payload = json.loads(_feed_bytes("director_delta.json"))
    payload.pop(missing, None)
    res = ldv.verify_delta(
        fetcher=FakeHost(overrides={_url(ldv.DELTA_FEED): (200, json.dumps(payload).encode())})
    )
    assert not res.ok
    assert any("D2" in f and missing in f for f in res.failures), res.failures


def test_stamp_feed_missing_a_required_key_fails():
    payload = json.loads(_feed_bytes("director_last_look.json"))
    payload.pop("state")
    res = ldv.verify_delta(
        fetcher=FakeHost(overrides={_url(ldv.STAMP_FEED): (200, json.dumps(payload).encode())})
    )
    assert not res.ok
    assert any("D2" in f and "state" in f for f in res.failures), res.failures


# --------------------------------------------------------------------------------
# D4 -- the verdict is read from data-state, and the panel's own failure states FAIL
# --------------------------------------------------------------------------------

def test_stamp_lost_renders_honestly_but_still_fails_the_control():
    """The panel is CORRECT to render a lost stamp loudly. The control must still fail:
    rendering an honest failure is good behaviour, not a working feature."""
    payload = json.loads(_feed_bytes("director_delta.json"))
    payload["stamp_status"] = "lost"
    payload["stamp_problem"] = "baseline file unreadable"
    res = ldv.verify_delta(
        fetcher=FakeHost(overrides={_url(ldv.DELTA_FEED): (200, json.dumps(payload).encode())})
    )
    assert not res.ok
    assert res.rendered_state == "stamp-lost"
    # Asserting the SPECIFIC message, not merely "some D4 failure". Found by mutating
    # the control: with the FAILURE_STATES branch deleted, `stamp-lost` fell through to
    # the "unrecognised state" branch, which also says D4 -- so a loose `any("D4" in f)`
    # stayed green and the branch was not load-bearing. A test that passes whichever
    # way the control is wired is not evidence.
    assert any("failure state 'stamp-lost'" in f for f in res.failures), res.failures
    assert not any("unrecognised" in f for f in res.failures), res.failures


def test_the_prose_read_would_have_been_unfalsifiable():
    """Why D4 reads data-state and not text.

    The stamp-lost copy QUOTES the phrase "nothing has changed" in order to deny it.
    Any substring test over the rendered prose therefore cannot tell the healthy quiet
    state from the loudest failure state -- it matches both. This test pins that the
    ambiguity is real, so nobody 'simplifies' D4 back into a text match.
    """
    payload = json.loads(_feed_bytes("director_delta.json"))
    payload["stamp_status"] = "lost"
    res = ldv.verify_delta(
        fetcher=FakeHost(overrides={_url(ldv.DELTA_FEED): (200, json.dumps(payload).encode())})
    )
    assert "nothing has changed" in res.sample.lower()
    assert res.rendered_state == "stamp-lost"
    assert not res.ok


def test_a_dead_boot_leaves_the_panel_unwritten_and_fails():
    """The failure everyone actually ships: the page deploys, one feed it awaits
    without a `.catch()` 404s, `Promise.all` rejects, and no panel is ever written.
    Both halves are green in the repo; the live page is dead.

    The harness reports only what the door's own script WROTE, so a dead boot surfaces
    as an unwritten panel rather than as a lingering placeholder -- which is why the
    two shapes are tested separately below.
    """
    res = ldv.verify_delta(
        fetcher=FakeHost(overrides={_url("../data/director_twin.json"): (404, b"")})
    )
    assert not res.ok
    assert any("rendered nothing" in f for f in res.failures), res.failures


def test_a_panel_the_door_writes_a_placeholder_into_fails():
    """The other half: the door boots, but writes a placeholder into the panel and
    never replaces it.

    Added after mutating the control: deleting the placeholder guard left every test
    green, i.e. the guard was carrying no weight. An uncovered branch in a control is
    indistinguishable from an absent one, so it is either covered or it is deleted.
    """
    stuck = _door_html().replace(
        'document.getElementById("lastlook-body").innerHTML=driftHTML+body;',
        'document.getElementById("lastlook-body").innerHTML="<div>Loading...</div>";',
    )
    assert stuck != _door_html(), "the mutation target moved; update this test"
    res = ldv.verify_delta(fetcher=FakeHost(html=stuck))
    assert not res.ok
    assert any("placeholder" in f for f in res.failures), res.failures


def test_a_panel_without_data_state_fails_rather_than_being_guessed():
    stripped = re.sub(r'data-state="[a-z-]+"', "", _door_html())
    res = ldv.verify_delta(fetcher=FakeHost(html=stripped))
    assert not res.ok
    assert any("D4" in f and "data-state" in f for f in res.failures), res.failures


def test_unrecognised_state_is_not_waved_through():
    """A future refactor that renames a state must FAIL here, not silently pass."""
    mutated = _door_html().replace('data-state="quiet"', 'data-state="somethingelse"')
    mutated = mutated.replace('data-state="changed"', 'data-state="somethingelse"')
    res = ldv.verify_delta(fetcher=FakeHost(html=mutated))
    assert not res.ok
    assert res.rendered_state == "somethingelse"
    assert any("D4" in f and "unrecognised" in f for f in res.failures), res.failures


# --------------------------------------------------------------------------------
# FAIL-SILENT -- an unavailable check is a FAILED check, never a skip
# --------------------------------------------------------------------------------

def test_unreachable_host_fails_it_does_not_skip():
    boom = LiveCheckUnavailable("connection refused")
    with pytest.raises(LiveCheckUnavailable):
        ldv.verify_delta(fetcher=FakeHost(overrides={DOOR_URL: boom}))


def test_main_returns_nonzero_when_the_check_cannot_be_performed(monkeypatch, capsys):
    def _explode(*_a, **_k):
        raise LiveCheckUnavailable("host unreachable")

    monkeypatch.setattr(ldv, "verify_delta", _explode)
    assert ldv.main([]) == 1
    assert "could not be performed" in capsys.readouterr().out


def test_main_returns_nonzero_on_a_failing_verdict(monkeypatch):
    monkeypatch.setattr(
        ldv, "verify_delta", lambda *a, **k: ldv.DeltaResult(ok=False, failures=["D1 nope"])
    )
    assert ldv.main([]) == 1


def test_main_returns_zero_only_on_a_real_pass(monkeypatch):
    monkeypatch.setattr(
        ldv,
        "verify_delta",
        lambda *a, **k: ldv.DeltaResult(ok=True, rendered_state="quiet", http_status=200),
    )
    assert ldv.main([]) == 0
