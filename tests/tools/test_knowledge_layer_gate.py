"""The knowledge-layer gate, each test named by the defect it exists to catch.

Director console, 2026-09-05: *"When a piece of work produces domain understanding, it lands in the
Knowledge layer with its sources and its gaps stated. Findings about the machine go to the
registers."*
"""
from __future__ import annotations

import pytest

from tools import knowledge_layer_gate as gate

_KNOWN = {"what-a-customer-is-worth", "price-cap"}


def test_new_research_with_no_declaration_is_refused():
    """THE DEFECT, measured: 78 of 82 documents in docs/market_research/ are named by no Knowledge
    surface at all. Research that reaches no reader is indistinguishable from research that does —
    both are a committed file — so nothing could ever notice."""
    ok, why = gate.verdict("docs/market_research/x.md", "# Some anchor\n\nA number and a source.\n",
                           _KNOWN)

    assert ok is False
    assert "does not say where its understanding lands" in why


def test_a_declaration_naming_a_live_topic_passes():
    ok, _ = gate.verdict(
        "docs/market_research/x.md",
        "# Anchor\n\n**Knowledge:** what-a-customer-is-worth\n\nbody\n", _KNOWN)
    assert ok is True


def test_a_declaration_naming_a_topic_THAT_DOES_NOT_EXIST_is_refused():
    """THE FAILURE THIS GATE WOULD MOST EASILY HAVE: accepting any text after the colon. A
    declaration pointing at a page nobody has written still reaches no reader, which is the whole
    defect, so it must fail exactly as a missing declaration does."""
    ok, why = gate.verdict(
        "docs/market_research/x.md",
        "# Anchor\n\n**Knowledge:** a-page-nobody-wrote\n\nbody\n", _KNOWN)

    assert ok is False
    assert "not a topic in" in why


def test_an_explicit_none_with_a_reason_passes_because_the_escape_is_counted_not_prevented():
    """A reason predicate cannot be written that a person cannot satisfy. Pretending otherwise
    would make this an exhortation wearing a mechanism's clothes. `--report` counts the escapes
    instead, from the documents themselves."""
    ok, _ = gate.verdict(
        "docs/market_research/x.md",
        "# Anchor\n\n**Knowledge:** none -- a raw source pull, the understanding lands in the "
        "cells page this feeds\n\nbody\n", _KNOWN)
    assert ok is True


def test_a_bare_none_without_a_reason_is_refused():
    """The other side: the escape is deliberate, but it must SAY something, or the count it feeds
    is a count of the word `none`."""
    ok, _ = gate.verdict("docs/market_research/x.md",
                         "# Anchor\n\n**Knowledge:** none\n\nbody\n", _KNOWN)
    assert ok is False


def test_a_declaration_BURIED_IN_THE_BODY_does_not_answer_for_the_header():
    """Research documents quote topic names constantly. A body-wide search would let a passing
    mention satisfy the header, which is the difference between a declaration and a coincidence."""
    body = "# Anchor\n\n" + ("filler\n" * 40) + "**Knowledge:** what-a-customer-is-worth\n"
    ok, _ = gate.verdict("docs/market_research/x.md", body, _KNOWN)

    assert ok is False, "a declaration below the head must not count as one"


def test_an_unreadable_topic_graph_does_not_wedge_every_lane(monkeypatch, capsys, tmp_path):
    """FAIL-OPEN, DELIBERATELY, and asserted because it is the arguable direction.

    The registry is not this gate's subject. A JSON parse error in it must not stop a tree several
    lanes write at once; one research document without a declaration is recoverable, a wedged tree
    is the thing that eats days. Contrast `tools/startup_anchor_freshness.py`, which fails CLOSED,
    because there the unmeasurable thing IS the subject.
    """
    monkeypatch.setattr(gate, "staged_new_research", lambda *a, **k: ["docs/market_research/x.md"])
    monkeypatch.setattr(gate, "GRAPH", tmp_path / "nope.json")

    assert gate.main([]) == 0
    assert "not blocking" in capsys.readouterr().err


def test_editing_research_is_not_an_add_so_the_gate_stays_quiet(monkeypatch):
    """REACHABILITY OF THE QUIET BRANCH, and the reason it exists. 45% of recent commits touch
    docs/market_research/; a gate firing on every one would teach every lane to type `none`
    reflexively, destroying the escape count as surely as removing it."""
    monkeypatch.setattr(gate, "staged_new_research", lambda *a, **k: [])
    assert gate.main([]) == 0


def test_the_backlog_is_derived_from_the_filesystem_and_is_not_empty():
    """REACHABILITY against the live tree, and the number the director asked for. A register of
    orphans would go stale; this re-asks "does any published surface name this file" every time.
    The floor guards the failure where a path moved and the scan silently measured nothing."""
    r = gate.orphan_research()

    assert r["research"] >= 50, "the research directory did not resolve — the scan is measuring nothing"
    assert r["orphans"] > 0
    assert r["orphans"] <= r["research"]


def test_the_gate_runs_THE_WAY_THE_HOOK_RUNS_IT(tmp_path):
    """FOURTH INSTANCE OF THIS DEFECT IN ONE SESSION would be this file.

    The hook runs gates as SCRIPTS, so `sys.path[0]` is `tools/` and not the repo root.
    `next_step_gate` shipped dead this way; `generate_project_state` published a placeholder over a
    live figure; `project_portfolio_to_2026` wrote None onto all 145 accounts. Every control was
    green in all three because pytest fixes the path before any test can import the module.

    `sys.path[0] = "tools"` is what makes this faithful — a plain `-c` leaves the CWD on the path
    and would pass with or without the guard.
    """
    import os
    import subprocess
    import sys as _sys

    done = subprocess.run(
        [_sys.executable, "-c",
         "import sys; sys.path[0] = 'tools';"
         "import runpy;"
         "m = runpy.run_path('tools/knowledge_layer_gate.py', run_name='probe');"
         "print(len(m['topic_ids']()))"],
        cwd=str(gate.PROJECT), capture_output=True, text=True, timeout=180,
        env={**os.environ, "PYTHONPATH": ""},
    )

    assert done.returncode == 0, done.stderr
    assert int(done.stdout.strip()) > 5, f"topic graph unreachable as a script: {done.stderr!r}"


@pytest.mark.parametrize("declared", ["what-a-customer-is-worth", "price-cap"])
def test_the_page_this_rule_was_written_for_is_a_real_topic(declared):
    """The CLV thesis was staged as an advisor reference and the director asked for it as a
    Knowledge page. If it is not in the graph, the gate cannot accept a declaration naming it and
    the rule has no destination."""
    assert declared in gate.topic_ids()
