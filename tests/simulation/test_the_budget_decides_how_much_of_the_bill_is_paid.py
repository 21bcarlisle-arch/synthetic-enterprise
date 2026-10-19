"""The household budget decides how much of each energy bill is paid (W2_4, built 2026-10-19).

Design: `docs/market_research/household_budget_w2_4.md`, "2026-10-16: design for the next build".
Each control names the defect it catches."""
from datetime import date

import pytest

import simulation.household_budget as hb
from background.live_payment_triad import LivePaymentTriad
from simulation.household import household_of


def _ids_by_margin(year, n=4000):
    """Real customer ids, split by the margin their own drawn budget gives in `year`."""
    under, short, comfortable = [], [], []
    for i in range(n):
        cid = f"RESI{i:05d}"
        b = hb.budget_in_year(hb.draw_household_budget(household_of(cid)), year)
        m = hb.margin_in_year(b, year)
        if m < -50 and b.savings_buffer < 200:
            under.append(cid)
        elif 20 < m < 100 and b.savings_buffer < 200:
            short.append(cid)
        elif m > 1500 and b.savings_buffer > 5000:
            comfortable.append(cid)
    return under, short, comfortable


def test_the_switch_ships_off_defect_a_world_change_landed_before_its_paired_grade():
    assert hb.BUDGET_DECIDES_PAYMENT is False


def test_the_floor_leaves_energy_out_defect_energy_counted_in_the_floor_and_again_as_the_bill():
    # JRF's whole basket holds GBP 24 (single) and 33 (couple) a week of electricity and gas. Its
    # itemised lines sum to 122 and 202 against headlines of 120 and 205, so the gap is the energy
    # line to within that rounding, never zero.
    for ex, whole, energy in ((hb._CORE_EX_ENERGY_SINGLE, hb._ESSENTIALS_GUARANTEE_SINGLE, 24),
                              (hb._CORE_EX_ENERGY_COUPLE, hb._ESSENTIALS_GUARANTEE_COUPLE, 33)):
        assert whole - ex == pytest.approx(energy * 52 / 12, abs=15)


def test_the_margin_is_in_the_run_years_pounds_defect_2026_prices_against_a_2016_bill():
    b = hb.draw_household_budget(household_of("RESI00007"))
    # Income deflates faster than the floor before 2021 (AWE 0.655 against the basket's 0.708), so a
    # 2016 margin is not the 2026/27 margin scaled, and both differ from the undeflated one.
    assert hb.margin_in_year(b, 2026) == pytest.approx(b.monthly_disposable_income - (
        hb._CORE_EX_ENERGY_BY_COMPOSITION[b.composition] + b.housing_cost_monthly), abs=0.01)
    assert hb.margin_in_year(b, 2016) < hb.margin_in_year(b, 2026)


def test_the_bottom_deciles_follow_the_benefit_path_and_it_can_be_read_off():
    """GAP named in the code (HBAI income by source not fetched): the path is a parameter, so a run
    can be read with it off rather than blended silently."""
    for i in range(400):
        b = hb.draw_household_budget(f"HH{i}")
        if b.income_decile in hb.BENEFIT_PATH_DECILES:
            break
    else:
        pytest.fail("no bottom-decile household in 400 draws")
    # 2022: benefits uprated by September 2021's 3.1%, earnings by AWE.
    assert hb.margin_in_year(b, 2022) != hb.margin_in_year(b, 2022, benefit_path_deciles=())


