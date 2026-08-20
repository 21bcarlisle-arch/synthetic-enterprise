"""A published page with no route in publishes nothing — reachability as a build-time control.

WHY THIS EXISTS (DIRECTOR_OBSERVATION_PUBLISHED_SURFACE_NAV_AND_STAMPS_2026-08-12, item 1
and "What is asked"): the director read the live site, found the Knowledge section had no
route in from the main nav, and reached exactly one of its nine pages — via the Company
section, by accident. Eight pages that exist, render, and pass their tests were effectively
unpublished. His ask was explicitly NOT the fix: "If a control could make 'a published page
with no route in' fail at build time rather than be found by the director looking at the
site, that is worth more than the fix."

THE SUBJECT IS DERIVED FROM THE REPO'S OWN WORDS, NOT INVENTED HERE. This matters because a
reachability control with a hand-authored list of "pages that are allowed to be orphans" is
the wrong-population defect this project has filed against itself repeatedly: the list
becomes the subject, and the list is written by the same person who wrote the orphan.
`site/sitemap.xml` already states the contract in its own comment —

    INCLUDED: the live, canonical door set, the front door plus every
    surface reachable from it that is not itself a 301 redirect target.

— that is a REACHABILITY PROMISE, authored 2026-07-18 and never enforced by anything. This
module enforces the promise the site already makes about itself. The three exclusion
sources below are likewise quoted from existing declarations, never decided here:

  1. `site/_redirects` — a path that 301s away is intentionally retired. Its own comment:
     "Old page directories are NOT deleted (absorbed content stays in-repo for reference)"
     and "The full page stays in-repo (noindex, unreachable canonically) for reference."
     An orphan by design, declared by the author, in a file that predates this control.
  2. The sitemap comment's named exclusions — `/director/` ("explicitly off-nav and noindex
     by design, an auth-adjacent surface") and `/shadow/` ("the internal advisor mirror,
     not a public surface").
  3. `STRUCTURAL_EXCLUSIONS` below — the handful of files that are not reader-facing pages
     at all (an error document the host serves, a page template, dated archive snapshots,
     brand token artefacts). This is the only list authored HERE, it is deliberately tiny,
     each entry carries its reason, and `check()` FAILS if an entry names a path that does
     not exist — so it cannot rot into a silent allowlist for deleted pages.

FAIL-CLOSED, deliberately (R15 killer pattern 2, FAIL-OPEN — passes on missing/zero/empty).
Every degenerate input that would make the check vacuously green RAISES instead:
  - a missing entry point (`site/index.html`) — the crawl would find nothing and every page
    would look like an orphan, or with the subtraction the other way, none would;
  - an empty page population — a moved/renamed `site/` directory must not read as "no
    orphans"; `MIN_PAGES` is a non-emptiness floor, the same shape the sitemap
    crawlability test already uses for its exclusion rules;
  - an entry point that reaches nothing — a homepage whose nav markup stopped parsing
    would otherwise silently orphan the entire site AND, because the orphans are then
    everything, look like a loud failure for the wrong reason. It is named separately so
    the diagnostic points at the parser, not at 30 innocent pages.

WHAT THIS IS NOT. It is not a link checker: a link to a page that does not exist is a
different defect, already covered for the sitemap by
`tests/tools/test_site1_proof_crawlability.py`. This module answers one question only —
can a reader get here from the front door — and reports `broken` separately as diagnostic
context without failing on it, so the two controls keep independent subjects.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_SITE_ROOT = REPO_ROOT / "site"

#: The front door. Reachability is defined FROM here because that is what the sitemap
#: comment says ("the front door plus every surface reachable from it").
ENTRY = "index.html"

#: Non-emptiness floor (R15 fail-open guard). The site has had 30+ pages for months; a
#: population below this means the caller pointed at the wrong directory, which must raise
#: rather than report a clean bill of health over nothing.
MIN_PAGES = 10

#: Schemes that leave the site. `href="#anchor"` is same-page and also not a route in.
_EXTERNAL = ("http://", "https://", "mailto:", "tel:", "javascript:", "data:", "#")

_HREF_RE = re.compile(r"""\bhref\s*=\s*["']([^"']+)["']""", re.IGNORECASE)

#: Inline scripts are STRIPPED before hrefs are read, and this is a correctness decision
#: rather than tidying (found 2026-08-12 while building this: the related-topics widget on
#: knowledge/electricity-wholesale builds `href="../'+esc(n.id)+'/"` by concatenation, and
#: the naive parse read the fragment `../` as a real link to a knowledge index that has
#: never existed). Two reasons to exclude them, both pointing the same way:
#:   1. CONSERVATISM. A route only a script can build is not a route a non-JS crawler — or
#:      a reader whose JS failed — can follow. Counting it would OVERSTATE reachability,
#:      and an overstated reachability is a MISSED orphan: fail-open, in the one direction
#:      this control must never fail. Excluding scripts can only ever find more orphans.
#:   2. It is the same population the site's own sitemap/noscript control already worries
#:      about ("a non-JS crawler indexes 'Loading...'", test_site1_proof_crawlability).
#: If a section ever legitimately routes via script, the fix is a real <a> in the markup,
#: which is what a reader needs anyway — not a widening of this parser.
_SCRIPT_RE = re.compile(r"<script\b.*?</script\s*>", re.IGNORECASE | re.DOTALL)

#: A `_redirects` line: "<from> <to> <status>". Only the FROM path matters here.
_REDIRECT_RE = re.compile(r"^\s*(?P<src>/[^\s]*)\s+\S+\s+\d{3}\s*$")

#: The only list authored by this control rather than quoted from an existing declaration.
#: Each entry is a reason, and `check()` fails on any entry whose path is absent (rot guard).
STRUCTURAL_EXCLUSIONS: dict[str, str] = {
    "404.html": (
        "the error document the host serves on a 404; linking to it from the site would be "
        "the defect, not the fix"
    ),
    "brand/exemplar.html": (
        "an internal brand-token visualisation used when changing brand.css, not a reader "
        "surface"
    ),
    "brand/proof.html": (
        "the internal token-adoption proof for the brand system, same non-reader status as "
        "brand/exemplar.html"
    ),
}

#: The reasons the site gives for its two deliberately-unadvertised doors, quoted from
#: `site/sitemap.xml`'s own comment. NOT a decision made by this module — a decision read
#: from the site. The MEMBERSHIP is not typed here; see below.
_INTERNAL_DOOR_REASONS: dict[str, str] = {
    "director/": (
        "sitemap.xml: 'explicitly off-nav and noindex by design, an auth-adjacent surface, "
        "not a public door'"
    ),
    "shadow/": "sitemap.xml: 'the internal advisor mirror, not a public surface'",
}


def _internal_door_exclusions() -> dict[str, str]:
    """The INTERNAL door set, taken from `site/ia_register.py` — not re-typed here.

    SITE4 (2026-08-18): this module used to carry its own hand-written copy of
    {director, shadow}, and so did `site/live_pixel_verify.py`. Three lists that must
    agree are three lists that will not: an internal door added or published in one place
    would have gone on being excluded here, silently, which on a REACHABILITY control means
    a newly-public page that nothing checks a route to. The register is the one definition
    of that set; this module keeps ownership of its own REASONS (the wording is the
    sitemap's, and its audience is this control's diagnostic).

    Fail-closed: a member the register declares and this module has no reason for still
    excludes, carrying a reason that says so, rather than being quietly dropped from the
    exclusion set and reported as an orphan.
    """
    site_dir = REPO_ROOT / "site"
    if str(site_dir) not in sys.path:
        sys.path.insert(0, str(site_dir))
    from ia_register import INTERNAL_DOORS

    out = {}
    for door in INTERNAL_DOORS:
        key = door.strip("/") + "/"
        out[key] = _INTERNAL_DOOR_REASONS.get(
            key,
            f"site/ia_register.py declares {door} INTERNAL (deployed, deliberately absent "
            f"from sitemap.xml); no reason recorded in this module yet",
        )
    return out


#: Directory prefixes excluded by the site's own declarations. The two internal doors come
#: from the register; `snapshots/` is this module's own structural call and stays here.
SITEMAP_DECLARED_EXCLUSIONS: dict[str, str] = {
    **_internal_door_exclusions(),
    "snapshots/": (
        "dated archive snapshots of a past dashboard render; each is a frozen artefact, not "
        "a live door (the live surface is /now/)"
    ),
}


#: The authoring template. A page BYTE-IDENTICAL to it has not been written yet, whatever
#: its directory name promises. Derived by content hash, never by a list of names.
# MOVED OUT OF THE PUBLISHED TREE, 2026-08-20. This was site/knowledge/_stub/index.html -- an
# authoring template that was nonetheless deployed, so the site served a stub at its own URL and
# every page-scanning control had to carry an exemption for it. It now lives at
# docs/site_templates/knowledge/_stub.html: still the byte-identical oracle for "this page has
# not been written yet", no longer a published surface, and no exemption needed anywhere.
STUB_TEMPLATE = "../docs/site_templates/knowledge/_stub.html"

#: A page whose entire body is "go somewhere else" is not a destination. Detected from the
#: page's OWN markup (the same declaration a browser obeys), so it needs no list either.
_META_REFRESH_RE = re.compile(
    r"""<meta[^>]*http-equiv\s*=\s*["']?refresh["']?[^>]*>""", re.IGNORECASE
)


