#!/usr/bin/env python3
"""Evidence pages behind the diagram nodes -- atom SITE_evidence_pages_behind_nodes.

WHY THIS EXISTS
---------------
The front-door MODEL-ON-A-PAGE diagram (site/index.html) states, for each of its six
nodes, a STAGE: Live / Building / Planned. Coherence-by-derivation already guarantees that
word is not hand-typed fiction -- Phase A (site/moap_coherence.py) fixes the node->atom
mapping, Phase B (site/moap_stage.py) COMPUTES the stage from those atoms' real levels in
docs/design/maturity_map.yaml, Phase C (site/moap_render.py) checks the rendered word equals
the computed one.

What a reader still could not do is DRILL. "Live" is a claim about 11 named atoms; the reader
had no way to see those atoms, their levels, the artefacts that substantiate them, or the
ledger entry that recorded the level move. The real-world twin is an investor data room: every
headline claim on the one-page overview walks to the underlying audited fact, so a reader
drills to the primary state rather than taking the summary on trust.

This module is that drill. It DERIVES -- never hand-types -- one evidence payload per node
from four primary artefacts, and renders it as a static page:

  1. site/data/moap_node_atoms.json      node -> the atoms its stage claim rests on
  2. docs/design/maturity_map.yaml       each atom's level_current/target, lane, loop_stage,
                                         and its `evidence:` list of named artefacts
  3. docs/observability/gate_authorizations.jsonl   the R16 RECORD of each level move
  4. docs/observability/test_execution_log.jsonl    the last executed suite count

FAIL-OPEN IS THE ENEMY (R15)
----------------------------
This feature's characteristic failure is a page that renders empty-but-plausible when its
source is absent -- a reader cannot tell "no evidence exists" from "the generator could not
read the map". Two mechanisms close that:

  * SOURCE ABSENT -> LOUD. Every one of the four sources is required. Missing, empty or
    unparseable raises EvidenceSourceUnavailable and NOTHING is written; the previous page
    stays up rather than being silently replaced by a blank one. An unavailable check is a
    FAILED check, never a passing one.
  * EVIDENCE ABSENT -> VISIBLY MISSING. An atom with no ledger record, an unresolvable
    citation, or no cited test file renders a MISSING badge naming exactly what is absent.
    "No evidence" is a legitimate and valuable rendering here; a quiet blank is not.

CITATIONS MUST RESOLVE
----------------------
SITE1/MAJOR-7 (cold-eyes Expert Hour 2026-07-29) found this site publishing evidence
citations that did not resolve -- and its 2026-08-03 follow-up found the deeper ROT class:
six of fifteen cited repo paths had simply been ARCHIVED out from under the citation
(docs/staging/X.md -> docs/staging/done/X.md). Telling a reader the evidence is at a path
where nothing sits is the same lie as a dead anchor in different clothes.

So every cited path is classified against real disk state:
    RESOLVED  -- exists exactly where the map says
    RELOCATED -- gone from the cited path, same basename found under an archive dir; BOTH
                 paths are shown, because silently rewriting hides the rot
    MISSING   -- nowhere on disk; rendered as an inert tag reading `unresolved`
No citation is EVER rendered as a clickable anchor. Repo-internal paths are not web-servable,
and per MAJOR-7 a dead citation wearing a live link's clothes trains a reader to distrust the
real ones. Every citation on this page is an inert provenance tag carrying its disk status.

INDEPENDENCE (R15, the tautology killer)
----------------------------------------
The GATE is not this module's own opinion. tests/tools/test_evidence_pages.py reads the
PUBLISHED site/data/evidence.json and stats every path ITSELF with the stdlib, so a generator
bug that mislabels a missing file as RESOLVED is caught by an oracle that never asked the
generator anything.

Run standalone for the report:   python3 tools/generate_evidence_data.py
"""
from __future__ import annotations

import html
import json
import re
import subprocess
import sys
import time
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent
SITE = PROJECT / "site"

# Phase B's derivation is REUSED, never re-implemented: the node stage rule lives in exactly
# one place (site/moap_stage.py) per coherence-by-derivation §6. Re-deriving it here would
# create a second definition that can drift.
if str(SITE) not in sys.path:
    sys.path.insert(0, str(SITE))
if str(PROJECT) not in sys.path:
    sys.path.insert(0, str(PROJECT))

# SITE4: /evidence/ is the one advertised area with NO `<nav>` element at all, and the
# only one whose page is GENERATED (here, every ~30 minutes on the publish path) --
# hand-editing the file is overwritten within the hour, so its nav has to be rendered
# from the register on this side. Same register as the other fifteen pages, imported
# rather than re-implemented: a second nav definition is the drift this step exists to
# end. site/ is already on sys.path above.
import ia_register as _ia  # noqa: E402

from tools import simplifications_store as store  # noqa: E402 (H41 record tenant)

MAP_PATH = PROJECT / "docs" / "design" / "maturity_map.yaml"
STORE_DIR = PROJECT / "docs" / "design" / "simplifications"
MAPPING_PATH = SITE / "data" / "moap_node_atoms.json"
LEDGER_PATH = PROJECT / "docs" / "observability" / "gate_authorizations.jsonl"
SUITE_LOG_PATH = PROJECT / "docs" / "observability" / "test_execution_log.jsonl"

OUT_JSON = SITE / "data" / "evidence.json"
OUT_HTML = SITE / "evidence" / "index.html"

# ── READER-READY: the evidence page is a machine record, and says so until it is not ─────────
# Director ruling, 2026-08-19: "Any live page showing wrong figures, internal vocabulary, or
# machine records a reader can't use gets replaced with an honest placeholder until it's right.
# That includes the evidence dump and the links into atom ids."
#
# I judged this page IN SCOPE, and it is the clearest case on the site. Measured on the rendered
# text rather than on impression: 509 hits of internal vocabulary and 19 raw atom ids. Its own
# opening paragraph -- the first thing a stranger reads -- says "it is computed from the levels
# of the named atoms the claim rests on", then cites `docs/design/maturity_map.yaml`,
# `docs/observability/gate_authorizations.jsonl` and a pytest collection count. Every word of
# that is TRUE and none of it is usable by the reader it is aimed at. SITE12's own title is the
# same finding: "The evidence surface answers a sceptic, not a maintainer."
#
# WHAT IS NOT SWITCHED OFF: `build_payload()` still runs and `site/data/evidence.json` is still
# written, checked and published every cycle. The derivation, the missing-artefact detection and
# the citation-status machinery all keep working -- so this is a rendering decision, not a
# retreat, and SITE12 rebuilds the reader-facing half from data that never stopped being current.
# If the payload were switched off too, the page would come back six months stale.
#
# Flip to True in the same commit that ships a reader-facing render. The control in
# tests/tools/test_evidence_reader_ready.py fails if this is True while the page still carries
# raw atom ids, so it cannot be flipped as a tidy-up.
EVIDENCE_READER_READY = False


