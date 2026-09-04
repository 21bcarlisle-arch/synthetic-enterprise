#!/usr/bin/env python3
"""Is the edge still serving a page this repo no longer contains? Derived, never remembered.

REUSE: tools/retired_paths_still_served.py
CLASS: CUSTOM
INDEX: searched "ghost", "retired", "deleted", "cache", "stale", "404", "edge". Two modules
       are adjacent and neither answers this. `tools/assert_deployed_bytes_are_served.py`
       asks whether THIS push's bytes reached a reader, and says so in its own docstring:
       a deleted file is only REPORTED there, never asserted, because one deploy cannot
       prove absence. `tools/edge_traffic_capture.py` WRITES the record this reads and has
       no reader of its own -- which is the gap below.

WHY THIS EXISTS
---------------
The 2026-08-20 finding `WORKER_FINDING_EIGHT_DELETED_PAGES_ARE_STILL_SERVED_TO_READERS`
closed with a recommendation: leave the ghosts alone, because

    "the ghosts appear in docs/observability/edge_traffic.jsonl as 200s on paths that no
     longer exist, so the moment they stop is recorded without anyone remembering to look."

Recorded, yes. Read, no. Before this module, the ONLY thing in the repo that opened
`edge_traffic.jsonl` was the collector that writes it. The clearing of the ghosts was a
state transition whose release triggered nothing, which R11 names as a defect in its own
right -- and it is the same shape as the thing being watched, since the reason the ghosts
went unnoticed for two days is that nobody was looking.

The second reason is sharper. That finding's ghost list was **enumerated by hand**, from
the paths someone had thought to check, and it was short:

  * it named eight; there are NINE. `/shadow/` was deleted by the same commit (03dd8c49e,
    the five-tab fold) and was still being served `200` when this module was written.
  * it recorded "the oldest is 30 hours". `/shadow/` was at `age: 198199` -- 55 hours --
    nearly double the figure the recommendation was reasoned from.

A hand-written list can only contain what someone remembered to visit, and no amount of
care fixes that. So this module DERIVES the population from two sources that were produced
independently and for other reasons:

  * **git** -- every page path ever deleted from `site/` and still absent. Complete by
    construction: it does not care whether anyone visited.
  * **the edge's own record** -- paths Cloudflare logged a real `200` for while the
    checkout could not serve them. Independent of this machine: those rows are written
    server-side.

Neither is trusted to be the whole answer. Their union is the subject set, and a candidate
git names that the edge has never logged is reported as UNOBSERVED, never as clear -- an
unwatched path is not a well-behaved one, and quietly counting it as fine is exactly the
fail-open pattern R15 names.

WHY IT DOES NOT PROBE THE GHOSTS BY DEFAULT
-------------------------------------------
Fetching each candidate hourly would convert every UNOBSERVED into an observation, and it
is the obvious design. It is also the one that can keep the thing it measures alive: these
objects are held in a cache we cannot see into or purge, and a cache that evicts by
recency is fed by every request -- including the check's. The passive instrument reads
traffic that would have happened anyway and cannot have that effect. `--probe` exists for
a deliberate one-off answer, and says what it costs.

FAILURE, WHICH IS THE POINT
---------------------------
An unavailable check is a FAILED check (R15). This raises rather than returning an empty
verdict when the capture is missing, empty or unparseable, and -- the mutation that scores
green if you forget it -- when the CHECKOUT looks empty. The subject set is derived by
subtraction, so a `site/` that failed to check out would make every live page on the site
read as a retired ghost, and a control whose broken state is "everything is a defect" gets
switched off within a day.
"""
from __future__ import annotations

import json
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from background.episode_prior import load_episode_prior  # noqa: E402

SITE = ROOT / "site"
CAPTURE = ROOT / "docs" / "observability" / "edge_traffic.jsonl"
STATE = ROOT / "docs" / "observability" / "retired_paths_served.json"

#: Cloudflare logs every HTTP/2 request to this zone twice, the second time as a phantom row
#: with protocol UNK. Kept identical to `tools.edge_traffic_capture.PHANTOM_PROTOCOL` by the
#: test that imports both -- a phantom is not evidence that anything was served.
PHANTOM_PROTOCOL = "UNK"

