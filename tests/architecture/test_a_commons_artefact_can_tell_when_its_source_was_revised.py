"""Every commons artefact can be ASKED whether the publication it cites has been revised since we read it.

Subject: `tools/commons_source_supersession.py`.
Commons: `docs/domain_artefact_library/`.
Opened by: `docs/staging/SEAT_FINDING_TWO_COMMONS_ARTEFACTS_CITE_A_PUBLICATION_THAT_HAS_MOVED_AND_FOUR_OF_NINE_COULD_NOT_BE_ASKED_2026-09-07.md`
Pre-registered in: `docs/staging/SEAT_PREREGISTRATION_WHICH_COMMONS_ARTEFACTS_CITE_A_SUPERSEDED_PUBLICATION_2026-09-07.md`

WHY THIS FILE EXISTS. On 2026-09-07 the CM supplier levy's 2024/25 row was 4.0% wrong in both lanes.
No values-vs-source control could have caught it: it was a CORRECT reading of Ofgem Annex 9 v1.8,
which published only Apr-Sep 2024. The artefact carried an honest caveat saying exactly that, and
the caveat travelled as prose while the number travelled as law. The defect was not the number and
not the citation -- it was that no machine could put the question "has this moved?", so nothing
could enumerate what needed re-reading.

REACH IS PROVEN BY A POISON ROUND PER LEG, NOT BY THE LIVE PASS. `test_the_live_commons_is_askable`
asserting green says almost nothing on its own -- a check that refused nothing would also pass it.
Every refusal leg below therefore takes a VALID artefact, introduces one named defect, and asserts
that specific leg fires and that the leg names the artefact. Each mutation asserts its target was
present before it was changed, so a patch that silently failed to apply cannot read as a survival.

AND THE LIVE PASS HAS ALREADY EARNED ITS KEEP: running `--check` against the tree BEFORE this
commit's blocks were written refused 9 of 9 artefacts, four of which carried no fetch date in any
form. That is the reachability evidence for the ASKABLE leg on real data.

KEYED TO THE PROPERTY, NEVER TO TODAY'S ANSWER. Nothing here pins an artefact to a version, a date
or a verdict. Re-checking a source and recording `current` is a green change; so is recording
`superseded` and opening the finding; so is adding a tenth artefact WITH a block. Only losing the
ability to ask is refused.
"""
from __future__ import annotations

import copy
import json
import subprocess
from datetime import date, timedelta
from pathlib import Path

import pytest

from tools.commons_source_supersession import (
    COMMONS,
    TOKEN_KINDS,
    UNRESOLVED_VERDICTS,
    VERDICTS,
    artefact_paths,
    check,
    check_artefact,
    report,
)

TODAY = date(2026, 9, 7)

REPO = Path(__file__).resolve().parents[2]

#: Any finding that really is in the tree. The obligation is that the path RESOLVES, so this is a
#: stand-in for "an act was performed", not a claim about this particular document.
A_FILED_FINDING = (
    "docs/staging/SEAT_FINDING_TWO_COMMONS_ARTEFACTS_CITE_A_PUBLICATION_THAT_HAS_MOVED"
    "_AND_FOUR_OF_NINE_COULD_NOT_BE_ASKED_2026-09-07.md"
)

#: Every `cannot_tell` this commons ever COMMITTED, as (commit, artefact). Found by walking all 26
#: commits touching `docs/domain_artefact_library/` on 2026-09-08; these are the real bytes the
#: OWNED leg exists to refuse, and there are no others.
EVERY_COMMITTED_CANNOT_TELL = (
    ("5a2778d06", "ofgem_cap_unit_rate_composition"),
    ("29b4dcd3b", "ofgem_cap_unit_rate_composition"),
    ("619ce4993", "ofgem_default_tariff_cap_windows"),
    ("a47792693", "gb_domestic_switching_rate"),
)

VALID = {
    "publication": "Ofgem Annex 9 'Levelisation allowance methodology and levelised cap levels'",
    "url": "https://www.ofgem.gov.uk/sites/default/files/2026-08/Annex-9-v1.11.xlsx",
    "fetched": "2026-09-01",
    "version_token": "v1.11",
    "version_token_is": "in_url",
    "how_to_recheck": "read the version in the Annex 9 filename the cap landing page links",
    "checked_for_supersession": {"on": "2026-09-07", "found": "current", "note": "still v1.11"},
}


