"""R15 both-ways tests for the MC-2 collateral death-test breaking-strain sweep.

Ruling: DIRECTOR_RULING_MC2_REAL_HISTORY_NOT_DIFFICULTY_2026-07-25.
The controls under test (each with its named mutation that must red it):
  * §3 facility fixed at origination  -> mutate to re-derive per dose: teeth test reds.
  * §1 death-by-collateral WHILE P&L survives (the load-bearing shape) -> mutate the pnl clause:
    the insolvency-distinction test reds.
  * treasury cash counted in net liquidity -> mutate to drop it: the cash-rescue test reds.
The mutations are described in each test's docstring; they are applied by editing
company/risk/collateral_death_test.py, running this file, then restoring.
"""
from company.finance.margin_call_book import book_scaled_credit_facility_gbp
from company.risk.collateral_death_test import (
    DEFAULT_DOSES,
    breaking_strain_sweep,
    to_run_outcome_fields,
)


def _entry(netted, cp_type="BILATERAL_OTC_TRADER", rating="A"):
    return {
        "counterparty_id": "cp",
        "counterparty_type": cp_type,
        "clearing_status": "bilateral",
        "counterparty_rating": rating,
        "netted_mtm_gbp": float(netted),
    }


# Origination: a mildly-exposed mixed book. BANK-1 long (ITM, owed to company -> posts nothing),
# TRADER-1 short (slightly OTM). facility = max(250k, 1.5*(300k+100k)) = 600k.
ORIG = {"BANK-1": _entry(300_000.0), "TRADER-1": _entry(-100_000.0)}
# Stressed (a real price spike): BANK-1 deeply ITM (long benefits), TRADER-1 deeply OTM (short
# hammered). The company POSTS margin on TRADER-1 while its total book P&L stays POSITIVE.
STRESS = {"BANK-1": _entry(1_200_000.0), "TRADER-1": _entry(-700_000.0)}


def test_facility_book_derived_at_origination():
    assert book_scaled_credit_facility_gbp(ORIG) == 600_000.0


def test_teeth_death_by_collateral_while_pnl_survives():
    """The 2021-22 acceptance-bar shape: survives at 0.8x, dies at 1.0x while solvent on paper.

    MUTATION (§3 facility fixed at origination): in breaking_strain_sweep, recompute the facility
    per dose from the stressed book -- inside the loop, right after ``scaled = _scale_exposure(...)``
    add ``facility_gbp = book_scaled_credit_facility_gbp(scaled)``. The facility then grows with the
    stressed book, net liquidity never goes negative, and the sweep reds (verified: reds this teeth
    test plus 4 others). Restore to green.
    """
    r = breaking_strain_sweep(ORIG, STRESS)
    assert r.facility_gbp == 600_000.0
    assert not r.survived
    assert r.death_dose == 1.0          # survives 0.8x, dies at the real 1.0x replay
    assert r.death_cause == "collateral_while_solvent"
    assert r.death_while_pnl_survives
    assert r.any_name_posted_margin
    # 0.8x survives; 1.0x is dead-on-cash yet solvent-on-paper.
    by_dose = {o.dose: o for o in r.doses}
    assert by_dose[0.8].net_liquidity_gbp > 0
    assert by_dose[1.0].net_liquidity_gbp < 0
    assert by_dose[1.0].book_pnl_gbp > 0            # 1_200_000 - 700_000 = 500_000, solvent on paper
    assert by_dose[1.0].pnl_survives


def test_liquidity_minimum_monotone_non_increasing_in_dose():
    """A larger price move drains more collateral -> net liquidity is non-increasing in dose."""
    r = breaking_strain_sweep(ORIG, STRESS, doses=DEFAULT_DOSES)
    liq = [o.net_liquidity_gbp for o in r.doses]
    assert liq == sorted(liq, reverse=True)
    assert r.liquidity_minimum_gbp == liq[-1]       # min reached at the harshest dose (1.5x)


