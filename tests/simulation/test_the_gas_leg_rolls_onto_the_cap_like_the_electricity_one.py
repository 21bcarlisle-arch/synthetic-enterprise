"""Repair 2 of the tariff-type determination: the gas leg rolls, and it rolls on the GAS cap.

THE DEFECT THIS FILE EXISTS FOR, AND WHY IT IS TWO DEFECTS AND NOT ONE.

`resolved_tariff_type`'s gas branch spelled the read `record.get("tariff_type", "fixed")` while
the electricity one spelled it `or "fixed"`, and a drawn record carries the key PRESENT and
`None` -- so 158 gas terms settled labelled `None` and the value arm refused them at the product
gate (`docs/staging/done/SEAT_RESULT_THE_LAST_158_REFUSED_RENEWALS_ARE_EIGHTEEN_GAS_ONLY_
ACCOUNTS_THAT_CANNOT_LEAVE_2026-09-16.md`). Repairing that ONE LINE and nothing else would have
produced the blanket-fixed that `DRAWN_BOOK_TARIFF_TYPE_FIDELITY_DETERMINATION.md` refused on
2026-08-28: every gas leg on a fixed deal for its whole tenure, against a published domestic fixed
share of roughly one third. So the line lands with the C1b roll that makes it the OPENING TERM of
a tenure the world then decides, exactly as electricity got on 2026-08-30.

Both halves can rot independently and each rots invisibly:

  * delete the roll and keep the line -> the refused blanket-fixed, and every existing control
    stays green because a schedule full of `fixed` terms is what they were all written against;
  * keep the roll and build its segments off the ELECTRICITY cap -> a gas household billed
    ~250 GBP/MWh where the published gas cap says ~60, which settles, balances, and is wrong by
    about 4x with no field anywhere that disagrees with any other field.

`test_the_gas_book_is_not_all_fixed_which_is_what_the_determination_refused` is the first;
`test_a_gas_segment_is_billed_off_the_published_GAS_cap_and_not_the_electricity_one` is the
second. Neither is implied by the other.

WHAT IS DELIBERATELY NOT ASSERTED HERE. No year's fixed/SVT share is pinned. The published split
is a CHECK on the output and never an input (`simulation/svt_product.py` states that rule and
`tools/svt_generated_share_check.py` runs it); a control asserting "2019 is 41% fixed" would be
keyed to today's answer, and would go red the day the world got more honest. What IS asserted is
that both answers of the roll are ATTAINED on the live roster -- the partition, not the split.

R15 MUTATIONS, applied to a COPY of the world file and the observed result recorded rather than
the intended one (never the live tree: a control proven by editing a file a concurrent run has
open is proven against a race):

  * `_build_gas_renewal_schedule`'s C1b block deleted entirely -> **6 red** (predicted 3):
    `..._gas_book_is_not_all_fixed...`, `..._both_answers_of_the_gas_roll_are_attained...`,
    `..._a_gas_svt_stint_is_bounded_by_the_anniversary_and_not_absorbing`,
    `..._gas_roll_asks_about_the_household_and_not_the_supply_point`,
    `..._billed_off_the_published_GAS_cap_and_not_the_electricity_one` and
    `..._neither_schedule_builder_mints_its_own_coin`. The three I missed all fail for lack of a
    SUBJECT rather than on the property -- with no `svt` term anywhere, the rate control and the
    replay control have nothing to look at. Recorded as observed: a control that reds because its
    population emptied is weaker evidence than one that reds on the claim, and the distinction is
    the reader's to make, not mine to smooth over.
  * the C1b block kept but `fuel="gas"` changed to `fuel="electricity"`
    -> **1 red**, `..._billed_off_the_published_GAS_cap_and_not_the_electricity_one`
    (`140.0` billed where the published gas cap says `40.0` on 2016-12-31). Nothing else moves --
    every structural control still sees `svt` segments in the schedule, which is precisely why
    the rate leg is asserted separately from the assignment leg.
  * `build_svt_schedule`'s `fuel` given a default of `"electricity"`
    -> **1 red**, `..._build_svt_schedule_refuses_to_guess_a_fuel` ("DID NOT RAISE TypeError").
  * the roll reseeded on `customer["customer_id"]` instead of `household_of(...)`
    -> **1 red**, `..._gas_roll_asks_about_the_household_and_not_the_supply_point` (the gas leg
    is registered as `<point>g`, so the two draw different archetypes for one family).
  * `resolved_tariff_type` reverted to the pre-repair commodity split -> **1 red** here (predicted
    2), `..._opening_term_is_fixed_on_both_fuels`, at `{None, 'fixed'}`. THE ONE I PREDICTED AND
    DID NOT GET IS THE INSTRUCTIVE ONE: `..._gas_book_is_not_all_fixed...` stayed GREEN, because
    the four founder gas legs (`C1g`..`C4g`) carry no `tariff_type` KEY at all, so the defeated
    spelling reaches its default on them, they roll, and `svt` is still in the book. A control
    over a whole-book label set cannot see a defect that spares four accounts. That is why the
    opening-term control is asserted per leg and not over the union. The same mutation also reds
    `test_the_two_commodities_are_now_read_the_same_way_on_purpose` in
    `test_the_tariff_type_read_has_one_home.py`, which is the read's own file.
"""
from __future__ import annotations

