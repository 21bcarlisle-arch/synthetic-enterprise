"""The map: one concept register in, every link and every gap generated out.

Director steers of 24 Oct (`docs/staging/advisor/DIRECTOR_STEER_THE_MAP_ONE_CONCEPT_REGISTER_FOUR_SPINES_AND_A_KNOWLEDGE_PLAN_2026-10-24.md`,
"Do that"; and its SKOS refinement, "Yes"). The register is `docs/design/the_map/concepts.yaml`,
small and curated. This module reads it and joins it to what the tree already carries, so the
register holds no list of links that could drift:

  pages      -- `site/data/knowledge_topics.json`, by the concept's `page`.
  notes      -- `docs/market_research/*.md` that name the page in their own `**Knowledge:**` line,
                or that the page's rungs cite by file name.
  modules    -- the declared home per layer, graded by `tools.capability_index` (wired, orphan,
                entrypoint, or gone). Every other module whose name or first docstring sentence
                carries one of the concept's names is listed as `also_named`: a second home, or a
                module that belongs here and does not say so. That list is the point of altLabel.
  atoms      -- live maturity-map atoms whose `file_scope` names a home's path.
  controls   -- `docs/design/canon_mechanisms.yaml` rows that name a home's path, and for How it's
                built the rule's own mechanisms.
  links      -- the register's relations, both directions, so a concept shows what points at it.

`python3 -m tools.the_map` prints the report; `--json` prints the generated map. Reporting only:
it exits 0 whatever it finds, until the backlog it exposes is planned (steer item 3).
"""
from __future__ import annotations

import argparse
import functools
import json
import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
REGISTER = "docs/design/the_map/concepts.yaml"
RULINGS = "docs/design/the_map/note_rulings.yaml"
PAGES = "site/data/knowledge_topics.json"
NOTES_DIR = "docs/market_research"
MECHANISMS = "docs/design/canon_mechanisms.yaml"

#: Which roots a world, wall or supplier module may come from. The wall is the seam package only.
LAYER_ROOTS = {
    "world": ("simulation.", "sim."),
    "wall": ("company.interfaces.",),
    "supplier": ("company.", "saas."),
}
LAYERS = ("world", "wall", "supplier")
RELATIONS = ("feeds", "depends_on", "graded_by", "causes")
#: A world or supplier concept needs these layers, or a `gap` saying why not. A belief or measure
#: lives on the supplier side and needs its grade or its code instead of a world rule.
NEEDS = {
    None: ("page", "world", "wall", "supplier", "match"),
    "belief": ("supplier", "graded_by", "match"),
    "measure": ("page", "computed_by", "match"),
}
BUILD_NEEDS = ("match", "rule", "enforced_by", "evidence")

_KNOWLEDGE_LINE = re.compile(r"^\*\*Knowledge:\*\*\s*`?([a-z0-9-]+)`?", re.M)


HOOK = "tools/git-hooks/pre-commit"


def _text(path: Path) -> str:
    """Every file this module matches text in is Markdown, JSON, YAML or the shell hook; never Python."""
    if path.suffix not in (".md", ".json", ".yaml") and not str(path).endswith(HOOK):
        raise ValueError(f"{path}: the map reads Python through capability_index, not as text")
    return path.read_text(encoding="utf-8", errors="replace")


def load_register(root: Path = ROOT) -> dict:
    return yaml.safe_load(_text(root / REGISTER))


def _terms(concept: dict) -> list[str]:
    return [t.lower() for t in [concept["prefLabel"], *concept.get("altLabel", [])]]


def _term_pattern(term: str) -> re.Pattern:
    words = [re.escape(w) for w in re.split(r"[\s_'-]+", term) if w]
    return re.compile(r"\b" + r"[\s_'-]*".join(words) + r"s?\b")


def _searchable(row: dict) -> str:
    """A module's own name, as words, and its first docstring sentence: what it says it is."""
    name = row["module"].rsplit(".", 1)[-1].replace("_", " ")
    return f"{name} | {row.get('plain_words') or ''}".lower()


