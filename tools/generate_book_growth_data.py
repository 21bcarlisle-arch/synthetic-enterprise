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
    # THE OTHER HALF OF THE SAME CAP, and the two carry opposite instructions to a reader.
    # `market` above is the REAL switching rate binding a year -- a commercial result, and
    # raising anything would falsify it. This is our own `PROSPECTS_PER_YEAR` binding it, which
    # is an artefact and should be raised. `quote_capacity` has worded them apart since PB3;
    # until 2026-08-29 neither reached `binding`, so both years rendered as `growth_rate` and
    # our ceiling was published as the supplier's own mandate.
    "prospect_ceiling": {
        "label": "Our prospect pool",
        "artefact": True,
        "meaning": "The company could afford more quotes than there were prospects for it to "
                   "quote. The cap is net_new_acquisition.PROSPECTS_PER_YEAR -- a constant of "
                   "ours, NOT the GB switching market -- so this year understates what this "
                   "supplier would have done.",
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
    "The company computed this from its own books, but it does not match what its FUNNEL won "
    "over the same years -- so some of the losses in that denominator were our settlement "
    "engine refusing a win rather than a prospect saying no. The company's inference is sound; "
    "the world it inferred from was not."
)
CLEAN_CAVEAT = (
    "Checked against what the company's own funnel converted over the same years, and equal to "
    "it: this conversion rate counts commercial outcomes only, with no settlement refusal in "
    "the denominator."
)
#: The third state, and it exists because the other two are a claim either way. A record with
#: no `funnel_wins` cannot be checked, and an unchecked rate must never render as a checked one.
UNCHECKABLE_CAVEAT = (
    "This campaign record does not carry the funnel's own win count, so whether our settlement "
    "engine is inside this rate CANNOT BE CHECKED. Read it as unverified, not as clean."
)


def _mark_learned_rate_provenance(years: list[dict]) -> None:
    """Say whether the rate the company planned on has our settlement engine inside it.

    KEYED TO THE PROPERTY, NOT TO A YEAR LABEL, and the rewrite of 2026-08-29 is why this
    docstring is worth reading. The old rule was positional: find the years where
    `binding == settlement_engine`, then latch every later learned rate as contaminated. It
    was correct for the mechanism it was written against and it decayed twice in four days.

      * 2026-08-28 moved the company's own `wins_to_date` onto FUNNEL wins, so the rate
        stopped being contaminated at source -- but this flag kept caveating it, and the
        published `win_rate_statement` still told readers the series "decays 0.169 -> 0.051"
        when the shipped record had been flat at ~0.175 for a day.
      * 2026-08-29 replaced the stop-the-year ceiling with a uniform sample, so NO year is
        engine-bound and the same flag would have flipped to silence -- publishing "none of
        them is an artefact of our engine" while four wins in five were refused.

    One flag, two opposite failures, both from asking WHICH YEAR instead of asking the
    question the reader has. The question is: is the number the company planned on equal to
    what its own funnel converted over the earlier years? That is checkable against the
    record on every row, it is true or false for a reason, and it goes red if anyone re-wires
    the planner onto booked wins -- which is the defect it exists to catch.

    NOT A WALL VIOLATION, and the distinction is the whole design. The COMPANY still learns
    whatever its books say and still plans on it -- nothing here changes a single company-side
    number, because a supplier that could tell which of its own losses were artefacts would be
    reading simulation internals. What changes is what the SITE tells its reader, which is the
    harness's own job and the one place the fact is legitimately known.
    """
    cum_quotes = 0
    cum_funnel = 0
    for y in years:
        # `planning_on` "belief"/"mandate" means no learned rate was used at all, so there is
        # nothing to caveat -- and saying otherwise would attach a warning to a number the
        # company never computed.
        used = y.get("realised_win_rate_used")
        learned = used is not None and y.get("planning_on") == "realised"
        expected = (cum_funnel / cum_quotes) if cum_quotes else None
        checkable = learned and expected is not None and y.get("funnel_wins") is not None

        if not learned:
            contaminated, caveat = False, ""
        elif not checkable:
            # FAIL CLOSED. A record that does not carry `funnel_wins` cannot be checked, and
            # "unchecked" must not render as "clean" -- that is the shape that publishes a
            # reassurance nobody verified.
            contaminated, caveat = True, UNCHECKABLE_CAVEAT
        elif abs(used - expected) <= 1e-6 * max(1.0, abs(expected)):
            contaminated, caveat = False, CLEAN_CAVEAT
        else:
            contaminated, caveat = True, CONTAMINATED_CAVEAT

        y["learned_win_rate_is_contaminated"] = contaminated
        y["learned_win_rate_caveat"] = caveat
        cum_quotes += y.get("quotes_issued") or 0
        cum_funnel += y.get("funnel_wins") or 0