import ast
import pathlib

import pytest

from simulation.household import household_of
from simulation.run_phase2b import (
    REPORT_END,
    _build_gas_renewal_schedule,
    resolved_tariff_type,
)
from simulation.settlement import CONTRACT_LENGTH_DAYS
from simulation.svt_product import SVT_TARIFF_TYPE, build_svt_schedule
from simulation.svt_rates import (
    get_svt_elec_rate_gbp_per_mwh,
    get_svt_gas_rate_gbp_per_mwh,
)

_REPO = pathlib.Path(__file__).resolve().parents[2]
_WORLD = _REPO / "simulation" / "run_phase2b.py"

# `REPORT_END` is THE WORLD'S OWN END, imported above rather than written here. It is derived from
# where the NBP series actually stops (2025-06-07 today), and a literal would either fall short of
# the book's decade or ask `generate_forward_price` for a window the feed does not cover -- which
# the gas builder answers by ending the schedule, so the control would measure a truncation
# instead of a roll.


@pytest.fixture(scope="module")
def gas_records():
    """The real NBP series. Skips rather than inventing one: a made-up forward would still
    produce `svt` segments (the cap does not consult it), so a synthetic feed would let every
    assignment control here pass while the PRICING leg measured nothing real."""
    if not (_REPO / "sim" / "gas_data" / "nbp_sap.csv").exists():
        pytest.skip("NBP gas price data not available; these controls need the real feed")
    from sim.gas_prices_history import load_nbp_history

    return load_nbp_history()


@pytest.fixture(scope="module")
def resi_gas_customers():
    from simulation.run_phase2b import GAS_CUSTOMERS

    resi = [c for c in GAS_CUSTOMERS if c.get("segment", "resi") == "resi"]
    if len(resi) < 20:
        pytest.skip(f"only {len(resi)} resi gas legs on the roster; these controls need the book")
    return resi


@pytest.fixture(scope="module")
def book(resi_gas_customers, gas_records):
    """Every resi gas leg's schedule, built exactly as `run_phase2b` builds it.

    THROUGH `resolved_tariff_type`, NOT WITH A LITERAL. The pairing this file is about is
    between that read and the roll; a fixture passing `tariff_type="fixed"` by hand would hold
    the two apart and could not see the read rot.
    """
    return {
        c["customer_id"]: _build_gas_renewal_schedule(
            c, gas_records, report_end=REPORT_END, tariff_type=resolved_tariff_type(c),
        )
        for c in resi_gas_customers
    }


# ---------------------------------------------------------------------------------------------
# THE PAIRING: THE READ RESOLVES, AND THE ROLL IS WHAT STOPS IT BEING A BLANKET
# ---------------------------------------------------------------------------------------------

