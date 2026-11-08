#!/usr/bin/env python3
"""The reading log's published side: `docs/institutional/reading_log.md` as a feed for the Knowledge
tab's "Building it" part (director's steer of 5 Nov, items 2 and 3: "the reading log's published
side" sits under Building it; his 8 Nov ruling spends this week's spare allowance on the site).

The log stays the one home. This module only reads its table and resolves each row's concept
against the map's register, so the page can link a row to the place on the map it belongs to.

WHAT A ROW'S CONCEPT RESOLVES TO, said before anything is counted. The log's last column is free
text written by whoever appended the row. It is read, in this order, as:

  concept  -- a `build` concept in `docs/design/the_map/concepts.yaml`, matched on its prefLabel or
              any altLabel, ignoring case and a leading "The". Links to `#c-<id>` on the map.
  step     -- one of the `build` spine's steps ("Agents and models", "Observability", ...). Links to
              `#s-build-<Step>` only when the map page has a panel there; a step with nothing placed
              on it has no panel, and the row says so rather than linking to the top of the page.
  none     -- the row names no concept ("—"): a source judged not relevant or with nothing to adopt.
  unplaced -- names a practice that is none of the above. Published as written, marked as not on the map yet. That is a finding about
              the register (the log names a practice the map does not hold), not about the row.

FAIL-CLOSED: a log with no table rows raises rather than writing an empty feed, so a broken parse
leaves the previous honest feed live.

    python3 -m tools.reading_log_feed          # the rows and their resolution, as text
    python3 -m tools.reading_log_feed --write  # also writes site/data/reading_log.json
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
LOG = "docs/institutional/reading_log.md"
REGISTER = "docs/design/the_map/concepts.yaml"
MAP_PAGE = "site/model/map/index.html"
OUT = "site/data/reading_log.json"
COLUMNS = ("read", "source", "claim", "evidence", "verdict", "done", "concept")


class ReadingLogUnreadable(RuntimeError):
    """The log has no table the feed can be built from. NOT an empty feed."""


def _norm(label: str) -> str:
    s = re.sub(r"\*\*|`", "", label).strip().lower()
    return s[4:] if s.startswith("the ") else s


def _cells(line: str) -> list[str]:
    return [c.strip() for c in line.strip().strip("|").split("|")]


def rows(text: str) -> list[dict]:
    """The table's data rows, header and rule skipped. A row of the wrong width is refused by name."""
    out, in_table = [], False
    for n, line in enumerate(text.splitlines(), 1):
        if not line.lstrip().startswith("|"):
            in_table = False
            continue
        cells = _cells(line)
        if [c.lower() for c in cells[:2]] == ["read", "source"]:
            in_table = True
            continue
        if not in_table or set("".join(cells)) <= set("-: "):
            continue
        if len(cells) != len(COLUMNS):
            raise ReadingLogUnreadable(f"{LOG}:{n} has {len(cells)} cells, the table has {len(COLUMNS)}")
        out.append(dict(zip(COLUMNS, cells)))
    return out


def resolver(root: Path = ROOT):
    reg = yaml.safe_load((root / REGISTER).read_text(encoding="utf-8"))
    by_label = {}
    for c in reg["concepts"]:
        if any(p.split("/")[0] == "build" for p in c.get("placed", [])):
            for label in [c["prefLabel"], *c.get("altLabel", [])]:
                by_label[_norm(label)] = (c["id"], c["prefLabel"])
    steps = {_norm(s): s for s in reg["spines"]["build"]["steps"]}
    try:
        page = (root / MAP_PAGE).read_text(encoding="utf-8")
    except OSError:
        page = ""

    def resolve(concept: str) -> dict:
        key = _norm(concept)
        if key in ("", "-", "\u2014"):
            return {"kind": "none", "label": None, "anchor": None}
        if key in by_label:
            cid, label = by_label[key]
            return {"kind": "concept", "label": label, "anchor": f"c-{cid}"}
        if key in steps:
            anchor = "s-build-" + steps[key].replace(" ", "-")
            return {"kind": "step", "label": steps[key],
                    "anchor": anchor if f'id="{anchor}"' in page else None}
        return {"kind": "unplaced", "label": None, "anchor": None}
    return resolve


def build(root: Path = ROOT) -> dict:
    try:
        text = (root / LOG).read_text(encoding="utf-8")
    except OSError as e:
        raise ReadingLogUnreadable(f"{LOG} unreadable: {e}") from e
    found = rows(text)
    if not found:
        raise ReadingLogUnreadable(f"{LOG} has no table rows")
    resolve = resolver(root)
    for r in found:
        r["placed"] = resolve(r["concept"])
    kinds = {k: sum(r["placed"]["kind"] == k for r in found) for k in ("concept", "step", "unplaced", "none")}
    return {"source": LOG, "register": REGISTER, "rows": found, "placed": kinds,
            "rejected": sum(_norm(r["verdict"]).startswith("reject") for r in found)}


def write(feed: dict, root: Path = ROOT) -> bool:
    path = root / OUT
    body = json.dumps(feed, indent=1, ensure_ascii=False) + "\n"
    if path.exists() and path.read_text(encoding="utf-8") == body:
        return False
    path.write_text(body, encoding="utf-8")
    return True


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--write", action="store_true", help=f"also write {OUT}")
    args = ap.parse_args(argv)
    feed = build()
    for r in feed["rows"]:
        p = r["placed"]
        print(f"{p['kind']:<9} {p['anchor'] or '-':<34} {r['concept']:<24} {r['source'][:60]}")
    print(f"\n{len(feed['rows'])} rows: {feed['placed']}; {feed['rejected']} rejected")
    if args.write:
        print(("wrote " if write(feed) else "unchanged ") + OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
