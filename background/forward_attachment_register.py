"""Forward-attachment register — DIRECTOR_RULING_FUTURE_COMMITMENT_SETS_2026-08-08 §2
(WORK-THIS-CREATES #2 and #5), atom `FUT1_attach_forward_hook`.

THE PROBLEM (the ruling's own evidence): discovery reaches forward daily — the heat-pump
anchor and the Clayton misdating are both future-epoch substance — and has nowhere to file
it. Findings scatter into whichever lane caught them and the future epochs never accrete.
Not blindness; homelessness.

THE PROPERTY (mandatory, per the ruling): any finding or DISCOVER mint MAY DECLARE which
future atoms it advances, and each future atom accretes a VISIBLE LEDGER of what has already
been built toward it. The mechanism is the worker's.

THE MECHANISM (deliberately a declared field plus a rendering — the atom's own simplicity
guard forbids a graph database):

  DECLARATION — one authoritative form, on its own line, in the finding/DISCOVER doc itself:

      **Advances:** EP16_anchored_generators, EP17_varied_population_draw — <optional note>

  The `Advances` keyword may be bolded or bare and may sit behind a list bullet; the payload
  is read TO END OF LINE ONLY and stops at the first note delimiter (an em-dash, `--`, `(`
  or `#`). That bound is deliberate: an unterminated field parser that swallows the rest of
  the document is a known defect class here — it produces false ids one way and, once the
  ids stop validating, silently drops the whole declaration the other.

  DERIVATION (LAW-C, the discipline `open_question_register` uses) — the ledger is DERIVED
  from PRIMARY state (the source docs) on every read. NOTHING is stored by hand. The rendered
  markdown (`docs/design/FORWARD_ATTACHMENT_LEDGER.md`) is a projection, and `--check` fails
  if the projection and the docs disagree. This is the exact R15 shape the atom's origin note
  names: "a ledger that renders whatever it is told" — an attachment that cannot be
  re-derived from the finding is not an attachment, and `verify_rendering()` is the control
  that fires on it (mutation-proven both ways in
  tests/background/test_forward_attachment_register.py).

  FAIL DIRECTION — every parse anomaly is a LOUD VIOLATION, never a silent drop:
    * a declared id that is not an atom in the maturity map  -> `unknown_atom`
    * a token that is not id-shaped                          -> `malformed_token`
    * a declaration with an empty payload                    -> `empty_declaration`
  Violations are returned to the caller and make the CLI exit non-zero. A doc that cannot be
  read contributes NOTHING and is reported as `unreadable_source` — this module never invents
  an attachment it did not read.

SCOPE — findings and DISCOVER mints live in `docs/staging/` (root, `in_progress/`, `done/`),
`docs/design/`, `docs/market_research/` and `docs/retrospectives/`. Any doc in those trees may
declare (the ruling says "any finding or DISCOVER mint", and refusing a declaration because a
doc's filename did not match a prefix would lose real accretion); each entry records the
`kind` it was recognised as, so provenance stays visible rather than enforced.

The register is a READER. It never edits a source doc, never writes the maturity map, and
imports nothing from `supervisor.py` — the draw does not read it (FUT2 is the proposal path
and it stops at the director; this file must never grow one).
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

import yaml

PROJECT_DIR = Path(__file__).resolve().parent.parent
if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))

from tools import maturity_map_store as map_store  # noqa: E402
from tools import simplifications_store as _atom_store  # noqa: E402 (the `name` drain)

MAP_PATH = PROJECT_DIR / "docs" / "design" / "maturity_map.yaml"
LEDGER_MD_PATH = PROJECT_DIR / "docs" / "design" / "FORWARD_ATTACHMENT_LEDGER.md"

# The doc trees a finding or DISCOVER mint can live in, relative to the project root.
SOURCE_TREES = (
    "docs/staging",
    "docs/design",
    "docs/market_research",
    "docs/retrospectives",
)
# Never scanned: the rendering itself (it would re-ingest its own projection) and any
# generated/observability tree.
EXCLUDED_RELPATHS = frozenset({"docs/design/FORWARD_ATTACHMENT_LEDGER.md"})

# ONE authoritative declaration form. Anchored to a line, payload bounded to that line.
_DECLARATION_RE = re.compile(
    r"^\s{0,8}(?:[-*+]\s+)?\*{0,2}Advances\*{0,2}\s*:\s*(?P<payload>[^\n]*)$",
    re.IGNORECASE | re.MULTILINE,
)
# The payload ends at the first note delimiter. Everything after it is free prose.
_NOTE_DELIM_RE = re.compile(r"\s(?:—|–|--|\(|#)\s?|\s*[—–]")
_ID_RE = re.compile(r"^[A-Za-z][A-Za-z0-9_]{2,63}$")
_TOKEN_SPLIT_RE = re.compile(r"[,;/]|\s+")
# A single declaration naming more ids than this is a parse accident, not a declaration.
MAX_IDS_PER_DECLARATION = 12
MAX_NOTE_CHARS = 240

_DATE_RE = re.compile(r"(20\d{2}-\d{2}-\d{2})")
_HEADING_RE = re.compile(r"^#\s+(.+?)\s*$", re.MULTILINE)

_DISCOVER_MARKERS = ("DISCOVER",)
_FINDING_MARKERS = ("FINDING", "FINDINGS")


def _map_atoms(map_path: Path | None = None) -> dict[str, dict]:
    """The maturity map's atoms by id. A map that cannot be read yields {} — every declared
    id then reads as `unknown_atom`, which is the SAFE direction (loud), never a silent pass."""
    p = map_path or MAP_PATH
    try:
        raw = map_store.load_atoms(p)
    except (OSError, yaml.YAMLError, map_store.MapStoreError):
        return {}
    if not isinstance(raw, list):
        return {}
    return {a["id"]: a for a in raw if isinstance(a, dict) and isinstance(a.get("id"), str)}


def _source_kind(relpath: str, text: str) -> str:
    """`discover` | `finding` | `other`, recognised from the filename and the first heading —
    recorded for provenance, never used to accept or reject a declaration."""
    head = text[:400].upper()
    name = Path(relpath).name.upper()
    if any(m in name for m in _DISCOVER_MARKERS) or any(m in head for m in _DISCOVER_MARKERS):
        return "discover"
    if any(m in name for m in _FINDING_MARKERS) or any(m in head for m in _FINDING_MARKERS):
        return "finding"
    return "other"


def _source_date(relpath: str, text: str) -> str | None:
    m = _DATE_RE.search(Path(relpath).name)
    if m:
        return m.group(1)
    m = _DATE_RE.search(text[:400])
    return m.group(1) if m else None


def _source_title(text: str) -> str | None:
    m = _HEADING_RE.search(text)
    return m.group(1).strip() if m else None


def parse_declarations(text: str) -> tuple[list[tuple[list[str], str]], list[str]]:
    """Extract (ids, note) declarations from one doc body.

    Returns (declarations, malformed) where `malformed` holds the raw tokens that were not
    id-shaped and the sentinel `""` for a declaration with an empty payload. Nothing is
    silently discarded: a line that says `Advances:` and yields no usable id is reported.
    """
    declarations: list[tuple[list[str], str]] = []
    malformed: list[str] = []
    for m in _DECLARATION_RE.finditer(text):
        payload = m.group("payload").strip()
        if not payload:
            malformed.append("")
            continue
        split = _NOTE_DELIM_RE.split(payload, maxsplit=1)
        id_part = split[0].strip()
        note = (split[1].strip() if len(split) > 1 else "")[:MAX_NOTE_CHARS]
        tokens = [t.strip().strip("`*.") for t in _TOKEN_SPLIT_RE.split(id_part)]
        tokens = [t for t in tokens if t]
        if not tokens:
            malformed.append("")
            continue
        ids = []
        for tok in tokens[:MAX_IDS_PER_DECLARATION]:
            (ids if _ID_RE.match(tok) else malformed).append(tok)
        malformed.extend(tokens[MAX_IDS_PER_DECLARATION:])
        if ids:
            declarations.append((ids, note))
    return declarations, malformed


def _iter_source_docs(root: Path):
    for tree in SOURCE_TREES:
        base = root / tree
        if not base.is_dir():
            continue
        for path in sorted(base.rglob("*.md")):
            rel = path.relative_to(root).as_posix()
            if rel in EXCLUDED_RELPATHS:
                continue
            yield path, rel


def derive(root: Path | None = None, map_path: Path | None = None) -> dict:
    """Derive the whole ledger from primary state. This is the ONLY producer of attachments —
    every consumer (the markdown rendering, the site JSON, the verifier) calls it, so no two
    surfaces can disagree about what was declared."""
    root = root or PROJECT_DIR
    atoms = _map_atoms(map_path if map_path is not None else (root / "docs/design/maturity_map.yaml"))
    entries: list[dict] = []
    violations: list[dict] = []
    for path, rel in _iter_source_docs(root):
        try:
            text = path.read_text(errors="replace")
        except OSError as exc:
            violations.append({"kind": "unreadable_source", "source": rel, "detail": str(exc)})
            continue
        if "advances" not in text.lower():
            continue
        declarations, malformed = parse_declarations(text)
        for bad in malformed:
            violations.append({
                "kind": "empty_declaration" if bad == "" else "malformed_token",
                "source": rel, "detail": bad,
            })
        if not declarations:
            continue
        kind = _source_kind(rel, text)
        date = _source_date(rel, text)
        title = _source_title(text)
        for ids, note in declarations:
            for atom_id in ids:
                if atom_id not in atoms:
                    violations.append({"kind": "unknown_atom", "source": rel, "detail": atom_id})
                    continue
                entries.append({
                    "atom_id": atom_id, "source": rel, "date": date,
                    "kind": kind, "title": title, "note": note,
                })
    entries.sort(key=lambda e: (e["atom_id"], e["date"] or "", e["source"]))
    ledger: dict[str, list[dict]] = {}
    for e in entries:
        ledger.setdefault(e["atom_id"], []).append(e)
    return {"ledger": ledger, "entries": entries, "violations": violations, "atoms": atoms}


def attachments_by_atom(root: Path | None = None, map_path: Path | None = None) -> dict[str, list[dict]]:
    """The per-atom view the site generator embeds. Never raises — a surface that cannot
    derive shows NO accretion rather than a stale one."""
    try:
        return derive(root=root, map_path=map_path)["ledger"]
    except Exception:  # pragma: no cover - defensive; a rendering must not take the site down
        return {}


# ---------------------------------------------------------------- rendering + its control

_HEADER = """# Forward-attachment ledger — what has already been built toward each future atom

