"""ONE CONVENTION, THREE READERS, AND TWO OF THEM COULD ONLY SEE THE FIRST 600 BYTES.

Director, 2026-09-02: *"two mints have been blocked for three hours and a drawable item sits
untouched."* The three hours is the alarm's re-escalation window. The mints are from 24 and 29
July, and one of them had not been blocked since **3 August** -- its own text says so.

WHAT WAS ACTUALLY WRONG. A parked mint declares itself with
`<!-- SUPERVISOR_DRAW: self-drawable|blocked -->`. Three modules read that marker:

  * `primary_state_scan.drawable_undrawn_mints`      -- read `body[:600]`
  * `deadmans_switch._open_blocked_mints`            -- read `body[:600]`, hand-copied
  * `staging_disposition.selfdrawable_mint_in_progress` -- whole document, and correct

`PLANNER_MINTED_reversibility_action_and_act_2026-07-29.md` carries its marker at character
**3513**, behind 3.5 KB of tick notes that later ticks prepended above it. So the two bounded
readers could not see it, and the mint was **invisible as drawable and alarming as blocked at the
same time** -- for a month. Nobody drew it from either direction: the alarm said it was blocked,
and the draw list did not contain it.

A control keyed to a POSITION goes quiet, not loud, when the thing moves past it. Widening 600
would only move the date of the next failure, which is why these tests are about the property.

`_open_blocked_mints`'s own docstring already claimed to be the complement of
`drawable_undrawn_mints`. It was not, and nothing checked.
"""
from __future__ import annotations

import re

import background.deadmans_switch as dms
from background.primary_state_scan import drawable_undrawn_mints
from background.staging_disposition import selfdrawable_mint_in_progress

_SELF = "<!-- SUPERVISOR_DRAW: self-drawable -->"
_BLOCKED = "<!-- SUPERVISOR_DRAW: blocked -->"


def _mint(dirpath, name, body):
    p = dirpath / "PLANNER_MINTED_{}.md".format(name)
    p.write_text(body)
    return p.name


# ── THE DEFECT, reproduced at its measured offset ───────────────────────────────────────────
def test_a_marker_behind_accreted_notes_is_still_seen(tmp_path):
    """THE INSTANCE, at the real distance. 3513 characters of prepended tick history is not a
    pathological fixture -- it is what that file actually looks like.

    MUTATION: restore `body[:600]` and this fails, and the mint disappears from the draw.
    """
    name = _mint(tmp_path, "buried",
                 "<!-- a tick note -->\n" + ("x" * 3400) + "\n" + _SELF + "\n\n# [PLANNER-MINTED] Buried\n")
    found = {n for n, _ in drawable_undrawn_mints(tmp_path)}
    assert name in found


def test_the_same_marker_is_seen_by_the_blocked_reader_too(tmp_path, monkeypatch):
    """Both bounded readers, because the second was a hand-copy of the first and fixing one would
    have left the alarm firing on a mint the draw could now see -- which is the disagreement."""
    monkeypatch.setattr(dms, "STAGING_DIR", tmp_path)
    ip = tmp_path / "in_progress"
    ip.mkdir()
    name = _mint(ip, "buried", ("y" * 3400) + "\n" + _SELF + "\n\n# [PLANNER-MINTED] Buried\n")
    assert name not in {n for n, _ in dms._open_blocked_mints()}


# ── THE PROPERTY: the two sets are complements, and nothing may be in both ──────────────────
def test_a_mint_is_never_both_drawable_and_blocked(tmp_path, monkeypatch):
    """`_open_blocked_mints`'s docstring has always claimed to be the COMPLEMENT of the drawable
    read. It was not, and nothing checked -- so one document sat in both sets, each reader right
    by its own lights, and the contradiction was silent.

    MUTATION: drop the self-drawable exclusion from `_open_blocked_mints` and this fails.
    """
    monkeypatch.setattr(dms, "STAGING_DIR", tmp_path)
    ip = tmp_path / "in_progress"
    ip.mkdir()
    _mint(ip, "a", _SELF + "\n# A\n")
    _mint(ip, "b", _BLOCKED + "\nUNBLOCKS ON: something real\n# B\n")
    _mint(ip, "c", "no marker at all\n# C\n")

    drawable = {n for n, _ in drawable_undrawn_mints(ip)}
    blocked = {n for n, _ in dms._open_blocked_mints()}
    assert not (drawable & blocked), "a mint in both sets is what nobody draws"
    assert drawable | blocked == {p.name for p in ip.glob("PLANNER_MINTED_*.md")}


