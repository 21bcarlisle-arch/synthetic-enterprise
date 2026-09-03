"""THE BANNER TABLE MUST MATCH THE GATES — the comparison nothing in the tree was making.

THE DEFECT THIS NAMES (2026-09-03)
-----------------------------------
`background/process_run_complete.py:_REFUSING_GATE_BANNERS` names the non-test gate that refused
a publish commit, so a reader is not sent to a suite that was never the problem. It shipped with
seven rows and **five of them matched nothing any gate prints**:

    WRITE-TIME GATE   the gate prints `[write-time-gate] ❌ COMMIT REFUSED`; the table's form
                      lives in that module's LINE-1 DOCSTRING and is never written to a stream.
    LEVEL PROMOTION   the gate prints `[level-gate] ❌ COMMIT REFUSED`.
    LIVE LEDGER       the guard raises `LiveLedgerWriteUnderTest` and is not a chain gate.
    FINDING SEVERITY  the words do not occur in this repository outside the table.
    I001              ruff's code; `tools/git-hooks/pre-commit` never invokes ruff.

Measured against the strings the gates really emit, a level-promotion refusal -- the second gate
in the chain -- reported `UNNAMEABLE` about a refusal that names itself on the next line.

WHY IT SURVIVED ITS OWN R15 SUITE, which is the part worth generalising
-----------------------------------------------------------------------
`test_a_non_test_gate_refusal_is_named.py` is a good suite and every leg of it passed. Its
fixtures are strings the TEST FILE supplies, so the table and its control were written from one
guess about what a gate prints, and a shared wrong guess is invisible to both. Nothing reached a
gate. That is this project's tautology shape wearing fixture clothes: the control could not fail
for the defect that was actually present.

SO THIS CONTROL IS KEYED TO THE PROPERTY, NOT TO TODAY'S WORDING
-----------------------------------------------------------------
It does not pin the table's contents -- rows may be added, dropped or reworded freely. It pins
the one relationship that makes the table mean anything: **every needle must be a string the
named emitter actually prints**, established by reading that file's own source, not ours.

A gate that rewords its banner therefore turns this RED, with the gate named, instead of going
quietly unnameable in `.publish_gate_state.json`. The module's comment argued that degradation
was fail-safe. It is -- for the reader of one refusal -- but "safe" is not "detected", and
undetected is how five rows were born dead and stayed dead.

DOCSTRINGS ARE EXCLUDED, AND THAT IS THE LOAD-BEARING PART. A plain `git grep` for the old
`WRITE-TIME GATE` needle answers PRESENT, because it is the first line of the gate's docstring.
Source-presence is the wrong question; *printed*-presence is the question, and the difference
between them is exactly one of the five dead rows. `test_a_needle_that_only_appears_in_a_docstring_is_rejected`
is the sole witness for that exclusion and uses that real string as its subject.

REUSE: tests/background/test_a_refusing_gate_banner_is_a_string_a_gate_prints.py
CLASS: CUSTOM
INDEX: searched "banner", "gate refusal", "refusing gate", "process_run_complete test". The
       closest is `tests/background/test_a_non_test_gate_refusal_is_named.py`, which owns the
       MATCHER's behaviour (fires / fail-safe / does-not-over-correct) against supplied fixtures
       and is the suite this defect passed straight through. This file asks the disjoint
       question it structurally cannot ask about itself -- do the fixtures correspond to
       anything real -- so it is a second control over the same table, not a duplicate of the
       first. `tests/architecture/test_a_domain_constant_carries_its_origin.py` is the nearest
       shape (a table checked against the world rather than against itself) but its subject is
       money constants and its evidence is an origin comment, neither of which applies here.
"""
from __future__ import annotations

import ast
import pathlib

import pytest

import background.process_run_complete as prc

PROJECT_DIR = pathlib.Path(prc.__file__).resolve().parent.parent

#: The hook chain, so the order claim below is read from the shell script rather than asserted.
PRE_COMMIT = PROJECT_DIR / "tools" / "git-hooks" / "pre-commit"


def _printed_literals(path: pathlib.Path) -> list[str]:
    """Every `str` constant in `path` that is NOT a module/class/function docstring.

    `ast.walk` descends into f-strings, so a banner assembled as f"[gate] {head}" contributes
    its literal parts -- which is what makes the `write-time gate` row checkable at all.
    """
    tree = ast.parse(path.read_text(encoding="utf-8"))
    docstrings = set()
    for node in ast.walk(tree):
        body = getattr(node, "body", None)
        if not isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        if body and isinstance(body[0], ast.Expr) and isinstance(body[0].value, ast.Constant) \
                and isinstance(body[0].value.value, str):
            docstrings.add(id(body[0].value))
    return [n.value for n in ast.walk(tree)
            if isinstance(n, ast.Constant) and isinstance(n.value, str)
            and id(n) not in docstrings]


