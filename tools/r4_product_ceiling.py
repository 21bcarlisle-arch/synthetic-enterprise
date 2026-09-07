"""R4: THE PRODUCTS-BEYOND-PRICE CEILING — what advice, tariff fit and measures could be worth.

REUSE: tools/r4_product_ceiling.py
CLASS: CUSTOM
INDEX: searched "ceiling", "bound", "product", "advice", "tariff fit", "efficiency", "solar",
       "heat pump", "measure". Seven ceiling instruments now exist and none touches R4: five are
       EP13's dispatch bounds, one is R1's inference bound and one is R3's carbon bound. This is
       the same move on a different subject, and the CEILING-or-FLOOR declaration and the
       fail-closed population floors are taken from `tools/r1_inference_ceiling.py` and
       `tools/r3_carbon_score_ceiling.py` deliberately. THE TIME-SHIFTING ARM IS NOT RECOMPUTED
       HERE: R3 already bounds it and this reads R3's own artefact, because two implementations of
       one quantity is how a figure comes to have two values and no owner.

WHY THIS EXISTS
---------------
Director canon, 2026-09-04 (`DIRECTOR_CANON_RERANKING_THE_ARC`), R4 — Products beyond price:

    "Advice, tariff fit, efficiency measures, solar, heat pumps, time-shifting. Today the company
     can make a household cheaper and never greener, so THE MISSION IS UNREACHABLE regardless of
     how good the inference becomes. These decisions also differ far more between households than
     price does, which makes them where per-customer advantage actually lives."

R4 is the biggest unbuilt programme on the map. A49 exists so it is not built the way EP13 was —
twelve passes, the ceiling arriving at pass seven, five candidate programmes retired that would
otherwise have been built first and measured afterwards.

THE QUESTION, PER PRODUCT: the most it could be worth per household-year, under PERFECT TARGETING
and PERFECT ADOPTION, against the null of PRICE ALONE — the money-only lever the company already
has.

WHAT THIS INSTRUMENT ACTUALLY DELIVERS, and it is not a league table
---------------------------------------------------------------------
The deliverable is the **CEILING-or-FLOOR verdict per product**, because that is what decides
whether a negative retires anything, and it is decided by WHAT THE BOOK HOLDS rather than by how
promising the product sounds.

    CEILING    perfect knowledge of the quantity a real method approximates. A negative RETIRES
               the candidate outright.
    FLOOR      bounds from below only. A negative retires NOTHING.
    UNBOUNDED  the company holds no datum the bound would have to be computed from. This reports
               `None` with the missing field named — never 0.0, because an honest `None` cannot be
               read as an established answer and a zero can.

THREE THINGS THIS INSTRUMENT REFUSES TO DO, each because doing it is how a ceiling becomes a lie
-------------------------------------------------------------------------------------------------
1. **It refuses to SUM the products.** They are not disjoint. Advice is the CHANNEL through which
   time-shifting and tariff fit reach a household, not a seventh pot beside them; solar and a heat
   pump both change grid import and overlap; fabric and a heat pump overlap. A sum would
   double-count, and a total is the number a reader would quote.

2. **It refuses to add the two CURRENCIES.** Tariff fit's pounds are a BILL SAVING — money moved
   from the company (or a competitor) to the household. Time-shifting's pounds are CARBON VALUED at
   the traded price — not a bill saving at all, because this book holds no time-of-use tariff for a
   shifted kWh to be cheaper on. Two correct figures whose sum is not a quantity is this project's
   most expensive recurring shape, so the payload keeps them in separate columns and says why.
   THE MISSING TARIFF IS NOW SIZED AND STILL NOT ADDED: `tools/tou_sharing_ceiling.py` bounds what
   a time-of-use tariff could create, and the time-shifting arm carries that figure under
   `if_a_time_of_use_tariff_existed` while its own pounds column stays `None`. The size is a
   COUNTERFACTUAL about a product that does not exist; putting it in the column would publish a
   bill saving no household on this book can receive.

3. **It refuses to price a measure it has no property data for.** An engineering estimate — "this
   measure typically saves this much" — is defensible as a design input and never as a measured
   result (`ADVISOR_SCOPE_BRIEF_CARBON_2026-08-04` §C). Multiplying one by a book with no floor
   area, no EPC, no heating system and no roof would produce a confident number about nothing.

THE CENSUS THAT DECIDES THE VERDICTS is run, not assumed: `property_attribute_census` walks every
log in the run output looking for any fabric, EPC, floor-area, roof, insulation or occupancy field.
If one is ever added, the verdict for the measure products moves on its own and this instrument
stops saying what it says today.
"""
from __future__ import annotations

