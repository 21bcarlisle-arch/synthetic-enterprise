"""Pull-forward proposal path — DIRECTOR_RULING_FUTURE_COMMITMENT_SETS_2026-08-08 §3
(WORK-THIS-CREATES #3), atom `FUT2_pull_forward_proposal`.

THE RULING, VERBATIM: "dials and the planner may PROPOSE unblocking a ripe future atom,
with its accretion ledger as the case. Unblocking is a true door: director's word only,
never silence."

THE DELIBERATE EXCEPTION. Everywhere else in this codebase, THE_STANDARD governs and
silence IS validation — propose, record, act. This one act inverts that, by the director's
own word, because the epoch a company lives through is R13 CURRICULUM authorship: the agent
controls both sides of the wall, so the curriculum must face the director. That is also
exactly why this survives the 2026-07-29 rip-out of the permission machinery while a
"BUILD is open" gate does not — it is authorship of the world, not permission to work.

WHAT THIS IS NOT (the origin note's two named risks, guarded here):
  * NOT a permission gate. It gates ONE act — moving a curriculum-parked atom into the
    draw. It never gates DISCOVER/FRAME/research/red-team on a parked atom (CLAUDE.md's
    epoch-gating rule keeps those available NOW), never gates any build, and nothing else
    in the system may consult it. `forward_attachment_register` deliberately does not
    import it and the draw deliberately does not call it.
  * NOT a second channel or ceremony. The director's word is read from the channel he
    already uses — `docs/staging/from_rich_*.md` (ntfy IS him) and any `[DIRECTOR-RULING]`
    doc, including the advisor-staged bridge. No PIN, no signature, no new topic, no new
    file convention he has to learn. He names the atom and says unblock it; that is all.

THE MECHANISM, three parts:

  1. THE CASE (`candidates`) — DERIVED, never curated. A parked atom (`loop_stage: idle`)
     that has accreted ≥1 forward attachment through FUT1 is ripe by construction: the
     ledger of what has already been built toward it IS the case the ruling asks for.
     Ripeness is deliberately NOT a wording match on `block_reason` — a regex over prose
     would silently omit any atom phrased differently, and an under-reporting index is a
     fail-open control (it authorises the omission). Every idle atom with accretion
     surfaces; the gate is quoted verbatim beside it, and a missing gate is itself shown.

  2. THE PROPOSAL (`render_markdown` -> docs/design/PULL_FORWARD_PROPOSALS.md) — a
     projection of primary state (LAW-C, the discipline `open_question_register` and
     `forward_attachment_register` both use). Nothing is stored by hand; `--check` fails
     if the rendering and the derivation disagree.

  3. THE DOOR (`release_verdict` / `verify_release` / `apply_release`) — the part that must
     be able to fail. THREE properties, each mutation-proven in
     tests/background/test_pull_forward_proposal.py:

     (a) SILENCE NEVER RELEASES. There is no clock anywhere in the release path — no `now`,
         no `max_age`, no `since`, no deadline, no default-after-N. A proposal open for a
         year with no director word resolves PENDING, identically to one opened a second
         ago. The failure this atom exists to prevent is a timeout that unblocks, and it is
         the failure that would be written by default, because propose-then-proceed is what
         every other path here does.

     (b) THE VERDICT IS RE-DERIVED, NEVER TRUSTED. `apply_release` does not act on a verdict
         it is handed; it re-reads the director's own docs and compares. A verdict claiming
         a release nobody wrote — the tautology shape, a door that opens on whatever it is
         told — is caught by `verify_release` and refused.

     (c) FAIL-CLOSED. An unreadable staging tree, an absent one, a director doc that will
         not decode: every one of these resolves to PENDING and is REPORTED as
         `unreadable_source`. An unavailable check is a FAILED check (R15), and for a true
         door "failed" means shut.

  RECOGNITION. In a director source, a line naming the atom id AND carrying a release verb
  (unblock / open / pull forward / release / proceed / go ahead / yes) releases it, unless
  that same line is negated ("do not unblock EP7..."). The matched line is recorded on the
  verdict and reproduced in the rendering, so what was read is visible rather than inferred.
  Under-recognition is safe (the door stays shut and the proposal stays open); over-
  recognition is the dangerous direction, which is why negation is guarded and why the
  scanned SET is narrow — a worker-, planner- or plain advisor-authored doc is not the
  director's word and cannot release, however it is phrased.

  THE RELEASE HAS A REAL EFFECT (R11, no orphan transitions). `apply_release` moves the
  atom `loop_stage: idle -> build` and DELETES the now-false `block_reason` (a park reason
  outliving its park is this project's stale-cell defect class). The map is edited as TEXT,
  reusing `tools.merge_atom_status`'s helpers, so the other 229 hand-authored atoms keep
  their bytes.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import yaml

from background import forward_attachment_register as far
from tools import maturity_map_store as map_store
from tools.merge_atom_status import (
    MergeError,
    _atom_block_bounds,
    _block_declares_field,
    _set_or_create_scalar,
)

PROJECT_DIR = Path(__file__).resolve().parent.parent
MAP_PATH = PROJECT_DIR / "docs" / "design" / "maturity_map.yaml"
PROPOSALS_MD_PATH = PROJECT_DIR / "docs" / "design" / "PULL_FORWARD_PROPOSALS.md"

# The director's OWN channel, and only it. `from_rich_*.md` is what ntfy_responder writes
# from his topic (NTFY IS THE DIRECTOR); the `[DIRECTOR-RULING]` header covers his rulings
# and the advisor-staged bridge, which CLAUDE.md holds equally sufficient. Everything else —
# WORKER_*, PLANNER_*, a plain ADVISOR_STEER_* — is somebody else talking.
DIRECTOR_SOURCE_DIRS = (
    "docs/staging",
    "docs/staging/in_progress",
    "docs/staging/done",
)
_DIRECTOR_HEADER_RE = re.compile(r"\[DIRECTOR-RULING\]", re.IGNORECASE)
_HEAD_BYTES = 4000

_RELEASE_VERB_RE = re.compile(
    r"\b(?:un-?block(?:s|ed|ing)?|open(?:s|ed)?|pull[\s-]?forward(?:s|ed)?|"
    r"pull\s+it\s+forward|release(?:s|d)?|proceed(?:s|ed)?|go\s+ahead|yes|approved?)\b",
    re.IGNORECASE,
)
# The line must not be a refusal. Over-recognition is the dangerous direction for a door.
_NEGATION_RE = re.compile(
    r"\b(?:not|never|no|don'?t|do\s+not|cannot|can'?t|without|refus\w*|"
    r"instead\s+of|rather\s+than|proposal[\s-]?only)\b",
    re.IGNORECASE,
)
_ATOM_ID_RE = re.compile(r"\b[A-Z][A-Za-z0-9]*_[A-Za-z0-9_]+\b")


class PullForwardNotReleased(Exception):
    """Raised when a release is attempted without the director's word on disk. This is the
    door doing its job — it is never caught-and-continued anywhere."""


class PullForwardError(Exception):
    """A structural problem applying an authorised release (atom missing, map unparsable)."""


# --------------------------------------------------------------------------- the case

def _map_atoms(map_path: Path | None = None) -> dict[str, dict]:
    """Every atom in the map, by id. Returns {} on an unreadable/unparsable map rather than
    raising — a missing map must not fabricate ripeness, and must not release anything
    either (a candidate set of {} proposes nothing, and the door reads elsewhere)."""
    p = Path(map_path) if map_path else MAP_PATH
    try:
        doc = map_store.load_atoms(p)
    except (OSError, yaml.YAMLError, map_store.MapStoreError):
        return {}
    found: dict[str, dict] = {}

    def walk(node):
        if isinstance(node, dict):
            if isinstance(node.get("id"), str) and "level_current" in node:
                found[node["id"]] = node
            for v in node.values():
                walk(v)
        elif isinstance(node, list):
            for item in node:
                walk(item)

    walk(doc)
    return found


def candidates(root: Path | None = None, map_path: Path | None = None) -> list[dict]:
    """Every parked atom with accretion behind it, richest case first.

    RIPE := `loop_stage == 'idle'` AND at least one forward attachment (FUT1). Derived from
    the map and the attachment ledger only — no hand-maintained list, no prose match.
    """
    atoms = _map_atoms(map_path)
    attachments = far.attachments_by_atom(root=root, map_path=map_path)
    cases: list[dict] = []
    for atom_id, atom in atoms.items():
        if (atom.get("loop_stage") or "").strip() != "idle":
            continue
        entries = attachments.get(atom_id) or []
        if not entries:
            continue
        deps_parked = [
            d for d in (atom.get("depends_on") or [])
            if (atoms.get(d, {}).get("loop_stage") or "").strip() == "idle"
        ]
        gate = (atom.get("block_reason") or "").strip()
        cases.append({
            "atom_id": atom_id,
            "title": atom.get("title") or "",
            "lane": atom.get("lane") or "",
            "epoch": atom.get("epoch"),
            "gate": gate,
            "gate_stated": bool(gate),
            "attachments": entries,
            "attachment_count": len(entries),
            "deps_parked": deps_parked,
        })
    cases.sort(key=lambda c: (-c["attachment_count"], c["atom_id"]))
    return cases


# ------------------------------------------------------------------- the director's word

def _is_director_source(name: str, head: str) -> bool:
    """R7 discipline: content is a primary signal, filename a secondary one. A `from_rich_*`
    is his ntfy; a `[DIRECTOR-RULING]` header is his ruling or the advisor bridge carrying
    it; a `DIRECTOR_*` filename is the same by convention. Nothing else qualifies."""
    if name.startswith("from_rich_") and name.endswith(".md"):
        return True
    if _DIRECTOR_HEADER_RE.search(head):
        return True
    return name.startswith("DIRECTOR_") and name.endswith(".md")


def director_sources(root: Path | None = None) -> tuple[list[tuple[str, str]], list[str]]:
    """(sources, unreadable). `sources` is [(relpath, body)] for each director-authored doc;
    `unreadable` names every path or directory that could not be read.

    FAIL-CLOSED BY CONSTRUCTION: an unreadable input contributes no source, so it can only
    ever withhold a release, never grant one — and it is reported rather than swallowed, so
    "the scan was blind" is visible instead of looking like "he said nothing"."""
    base = Path(root) if root else PROJECT_DIR
    sources: list[tuple[str, str]] = []
    unreadable: list[str] = []
    for rel in DIRECTOR_SOURCE_DIRS:
        d = base / rel
        try:
            files = sorted(d.glob("*.md"))
        except OSError:
            unreadable.append(rel)
            continue
        for p in files:
            try:
                body = p.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError):
                unreadable.append(str(p.relative_to(base)))
                continue
            if _is_director_source(p.name, body[:_HEAD_BYTES]):
                sources.append((str(p.relative_to(base)), body))
    return sources, unreadable


def _release_lines(atom_id: str, body: str) -> list[str]:
    """Lines in one doc that name this atom AND ask for it to be opened, un-negated."""
    hits = []
    for line in body.splitlines():
        if atom_id not in line:
            continue
        if not _RELEASE_VERB_RE.search(line):
            continue
        if _NEGATION_RE.search(line):
            continue
        hits.append(line.strip())
    return hits


def release_verdict(atom_id: str, root: Path | None = None) -> dict:
    """Has the director said to unblock this atom?

    THERE IS NO CLOCK IN THIS FUNCTION AND THERE MUST NEVER BE ONE. It takes no `now`, no
    `max_age`, no `since`; nothing about how long a proposal has been open can appear in its
    answer. Silence resolves PENDING, forever, which is the whole point of the atom.
    """
    sources, unreadable = director_sources(root)
    matched = [
        {"source": rel, "line": line}
        for rel, body in sources
        for line in _release_lines(atom_id, body)
    ]
    return {
        "atom_id": atom_id,
        "released": bool(matched),
        "matched": matched,
        "unreadable_sources": unreadable,
        "reason": (
            f"released by {matched[0]['source']}" if matched
            else "PENDING — no director word on disk names this atom with a release"
        ),
    }


def verify_release(verdict: dict, root: Path | None = None) -> list[dict]:
    """THE CONTROL. Re-derive the verdict from the director's docs and report every way the
    one it was handed disagrees. This is what makes the door untrusting: `apply_release`
    acts on THIS, never on a verdict object someone built.

    Violations:
      `fabricated_release`  — claims released, re-derivation says PENDING (silence, a
                              timeout, a worker-authored doc, a hand-built dict).
      `fabricated_evidence` — cites a (source, line) pair the re-derivation did not find.
      `missing_evidence`    — the re-derivation found a release the verdict omits.
      `atom_mismatch`       — the verdict is about a different atom than it claims.
      `blind_scan`          — a source could not be read; the answer is not trustworthy.
    """
    violations: list[dict] = []
    atom_id = (verdict or {}).get("atom_id") or ""
    if not atom_id:
        return [{"kind": "atom_mismatch", "detail": "verdict names no atom"}]
    truth = release_verdict(atom_id, root)
    if verdict.get("released") and not truth["released"]:
        violations.append({
            "kind": "fabricated_release", "atom_id": atom_id,
            "detail": "verdict claims a release no director doc contains",
        })
    claimed = {(m.get("source"), m.get("line")) for m in (verdict.get("matched") or [])}
    actual = {(m["source"], m["line"]) for m in truth["matched"]}
    for src, line in sorted(claimed - actual, key=lambda t: (str(t[0]), str(t[1]))):
        violations.append({"kind": "fabricated_evidence", "atom_id": atom_id,
                           "source": src, "line": line})
    for src, line in sorted(actual - claimed):
        violations.append({"kind": "missing_evidence", "atom_id": atom_id,
                           "source": src, "line": line})
    for path in truth["unreadable_sources"]:
        violations.append({"kind": "blind_scan", "atom_id": atom_id, "source": path})
    return violations


# ------------------------------------------------------------------------ the release act

def _remove_scalar_field(block: list[str], atom_id: str, field: str) -> list[str]:
    """Delete `field:` and any continuation lines from an atom block. A YAML scalar may be
    folded over several lines, so the field ends at the next line whose indentation is at or
    below the field's own — not merely at the next line."""
    for k, ln in enumerate(block):
        m = re.match(rf"^(\s*){re.escape(field)}:", ln)
        if not m:
            continue
        indent = len(m.group(1))
        end = k + 1
        while end < len(block):
            nxt = block[end]
            if not nxt.strip():
                break
            if len(nxt) - len(nxt.lstrip(" ")) <= indent:
                break
            end += 1
        return block[:k] + block[end:]
    if _block_declares_field(block, field):
        raise PullForwardError(
            f"atom '{atom_id}' HAS a '{field}:' the release could not parse — refusing to "
            "leave a half-deleted park reason behind"
        )
    return block


