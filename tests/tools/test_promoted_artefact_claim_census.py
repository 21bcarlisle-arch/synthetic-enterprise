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
        p.write_text(json.dumps({"generated_at": "2026-09-08T21:01:30Z",
                                 "run_identity_fields": ["generated_at"]}))
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
    stamped = {"generated_at": "2026-09-08T04:00:00Z",
               "run_identity_fields": ["generated_at"]}
    (obs / "thing_20260908.json").write_text(json.dumps(stamped))
    (obs / "thing.json").write_text(json.dumps(stamped))
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


def test_grading_reads_only_what_the_producer_declared_as_run_identity(tmp_path):
    """The defect this replaced, and it is a SECOND repair on the same leg -- not a re-tune.

    The first repair read shallow metadata only, on the theory that run identity is shallow and
    data is deep. Its own docstring recorded `run_output_latest.json` going "to none". Measured
    again on 2026-09-09 it was SEVENTEEN, and every one of the seventeen was a date inside the
    simulated world or another producer's stamp folded in whole -- `mark_date`, `stressed_date`,
    `clv_snapshot_as_of`. Shallowness is not the property, because `portfolio_as_of` (a real
    run stamp) and `wholesale_credit_exposure.mark_date` (a date in 2025 the company lived
    through) are the same English at the same depth.

    So the fixture below is the shape that defeats every consumer-side rule: a real run stamp and
    a simulation-world date, BOTH shallow, BOTH named like a clock. Only the producer's own
    declaration separates them, and this asserts that separation rather than today's counts.
    """
    import json
    p = tmp_path / "a.json"
    p.write_text(json.dumps({
        "generated_at": "2026-09-09T01:24:34Z",
        "run_identity_fields": ["generated_at", "world_identity.digest"],
        # Shallow, scalar, and NOT this run -- the case the depth rule could never exclude.
        "mark_date": "2025-06-07",
        "world_identity": {"digest": "39a192ce04c1eda8", "anchors": {"2016": "2016-12-31"}},
        "rows": [{"acquisition_date": "2016-01-01"} for _ in range(50)],
    }))
    tokens = census_mod._artefact_dates(p)
    assert "2026-09-09" in tokens, "a declared run stamp must be read"
    assert "39a192ce04c1eda8" in tokens, "a declared nested leaf must be read"
    assert "2025-06-07" not in tokens, (
        "an UNDECLARED shallow scalar is a date in the world, and grading a run claim against it "
        "is the fail-open this repair exists to close")
    assert "2016-12-31" not in tokens, (
        "declaring `world_identity.digest` must not drag in the block's world anchors")
    assert "2016-01-01" not in tokens


def test_an_artefact_that_declares_nothing_grades_nothing(tmp_path):
    """The fail-closed direction, asserted over the whole partition of malformed declarations.

    A missing key, an empty list, a list of non-strings and a non-list all mean one thing: this
    artefact does not say which of its fields identify it, so nothing about which run sits here
    can be checked. The alternative -- falling back to the old walk when the declaration is
    absent -- would be a fail-open that never gets closed, because nothing would ever go red to
    say a producer had not adopted the convention.
    """
    import json
    stamp = {"generated_at": "2026-09-09T01:24:34Z"}
    for undeclared in ({}, {"run_identity_fields": []}, {"run_identity_fields": [1, 2]},
                       {"run_identity_fields": "generated_at"}, {"run_identity_fields": None}):
        p = tmp_path / "a.json"
        p.write_text(json.dumps({**stamp, **undeclared}))
        assert census_mod._artefact_dates(p) == set(), undeclared
        assert census_mod.declared_run_identity_fields({**stamp, **undeclared}) is None
    # And a declaration naming a path that does not resolve contributes nothing rather than
    # falling back to a guess.
    p = tmp_path / "a.json"
    p.write_text(json.dumps({**stamp, "run_identity_fields": ["renamed_at", "generated_at.x"]}))
    assert census_mod._artefact_dates(p) == set()


def test_a_pinned_dated_sibling_is_read_whole_because_it_cannot_be_promoted_onto(tmp_path):
    """The asymmetry, and it is what stops this repair firing as a false red on every old pin.

    A dated sibling is named by the reader and nothing is ever copied onto it, so the question is
    only "is this literal in the file you named" -- no declaration is required or possible for
    artefacts written before the convention existed. Requiring one would turn every pin to a
    2026-09-08 artefact into a STALE row caused by the control changing rather than the tree.
    """
    import json
    obs = tmp_path / "docs" / "observability"
    obs.mkdir(parents=True)
    # The sibling predates the convention: a stamp, no declaration.
    (obs / "thing_20260908.json").write_text(json.dumps({"generated_at": "2026-09-08T21:01:30Z"}))
    (obs / "thing.json").write_text(json.dumps({"generated_at": "2026-09-09T04:00:00Z",
                                                "run_identity_fields": ["generated_at"]}))
    body = ('"""`thing_20260908.json` (21:01:30Z) is the pin `thing.json` was cut from."""\n'
            'X = "thing.json"\nY = "thing_20260908.json"\n')
    result = census_mod.census(root=tmp_path, sources={"tools/m.py": body})
    assert not result["stale"], (
        "a bare clock recoverable only from the pinned sibling's payload must excuse the claim")
    # The same leg still refuses a clock that is in NEITHER file.
    poisoned = census_mod.census(
        root=tmp_path,
        sources={"tools/m.py": body.replace("21:01:30Z", "09:09:09Z")})["stale"]
    assert poisoned and poisoned[0]["token"] == "09:09:09Z"


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


