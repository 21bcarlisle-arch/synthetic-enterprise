"""R15 both-ways proof of the REGISTRATION-HOLE lint
(DIRECTOR_RULING_SWEEP_VERDICT 2026-07-27, section 1: "Close the registration hole").

The lint closes the sweep's own honest gap: `suppression_register.py` enforces the standing
consequence on every *registered* suppression, but *registering* a newly-written one was a
convention. This lint fails the gate when suppression-shaped code in `background/**` is not
accounted for by the register (`code_markers`) or an explicit `not-a-suppression` waiver.

Both ways (R15), plus the director's own stated acceptance criterion:
  * test_live_tree_passes                 -- the real committed tree is clean (no false
                                             positive on legitimate input; the control does
                                             not red the whole tree).
  * test_unregistered_suppression_reds     -- the RULING's criterion verbatim: an unregistered
                                             suppression added in a fixture MUST fail the gate.
  * test_waiver_clears_a_false_positive     -- a reasoned `not-a-suppression` waiver clears a
                                             genuine false positive (the escape the ruling
                                             explicitly permits: "state why it is not").
  * test_waiver_requires_a_reason           -- a waiver with no reason does NOT clear (a bare
                                             silence is not an account).
  * test_dead_code_marker_reds              -- register<->code integrity: a code_marker naming
                                             no live identifier is a dead pointer -> flagged.
  * test_removing_a_marker_re_reds_its_site  -- a `code_markers` token is LOAD-BEARING: drop it
                                             and the site it covered goes un-accounted-for
                                             (proves coverage is real, not theatre).
  * test_untokenisable_file_reds            -- FAIL-CLOSED: an unscannable file is a FAILED
                                             check (R15 fail-silent killer), never a pass.
  * test_prose_about_suppression_does_not_trip -- a comment/docstring mentioning "suppress" is
                                             not a code site (NAME-token scope honesty).
"""
from __future__ import annotations

import copy

import background.suppression_lint as sl
import background.suppression_register as sr


def _fixture(tmp_path, body: str):
    p = tmp_path / "candidate.py"
    p.write_text(body, encoding="utf-8")
    return tmp_path


def test_live_tree_passes():
    """The real committed background/** tree is clean -- every suppression-shaped site is
    registered or reasoned-waived, and no code_marker is dead. No false positive."""
    violations = sl.lint_suppression_registration()
    assert violations == [], f"live tree should be clean, got: {violations}"
    assert sl.registration_is_clean() is True


def test_unregistered_suppression_reds(tmp_path):
    """RULING criterion: an unregistered suppression added in a fixture MUST fail the gate."""
    root = _fixture(tmp_path, "def _quiet_gate():\n    my_cooldown = 0\n    return []  # nothing to do\n")
    violations = sl.lint_suppression_registration(root=root)
    assert any("my_cooldown" in v for v in violations), (
        f"an unregistered suppression-shaped identifier must red the lint, got: {violations}"
    )


def test_waiver_clears_a_false_positive(tmp_path):
    """A reasoned `not-a-suppression` waiver clears a genuine false positive."""
    root = _fixture(
        tmp_path,
        "# suppression-lint: not-a-suppression my_cooldown -- functional timer, not a page suppression\n"
        "def gate():\n    my_cooldown = 0\n    return []\n",
    )
    assert sl.lint_suppression_registration(root=root) == []


def test_waiver_requires_a_reason(tmp_path):
    """A waiver with an empty reason is not an account -- it must NOT clear the site."""
    root = _fixture(
        tmp_path,
        "# suppression-lint: not-a-suppression my_cooldown --   \n"
        "def gate():\n    my_cooldown = 0\n    return []\n",
    )
    violations = sl.lint_suppression_registration(root=root)
    assert any("my_cooldown" in v for v in violations), (
        "a reasonless waiver must NOT clear a suppression-shaped site"
    )


def test_dead_code_marker_reds():
    """Register<->code integrity: a code_marker matching no live identifier is a dead pointer."""
    reg = copy.deepcopy(sr.load_register())
    reg["entries"].append({
        "id": "bogus_dead_pointer",
        "code_markers": ["identifier_that_is_definitely_not_in_the_code_xyz"],
        "failure_direction": "noisy", "remediation": "none",
        "status": "compliant", "what_still_pages": "n/a",
    })
    violations = sl.lint_suppression_registration(register=reg)
    assert any("dead register/code pointer" in v for v in violations), (
        "a code_marker naming no live identifier must be flagged as a dead pointer"
    )


def test_removing_a_marker_re_reds_its_site():
    """A `code_markers` token is LOAD-BEARING: drop `proven_rest` from the deadman entry and the
    real site it covered (deadmans_switch.py) goes un-accounted-for -> coverage is not theatre."""
    reg = copy.deepcopy(sr.load_register())
    for e in reg["entries"]:
        if e.get("id") == "deadman_proven_rest_fold":
            e["code_markers"] = [m for m in e.get("code_markers", []) if m != "proven_rest"]
    violations = sl.lint_suppression_registration(register=reg)
    assert any("proven_rest" in v and "deadmans_switch" in v for v in violations), (
        f"dropping the load-bearing marker must re-red its live site, got: {violations}"
    )


def test_untokenisable_file_reds(tmp_path):
    """FAIL-CLOSED: an unscannable file is a FAILED check, never a silent pass."""
    (tmp_path / "broken.py").write_text("def x(:\n    this is not python (unterminated\n", encoding="utf-8")
    violations = sl.lint_suppression_registration(root=tmp_path)
    assert any("could not tokenise" in v or "FAILED check" in v for v in violations), (
        f"an untokenisable file must be a violation (fail-closed), got: {violations}"
    )


def test_prose_about_suppression_does_not_trip(tmp_path):
    """Scope honesty: a comment/docstring discussing suppression is not a code site -- only
    NAME tokens count, so prose about the sweep never false-positives."""
    root = _fixture(
        tmp_path,
        '"""This module discusses suppress / cooldown / throttle / silence at length."""\n'
        "# it also mentions suppress and fold in a comment\n"
        "def ordinary():\n    return 1\n",
    )
    assert sl.lint_suppression_registration(root=root) == []
