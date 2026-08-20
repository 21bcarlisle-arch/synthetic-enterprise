#!/usr/bin/env python3
"""Snapshot Cloudflare's edge analytics into the repo, because the free plan forgets.

REUSE: tools/edge_traffic_capture.py
CLASS: CUSTOM
INDEX: searched "analytics", "traffic", "edge", "cloudflare", "capture", "504". Nothing in the
       repo reads Cloudflare's analytics -- `background/publish_freshness.py` and
       `site/live_pixel_verify.py` both fetch the live SITE, which is a different question
       (what does a reader get) from this one (what has the edge been serving to everyone).

WHY THIS EXISTS
---------------
Director, 2026-08-20: *"set up whatever ongoing visibility you need before the free plan's 1-day
retention loses it -- if we can only see 24 hours, we should be capturing the shape ourselves
rather than rediscovering it."*

The zone is on the Free plan, and its GraphQL analytics **refuse any query wider than one day**:

    zone "f8261..." cannot request a time range wider than 1d, but your query time range spans 4w2d

So the answer to "has this been getting worse?" exists for 24 hours and then stops existing.

On 2026-08-20 that window appeared to show 29% of all requests returning 504, rising from 11% to
47% across the day. **It did not.** Cloudflare logs every HTTP/2 request to this zone twice, the
second time as a phantom `504`/`UNK` row, and the "rate" was the HTTP/2 share of a small sample.
Keeping the capture is still right -- but the reason changed. It is here so a claim about edge
behaviour can be checked against rows that were recorded at the time, instead of against a shape
someone remembers. The first thing it was used for was disproving itself.

See `is_phantom` below: the artefact rows stay in the file and stay out of the error rate.

WHAT IT CAPTURES, AND WHY THESE FIELDS
--------------------------------------
One row per hour per (path, status, colo, country, protocol), appended to
`docs/observability/edge_traffic.jsonl`. Every dimension is here because leaving it out cost
something real:

  * **status by path** -- an aggregate error RATE hides which surfaces are affected, and
    "which surfaces" is usually the whole diagnosis.
  * **the hour** -- so the trend is recoverable. A snapshot without time is a number, not a shape.
  * **colo and country** -- a first reading of "399 of 459 from LHR, so it is only this machine"
    was wrong, and per-colo rows are what corrected it. Global-versus-local is the difference
    between "the site is down" and "our own checks are failing".
  * **protocol** -- ADDED 2026-08-20, and it is the field that ended the incident. Four theories
    about Cloudflare's internals died to one dimension nobody had queried: every phantom 504 has
    `UNK`, and nothing else does. Capture the boring dimensions; the answer was in the one that
    looked like metadata.

APPEND-ONLY, and deduplicated by that whole key so re-running mid-hour cannot double-count a
partial hour. Re-running is expected: the collector is cheap and the window is short, so it is
better to run it often and drop duplicates than to run it once and risk missing an outage.

CREDENTIALS -- WHY THIS IS NOT WIRED TO THE TICK YET
----------------------------------------------------
The Cloudflare access granted on 2026-08-20 is an **MCP OAuth session**, held by the interactive
agent. A cron job has no such session, so this script cannot run unattended on that grant. It
needs a token in `CLOUDFLARE_API_TOKEN` with **Zone -> Analytics -> Read** on this zone and
nothing else.

That token is the director's to create -- it is a credential, and the standing rule is that the
agent never widens its own access. Until it exists, run this by hand:

    CLOUDFLARE_API_TOKEN=... python3 -m tools.edge_traffic_capture

DELIBERATELY NOT DNS-CAPABLE. The token above needs Analytics:Read only. If it is ever minted
with more, this script still cannot do more -- it issues exactly one GraphQL POST and has no
other endpoint in it.
"""
from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from tools import retired_paths_still_served as retired_paths  # noqa: E402