# Where the staging protocol parks an actioned/archived directive. Ordered: first hit wins.
# Same convention as tools/generate_proof_data.py::CITATION_ARCHIVE_DIRS -- this is the ROT
# class that keeps recurring, so both citation surfaces must look in the same places.
ARCHIVE_DIRS = (
    "docs/staging/done",
    "docs/staging/in_progress",
    "docs/staging/fyi",
    "docs/staging/drafts",
    "docs/review_gates/done",
)

RESOLVED = "RESOLVED"
RELOCATED = "RELOCATED"
MISSING = "MISSING"

# Why an atom's evidence is incomplete. These are RENDERED, not suppressed -- the honest
# MISSING states are the most informative thing on the page.
NO_LEDGER_RECORD = "NO_LEDGER_RECORD"
UNRESOLVED_CITATION = "UNRESOLVED_CITATION"
NO_TEST_CITED = "NO_TEST_CITED"
DEAD_ATOM_REF = "DEAD_ATOM_REF"

MISSING_BLURB = {
    NO_LEDGER_RECORD: "level claimed but no entry in gate_authorizations.jsonl (R16 record absent)",
    UNRESOLVED_CITATION: "at least one cited artefact does not exist on disk",
    NO_TEST_CITED: "no test file among the cited artefacts",
    DEAD_ATOM_REF: "the node cites an atom that is not in the maturity map",
}

# A repo-relative path token inside a free-text evidence entry. The map's `evidence:` entries
# mix path and prose in one string, e.g.
#   'tests/sim/test_weather_price_chain.py + tests/company/test_x.py (19 tests, R15 mutation)'
# so paths are EXTRACTED rather than assumed to be the whole string. Anchored on a real file
# extension so a prose fragment can never be stat()'d as a filename.
_PATH_TOKEN = re.compile(
    r"(?:[A-Za-z0-9_.\-]+/)+[A-Za-z0-9_.\-]+"
    r"\.(?:py|md|json|jsonl|ya?ml|html|svg|csv|txt|sh)"
)
_ATOM_ID = re.compile(r"\s*-\s+id:\s*([A-Za-z0-9_]+)\s*$")
_SCALAR = re.compile(r"^\s{2,}([a-z_]+):\s*(.*?)\s*$")
_DEF_TEST = re.compile(r"^\s*(?:async\s+)?def\s+(test_[A-Za-z0-9_]*)", re.M)


class EvidenceSourceUnavailable(RuntimeError):
    """A primary source this page derives from is missing, empty or unparseable.

    Raised instead of emitting a thin payload. The publish pipeline logs the failure and the
    PREVIOUS evidence page stays live -- strictly better than replacing a real page with a
    plausible-looking empty one that a reader would read as "there is no evidence".
    """


# --- primary sources ---------------------------------------------------------


def _require(path: Path, what: str) -> str:
    if not path.is_file():
        raise EvidenceSourceUnavailable(f"{what} missing: {path}")
    text = path.read_text(encoding="utf-8")
    if not text.strip():
        raise EvidenceSourceUnavailable(f"{what} is empty: {path}")
    return text


def atom_records(map_path: Path = MAP_PATH) -> dict[str, dict]:
    """{atom id -> its raw map record} parsed off the committed maturity-map text.

    Text-parsed rather than yaml-loaded to match the existing site-scope convention
    (moap_coherence.map_atom_lanes, moap_stage.map_atom_levels) and to avoid a yaml
    dependency at publish scope. Captures the scalar fields this page shows plus the
    multi-line-tolerant `evidence:` list.
    """
    text = _require(map_path, "maturity map")
    records: dict[str, dict] = {}
    current: str | None = None
    ev_buf: list[str] | None = None
    for line in text.splitlines():
        m_id = _ATOM_ID.match(line)
        if m_id:
            if current and ev_buf is not None:
                records[current]["evidence_raw"] = "\n".join(ev_buf)
            ev_buf = None
            current = m_id.group(1)
            records[current] = {"id": current, "evidence_raw": ""}
            continue
        if current is None:
            continue
        if ev_buf is not None:
            # Inside a multi-line evidence list: accumulate until the closing bracket.
            ev_buf.append(line)
            if "]" in line:
                records[current]["evidence_raw"] = "\n".join(ev_buf)
                ev_buf = None
            continue
        m = _SCALAR.match(line)
        if not m:
            continue
        key, value = m.group(1), m.group(2)
        if key == "evidence":
            if value.count("[") and "]" in value:
                records[current]["evidence_raw"] = value
            elif value.startswith("["):
                ev_buf = [value]
            continue
        if key in ("name", "lane", "loop_stage", "value_stream", "epoch", "provenance",
                   "records_rehomed", "notes_rehomed"):
            records[current][key] = value.strip().strip("'\"")
    if current and ev_buf is not None:
        records[current]["evidence_raw"] = "\n".join(ev_buf)
    if not records:
        raise EvidenceSourceUnavailable(f"maturity map parsed to zero atoms: {map_path}")
    # The record store is DERIVED from the map's own location, never hard-coded to
    # the live one: a caller handed a map copy (every test fixture here) must get
    # that copy's store, or it would silently read the real tree's evidence and the
    # fixture would be testing the wrong pair. Same rule as
    # merge_atom_status._store_dir_for.
    store_dir = Path(map_path).parent / "simplifications"
    return _attach_rehomed_names(_attach_rehomed_evidence(records, store_dir), store_dir)