class ReachabilityError(RuntimeError):
    """A degenerate input that would make the check vacuous. Never a finding — a refusal."""


def redirect_sources(site_root: Path) -> set[str]:
    """Path prefixes that `site/_redirects` 301s away — intentionally retired directories.

    Returns bare prefixes with no leading slash ("method/", "wip-flow/") so they compose
    with the repo-relative page paths used everywhere else here. A `/method/*` wildcard and
    a bare `/method` both contribute the same prefix; the file always writes both.
    """
    path = site_root / "_redirects"
    if not path.exists():
        # Not fail-closed by RAISING: a site with no redirects file is legitimate (it is
        # host config, not a page). But it MUST NOT silently widen the exclusion set, so an
        # absent file contributes nothing and every page stays in the subject.
        return set()
    prefixes: set[str] = set()
    for line in path.read_text(errors="ignore").splitlines():
        if line.lstrip().startswith("#"):
            continue
        m = _REDIRECT_RE.match(line)
        if not m:
            continue
        src = m.group("src").lstrip("/").rstrip("*").rstrip("/")
        if not src or "//" in src:
            continue  # absolute-URL rules (the www canonicalisation) are not page paths
        prefixes.add(src + "/")
    return prefixes


def page_population(site_root: Path) -> set[str]:
    """Every `.html` file under the site, as repo-relative-to-site POSIX paths."""
    return {
        p.relative_to(site_root).as_posix()
        for p in site_root.rglob("*.html")
        if p.is_file()
    }


