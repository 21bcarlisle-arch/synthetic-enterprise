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
import hashlib
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
    COMPANY_PACKAGES,
    SIM_PACKAGES,
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
# EACH SIDE HAS TWO LAWFUL SHAPES, and which one a module uses is fixed by the wall rather than by
# preference. The COMPANY owns exactly one codec and reaches a leg by importing its named entry
# point (`encode_request`, `decode_response`). The COUNTERPARTY may not import `company.*` at all
# (`simulation/payment_seam_adapter.py`'s own comment: a mock that encoded with the company's codec
# would make the round-trip a tautology), so it restates the contract's key set and builds or
# refuses the bytes itself -- recognised by the SHAPE it emits, or by the exact wire key set it
# mirrors. Recognising only one shape per side red-lists a leg for the end that is written the way
# the wall requires: matching encoders by shape alone missed every company-side encoder, and
# matching decoders by import alone missed every counterparty-side refusal.
#
# THE FIELD SETS ARE READ FROM `wall_protocol`'S OWN CONSTANTS, never restated here. That module
# already declares `REQUEST_WIRE_FIELDS`/`RESPONSE_WIRE_FIELDS` as the exact key set of a message,
# so a field added to the envelope moves the encoder's target and this control with it. A copy of
# the key set in this file would agree with itself forever.

#: The company's sole codec -- the module a decode site is recognised by importing.
CODEC_MODULE = "company.interfaces.wall_protocol"

#: THE TWO LEGS, and the reason the verdict is per-leg rather than per-seam. A seam resolves in two
#: separate-in-time crossings: the company EMITS a `WallRequest` and later OBSERVES a `WallResponse`.
#: Scored as one, a seam is credited wire-borne on any one encoder and any one decoder among its
#: importers -- so migrating only the observable leg reports the seam DONE while the request still
#: crosses the call frame carrying a version nobody reads. That is the identical defect, hiding on
#: the leg the instrument cannot see, and it is the reading this file used to give.
REQUEST_LEG = "request"
RESPONSE_LEG = "response"

#: How a seam DECLARES which legs it owns: by specialising the generic envelope. Derived from the
#: seam's own source rather than listed here for `envelope_seams`' reason -- a seam that grows a
#: request leg tomorrow owns the question on the day it lands, not the day someone remembers it.
LEG_ENVELOPE_NAMES: dict[str, str] = {"WallRequest": REQUEST_LEG, "WallResponse": RESPONSE_LEG}

#: leg -> the codec constant declaring that leg's exact wire form.
LEG_WIRE_CONSTANT: dict[str, str] = {
    REQUEST_LEG: "REQUEST_WIRE_FIELDS",
    RESPONSE_LEG: "RESPONSE_WIRE_FIELDS",
}

#: leg -> the codec entry point that DECODES it.
LEG_DECODE_NAME: dict[str, str] = {
    REQUEST_LEG: "decode_request",
    RESPONSE_LEG: "decode_response",
}

#: leg -> the codec entry point that ENCODES it. BOTH ends of a leg have two lawful shapes, and
#: which one a side uses is fixed by the wall rather than by preference: the COMPANY owns the codec
#: and calls it, the COUNTERPARTY may not import `company.*` and so restates the contract's key set
#: and builds the bytes itself. Recognising only the second (the reading this file used to give)
#: misses every company-side encoder -- `conversation_generator.generate_wire_request` calls
#: `encode_request` and builds no dict at all -- and reports a wired leg as DECODED-only.
LEG_ENCODE_NAME: dict[str, str] = {
    REQUEST_LEG: "encode_request",
    RESPONSE_LEG: "encode_response",
}

DECODE_NAMES: frozenset[str] = frozenset(LEG_DECODE_NAME.values())

#: Where the wire field sets are DECLARED. Read from the tree under measurement, not imported, so
#: the check reads the same rev everything else in this module does (a two-sided census must read
#: both sides from one ref).
CODEC_REL = "company/interfaces/wall_protocol.py"
WIRE_FIELD_CONSTANTS: tuple[str, ...] = (
    LEG_WIRE_CONSTANT[REQUEST_LEG],
    LEG_WIRE_CONSTANT[RESPONSE_LEG],
)

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


def wire_field_sets_by_leg(root: str) -> dict[str, frozenset[str]]:
    """`wire_field_sets`, keyed by the leg each form belongs to. Same fail-closed contract."""
    request_fields, response_fields = wire_field_sets(root)
    return {REQUEST_LEG: request_fields, RESPONSE_LEG: response_fields}


def seam_legs(root: str, seam: str) -> frozenset[str]:
    """The legs a seam OWNS, read from its own `X = WallRequest[Payload]` specialisations.

    A seam is red-listed only for legs it actually declares: `payment_observable_seam` would
    otherwise be marked unwired for a request it never makes. Returns empty for a seam that
    specialises neither envelope -- callers must treat that as UNKNOWN and fall back to the
    whole-seam rule, never as "owns nothing" (which would pass vacuously; see
    `envelope_wire_conformance`).
    """
    tree = _parse(os.path.join(root, *seam.split(".")) + ".py")
    if tree is None:
        return frozenset()
    return frozenset(
        leg
        for node in tree.body
        if isinstance(node, ast.Assign) and isinstance(node.value, ast.Subscript)
        for leg in [LEG_ENVELOPE_NAMES.get(_subscript_base_name(node.value))]
        if leg is not None
    )


def _subscript_base_name(node: ast.Subscript) -> str | None:
    """`WallRequest` from `WallRequest[Payload]`, whether plain or dotted."""
    base = node.value
    if isinstance(base, ast.Name):
        return base.id
    if isinstance(base, ast.Attribute):
        return base.attr
    return None


def leg_payload_types(root: str, seam: str) -> dict[str, set[str]]:
    """{leg -> the payload type names that leg's envelopes carry}, from the seam's own source."""
    tree = _parse(os.path.join(root, *seam.split(".")) + ".py")
    payloads: dict[str, set[str]] = {REQUEST_LEG: set(), RESPONSE_LEG: set()}
    if tree is None:
        return payloads
    for node in tree.body:
        if not (isinstance(node, ast.Assign) and isinstance(node.value, ast.Subscript)):
            continue
        leg = LEG_ENVELOPE_NAMES.get(_subscript_base_name(node.value))
        if leg is None:
            continue
        target = node.value.slice
        if isinstance(target, ast.Name):
            payloads[leg].add(target.id)
        elif isinstance(target, ast.Attribute):
            payloads[leg].add(target.attr)
    return payloads


def constructed_type_names(root: str) -> set[str]:
    """Every name CONSTRUCTED anywhere in the census trees -- `Foo(...)` call sites.

    What this distinguishes: a declared leg nobody ever sends (DORMANT -- the contract describes a
    message this build does not yet exchange) from a declared leg that crosses as an object
    (IN-PROCESS -- the defect). Transport evidence alone cannot tell them apart, because "never
    encoded, never decoded" is what both look like, and red-listing the first would make the
    control permanently red for a reason its subject cannot fix without deleting the contract.

    FAIL-CLOSED toward IN-PROCESS: an unparseable module contributes no constructions, so the only
    error this can make on a broken tree is to call a live leg dormant -- which is why the caller
    also requires the SEAM's own module to have parsed before it trusts a dormant reading, and why
    tests are outside `CENSUS_DIRS`: a payload built only by its own contract test is not traffic.
    """
    names: set[str] = set()
    for path, _rel in _census_py_files(root):
        tree = _parse(path)
        if tree is None:
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    names.add(node.func.id)
                elif isinstance(node.func, ast.Attribute):
                    names.add(node.func.attr)
    return names


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


def _emitted_legs(tree: ast.Module, shapes: dict[str, frozenset[str]]) -> set[str]:
    """Which legs' wire forms this module builds as a dict literal, keyed EXACTLY.

    EXACTLY, never a superset: `absence is never agreement` is the envelope's own rule, so a dict
    carrying six of seven keys is a message the far side must refuse, not a lenient pass here. A
    computed or **-spread key set is invisible to this and the limit is stated rather than hidden
    -- the same lower-bound caveat `wire_call_sites` carries.
    """
    emitted: set[str] = set()
    for node in ast.walk(tree):
        if not isinstance(node, ast.Dict):
            continue
        keys = [k.value for k in node.keys if isinstance(k, ast.Constant)]
        if len(keys) != len(node.keys) or not all(isinstance(k, str) for k in keys):
            continue
        for leg, shape in shapes.items():
            if frozenset(keys) == shape:
                emitted.add(leg)
    return emitted


def _emits_a_wire_shape(tree: ast.Module, shapes: list[frozenset[str]]) -> bool:
    """Whether this module emits ANY declared wire form. Retained as the leg-blind predicate."""
    return bool(_emitted_legs(tree, {str(i): s for i, s in enumerate(shapes)}))


def _decoded_legs(
    tree: ast.Module, dotted: str, imports: dict[str, set[str]], shapes: dict[str, frozenset[str]]
) -> set[str]:
    """Which legs this module REFUSES a malformed message on -- the two lawful decoder shapes.

    TWO SHAPES, because the wall itself forbids one. The company has a single codec and its decode
    sites are recognised by importing the entry point for that leg. The COUNTERPARTY may not import
    `company.*` at all, so it cannot use that codec and instead mirrors the leg's exact key set from
    the published contract and refuses against it -- `simulation/conversation_response.py`'s
    `_REQUEST_WIRE_FIELDS` is precisely that. Recognising only the import would report the
    conversation request leg as ENCODED-only, red-listing the seam for a decoder that exists and is
    written the one way the wall permits.

    Mirroring the exact key set is the strong signal here: it is the contract's form restated, which
    is what a foreign counterparty reading a published schema does. The same lower-bound caveat as
    the encoder match applies -- a computed key set is invisible.
    """
    legs = _codec_entry_legs(tree, dotted, imports, LEG_DECODE_NAME)
    for leg, shape in shapes.items():
        for declared in _module_level_string_sets(tree):
            if declared == shape:
                legs.add(leg)
    return legs


def _codec_entry_legs(
    tree: ast.Module, dotted: str, imports: dict[str, set[str]], entry_names: dict[str, str]
) -> set[str]:
    """Which legs this module reaches through the company codec's named entry points."""
    if CODEC_MODULE not in imports.get(dotted, set()):
        return set()
    imported = {
        alias.name
        for n in ast.walk(tree)
        if isinstance(n, ast.ImportFrom) and n.module == CODEC_MODULE
        for alias in n.names
    }
    return {leg for leg, name in entry_names.items() if name in imported}