#: Served by Cloudflare itself, never from the deployment, so their absence from the checkout
#: is correct rather than a ghost. Deliberately two exact prefixes and not a general "unknown
#: paths are fine" clause: the whole value of this check is that an unrecognised 200 on a path
#: the repo cannot serve is REPORTED.
INFRASTRUCTURE_PREFIXES = ("/cdn-cgi/", "/.well-known/")

#: Below this many real pages, the checkout is treated as broken rather than the site as
#: retired. The site is a five-tab fold plus the root; asking for 3 is well under today's
#: number so an ordinary page retirement cannot trip it, and well over zero, which is the
#: only value that matters -- see the docstring's last paragraph.
MIN_LIVE_PAGES = 3


class RetiredPathCheckUnavailable(RuntimeError):
    """The check could not be run. Never a verdict of "clear" -- an instrument that reports
    nothing wrong when it cannot see is the fail-silent pattern R15 names."""


def normalise(path: str) -> str:
    """Collapse the spellings the edge records for one resource. `/./harness/`, `//harness/`
    and `/harness/` are the same page to Pages and are logged as three paths; without this
    the first two look like paths the checkout cannot serve, i.e. ghosts."""
    if not path:
        return "/"
    path = path.split("?", 1)[0].split("#", 1)[0]
    trailing = path.endswith("/")
    parts = [p for p in path.split("/") if p not in ("", ".")]
    out = "/" + "/".join(parts)
    if trailing and not out.endswith("/"):
        out += "/"
    return out or "/"


def checkout_serves(path: str, site: Path = SITE) -> bool:
    """Would this checkout answer that URL? Pages' own resolution: a directory URL is its
    `index.html`, and an extensionless URL may be either a file or a directory."""
    p = normalise(path)
    if p == "/":
        return (site / "index.html").is_file()
    rel = p.strip("/")
    if p.endswith("/"):
        return (site / rel / "index.html").is_file()
    return (
        (site / rel).is_file()
        or (site / f"{rel}.html").is_file()
        or (site / rel / "index.html").is_file()
    )


def live_pages(site: Path = SITE) -> list[str]:
    """The page URLs this checkout can serve. Used only to decide whether the checkout is
    real enough to subtract from."""
    if not site.is_dir():
        return []
    pages = []
    for f in site.rglob("index.html"):
        rel = f.parent.relative_to(site).as_posix()
        pages.append("/" if rel == "." else f"/{rel}/")
    return pages


def deleted_page_paths(root: Path = ROOT) -> set[str]:
    """Every page path git has ever seen deleted from `site/` and that is still absent.

    Complete by construction and blind to traffic, which is the half a request log cannot
    supply: a page nobody has visited since it was deleted is exactly the one a hand-written
    list omits.

    PAGES ONLY -- a deleted `index.html`, i.e. a URL a reader could visit. The 66 other
    files the fold deleted from `site/` are test modules and render harnesses that were
    never linked from anything, and listing them as unobserved candidates buries the nine
    real ghosts under a noise floor, which is how a report stops being read. The narrowing
    costs something and it is stated: a deleted `/data/*.json` nobody requests is invisible
    to this. The edge half of the subject set carries no such filter -- ANY path Cloudflare
    logs a real 200 for that this checkout cannot serve becomes a subject, extension or
    not -- so the blind spot is exactly "deleted, non-page, and never requested"."""
    try:
        out = subprocess.run(
            ["git", "log", "--diff-filter=D", "--name-only", "--pretty=format:", "--", "site/"],
            cwd=root, capture_output=True, text=True, timeout=60, check=True,
        ).stdout
    except (subprocess.SubprocessError, OSError) as exc:
        raise RetiredPathCheckUnavailable(f"git could not list deletions under site/: {exc}") from exc

    paths = set()
    for line in out.splitlines():
        line = line.strip()
        if not line.startswith("site/") or not line.endswith("index.html"):
            continue
        rel = line[len("site/"):]
        url = normalise("/" + rel[: -len("index.html")])
        if not checkout_serves(url, root / "site"):
            paths.add(url)
    return paths