# --- THE RETRACTION CLASS ------------------------------------------------------------------
#
# A past-tense account of a WITHDRAWN wording cannot be falsified by a promote-by-copy: it says
# what the text used to say over an interval that has already closed. The census graded one as a
# live claim and refused the whole tree for it, which put a price on the one habit CLAUDE.md
# requires -- "correct yourself plainly, in the record, beside the claim" -- and made DELETING the
# account of a defect the cheapest way to go green.


def _retraction_tree(tmp_path, current="2026-09-18T05:43:40Z"):
    """A tree with one promote target whose canonical copy carries `current`.

    Named for this block rather than reusing a bare `run`/`tree` helper on purpose: a helper
    appended to a large suite can shadow an existing one and redden controls that have nothing to
    do with the change, and the reds then read as pre-existing.
    """
    import json
    obs = tmp_path / "docs" / "observability"
    obs.mkdir(parents=True, exist_ok=True)
    (obs / "thing_20260908.json").write_text(json.dumps(
        {"generated_at": "2026-09-08T04:00:00Z", "run_identity_fields": ["generated_at"]}))
    (obs / "thing.json").write_text(json.dumps(
        {"generated_at": current, "run_identity_fields": ["generated_at"]}))
    (tmp_path / "tools").mkdir(exist_ok=True)

    def run(body: str) -> dict:
        return census_mod.census(root=tmp_path, sources={"tools/m.py": body})
    return run


def test_every_branch_of_the_retraction_grading_is_reachable_in_one_tree(tmp_path):
    """THE PARTITION CONTROL, and it comes first because the rest are worthless without it.

    A classifier that answered "retraction" to everything would pass every "does it stand down
    correctly" test below, and one that answered "live claim" to everything would pass every "does
    it still refuse" test. Neither could be caught by a leg-per-branch suite. So this asserts that
    ONE tree drives all three outcomes at once -- a live claim that refuses, an accurate retraction
    that stands down, and a false retraction that refuses again -- which is the only shape that
    proves the branches are distinguishable rather than merely present.
    """
    run = _retraction_tree(tmp_path)
    result = run(
        'X = "thing.json"\n'
        '# `thing.json` carries the 2026-08-31 run.\n'
        'A = 1\n'
        '# This sentence read "the 2017-01-01 run" until 2026-09-09 and became false.\n'
        'B = 2\n'
        '# `thing.json` previously said the 2026-09-18 run, and that is no longer so.\n'
        'C = 3\n')
    assert result["stale"], "the live-claim branch is unreachable"
    assert result["retractions"], "the retraction branch is unreachable"
    assert result["false_retractions"], "the false-retraction branch is unreachable"


def test_a_past_tense_account_of_a_withdrawn_wording_is_not_read_as_a_live_claim(tmp_path):
    """The defect: the census refused the tree for a comment RECORDING A CORRECTION.

    `tools/generate_value_arms_data.py:9882` said its sentence `read "published beside the
    2026-08-31 run" until 2026-09-09` and had been repaired -- the live expression beside it is a
    `{when}` placeholder resolved from the payload. The code was right and the census was wrong,
    and the cheap way to clear the red was to delete the account of the defect.
    """
    run = _retraction_tree(tmp_path)
    result = run('X = "thing.json"\n'
                 '# `thing.json` read "the 2026-08-31 run" until 2026-09-09, and that became\n'
                 '# false when the newer run was promoted onto the canonical name.\n')
    assert not result["stale"], "a recorded correction still refuses the tree"
    assert [r for r in result["retractions"] if r["token"] == "2026-08-31"]


def test_a_retraction_that_is_not_yet_true_refuses(tmp_path):
    """The leg that stops the class being an escape hatch, and the reason it can fail.

    A retraction ASSERTS that a wording stopped standing. This census already knows whether it
    did. So the claim is graded, not excused: if the run at the path still answers to the literal
    being retracted, the correction is a second wrong claim stacked on the first.
    """
    run = _retraction_tree(tmp_path, current="2026-09-18T05:43:40Z")
    result = run('X = "thing.json"\n'
                 '# `thing.json` previously said the 2026-09-18 run, and that is no longer so.\n')
    assert result["false_retractions"], (
        "a retraction of a literal that still matches the run at the path must refuse -- "
        "otherwise `previously` is a password that turns any stale claim green")
    assert not result["stale"], "it belongs in its own class, not silently among the stale"


