"""The promote-by-copy claim census: what it catches, and the half it provably cannot.

The defect class: a promote-by-copy moves BYTES onto a canonical path, so no constant, import or
source line changes while a page's meaning can invert. Every control in this tree keyed to a
constant is blind to it by construction -- that is why `77d92e0d1`'s three instances all passed
"does the constant point at the right file".

These tests exist to stop the census being believed for more than it does. The most important one
is `test_the_narrowing_catches_only_one_of_the_three_named_instances`, which PINS A KNOWN
BLINDNESS: a narrowing added to kill a false positive is asymmetric and can only hide, so its cost
is measured against the NAMED instances out of `77d92e0d1^` rather than against a count.
"""

from __future__ import annotations

import subprocess

import pytest

from tools import promoted_artefact_claim_census as census_mod

PRE_REPAIR = "77d92e0d1^:tools/generate_value_arms_data.py"


@pytest.fixture(scope="module")
def pre_repair_source() -> str:
    """The producer as it stood BEFORE `77d92e0d1` repaired its three instances."""
    out = subprocess.run(["git", "show", PRE_REPAIR], capture_output=True, text=True)
    if out.returncode != 0:
        pytest.skip(f"{PRE_REPAIR} is unreachable from this extract")
    return out.stdout


def test_targets_are_discovered_from_the_tree_and_not_a_list_of_filenames():
    """A target is a canonical path WITH a dated sibling -- the signature of the convention.

    Keyed to the property so a fifth promote target is picked up for free and a retired one stops
    being asked about. A census naming two filenames would be keyed to today's answer, which is
    the failure this project has repeatedly paid for.
    """
    targets = census_mod.promote_targets()
    names = {t["canonical"] for t in targets}
    assert "docs/observability/value_cycle_ab_s1_three_arm.json" in names
    assert "docs/observability/value_cycle_ab_s1_noise_floor.json" in names
    # Every target must be able to SHOW its dated siblings; that evidence is what makes it one.
    assert all(t["dated_siblings"] for t in targets)
    # And a dated artefact with no canonical twin is NOT in the class: nothing is copied onto it.
    assert not any(census_mod._STAMPED_NAME.match(t["name"]) for t in targets)


def test_the_census_catches_a_docstring_naming_a_promoted_path_as_a_guards_sole_witness(
        pre_repair_source):
    """Instance 3 of `77d92e0d1`, replayed. Reachability, not intent.

    `_current_world_bound`'s docstring named `value_cycle_ab_s1_noise_floor.json` as the sole
    witness satisfying one guard leg while failing another. That path IS the promotion target, so
    it gained a world digest and stopped having the property -- with no source edit at all.
    """
    rows = census_mod.census(
        sources={"tools/generate_value_arms_data.py": pre_repair_source})
    witness = [r for r in rows["ordering_only"]
               if "sole witness" in " ".join(r["ordering"]).lower()
               and r["target"].endswith("value_cycle_ab_s1_noise_floor.json")
               and "noise_floor.json`" in r["text"]]
    assert witness, (
        "the census no longer catches the pre-repair docstring that names the promotion target "
        "as a guard's sole witness -- the one named instance it is proven against")


def test_the_narrowing_catches_only_one_of_the_three_named_instances(pre_repair_source):
    """THE COST OF THE NARROWING, PINNED SO IT CANNOT BE FORGOTTEN.

    Unnarrowed, the census reported 406 stale claims across 27 modules -- every `# measured
    2026-08-19` in any file that also reads a run output. Requiring one SENTENCE to carry both a
    reference to the target and a run-identity claim took that to 3, and that narrowing is what
    makes the tool usable.

    It also makes it blind to two of the three instances it was built from, FOR A STRUCTURAL
    REASON RATHER THAN A TUNING ONE. Both missed instances were sentences that reached the reader:
    "It is a LARGER advantage than the GBP 17,453 below" and "published beside the 2026-08-31
    run". A reader-facing sentence never names a file path -- that is what makes it reader-facing
    -- so no narrowing or widening over module text can pair it with a promote target. The pairing
    is not in the text.

    This test asserts the blindness rather than papering over it. If someone later makes the
    published half reachable, this test SHOULD fail, and the right response is to raise the number
    here -- not to quietly widen a regex until a fixture agrees, which is a fixture fitted to its
    conclusion.
    """
    rows = census_mod.census(
        sources={"tools/generate_value_arms_data.py": pre_repair_source})
    caught = rows["stale"] + rows["ordering_only"]
    # The published ordering claim carries no reference to the artefact at all.
    assert not [r for r in caught if "LARGER advantage" in r["text"]
                or "SMALLER advantage" in r["text"]]
    # Nor does the `how_to_read_this` date literal.
    assert not [r for r in caught if "rather than instead of it" in r["text"]]
    assert any("sole witness" in " ".join(r["ordering"]).lower()
               for r in rows["ordering_only"]), "the one instance in reach must stay in reach"


