"""THE £130 IS MULTIPLIED BY ONE NAMED POPULATION, AND THE FIGURE CARRIES ITS NAME.

The defect these controls exist against, 2026-08-29. `docs/reports/run_output_latest.json`
published `by_billing_account` with 13 entries and `enterprise_value_account_count` = 113 in the
same file from the same run; the arms artefact said 210 settled and 128 at the end; the growth page
said 172 on the book and 587 accounts held. Five populations, no statement anywhere of what each
one counts — an instance of this project's own rule, "before dividing two numbers, say out loud
what each one counts", broken under a published solvency claim.

Underneath it the collateral desk was multiplying £130 by a SIXTH number that is none of the five:
`len(_ALL_KNOWN_CUSTOMERS)` = 24, the per-COMMODITY legs of the static founder roster, bound at
import. Wrong three ways at once — dual-fuel households counted twice against a per-ACCOUNT
obligation, not one funnel win visible, no domestic/non-domestic split — and it published a free
equity figure overstated by £12,480.

WHAT EACH CONTROL BELOW IS KEYED TO, because a control keyed to today's answer goes red when the
code becomes more honest:

  * the SELECTION, leg by leg, each mutated by performing the specific defect (count legs; keep
    ceased; keep non-domestic). Not "the answer is 120".
  * the WIRING — the desk must overwrite a caller-supplied count, because a census the run does
    not reach is the R1 defect wearing different clothes.
  * the NULL control — omit either half of the census input and the caller's own number must
    stand, unchanged. Without this, "the desk counts for you" is satisfiable by a desk that
    ignores its inputs and always counts.
  * the RECONCILIATION — the published `free_equity_gbp` and the published `accounts_held` must
    satisfy `free = net_assets - accounts x £130` with each other. This is the one that survives a
    rewrite: it goes red whenever either side of the subtraction is restated independently of the
    other, which is the whole class of defect, not this instance of it.
"""

from __future__ import annotations

from datetime import date, timedelta

from company.pricing.tariff_engine import CompanyTariffEngine
from company.risk import counterparty_collateral_desk as impl
from company.trading.forward_book import (
    ForwardContract,
    TradingBook,
    assign_default_counterparty,
)
from saas.capital.solvency import (
    MCR_DOMESTIC_SEGMENTS,
    MCR_FLOOR_GBP_PER_CUSTOMER,
    mcr_accounts_on_supply,
)

MARK_DATE = "2023-06-30"


# ---------------------------------------------------------------------------
# The census fixture. Five accounts, each present to make ONE leg of the
# selection able to fail — asserted below rather than asserted about.
# ---------------------------------------------------------------------------

#: (customer_id, segment, last settlement date). `_billing_account_id` collapses a trailing "g",
#: so DUAL/DUALg are ONE billing account: the fixture cannot be satisfied by counting legs.
_BOOK = [
    ("DUAL", "resi", "2023-06-30"),      # dual-fuel domestic, on supply
    ("DUALg", "resi", "2023-06-30"),     # ...its gas leg. Same account, same £130.
    ("SOLO", "resi", "2023-06-30"),      # single-fuel domestic, on supply
    ("BIZ", "SME", "2023-06-30"),        # non-domestic, on supply -> no MCR
    ("GONE", "resi", "2022-01-01"),      # domestic, quiet for 18 months -> ceased
]

#: The answer the fixture is built to produce: DUAL(+g) and SOLO. Written out as the accounts
#: rather than as the integer 2, so a reader can see WHICH accounts the number is.
_EXPECTED_MCR_ACCOUNTS = {"DUAL", "SOLO"}


def _settled_records() -> list[dict]:
    """One record per account per month up to its last settlement date."""
    records = []
    for cid, _seg, last in _BOOK:
        day = date(2021, 1, 1)
        stop = date.fromisoformat(last)
        while day <= stop:
            records.append({"customer_id": cid, "settlement_date": day.isoformat()})
            day += timedelta(days=28)
    return records


def _segment_by_cid() -> dict[str, str]:
    return {cid: seg for cid, seg, _ in _BOOK}


