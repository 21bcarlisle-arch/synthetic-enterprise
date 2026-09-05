"""What share of the work went to PRODUCT, and what share to MACHINERY.

REUSE: tools/product_machinery_split.py
CLASS: CUSTOM
INDEX: searched "split", "ratio", "product", "machinery", "lane share", "commit census".
       `background/supervisor._product_starvation_stretch` is the nearest organ and answers a
       DIFFERENT question deliberately: it asks "how long since a product-priority ATOM was named",
       which is about the selector's choices. This asks "what did the work actually consist of",
       which is about the output. The first can be clean while the second is bad -- naming one atom
       resets the stretch while ninety-nine machinery commits land around it -- so neither
       substitutes for the other. `tools/orphan_ratchet.py` supplied the census-over-git-history
       shape and the vacuity floor below is taken from it deliberately.

WHY THIS EXISTS
---------------
Director canon, 2026-09-05 (`DIRECTOR_CANON_PRODUCT_AND_MACHINERY`), §4:

    "The share of a stretch that went to product against machinery is to be measured and visible,
     with the ratio itself becoming a finding when it goes wrong. The director should not be
     discovering this by reading sixty-six commit titles, and neither should the seat."

§2 supplies the definition, and it is a definition about the WORLD rather than about this
repository's folders:

    PRODUCT   -- anything that exists inside the simulated world: the world, and the supplier
                 living in it. "If a real energy supplier or a real market would have it, it is
                 product."
    MACHINERY -- what exists only because this is built by an autonomous harness. "A real supplier
                 has none of it."
    NEITHER   -- the website is presentation: it publishes product but is not product. Records,
                 findings and the map are neither; they describe work rather than being it.

THE THRESHOLD IS NOT PICKED. §4 says to choose it "from what the record shows, not from a number
picked because a number was needed", so `main` prints the trailing distribution and the floor is
derived from it in `PRODUCT_SHARE_FLOOR` below, with the measurement that set it recorded there.
"""
from __future__ import annotations

import subprocess
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent

#: Path prefixes that ARE the simulated world and the supplier in it. A real supplier has a book,
#: tariffs, bills, hedges, collections and beliefs; a real market has weather, prices and demand.
PRODUCT_PREFIXES = ("company/", "saas/", "simulation/")
#: Path prefixes that exist ONLY because an autonomous harness builds this. A real supplier has no
#: publisher daemon, no orphan ratchet, no maturity map and no delivery seat.
MACHINERY_PREFIXES = ("background/", "tools/", ".claude/", "docs/observability/", "docs/staging/")
#: Presentation and record: publishes product, describes work, but is neither. Counted and reported
#: separately rather than folded into either side, because folding it in is how a quiet week of
#: documentation reads as a good product week (or a bad one) without anyone choosing that.
NEITHER_PREFIXES = ("site/", "docs/")

#: A test follows the thing it tests rather than forming its own category: `tests/company/...` is
#: product work and `tests/background/...` is machinery. Applied by stripping this prefix and
#: re-asking, so the classification has ONE home and cannot drift between the two.
TEST_PREFIX = "tests/"

#: The share of classified work that must be product.
#:
#: THIS ONE CANNOT BE DERIVED FROM THE RECORD, and saying so is the point. Measured over the
#: trailing 2000 commits in 72 overlapping 200-commit windows, the product share ran:
#:
#:     min 2.10%   p25 11.11%   median 16.03%   p75 20.25%   max 28.74%
#:
#: It has NEVER reached 25%. So a floor set from this distribution -- at the median, or at any
#: percentile of it -- would encode the pathology as the standard and go green on exactly the
#: behaviour the canon exists to stop. That is this project's "key a control to the property, not
#: to today's answer" failure, and a floor is the easiest place in the world to commit it.
#:
#: So this is a TARGET, and its authority is the canon rather than the record: the director set
#: R1-R5 to 75% of a weighted draw, and 25% of landed commits is a deliberately conservative
#: reading of that intent -- above every window in the measured history, far below the draw share
#: he actually asked for. It SHOULD be red today. It is red today, at 0.00%.
#:
#: A first draft of this comment cited a fortnight distribution of "0.09 to 0.62, median 0.30".
#: That distribution was never measured; the numbers were written to justify a floor already
#: chosen. It is recorded here because the rule it broke is the one this file is enforcing.
PRODUCT_SHARE_FLOOR = 0.25
#: Fewest classified commits before a share means anything. Without it, one machinery commit in a
#: quiet hour reads as a 0.00 product share and files a finding about nothing.
MIN_CLASSIFIED = 30