#: WHY THE RECORD IS ABSENT, and the three answers carry three different instructions to a reader.
#: They were one string until 2026-08-29, and that string -- "no run has assembled a book since this
#: generator was wired" -- asserted a fact about HISTORY that this generator cannot observe and that
#: is false in the commonest case: `book_growth_campaign.json` is a RUN OUTPUT, untracked and not
#: gitignored, so every fresh checkout has none however many books have been assembled. A reader
#: sent to check whether the generator got wired up is being sent to the wrong place. `generate()`
#: knows which of the three it hit and now says so; a reason that names its cause is how the refusal
#: itself becomes checkable.
ABSENCE_REASON = {
    "missing": "no campaign record at {path} on this tree. That file is a RUN OUTPUT, not a "
               "committed artefact, so a checkout that has not run the simulation has none -- "
               "run the simulation to produce one. It does NOT mean no book was ever assembled.",
    "unreadable": "no campaign record could be read: {path} is present on this tree but did not "
                  "parse. What the company won CANNOT BE READ from it. That is a defect in "
                  "whatever wrote the file, not a supplier that won nothing.",
    "empty": "no campaign record with any years in it: {path} parsed but carries no campaign. A "
             "run wrote the record and put no years in it, which is a producer defect, not a "
             "supplier that won nothing.",
}

#: What we say when nobody told us which of the three it was -- a direct `build(None)` call. It
#: claims no cause, because asserting one we did not observe is the defect above.
UNKNOWN_ABSENCE_REASON = (
    "no campaign record was given to this generator, and it was not told why. What the company "
    "won CANNOT BE READ from it -- this is an absent record, not a supplier that won nothing."
)