def load_rulings(root: Path = ROOT) -> dict:
    """Steer item 4's ruling on each note no page cites: attach / owed / dead. Absent file, no rulings."""
    path = root / RULINGS
    return (yaml.safe_load(_text(path)) or {}) if path.exists() else {}


def notes_by_page(root: Path = ROOT, pages: dict | None = None) -> dict[str, set[str]]:
    """{page id: the notes that attach to it}, by the note's own line, the page's citation, or a ruling."""
    out: dict[str, set[str]] = {}
    for page_id, stems in (load_rulings(root).get("attach") or {}).items():
        out.setdefault(page_id, set()).update(stems)
    for note in sorted((root / NOTES_DIR).glob("*.md")):
        found = _KNOWLEDGE_LINE.search(_text(note))
        if found and found.group(1) != "none":
            out.setdefault(found.group(1), set()).add(note.stem)
    for page_id, page in (pages or {}).items():
        text = json.dumps(page)
        for cited in re.findall(r"([a-z0-9_]+)\.md", text):
            if (root / NOTES_DIR / f"{cited}.md").exists():
                out.setdefault(page_id, set()).add(cited)
    return out


def note_coverage(root: Path = ROOT, pages: dict | None = None) -> dict:
    """How many research notes attach to some published page, and how many to none."""
    attached = set().union(*notes_by_page(root, pages).values()) if pages is not None else set()
    every = {p.stem for p in (root / NOTES_DIR).glob("*.md")}
    return {"notes": len(every), "on_a_page": len(attached & every),
            "on_no_page": sorted(every - attached)}


def ruling_counts(root: Path, unattached: set[str]) -> dict:
    """Of the notes on no page, how many are ruled owed (a page is coming), dead, or not ruled at all."""
    rulings = load_rulings(root)
    owed = {n for ns in (rulings.get("owed") or {}).values() for n in ns} & unattached
    dead = {n for row in rulings.get("dead") or [] if row.get("reason") for n in row.get("notes", [])} & unattached
    return {"owed": len(owed), "dead": len(dead), "unruled": len(unattached - owed - dead)}


def coverage(root: Path, pages: dict, rows: list[dict], concepts: list[dict], reg: dict) -> dict:
    """Steer item 3's three checks as counts. A page or note is covered when a concept's page is it
    (or cites it); a module is covered when a concept declares it or lists it as also named, or the
    register's `machinery` list (prefix + reason) rules it plumbing. Layer gaps are the findings."""
    on_concept = {c["page"]["id"] for c in concepts if c.get("page")}
    by_page = notes_by_page(root, pages)
    every = {p.stem for p in (root / NOTES_DIR).glob("*.md")}
    noted = set().union(*(by_page.get(p, set()) for p in on_concept)) & every
    machinery = [m for m in reg.get("machinery") or [] if m.get("prefix") and m.get("reason")]
    mods = [r["module"] for r in rows if r["module"].startswith(("simulation.", "sim.", "company.", "saas."))]
    attached = {m["module"] for c in concepts for layer in LAYERS for m in c.get(layer, [])}
    attached |= {m["module"] for c in concepts for m in c.get("also_named", [])}
    plumbing = {m for m in mods if any(m.startswith(x["prefix"]) for x in machinery)}
    loose = sorted(set(mods) - attached - plumbing)
    return {"pages": {"total": len(pages), "on_a_concept": len(on_concept & set(pages)),
                      "on_none": sorted(set(pages) - on_concept)},
            "notes": {"total": len(every), "on_a_concept": len(noted), "on_none": len(every - noted),
                      "on_no_page": len(every - set().union(*by_page.values())),
                      **ruling_counts(root, every - set().union(*by_page.values()))},
            "modules": {"total": len(mods), "on_a_concept": len(set(mods) & attached),
                        "machinery": len(plumbing - attached), "on_none": len(loose), "sample_on_none": loose[:10]}}


# --- How it's built: each evidence figure has one function, named in the register -------------