def _attach_rehomed_names(records: dict[str, dict], store_dir: Path = STORE_DIR) -> dict:
    """Resolve `name` for atoms that declare it REHOMED to the note store (2026-08-14).

    Exactly the sibling of `_attach_rehomed_evidence` below, one tenant over, and it
    exists for the same reason: the text parse above looks for a `name:` line that
    296 atoms no longer carry, so without this every atom on every node renders with
    a blank brief -- the `atom-name` paragraph is emitted only `if atom.get("name")`,
    so the page would simply lose it and nothing would raise.

    SAME TWO-TIER FAIL RULE (this module's header): a store directory that is gone,
    or a map where every atom declares a rehomed name and NOT ONE resolves, is the
    SOURCE being unavailable -- raise, write nothing, leave the previous page up. A
    single unresolvable atom is per-atom absence and renders blank, as before.

    Inline wins, matching `simplifications_store.atom_name`: an atom that still has
    its `name:` line (a pre-drain fixture, or a partial migration) keeps it."""
    declared = [
        aid for aid, r in records.items()
        if "name" in str(r.get("notes_rehomed") or "") and not r.get("name")
    ]
    if not declared:
        return records
    if not store_dir.is_dir():
        raise EvidenceSourceUnavailable(
            f"{len(declared)} atom(s) declare a rehomed name but the note store "
            f"is missing: {store_dir}"
        )
    loaded = store.notes_load_all(store_dir)
    resolved = 0
    for aid in declared:
        text = (loaded.get(aid) or {}).get("name")
        if isinstance(text, str) and text.strip():
            records[aid]["name"] = text
            resolved += 1
    if not resolved:
        raise EvidenceSourceUnavailable(
            f"{len(declared)} atom(s) declare a rehomed name and the note store "
            f"resolved none of them: {store_dir}"
        )
    return records


def _attach_rehomed_evidence(records: dict[str, dict], store_dir: Path = STORE_DIR) -> dict:
    """Resolve `evidence` for atoms that declare it REHOMED to the record store (H41).

    `evidence` was the bulk of the maturity map's byte growth and now lives in
    docs/design/simplifications/<atom_id>.yaml under `map_records:`, with the map
    keeping a `records_rehomed: [evidence]` declaration. Without this the text parse
    above would find no `evidence:` line for 259 atoms and this page would render a
    MISSING badge against every citation on every node -- a page that looks like a
    verdict ("nothing substantiates these claims") but is really a stale reader.

    THE TWO-TIER FAIL RULE IS THIS MODULE'S OWN (see the header): SOURCE ABSENT ->
    LOUD, EVIDENCE ABSENT -> VISIBLY MISSING. A store directory that is gone, or a
    map where every atom declares rehomed evidence and NOT ONE resolves, is the
    source being unavailable -- raise, write nothing, leave the previous page up.
    A single declared atom the store has no record for is per-atom absence and
    renders the ordinary MISSING badge, exactly as an unresolvable citation does.

    Reading through `simplifications_store.records_load_all` rather than re-parsing
    the store's yaml here is deliberate: one module owns that file format, and this
    is the same loader the H41 migration's hash proof and the store contract tests
    verify against -- so this page cannot drift into its own private idea of the
    store's shape."""
    declared = [
        aid for aid, r in records.items()
        if "evidence" in str(r.get("records_rehomed") or "")
    ]
    if not declared:
        # Pre-H41 map (or a test fixture): evidence is still inline and the text
        # parse above is complete. Not an error -- and not a silent pass either,
        # since the map either declares the rehome or still carries the field.
        return records
    if not store_dir.is_dir():
        raise EvidenceSourceUnavailable(
            f"{len(declared)} atom(s) declare rehomed evidence but the record store "
            f"is missing: {store_dir}"
        )
    loaded = store.records_load_all(store_dir)
    resolved = 0
    for aid in declared:
        entries = (loaded.get(aid) or {}).get("evidence")
        if isinstance(entries, list) and entries:
            records[aid]["evidence_entries"] = [str(e) for e in entries]
            resolved += 1
    if not resolved:
        raise EvidenceSourceUnavailable(
            f"{len(declared)} atom(s) declare rehomed evidence and the store "
            f"({store_dir}) resolved NONE of them -- refusing to publish an "
            "evidence page whose every citation would read MISSING for a reader-side "
            "reason"
        )
    return records


def ledger_by_atom(ledger_path: Path = LEDGER_PATH) -> dict[str, list[dict]]:
    """{atom id -> its gate_authorizations.jsonl entries, oldest first}.

    This is the R16 RECORD of a level move -- the auditable trace that a level was
    self-certified with evidence. An atom whose level is claimed with no entry here is not a
    failure to hide; it is exactly the MISSING state this page must show.
    """
    text = _require(ledger_path, "gate authorizations ledger")
    out: dict[str, list[dict]] = {}
    parsed = 0
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            entry = json.loads(line)
        except json.JSONDecodeError:
            continue
        parsed += 1
        atom = entry.get("atom")
        if atom:
            out.setdefault(atom, []).append(entry)
    if not parsed:
        raise EvidenceSourceUnavailable(
            f"gate authorizations ledger has no parseable records: {ledger_path}"
        )
    for entries in out.values():
        entries.sort(key=lambda e: e.get("ts") or 0)
    return out


def suite_snapshot(log_path: Path = SUITE_LOG_PATH) -> dict:
    """The LARGEST recorded pytest collection, with the timestamp of that run.

    Deliberately the maximum, not the most recent. Every pytest invocation appends to this
    log, including a developer running one file -- so "most recent" is whatever sub-suite ran
    last, and a 25-test run would silently replace the 18,000-test figure on a published page.
    That is a real misstatement, not a cosmetic one, so the published figure is the largest
    collection ever recorded (ties resolved to the later run) and is LABELLED as exactly that.
    A partial run can never shrink it; only a genuinely bigger suite moves it.

    Distinct from the per-atom static counts elsewhere in this module: this one was executed.
    """
    text = _require(log_path, "test execution log")
    best = None
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            entry = json.loads(line)
        except json.JSONDecodeError:
            continue
        count = entry.get("test_count")
        if not isinstance(count, int) or isinstance(count, bool):
            continue
        if best is None or count >= best["test_count"]:
            best = {"test_count": count, "timestamp": entry.get("timestamp")}
    if best is None:
        raise EvidenceSourceUnavailable(f"no test_count records in {log_path}")
    return best


# --- citations ---------------------------------------------------------------


def citation_paths(raw: str) -> list[str]:
    """Every repo-relative path token inside one free-text map evidence entry, in order,
    de-duplicated. An entry that is pure prose yields none."""
    seen: list[str] = []
    for m in _PATH_TOKEN.finditer(raw or ""):
        token = m.group(0)
        if token not in seen:
            seen.append(token)
    return seen


