"""AN UNCLASSIFIED DOCUMENT ARRIVING FROM THE CONSOLE REFUSED EVERY LANE'S COMMIT.

Director, 2026-09-02: *"a staged document arriving should never block your landing."* Then, the same
day: *"The unclassified block was my defect three times over; it won't recur."*

It recurred within the hour, and that is why this is a mechanism rather than a reminder.

**IT WAS NEVER CARELESSNESS.** On the third occasion he DID state the severity — *"Severity: LATENT
— a programme, not a live defect"* — inside the `**Type:**` line. `finding_severity` parses a fixed
shape (`**Severity:** X · **Lane:** Y`) and there was no lane at all. **A machine format satisfied
in the wrong register by someone writing prose is a design problem.** Three times: 2026-08-30,
2026-08-31, 2026-09-02.

What it cost each time: an UNCLASSIFIED staging document refuses EVERY lane's commit, so a brief
arriving from the console blocked four gated landings, the publish path and the site until a human
noticed and chained it by hand.
"""
from __future__ import annotations

import inspect

import pytest

from background import finding_severity as fs
from background import staging_watcher as sw

BRIEF = "# [DIRECTOR-BRIEF] — a brief (2026-09-02)\n\n{body}\n\n## 1. Why\n\nBecause.\n"


def _write(tmp_path, name, body):
    p = tmp_path / name
    p.write_text(BRIEF.format(body=body))
    return p


# ── the window it closes ────────────────────────────────────────────────────────────────────
def test_an_unclassified_director_document_is_chained_on_arrival(tmp_path):
    """MUTATION: make `auto_chain` return None for `DIRECTOR_` and this fails — which is the state
    that blocked four landings, the publish path and the site."""
    p = _write(tmp_path, "DIRECTOR_BRIEF_X_2026-09-02.md", "A brief about a thing.")
    assert fs.parse_severity_file(p).severity == fs.UNCLASSIFIED
    assert sw.auto_chain(p) == "RECORDED"
    assert fs.parse_severity_file(p).severity == "RECORDED"


def test_the_authors_own_severity_wins_wherever_they_wrote_it(tmp_path):
    """THE THIRD OCCURRENCE EXACTLY. He stated it inside the `**Type:**` line, in prose. The
    machine could not read it; a human could. Carrying it through is the difference between
    accepting his classification and substituting one."""
    p = _write(tmp_path, "DIRECTOR_BRIEF_Y_2026-09-02.md",
               "**Type:** [BRIEF — problem and requirements. Severity: LATENT — a programme, not a "
               "live defect. The design is the delivery seat's.]")
    assert sw.auto_chain(p) == "LATENT"
    assert "carried through from the author's own words" in p.read_text()


def test_it_says_the_header_was_applied_automatically(tmp_path):
    """A classification the machine chose must never read as the author's. The note is what stops
    a later reader treating `RECORDED` as the director's own judgement."""
    p = _write(tmp_path, "DIRECTOR_CANON_Z_2026-09-02.md", "Canon.")
    sw.auto_chain(p)
    text = p.read_text()
    assert "applied AUTOMATICALLY" in text
    assert "correct it if it belongs to a lane" in text


def test_not_one_word_of_the_author_is_altered(tmp_path):
    """The header is purely additive — the same property the hand-chaining had, and the reason it
    was acceptable to do at all."""
    body = "**Type:** [BRIEF] and a sentence that must survive verbatim."
    p = _write(tmp_path, "DIRECTOR_BRIEF_W_2026-09-02.md", body)
    before = p.read_text()
    sw.auto_chain(p)
    after = p.read_text()
    for line in before.splitlines():
        assert line in after.splitlines(), line
    assert after.splitlines()[0] == before.splitlines()[0], "the title stays the first line"


# ── what it must never do ───────────────────────────────────────────────────────────────────
def test_it_cannot_launder_a_document_that_says_an_instrument_IS_WRONG(tmp_path):
    """THE HOLE THIS DEFAULT COULD HAVE OPENED. `RECORDED` is right for an instruction. An advisor
    document whose own text says a published figure is wrong is not an instruction, and defaulting
    it quiet would be exactly the laundering the severity gate exists to prevent.

    `finding_severity.by_construction_evidence` already names those documents, so the automatic
    path can only ever be as severe as the document's own words.

    MUTATION: drop the `by_construction_evidence` branch and this fails.
    """
    p = _write(tmp_path, "ADVISOR_POINTER_V_2026-09-02.md",
               "The published figures are wrong and overstated across the board.")
    assert sw.auto_chain(p) == "BLOCKING"


def test_it_never_touches_a_machine_authored_finding(tmp_path):
    """A `WORKER_FINDING`'s severity is a judgement about a defect and is the author's to make.
    Restricted to the same externally-authored set `finding_classes` already holds out of
    consolidation, because those are another party's ask rather than this machine's finding.

    MUTATION: widen the prefix test to all documents and this fails.
    """
    p = _write(tmp_path, "WORKER_FINDING_SOMETHING_2026-09-02.md", "A finding.")
    assert sw.auto_chain(p) is None
    assert fs.parse_severity_file(p).severity == fs.UNCLASSIFIED, "left alone, still refusing"


def test_an_already_classified_document_is_left_exactly_as_it_is(tmp_path):
    p = _write(tmp_path, "DIRECTOR_BRIEF_U_2026-09-02.md",
               "**Severity:** BLOCKING · **Lane:** D_billing_metering")
    before = p.read_text()
    assert sw.auto_chain(p) is None
    assert p.read_text() == before


def test_an_unreadable_document_does_not_take_the_watcher_down(tmp_path):
    """A watcher that dies on one malformed document stops watching all of them."""
    assert sw.auto_chain(tmp_path / "DIRECTOR_BRIEF_MISSING_2026-09-02.md") is None


# ── and it runs where it has to ─────────────────────────────────────────────────────────────
def test_it_chains_BEFORE_the_arrival_is_announced():
    """The window between "arrived" and "a human noticed" is a window in which nothing on this
    machine can land. Chaining inside that window makes it zero.

    MUTATION: remove the `auto_chain(...)` call from the new-file path and this fails.
    """
    src = inspect.getsource(sw)
    body = src.split("new_files = sorted(files - seen)", 1)[1]
    chained = body.index("auto_chain(")
    announced = body.index("New staged instruction:")
    assert chained < announced, "it must be chained before it is announced, not after"


@pytest.mark.parametrize("prefix", ["DIRECTOR_", "ADVISOR_"])
def test_the_set_is_the_one_finding_classes_already_holds_out(prefix):
    """One definition of "externally authored", not two that can drift apart."""
    from background import finding_classes as fc
    assert prefix in fc.EXTERNALLY_AUTHORED_PREFIXES
    assert "fc.EXTERNALLY_AUTHORED_PREFIXES" in inspect.getsource(sw.auto_chain)