def test_the_opening_term_is_fixed_on_both_fuels(book):
    """An account arrives by taking a deal, so its first term is a fixed one -- either fuel.

    THE DEFECT: the gas read left at `.get(..., "fixed")`, so a drawn leg's first term is
    labelled `None` and every downstream product gate refuses it. That is the 158.
    """
    firsts = {cid: schedule[0]["tariff_type"] for cid, schedule in book.items() if schedule}
    assert firsts, "no gas schedules built -- this control would pass vacuously"
    assert set(firsts.values()) == {"fixed"}, (
        f"a gas leg does not open on a fixed term: "
        f"{sorted({v for v in firsts.values() if v != 'fixed'})}")


def test_the_gas_book_is_not_all_fixed_which_is_what_the_determination_refused(book):
    """The other half of the pairing, and the one a lone `or \"fixed\"` would break.

    THE DEFECT: the read repaired and the roll absent, so every gas leg is on a fixed deal for
    its whole tenure. `DRAWN_BOOK_TARIFF_TYPE_FIDELITY_DETERMINATION.md` refused exactly that
    against a published domestic fixed share of roughly a third, and no existing control would
    have noticed: a schedule of nothing but `fixed` terms is what all of them were written
    against.

    A COUNT, NOT A SHARE. Pinning the share would key this to today's answer; what is claimed is
    that the refused shape -- a book with no SVT in it at all -- is not what we built.
    """
    labels = {t["tariff_type"] for schedule in book.values() for t in schedule}
    assert SVT_TARIFF_TYPE in labels, (
        "no gas term anywhere in the book is on the standard variable product: the `or \"fixed\"` "
        "read has landed without the roll that makes it an opening term, which is the "
        "blanket-fixed the 2026-08-28 determination refused")
    assert "fixed" in labels, (
        "no gas term anywhere is fixed -- SVT has become absorbing or the roll always rolls "
        "passive, and the published share is a minority in every year but never nothing")


def test_both_answers_of_the_gas_roll_are_attained_on_the_live_roster(book):
    """One control over the whole partition, because a roll that always says the same thing
    passes every per-leg assertion above.

    THE DEFECT: assignment keyed to something that is not engagement -- a constant, the term
    index, an always-true predicate. The book would still contain both labels (every household
    opens fixed), so the control above cannot see it. This one asks whether DIFFERENT HOUSEHOLDS
    got different answers.
    """
    ever_svt = {cid for cid, s in book.items() if any(t["tariff_type"] == SVT_TARIFF_TYPE for t in s)}
    never_svt = set(book) - ever_svt
    assert ever_svt and never_svt, (
        f"the gas roll gave the same answer to every household: {len(ever_svt)} ever reached SVT, "
        f"{len(never_svt)} never did -- one of those is the whole roster")


def test_a_gas_svt_stint_is_bounded_by_the_anniversary_and_not_absorbing(book):
    """A passive stint runs to the household's next anniversary and it can take a deal again.

    THE DEFECT: SVT absorbing on the gas leg. It was the first draft of the electricity
    mechanism and the published split refutes it -- with no route back the fixed share decays to
    nothing, against a share that is a minority in every year of the window and never vanishes.

    Also asserts the BOUNDARY arithmetic, which is the part that is this builder's own and not
    the shared roll's: the segments of one stint span exactly the year from the boundary the roll
    was taken at, so a fixed term resuming later or sooner is a different world.
    """
    from datetime import date, timedelta

    returned = [
        cid for cid, s in book.items()
        if any(a["tariff_type"] == SVT_TARIFF_TYPE and b["tariff_type"] == "fixed"
               for a, b in zip(s, s[1:]))
    ]
    assert returned, (
        "no gas household on the SVT product ever takes a fixed deal again: the product is "
        "absorbing, which the published fixed share refutes")

    for cid in returned:
        schedule = book[cid]
        for i, term in enumerate(schedule):
            if term["tariff_type"] != SVT_TARIFF_TYPE:
                continue
            prior_fixed = next(
                (t for t in reversed(schedule[:i]) if t["tariff_type"] == "fixed"), None)
            if prior_fixed is None:
                continue
            stint_open = date.fromisoformat(
                next(t for t in schedule[:i + 1][::-1]
                     if t["tariff_type"] == SVT_TARIFF_TYPE)["acquisition_date"])
            assert date.fromisoformat(term["acquisition_date"]) < stint_open + timedelta(
                days=CONTRACT_LENGTH_DAYS), (
                f"{cid}: an SVT segment starting {term['acquisition_date']} sits beyond the "
                f"anniversary of the stint that opened {stint_open} -- the stint is not bounded "
                "by the household's own next look at the market")
            break