def load_rows(capture: Path = CAPTURE) -> list[dict]:
    """Real request rows from the edge's record. Raises rather than returning [] on every
    way of having no answer."""
    if not capture.is_file():
        raise RetiredPathCheckUnavailable(
            f"{capture} does not exist. The edge record is the instrument; without it this "
            "check has no observations and 'no ghosts found' would be a lie."
        )
    rows, malformed = [], 0
    for line in capture.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            r = json.loads(line)
        except ValueError:
            malformed += 1
            continue
        if r.get("protocol") == PHANTOM_PROTOCOL:
            continue
        rows.append(r)
    if not rows:
        raise RetiredPathCheckUnavailable(
            f"{capture} holds no real rows ({malformed} unparseable). An empty record is "
            "indistinguishable from a silent edge, so it is a failed read, not a clean one."
        )
    return rows


def observations(rows: list[dict]) -> dict[str, dict[str, set]]:
    """path -> hour -> {statuses}.

    Phantoms are dropped HERE as well as in `load_rows`, and the duplication is deliberate.
    `load_rows` is one caller among several -- the tests hand rows straight in, and so would
    any future consumer that already has the record in memory. A filter that lives only in
    the reader is a filter you can walk around, and walking around it makes Cloudflare's
    duplicate rows evidence again."""
    seen: dict[str, dict[str, set]] = {}
    for r in rows:
        if r.get("protocol") == PHANTOM_PROTOCOL:
            continue
        path = normalise(str(r.get("path") or ""))
        hour = r.get("hour")
        if not hour:
            continue
        seen.setdefault(path, {}).setdefault(hour, set()).add(r.get("status"))
    return seen


def verdicts(rows: list[dict], site: Path = SITE, root: Path = ROOT,
             deleted: set[str] | None = None) -> dict[str, dict]:
    """One verdict per retired path. `still_served` is True, False, or None for never
    observed -- three states, because collapsing the third into False is the fail-open."""
    if len(live_pages(site)) < MIN_LIVE_PAGES:
        raise RetiredPathCheckUnavailable(
            f"{site} serves {len(live_pages(site))} pages, under the floor of {MIN_LIVE_PAGES}. "
            "The subject set is derived by subtracting the checkout, so an empty or partial "
            "checkout would report every live page on the site as a retired ghost."
        )

    seen = observations(rows)
    subjects = set(deleted_page_paths(root) if deleted is None else deleted)
    for path, hours in seen.items():
        if path.startswith(INFRASTRUCTURE_PREFIXES):
            continue
        if any(200 in st for st in hours.values()) and not checkout_serves(path, site):
            subjects.add(path)
    subjects = {p for p in subjects if not p.startswith(INFRASTRUCTURE_PREFIXES)}

    out: dict[str, dict] = {}
    for path in sorted(subjects):
        hours = seen.get(path)
        if not hours:
            out[path] = {"still_served": None, "last_seen": None, "last_status": None,
                         "note": "never observed by the edge record"}
            continue
        last = max(hours)
        statuses = sorted(s for s in hours[last] if s is not None)
        out[path] = {
            "still_served": 200 in hours[last],
            "last_seen": last,
            "last_status": statuses,
            "note": "served from a cache the deployment no longer backs"
                    if 200 in hours[last] else "the edge now answers correctly",
        }
    return out


def transitions(previous: dict, current: dict) -> list[str]:
    """What CHANGED. R5: an alarm reports state transitions, never an unchanged status --
    and the transition this exists for is the quiet one, a ghost finally clearing."""
    prev = (previous or {}).get("paths", {})
    lines = []
    for path, v in sorted(current.items()):
        was = prev.get(path, {}).get("still_served", "absent")
        now = v["still_served"]
        if was == now:
            continue
        if now is True and was in (False, None):
            lines.append(f"NOW SERVED   {path} -- a retired path is being served 200 again")
        elif now is True and was == "absent":
            lines.append(f"NEW GHOST    {path} -- retired, and the edge is serving it 200")
        elif now is False and was is True:
            lines.append(f"CLEARED      {path} -- the ghost is gone; the edge 404s it "
                         f"(last seen {v['last_seen']})")
        elif now is None and was is True:
            lines.append(f"UNOBSERVED   {path} -- was a live ghost, now no rows at all; "
                         "silence is not a clearance")
    for path in sorted(set(prev) - set(current)):
        lines.append(f"RETIRED PATH GONE  {path} -- no longer in the subject set "
                     "(restored to the checkout, or history rewritten)")
    return lines