def classify_citation(path: str, project: Path = PROJECT) -> dict:
    """Classify one cited path against real disk state.

    RESOLVED at the cited path; else RELOCATED if the same basename sits under an archive
    dir (the SITE1 ROT class -- reported, never silently rewritten); else MISSING.
    """
    if (project / path).exists():
        return {"path": path, "status": RESOLVED, "resolved_path": path}
    name = Path(path).name
    for d in ARCHIVE_DIRS:
        candidate = project / d / name
        if candidate.exists():
            return {"path": path, "status": RELOCATED, "resolved_path": f"{d}/{name}"}
    return {"path": path, "status": MISSING, "resolved_path": None}


def _is_test_path(path: str) -> bool:
    return path.startswith("tests/") or Path(path).name.startswith("test_")


def _count_test_functions(path: str, project: Path = PROJECT) -> int:
    """Test functions DEFINED in a cited test file (static count, not an execution).

    Deliberately labelled as such everywhere it is rendered: it is a real number read off
    real disk, but it is not a pass count. The executed number on this page is the
    whole-suite figure from test_execution_log.jsonl.
    """
    f = project / path
    if not f.is_file():
        return 0
    try:
        return len(_DEF_TEST.findall(f.read_text(encoding="utf-8", errors="replace")))
    except OSError:
        return 0


# --- payload -----------------------------------------------------------------


def _git_hash() -> str:
    try:
        out = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=str(PROJECT), capture_output=True, text=True, timeout=10,
        )
        if out.returncode == 0:
            return out.stdout.strip()
    except (OSError, subprocess.SubprocessError):
        pass
    return "unknown"


def build_payload(
    map_path: Path = MAP_PATH,
    mapping_path: Path = MAPPING_PATH,
    ledger_path: Path = LEDGER_PATH,
    suite_log_path: Path = SUITE_LOG_PATH,
    project: Path = PROJECT,
) -> dict:
    """The whole evidence payload, derived from the four primary sources. Raises
    EvidenceSourceUnavailable if any source is absent/empty/unparseable."""
    _require(mapping_path, "node->atom mapping")
    records = atom_records(map_path)
    ledger = ledger_by_atom(ledger_path)
    suite = suite_snapshot(suite_log_path)

    from moap_stage import node_stages  # Phase B derivation, single-sourced

    stages = node_stages(map_path, mapping_path)
    if not stages:
        raise EvidenceSourceUnavailable(
            f"node->atom mapping yielded zero nodes: {mapping_path}"
        )
    mapping = json.loads(mapping_path.read_text(encoding="utf-8"))
    look = {n.get("id"): n.get("look_href") for n in mapping.get("nodes", [])}

    nodes = []
    for stage in stages:
        atoms_out = []
        for a in stage["atoms"]:
            rec = records.get(a["id"], {})
            citations = []
            # Rehomed atoms carry their entries as a real list (H41); only a still-
            # inline atom needs the flow-list text split.
            raw_entries = rec.get("evidence_entries")
            if raw_entries is None:
                raw_entries = _split_evidence(rec.get("evidence_raw", ""))
            for raw in raw_entries:
                for p in citation_paths(raw):
                    c = classify_citation(p, project)
                    c["raw"] = raw
                    c["is_test"] = _is_test_path(p)
                    if c["is_test"] and c["status"] != MISSING:
                        c["test_functions"] = _count_test_functions(
                            c["resolved_path"], project
                        )
                    citations.append(c)
            entries = [
                {
                    "action": e.get("action"),
                    "level": e.get("level"),
                    "ts": e.get("ts"),
                    "iso": _iso(e.get("ts")),
                    "authorized_by": e.get("authorized_by"),
                    "provenance": e.get("provenance") or "",
                }
                for e in ledger.get(a["id"], [])
            ]
            test_cits = [c for c in citations if c["is_test"]]
            missing = []
            if not a["in_map"]:
                missing.append(DEAD_ATOM_REF)
            if not entries and a["current"] > 0:
                missing.append(NO_LEDGER_RECORD)
            if any(c["status"] == MISSING for c in citations):
                missing.append(UNRESOLVED_CITATION)
            if not test_cits:
                missing.append(NO_TEST_CITED)
            atoms_out.append(
                {
                    "id": a["id"],
                    "name": rec.get("name", ""),
                    "lane": rec.get("lane", ""),
                    "loop_stage": rec.get("loop_stage", ""),
                    "level_current": a["current"],
                    "level_target": a["target"],
                    "at_target": a["at_target"],
                    "in_map": a["in_map"],
                    "citations": citations,
                    "test_files": len(test_cits),
                    "test_functions": sum(c.get("test_functions", 0) for c in test_cits),
                    "ledger": entries,
                    "missing": missing,
                }
            )
        nodes.append(
            {
                "id": stage["id"],
                "name": stage["name"],
                "declared_stage": stage["declared_stage"],
                "computed_stage": stage["computed_stage"],
                "stage_matches": stage["matches"],
                "look_href": look.get(stage["id"]),
                "evidence_href": f"./evidence/#{stage['id']}",
                "atoms": atoms_out,
                "atoms_at_target": sum(1 for x in atoms_out if x["at_target"]),
                "atoms_with_ledger": sum(1 for x in atoms_out if x["ledger"]),
                "atoms_with_missing": sum(1 for x in atoms_out if x["missing"]),
            }
        )

    all_cits = [c for n in nodes for a in n["atoms"] for c in a["citations"]]
    return {
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "git_hash": _git_hash(),
        "suite": suite,
        "sources": {
            "node_mapping": _rel(mapping_path, project),
            "maturity_map": _rel(map_path, project),
            "ledger": _rel(ledger_path, project),
            "test_execution_log": _rel(suite_log_path, project),
        },
        "nodes": nodes,
        "totals": {
            "nodes": len(nodes),
            "atoms": sum(len(n["atoms"]) for n in nodes),
            "citations": len(all_cits),
            "citations_resolved": sum(1 for c in all_cits if c["status"] == RESOLVED),
            "citations_relocated": sum(1 for c in all_cits if c["status"] == RELOCATED),
            "citations_missing": sum(1 for c in all_cits if c["status"] == MISSING),
            "atoms_with_missing": sum(
                1 for n in nodes for a in n["atoms"] if a["missing"]
            ),
            "nodes_fully_evidenced": sum(
                1 for n in nodes if n["atoms_with_missing"] == 0
            ),
        },
    }