def test_the_fixture_can_see_each_leg_of_the_selection_fail():
    """Vacuity guard. A balanced fixture cannot see a weighting choice, and a fixture with no
    dual-fuel pair / no ceased account / no non-domestic account cannot see the leg that drops
    it. Each of the three must be PRESENT and must MOVE the answer.
    """
    census = mcr_accounts_on_supply(_settled_records(), _segment_by_cid(), as_of=MARK_DATE)
    assert census["settled_accounts_ever"] == 4, (
        "the fixture's five customer ids must collapse to four billing accounts — "
        "with no dual-fuel pair, the leg-collapsing leg of the selection is untested"
    )
    assert census["ceased_accounts"] == 1, "no ceased account: the cessation leg is untested"
    assert census["non_domestic_on_supply"] == 1, (
        "no non-domestic account on supply: the domestic leg is untested"
    )
    assert census["count"] == len(_EXPECTED_MCR_ACCOUNTS)


# ---------------------------------------------------------------------------
# The selection, leg by leg. Each mutation PERFORMS the defect.
# ---------------------------------------------------------------------------


def test_a_dual_fuel_household_is_one_account_and_owes_one_mcr():
    """DEFECT: counting per-commodity legs. That is what the live run did — 24 legs off an
    18-record roster of 13 households — and it doubles the obligation of every dual-fuel
    customer against a requirement that is levied per ACCOUNT.

    UNCONFOUNDED ON PURPOSE. The obvious form of this — "the count is lower than the number of
    live legs" — is also satisfied by the domestic and cessation legs on their own, so it passes
    on a census that never collapses anything. The property is instead measured directly: adding
    a GAS LEG to an account already counted must not change the count, and adding a whole new
    account must.
    """
    base = mcr_accounts_on_supply(_settled_records(), _segment_by_cid(), as_of=MARK_DATE)
    a_second_leg = _settled_records() + [
        {"customer_id": "SOLOg", "settlement_date": MARK_DATE},
    ]
    a_new_account = _settled_records() + [
        {"customer_id": "OTHER", "settlement_date": MARK_DATE},
    ]
    with_leg = mcr_accounts_on_supply(
        a_second_leg, {**_segment_by_cid(), "SOLOg": "resi"}, as_of=MARK_DATE
    )
    with_account = mcr_accounts_on_supply(
        a_new_account, {**_segment_by_cid(), "OTHER": "resi"}, as_of=MARK_DATE
    )
    assert with_leg["count"] == base["count"], (
        f"giving SOLO a gas leg took the count from {base['count']} to {with_leg['count']} — "
        "this is a count of meters, and every dual-fuel household is charged twice"
    )
    assert with_account["count"] == base["count"] + 1, (
        "a genuinely new account did not raise the count — the collapse is over-eager and is "
        "now merging distinct customers"
    )


def test_an_account_that_has_gone_obliges_no_capital():
    """DEFECT: counting the whole settled history. GONE last settled 18 months before the mark;
    a supplier does not hold £130 against a customer it no longer supplies. Mutation: read the
    census with a continuity window wide enough to keep GONE, and the count must rise.
    """
    census = mcr_accounts_on_supply(_settled_records(), _segment_by_cid(), as_of=MARK_DATE)
    assert "GONE" not in _EXPECTED_MCR_ACCOUNTS
    assert census["count"] == census["settled_accounts_ever"] - census["ceased_accounts"] - census[
        "non_domestic_on_supply"
    ], "the reported parts do not add up to the reported whole"
    # The same records read as at the day GONE last settled: it is on supply there, so the
    # count must be HIGHER. A census blind to the as-of date returns the same number twice.
    earlier = mcr_accounts_on_supply(_settled_records(), _segment_by_cid(), as_of="2022-01-05")
    assert earlier["count"] > census["count"], (
        "the census did not move when read at a date GONE was still supplied — it is not "
        "reading cessation at all"
    )


def test_a_non_domestic_account_owes_no_mcr_and_is_counted_not_dropped():
    """DEFECT (two of them). Ofgem's per-account capital regime is a DOMESTIC obligation, so an
    SME account on the same book carries no £130. And an exclusion that cannot be counted hides
    what it removed — `non_domestic_on_supply` is the count, published rather than implied.
    """
    census = mcr_accounts_on_supply(_settled_records(), _segment_by_cid(), as_of=MARK_DATE)
    assert "SME" not in MCR_DOMESTIC_SEGMENTS
    assert census["non_domestic_on_supply"] == 1
    all_domestic = mcr_accounts_on_supply(
        _settled_records(), {cid: "resi" for cid, _s, _l in _BOOK}, as_of=MARK_DATE
    )
    assert all_domestic["count"] == census["count"] + 1, (
        "relabelling the SME account domestic did not change the count — the segment leg of "
        "the selection is not being applied"
    )


