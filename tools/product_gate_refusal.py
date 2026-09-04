"""What the arm's product gate actually refused, read off the run's own per-value breakdown.

WHY THIS EXISTS (2026-09-04)
----------------------------
`site/data/value_arms.json` published this, under the largest single drop in the value arm's
funnel — 1,223 of 1,953 renewals, 62.6%:

    "A term carrying `None` is a DRAWN account, and the field is unset because the world has no
     standard-variable product to set it to -- `build_renewal_schedule` settles exactly fixed,
     flex, deemed and pass_through, and SVT exists only as a comparison benchmark."

Every clause of that was false when it was published. `simulation/svt_product.py` landed the
standard variable product on 2026-08-30, `simulation/renewals.build_renewal_schedule` delegates to
it (a passive renewal roll builds SVT segments, C1b), and `run_phase2b` passes
`tariff_type=c.get("tariff_type") or "fixed"` so no drawn electricity leg carries `None` any more.
The artefact the page was generated from said so in the same file, one key away: its
`product_not_upliftable_by_tariff_type` reads `{"'svt'": 1223}` — not one `None` among them.

So the page told a reader that a plumbing gap explained 62.6% of the arm's blindness, four days
after that gap was closed, while the evidence that refuted it sat unread in the artefact the page
was reading. The prose was a STRING and the breakdown was a MEASUREMENT, and a string cannot go
stale loudly.

THE SHAPE OF THE FIX
--------------------
The cause is DERIVED from the breakdown, here, in one place, and both the producer
(`tools/run_value_cycle_ab.py`, which writes the artefact) and the publisher
(`tools/generate_value_arms_data.py`, which renders the page from artefacts that may be weeks
old) call it. Two copies of a sentence about the world is how this one survived: it was written
into `FUNNEL_STAGE_MEANINGS` and into `_is_the_lever_reachable` and into
`_who_the_method_has_priced.what_is_owed`, and repairing any one of them would have left the
reader two others.

KEYED TO THE PROPERTY, NOT TO TODAY'S ANSWER. Nothing here asserts that the refusals are SVT.
Feed it a breakdown of `None`s and it says the records are unlabelled and that is a defect; feed
it SVT and it says the households are on a product with no renewal to price and that is the
market's shape; feed it both and it says both, with counts. The verdict a reader gets is a
reading of the run, and it changes when the run changes without anyone editing a sentence.

FAIL CLOSED. An artefact with no breakdown at all — every run before 2026-08-30 — gets an
explicit "this run did not record which products" and NOT the last confident sentence anybody
wrote. A value this module has never heard of is NAMED and left unexplained rather than folded
into a neighbouring clause, because an unexplained label is the finding.

REUSE
-----
REUSE: tools/product_gate_refusal.py
CLASS: CUSTOM
INDEX: searched "product gate refusal", "tariff type", "uplift", "funnel stage", "not
       upliftable", "exclusion", "why not priced".
       `company/crm/customer_profitability.UPLIFTABLE_TARIFF_TYPES` is the guard itself and is
       IMPORTED here, never restated — a second literal list of which products the arm prices is
       one name and two answers, and this module exists because prose about a guard drifted from
       the guard.
       `tools/run_value_cycle_ab.renewal_funnel` COUNTS the refusals by value and is the producer
       of the breakdown this reads; it deliberately does not interpret them, and the interpretation
       could not live there anyway because the page must interpret artefacts that module wrote
       weeks ago.
       `tools/generate_value_arms_data._exclusions` renders the funnel for the reader and is the
       CALLER; putting the derivation there would have left the artefact still born carrying a
       false `means` string for every other consumer.
       `simulation/svt_product.py` is the world side and is the SUBJECT, not a dependency — this
       module never imports `simulation`, because a site publisher that drags the world onto its
       import graph is a wall problem of its own.
"""
from __future__ import annotations

from company.interfaces.customer_profitability import UPLIFTABLE_TARIFF_TYPES

#: The key grammar of `renewal_funnel.product_not_upliftable_by_tariff_type`: `repr()` of the
#: world's own value, so a string label arrives quoted and an unset one arrives as `None`. Read
#: rather than reformatted, because the two are DIFFERENT facts — `"None"` (no product decided)
#: and `"'None'"` (a product literally named "None") would collapse into one bucket otherwise.
_UNLABELLED_KEY = "None"