def _write(tmp_path: Path, block: object, name: str = "subject") -> Path:
    path = tmp_path / f"{name}.json"
    doc = {"artefact": name, "what_this_is": "a fixture"}
    if block is not _ABSENT:
        doc["source_check"] = block
    path.write_text(json.dumps(doc, indent=2), encoding="utf-8")
    return path


_ABSENT = object()


def _legs(path: Path) -> list[str]:
    return [r.leg for r in check_artefact(path, TODAY)]


def _mutate(**changes: object) -> dict:
    """A copy of VALID with named changes, asserting every target was PRESENT before changing it.

    Without that assertion a typo'd key would add a field nobody reads, the leg would not fire,
    and the test would read as 'the control is fine' rather than 'the mutation never applied'.
    """
    out = copy.deepcopy(VALID)
    for key, value in changes.items():
        assert key in out, f"mutation target {key!r} absent from VALID -- the patch would not apply"
        if value is _ABSENT:
            del out[key]
        else:
            out[key] = value
    return out


# --------------------------------------------------------------------------------------
# The live commons
# --------------------------------------------------------------------------------------


def test_the_live_commons_is_askable() -> None:
    """DEFECT: an artefact lands with no way to ask whether its source has been revised.

    This is the leg that refused 9 of 9 before the blocks were written, and it is the one that
    fires when the NEXT artefact is added without one.
    """
    refusals = check(today=TODAY)
    assert refusals == [], "\n".join(str(r) for r in refusals)


def test_every_commons_artefact_is_covered_and_the_census_is_not_empty() -> None:
    """DEFECT: the census silently stops covering the library (e.g. scoped to the top level).

    `regulatory/` is a subdirectory today and the next subject will make another one. A non-empty
    assertion alone would pass on a census that found one file.
    """
    paths = artefact_paths()
    assert len(paths) >= 9, f"only {len(paths)} artefacts found -- census has narrowed"
    assert any(p.parent != COMMONS for p in paths), "census is not reaching subdirectories"


def test_a_superseded_verdict_in_the_live_commons_names_a_finding_that_exists() -> None:
    """DEFECT: a supersession is recorded and nothing is opened -- the CM levy failure repeated.

    Keyed to the property, not to which artefacts are superseded today: if none are, this passes
    vacuously and `test_the_actioned_leg_fires...` below carries the reach.
    """
    root = COMMONS.parent.parent
    for path in artefact_paths():
        block = json.loads(path.read_text(encoding="utf-8")).get("source_check", {})
        checked = block.get("checked_for_supersession", {})
        if checked.get("found") != "superseded":
            continue
        named = checked.get("open_finding")
        assert named, f"{path.stem} records superseded and names no finding"
        assert (root / named).exists(), f"{path.stem} names {named}, which is not in the tree"


# --------------------------------------------------------------------------------------
# One poison round per refusal leg
# --------------------------------------------------------------------------------------


def test_the_askable_leg_fires_when_the_block_is_absent(tmp_path: Path) -> None:
    """DEFECT: the artefact carries no `source_check` at all -- four of nine did."""
    assert _legs(_write(tmp_path, _ABSENT)) == ["ASKABLE"]


@pytest.mark.parametrize("field", ["publication", "url", "fetched"])
def test_the_askable_leg_fires_when_a_required_field_is_missing(
    tmp_path: Path, field: str
) -> None:
    """DEFECT: a block exists but is missing the thing that makes the question answerable.

    `fetched` is the load-bearing one: without it there is no 'since' for 'revised since'.
    """
    assert "ASKABLE" in _legs(_write(tmp_path, _mutate(**{field: _ABSENT})))


def test_the_askable_leg_fires_when_the_question_was_never_recorded_as_asked(
    tmp_path: Path,
) -> None:
    """DEFECT: a citation complete enough to check, that nobody ever checked."""
    assert "ASKABLE" in _legs(_write(tmp_path, _mutate(checked_for_supersession=_ABSENT)))


def test_a_fetch_date_that_is_not_a_date_is_refused(tmp_path: Path) -> None:
    """DEFECT: `fetched` reverts to the prose it used to be ('2026-08-19, EP14 source check').

    Two artefacts carried their date only inside an English sentence. A machine cannot difference
    that against a publisher's timestamp, which is the whole point of normalising the block.
    """
    prose = "2026-08-19, EP14 published cost stack RO source check"
    assert "ASKABLE" in _legs(_write(tmp_path, _mutate(fetched=prose)))