def mutation_recorded_share(root: Path, rows: list[dict]) -> str | None:
    from tools.harness_page_figures import _mutation_index
    marked, total = _mutation_index(root)
    if marked is None:
        return None
    return f"{len(marked)} of {total} test files record the mutation that put their defect back"


def gate_hook_count(root: Path, rows: list[dict]) -> str | None:
    if not (root / HOOK).exists():
        return None
    calls = re.findall(r"^\s*(?:python3?|\"\$PY\"|\$PY)\s+(?:-m\s+)?(\S+)", _text(root / HOOK), re.M)
    return f"{len(set(calls))} distinct checks named in the pre-commit hook" if calls else None


def orphan_count(root: Path, rows: list[dict]) -> str | None:
    gone = [r for r in rows if r["status"] == "orphan" and r["module"].startswith(("company.", "saas."))]
    lines = sum(len((root / r["path"]).read_text(encoding="utf-8", errors="replace").splitlines())
                for r in gone)
    return f"{len(gone)} supplier modules nothing imports and no command runs, {lines:,} lines"


def second_homes_on_the_map(root: Path, rows: list[dict], concepts: list[dict] | None = None) -> str | None:
    if concepts is None:
        return None
    pairs = [m["module"] for c in concepts for m in c.get("also_named", [])]
    return (f"{len(set(pairs))} modules ({len(pairs)} module-concept pairs) carry a mapped concept's "
            "name and are not its declared home")


EVIDENCE = {f.__name__: f for f in (mutation_recorded_share, gate_hook_count, orphan_count)}


@functools.lru_cache(maxsize=2)
def _index_rows(root: Path) -> list[dict]:
    """The capability index, built once per process: it is most of the map's 20 seconds."""
    from tools import capability_index
    return capability_index.build_rows(root)


# --- the build ---------------------------------------------------------------------------------