import argparse
import json
import statistics
import sys
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent
if str(PROJECT) not in sys.path:
    sys.path.insert(0, str(PROJECT))

from tools.r3_carbon_score_ceiling import (  # noqa: E402
    CeilingUnavailable,
    book_run_output,
    electricity_eac,
)

#: The SHARING ceiling's artefact path, taken from the instrument that owns it rather than
#: restated here -- a second copy of a path is how an artefact comes to be written to one place
#: and read from another. Its CONTENTS are read, never recomputed, for the same reason the carbon
#: above is read from R3: two implementations of one quantity is how a figure gets two values and
#: no owner. It never fills the pounds column, because on THIS book the bill saving from shifting
#: really is zero and that is the finding.
from tools.tou_sharing_ceiling import OUT_PATH as TOU_ARTEFACT  # noqa: E402

OUT_PATH = PROJECT / "docs" / "observability" / "r4_product_ceiling.json"
R3_ARTEFACT = PROJECT / "docs" / "observability" / "r3_carbon_score_ceiling.json"

CEILING = "CEILING"
FLOOR = "FLOOR"
UNBOUNDED = "UNBOUNDED"

#: Fewest households a product arm reports over. FAIL CLOSED, and matched to R3's floor for the
#: same reason: an arm that returns "0 households, £0.00" reads exactly like "measured, worth
#: nothing", which is the opposite claim to "measured nothing".
MIN_HOUSEHOLDS = 20

#: Any field name containing one of these would let a measure be sized for a specific home. The
#: list is the SUBJECT of the census, not a filter over a known answer — it is deliberately wide,
#: because a census that only looks for what it expects cannot report a surprise.
PROPERTY_ATTRIBUTE_MARKERS = (
    "fabric", "epc", "floor_area", "floorarea", "roof", "insulat", "loft", "wall_type",
    "occupan", "bedroom", "dwelling", "property_", "heating_system", "boiler", "u_value",
    "orientation", "glazing", "tenure", "build_year", "construction",
)

#: What each measure product would need before it could be bounded at all. Named per product so the
#: gap is a work item rather than a shrug.
MISSING_FOR = {
    "efficiency_fabric": (
        "floor area, wall and loft construction, and a heating system — the fabric parameters an "
        "engineering estimate is a function of"
    ),
    "solar": (
        "roof area, pitch and orientation, plus a shading assessment. Nothing in the book "
        "distinguishes a south-facing roof from a north-facing one, and the whole value turns on it"
    ),
    "heat_pump": (
        "the incumbent heating system and fuel, plus the fabric above — a heat pump's saving is "
        "the difference against what it replaced, so without the incumbent there is no difference"
    ),
}


def property_attribute_census(payload: dict) -> dict:
    """Every field in the run output that could size a measure for a specific home.

    RUN, NOT ASSUMED. The measure arms' FLOOR verdicts rest entirely on this coming back empty, so
    it is computed from the payload each time rather than stated in prose. If the world ever starts
    writing a fabric parameter, this finds it and those verdicts move on their own — which is the
    difference between a control keyed to the PROPERTY and one pinned to today's answer.
    """
    found: dict[str, int] = {}
    logs = 0
    for log_name, rows in payload.items():
        if not (isinstance(rows, list) and rows and isinstance(rows[0], dict)):
            continue
        logs += 1
        for row in rows[:500]:
            for field in row:
                lowered = field.lower()
                if any(marker in lowered for marker in PROPERTY_ATTRIBUTE_MARKERS):
                    found[f"{log_name}.{field}"] = found.get(f"{log_name}.{field}", 0) + 1
    return {"logs_scanned": logs, "attributes_found": dict(sorted(found.items()))}