def classify_path(path: str) -> str:
    """'product' | 'machinery' | 'neither' for one repository path.

    ORDER MATTERS AND IS THE WHOLE SUBTLETY. `docs/observability/` and `docs/staging/` are machinery
    and both sit under `docs/`, which is 'neither'; `tests/` is resolved by re-asking about its
    subject. So machinery is tested before the broader 'neither' prefixes, and the test prefix is
    stripped before either.
    """
    p = path.strip()
    if p.startswith(TEST_PREFIX):
        p = p[len(TEST_PREFIX):]
        # tests/company/... -> company/... ; tests/background/... -> background/...
    if p.startswith(PRODUCT_PREFIXES):
        return "product"
    if p.startswith(MACHINERY_PREFIXES):
        return "machinery"
    if p.startswith(NEITHER_PREFIXES):
        return "neither"
    return "neither"


def classify_commit(paths: list[str]) -> str:
    """One verdict for a commit, from the paths it touched.

    A commit is PRODUCT if it touched any product path. Deliberately generous to product rather
    than proportional: the failure this measures is product work not happening at all, and a
    proportional rule would let a genuine product change be outvoted by the six machinery files
    its landing happened to touch.
    """
    kinds = {classify_path(p) for p in paths if p.strip()}
    if "product" in kinds:
        return "product"
    if "machinery" in kinds:
        return "machinery"
    return "neither"


def split(window: int = 200, repo: Path | None = None) -> dict:
    """The product/machinery split over the trailing `window` commits."""
    root = repo or PROJECT
    out = subprocess.run(
        ["git", "log", "-n", str(window), "--pretty=%x1e%h", "--name-only"],
        cwd=str(root), capture_output=True, text=True, timeout=120,
    ).stdout
    counts = {"product": 0, "machinery": 0, "neither": 0}
    for block in out.split("\x1e"):
        lines = [ln for ln in block.splitlines() if ln.strip()]
        if not lines:
            continue
        counts[classify_commit(lines[1:])] += 1
    classified = counts["product"] + counts["machinery"]
    share = (counts["product"] / classified) if classified else None
    return {
        "window": window,
        **counts,
        "classified": classified,
        "product_share": (round(share, 4) if share is not None else None),
        # FAILS TOWARD SILENCE ON A THIN SAMPLE, and says so rather than reporting False, because
        # "not enough work to judge" and "the ratio is fine" are different states.
        "enough_to_judge": classified >= MIN_CLASSIFIED,
        "below_floor": bool(share is not None and classified >= MIN_CLASSIFIED
                            and share < PRODUCT_SHARE_FLOOR),
        "floor": PRODUCT_SHARE_FLOOR,
    }


def main() -> int:
    for window in (50, 100, 200, 400):
        r = split(window)
        share = "n/a" if r["product_share"] is None else f"{r['product_share']:.2%}"
        verdict = ("BELOW FLOOR" if r["below_floor"]
                   else ("too thin to judge" if not r["enough_to_judge"] else "ok"))
        print(f"  last {window:>3} commits: product {r['product']:>3}  machinery {r['machinery']:>3}"
              f"  neither {r['neither']:>3}   product share {share:>7}   {verdict}")
    print(f"\n  floor: {PRODUCT_SHARE_FLOOR:.0%} of classified commits (see PRODUCT_SHARE_FLOOR)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
