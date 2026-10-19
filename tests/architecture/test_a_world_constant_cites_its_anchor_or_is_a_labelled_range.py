"""A constant the world draws from cites its anchor or is a labelled evidence range.

Director steer, 19 Oct 2026, item 1 ("Anchor or range"). The definition of the population, the two
origins that discharge it, and why it is an exact set rather than a count: `tools/world_constant_anchors.py`.

WHAT EACH TEST NAMES AS ITS OWN DEFECT:

  * `test_the_register_is_EXACTLY_the_bare_world_constants` -- a number added to the world because a
    number was needed. The 13 July fuel-split "placeholder" and `DEFAULT_BAND_WEIGHTS` are the
    shape. Reds both ways: a new bare constant by name, and an anchored one still listed.
  * `test_the_scan_has_not_lost_its_SUBJECTS` -- the population floor. A scan that finds nothing
    reports a register of zero owed and goes green forever.
  * `test_an_UNPARSEABLE_world_file_is_reported` -- a file that will not parse contributes no
    constants, so it can only make the register look smaller.
  * `test_every_ANCHOR_verdict_is_reachable_and_a_placeholder_must_cite` -- one control over the
    whole partition: a classifier that reads every comment as cited, or none as a range, or lets
    "placeholder" stand as an anchor, passes the exact-set test against a register written by the
    same broken classifier.
  * `test_a_new_bare_constant_is_refused_BY_NAME` -- the rare branch, asserted takeable on a
    synthetic tree rather than assumed from today's empty diff.

R15 MUTATIONS, each applied in place and reverted, 2026-10-19. The counts were written down as
predictions before the run and four of five were wrong in the count, never in the direction; these
are the observed ones:

  * `anchor` returns "cited" unconditionally -> 3 red (exact set: all 446 to strike; partition;
    refused-by-name).
  * `_RANGE` matches nothing -> 2 red (partition; refused-by-name, whose ranged constant goes bare).
  * the placeholder refusal deleted -> 1 red (partition only). The exact set stays green, because
    no constant in the tree today pairs "placeholder" with a range label and no source -- an
    equivalence on this tree, which is why the partition test carries that case.
  * `_has_float` always False -> 3 red (floor and subject; exact set; refused-by-name).
  * `_files` yields nothing -> 3 red (floor and subject; exact set; refused-by-name).
"""
from __future__ import annotations

from tools.world_constant_anchors import anchor, bare, registered, scan


def test_the_register_is_EXACTLY_the_bare_world_constants():
    owed, listed = bare(), registered()
    new, struck = sorted(owed - listed), sorted(listed - owed)
    assert not new, (
        f"{len(new)} world constant(s) carry a bare number -- cite the knowledge page or source in "
        f"the comment above, or label it EVIDENCE RANGE (W7, W8). Do not add them to the register: "
        f"it only shrinks. {new[:10]}")
    assert not struck, (
        f"{len(struck)} constant(s) are anchored (or gone) but still listed in "
        f"docs/design/world_constant_anchor_register.txt -- strike these lines: {struck[:10]}")


def test_the_scan_has_not_lost_its_SUBJECTS():
    rows, _ = scan()
    keys = {r["key"] for r in rows}
    assert len(rows) >= 500, f"the world scan found only {len(rows)} constants; it found 557 on 2026-10-19"
    assert "simulation/population_draw.py::DEFAULT_BAND_WEIGHTS" in keys, (
        "the scan no longer sees DEFAULT_BAND_WEIGHTS, the steer's named first entry")


def test_an_UNPARSEABLE_world_file_is_reported():
    _, unreadable = scan()
    assert unreadable == [], f"these world files did not parse and were not scanned: {unreadable}"


def test_every_ANCHOR_verdict_is_reachable_and_a_placeholder_must_cite():
    verdicts = {
        "# Share of homes: docs/market_research/fuel_split.md": "cited",
        "# Ofgem consumer survey 2023, table 4": "cited",
        "# EVIDENCE RANGE 0.2-0.4; no published take-up, swept in the sensitivity": "range",
        "# documented placeholder until a source is found": None,
        "# placeholder, EVIDENCE RANGE 0.2-0.4": None,
        "# placeholder until docs/market_research/fuel_split.md lands": "cited",
        "# SIMPLIFIED: one band": None,
        "# looks about right": None,
    }
    got = {c: anchor(c) for c in verdicts}
    assert set(got.values()) == {"cited", "range", None}
    assert got == verdicts


def test_a_new_bare_constant_is_refused_BY_NAME(tmp_path):
    pkg = tmp_path / "simulation"
    pkg.mkdir()
    (pkg / "m.py").write_text(
        "# docs/market_research/x.md\nCITED_SHARE = 0.75\n\n"
        "# EVIDENCE RANGE 0.1-0.3\nRANGED_SHARE = 0.2\n\n"
        "BARE_SHARE = 0.4\n\nPERIODS = 48\n", encoding="utf-8")
    assert bare(tmp_path) == {"simulation/m.py::BARE_SHARE"}
