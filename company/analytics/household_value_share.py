"""The household's side of the score — what a customer kept, in pounds.

INDEX: searched "household saving", "value created", "value shared", "customer
       saving", "fair value", "counterfactual price", "vs SVT", "price cap
       saving". Nearest existing modules, and why each is not this one:
       `company.analytics.customer_value_view` builds the supplier's OPINION
       about what a customer is worth TO US (cost-to-serve, churn risk, CLV) —
       the other side of the same ledger, and its docstring says so.
       `company.compliance.fair_value_assessment_register` is the closest in
       INTENT (Consumer Duty: "benefit received proportionate to price paid")
       and the furthest in GRAIN: it is an annual, per-product-category board
       assessment with no per-customer figure, and it is one of the company-side
       orphans ruled `unhooked` in the orphan disposition register.
       `company.crm.switching_cba` scores whether a SAVE is worth making to us.
       None of them answers "what did this household keep", so this module is
       new rather than a rename.

       NAMED BY DOTTED MODULE, NOT BY REPO PATH, AND THAT IS DELIBERATE:
       `tools/capability_index.py` counts a repo-relative `.py` path appearing
       anywhere in a module's text as a CALLER, docstrings included, so citing a
       rejected candidate the obvious way silently un-orphans it. Found the hard
       way — the first draft of this docstring flipped
       `fair_value_assessment_register` from orphan to wired and made its
       disposition row report STALE. Filed as
       `WORKER_FINDING_THE_REUSE_CONVENTION_MANUFACTURES_FALSE_CALLERS_2026-08-28`.

WHY IT EXISTS (atom `A47_the_score_has_no_household_side`; director, 2026-08-28)
-------------------------------------------------------------------------------
The mission: "creating enterprise value by automating ways to find individual
customers we can create value for, and SHARING in that value — by saving them
money, time and carbon". Value is created and then shared, so every decision has
two sides. The score had one: SURVIVE and EARN are the company's by
construction, and ABATE — though it counts a household's tonnes — is SCORED as
our £/tCO₂e, and is not instrumented at all yet. Nothing anywhere computed what a
household kept.

That absence is not cosmetic. It is the structural reason the profit maximiser
kept finding the price cap
(`WORKER_FINDING_THE_CHURN_MODELS_CAP_MAKES_THE_PROFIT_MAXIMISING_PRICE_UNBOUNDED_2026-08-25`):
it was optimising a one-sided objective CORRECTLY. A ceiling repair makes cap
pricing unreachable; a household-side term makes it unattractive.

WHAT THIS MEASURES, AND THE ONE THING IT DOES NOT
--------------------------------------------------
It measures the **SHARE**, and the module is named for that rather than for what
the mission asks, because the two are not the same and conflating them would be
the whole error over again.

    counterfactual_gbp   what this household would have paid on the published
                         default tariff over the same settled rows, at its own
                         metered volumes
    paid_gbp             what it actually paid us (settled revenue)
    household_saving_gbp counterfactual - paid   <- the HOUSEHOLD's share
    our_margin_gbp       what we kept on it      <- OUR share

**VALUE CREATED IS NOT household_saving + our_margin, and this module does not
claim it.** Creation is a comparison of COSTS, not prices: a supplier whose cost
stack equals the incumbent's and prices below it has TRANSFERRED margin to the
household, not created anything. Total value created is (their cost - our cost)
× volume, and the counterfactual supplier's cost is not observable to us — the
regulated pass-throughs are common, and what differs is trading skill,
cost-to-serve and bad debt, none of which a rival publishes. So the honest
report is the split of a surplus whose SIZE we cannot yet measure. That is the
L3 half of `A47`, and `A48_enterprise_value_is_the_method_not_the_book` is where
it goes.

Saying it plainly: **charging a household the cap shows household_saving = 0
here.** Not a small number — zero, exactly, by construction. That is the
director's sentence made arithmetic, and `test_pricing_at_the_counterfactual_
shares_nothing` pins it.

EPISTEMIC POSITION — this is a COMPANY figure and it is honestly one
--------------------------------------------------------------------
Every input is an observable a real UK supplier has: its own settled records,
and the published default tariff. It is the "you saved £X against the price cap"
line that appears on real bills, computed the way a supplier would compute it.
Nothing here reads the world's counterfactual, because there isn't one — the
household's actual alternative is unknowable to us, and the published default
tariff is the standard, defensible stand-in the whole industry quotes against.

The SVT lookup is INJECTED (`svt_rate_for_date`), never imported, for the same
reason `simulation/competitor_reference.py` takes its wholesale price through
the signature: this module must not import `simulation/`, and a caller supplying
the rate is what keeps that true by construction rather than by discipline.

R12 — A DIAGNOSTIC, AND THE RELEASE IS NAMED
---------------------------------------------
Nothing may optimise this figure yet, and `tests/company/test_household_share_is_not_yet_a_target.py`
holds that as a reachability property (the shape `test_carbon_not_a_target.py`
uses). The reason is not that household saving is an illegitimate target — it is
half of the objective the mission describes — but that wiring it into a decision
surface CHANGES COMPANY BEHAVIOUR, and under R13 a difficulty change is the
director's, named and versioned, never the agent's. **What releases the guard:**
a director decision on the two-sided objective, at which point the declaration
register in that test gains its first entry with a written reason. A guard whose
release triggers nothing is a defect; this one's release is a named decision.

ONE RATE PER COMMODITY, AND THAT IS NOT A DETAIL
-------------------------------------------------
The settled book is DUAL FUEL: `simulation/gas_settlement.py` writes gas rows
into the same record list as electricity, tagged by a `commodity` field. The
first draft of this module took a single `svt_rate_for_date(d)` and would have
valued a household's **gas** volumes at the **electricity** default tariff — off
by roughly four times, silently, in the direction that flatters us on any book
with gas. Caught by reading what `all_records` actually contains before running
it, not by reading the output.

So the injected lookup is `svt_rate_for(date, commodity)` and a commodity with no
published reference returns None, which excludes those rows from BOTH sides and
counts them. A caller that knows only one fuel is expected to return None for the
other rather than a plausible substitute.

BASIS, R14
-----------
`our_gross_margin_gbp` is settled revenue less wholesale, straight off the
records. `our_net_margin_gbp` is the records' own `net_margin_gbp` — after policy
levies, network charges, capital and bad debt — and it is None unless EVERY
comparable row carries one. Never a partial sum wearing the whole figure's name,
and never the gross line silently standing in for the net: that substitution is
the defect
`WORKER_FINDING_THE_BOOK_IS_VALUED_ON_A_MARGIN_THAT_EXCLUDES_THREE_QUARTERS_OF_THE_COST_STACK`
recorded against `saas/cost_to_serve.py` on 2026-08-17, where a contribution
margin wearing a net margin's name valued the entire customer book.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from typing import Callable, Iterable, Mapping

#: The share fields are ratios of pounds and are meaningless when the surplus
#: they divide is zero or negative. Callers get None rather than a divide-by-zero
#: guard's quiet 0.0, because "the household kept none of it" and "there was
#: nothing to keep" are different statements and only one of them is a warning.
_SHARE_UNDEFINED = None


@dataclass(frozen=True)
class HouseholdValueShare:
    """One customer-PERIOD of the two-sided ledger, in pounds.

    The period is whatever the caller grouped by — a calendar year by default, a
    priced term where the caller supplied `period_of`. See the `period` field.

    EVERY POUND FIGURE HERE IS OVER THE COMPARABLE ROWS ONLY — the settled rows
    whose date and fuel had a published counterfactual rate. Rows, not settlement
    periods: `simulation/settlement_daily.fold_to_days` collapses a term's
    half-hours to one row per (customer, commodity, day) before they reach any
    consumer, so a field named for periods here would be counting days. That is not a
    detail, it is the difference between a figure and a wrong one, and it was
    caught by printing the table before writing a test: the first draft summed
    what a household PAID over its whole year and what it WOULD have paid over
    only the covered part, so any year straddling the cap's 2019 start reported
    a saving that was really a coverage gap. A supplier trading from 2016 has
    three and a half such years. `excluded_consumption_mwh` carries what was
    left out, so a caller can see the coverage rather than infer it.
    """

    customer_id: str
    #: THE GROUPING LABEL, NOT NECESSARILY A YEAR (generalised 2026-08-28, atom
    #: `A48`). The default grouping is still the calendar year and every caller
    #: that predates `A48` gets an `int` here unchanged. But a PRICING DECISION
    #: covers a TERM -- 365 days from an arbitrary start -- so for most accounts a
    #: term straddles two calendar years and a customer-year mixes the tail of one
    #: priced decision with the head of the next. Attributing a year's joint value
    #: to one decision would be wrong in a way invisible in the output, which is
    #: why the caller supplies the key rather than this module assuming one.
    period: object
    consumption_mwh: float
    paid_gbp: float
    counterfactual_gbp: float
    #: None — never 0.0 — when no period in this customer-year had a published
    #: counterfactual. "They saved nothing" and "we cannot say" are different
    #: statements and a zero would collapse them (the FAIL-OPEN killer, R15).
    household_saving_gbp: float | None
    our_gross_margin_gbp: float
    our_net_margin_gbp: float | None
    #: Settled rows (customer x commodity x day) whose date and fuel had no
    #: published counterfactual rate, and the volume they carried. Non-zero means
    #: the figures above cover LESS than the customer's year — stated, never
    #: silently absorbed.
    settled_rows_without_a_counterfactual: int = 0
    excluded_consumption_mwh: float = 0.0

    @property
    def coverage_pct(self) -> float | None:
        """Share of this customer-year's volume the comparison actually covers."""
        total = self.consumption_mwh + self.excluded_consumption_mwh
        if total <= 0:
            return _SHARE_UNDEFINED
        return 100.0 * self.consumption_mwh / total

    @property
    def household_saving_pct_of_counterfactual(self) -> float | None:
        if self.household_saving_gbp is None or self.counterfactual_gbp <= 0:
            return _SHARE_UNDEFINED
        return 100.0 * self.household_saving_gbp / self.counterfactual_gbp

    @property
    def household_share_of_the_split_pct(self) -> float | None:
        """The household's share of (household saving + our gross margin).

        NOT its share of value CREATED — see the module docstring. This is how a
        measurable surplus was divided, not evidence that the surplus was made.
        """
        if self.household_saving_gbp is None:
            return _SHARE_UNDEFINED
        split = self.household_saving_gbp + self.our_gross_margin_gbp
        if split <= 0:
            return _SHARE_UNDEFINED
        return 100.0 * self.household_saving_gbp / split


