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
        verdict = check(current, load_baseline())
    except CensusUnavailable as exc:
        print(f"BASELINE UNAVAILABLE (a failed check, not a pass): {exc}", file=sys.stderr)
        return 2
    print(verdict.report())
    return 0 if verdict.ok else 1


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