def build(campaign: dict | None, absence: str | None = None) -> dict:
    """The published shape. `campaign` is the record, or None when there is no run to describe.

    `absence` is why there is no record -- a key of `ABSENCE_REASON`, or None when the caller does
    not know. It only ever reaches the unavailable branch, so a caller that has a record can ignore
    it and the old one-argument signature still means what it did.
    """
    stamp = datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")
    if not campaign or not campaign.get("by_year"):
        # FAIL LOUD AND EMPTY, never zero. A curve of zeroes would read as a supplier that won
        # nothing, which is a claim; "we have no record" is the truth. The reason must be the
        # truth too: this branch is reached by three different failures and they are not
        # interchangeable, so an unrecognised `absence` falls back to claiming no cause at all
        # rather than to the first plausible one.
        rel = CAMPAIGN_PATH.relative_to(PROJECT).as_posix()
        template = ABSENCE_REASON.get(absence or "")
        return {
            "generated_at": stamp,
            "available": False,
            "absence": absence if template else None,
            "reason": template.format(path=rel) if template else UNKNOWN_ABSENCE_REASON,
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
            # THE THREE NUMBERS THAT MAKE UP A YEAR'S GROWTH, on the row rather than only in
            # the campaign total, because "the market gave us this many and we settled this
            # many" is a per-year fact and the identity funnel_wins == wins + refused is only
            # checkable if all three are here.
            "funnel_wins": row.get("funnel_wins"),
            "wins_refused_by_settlement_budget": row.get(
                "wins_refused_by_settlement_budget"),
            # THE SUPPLIER'S ACCOUNT COUNT AND THE BOOK'S, which stopped being the same number
            # on 2026-08-29. `accounts_after` is what the company holds and sizes its capital
            # against; `book_after` is what this machine settled.
            "accounts_after": row.get("accounts_after"),
            "book_after": row.get("book_after"),
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

    # TWO LISTS, BECAUSE THERE ARE NOW TWO ARTEFACTS AND ONE NAME CANNOT BE TRUE OF BOTH.
    # `engine_bound_years` means what it says -- years the SETTLEMENT engine stopped -- and is
    # empty since the ceiling became a sample. `artefact_bound_years` is the wider set: any
    # year bound by a constant of ours rather than by the market or the company's own
    # balance sheet, which since 2026-08-29 also includes `PROSPECTS_PER_YEAR`. Letting the
    # prospect-pool years quietly join a list called "engine bound" is how a name stops being
    # checkable, which is the failure this whole file spent the day repairing.
    artefact_years = [y["year"] for y in years if y["binding_is_our_artefact"]]
    engine_years = [y["year"] for y in years if y["binding"] == "settlement_engine"]
    prospect_years = [y["year"] for y in years if y["binding"] == "prospect_ceiling"]
    _mark_learned_rate_provenance(years)
    contaminated = [y["year"] for y in years if y["learned_win_rate_is_contaminated"]]

    # HOW MUCH OF WHAT THE COMPANY WON REACHED THE BOOK. Read from the campaign's own record,
    # never recomputed here (SITE_CONSTITUTION rule 3: this file renders, it does not author).
    # `None` when the record does not carry it, which is a state the statement below must say
    # out loud rather than default to the flattering branch -- a record with no rate is a
    # record we cannot read, not a run in which nothing was refused.
    raw_rate = campaign.get("settlement_sample_rate")
    sample_rate = (
        float(raw_rate)
        if isinstance(raw_rate, (int, float)) and not isinstance(raw_rate, bool)
        else None
    )
    funnel_wins = sum(y["funnel_wins"] or 0 for y in years)
    refused = sum(y["wins_refused_by_settlement_budget"] or 0 for y in years)
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
        #
        # IT IS KEYED TO THE SAMPLE RATE, NOT TO `binding`, and that is a 2026-08-29 repair
        # rather than a preference. Until then our engine STOPPED a year dead when it ran out
        # of customer-years, so "which years were engine-bound" was the right question and
        # `binding == settlement_engine` was the right way to ask it. It now takes a uniform
        # sample of the whole campaign instead, so NO year is stopped and that question's
        # answer is honestly "none" -- at which point this statement would have told the
        # reader "no year was bound by our settlement engine" while the engine was refusing
        # four wins in five. A control keyed to yesterday's answer goes quiet exactly when the
        # mechanism it watches changes shape. This one is keyed to the property: how much of
        # what the company won reached the book.
        "engine_bound_years": engine_years,
        "artefact_bound_years": artefact_years,
        "prospect_ceiling_years": prospect_years,
        # THE SECOND ARTEFACT GETS ITS OWN SENTENCE, because it carries the opposite
        # instruction from the thin-market years it used to be lumped with: this one should be
        # RAISED, and 2022's real switching collapse must never be.
        "prospect_ceiling_statement": (
            "In {n} year(s) ({yrs}) the company could afford more quotes than there were "
            "prospects to quote. That cap is OURS (net_new_acquisition.PROSPECTS_PER_YEAR = "
            "400, sized when the company could afford tens), not the GB switching market — "
            "those years understate what this supplier would have done.".format(
                n=len(prospect_years), yrs=", ".join(str(y) for y in prospect_years))
        ) if prospect_years else (
            "No year was capped by our prospect pool: where the campaign was short of quotes "
            "it was the company's own capital or the real switching market that decided."
        ),
        "settlement_sample_rate": sample_rate,
        "settlement_wins_refused": refused,
        "settlement_funnel_wins": funnel_wins,
        # WHAT EACH PER-YEAR COUNT SELECTS (2026-08-29,
        # `docs/design/ACCOUNT_POPULATION_CENSUS_2026-08-29.md`). This page carries the two
        # numbers whose divergence makes "which supplier?" a live question rather than a
        # pedantic one, and it named neither. Six populations were live across the repository's
        # artefacts at once and the collateral desk was netting Ofgem capital against a seventh.
        "what_each_count_selects": {
            "accounts_after": (
                "THE COMMERCIAL BOOK: founders plus every account the funnel won, settled or "
                "not. This is the supplier a real Ofgem return would describe, and it is what "
                "the growth desk sizes its capital headroom against — correctly, because it "
                "nets it against the FOUNDING CAPITAL, the same supplier's balance sheet."
            ),
            "book_after": (
                "THE SETTLED BOOK: the sample of those accounts our settlement engine could "
                "process. Its difference from `accounts_after` is entirely an engineering "
                "artefact of ours. Every figure derived from the run's own settled records — "
                "treasury, margin, the collateral desk's MCR — describes THIS supplier, so a "
                "capital figure netted against `accounts_after` would be mixing the two."
            ),
        },
        "engine_bound_statement": (
            "The company won {fw:,} accounts and OUR settlement engine could settle {bw:,} of "
            "them — a uniform {pct:.1f}% sample, {refused:,} wins refused. Every year is "
            "represented in proportion to what it won, so the SHAPE of this curve is "
            "commercial; its HEIGHT is our machine. Divide a booked count by {rate:.3f} to "
            "read the supplier rather than the sample.".format(
                fw=funnel_wins, bw=funnel_wins - refused, refused=refused,
                pct=sample_rate * 100.0, rate=sample_rate)
        ) if sample_rate is not None and sample_rate < 1.0 else (
            "Our settlement engine settled every account the company won: the book below is "
            "the supplier, not a sample of it. No year's growth was limited by this machine."
        ) if sample_rate is not None else (
            "This campaign record does not carry a settlement sample rate, so what share of "
            "the company's wins reached the book CANNOT BE READ FROM IT. Treat the book below "
            "as a lower bound on what this supplier won, not as what it won."
        ),
        # THE SECOND HALF OF THE SAME INSTRUCTION. The curve is not the only thing our engine
        # shaped: the company LEARNS its conversion rate from these years and plans the next
        # campaign on it, so an engine-bound year does not just flatten one bar -- it lowers
        # every learned rate after it, and the quote budget (and the acquisition spend a reader
        # would use to judge whether growth was worth it) is computed from that.
        "learned_win_rate_contaminated_years": contaminated,
        "win_rate_statement": (
            "From {first} onward the conversion rate the company planned on does not match what "
            "its own funnel converted over the same years, so our settlement engine is inside "
            "the number it planned the next campaign on. Read any decline as an artefact of "
            "this simulation, not as a supplier losing its touch -- and note the quote budget, "
            "and therefore the acquisition spend, is derived from that same rate.".format(
                first=contaminated[0])
        ) if contaminated else (
            "Every conversion rate the company planned on was CHECKED against what its own "
            "funnel converted over the earlier years, and equals it. Our settlement engine "
            "decides how much of the book we settle; it is not inside the rate the company "
            "plans on."
        ),
        "notes": campaign.get("notes") or [],
    }


def generate(out_path: Path | None = None, campaign_path: Path | None = None) -> dict:
    src = CAMPAIGN_PATH if campaign_path is None else campaign_path
    # THE READ IS THE ONLY PLACE THAT CAN TELL THESE APART. `OSError` and `ValueError` were caught
    # together and both became "no record on disk", which is a false sentence about a file that is
    # on disk and corrupt. Split at the only site that has the evidence.
    campaign, absence = None, None
    try:
        campaign = json.loads(src.read_text(encoding="utf-8"))
    except OSError:
        absence = "missing"
    except ValueError:
        absence = "unreadable"
    else:
        if not campaign or not campaign.get("by_year"):
            absence = "empty"
    data = build(campaign, absence)
    dest = OUT_PATH if out_path is None else out_path
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    return data


if __name__ == "__main__":
    d = generate()
    print("wrote {} (available={}, {} year(s), engine-bound: {})".format(
        OUT_PATH, d["available"], len(d["years"]), d.get("engine_bound_years")))