@dataclass(frozen=True)
class HouseholdValueShareView:
    """The book's two-sided ledger, per customer-period and in total."""

    by_customer_period: dict[tuple[str, object], HouseholdValueShare]
    portfolio: HouseholdValueShare
    #: Customer-periods the caller's records covered but no counterfactual rate
    #: reached at all. A population floor for this control: an empty book and a
    #: book whose rates all went missing produce the same zeros otherwise.
    groups_without_any_counterfactual: list[tuple[str, object]] = field(
        default_factory=list)
    #: Rows the caller supplied that carry no settlement date, customer, volume or
    #: revenue -- skipped rather than reached into, counted rather than dropped.
    #: Non-zero is not necessarily wrong (a settled book legitimately carries
    #: non-settlement rows); it being INVISIBLE would be.
    records_this_view_could_not_value: int = 0

    @property
    def groups(self) -> int:
        """How many customer-periods this view holds — customer-YEARS under the
        default grouping, customer-TERMS where the caller supplied one."""
        return len(self.by_customer_period)


#: The fields a record must carry to be valued at all. Named as a constant so the
#: skip and the reason for it are one thing rather than a condition that drifts.
_REQUIRED_FIELDS = ("customer_id", "settlement_date", "consumption_kwh",
                    "revenue_gbp", "margin_gbp")


