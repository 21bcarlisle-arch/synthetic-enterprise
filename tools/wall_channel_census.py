#!/usr/bin/env python3
"""
REUSE: tools/wall_channel_census.py
CLASS: CUSTOM
INDEX: searched "wall", "crossing", "census", "channel", "ratchet", "enumerator", "conformance".
       `tools/epistemic_wall.py` already enumerates TWO of the six channels (A: the direct import
       edge, B: the indirect edge through a bridge) and owns the walker, the classifiers and the
       HEAD export. All three are REUSED here by import, never reimplemented -- a second walker
       with its own notion of an edge is exactly the drift `epistemic_wall`'s own docstring warns
       about. `tools/wall_crossing_dispositions.py` rules channels A and B row by row and is the
       enforcement this module deliberately does NOT duplicate (see A/B DELEGATION below).
       `tools/annual_report_import_ratchet.py` and `tools/company_network_isolation.py` are the
       shape reused for the freeze: frozen set, fail on new, shrink-only, fail-closed.

EVERY CHANNEL ACROSS THE WALL GETS AN ENUMERATOR. THAT IS THIS ATOM'S EXIT CRITERION.

Atom `EP6_wall_protocol_typing`. The 2026-08-15 conformance census
(`docs/design/EP6_WALL_CONFORMANCE_CENSUS_DISCOVER.md`) found SIX mechanisms carrying data across
the SIM/company wall, and that the repo's one enumerator sees TWO of them. Its §8 then rejected
the obvious exit criterion and named the testable one, verbatim:

    "An exit criterion of the form 'every crossing is envelope-borne or grandfathered' is not
    directly testable at HEAD today, and an atom that adopted it would be adopting an
    unfalsifiable criterion ... The testable form is PER-CHANNEL: each channel gets its own
    enumerator and its own shrink-only list, and the exit criterion is that every channel HAS an
    enumerator."

This module is the four missing enumerators (C, D, E, F) and the shrink-only list over them. It
also DELEGATES to the two that exist, so that "does every channel have an enumerator?" is a
question one function answers instead of a question a reader has to assemble.

WHY AN ENUMERATOR AND NOT A MIGRATION. Four of these channels should not become envelopes and the
census says why: wrapping 93 report keys in `WallResponse` is the "protocol cathedral" this atom's
own `origin_note` forbids by name, and a structural Protocol (channel E) has nowhere to put a
schema version at all. What every channel CAN have is a stable identifier for its members and a
list that may shrink but not grow. That is what makes the invisible ones visible, and it is the
whole of what this module claims.

THE UNIT PER CHANNEL, chosen because it is the only stable identifier that channel has:

  A  direct import edge          (src module, dst module)          -- delegated, see below
  B  indirect edge via a bridge  (src module, dst module)          -- delegated, see below
  C  the envelope                (importer module, seam module)
  D  the same-step typed port    (port module, importer module)
  E  the structural Protocol     (file path, class name)
  F  the published artefact      (top-level key, reader file path)

A/B DELEGATION -- WHY THIS MODULE ENUMERATES SIX CHANNELS AND FREEZES ONLY FOUR. Channels A and B
already have an enforced shrink-only control: `docs/design/WALL_CROSSING_DISPOSITION_REGISTER.md`
carries a disposition per row and `tools/wall_crossing_dispositions.py` fails the commit when one
is missing. Freezing them a second time here would put two controls on one subject, which does not
double the safety -- it means an ordinary ruled change reds a gate whose owner is another file, and
a gate that reds for reasons its subject cannot fix is routed around within a day. So A and B are
REPORTED (the exit criterion is about coverage) and NOT frozen (enforcement has an owner already).

FAIL-CLOSED, THREE WAYS (R15: an unavailable check is a FAILED check):
  1. The tree cannot be exported at `rev`      -> `head_export` raises. Never an empty tree, which
                                                  would confirm every claim ever made.
  2. The artefact is absent/unparseable at rev -> `CensusUnavailable`. "Could not look" and "found
                                                  nothing" are the same number and opposite facts.
  3. The artefact has no top-level keys        -> `CensusUnavailable`. An empty denominator makes
                                                  channel F vacuously conformant.
A channel measuring ZERO members is NOT refused, deliberately: zero is a legitimate reading of a
channel that has been fully paid down, and a control pinned to a non-zero count reds on its own
success case (`feedback_a_control_pinned_as_a_count_reds_on_its_own_success_case`).

ONE REF, BOTH SIDES. Channel F joins the artefact's key set against the reader modules that access
those keys. Those are two sides of one census and they are read from THE SAME `rev` -- the tree via
`git archive`, the artefact via `git show rev:path`. Reading the artefact from the working tree
while reading the readers from HEAD would compare a publisher's live output against a committed
reader set and report a difference that is nobody's defect
(`feedback_a_two_sided_census_must_read_both_sides_from_one_ref`).

INDEPENDENCE. The current reading is COMPUTED from a tree; the baseline is a COMMITTED data file
written by a human-reviewed freeze. Neither is derived from the other, so the comparison is not the
tautology R15 names first.

WHAT THIS DOES NOT ESTABLISH, stated here rather than discovered later:
  * Channel F's list is the CHANNEL WIDTH, not the count of SIM-origin crossings. The per-key
    provenance walk was attempted on 2026-08-15 and is unanswerable for 38 of the keys by
    construction (this atom's store, FINDING 1) -- the orchestrator binds both sides' values into
    one row in one function scope. A shrink-only width is the honest control that walk leaves
    available: the set cannot grow silently.
  * Channel E's list is a SUPERSET. It enumerates every `Protocol` declared business-side, not only
    those a world object satisfies -- deciding satisfaction needs a type checker. Superset is the
    safe direction for a ratchet: a new Protocol must be looked at, and a company-only one is
    dismissed in the freeze note rather than missed.

CLI:
    python3 -m tools.wall_channel_census            # check the tree at HEAD against the baseline
    python3 -m tools.wall_channel_census --worktree # check the working tree (diagnosis only)
    python3 -m tools.wall_channel_census --freeze   # rewrite the baseline from HEAD
"""
from __future__ import annotations

import argparse
import ast
import json
import os
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parents[1]
if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))

from tools.epistemic_wall import (  # noqa: E402
    BRIDGE_PACKAGES,
    WALL_DIRS,
    build_edges,
    crossings_at,
    head_export,
    indirect_crossings,
)

BASELINE_PATH = PROJECT_DIR / "docs" / "design" / "wall_channel_census_baseline.json"

#: The artefact channel F is a census of. Tracked in git, so it can be read at a rev.
ARTEFACT_REL = "docs/reports/run_output_latest.json"

#: Every tree a crossing can live in. `tools` is here because channel D's ports live there.
CENSUS_DIRS: tuple[str, ...] = tuple(dict.fromkeys(WALL_DIRS + BRIDGE_PACKAGES + ("tools",)))

#: The business side -- channels E and F ask their questions of these trees only.
BUSINESS_DIRS: tuple[str, ...] = ("company", "saas")

#: The envelope package channel C is defined by.
CONTRACTS_PREFIX = "interface.contracts."


@dataclass(frozen=True)
class Channel:
    """One mechanism that carries data across the wall."""

    id: str
    subject: str
    #: False for A and B -- reported for coverage, enforced by the disposition register.
    frozen: bool


CHANNELS: tuple[Channel, ...] = (
    Channel("A_direct_import", "src module imports a module on the other side", frozen=False),
    Channel("B_indirect_import", "src reaches the other side through a bridge package", frozen=False),
    Channel("C_envelope", "module imports an `interface.contracts` seam", frozen=True),
    Channel("D_typed_port", "module imports a `tools/*_port` same-step port", frozen=True),
    Channel("E_structural_protocol", "business-side `Protocol` satisfied structurally", frozen=True),
    Channel("F_published_artefact", "business-side module reads a run-output key", frozen=True),
)

