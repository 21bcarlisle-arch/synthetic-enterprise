"""THE GATE BLOCKING RECORD'S READER — the honesty contract, in a module that publishes nothing.

WHY THIS MODULE EXISTS (2026-08-21, the 33-hour publish outage)
--------------------------------------------------------------
The publish gate's blocking scope is DERIVED, not listed: `background/publish_scope.py` walks
the static import graph backwards from the six modules that produce or render a published
number, and every test that transitively imports one of them may block a publish. That design
is right and stays. What it cannot see is a single import edge that has nothing to do with
publishing.

`background/supervisor.py` — the harness's draw/queue brain, which nearly every
`tests/background/**` module imports — reached `background/process_run_complete.py` for ONE
function: `last_blocking_tests`, a pure JSON reader over
`.last_gate_blocking_tests.json`. The publisher imports all five other publish-path modules,
so that one edge put the ENTIRE harness self-governance suite inside the publish gate:

    tests/background/test_blocked_atom_visibility.py
        -> background/supervisor.py
        -> background/process_run_complete.py
        -> simulation/publish_market_feed.py          (and the other four)

Measured on the real graph at 104101496: cutting that one edge removes **36 test files** from
the blocking scope (198 -> 162) — the draw ladder, the executor daemon and governor, the harden
gates, forward discovery, the mint, blocked-atom visibility. None of them can make a figure on
the live site wrong, which is `publish_scope.PUBLISH_PATH_SOURCES`'s own membership test. They
were in the gate because of an import, not because of a risk.

The cost was not theoretical. `tests/background/test_blocked_atom_visibility.py` alone shells
`blocked_atom_visibility --check` with no timeout, and that child runs the real BUILD draw twice
per parked atom: **198 seconds**, inside a gate that runs every publish cycle, on a repo whose
publish cadence is 330 seconds.

WHAT THIS IS
------------
Contracts the supervisor must be able to ASK without importing the publisher. It has no imports
beyond the standard library, so nothing that reads one of them is dragged toward the publish
path again. Two live here now:

  * the gate blocking record's four-way honesty contract (`read_blocking_record`), the reason
    the module was cut in the first place;
  * the operational-layer timeout vocabulary (`operational_layer_timeout_named_a_test` and the
    three "cannot tell" phrases), moved 2026-09-11 after the SAME edge was re-cut by hand.

That membership rule is deliberately narrow, and it is NOT "small things the supervisor uses".
It is: a contract with more than one reader, where at least one reader must stay off the
publish path. Anything that WRITES a published number, or reads one, does not belong here --
`process_run_complete` keeps every such thing, including the producer of the phrases below.

WHY THE POLICY IS AN ARGUMENT, AND WHY THE DEFAULTS ARE ALLOWED TO BE A SECOND COPY
-----------------------------------------------------------------------------------
`GATE_BLOCKING_TESTS_MAX_AGE_SECONDS` is `2 * GATE_SUITE_TIMEOUT_SECONDS` — the PUBLISHER's
policy, derived from the publisher's own bound. It cannot be computed here without dragging
that bound back across the seam, which would re-cut nothing.

So the age bound and the citation cap are ARGUMENTS, and `process_run_complete` passes its own
authoritative constants at call time. That also preserves the existing test contract exactly:
six test modules monkeypatch `prc.GATE_BLOCKING_TESTS_FILE` /
`prc.GATE_BLOCKING_TESTS_MAX_AGE_SECONDS` and still steer the read, because the wrapper reads
those globals when it is called.

The supervisor has no such constants and must not grow them, so the DEFAULTS below exist for
it. They are, deliberately and visibly, a SECOND COPY of the publisher's values — the shape
this repo normally refuses. It is admissible here only because the copy cannot drift SILENTLY:
`tests/background/test_publish_scope.py::test_the_blocking_readers_defaults_match_the_publisher`
asserts the equality and fails on any divergence, so the duplication is a checked mirror rather
than a remembered one. If that control is ever deleted, delete these defaults with it.

DELEGATION IS STILL THE POINT (supervisor.py::_live_gate_blocking_record). The contract lives in
exactly ONE place; both the publisher's alarm payload and the supervisor's RUNG-1 draw ask it
rather than restating it. What changed is only WHERE the one place sits — a leaf, not the
publisher — so that asking it no longer means importing the publish path.

REUSE: background/publish_gate_blocking_read.py
CLASS: CUSTOM
INDEX: searched "blocking record", "gate state reader" — the record has exactly two readers
       (`process_run_complete.last_blocking_tests` and `.last_red_census`) and this is the
       first, relocated whole rather than reimplemented. The census reader deliberately stays
       in the publisher: nothing outside it reads the census, so moving it would widen the
       change without cutting any edge.
"""
from __future__ import annotations