def test_an_unmarked_mint_parks_rather_than_being_drawn(tmp_path, monkeypatch):
    """Fail-closed: the marker is a positive declaration. An absent one must not read as drawable,
    or a mint that never said it was ready gets picked up as if it had."""
    monkeypatch.setattr(dms, "STAGING_DIR", tmp_path)
    ip = tmp_path / "in_progress"
    ip.mkdir()
    name = _mint(ip, "silent", "# no marker\n")
    assert name not in {n for n, _ in drawable_undrawn_mints(ip)}
    assert name in {n for n, _ in dms._open_blocked_mints()}


def test_both_markers_present_parks_the_mint(tmp_path, monkeypatch):
    """A whole-document scan can meet a token quoted inside a historical note, so the two can now
    co-occur where a 600-byte window would rarely have seen both. Parking on a contradiction is the
    safe direction: an over-reported drawable is drawn and found done; an under-reported block is
    work nobody does."""
    monkeypatch.setattr(dms, "STAGING_DIR", tmp_path)
    ip = tmp_path / "in_progress"
    ip.mkdir()
    name = _mint(ip, "both", _BLOCKED + "\nan old note once said " + _SELF + "\n# Both\n")
    assert name not in {n for n, _ in drawable_undrawn_mints(ip)}
    assert name in {n for n, _ in dms._open_blocked_mints()}


# ── AND THE THREE INDEPENDENT READERS MUST AGREE ────────────────────────────────────────────
def test_the_three_readers_of_one_convention_agree_on_the_real_tree():
    """THE INTERCONNECTION CONTROL, and the one that would have caught this in August.

    The three reads are deliberately INDEPENDENT -- `primary_state_scan` imports nothing at all,
    which is the LAW-C property that makes it a check on the tick rather than a restatement of it.
    Independence is worth keeping; silent DIVERGENCE is not. So they are not merged into one
    implementation, they are required to agree.

    Run against the live tree, because a fixture cannot tell you that a real document drifted past
    a real window -- which is exactly what happened. `population_floors_and_split_seams`: assert
    the population is non-empty first, or an emptied directory passes this quietly.
    """
    ip = dms.STAGING_DIR / "in_progress"
    mints = sorted(ip.glob("PLANNER_MINTED_*.md"))
    assert mints, "no mints on disk: this control would pass on an empty population"

    a = {n for n, _ in drawable_undrawn_mints(ip)}
    b = {n for n in selfdrawable_mint_in_progress(ip) if n.startswith("PLANNER_MINTED_")}
    assert a == b, (
        "two independent readers of `SUPERVISOR_DRAW:` disagree about which mints are drawable: "
        "only in primary_state_scan={}, only in staging_disposition={}".format(a - b, b - a))


def test_every_parked_mint_declares_itself_readably():
    """The convention's own precondition. A mint carrying neither marker is parked forever with no
    reason anyone can read, which is how work goes missing rather than being decided against."""
    ip = dms.STAGING_DIR / "in_progress"
    mints = sorted(ip.glob("PLANNER_MINTED_*.md"))
    assert mints, "no mints on disk: this control would pass on an empty population"
    for p in mints:
        body = p.read_text(encoding="utf-8", errors="replace")
        assert re.search(r"SUPERVISOR_DRAW:\s*(self-drawable|blocked)", body, re.IGNORECASE), (
            "{} carries no SUPERVISOR_DRAW marker, so it is invisible to the draw and reported "
            "as blocked with no stated reason".format(p.name))
