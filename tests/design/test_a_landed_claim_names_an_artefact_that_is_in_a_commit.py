"""A record that says a named artefact LANDED fails while that artefact is in no commit.

THE DEFECT, 2026-09-01. `docs/staging/SEAT_DISPOSITION_THE_PUBLISHED_CUSTOMER_SURFACE_AND_ITS_
MISSING_INPUT_2026-09-01.md` carried a section headed *"What landed"* naming a control file and a
repaired input, and asserted underneath that the control was mutation-proven three ways. Both were
UNTRACKED. `git log --all` returned nothing for either, and the document itself was in no commit
either -- so the record, its evidence and its subject were all on one disk, in a shared tree where
`fork_salvage` had committed into live worktrees twice in ninety minutes that same day. It was not
a lie and nobody had to be careless: the pre-commit gate had refused the commit, which leaves the
prose written and the payload staged, and nothing anywhere reads the difference.

WHY THIS IS THE ONE LEG AND NOT A REGISTER. The tempting shapes are all wider and all worse: a list
of the five files that were untracked that morning (which goes green the moment they land and can
never fire again), a census of untracked files (which is noise -- every lane holds work in progress
and that is the point of a shared tree), or a daemon that watches (which is a control guarding
controls, and this repo has 117 harness atoms as evidence of where that ends). The property is
narrower than any of them and it is the one that was violated: a record makes a claim in the PAST
TENSE about a NAMED artefact, and that claim is checkable against the commits.

FAIL-CLOSED, AND THE DIRECTION MATTERS. A git call that does not answer is a RED, never a skip --
"I could not tell whether the evidence exists" is not compatible with a record that says it does.

GITIGNORED PATHS ARE EXCLUDED, and that is a rule about the claim rather than a hole in it. A path
in `.gitignore` is DECLARED never-to-be-committed, so "in no commit" is its intended state and
naming it cannot be a false landing claim. `docs/observability/ntfy-delivery-log.md` is the live
instance: a 2026-08-12 report names it under "What landed", `background/ntfy_utils.py` writes it at
runtime, and it is ignored on line 13. Without this carve-out the control would have been red on a
record that was telling the truth -- which is the failure mode that gets a control deleted.
"""

import pathlib
import re
import subprocess

PROJECT = pathlib.Path(__file__).resolve().parents[2]
RECORDS = PROJECT / "docs" / "staging"

#: The past-tense claim this control is about. Kept to the heading the records actually use rather
#: than a general "landed" search: a sentence mentioning the word in passing is not an assertion,
#: and a control that cannot tell those apart reports the OR of the two.
#:
#: THE SECTION NUMBER IS OPTIONAL, 2026-09-17, AND ITS ABSENCE WAS A BLIND SPOT OF EXACTLY THIS
#: CONTROL'S OWN DEFECT. `\s*` allows only whitespace between the hashes and the phrase, so the
#: numbered form this project's records actually favour -- `## 8. WHAT LANDED` -- did not match and
#: the whole document went ungraded. 22 of the 128 records in `docs/staging/` head the section that
#: way, and re-asking all 128 under the widened pattern fired on exactly ONE: a 2026-09-16 worker
#: result headed `## 8. WHAT LANDED` that named five files -- `tools/build_weather_world.py`,
#: `tools/validate_weather_world.py`, `sim/weather_world.py` and two test files -- and asserted
#: "The code is landed" while `git log --all` returned nothing for any of them. The other 21 told
#: the truth, so this widening bought one real defect and no noise.
#:
#: THE DIRECTION OF THE CHANGE IS WHY IT IS SAFE. It enlarges the population the control grades;
#: it does not add an exception to it. A narrowing here could only ever hide a claim.
_HEADING = re.compile(r"^(#+)\s*(?:\d+[.)]\s*)?What landed\b.*$", re.IGNORECASE | re.MULTILINE)

#: A repo path in backticks. Requires a directory separator, so bare module names and prose in
#: `code font` do not become artefact claims.
_PATH = re.compile(r"`([A-Za-z0-9_][A-Za-z0-9_./-]*/[A-Za-z0-9_./-]*\.(?:py|json|yaml|yml|html|js|md|sh))`")


def landed_section(text: str) -> str | None:
    """The body under the first `What landed` heading, to the next heading of the same level or
    higher. None when the record makes no such claim -- which is most of them, and is not a defect.
    """
    found = _HEADING.search(text)
    if found is None:
        return None
    rest = text[found.end():]
    nxt = re.search(r"^#{1,%d}\s" % len(found.group(1)), rest, re.MULTILINE)
    return rest[:nxt.start()] if nxt else rest


def artefacts_claimed_landed(text: str) -> list[str]:
    """Every repo path named under this record's `What landed` heading, deduped and sorted."""
    section = landed_section(text)
    return sorted(set(_PATH.findall(section))) if section else []


def _is_ignored(rel: str) -> bool:
    done = subprocess.run(["git", "check-ignore", "-q", "--", rel],
                          cwd=str(PROJECT), capture_output=True, text=True, check=False)
    return done.returncode == 0


