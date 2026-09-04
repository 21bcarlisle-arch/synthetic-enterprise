"""The SVT share check's verdict must track the published BAND, and must not fail open.

THE DEFECT THIS EXISTS TO CATCH, and it had already happened. `tools/svt_generated_share_check`
printed `OUT` beside eight of eight judged years and `main()` ended `return 0`. So the one control
over the world's product mix reported PASS to every possible consumer while displaying its own
refutation, and `SEAT_FINDING_THE_WORLDS_FIXED_DEAL_SHARE_IS_OUTSIDE_THE_PUBLISHED_BAND_IN_EVERY_YEAR`
records that nothing read it. That is this repository's FAIL-OPEN shape: a verdict computed,
rendered for a human, and thrown away before anything could act on it.

WHAT IS ASSERTED HERE AND WHAT DELIBERATELY IS NOT. `tests/simulation/test_svt_product.py` states
the rule this file obeys: *"a control that pinned a year's share would be keyed to today's answer"*.
So nothing below asserts that the world IS in band -- it is not, in every judged year, and forgiving
that is the head-red register's business and a human's, not a test's. What is asserted is the
PROPERTY: given a share and a band, the verdict and the exit code follow the band. These stay green
when the world is repaired and go red if the comparison is ever severed, which is the direction a
control has to fail in.

THE THIRD STATE IS THE POINT OF THE SECOND TEST. 2020 and 2021 carry no established figure. Rolling
them into the pass branch would let the check report conformance over years it never judged -- the
mixed-subject shape where a verdict over an unobservable class reads as PASS.

REUSE
-----
REUSE: tests/tools/test_the_svt_share_check_verdict_is_keyed_to_the_band.py
CLASS: CUSTOM
INDEX: searched "svt share", "share check", "tariff mix", "band", "fail open", "verdict",
       "exit code". `tests/simulation/test_svt_product.py` and `test_svt_assignment.py` both name
       this tool, and both do so in a DOCSTRING to explain what they are not asserting -- neither
       imports it and neither has a subject on the tools/ side. `tests/tools/` holds no existing
       control over a published-versus-generated report's exit code.
"""
from __future__ import annotations

import json

import pytest

from tools.published_tariff_mix import fixed_share
from tools.svt_generated_share_check import (
    CANNOT_TELL,
    IN_BAND,
    OUT_OF_BAND,
    CannotMeasure,
    build_verdict,
    main,
)

BASIS = "all_domestic"
#: A year the published record establishes, and one it does not. Both are read from the commons
#: rather than hard-coded, so this file cannot drift from the series it is judging against.
A_BANDED_YEAR = 2022
AN_UNBANDED_YEAR = 2020


def _rows(share_by_year: dict[int, float]) -> dict[int, dict]:
    """Year -> the row shape `generated_fixed_share_by_year` returns. Int keys, as it produces."""
    return {
        year: {"total_account_days": 1000, "fixed_share": share, "svt_share": 1.0 - share}
        for year, share in share_by_year.items()
    }


def test_the_bands_are_the_ones_this_file_assumes() -> None:
    """A scope check, kept AHEAD of nothing so a band change reads as a band change."""
    assert fixed_share(A_BANDED_YEAR, BASIS) is not None, (
        f"{A_BANDED_YEAR} no longer carries a published band; pick another banded year"
    )
    assert fixed_share(AN_UNBANDED_YEAR, BASIS) is None, (
        f"{AN_UNBANDED_YEAR} now carries a published band; pick another unestablished year"
    )


def test_a_share_inside_the_band_passes_and_one_outside_it_fails() -> None:
    """The verdict is `lo <= share <= hi` and nothing else. Mutate the comparison and this dies."""
    lo, hi = fixed_share(A_BANDED_YEAR, BASIS)

    inside = build_verdict(_rows({A_BANDED_YEAR: (lo + hi) / 2}), BASIS)
    assert inside["status"] == IN_BAND
    assert inside["years_out_of_band"] == []

    outside = build_verdict(_rows({A_BANDED_YEAR: hi + 0.10}), BASIS)
    assert outside["status"] == OUT_OF_BAND
    assert outside["years_out_of_band"] == [A_BANDED_YEAR]


