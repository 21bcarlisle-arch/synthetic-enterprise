"""What the project has learned, read from the canon at publish: each principle, and the code that holds it.

Director, 23 Oct 2026 09:27 (advisor channel, DIRECTOR_STEER_SHOW_EVERYTHING_WE_HAVE_LEARNED_FROM_THE
_RECORD_NOT_FROM_MEMORY): "It feels we've learned and done more than all of this along the way." The
steer asks for each lesson as a chain -- what happened, the principle, the mechanism that enforces it
or plainly "prose only", and live evidence that the mechanism fires -- mined from the record, never
hand-curated, with the share that reaches the mechanism as the headline "whichever way it reads".

The principles and their plain words come from `docs/design/DIRECTOR_CANON.md` itself, so the page
says what the canon says today. Which code holds a principle CANNOT be read from the record: the
canon names its own enforcing code for 3 of its 168 principles, and code cites canon ids in a form
that collides with other id families (a bare-id join reads 134 of 168 "held", nearly all of it
noise; the unambiguous form "canon X1" reaches 7). So the binding is a file of judgements,
`docs/design/canon_mechanisms.yaml`, and the page counts an unbound principle as unbound -- "no
mechanism named yet" -- rather than as enforced or as prose only, because nobody has told those two
apart. The evidence step is the project's own standard: a test that records the MUTATION that put
its defect back (`harness_page_figures._mutation_index`).

The control: a bound path that has left the tree is "named, but gone", and `--check` exits 1 naming
it, because a binding that rots silently would keep printing a mechanism that no longer exists.
"""
from __future__ import annotations

import argparse
import html
import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
CANON = "docs/design/DIRECTOR_CANON.md"
BINDINGS = "docs/design/canon_mechanisms.yaml"

_AREA = re.compile(r"^## (\d+)\. (.+?)(?: \(([A-Z]+)\))?(?: — .*)?$")
_PRINCIPLE = re.compile(r"^\*\*([A-Z]{1,2}\d+)\. (.+?)\*\*\s*(.*)$")
_WHEN_ANY = re.compile(r"\*\(([^()]*(?:\([^()]*\)[^()]*)*)\)\*")
# The numbered areas hold principles; 15 (the rulings and what is owed) and 16 (superseded) do not.
LAST_PRINCIPLE_AREA = 14

HELD_PROVEN = "held, and shown able to fail"
HELD = "held, not yet shown able to fail"
GONE = "named, but gone"
UNBOUND = "no mechanism named yet"


def _plain(text):
    return re.sub(r"[`*]", "", text).strip()


def _first_sentence(text, limit=240):
    text = _plain(text)
    # The end of a sentence is never inside a quotation: his words are not cut mid-ruling.
    ends = [m.start() for m in re.finditer(r"(?<=[.!?\"”])\s", text)
            if text[:m.start()].count('"') % 2 == 0]
    out = text[:ends[0]] if ends else text
    return out if len(out) <= limit else out[:limit - 1].rstrip() + "…"


def principles(root=ROOT):
    """[{id, title, area, words, when}] in canon order, or None when the canon cannot be read."""
    try:
        # The literal, not CANON: the census of source scans reads what a scope opens from the
        # scope itself, and this one reads markdown, never Python.
        lines = (Path(root) / "docs/design/DIRECTOR_CANON.md").read_text(
            encoding="utf-8").splitlines()
    except OSError:
        return None
    found, area, n = [], None, 0
    for line in lines:
        a = _AREA.match(line)
        if a or line.startswith("#") or line.strip() == "---":
            n, area = (int(a.group(1)), a.group(2).strip()) if a else (n, area)
            if line.startswith("## ") and not a:
                n = 99
            found.append(None)
            continue
        p = _PRINCIPLE.match(line)
        if p and area and n <= LAST_PRINCIPLE_AREA:
            found.append([p.group(1), p.group(2), area, [p.group(3)]])
        elif found and found[-1] and line.strip():
            # A principle's text can run on below its title line, as a list or a quotation.
            found[-1][3].append(re.sub(r"^\s*(?:[-*>]|\d+\.)\s+", "", line))
        elif found and found[-1] and not line.strip() and found[-1][3] != [""]:
            found[-1][3].append("")
    out = []
    for pid, title, area, body in (f for f in found if f):
        text = " ".join(b for b in body if b).strip()
        whens = _WHEN_ANY.findall(text)
        out.append({"id": pid, "title": _plain(title).rstrip("."), "area": area,
                    "words": _first_sentence(_WHEN_ANY.sub("", text)),
                    "when": _plain(whens[-1]).rstrip(".") if whens else ""})
    return out