def test_an_unclassified_account_is_domestic_because_the_default_must_cost_us():
    """A fail-open default here waives an obligation on a labelling failure of ours. The
    conservative direction is to charge the £130 and be wrong expensively.
    """
    unlabelled = mcr_accounts_on_supply(_settled_records(), {}, as_of=MARK_DATE)
    labelled = mcr_accounts_on_supply(_settled_records(), _segment_by_cid(), as_of=MARK_DATE)
    assert unlabelled["count"] > labelled["count"], (
        "an account with no segment label fell OUT of the obligation — the default waives "
        "capital on our own missing data"
    )


def test_the_census_names_its_own_population():
    """A number without its selection is what the five published counts already were."""
    census = mcr_accounts_on_supply(_settled_records(), _segment_by_cid(), as_of=MARK_DATE)
    assert MARK_DATE in census["population"], census["population"]
    for leg in ("billing accounts", "ceased", "resi"):
        assert leg in census["selection"], (
            f"the published selection does not mention '{leg}', so a reader cannot tell "
            f"whether that leg was applied: {census['selection']}"
        )


# ---------------------------------------------------------------------------
# The wiring, the null control, and the reconciliation.
# ---------------------------------------------------------------------------


def _spot_records(level: float) -> list[dict]:
    records = []
    day = date(2020, 1, 1)
    while day <= date.fromisoformat(MARK_DATE):
        records.append({
            "settlementDate": day.isoformat(),
            "systemSellPrice": level + (day.month % 5) * 1.5 + day.day * 0.1,
        })
        day += timedelta(days=1)
    return records


def _book() -> TradingBook:
    """One deeply out-of-the-money contract: enough to mark, and enough to form an exposure
    for free equity to be compared against.
    """
    book = TradingBook()
    cp = assign_default_counterparty("OTM-ELEC-2", "2021-01-01", 900.0)
    book.open_hedge(
        ForwardContract(
            customer_id="OTM-ELEC-2",
            term_start="2021-01-01",
            term_end="2023-12-31",
            agreed_price_gbp_per_mwh=260.0,
            notional_mwh=900.0,
            hedge_fraction=0.85,
            counterparty_id=cp.counterparty_id,
            counterparty_type=cp.counterparty_type,
            clearing_status=cp.clearing_status,
            counterparty_rating=cp.counterparty_rating,
            broker_arranged=cp.broker_arranged,
        )
    )
    return book


_NET_ASSETS = 400_000.0
#: A number the census can never produce, so "the desk overwrote it" is unambiguous.
_A_COUNT_NOBODY_COUNTED = 9_999


def _build(**kwargs):
    return impl.build_counterparty_collateral(
        _book(),
        commodity_by_customer_id={"OTM-ELEC-2": "electricity"},
        elec_spot_records=_spot_records(95.0),
        gas_spot_records=_spot_records(28.0),
        mark_date=MARK_DATE,
        **kwargs,
    )


def test_the_fixture_marks_and_forms_an_exposure():
    """Vacuity guard: with no marked exposure the free-equity arithmetic below short-circuits
    on `no_exposure` and every control after it passes on nothing.
    """
    engine = CompanyTariffEngine()
    assert engine.get_forward_price("electricity", MARK_DATE, _spot_records(95.0)) > 0
    built = _build(balance_sheet={"net_assets_gbp": _NET_ASSETS})
    assert built.credit_feed_error is None, built.credit_feed_error
    assert built.margin_call_summary is not None
    assert built.margin_call_summary["gross_marked_exposure_gbp"] > 0, (
        "the fixture book is unmarked — the free-equity comparison is vacuous"
    )