def fabric_eligibility(payload: dict) -> dict:
    """How many households the world will even admit fabric parameters for.

    Carried because it is the honest size of the efficiency arm's REACHABLE population, and it is
    not the same question as the census above: eligibility says a household COULD have fabric
    parameters, the census says whether any parameter reaches the company's book. A book can be
    eligible and blind at the same time, and here it is.
    """
    rows = payload.get("fabric_eligibility")
    if not (isinstance(rows, list) and rows):
        return {"available": False, "why": "the run output carries no fabric_eligibility log"}
    eligible = sum(1 for r in rows if r.get("is_eligible") is True)
    return {
        "available": True,
        "rows": len(rows),
        "eligible": eligible,
        "share": round(eligible / len(rows), 4),
        "reason_given": next(
            (r.get("reason") for r in rows if r.get("is_eligible") is True), None),
    }


def rate_against_reference(payload: dict) -> dict[str, dict[str, float]]:
    """household -> its contracted rate and the market reference on the same day, £/MWh.

    Both are on the company's own book: the rate is what it charged, and the market reference is
    the comparator its own pricing chain already reads. So the tariff-fit bound stays the right
    side of the epistemic wall.

    BOTH FIELDS COME OFF THE SAME ROW, and that is a correction rather than a preference — the
    first draft of this function collected rates from every log and references from the one log
    that carries them, then differenced the two per-household MEANS. It returned £88.21 per
    household-year, and the figure was an artefact: the rate was averaged over every priced term a
    household ever had, the reference only over its renewal occasions, and GB electricity prices
    move by a factor of three across 2016-2025. Differencing two averages taken over different
    windows is not a price gap, it is a price TREND. Printing the numbers at real inputs is what
    caught it. The two quantities are only comparable on the same day, so only rows carrying both
    are read.
    """
    per_id: dict[str, list[tuple[float, float]]] = {}
    for rows in payload.values():
        if not (isinstance(rows, list) and rows and isinstance(rows[0], dict)):
            continue
        for row in rows:
            cid = row.get("customer_id")
            rate = row.get("unit_rate_gbp_per_mwh")
            reference = row.get("market_reference_gbp_per_mwh")
            if not cid:
                continue
            if not all(isinstance(v, (int, float)) and not isinstance(v, bool) and v > 0
                       for v in (rate, reference)):
                continue
            per_id.setdefault(str(cid), []).append((float(rate), float(reference)))
    return {
        cid: {
            "rate_gbp_per_mwh": statistics.fmean([r for r, _ in pairs]),
            "reference_gbp_per_mwh": statistics.fmean([m for _, m in pairs]),
            "occasions": len(pairs),
        }
        for cid, pairs in sorted(per_id.items())
    }