#: What each product the gate can refuse MEANS, and whether the refusal is the world's shape or
#: our own defect. One entry per value; a value with no entry is named and left unexplained.
#:
#: `is_a_defect` is the load-bearing field and it is not a judgement about the arm. It asks: is
#: there a household here that a real supplier could have made a renewal offer to, which this
#: company failed to reach? An SVT household has no renewal to reach — its price is the published
#: cap and its segment boundaries are cap changes. An unlabelled record has one and we lost it.
PRODUCT_REFUSAL_MEANINGS: dict[str, dict] = {
    "svt": {
        "is_a_defect": False,
        "what_it_is": (
            "the household is on the standard variable product (`simulation/svt_product.py`). Its "
            "rate is the published Ofgem default-tariff cap, its segment boundaries are cap "
            "changes rather than expiries, and no notice is served and no offer made at one. The "
            "arm prices a RENEWAL by moving a struck rate; there is no struck rate here and no "
            "renewal at which to move one. A real supplier reaches this household by winning it "
            "onto a fixed deal, which is an acquisition decision and not this arm's."),
    },
    _UNLABELLED_KEY: {
        "is_a_defect": True,
        "what_it_is": (
            "the world settled this term without deciding what product it was. That is a defect "
            "in the record and not a fact about the market: a household on the book is on "
            "SOMETHING, and until 2026-08-30 every account this world drew or won carried the "
            "key present and unset, so the arm refused it on a shape rather than on a product "
            "(`docs/design/DRAWN_BOOK_TARIFF_TYPE_FIDELITY_DETERMINATION.md`)."),
    },
    "deemed": {
        "is_a_defect": False,
        "what_it_is": (
            "an out-of-contract deemed period — spot plus a premium, days long, priced at "
            "settlement. There is no locked margin for any arm to move."),
    },
    "flex": {
        "is_a_defect": False,
        "what_it_is": (
            "a flexible contract whose price is indexed rather than struck, so there is no locked "
            "margin for any arm to move."),
    },
}


def _value_of(key: str) -> str:
    """The world's own value, back out of the artefact's `repr()` key grammar.

    `"'svt'"` -> `"svt"`; `"None"` stays `"None"` and is the unlabelled bucket. Anything else is
    handed back untouched so it reaches the caller as the unrecognised value it is.
    """
    if len(key) >= 2 and key[0] == key[-1] and key[0] in ("'", '"'):
        return key[1:-1]
    return key


def refusal_breakdown(by_tariff_type) -> dict:
    """Read `product_not_upliftable_by_tariff_type` and say what it means. Never asserts.

    Returns, always:
      available            -- False when the run recorded no breakdown at all
      total                -- refusals accounted for
      rows                 -- one per value, count, share, meaning, and whether it is a defect
      defect_count         -- refusals that are OUR defect
      structural_count     -- refusals that are the world's product mix
      unexplained_values   -- values this module has no meaning for, NAMED
      why                  -- the sentence a reader gets, derived from the counts above
    """
    if not isinstance(by_tariff_type, dict) or not by_tariff_type:
        return {
            "available": False,
            "total": 0,
            "rows": [],
            "defect_count": 0,
            "structural_count": 0,
            "unexplained_values": [],
            "why": (
                "the term's `tariff_type` is not one this writer prices (`UPLIFTABLE_TARIFF_TYPES`"
                " = {}). WHICH products these were is NOT established here: this run recorded no "
                "per-value breakdown, so nothing on this page can say whether they are households "
                "on a product with no renewal to price or records whose product was never decided "
                "-- and those license opposite decisions. Re-run "
                "`python3 -m tools.run_value_cycle_ab` on a tree that carries "
                "`renewal_funnel.product_not_upliftable_by_tariff_type`."
            ).format(", ".join(sorted(UPLIFTABLE_TARIFF_TYPES))),
        }

    rows = []
    unexplained = []
    total = 0
    for key, count in sorted(by_tariff_type.items()):
        if not isinstance(count, int) or count < 0:
            continue
        total += count
        value = _value_of(str(key))
        meaning = PRODUCT_REFUSAL_MEANINGS.get(value)
        if meaning is None:
            unexplained.append(value)
        rows.append({
            "tariff_type": value,
            "count": count,
            "what_it_is": (meaning or {}).get(
                "what_it_is",
                "this surface has no established meaning for this product. It is NAMED rather "
                "than explained, because an unexplained label at the largest drop in the funnel "
                "is a finding and not a footnote."),
            # `None` for an unexplained value, never False: "we know it is not a defect" and "we
            # do not know what this is" are the two readings this whole module exists to keep
            # apart, and defaulting to False is the flattering one.
            "is_a_defect": None if meaning is None else meaning["is_a_defect"],
        })
    for row in rows:
        row["share_of_the_refusals"] = round(row["count"] / total, 4) if total else None

    defect = sum(r["count"] for r in rows if r["is_a_defect"] is True)
    structural = sum(r["count"] for r in rows if r["is_a_defect"] is False)
    return {
        "available": True,
        "total": total,
        "rows": sorted(rows, key=lambda r: -r["count"]),
        "defect_count": defect,
        "structural_count": structural,
        "unexplained_values": sorted(unexplained),
        "why": _why_sentence(rows, total, defect, structural, unexplained),
    }