def test_the_gas_roll_asks_about_the_household_and_not_the_supply_point(book, gas_records,
                                                                       resi_gas_customers):
    """A gas leg is registered `<point>g`; the engagement archetype is a fact about the HOUSEHOLD.

    THE DEFECT: seeding the roll on the raw gas supply-point id. It would draw a second,
    independent archetype for a family the world has already given one, so a dual-fuel
    household's two legs would disagree about how engaged it is -- and the world would be
    internally inconsistent about a household trait with nothing on any surface to say so.

    Driven by REPLAYING the roll off `household_of` and demanding the built schedule agrees. A
    control that asserted the source text says `household_of` would pass on a world that computed
    it and threw it away.
    """
    from simulation.household_segments import active_renewal_probability_for_customer
    from simulation.renewal_engagement import rolls_active_renewal

    suffixed = [c for c in resi_gas_customers
                if household_of(c["customer_id"]) != c["customer_id"]]
    assert suffixed, (
        "no gas leg on the roster carries the gas suffix, so the two keys agree everywhere and "
        "this control cannot tell them apart -- it has lost its subject")

    checked = 0
    for customer in suffixed:
        schedule = book[customer["customer_id"]]
        if len(schedule) < 2:
            continue
        household = household_of(customer["customer_id"])
        second = schedule[1]
        rolled_active = rolls_active_renewal(
            second["acquisition_date"], f"{household}_1",
            active_renewal_probability_for_customer(household),
        )
        expected = "fixed" if rolled_active else SVT_TARIFF_TYPE
        assert second["tariff_type"] == expected, (
            f"{customer['customer_id']}: the world's own roll for household {household} says "
            f"{expected!r} at {second['acquisition_date']} and the schedule says "
            f"{second['tariff_type']!r} -- the builder is not reading the household's archetype")
        checked += 1
    assert checked >= 10, f"only {checked} suffixed gas legs reached a second term"


# ---------------------------------------------------------------------------------------------
# THE FUEL: A GAS SEGMENT IS BILLED OFF THE GAS CAP
# ---------------------------------------------------------------------------------------------

def test_a_gas_segment_is_billed_off_the_published_GAS_cap_and_not_the_electricity_one(book):
    """THE DEFECT: `fuel="electricity"` at the gas call site, or a `fuel` default that reads it.

    A gas household billed the electricity cap settles, balances, and is wrong by about 4x --
    every field agrees with every other field, because there is only one of them. This is the
    only control in the tree that can see it, which is why it is asserted separately from the
    assignment: the mutation that swaps the fuel leaves every structural control green.

    The two series are checked to be DISTINGUISHABLE first, on this book's own dates. Asserting
    equality against one series proves nothing if the two series happen to agree.
    """
    segments = [t for schedule in book.values() for t in schedule
                if t["tariff_type"] == SVT_TARIFF_TYPE]
    assert segments, "no gas SVT segments in the book -- this control would pass vacuously"

    dates = sorted({t["acquisition_date"] for t in segments})
    separable = [
        d for d in dates
        if get_svt_gas_rate_gbp_per_mwh(d) != get_svt_elec_rate_gbp_per_mwh(d)
    ]
    assert len(separable) == len(dates), (
        "the published gas and electricity cap series agree on some of this book's segment "
        f"dates ({len(dates) - len(separable)} of {len(dates)}), so equality with one of them "
        "does not exclude the other -- repoint this control before trusting it")

    for term in segments:
        expected = get_svt_gas_rate_gbp_per_mwh(term["acquisition_date"])
        assert term["unit_rate_gbp_per_mwh"] == expected, (
            f"a gas SVT segment starting {term['acquisition_date']} is billed "
            f"{term['unit_rate_gbp_per_mwh']} where the published GAS cap says {expected} "
            f"(the electricity cap says {get_svt_elec_rate_gbp_per_mwh(term['acquisition_date'])})")