def _split_evidence(raw: str) -> list[str]:
    """The map's `evidence:` flow-list text -> its individual entries. Splits on commas that
    are not inside quotes, so a quoted entry containing a comma stays whole."""
    if not raw:
        return []
    body = raw.strip()
    start, end = body.find("["), body.rfind("]")
    if start == -1 or end == -1:
        return []
    body = body[start + 1 : end]
    out, buf, quote = [], [], None
    for ch in body:
        if quote:
            if ch == quote:
                quote = None
            else:
                buf.append(ch)
            continue
        if ch in "'\"":
            quote = ch
            continue
        if ch == ",":
            out.append("".join(buf).strip())
            buf = []
            continue
        buf.append(ch)
    out.append("".join(buf).strip())
    return [x for x in (s.strip() for s in out) if x]


def _rel(path: Path, project: Path) -> str:
    """Repo-relative display path, tolerating a source that lives outside the tree (a test
    fixture pointing at tmp_path). Never raises -- a display string is not worth an
    exception, and the loud failures in this module are reserved for absent evidence."""
    try:
        return str(path.relative_to(project))
    except ValueError:
        return str(path)


def _iso(ts) -> str:
    if not isinstance(ts, (int, float)):
        return ""
    return time.strftime("%Y-%m-%d", time.gmtime(ts))


# --- control -----------------------------------------------------------------


def findings(payload: dict) -> list[tuple[str, str, str]]:
    """Every place the published evidence claim outruns real disk state, as
    (kind, subject, detail). Empty means every node drills to evidence that exists.

    This is a REPORT, not the gate. The gate is tests/tools/test_evidence_pages.py, which
    re-stats every path itself rather than trusting this payload -- an independent oracle, so
    the pair cannot be tautological.
    """
    out: list[tuple[str, str, str]] = []
    for node in payload["nodes"]:
        if not node["atoms"]:
            out.append(("NODE_WITHOUT_ATOMS", node["id"], "no atoms mapped to this node"))
        for atom in node["atoms"]:
            for c in atom["citations"]:
                if c["status"] == MISSING:
                    out.append(
                        ("UNRESOLVED_CITATION", atom["id"], f"{c['path']} not on disk")
                    )
                elif c["status"] == RELOCATED:
                    out.append(
                        (
                            "RELOCATED_CITATION",
                            atom["id"],
                            f"{c['path']} -> {c['resolved_path']}",
                        )
                    )
    return out


# --- render ------------------------------------------------------------------

_E = html.escape


def _stage_class(stage: str) -> str:
    return {"Live": "live", "Building": "building", "Planned": "planned"}.get(
        stage or "", "planned"
    )


def _citation_html(c: dict) -> str:
    """One citation as an INERT provenance tag carrying its disk status.

    Never an anchor. Repo-internal paths are not web-servable, and per SITE1/MAJOR-7 a dead
    citation styled as a live link trains a reader to distrust the real ones -- so on this
    page nothing that cannot be clicked pretends it can be.
    """
    status = c["status"]
    if status == RESOLVED:
        tag, cls, title = "on disk", "ev-ok", "exists at the cited path"
        shown = c["path"]
    elif status == RELOCATED:
        tag, cls = "relocated", "ev-moved"
        title = f"cited as {c['path']}; found at {c['resolved_path']}"
        shown = c["resolved_path"]
    else:
        tag, cls = "unresolved", "ev-missing"
        title = "cited by the maturity map but no such file exists on disk"
        shown = c["path"]
    extra = ""
    if c.get("test_functions"):
        extra = (
            f'<span class="ev-count">{c["test_functions"]} test fns</span>'
        )
    return (
        f'<span class="evsrc {cls}" title="{_E(title)}">{_E(shown)}'
        f'<span class="evsrc-tag">{tag}</span>{extra}</span>'
    )


def _atom_html(atom: dict) -> str:
    lvl = f'{atom["level_current"]}/{atom["level_target"]}'
    at = "ev-ok" if atom["at_target"] else "ev-below"
    # SITE7: a per-work-item anchor, so another surface can link to the record that proves
    # ONE claim rather than to the whole node. The Capabilities door needs exactly this --
    # "a sceptic should be able to get from 'Bills that add up' to the thing that proves it
    # in one click" -- and a node anchor drops the reader into a section holding a dozen
    # unrelated items. Prefixed `w-` because a bare id could collide with a node id.
    head = (
        f'<div class="atom-head" id="w-{_E(atom["id"])}">'
        f'<code class="atom-id">{_E(atom["id"])}</code>'
        f'<span class="lvl {at}">L{lvl}</span>'
        f'<span class="atom-meta">{_E(atom["lane"])} &middot; {_E(atom["loop_stage"])}</span></div>'
    )
    name = (
        f'<p class="atom-name">{_E(atom["name"])}</p>' if atom.get("name") else ""
    )
    miss = ""
    if atom["missing"]:
        items = "".join(
            f'<li><span class="miss-tag">{_E(k)}</span> {_E(MISSING_BLURB.get(k, ""))}</li>'
            for k in atom["missing"]
        )
        miss = f'<ul class="missing">{items}</ul>'
    cits = (
        '<div class="cits">' + "".join(_citation_html(c) for c in atom["citations"]) + "</div>"
        if atom["citations"]
        else '<p class="none">No artefact cited by the map for this atom.</p>'
    )
    if atom["ledger"]:
        rows = "".join(
            f'<li><span class="led-lvl">L{_E(str(e["level"]))}</span> '
            f'<span class="led-ts">{_E(e["iso"])}</span> '
            f'<span class="led-who">{_E(e["authorized_by"] or "")}</span>'
            f'<p class="led-prov">{_E(e["provenance"][:600])}'
            f'{"&hellip;" if len(e["provenance"]) > 600 else ""}</p></li>'
            for e in atom["ledger"]
        )
        led = f'<ul class="ledger">{rows}</ul>'
    else:
        led = (
            '<p class="none">No entry in <code>gate_authorizations.jsonl</code>. '
            "This atom&rsquo;s level predates the self-certification ledger, so the level "
            "move itself has no recorded evidence trail.</p>"
        )
    tests = (
        f'<p class="tests">{atom["test_functions"]} test functions defined across '
        f'{atom["test_files"]} cited test file(s) &mdash; counted from the files on disk, '
        "not executed here.</p>"
        if atom["test_files"]
        else '<p class="none">No test file among this atom&rsquo;s cited artefacts.</p>'
    )
    return (
        f'<div class="atom" id="atom-{_E(atom["id"])}">{head}{name}{miss}'
        f'<h4>Artefacts cited by the map</h4>{cits}'
        f'<h4>Tests</h4>{tests}'
        f'<h4>Level record (R16)</h4>{led}</div>'
    )