def _encoded_legs(
    tree: ast.Module, dotted: str, imports: dict[str, set[str]], shapes: dict[str, frozenset[str]]
) -> set[str]:
    """Which legs this module PRODUCES a message on -- the two lawful encoder shapes.

    Symmetric with `_decoded_legs` and for the same reason: the company calls its own codec's
    `encode_*`, the counterparty builds the dict itself because it may not import that codec.
    """
    return _emitted_legs(tree, shapes) | _codec_entry_legs(tree, dotted, imports, LEG_ENCODE_NAME)


def _module_level_string_sets(tree: ast.Module) -> list[frozenset[str]]:
    """Every module-level `NAME = frozenset({...})`-style literal set of strings in this module."""
    found: list[frozenset[str]] = []
    for node in tree.body:
        if not isinstance(node, (ast.Assign, ast.AnnAssign)):
            continue
        value = node.value
        if isinstance(value, ast.Call) and value.args:
            value = value.args[0]
        if isinstance(value, (ast.Set, ast.List, ast.Tuple)):
            members = [e.value for e in value.elts if isinstance(e, ast.Constant)]
            if members and len(members) == len(value.elts) and all(
                isinstance(m, str) for m in members
            ):
                found.append(frozenset(members))
    return found


def envelope_transport(root: str) -> dict[str, tuple[set[str], set[str]]]:
    """{seam -> (modules that ENCODE its envelopes, modules that DECODE them)}.

    A module counts for a seam only if it IMPORTS that seam, which is what ties a wire form to the
    crossing it belongs to: the codec module itself encodes and decodes the generic envelope and
    imports no payload seam, so it is nobody's transport and is never credited as one.
    """
    shapes = wire_field_sets_by_leg(root)
    seams = envelope_seams(root)
    imports = _module_imports(root)
    transport: dict[str, dict[str, tuple[set[str], set[str]]]] = {
        s: {leg: (set(), set()) for leg in shapes} for s in seams
    }
    for path, rel in _census_py_files(root):
        dotted = rel[: -len(".py")].replace("/", ".")
        crossed = seams & imports.get(dotted, set())
        if not crossed:
            continue
        tree = _parse(path)
        if tree is None:
            continue
        encodes = _encoded_legs(tree, dotted, imports, shapes)
        decodes = _decoded_legs(tree, dotted, imports, shapes)
        for seam in crossed:
            for leg in encodes:
                transport[seam][leg][0].add(dotted)
            for leg in decodes:
                transport[seam][leg][1].add(dotted)
    return transport