def test_a_bare_clock_citation_can_match_the_stamp_an_artefact_actually_writes():
    """The clock leg matched prose and never payloads, so every bare-clock citation was stale.

    An artefact writes `2026-09-08T21:01:30Z`; prose cites "the 21:01:30Z run". The `\\b` before
    the clock alternative cannot fire inside the full stamp -- the preceding `T` is a word
    character -- and the ISO alternative consumes the whole stamp first regardless. Found by a
    false STALE on a claim that was true, which is the direction that gets noticed; the same bug
    pointed the other way would have been silent.
    """
    forms = census_mod._normalise("2026-09-08T21:01:30Z")
    assert "2026-09-08T21:01:30Z" in forms
    # The repair lives in `_artefact_dates`, which emits the clock sub-token of every full stamp.
    import json
    import tempfile
    from pathlib import Path
    with tempfile.TemporaryDirectory() as d:
        p = Path(d) / "a.json"
        p.write_text(json.dumps({"generated_at": "2026-09-08T21:01:30Z"}))
        tokens = census_mod._artefact_dates(p)
    assert "21:01:30Z" in tokens, "a bare-clock citation can never be matched against a payload"
    assert "2026-09-08T21:01:30Z" in tokens


def test_a_stale_claim_is_caught_and_a_true_one_is_not(tmp_path):
    """The poison round: the refusing leg can fire, and does not fire on a correct sentence.

    Built as ONE control over the whole partition rather than a leg per branch, because a detector
    that flags EVERYTHING passes every "does it refuse correctly" test on its own.
    """
    import json
    obs = tmp_path / "docs" / "observability"
    obs.mkdir(parents=True)
    (obs / "thing_20260908.json").write_text(json.dumps({"generated_at": "2026-09-08T04:00:00Z"}))
    (obs / "thing.json").write_text(json.dumps({"generated_at": "2026-09-08T04:00:00Z"}))
    tools = tmp_path / "tools"
    tools.mkdir()

    def run(body: str) -> list[dict]:
        return census_mod.census(root=tmp_path,
                                 sources={"tools/m.py": body})["stale"]

    # A claim naming the run actually there: not stale.
    assert not run('"""`thing.json` carries the 2026-09-08 run."""\nX = "thing.json"\n')
    # The same sentence naming a run that is NOT there: stale.
    poisoned = run('"""`thing.json` carries the 2026-08-31 run."""\nX = "thing.json"\n')
    assert poisoned and poisoned[0]["token"] == "2026-08-31"
    # A date with no reference to the artefact in its sentence: correctly out of scope.
    assert not run('"""Measured 2026-08-31.\n\nSeparately, `thing.json` is read."""\n'
                   'X = "thing.json"\n')


def test_grading_reads_run_identity_metadata_and_not_the_whole_payload(tmp_path):
    """The repair for a leg that was useless without ever looking fail-open.

    `run_output_latest.json` graded against its raw text yielded 28,676 distinct run-identity
    tokens -- every customer's acquisition date -- so every claim about it was "supported" and the
    leg could not fail. Reading shallow metadata only takes it to 17. This asserts the SHAPE (data
    inside collections is excluded, metadata is not), not today's counts, so it stays true as the
    artefacts move.
    """
    import json
    p = tmp_path / "a.json"
    p.write_text(json.dumps({
        "generated_at": "2026-09-09T01:24:34Z",
        "rows": [{"acquisition_date": "2016-01-01"} for _ in range(50)],
        "per_customer": {f"C{i}": {"inner": {"date": "2019-04-01"}} for i in range(50)},
    }))
    tokens = census_mod._artefact_dates(p)
    assert "2026-09-09" in tokens, "run identity must be read"
    assert "2016-01-01" not in tokens, "a date inside a list is DATA, not which run this is"
    assert "2019-04-01" not in tokens, "nor is one buried in a per-entity collection"


def test_a_target_publishing_no_run_identity_is_reported_as_we_cannot_tell(tmp_path):
    """THE RARE BRANCH, ASSERTED REACHABLE BEFORE ANYTHING ASSERTS WHAT IT DOES.

    No promote target in the tree is currently ungradable, so this branch does not fire in
    production. An unfired branch is either a missing test or an equivalence, and leaving the
    reader to guess which is how a guard that refuses everything passes every test of it.
    """
    import json
    obs = tmp_path / "docs" / "observability"
    obs.mkdir(parents=True)
    # A target with dated siblings but NO run identity of its own.
    (obs / "mute_20260908.json").write_text(json.dumps({"rows": [1, 2, 3]}))
    (obs / "mute.json").write_text(json.dumps({"rows": [1, 2, 3]}))
    result = census_mod.census(
        root=tmp_path,
        sources={"tools/m.py": '"""`mute.json` carries the 2026-08-31 run."""\nX = "mute.json"\n'})
    assert result["ungradable_targets"] == ["mute.json"]
    assert len(result["cannot_tell"]) == 1
    # And the unanswerable question must NOT be laundered into a defect or into a pass.
    assert not result["stale"]


def test_the_feed_leg_fails_open_and_the_module_says_so():
    """A control that cannot separate its populations must name that on its surface.

    `feed_claims` cannot tell a dated historical record (`withdrawn_on`, `history[].on` -- a wrong
    claim kept beside the result, which this project requires) from a claim about the current run.
    So it reports and never refuses, and `--check` must not consult it. A gate that reds on
    correct prose trains its readers to bypass it.
    """
    doc = census_mod.feed_claims.__doc__ or ""
    assert "fails open" in doc.lower()
    assert "REPORTS AND DOES NOT REFUSE" in doc
    src = (census_mod.__file__)
    with open(src, encoding="utf-8") as fh:
        text = fh.read()
    assert 'if args.check and result["stale"]:' in text, (
        "--check must refuse on the source leg ONLY; consulting the feed leg would make a "
        "fail-open measure into a gate that reds on legitimate dated records")