def tariff_fit_ceiling(payload: dict, eac: dict[str, float]) -> dict:
    """The most perfect tariff fit could be worth: every household at the market reference.

    A TRUE CEILING ON THE MONEY, because the company holds both sides of the subtraction — the rate
    it charged and the reference its own pricing chain reads. Nothing buildable beats putting every
    household on the better of the two.

    ONLY THE POSITIVE SIDE COUNTS. A household already below the reference is not a source of
    negative value that a perfect method would harvest; a perfect method leaves it alone. Summing
    the signed differences would net a saving against a household the programme would never touch,
    which understates the ceiling and would be the wrong direction for a bound.

    AND ITS CARBON CEILING IS EXACTLY ZERO, BY RULE AND NOT BY MEASUREMENT. The director's standing
    rule: savings count only from reduced or time-shifted usage, never from discounting. A cheaper
    tariff moves money; the household burns the same kWh at the same hours. This is the canon's own
    charge -- "the company can make a household cheaper and never greener" -- as arithmetic.
    """
    pairs = rate_against_reference(payload)
    shared = sorted(set(pairs) & set(eac))
    if len(shared) < MIN_HOUSEHOLDS:
        return {
            "product": "tariff_fit",
            "bound_kind": UNBOUNDED,
            "gbp_per_household_year": None,
            "kg_co2e_per_household_year": 0.0,
            "households": len(shared),
            "why": (
                f"only {len(shared)} household(s) carry a rate, a market reference AND an "
                f"electricity EAC together, and this arm reports nothing under {MIN_HOUSEHOLDS}. "
                "That is a data-availability refusal and NOT a finding that tariff fit is worthless."
            ),
        }
    savings = []
    above = 0
    for cid in shared:
        gap = pairs[cid]["rate_gbp_per_mwh"] - pairs[cid]["reference_gbp_per_mwh"]
        if gap > 0:
            above += 1
        savings.append(max(0.0, gap) * eac[cid] / 1000.0)
    return {
        "product": "tariff_fit",
        "bound_kind": CEILING,
        "gbp_per_household_year": round(statistics.fmean(savings), 2),
        "kg_co2e_per_household_year": 0.0,
        "carbon_is_zero_by_rule": (
            "The director's standing rule: savings count only from reduced or time-shifted usage, "
            "never from discounting. A cheaper tariff moves money and changes no kWh and no hour, "
            "so its abatement is zero by rule and not by measurement."
        ),
        "households": len(shared),
        "households_above_the_reference": above,
        "book_gbp_per_year": round(sum(savings), 2),
        "why_a_ceiling": (
            "The company holds both sides of the subtraction -- the rate it charged and the "
            "market reference its own pricing chain reads -- so putting every household on the "
            "better of the two is the best any targeting could do. A negative here would retire "
            "tariff fit outright."
        ),
    }


def time_shifting_ceiling() -> dict:
    """R3's own answer, READ rather than recomputed.

    Two implementations of one quantity is how a figure comes to have two values and no owner, and
    this repository has already paid for that once with the VAT rule -- one legal requirement, five
    implementations, a defect fixed in one of them in July and still live in another in August.
    """
    if not R3_ARTEFACT.exists():
        raise CeilingUnavailable(
            f"{R3_ARTEFACT.name} is not present, so R4's time-shifting arm has nothing to read. "
            "Run `python3 -m tools.r3_carbon_score_ceiling --save` first. This arm will NOT "
            "recompute the quantity R3 owns."
        )
    r3 = json.loads(R3_ARTEFACT.read_text(encoding="utf-8"))
    rung = r3.get("corrected_headline") or r3["rungs"]["forecast_ceiling"]
    return {
        "product": "time_shifting",
        "bound_kind": CEILING,
        "gbp_per_household_year": None,
        "carbon_value_gbp_per_household_year": rung["gbp_per_household_year"],
        "kg_co2e_per_household_year": rung["kg_co2e_per_household_year"],
        "source": "tools/r3_carbon_score_ceiling.py — read, not recomputed",
        "why_the_gbp_column_is_None": (
            "R3's pounds are CARBON VALUED at the traded price, not a bill saving. A shifted kWh "
            "is cheaper only on a time-of-use tariff and this book holds none, so the BILL saving "
            "from shifting is zero here and the carbon value sits in its own column. Adding it to "
            "tariff fit's pounds would sum two different quantities."
        ),
        "at_shiftable_share": 1.0,
        "caveat": (
            "R3's figure is at a shiftable share of 1.0 -- every kWh moved -- because no source "
            "establishes a domestic shiftable share. At a tenth of load moved it is a tenth."
        ),
        "if_a_time_of_use_tariff_existed": the_sharing_ceiling(),
    }