def apply_release(
    atom_id: str,
    map_path: Path | None = None,
    root: Path | None = None,
    verdict: dict | None = None,
) -> dict:
    """Move a released atom into the draw. REFUSES unless the director's word is on disk.

    `verdict` is accepted only so a caller can show its work — it is VERIFIED against a fresh
    re-derivation and never believed. Passing a released-looking dict with nothing behind it
    raises, which is the tautology this door is built to fail on.

    R11: the release is not an orphan transition. It sets `loop_stage: build` (the draw's own
    condition) and deletes `block_reason`, whose park has just ended.
    """
    truth = release_verdict(atom_id, root)
    if verdict is not None:
        bad = verify_release(verdict, root)
        if bad:
            raise PullForwardNotReleased(
                f"REFUSED to release {atom_id!r}: the verdict does not survive re-derivation "
                f"from the director's own docs: {bad}"
            )
    if not truth["released"]:
        raise PullForwardNotReleased(
            f"REFUSED to release {atom_id!r}: {truth['reason']}. Unblocking is a true door — "
            "the director's word only, never silence, never elapsed time. The proposal stays "
            "open and the atom stays parked."
        )

    p = Path(map_path) if map_path else MAP_PATH
    try:
        lines = p.read_text(encoding="utf-8").splitlines(keepends=True)
    except OSError as exc:
        raise PullForwardError(f"cannot read {p}: {exc}") from exc
    try:
        start, end = _atom_block_bounds(lines, atom_id)
    except MergeError as exc:
        raise PullForwardError(str(exc)) from exc
    block = lines[start:end]
    before = "".join(block)
    block = _set_or_create_scalar(block, atom_id, "loop_stage", "build")
    block = _remove_scalar_field(block, atom_id, "block_reason")
    p.write_text("".join(lines[:start] + block + lines[end:]), encoding="utf-8")
    return {
        "atom_id": atom_id,
        "released_by": [m["source"] for m in truth["matched"]],
        "matched": truth["matched"],
        "changed": before != "".join(block),
    }