# ── THE CONTROL ──────────────────────────────────────────────────────────────────────────────

@pytest.mark.parametrize("name,needles,emitter", prc._REFUSING_GATE_BANNERS,
                         ids=[row[0] for row in prc._REFUSING_GATE_BANNERS])
def test_every_needle_is_a_string_its_named_emitter_actually_prints(name, needles, emitter):
    """Defect: five of seven rows matched nothing any gate emits, so the gates they name were
    unnameable in the register while their real banners sat in the buffer being parsed."""
    path = PROJECT_DIR / emitter
    assert path.exists(), f"{name}: emitter {emitter} does not exist"

    literals = _printed_literals(path)
    for needle in needles:
        assert any(needle in lit for lit in literals), (
            f"{name}: the needle {needle!r} is printed by nothing in {emitter}. "
            f"Either the gate reworded its banner (update the row) or the row was never real. "
            f"Until one of those happens, a refusal by this gate reports UNNAMEABLE.")


def test_a_needle_that_only_appears_in_a_docstring_is_rejected():
    """Defect (the sole witness for the docstring exclusion): `WRITE-TIME GATE` was a live row
    for a day. `git grep` says PRESENT -- it is line 1 of the gate's docstring -- and the process
    prints it never. If this control counted docstrings, that dead row would pass it."""
    gate = PROJECT_DIR / "tools" / "write_time_gate.py"
    source = gate.read_text(encoding="utf-8")

    assert "WRITE-TIME GATE" in source, (
        "subject moved: this leg needs a string that IS in the source and IS NOT printed")
    assert not any("WRITE-TIME GATE" in lit for lit in _printed_literals(gate)), (
        "the docstring exclusion is not excluding docstrings, so source-presence and "
        "printed-presence have collapsed into one answer and the dead row would pass")


def test_all_of_a_rows_needles_are_required_not_any_of_them():
    """Defect (fail-open twin): the write-time gate prints `[write-time-gate] ⚠️  WARN ONLY` when
    it is NOT refusing. A one-substring match on its prefix would name it as the refuser of a
    commit it deliberately let through."""
    warn_only = "\n[write-time-gate] ⚠️  WARN ONLY (tools/write_time_gate.mode) -- AO2.\n"
    assert prc._parse_refusing_gate(warn_only) is None, (
        "a gate that explicitly did not refuse is being named as the refuser")

    refused = "\n[write-time-gate] ❌ COMMIT REFUSED -- AO2, the write-time reuse gate.\n"
    assert prc._parse_refusing_gate(refused) == "write-time gate", (
        "and the real refusal must still be named, or the leg above is passing by being blind")


def test_the_table_is_ordered_by_the_chain_that_actually_runs_the_gates():
    """Defect: the chain short-circuits, so on a mixed buffer the FIRST matching row is reported.
    The original table put orphan-ratchet first and level-promotion fourth; `pre-commit` runs
    level-promotion at line 33 and the ratchet at line 111. Ordering the table by anything other
    than the chain reports a gate that never got to run."""
    chain = PRE_COMMIT.read_text(encoding="utf-8").splitlines()

    def chain_line(fragment):
        for i, line in enumerate(chain):
            if fragment in line and not line.lstrip().startswith("#"):
                return i
        return None

    # Only the rows whose gate is invoked by pre-commit itself can be ordered against it. The
    # write-time gate runs from commit-msg, i.e. strictly after all of pre-commit passed, so it
    # is last by construction and is asserted as such rather than looked up here.
    positions = []
    for name, _needles, emitter in prc._REFUSING_GATE_BANNERS:
        at = chain_line(pathlib.Path(emitter).name)
        if at is not None:
            positions.append((name, at))

    assert len(positions) >= 2, "nothing left to order -- this leg has stopped being a control"
    assert positions == sorted(positions, key=lambda p: p[1]), (
        f"table order {[p[0] for p in positions]} is not the chain's order; "
        f"a mixed buffer would name a gate that ran after the one that refused")

    assert prc._REFUSING_GATE_BANNERS[-1][0] == "write-time gate", (
        "the commit-msg gate must sit last: its needles are the only ones that can co-occur "
        "with an earlier gate's refusal, and last is what makes the earlier gate win")


def test_the_table_does_not_silently_claim_to_cover_the_whole_chain():
    """Defect: 'no gate banner this classifier knows' is honest only while the reader knows the
    table is partial. The chain has far more gates than the table names, and a future reader
    treating UNNAMED as 'not a gate' would repeat the 18.7-hour misdiagnosis."""
    chain = PRE_COMMIT.read_text(encoding="utf-8")
    invoked = [ln for ln in chain.splitlines()
               if "|| exit 1" in ln and not ln.lstrip().startswith("#")]

    assert len(invoked) > len(prc._REFUSING_GATE_BANNERS), (
        "coverage is no longer partial -- if the table now names every gate, delete this leg "
        "and say so, rather than leaving a control that cannot fail")
