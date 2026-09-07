"""A commons entry's CITATION must support the PROVENANCE LEVEL that entry claims for itself.

Subject: `tools/commons_citation_supports_provenance.py`.
Commons: `docs/domain_artefact_library/`.
Sits beside: `tests/architecture/test_a_commons_artefact_can_tell_when_its_source_was_revised.py`,
which grades the DIFFERENT question -- has the source moved since we read it.

WHY THIS FILE EXISTS. On 2026-09-07 two commons artefacts were repaired for citing superseded
publications. The repair pass found a second defect one row over that the supersession checker
structurally cannot see: `ro_obligation_and_buyout`'s obligation year 2025 buy-out price was stamped
`primary` while citing the 2026-27 notice, which that file's own legend defines as `secondary`. No
publisher was needed to see it -- 2026 is after 2025, and that is visible from the artefact's bytes.

REACH IS PROVEN BY A POISON ROUND PER LEG, AND THE NOT_AFTER LEG IS PROVEN AGAINST THE REAL DEFECT.
`test_the_not_after_leg_refuses_the_real_artefact_as_it_stood_before_the_repair` reads the actual
pre-repair bytes out of commit 5a2778d06 and asserts the refusal names that entry. A synthetic
fixture would only have proved the leg fires on a fixture built to make it fire.

THE DIRECTION IS THE WHOLE SUBTLETY, and it has its own control. A citation EARLIER than its subject
is ordinary and correct: `ccl_main_rates` cites the Finance Act 2016 for rates commencing 2017,
because that is the Act that set them. An undirected "the years disagree" leg would refuse ten
correct rows to catch one wrong one, so `test_a_source_earlier_than_its_subject_is_not_refused`
holds the leg to LATER only, and `test_the_ccl_act_shape_is_accepted_by_the_live_commons` pins that
against real data rather than against a fixture written to agree.

KEYED TO THE PROPERTY, NEVER TO TODAY'S ANSWER. Nothing here pins an artefact to a level, a year or
a URL. Demoting an entry to `secondary` is a green change, so is re-pointing it at its own year's
notice, and so is adding a tenth artefact that stamps no provenance at all. Only claiming the
strongest level over a citation that cannot bear it is refused.

WHAT A PASS DOES NOT MEAN, asserted rather than left to the reader. `test_the_report_states_how_much
_of_the_commons_this_can_actually_grade` fixes that the module can place only some primary entries
in time, and `test_an_artefact_stamping_no_provenance_is_silent_not_green` fixes that four of the
nine artefacts are outside this control entirely.
"""
from __future__ import annotations

import copy
import json
import subprocess
from pathlib import Path

import pytest

from tools.commons_citation_supports_provenance import (
    COMMONS,
    STRONGEST,
    Refusal,
    artefact_paths,
    check,
    check_artefact,
    period_year,
    report,
    years_in,
)

#: The commit that landed the supersession detector and, deliberately, did NOT repair what it found.
#: Its copy of the RO artefact still carries the defect this module was built for.
BEFORE_THE_REPAIR = "5a2778d06"

RO = "docs/domain_artefact_library/regulatory/ro_obligation_and_buyout.json"

VALID = {
    "artefact": "subject",
    "provenance_legend": {
        "primary": "read from THIS entry's own source during the pass that wrote it",
        "secondary": "read from another year's notice quoting it",
    },
    "rows": [
        {
            "obligation_year": 2024,
            "gbp_per_roc": 64.73,
            "provenance": "primary",
            "source": "https://example.invalid/buy-out-price-2024-2025",
        },
        {
            "obligation_year": 2025,
            "gbp_per_roc": 67.06,
            "provenance": "secondary",
            "source": "https://example.invalid/buy-out-price-2026-2027",
        },
    ],
}


def _write(tmp_path: Path, doc: dict, name: str = "subject") -> Path:
    path = tmp_path / f"{name}.json"
    path.write_text(json.dumps(doc, indent=2), encoding="utf-8")
    return path


def _legs(refusals: list[Refusal]) -> set[str]:
    return {r.leg for r in refusals}


# --------------------------------------------------------------------------------------------
# The live commons
# --------------------------------------------------------------------------------------------


def test_the_live_commons_is_coherent() -> None:
    """Every artefact in the tree passes all three legs.

    On its own this asserts almost nothing -- a check that refused nothing would pass it too -- and
    the poison rounds below are what make it mean something. It is here because the module is wired
    into the pre-commit hook, so a red here is a wedged tree for every lane.
    """
    refusals = check()
    assert refusals == [], "\n".join(str(r) for r in refusals)