# ------------------------------------------------- the discharge control (R10 class fix)

# The map has exactly TWO legal states for a curriculum park, and `apply_release` is what
# moves between them: `block_reason` present (parked), or the field ABSENT (released through
# the door, which DELETES it). There is no third state, and this set is the enumeration of
# that fact. Adding a name here is a deliberate act — a discharge recorded in a field nothing
# reads is a hopeful pointer, not a record.
LEGAL_BLOCK_FIELDS = frozenset({"block_reason"})


def discharge_violations(map_path: Path | None = None, root: Path | None = None) -> dict:
    """THE CONTROL over discharged blocks: a claim that a park ENDED must resolve.

    Origin: `EP6_wall_protocol_typing` was moved `idle -> build` by a hand-authored
    `block_reason_discharged:` citing "the director's instruction of 2026-08-19 naming EP6
    for promotion". No such artefact exists on any channel, and the field itself is one this
    codebase never writes and never reads — `apply_release` deletes `block_reason`, it does
    not rename it. So the map recorded an authority that no reader can reach: the
    `the record outran its code` shape applied to AUTHORITY instead of to code.

    R10, so the POPULATION IS THE CLASS and not that cell: every `block_reason*` field on
    every atom in the map. Two violations, and the pairing is the point —

      `unknown_block_field`     — a `block_reason*` field outside `LEGAL_BLOCK_FIELDS`.
                                  Renaming the claim to a new spelling IS this violation, so
                                  the control cannot be greened by rewording it.
      `unresolvable_discharge`  — such a field exists AND `release_verdict` finds no director
                                  word naming the atom. This is the "cited artefact must
                                  EXIST and NAME the atom" leg, and it deliberately reuses
                                  the door's own recogniser rather than inventing a second
                                  authority channel (CLAUDE.md: do not invent authority
                                  checks).

    WHAT THIS CANNOT SEE, stated rather than glossed. An atom whose `block_reason` is simply
    DELETED by hand, with `loop_stage` set to `build`, is byte-indistinguishable from one the
    door released honestly — the map carries no field saying "this atom is curriculum-gated"
    other than the free-text gate itself, and `candidates()` already refuses to match on that
    prose for good reason. Closing that needs a typed facet on the atom, which is queued as a
    finding, not invented here.

    TWO LEGS MEASURED AND REJECTED, because the plausible ones are the wrong population:
      * "epoch >= 3 not parked must have a director release" — 109 of 164 epoch-3+ atoms are
        already drawn at HEAD. `epoch` is the NARRATIVE arc label, not the gate.
      * "a live `block_reason` on a drawn atom" — 10 such at HEAD, none of them this defect;
        that is the known stale-park-cell class and is reported below, never enforced here.
        (A further 11 carry the key with an EMPTY value; those belong to the existing
        `unstated_reason_block` gate and are deliberately not counted with the 10.)

    FAIL-CLOSED (R15): an unreadable map is a violation, not an empty pass; an unreadable
    director source is a `blind_scan` violation, because an unavailable check is a FAILED
    check. `population` is returned explicitly so an EMPTY population is visible rather than
    silently green — a wall enforced over a rotation set of zero is this project's own
    recurring defect, and this control's population legitimately drops to zero the moment the
    EP6 cell is restored.
    """
    p = Path(map_path) if map_path else MAP_PATH
    try:
        doc = map_store.load_atoms(p)
    except (OSError, yaml.YAMLError, map_store.MapStoreError) as exc:
        return {
            "atoms_scanned": 0, "population": 0, "stale_park_cells": [],
            "violations": [{"kind": "unreadable_map", "path": str(p), "detail": str(exc)}],
        }
    if doc is None:
        return {
            "atoms_scanned": 0, "population": 0, "stale_park_cells": [],
            "violations": [{"kind": "unreadable_map", "path": str(p),
                            "detail": "map is empty"}],
        }

    atoms = _map_atoms(p)
    violations: list[dict] = []
    population: list[str] = []
    stale_park_cells: list[str] = []

    for atom_id in sorted(atoms):
        atom = atoms[atom_id]
        block_fields = sorted(k for k in atom if str(k).startswith("block_reason"))
        for field in block_fields:
            if field in LEGAL_BLOCK_FIELDS:
                # Reported, never enforced — and TRUTHY only. A `block_reason:` present but
                # EMPTY is the separate, already-gated `unstated_reason_block` class (11 such
                # at HEAD); folding the two together would make this number mean two things.
                if (atom.get(field) or "").strip() and (
                    atom.get("loop_stage") or ""
                ).strip() not in ("idle", ""):
                    stale_park_cells.append(atom_id)
                continue
            population.append(atom_id)
            violations.append({
                "kind": "unknown_block_field", "atom_id": atom_id, "field": field,
                "detail": (
                    f"'{field}:' is not a field this codebase writes or reads; the door "
                    "deletes 'block_reason', it does not rename it"
                ),
            })
            verdict = release_verdict(atom_id, root)
            for src in verdict["unreadable_sources"]:
                violations.append({"kind": "blind_scan", "atom_id": atom_id, "source": src})
            if not verdict["released"]:
                violations.append({
                    "kind": "unresolvable_discharge", "atom_id": atom_id, "field": field,
                    "claim": str(atom.get(field) or "").strip(),
                    "detail": (
                        "the discharge cites an authority no director doc on disk contains: "
                        + verdict["reason"]
                    ),
                })

    return {
        "atoms_scanned": len(atoms),
        "population": len(population),
        "stale_park_cells": sorted(set(stale_park_cells)),
        "violations": violations,
    }