<!-- GENERATED FILE — DO NOT EDIT BY HAND.
     Producer: background/forward_attachment_register.py  (atom FUT1_attach_forward_hook,
     DIRECTOR_RULING_FUTURE_COMMITMENT_SETS_2026-08-08 §2).
     Regenerate: python3 -m background.forward_attachment_register --write
     Verify:     python3 -m background.forward_attachment_register --check
     Every row is DERIVED from an `**Advances:**` declaration in the cited source doc. An
     entry that cannot be re-derived from its source is a FAILURE of --check, not a row. -->

A finding or DISCOVER mint declares what it advances by putting one line in its own body:

    **Advances:** EP16_anchored_generators, EP17_varied_population_draw — why

Nothing below is stored by hand. Delete the declaration and the row disappears.
"""

_ENTRY_RE = re.compile(r"^- `(?P<date>[^`]*)` · `(?P<source>[^`]+)`", re.MULTILINE)
_ATOM_HEADING_RE = re.compile(r"^## (?P<atom_id>[A-Za-z][A-Za-z0-9_]{2,63})\b", re.MULTILINE)


def render_markdown(derived: dict) -> str:
    ledger, atoms = derived["ledger"], derived["atoms"]
    out = [_HEADER, ""]
    out.append(
        f"**{len(derived['entries'])} attachment(s)** from "
        f"{len({e['source'] for e in derived['entries']})} source doc(s), across "
        f"{len(ledger)} atom(s).\n"
    )
    if not ledger:
        out.append("_No forward attachments declared yet._\n")
    for atom_id in sorted(ledger):
        a = atoms.get(atom_id, {})
        out.append(f"## {atom_id}")
        # `name` moved to the note store 2026-08-14; hydrate rather than read inline, or
        # every atom without a `title` renders a blank heading here and nothing raises.
        title = a.get("title") or _atom_store.atom_name(a)[:100]
        if title:
            out.append(f"**{title}**  ")
        out.append(
            f"_epoch {a.get('epoch')} · lane {a.get('lane')} · "
            f"L{a.get('level_current')}→L{a.get('level_target')} · {a.get('loop_stage')}_\n"
        )
        for e in ledger[atom_id]:
            line = f"- `{e['date'] or ''}` · `{e['source']}` ({e['kind']})"
            if e["note"]:
                line += f" — {e['note']}"
            out.append(line)
        out.append("")
    return "\n".join(out).rstrip() + "\n"


def verify_rendering(rendered: str, derived: dict) -> list[dict]:
    """THE CONTROL (R15). The named defect this must fire on: *a ledger that renders whatever
    it is told*. It parses the rendering BACK to (atom_id, source) pairs and compares against
    a fresh derivation from the source docs — so a row nobody declared is `fabricated_entry`
    and a declaration the rendering dropped is `missing_entry`. Both directions fail; a
    rendering that merely LOOKS plausible does not pass.

    Vacuity: an empty derivation with an empty rendering trivially agrees, so callers that
    depend on this control must also assert the derivation is non-empty (the live tests do).
    """
    rendered_pairs: set[tuple[str, str]] = set()
    current: str | None = None
    for line in rendered.splitlines():
        h = _ATOM_HEADING_RE.match(line)
        if h:
            current = h.group("atom_id")
            continue
        m = _ENTRY_RE.match(line)
        if m:
            rendered_pairs.add((current or "<no-atom-heading>", m.group("source")))
    derived_pairs = {(e["atom_id"], e["source"]) for e in derived["entries"]}
    violations = [
        {"kind": "fabricated_entry", "atom_id": a, "source": s}
        for a, s in sorted(rendered_pairs - derived_pairs)
    ]
    violations += [
        {"kind": "missing_entry", "atom_id": a, "source": s}
        for a, s in sorted(derived_pairs - rendered_pairs)
    ]
    return violations


def check(root: Path | None = None, map_path: Path | None = None,
          ledger_md: Path | None = None) -> tuple[list[dict], dict]:
    """Full check: parse violations + the committed rendering vs a fresh derivation.

    THE ORACLE MUST COVER EVERY DIMENSION ITS BLOCKING TEST ASSERTS (2026-08-10, eighth publish
    wedge). `verify_rendering` compares (atom_id, source) PAIRS -- a strict SUBSET of what
    `tests/background/test_forward_attachment_register.py::test_live_rendering_is_current`
    asserts, which is whole-text equality. So drift in any OTHER dimension of the rendering was
    invisible here and red at the gate: the live case was an atom's level/stage annotation
    moving `L0→L2 · build_` -> `L2→L2 · harden_` after an ordinary map edit, with every pair
    unchanged. That mattered beyond this file, because `background/derived_artefact_register.py`
    drives `--check` as its STALENESS ORACLE -- the self-healing repair built to close this very
    wedge class asked a question that could not see the staleness, reported "nothing stale", and
    let the gate red for hours (episode 8: 91 failures, ~15h).

    So the whole-text comparison is the LAST word here. The pair-level violations are kept
    because they are independently valuable (they name a fabricated or dropped row precisely,
    and they fire on a hand-edited rendering that whole-text equality would also catch but not
    explain) -- but they are no longer the only thing standing between drift and the gate.
    """
    root = root or PROJECT_DIR
    derived = derive(root=root, map_path=map_path)
    md_path = ledger_md or (root / "docs/design/FORWARD_ATTACHMENT_LEDGER.md")
    problems = list(derived["violations"])
    try:
        rendered = md_path.read_text()
    except OSError:
        # An unavailable rendering is a FAILED rendering (R15), never a pass.
        problems.append({"kind": "rendering_missing", "source": str(md_path)})
        return problems, derived
    problems.extend(verify_rendering(rendered, derived))
    if rendered != render_markdown(derived):
        problems.append({
            "kind": "stale_rendering", "source": str(md_path),
            "detail": "the committed rendering differs from a fresh derivation "
                      "(regenerate: python3 -m background.forward_attachment_register --write)",
        })
    return problems, derived


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--write", action="store_true", help="regenerate the markdown ledger")
    ap.add_argument("--check", action="store_true", help="fail if the rendering and the docs disagree")
    ap.add_argument("--json", action="store_true", help="print the derived ledger as JSON")
    args = ap.parse_args(argv)

    if args.check:
        problems, derived = check()
        for p in problems:
            print(f"VIOLATION {p['kind']}: {p.get('source') or p.get('atom_id')} {p.get('detail', '')}")
        print(f"{len(derived['entries'])} attachment(s) across {len(derived['ledger'])} atom(s); "
              f"{len(problems)} violation(s).")
        return 1 if problems else 0

    derived = derive()
    if args.json:
        print(json.dumps({"ledger": derived["ledger"], "violations": derived["violations"]}, indent=2))
        return 1 if derived["violations"] else 0
    text = render_markdown(derived)
    if args.write:
        LEDGER_MD_PATH.write_text(text)
        print(f"Wrote {LEDGER_MD_PATH} — {len(derived['entries'])} attachment(s), "
              f"{len(derived['ledger'])} atom(s), {len(derived['violations'])} violation(s).")
    else:
        print(text)
    for v in derived["violations"]:
        print(f"VIOLATION {v['kind']}: {v.get('source')} {v.get('detail', '')}", file=sys.stderr)
    return 1 if derived["violations"] else 0


if __name__ == "__main__":
    try:  # seat guard, FIRST act -- refuse to start on foreign soil (background/_seat.py)
        from background._seat import refuse_if_foreign
    except ModuleNotFoundError:  # launched as `python3 background/forward_attachment_register.py`
        from _seat import refuse_if_foreign
    refuse_if_foreign("forward_attachment_register")
    raise SystemExit(main())