def test_every_branch_of_the_book_is_reachable_defect_a_book_that_pays_everything_or_nothing():
    """The partition first: a bill paid on time, a run of unpaid bills, and an unpaid bill cleared
    later must all occur, or every other control here passes on a book that never branches."""
    under, short, comfortable = _ids_by_margin(2022)
    assert under and short and comfortable, "the draw lacks one of the three households"
    book = hb.BudgetPaymentBook()
    paid_on_time = unpaid = cleared_later = 0
    ref = 0
    for cid in comfortable[:5] + under[:5]:
        for m in range(1, 13):
            ref += 1
            paid, earlier = book.settle_month(supply_point=cid, household=household_of(cid),
                                              year=2022, amount_gbp=150.0, legs=1, ref=ref)
            paid_on_time += paid
            unpaid += not paid
            cleared_later += len(earlier)
    # A household whose margin is positive but short of the bill falls behind and catches up as its
    # money accumulates, oldest bill first.
    for cid in short[:5]:
        for m in range(1, 13):
            ref += 1
            _, earlier = book.settle_month(supply_point=cid, household=household_of(cid),
                                           year=2022, amount_gbp=150.0, legs=1, ref=ref)
            cleared_later += len(earlier)
    assert paid_on_time and unpaid and cleared_later, (paid_on_time, unpaid, cleared_later)


def test_a_household_under_water_misses_month_after_month_defect_one_miss_then_resume():
    under, short, _ = _ids_by_margin(2022)
    cid = under[0]
    book = hb.BudgetPaymentBook()
    results = [book.settle_month(supply_point=cid, household=household_of(cid), year=2022,
                                 amount_gbp=120.0, legs=1, ref=m)[0] for m in range(12)]
    assert results.count(False) >= 11, results
    assert len(book.unpaid_of(cid)) >= 11


def test_a_comfortable_household_pays_every_bill_defect_the_budget_fails_everyone():
    _, _, comfortable = _ids_by_margin(2022)
    cid = comfortable[0]
    book = hb.BudgetPaymentBook()
    assert all(book.settle_month(supply_point=cid, household=household_of(cid), year=2022,
                                 amount_gbp=300.0, legs=1, ref=m)[0] for m in range(24))


def test_arrears_clear_oldest_first_defect_a_newer_bill_paid_while_an_older_one_ages():
    under, short, _ = _ids_by_margin(2022)
    cid = short[0]
    book = hb.BudgetPaymentBook()
    for r in (1, 2, 3):
        assert not book.settle_month(supply_point=cid, household=household_of(cid), year=2022,
                                     amount_gbp=500.0, legs=1, ref=r)[0]
    earlier = ()
    for r in range(4, 40):
        _, earlier = book.settle_month(supply_point=cid, household=household_of(cid), year=2022,
                                       amount_gbp=1.0, legs=1, ref=r)
        if earlier:
            break
    assert earlier[:1] == (1,), earlier
    assert list(earlier) == sorted(earlier)


def _triad_book(monkeypatch, on):
    monkeypatch.setattr(hb, "BUDGET_DECIDES_PAYMENT", on)
    under, short, _ = _ids_by_margin(2022)
    triad = LivePaymentTriad()
    out = []
    for cid in under[:6]:
        for m in range(1, 13):
            rec = triad.record_period(customer_id=cid, due_date=date(2022, m, 28), amount_gbp=120.0,
                                      income_stress_value="low", segment="resi")
            out.append(rec["result"])
    return out


def _failed(results):
    return sum(r != "PAID" and "FAIL" in r for r in results)


def test_the_triad_reaches_the_book_only_with_the_switch_on_defect_a_rule_no_payment_path_reads(monkeypatch):
    """The finding's own diagnosis was a budget nothing on a payment path read. On, the households
    under water miss most of their bills through the triad; off, the per-bill draw alone decides."""
    on = _triad_book(monkeypatch, True)
    off = _triad_book(monkeypatch, False)
    assert _failed(on) > len(on) // 2, on
    assert _failed(off) < len(off) // 4, off


def test_a_sub_penny_bill_is_paid_from_ample_money_defect_rounded_payment_against_an_unrounded_bill():
    """The run's bills carry sub-penny amounts (GBP 17.441972); the allocation pays in pence. The
    first on-arm capture left about half of all bills unpaid this way, from households holding
    thousands."""
    _, _, comfortable = _ids_by_margin(2022)
    cid = comfortable[0]
    book = hb.BudgetPaymentBook()
    for r, amount in enumerate((17.441972, 15.745179, 15.815389, 66.610832, 62.875984, 0.004)):
        paid, earlier = book.settle_month(supply_point=cid, household=household_of(cid), year=2016,
                                          amount_gbp=amount, legs=2, ref=r)
        assert paid and not earlier, (amount, book.unpaid_of(cid))