def the_sharing_ceiling() -> dict:
    """What the pounds column WOULD carry if this book held a time-of-use tariff.

    IT DOES NOT FILL THE POUNDS COLUMN, and that is deliberate rather than timid. On this book the
    bill saving from shifting is zero -- there is no tariff on which a shifted kWh is cheaper --
    and that zero IS the finding. What was missing was the SIZE of the gap: a reader could see the
    arm had no pounds and could not see whether the missing product was worth a penny or fifty.

    READ, never recomputed, for the same reason the carbon above is read from R3.
    """
    if not TOU_ARTEFACT.exists():
        return {
            "available": False,
            "why": (
                f"{TOU_ARTEFACT.name} is not present, so the size of the missing product is not "
                "known here. Run `python3 -m tools.tou_sharing_ceiling --save`. The pounds column "
                "above is unaffected: it is None because this book holds no time-of-use tariff, "
                "not because this artefact is absent."
            ),
        }
    tou = json.loads(TOU_ARTEFACT.read_text(encoding="utf-8"))
    created = tou.get("created_value") or {}
    reachable = tou.get("reachable_book") or {}
    carbon = tou.get("the_carbon_column") or {}
    frontier = tou.get("sharing_frontier") or []
    interior = tou.get("the_interior_optimum") or {}
    #: DERIVED, never restated: the two shares sum to the created value at every pass-through, or
    #: this goes false and the page stops claiming an identity it no longer has. Keyed to the
    #: property rather than to today's rows, which is the only version that can go red for the
    #: right reason.
    created_gbp = created.get("gbp_per_household_year")
    the_split_is_an_identity = bool(frontier) and created_gbp is not None and all(
        abs(row.get("household_gbp_per_household_year", 0.0)
            + row.get("company_gbp_per_household_year", 0.0) - created_gbp) < 0.01
        for row in frontier
    )
    return {
        "available": True,
        "source": "tools/tou_sharing_ceiling.py — read, not recomputed",
        "created_gbp_per_household_year": created.get("gbp_per_household_year"),
        "times_the_carbon_value_of_the_same_act": carbon.get("money_over_carbon"),
        "reachable_households": reachable.get("households"),
        "reachable_book_gbp_per_year": reachable.get("book_gbp_per_year"),
        "why_it_is_not_added_to_this_arm": (
            "It is a COUNTERFACTUAL about a product that does not exist, and this arm reports what "
            "THIS book can do. Adding it would publish a bill saving no household on this book can "
            "receive. It is carried beside the None so the size of the missing product is visible: "
            "the gap is not a rounding error, it is the largest bounded figure in R4."
        ),
        "and_only_this_column_can_be_shared": (
            "The carbon lands on nobody's bill, so no tariff can share it. The money does. That "
            "makes the tariff the PRECONDITION for the abatement rather than a way of monetising "
            "it -- the money is what pays for the behaviour that abates."
        ),
        # THE SHARING SIDE ITSELF, which is the half the instrument was built to bound and the
        # half that reached no reader: the size of the created value was published and how it
        # DIVIDES was not. These three travel together or not at all, for the reason below.
        "the_split_is_an_identity": the_split_is_an_identity,
        "the_optimum_is_interior": interior.get("therefore"),
        "where_the_optimum_sits": interior.get("what_it_does_NOT_say"),
        "why_the_frontier_ROWS_are_not_published_here": (
            "The frontier holds the created value FIXED, so its rows are conditional on the shift "
            "happening at all. Its zero-pass-through row therefore reads `company keeps the whole "
            "ceiling`, and that is not a take anyone could bank: at zero pass-through a household's "
            "bill is identical whenever it draws, so nothing moves and nothing is created. "
            "Published as a row it would read as value the company could keep for doing nothing -- "
            "value TRANSFERRED dressed as value CREATED, which is the one substitution the mission "
            "forbids. So the identity travels with the endpoints that bound it and never alone."
        ),
    }