def _leg_is_transported(encoders: set[str], decoders: set[str]) -> bool:
    """Both ends present, and they are NOT the same single module.

    A wire has two ends. Without the distinctness rule a module that emits the shape and also
    mirrors the leg's key set would certify its own leg -- it would be talking to itself, and the
    mirror half of `_decoded_legs` is exactly what makes that reachable.
    """
    return bool(encoders and decoders and (encoders - decoders or decoders - encoders))


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
    #: (seam, leg) that the seam declares and this build never sends -- reported, not scored.
    dormant_legs: tuple[tuple[str, str], ...] = ()
    #: (seam, leg, state) for every leg of every scored seam. The detail the seam-level buckets
    #: above summarise, kept so a partly-migrated seam names WHICH leg is still on the call frame.
    leg_states: tuple[tuple[str, str, str], ...] = ()
    #: Seams specialising neither envelope, so their legs are UNKNOWN and they fall back to the
    #: leg-blind rule. A bucket that must not quietly fill up: see the live test of the same name.
    legless: tuple[str, ...] = ()

    @property
    def ok(self) -> bool:
        return not self.in_process and not self.half_wired

    def report(self) -> str:
        lines = [
            f"channel C: {len(self.wire_borne)} of "
            f"{len(self.wire_borne) + len(self.half_wired) + len(self.in_process)} "
            "versioned seam(s) cross on a wire"
        ]
        legs_of = {}
        for seam, leg, state in self.leg_states:
            legs_of.setdefault(seam, []).append(f"{leg}={state}")
        lines += [
            f"    * {s} -- encoded and decoded"
            + (f" [{', '.join(legs_of[s])}]" if s in legs_of else "")
            for s in self.wire_borne
        ]
        lines += [
            f"    ! {s} -- {half} ONLY: transported on one side"
            + (f" [{', '.join(legs_of[s])}]" if s in legs_of else "")
            for s, half in self.half_wired
        ]
        lines += [
            f"    ! {s} -- IN-PROCESS: the envelope object crosses the call frame, so its "
            "schema_version is never encoded, never decoded and never refused"
            + (f" [{', '.join(legs_of[s])}]" if s in legs_of else "")
            for s in self.in_process
        ]
        lines += [
            f"    . {s} -- declares a {leg} leg this build never sends, so it is not scored"
            for s, leg in self.dormant_legs
        ]
        lines += [
            f"    - {s} -- declares no {SEAM_VERSION_CONSTANT}, so it has no version to carry"
            for s in self.unversioned
        ]
        lines += [
            f"    ? {s} -- specialises neither envelope, so its legs are unknown and it is scored "
            "leg-blind"
            for s in self.legless
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
    constructed = constructed_type_names(root)
    wire_borne, half_wired, in_process = [], [], []
    dormant_legs: list[tuple[str, str]] = []
    leg_states: list[tuple[str, str, str]] = []
    legless: list[str] = []
    for seam in sorted(versioned):
        owned = seam_legs(root, seam)
        payloads = leg_payload_types(root, seam)
        if not owned:
            # UNKNOWN legs, not "no legs": scoring a seam that owns nothing would pass vacuously,
            # so deleting the specialisations would be the cheapest way to silence this control.
            # Fall back to the leg-blind rule -- never weaker than the reading this replaced -- and
            # report the fallback so it cannot be taken quietly.
            legless.append(seam)
            encoders = set().union(*(e for e, _ in transport[seam].values()))
            decoders = set().union(*(d for _, d in transport[seam].values()))
            scored = [(encoders, decoders)]
        else:
            scored = []
            for leg in sorted(owned):
                encoders, decoders = transport[seam][leg]
                if not (payloads[leg] & constructed):
                    dormant_legs.append((seam, leg))
                    leg_states.append((seam, leg, "dormant"))
                    continue
                scored.append((encoders, decoders))
                leg_states.append((
                    seam, leg,
                    "wire" if _leg_is_transported(encoders, decoders)
                    else "ENCODED-only" if encoders
                    else "DECODED-only" if decoders
                    else "IN-PROCESS",
                ))
        if not scored:
            # Every declared leg is dormant: the seam describes messages this build never
            # exchanges. No crossing, so nothing to red -- reported via `dormant_legs`.
            continue
        if all(_leg_is_transported(e, d) for e, d in scored):
            wire_borne.append(seam)
        elif any(e or d for e, d in scored):
            any_encoder = any(e for e, _ in scored)
            half_wired.append((seam, "ENCODED" if any_encoder else "DECODED"))
        else:
            in_process.append(seam)
    return EnvelopeWireVerdict(
        wire_borne=wire_borne, half_wired=half_wired,
        in_process=in_process, unversioned=unversioned,
        dormant_legs=tuple(dormant_legs), leg_states=tuple(leg_states),
        legless=tuple(legless),
    )


def envelope_wire_conformance_at(
    rev: str = "HEAD", worktree: bool = False, repo_root: Path = PROJECT_DIR
) -> EnvelopeWireVerdict:
    """`envelope_wire_conformance` against the worktree, or against the tree at `rev`."""
    if worktree:
        return envelope_wire_conformance(str(repo_root))
    with head_export(str(repo_root), CENSUS_DIRS, rev=rev) as root:
        return envelope_wire_conformance(root)


# ── channel C, per CONVERSATION: does the exchange the seam declares actually happen? ─────────
#
# WHY THIS QUESTION EXISTS (2026-08-20, pass 34). The cold-eyes walk recorded in pass 33 was given
# five sentences of plain words and no code, and it named this failure shape BEFORE seeing the
# build: *"'We model it as a response to a synthetic request' is a fail."* It is exactly what two
# of the three versioned seams do. `flex_observable_seam` and `payment_observable_seam` each
# declare a request leg this build NEVER SENDS, and the company receives their observations as
# responses to nothing. That is unsolicited inbound wearing a response's envelope.
#
# THE CENSUS ALREADY SAW IT AND COULD NOT FAIL ON IT. `envelope_wire_conformance` above resolves
# the dormant request leg correctly, records it in `dormant_legs`, prints it with a neutral `.`
# marker -- and then credits the seam as `wire_borne` on its response leg alone, because `scored`
# skips dormant legs and every leg that remains is transported. So the transport question's
# strongest possible answer, 3 of 3 wire-borne, is returned by a wall on which two of the three
# conversations do not happen. An outsider with five sentences found what an in-house control
# reports as a status word, which is the whole argument for the technique and the reason this
# function is a SEPARATE question rather than a stricter setting on that one.
#
# WHY NOT JUST SCORE THE DORMANT LEG IN THE TRANSPORT VERDICT. Because dormancy is not a transport
# fact and the existing docstring is right to refuse it: a contract describing a message this build
# does not yet exchange is indistinguishable, on transport evidence alone, from an unmigrated
# crossing, and reddening it there would make that control permanently red for a reason its subject
# cannot fix without deleting the contract. The conversation question is answerable because it does
# not ask about transport at all. It asks which ROLES ARE LIVE, and "nobody ever asks" is a fact
# about this build that a repair can actually change -- by sending the request, or by giving
# unsolicited inbound a message shape that does not pretend to be an answer.
#
# ROLE LIVENESS, NOT LEG DECLARATION, IS THE UNIT -- and that choice closes a fail-open rather than
# creating one. A seam could shed the finding by DELETING its `WallRequest[...]` specialisation:
# with no request leg declared there would be no dormant leg to point at, and a leg-declaration
# rule would go quiet on the seam that had just made the defect worse. So a role that is not
# declared and a role that is declared-but-dormant are both NOT LIVE, and land in the same bucket.
# Deleting the declaration is not available as a repair.


@dataclass(frozen=True)
class ConversationVerdict:
    """Every versioned seam, asked whether both ends of its exchange are actually live.

    A ROLE IS LIVE when some module in the tree constructs the payload type that role's envelope
    carries. That is the same liveness `envelope_wire_conformance` uses to decide dormancy, read
    through `constructed_type_names`, and it is deliberately NOT a transport question: a role can
    be live and unwired (in-process), or wired and dead. What this asks is whether anybody in this
    build plays each part.

    FOUR SCORED BUCKETS, because each names a different repair:
      * `conversant`  -- both roles live. The green case, and the only one in which the
        request/response envelope is telling the truth about what happens.
      * `unsolicited` -- the response role is live and the request role is NOT. The company
        receives messages it never asked for, carried in an envelope whose `correlation_id`
        correlates to nothing it sent. Two repairs, and the choice between them is architectural:
        send the request, or give unsolicited inbound its own shape.
      * `unanswered`  -- the request role is live and the response role is NOT. The mirror: the
        company asks and this build contains nothing that ever answers.
      * `silent`      -- neither role is live. The seam describes an exchange this build does not
        have at either end. `envelope_wire_conformance` drops these before scoring ("no crossing,
        so nothing to red"); here they are the reason the question is being asked.
    `versionless` and `legless` are reported and NOT scored, carrying the same honesty the
    transport verdict carries: `wall_envelope` defines the shape rather than crossing, and a seam
    that specialises neither envelope has UNKNOWN roles, not absent ones.

    WHAT THIS CANNOT SEE, stated rather than implied. Liveness is repo-wide: a payload constructed
    ANYWHERE -- including in a module that never reaches the seam -- reads as live, exactly as it
    does for dormancy above. So this can prove a role dead and cannot prove one genuinely
    exercised. It is also blind to CARDINALITY: a conversation of three or more legs cannot be
    expressed by two envelope specialisations at all, so a seam that needs one reads as conversant
    the moment its two declared roles are live. Both limits are one-directional -- they lose
    findings, never manufacture them.
    """

    conversant: tuple[str, ...] = ()
    unsolicited: tuple[str, ...] = ()
    unanswered: tuple[str, ...] = ()
    silent: tuple[str, ...] = ()
    versionless: tuple[str, ...] = ()
    legless: tuple[str, ...] = ()

    @property
    def ok(self) -> bool:
        return not self.unsolicited and not self.unanswered and not self.silent

    def report(self) -> str:
        scored = (
            len(self.conversant) + len(self.unsolicited)
            + len(self.unanswered) + len(self.silent)
        )
        lines = [
            f"channel C conversations: {len(self.conversant)} of {scored} versioned seam(s) have "
            "BOTH ends of the exchange they declare live in this build"
        ]
        lines += [f"    * {s} -- both roles live" for s in self.conversant]
        lines += [
            f"    ! {s} -- UNSOLICITED INBOUND: the response role is live and NOTHING IN THIS "
            "BUILD EVER ASKS. The company receives these as answers to a request it never sent, "
            "so the envelope's correlation_id correlates to nothing and the request/response "
            "split is describing an exchange that does not happen. Either send the request or "
            "give unsolicited inbound a shape that does not pretend to be an answer."
            for s in self.unsolicited
        ]
        lines += [
            f"    ! {s} -- UNANSWERED: the request role is live and nothing in this build ever "
            "answers. The company asks into silence, and the response type is a promise the wall "
            "does not keep."
            for s in self.unanswered
        ]
        lines += [
            f"    ! {s} -- SILENT: neither role is live. The seam declares an exchange this "
            "build has at neither end."
            for s in self.silent
        ]
        lines += [
            f"    - {s} -- declares no {SEAM_VERSION_CONSTANT}, so it is not a crossing this "
            "question is about"
            for s in self.versionless
        ]
        lines += [
            f"    ? {s} -- specialises neither envelope, so its roles are UNKNOWN rather than "
            "absent and it is not scored"
            for s in self.legless
        ]
        return "\n".join(lines)


def seam_conversation_conformance(root: str) -> ConversationVerdict:
    """Every channel C seam, asked whether the conversation it declares actually happens.

    The seam set is DERIVED from `envelope_seams` for that function's stated reason: a fourth seam
    landing tomorrow owns this question on the day it lands. It lands scored -- and if it is
    another observation feed modelled as a reply to a synthetic request, it lands RED rather than
    unnoticed, which is the fail-closed direction and the entire point.

    FAIL-CLOSED on an unreadable subject, R15 FAIL-SILENT: a tree with versioned seams none of
    which specialises an envelope means the specialisations that carry every role in this question
    have been removed, and deleting them is the cheapest way to make this pass. That refuses.
    """
    seams = envelope_seams(root)
    if not seams:
        # A fully paid-down envelope channel is a legitimate reading, and a control pinned to a
        # non-zero count reds on its own success case. Same rule as the transport question.
        return ConversationVerdict()
    constructed = constructed_type_names(root)
    conversant: list[str] = []
    unsolicited: list[str] = []
    unanswered: list[str] = []
    silent: list[str] = []
    versionless: list[str] = []
    legless: list[str] = []

    for seam in sorted(seams):
        if _seam_version(root, seam) is None:
            versionless.append(seam)
            continue
        if not seam_legs(root, seam):
            legless.append(seam)
            continue
        payloads = leg_payload_types(root, seam)
        asks = bool(payloads[REQUEST_LEG] & constructed)
        answers = bool(payloads[RESPONSE_LEG] & constructed)
        if asks and answers:
            conversant.append(seam)
        elif answers:
            unsolicited.append(seam)
        elif asks:
            unanswered.append(seam)
        else:
            silent.append(seam)

    if versionless and not (conversant or unsolicited or unanswered or silent or legless):
        raise CensusUnavailable(
            f"{len(versionless)} channel C seam(s) exist and none declares "
            f"`{SEAM_VERSION_CONSTANT}` -- the subject of the conversation question has been "
            "removed, which is a failed check"
        )
    return ConversationVerdict(
        conversant=tuple(conversant),
        unsolicited=tuple(unsolicited),
        unanswered=tuple(unanswered),
        silent=tuple(silent),
        versionless=tuple(versionless),
        legless=tuple(legless),
    )


def seam_conversation_conformance_at(
    rev: str = "HEAD", worktree: bool = False, repo_root: Path = PROJECT_DIR
) -> ConversationVerdict:
    """`seam_conversation_conformance` against the worktree, or against the tree at `rev`."""
    if worktree:
        return seam_conversation_conformance(str(repo_root))
    with head_export(str(repo_root), CENSUS_DIRS, rev=rev) as root:
        return seam_conversation_conformance(root)


# ── channel C, the second question: what does a version MEAN? ────────────────────────────────
# Channel C above asks whether a seam's version reaches a wire, and at HEAD it answers 3 of 3.
# That reading is saturated, and a saturated instrument is a reason to move the ORIGIN rather
# than to stop asking: it cannot put the question that makes its own answer worth having, which
# is whether that version still DENOTES the surface it denoted when a counterparty agreed to it.
#
# `SCHEMA_VERSION` is not decoration here. It is encoded into every envelope and REFUSED on
# mismatch by each decoder (`schema_version {version} is not the {SCHEMA_VERSION} this seam
# speaks`). So a version whose meaning moves silently is strictly worse than no version at all:
# the counterparty's check passes and its assumption is wrong, which is the failure mode a
# version exists to prevent. Nothing inside a seam can raise this -- the declaration and the
# version are two literals in ONE file, one keystroke each, and every existing control on them
# (the mirror test, the AST literal guard, the denylist) is satisfied by editing both.
#
# THE PIN THEREFORE LIVES HERE, IN THE INSTRUMENT, AND NOT THERE, IN THE SUBJECT. That
# separation IS the control (R15 TAUTOLOGY): the seam declares what it observes, the census
# independently records what each version was pinned to mean, and a surface that moves without
# its version moving reds. Two files, two edits, two review moments.
#
# WHAT THIS DOES NOT DO, stated because the honest limit is the point of the check: it does not
# stop a leak. An editor who bumps `SCHEMA_VERSION` and re-pins below has widened the observable
# surface deliberately, and no code can make the observable/hidden judgement on their behalf --
# that judgement is irreducibly a human one. What it removes is the SILENT widening. After this,
# the one-line tuple append that went red and then green costs a version bump and a second file,
# both of which a diff shows and a counterparty can act on.

#: The per-seam declaration of what crosses. Read from the seam's own source, never imported --
#: same discipline as `wire_field_sets`, and for the same reason: the question is about the text
#: someone edits, not about the object a already-imported module happens to hold.
DECLARED_SURFACE_CONSTANT = "OBSERVABLE_PAYLOAD_FIELDS"


#: {seam -> (version pinned, digest of the surface that version denotes)}.
#:
#: HAND-WRITTEN AND REQUIRED TO STAY SO. A pin computed from the declaration it pins would move
#: with its subject and could never fire -- `test_the_pins_are_literal_and_not_derived` asserts
#: this stays a literal, the same guard the contracts' own closed sets carry.
#:
#: RE-PIN ONLY IN THE SAME EDIT THAT BUMPS THAT SEAM'S `SCHEMA_VERSION`. A re-pin without a bump
#: is the defect this table exists to make visible, performed by hand.
SURFACE_PINS: dict[str, tuple[int, str]] = {
    "interface.contracts.conversation_seam": (1, "f0f702d4c7af9083"),
    "interface.contracts.flex_observable_seam": (1, "ea1b70a309a2a3e4"),
    "interface.contracts.payment_observable_seam": (1, "cee449961c9f268b"),
}


def _dict_of_string_tuples(tree: ast.Module, name: str) -> dict[str, tuple[str, ...]] | None:
    """A module-level `NAME: ... = {"k": ("a", "b"), ...}` as a dict, or None if it is not that.

    None covers BOTH "absent" and "present but computed". The caller must treat them the same
    and fail closed: a declaration the census cannot read is a declaration it cannot pin, and a
    surface nothing pins is exactly the unbounded case this check is about.
    """
    for node in tree.body:
        targets = (
            [node.target] if isinstance(node, ast.AnnAssign)
            else node.targets if isinstance(node, ast.Assign)
            else []
        )
        if not any(isinstance(t, ast.Name) and t.id == name for t in targets):
            continue
        if not isinstance(node.value, ast.Dict):
            return None
        surface: dict[str, tuple[str, ...]] = {}
        for key, value in zip(node.value.keys, node.value.values):
            if not (isinstance(key, ast.Constant) and isinstance(key.value, str)):
                return None
            if not isinstance(value, (ast.Tuple, ast.List)):
                return None
            fields = [
                e.value for e in value.elts
                if isinstance(e, ast.Constant) and isinstance(e.value, str)
            ]
            if len(fields) != len(value.elts):
                return None
            surface[key.value] = tuple(fields)
        return surface
    return None


def declared_surface(root: str, seam: str) -> dict[str, tuple[str, ...]] | None:
    """The observable surface a seam declares, read from its own source. None if it declares none.

    FAIL-CLOSED (R15 FAIL-SILENT): an unreadable seam raises rather than returning None, because
    "I could not parse it" and "it declares nothing" are different facts and only one of them is
    the seam's own doing.
    """
    tree = _parse(os.path.join(root, *seam.split(".")) + ".py")
    if tree is None:
        raise CensusUnavailable(
            f"{seam} is unreadable, so its observable surface cannot be pinned -- an unavailable "
            "check is a FAILED check"
        )
    return _dict_of_string_tuples(tree, DECLARED_SURFACE_CONSTANT)


def surface_digest(surface: dict[str, tuple[str, ...]]) -> str:
    """A stable digest of an observable surface: which payloads, carrying which field NAMES.

    SORTED ON BOTH AXES, deliberately. The wire form is a mapping, so re-ordering a payload's
    fields is not a schema change and must not red -- a control that fires on a cosmetic edit is
    one that gets tuned away, and then the real edit passes with it.
    """
    canonical = json.dumps(
        {name: sorted(fields) for name, fields in sorted(surface.items())},
        separators=(",", ":"),
        sort_keys=True,
    )
    return hashlib.sha256(canonical.encode()).hexdigest()[:16]


@dataclass(frozen=True)
class SurfacePinVerdict:
    """Whether each versioned seam's observable surface still means what its version says.

    FOUR BUCKETS, because "not pinned" hides repairs that are not the same repair:
      * `pinned`     -- version matches its pin and the surface digest matches. The green case.
      * `drifted`    -- version UNCHANGED and the surface moved. THE DEFECT: every counterparty
        that accepted this version is now being sent a different shape under the same number.
      * `unpinned`   -- the seam declares a version this table has no entry for. Covers a new
        seam nobody pinned AND a version bumped without a re-pin. Both need the same deliberate
        act, and both are RED rather than skipped -- an unpinned surface is the unbounded case.
      * `undeclared` -- declares a `SCHEMA_VERSION` but no readable literal surface. RED: a
        versioned seam whose surface cannot be read is one nothing can hold to its version.
    `versionless` is reported and NOT scored -- `wall_envelope` defines the shape and is not a
    crossing, the same honest member channel C's own verdict carries.
    """

    pinned: tuple[str, ...] = ()
    drifted: tuple[tuple[str, int, str, str], ...] = ()
    unpinned: tuple[tuple[str, object], ...] = ()
    undeclared: tuple[str, ...] = ()
    versionless: tuple[str, ...] = ()

    @property
    def ok(self) -> bool:
        return not self.drifted and not self.unpinned and not self.undeclared

    def report(self) -> str:
        scored = len(self.pinned) + len(self.drifted) + len(self.unpinned) + len(self.undeclared)
        lines = [
            f"channel C surface pins: {len(self.pinned)} of {scored} versioned seam(s) still "
            "mean what their version says"
        ]
        lines += [
            f"    * {seam} -- v{SURFACE_PINS[seam][0]} = {SURFACE_PINS[seam][1]}"
            for seam in self.pinned
        ]
        lines += [
            f"    ! {seam} -- DRIFTED: v{version} was pinned to {want}, the tree now declares "
            f"{got}. The surface changed and the version did not, so every counterparty that "
            f"accepted v{version} is being sent a different shape under the same number. Bump "
            f"{SEAM_VERSION_CONSTANT} and re-pin, or put the field back."
            for seam, version, want, got in self.drifted
        ]
        lines += [
            f"    ! {seam} -- UNPINNED: declares version {version!r}, which SURFACE_PINS has no "
            "entry for. A surface nothing pins can widen silently; add the pin in this commit."
            for seam, version in self.unpinned
        ]
        lines += [
            f"    ! {seam} -- UNDECLARED: carries a {SEAM_VERSION_CONSTANT} but no readable "
            f"literal `{DECLARED_SURFACE_CONSTANT}`, so nothing can hold it to that version."
            for seam in self.undeclared
        ]
        lines += [
            f"    - {seam} -- declares no {SEAM_VERSION_CONSTANT}, so it has no version to mean "
            "anything by"
            for seam in self.versionless
        ]
        return "\n".join(lines)


def surface_pin_conformance(root: str) -> SurfacePinVerdict:
    """Every channel C seam, asked whether its declared surface still matches its pinned version.

    The seam set is DERIVED from `envelope_seams`, not listed, for that function's stated reason:
    a fourth seam added tomorrow owns this question on the day it lands, and it lands UNPINNED
    (red) rather than unnoticed (green), which is the fail-closed direction.
    """
    pinned: list[str] = []
    drifted: list[tuple[str, int, str, str]] = []
    unpinned: list[tuple[str, object]] = []
    undeclared: list[str] = []
    versionless: list[str] = []

    for seam in sorted(envelope_seams(root)):
        version = _seam_version(root, seam)
        if version is None:
            versionless.append(seam)
            continue
        surface = declared_surface(root, seam)
        if not surface:
            undeclared.append(seam)
            continue
        pin = SURFACE_PINS.get(seam)
        if pin is None or pin[0] != version:
            unpinned.append((seam, version))
            continue
        got = surface_digest(surface)
        if got != pin[1]:
            drifted.append((seam, version, pin[1], got))
        else:
            pinned.append(seam)

    return SurfacePinVerdict(
        pinned=tuple(pinned),
        drifted=tuple(drifted),
        unpinned=tuple(unpinned),
        undeclared=tuple(undeclared),
        versionless=tuple(versionless),
    )


def surface_pin_conformance_at(
    rev: str = "HEAD", worktree: bool = False, repo_root: Path = PROJECT_DIR
) -> SurfacePinVerdict:
    """`surface_pin_conformance` against the worktree, or against the tree at `rev`."""
    if worktree:
        return surface_pin_conformance(str(repo_root))
    with head_export(str(repo_root), CENSUS_DIRS, rev=rev) as root:
        return surface_pin_conformance(root)


SECOND_BELT_CONSTANT = "FORBIDDEN_TRUTH_FIELDS"


def _tuple_of_strings(tree: ast.Module, name: str) -> tuple[str, ...] | None:
    """A module-level `NAME: ... = ("a", "b")` as a tuple, or None if it is not that.

    None covers ABSENT, COMPUTED and EMPTY alike, and the caller must fail closed on all three.
    Empty is folded in on purpose rather than reported as a third state: a denylist with no
    names in it refuses nothing, which is precisely the R15 FAIL-OPEN shape, and it is exactly
    what "delete the awkward entries" leaves behind.
    """
    for node in tree.body:
        targets = (
            [node.target] if isinstance(node, ast.AnnAssign)
            else node.targets if isinstance(node, ast.Assign)
            else []
        )
        if not any(isinstance(t, ast.Name) and t.id == name for t in targets):
            continue
        if not isinstance(node.value, (ast.Tuple, ast.List)):
            return None
        names = [
            e.value for e in node.value.elts
            if isinstance(e, ast.Constant) and isinstance(e.value, str)
        ]
        if not names or len(names) != len(node.value.elts):
            return None
        return tuple(names)
    return None


def declared_second_belt(root: str, seam: str) -> tuple[str, ...] | None:
    """The truth-field denylist a seam declares, read from its own source. None if it has none.

    FAIL-CLOSED (R15 FAIL-SILENT), the same way `declared_surface` is: an unreadable seam
    RAISES rather than returning None, because "I could not parse it" and "it declares nothing"
    are different facts and only one of them is the seam's own doing.
    """
    tree = _parse(os.path.join(root, *seam.split(".")) + ".py")
    if tree is None:
        raise CensusUnavailable(
            f"{seam} is unreadable, so whether it carries a second belt cannot be established "
            "-- an unavailable check is a FAILED check"
        )
    return _tuple_of_strings(tree, SECOND_BELT_CONSTANT)


def _refuses_on(tree: ast.Module, name: str) -> bool:
    """Does some function in this module READ `name` and RAISE in the same body?

    NOT symbol-presence, and the difference is the whole point of this half. A module that
    imports a denylist and never acts on it is the FAIL-OPEN case being looked for -- the
    declaration exists, the census sees the name, and nothing refuses anything. Requiring the
    read and the raise to co-occur inside one function body is a coarse proxy for "it is on a
    refusal path", and coarse is stated rather than hidden: this cannot tell a belt checked in
    the encode path from one checked in an unrelated helper that happens to raise. What it CAN
    tell, which is the failure this exists for, is enforced-somewhere from enforced-nowhere.
    """
    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        body = list(ast.walk(node))
        reads = any(
            isinstance(n, ast.Name) and n.id == name and isinstance(n.ctx, ast.Load)
            for n in body
        )
        if reads and any(isinstance(n, ast.Raise) for n in body):
            return True
    return False


def belt_enforcers(root: str, seam: str) -> tuple[str, ...]:
    """Every non-test module that imports this seam's denylist AND refuses on it.

    TESTS ARE OUT OF SCOPE BY CONSTRUCTION, not by a filter that could be relaxed:
    `_census_py_files` walks `CENSUS_DIRS`, which is the wall's own trees, and `tests/` is not
    one of them. That is the right subject -- a belt only the tests consult stops nothing at
    the crossing, which is where the payload actually goes past.
    """
    enforcers: list[str] = []
    seam_rel = "/".join(seam.split(".")) + ".py"
    for path, label in _census_py_files(root):
        if label == seam_rel:
            continue
        try:
            # Cheap prefilter before the parse. Safe rather than fail-open: any module that
            # REFERENCES the name contains the name textually, `import *` included.
            if SECOND_BELT_CONSTANT not in open(path, encoding="utf-8").read():
                continue
        except OSError:
            continue
        tree = _parse(path)
        if tree is None:
            continue
        imported = any(
            isinstance(n, ast.ImportFrom)
            and n.module == seam
            and any(a.name == SECOND_BELT_CONSTANT for a in n.names)
            for n in ast.walk(tree)
        )
        if imported and _refuses_on(tree, SECOND_BELT_CONSTANT):
            enforcers.append(label)
    return tuple(sorted(enforcers))


def _enforcer_side(label: str) -> str | None:
    """Which SIDE of the wall an enforcing module sits on. None = neither side.

    SIDE, NOT LEG, and the distinction is this file's own established vocabulary rather than
    style. A seam has two LEGS (`seam_legs`: request and response); each leg has two ENDS
    (encode and decode); the two ends sit on opposite SIDES of the wall. The question below is
    about sides -- `one_sided` and `wire_field_sets_by_leg` must not be readable as the same
    axis, because a seam can be fully wired on both LEGS and belted on only one SIDE, which is
    exactly the state this was added to catch.

    `COMPANY_PACKAGES` and `SIM_PACKAGES` are imported from `tools.epistemic_wall` rather than
    respelled here on purpose: they are the wall's OWN definition of its two sides, so this
    question cannot drift away from the boundary it is asking about, and a package added to
    either side is a side here on the same day it is one there.

    NONE IS FAIL-CLOSED AND IS NOT A THIRD SIDE. `belt_enforcers` walks `CENSUS_DIRS`, which
    includes the BRIDGE packages (`tools`, `background`, `interface`) because channel D's ports
    live there. A bridge module refusing on a seam's denylist is a real fact and is reported,
    but it is not a SIDE of the crossing: the payload does not go past it on its way from the
    world to the company, so its refusal defends neither side.
    """
    top = label.split("/", 1)[0]
    if top in COMPANY_PACKAGES:
        return "company"
    if top in SIM_PACKAGES:
        return "world"
    return None


@dataclass(frozen=True)
class BeltSides:
    """One seam's enforcers, split by which side of the wall each sits on."""

    company: tuple[str, ...] = ()
    world: tuple[str, ...] = ()
    neither: tuple[str, ...] = ()

    @property
    def both(self) -> bool:
        return bool(self.company) and bool(self.world)

    @property
    def any_side(self) -> bool:
        return bool(self.company) or bool(self.world)

    @property
    def missing(self) -> str:
        """The side with NO enforcer, when exactly one is missing; `""` otherwise."""
        if self.company and not self.world:
            return "world"
        if self.world and not self.company:
            return "company"
        return ""


def belt_enforcer_sides(root: str, seam: str) -> BeltSides:
    """`belt_enforcers`, partitioned by which side of the wall each one sits on.

    WHY PER-SIDE AND NOT PER-SEAM (2026-08-20, EP6 pass 28). The per-seam verdict this refines
    was satisfied by ONE enforcer anywhere, and on its first run it reported -- in its enforcer
    list, where nothing could fail on it -- that `conversation_seam` was enforced by
    `simulation/conversation_response.py` alone. That is the seam carrying a customer's hidden
    latent traits, belted on the side the WORLD owns and bare on the side the COMPANY owns.

    THE TWO SIDES ARE NOT INTERCHANGEABLE. The encode end stops a leak being SENT; the decode
    end stops it being BELIEVED, and the decode end of a wall->company crossing is the only end
    of it the company still owns at go-live, when the counterparty is a real bank or a real CRM
    rather than this simulation. A seam belted on the sending side alone is defended entirely by
    the party that is about to be replaced.
    """
    company: list[str] = []
    world: list[str] = []
    neither: list[str] = []
    for label in belt_enforcers(root, seam):
        side = _enforcer_side(label)
        {"company": company, "world": world, None: neither}[side].append(label)
    return BeltSides(tuple(company), tuple(world), tuple(neither))


@dataclass(frozen=True)
class SecondBeltVerdict:
    """Whether each versioned seam carries a truth-field denylist that something acts on.

    WHY THE CENSUS OWNS THIS QUESTION AND NOT THE SEAMS. Two of the three seams grew a belt;
    the third did not, and the way that was found on 2026-08-20 was a human reading three files
    side by side. Nothing could have failed. A fourth seam lands tomorrow with the same hole
    and the same nothing happens -- which is the R10 shape: the CLASS has to fail, not the
    instance somebody noticed. The question also cannot live in the seams, because a seam that
    declares no belt is exactly the one that would not carry the check.

    FOUR SCORED BUCKETS, because each is a different repair:
      * `belted`     -- declares a non-empty literal denylist AND a non-test module on EACH
        SIDE of the wall refuses on it. The green case, and it names the enforcers per side: a
        claim carries a location.
      * `unbelted`   -- declares no readable non-empty denylist. Absent, computed and empty all
        land here (see `_tuple_of_strings`).
      * `unenforced` -- declares one that NOTHING on either side acts on. The fail-open case:
        the declaration is real, the refusal is not. A bridge module refusing is reported with
        the entry and does NOT redeem it (see `_enforcer_side`).
      * `one_sided`  -- declares one that exactly ONE side of the wall refuses on. Added by pass
        28 after the per-seam verdict reported precisely this state on `conversation_seam` in a
        list nothing could fail on; see `belt_enforcer_sides` for why the two sides are not
        interchangeable.
    `versionless` is reported and NOT scored -- `wall_envelope` defines the shape and is not a
    crossing, the same honest member channel C's own verdict and the surface pins carry.

    WHAT THIS STILL CANNOT SEE, stated rather than implied by the word "side": `_refuses_on` is
    a per-MODULE proxy, so this asks whether each SIDE has a refusing module, never whether the
    refusal sits on the codec the payload actually travels through. A company-side module that
    refuses on the denylist in an unrelated helper reads as a belted side here. SIDE is also not
    LEG: this says nothing about whether the request and response legs are separately belted,
    which is the finer unit `seam_legs` names and no check has yet been built on.
    """

    belted: tuple[tuple[str, int, tuple[str, ...], tuple[str, ...]], ...] = ()
    unbelted: tuple[str, ...] = ()
    unenforced: tuple[tuple[str, int, tuple[str, ...]], ...] = ()
    one_sided: tuple[tuple[str, int, str, tuple[str, ...]], ...] = ()
    versionless: tuple[str, ...] = ()

    @property
    def ok(self) -> bool:
        return not self.unbelted and not self.unenforced and not self.one_sided

    def report(self) -> str:
        scored = (
            len(self.belted) + len(self.unbelted) + len(self.unenforced) + len(self.one_sided)
        )
        lines = [
            f"channel C second belt: {len(self.belted)} of {scored} versioned seam(s) carry a "
            "truth-field denylist BOTH SIDES of the wall refuse on"
        ]
        lines += [
            f"    * {seam} -- {count} name(s), company side {', '.join(company)}; "
            f"world side {', '.join(world)}"
            for seam, count, company, world in self.belted
        ]
        lines += [
            f"    ! {seam} -- UNBELTED: no readable non-empty `{SECOND_BELT_CONSTANT}`. Its "
            f"closed set is its only belt, so a truth field added to a payload AND declared "
            "observable in the same edit crosses unrefused."
            for seam in self.unbelted
        ]
        lines += [
            f"    ! {seam} -- UNENFORCED: declares {count} forbidden name(s) and nothing on "
            "either side of the wall refuses on them. A denylist nothing reads is a comment."
            + (f" (refused only off-wall by {', '.join(off)})" if off else "")
            for seam, count, off in self.unenforced
        ]
        lines += [
            f"    ! {seam} -- ONE-SIDED: declares {count} forbidden name(s) refused on the "
            f"{'world' if missing == 'company' else 'company'} side ({', '.join(where)}) and "
            f"on nothing on the {missing} side. The bare side may be the one that decides "
            "whether a leak is BELIEVED, which at go-live is the only end the company owns."
            for seam, count, missing, where in self.one_sided
        ]
        lines += [
            f"    - {seam} -- declares no {SEAM_VERSION_CONSTANT}, so it is not a crossing this "
            "question is about"
            for seam in self.versionless
        ]
        return "\n".join(lines)


def second_belt_conformance(root: str) -> SecondBeltVerdict:
    """Every channel C seam, asked whether it carries an enforced second belt.

    The seam set is DERIVED from `envelope_seams` for that function's stated reason: a fourth
    seam added tomorrow owns this question on the day it lands, and it lands UNBELTED (red)
    rather than unnoticed (green), which is the fail-closed direction.
    """
    belted: list[tuple[str, int, tuple[str, ...], tuple[str, ...]]] = []
    unbelted: list[str] = []
    unenforced: list[tuple[str, int, tuple[str, ...]]] = []
    one_sided: list[tuple[str, int, str, tuple[str, ...]]] = []
    versionless: list[str] = []

    for seam in sorted(envelope_seams(root)):
        if _seam_version(root, seam) is None:
            versionless.append(seam)
            continue
        belt = declared_second_belt(root, seam)
        if not belt:
            unbelted.append(seam)
            continue
        sides = belt_enforcer_sides(root, seam)
        if not sides.any_side:
            unenforced.append((seam, len(belt), sides.neither))
        elif not sides.both:
            one_sided.append(
                (seam, len(belt), sides.missing, sides.company or sides.world)
            )
        else:
            belted.append((seam, len(belt), sides.company, sides.world))

    return SecondBeltVerdict(
        belted=tuple(belted),
        unbelted=tuple(unbelted),
        unenforced=tuple(unenforced),
        one_sided=tuple(one_sided),
        versionless=tuple(versionless),
    )


def second_belt_conformance_at(
    rev: str = "HEAD", worktree: bool = False, repo_root: Path = PROJECT_DIR
) -> SecondBeltVerdict:
    """`second_belt_conformance` against the worktree, or against the tree at `rev`."""
    if worktree:
        return second_belt_conformance(str(repo_root))
    with head_export(str(repo_root), CENSUS_DIRS, rev=rev) as root:
        return second_belt_conformance(root)


# ── channel E's conformance: does a WORLD class actually satisfy the Protocol? ───────────────
#
# WHY (2026-08-20, pass 30 -- this is the oldest un-progressed item on the atom, filed at pass 22
# as "four of six channels have no conformance question" and unchanged for seven passes).
# `enumerate_e` answers "how many business-side Protocols are declared", which is a WIDTH. The
# module docstring names its own limitation: "Channel E's list is a SUPERSET. It enumerates every
# `Protocol` declared business-side, not only those a world object satisfies." So the width cannot
# tell a real wall crossing from a company-internal interface, and it is blind to the failure mode
# that is SPECIFIC to structural typing: neither side declares the other, so when the world-side
# class drifts out of shape NOTHING BREAKS AT IMPORT TIME. There is no `implements` clause to go
# stale, no envelope to fail decoding, no version to mismatch. The company simply starts reading an
# attribute that is no longer there. Channels C and D cannot fail this way and that is exactly why
# E needed its own question rather than a copy of theirs.
#
# THE UNIT IS THE (PROTOCOL, WORLD SATISFIER) PAIR, frozen in the baseline, so the reading reds in
# BOTH directions: a world class that STOPS satisfying (the silent drift above) and a world class
# that STARTS satisfying (a new structural crossing nobody looked at).
#
# NOT A PROSE SCAN, ON PURPOSE -- the same discipline pass 29 installed for the conversation belt.
# Both Protocols here NAME their world-side implementor in a docstring ("the world's own
# `MeterReadEvent` satisfies it as-is"), and reading that sentence would score the DOCUMENTATION as
# evidence the coupling holds. It is the sentence that stays true while the code drifts. Membership
# is computed from the class bodies on both sides instead.

#: Only these trees can hold a SATISFIER. A company-side class satisfying a company-side Protocol
#: is ordinary internal typing and NOT a wall crossing -- without this pin, "the Protocol is
#: satisfied" would be answerable by a test double and the control would report crossings that do
#: not exist. Deliberately not `WALL_DIRS`, which contains both sides.
SATISFIER_DIRS: tuple[str, ...] = tuple(sorted(SIM_PACKAGES))


def _protocol_members(node: ast.ClassDef) -> set[str]:
    """The names a Protocol requires: annotated attributes and declared methods.

    Dunders are excluded -- `object` supplies them, so counting them would make every class a
    satisfier of any Protocol that declared one.
    """
    out: set[str] = set()
    for stmt in node.body:
        if isinstance(stmt, ast.AnnAssign) and isinstance(stmt.target, ast.Name):
            out.add(stmt.target.id)
        elif isinstance(stmt, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if not (stmt.name.startswith("__") and stmt.name.endswith("__")):
                out.add(stmt.name)
    return out


def _class_members(node: ast.ClassDef) -> set[str]:
    """The names a class provides: annotated fields (dataclasses), plain class attrs, methods."""
    out: set[str] = set()
    for stmt in node.body:
        if isinstance(stmt, ast.AnnAssign) and isinstance(stmt.target, ast.Name):
            out.add(stmt.target.id)
        elif isinstance(stmt, ast.Assign):
            out.update(t.id for t in stmt.targets if isinstance(t, ast.Name))
        elif isinstance(stmt, (ast.FunctionDef, ast.AsyncFunctionDef)):
            out.add(stmt.name)
    return out


def _world_classes(root: str) -> list[tuple[str, str, set[str]]]:
    """Every class declared in the SIM trees, as (rel path, class name, member names)."""
    found: list[tuple[str, str, set[str]]] = []
    for top in SATISFIER_DIRS:
        for dirpath, _dirnames, filenames in os.walk(os.path.join(root, top)):
            for fn in sorted(filenames):
                if not fn.endswith(".py"):
                    continue
                path = os.path.join(dirpath, fn)
                tree = _parse(path)
                if tree is None:
                    continue
                rel = os.path.relpath(path, root).replace(os.sep, "/")
                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef):
                        found.append((rel, node.name, _class_members(node)))
    return found


def _business_protocols(root: str) -> list[tuple[str, str, set[str]]]:
    """Every business-side Protocol, as (rel path, class name, required member names).

    Same subject as `enumerate_e` and found the same way, so the conformance question and the
    width are asking about one population rather than two that can drift apart.
    """
    found: list[tuple[str, str, set[str]]] = []
    for path, rel in _business_py_files(root):
        tree = _parse(path)
        if tree is None:
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and _protocol_base(node):
                found.append((rel, node.name, _protocol_members(node)))
    return found


@dataclass(frozen=True)
class SatisfactionVerdict:
    """Channel E's structural conformance: which Protocols a world class actually satisfies.

    `crossings` maps `file -> Name` to the sorted world-side satisfiers. `internal` are Protocols
    no world class satisfies -- company-internal typing, reported so the partition is visible and
    the superset is measured rather than assumed.
    """

    crossings: dict[str, tuple[str, ...]]
    internal: tuple[str, ...]

    def report(self) -> str:
        total = len(self.crossings) + len(self.internal)
        lines = [
            f"channel E structural satisfaction: {len(self.crossings)} of {total} "
            "business-side Protocol(s) are satisfied by a world class"
        ]
        for entry in sorted(self.crossings):
            lines.append(f"    * {entry} -- satisfied by {', '.join(self.crossings[entry])}")
        for entry in self.internal:
            lines.append(f"    - {entry} -- no world class satisfies it, so it is not a crossing")
        return "\n".join(lines)


def structural_satisfaction(root: str) -> SatisfactionVerdict:
    """THE READING. Which channel-E Protocols are real wall crossings, and satisfied by what.

    FAIL-CLOSED, and the first branch is the one that matters most here:
      * the SIM trees yield NO classes -> `CensusUnavailable`. This is this control's fail-open.
        An empty satisfier population makes every Protocol look internal, which reports "nothing
        crosses structurally" -- the reassuring answer -- from a measurement that looked at
        nothing. "Could not look" and "found nothing" are the same number and opposite facts.
      * a Protocol declares NO members -> `CensusUnavailable`. An empty requirement is satisfied by
        every class in the tree, so it can neither be a meaningful crossing nor a meaningful
        internal, and emptying a Protocol is the cheapest way to make this check say what you want.
      * NO business-side Protocols at all -> NOT refused. Channel E fully paid down is a legitimate
        reading and a control pinned to a non-zero count reds on its own success case.
    """
    protocols = _business_protocols(root)
    if not protocols:
        return SatisfactionVerdict(crossings={}, internal=())

    memberless = sorted(_entry(rel, name) for rel, name, members in protocols if not members)
    if memberless:
        raise CensusUnavailable(
            f"{len(memberless)} channel-E Protocol(s) declare no members: {memberless} -- an empty "
            "requirement is satisfied by every class in the tree, so this is a failed check, not a "
            "pass"
        )

    world = _world_classes(root)
    if not world:
        raise CensusUnavailable(
            f"no classes found in {list(SATISFIER_DIRS)} -- refusing to measure an empty satisfier "
            "population, which would report every Protocol as company-internal without looking"
        )

    crossings: dict[str, tuple[str, ...]] = {}
    internal: list[str] = []
    for rel, name, members in protocols:
        satisfiers = tuple(
            sorted(f"{wrel}::{wname}" for wrel, wname, wmembers in world if members <= wmembers)
        )
        entry = _entry(rel, name)
        if satisfiers:
            crossings[entry] = satisfiers
        else:
            internal.append(entry)
    return SatisfactionVerdict(crossings=crossings, internal=tuple(sorted(internal)))


def structural_satisfaction_at(
    rev: str = "HEAD", worktree: bool = False, repo_root: Path = PROJECT_DIR
) -> SatisfactionVerdict:
    """`structural_satisfaction` against the worktree, or against the tree at `rev`."""
    if worktree:
        return structural_satisfaction(str(repo_root))
    with head_export(str(repo_root), CENSUS_DIRS, rev=rev) as root:
        return structural_satisfaction(root)


# ── channel F's conformance: does the surface widen under an unchanged key set? ───────────────
# WHY (2026-08-20, pass 31 -- the last unowned channel). `enumerate_f`'s unit is the (TOP-LEVEL
# key, business reader) pair, which is a WIDTH and the only control channel F has ever had. The
# blindness that unit carries was MEASURED before this was written, not predicted: 93 top-level
# keys hide 693 distinct NESTED field names, and every ground-truth-shaped field that actually
# reaches the business side sits at depth >= 1 where the width cannot see it --
# `true_consumption_kwh`, `true_commodity_amount_gbp` and `true_total_amount_gbp` read by
# `company/billing/monthly_bill_assembly.py`, `true_total_equity_gbp` by
# `company/finance/double_entry.py`. Adding a nested field to a published blob moves NOTHING in
# the census: the top-level key set is unchanged, the reader set is unchanged, the width is
# unchanged. That is channel C's pass-26 disease in worse form -- there the surface could widen
# under an unchanged VERSION; here it widens under an unchanged KEY, and channel F has no version
# to pin it to.
#
# WHY THIS IS NOT A DENYLIST, which is the trap this atom already fell into once. Pass 25
# established that `FORBIDDEN_TRUTH_FIELDS` was fail-open on 9 of the 11 fields of the SIM's own
# truth record, because it "enumerates INSTANCES of a class it does not describe". A `true_*`
# prefix detector over the artefact would rebuild exactly that defect: it would catch
# `true_consumption_kwh` and miss the next hidden field somebody names `settled_actual`. So the
# unit here is the CLOSED SET -- every nested field name under a key the business side reads,
# whatever it is called. Widening is the event; the name is not the test.
#
# WIDENING IS THE SUBJECT AND NARROWING IS NOT, stated rather than left to be inferred from the
# code. A nested field DISAPPEARING is a paydown -- the artefact stopped publishing something --
# and a control that reds on that reds on its own success case and gets relaxed
# (`feedback_a_control_pinned_as_a_count_reds_on_its_own_success_case`). A RENAME still fires,
# because the new name is an addition; that is what keeps narrowing-tolerance from being a hole.
#
# THE ID-MAP DISCRIMINATOR, AND WHY IT IS NOT A GUESS. Several published blobs are dicts keyed by
# customer id or year (`clv_snapshots`, `dd_balance_book`, `per_cid_pnl`), so a naive walk over
# nested key names reds every time the population changes -- measured across 8 committed
# artefacts: `churn_risk: +SYN-2021-001 -C1_2` is population churn and no wall event at all. A
# dict whose values ALL share one shape is a MAP keyed by an identifier, and its keys are DATA;
# a dict whose values differ is a RECORD, and its keys are SCHEMA. That reading was validated
# against the same 8 artefacts: it is silent across four consecutive runs and moves on the real
# schema changes (`bills` gaining `billing_basis`, `ledger_pnl` gaining
# `back_billing_write_off_gbp`).

#: How deep the schema walk goes. Bounded because the artefact is arbitrary JSON and an unbounded
#: walk on a cyclic-by-construction blob is a hang, not a check.
SCHEMA_MAX_DEPTH = 7

#: NOTHING IS SAMPLED, and this constant records why rather than leaving the absence to be
#: rediscovered. The first cut of this walk read the first 5 values of a map and the first 80
#: elements of a list, on the reasoning that `_is_id_map` guarantees homogeneity so any value
#: would do. R15 mutation 6 falsified that: homogeneity holds at the TOP of a map and not
#: through the sub-maps beneath it, so removing one customer shifted the sample window and the
#: reading moved -- `years` gained `2021-12` and `SYN-2021-001` from population churn alone.
#: A control whose value depends on dict ordering reds on ordinary work and then gets relaxed.
#: The walk is exhaustive and bounded only by depth; it is a set union over field names, which
#: is cheap even on the 1,600-row logs.
SCHEMA_WALK_IS_EXHAUSTIVE = True


def _is_id_map(obj: dict) -> bool:
    """Is this dict keyed by an IDENTIFIER (data) rather than by FIELD NAMES (schema)?

    The test is homogeneity of the VALUES, never a pattern on the keys: matching keys against
    something that looks like a customer id would be a denylist over identifier spellings, and
    the next id format would walk straight through it. A single-entry dict is deliberately NOT a
    map -- one value is homogeneous with itself, so every one-field record would read as data and
    its field name would stop being pinned. That is the safe direction (it can only pin MORE than
    necessary), and it is the residual noise source this control has: a map that shrinks to one
    customer will red once. Stated because it will be seen.
    """
    if len(obj) < 2:
        return False
    if not all(isinstance(v, (dict, list)) for v in obj.values()):
        return False
    shapes = {
        frozenset(v) if isinstance(v, dict) else ("list",)
        for v in obj.values()
    }
    return len(shapes) == 1


def record_schema(obj: object, depth: int = 0) -> set[str]:
    """The FIELD NAMES beneath `obj` -- schema keys only, identifier keys excluded.

    A MAP contributes the schema of its values and NOT its own keys, which is what keeps
    population churn out of the reading.
    """
    out: set[str] = set()
    if depth > SCHEMA_MAX_DEPTH:
        return out
    if isinstance(obj, dict):
        if _is_id_map(obj):
            for value in obj.values():
                out |= record_schema(value, depth + 1)
        else:
            for key, value in obj.items():
                out.add(key)
                out |= record_schema(value, depth + 1)
    elif isinstance(obj, list):
        for value in obj:
            out |= record_schema(value, depth + 1)
    return out


def _read_top_level_keys(channel_f: set[str]) -> set[str]:
    """The top-level keys the business side actually reads, from channel F's own width.

    SAME POPULATION AS `enumerate_f`, on purpose and for the reason channel E's conformance gives
    for sharing `enumerate_e`'s subject: a conformance question asked of a different population
    than the width can drift away from it, and then the two halves of one channel disagree about
    what the channel is.
    """
    return {member.split(" -> ", 1)[0] for member in channel_f}


@dataclass(frozen=True)
class NestedSchemaVerdict:
    """Channel F's nested surface: the field names under every top-level key a reader touches.

    `pins` maps a top-level key to its sorted nested field names. `unread` are artefact keys no
    business module reads -- reported so the partition is visible, never pinned: pinning them
    would red on artefact changes that cross no wall, which is how a control acquires a
    reputation for noise and then gets switched off.
    """

    pins: dict[str, tuple[str, ...]]
    unread: tuple[str, ...]

    def report(self) -> str:
        total = len(self.pins) + len(self.unread)
        widest = sorted(self.pins.items(), key=lambda kv: (-len(kv[1]), kv[0]))[:3]
        lines = [
            f"channel F nested surface: {len(self.pins)} of {total} artefact key(s) are read "
            f"business-side and pinned at "
            f"{sum(len(v) for v in self.pins.values())} nested field name(s)"
        ]
        for key, fields in widest:
            lines.append(f"    * {key} -- {len(fields)} nested field name(s)")
        if self.unread:
            lines.append(
                f"    - {len(self.unread)} artefact key(s) no business module reads, so they "
                "are not crossings and are not pinned"
            )
        return "\n".join(lines)


def nested_schema(artefact: dict, channel_f: set[str]) -> NestedSchemaVerdict:
    """THE READING. What nested field names cross channel F today.

    FAIL-CLOSED, three ways (R15: an unavailable check is a FAILED check):
      * the artefact has NO top-level keys -> `CensusUnavailable`, the same doctrine and the same
        sentence as `enumerate_f`: an empty denominator makes channel F vacuously conformant.
      * NO top-level key is read business-side -> `CensusUnavailable`. Zero pins is the reassuring
        answer -- "no nested field crosses the wall" -- produced by a measurement that looked at
        nothing, and it is exactly what a broken `enumerate_f` would hand this function.
      * a pinned key whose value carries NO nested field names at all -> NOT refused. A top-level
        scalar (`total_net_gbp`) is a legitimate reading and pins the empty set honestly.
    """
    if not artefact:
        raise CensusUnavailable(
            "the run-output artefact has no top-level keys -- refusing to measure an empty "
            "denominator, because an empty denominator makes channel F vacuously conformant"
        )
    read = _read_top_level_keys(channel_f)
    if not read:
        raise CensusUnavailable(
            "no artefact key is read business-side, so channel F's nested surface has no subject "
            "-- refusing to report zero crossings from a measurement that looked at nothing"
        )
    pins = {
        key: tuple(sorted(record_schema(artefact[key], 1)))
        for key in sorted(read)
        if key in artefact
    }
    unread = tuple(sorted(set(artefact) - read))
    return NestedSchemaVerdict(pins=pins, unread=unread)


def nested_schema_at(
    rev: str = "HEAD", worktree: bool = False, repo_root: Path = PROJECT_DIR
) -> NestedSchemaVerdict:
    """`nested_schema` against the worktree, or against the tree at `rev`.

    ONE REF, BOTH SIDES -- the artefact and the readers come from the same rev, for the reason
    the module docstring gives channel F's width: comparing a live artefact against a committed
    reader set reports a difference that is nobody's defect.
    """
    if worktree:
        artefact = json.loads((repo_root / ARTEFACT_REL).read_text(encoding="utf-8"))
        return nested_schema(artefact, enumerate_f(str(repo_root), artefact))
    artefact = artefact_at(rev, repo_root)
    with head_export(str(repo_root), CENSUS_DIRS, rev=rev) as root:
        return nested_schema(artefact, enumerate_f(root, artefact))


NESTED_SCHEMA_KEY = "F_nested_schema"


def load_nested_schema_baseline(path: Path = BASELINE_PATH) -> dict[str, tuple[str, ...]]:
    """The frozen (top-level key -> nested field names) map. Missing is a FAILED check."""
    try:
        with open(path, encoding="utf-8") as fh:
            raw = json.load(fh)
    except (OSError, json.JSONDecodeError) as exc:
        raise CensusUnavailable(f"baseline {path} is unreadable: {exc}") from exc
    frozen = raw.get(NESTED_SCHEMA_KEY)
    if not isinstance(frozen, dict):
        raise CensusUnavailable(
            f"baseline {path} has no `{NESTED_SCHEMA_KEY}` object -- channel F's conformance "
            "question has no frozen answer to compare against, which is a failed check"
        )
    return {key: tuple(sorted(fields)) for key, fields in frozen.items()}


@dataclass(frozen=True)
class NestedSchemaDrift:
    """What changed about the nested surface.

    `widened` is THE FAILURE this control exists for: a new nested field name under a key the
    business side reads, landing with nothing to look at it. `newly_read` is a top-level key that
    has acquired its first business reader -- a new crossing, equally unlooked-at. `narrowed` and
    `paid_down` are the success cases, recorded and tolerated.
    """

    widened: dict[str, tuple[str, ...]]
    newly_read: tuple[str, ...]
    narrowed: dict[str, tuple[str, ...]]
    paid_down: tuple[str, ...]

    @property
    def ok(self) -> bool:
        return not self.widened and not self.newly_read

    def report(self) -> str:
        lines: list[str] = []
        for key, gained in sorted(self.widened.items()):
            lines.append(
                f"WIDENED on channel F -- `{key}` now publishes {', '.join(gained)} to a business "
                "reader; the top-level key set did not move, so nothing else catches this"
            )
        for key in self.newly_read:
            lines.append(
                f"NEW crossing on channel F -- `{key}` has acquired its first business reader, "
                "which has not been looked at"
            )
        for key, lost in sorted(self.narrowed.items()):
            lines.append(f"narrowed on channel F -- `{key}` dropped {', '.join(lost)}; re-freeze")
        for key in self.paid_down:
            lines.append(f"paid down on channel F -- `{key}` is no longer a crossing; re-freeze")
        return "\n".join(lines) or (
            "channel F: the nested surface under every read key is exactly what was frozen."
        )


def check_nested_schema(
    current: NestedSchemaVerdict, baseline: dict[str, tuple[str, ...]]
) -> NestedSchemaDrift:
    """Compare the nested surface against its frozen answer."""
    widened, narrowed = {}, {}
    newly_read, paid_down = [], []
    for key, fields in current.pins.items():
        if key not in baseline:
            newly_read.append(key)
            continue
        gained = tuple(sorted(set(fields) - set(baseline[key])))
        lost = tuple(sorted(set(baseline[key]) - set(fields)))
        if gained:
            widened[key] = gained
        if lost:
            narrowed[key] = lost
    for key in baseline:
        if key not in current.pins:
            paid_down.append(key)
    return NestedSchemaDrift(
        widened=widened,
        newly_read=tuple(sorted(newly_read)),
        narrowed=narrowed,
        paid_down=tuple(sorted(paid_down)),
    )


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


#: The L3 exit criterion this atom cannot reach from a worker tick, named so the map can
#: point at it. Passes 26-31 each recorded, in prose, that the cold-eyes walk on the three
#: seam codecs was the first blocker on L3 and that the invocation could not spawn the fresh
#: instance it requires; pass 31 recorded plainly that "L3 IS BLOCKED ON AN INSTRUMENT, NOT
#: ON BUILD WORK". Six consecutive prose recordings is what CLAUDE.md means by a rule that
#: evaporates, so this is the machine-readable half.
COLD_EYES_WALK_CRITERION = "L3_cold_eyes_walk_on_the_three_seam_codecs"

#: The capability id a blind review of this atom is recorded under. `tools/blind_review.py`
#: keys its ledger on the maturity-map atom id (`index_plain_words` resolves exactly that),
#: so this is a join key and not a label.
BLIND_REVIEW_CAPABILITY = "EP6_wall_protocol_typing"


def cold_eyes_walk_outstanding(ledger_path: Path | None = None) -> tuple[str, ...]:
    """The L3 criteria this seat cannot pay for — `()` once the walk has been RECORDED.

    This is the live half of the map's `infeasible_here` record on
    `EP6_wall_protocol_typing`, built to the pattern
    `background.lcl_household_anchors.unpayable_here_bands` established for
    `H_GAP_fabric_belief_truth_gap` — an atom that took FIFTEEN consecutive BUILD draws
    landing real green work while its level never moved, for the same structural reason.
    This atom has now taken twenty-three passes since its level last moved.

    WHAT IT READS, AND WHY THAT AND NOT A FLAG. The subject is the blind-review LEDGER —
    the artefact only a walk that actually happened can produce. A predicate reading
    "is this invocation allowed to delegate?" would be a flag about the seat's permissions,
    which is both unreadable from disk and the wrong question: the atom is not blocked on
    permission, it is blocked on a review that has not been performed. `tools/blind_review.py`
    is the mechanised blindfold for exactly this subject type (a capability, not a rendered
    artefact), and it records a transcript-and-battery per review. So the re-open is an
    observable event: on the day a blind review of this capability is recorded, this returns
    `()`, the map still claims a blocker, and the disagreement REDS rather than sitting there
    being politely out of date.

    FAIL-CLOSED. An unreadable ledger raises `CensusUnavailable` rather than reporting the
    walk outstanding OR done — an unavailable check is a FAILED check (R15 FAIL-SILENT), and
    both silent answers here are wrong in a way that matters. A ledger that does not exist
    yet is NOT unreadable: nothing recorded is the honest reading that no walk has run, which
    is the state at the time of writing (the ledger file does not exist, zero reviews ever).
    """
    try:
        from tools.blind_review import load_records
    except ImportError as exc:  # pragma: no cover - the module is in-tree
        raise CensusUnavailable(f"blind_review unavailable, so the walk is unknowable: {exc}")
    try:
        records = load_records(ledger_path)
    except Exception as exc:  # noqa: BLE001 - see the fail-closed paragraph above
        raise CensusUnavailable(
            f"the blind-review ledger could not be read, so whether the walk has run is "
            f"unknown -- that is a failed check, not an answer: {exc}"
        ) from exc
    for record in records:
        if record.get("capability") == BLIND_REVIEW_CAPABILITY:
            return ()
    return (COLD_EYES_WALK_CRITERION,)


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


SATISFACTION_KEY = "E_structural_satisfaction"


def load_satisfaction_baseline(path: Path = BASELINE_PATH) -> dict[str, tuple[str, ...]]:
    """The frozen (Protocol -> world satisfiers) map. Missing is a FAILED check, not a pass."""
    try:
        with open(path, encoding="utf-8") as fh:
            raw = json.load(fh)
    except (OSError, json.JSONDecodeError) as exc:
        raise CensusUnavailable(f"baseline {path} is unreadable: {exc}") from exc
    frozen = raw.get(SATISFACTION_KEY)
    if not isinstance(frozen, dict):
        raise CensusUnavailable(
            f"baseline {path} has no `{SATISFACTION_KEY}` object -- channel E's conformance "
            "question has no frozen answer to compare against, which is a failed check"
        )
    return {entry: tuple(sorted(sats)) for entry, sats in frozen.items()}


@dataclass(frozen=True)
class SatisfactionDrift:
    """What changed about who satisfies what.

    `drifted` is THE FAILURE and the reason this control exists: a Protocol still declared
    business-side whose frozen world satisfier no longer satisfies it. Structural typing means
    that breaks nothing at import time, so this is the only place it can surface.
    `appeared` is a new structural crossing -- also a failure, because nobody has looked at it.
    `paid_down` is a Protocol that left the tree entirely: the success case, recorded and tolerated.
    """

    drifted: dict[str, tuple[str, ...]]
    appeared: dict[str, tuple[str, ...]]
    paid_down: tuple[str, ...]

    @property
    def ok(self) -> bool:
        return not self.drifted and not self.appeared

    def report(self) -> str:
        lines: list[str] = []
        for entry, lost in sorted(self.drifted.items()):
            lines.append(
                f"DRIFTED on channel E -- {entry} is still declared and {', '.join(lost)} no "
                "longer satisfies it; structural typing breaks silently, so nothing else catches "
                "this"
            )
        for entry, gained in sorted(self.appeared.items()):
            lines.append(
                f"NEW structural crossing on channel E -- {entry} is now satisfied by "
                f"{', '.join(gained)}, which has not been looked at"
            )
        for entry in self.paid_down:
            lines.append(f"paid down on channel E -- {entry} left the tree; re-freeze to record")
        return "\n".join(lines) or "channel E: every Protocol is satisfied by exactly who it was."


def check_satisfaction(
    current: SatisfactionVerdict, baseline: dict[str, tuple[str, ...]]
) -> SatisfactionDrift:
    """Compare the satisfaction reading against its frozen answer.

    A satisfier that vanishes while its Protocol REMAINS is drift (red). A satisfier that vanishes
    because the whole Protocol left the tree is a paydown (green, recorded) -- the same split the
    width ratchet makes, applied to the finer unit.
    """
    declared = set(current.crossings) | set(current.internal)
    drifted, appeared = {}, {}
    paid_down = []
    for entry, frozen_sats in baseline.items():
        if entry not in declared:
            paid_down.append(entry)
            continue
        have = set(current.crossings.get(entry, ()))
        lost = tuple(sorted(set(frozen_sats) - have))
        if lost:
            drifted[entry] = lost
    for entry, sats in current.crossings.items():
        gained = tuple(sorted(set(sats) - set(baseline.get(entry, ()))))
        if gained:
            appeared[entry] = gained
    return SatisfactionDrift(
        drifted=drifted, appeared=appeared, paid_down=tuple(sorted(paid_down))
    )


def freeze_payload(
    current: dict[str, set[str]],
    rev: str,
    satisfaction: SatisfactionVerdict | None = None,
    nested: NestedSchemaVerdict | None = None,
) -> dict:
    payload = {
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
    if satisfaction is not None:
        payload[SATISFACTION_KEY] = {
            entry: list(sats) for entry, sats in sorted(satisfaction.crossings.items())
        }
    if nested is not None:
        payload[NESTED_SCHEMA_KEY] = {
            key: list(fields) for key, fields in sorted(nested.pins.items())
        }
    return payload


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

    try:
        satisfaction = structural_satisfaction_at(rev=args.rev, worktree=args.worktree)
    except CensusUnavailable as exc:
        print(
            f"CHANNEL E SATISFACTION UNAVAILABLE (a failed check, not a pass): {exc}",
            file=sys.stderr,
        )
        return 2

    try:
        nested = nested_schema_at(rev=args.rev, worktree=args.worktree)
    except CensusUnavailable as exc:
        print(
            f"CHANNEL F NESTED SURFACE UNAVAILABLE (a failed check, not a pass): {exc}",
            file=sys.stderr,
        )
        return 2

    if args.freeze:
        rev = "worktree" if args.worktree else args.rev
        BASELINE_PATH.write_text(
            json.dumps(freeze_payload(current, rev, satisfaction, nested), indent=2) + "\n",
            encoding="utf-8",
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

    # REPORTS AND DOES NOT GATE, by this file's own twice-stated rule -- a check becomes a gate
    # "in the same commit that makes it satisfiable" -- and this is the first check to arrive
    # UNSATISFIED. Two of the three live seams are unsolicited inbound at HEAD, so gating here
    # would refuse EVERY commit in the repo including the ones that repair it: pass 13's
    # landing-order defect, which this file has already learned twice and will not learn a third
    # time. The red is the finding, printed; `.ok` is asserted by the tests against fixtures where
    # the control's own success case is reachable, so it is proven able to fail without being
    # allowed to wedge the tree. It becomes part of this return the day `.ok` is True on HEAD.
    try:
        conversations = seam_conversation_conformance_at(rev=args.rev, worktree=args.worktree)
    except CensusUnavailable as exc:
        print(
            f"CHANNEL C CONVERSATION CHECK UNAVAILABLE (a failed check, not a pass): {exc}",
            file=sys.stderr,
        )
        return 2
    print(conversations.report())

    # THIS ONE GATES FROM ITS FIRST COMMIT, and the rule it follows is the one stated above: a
    # check becomes a gate "in the same commit that makes it satisfiable". Channel C's transport
    # question could not gate on arrival because two seams were genuinely in-process and it would
    # have refused its own repair. The pin has no such excuse -- all three seams are pinned green
    # at HEAD, so the only commits it can refuse are commits that move a surface without moving
    # its version, which is precisely its subject.
    try:
        surface_pins = surface_pin_conformance_at(rev=args.rev, worktree=args.worktree)
    except CensusUnavailable as exc:
        print(f"SURFACE PIN CHECK UNAVAILABLE (a failed check, not a pass): {exc}", file=sys.stderr)
        return 2
    print(surface_pins.report())

    # GATES FROM ITS FIRST COMMIT, by the rule this file has now stated twice: a check becomes
    # a gate "in the same commit that makes it satisfiable". All three seams are belted and
    # enforced in the commit that adds this, so the only commits it can refuse are commits that
    # land a crossing with no second belt -- which is its subject, not its collateral.
    try:
        second_belt = second_belt_conformance_at(rev=args.rev, worktree=args.worktree)
    except CensusUnavailable as exc:
        print(f"SECOND BELT CHECK UNAVAILABLE (a failed check, not a pass): {exc}", file=sys.stderr)
        return 2
    print(second_belt.report())

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

    # GATES FROM ITS FIRST COMMIT, by the rule this file has now stated three times: a check
    # becomes a gate "in the same commit that makes it satisfiable". Both channel-E Protocols are
    # satisfied by exactly one world class each at HEAD and the freeze records that, so the only
    # commits this can refuse are commits that break a structural crossing or add one -- its
    # subject, not its collateral.
    print(satisfaction.report())
    try:
        drift = check_satisfaction(satisfaction, load_satisfaction_baseline())
    except CensusUnavailable as exc:
        print(
            f"CHANNEL E BASELINE UNAVAILABLE (a failed check, not a pass): {exc}", file=sys.stderr
        )
        return 2
    print(drift.report())

    # GATES FROM ITS FIRST COMMIT, by the rule this file has now stated four times: a check
    # becomes a gate "in the same commit that makes it satisfiable". The freeze in this commit
    # records the nested surface as it stands at HEAD, so the only commits this can refuse are
    # commits that widen a published blob under an unchanged key or hand an unread key its first
    # business reader -- its subject, not its collateral.
    print(nested.report())
    try:
        nested_drift = check_nested_schema(nested, load_nested_schema_baseline())
    except CensusUnavailable as exc:
        print(
            f"CHANNEL F BASELINE UNAVAILABLE (a failed check, not a pass): {exc}", file=sys.stderr
        )
        return 2
    print(nested_drift.report())

    try:
        verdict = check(current, load_baseline())
    except CensusUnavailable as exc:
        print(f"BASELINE UNAVAILABLE (a failed check, not a pass): {exc}", file=sys.stderr)
        return 2
    print(verdict.report())
    return (
        0
        if (
            verdict.ok
            and wire.ok
            and surface_pins.ok
            and second_belt.ok
            and drift.ok
            and nested_drift.ok
        )
        else 1
    )


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
