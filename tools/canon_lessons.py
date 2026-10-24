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


def _first_sentence(text):
    text = _plain(text)
    # The end of a sentence is never inside a quotation: his words are not cut mid-ruling.
    # Nor mid-word: a clipped canon sentence reads as a misquote to tools/canon_drift_check.
    ends = [m.start() for m in re.finditer(r"(?<=[.!?\"”])\s", text)
            if text[:m.start()].count('"') % 2 == 0]
    return text[:ends[0]] if ends else text


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


#: How many chains are lifted into cards above the full list. The steer asked for "a handful".
CARDS = 5
_MONTHS = "Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec".split()


def _date(iso):
    y, m, d = iso[:10].split("-")
    return "{} {} {}".format(int(d), _MONTHS[int(m) - 1], y)


def _rule_title(words, july_name):
    """A rule's card title in the canon's current words when they are short enough to be one, so
    a rule reworded since July (R8 lost its NTFY clause) is not headed by its retired name."""
    short = re.sub(r"\s*\([^)]*\)", "", _first_sentence(words)).strip().rstrip(".")
    short = re.split(r"[:;]", short)[0].strip()
    return short if short and '"' not in short and len(short) <= 80 else july_name


def _held(root, marked, paths):
    present = [(p, (Path(root) / p).exists()) for p in paths]
    gone = [p for p, ok in present if not ok]
    shown = sum(_shown(p, marked) for p, ok in present if ok)
    return dict(mechanisms=paths, gone=gone, shown=shown,
                status=(UNBOUND if not paths else GONE if gone
                        else HELD_PROVEN if shown else HELD))


def chains(root=ROOT, marked=None, rules=None, classes=None):
    """Each lesson as a chain, newest first: what happened, the principle, what holds it, and the
    evidence that the holding code can fail. None when the canon or the bindings cannot be read.

    Two sources, both read at publish: the permanent rules (canon H1 wording, with the incident
    each was learned from in generate_proof_data.RULES) and the registered classes of mistake
    (background/finding_classes.CLASSES). Which code holds a lesson is a judgement in BINDINGS,
    for the reason the module docstring gives; an unbound lesson says so beside itself."""
    try:
        data = yaml.safe_load((Path(root) / BINDINGS).read_text(encoding="utf-8")) or {}
    except (OSError, yaml.YAMLError):
        return None
    if rules is None:
        from tools.generate_proof_data import RULES as rules
    if classes is None:
        from background.finding_classes import CLASSES as classes
    if marked is None:
        from tools.harness_page_figures import _mutation_index
        marked = _mutation_index(root)[0] or {}
    from tools.generate_proof_data import _canon_rule_text
    canon_rules = _canon_rule_text(Path(root) / CANON)
    by_principle = {r["id"]: r for r in (principles(root) or [])}
    rule_bind, class_bind = data.get("rules") or {}, data.get("classes") or {}

    out = []
    for r in rules:
        words = canon_rules.get(r["id"]) or r["rule"]
        out.append(dict(kind="rule", date=r["date"], title=_rule_title(words, r["name"]),
                        happened=r["incident"], principle=words, ref="Rule " + r["id"],
                        **_held(root, marked, list((rule_bind.get(r["id"]) or {}).get("mechanisms") or []))))
    for c in classes:
        bind = class_bind.get(c.id) or {}
        if bind.get("rule"):
            ref = bind["rule"]
            principle = canon_rules.get(ref, "")
            ref = "Rule " + ref
        elif bind.get("principle") in by_principle:
            p = by_principle[bind["principle"]]
            principle, ref = "{}. {}".format(p["title"], p["words"]), "Canon " + p["id"]
        else:
            principle, ref = "", ""
        name, _, shape = c.title.partition(": ")
        shape = shape or name
        happened = "{}{}. Seen {:,} times before it was registered as a class of mistake.".format(
            shape[0].upper(), shape[1:].rstrip("."), c.ruling_count)
        out.append(dict(kind="class", date=c.registered, title=name,
                        happened=happened, principle=principle, ref=ref,
                        **_held(root, marked, list(bind.get("mechanisms") or []))))
    out.sort(key=lambda ch: ch["date"], reverse=True)
    return out


def _holds(ch):
    if not ch["mechanisms"]:
        return "Not yet enforced: no code is named as holding it, so it is prose only for now."
    code = ", ".join("<code>{}</code>".format(html.escape(p)) for p in ch["mechanisms"])
    if ch["gone"]:
        return "Named, but gone: {} has left the build.".format(code)
    return "{}.".format(code)


def _evidence(ch):
    if not ch["mechanisms"] or ch["gone"]:
        return "None, because nothing holds it yet."
    if not ch["shown"]:
        return "No test has yet been seen to fail on this code's own defect."
    return "{:,} test{} seen to fail on this code's own defect.".format(
        ch["shown"], "" if ch["shown"] == 1 else "s")


def render_chains_html(result, cards=CARDS):
    """The lesson cards, then every chain one click down. Cards are the newest chains whose code is
    shown able to fail; the full list keeps the unenforced ones beside the rest."""
    if not result:
        return ('<p class="sub">The lessons could not be read at this publish, so none is '
                'shown.</p>')
    reach = sum(1 for ch in result if ch["status"] != UNBOUND)
    proven = sum(1 for ch in result if ch["status"] == HELD_PROVEN)
    rules = sum(1 for ch in result if ch["kind"] == "rule")
    head = ('<p class="brief-s"><b>{} of {} lessons name the code that holds them, and {} of '
            'those have a test seen to fail on that code\'s own defect.</b> The other {} are '
            'prose only for now, and each says so.</p>\n<p class="sub">A lesson here is one of '
            'the {} permanent rules the machine works under, or one of the {} classes of mistake '
            'it has registered so far; a class can share its rule\'s code, so some code appears '
            'twice. A test counts as evidence only when someone put the defect back into the code '
            'and watched that test fail. These are lessons about how the machine builds and '
            'checks itself. What the model has learned about supplying energy is on Capabilities '
            'and the knowledge pages. Each lesson is read at publish from the canon\'s rules and '
            'the register of mistake classes.</p>').format(
        reach, len(result), proven, len(result) - reach, rules, len(result) - rules)

    def card(ch, tag):
        return ('<{t} class="card"><div class="meta">{d}{ref}</div>\n  <h3>{title}</h3>\n'
                '  <p><b>What happened.</b> {h}</p>\n'
                '  <p><b>The principle.</b> {p}</p>\n'
                '  <p><b>What holds it.</b> {m}</p>\n'
                '  <p><b>Evidence it can fail.</b> {e}</p></{t}>').format(
            t=tag, d=_date(ch["date"]), title=html.escape(ch["title"]),
            ref=" · " + html.escape(ch["ref"]) if ch["ref"] else "",
            h=html.escape(ch["happened"]),
            p=html.escape(ch["principle"]) if ch["principle"]
            else "No principle is named for it yet.",
            m=_holds(ch), e=_evidence(ch))

    top, refs = [], set()
    for ch in result:
        if ch["status"] == HELD_PROVEN and ch["ref"] not in refs and len(top) < cards:
            top.append(ch)
            refs.add(ch["ref"])
    return (head + '\n<div class="lessons">\n' + "\n".join(card(ch, "div") for ch in top)
            + '\n</div>\n<details class="more"><summary>Every lesson, newest first ({})'
            '</summary>\n<div class="lessons">\n'.format(len(result))
            + "\n".join(card(ch, "div") for ch in result) + "\n</div></details>")


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