def _valuable(record) -> bool:
    """True if this row carries everything the two-sided ledger needs."""
    return all(record.get(f) is not None for f in _REQUIRED_FIELDS)


def _calendar_year(record: Mapping) -> int:
    """The DEFAULT grouping: the calendar year of the settlement date.

    A record-level callable rather than a date-level one so a caller's own
    grouping (a priced term, say) can key on the customer as well as the date —
    terms start on different days for different accounts, so a date alone cannot
    name one.
    """
    return int(record["settlement_date"][:4])


def build_household_value_share(
    settlement_records: Iterable[Mapping],
    *,
    svt_rate_for: Callable[[date, str], float | None],
    period_of: Callable[[Mapping], object] = _calendar_year,
) -> HouseholdValueShareView:
    """The household's side of the score, from settled records and published rates.

    `settlement_records` are the supplier's own settled half-hours — the shape
    `simulation/settlement.py` produces and `company/analytics/customer_value_view.py`
    already consumes: {customer_id, settlement_date, consumption_kwh,
    revenue_gbp, wholesale_cost_gbp, margin_gbp}.

    `svt_rate_for(date, commodity)` returns the published default-tariff unit
    rate in £/MWh for that date AND that fuel, or None where none was published.
    Injected, never imported — see the module docstring. Rows with no published
    rate are COUNTED and EXCLUDED, never valued at zero: a missing counterfactual
    makes the saving look larger, which is the direction a fail-open would
    flatter us in.

    `period_of(record)` names the group a record belongs to, and defaults to its
    calendar year — which is what every caller before `A48` got and still gets.
    A caller scoring PRICING DECISIONS supplies the priced term instead, because
    a term straddles two calendar years for most accounts and a customer-year
    therefore mixes two decisions. A record the caller's own key function cannot
    place returns None from it and is EXCLUDED and COUNTED, on the same reasoning
    as a missing rate: silently folding an unplaceable row into some default group
    would put one decision's pounds against another decision's signal.
    """
    rows: dict[tuple[str, object], dict] = {}
    rate_cache: dict[tuple[str, str], float | None] = {}
    unshaped = 0

    for record in settlement_records:
        # NOT EVERY ROW IN A SETTLED BOOK IS A SETTLED HALF-HOUR.
        # `simulation/settlement_daily.fold_to_days` passes any record WITHOUT a
        # `settlement_date` through untouched -- "this function's job is to make
        # the book smaller, not to decide what counts as settled" -- so a live
        # `all_records` carries rows this view cannot value. Reaching into them
        # would raise mid-run; skipping them silently would shrink the book
        # without saying so. They are skipped AND COUNTED, and the count is
        # published on the view so a caller sees the population it did not get.
        if not _valuable(record):
            unshaped += 1
            continue
        customer_id = record["customer_id"]
        settlement_date = record["settlement_date"]
        period = period_of(record)
        if period is None:
            # THE CALLER COULD NOT PLACE THIS ROW IN A GROUP. Counted with the
            # rows this view could not value rather than dropped, because a
            # decision-scored caller's coverage is exactly the question its
            # reader has to be able to ask.
            unshaped += 1
            continue
        key = (customer_id, period)
        row = rows.setdefault(key, {
            "consumption_mwh": 0.0,
            "paid_gbp": 0.0,
            "counterfactual_gbp": 0.0,
            "gross_margin_gbp": 0.0,
            "net_margin_gbp": 0.0,
            "rows_without_a_net_margin": 0,
            "comparable": 0,
            "missing": 0,
            "excluded_mwh": 0.0,
        })

        consumption_mwh = float(record["consumption_kwh"]) / 1000.0
        # DEFAULTS TO ELECTRICITY ONLY WHEN THE FIELD IS ABSENT ENTIRELY. A record
        # carrying `commodity: None` is a record whose fuel is unknown, and guessing
        # it is how gas volumes get priced at the electricity tariff.
        commodity = record["commodity"] if "commodity" in record else "electricity"

        cache_key = (settlement_date, commodity)
        if cache_key not in rate_cache:
            rate_cache[cache_key] = svt_rate_for(
                date.fromisoformat(settlement_date), commodity)
        rate = rate_cache[cache_key]
        if rate is None:
            # EXCLUDED FROM BOTH SIDES, not just from the counterfactual. Adding
            # this record's revenue while omitting its counterfactual is what
            # made the first draft's saving a coverage gap wearing a figure's
            # name.
            row["missing"] += 1
            row["excluded_mwh"] += consumption_mwh
            continue

        row["comparable"] += 1
        row["consumption_mwh"] += consumption_mwh
        row["paid_gbp"] += float(record["revenue_gbp"])
        row["gross_margin_gbp"] += float(record["margin_gbp"])
        row["counterfactual_gbp"] += consumption_mwh * float(rate)
        net = record.get("net_margin_gbp")
        if net is None:
            row["rows_without_a_net_margin"] += 1
        else:
            row["net_margin_gbp"] += float(net)

    by_customer_period: dict[tuple[str, object], HouseholdValueShare] = {}
    blind: list[tuple[str, object]] = []
    for (customer_id, period), row in rows.items():
        if not row["comparable"]:
            blind.append((customer_id, period))
        by_customer_period[(customer_id, period)] = HouseholdValueShare(
            customer_id=customer_id,
            period=period,
            consumption_mwh=row["consumption_mwh"],
            paid_gbp=row["paid_gbp"],
            counterfactual_gbp=row["counterfactual_gbp"],
            household_saving_gbp=(
                None if not row["comparable"]
                else row["counterfactual_gbp"] - row["paid_gbp"]),
            our_gross_margin_gbp=row["gross_margin_gbp"],
            # None unless EVERY comparable row carried one -- a partial sum would
            # be a smaller net margin wearing the whole year's name.
            our_net_margin_gbp=(
                None if row["rows_without_a_net_margin"] or not row["comparable"]
                else row["net_margin_gbp"]),
            settled_rows_without_a_counterfactual=row["missing"],
            excluded_consumption_mwh=row["excluded_mwh"],
        )

    return HouseholdValueShareView(
        by_customer_period=by_customer_period,
        portfolio=_portfolio(by_customer_period),
        # `sorted` on a MIXED key set raises, and a caller's period labels are
        # its own -- so sort by the printable form rather than assuming the
        # labels are mutually comparable. Deterministic order, no type contract.
        groups_without_any_counterfactual=sorted(blind, key=repr),
        records_this_view_could_not_value=unshaped,
    )