def load_bindings(root=ROOT):
    try:
        data = yaml.safe_load((Path(root) / BINDINGS).read_text(encoding="utf-8")) or {}
    except (OSError, yaml.YAMLError):
        return None
    return {k: list((v or {}).get("mechanisms") or []) for k, v in
            (data.get("principles") or {}).items()}


def _shown(path, marked):
    """How many mutation-marked tests stand behind one mechanism path."""
    if path in marked:
        return 1
    stem = re.compile(r"\b{}\b".format(re.escape(Path(path).stem)))
    return sum(1 for f, text in marked.items() if f != path and stem.search(text))


def build(root=ROOT, marked=None):
    """{rows, counts, unknown_ids} or None when the canon or the bindings cannot be read."""
    rows, bindings = principles(root), load_bindings(root)
    if rows is None or bindings is None:
        return None
    if marked is None:
        from tools.harness_page_figures import _mutation_index
        marked = _mutation_index(root)[0] or {}
    known = {r["id"] for r in rows}
    for r in rows:
        paths = bindings.get(r["id"], [])
        gone = [p for p in paths if not (Path(root) / p).exists()]
        shown = sum(_shown(p, marked) for p in paths if p not in gone)
        r.update(mechanisms=paths, gone=gone, shown=shown,
                 status=(UNBOUND if not paths else GONE if gone
                         else HELD_PROVEN if shown else HELD))
    counts = {s: sum(1 for r in rows if r["status"] == s)
              for s in (HELD_PROVEN, HELD, GONE, UNBOUND)}
    return {"rows": rows, "counts": counts, "total": len(rows),
            "unknown_ids": sorted(set(bindings) - known)}


def problems(result):
    """Why --check refuses: a bound path that is gone, or a binding to a principle the canon lacks."""
    if result is None:
        return ["the canon or {} could not be read".format(BINDINGS)]
    out = ["{}: {} names {}, which is not in the tree".format(r["id"], BINDINGS, ", ".join(r["gone"]))
           for r in result["rows"] if r["gone"]]
    out += ["{}: bound in {} but the canon has no such principle".format(i, BINDINGS)
            for i in result["unknown_ids"]]
    return out


def render_html(result):
    if result is None:
        return ('<p class="sub">The canon or its list of mechanisms could not be read at this '
                'publish, so no principle is shown.</p>')
    c, total = result["counts"], result["total"]
    bound = total - c[UNBOUND]
    head = ('<p class="brief-s"><b>{} of the canon\'s {} principles name the code that holds '
            'them, and {} of those have a test that has been seen to fail on its own defect.</b> '
            'The other {} are not yet linked to any code. Some are held by checks nobody has '
            'linked, and some are prose only: we have not yet told those apart, so none of them '
            'is counted as enforced.{}</p>').format(
        bound, total, c[HELD_PROVEN], c[UNBOUND],
        " {} name code that has since left the build.".format(c[GONE]) if c[GONE] else "")
    areas = []
    for area in dict.fromkeys(r["area"] for r in result["rows"]):
        rows = [r for r in result["rows"] if r["area"] == area]
        n = sum(1 for r in rows if r["status"] != UNBOUND)
        items = []
        for r in rows:
            mech = (" Held by {}.".format(", ".join(
                "<code>{}</code>".format(html.escape(p)) for p in r["mechanisms"]))
                if r["mechanisms"] else "")
            items.append('  <li><b>{}.</b> {} <span class="wd">{}{}</span><br>'
                         '<span class="sub">{}{}{}</span></li>'.format(
                html.escape(r["title"]), html.escape(r["words"]), html.escape(r["status"]),
                ", {:,} test{}".format(r["shown"], "" if r["shown"] == 1 else "s")
                if r["shown"] else "", mech,
                " Ruled: {}.".format(html.escape(r["when"])) if r["when"] else "",
                " Canon {}.".format(html.escape(r["id"]))))
        areas.append('<details class="more"><summary>{} ({} of {} linked to code)</summary>\n'
                     '<ul class="week">\n{}\n</ul></details>'.format(
                         html.escape(area), n, len(rows), "\n".join(items)))
    return head + "\n" + "\n".join(areas)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--check", action="store_true",
                    help="exit 1 when a bound mechanism is gone or a binding names no principle")
    args = ap.parse_args(argv)
    result = build(ROOT)
    if args.check:
        bad = problems(result)
        for line in bad:
            print("REFUSED: " + line)
        return 1 if bad else 0
    if result:
        print("{total} principles: ".format(**result) + "; ".join(
            "{} {}".format(v, k) for k, v in result["counts"].items()))
    return 0 if result else 1


if __name__ == "__main__":
    sys.exit(main())