def test_a_gas_segment_closes_the_who_paid_it_identity_and_the_split_actually_bites(gas_records):
    """`unit_rate = household_charged + hmt_epg_receipt`, on gas, with the EPG window ATTAINED.

    THE DEFECT: the gas twin of `get_svt_elec_rate_charged_to_household_gbp_per_mwh` wired to the
    wrong instrument, or not wired at all. Outside 2022-10-01..2023-06-30 the two legs are the
    same number, so an identity asserted only on those dates is true of a segment that never
    heard of the EPG. The window is straddled deliberately and the receipt is asserted STRICTLY
    POSITIVE inside it -- "the split turned on" and "the split is always on" are the two things
    this ordering exists to keep apart.
    """
    schedule = build_svt_schedule("C-GAS-EPG", "2022-07-01", "2023-12-31", gas_records, fuel="gas")
    assert schedule, "no segments built"

    inside = [t for t in schedule if "2022-10-01" <= t["acquisition_date"] <= "2023-06-30"]
    outside = [t for t in schedule if t not in inside]
    assert inside and outside, (
        f"the fixture does not straddle the EPG window: {len(inside)} in, {len(outside)} out")

    for term in schedule:
        assert term["unit_rate_gbp_per_mwh"] == pytest.approx(
            term["household_charged_unit_rate_gbp_per_mwh"]
            + term["hmt_epg_receipt_gbp_per_mwh"]), (
            f"the gas split does not close at {term['acquisition_date']}")

    assert all(t["hmt_epg_receipt_gbp_per_mwh"] > 0.0 for t in inside), (
        "a gas segment inside the Energy Price Guarantee carries no HM Treasury receipt: the "
        "household is being billed the Ofgem cap where the published guarantee held it at "
        "10.3p/kWh, and the identity above passes because both legs are the same wrong number")
    assert all(t["hmt_epg_receipt_gbp_per_mwh"] == 0.0 for t in outside), (
        "a gas segment outside the scheme carries a receipt: HM Treasury paid nothing there")


def test_build_svt_schedule_refuses_to_guess_a_fuel(gas_records):
    """THE DEFECT: a `fuel` default. Then a caller that never thought about the question gets
    electricity, and the omission looks exactly like a deliberate choice at every call site.

    Both refusals in one control: the missing argument and the unknown fuel. The second fails
    CLOSED and names its reason, because a fuel with no published domestic default tariff has no
    SVT product to be put on and a made-up ceiling would enter settlement under a name that says
    "published".
    """
    with pytest.raises(TypeError):
        build_svt_schedule("C-X", "2020-01-01", "2020-12-31", gas_records)

    with pytest.raises(ValueError) as refusal:
        build_svt_schedule("C-X", "2020-01-01", "2020-12-31", gas_records, fuel="hydrogen")
    assert "hydrogen" in str(refusal.value), (
        f"the refusal does not name what it refused: {refusal.value}")


# ---------------------------------------------------------------------------------------------
# NEITHER BUILDER RESTATES THE ROLL
# ---------------------------------------------------------------------------------------------

def test_neither_schedule_builder_mints_its_own_coin(gas_records):
    """THE DEFECT: the gas builder reproducing `rolls_active_renewal`'s draw inline.

    That is the shape `renewal_engagement.py`'s own docstring records having already happened
    once in this tree -- `rolls_active_renewal` reproduced `is_active_renewal`'s draw, and the
    two then had to be proven equal by hand. Reaches the SOURCE because the defect is about how
    many homes the decision has, and two implementations that agree today would pass any
    behavioural assertion.
    """
    tree = ast.parse(_WORLD.read_text())
    builder = next(
        (n for n in ast.walk(tree)
         if isinstance(n, ast.FunctionDef) and n.name == "_build_gas_renewal_schedule"), None)
    assert builder is not None, "_build_gas_renewal_schedule is gone -- repoint this control"

    called = {
        n.func.id for n in ast.walk(builder)
        if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)
    }
    assert "rolls_active_renewal" in called, (
        "the gas builder does not call the world's own roll: either the C1b block is gone or the "
        "decision has been restated here")
    assert not any(
        isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
        and n.func.attr in {"random", "Random"}
        for n in ast.walk(builder)), (
        "the gas builder draws its own random number -- the assignment must be the world's own "
        "roll and not a second one")