def test_the_date_a_retraction_closes_at_is_not_graded_as_a_claim_about_the_run(tmp_path):
    """`until 2026-09-18` names WHEN the wording ended. It is not a claim that a run sits anywhere.

    Grading it as one would red a correct retraction for the accident of being written on the day
    of the promotion it records -- the control keyed to today's answer from the far end, which is
    exactly the shape this project keeps paying for.
    """
    run = _retraction_tree(tmp_path, current="2026-09-18T05:43:40Z")
    result = run('X = "thing.json"\n'
                 '# `thing.json` read "the 2017-01-01 run" until 2026-09-18, when it went false.\n')
    assert not result["false_retractions"], (
        "the closure date was graded as if it asserted which run sits at the path")
    assert not result["stale"]
    closing = [r for r in result["retractions"] if r["token"] == "2026-09-18"]
    assert closing and closing[0]["is_closure"]


def test_half_a_retraction_buys_no_silence(tmp_path):
    """BOTH halves or none, and this is the control that keeps the predicate from being a password.

    `read`/`said`/`previously` appear in every other line about an artefact; `until` appears in
    every deferral. Either alone would let a stale claim go quiet by accident of wording. A writer
    has to say what it read AND when that stopped -- which is the attribution the control exists to
    protect, so the cost of standing it down is paying the thing it wants.
    """
    run = _retraction_tree(tmp_path)
    verb_only = run('X = "thing.json"\n'
                    '# `thing.json` previously carried the 2026-08-31 run.\n')
    assert verb_only["stale"] and not verb_only["retractions"], (
        "a saying-verb with no stated ending stood the census down")
    closure_only = run('X = "thing.json"\n'
                       '# `thing.json` holds the 2026-08-31 run until 2026-09-09.\n')
    assert closure_only["stale"] and not closure_only["retractions"], (
        "a bare `until` stood the census down")


def test_a_dated_measurement_is_still_a_live_claim(tmp_path):
    """The population `feed_claims` provably cannot separate, and which this leg must not blur.

    A record of what was measured on a date and a claim about which run is at a path look identical
    from the date alone -- that is why the feed leg fails open. The retraction predicate does not
    rest on a date: it needs a report of a former WORDING plus a stated ending. So a sentence that
    merely carries a measurement date stays gradable, and this is the control that says so.
    """
    run = _retraction_tree(tmp_path)
    result = run('X = "thing.json"\n'
                 '# Measured 2026-09-17: the folded family is stamped against `thing.json`\n'
                 "# at 2026-08-31, so the staleness caveat is satisfied rather than bypassed.\n")
    assert result["stale"], "a dated measurement was mistaken for a retraction"
    assert not result["retractions"]


# --- THE CLAIM UNIT ------------------------------------------------------------------------


def test_a_wrapped_comment_is_one_claim_because_the_line_break_is_the_rulers_not_the_writers(
        tmp_path):
    """THE WIDENING, and the evidence that the retraction class was not bought with blindness.

    `tokenize` hands back one row per `#` line, so `_CLAIM_NEEDS_BOTH_HALVES` was asked of a unit
    the writer never chose: the reference to the target landed on one line and the run-identity
    token on the next, and the census saw neither half beside the other. Measured on this tree on
    2026-09-18, joining the block first took the row count 16 -> 23 and raised THREE stale claims
    that had been invisible, one of them live and current
    (`generate_value_arms_data.py:230`, `the arms' 2026-09-10T14:04:08Z` against an artefact
    stamped 2026-09-18). A change that only ever hides cannot do that.
    """
    run = _retraction_tree(tmp_path)
    wrapped = run('X = "thing.json"\n'
                  '# The bound is taken over the run sitting at `thing.json`, which this\n'
                  '# tree promoted on 2026-08-31 and has not re-taken since.\n')
    assert [r for r in wrapped["stale"] if r["token"] == "2026-08-31"], (
        "a claim split across a line wrap is invisible to the census")
    assert wrapped["stale"][0]["line"] == 2, "a row must point at where the prose STARTS"


def test_two_trailing_comments_are_not_joined_into_a_sentence_nobody_wrote(tmp_path):
    """The block boundary, and the false claim the naive version would manufacture.

    `x = 1  # names thing.json` and `y = 2  # the 2026-08-31 run` are two remarks about two
    statements. Running them together would mint a sentence carrying both halves that no writer
    ever put in one breath -- a fabricated claim, which is worse than a missed one because it is
    unfalsifiable at the source.
    """
    run = _retraction_tree(tmp_path)
    result = run('X = "thing.json"  # the bound is taken over `thing.json`\n'
                 'Y = 2  # the 2026-08-31 run is the one that matters\n')
    assert not result["stale"], (
        "two trailing comments were joined into a claim neither of them makes")