def test_every_commons_artefact_is_covered_and_the_census_is_not_empty() -> None:
    """The census walks the whole library, subdirectories included."""
    rows = report()
    assert {r["artefact"] for r in rows} == {p.stem for p in artefact_paths()}
    assert len(rows) >= 9


def test_an_artefact_stamping_no_provenance_is_silent_not_green() -> None:
    """The named limit of this control, fixed so a pass is never read as full coverage.

    Four of the nine artefacts stamp no provenance anywhere. This module says NOTHING about them,
    and that is a gap in the commons rather than a property of those files. If a later pass gives
    them provenance this control starts grading them and this assertion is the thing that has to be
    updated -- which is the point: the gap is visible rather than inferred from a green.
    """
    silent = [r for r in report() if r["stamped"] == 0]
    assert silent, "expected at least one artefact outside this control; the limit is real"
    for row in silent:
        path = next(p for p in artefact_paths() if p.stem == row["artefact"])
        assert check_artefact(path) == []


def test_the_report_states_how_much_of_the_commons_this_can_actually_grade() -> None:
    """`placeable_in_time` is below `strongest`, and the module does not pretend otherwise.

    A primary entry with no period key, or with a year-less rolling-page URL, is one NOT_AFTER
    cannot grade. Eight RO buy-out rows are exactly that shape. Asserting the inequality keys the
    control to the PROPERTY that coverage is partial, not to today's counts.
    """
    rows = report()
    strongest = sum(r["strongest"] for r in rows)
    placeable = sum(r["placeable_in_time"] for r in rows)
    assert 0 < placeable < strongest, (
        f"{placeable} of {strongest} primary entries placeable; a module that could place all of "
        "them, or none, is not the one this test was written against"
    )


def test_the_ccl_act_shape_is_accepted_by_the_live_commons() -> None:
    """A real primary row citing a source EARLIER than its subject survives, against real data.

    `ccl_main_rates` cites Finance Act 2016 for rates commencing 2017 and 2018. If NOT_AFTER were
    undirected this would be refused. Written against the live artefact rather than a fixture,
    because a fixture would only prove the leg agrees with the fixture.
    """
    path = COMMONS / "regulatory" / "ccl_main_rates.json"
    doc = json.loads(path.read_text())
    earlier = [
        row for row in doc["rates"]
        if row.get("provenance") == STRONGEST
        and isinstance(row.get("source"), str)
        and years_in(row["source"])
        and period_year(row) is not None
        and max(years_in(row["source"])) < period_year(row)
    ]
    assert earlier, "expected at least one primary row citing an earlier document; none found"
    assert check_artefact(path) == []


# --------------------------------------------------------------------------------------------
# NOT_AFTER -- the leg this module was built for
# --------------------------------------------------------------------------------------------


def test_the_not_after_leg_refuses_the_real_artefact_as_it_stood_before_the_repair(
    tmp_path: Path,
) -> None:
    """The real defect, from the real bytes, out of the commit that still carried it.

    This is the reachability evidence for the whole module. It reads
    `ro_obligation_and_buyout.json` at 5a2778d06 -- obligation year 2025 stamped `primary` while
    citing the 2026-27 notice -- and asserts NOT_AFTER fires on that entry and names both years.
    """
    raw = subprocess.run(
        ["git", "show", f"{BEFORE_THE_REPAIR}:{RO}"],
        capture_output=True, text=True, check=True,
        cwd=Path(__file__).resolve().parents[2],
    ).stdout
    doc = json.loads(raw)

    offending = [
        row for row in doc["buy_out_prices"]
        if row["obligation_year"] == 2025 and row["provenance"] == STRONGEST
    ]
    assert offending, (
        "the pre-repair artefact no longer carries the defect this test exists to catch; the "
        "fixture is spent and the test proves nothing until it is re-pointed"
    )
    assert "2026-2027" in offending[0]["source"]

    path = _write(tmp_path, doc, name="ro_obligation_and_buyout")
    refusals = check_artefact(path)
    not_after = [r for r in refusals if r.leg == "NOT_AFTER"]
    assert len(not_after) == 1, refusals
    assert "2025" in not_after[0].detail and "2026" in not_after[0].detail
    assert "buy_out_prices[9]" in not_after[0].detail