def _node_html(node: dict) -> str:
    stage = node["computed_stage"]
    agree = (
        ""
        if node["stage_matches"]
        else '<p class="drift">The stage the site declares and the stage its atoms compute '
        f'DISAGREE: declared {_E(str(node["declared_stage"]))}, computed {_E(stage)}.</p>'
    )
    summary = (
        f'<p class="summary">This node&rsquo;s <strong>{_E(stage)}</strong> claim rests on '
        f'<strong>{len(node["atoms"])}</strong> atoms: '
        f'<strong>{node["atoms_at_target"]}</strong> at target, '
        f'<strong>{node["atoms_with_ledger"]}</strong> with a level record in the ledger, '
        f'<strong>{node["atoms_with_missing"]}</strong> with something missing.</p>'
    )
    back = (
        f'<a class="back" href="../#model">&larr; back to the diagram</a>'
        if True
        else ""
    )
    return (
        f'<section class="node-ev" id="{_E(node["id"])}">'
        f'<h2>{_E(node["name"])}'
        f'<span class="stage stage-{_stage_class(stage)}">{_E(stage)}</span></h2>'
        f"{agree}{summary}{back}"
        + "".join(_atom_html(a) for a in node["atoms"])
        + "</section>"
    )


def render_placeholder(payload: dict) -> str:
    """The honest hole. Carries the same reader-facing marker as the site's other early doors,
    so a reader meets one consistent signal rather than three dialects of "not finished"."""
    site_nav = _ia.render_nav("/evidence/", indent="")
    t = payload["totals"]
    nodes = len(payload.get("nodes") or [])
    return f"""<!DOCTYPE html>
<html lang="en-GB">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex">
<title>Evidence — Poesys</title>
<link rel="icon" type="image/svg+xml" href="../favicon.svg">
<link rel="stylesheet" href="../brand/brand.css">
<style>
* {{ box-sizing: border-box; margin: 0; padding: 0; }}
body {{ background: var(--bg); color: var(--text); font-family: system-ui, sans-serif; font-size: 14px; line-height: 1.6; }}
.site-nav {{ background: var(--surface); border-bottom: 1px solid var(--border);
  display: flex; align-items: center; padding: 0 20px; height: 48px; gap: 8px; flex-wrap: wrap; }}
.nav-logo {{ font-weight: 700; color: var(--teal); text-decoration: none; margin-right: 16px; font-size: 15px; }}
.nav-link {{ color: var(--muted); text-decoration: none; padding: 6px 12px; border-radius: 6px; font-size: 13px; }}
.nav-link:hover, .nav-link.active {{ color: var(--text); background: var(--surface2); }}
.nav-spacer {{ flex: 1; }}
main {{ max-width: 760px; margin: 0 auto; padding: 48px 24px 80px; }}
.badge {{ display: inline-block; background: var(--surface2); color: var(--muted);
  border: 1px solid var(--border); border-radius: 999px; padding: 4px 12px; font-size: 12px;
  letter-spacing: .04em; text-transform: uppercase; margin-bottom: 20px; }}
h1 {{ font-size: 30px; line-height: 1.25; margin-bottom: 16px; }}
.lede {{ font-size: 16px; color: var(--muted); margin-bottom: 32px; }}
h2 {{ font-size: 15px; margin: 32px 0 10px; }}
p {{ margin-bottom: 14px; }}
ul {{ margin: 0 0 14px 20px; }} li {{ margin-bottom: 6px; }}
.note {{ border-left: 3px solid var(--border); padding: 12px 16px; background: var(--surface);
  color: var(--muted); font-size: 13px; margin: 24px 0; }}
a {{ color: var(--teal); }}
</style>
</head>
<body>
<nav class="site-nav">
  <a href="../" class="nav-logo">Poesys</a>
{site_nav}
</nav>
<main>
  <span class="badge">This page is being built</span>
  <h1>Evidence behind the claims</h1>
  <p class="lede">
    This page used to exist, and it was taken down on purpose. It was a correct, complete,
    automatically generated record — written in the project's own internal vocabulary, and
    close to unreadable for anyone who does not maintain it.
  </p>

  <h2>What was wrong with it</h2>
  <p>
    It opened by telling you that a claim's status is "computed from the levels of the named
    atoms the claim rests on", and then cited file paths inside the code repository. Those
    sentences are accurate. They are also no use to a reader trying to work out whether to
    believe anything on this site, which is the only reason the page exists.
  </p>

  <h2>What this page will show</h2>
  <ul>
    <li>For each claim the site makes, the specific thing that would have to be true for it to
        hold — in plain words, not internal identifiers.</li>
    <li>What was actually checked, when, and by what — including the checks that failed.</li>
    <li>Where the evidence is thin or missing, said plainly rather than shown as a tidy blank.</li>
    <li>A route to the underlying record for anyone who does want the machine-level detail.</li>
  </ul>

  <h2>Roughly when</h2>
  <p>
    Next, alongside the other two pages being rebuilt. The underlying data is unaffected and is
    still generated and checked on every publish — {nodes} claim areas, {t.get("atoms_total", 0)}
    supporting records — so what is missing is a version of it written for a reader, not the
    evidence itself.
  </p>

  <div class="note">
    <strong>Why a hole rather than the old page.</strong> A page that looks thorough and cannot
    be read is worse than an absence: it invites you to assume it says something it does not.
    Meanwhile <a href="../proof/">Proof</a> carries the corrections record and the known
    limitations in readable form.
  </div>
</main>
<footer style="margin-top:48px;padding:20px 0;border-top:1px solid var(--border);text-align:center;font-size:11px;color:var(--muted);">&copy; 2026 Poesys Platforms. All rights reserved. &middot; <a href="../privacy/" style="color:var(--muted);">Privacy</a></footer>
</body>
</html>
"""