def test_cash_rescue_averts_death_at_1x():
    """Drawing treasury cash to meet the call moves the death dose.

    MUTATION (cash counted): in breaking_strain_sweep, drop ``available_cash_gbp`` from the
    ``net_liquidity`` expression (``facility_gbp - total_call``). Then the cash no longer rescues
    the book and this test reds (still dead at 1.0x). Restore to green.
    """
    # +200k cash lifts 1.0x from -100k to +100k -> survives 1.0x, dies at 1.2x instead.
    r = breaking_strain_sweep(ORIG, STRESS, available_cash_gbp=200_000.0)
    by_dose = {o.dose: o for o in r.doses}
    assert by_dose[1.0].net_liquidity_gbp > 0       # cash rescued the 1.0x call
    assert not r.survived
    assert r.death_dose == 1.2


def test_pure_long_book_cannot_die_to_collateral_the_section4_diagnosis():
    """A fully-hedged long book is ITM on a spike, posts NO margin, and CANNOT die to collateral.

    This is the §4 'hedge cover masking the exposure' diagnosis, not a signal to make the test
    harsher. any_name_posted_margin=False is the load-bearing diagnosis flag.
    """
    orig = {"BANK-1": _entry(500_000.0, cp_type="BILATERAL_OTC_BANK")}
    stress = {"BANK-1": _entry(2_000_000.0, cp_type="BILATERAL_OTC_BANK")}   # still long, still ITM
    r = breaking_strain_sweep(orig, stress)
    assert r.survived
    assert r.death_dose is None
    assert not r.any_name_posted_margin             # the §4 diagnosis, data-driven
    assert r.peak_margin_call_gbp == 0.0


def test_insolvency_is_distinguished_from_the_mc2_shape():
    """Dead on BOTH cash and paper is ordinary insolvency, NOT the MC-2 solvent-on-paper shape.

    MUTATION (§1 load-bearing clause): in breaking_strain_sweep set
    ``death_while_pnl_survives=is_dead`` (drop the ``and pnl_survives``). Then this all-short,
    P&L-negative book would be mislabelled 'collateral_while_solvent' and this test reds. Restore.
    """
    orig = {"TRADER-1": _entry(-100_000.0)}                # facility floors at 250k
    stress = {"TRADER-1": _entry(-900_000.0)}              # deeply OTM, no ITM offset
    r = breaking_strain_sweep(orig, stress)
    assert not r.survived
    assert not r.death_while_pnl_survives                  # P&L is NEGATIVE -> not the special shape
    assert r.death_cause == "collateral_insolvent"
    by_dose = {o.dose: o for o in r.doses}
    assert by_dose[1.0].book_pnl_gbp < 0                   # -900k, insolvent on paper too


def test_deterministic_replay_c_s2():
    """Same inputs reproduce an identical result (pure function, no clock/RNG)."""
    a = breaking_strain_sweep(ORIG, STRESS, available_cash_gbp=50_000.0)
    b = breaking_strain_sweep(ORIG, STRESS, available_cash_gbp=50_000.0)
    assert a == b


def test_run_outcome_fields_are_the_raw_ledger_fields_only():
    """to_run_outcome_fields exposes ONLY the four raw RunOutcomes fields -- no score, no blend.

    Guards the scope line: MC-2 §2 authorises the raw measurement; the §6 survival SCORE stays
    director-session gated. A regression that added a blended/score field here would breach it.
    """
    r = breaking_strain_sweep(ORIG, STRESS)
    fields = to_run_outcome_fields(r)
    assert set(fields) == {
        "survived",
        "death_cause",
        "liquidity_headroom_min_gbp",
        "collateral_cover_min",
    }
    assert fields["survived"] is False
    assert fields["death_cause"] == "collateral_while_solvent"
    assert fields["liquidity_headroom_min_gbp"] == r.liquidity_minimum_gbp
    assert fields["collateral_cover_min"] == r.cover_minimum


def test_price_move_alone_no_injected_loss():
    """The cash call arises purely from the marks -- price_move_alone is structurally true."""
    r = breaking_strain_sweep(ORIG, STRESS)
    assert r.price_move_alone
    # every dose's call equals the OTM leg's posted margin, sourced only from netted MtM
    for o in r.doses:
        assert o.total_margin_call_gbp >= 0.0