# -------------------------------------------------------------------------- the rendering

def render_markdown(cases: list[dict], root: Path | None = None) -> str:
    """The proposal document. A projection of `candidates()` + `release_verdict()`; every
    line here is re-derivable, and `check()` fails if it stops being."""
    out = [
        "# Pull-forward proposals — ripe parked atoms and their accretion",
        "",
        "GENERATED by `background/pull_forward_proposal.py` "
        "(`python3 -m background.pull_forward_proposal --write`). Do not hand-edit: "
        "`--check` fails if this file and the derivation disagree.",
        "",
        "Each atom below is parked (`loop_stage: idle`) and has had work filed toward it "
        "through the FUT1 attach-hook. That accretion IS the case for unblocking it "
        "(DIRECTOR_RULING_FUTURE_COMMITMENT_SETS_2026-08-08 §3).",
        "",
        "**These are proposals, and nothing here proceeds on silence.** Unblocking is the "
        "director's word only — reply on ntfy naming the atom (\"unblock "
        "EP7_adapter_elexon_insights\"). No reply leaves the atom parked, indefinitely; "
        "there is no clock in the release path.",
        "",
    ]
    if not cases:
        out += ["_No parked atom has accreted any forward attachment yet._", ""]
        return "\n".join(out)
    for c in cases:
        out.append(f"## {c['atom_id']} — {c['title']}")
        out.append("")
        out.append(
            f"- Lane `{c['lane']}` · epoch {c['epoch']} · **{c['attachment_count']} built toward it**"
        )
        out.append(f"- Gate: {c['gate']}" if c["gate_stated"]
                   else "- Gate: _none stated on the atom_")
        if c["deps_parked"]:
            out.append("- Still parked upstream: " + ", ".join(f"`{d}`" for d in c["deps_parked"]))
        v = release_verdict(c["atom_id"], root)
        if v["released"]:
            out.append("- **RELEASED** by " + ", ".join(
                f"`{m['source']}`" for m in v["matched"]))
        else:
            out.append("- Status: **PENDING the director** — no word on disk")
        out.append("")
        out.append("The case (accretion ledger):")
        out.append("")
        for e in c["attachments"]:
            note = f" — {e['note']}" if e.get("note") else ""
            out.append(f"- `{e.get('date') or '????-??-??'}` · `{e['source']}`{note}")
        out.append("")
    return "\n".join(out)


