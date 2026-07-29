"""R15 both-ways proof for background/reserved_clause_gate.py -- exit-criterion §4 of the
reversible-draws atom (ruling DIRECTOR_RULING_WORK_AT_RISK_DEFAULT_2026-07-29.md §4).

R15 requires a control PROVE it fires on its own named defect AND that it does NOT fire on the
legitimate case (not a tautology / not fail-noisy). The named defect: a reserved clause staged
WITHOUT a §2 (irreversibility) justification. The legitimate case: the same clause carrying a
§2 justification.

MUTATION arguments (why each direction is a real proof, not theatre):
- Delete the justification check (make scan always report on any reserved clause) ->
  test_justified_reserved_clause_passes fails (a legit clause would be flagged). Proves the
  §2-justification is what clears the clause, independently of the trigger phrase.
- Delete the trigger detection (make scan always return []) -> test_unjustified_clause_flagged
  fails. Proves the control actually fires on its defect.
"""
from background.reserved_clause_gate import (
    has_section2_justification,
    scan_reserved_clauses,
)

_CLAUSE = "This new step returns to the director for ratification before it proceeds."


def test_unjustified_reserved_clause_flagged():
    """(a) FIRES on the defect: a reserved clause with no §2 justification is reported."""
    violations = scan_reserved_clauses(_CLAUSE)
    assert len(violations) == 1
    assert "ratification" in violations[0]["clause"]
    assert violations[0]["line"] == 1


def test_justified_reserved_clause_passes():
    """(b) does NOT fire on the legitimate case: the SAME clause + a machine-readable §2 tag is
    valid. The justification -- not the phrase -- is what changes the verdict (independence)."""
    text = _CLAUSE + " [§2: real money -- releasing funds commits an irreversible bank payment]"
    assert scan_reserved_clauses(text) == []


def test_prose_irreversibility_marker_also_justifies():
    text = _CLAUSE + " This is a one-way door: the payment cannot be reversed."
    assert scan_reserved_clauses(text) == []


def test_ascii_s2_tag_justifies():
    text = _CLAUSE + " [S2: touches a safety control, director-console only]"
    assert scan_reserved_clauses(text) == []


def test_ordinary_reversible_text_not_flagged():
    """No reserved clause at all -> nothing to justify, nothing reported."""
    text = "This refactor renames the draw function and adds a new tier. git revert undoes it."
    assert scan_reserved_clauses(text) == []


def test_justification_must_share_the_paragraph():
    """A §2 marker in a DIFFERENT paragraph does not justify the clause -- the ruling says 'in
    the same document' but the gate binds it to the same paragraph so an unrelated justification
    elsewhere cannot launder an unjustified clause."""
    text = _CLAUSE + "\n\n[§2: unrelated irreversible thing over here]"
    violations = scan_reserved_clauses(text)
    assert len(violations) == 1


def test_line_number_points_at_the_clause():
    text = "intro line\n\nsecond para\n\n" + _CLAUSE
    violations = scan_reserved_clauses(text)
    assert len(violations) == 1
    assert violations[0]["line"] == 5


def test_denied_clause_not_flagged():
    """NEGATION guard: a clause being DENIED ('does not queue for permission') is discussing the
    mechanism, not staging a reserved clause -- it must not be flagged (kills the obvious false
    positive the atom's own doc triggered)."""
    assert scan_reserved_clauses("Reversible work proceeds; it does not queue for permission.") == []
    assert scan_reserved_clauses("This step never returns for ratification.") == []


def test_fail_safe_on_empty_and_none():
    """FAIL-SAFE: empty/None never crashes and never fabricates a violation."""
    assert scan_reserved_clauses("") == []
    assert scan_reserved_clauses(None) == []
    assert scan_reserved_clauses(123) == []  # type: ignore[arg-type]


def test_has_section2_justification_direct():
    assert has_section2_justification("[§2: irreversible]") is True
    assert has_section2_justification("provably irreversible act") is True
    assert has_section2_justification("just a normal sentence") is False
    assert has_section2_justification("") is False


def test_multiple_clauses_each_evaluated():
    text = (
        _CLAUSE
        + "\n\n"
        + "A second step is director-reserved. [§2: changes what the machine is allowed to do]"
        + "\n\n"
        + "A third step queues for permission with no reason given."
    )
    violations = scan_reserved_clauses(text)
    # first and third unjustified; second justified
    assert len(violations) == 2
    lines = sorted(v["line"] for v in violations)
    assert lines == [1, 5]