def test_the_coherent_leg_fires_when_a_check_predates_the_fetch_it_rechecks(
    tmp_path: Path,
) -> None:
    """DEFECT: a re-check dated before the read it re-checks -- it cannot have looked at it."""
    block = _mutate(fetched="2026-09-05")
    block["checked_for_supersession"]["on"] = "2026-09-01"
    assert "COHERENT" in _legs(_write(tmp_path, block))


@pytest.mark.parametrize("field", ["fetched", "on"])
def test_the_coherent_leg_fires_on_a_future_date(tmp_path: Path, field: str) -> None:
    """DEFECT: a date in the future -- a check that has not happened, recorded as if it had."""
    future = (TODAY + timedelta(days=30)).isoformat()
    if field == "fetched":
        block = _mutate(fetched=future)
        block["checked_for_supersession"]["on"] = future
    else:
        block = _mutate()
        block["checked_for_supersession"]["on"] = future
    assert "COHERENT" in _legs(_write(tmp_path, block))


def test_the_enumerated_leg_fires_on_a_verdict_outside_the_three(tmp_path: Path) -> None:
    """DEFECT: a free-text verdict ('probably fine') that no reader can aggregate."""
    block = _mutate()
    block["checked_for_supersession"]["found"] = "probably fine"
    assert "ENUMERATED" in _legs(_write(tmp_path, block))


def test_the_enumerated_leg_fires_on_an_unknown_token_kind(tmp_path: Path) -> None:
    """DEFECT: a version-token kind outside the five, so the HONEST legs silently do not apply."""
    assert "ENUMERATED" in _legs(_write(tmp_path, _mutate(version_token_is="vibes")))


def test_the_actioned_leg_fires_when_a_supersession_opens_nothing(tmp_path: Path) -> None:
    """DEFECT: THE CM LEVY FAILURE ITSELF -- the staleness is known, recorded, and acted on by nobody.

    The artefact's honest caveat said the row was half-year only. It was true, it was recorded, and
    the number was still wrong in both lanes for weeks.
    """
    block = _mutate()
    block["checked_for_supersession"]["found"] = "superseded"
    assert "ACTIONED" in _legs(_write(tmp_path, block))


def test_the_actioned_leg_fires_when_the_named_finding_is_not_in_the_tree(
    tmp_path: Path,
) -> None:
    """DEFECT: a finding named but never filed, or filed and later archived out from under it."""
    block = _mutate()
    block["checked_for_supersession"].update(
        {"found": "superseded", "open_finding": "docs/staging/NEVER_WRITTEN.md"}
    )
    assert "ACTIONED" in _legs(_write(tmp_path, block))


# --------------------------------------------------------------------------------------
# OWNED -- `cannot_tell` carries the same obligation as `superseded`
# --------------------------------------------------------------------------------------


def test_the_owned_leg_fires_when_a_cannot_tell_opens_nothing(tmp_path: Path) -> None:
    """DEFECT: THE DEFECT THAT COST TWELVE OFGEM EDITIONS -- an unanswerable recipe, owned by nobody.

    `ofgem_cap_unit_rate_composition`'s `how_to_recheck` sent the reader to a page that has never
    linked the cap level model. The recipe terminated in `cannot_tell` every time it was run, and
    would have forever, while reading exactly like a question that had been asked and answered.
    """
    block = _mutate()
    block["checked_for_supersession"]["found"] = "cannot_tell"
    assert "OWNED" in _legs(_write(tmp_path, block))


def test_the_owned_leg_fires_when_the_named_finding_is_not_in_the_tree(tmp_path: Path) -> None:
    """DEFECT: a `cannot_tell` discharged by naming a finding nobody filed, or one since archived."""
    block = _mutate()
    block["checked_for_supersession"].update(
        {"found": "cannot_tell", "open_finding": "docs/staging/NEVER_WRITTEN.md"}
    )
    assert "OWNED" in _legs(_write(tmp_path, block))