def test_the_repaired_artefact_passes_because_it_became_more_honest() -> None:
    """The same entry, demoted to `secondary`, is green -- and green for the right reason.

    Keyed to the property: what discharges the refusal is the LEVEL matching the evidence, not the
    URL being edited to hide the year. The entry still cites the 2026-27 notice.
    """
    path = COMMONS / "regulatory" / "ro_obligation_and_buyout.json"
    doc = json.loads(path.read_text())
    row = next(r for r in doc["buy_out_prices"] if r["obligation_year"] == 2025)
    assert row["provenance"] == "secondary"
    assert "2026-2027" in row["source"]
    assert check_artefact(path) == []


def test_the_not_after_leg_fires_on_a_synthetic_later_citation(tmp_path: Path) -> None:
    doc = copy.deepcopy(VALID)
    assert doc["rows"][0]["source"].endswith("2024-2025")  # the target was present
    doc["rows"][0]["source"] = "https://example.invalid/buy-out-price-2026-2027"
    refusals = check_artefact(_write(tmp_path, doc))
    assert _legs(refusals) == {"NOT_AFTER"}
    assert "rows[0]" in refusals[0].detail


def test_a_source_earlier_than_its_subject_is_not_refused(tmp_path: Path) -> None:
    """The Finance Act shape, as a fixture, so the direction is pinned as well as observed."""
    doc = copy.deepcopy(VALID)
    doc["rows"][0]["source"] = "https://example.invalid/finance-act-2016/section/145"
    assert check_artefact(_write(tmp_path, doc)) == []


def test_a_citation_naming_both_the_entry_year_and_a_later_one_is_accepted(
    tmp_path: Path,
) -> None:
    """`.../2024-2025` for obligation year 2024 is the entry's OWN notice, not a restatement.

    The leg is `min(cited) > year`, not `max(cited) > year`, and this is the control over that
    choice: a two-year obligation-period URL names a later year by construction, and refusing on
    the maximum would refuse every correctly-cited row in the file.
    """
    doc = copy.deepcopy(VALID)
    doc["rows"][0]["source"] = "https://example.invalid/level-calculations-2024-to-2025/calculating"
    assert check_artefact(_write(tmp_path, doc)) == []


def test_a_weaker_level_may_cite_a_later_document(tmp_path: Path) -> None:
    """Only the strongest level is held to this. `secondary` MEANS a later restatement."""
    doc = copy.deepcopy(VALID)
    assert doc["rows"][1]["provenance"] == "secondary"
    assert min(years_in(doc["rows"][1]["source"])) > doc["rows"][1]["obligation_year"]
    assert check_artefact(_write(tmp_path, doc)) == []


def test_a_year_less_url_is_not_graded_rather_than_passed(tmp_path: Path) -> None:
    """A rolling page cannot be placed in time, so the leg is silent about it.

    This is a real weakness -- eight live RO rows are this shape -- and it is fixed here as a
    KNOWN limit so nobody reads their green as evidence of anything.
    """
    doc = copy.deepcopy(VALID)
    doc["rows"][0]["source"] = "https://example.invalid/renewables-obligation/suppliers"
    assert years_in(doc["rows"][0]["source"]) == []
    assert check_artefact(_write(tmp_path, doc)) == []


@pytest.mark.parametrize(
    "url",
    [
        "https://example.invalid/media/5a80b6cf40f0b62305b8cbc4/note.pdf",
        "https://example.invalid/uploads/attachment_data/file/464685/notice.pdf",
    ],
)
def test_a_hex_id_or_asset_number_does_not_manufacture_a_year(tmp_path: Path, url: str) -> None:
    """The false-positive shape that would have made this leg untrustworthy on real URLs.

    Both of these are live RO `source` URLs. Without the non-alphanumeric boundary in the year
    pattern, an id like `...b62305b8...` yields a year and refuses a correct row.
    """
    assert years_in(url) == []
    doc = copy.deepcopy(VALID)
    doc["rows"][0]["source"] = url
    assert check_artefact(_write(tmp_path, doc)) == []


# --------------------------------------------------------------------------------------------
# DEFINED
# --------------------------------------------------------------------------------------------


def test_the_defined_leg_fires_when_there_is_no_legend_at_all(tmp_path: Path) -> None:
    doc = copy.deepcopy(VALID)
    del doc["provenance_legend"]
    refusals = check_artefact(_write(tmp_path, doc))
    assert _legs(refusals) == {"DEFINED"}
    assert "provenance_legend" in refusals[0].detail


def test_the_defined_leg_fires_on_a_level_the_legend_does_not_define(tmp_path: Path) -> None:
    doc = copy.deepcopy(VALID)
    assert doc["rows"][0]["provenance"] in doc["provenance_legend"]  # the target was present
    doc["rows"][0]["provenance"] = "asserted"
    refusals = check_artefact(_write(tmp_path, doc))
    assert _legs(refusals) == {"DEFINED"}
    assert "'asserted'" in refusals[0].detail