PROJECT = Path(__file__).resolve().parent.parent
OUT = PROJECT / "docs" / "observability" / "edge_traffic.jsonl"
ZONE_TAG = "f8261ea75d95ecb93867e7318f57766d"   # poesys.net; the account's only zone
GRAPHQL = "https://api.cloudflare.com/client/v4/graphql"

#: The Free plan's hard limit. Asking for more is an error, not a truncation, so the collector
#: must stay inside it rather than discover the ceiling in production.
MAX_WINDOW_HOURS = 24

QUERY = """
query($zoneTag:String!,$since:Time!,$until:Time!){
  viewer{ zones(filter:{zoneTag:$zoneTag}){
    httpRequestsAdaptiveGroups(limit:5000,
      filter:{datetime_geq:$since, datetime_leq:$until},
      orderBy:[datetimeHour_ASC]){
      count
      dimensions{ datetimeHour clientRequestPath edgeResponseStatus coloCode clientCountryName clientRequestHTTPProtocol }
    }
  }}}
"""


class CaptureUnavailable(RuntimeError):
    """No token, no answer, or a refused query. NEVER an empty capture written as if clean --
    a zero-row file is indistinguishable from a silent site, which is the failure this whole
    exercise exists to stop being invisible."""


def fetch(token: str, hours: int = MAX_WINDOW_HOURS) -> list[dict]:
    if hours > MAX_WINDOW_HOURS:
        raise CaptureUnavailable(
            f"asked for {hours}h; the Free plan refuses anything over {MAX_WINDOW_HOURS}h "
            "and returns an error rather than a shorter window"
        )
    until = datetime.now(timezone.utc)
    since = until - timedelta(hours=hours)
    body = json.dumps({
        "query": QUERY,
        "variables": {
            "zoneTag": ZONE_TAG,
            "since": since.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "until": until.strftime("%Y-%m-%dT%H:%M:%SZ"),
        },
    }).encode()
    req = urllib.request.Request(
        GRAPHQL, data=body,
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            payload = json.loads(resp.read())
    except (urllib.error.URLError, OSError, ValueError) as exc:
        raise CaptureUnavailable(f"analytics request failed: {exc}") from exc

    if payload.get("errors"):
        raise CaptureUnavailable(f"graphql refused: {payload['errors']}")
    try:
        groups = payload["data"]["viewer"]["zones"][0]["httpRequestsAdaptiveGroups"]
    except (KeyError, IndexError, TypeError) as exc:
        raise CaptureUnavailable(f"unexpected analytics shape: {str(payload)[:200]}") from exc
    return groups


def rows(groups: list[dict]) -> list[dict]:
    out = []
    for g in groups:
        d = g.get("dimensions") or {}
        out.append({
            "hour": d.get("datetimeHour"),
            "path": d.get("clientRequestPath"),
            "status": d.get("edgeResponseStatus"),
            "colo": d.get("coloCode"),
            "country": d.get("clientCountryName"),
            "protocol": d.get("clientRequestHTTPProtocol"),
            "count": g.get("count", 0),
        })
    return out


#: Cloudflare logs every HTTP/2 request to this zone TWICE: once truthfully, and once as a
#: phantom row with status 504 and protocol UNK. Measured 2026-08-20 -- 30 parallel requests
#: that all returned 404 in under a second produced 30 real rows AND 30 phantom 504s, while
#: 20 `--http1.1` requests produced none; in 24h, the number of 5xx rows carrying a real
#: protocol was ZERO. The phantoms cost a day: they read as "29% of requests are failing" and
#: sent four wrong theories chasing an origin that was fine.
PHANTOM_PROTOCOL = "UNK"


def is_phantom(row: dict) -> bool:
    """A logging artefact, not a request a client ever made. Kept in the file (so the
    artefact stays auditable and this claim stays checkable against raw rows) and excluded
    from the error rate (so the alarm it caused cannot recur)."""
    return row.get("protocol") == PHANTOM_PROTOCOL


def _key(r: dict) -> tuple:
    return (r["hour"], r["path"], r["status"], r["colo"], r["country"], r.get("protocol"))


def append(new_rows: list[dict], out: Path = OUT) -> int:
    """Append only rows we have not already recorded. A partial hour captured twice must not
    double its counts, so the LATEST count for a key replaces the earlier one."""
    existing: dict[tuple, dict] = {}
    if out.is_file():
        for line in out.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            try:
                r = json.loads(line)
            except ValueError:
                continue
            existing[_key(r)] = r

    added = 0
    for r in new_rows:
        k = _key(r)
        if existing.get(k, {}).get("count") != r["count"]:
            existing[k] = r
            added += 1

    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8") as fh:
        for r in sorted(existing.values(), key=lambda x: (x["hour"] or "", x["path"] or "")):
            fh.write(json.dumps(r, sort_keys=True) + "\n")
    return added


def summarise(new_rows: list[dict]) -> str:
    """Hourly real traffic and the real error rate. Phantom rows are counted separately
    and never fold into either -- reporting them as errors is what made a healthy site
    look like it was failing half its page loads."""
    by_hour: dict[str, dict] = {}
    for r in new_rows:
        h = by_hour.setdefault(r["hour"], {"total": 0, "err": 0, "phantom": 0})
        if is_phantom(r):
            h["phantom"] += r["count"]
            continue
        h["total"] += r["count"]
        if isinstance(r["status"], int) and r["status"] >= 500:
            h["err"] += r["count"]
    lines = []
    for hour in sorted(by_hour)[-6:]:
        v = by_hour[hour]
        pct = round(v["err"] / v["total"] * 100) if v["total"] else 0
        lines.append(f"  {hour}  real={v['total']:>5}  5xx={v['err']:>5}  {pct}%"
                     f"  (phantom rows ignored: {v['phantom']})")
    return "\n".join(lines)


def main() -> int:
    token = os.environ.get("CLOUDFLARE_API_TOKEN")
    if not token:
        print(
            "CLOUDFLARE_API_TOKEN is not set. This needs a token with Zone -> Analytics -> Read\n"
            "on poesys.net and nothing else. The MCP OAuth grant is a session held by the\n"
            "interactive agent and cannot be used by an unattended run.",
            file=sys.stderr,
        )
        return 2
    try:
        groups = fetch(token)
    except CaptureUnavailable as exc:
        print(f"CAPTURE FAILED: {exc}", file=sys.stderr)
        return 1     # loud, and non-zero -- see the deploy purge that exited 0 on failure
    new_rows = rows(groups)
    if not new_rows:
        print("CAPTURE FAILED: the window returned zero rows, which is not a quiet site -- "
              "even a silent zone records bot traffic. Treating as a broken query.", file=sys.stderr)
        return 1
    added = append(new_rows)
    print(f"captured {len(new_rows)} row(s), {added} new -> {OUT.relative_to(PROJECT)}")
    print(summarise(new_rows))

    # RECORDING IS NOT NOTICING (2026-08-20). The finding that produced these rows closed on
    # "the moment the ghosts stop is recorded without anyone remembering to look" -- and until
    # this call, the only thing in the repo that opened edge_traffic.jsonl was the writer
    # above. A transition whose release triggers nothing is the defect R11 names, and here it
    # was the same shape as the thing being watched. The read belongs in THIS process because
    # this is the one that runs every hour and has just written the rows the answer comes from.
    #
    # An unreadable record fails the whole unit rather than passing quietly: capturing rows
    # nobody can read is the half-job that started this.
    try:
        current, changes = retired_paths.run()
    except retired_paths.RetiredPathCheckUnavailable as exc:
        print(f"RETIRED-PATH CHECK UNAVAILABLE: {exc}", file=sys.stderr)
        return 3
    print(retired_paths.report(current, changes, brief=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
