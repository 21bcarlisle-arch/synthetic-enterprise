#!/usr/bin/env python3
"""Generate site/data/book_growth.json -- the growth curve WITH the reason it has that shape.

THE DIRECTOR'S INSTRUCTION, 2026-08-24 console, verbatim: *"if our own code binds growth rather
than the simulated economics, say so on the site and fix it if it's cheap. A growth curve that's
an artefact of our engine is an inconsistency, not a result."*

The campaign already knows. `simulation.live_population._resolve_campaign` writes
`docs/observability/book_growth_campaign.json` with per-year quotes, wins, spend, the market it
faced and the BINDING reason, and its own comment says it is persisted "because the site has to be
able to say WHICH constraint stopped the book". Nothing read it. The record was written every run
and reached no reader, so on the published site a flat year still looked like one thing when it
could be any of four:

  capital       -- the supplier could not afford to quote. A commercial result.
  growth_rate   -- the supplier CHOSE not to grow faster than its own mandate. A commercial result.
  market        -- almost nobody was switching that year (2022 is 0.44x the 2024 normal). A REAL
                   world fact, and the one most likely to be misread as failure.
  settlement_engine -- OUR machine refused to settle the wins. NOT a result. An artefact.

Those are four different facts and they look identical on a chart. This makes the difference
legible instead of leaving it to be inferred.

SITE_CONSTITUTION rule 3: the site is a RENDERING, never an author. Every number here is copied or
counted from the campaign record; nothing is derived that the run did not already decide, and no
figure is invented when the record is absent -- a missing record produces `available: false` and a
reason, never a zero that would read as "the company won nothing".
"""
import json
from datetime import datetime, timezone
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent
CAMPAIGN_PATH = PROJECT / "docs" / "observability" / "book_growth_campaign.json"
OUT_PATH = PROJECT / "site" / "data" / "book_growth.json"

#: What each `binding` value means to a reader, and -- the point of the whole file -- whether it is
#: a fact about the COMPANY or a fact about our MACHINE. `artefact: true` is the director's
#: "inconsistency, not a result".
BINDING_MEANING = {
    "capital": {
        "label": "Capital",
        "artefact": False,
        "meaning": "The supplier could not afford more quotes from the headroom above its "
                   "regulatory capital requirement. A commercial result.",
    },
    "growth_rate": {
        "label": "Own mandate",
        "artefact": False,
        "meaning": "The supplier could have afforded more but caps its own growth rate. A "
                   "deliberate commercial choice, not a limit imposed on it.",
    },
    "market": {
        "label": "The market",
        "artefact": False,
        "meaning": "Too few households were switching supplier that year for the campaign to "
                   "spend its budget. A real feature of the GB market, not a company failure.",
    },
    "settlement_engine": {
        "label": "Our settlement engine",
        "artefact": True,
        "meaning": "This machine refused to settle the accounts the company won. NOT a "
                   "commercial result -- a limit of the simulation, surfaced rather than hidden.",
    },
    "mandate": {
        "label": "No growth mandate",
        "artefact": False,
        "meaning": "The supplier was not running acquisition campaigns that year.",
    },
}


def _binding_of(row: dict) -> str:
    return str(row.get("binding") or "unknown")


#: What a reader is told about a learned conversion rate our own engine helped produce.
CONTAMINATED_CAVEAT = (
    "The company computed this from its own books, and its books say it quoted and did not win. "
    "But an earlier year's wins were refused by OUR settlement engine, so some of the losses in "
    "that denominator were never a commercial event. The company's inference is sound; the world "
    "it inferred from was not."
)
CLEAN_CAVEAT = (
    "Computed over years the market and the company's own balance sheet decided, with no year "
    "our settlement engine bound. This conversion rate is a commercial result."
)


def _mark_learned_rate_provenance(years: list[dict]) -> None:
    """Say which learned win rates were computed over a history OUR engine had already touched.

    WHY THIS IS NOT THE SAME FLAG AS `binding_is_our_artefact`, and why getting it wrong would be
    worse than omitting it. That flag answers "did our engine stop the book THIS year". This
    answers a different question -- "was the number the company PLANNED on computed over a history
    that includes such a year" -- and the two diverge in both directions:

      * 2020 was engine-bound AND still won 22 accounts. Its learned rate came from 2016-2019,
        all commercial. Flagging it because it is itself engine-bound would caveat a clean number.
      * 2021 was engine-bound too, but the thing that matters about its learned rate is that the
        rate was computed over a history INCLUDING 2020 -- and from there the contamination is
        permanent, because the company's history only grows.

    So the rule is STRICTLY EARLIER, and it latches: once an engine-bound year enters the history,
    every later learned rate carries it. That is why the published series decays 0.169 -> 0.051
    while nothing commercial suppressed the conversion
    (WORKER_FINDING_THE_COMPANY_NOW_LEARNS_A_WIN_RATE_FROM_YEARS_AN_ENGINEERING_CAP_DECIDED).

    NOT A WALL VIOLATION, and the distinction is the whole design. The COMPANY still learns the
    contaminated rate and still plans on it -- nothing here changes a single company-side number,
    because a supplier that could tell which of its own losses were artefacts would be reading
    simulation internals. What changes is what the SITE tells its reader, which is the harness's
    own job and the one place the fact is legitimately known.
    """
    seen_engine_bound = False
    for y in years:
        # `planning_on` "belief"/"mandate" means no learned rate was used at all, so there is
        # nothing to caveat -- and saying otherwise would attach a warning to a number the
        # company never computed.
        learned = y.get("realised_win_rate_used") is not None and y.get("planning_on") == "realised"
        y["learned_win_rate_is_contaminated"] = bool(learned and seen_engine_bound)
        y["learned_win_rate_caveat"] = (
            CONTAMINATED_CAVEAT if y["learned_win_rate_is_contaminated"]
            else (CLEAN_CAVEAT if learned else "")
        )
        if y["binding_is_our_artefact"]:
            seen_engine_bound = True