def _portfolio(
    rows: Mapping[tuple[str, object], HouseholdValueShare],
) -> HouseholdValueShare:
    """The book total. `customer_id` is the sentinel `__portfolio__` and `period`
    is 0 — deliberately not a real id and not a real period, so a portfolio row
    that leaks into a per-customer table is obvious rather than plausible."""
    # None if ANY customer-year could not supply one -- the book's net margin is
    # not the sum of the rows that happened to carry the field.
    nets = [r.our_net_margin_gbp for r in rows.values()]
    net = sum(nets) if nets and all(n is not None for n in nets) else None
    savings = [r.household_saving_gbp for r in rows.values()
               if r.household_saving_gbp is not None]
    return HouseholdValueShare(
        customer_id="__portfolio__",
        period=0,
        consumption_mwh=sum(r.consumption_mwh for r in rows.values()),
        paid_gbp=sum(r.paid_gbp for r in rows.values()),
        counterfactual_gbp=sum(r.counterfactual_gbp for r in rows.values()),
        # None when NO customer-period was comparable — an empty book and a book
        # whose counterfactual never resolved must not both report £0 saved.
        household_saving_gbp=sum(savings) if savings else None,
        our_gross_margin_gbp=sum(r.our_gross_margin_gbp for r in rows.values()),
        our_net_margin_gbp=net,
        settled_rows_without_a_counterfactual=sum(
            r.settled_rows_without_a_counterfactual for r in rows.values()),
        excluded_consumption_mwh=sum(
            r.excluded_consumption_mwh for r in rows.values()),
    )