@pytest.mark.parametrize(("commit", "artefact"), EVERY_COMMITTED_CANNOT_TELL)
def test_the_owned_leg_refuses_every_cannot_tell_this_commons_ever_committed(
    tmp_path: Path, commit: str, artefact: str
) -> None:
    """THE REACHABILITY EVIDENCE, from the real bytes, out of the commits that carried them.

    At HEAD nothing is `cannot_tell`, so the live pass is green and proves nothing about this leg --
    a control green on an empty subject is not a control. These are the four real blocks.

    OWNED must be the SOLE refusal on each. If a fixture were also refused by ASKABLE or COHERENT,
    a passing test would not tell us which leg did the work, and this leg could be broken while the
    test stayed green on the collateral.
    """
    raw = subprocess.run(
        ["git", "show", f"{commit}:docs/domain_artefact_library/regulatory/{artefact}.json"],
        capture_output=True, text=True, check=True, cwd=REPO,
    ).stdout
    block = json.loads(raw)["source_check"]

    recorded = block["checked_for_supersession"]
    assert recorded["found"] == "cannot_tell", (
        f"{artefact} at {commit} no longer records `cannot_tell`; this fixture is spent and the "
        "test proves nothing until it is re-pointed at bytes that still carry the defect"
    )
    assert "open_finding" not in recorded, (
        "the pre-repair block already names an owner, so it is not the defect this leg catches"
    )

    assert _legs(_write(tmp_path, block, name=artefact)) == ["OWNED"]


def test_a_reason_shaped_leg_would_have_passed_every_one_of_them(tmp_path: Path) -> None:
    """DEFECT THIS LEG WAS DESIGNED AROUND: keying the obligation to a REASON instead of an ACT.

    The obvious leg -- "a `cannot_tell` must say WHY" -- is satisfied by every instance it exists
    to refuse. All four blocks carried articulate prose and two asserted their own honesty in it
    ("An honest cannot_tell, with the missing thing named"; "recorded rather than a guess"). They
    WERE honest; honesty was never the missing thing. A stuck block can always supply another
    sentence, so the leg demands a filed finding instead -- something only an act can produce.

    This test fails if a future session weakens OWNED back to a prose check: the notes are still
    there, so the weaker leg would go green on all four and this assertion is what says so.
    """
    for commit, artefact in EVERY_COMMITTED_CANNOT_TELL:
        raw = subprocess.run(
            ["git", "show", f"{commit}:docs/domain_artefact_library/regulatory/{artefact}.json"],
            capture_output=True, text=True, check=True, cwd=REPO,
        ).stdout
        note = json.loads(raw)["source_check"]["checked_for_supersession"].get("note", "")
        assert isinstance(note, str) and len(note.strip()) > 80, (
            f"{artefact} at {commit} carries no substantial note, so a reason-shaped leg WOULD have "
            "caught it and this module's stated design reason is wrong"
        )


@pytest.mark.parametrize("verdict", sorted(UNRESOLVED_VERDICTS))
@pytest.mark.parametrize("empty", ["", "   ", "\n"])
def test_a_blank_open_finding_does_not_discharge_the_obligation(
    tmp_path: Path, verdict: str, empty: str
) -> None:
    """DEFECT: FAIL-OPEN -- `open_finding: ""` joins to the REPO ROOT, which exists, so it passes.

    Found by mutation on 2026-09-08: dropping the `.strip()` from the emptiness test left all 39
    tests green. The existence check cannot catch it, because `REPO / ""` IS `REPO` and a directory
    that exists reads as a finding that was filed. A whitespace path is the cheapest possible way to
    silence either leg, and it would look like an author who meant to fill the field in later.

    Parametrised over BOTH unresolved verdicts: the two legs share one implementation, and this hole
    was in `ACTIONED` from the day it was written.
    """
    block = _mutate()
    block["checked_for_supersession"].update({"found": verdict, "open_finding": empty})
    leg = UNRESOLVED_VERDICTS[verdict][0]
    assert _legs(_write(tmp_path, block)) == [leg]


def test_only_the_unresolved_verdicts_owe_a_finding(tmp_path: Path) -> None:
    """DEFECT: the obligation lands on the wrong partition -- on `current`, or on neither.

    One control over the WHOLE partition rather than a leg per verdict: a rule that demanded a
    finding from everything, or from nothing, would pass a per-verdict test written either way.
    """
    owing, free = {}, {}
    for verdict in VERDICTS:
        block = _mutate()
        block["checked_for_supersession"]["found"] = verdict
        (owing if _legs(_write(tmp_path, block, name=verdict)) else free)[verdict] = True

    assert set(owing) == set(UNRESOLVED_VERDICTS) == {"superseded", "cannot_tell"}
    assert set(free) == {"current"}, (
        "`current` is the only verdict that settles anything, so it is the only one that owes "
        "nothing; every other verdict leaves a debt somebody must hold"
    )


def test_the_honest_leg_fires_when_the_cited_version_is_not_the_one_in_its_own_url(
    tmp_path: Path,
) -> None:
    """DEFECT: THE DRIFT THAT COST 4.0% -- 'v1.8' in prose beside a record that had moved to v1.11.

    The mutation asserts the token was genuinely in the URL first, so a survival cannot be a patch
    that never applied.
    """
    assert VALID["version_token"] in VALID["url"]
    legs = _legs(_write(tmp_path, _mutate(version_token="v1.8")))
    assert "HONEST" in legs