def _normalise_target(source: str, href: str) -> str | None:
    """Resolve one href against the page containing it. None when it leaves the site.

    Directory-style targets ("../world/", "./") resolve to that directory's index.html,
    which is how the host serves them and therefore what reachability must mean.
    """
    href = href.strip()
    if not href or href.lower().startswith(_EXTERNAL):
        return None
    href = href.split("#", 1)[0].split("?", 1)[0]
    if not href:
        return None
    if href.startswith("/"):
        parts: list[str] = []
        rest = href.lstrip("/")
    else:
        parts = Path(source).parent.as_posix().split("/")
        parts = [seg for seg in parts if seg not in ("", ".")]
        rest = href
    trailing_dir = rest.endswith("/")
    for seg in rest.split("/"):
        if seg in ("", "."):
            continue
        if seg == "..":
            if parts:
                parts.pop()
            continue
        parts.append(seg)
    if not parts:
        return ENTRY
    target = "/".join(parts)
    if target.endswith(".html"):
        return target
    if trailing_dir:
        return f"{target}/{ENTRY}"
    # A NON-HTML SUFFIX IS AN ASSET, NOT A PAGE (stylesheets, icons, JSON feeds). Appending
    # `/index.html` to it would invent a page path that can never exist and report it as a
    # broken link — noise in a diagnostic whose whole value is that it is short.
    if "." in parts[-1]:
        return None
    return f"{target}/{ENTRY}"