def build(root: Path = ROOT, rows: list[dict] | None = None) -> dict:
    if rows is None:
        rows = _index_rows(root)
    by_module = {r["module"]: r for r in rows}
    reg = load_register(root)
    pages = json.loads(_text(root / PAGES))["pages"]
    notes = notes_by_page(root, pages)
    mechanisms = (yaml.safe_load(_text(root / MECHANISMS)) or {}).get("principles", {})
    try:
        from tools import maturity_map_store
        atoms = maturity_map_store.load_live_atoms(root / maturity_map_store.MAP_REL)
    except Exception:  # the map is reported, never blocked, by a store it cannot read
        atoms = []
    ids = {c["id"] for c in reg["concepts"]}
    concepts, findings = [], []

    term_owner: dict[str, str] = {}
    for c in reg["concepts"]:
        for t in _terms(c):
            if t in term_owner and term_owner[t] != c["id"]:
                findings.append({"kind": "one name, two concepts", "concept": c["id"],
                                 "detail": f"'{t}' also names {term_owner[t]}"})
            term_owner.setdefault(t, c["id"])

    for c in reg["concepts"]:
        out = {k: c[k] for k in ("id", "prefLabel", "definition", "placed") if k in c}
        out.update({k: c[k] for k in ("altLabel", "match", "kind", "built_from", "decides", "measure", "gap") if k in c})
        gaps = dict(c.get("gap") or {})
        is_build = all(p.startswith("build/") for p in c.get("placed", []))
        homes = []
        for layer in LAYERS:
            graded = []
            for mod in c.get(layer, []):
                row = by_module.get(mod)
                status = row["status"] if row else "gone"
                if row and not mod.startswith(LAYER_ROOTS[layer]):
                    status = "wrong side"
                graded.append({"module": mod, "status": status,
                               "callers": len(row["callers"]) if row else 0,
                               "tests": len(row["evidence"]) if row else 0,
                               "path": row["path"] if row else None})
                if row:
                    homes.append(row["path"])
                if status in ("gone", "orphan", "wrong side"):
                    findings.append({"kind": f"home {status}", "concept": c["id"], "detail": f"{layer}: {mod}"})
            if graded:
                out[layer] = graded

        if not is_build:
            pats = [_term_pattern(t) for t in _terms(c)]
            declared = {m for layer in LAYERS for m in c.get(layer, [])}
            out["also_named"] = [{"module": r["module"], "status": r["status"]}
                                 for r in sorted(rows, key=lambda r: r["module"])
                                 if r["module"].startswith(("simulation.", "sim.", "company.", "saas."))
                                 and r["module"] not in declared
                                 and any(p.search(_searchable(r)) for p in pats)]

        if c.get("page"):
            out["page"] = {"id": c["page"], "published": c["page"] in pages,
                           "notes": sorted(notes.get(c["page"], ()))}
            if c["page"] not in pages:
                findings.append({"kind": "page not published", "concept": c["id"], "detail": c["page"]})

        out["atoms"] = sorted({a["id"] for a in atoms for scope in [a.get("file_scope") or []]
                               for h in homes if any(h == s or h.startswith(s.rstrip("/") + "/")
                                                     for s in (scope if isinstance(scope, list) else [scope])
                                                     if isinstance(s, str) and s.endswith(".py"))})
        out["controls"] = sorted(pid for pid, row in mechanisms.items()
                                 if set((row or {}).get("mechanisms", [])) & (set(homes) | set(c.get("enforced_by", []))))

        if is_build:
            rule = c.get("rule")
            out["rule"] = rule
            out["rule_mechanisms"] = (mechanisms.get(rule) or {}).get("mechanisms", []) if rule else []
            out["enforced_by"] = [{"path": p, "exists": (root / p).exists()} for p in c.get("enforced_by", [])]
            for p in out["enforced_by"]:
                if not p["exists"]:
                    findings.append({"kind": "named, but gone", "concept": c["id"], "detail": p["path"]})
            fn = EVIDENCE.get(c.get("evidence"))
            out["evidence"] = fn(root, rows) if fn else None
            needs = BUILD_NEEDS
        else:
            needs = NEEDS.get(c.get("kind"), NEEDS[None])

        missing = []
        for need in needs:
            have = {"page": c.get("page"), "match": c.get("match"), "graded_by": (c.get("relations") or {}).get("graded_by"),
                    "computed_by": (c.get("measure") or {}).get("computed_by"), "rule": c.get("rule"),
                    "enforced_by": c.get("enforced_by"),
                    "evidence": out.get("evidence") or c.get("evidence") == "second_homes_on_the_map"}.get(need, c.get(need))
            if not have:
                missing.append(need)
                if need not in gaps:
                    findings.append({"kind": "layer missing, no reason", "concept": c["id"], "detail": need})
        out["missing"] = missing
        concepts.append(out)

    links = []
    for c in reg["concepts"]:
        for rel in RELATIONS:
            for target in (c.get("relations") or {}).get(rel, []):
                if target not in ids:
                    findings.append({"kind": "relation to no concept", "concept": c["id"], "detail": f"{rel} {target}"})
                links.append({"from": c["id"], "rel": rel, "to": target})
    for out in concepts:
        out["links"] = ([{"rel": link["rel"], "to": link["to"]} for link in links if link["from"] == out["id"]]
                        + [{"rel": f"{link['rel']} (from)", "to": link["from"]} for link in links if link["to"] == out["id"]])

    for out in concepts:
        if out.get("also_named"):
            findings.append({"kind": "also named, not declared", "concept": out["id"],
                             "detail": f"{len(out['also_named'])} modules"})
    for c, out in zip(reg["concepts"], concepts):
        if c.get("evidence") == "second_homes_on_the_map":
            out["evidence"] = second_homes_on_the_map(root, rows, concepts)

    cov = coverage(root, pages, rows, concepts, reg)
    cov["layers"] = {"concepts": len(concepts), "with_a_missing_layer": sum(1 for c in concepts if c["missing"]),
                     "missing_without_reason": sum(1 for f in findings if f["kind"] == "layer missing, no reason")}
    return {"register": REGISTER, "spines": reg["spines"], "concepts": concepts, "links": links,
            "findings": findings, "notes": note_coverage(root, pages), "coverage": cov}