def build(campaign: dict | None) -> dict:
    """The published shape. `campaign` is the record, or None when there is no run to describe."""
    stamp = datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")
    if not campaign or not campaign.get("by_year"):
        # FAIL LOUD AND EMPTY, never zero. A curve of zeroes would read as a supplier that won
        # nothing, which is a claim; "we have no record" is the truth.
        return {
            "generated_at": stamp,
            "available": False,
            "reason": "no campaign record on disk -- no run has assembled a book since this "
                      "generator was wired, so there is no growth curve to render.",
            "years": [],
        }

    years = []
    for row in campaign["by_year"]:
        binding = _binding_of(row)
        meaning = BINDING_MEANING.get(binding, {
            "label": binding, "artefact": False,
            "meaning": "Unrecognised binding reason -- shown verbatim rather than guessed at.",
        })
        years.append({
            "year": row.get("year"),
            "quotes_issued": row.get("quotes_issued"),
            "wins": row.get("wins"),
            "accounts_after": row.get("accounts_after"),
            "spend_gbp": row.get("spend_gbp"),
            "clock": "settled",
            "homes_in_market": row.get("homes_in_market"),
            "switching_multiplier": row.get("switching_multiplier"),
            "binding": binding,
            "binding_label": meaning["label"],
            "binding_is_our_artefact": meaning["artefact"],
            "binding_meaning": meaning["meaning"],
            # What the company BELIEVED its conversion was that year, against what its own books
            # said. Both are the company's own numbers; the gap is the point.
            "believed_win_rate": row.get("believed_win_rate"),
            "realised_win_rate_used": row.get("realised_win_rate_used"),
            "planning_on": row.get("planning_on"),
        })

    artefact_years = [y["year"] for y in years if y["binding_is_our_artefact"]]
    _mark_learned_rate_provenance(years)
    contaminated = [y["year"] for y in years if y["learned_win_rate_is_contaminated"]]
    return {
        "generated_at": stamp,
        "available": True,
        "years": years,
        "totals": {
            "quotes": campaign.get("quotes"),
            "wins": campaign.get("wins"),
            "spend_gbp": campaign.get("spend_gbp"),
            "clock": "settled",
        },
        "settlement": {
            "customer_years_committed": campaign.get("customer_years_committed"),
            "customer_year_budget": campaign.get("customer_year_budget"),
        },
        # THE HEADLINE THE DIRECTOR ASKED FOR, stated rather than left to be read off a chart.
        "engine_bound_years": artefact_years,
        "engine_bound_statement": (
            "In {n} of {t} years the book was stopped by OUR settlement engine and not by the "
            "market or the company's balance sheet ({yrs}). Those years understate what this "
            "supplier would have won, and the flat curve there is an artefact of the "
            "simulation rather than a commercial result.".format(
                n=len(artefact_years), t=len(years),
                yrs=", ".join(str(y) for y in artefact_years))
        ) if artefact_years else (
            "No year was bound by our settlement engine: every year's growth was decided by the "
            "market, the company's capital, or its own growth mandate."
        ),
        # THE SECOND HALF OF THE SAME INSTRUCTION. The curve is not the only thing our engine
        # shaped: the company LEARNS its conversion rate from these years and plans the next
        # campaign on it, so an engine-bound year does not just flatten one bar -- it lowers
        # every learned rate after it, and the quote budget (and the acquisition spend a reader
        # would use to judge whether growth was worth it) is computed from that.
        "learned_win_rate_contaminated_years": contaminated,
        "win_rate_statement": (
            "From {first} onward the conversion rate the company planned on was computed over a "
            "history our own settlement engine had already bound, so it falls without any "
            "commercial mechanism suppressing it. Read the decline as an artefact of this "
            "simulation, not as a supplier losing its touch -- and note the quote budget, and "
            "therefore the acquisition spend, is derived from that same rate.".format(
                first=contaminated[0])
        ) if contaminated else (
            "Every conversion rate the company planned on was computed over years the market and "
            "its own balance sheet decided. None of them is an artefact of our engine."
        ),
        "notes": campaign.get("notes") or [],
    }


def generate(out_path: Path | None = None, campaign_path: Path | None = None) -> dict:
    src = CAMPAIGN_PATH if campaign_path is None else campaign_path
    try:
        campaign = json.loads(src.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        campaign = None
    data = build(campaign)
    dest = OUT_PATH if out_path is None else out_path
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    return data


if __name__ == "__main__":
    d = generate()
    print("wrote {} (available={}, {} year(s), engine-bound: {})".format(
        OUT_PATH, d["available"], len(d["years"]), d.get("engine_bound_years")))