def test_the_desk_counts_the_accounts_rather_than_believing_the_caller():
    """THE WIRING ASSERTION. A census the run does not reach is the R1 defect in new clothes —
    and the specific way this went wrong was a count handed in by a caller that had no business
    computing it. Given the records and the register, the desk's own count must WIN.
    """
    built = _build(
        balance_sheet={
            "net_assets_gbp": _NET_ASSETS,
            "accounts_held": _A_COUNT_NOBODY_COUNTED,
        },
        settled_records=_settled_records(),
        segment_by_customer_id=_segment_by_cid(),
    )
    summary = built.margin_call_summary
    assert summary["accounts_held"] == len(_EXPECTED_MCR_ACCOUNTS), (
        f"the desk published {summary['accounts_held']} — the caller's "
        f"{_A_COUNT_NOBODY_COUNTED} was not overwritten, so the census is unwired"
    )
    assert MARK_DATE in summary["accounts_population"]


def test_without_both_halves_of_the_census_the_callers_number_stands():
    """THE NULL CONTROL. Without it, "the desk counts for you" is equally satisfied by a desk
    that ignores its inputs and always counts — which would silently overwrite every existing
    caller. Each of the two omissions is tested separately: a segment map with no records
    cannot count anything, and records with no segment map would read every non-domestic
    account as domestic.
    """
    for kwargs in (
        {},
        {"settled_records": _settled_records()},
        {"segment_by_customer_id": _segment_by_cid()},
    ):
        built = _build(
            balance_sheet={
                "net_assets_gbp": _NET_ASSETS,
                "accounts_held": _A_COUNT_NOBODY_COUNTED,
            },
            **kwargs,
        )
        assert built.margin_call_summary["accounts_held"] == _A_COUNT_NOBODY_COUNTED, (
            f"the desk recounted on a partial census input ({sorted(kwargs)}) and overwrote "
            "the caller's number — the 'both or neither' contract is not held"
        )


def test_a_caller_that_does_not_name_its_population_is_published_as_unnamed():
    """A wrong name is worse than no name: it sends the next reader to the wrong roster. So the
    default label must be one nobody can mistake for a selection.
    """
    built = _build(balance_sheet={"net_assets_gbp": _NET_ASSETS, "accounts_held": 7})
    assert "unnamed" in built.margin_call_summary["accounts_population"]
    assert built.margin_call_summary["accounts_selection"] is None


def test_the_published_free_equity_reconciles_with_the_published_account_count():
    """THE CONTROL THAT OUTLIVES THIS REPAIR. Free equity is `net_assets - accounts x £130`.
    Publishing the difference and the subtrahend separately is exactly how the two came to
    describe different suppliers, so the two published fields must satisfy the identity that
    produced them. This goes red whenever either side is restated independently of the other —
    which is the class, not this instance.
    """
    built = _build(
        balance_sheet={"net_assets_gbp": _NET_ASSETS},
        settled_records=_settled_records(),
        segment_by_customer_id=_segment_by_cid(),
    )
    summary = built.margin_call_summary
    expected = _NET_ASSETS - summary["accounts_held"] * MCR_FLOOR_GBP_PER_CUSTOMER
    assert abs(summary["free_equity_gbp"] - expected) < 0.01, (
        f"published free equity £{summary['free_equity_gbp']:,.2f} does not reconcile with the "
        f"published count of {summary['accounts_held']} accounts at "
        f"£{MCR_FLOOR_GBP_PER_CUSTOMER}/account (£{expected:,.2f}) — the figure and its basis "
        "are describing different books"
    )


def test_the_count_moves_the_free_equity_it_is_netted_against():
    """A count published beside a figure it does not actually enter is a caption, not a basis.
    Adding one domestic account on supply must move free equity by exactly one £130.
    """
    extra = _settled_records() + [
        {"customer_id": "NEW", "settlement_date": MARK_DATE},
    ]
    base = _build(
        balance_sheet={"net_assets_gbp": _NET_ASSETS},
        settled_records=_settled_records(),
        segment_by_customer_id=_segment_by_cid(),
    ).margin_call_summary
    grown = _build(
        balance_sheet={"net_assets_gbp": _NET_ASSETS},
        settled_records=extra,
        segment_by_customer_id={**_segment_by_cid(), "NEW": "resi"},
    ).margin_call_summary
    assert grown["accounts_held"] == base["accounts_held"] + 1
    assert abs(
        (base["free_equity_gbp"] - grown["free_equity_gbp"]) - MCR_FLOOR_GBP_PER_CUSTOMER
    ) < 0.01, (
        "winning one domestic account did not cost exactly one MCR of free equity — the "
        "published count is not the one the arithmetic used"
    )