CHANNEL_IDS: tuple[str, ...] = tuple(c.id for c in CHANNELS)
FROZEN_CHANNEL_IDS: tuple[str, ...] = tuple(c.id for c in CHANNELS if c.frozen)


class CensusUnavailable(RuntimeError):
    """The census could not be taken. Deliberately an error, never an empty result."""


# ── the six enumerators ──────────────────────────────────────────────────────────────────────
# Each takes the root of a tree (and, for F, the artefact read from the SAME rev) and returns a
# set of stable identifiers. Parameterised by root so the R15 fixtures point them at a tmp tree.

def _entry(*parts: str) -> str:
    """One census member, rendered as the identifier the baseline stores."""
    return " -> ".join(parts)


def enumerate_a(root: str, artefact: dict) -> set[str]:
    """Channel A -- the direct import edge. Delegated to the walker that owns this subject."""
    return {_entry(src, dst) for src, dst in crossings_at(root)}


def enumerate_b(root: str, artefact: dict) -> set[str]:
    """Channel B -- the indirect edge through a bridge. Delegated, same reason."""
    return {_entry(src, dst) for src, dst in indirect_crossings(root)}


def _seam_module(dotted: str) -> str:
    """`interface.contracts.x.Y` -> `interface.contracts.x`; the seam, not the symbol."""
    return ".".join(dotted.split(".")[:3])


def enumerate_c(root: str, artefact: dict) -> set[str]:
    """Channel C -- the envelope. Every module importing an `interface.contracts` seam.

    Walker-invisible to channels A and B by construction: `interface` is not under `WALL_DIRS`,
    and `tests/architecture/test_epistemic_wall_ratchet.py` asserts that on purpose. So the
    walker cannot tell "this crossing is envelope-borne" from "this crossing does not exist",
    and this enumerator is the only thing that can.
    """
    return {
        _entry(e.src, _seam_module(e.dst))
        for e in build_edges(root, CENSUS_DIRS)
        if e.dst.startswith(CONTRACTS_PREFIX)
    }


def _port_modules(root: str) -> set[str]:
    """Every `*_port` module under `tools/`, discovered from the FILESYSTEM.

    DISCOVERED FROM FILES, NOT FROM THE EDGE LIST, and the fixture is why: a port module that
    imports nothing produces no edge, so deriving the port set from the edges makes exactly the
    ports with no dependencies invisible -- a fail-open whose blind spot is the simplest port
    anyone could write. Found by `test_MUTATION_a_SIXTH_port_appearing_is_a_new_member`, which
    built one and got a clean bill of health from the first version of this function.
    """
    ports: set[str] = set()
    tools_root = os.path.join(root, "tools")
    for dirpath, _dirnames, filenames in os.walk(tools_root):
        rel = os.path.relpath(dirpath, root).replace(os.sep, ".")
        for fn in filenames:
            if fn.endswith("_port.py"):
                ports.add(f"{rel}.{fn[: -len('.py')]}")
    return ports


def _two_deep(dotted: str) -> str:
    parts = dotted.split(".")
    return ".".join(parts[:2]) if len(parts) >= 2 else dotted


def enumerate_d(root: str, artefact: dict) -> set[str]:
    """Channel D -- the same-step typed port and its importers.

    A port answers in the SAME call frame: no request object, no correlation id, no separation in
    time. That is the property C-S3 exists to prevent spreading, so the population that has it is
    worth a list. The ports are discovered from the tree (any `tools/*_port.py`), never from a
    hardcoded five, so a sixth port added tomorrow is a NEW member rather than an invisible one.
    """
    edges = build_edges(root, CENSUS_DIRS)
    ports = _port_modules(root)
    return {
        _entry(_two_deep(e.dst), e.src)
        for e in edges
        if _two_deep(e.dst) in ports and e.src not in ports
    }


def _protocol_base(node: ast.ClassDef) -> bool:
    for base in node.bases:
        if isinstance(base, ast.Name) and base.id == "Protocol":
            return True
        if isinstance(base, ast.Attribute) and base.attr == "Protocol":
            return True
    return False


def _business_py_files(root: str):
    for top in BUSINESS_DIRS:
        for dirpath, _dirnames, filenames in os.walk(os.path.join(root, top)):
            for fn in sorted(filenames):
                if fn.endswith(".py"):
                    path = os.path.join(dirpath, fn)
                    yield path, os.path.relpath(path, root).replace(os.sep, "/")


def _parse(path: str) -> ast.Module | None:
    try:
        with open(path, encoding="utf-8") as fh:
            return ast.parse(fh.read(), filename=path)
    except (SyntaxError, UnicodeDecodeError, OSError):
        return None


def enumerate_e(root: str, artefact: dict) -> set[str]:
    """Channel E -- the business-side structural Protocol.

    The census's own words: a structural crossing has nowhere to put a schema version, because the
    whole point of the pattern is that neither side declares the other. It is invisible to A and B
    (no import edge), to C (no envelope) and to D (no message object). A declared Protocol class is
    the one thing it does have a name for, so that is the unit. Superset by design -- see the
    module docstring.
    """
    found: set[str] = set()
    for path, rel in _business_py_files(root):
        tree = _parse(path)
        if tree is None:
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and _protocol_base(node):
                found.add(_entry(rel, node.name))
    return found


def _literal_key_reads(tree: ast.Module, keys: frozenset[str]) -> set[str]:
    """Keys this module accesses by literal: `d["k"]` or `d.get("k")`.

    Literal-only on purpose. A computed key (`d[name]`) is unresolvable statically and pretending
    otherwise would put a guess in a frozen list. The consequence is stated rather than hidden:
    this enumerator is a LOWER BOUND on channel F's readers.
    """
    hits: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Subscript):
            sl = node.slice
            if isinstance(sl, ast.Constant) and isinstance(sl.value, str) and sl.value in keys:
                hits.add(sl.value)
        elif (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and node.func.attr == "get"
            and node.args
        ):
            arg = node.args[0]
            if isinstance(arg, ast.Constant) and isinstance(arg.value, str) and arg.value in keys:
                hits.add(arg.value)
    return hits


def enumerate_f(root: str, artefact: dict) -> set[str]:
    """Channel F -- the published artefact. (top-level key, business-side reader).

    The widest channel and the one with no control at all before this module: 93 keys, and the
    business side is not merely a reader of them -- `company/billing/monthly_bill_assembly.py`
    WRITES `true_*` fields onto published bills, so a conformance control that only inspected
    reads would find nothing there. This one inspects access, not direction, for that reason.
    """
    keys = frozenset(artefact)
    if not keys:
        raise CensusUnavailable(
            "the run-output artefact has no top-level keys -- refusing to measure an empty "
            "denominator, because an empty denominator makes channel F vacuously conformant"
        )
    found: set[str] = set()
    for path, rel in _business_py_files(root):
        tree = _parse(path)
        if tree is None:
            continue
        for key in _literal_key_reads(tree, keys):
            found.add(_entry(key, rel))
    return found


# ── channel D's conformance: is the version actually ON THE WIRE? ────────────────────────────
# The enumerators above answer "who crosses on this channel". They cannot answer the question the
# 2026-08-15 census named as channel D's WHOLE conformance -- "they already own a version field,
# and putting it on the wire is the whole of their conformance". A port can declare
# `schema_version`, be counted by `enumerate_d`, and still emit it nowhere: for four days every
# live call site took the `include_schema_version=False` default and the field was structurally
# present and never populated. A count of importers is blind to that by construction, which is why
# this is a separate control and not a bigger enumerator.

#: The serialiser a port message crosses on, and the flag that puts the version in its output.
WIRE_METHOD = "to_log_entry"
WIRE_FLAG = "include_schema_version"


def _ports_declaring_the_flag(root: str) -> set[str]:
    """Port modules whose `to_log_entry` ACCEPTS the flag -- the subject this check is about.

    Read from each port's own AST rather than assumed, so a port that never had a version field is
    not reported as silent: it has nothing to say, which is a different fact from staying quiet.
    """
    declaring: set[str] = set()
    for dotted in _port_modules(root):
        tree = _parse(os.path.join(root, *dotted.split(".")) + ".py")
        if tree is None:
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == WIRE_METHOD:
                names = [a.arg for a in node.args.args + node.args.kwonlyargs]
                if WIRE_FLAG in names:
                    declaring.add(dotted)
    return declaring


