#!/usr/bin/env python3
"""Which pages of the built site can a reader actually get to, starting from the front door?

REUSE: tools/reader_reachability.py
CLASS: CUSTOM
INDEX: searched "reachab", "link_walk", "orphan", "redirect", "nav", "door". The nearest
       analogue WAS `site/link_walk.py`, a DEAD/REDIRECTED/OK classifier that its own docstring
       described as a diagnostic wired into no gate -- it was deleted on 2026-08-20 with the
       redirects it classified, and this module inherits the only question anyone asked of it.
       `tools/site_reachability.py` remains and is different: it asks whether a page has SOME
       route in, which cannot see the defect that produced this module -- a page with a route
       in whose every follower was 301'd away.

DIRECTOR RULING, 2026-08-20: "a surface no reader can reach must never be able to block
publishing."

WHY THIS EXISTS
---------------
On 2026-08-19 a gate compared the dashboard's headline figures against the exec summary in
`docs/observability/run_insights.json` and raised a director-facing alarm when they drifted.
Neither side of that comparison was on a page anyone could open: `/project` had 301'd to
`/proof/` since 2026-07-23, and `run_insights.json` is fetched by no page on the site at all.
The two surfaces existed to be consistent with each other. Keeping them so was the whole job.

That is a class, not an incident. A surface with no reader accretes checks, alarms and
maintenance exactly like a real one, and none of that cost shows up as a reader-visible
benefit -- so nothing ever prompts the question "who is this for?". The rule closes it at the
only point where the cost becomes acute: the moment such a surface can stop the site from
publishing.

WHAT "REACHABLE" MEANS HERE
---------------------------
Reachable = there is a path of static `href`s from `site/index.html` to the page. Deliberately:

  - **From the front door, not from anywhere.** A page two unreachable pages link to is still
    unreachable. Transitive closure from `/` is the reader's actual position.
  - **Static hrefs only.** JS-templated links (`'"+esc(x)+"'`) are excluded -- they are a
    promise about data, not a route this can verify. A page reachable ONLY by a dynamic link
    reads as unreachable, which is the fail-closed direction: it under-claims reachability
    and so over-reports blockers, and a false blocker report costs a conversation while a
    missed one costs another 11-hour outage.
  - **A redirect SOURCE is not a destination**, and this still holds even though it now finds
    nothing. `site/_redirects` was cut from forty rules to two on 2026-08-20 (favicon and www),
    neither of which is a page, so no built page is a redirect source any more. The check is
    kept because it costs one set lookup and it is the difference between "reachable" and
    "reachable today"; it is not kept because anything currently needs it.

FAIL-CLOSED
-----------
An unavailable check is a FAILED check (R15). A walk that cannot read the front door, or that
finds implausibly few pages, raises `ReachabilityUnavailable` rather than returning a small
set -- because an empty or tiny result set makes EVERY surface look unreachable, which would
read as "every blocker is illegitimate" and retire the lot.
"""
from __future__ import annotations

import posixpath
import re
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent
SITE = PROJECT / "site"
REDIRECTS = SITE / "_redirects"

# Below this, assume the walk is broken rather than the site. The reachable set has been in the
# low twenties since the five-tab fold (2026-08-19); 6 is the front door plus the five doors,
# i.e. the smallest site that could honestly be called the shipped one.
MIN_PLAUSIBLE_REACHABLE = 6

_SCRIPT = re.compile(r"<script.*?</script>", re.S)
# The href AND what follows its closing quote. The trailing group is why: a JS-templated href
# reads `href="./x/"+esc(id)+"/"`, and an attribute-only regex extracts `./x/` from it -- a
# clean-looking static link to a directory that may well exist. The concatenation is OUTSIDE
# the quotes, so the only way to see it is to look past them.
_HREF = re.compile(r"""href=(["'])(.*?)\1(\s*\+)?""")
# A concatenation INSIDE the value, for the other half of the same template shape.
_DYNAMIC = re.compile(r"""["']\s*\+|\+\s*["']""")


class ReachabilityUnavailable(RuntimeError):
    """The walk could not be performed. Never silently a small answer."""


def _url_of(page: Path, site: Path) -> str:
    rel = page.parent.relative_to(site).as_posix()
    return "/" if rel == "." else "/" + rel + "/"


def pages(site: Path = SITE) -> dict:
    """{url path -> file} for every built page."""
    return {_url_of(p, site): p for p in sorted(site.rglob("index.html"))}


def redirect_sources(redirects: Path = None) -> set:
    """URL paths that appear as a redirect SOURCE, normalised to '/x/' form."""
    path = redirects or REDIRECTS
    if not path.is_file():
        return set()
    out = set()
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        src = line.split()[0]
        src = re.sub(r"^https?://[^/]+", "", src)
        src = src.split("*")[0].rstrip("/")
        if src.startswith("/") and src != "/":
            out.add(src + "/")
    return out


def outlinks(url: str, markup: str) -> set:
    """Static internal page links on one page, resolved against its own url."""
    body = _SCRIPT.sub(" ", markup)
    found = set()
    for _quote, href, concatenated in _HREF.findall(body):
        if concatenated:  # `href="./x/"+esc(id)+"/"` -- a template, not a route
            continue
        if href.startswith(("http://", "https://", "#", "mailto:", "tel:", "//")):
            continue
        if _DYNAMIC.search(href):
            continue
        href = href.split("#")[0].split("?")[0]
        if not href:
            continue
        target = posixpath.normpath(posixpath.join(url, href))
        if re.search(r"\.\w+$", target):  # a file, not a page directory
            continue
        found.add(target if target.endswith("/") else target + "/")
    return found


def reachable(site: Path = SITE, redirects: Path = None) -> set:
    """URL paths a reader can get to from the front door. Fails closed."""
    site = Path(site)
    front = site / "index.html"
    if not front.is_file():
        raise ReachabilityUnavailable(
            f"no front door at {front} -- the reachability walk has nothing to start from, and "
            "an empty answer would report every surface on the site as unreachable"
        )
    built = pages(site)
    blocked = redirect_sources(redirects)

    seen, queue = {"/"}, ["/"]
    while queue:
        here = queue.pop()
        page = built.get(here)
        if page is None:
            continue
        for target in outlinks(here, page.read_text(encoding="utf-8", errors="replace")):
            if target in seen or target in blocked:
                continue
            seen.add(target)
            queue.append(target)

    found = {u for u in seen if u in built}
    if len(found) < MIN_PLAUSIBLE_REACHABLE:
        raise ReachabilityUnavailable(
            f"the walk reached only {len(found)} page(s) from the front door "
            f"({sorted(found)}), below the {MIN_PLAUSIBLE_REACHABLE} that the shipped five-tab "
            "site cannot go under. Treating this as a broken walk, not a broken site: a small "
            "answer here would mark every publish-blocking check as guarding nothing."
        )
    return found


def unreachable(site: Path = SITE, redirects: Path = None) -> set:
    """Built pages no reader can get to. The complement, for reporting."""
    return set(pages(Path(site))) - reachable(site, redirects)


def main() -> int:
    reach = reachable()
    dead = sorted(set(pages()) - reach)
    print(f"reachable from the front door: {len(reach)}")
    for u in sorted(reach):
        print(f"  OK   {u}")
    print(f"\nunreachable: {len(dead)}")
    for u in dead:
        print(f"  DEAD {u}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
