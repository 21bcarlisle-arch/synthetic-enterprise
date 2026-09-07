"""The machine's bookkeeping is the machine's, each test named by the defect it catches.

Four director documents in two days arrived without the severity header, and 51 without a Knowledge
declaration. Both are machine requirements on documents written by someone with no reason to know
they exist, and transcribing them by hand a fifth time is the same act repeated, not a fix.
"""
from __future__ import annotations

import pytest

from tools import file_director_document as filer


def _doc(tmp_path, body, name="DIRECTOR_CANON_X_2026-09-07.md"):
    p = tmp_path / name
    p.write_text(body, encoding="utf-8")
    return p


def test_SEVERITY_IS_READ_FROM_THE_DOCUMENT_never_chosen(tmp_path):
    """The director states his own severity in the Type block and that sentence is his. Reading it
    is transcription; picking one would be deciding on his behalf how serious his own instruction
    is -- which `finding_severity` names as the anti-pattern in its own docstring."""
    p = _doc(tmp_path, "# [DIRECTOR-CANON] - A thing\n\n"
                       "**Type:** [CANON - about households. Severity: BLOCKING. More words.]\n")
    out = filer.file_document(p, lane="W2_customer_generator")
    assert "**Severity:** BLOCKING" in out


def test_A_DOCUMENT_THAT_STATES_NO_SEVERITY_IS_REFUSED_not_defaulted(tmp_path):
    """FAIL-CLOSED ON THE ONE DEFAULT THAT WOULD BE INVISIBLE. Defaulting to LATENT would let a
    genuinely blocking instruction file itself as minor, and nothing downstream could tell."""
    p = _doc(tmp_path, "# [DIRECTOR-CANON] - A thing\n\n**Type:** [CANON - about households.]\n")
    with pytest.raises(filer.CannotFile, match="states no severity"):
        filer.file_document(p, lane="W2_customer_generator")


def test_AN_UNREADABLE_LANE_IS_REFUSED_because_a_wrong_lane_LOOKS_ANSWERED(tmp_path):
    """An absent header is visibly absent. A header naming the wrong lane points the machine at the
    wrong work while reading as complete, which is worse."""
    p = _doc(tmp_path, "# [DIRECTOR-CANON] - A thing\n\n**Type:** [CANON. Severity: LATENT.]\n")
    with pytest.raises(filer.CannotFile, match="no lane"):
        filer.file_document(p)


def test_THE_KNOWLEDGE_TOPIC_IS_NEVER_INVENTED(tmp_path):
    """A topic id that does not exist in the graph would satisfy the gate and reach no reader --
    exactly the failure the gate exists to catch. Absent an explicit topic, the honest `none --
    reason` form is written instead."""
    p = _doc(tmp_path, "# [DIRECTOR-CANON] - A thing\n\n"
                       "**Type:** [CANON - households. Severity: LATENT.]\n")
    out = filer.file_document(p, lane="W2_customer_generator")
    assert "**Knowledge:** none --" in out
    assert "**Knowledge:** how-many" not in out, "a topic was invented rather than left to a seat"


def test_FILING_IS_IDEMPOTENT_and_leaves_an_existing_header_alone(tmp_path):
    """The filer runs over documents that already carry one piece and not the other; doubling a
    header would break the reader that parses the first match."""
    p = _doc(tmp_path, "# [DIRECTOR-CANON] - A thing\n\n"
                       "**Severity:** RECORDED · **Lane:** H_harness\n\n"
                       "**Type:** [CANON - harness. Severity: BLOCKING.]\n")
    once = filer.file_document(p, lane="H_harness")
    p.write_text(once, encoding="utf-8")
    twice = filer.file_document(p, lane="H_harness")
    assert once == twice
    assert once.count("**Severity:**") == 1, "the existing header was duplicated"
    assert "**Severity:** RECORDED" in once, (
        "an existing header was overwritten from the Type block; the header on the document wins")


def test_THE_BACKLOG_IS_VISIBLE():
    """The count is the argument for the tool existing. If it ever reads zero the migration is done
    and this assertion should be deleted with a note, not left to pass vacuously."""
    missing = filer.unfiled()
    assert isinstance(missing, list)