def report(the_map: dict) -> str:
    lines = []
    for c in the_map["concepts"]:
        lines.append(f"\n{c['id']}  {c['prefLabel']}  [{', '.join(c.get('placed', []))}]")
        if c.get("page"):
            p = c["page"]
            lines.append(f"  page    {p['id']} ({'published' if p['published'] else 'NOT PUBLISHED'}), "
                         f"{len(p['notes'])} notes")
        for layer in LAYERS:
            for m in c.get(layer, []):
                lines.append(f"  {layer:8}{m['module']}  {m['status']}, {m['callers']} callers, {m['tests']} tests")
        if "rule" in c:
            lines.append(f"  rule    {c['rule']}  mechanisms: {', '.join(c['rule_mechanisms']) or 'none named'}")
            lines.append(f"  evidence {c.get('evidence') or 'none computed'}")
        if c.get("also_named"):
            lines.append(f"  also named ({len(c['also_named'])}): "
                         + ", ".join(f"{m['module']} ({m['status']})" for m in c["also_named"]))
        if c.get("atoms"):
            lines.append(f"  atoms   {', '.join(c['atoms'])}")
        for need in c.get("missing", []):
            lines.append(f"  missing {need}: {(c.get('gap') or {}).get(need, 'NO REASON RECORDED')}")
        for link in c["links"]:
            lines.append(f"  -> {link['rel']} {link['to']}")
    counts: dict[str, int] = {}
    for f in the_map["findings"]:
        counts[f["kind"]] = counts.get(f["kind"], 0) + 1
    n = the_map["notes"]
    lines.append(f"\nfindings by kind: {json.dumps(counts)}")
    lines.append(f"research notes: {n['on_a_page']} of {n['notes']} attach to a published page, "
                 f"{len(n['on_no_page'])} to none")
    return "\n".join(lines)


def summary(the_map: dict) -> str:
    """The counts, for the Monday end-to-end step: findings by kind, each finding, note coverage."""
    counts: dict[str, int] = {}
    for f in the_map["findings"]:
        counts[f["kind"]] = counts.get(f["kind"], 0) + 1
    n = the_map["notes"]
    lines = [f"{len(the_map['concepts'])} concepts registered; "
             + (", ".join(f"{v} {k}" for k, v in sorted(counts.items())) or "no findings") + ".",
             f"{n['on_a_page']} of {n['notes']} research notes attach to a published page; "
             f"{len(n['on_no_page'])} attach to none.", ""]
    cv = the_map.get("coverage")
    if cv:
        lines += [f"Coverage (reporting only): {cv['pages']['on_a_concept']} of {cv['pages']['total']} published pages "
                  f"sit on a concept; {cv['notes']['on_a_concept']} of {cv['notes']['total']} notes attach to a page a concept uses; "
                  f"{cv['notes']['on_no_page']} notes sit on no page ({cv['notes']['owed']} ruled owed a page, "
                  f"{cv['notes']['dead']} ruled dead, {cv['notes']['unruled']} unruled); "
                  f"{cv['modules']['on_a_concept']} of {cv['modules']['total']} supplier and world modules attach to a concept "
                  f"({cv['modules']['machinery']} more declared machinery, {cv['modules']['on_none']} on none); "
                  f"{cv['layers']['with_a_missing_layer']} of {cv['layers']['concepts']} concepts miss a layer, "
                  f"{cv['layers']['missing_without_reason']} with no recorded reason.", ""]
    lines += [f"- {f['kind']}: {f['concept']} -- {f['detail']}" for f in the_map["findings"]]
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--json", action="store_true", help="print the generated map")
    args = ap.parse_args(argv)
    the_map = build()
    print(json.dumps(the_map, indent=1) if args.json else report(the_map))
    return 0


if __name__ == "__main__":
    sys.exit(main())
