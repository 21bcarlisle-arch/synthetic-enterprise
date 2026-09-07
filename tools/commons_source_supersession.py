"""Every commons artefact must be ABLE to be asked whether its source has been revised since we read it.

REUSE: tools/commons_source_supersession.py
CLASS: CUSTOM
INDEX: searched "supersession", "source", "freshness", "stale", "provenance", "commons". Three rows
       come close and none asks this question.
       * `tools/startup_anchor_freshness.py` asks whether a document's DECLARED age agrees with its
         REAL age -- self-consistency of one of OUR files against git. It cannot see a publisher.
       * `tools/domain_constant_origins.py` asks whether a constant declares WHERE it came from.
         It is satisfied the moment an origin is named, and says nothing about whether that origin
         still says what it said.
       * `tools/map_assertion_provenance.py` is about maturity-map rows, not published sources.
       The gap is the join: a citation can be complete, honest, correctly transcribed AND stale, and
       nothing in the tree could put the question. This module is the thing that can put it.

WHY THIS EXISTS
---------------
2026-09-07. The capacity market supplier levy's 2024/25 row was 4.0% wrong in BOTH lanes at once.
It was not a transcription slip and no values-vs-source control could have caught it, because it
was a CORRECT reading of Ofgem Annex 9 **v1.8**, which published only Apr-Sep 2024. v1.11 publishes
the full year and the H2 level is materially lower. The artefact even carried an honest caveat
saying the row was half-year -- and the caveat travelled as prose while the number travelled as law.

The lesson is NOT "check your sources more often". It is that the artefact could not be ASKED. There
was no machine-readable "which edition, read when", so no process, human or otherwise, could
enumerate what needed re-reading. Four of the nine artefacts still could not be asked when this
module was written, carrying no fetch date in any form.

WHAT IS REFUSED, AND WHAT DELIBERATELY IS NOT
---------------------------------------------
This follows `startup_anchor_freshness.py`, which learned the distinction the expensive way:
**refuse the lie, report the age.**

REFUSED -- all offline, all deterministic, none needing a network:
  ASKABLE      an artefact with no `source_check` block naming publication, url and an ISO fetch
               date. Without those there is no "since" to measure "revised since" from.
  COHERENT     a check dated before the fetch it re-checks, or either date in the future.
  ENUMERATED   a verdict outside {current, superseded, cannot_tell}.
  ACTIONED     a `superseded` verdict that names no open finding. Recording that a source has moved
               and then doing nothing is the CM levy failure with extra paperwork.
  HONEST       a version token that disagrees with the version in its own URL, or a token claimed
               where the source publishes none. This is the prose-vs-record drift that let "v1.8"
               sit beside a record that had moved to v1.11, mechanised.
  RECHECKABLE  an empty `how_to_recheck`. The field is what stops the next session re-deriving how
               to put the question -- for one source it is a filename token, for another a CKAN
               `metadata_modified`, for a third a page's own "last updated". Nobody should have to
               work that out twice.

NOT REFUSED: age. An artefact whose last check is old is a thing to schedule, not a thing to block a
commit on. A control keyed to age goes red for a reason nobody can act on inside the commit that
trips it, and it gets turned off -- which is how you end up with no control at all. `--report`
prints the ages and the due list; that surface is where age belongs.

KEYED TO THE PROPERTY, NEVER TO TODAY'S ANSWER. Nothing here pins an artefact to a version, a date
or a verdict. Re-checking a source and recording `current` is a green change; so is recording
`superseded` and opening the finding. Letting a citation drift from its own URL is not, and neither
is deleting the block.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from datetime import date
from pathlib import Path

COMMONS = Path(__file__).resolve().parent.parent / "docs" / "domain_artefact_library"

VERDICTS = ("current", "superseded", "cannot_tell")

TOKEN_KINDS = (
    # the version is written into the source URL itself, so a revision changes the URL
    "in_url",
    # the publisher stamps its own page with a "last updated" date
    "publisher_page_date",
    # the publisher exposes a machine-readable modification time (e.g. a CKAN metadata_modified)
    "publisher_api_timestamp",
    # THE MOST DANGEROUS SHAPE, and it earns its own name. The publication carries a version token
    # but the URL we stored is a LANDING PAGE, so the URL keeps resolving and silently serves a
    # newer edition. A dead link announces itself; this does not. `ofgem_cap_unit_rate_composition`
    # cites `Default_tariff_cap_level_v1.19.xlsx` behind exactly such a URL.
    "in_filename_only",
    # the source is a rolling page with no edition marker of any kind
    "none_published",
)


@dataclass(frozen=True)
class Refusal:
    artefact: str
    leg: str
    detail: str

    def __str__(self) -> str:  # pragma: no cover - formatting only
        return f"{self.artefact}: [{self.leg}] {self.detail}"


def artefact_paths(root: Path = COMMONS) -> list[Path]:
    """Every JSON artefact in the commons, in a stable order.

    Recursive on purpose: `regulatory/` is a subdirectory today and the next subject will make
    another one. A census scoped to the top level would silently stop covering the library.
    """
    return sorted(p for p in root.rglob("*.json"))


def _iso(value: object) -> date | None:
    if not isinstance(value, str):
        return None
    try:
        return date.fromisoformat(value)
    except ValueError:
        return None


def _version_tokens_in(url: str) -> list[str]:
    """Version-looking tokens in a URL: `v1.11`, `v2`, `_20260902`, `-2026-08-`.

    Deliberately generous. The HONEST leg only fires when a token is CLAIMED and absent, so a
    false positive here costs nothing and a miss costs the thing this module exists for.
    """
    return re.findall(r"v\d+(?:\.\d+)*", url, flags=re.IGNORECASE)


def check_artefact(path: Path, today: date) -> list[Refusal]:
    name = path.stem
    try:
        doc = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return [Refusal(name, "ASKABLE", f"not readable as JSON: {exc}")]

    block = doc.get("source_check")
    if not isinstance(block, dict):
        return [
            Refusal(
                name,
                "ASKABLE",
                "no `source_check` block -- nothing can ask whether this source has been revised",
            )
        ]

    out: list[Refusal] = []

    publication = block.get("publication")
    if not isinstance(publication, str) or not publication.strip():
        out.append(Refusal(name, "ASKABLE", "`publication` is empty -- no document is named"))

    url = block.get("url")
    if not isinstance(url, str) or not url.strip():
        out.append(Refusal(name, "ASKABLE", "`url` is empty -- there is nowhere to go and look"))
        url = ""

    fetched = _iso(block.get("fetched"))
    if fetched is None:
        out.append(
            Refusal(
                name,
                "ASKABLE",
                f"`fetched` is not an ISO date (got {block.get('fetched')!r}) -- "
                "there is no 'since' for 'revised since we read it'",
            )
        )
    elif fetched > today:
        out.append(Refusal(name, "COHERENT", f"`fetched` {fetched} is in the future"))

    how = block.get("how_to_recheck")
    if not isinstance(how, str) or not how.strip():
        out.append(
            Refusal(
                name,
                "RECHECKABLE",
                "`how_to_recheck` is empty -- the next session has to re-derive how to put the "
                "question, which is the cost this block exists to remove",
            )
        )

    kind = block.get("version_token_is")
    token = block.get("version_token")
    if kind not in TOKEN_KINDS:
        out.append(
            Refusal(
                name,
                "ENUMERATED",
                f"`version_token_is` is {kind!r}, not one of {TOKEN_KINDS}",
            )
        )
    elif kind == "none_published":
        if token is not None:
            out.append(
                Refusal(
                    name,
                    "HONEST",
                    f"claims version token {token!r} while declaring the source publishes none",
                )
            )
    elif kind == "in_filename_only":
        if not isinstance(token, str) or not token.strip():
            out.append(
                Refusal(
                    name,
                    "HONEST",
                    "declares a versioned publication behind a landing-page URL but names no "
                    "token -- then nothing can tell whether the page now serves a newer edition",
                )
            )
    elif kind == "in_url":
        if not isinstance(token, str) or not token.strip():
            out.append(
                Refusal(name, "HONEST", "declares the version is in the URL but names no token")
            )
        elif token not in url:
            found = _version_tokens_in(url) or ["none"]
            out.append(
                Refusal(
                    name,
                    "HONEST",
                    f"cites version {token!r} but its own URL carries {', '.join(found)} -- "
                    "this is the v1.8-in-prose-beside-v1.11-in-the-record drift",
                )
            )

    checked = block.get("checked_for_supersession")
    if not isinstance(checked, dict):
        out.append(
            Refusal(
                name,
                "ASKABLE",
                "no `checked_for_supersession` -- the question has never been recorded as asked",
            )
        )
        return out

    on = _iso(checked.get("on"))
    if on is None:
        out.append(
            Refusal(
                name,
                "COHERENT",
                f"`checked_for_supersession.on` is not an ISO date (got {checked.get('on')!r})",
            )
        )
    else:
        if on > today:
            out.append(Refusal(name, "COHERENT", f"checked on {on}, which is in the future"))
        if fetched is not None and on < fetched:
            out.append(
                Refusal(
                    name,
                    "COHERENT",
                    f"checked on {on} but fetched on {fetched} -- a re-check cannot predate the "
                    "read it re-checks",
                )
            )

    found_verdict = checked.get("found")
    if found_verdict not in VERDICTS:
        out.append(
            Refusal(name, "ENUMERATED", f"verdict {found_verdict!r} is not one of {VERDICTS}")
        )
    elif found_verdict == "superseded":
        finding = checked.get("open_finding")
        if not isinstance(finding, str) or not finding.strip():
            out.append(
                Refusal(
                    name,
                    "ACTIONED",
                    "recorded `superseded` and names no `open_finding` -- knowing the source moved "
                    "and doing nothing is the CM levy failure with extra paperwork",
                )
            )
        elif not (COMMONS.parent.parent / finding).exists():
            out.append(
                Refusal(
                    name,
                    "ACTIONED",
                    f"`open_finding` names {finding}, which is not in the tree",
                )
            )

    return out


def check(root: Path = COMMONS, today: date | None = None) -> list[Refusal]:
    today = today or date.today()
    out: list[Refusal] = []
    for path in artefact_paths(root):
        out.extend(check_artefact(path, today))
    return out


def report(root: Path = COMMONS, today: date | None = None) -> list[dict]:
    """Age and verdict per artefact, oldest check first. Reported, never refused."""
    today = today or date.today()
    rows: list[dict] = []
    for path in artefact_paths(root):
        try:
            doc = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        block = doc.get("source_check") or {}
        checked = block.get("checked_for_supersession") or {}
        on = _iso(checked.get("on"))
        rows.append(
            {
                "artefact": path.stem,
                "publication": block.get("publication"),
                "checked_on": checked.get("on"),
                "age_days": (today - on).days if on else None,
                "found": checked.get("found"),
                "how_to_recheck": block.get("how_to_recheck"),
            }
        )
    # None sorts last: an artefact that has never been checked is the oldest thing there is.
    rows.sort(key=lambda r: (r["age_days"] is None, -(r["age_days"] or 0)))
    return rows


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--check", action="store_true", help="refuse on the offline legs")
    parser.add_argument("--report", action="store_true", help="print ages and verdicts")
    parser.add_argument("--json", action="store_true", help="machine-readable report")
    args = parser.parse_args(argv)

    if args.report or args.json:
        rows = report()
        if args.json:
            print(json.dumps(rows, indent=2))
        else:
            print(f"{'artefact':46} {'checked':11} {'age':>5}  verdict")
            for r in rows:
                age = "never" if r["age_days"] is None else f"{r['age_days']}d"
                print(
                    f"{r['artefact']:46} {str(r['checked_on'] or '-'):11} {age:>5}  "
                    f"{r['found'] or '-'}"
                )
        if not args.check:
            return 0

    refusals = check()
    if refusals:
        print(f"\ncommons source supersession: REFUSED ({len(refusals)})", file=sys.stderr)
        for r in refusals:
            print(f"  {r}", file=sys.stderr)
        return 1
    print(f"commons source supersession: PASS ({len(artefact_paths())} artefacts askable)")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