def render_html(payload: dict) -> str:
    t = payload["totals"]
    site_nav = _ia.render_nav("/evidence/", indent="")
    nav = "".join(
        f'<a href="#{_E(n["id"])}">{_E(n["name"])} '
        f'<span class="nav-n">{n["atoms_with_missing"]}/{len(n["atoms"])}</span></a>'
        for n in payload["nodes"]
    )
    return f"""<!DOCTYPE html>
<html lang="en-GB">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Evidence behind the diagram &middot; Poesys</title>
<meta name="description" content="Every node on the model-on-a-page diagram, drilled to the
primary state that substantiates its stage: atom levels, the artefacts cited, the tests, and
the ledger record of each level move.">
<link rel="stylesheet" href="../brand/brand.css">
<style>
/* GENERATED by tools/generate_evidence_data.py -- do not hand-edit. */
.wrap {{ max-width: 900px; margin: 0 auto; padding: 32px 20px 80px; }}
h1 {{ font-size: 26px; letter-spacing: -0.02em; margin: 0 0 8px; }}
.lede {{ color: var(--muted); font-size: 14px; line-height: 1.6; max-width: 62ch; }}
.stamp {{ font-size: 11px; color: var(--muted); margin-top: 14px; }}
.nav {{ display: flex; flex-wrap: wrap; gap: 8px; margin: 22px 0 8px; }}
.nav a {{ font-size: 12px; font-weight: 600; text-decoration: none; color: var(--text);
  border: 1px solid var(--border); border-radius: 6px; padding: 5px 9px; }}
.nav a:hover {{ background: var(--surface2); }}
.nav-n {{ color: var(--muted); font-weight: 400; }}
.totals {{ border: 1px solid var(--border); border-radius: 8px; padding: 14px 16px;
  margin: 18px 0 30px; background: var(--surface); font-size: 13px; line-height: 1.7; }}
.node-ev {{ border-top: 2px solid var(--text); padding-top: 18px; margin-top: 40px;
  scroll-margin-top: 20px; }}
.node-ev h2 {{ font-size: 19px; margin: 0 0 10px; display: flex; align-items: baseline;
  gap: 10px; flex-wrap: wrap; }}
.stage {{ font-size: 10px; font-weight: 700; text-transform: uppercase; letter-spacing: .05em;
  border-radius: 4px; padding: 2px 6px; }}
.stage-live {{ color: var(--green); border: 1px solid var(--green); }}
.stage-building {{ color: var(--amber); border: 1px solid var(--amber); }}
.stage-planned {{ color: var(--muted); border: 1px solid var(--border); }}
.summary {{ font-size: 13px; line-height: 1.7; }}
.drift {{ font-size: 13px; color: var(--red); border-left: 3px solid var(--red);
  padding-left: 10px; }}
.back {{ font-size: 12px; font-weight: 600; }}
.atom {{ border: 1px solid var(--border); border-radius: 8px; padding: 14px 16px;
  margin: 16px 0; background: var(--surface); scroll-margin-top: 20px; }}
.atom-head {{ display: flex; align-items: baseline; gap: 10px; flex-wrap: wrap; }}
.atom-id {{ font-size: 12px; font-weight: 700; }}
.lvl {{ font-size: 10px; font-weight: 700; border-radius: 4px; padding: 1px 5px; }}
.ev-ok {{ color: var(--green); border: 1px solid var(--green); }}
.ev-below {{ color: var(--amber); border: 1px solid var(--amber); }}
.atom-meta {{ font-size: 11px; color: var(--muted); }}
.atom-name {{ font-size: 13px; line-height: 1.6; margin: 8px 0; }}
.atom h4 {{ font-size: 11px; text-transform: uppercase; letter-spacing: .06em;
  color: var(--muted); margin: 16px 0 6px; }}
.cits {{ display: flex; flex-wrap: wrap; gap: 6px; }}
/* SITE1/MAJOR-7: a repo-internal citation is NOT web-servable, so it renders as an inert
   tag -- never an anchor. A dead citation wearing a live link's clothes trains a reader to
   distrust the real ones. */
.evsrc {{ font-size: 11px; color: var(--muted); border: 1px solid var(--border);
  border-radius: 4px; padding: 2px 6px; cursor: help; }}
.evsrc-tag {{ font-size: 8px; border: 1px solid currentColor; border-radius: 3px;
  padding: 0 4px; margin-left: 5px; text-transform: uppercase; letter-spacing: .03em; }}
.evsrc.ev-ok {{ color: var(--muted); border-color: var(--border); }}
.evsrc.ev-moved {{ color: var(--amber); border-color: var(--amber); }}
.evsrc.ev-missing {{ color: var(--red); border-color: var(--red); font-weight: 700; }}
.ev-count {{ font-size: 9px; color: var(--muted); margin-left: 5px; }}
.missing {{ margin: 10px 0; padding-left: 18px; }}
.missing li {{ font-size: 12px; color: var(--muted); line-height: 1.6; }}
.miss-tag {{ font-size: 9px; font-weight: 700; color: var(--red);
  border: 1px solid var(--red); border-radius: 3px; padding: 0 4px; margin-right: 5px; }}
.none {{ font-size: 12px; color: var(--muted); line-height: 1.6; font-style: italic; }}
.tests {{ font-size: 12px; line-height: 1.6; }}
.ledger {{ padding-left: 0; list-style: none; margin: 0; }}
.ledger li {{ border-left: 2px solid var(--border); padding: 2px 0 2px 10px;
  margin-bottom: 10px; }}
.led-lvl {{ font-size: 10px; font-weight: 700; color: var(--blue);
  border: 1px solid var(--blue); border-radius: 3px; padding: 0 4px; }}
.led-ts, .led-who {{ font-size: 11px; color: var(--muted); margin-left: 6px; }}
.led-prov {{ font-size: 12px; line-height: 1.6; margin: 6px 0 0; }}
/* SITE4: the site nav, rendered from site/ia_register.py. Same declarations the other
   fifteen pages carry inline -- this page links brand.css, which styles only
   `.nav-logo.wordmark`, so the layout rules have to live here as they do everywhere else.
   `.nav` above is this page's own node jump-list and is a different thing. */
.site-nav {{ background: var(--surface); border-bottom: 1px solid var(--border);
  display: flex; align-items: center; padding: 0 20px; height: 48px; gap: 8px; flex-wrap: wrap; }}
.nav-logo {{ font-weight: 700; color: var(--teal); text-decoration: none; margin-right: 16px; font-size: 15px; }}
.nav-link {{ color: var(--muted); text-decoration: none; padding: 6px 12px; border-radius: 6px; font-size: 13px; }}
.nav-link:hover, .nav-link.active {{ color: var(--text); background: var(--surface2); }}
</style>
</head>
<body>
<nav class="site-nav">
<a href="../" class="nav-logo wordmark">poesys.</a>
{site_nav}
</nav>
<div class="wrap">
<h1>Evidence behind the diagram</h1>
<p class="lede">Each node on the <a href="../#model">model-on-a-page diagram</a> claims a
stage &mdash; Live, Building or Planned. That word is not an opinion: it is computed from the
levels of the named atoms the claim rests on. This page is the drill. For every node it shows
those atoms, the artefacts the map cites for each, the tests, and the ledger entry that
recorded the level move &mdash; and, where any of that is absent, it says so rather than
showing a tidy blank.</p>
<p class="lede"><strong>Nothing here is hand-typed.</strong> Every figure and path on this page
is generated from <code>{_E(payload["sources"]["node_mapping"])}</code>,
<code>{_E(payload["sources"]["maturity_map"])}</code>,
<code>{_E(payload["sources"]["ledger"])}</code> and
<code>{_E(payload["sources"]["test_execution_log"])}</code>. Citations are shown as inert tags
carrying their disk status, never as links: these are repo paths, not web pages, and a dead
citation dressed as a live link is the defect this page exists to avoid.</p>
<p class="stamp">Generated {_E(payload["generated_at"])} at commit
<code>{_E(payload["git_hash"])}</code>. Largest recorded pytest collection:
<strong>{payload["suite"]["test_count"]}</strong> tests
({_E(str(payload["suite"]["timestamp"]))}) &mdash; the biggest run ever logged, not the most
recent, so a partial run cannot shrink the figure.</p>
<div class="nav">{nav}</div>
<div class="totals">
<strong>{t["nodes"]}</strong> diagram nodes &middot;
<strong>{t["atoms"]}</strong> atoms carrying their claims &middot;
<strong>{t["citations"]}</strong> cited artefacts, of which
<strong>{t["citations_resolved"]}</strong> resolve on disk,
<strong>{t["citations_relocated"]}</strong> have been archived to a new path, and
<strong>{t["citations_missing"]}</strong> do not exist anywhere &mdash; shown in red below.
<strong>{t["atoms_with_missing"]}</strong> of {t["atoms"]} atoms have at least one thing
missing; <strong>{t["nodes_fully_evidenced"]}</strong> of {t["nodes"]} nodes are complete on
every atom.
</div>
{"".join(_node_html(n) for n in payload["nodes"])}
</div>
<footer style="margin-top:48px;padding:20px 0;border-top:1px solid var(--border);text-align:center;font-size:11px;color:var(--muted);">&copy; 2026 Poesys Platforms. All rights reserved.</footer>
</body>
</html>
"""


