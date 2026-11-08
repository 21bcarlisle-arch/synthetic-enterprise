#!/usr/bin/env python3
"""What the method has shown: the experiments the supplier has run on itself, each with the status its
own published record gives it, for the Knowledge tab's "What we've learned" filter (director's steer of
5 Nov, item 2: "Method insight belongs there too ... That includes the 'we cannot tell' results and the
experiments that failed. M4 says the method is the asset, and this is its evidence").

WHAT A ROW IS, said before anything is counted: one question the method put to the world, read from the
committed site feed that already publishes its answer. Nothing here is typed by hand except the question
and where on the site the full answer lives; the status and the sentence quoted are the feed's own.

THE STATUS, one of five, each computed from a field the source feed carries:
  held             -- a prediction filed before the run, and the run did not refute it.
  did not hold     -- a filed prediction the run refuted.
  no association   -- the measured relation sits inside what shuffling the pairs produces.
  withdrawn        -- a claim we published and later took back, kept with the reason.
  we cannot tell   -- the evidence does not settle it either way, and the source says so.

The improvement loop's own register (docs/design/THE_IMPROVEMENT_LOOP.md section 5) is held behind the
correctness stretch's exit test, so it has no rounds to report yet; the feed says so rather than
implying the loop has run.

FAIL-CLOSED: a source feed that is missing or lacks the field its status is read from becomes a row
whose status is "we cannot tell" with the reason named, never a dropped row.

    python3 -m tools.method_results_feed          # the rows, as text
    python3 -m tools.method_results_feed --write  # also writes site/data/method_results.json
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = "site/data/method_results.json"
LOOP = "docs/design/THE_IMPROVEMENT_LOOP.md"
STATUSES = ("held", "did not hold", "no association", "withdrawn", "we cannot tell")


def _feed(root: Path, name: str) -> dict | None:
    try:
        d = json.loads((root / "site" / "data" / f"{name}.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    return d if isinstance(d, dict) else None


def _row(id_, question, feed, page, status, finding, why):
    assert status in STATUSES, status
    return {"id": id_, "question": question, "status": status, "finding": finding, "why_this_status": why,
            "source": f"site/data/{feed}.json", "page": page}


def _unreadable(id_, question, feed, page, what):
    return _row(id_, question, feed, page, "we cannot tell", None,
                f"the source feed {what}, so its answer cannot be read here")


def dd_opening(root: Path) -> list[dict]:
    q = "Does sizing a new account's first direct debit from an estimate beat waiting for its first bill?"
    page = "../capabilities/#dd-opening"
    d = _feed(root, "dd_opening_arms")
    fp = (d or {}).get("filed_prediction") or {}
    if fp.get("verdict") not in ("held", "refuted"):
        return [_unreadable("dd-opening", q, "dd_opening_arms", page, "carries no filed prediction with a verdict")]
    held = fp["verdict"] == "held"
    return [_row("dd-opening", q, "dd_opening_arms", page, "held" if held else "did not hold", fp.get("statement"),
                 f"a prediction filed on {fp.get('filed_on')} before the run, which the run "
                 f"{'did not refute' if held else 'refuted'}")]


def pricing_arms(root: Path) -> list[dict]:
    q = "Does pricing each renewal for the customer earn more than one margin for everyone?"
    page = "../capabilities/#value-arms"
    d = _feed(root, "value_arms")
    if d is None or "provisional" not in d:
        return [_unreadable("pricing-arms", q, "value_arms", page, "is missing or does not say whether it is provisional")]
    out = [_row("pricing-arms", q, "value_arms", page, "we cannot tell" if d["provisional"] else "held",
                d.get("provisional_note") if d["provisional"] else d.get("headline"),
                "the comparison marks itself provisional: its error bar is wider than the effect it measures"
                if d["provisional"] else "the comparison is no longer marked provisional")]
    w = d.get("withdrawn_claim") or {}
    if w.get("the_words"):
        out.append(_row("pricing-arms-withdrawn", "A claim about the flat-margin arm, published and taken back",
                        "value_arms", page, "withdrawn", w["the_words"],
                        f"withdrawn on {w.get('withdrawn_on')}: " + (w.get("why") or "").split(". ")[0] + "."))
    return out


def engagement(root: Path) -> list[dict]:
    q = "Are the households that do not shop around also the ones least moved by price?"
    page = "../capabilities/#engagement-separation"
    d = _feed(root, "engagement_separation")
    a = (d or {}).get("association") or {}
    if "outside_the_null" not in a:
        return [_unreadable("engagement", q, "engagement_separation", page, "carries no association against a shuffled null")]
    return [_row("engagement", q, "engagement_separation", page,
                 "held" if a["outside_the_null"] else "no association", d.get("headline"),
                 f"rank correlation {a['rho']:+.2f} across {a['n']} households, "
                 f"{'outside' if a['outside_the_null'] else 'inside'} the {a['null_low']:+.2f} to "
                 f"{a['null_high']:+.2f} that {a['permutations']:,} shuffles produce")]


def reviewers(root: Path) -> list[dict]:
    q = "Do the fresh-context reviewers that pass finished work catch the defects that later surface?"
    page = "../harness/#meaning"
    d = _feed(root, "judge_validation")
    m = (d or {}).get("measurement_coverage") or {}
    if "all_measured" not in m:
        return [_unreadable("reviewers", q, "judge_validation", page, "carries no measurement coverage")]
    # No finding is quoted: the record's own note is written for the harness, not for a reader, and
    # the status line below already says everything it does.
    return [_row("reviewers", q, "judge_validation", page, "held" if m["all_measured"] else "we cannot tell",
                 None,
                 f"{len(m.get('measured_judges') or [])} of {m.get('judges_with_a_pass_record')} reviewers have "
                 f"the {m.get('min_passes_for_measured_rate')} passes a measured error rate needs")]


SOURCES = (pricing_arms, dd_opening, engagement, reviewers)


def build(root: Path = ROOT) -> dict:
    rows = [r for f in SOURCES for r in f(root)]
    return {"what_this_is": "The questions the method has put to its world, each with the status its own "
                            "published record gives it. A result that went against us stays.",
            "statuses": list(STATUSES),
            "counts": {s: sum(r["status"] == s for r in rows) for s in STATUSES},
            "loop": {"design": LOOP, "rounds": 0,
                     "why": "the improvement loop's register is built after the correctness stretch's exit "
                            "test, so no area has gone round it yet"},
            "rows": rows}


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
        print(f"{r['status']:<15} {r['id']:<22} {r['why_this_status'][:90]}")
    print(f"\n{feed['counts']}")
    if args.write:
        print(("wrote " if write(feed) else "unchanged ") + OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