def test_the_honest_leg_fires_when_a_version_is_claimed_where_none_is_published(
    tmp_path: Path,
) -> None:
    """DEFECT: a rolling page dressed up as a versioned one, so a check reads as decisive."""
    assert "HONEST" in _legs(_write(tmp_path, _mutate(version_token_is="none_published")))


def test_the_honest_leg_fires_when_a_landing_page_source_names_no_edition(
    tmp_path: Path,
) -> None:
    """DEFECT: the `in_filename_only` shape with nothing to compare -- the most dangerous of the five.

    A versioned workbook behind a landing-page URL: the URL keeps resolving and serves a newer
    edition. A dead link announces itself; this does not.
    """
    block = _mutate(version_token_is="in_filename_only", version_token=None)
    assert "HONEST" in _legs(_write(tmp_path, block))


def test_the_recheckable_leg_fires_when_no_recipe_is_given(tmp_path: Path) -> None:
    """DEFECT: the next session re-derives how to put the question, which is the cost this removes.

    The five sources need five different recipes -- a filename token, a CKAN `metadata_modified`, a
    gov.uk `public_updated_at`, a rolling table, a third-party page with no edition at all.
    """
    assert "RECHECKABLE" in _legs(_write(tmp_path, _mutate(how_to_recheck="   ")))


# --------------------------------------------------------------------------------------
# The valid fixture must PASS, or every leg above proves nothing
# --------------------------------------------------------------------------------------


def test_the_valid_fixture_is_accepted(tmp_path: Path) -> None:
    """DEFECT: the checker refuses everything, and every poison round above passes vacuously.

    This is the control over the whole partition: a checker that refused all input would satisfy
    every single refusal test in this file.
    """
    assert check_artefact(_write(tmp_path, copy.deepcopy(VALID)), TODAY) == []


@pytest.mark.parametrize("kind", TOKEN_KINDS)
def test_every_declared_token_kind_has_a_valid_form_that_passes(
    tmp_path: Path, kind: str
) -> None:
    """DEFECT: a token kind that can be declared but never satisfied, so it is unusable in practice.

    A kind nobody can pass would push authors onto a wrong-but-passable kind, which is worse than
    having no kind at all.
    """
    token = None if kind == "none_published" else VALID["version_token"]
    block = _mutate(version_token_is=kind, version_token=token)
    assert check_artefact(_write(tmp_path, block), TODAY) == []


@pytest.mark.parametrize("verdict", VERDICTS)
def test_every_verdict_can_be_recorded(tmp_path: Path, verdict: str) -> None:
    """DEFECT: a verdict the schema names but refuses, so `cannot_tell` gets recorded as `current`.

    'We cannot tell' is a result and must be as easy to record as the flattering one -- otherwise
    the honest verdict is the expensive one and nobody files it.
    """
    block = _mutate()
    block["checked_for_supersession"]["found"] = verdict
    if verdict in UNRESOLVED_VERDICTS:
        block["checked_for_supersession"]["open_finding"] = A_FILED_FINDING
    assert check_artefact(_write(tmp_path, block), TODAY) == []


# --------------------------------------------------------------------------------------
# Age is reported, never refused
# --------------------------------------------------------------------------------------


def test_age_is_reported_and_never_refused() -> None:
    """DEFECT: age becomes a refusal, goes red for a reason nobody can act on, and gets turned off.

    `tools/startup_anchor_freshness.py` learned this the expensive way. A very old check must
    still PASS `check()` while being visible in `report()` -- otherwise the control wedges every
    lane on a calendar and the fix is to delete the control.
    """
    ancient = date(2030, 1, 1)  # every check in the tree is years stale at this clock
    assert check(today=ancient) == [], "age must not be refusable"
    rows = report(today=ancient)
    assert rows and all(r["age_days"] is not None and r["age_days"] > 365 for r in rows)


def test_the_report_puts_the_never_checked_first() -> None:
    """DEFECT: an unchecked artefact sorts as freshest and drops off the bottom of the due list.

    `None` age is the oldest thing there is, not the newest.
    """
    rows = report(today=TODAY)
    ages = [r["age_days"] for r in rows]
    assert ages == sorted(ages, key=lambda a: (a is None, -(a or 0)))
