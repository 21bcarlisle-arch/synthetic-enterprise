#!/usr/bin/env python3
"""What the method has shown: the experiments the supplier has run on itself, each with the status its
own published record gives it, for the Knowledge tab's "What we've learned" filter (director's steer of
5 Nov, item 2: "Method insight belongs there too ... That includes the 'we cannot tell' results and the
experiments that failed. M4 says the method is the asset, and this is its evidence").

WHAT A ROW IS, said before anything is counted: one question the method put to its world whose answer a
committed site feed already publishes. The question and where the full answer lives are typed here; the
status, the figures, the date and the sentence quoted are the feed's own. The rows are the experiments
whose feeds this module reads (SOURCES), not every question ever asked, and the page says so.

THE STATUS, one of five. HELD and DID NOT HOLD are reachable ONLY from a prediction filed before the run
(cold read, 8 Nov: an earlier version let three rows become "held" when their source merely reached a
state -- a reviewer measured, a comparison no longer provisional, a correlation outside its null --
whatever the result said, so the first such row would have published a refutation as "held"):
  held             -- a prediction filed before the run, and the run did not refute it.
  did not hold     -- a filed prediction the run refuted.
  withdrawn        -- a claim we published and later took back, kept with the reason.
  measured         -- a result with no prediction filed before it: it describes, it does not confirm.
  we cannot tell   -- the evidence does not settle it either way, and the source says so.

NOT A ROW: `engagement_separation.json`. Its own `by_construction` says the two traits are drawn
independently, so the figure checks the build and discovers nothing; publishing it here as a result
would be the build grading itself.

FAIL-CLOSED: a source feed that is missing or lacks the field its status is read from becomes a row
whose status is "we cannot tell" with the reason named, never a dropped row.

    python3 -m tools.method_results_feed          # the rows, as text
    python3 -m tools.method_results_feed --write  # also writes site/data/method_results.json
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = "site/data/method_results.json"
LOOP = "docs/design/THE_IMPROVEMENT_LOOP.md"
STATUSES = ("held", "did not hold", "withdrawn", "measured", "we cannot tell")


def _feed(root: Path, name: str) -> dict | None:
    try:
        d = json.loads((root / "site" / "data" / f"{name}.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    return d if isinstance(d, dict) else None


def _sentences(text: str) -> list[str]:
    return [s for s in re.split(r"(?<=[.!?])\s+", (text or "").strip()) if s]


def _row(id_, question, feed, page, status, finding, why, dated):
    assert status in STATUSES, status
    return {"id": id_, "question": question, "status": status, "finding": finding, "why_this_status": why,
            "dated": dated or "its source carries no date", "source": f"site/data/{feed}.json", "page": page}


def _unreadable(id_, question, feed, page, what):
    return _row(id_, question, feed, page, "we cannot tell", None,
                f"the source feed {what}, so its answer cannot be read here", None)


def dd_opening(root: Path) -> list[dict]:
    q = ("For accounts opened under the price cap, does sizing the first direct debit from an estimate "
         "beat waiting for the first bill?")
    page = "../capabilities/#dd-opening"
    d = _feed(root, "dd_opening_arms")
    fp = (d or {}).get("filed_prediction") or {}
    if fp.get("verdict") not in ("held", "refuted"):
        return [_unreadable("dd-opening", q, "dd_opening_arms", page, "carries no filed prediction with a verdict")]
    held = fp["verdict"] == "held"
    lo, hi = (fp.get("mean_change_in_abs_drift_ci95_gbp") or [None, None])[:2]
    figures = (f": across {fp.get('n_matched_accounts')} matched accounts the estimate moved the direct debit "
               f"£{-fp['mean_change_in_abs_drift_gbp']:,.2f} closer to the bill on average (95% interval "
               f"£{-hi:,.2f} to £{-lo:,.2f} closer), on the billed clock"
               if None not in (fp.get("mean_change_in_abs_drift_gbp"), lo, hi) else "")
    out = [_row("dd-opening", q, "dd_opening_arms", page, "held" if held else "did not hold", fp.get("statement"),
                f"a prediction filed on {fp.get('filed_on')}, before the run, which the run "
                f"{'did not refute' if held else 'refuted'}{figures}", fp.get("filed_on"))]
    # The claim this comparison published earlier and took back. It stays: "a result that went
    # against us stays". A feed without the field says so rather than dropping the row.
    earlier = d.get("earlier_claims")
    if not isinstance(earlier, list):
        return out + [_unreadable("dd-opening-earlier", q, "dd_opening_arms", page,
                                  "does not say what it published before")]
    for i, c in enumerate(earlier):
        rid = "dd-opening-withdrawn" + (f"-{i + 1}" if i else "")
        if not (c.get("the_words") and c.get("why")):
            out.append(_unreadable(rid, q, "dd_opening_arms", page, "names an earlier claim without its words or reason"))
            continue
        out.append(_row(rid, f"{q} (as published on {c.get('published_on')})", "dd_opening_arms", page,
                        "withdrawn", c["the_words"], c["why"], c.get("withdrawn_on")))
    return out


def pricing_arms(root: Path) -> list[dict]:
    q = "Does pricing each renewal for the customer earn more than one margin for everyone?"
    page = "../capabilities/#value-arms"
    d = _feed(root, "value_arms")
    if d is None or "provisional" not in d:
        return [_unreadable("pricing-arms", q, "value_arms", page, "is missing or does not say whether it is provisional")]
    wp = d.get("world_provenance") or {}
    split = wp.get("one_world_across_every_figure") is False
    why = ("the comparison marks itself provisional" + (
        f": its figures were measured in {len(wp.get('worlds_these_figures_were_measured_in') or [])} different "
        "worlds, so the spread from one cannot bound the figure from another" if split else "")
           if d["provisional"] else "no prediction was filed before the comparison ran")
    out = [_row("pricing-arms", q, "value_arms", page, "we cannot tell" if d["provisional"] else "measured",
                None, why, (d.get("run_generated_at") or "")[:10] or None)]
    w = d.get("withdrawn_claim") or {}
    words = _sentences(w.get("the_words"))
    reason = _sentences(w.get("why"))
    if words:
        middle = (reason and reason[0].lower().startswith("the middle sentence") and len(words) == 3)
        out.append(_row("pricing-arms-withdrawn",
                        "Did the flat-margin arm price exactly the same renewals as the per-customer arm?",
                        "value_arms", page, "withdrawn", words[1] if middle else w["the_words"],
                        re.sub(r"^The middle sentence was", "it was", reason[0]) if reason
                        else "the source records it as withdrawn and gives no reason",
                        w.get("withdrawn_on")))
    return out


def reviewers(root: Path) -> list[dict]:
    q = "Do the reviewers that pass finished work catch the defects that later surface?"
    page = "../harness/#meaning"
    d = _feed(root, "judge_validation")
    m = (d or {}).get("measurement_coverage") or {}
    if "all_measured" not in m:
        return [_unreadable("reviewers", q, "judge_validation", page, "carries no measurement coverage")]
    traced = m.get("judges_with_a_pass_record")
    why = (f"{len(m.get('measured_judges') or [])} of the {traced} reviewer{'s' if traced != 1 else ''} whose "
           f"passes are traced to later defects {'has' if traced == 1 else 'have'} the "
           f"{m.get('min_passes_for_measured_rate')} passes a measured error rate needs; the blind reviews in "
           "the review ledger are not traced to later defects at all")
    # No finding is quoted: the record's own note is written for the harness, not for a reader.
    return [_row("reviewers", q, "judge_validation", page, "measured" if m["all_measured"] else "we cannot tell",
                 None, why if not m["all_measured"] else "no prediction was filed before the rates were measured",
                 None)]


SOURCES = (pricing_arms, dd_opening, reviewers)


def build(root: Path = ROOT) -> dict:
    rows = [r for f in SOURCES for r in f(root)]
    return {"what_this_is": "The questions the method has put to its world whose answers are published, each "
                            "with the status its own record gives it. A result that went against us stays.",
            "statuses": list(STATUSES),
            "counts": {s: sum(r["status"] == s for r in rows) for s in STATUSES},
            "loop": {"design": LOOP,
                     "why": "the improvement loop has not gone round yet: its register is built once the "
                            "current correctness work is finished (the director's ruling of 26 Oct)"},
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
        print(f"{r['status']:<15} {r['id']:<22} {r['dated']:<12} {r['why_this_status'][:110]}")
        if r["finding"]:
            print(f"{'':<38}“{r['finding'][:110]}”")
    print(f"\n{feed['counts']}")
    if args.write:
        print(("wrote " if write(feed) else "unchanged ") + OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