def _census_py_files(root: str):
    """Every module the wall's own trees hold, as (path, repo-relative dotted-ish label)."""
    for top in CENSUS_DIRS:
        for dirpath, _dirnames, filenames in os.walk(os.path.join(root, top)):
            for fn in sorted(filenames):
                if fn.endswith(".py"):
                    path = os.path.join(dirpath, fn)
                    yield path, os.path.relpath(path, root).replace(os.sep, "/")


def _flag_is_true(call: ast.Call) -> bool:
    for kw in call.keywords:
        if kw.arg == WIRE_FLAG:
            return isinstance(kw.value, ast.Constant) and kw.value.value is True
    return False


def wire_call_sites(root: str) -> dict[str, bool]:
    """Every `<something>.to_log_entry(...)` OUTSIDE the port modules -> does it ask for the version.

    OUTSIDE THE PORTS ON PURPOSE. `tools/acquisition_funnel_port.py` calls `to_log_entry()` on its
    own nested `FunnelStageMessage` rows, whose serialiser takes no flag at all -- that is one
    message building itself, not a message leaving the process. Counting it would make the control
    permanently red for a reason its subject cannot fix.

    A LOWER BOUND, stated rather than hidden, and the same limit `_literal_key_reads` carries: the
    method is matched by NAME on an attribute call, so a port message serialised through an alias
    or a computed getattr is invisible here.
    """
    ports = _port_modules(root)
    sites: dict[str, bool] = {}
    for path, rel in _census_py_files(root):
        dotted = rel[: -len(".py")].replace("/", ".")
        if dotted in ports:
            continue
        tree = _parse(path)
        if tree is None:
            continue
        for node in ast.walk(tree):
            if (
                isinstance(node, ast.Call)
                and isinstance(node.func, ast.Attribute)
                and node.func.attr == WIRE_METHOD
            ):
                sites[_entry(rel, str(node.lineno))] = _flag_is_true(node)
    return sites


@dataclass(frozen=True)
class WireVerdict:
    """Channel D's wire conformance. `silent` is the failure -- a crossing that could carry the
    version and does not."""

    carrying: list[str]
    silent: list[str]

    @property
    def ok(self) -> bool:
        return not self.silent

    def report(self) -> str:
        if self.silent:
            return "\n".join(
                [f"SILENT on channel D ({len(self.silent)}) -- {WIRE_FLAG} not set:"]
                + [f"    ! {s}" for s in self.silent]
            )
        return f"channel D: all {len(self.carrying)} wire site(s) put the version on the wire."


def wire_conformance(root: str) -> WireVerdict:
    """THE CONTROL. Fails when a port message crosses without its version.

    THREE FAIL-CLOSED BRANCHES, because each is a different way this could go quiet:
      * ports exist but NONE declares the flag -- the subject has been deleted. Removing the
        parameter is the cheapest way to make this check pass, so it must be the loudest failure.
      * ports declare the flag and NOTHING calls the serialiser -- an empty denominator, which
        would make conformance vacuously true. Same doctrine as channel F's empty artefact.
      * no ports at all -- NOT refused. Channel D fully paid down is this atom's success case, and
        a control pinned to a non-zero count reds on its own success.
    """
    ports = _port_modules(root)
    if not ports:
        return WireVerdict(carrying=[], silent=[])
    declaring = _ports_declaring_the_flag(root)
    if not declaring:
        raise CensusUnavailable(
            f"{len(ports)} port module(s) exist and none declares `{WIRE_FLAG}` -- the subject of "
            "channel D's wire check has been removed, which is a failed check, not a pass"
        )
    sites = wire_call_sites(root)
    if not sites:
        raise CensusUnavailable(
            f"{len(declaring)} port(s) declare `{WIRE_FLAG}` and nothing calls `{WIRE_METHOD}` -- "
            "refusing to measure an empty denominator, which would make channel D vacuously "
            "conformant"
        )
    return WireVerdict(
        carrying=sorted(s for s, on in sites.items() if on),
        silent=sorted(s for s, on in sites.items() if not on),
    )


def wire_conformance_at(
    rev: str = "HEAD", worktree: bool = False, repo_root: Path = PROJECT_DIR
) -> WireVerdict:
    """`wire_conformance` against the worktree, or against the tree at `rev`.

    The worktree is the subject the commit gate uses, for `census_of_worktree`'s reason: a ratchet
    keyed to HEAD only reds AFTER the silent crossing has landed.
    """
    if worktree:
        return wire_conformance(str(repo_root))
    with head_export(str(repo_root), CENSUS_DIRS, rev=rev) as root:
        return wire_conformance(root)


def wire_on_artefact(artefact: dict) -> dict[str, tuple[int, int]]:
    """OBSERVATION, NEVER A GATE: {published key: (rows carrying a version, rows)}.

    This is the R11 half -- the code check above proves the call asks for the version, and only
    the artefact proves it arrived. It is deliberately NOT wired into the commit gate, because the
    artefact is regenerated by a SIM RUN: flipping the call sites cannot change a single row until
    the next run publishes, so a gate on this reds the very commit that repairs it and passes the
    one that broke it. Derived from the artefact's shape rather than a declared key list, so a
    fourth port's log is reported the day it appears instead of the day someone remembers it.
    """
    coverage: dict[str, tuple[int, int]] = {}
    for key, value in artefact.items():
        if isinstance(value, list) and value and all(isinstance(r, dict) for r in value):
            carrying = sum(1 for r in value if "schema_version" in r)
            coverage[key] = (carrying, len(value))
    return coverage


# ── the artefact half needs a SUBJECT, or its silence is unreadable ───────────────────────────
# `wire_on_artefact` above answers "how many rows of every published list carry a version". That
# is a reading of the whole artefact and it cannot state this atom's claim, because it does not
# know which of the 131 published keys are supposed to carry one. Both of the two facts it can
# report about `meter_read_log` -- "0 of 1600" and "not a port log at all" -- are the same number
# on that reading, and the CLI's own `if carrying:` filter then printed neither. At HEAD b22698df8
# that is not hypothetical: the three migrated logs carry the version on 0 of 1,996 rows and the
# report printed nothing, which reads exactly like a clean run
# (`WORKER_FINDING_THE_ARTEFACT_HIDES_IN_THE_OFF_STATE_2026-08-09`).
#
# So the subject is DERIVED, never declared: for each wire call site, the artefact key the rows it
# emits are published under, read out of the same module that emits them. A declared set of three
# keys would be the hardcoded-five this file's own docstring refuses -- a fourth port's log would
# be silent and unlisted on the same day.


def _wire_row_sinks(tree: ast.Module) -> dict[int, str]:
    """{line of a wire call -> the local name its emitted rows land in}.

    Two shapes, because the three live sites use both: `NAME = [... to_log_entry(...) ...]` and
    `NAME.append(<call>)`. A call landing in neither gets no entry here; `wire_publish_keys` walks
    the calls rather than these sinks, so such a site is reported UNRESOLVED rather than dropped.
    """
    sinks: dict[int, str] = {}
    for node in ast.walk(tree):
        calls = [
            n for n in ast.walk(node)
            if isinstance(n, ast.Call)
            and isinstance(n.func, ast.Attribute)
            and n.func.attr == WIRE_METHOD
        ]
        if not calls:
            continue
        name: str | None = None
        if (
            isinstance(node, ast.Assign)
            and len(node.targets) == 1
            and isinstance(node.targets[0], ast.Name)
        ):
            name = node.targets[0].id
        elif (
            isinstance(node, ast.Expr)
            and isinstance(node.value, ast.Call)
            and isinstance(node.value.func, ast.Attribute)
            and node.value.func.attr == "append"
            and isinstance(node.value.func.value, ast.Name)
        ):
            name = node.value.func.value.id
        if name is not None:
            for call in calls:
                sinks.setdefault(call.lineno, name)
    return sinks