# --- entry point -------------------------------------------------------------


def generate(git_hash: str | None = None, write_page: bool | None = None) -> dict:
    """Write site/data/evidence.json -- and site/evidence/index.html only if that door still exists.

    Safe to call from background/process_run_complete.py: on a missing/empty source it raises
    EvidenceSourceUnavailable BEFORE writing anything, so the publish step logs the failure
    and the previous page stays live rather than being replaced by a plausible blank.

    THE PAGE CAN NO LONGER BE RESURRECTED BY THIS FUNCTION (2026-08-22). `/evidence/` was
    deleted on 2026-08-20 (director: the five tabs are the site) and this generator recreated
    it thirty minutes later, because it ran `OUT_HTML.parent.mkdir()` unconditionally -- so the
    publish cycle had to drop the call entirely to keep the door dead. That took the PAYLOAD
    down with the page, and the payload has a SECOND consumer: `generate_capabilities_door`
    reads `site/data/evidence.json` for the "Checked by N automated checks, last run <date>"
    line on the live Capabilities door. Observed 2026-08-22: `capabilities_door.json`
    regenerated at 10:02:21Z was still publishing `last_run 2026-08-20T05:08:54Z` to nine
    capabilities, and would have kept doing so indefinitely -- a stale claim inside a fresh
    feed, which is worse than a stale page because nothing about it looks old.

    The refusal belongs HERE, at the sink, not in the caller: a guard in the publish path is
    one caller's discipline, and this is the function that did the resurrecting. `write_page`
    defaults to "the door's directory already exists" -- an absent directory is never created,
    so wiring this back into the cycle cannot bring a retired page back. Pass it explicitly
    only to pin the behaviour in a test.
    """
    # Sources passed EXPLICITLY from the module globals rather than relying on build_payload's
    # defaults: a default argument binds once at definition time, so a redirected source path
    # would have been silently ignored -- which also made the "writes nothing on an
    # unavailable source" guarantee untestable, and an untestable guarantee is not one.
    payload = build_payload(
        map_path=MAP_PATH,
        mapping_path=MAPPING_PATH,
        ledger_path=LEDGER_PATH,
        suite_log_path=SUITE_LOG_PATH,
    )
    if git_hash:
        payload["git_hash"] = git_hash
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    # The DATA is written unconditionally; only the RENDERING is held back. See
    # EVIDENCE_READER_READY for why that split is the whole point.
    if OUT_HTML.parent.is_dir() if write_page is None else write_page:
        OUT_HTML.parent.mkdir(parents=True, exist_ok=True)
        OUT_HTML.write_text(
            render_html(payload) if EVIDENCE_READER_READY else render_placeholder(payload),
            encoding="utf-8")
    return payload


def main() -> int:
    try:
        payload = generate()
    except EvidenceSourceUnavailable as exc:
        print(f"EVIDENCE SOURCE UNAVAILABLE (nothing written): {exc}")
        return 2
    t = payload["totals"]
    print("=== evidence pages behind the diagram nodes ===\n")
    for n in payload["nodes"]:
        print(
            f'{n["name"]:22s} {n["computed_stage"]:9s} atoms={len(n["atoms"]):2d} '
            f'at_target={n["atoms_at_target"]:2d} ledger={n["atoms_with_ledger"]:2d} '
            f'incomplete={n["atoms_with_missing"]:2d}'
        )
    print(
        f'\ncitations: {t["citations"]} total / {t["citations_resolved"]} resolved / '
        f'{t["citations_relocated"]} relocated / {t["citations_missing"]} MISSING'
    )
    found = findings(payload)
    print(f"\nFINDINGS: {len(found)}")
    for kind, subject, detail in found:
        print(f"  [{kind}] {subject}: {detail}")
    # Named from what is ON DISK afterwards rather than from the intent: this tool printed
    # "wrote <page>" for two days while writing no page at all would have been the honest line.
    wrote = str(OUT_JSON.relative_to(PROJECT))
    if OUT_HTML.is_file():
        wrote += f" and {OUT_HTML.relative_to(PROJECT)}"
    else:
        wrote += f" (no page: {OUT_HTML.parent.relative_to(PROJECT)} is retired)"
    print(f"\nwrote {wrote}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