def internal_links(site_root: Path, page: str) -> set[str]:
    """Every in-site page path the given page links to (existing or not)."""
    text = _SCRIPT_RE.sub(" ", (site_root / page).read_text(errors="ignore"))
    out: set[str] = set()
    for href in _HREF_RE.findall(text):
        target = _normalise_target(page, href)
        if target is not None:
            out.add(target)
    return out


def crawl(site_root: Path, population: set[str]) -> tuple[set[str], set[str]]:
    """Breadth-first from the front door. Returns (reachable, broken-link targets).

    Only pages IN the population propagate the crawl — a link to a missing file cannot
    carry a reader onward, so it is recorded as broken and never treated as a route.
    """
    if ENTRY not in population:
        raise ReachabilityError(
            f"entry point {ENTRY!r} is not present under {site_root} — reachability from a "
            "front door that does not exist is not a question this control can answer"
        )
    reachable = {ENTRY}
    broken: set[str] = set()
    stack = [ENTRY]
    while stack:
        current = stack.pop()
        for target in internal_links(site_root, current):
            if target not in population:
                broken.add(target)
                continue
            if target not in reachable:
                reachable.add(target)
                stack.append(target)
    return reachable, broken


def unwritten_pages(site_root: Path) -> set[str]:
    """Pages byte-identical to `STUB_TEMPLATE` — deployed placeholders, not written pages.

    REPORTED, NEVER EXCUSED (measured 2026-08-12): seven of the nine knowledge directories
    are the template to the byte. They are still subject to the orphan rule — see the note
    in `orphans()` for why excusing them would have been this control deciding a content
    question in its own favour. What this function adds is VISIBILITY: a section can be
    fully routed and still be mostly unwritten, and a reachability verdict that said only
    "no orphans" would let that read as a finished section. The count is printed every run.
    """
    template = site_root / STUB_TEMPLATE
    if not template.is_file():
        return set()
    body = template.read_bytes()
    return {
        page
        for page in page_population(site_root)
        if page != STUB_TEMPLATE and (site_root / page).read_bytes() == body
    }


def redirect_pages(site_root: Path) -> set[str]:
    """Pages that are a meta-refresh redirect — a signpost, never a destination."""
    out: set[str] = set()
    for page in page_population(site_root):
        text = (site_root / page).read_text(errors="ignore")
        if _META_REFRESH_RE.search(text):
            out.add(page)
    return out


def excluded(page: str, retired: set[str]) -> str | None:
    """The REASON this page is legitimately unreachable, or None if it must have a route."""
    if page in STRUCTURAL_EXCLUSIONS:
        return STRUCTURAL_EXCLUSIONS[page]
    for prefix, reason in SITEMAP_DECLARED_EXCLUSIONS.items():
        if page.startswith(prefix):
            return reason
    for prefix in sorted(retired):
        if page.startswith(prefix):
            return f"_redirects 301s /{prefix.rstrip('/')} away; kept in-repo for reference"
    return None


