"""Published provenance must name a commit or admit it cannot (cold-eyes Expert Hour, 2026-07-29).

THE DEFECT THIS CLASS-CLOSES (R10 -- an absurdity-class defect may not be closed
with an instance fix): every published door carried ``git_commit: "latest"``. It
came from a fallback that parsed the RUN FILENAME -- ``run_output_latest.json``
-> ``stem.split("_")[2]`` -> ``"latest"`` -- so the audit chain the site promises
("every claim links to its evidence") began at a provenance stamp that named
nothing. It is the textbook FAIL-OPEN: it satisfies any presence check forever
and can never contradict a claim, which is exactly why nine days of dashboards
shipped with it and no control noticed.

The gate is therefore NOT "git_commit is non-empty" -- that is the very check the
defect passed. It is a SHAPE gate: a published provenance value is either a real
40-hex git SHA, or the honest literal "unknown". Anything else -- a filename
fragment, a branch name, a tag, "latest", "HEAD" -- is a fake dressed as a SHA
and fails. A non-empty string is not a referent.

R15: each guard below names the defect it fires on, and the mutation tests prove
it FIRES on that defect rather than passing everything handed to it.
"""
from __future__ import annotations

import re

import pytest

# A published provenance value is one of exactly two honest things.
_SHA_RE = re.compile(r"^[0-9a-f]{40}$")
_HONEST_UNKNOWN = "unknown"


def is_honest_provenance(value) -> bool:
    """The gate. Pure function of its argument -- it never reads the repo to
    decide (INDEPENDENCE: a gate that re-derived the answer from the same source
    it checks would be a tautology, per this project's own R15 doctrine)."""
    if not isinstance(value, str):
        return False
    if value == _HONEST_UNKNOWN:
        return True
    return bool(_SHA_RE.match(value))


class TestTheGateItself:
    def test_a_real_sha_is_honest(self):
        assert is_honest_provenance("4d1e899d18cb1c64dd79eb593bd5d848e7f1955a")

    def test_the_literal_unknown_is_honest(self):
        """Admitting ignorance is a PASS. The point of the gate is to make
        "unknown" the cheap option so inventing a stamp is never tempting."""
        assert is_honest_provenance(_HONEST_UNKNOWN)

    @pytest.mark.parametrize(
        "fake",
        [
            "latest",          # THE observed defect: run_output_latest.json filename fragment
            "main",            # a branch is not a commit
            "HEAD",            # a symbolic ref is not a commit
            "v1.2.3",          # a tag is not a commit
            "output",          # another filename fragment from the same split()
            "4d1e899",         # abbreviated -- ambiguous, not the full referent
            "4D1E899D18CB1C64DD79EB593BD5D848E7F1955A",  # uppercase: not git's own form
            "zzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz",  # 40 chars, not hex
        ],
    )
    def test_r15_mutation_a_plausible_looking_fake_FIRES_the_gate(self, fake):
        """MUTATION: hand the gate the exact class of value that shipped for nine
        days. If any of these passes, the gate is theatre."""
        assert not is_honest_provenance(fake), (
            f"{fake!r} passed the provenance gate -- this is the fail-open that "
            "published 'latest' as a commit stamp"
        )

    @pytest.mark.parametrize("empty", [None, "", "   ", 0, False, [], {}])
    def test_r15_fail_open_missing_or_empty_provenance_is_a_FAILED_check(self, empty):
        """FAIL-OPEN: absent/empty/malformed provenance must be a FAILED check,
        never a silent pass. A missing stamp is strictly worse than "unknown"
        because nothing on the page admits it is missing."""
        assert not is_honest_provenance(empty)


class TestTheGeneratorHonoursIt:
    def test_git_head_returns_a_real_sha_or_none_never_a_guess(self):
        """_git_head must return a verifiable SHA or None. Returning None is what
        lets the caller publish "unknown"; returning a guess is what caused the
        defect."""
        from tools.generate_dashboard_data import _git_head

        head = _git_head()
        if head is None:
            pytest.skip("git unavailable in this environment -- None is the correct answer")
        assert is_honest_provenance(head), f"_git_head returned a non-SHA: {head!r}"

    def test_the_old_filename_fallback_is_gone(self):
        """REGRESSION, pinned to the mechanism not the symptom: the generator must
        no longer derive provenance from the run filename. Re-introducing
        `run_json_path.stem.split("_")` for git_commit revives the whole class."""
        from pathlib import Path

        src = Path("tools/generate_dashboard_data.py").read_text()
        # Find the git_commit assignment and assert it does not read the filename.
        assign = [ln for ln in src.splitlines() if ln.strip().startswith("git_commit = ")]
        assert assign, "git_commit assignment not found -- did the generator change shape?"
        for ln in assign:
            assert "run_json_path" not in ln, (
                "git_commit is being derived from the run filename again: " + ln.strip()
            )
            assert "stem" not in ln, (
                "git_commit is being derived from a filename stem again: " + ln.strip()
            )


class TestBridgeEvidencePathResolves:
    def test_bridge_url_resolves_from_a_door_page_not_from_the_site_root(self):
        """Door pages live one level down (/company/, /proof/), so an evidence
        path must be ../data/... -- "./data/..." resolved to
        /company/data/margin_bridge.json -> 404 on the live site. Pinned because
        the field currently has no site/ consumer: the next surface to read it
        would silently ship a dead evidence link, and 'no consumer yet' is
        exactly why it went unnoticed."""
        from pathlib import Path

        src = Path("tools/generate_dashboard_data.py").read_text()
        assert '"bridge_url": "../data/margin_bridge.json"' in src, (
            "bridge_url must resolve from a door page (../data/), not from the site root"
        )
        assert '"bridge_url": "./data/margin_bridge.json"' not in src, (
            "the ./data/ bridge_url regressed -- it 404s when resolved from /company/"
        )