def _why_sentence(rows: list[dict], total: int, defect: int, structural: int,
                  unexplained: list[str]) -> str:
    """The published cause, composed from the counts. Every clause is a count a reader can check.

    THE THREE READINGS ARE KEPT APART because they license opposite decisions: a defect says fix
    our code, a structural refusal says this is the market's shape and the ceiling is real, and
    an unexplained label says we do not yet know which. A version that reported the OR of them —
    or picked the largest and spoke as though it were all of them — is the mixed-subject failure
    this page has already published once.
    """
    head = ("the term's `tariff_type` is not one this writer prices (`UPLIFTABLE_TARIFF_TYPES` = "
            "{}). The breakdown beside this count is the evidence and this sentence is derived "
            "from it: ").format(", ".join(sorted(UPLIFTABLE_TARIFF_TYPES)))
    named = "; ".join("{:,} on `{}`".format(r["count"], r["tariff_type"]) for r in
                      sorted(rows, key=lambda r: -r["count"]))
    parts = [head + named + "."]

    if unexplained:
        parts.append(
            "{:,} of them carry a product this surface has no established meaning for ({}), so "
            "what bounds the arm here is NOT settled and the count below is not attributed."
            .format(sum(r["count"] for r in rows if r["is_a_defect"] is None),
                    ", ".join("`{}`".format(v) for v in unexplained)))

    if structural and not defect:
        parts.append(
            "None of it is a missing label. All {structural:,} are households the world settled "
            "on a product that has no renewal decision to price, so no repair to this company's "
            "code moves one of them into the arm's reach. THIS IS THE ARM'S CEILING AND IT IS A "
            "FACT ABOUT THE MARKET: only a household on a fixed deal has a renewal rate that can "
            "be moved, and the rest of a domestic book does not. Reaching them is an ACQUISITION "
            "decision -- winning them onto a fixed deal -- and this arm does not make it."
            .format(structural=structural))
    elif defect and not structural:
        parts.append(
            "All {defect:,} are OUR defect, not the market's shape: the world settled these terms "
            "without deciding what product they were, so the arm refused a record rather than a "
            "product. Every one of them is a household a real supplier would have made a renewal "
            "offer to.".format(defect=defect))
    elif defect and structural:
        parts.append(
            "The two halves are NOT the same finding. {structural:,} are households on a product "
            "with no renewal to price -- the arm's real ceiling, which no repair to our code "
            "moves -- and {defect:,} are terms the world settled without deciding what product "
            "they were, which is our defect and is reachable.".format(
                structural=structural, defect=defect))
    return " ".join(parts)


def is_a_company_defect(by_tariff_type) -> bool | None:
    """Whether ANY of the product-gate refusals is ours to fix. `None` when it is not established.

    Three-valued on purpose. A caller that needs "is the arm's small surface plumbing or market
    structure" gets `True`, `False`, or an honest "this run cannot say" — and the third is what an
    artefact predating the breakdown returns, so an old artefact can never be read as a clean bill.
    """
    result = refusal_breakdown(by_tariff_type)
    if not result["available"] or result["unexplained_values"]:
        return None
    return result["defect_count"] > 0