def check(root: Path | None = None, map_path: Path | None = None,
          rendering_path: Path | None = None) -> dict:
    """Derive, then confirm the written rendering matches. Also surfaces any blind scan."""
    cases = candidates(root, map_path)
    rp = Path(rendering_path) if rendering_path else PROPOSALS_MD_PATH
    expected = render_markdown(cases, root)
    try:
        actual = rp.read_text(encoding="utf-8")
    except OSError:
        actual = None
    _, unreadable = director_sources(root)
    problems: list[dict] = []
    if actual is None:
        problems.append({"kind": "missing_rendering", "path": str(rp)})
    elif actual.strip() != expected.strip():
        problems.append({"kind": "stale_rendering", "path": str(rp)})
    for u in unreadable:
        problems.append({"kind": "blind_scan", "source": u})
    discharges = discharge_violations(map_path, root)
    problems.extend(discharges["violations"])
    return {"cases": cases, "problems": problems, "rendering": expected,
            "discharges": discharges}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--write", action="store_true", help="write the proposal rendering")
    ap.add_argument("--check", action="store_true", help="fail if the rendering is stale")
    ap.add_argument("--release", metavar="ATOM_ID",
                    help="apply a director-released pull-forward (refuses without his word)")
    args = ap.parse_args(argv)

    if args.release:
        try:
            res = apply_release(args.release)
        except (PullForwardNotReleased, PullForwardError) as exc:
            print(f"REFUSED: {exc}", file=sys.stderr)
            return 2
        print(f"released {res['atom_id']} -> loop_stage: build "
              f"(by {', '.join(res['released_by'])})")
        return 0

    res = check()
    if args.write:
        PROPOSALS_MD_PATH.write_text(res["rendering"], encoding="utf-8")
        print(f"wrote {PROPOSALS_MD_PATH} ({len(res['cases'])} ripe atoms)")
        return 0
    for c in res["cases"]:
        print(f"{c['atom_id']:44s} {c['attachment_count']:3d} built toward  "
              f"{'RELEASED' if release_verdict(c['atom_id'])['released'] else 'pending'}")
    d = res["discharges"]
    print(f"discharge control: {d['atoms_scanned']} atoms scanned, "
          f"population {d['population']}, {len(d['violations'])} violations"
          + (f", {len(d['stale_park_cells'])} stale park cells (reported, not enforced)"
             if d["stale_park_cells"] else ""))
    if args.check and res["problems"]:
        for p in res["problems"]:
            print(f"PROBLEM {p['kind']}: "
                  f"{p.get('atom_id') or p.get('path') or p.get('source')}"
                  f"{' — ' + p['detail'] if p.get('detail') else ''}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    try:  # seat guard, FIRST act -- refuse to start on foreign soil (background/_seat.py)
        from background._seat import refuse_if_foreign
    except ModuleNotFoundError:  # launched as `python3 background/pull_forward_proposal.py`
        from _seat import refuse_if_foreign
    refuse_if_foreign("pull_forward_proposal")
    raise SystemExit(main())