def measure_arm(product: str, census: dict, eligibility: dict) -> dict:
    """One of the three physical measures — and each is a FLOOR, for a reason that is measured.

    `None`, never 0.0. An honest `None` with a named reason is worth more than a plausible number,
    because the number will be read as established and the `None` cannot be.
    """
    return {
        "product": product,
        "bound_kind": FLOOR,
        "gbp_per_household_year": None,
        "kg_co2e_per_household_year": None,
        "why_a_floor_and_not_a_ceiling": (
            "The company holds NO property attribute to target on -- the census over this run "
            f"found {len(census['attributes_found'])} across {census['logs_scanned']} logs -- so "
            "no per-household bound can be computed. Whatever number a book-average engineering "
            "estimate produced would bound from below at best, and A NEGATIVE WOULD THEREFORE "
            "RETIRE NOTHING. That is the distinction A49 requires be stated, and it is the "
            "opposite of R3's."
        ),
        "missing_data": MISSING_FOR[product],
        "reachable_population": eligibility,
    }


def advice_arm(arms: dict) -> dict:
    """Advice is a CHANNEL, not a seventh pot, and saying so is the point of this arm.

    Its ceiling is the union of the levers it can deliver, and a reader who added it to those
    levers would count the same value twice. `C30_advice_reaches_a_household` is the atom that
    builds the channel; this bounds what there is for the channel to carry.
    """
    deliverable = [name for name in ("time_shifting", "tariff_fit")
                   if arms.get(name, {}).get("bound_kind") == CEILING]
    return {
        "product": "advice",
        "bound_kind": CEILING if deliverable else UNBOUNDED,
        "gbp_per_household_year": None,
        "kg_co2e_per_household_year": None,
        "not_additive": True,
        "why": (
            "Advice is the CHANNEL through which time-shifting and tariff fit reach a household, "
            "not a value pot beside them. Its ceiling IS their ceiling and adding it to theirs "
            "would count the same value twice. What advice can add beyond them is the measures "
            "-- and those are FLOORS for want of property data, so advice inherits that too."
        ),
        "delivers": deliverable,
        "bounded_by": "the union of the arms it delivers, never their sum",
    }


def measure(run_path: Path | None = None) -> dict:
    run_path = run_path or book_run_output()
    payload = json.loads(run_path.read_text(encoding="utf-8"))
    eac = electricity_eac(payload)
    if len(eac) < MIN_HOUSEHOLDS:
        raise CeilingUnavailable(
            f"{run_path.name} carries {len(eac)} household(s) with an electricity EAC and this "
            f"instrument reports nothing under {MIN_HOUSEHOLDS}. That is a data-availability "
            "refusal and NOT a finding that R4 is worthless."
        )

    census = property_attribute_census(payload)
    eligibility = fabric_eligibility(payload)

    arms: dict[str, dict] = {
        "tariff_fit": tariff_fit_ceiling(payload, eac),
        "time_shifting": time_shifting_ceiling(),
    }
    for product in ("efficiency_fabric", "solar", "heat_pump"):
        arms[product] = measure_arm(product, census, eligibility)
    arms["advice"] = advice_arm(arms)

    bounded = [a for a in arms.values() if a["bound_kind"] == CEILING]
    floors = [a for a in arms.values() if a["bound_kind"] == FLOOR]

    return {
        "bound_kind": "MIXED — declared per product, and the split IS the finding",
        "bound_kind_reason": (
            "A49 requires each instrument to state whether it is a true CEILING (a negative "
            "retires the candidate outright) or a handicapped FLOOR (a negative retires nothing). "
            "R4 is not one programme, so it does not get one answer: the arms the company holds "
            "both sides of are CEILINGS, and the arms that need a property attribute are FLOORS "
            "because the company holds no property attribute at all."
        ),
        "book": {
            "source_run": run_path.name,
            "households": len(eac),
            "median_eac_kwh": round(statistics.median(eac.values()), 1),
        },
        "property_attribute_census": census,
        "fabric_eligibility": eligibility,
        "arms": arms,
        "refuses_to_total": (
            "There is no total here and that is deliberate. The products are NOT disjoint (advice "
            "is the channel for the others; solar and a heat pump both change grid import) and "
            "the columns are NOT one currency (tariff fit's pounds are a bill saving, "
            "time-shifting's are carbon valued at the traded price). A sum would double-count "
            "across products and add two quantities across currencies, and it is the number a "
            "reader would quote."
        ),
        "verdict": {
            "ceilings": [a["product"] for a in bounded],
            "floors": [a["product"] for a in floors],
            "the_bounded_arm_that_abates": [
                a["product"] for a in bounded
                if (a.get("kg_co2e_per_household_year") or 0.0) > 0.0
            ],
            "the_bounded_arm_that_does_not": [
                a["product"] for a in bounded
                if (a.get("kg_co2e_per_household_year") or 0.0) == 0.0
                and a.get("gbp_per_household_year") is not None
            ],
        },
        "named_gaps": [
            "PROPERTY ATTRIBUTES. Nothing in the book distinguishes one home's fabric, roof or "
            "heating system from another's. This is the single acquisition that would turn three "
            "FLOORS into CEILINGS, and it is a data question rather than a modelling one.",
            "A TIME-OF-USE TARIFF. Without one a shifted kWh is not cheaper, so time-shifting has "
            "a carbon ceiling and no bill-saving ceiling at all. That is a product decision, and "
            "it is what would let the household share in the value R3 measures. IT IS NOW SIZED: "
            "`tools/tou_sharing_ceiling.py` bounds it, and the arm carries the figure under "
            "`if_a_time_of_use_tariff_existed` -- the gap is the largest bounded number in R4.",
            "Book depth (A46) bounds how much any of this can be DEMONSTRATED over.",
        ],
    }