def orphans(site_root: Path = DEFAULT_SITE_ROOT) -> list[str]:
    """Pages that must have a route in and do not. THE control's answer."""
    site_root = Path(site_root)
    population = page_population(site_root)
    if len(population) < MIN_PAGES:
        raise ReachabilityError(
            f"only {len(population)} page(s) found under {site_root} (floor {MIN_PAGES}) — "
            "refusing to report 'no orphans' over a population this small, which means the "
            "site directory moved rather than that the site is healthy"
        )
    reachable, _broken = crawl(site_root, population)
    if len(reachable) <= 1:
        raise ReachabilityError(
            f"the front door {ENTRY!r} reaches no other page — this is an href-parsing or "
            "markup failure, not {len(population) - 1} orphans; fix the parse before "
            "reading the orphan list"
        )
    retired = redirect_sources(site_root)
    signposts = redirect_pages(site_root)
    # AN UNWRITTEN PAGE IS NOT EXCUSED FROM THE ORPHAN RULE, and the first draft of this
    # module had that wrong. Excusing it looked prudent -- routing seven empty pages seemed
    # worse than leaving them stranded -- but the stub template says in its own body that a
    # stub is a deliberate published artefact ("This node exists to hold its place in the
    # domain graph ... It is not a to-do list in costume"), carries a Stub badge and states
    # that the explanation is not yet written. Designed-to-be-published is exactly the
    # director's subject, so a stub with no route in IS the defect, and excusing it would
    # have been this control quietly deciding a content question in the direction that made
    # its own verdict green. `unwritten_pages` survives as a COUNT, never as an excuse.
    return sorted(
        page
        for page in population - reachable
        if excluded(page, retired) is None
        and page not in signposts
    )


def stale_exclusions(site_root: Path = DEFAULT_SITE_ROOT) -> list[str]:
    """`STRUCTURAL_EXCLUSIONS` entries naming a path that no longer exists.

    Without this the one hand-authored list here would rot into an allowlist covering
    whatever later takes that filename — the exact shape that makes an exemption list the
    subject instead of the site.
    """
    site_root = Path(site_root)
    return sorted(p for p in STRUCTURAL_EXCLUSIONS if not (site_root / p).is_file())


def check(site_root: Path = DEFAULT_SITE_ROOT) -> list[str]:
    """Every failure, as human-readable lines. Empty list means the site is fully routed."""
    failures = [
        f"STALE EXCLUSION: {p!r} is excluded by name but no such page exists — remove the "
        "entry or restore the page"
        for p in stale_exclusions(site_root)
    ]
    failures += [
        f"NO ROUTE IN: {p!r} exists and renders but nothing reachable from the front door "
        "links to it — it is published to nobody"
        for p in orphans(site_root)
    ]
    return failures


def _report(site_root: Path) -> int:
    population = page_population(site_root)
    reachable, broken = crawl(site_root, population)
    retired = redirect_sources(site_root)
    failures = check(site_root)
    unwritten = unwritten_pages(site_root)
    signposts = redirect_pages(site_root)
    print(
        f"pages={len(population)}  reachable={len(reachable)}  "
        f"unwritten={len(unwritten)}  redirect-pages={len(signposts)}  "
        f"failures={len(failures)}"
    )
    for page in sorted(population - reachable):
        reason = excluded(page, retired)
        if reason:
            print(f"  ok (excluded) {page} — {reason}")
    # Counted and named every run: an unfinished section must not be able to hide inside a
    # green verdict just because "unwritten" is not "unreachable".
    for page in sorted(unwritten):
        print(f"  UNWRITTEN {page} — byte-identical to {STUB_TEMPLATE}, never authored")
    for page in sorted(signposts):
        print(f"  ok (redirect page) {page} — meta-refresh signpost, not a destination")
    for line in failures:
        print(f"  FAIL {line}")
    if broken:
        # Diagnostic only, never a failure: a different control's subject (see module docstring).
        print(f"  note: {len(broken)} link target(s) do not exist, e.g. {sorted(broken)[:3]}")
    return 1 if failures else 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--site-root", default=str(DEFAULT_SITE_ROOT), type=Path)
    args = ap.parse_args(argv)
    try:
        return _report(args.site_root)
    except ReachabilityError as exc:
        print(f"REFUSED: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":  # pragma: no cover - CLI
    raise SystemExit(main())