# THE INCOME MOVES EACH YEAR (2026-10-19): `household_budget_w2_4.md`, "how an under-water spell
# ends in the record". The 19 Oct paired grade found a household under water never left it.

def _under_water_paths(n=6000, years=range(2016, 2025)):
    paths = []
    for i in range(n):
        b = hb.draw_household_budget(household_of(f"RESI{i:05d}"))
        paths.append([hb.margin_in_year(hb.budget_in_year(b, y), y) < 0 for y in years])
    return paths


def test_an_under_water_spell_can_end_and_can_last_defect_a_margin_fixed_for_life():
    """The partition first: some household under water in 2016 is out of it by 2024, and some
    is still under water every year. A move rate of 1 or 0 fails one leg."""
    paths = [p for p in _under_water_paths() if p[0]]
    assert paths, "no household under water in 2016"
    assert any(not all(p) for p in paths) and any(all(p) for p in paths)


def test_the_yearly_exit_is_near_the_published_third_defect_an_exit_rate_nobody_printed():
    """DWP Income Dynamics: 36% AHC leave low income a year (range 32-40%)."""
    pairs = [(a, c) for p in _under_water_paths() for a, c in zip(p, p[1:]) if a]
    exit_rate = sum(not c for _, c in pairs) / len(pairs)
    assert 0.25 <= exit_rate <= 0.45, exit_rate


def test_the_move_leaves_the_under_water_share_where_it_was_defect_the_exit_drains_the_level():
    """A fresh draw from the same ladder: the share under water in 2024 is the drawn share at
    2024 prices, within sampling noise. The level is W2_38's question, not this build's."""
    n = 6000
    drawn = moved = 0
    for i in range(n):
        b = hb.draw_household_budget(household_of(f"RESI{i:05d}"))
        drawn += hb.margin_in_year(b, 2024) < 0
        moved += hb.margin_in_year(hb.budget_in_year(b, 2024), 2024) < 0
    assert abs(moved - drawn) / n < 0.015, (drawn, moved)


def test_two_legs_read_the_same_years_income_defect_a_purse_that_depends_on_posting_order():
    b = hb.draw_household_budget(household_of("RESI00042"))
    later_first = [hb.budget_in_year(b, y).monthly_disposable_income for y in (2024, 2019, 2016)]
    earlier_first = [hb.budget_in_year(b, y).monthly_disposable_income for y in (2016, 2019, 2024)]
    assert later_first == earlier_first[::-1]
    assert hb.budget_in_year(b, 2016) == b


def test_the_book_reads_the_moving_income_defect_an_exit_the_payment_path_never_reaches():
    """An under-water household whose income moves up pays again; with the move off, it never
    does. Unwiring `budget_in_year` from `settle_month` reds this."""
    for i in range(6000):
        cid = f"RESI{i:05d}"
        b = hb.draw_household_budget(household_of(cid))
        if b.savings_buffer < 50 and hb.margin_in_year(b, 2017) < -50 and \
                hb.margin_in_year(hb.budget_in_year(b, 2021), 2021) > 600:
            break
    else:
        pytest.fail("no household under water in 2017 that recovers by 2021")
    paid = {}
    for move in (hb.INCOME_MOVE_PER_YEAR, 0.0):
        book = hb.BudgetPaymentBook(income_move_per_year=move)
        ref = 0
        for year in (2017, 2018, 2019, 2020, 2021):
            for _ in range(12):
                ref += 1
                book.settle_month(supply_point=cid, household=household_of(cid), year=year,
                                  amount_gbp=60.0, legs=1, ref=ref)
        paid[move] = len(book.unpaid_of(cid))
    assert paid[hb.INCOME_MOVE_PER_YEAR] < paid[0.0], paid