def _published_names(tree: ast.Module) -> dict[str, str]:
    """{local name -> the string key a dict literal in this module publishes it under}.

    This is the step that makes the mapping a MEASUREMENT rather than an echo of the local name.
    A list assembled and never placed in a published dict resolves to nothing, which is the honest
    answer: those rows do not reach the artefact and no artefact reading can speak for them.
    """
    published: dict[str, str] = {}
    for node in ast.walk(tree):
        if not isinstance(node, ast.Dict):
            continue
        for key, value in zip(node.keys, node.values):
            if (
                isinstance(key, ast.Constant)
                and isinstance(key.value, str)
                and isinstance(value, ast.Name)
            ):
                published.setdefault(value.id, key.value)
    return published


def wire_publish_keys(root: str) -> dict[str, str | None]:
    """{wire call site -> the artefact key its rows are published under, or None}.

    Same site identifiers as `wire_call_sites`, so the two halves of channel D's conformance --
    "the call asks for the version" and "the version arrived in the bytes" -- are joined on one
    key and not on two independently-drifting notions of a site.
    """
    ports = _port_modules(root)
    resolved: dict[str, str | None] = {}
    for path, rel in _census_py_files(root):
        dotted = rel[: -len(".py")].replace("/", ".")
        if dotted in ports:
            continue
        tree = _parse(path)
        if tree is None:
            continue
        sinks = _wire_row_sinks(tree)
        published = _published_names(tree)
        # EVERY wire call in the file, not just the ones a sink was found for. Iterating the sinks
        # would make a site the sink rule does not recognise -- a bare `return [... ]`, the shape
        # the R15 fixture uses -- vanish from the subject rather than surface as UNRESOLVED, which
        # is the same exclusion-that-greens-the-verdict this half exists to refuse.
        for node in ast.walk(tree):
            if (
                isinstance(node, ast.Call)
                and isinstance(node.func, ast.Attribute)
                and node.func.attr == WIRE_METHOD
            ):
                name = sinks.get(node.lineno)
                resolved[_entry(rel, str(node.lineno))] = (
                    published.get(name) if name is not None else None
                )
    return resolved


@dataclass(frozen=True)
class ArtefactWireVerdict:
    """Did the version reach the BYTES, for the keys the wire sites actually publish.

    `silent` is the failure this exists for: a published log whose emitting call asks for the
    version and whose rows do not carry it. `unresolved` and `absent` are the two ways the
    question cannot be answered, kept separate from the answer `0` on purpose.
    """

    #: key -> (rows carrying a version, rows), every row carrying.
    carrying: dict[str, tuple[int, int]]
    #: key -> (rows carrying a version, rows), at least one row not carrying.
    silent: dict[str, tuple[int, int]]
    #: wire call sites whose published key could not be resolved from the tree.
    unresolved: list[str]
    #: resolved keys absent from the artefact, or present with no rows.
    absent: list[str]

    @property
    def ok(self) -> bool:
        return not self.silent and not self.unresolved and not self.absent

    def report(self) -> str:
        lines: list[str] = []
        for key, (carrying, rows) in sorted(self.silent.items()):
            lines.append(f"    ! artefact {key:<28} {carrying}/{rows} row(s) carry a version")
        for site in self.unresolved:
            lines.append(f"    ? {site} -- emits rows this tree does not publish under any key")
        for key in self.absent:
            lines.append(f"    ? artefact {key} -- no rows to read, so the wire is unobservable")
        for key, (carrying, rows) in sorted(self.carrying.items()):
            lines.append(f"      artefact {key:<28} {carrying}/{rows} row(s) carry a version")
        head = (
            f"channel D on the artefact: {len(self.carrying)} log(s) carry the version on every row"
            if self.ok
            else f"channel D on the artefact: {len(self.silent)} silent, "
            f"{len(self.unresolved)} unresolved, {len(self.absent)} unobservable"
        )
        return "\n".join([head] + lines)


def artefact_wire_conformance(root: str, artefact: dict) -> ArtefactWireVerdict:
    """THE R11 HALF, with its subject. Reads bytes; the code half reads program text.

    INDEPENDENCE (R15's first killer): the key set comes from the TREE and the row counts come
    from the ARTEFACT, which is a publisher's output from a past sim run. Neither side is derived
    from the other, so this cannot agree with `wire_conformance` by construction -- and at HEAD
    b22698df8 it does not: the code half is green on all three sites and this half is silent on
    all three logs, which is the true state of a migration that has not been published yet.

    FAIL-CLOSED. Wire sites exist and none resolves to a published key -> `CensusUnavailable`:
    that is the mapping having been removed, not conformance. No wire sites at all is NOT refused,
    for `wire_conformance`'s reason -- channel D fully paid down is this atom's success case.

    STILL NOT A GATE, and the reason is narrower than "it is an observation". The artefact is
    regenerated by a sim run, so the commit that repairs a silent log cannot move a row until the
    next run publishes; gating would red the repair and pass the breakage. Closing that needs the
    artefact to say WHICH CODE PRODUCED IT, which it does not
    (`WORKER_FINDING_THE_PUBLISHED_ARTEFACT_CARRIES_NO_PRODUCTION_STAMP_2026-08-15`). Named here so
    the condition for promoting this to a gate is on the record rather than rediscovered.
    """
    sites = wire_publish_keys(root)
    if not sites:
        return ArtefactWireVerdict(carrying={}, silent={}, unresolved=[], absent=[])
    unresolved = sorted(site for site, key in sites.items() if key is None)
    keys = {key for key in sites.values() if key is not None}
    if not keys:
        raise CensusUnavailable(
            f"{len(sites)} wire call site(s) exist and none resolves to a published artefact key "
            "-- refusing to report an empty subject, which would make the artefact half "
            "vacuously conformant"
        )
    coverage = wire_on_artefact(artefact)
    carrying: dict[str, tuple[int, int]] = {}
    silent: dict[str, tuple[int, int]] = {}
    absent: list[str] = []
    for key in sorted(keys):
        if key not in coverage:
            absent.append(key)
            continue
        rows_carrying, rows = coverage[key]
        (carrying if rows_carrying == rows else silent)[key] = (rows_carrying, rows)
    return ArtefactWireVerdict(
        carrying=carrying, silent=silent, unresolved=unresolved, absent=absent
    )


