"""A commons artefact that publishes a REFUTATION of its own values must keep it true.

Subject: `docs/domain_artefact_library/regulatory/gb_domestic_switching_rate.json` and any other
commons artefact that grows a `values_refuted_by_the_publisher` block.

THE DEFECT THIS EXISTS FOR, and it is a shape this project has paid for repeatedly. On 2026-09-07
the switching artefact was found to disagree with the publisher's own release in 8 of 10 years. The
values could not be corrected in that landing -- the committed world capture embeds them, so the
repair needs a re-capture -- so the artefact carries the refutation as a block BESIDE the wrong
values, with the publisher's figures tabulated in it.

That is an honest state and it is also a fragile one. The block is a MEASUREMENT of `rates` against
the publisher, stored next to `rates`, and nothing stops the two drifting apart:

  - a later session corrects ONE band and leaves the comparison flags saying it is still refuted, so
    the file reports a defect it no longer has;
  - or WIDENS a band until it swallows the publisher's figure, which makes the refutation disappear
    without a single value being corrected -- the cheapest possible way to turn this finding green;
  - or corrects every band properly and leaves the block in place, so the artefact permanently
    accuses itself of a defect it has fixed and the next reader cannot tell which half to believe;
  - or marks the artefact `current` while the values the cited edition contradicts are still there.

KEYED TO THE PROPERTY, NEVER TO TODAY'S ANSWER. Nothing here asserts "8 of 10". The assertion is
*the stored refutation recomputes from the bands actually in this file*, so landing the real repair
passes as soon as the block is regenerated, and it fails on the day the block stops being true --
in EITHER direction. A control pinned at 8 would have to be edited by the very commit that fixes the
defect, which is how a control ends up being tuned to whatever the tree currently says.

R15: every control below names the mutation that must make it fire.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

COMMONS_DIR = (
    Path(__file__).resolve().parent.parent.parent
    / "docs" / "domain_artefact_library" / "regulatory"
)

_BLOCK = "values_refuted_by_the_publisher"


def _artefacts_with_a_refutation() -> list[tuple[str, dict]]:
    """Every commons artefact carrying a refutation block, by filename."""
    out = []
    for path in sorted(COMMONS_DIR.glob("*.json")):
        payload = json.loads(path.read_text())
        if isinstance(payload.get(_BLOCK), dict):
            out.append((path.name, payload))
    return out


def _bands_by_year(payload: dict) -> dict[int, tuple[float, float]]:
    return {
        int(r["year"]): (float(r["rate_pct_lo"]), float(r["rate_pct_hi"]))
        for r in payload["rates"]
        if r.get("rate_pct_lo") is not None and r.get("rate_pct_hi") is not None
    }


def _recompute(payload: dict) -> list[tuple[int, bool, bool]]:
    """`[(year, stored_flag, recomputed_flag)]` for every row of the comparison."""
    bands = _bands_by_year(payload)
    rows = []
    for row in payload[_BLOCK]["comparison"]:
        year = int(row["year"])
        lo, hi = bands[year]
        rows.append((
            year,
            bool(row["band_contains_the_publisher"]),
            lo <= float(row["published_rate_pct"]) <= hi,
        ))
    return rows


def test_the_subject_is_present_and_the_register_is_not_empty() -> None:
    """The whole file is vacuous if no artefact carries a refutation.

    MUTATION THAT MUST FIRE: delete the `values_refuted_by_the_publisher` block from the switching
    artefact without correcting its values. Every other control here quantifies over an empty list
    and passes, which is the fail-open shape -- 'absent' reading as 'clean'.
    """
    found = _artefacts_with_a_refutation()
    assert found, (
        "no commons artefact carries a `values_refuted_by_the_publisher` block. If the switching "
        "artefact's values were corrected, the block is removed legitimately -- and this control "
        "must then be retired WITH its subject, not left passing over nothing."
    )
    assert "gb_domestic_switching_rate.json" in {name for name, _ in found}


@pytest.mark.parametrize("name,payload", _artefacts_with_a_refutation())
def test_the_stored_refutation_recomputes_from_the_bands_in_this_file(
    name: str, payload: dict
) -> None:
    """Each comparison flag must agree with the band the file actually carries today.

    MUTATION THAT MUST FIRE, and there are two in opposite directions: (a) widen any refuted year's
    `rate_pct_hi` until it swallows `published_rate_pct` -- the refutation vanishes with no value
    corrected; (b) correct a year's band to the publisher and leave its flag `false`.
    """
    disagreements = [
        (year, stored, live) for year, stored, live in _recompute(payload) if stored != live
    ]
    assert not disagreements, (
        f"{name}: the stored refutation no longer describes this file's own bands "
        f"{disagreements} (year, stored_flag, recomputed_flag). Regenerate the block beside the "
        "values it measures -- a refutation that has drifted from its subject is worse than none, "
        "because it reads as though the question has been asked."
    )


@pytest.mark.parametrize("name,payload", _artefacts_with_a_refutation())
def test_the_headline_count_matches_the_rows_it_summarises(name: str, payload: dict) -> None:
    """The prose headline must not disagree with the table under it.

    MUTATION THAT MUST FIRE: edit `headline` to say '2 of 10' while the comparison still carries 8
    refuted rows. The catalogued *severity column disagrees with the verdict beside it*, in a file
    whose headline is the only part most readers will read.
    """
    refuted = sum(1 for _, _, live in _recompute(payload) if not live)
    total = len(payload[_BLOCK]["comparison"])
    headline = payload[_BLOCK]["headline"]
    assert f"{refuted} of {total}" in headline, (
        f"{name}: headline {headline!r} does not state the {refuted} of {total} its own comparison "
        "table computes."
    )


@pytest.mark.parametrize("name,payload", _artefacts_with_a_refutation())
def test_an_artefact_with_live_refuted_values_is_not_marked_current(
    name: str, payload: dict
) -> None:
    """`current` is the one verdict a refuted artefact may not carry.

    `superseded` is honest here and `cannot_tell` is available; `current` asserts the values agree
    with the cited edition, which is the exact claim the comparison refutes.

    MUTATION THAT MUST FIRE: flip `checked_for_supersession.found` to `current` while any row is
    still refuted -- the single edit that would make this artefact read as settled.
    """
    refuted = [year for year, _, live in _recompute(payload) if not live]
    verdict = payload["source_check"]["checked_for_supersession"]["found"]
    if refuted:
        assert verdict != "current", (
            f"{name}: verdict is `current` while the publisher's own release contradicts "
            f"{len(refuted)} year(s) {refuted}. Correct the values or keep the verdict honest."
        )


@pytest.mark.parametrize("name,payload", _artefacts_with_a_refutation())
def test_no_row_is_stamped_primary_against_an_edition_that_refutes_it(
    name: str, payload: dict
) -> None:
    """A refuted year may not claim it was read from the publisher.

    MUTATION THAT MUST FIRE: stamp the refuted 2017 row `primary`. It is the cheapest way to make
    `commons_citation_supports_provenance` count this artefact as sourced, and it would be false in
    the strongest possible way -- claiming the publisher as the origin of a number the publisher
    contradicts.
    """
    refuted = {year for year, _, live in _recompute(payload) if not live}
    offenders = [
        int(r["year"]) for r in payload["rates"]
        if int(r["year"]) in refuted and r.get("provenance") == "primary"
    ]
    assert not offenders, (
        f"{name}: years {offenders} are stamped `primary` while the cited edition refutes them."
    )


def test_the_poison_round_every_leg_above_can_fail() -> None:
    """Reachability, proved on a witness rather than asserted in a docstring.

    A payload built to be wrong in each way must be caught by the corresponding recomputation. This
    runs FIRST in intent even though it sits last: 'the battery passed' means two opposite things
    until the harness is shown refusing something.
    """
    poison = {
        "rates": [
            {"year": 2017, "rate_pct_lo": 13.5, "rate_pct_hi": 14.0, "provenance": "primary"},
            {"year": 2019, "rate_pct_lo": 20.7, "rate_pct_hi": 21.3, "provenance": "secondary"},
        ],
        _BLOCK: {
            "headline": "0 of 2 bands do not contain the publisher's own figure for that year.",
            "comparison": [
                # stored flag LIES: 18.195 is not inside 13.5-14.0
                {"year": 2017, "published_rate_pct": 18.195,
                 "band_contains_the_publisher": True},
                {"year": 2019, "published_rate_pct": 20.822,
                 "band_contains_the_publisher": True},
            ],
        },
        "source_check": {"checked_for_supersession": {"found": "current"}},
    }

    rows = _recompute(poison)
    assert (2017, True, False) in rows, "the drifted flag was not detected"

    refuted = [y for y, _, live in rows if not live]
    assert refuted == [2017], "the refuted year was not recomputed from the live band"

    # the headline leg
    assert f"{len(refuted)} of {len(rows)}" not in poison[_BLOCK]["headline"]
    # the verdict leg
    assert poison["source_check"]["checked_for_supersession"]["found"] == "current"
    # the primary-stamp leg
    assert [
        int(r["year"]) for r in poison["rates"]
        if int(r["year"]) in set(refuted) and r.get("provenance") == "primary"
    ] == [2017]