@pytest.mark.parametrize("edge", ["lo", "hi"])
def test_the_band_is_inclusive_at_both_edges(edge: str) -> None:
    """A year exactly on an endpoint is inside it. A `<` for a `<=` is the silent one-year miss."""
    lo, hi = fixed_share(A_BANDED_YEAR, BASIS)
    report = build_verdict(_rows({A_BANDED_YEAR: lo if edge == "lo" else hi}), BASIS)
    assert report["status"] == IN_BAND


def test_a_year_with_no_established_figure_is_never_counted_as_conformance() -> None:
    """`CANNOT_TELL` is a third state. A subject made only of unjudged years is not a pass."""
    report = build_verdict(_rows({AN_UNBANDED_YEAR: 0.42}), BASIS)

    assert report["status"] == CANNOT_TELL, (
        "a year the published record does not establish was reported as conformance; the check "
        "would then read PASS over a subject it never judged"
    )
    assert report["years_judged"] == 0
    assert report["years_with_no_established_figure"] == [AN_UNBANDED_YEAR]
    assert report["years"][0]["why_no_verdict"], "an unjudged year must say why it was not judged"


def test_an_unjudged_year_cannot_mask_an_out_of_band_one() -> None:
    """The mixed subject: the verdict over several years is the WORST, not the OR of the passes."""
    lo, hi = fixed_share(A_BANDED_YEAR, BASIS)
    report = build_verdict(
        _rows({A_BANDED_YEAR: hi + 0.10, AN_UNBANDED_YEAR: 0.42}), BASIS
    )
    assert report["status"] == OUT_OF_BAND
    assert report["years_judged"] == 1


def test_the_exit_code_carries_the_verdict(monkeypatch, tmp_path, capsys) -> None:
    """THE ORIGINAL DEFECT: `main()` returned 0 while printing OUT in every judged year."""
    lo, hi = fixed_share(A_BANDED_YEAR, BASIS)
    out = tmp_path / "verdict.json"

    def _out_of_band(_report_end: str) -> dict[int, dict]:
        return _rows({A_BANDED_YEAR: hi + 0.10})

    monkeypatch.setattr(
        "tools.svt_generated_share_check.generated_fixed_share_by_year", _out_of_band
    )
    monkeypatch.setattr(
        "sys.argv", ["svt_generated_share_check", "--basis", BASIS, "--out", str(out)]
    )

    assert main() == 1, "the check printed OUT and exited 0, so no consumer could ever act on it"
    assert "OUT" in capsys.readouterr().out
    assert json.loads(out.read_text())["status"] == OUT_OF_BAND


def test_a_refusal_writes_the_artefact_rather_than_leaving_it_absent(
    monkeypatch, tmp_path, capsys
) -> None:
    """A refusal that writes nothing leaves a stale file readable as today's verdict."""
    out = tmp_path / "verdict.json"

    def _refuse(_report_end: str) -> dict[int, dict]:
        raise CannotMeasure("no cached SSP records for the window")

    monkeypatch.setattr("tools.svt_generated_share_check.generated_fixed_share_by_year", _refuse)
    monkeypatch.setattr(
        "sys.argv", ["svt_generated_share_check", "--basis", BASIS, "--out", str(out)]
    )

    assert main() == 2, (
        "a refusal must not share an exit code with a measured pass or a measured fail"
    )
    assert out.exists(), "the refusal wrote nothing, so the absence is silent"
    written = json.loads(out.read_text())
    assert written["status"] == CANNOT_TELL
    assert "no cached SSP records" in written["refused"], "a refusal must name its reason"
    assert "REFUSED" in capsys.readouterr().out
