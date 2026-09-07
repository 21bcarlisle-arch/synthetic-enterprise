"""Does the citation beside a value SUPPORT the provenance level that value claims?

REUSE: tools/commons_citation_supports_provenance.py
CLASS: CUSTOM
INDEX: searched "provenance", "citation", "source", "commons", "supersession", "origin". Four rows
       come close and none asks this question.
       * `tools/commons_source_supersession.py` -- the module this one sits BESIDE, and the reason
         it is a separate module rather than another leg inside it. It asks whether the source has
         MOVED SINCE WE READ IT. That question needs a publisher and a clock. This one asks whether
         the citation already recorded supports the strength already claimed for it, which needs
         neither: it is answerable from the artefact's own bytes.
       * `tools/domain_constant_origins.py` asks whether a constant declares WHERE it came from. It
         is satisfied the moment an origin is NAMED, and says nothing about whether the named origin
         can bear the weight put on it.
       * `tests/architecture/test_a_cited_constant_has_a_caller.py` asks whether a cited constant is
         REACHED. Reachability, not strength.
       * `tools/map_assertion_provenance.py` is maturity-map rows, not published sources.
       The gap is the join between the LEVEL and the CITATION: `provenance: "primary"` and a
       `source` URL can each be individually well-formed, individually honest, and contradict each
       other, and nothing in the tree could put that question.

WHY THIS EXISTS
---------------
2026-09-07. Two commons artefacts were found to cite superseded publications and were repaired. The
repair pass found a SECOND defect, one row over, that the supersession checker structurally cannot
see: `ro_obligation_and_buyout`'s obligation year 2025 buy-out price was stamped

    "obligation_year": 2025, "provenance": "primary",
    "source": ".../renewables-obligation-buy-out-price-and-mutualisation-...-2026-2027"

-- primary, citing the NEXT obligation year's notice, which that same file's own legend defines as
`secondary` ("read from ANOTHER obligation year's notice quoting it in a comparison table"). The
value was not in doubt. The STRENGTH claimed for it was, and it read stronger than its evidence.

NO PUBLISHER WAS NEEDED TO SEE THAT. It is visible from the artefact alone -- 2026 is after 2025 --
and it sat there because "has the source moved" and "does this citation support the provenance it
claims" are different questions, and only the first one had a module.

THE THREE LEGS, and why each is the property rather than today's answer
-----------------------------------------------------------------------
DEFINED   An artefact that stamps entries with `provenance` must carry a `provenance_legend`, and
          every level it uses must be a key in it. A level with no definition is a word, and a word
          cannot be checked against anything. This is the leg that makes the other two mean
          something: NOT_AFTER below is an argument about what `primary` MEANS, and an artefact
          with no legend has not said.

CITED     An entry stamped `primary` inside a collection where at least one SIBLING carries a
          `source` must carry one itself. The sibling is what proves the schema supports the field,
          so the missing one is a hole rather than a house style. Scoped that way on purpose:
          `capacity_market_auction_results` cites one register for the whole file and names it at
          the top level, which is a legitimate shape, and a leg demanding a per-entry URL would
          have refused twenty-five correct rows to catch nothing.

NOT_AFTER An entry stamped `primary`, keyed to a period, whose `source` URL identifies itself
          ENTIRELY with a period AFTER that key, is not primary under any legend in this commons. A
          document published for a later period can only be RESTATING the earlier year's figure,
          and a restatement is what every legend here calls `secondary`. The direction matters and
          is the whole subtlety: a source EARLIER than its subject is ordinary and correct --
          `ccl_main_rates` cites the Finance Act 2016 for rates that begin in 2017, because that is
          the Act that set them -- so an undirected "the years disagree" leg would refuse ten
          correct rows. Only LATER is impossible.

KEYED TO THE PROPERTY, NEVER TO TODAY'S ANSWER. Nothing here pins an artefact to a level, a year or
a URL. Demoting an entry to `secondary` is a green change; so is re-pointing it at its own year's
notice; so is adding a tenth artefact that does neither because it stamps no provenance at all.
Claiming the strongest level over evidence that cannot bear it is not.

WHAT THIS DELIBERATELY DOES NOT REFUSE, so that nobody reads a pass as more than it is
----------------------------------------------------------------------------------------
* An artefact that stamps NO provenance anywhere is silent here, not green. Four of the nine
  artefacts are in that state. "Every asserted value must carry provenance" is a much larger census
  and a different control; this one grades the artefacts that opted in, and an artefact could in
  principle escape it by removing the field -- which `--report` makes visible by counting.
* A `source` URL with no year token in it cannot be placed in time, so NOT_AFTER says nothing about
  it. Eight buy-out rows cite a rolling supplier page of exactly that shape. Their weakness is real
  and it is the `version_token_is: none_published` shape that the supersession module reports; it
  is not this module's leg and is not counted as a pass by it.
* The value itself. Whether 67.06 is the right number is a values-vs-source control's job, and no
  amount of provenance hygiene substitutes for one.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path

COMMONS = Path(__file__).resolve().parent.parent / "docs" / "domain_artefact_library"

#: The level whose meaning every legend in this commons agrees on: the value was read from THIS
#: entry's own source, from the publisher, during the pass that wrote it. It is the only level
#: NOT_AFTER and CITED speak about, because it is the only one whose definition is contradicted by
#: a later-dated citation. `secondary`, `estimated`, `bracketed` and `recalled` all already say
#: they rest on something weaker, and saying so is the behaviour this module wants.
STRONGEST = "primary"

#: Entry keys that carry the period the value belongs to. Named, not sniffed: a key called
#: `published_year` or `fetched` is about the DOCUMENT, and comparing a document's date to its own
#: URL's date would be a tautology dressed as a control.
PERIOD_KEYS = ("year", "obligation_year", "delivery_year", "from", "starts", "cap_period")

#: A four-digit year, bounded by something that is not a letter or a digit. The boundary is what
#: stops `.../media/5a80b6cf40f0b62305b8cbc4/...` and `.../file/464685/...` from manufacturing
#: years out of hex ids and asset numbers -- the false-positive shape that would have made this
#: leg untrustworthy on its first run over the real commons.
_YEAR = re.compile(r"(?<![0-9A-Za-z])((?:19|20)\d{2})(?![0-9A-Za-z])")


@dataclass(frozen=True)
class Refusal:
    artefact: str
    leg: str
    detail: str

    def __str__(self) -> str:  # pragma: no cover - formatting only
        return f"{self.artefact}: [{self.leg}] {self.detail}"


def artefact_paths(root: Path = COMMONS) -> list[Path]:
    """Every JSON artefact in the commons, in a stable order.

    Recursive, for the reason `commons_source_supersession.artefact_paths` gives: `regulatory/` is a
    subdirectory today and the next subject will make another one.
    """
    return sorted(p for p in root.rglob("*.json"))


def years_in(text: str) -> list[int]:
    """Every four-digit year in a string, in the order they appear. Empty when it cannot be placed."""
    return [int(m) for m in _YEAR.findall(text)]


def period_year(entry: dict) -> int | None:
    """The year an entry's value belongs to, or None when the entry is not keyed to one.

    The FIRST year in the first period key present: `2024-2025`, `2024/25` and `2024-04-01` all mean
    the period that BEGINS in 2024, which is the convention every year-keyed artefact in this
    commons already uses and states in its own `basis`.
    """
    for key in PERIOD_KEYS:
        if key in entry:
            found = years_in(str(entry[key]))
            if found:
                return found[0]
    return None


def _entries(node: object, path: str = "") -> list[tuple[str, dict, list[dict]]]:
    """Every dict carrying a `provenance`, with its own path and its SIBLING list.

    The sibling list is what the CITED leg needs: a collection where some entries cite and others do
    not is a hole, and a collection where none of them cite is a file-level citation shape.
    """
    out: list[tuple[str, dict, list[dict]]] = []
    if isinstance(node, dict):
        for key, value in node.items():
            out.extend(_entries(value, f"{path}/{key}"))
    elif isinstance(node, list):
        siblings = [item for item in node if isinstance(item, dict)]
        for index, item in enumerate(node):
            here = f"{path}[{index}]"
            if isinstance(item, dict) and "provenance" in item:
                out.append((here, item, siblings))
            out.extend(_entries(item, here))
    return out


def check_artefact(path: Path) -> list[Refusal]:
    name = path.stem
    try:
        doc = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return [Refusal(name, "DEFINED", f"not readable as JSON: {exc}")]

    entries = _entries(doc)
    if not entries:
        return []  # stamps no provenance: silent, not green. See the docstring.

    out: list[Refusal] = []
    legend = doc.get("provenance_legend")
    if not isinstance(legend, dict) or not legend:
        return [
            Refusal(
                name,
                "DEFINED",
                f"stamps {len(entries)} entries with `provenance` and carries no "
                "`provenance_legend` -- the level is a word with no definition in the file that "
                "uses it, so nothing can say whether any citation supports it",
            )
        ]

    for where, entry, siblings in entries:
        level = entry.get("provenance")
        if level not in legend:
            out.append(
                Refusal(
                    name,
                    "DEFINED",
                    f"{where} claims provenance {level!r}, which this artefact's own "
                    f"`provenance_legend` does not define (it defines {sorted(legend)})",
                )
            )
            continue
        if level != STRONGEST:
            continue

        source = entry.get("source")
        has_source = isinstance(source, str) and bool(source.strip())
        if not has_source:
            if any(isinstance(s.get("source"), str) and s.get("source", "").strip()
                   for s in siblings):
                out.append(
                    Refusal(
                        name,
                        "CITED",
                        f"{where} claims {STRONGEST!r} and carries no `source`, while a sibling in "
                        "the same collection does -- the sibling proves the field exists here, so "
                        "this is a missing citation and not a file-level one",
                    )
                )
            continue

        year = period_year(entry)
        cited = years_in(source)
        if year is None or not cited:
            continue
        if min(cited) > year:
            out.append(
                Refusal(
                    name,
                    "NOT_AFTER",
                    f"{where} is keyed to {year} and claims {STRONGEST!r}, but every year in its "
                    f"`source` URL ({', '.join(str(c) for c in sorted(set(cited)))}) is AFTER it. "
                    "A document published for a later period can only be restating this one, which "
                    "is what this commons calls `secondary`",
                )
            )

    return out


def check(root: Path = COMMONS) -> list[Refusal]:
    out: list[Refusal] = []
    for path in artefact_paths(root):
        out.extend(check_artefact(path))
    return out


def report(root: Path = COMMONS) -> list[dict]:
    """Per artefact, how much of it this module can actually speak about.

    `stamped` against `placeable` is the honest coverage figure: an entry with no period key or a
    year-less URL is one NOT_AFTER cannot grade, and a report that showed only refusals would read
    as full coverage of a commons this module can only partly see.
    """
    rows: list[dict] = []
    for path in artefact_paths(root):
        try:
            doc = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        entries = _entries(doc)
        strongest = [e for _, e, _ in entries if e.get("provenance") == STRONGEST]
        placeable = [
            e for e in strongest
            if period_year(e) is not None
            and isinstance(e.get("source"), str)
            and years_in(e["source"])
        ]
        rows.append({
            "artefact": path.stem,
            "stamped": len(entries),
            "strongest": len(strongest),
            "placeable_in_time": len(placeable),
            "has_legend": isinstance(doc.get("provenance_legend"), dict),
        })
    rows.sort(key=lambda r: (-r["stamped"], r["artefact"]))
    return rows


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--check", action="store_true", help="refuse on the three legs")
    parser.add_argument("--report", action="store_true", help="print what this module can grade")
    parser.add_argument("--json", action="store_true", help="machine-readable report")
    args = parser.parse_args(argv)

    if args.report or args.json:
        rows = report()
        if args.json:
            print(json.dumps(rows, indent=2))
        else:
            print(f"{'artefact':46} {'stamped':>8} {'primary':>8} {'placeable':>10}  legend")
            for r in rows:
                print(f"{r['artefact']:46} {r['stamped']:8} {r['strongest']:8} "
                      f"{r['placeable_in_time']:10}  {'yes' if r['has_legend'] else 'NO'}")
        if not args.check:
            return 0

    refusals = check()
    if refusals:
        print(f"\ncommons citation supports provenance: REFUSED ({len(refusals)})", file=sys.stderr)
        for r in refusals:
            print(f"  {r}", file=sys.stderr)
        return 1
    graded = sum(r["placeable_in_time"] for r in report())
    print(f"commons citation supports provenance: PASS ({graded} primary entries placeable in time)")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