def test_an_undefined_level_is_not_then_graded_as_if_it_were_primary(tmp_path: Path) -> None:
    """One refusal, not two. An undefined level cannot also be judged against a definition."""
    doc = copy.deepcopy(VALID)
    doc["rows"][0]["provenance"] = "asserted"
    doc["rows"][0]["source"] = "https://example.invalid/buy-out-price-2026-2027"
    refusals = check_artefact(_write(tmp_path, doc))
    assert [r.leg for r in refusals] == ["DEFINED"]


def test_the_defined_leg_fires_on_the_live_switching_artefact_as_it_stood_before_this_commit(
    tmp_path: Path,
) -> None:
    """Reachability for DEFINED on real data: `gb_domestic_switching_rate` had no legend.

    Ten rows stamped `primary` in a file whose own `how_to_recheck` says it cites a derivation and
    not an edition. This reconstructs that state from the live artefact by removing the legend that
    this commit added, so the test cannot go quietly vacuous if the file is later restructured.
    """
    path = COMMONS / "regulatory" / "gb_domestic_switching_rate.json"
    doc = json.loads(path.read_text())
    assert doc["provenance_legend"], "the legend this test removes is gone; re-point the test"
    del doc["provenance_legend"]
    refusals = check_artefact(_write(tmp_path, doc, name="gb_domestic_switching_rate"))
    assert _legs(refusals) == {"DEFINED"}
    assert "10 entries" in refusals[0].detail


# --------------------------------------------------------------------------------------------
# CITED
# --------------------------------------------------------------------------------------------


def test_the_cited_leg_fires_when_a_sibling_cites_and_this_one_does_not(tmp_path: Path) -> None:
    doc = copy.deepcopy(VALID)
    assert doc["rows"][0]["source"]  # the target was present
    del doc["rows"][0]["source"]
    refusals = check_artefact(_write(tmp_path, doc))
    assert _legs(refusals) == {"CITED"}
    assert "rows[0]" in refusals[0].detail


def test_the_cited_leg_is_silent_when_no_sibling_cites_either(tmp_path: Path) -> None:
    """The file-level-citation shape, which `capacity_market_auction_results` really uses.

    Twenty-five register rows carry no per-entry source and name one register at the top level.
    A leg demanding a per-entry URL would refuse all twenty-five to catch nothing.
    """
    doc = copy.deepcopy(VALID)
    for row in doc["rows"]:
        row.pop("source", None)
        row["provenance"] = STRONGEST
    assert check_artefact(_write(tmp_path, doc)) == []


def test_an_empty_source_string_does_not_count_as_a_citation(tmp_path: Path) -> None:
    doc = copy.deepcopy(VALID)
    doc["rows"][0]["source"] = "   "
    refusals = check_artefact(_write(tmp_path, doc))
    assert _legs(refusals) == {"CITED"}


# --------------------------------------------------------------------------------------------
# The valid fixture, and the parts
# --------------------------------------------------------------------------------------------


def test_the_valid_fixture_is_accepted(tmp_path: Path) -> None:
    """Without this every refusal above could be the fixture rather than the mutation."""
    assert check_artefact(_write(tmp_path, copy.deepcopy(VALID))) == []


def test_unreadable_json_is_refused_rather_than_skipped(tmp_path: Path) -> None:
    path = tmp_path / "broken.json"
    path.write_text("{not json", encoding="utf-8")
    refusals = check_artefact(path)
    assert _legs(refusals) == {"DEFINED"}


@pytest.mark.parametrize(
    ("entry", "expected"),
    [
        ({"obligation_year": 2024}, 2024),
        ({"year": 2016}, 2016),
        ({"from": "2019-04-01"}, 2019),
        ({"delivery_year": "2024/25"}, 2024),
        ({"cap_period": "April 2022 - September 2022"}, 2022),
        ({"gbp_per_roc": 64.73}, None),
    ],
)
def test_the_period_key_reader_takes_the_year_the_period_begins(
    entry: dict, expected: int | None
) -> None:
    assert period_year(entry) == expected


def test_a_document_date_is_not_mistaken_for_the_subject_period() -> None:
    """`fetched` and `published_year` are about the DOCUMENT, and are not period keys.

    Comparing a document's own date to its own URL's date would be a tautology wearing a control's
    clothes -- it would always agree, and it would say nothing about the value.
    """
    assert period_year({"fetched": "2026-09-07", "published_year": 2026}) is None