def is_in_some_commit(rel: str) -> bool:
    """Has any commit on any ref ever touched `rel`?

    `--all`, not `HEAD`: the claim is "this exists as committed work somewhere", and a path that
    landed on a fork branch is not the defect being hunted. A git call that FAILS is not an
    absence -- it raises, so the test reds rather than certifying an unread tree.
    """
    done = subprocess.run(["git", "log", "--all", "--oneline", "-1", "--", rel],
                          cwd=str(PROJECT), capture_output=True, text=True, check=False)
    if done.returncode != 0:
        raise AssertionError(
            f"`git log --all -- {rel}` failed rc={done.returncode}: {done.stderr.strip()[-300:]}. "
            "Whether the claimed artefact is committed could not be established, which a record "
            "asserting it landed cannot be graded against."
        )
    return bool(done.stdout.strip())


def unlanded_claims(text: str) -> list[str]:
    """The artefacts this record says landed that are in no commit. Empty is the passing answer."""
    return [p for p in artefacts_claimed_landed(text)
            if not _is_ignored(p) and not is_in_some_commit(p)]


def test_no_record_claims_an_artefact_landed_while_it_is_in_no_commit():
    """The enforced leg, over every record in `docs/staging/` including the archive."""
    offenders = {}
    for record in sorted(RECORDS.rglob("*.md")):
        missing = unlanded_claims(record.read_text(errors="replace"))
        if missing:
            offenders[str(record.relative_to(PROJECT))] = missing
    assert not offenders, (
        "A RECORD SAYS AN ARTEFACT LANDED AND IT IS IN NO COMMIT.\n"
        + "\n".join(f"  {rec}\n    " + "\n    ".join(paths) for rec, paths in offenders.items())
        + "\nEither commit the artefact, or correct the claim BESIDE itself rather than deleting "
        "it -- a claim quietly revised is the only kind that leaves no evidence it was made."
    )


def test_MUTATION_a_record_naming_an_uncommitted_artefact_is_caught(tmp_path):
    """The proof this can fail. A path git has never seen must be reported, and a real one not.

    Both directions in one test on purpose: the first assertion alone is satisfied by a checker
    that reports EVERYTHING, which is the fail-loud twin of the fail-open shape and just as useless.
    """
    absent = "docs/staging/a_file_that_was_never_written_2026-09-01.md"
    assert not is_in_some_commit(absent), "fixture invalid: the decoy path is in a commit"

    claimed_absent = f"## What landed\n\n**`{absent}`** -- the control.\n\n## Next\n"
    assert unlanded_claims(claimed_absent) == [absent]

    present = "background/publish_cause.py"
    assert is_in_some_commit(present), "fixture invalid: the control path is in no commit"
    assert unlanded_claims(f"## What landed\n\n**`{present}`** -- the cause.\n\n## Next\n") == []


def test_MUTATION_a_mention_outside_the_landed_section_is_not_a_claim():
    """Scope, proven rather than asserted. A path named anywhere else is not graded.

    Without this the control's subject is every backticked path in every record, which would red on
    documents that name what is OWED -- the opposite claim -- and the first person to hit that would
    correctly delete it.
    """
    absent = "docs/staging/a_file_that_was_never_written_2026-09-01.md"
    assert unlanded_claims(f"## What is owed\n\n`{absent}` -- still to write.\n") == []
    assert unlanded_claims(f"## What landed\n\n`x`\n\n## What is owed\n\n`{absent}`\n") == []


def test_MUTATION_a_NUMBERED_landed_heading_is_graded_like_an_unnumbered_one():
    """R15: the blind spot that let a false claim through for a day, kept as the control on it.

    ASKED OF A SYNTHETIC RECORD AND NOT OF THE LIVE ONE, on purpose. The document that exposed this
    -- a 2026-09-16 worker result headed `## 8. WHAT LANDED` naming five uncommitted files -- is
    discharged by the commit that lands those files, so a control keyed to it would go green
    because the tree got MORE honest and could never fire again. The property is the heading
    grammar, which is permanent; today's offender is not.

    Both directions, because a checker that grades every heading shape by grading none of them
    passes the first assertion alone.
    """
    absent = "docs/staging/a_file_that_was_never_written_2026-09-01.md"
    assert not is_in_some_commit(absent), "fixture invalid: the decoy path is in a commit"

    for heading in ("## 8. WHAT LANDED", "## 3. What landed", "## 1) What landed anyway",
                    "## What landed"):
        claimed = f"{heading}\n\n**`{absent}`** -- the control.\n\n## Next\n"
        assert unlanded_claims(claimed) == [absent], (
            f"{heading!r} was not graded: a numbered section heading is the form this project's "
            "records actually favour, and a control blind to it reads a false landing claim as "
            "no claim at all."
        )

    present = "background/publish_cause.py"
    assert is_in_some_commit(present), "fixture invalid: the control path is in no commit"
    assert unlanded_claims(f"## 8. WHAT LANDED\n\n**`{present}`** -- the cause.\n\n## Next\n") == []