def probe(paths: list[str], host: str = "https://poesys.net") -> dict[str, dict]:
    """Ask the edge directly, plain and cache-busted. INVASIVE: a request is what keeps an
    object warm in a recency-evicted cache, so this is a deliberate one-off, never the tick."""
    out = {}
    for path in paths:
        row = {}
        for label, url in (("plain", f"{host}{path}"), ("busted", f"{host}{path}?cb=probe")):
            try:
                with urllib.request.urlopen(url, timeout=20) as resp:
                    row[label] = resp.status
            except urllib.error.HTTPError as exc:
                row[label] = exc.code
            except (urllib.error.URLError, OSError) as exc:
                row[label] = f"unreachable: {exc}"
        out[path] = row
    return out


def report(current: dict[str, dict], changes: list[str], brief: bool = False) -> str:
    ghosts = [p for p, v in current.items() if v["still_served"] is True]
    unobserved = [p for p, v in current.items() if v["still_served"] is None]
    cleared = [p for p, v in current.items() if v["still_served"] is False]
    lines = [
        f"retired paths: {len(current)}  |  still served: {len(ghosts)}  "
        f"|  edge 404s: {len(cleared)}  |  never observed: {len(unobserved)}",
    ]
    if not brief:
        for path in ghosts:
            lines.append(f"  GHOST      {path}  (200 at {current[path]['last_seen']})")
        for path in unobserved:
            lines.append(f"  UNOBSERVED {path}  (no rows -- not a clearance)")
    lines.append("changes since last run:")
    if changes:
        lines.extend(f"  {c}" for c in changes)
    else:
        lines.append("  none")
    return "\n".join(lines)


def _load_previous_state() -> dict:
    """Last run's verdicts, for `transitions` to difference against.

    `except ValueError` caught the truncated file and not `[1, 2, 3]` or `"abc"`, which parse --
    `transitions`' `(previous or {}).get` then raised AttributeError (measured 2026-09-05, census
    loader sweep). `null` did NOT raise, because `None or {}` is `{}`, and that is the trap: one
    member of the partition answered correctly by accident and made the other two look impossible.

    A NAMED FUNCTION RATHER THAN FOUR LINES INSIDE `run` BECAUSE OF WHAT `run` NEEDS. `run` starts
    with `verdicts(load_rows())`, which refuses outright unless a real site checkout is present, so
    a test written against `run` cannot reach this load at all -- and the alternative, a test that
    calls `load_episode_prior` itself, passes whatever this function does. That test was written
    first here and SURVIVED the mutation restoring the old inline read: it was asserting the
    helper, not the caller. The seam exists so the control has this module as its subject.

    No preserve is earned: `current` is recomputed in full from the edge rows, so the write that
    follows loses nothing. An unreadable prior costs one re-report of every live ghost."""
    previous, _verdict = load_episode_prior(STATE)
    return previous


def run(write_state: bool = True) -> tuple[dict[str, dict], list[str]]:
    current = verdicts(load_rows())
    previous = _load_previous_state()
    changes = transitions(previous, current)
    if write_state:
        STATE.parent.mkdir(parents=True, exist_ok=True)
        STATE.write_text(
            json.dumps({"paths": current, "last_changes": changes}, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    return current, changes


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    try:
        current, changes = run()
    except RetiredPathCheckUnavailable as exc:
        print(f"RETIRED-PATH CHECK UNAVAILABLE: {exc}", file=sys.stderr)
        return 2
    print(report(current, changes))
    if "--probe" in argv:
        print("probing the edge directly (this request itself can keep a cached ghost warm):")
        for path, row in probe(sorted(current)).items():
            print(f"  {path}  plain={row['plain']}  cache-busted={row['busted']}")
    if "--fail-on-ghost" in argv and any(v["still_served"] for v in current.values()):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