import json
import time
from pathlib import Path

# The publisher's values, mirrored for readers that must not import the publisher (see the
# module docstring). Held equal to `process_run_complete`'s constants by a control that fails on
# divergence — never by memory. 3800s is the gate bound at the time of writing; the derivation
# (2x) and the cap (12) are the publisher's, not this module's, to change.
DEFAULT_MAX_AGE_SECONDS = 2 * 3800
DEFAULT_MAX_CITED = 12


# ── THE OPERATIONAL-LAYER TIMEOUT VOCABULARY (moved here 2026-09-11, same reason as above) ──
#
# These live in a leaf for exactly the reason the module docstring gives, and they are here
# because the reason was proven a second time. 59a91d4a2 gave the supervisor's RUNG-1 draw a
# top-level `from background.process_run_complete import operational_layer_timeout_named_a_test`
# -- one symbol, a four-token predicate, no publishing anywhere near it -- and that single edge
# re-enrolled the whole harness self-governance suite in the publish gate, measured at 275
# blocking test files against 239 when the edge is cut. It was the right instinct (import the
# contract, never mirror it) pointed at the wrong module.
#
# So the vocabulary moves to where the supervisor can ask it WITHOUT reaching the publisher.
# `process_run_complete` imports these back and remains their only WRITER: the phrases are
# emitted by `operational_layer_timeout_subject`, which reads a dead subprocess's output and
# has no business in a leaf. Only the shared part -- the phrases themselves and the predicate
# that distinguishes them from a real nodeid -- lives here.
#
# THE CONVENTION, stated once because two modules now depend on it: a "cannot tell" answer is
# PARENTHESISED and a real pytest nodeid is not. That is what `..._named_a_test` tests, and it
# is why the phrases and the predicate had to travel together -- splitting them would leave the
# convention implicit in one module and asserted in another, free to drift silently.
OPERATIONAL_LAYER_TIMEOUT_NO_OUTPUT = (
    "(the killed run captured no output at all -- it named nothing)")
OPERATIONAL_LAYER_TIMEOUT_IN_COLLECTION = (
    "(no test had started -- the budget ran out during COLLECTION)")
OPERATIONAL_LAYER_TIMEOUT_BETWEEN_TESTS = (
    "(between tests -- the last one to start, `{}`, had already reported; the budget ran out "
    "in teardown, a fixture, or session shutdown)")


def operational_layer_timeout_named_a_test(subject):
    """True when `subject` is a real nodeid rather than one of the "cannot tell" phrases.

    One place, so the log line, the state file and the supervisor's draw all agree about when
    there is something to go and look at -- and so the distinction is testable on its own."""
    return bool(subject) and not subject.startswith("(")


def read_blocking_record(path, *, now=None, max_age=DEFAULT_MAX_AGE_SECONDS,
                         max_cited=DEFAULT_MAX_CITED):
    """(node_ids, git_hash) from the last red gate, or ([], None) if not knowably recent.

    ([], None) is returned for absent, unreadable, malformed AND stale — all four mean the same
    thing to a reader, which is "this alarm does not know", and the alarm says so.

    `max_age` (seconds) and `max_cited` are the CALLER's policy; see the module docstring for
    why they are not declared here."""
    p = Path(path)
    now = time.time() if now is None else float(now)
    try:
        rec = json.loads(p.read_text())
        if not isinstance(rec, dict):
            return [], None
        ts = rec.get("ts")
        if not isinstance(ts, (int, float)):
            return [], None
        if now - float(ts) > max_age:
            return [], None
        node_ids = rec.get("node_ids")
        if not isinstance(node_ids, list):
            return [], None
        gh = rec.get("git_hash")
        return ([str(n) for n in node_ids[:max_cited]],
                str(gh) if isinstance(gh, str) else None)
    except (json.JSONDecodeError, OSError, ValueError, TypeError):
        return [], None
