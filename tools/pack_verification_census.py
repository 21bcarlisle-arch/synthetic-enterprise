#!/usr/bin/env python3
"""How much of the 25 Oct evidence packs has been checked: one row per pack, published.

The director's verify steer (`docs/staging/advisor/DIRECTOR_STEER_VERIFY_THE_PACKS_UNVERIFIED_ITEMS_AS_YOU_DRAFT_2026-10-25.md`)
asks for each [unverified] item to be checked at its primary source as the pack becomes a
Knowledge page, and for "a per-pack count of confirmed, corrected and still-open items" on the
Knowledge index. Before this module those counts sat in free text on some pages and nowhere on
the rest, so nobody could add them up.

WHAT IS COUNTED, said before any number:

  item       -- one `[unverified...]` tag in a pack (`[unverified]`, `[UNVERIFIED]`,
                `[unverified for GB]`, ...). A sentence that only explains what the tag means
                ("Items marked [unverified] are not claims") is the legend, not an item. A tag is
                the pack author's own unit; one tag can cover a short list, so this is a count of
                flags, not of figures.
  page       -- a `docs/market_research/` note that names the pack's file. A pack no note names
                has not been drafted.
  tally      -- the page's own count, written by whoever checked it, in the line that states it:
                "Counts: confirmed 5, corrected 3, still open 18", "Confirmed 0, corrected 3,
                open 33", "confirmed 8 (...); partly confirmed 1 (8); still unpublished 1 (9)".
                The LAST such line on the page is read, so a later verification pass supersedes
                an earlier one. The census adds the pages' tallies up; it does not re-grade them.
  no tally   -- a page that states no count. All its pack's flags are shown as still open, and
                the row says the page records no count, so the gap reads as unchecked rather
                than as checked and clean.

A page's tally and its pack's flag count need not agree: a checker may split one flag into
several figures, or spot-check sourced figures as well. Both are published, side by side, and
neither is divided by the other.

    python3 -m tools.pack_verification_census          # the table, as text
    python3 -m tools.pack_verification_census --write  # also writes site/data/pack_verification_census.json

Reporting only: it exits 0 whatever it finds.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ADVISOR = "docs/staging/advisor"
NOTES = "docs/market_research"
OUT = "site/data/pack_verification_census.json"

TAG = re.compile(r"\[unverified[^\]]*\]", re.IGNORECASE)
LEGEND = re.compile(
    r"\b(?:marked|marks)\s+\**\[unverified\]|\[unverified\]\**\s+(?:figures\s+)?(?:are|is)\s+not\s+claims",
    re.IGNORECASE)
_KIND = r"partly confirmed|still unpublished|still open|confirmed|corrected|unpublished|open"
TALLY_TERM = re.compile(rf"(?:(\d+)\s+({_KIND})\b|\b({_KIND}):?\s+(\d+))", re.IGNORECASE)
FIELD = {"confirmed": "confirmed", "partly confirmed": "partly_confirmed", "corrected": "corrected",
         "still unpublished": "unpublished", "unpublished": "unpublished",
         "still open": "open", "open": "open"}
KNOWLEDGE = re.compile(r"^\*\*Knowledge:\*\*\s*(\S+)", re.MULTILINE)


def count_items(text: str) -> int:
    return sum(0 if LEGEND.search(line) else len(TAG.findall(line)) for line in text.splitlines())


def read_tally(text: str) -> dict[str, int] | None:
    """The last line on the page that states a confirmed count beside another outcome."""
    found = None
    for line in text.splitlines():
        terms: dict[str, int] = {}
        last = None
        for m in TALLY_TERM.finditer(line):
            field, n = FIELD[(m.group(2) or m.group(3)).lower()], int(m.group(1) or m.group(4))
            if field in terms:
                continue
            # "open 9 (incl. 2 unpublished)": the 2 is inside the 9, not beside it.
            if last and re.search(r"(?:incl\.?|including|of which)\s*$", line[:m.start()], re.IGNORECASE):
                terms[last] -= n
            terms[field] = n
            last = field
        if "confirmed" in terms and len(terms) >= 2:
            found = {k: terms.get(k, 0) for k in ("confirmed", "partly_confirmed", "corrected",
                                                   "unpublished", "open")}
    return found


# Display only: the pack filenames are upper-snake, so acronyms and country names are restored.
_WORDS = {"evs": "EVs", "pv": "PV", "vpps": "VPPs", "psr": "PSR", "tdcv": "TDCV", "vat": "VAT",
          "rts": "RTS", "caltrack": "CalTRACK", "eco": "ECO", "iuf": "IUF", "gb": "GB",
          "australia": "Australia", "belgium": "Belgium", "france": "France", "germany": "Germany",
          "italy": "Italy", "japan": "Japan", "spain": "Spain"}


def _title(pack_name: str) -> str:
    stem = pack_name.removeprefix("DIRECTOR_EVIDENCE_").removesuffix("_2026-10-25.md")
    stem = stem.removeprefix("OTHER_MARKET_")
    words = [_WORDS.get(w, w) for w in stem.lower().split("_")]
    words[0] = words[0][0].upper() + words[0][1:]
    return " ".join(words)


PACK_NAME = re.compile(r"DIRECTOR_EVIDENCE_[A-Z0-9_]+_2026-10-25\.md")


def packs(root: Path = ROOT) -> list[Path]:
    found = {p.name: p for p in sorted((root / ADVISOR).glob("DIRECTOR_EVIDENCE_*_2026-10-25.md"))}
    for p in sorted((root / ADVISOR / "done").glob("DIRECTOR_EVIDENCE_*_2026-10-25.md")):
        found.setdefault(p.name, p)
    # A file that names another pack is a report ABOUT packs (the advisor's verification pass of
    # 25 Oct), not a pack: its [unverified] tags quote theirs, and counting them double-counts.
    return [found[k] for k in sorted(found)
            if not set(PACK_NAME.findall(found[k].read_text(encoding="utf-8"))) - {k}]


def build(root: Path = ROOT) -> dict:
    notes = {p: p.read_text(encoding="utf-8") for p in sorted((root / NOTES).glob("*.md"))}
    rows = []
    for pack in packs(root):
        items = count_items(pack.read_text(encoding="utf-8"))
        cited = [(p, t) for p, t in notes.items() if pack.name in t]
        pages, tallies = [], []
        for p, t in cited:
            m = KNOWLEDGE.search(t)
            slug = m.group(1) if m else None
            tally = read_tally(t)
            if tally:
                tallies.append(tally)
            pages.append({"note": str(p.relative_to(root)), "knowledge": slug, "tally": tally,
                          "published": bool(slug and (root / "site/knowledge" / slug / "index.html").exists())})
        if tallies:
            counts = {k: sum(x[k] for x in tallies) for k in tallies[0]}
        else:
            counts = {"confirmed": 0, "partly_confirmed": 0, "corrected": 0, "unpublished": 0,
                      "open": items}
        rows.append({
            "pack": pack.name,
            "title": _title(pack.name),
            "scope": "other market" if "_OTHER_MARKET_" in pack.name else "GB",
            "items": items,
            **counts,
            "counted": sum(counts.values()) if tallies else None,
            "drafted": bool(cited),
            "tally_recorded": bool(tallies),
            "pages": pages,
        })
    # GB first, then other markets: the steer's own priority ("the other-markets packs are
    # knowledge only"), then most-open first so the next check is the top row.
    rows.sort(key=lambda r: (r["scope"] != "GB", -r["open"], r["pack"]))
    total = {k: sum(r[k] for r in rows)
             for k in ("items", "confirmed", "partly_confirmed", "corrected", "unpublished", "open")}
    total["packs"] = len(rows)
    total["drafted"] = sum(r["drafted"] for r in rows)
    total["no_tally"] = sum(not r["tally_recorded"] for r in rows)
    return {
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "source": "python3 -m tools.pack_verification_census --write",
        "steer": f"{ADVISOR}/DIRECTOR_STEER_VERIFY_THE_PACKS_UNVERIFIED_ITEMS_AS_YOU_DRAFT_2026-10-25.md",
        "unit": "flags: one [unverified] tag in a pack, legend sentences excluded; "
                "outcomes: the page's own last stated tally, summed",
        "total": total,
        "packs": rows,
    }


def write(census: dict, root: Path = ROOT) -> bool:
    """Write the feed; an empty census is refused rather than published as nothing outstanding."""
    if not census["packs"]:
        return False
    (root / OUT).write_text(json.dumps(census, indent=1) + "\n", encoding="utf-8")
    return True


def report(census: dict) -> str:
    t = census["total"]
    lines = [f"{t['packs']} packs, {t['drafted']} drafted, {t['no_tally']} with no tally on the page; "
             f"{t['items']} flags. Tallied: {t['confirmed']} confirmed (+{t['partly_confirmed']} partly), "
             f"{t['corrected']} corrected, {t['unpublished']} unpublished, {t['open']} open"]
    for r in census["packs"]:
        tally = (f"{r['confirmed']:>2}+{r['partly_confirmed']}/{r['corrected']:>2}/{r['unpublished']}"
                 f"  open {r['open']:>3}" if r["tally_recorded"] else "no tally on the page")
        lines.append(f"  {r['scope']:<12} {r['items']:>3} flags  {tally:<26} {r['title']}")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--write", action="store_true")
    a = ap.parse_args(argv)
    census = build()
    if not census["packs"]:
        print("no 25 Oct evidence packs found -- refusing to write an empty census", file=sys.stderr)
        return 0
    print(report(census))
    if a.write:
        write(census)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