def headline(result: dict) -> str:
    arms = result["arms"]
    tariff = arms["tariff_fit"]
    shifting = arms["time_shifting"]
    census = result["property_attribute_census"]
    floors = result["verdict"]["floors"]

    money = (f"£{tariff['gbp_per_household_year']:.2f}"
             if tariff.get("gbp_per_household_year") is not None else "unbounded")
    return (
        f"R4 SPLITS, AND THE SPLIT IS THE ANSWER. Of six products, "
        f"{len(result['verdict']['ceilings'])} are true CEILINGS and {len(floors)} are FLOORS "
        f"({', '.join(floors)}) -- because the property-attribute census over "
        f"{census['logs_scanned']} logs found {len(census['attributes_found'])} attributes, so a "
        "measure cannot be sized for a specific home and a negative would retire nothing. "
        f"THE PART WE CAN BOUND IS THE PART THAT CANNOT ABATE: tariff fit is worth {money} per "
        "household-year and its carbon ceiling is EXACTLY ZERO by the director's own rule, "
        "because discounting moves money and changes no kWh and no hour. The part that abates -- "
        f"time-shifting, at {shifting['kg_co2e_per_household_year']:.1f} kgCO2e per "
        "household-year -- carries no bill saving at all, because this book holds no "
        "time-of-use tariff for a shifted kWh to be cheaper on. So the canon's charge is "
        "confirmed by arithmetic rather than by assertion: the company can make a household "
        "cheaper and never greener. AND BOTH BOUNDED ARMS ARE SMALL: "
        f"{money} of bill saving and "
        f"£{shifting['carbon_value_gbp_per_household_year']:.2f} of carbon value per "
        f"household-year, only {tariff['households_above_the_reference']} of "
        f"{tariff['households']} households priced above the market reference at all. So the "
        "whole of the part of R4 this book can bound is worth a few pounds a household-year, and "
        "any real value in the programme lives in the arms that are FLOORS. R4 IS NOT RETIRED -- "
        "nothing here bounds the measures from above -- but what stands between it and a bound "
        "is a DATA ACQUISITION, not a model."
    )


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--run", type=Path, default=None)
    parser.add_argument("--save", action="store_true", help=f"write {OUT_PATH.name}")
    args = parser.parse_args(argv)

    try:
        result = measure(run_path=args.run)
    except CeilingUnavailable as exc:
        print(f"REFUSED: {exc}")
        return 2

    result["headline"] = headline(result)
    print(json.dumps(result, indent=2))
    print("\n" + result["headline"])
    if args.save:
        OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
        OUT_PATH.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
        print(f"\nwrote {OUT_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