def artefact_wire_conformance_at(
    rev: str = "HEAD", worktree: bool = False, repo_root: Path = PROJECT_DIR
) -> ArtefactWireVerdict:
    """ONE REF, BOTH SIDES -- the tree and the artefact are read from the same `rev`.

    Reading the key mapping from the worktree against an artefact committed at HEAD would compare
    a migration that has landed against bytes published before it and report a difference that is
    nobody's defect (`feedback_a_two_sided_census_must_read_both_sides_from_one_ref`). The
    `worktree` branch therefore takes the artefact from the worktree too.
    """
    if worktree:
        artefact_path = repo_root / ARTEFACT_REL
        try:
            artefact = json.loads(artefact_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise CensusUnavailable(f"{ARTEFACT_REL} is unreadable in the worktree: {exc}") from exc
        if not isinstance(artefact, dict):
            raise CensusUnavailable(f"{ARTEFACT_REL} in the worktree is not an object")
        return artefact_wire_conformance(str(repo_root), artefact)
    with head_export(str(repo_root), CENSUS_DIRS, rev=rev) as root:
        return artefact_wire_conformance(root, artefact_at(rev, repo_root=repo_root))


# ── can a cold reader tell a STALE ARTEFACT from a BROKEN WIRE? ──────────────────────────────
#
# WHY (2026-08-20, this atom's own named next move -- the Expert Hour on channel D, run as a
# cold-eyes walk against the REPORT rather than the code). The two halves above print, at HEAD:
#
#     channel D: all 3 wire site(s) put the version on the wire.
#     channel D on the artefact: 3 silent, 0 unresolved, 0 unobservable
#         ! artefact meter_read_log            0/1600 row(s) carry a version
#
# A reader who has never seen this atom cannot read that. The code half is green, the artefact
# half is zero on every row, and the two facts contradict each other on their face. The `!` says
# defect. The true state is a migration that has landed and has not been published yet -- and
# NOTHING IN THE OUTPUT SAYS SO. Pass 17 called the disagreement evidence that the halves are
# independent, which it is; what it did not notice is that the same disagreement is what a broken
# wire looks like, so the report cannot tell its success case from its failure case.
#
# WHAT CAN HONESTLY BE SAID, given the artefact carries no production stamp
# (`WORKER_FINDING_THE_PUBLISHED_ARTEFACT_CARRIES_NO_PRODUCTION_STAMP_2026-08-15`, still open).
# Not "this artefact was produced by this code" -- that is the stamp, and inventing a proxy for it
# is exactly the fabrication that finding refuses. What IS derivable, from git alone and at the
# same rev both halves already use, is a BOUND: the commit that last touched the artefact, and the
# commit that last touched each module whose call sites emit its rows. If the artefact's commit is
# a strict ancestor of a producer's, the artefact PREDATES the code that would have put the version
# in it, and silence is unreadable rather than damning. If it is not older than any producer, then
# staleness-by-commit-order is no longer available as an excuse and a silent log is a real defect.
#
# THE ASYMMETRY IS DELIBERATE AND IS THE HONEST HALF. "Older than a producer" is a SUFFICIENT
# explanation of silence. "Not older than any producer" is NOT a production stamp and must never be
# printed as one: a publisher process running code from before the migration can commit fresh bytes
# at any time (R2 -- committed is not running). So this narrows the reading from "unknown" to
# "unexplained"; it does not close the finding, and the report says which of the two it is saying.
#
# THE SUBJECT IS DERIVED, never declared, for pass 17's reason: the producers come from the wire
# call sites themselves, so a fourth port emitting from a fourth module is dated on the day it
# lands rather than silently omitted from a hardcoded list of three.

def producer_paths_of(root: str) -> list[str]:
    """The modules that emit the wire's rows, read out of the wire call sites themselves."""
    return sorted({site.split(" -> ")[0] for site in wire_publish_keys(root)})


def _last_commit_touching(rel: str, rev: str, repo_root: Path) -> str | None:
    """The commit at or before `rev` that last changed `rel`, or None if git cannot say.

    None is UNDETERMINED, never "unchanged" -- every caller routes it to the undetermined list.
    """
    try:
        proc = subprocess.run(
            ["git", "-C", str(repo_root), "rev-list", "-1", rev, "--", rel],
            capture_output=True, text=True, check=False,
        )
    except OSError:
        return None
    if proc.returncode != 0:
        return None
    return proc.stdout.strip() or None


def _strictly_precedes(earlier: str, later: str, repo_root: Path) -> bool | None:
    """Is `earlier` a STRICT ancestor of `later`? None when the two cannot be ordered.

    Topology, not timestamps: a commit date is metadata a rebase rewrites, and two commits made a
    second apart can land in either order. Divergent commits return None rather than False,
    because "no ancestry either way" is not "the artefact is current".
    """
    if earlier == later:
        return False
    try:
        forward = subprocess.run(
            ["git", "-C", str(repo_root), "merge-base", "--is-ancestor", earlier, later],
            capture_output=True, text=True, check=False,
        )
        backward = subprocess.run(
            ["git", "-C", str(repo_root), "merge-base", "--is-ancestor", later, earlier],
            capture_output=True, text=True, check=False,
        )
    except OSError:
        return None
    if forward.returncode == 0:
        return True
    if backward.returncode == 0:
        return False
    # rc 1 both ways is a genuine fork; anything else is git failing to answer. Neither is False.
    return None


@dataclass(frozen=True)
class ArtefactProvenance:
    """Where the artefact sits in commit order relative to the code that produces its rows."""

    #: the commit that last touched the artefact, or None when git could not say.
    artefact_commit: str | None
    #: producer module -> the commit that last touched it, or None when git could not say.
    producers: dict[str, str | None]
    #: producers that landed AFTER the artefact -- the artefact cannot contain their output.
    predates: list[str]
    #: producers whose order against the artefact could not be established.
    undetermined: list[str]
    #: set when nothing could be established at all, and printed instead of a verdict.
    reason: str | None = None

    @property
    def staleness_explains_silence(self) -> bool:
        """Is a silent log above accounted for by the artefact being older than its code?"""
        return bool(self.predates)

    @property
    def determined(self) -> bool:
        """Every producer ordered against a known artefact commit, and at least one producer."""
        return (
            self.artefact_commit is not None
            and bool(self.producers)
            and not self.undetermined
        )

    def report(self) -> str:
        if not self.producers:
            return (
                "    channel D has no wire site, so the artefact has no producer to be dated "
                f"against{f' ({self.reason})' if self.reason else ''}"
            )
        lines: list[str] = []
        if self.predates:
            named = ", ".join(
                f"{path}@{(self.producers.get(path) or '?')[:9]}" for path in self.predates
            )
            lines.append(
                f"    the artefact PREDATES {len(self.predates)} of {len(self.producers)} "
                f"producer(s): {named}"
            )
            lines.append(
                "      -> a silent log above is STALE BYTES, not evidence of a broken wire: "
                "these bytes were published before that code existed."
            )
        if self.undetermined:
            lines.append(
                f"    ? provenance UNDETERMINED against {len(self.undetermined)} producer(s): "
                + ", ".join(self.undetermined)
            )
            lines.append(
                "      -> silence above cannot be read either way"
                + (f" ({self.reason})" if self.reason else "")
            )
        if not lines:
            lines.append(
                f"    the artefact is no older than any of its {len(self.producers)} producer(s)"
            )
            lines.append(
                "      -> a silent log above is NOT explained by staleness. This is a "
                "COMMIT-ORDER bound and NOT a production stamp: a publisher still running "
                "pre-migration code can commit fresh bytes at any time (R2)."
            )
        return "\n".join(lines)


def artefact_provenance(
    producer_paths: list[str], rev: str = "HEAD", repo_root: Path = PROJECT_DIR
) -> ArtefactProvenance:
    """Order the artefact against the modules that emit its rows. Never asserts production."""
    producers: dict[str, str | None] = {
        path: _last_commit_touching(path, rev, repo_root) for path in producer_paths
    }
    if not producers:
        return ArtefactProvenance(
            artefact_commit=None, producers={}, predates=[], undetermined=[],
            reason="no wire call sites in this tree",
        )
    artefact_commit = _last_commit_touching(ARTEFACT_REL, rev, repo_root)
    if artefact_commit is None:
        return ArtefactProvenance(
            artefact_commit=None, producers=producers, predates=[],
            undetermined=sorted(producers),
            reason=f"no commit at {rev} touches {ARTEFACT_REL}",
        )
    predates: list[str] = []
    undetermined: list[str] = []
    for path in sorted(producers):
        commit = producers[path]
        if commit is None:
            undetermined.append(path)
            continue
        order = _strictly_precedes(artefact_commit, commit, repo_root)
        if order is None:
            undetermined.append(path)
        elif order:
            predates.append(path)
    return ArtefactProvenance(
        artefact_commit=artefact_commit, producers=producers,
        predates=predates, undetermined=undetermined,
        reason="a producer's history is unreadable at this rev" if undetermined else None,
    )


def artefact_provenance_at(
    rev: str = "HEAD", worktree: bool = False, repo_root: Path = PROJECT_DIR
) -> ArtefactProvenance:
    """The provenance reading for the same subject the artefact half measured.

    WORKTREE MODE IS UNDETERMINED BY CONSTRUCTION when the artefact is dirty, and says so rather
    than dating uncommitted bytes against the commit that last touched their path -- that
    comparison would be a lie in the reassuring direction on every tree with a daemon running.
    """
    if worktree:
        producer_paths = producer_paths_of(str(repo_root))
        try:
            dirty = subprocess.run(
                ["git", "-C", str(repo_root), "status", "--porcelain", "--", ARTEFACT_REL],
                capture_output=True, text=True, check=False,
            )
        except OSError as exc:
            raise CensusUnavailable(f"could not run git status: {exc}") from exc
        if dirty.returncode != 0:
            raise CensusUnavailable(f"git status failed on {ARTEFACT_REL}: {dirty.stderr.strip()}")
        if dirty.stdout.strip():
            return ArtefactProvenance(
                artefact_commit=None,
                producers={path: None for path in producer_paths},
                predates=[], undetermined=sorted(producer_paths),
                reason=f"{ARTEFACT_REL} is uncommitted in the worktree, so it has no commit order",
            )
        return artefact_provenance(producer_paths, rev=rev, repo_root=repo_root)
    with head_export(str(repo_root), CENSUS_DIRS, rev=rev) as root:
        producer_paths = producer_paths_of(root)
    return artefact_provenance(producer_paths, rev=rev, repo_root=repo_root)


# ── channel C's conformance: does the envelope crossing GO THROUGH A WIRE? ───────────────────
# THE SECOND CHANNEL TO OWN A CONFORMANCE QUESTION, and this atom's own named next move: L3 is the
# per-channel conformance shape, and one channel with a conformance question is a sample of one.
#
# WHY THIS QUESTION AND NOT "DOES IT CARRY A VERSION". `WallRequest`/`WallResponse` declare
# `schema_version` as a REQUIRED field, so "an envelope crossing carries a version" is true by
# dataclass construction and asking it would be R15 TAUTOLOGY -- a control whose checked value is
# guaranteed by the same definition it checks. The field being structurally present is PRECISELY
# what makes an in-process crossing look conformant: a `WallResponse` handed to the far side as a
# Python object has a `schema_version` attribute that is never serialised, never decoded, never
# version-checked, and no reader ever had the chance to refuse it. Channel D's question --
# "is the version actually ON THE WIRE" -- asked of the envelope channel is therefore: does this
# seam's envelope get ENCODED into the declared wire form by one side and DECODED back by the
# other, or does the object simply cross the call frame?
#
# THE TWO SIDES ARE DETECTED DIFFERENTLY, and the asymmetry is the design's, not a shortcut. The
# counterparty writes its own bytes on purpose (`simulation/payment_seam_adapter.py`'s own comment:
# a mock that encoded with the company's codec would make the round-trip a tautology, and it may
# not import `company.*` at all), so there is no shared encoder to look for -- an ENCODE site is
# recognised by the SHAPE it emits. The company has exactly one codec, so a DECODE site is
# recognised by importing it.
#
# THE FIELD SETS ARE READ FROM `wall_protocol`'S OWN CONSTANTS, never restated here. That module
# already declares `REQUEST_WIRE_FIELDS`/`RESPONSE_WIRE_FIELDS` as the exact key set of a message,
# so a field added to the envelope moves the encoder's target and this control with it. A copy of
# the key set in this file would agree with itself forever.

#: The company's sole codec -- the module a decode site is recognised by importing.
CODEC_MODULE = "company.interfaces.wall_protocol"

#: The decoding entry points. Encoders are matched by emitted shape, not by name: see above.
DECODE_NAMES: frozenset[str] = frozenset({"decode_request", "decode_response"})

#: Where the wire field sets are DECLARED. Read from the tree under measurement, not imported, so
#: the check reads the same rev everything else in this module does (a two-sided census must read
#: both sides from one ref).
CODEC_REL = "company/interfaces/wall_protocol.py"
WIRE_FIELD_CONSTANTS: tuple[str, ...] = ("REQUEST_WIRE_FIELDS", "RESPONSE_WIRE_FIELDS")

#: The per-seam version constant. A seam that declares none has no version to put on a wire, which
#: is a different fact from staying quiet -- same discipline as `_ports_declaring_the_flag`.
SEAM_VERSION_CONSTANT = "SCHEMA_VERSION"


def _frozenset_literal_fields(tree: ast.Module, name: str) -> frozenset[str] | None:
    """The string members of a module-level `NAME: ... = frozenset({...})`, or None."""
    for node in tree.body:
        targets = (
            [node.target] if isinstance(node, ast.AnnAssign)
            else node.targets if isinstance(node, ast.Assign)
            else []
        )
        if not any(isinstance(t, ast.Name) and t.id == name for t in targets):
            continue
        value = node.value
        if isinstance(value, ast.Call) and value.args:
            value = value.args[0]
        if isinstance(value, (ast.Set, ast.List, ast.Tuple)):
            members = [e.value for e in value.elts if isinstance(e, ast.Constant)]
            if len(members) == len(value.elts) and all(isinstance(m, str) for m in members):
                return frozenset(members)
    return None


def wire_field_sets(root: str) -> list[frozenset[str]]:
    """The declared key set of a request and of a response, read from the codec's own source.

    FAIL-CLOSED (R15 FAIL-SILENT): an unreadable codec, a missing constant or a constant that is
    not a literal set of strings raises. Every one of those makes the encoder-shape match
    impossible to compute, and a shape match that can never fire would report every seam
    in-process -- loud, but for the wrong reason, and it would then be tuned away.
    """
    tree = _parse(os.path.join(root, *CODEC_REL.split("/")))
    if tree is None:
        raise CensusUnavailable(
            f"{CODEC_REL} is unreadable, so channel C's wire shapes cannot be read -- an "
            "unavailable check is a FAILED check"
        )
    sets: list[frozenset[str]] = []
    for name in WIRE_FIELD_CONSTANTS:
        fields = _frozenset_literal_fields(tree, name)
        if not fields:
            raise CensusUnavailable(
                f"{CODEC_REL} declares no literal `{name}` -- channel C's wire form is undefined, "
                "which is a failed check, not a pass"
            )
        sets.append(fields)
    return sets


def envelope_seams(root: str) -> set[str]:
    """Channel C's seams -- the DESTINATIONS of its members, derived from the enumerator.

    DERIVED, NOT LISTED, for `_port_modules`' reason: a fourth seam added tomorrow owns a wire
    question on the day it lands rather than on the day someone remembers to name it here. The
    subject is the seam and not the importer because the transport is a property of the crossing:
    six modules importing one in-process seam are one unwired crossing, not six.
    """
    return {m.split(" -> ", 1)[1] for m in enumerate_c(root, {})}


def _seam_version(root: str, seam: str) -> int | str | None:
    """The `SCHEMA_VERSION` a seam declares, or None if it declares none."""
    tree = _parse(os.path.join(root, *seam.split(".")) + ".py")
    if tree is None:
        return None
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(
            isinstance(t, ast.Name) and t.id == SEAM_VERSION_CONSTANT for t in node.targets
        ):
            if isinstance(node.value, ast.Constant):
                return node.value.value
    return None


def _module_imports(root: str) -> dict[str, set[str]]:
    """{importer -> the modules it imports}, from the census edge list."""
    imports: dict[str, set[str]] = {}
    for e in build_edges(root, CENSUS_DIRS):
        imports.setdefault(e.src, set()).add(e.dst)
    return imports


def _emits_a_wire_shape(tree: ast.Module, shapes: list[frozenset[str]]) -> bool:
    """Does this module build a dict literal whose key set is EXACTLY a declared wire form?

    EXACTLY, never a superset: `absence is never agreement` is the envelope's own rule, so a dict
    carrying six of seven keys is a message the far side must refuse, not a lenient pass here. A
    computed or **-spread key set is invisible to this and the limit is stated rather than hidden
    -- the same lower-bound caveat `wire_call_sites` carries.
    """
    for node in ast.walk(tree):
        if not isinstance(node, ast.Dict):
            continue
        keys = [k.value for k in node.keys if isinstance(k, ast.Constant)]
        if len(keys) != len(node.keys) or not all(isinstance(k, str) for k in keys):
            continue
        if frozenset(keys) in shapes:
            return True
    return False


def envelope_transport(root: str) -> dict[str, tuple[set[str], set[str]]]:
    """{seam -> (modules that ENCODE its envelopes, modules that DECODE them)}.

    A module counts for a seam only if it IMPORTS that seam, which is what ties a wire form to the
    crossing it belongs to: the codec module itself encodes and decodes the generic envelope and
    imports no payload seam, so it is nobody's transport and is never credited as one.
    """
    shapes = wire_field_sets(root)
    seams = envelope_seams(root)
    imports = _module_imports(root)
    transport: dict[str, tuple[set[str], set[str]]] = {s: (set(), set()) for s in seams}
    for path, rel in _census_py_files(root):
        dotted = rel[: -len(".py")].replace("/", ".")
        crossed = seams & imports.get(dotted, set())
        if not crossed:
            continue
        tree = _parse(path)
        if tree is None:
            continue
        encodes = _emits_a_wire_shape(tree, shapes)
        decodes = CODEC_MODULE in imports.get(dotted, set()) and any(
            isinstance(n, ast.ImportFrom)
            and n.module == CODEC_MODULE
            and any(a.name in DECODE_NAMES for a in n.names)
            for n in ast.walk(tree)
        )
        for seam in crossed:
            if encodes:
                transport[seam][0].add(dotted)
            if decodes:
                transport[seam][1].add(dotted)
    return transport


@dataclass(frozen=True)
class EnvelopeWireVerdict:
    """Channel C's conformance, in four populations -- the same shape the artefact half uses.

    FOUR AND NOT TWO, because "not wire-borne" hides three different repairs:
      * `in_process`  -- neither side. The envelope crosses as a Python object and its version is
        a field nobody reads. This is the defect the atom exists to close.
      * `half_wired`  -- one side only. A version put on the wire that nothing version-checks, or
        a decoder with no producer: strictly worse than in-process, because it LOOKS transported.
      * `unversioned` -- a channel C seam declaring no `SCHEMA_VERSION`. It has nothing to put on
        a wire, so it is reported rather than counted as a failure or silently dropped. The
        envelope module itself is the honest member: it defines the shape, it is not a crossing.
    """

    wire_borne: list[str]
    half_wired: list[tuple[str, str]]
    in_process: list[str]
    unversioned: list[str]

    @property
    def ok(self) -> bool:
        return not self.in_process and not self.half_wired

    def report(self) -> str:
        lines = [
            f"channel C: {len(self.wire_borne)} of "
            f"{len(self.wire_borne) + len(self.half_wired) + len(self.in_process)} "
            "versioned seam(s) cross on a wire"
        ]
        lines += [f"    * {s} -- encoded and decoded" for s in self.wire_borne]
        lines += [f"    ! {s} -- {half} ONLY: transported on one side" for s, half in self.half_wired]
        lines += [
            f"    ! {s} -- IN-PROCESS: the envelope object crosses the call frame, so its "
            "schema_version is never encoded, never decoded and never refused"
            for s in self.in_process
        ]
        lines += [
            f"    - {s} -- declares no {SEAM_VERSION_CONSTANT}, so it has no version to carry"
            for s in self.unversioned
        ]
        return "\n".join(lines)


def envelope_wire_conformance(root: str) -> EnvelopeWireVerdict:
    """THE CONTROL. Fails when an envelope crossing never becomes a message.

    FAIL-CLOSED, and each branch is a different way this could go quiet:
      * the codec's wire field sets unreadable -> raises (`wire_field_sets`).
      * seams exist and NONE declares a version -> the subject has been removed. Deleting the
        version constants is the cheapest way to make this pass, so it is the loudest failure.
      * NO channel C members at all -> NOT refused. A fully paid-down envelope channel is a
        legitimate reading and a control pinned to a non-zero count reds on its own success case.
    """
    seams = envelope_seams(root)
    if not seams:
        return EnvelopeWireVerdict(wire_borne=[], half_wired=[], in_process=[], unversioned=[])
    unversioned = sorted(s for s in seams if _seam_version(root, s) is None)
    versioned = seams - set(unversioned)
    if not versioned:
        raise CensusUnavailable(
            f"{len(seams)} channel C seam(s) exist and none declares `{SEAM_VERSION_CONSTANT}` -- "
            "the subject of channel C's wire check has been removed, which is a failed check"
        )
    transport = envelope_transport(root)
    wire_borne, half_wired, in_process = [], [], []
    for seam in sorted(versioned):
        encoders, decoders = transport[seam]
        if encoders and decoders:
            wire_borne.append(seam)
        elif encoders:
            half_wired.append((seam, "ENCODED"))
        elif decoders:
            half_wired.append((seam, "DECODED"))
        else:
            in_process.append(seam)
    return EnvelopeWireVerdict(
        wire_borne=wire_borne, half_wired=half_wired,
        in_process=in_process, unversioned=unversioned,
    )


def envelope_wire_conformance_at(
    rev: str = "HEAD", worktree: bool = False, repo_root: Path = PROJECT_DIR
) -> EnvelopeWireVerdict:
    """`envelope_wire_conformance` against the worktree, or against the tree at `rev`."""
    if worktree:
        return envelope_wire_conformance(str(repo_root))
    with head_export(str(repo_root), CENSUS_DIRS, rev=rev) as root:
        return envelope_wire_conformance(root)


ENUMERATORS = {
    "A_direct_import": enumerate_a,
    "B_indirect_import": enumerate_b,
    "C_envelope": enumerate_c,
    "D_typed_port": enumerate_d,
    "E_structural_protocol": enumerate_e,
    "F_published_artefact": enumerate_f,
}


def channels_without_an_enumerator() -> list[str]:
    """THE EXIT CRITERION ITSELF, as a function.

    A channel named in `CHANNELS` with no callable in `ENUMERATORS` is a channel nothing can see.
    This is what the atom's L3 criterion asks, and a test asserts it is empty.
    """
    return [c.id for c in CHANNELS if not callable(ENUMERATORS.get(c.id))]


# ── taking the census ────────────────────────────────────────────────────────────────────────

def census(root: str, artefact: dict) -> dict[str, set[str]]:
    """Run every enumerator against one tree and one artefact. Raises rather than skipping."""
    missing = channels_without_an_enumerator()
    if missing:
        raise CensusUnavailable(f"channels with no enumerator: {missing}")
    return {cid: ENUMERATORS[cid](root, artefact) for cid in CHANNEL_IDS}


def artefact_at(rev: str, repo_root: Path = PROJECT_DIR) -> dict:
    """The published artefact AS `rev` CONTAINS IT -- the same tree the readers come from."""
    try:
        proc = subprocess.run(
            ["git", "-C", str(repo_root), "show", f"{rev}:{ARTEFACT_REL}"],
            capture_output=True, text=True, check=False,
        )
    except OSError as exc:
        raise CensusUnavailable(f"could not run git show: {exc}") from exc
    if proc.returncode != 0:
        raise CensusUnavailable(
            f"{ARTEFACT_REL} is not readable at {rev} (rc {proc.returncode}): "
            f"{proc.stderr.strip()}"
        )
    try:
        loaded = json.loads(proc.stdout)
    except json.JSONDecodeError as exc:
        raise CensusUnavailable(f"{ARTEFACT_REL} at {rev} is not valid JSON: {exc}") from exc
    if not isinstance(loaded, dict):
        raise CensusUnavailable(f"{ARTEFACT_REL} at {rev} is not an object")
    return loaded


def census_at(rev: str = "HEAD", repo_root: Path = PROJECT_DIR) -> dict[str, set[str]]:
    """The census of the tree at `rev`. Both sides of channel F come from that one rev."""
    artefact = artefact_at(rev, repo_root)
    with head_export(str(repo_root), CENSUS_DIRS, rev=rev) as root:
        return census(root, artefact)


def census_of_worktree(repo_root: Path = PROJECT_DIR, rev: str = "HEAD") -> dict[str, set[str]]:
    """The tree under your feet -- the reading the enforced check uses.

    THE WORKING TREE IS THE SUBJECT ON PURPOSE, the same call and the same reason as
    `epistemic_wall.live_crossings()`: a ratchet whose subject is HEAD only reds AFTER the new
    crossing has landed, and the point of a shrink-only list is to red BEFORE.

    CHANNEL F'S DENOMINATOR STILL COMES FROM `rev`, NOT FROM THE FILE ON DISK, and this is the one
    place the two-sided-census rule is deliberately traded off rather than followed:
      * `docs/reports/run_output_latest.json` is a PUBLISHER'S OUTPUT. Daemons rewrite it on this
        shared tree while tests run, so a check keyed to the file on disk is red for reasons its
        subject cannot fix -- and a control that only fails for unfixable reasons is disabled
        within a week. The committed copy is stable and reproducible.
      * What that costs, stated exactly: a key that is BRAND NEW in the uncommitted artefact and
        already read by a literal in the tree is invisible until the artefact commits. It is then
        caught on the next run. The reader side -- which is the side that changes when someone
        widens the channel -- is measured live and is never lagged.
    """
    return census(str(repo_root), artefact_at(rev, repo_root))


# ── the shrink-only list ─────────────────────────────────────────────────────────────────────

def load_baseline(path: Path = BASELINE_PATH) -> dict[str, set[str]]:
    """The frozen list. Unreadable or missing a frozen channel is a FAILED check, not a pass."""
    try:
        with open(path, encoding="utf-8") as fh:
            raw = json.load(fh)
    except (OSError, json.JSONDecodeError) as exc:
        raise CensusUnavailable(f"baseline {path} is unreadable: {exc}") from exc
    frozen = raw.get("frozen")
    if not isinstance(frozen, dict):
        raise CensusUnavailable(f"baseline {path} has no `frozen` object")
    missing = [cid for cid in FROZEN_CHANNEL_IDS if cid not in frozen]
    if missing:
        raise CensusUnavailable(f"baseline {path} is missing frozen channels: {missing}")
    return {cid: set(frozen[cid]) for cid in FROZEN_CHANNEL_IDS}


@dataclass(frozen=True)
class Verdict:
    """What the ratchet found. `new` is the failure; `gone` is the success it must tolerate."""

    new: dict[str, list[str]]
    gone: dict[str, list[str]]

    @property
    def ok(self) -> bool:
        return not any(self.new.values())

    def report(self) -> str:
        lines: list[str] = []
        for cid in FROZEN_CHANNEL_IDS:
            added, removed = self.new.get(cid, []), self.gone.get(cid, [])
            if added:
                lines.append(f"NEW on channel {cid} ({len(added)}) -- not in the frozen list:")
                lines.extend(f"    + {m}" for m in added)
            if removed:
                lines.append(f"paid down on {cid} ({len(removed)}) -- re-freeze to record:")
                lines.extend(f"    - {m}" for m in removed)
        return "\n".join(lines) or "every frozen channel matches its list exactly."


def check(current: dict[str, set[str]], baseline: dict[str, set[str]]) -> Verdict:
    """Compare a census against the frozen list. Growth fails; shrink is recorded and passes."""
    new, gone = {}, {}
    for cid in FROZEN_CHANNEL_IDS:
        have, frozen = current.get(cid, set()), baseline.get(cid, set())
        new[cid] = sorted(have - frozen)
        gone[cid] = sorted(frozen - have)
    return Verdict(new=new, gone=gone)


def freeze_payload(current: dict[str, set[str]], rev: str) -> dict:
    return {
        "_meta": {
            "title": "The wall's per-channel census -- shrink-only list",
            "atom": "EP6_wall_protocol_typing",
            "tool": "tools/wall_channel_census.py",
            "census": "docs/design/EP6_WALL_CONFORMANCE_CENSUS_DISCOVER.md",
            "frozen_at_rev": rev,
            "rule": (
                "A member present here and absent from the tree is PAID DOWN -- re-freeze to "
                "record it. A member in the tree and absent here is NEW and fails the check. "
                "Channels A and B are reported by the tool and enforced by "
                "docs/design/WALL_CROSSING_DISPOSITION_REGISTER.md, not frozen here."
            ),
        },
        "reported_not_frozen": {
            cid: sorted(current[cid]) for cid in CHANNEL_IDS if cid not in FROZEN_CHANNEL_IDS
        },
        "frozen": {cid: sorted(current[cid]) for cid in FROZEN_CHANNEL_IDS},
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[5])
    ap.add_argument("--freeze", action="store_true", help="rewrite the baseline from the tree")
    ap.add_argument("--worktree", action="store_true", help="measure the worktree, not a commit")
    ap.add_argument("--rev", default="HEAD", help="the rev to measure (default HEAD)")
    args = ap.parse_args(argv)

    try:
        current = (
            census_of_worktree() if args.worktree else census_at(args.rev)
        )
    except CensusUnavailable as exc:
        print(f"CENSUS UNAVAILABLE (a failed check, not a pass): {exc}", file=sys.stderr)
        return 2

    for cid in CHANNEL_IDS:
        print(f"  {cid:<24} {len(current[cid]):>4} member(s)")

    if args.freeze:
        rev = "worktree" if args.worktree else args.rev
        BASELINE_PATH.write_text(
            json.dumps(freeze_payload(current, rev), indent=2) + "\n", encoding="utf-8"
        )
        print(f"froze {BASELINE_PATH.relative_to(PROJECT_DIR)} at {rev}")
        return 0

    try:
        wire = wire_conformance_at(rev=args.rev, worktree=args.worktree)
    except CensusUnavailable as exc:
        print(f"WIRE CHECK UNAVAILABLE (a failed check, not a pass): {exc}", file=sys.stderr)
        return 2
    print(wire.report())

    # CHANNEL C REPORTS AND DOES NOT GATE, and the condition for that changing is stated so the
    # next pass does not have to re-derive it: two of the three versioned seams are in-process at
    # HEAD, so gating here would refuse EVERY commit in the repo including the ones that repair it
    # -- pass 13's landing-order defect, which this file has already learned once. It becomes a
    # gate in the same commit that makes it satisfiable, which is the only commit in which
    # restoring it is honest.
    try:
        envelope_wire = envelope_wire_conformance_at(rev=args.rev, worktree=args.worktree)
    except CensusUnavailable as exc:
        print(
            f"CHANNEL C WIRE CHECK UNAVAILABLE (a failed check, not a pass): {exc}", file=sys.stderr
        )
        return 2
    print(envelope_wire.report())

    # The artefact half prints its SILENT and UNOBSERVABLE keys as loudly as its carrying ones.
    # The `if carrying:` filter this replaces suppressed exactly the state the check exists to
    # find: at HEAD b22698df8, three logs at 0/1,996 printed as an empty section.
    try:
        artefact_wire = artefact_wire_conformance_at(rev=args.rev, worktree=args.worktree)
    except CensusUnavailable as exc:
        print(
            f"ARTEFACT WIRE CHECK UNAVAILABLE (a failed check, not a pass): {exc}", file=sys.stderr
        )
        return 2
    print(artefact_wire.report())

    # Silence above is unreadable without this line -- it is what tells a stale artefact from a
    # broken wire, and the CLI is where a cold reader meets the number, so it prints here and not
    # in a report nobody runs. Printed on the green case too: "no older than its producers" is the
    # sentence that makes the next silent log mean something.
    try:
        print(artefact_provenance_at(rev=args.rev, worktree=args.worktree).report())
    except CensusUnavailable as exc:
        print(f"PROVENANCE UNAVAILABLE (a failed check, not a pass): {exc}", file=sys.stderr)
        return 2

    try:
        verdict = check(current, load_baseline())
    except CensusUnavailable as exc:
        print(f"BASELINE UNAVAILABLE (a failed check, not a pass): {exc}", file=sys.stderr)
        return 2
    print(verdict.report())
    return 0 if (verdict.ok and wire.ok) else 1


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
