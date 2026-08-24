"""EP1's controls. Each of the four constraint sections below has a NAMED defect it fires on.

The fixture is built so the controls can DISCRIMINATE, which is the thing the sibling
suite (`tests/company/crm/test_clv_cohort_book.py`, 19 green) cannot do: every one of its
records carries a concrete float, so the blank-population question it exists beside
cannot arise in it, and three of its tests pin the blank-as-zero collapse as intended.
Here the two cells the live population cannot supply — a SUPPLIED account carrying no
margin, and a CEASED account carrying one — are constructed deliberately, because the
2026-08-19 finding measured that without them a population control on this book is
degenerate: `drop_null` and `supplied` came out bit-identical on every field.
"""

from __future__ import annotations

import json
import math
import subprocess
import tempfile
import textwrap
from pathlib import Path

import pytest

from company.analytics.clv_three_horizon import (
    CLV_SEAM_REGISTER,
    DISCOUNT_RATE,
    AccountObservables,
    BookCLV,
    Exclusion,
    Horizon,
    RenewalPoint,
    TimeModel,
    census_clv_modules,
    estimate_account,
    estimate_book,
    survival_discounted_value_gbp,
    unregistered_clv_modules,
)

REPO_ROOT = Path(__file__).resolve().parents[3]


def _renewals(*probabilities: float) -> tuple[RenewalPoint, ...]:
    return tuple(
        RenewalPoint(renewal_period="20" + str(20 + i) + "-06", churn_probability=p)
        for i, p in enumerate(probabilities)
    )


def _account(
    account_id: str,
    *,
    still_supplied: bool,
    margin: float | None,
    churns: tuple[float, ...] = (0.20,),
    segment: str = "residential",
    term_years: float = 1.0,
) -> AccountObservables:
    return AccountObservables(
        account_id=account_id,
        segment=segment,
        channel="pcw",
        acquisition_year=2020,
        contract_term_years=term_years,
        renewal_history=_renewals(*churns),
        annual_margin_gbp=margin,
        still_supplied=still_supplied,
    )


# The four-cell population the finding named. Two of these cells are EMPTY in the live
# book, which is why a control built only on live data cannot discriminate.
SUPPLIED_AND_VALUED = _account("A_sv", still_supplied=True, margin=100.0)
SUPPLIED_AND_BLANK = _account("A_sb", still_supplied=True, margin=None)
CEASED_AND_VALUED = _account("A_cv", still_supplied=False, margin=100.0)
CEASED_AND_BLANK = _account("A_cb", still_supplied=False, margin=None)
FOUR_CELLS = [
    SUPPLIED_AND_VALUED,
    SUPPLIED_AND_BLANK,
    CEASED_AND_VALUED,
    CEASED_AND_BLANK,
]


# ---------------------------------------------------------------------------
# The valuation kernel — the finite term, whose absence cost a published figure.
# ---------------------------------------------------------------------------


def test_term_is_priced_not_assumed_away():
    """A longer term is worth more, and the perpetuity is only its limit.

    Fires on: reinstating the perpetuity (the 2026-08-15 finding's own defect), which is
    invariant to `term_years` and would make all three of these equal.
    """
    one = survival_discounted_value_gbp(100.0, 0.20, 0.08, 1.0)
    two = survival_discounted_value_gbp(100.0, 0.20, 0.08, 2.0)
    thirty = survival_discounted_value_gbp(100.0, 0.20, 0.08, 30.0)
    assert one < two < thirty
    # The T -> infinity limit, reached but never exceeded.
    limit = 100.0 * 0.80 / (1.08 - 0.80)
    assert thirty < limit
    assert survival_discounted_value_gbp(100.0, 0.20, 0.08, 400.0) == pytest.approx(
        limit, rel=1e-9
    )


def test_term_value_is_bounded_by_the_undiscounted_ceiling():
    for term in (0.5, 1.0, 5.0, 30.0):
        value = survival_discounted_value_gbp(100.0, 0.20, 0.08, term)
        assert value <= 100.0 * term


def test_unit_retention_is_the_algebraic_limit_not_a_fallback():
    """retention == 1 + d: every period contributes exactly `margin` in present value."""
    # churn = -0.08 gives retention 1.08 == 1 + d exactly.
    assert survival_discounted_value_gbp(100.0, -0.08, 0.08, 7.0) == pytest.approx(700.0)


def test_certain_churn_and_zero_term_are_worth_nothing():
    assert survival_discounted_value_gbp(100.0, 1.0, 0.10, 5.0) == 0.0
    assert survival_discounted_value_gbp(100.0, 0.20, 0.10, 0.0) == 0.0


# ---------------------------------------------------------------------------
# Constraint 1 — every horizon declares its time model, and the declaration is TRUE.
# This is pass 8's free falsifier: same renewals, reversed order.
# ---------------------------------------------------------------------------


def test_reversing_a_customers_history_moves_the_order_aware_horizons():
    """THE control this atom has owed for eight passes.

    A deteriorating customer (shocks recent) and a recovering one (shocks ancient) have
    the same renewals in reversed order. The shipped sBG estimator returns bit-identical
    values for both, because its sufficient statistic is a SUM. H1 and H2 declare
    themselves order-aware, so they must not.

    Fires on: replacing `latest_renewal` with any order-blind statistic — a mean, a sum,
    a conjugate update on soft counts. Every one of those passes the between-account
    mutation the existing control uses and fails this one.
    """
    deteriorating = _account("D", still_supplied=True, margin=100.0,
                             churns=(0.05, 0.08, 0.14, 0.23, 0.32))
    recovering = _account("R", still_supplied=True, margin=100.0,
                          churns=(0.32, 0.23, 0.14, 0.08, 0.05))

    d = estimate_account(deteriorating)
    r = estimate_account(recovering)

    assert d.contract_term.time_model is TimeModel.CONSTANT_HAZARD_FIXED_TERM
    assert d.tenure_expected.time_model is TimeModel.LATEST_RENEWAL_CONDITIONED

    assert d.contract_term.value_gbp != r.contract_term.value_gbp
    assert d.tenure_expected.value_gbp != r.tenure_expected.value_gbp
    # And in the right direction: the customer whose latest renewal is the worst is worth
    # less. A control that only asserted "different" would pass on a sign error.
    assert d.tenure_expected.value_gbp < r.tenure_expected.value_gbp


def test_the_cohort_horizon_is_exchangeable_and_says_so():
    """THE NULL CONTROL for the test above.

    H3 pools over every renewal point of every member, so reversing a member's history
    cannot move it — and that is DECLARED, not discovered. Without this assertion the
    test above would be satisfied by an implementation in which everything moves, which
    would tell us nothing about whether the mutation reached the horizon it was aimed at.
    """
    forward = [
        _account("D", still_supplied=True, margin=100.0, churns=(0.05, 0.32)),
        _account("P", still_supplied=True, margin=100.0, churns=(0.10, 0.10)),
    ]
    reversed_history = [
        _account("D", still_supplied=True, margin=100.0, churns=(0.32, 0.05)),
        _account("P", still_supplied=True, margin=100.0, churns=(0.10, 0.10)),
    ]
    a = estimate_book(forward).account("D").portfolio_cohort
    b = estimate_book(reversed_history).account("D").portfolio_cohort
    assert a.time_model is TimeModel.POOLED_EXCHANGEABLE
    assert a.value_gbp == b.value_gbp

    # ...and the SAME permutation did move the order-aware horizon in the same run, so
    # the null control is a null control and not a broken mutation.
    assert (
        estimate_book(forward).account("D").tenure_expected.value_gbp
        != estimate_book(reversed_history).account("D").tenure_expected.value_gbp
    )


def test_every_horizon_carries_a_time_model_even_when_unestimable():
    """A blank is still a horizon, and a reader still needs to know which model it is."""
    blank = estimate_account(SUPPLIED_AND_BLANK)
    for which in Horizon:
        hv = blank.horizon(which)
        assert hv.value_gbp is None
        assert isinstance(hv.time_model, TimeModel)


# ---------------------------------------------------------------------------
# Constraint 2 — the output carries its population, not only its number.
# ---------------------------------------------------------------------------


def test_no_aggregate_is_published_without_its_population():
    book = estimate_book(FOUR_CELLS)
    assert book.portfolio.population.counted == 1  # only A_sv
    assert book.portfolio.population.excluded == 3
    assert book.portfolio.population.reasons == {
        Exclusion.CEASED.value: 2,
        Exclusion.NO_MARGIN_OBSERVED.value: 1,
    }
    assert book.portfolio.population.available == 4
    assert "ceased=2" in book.portfolio.population.describe()


def test_a_ceased_account_is_valued_and_excluded():
    """Both halves, because either alone is a defect this repo has already shipped.

    Fires on: dropping ceased accounts from the account list (the fact about a customer
    who left is destroyed) OR counting them in the aggregate (`66141b70c`'s defect — a
    forward book value built on customers the company no longer supplies).
    """
    book = estimate_book(FOUR_CELLS)
    ceased = book.account("A_cv")
    assert ceased is not None
    # VALUED: the account-level fact about a customer who left survives.
    assert ceased.tenure_expected.value_gbp is not None
    # EXCLUDED: and it is not in the forward claim about the book. Compared against the
    # same book with that account supplied, so the assertion is about the flag and not
    # about the arithmetic.
    supplied_instead = estimate_book(
        [SUPPLIED_AND_VALUED, _account("A_cv", still_supplied=True, margin=100.0)]
    )
    assert book.portfolio.population.reasons[Exclusion.CEASED.value] == 2
    assert book.portfolio.population.counted == 1
    assert supplied_instead.portfolio.population.counted == 2
    assert (
        supplied_instead.portfolio.total_value_gbp > book.portfolio.total_value_gbp
    )


def test_still_supplied_has_no_default_and_no_truthy_stand_in():
    with pytest.raises(TypeError):
        AccountObservables(
            account_id="X",
            segment="residential",
            channel="pcw",
            acquisition_year=2020,
            contract_term_years=1.0,
            renewal_history=_renewals(0.2),
            annual_margin_gbp=100.0,
            still_supplied="yes",  # type: ignore[arg-type]
        )
    with pytest.raises(TypeError):
        AccountObservables(
            account_id="X",
            segment="residential",
            channel="pcw",
            acquisition_year=2020,
            contract_term_years=1.0,
            renewal_history=_renewals(0.2),
            annual_margin_gbp=100.0,
            still_supplied=None,  # type: ignore[arg-type]
        )


def test_populations_differ_between_horizons_which_is_why_there_are_three():
    """An account with no history is unestimable on H1/H2 and fine on H3."""
    no_history = AccountObservables(
        account_id="NEW", segment="residential", channel="pcw",
        acquisition_year=2025, contract_term_years=1.0, renewal_history=(),
        annual_margin_gbp=100.0, still_supplied=True,
    )
    book = estimate_book([no_history, SUPPLIED_AND_VALUED])
    new = book.account("NEW")
    assert new.contract_term.value_gbp is None
    assert new.tenure_expected.value_gbp is None
    assert new.contract_term.population.reasons == {
        Exclusion.NO_RENEWAL_OBSERVED.value: 1
    }
    assert new.portfolio_cohort.value_gbp is not None

    on_tenure = estimate_book([no_history, SUPPLIED_AND_VALUED],
                              horizon=Horizon.TENURE_EXPECTED)
    on_cohort = estimate_book([no_history, SUPPLIED_AND_VALUED],
                              horizon=Horizon.PORTFOLIO_COHORT)
    assert on_tenure.portfolio.population.counted == 1
    assert on_cohort.portfolio.population.counted == 2


# ---------------------------------------------------------------------------
# Constraint 3 — a structural blank is not the number zero.
# ---------------------------------------------------------------------------


def test_swapping_a_blank_between_null_and_zero_moves_the_rendered_figure():
    """Pass 6's free falsifier, RUNNABLE on this horizon.

    On `company/crm/clv_cohort_book.py` this same mutation raises TypeError before either
    figure exists, so the control is un-runnable there — and a control that cannot be
    executed is not a control that passes. Here it runs and it must MOVE the number.

    Fires on: coercing `None` to `0.0` anywhere on the path — the `84ae6bbeb` defect.
    """
    with_blank = estimate_book([SUPPLIED_AND_VALUED, SUPPLIED_AND_BLANK])
    as_zero = estimate_book(
        [SUPPLIED_AND_VALUED, _account("A_sb", still_supplied=True, margin=0.0)]
    )
    assert with_blank.portfolio.mean_value_gbp is not None
    assert as_zero.portfolio.mean_value_gbp is not None
    assert with_blank.portfolio.mean_value_gbp != as_zero.portfolio.mean_value_gbp
    assert with_blank.portfolio.population.counted == 1
    assert as_zero.portfolio.population.counted == 2
    # The blank was named, the zero was counted. Both facts, not one.
    assert with_blank.portfolio.population.reasons == {
        Exclusion.NO_MARGIN_OBSERVED.value: 1
    }
    assert as_zero.portfolio.population.reasons == {}


def test_an_empty_cohort_is_not_a_worthless_cohort():
    """The §5 repair. The sibling module publishes the same object for both.

    Fires on: returning an all-zeros summary for an absent cohort, which is what
    `_cohort_summary` does one module away and what three of its tests assert as intended.
    """
    book = estimate_book([_account("Z", still_supplied=True, margin=0.0)])
    worthless = book.cohort("residential")
    nonexistent = book.cohort("sme")

    assert nonexistent is None  # no such cohort
    assert worthless is not None
    assert worthless.population.counted == 1
    assert worthless.mean_value_gbp == 0.0
    assert worthless.is_profitable is False

    # A cohort that exists but can value nobody is a THIRD state, distinct from both.
    all_blank = estimate_book([SUPPLIED_AND_BLANK]).cohort("residential")
    assert all_blank is not None
    assert all_blank.mean_value_gbp is None
    assert all_blank.is_profitable is None
    assert all_blank.population.is_empty


def test_a_blank_margin_must_be_explicit():
    with pytest.raises(TypeError):
        AccountObservables(
            account_id="X", segment="residential", channel="pcw",
            acquisition_year=2020, contract_term_years=1.0,
            renewal_history=_renewals(0.2),
            annual_margin_gbp="unknown",  # type: ignore[arg-type]
            still_supplied=True,
        )


def test_zero_hazard_is_refused_rather_than_priced_as_immortality():
    """No observed propensity to leave is not evidence of an infinite tenure."""
    immortal = _account("I", still_supplied=True, margin=100.0, churns=(0.0,))
    result = estimate_account(immortal)
    assert result.tenure_expected.value_gbp is None
    assert result.tenure_expected.population.reasons == {
        Exclusion.NO_RENEWAL_OBSERVED.value: 1
    }
    # H1 still values it: a term is finite whether or not the hazard is zero.
    assert result.contract_term.value_gbp == pytest.approx(100.0 / (1 + DISCOUNT_RATE))


def test_a_lonely_account_gets_no_cohort_horizon_rather_than_its_own_numbers():
    """H3 must not silently become H2 for an account with no peers."""
    lonely = _account("L", still_supplied=False, margin=100.0)
    result = estimate_account(lonely)  # no cohort statistics supplied
    assert result.portfolio_cohort.value_gbp is None
    assert result.portfolio_cohort.population.reasons == {
        Exclusion.NO_COHORT_PEERS.value: 1
    }


def test_no_finite_horizon_is_ever_nan_or_inf():
    book = estimate_book(FOUR_CELLS + [
        _account("EDGE", still_supplied=True, margin=100.0, churns=(1.0,)),
    ])
    for account in book.accounts:
        for which in Horizon:
            value = account.horizon(which).value_gbp
            assert value is None or math.isfinite(value)


# ---------------------------------------------------------------------------
# Constraint 4 — the reconciliation is a ratchet, not a recommendation.
# ---------------------------------------------------------------------------


def test_the_register_names_every_clv_module_in_the_tree():
    """No nineteenth CLV without a horizon.

    Fires on: any new module binding a CLV-named symbol. Mutation-proven below on a real
    probe module written into the real tree.
    """
    unregistered, stale = unregistered_clv_modules(REPO_ROOT)
    assert unregistered == [], (
        "CLV producers with no entry in CLV_SEAM_REGISTER: " + str(unregistered)
        + " -- name the horizon it answers, or retire it."
    )
    assert stale == [], (
        "CLV_SEAM_REGISTER entries whose module no longer binds a CLV symbol: "
        + str(stale) + " -- if the disposition was executed, drop the entry."
    )


def test_the_census_actually_reached_the_tree():
    """Anti-fail-open: a census that read nothing would make the test above vacuous.

    Fires on: any collapse of the walk (wrong root, skipped package, swallowed error) —
    the register would then be trivially complete against an empty census.
    """
    census = census_clv_modules(REPO_ROOT)
    assert len(census) >= 15, "census found only " + str(len(census)) + " modules"
    assert "saas/clv_model.py" in census
    assert "company/crm/clv_cohort_book.py" in census
    assert "<unparseable>" not in [s for names in census.values() for s in names]
    # The census's own home is excluded, and it is the ONLY exclusion.
    assert "company/analytics/clv_three_horizon.py" not in census


def test_every_register_entry_states_a_disposition_and_a_reason():
    for module, (disposition, reason) in CLV_SEAM_REGISTER.items():
        assert disposition in {"ADOPT", "RETIRE", "DIFFERS"}, module
        assert len(reason) > 40, module  # a disposition without an argument is a note


def test_a_new_clv_producer_is_refused_by_the_register():
    """R15 RED leg, on the REAL tree — the defect the ratchet exists for.

    Writes a probe module that binds a CLV symbol into `company/analytics/`, asserts the
    census sees it and the register refuses it, and deletes it in a `finally`. Without
    this the ratchet is a claim about code that has never been shown to fire.
    """
    probe = REPO_ROOT / "company" / "analytics" / "_ep1_probe_clv_producer.py"
    try:
        probe.write_text(
            textwrap.dedent(
                '''
                """Transient R15 probe. Deleted by the test that wrote it."""
                def probe_clv_gbp() -> float:
                    return 1.0
                '''
            ).lstrip(),
            encoding="utf-8",
        )
        census = census_clv_modules(REPO_ROOT)
        rel = "company/analytics/_ep1_probe_clv_producer.py"
        assert rel in census, "the census did not see a new CLV producer"
        unregistered, _ = unregistered_clv_modules(REPO_ROOT)
        assert rel in unregistered, "the register did not refuse an unregistered producer"
    finally:
        probe.unlink(missing_ok=True)
    # And green again once the probe is gone, so the RED was the probe and not the tree.
    assert unregistered_clv_modules(REPO_ROOT)[0] == []


def test_the_census_fails_loudly_on_an_unparseable_module():
    """R15: an unreadable file must not read as a clean one.

    Fires on: swallowing SyntaxError and `continue`-ing, which would let a module hide
    from the ratchet by failing to parse.
    """
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        (root / "company").mkdir()
        (root / "company" / "broken.py").write_text("def (:\n", encoding="utf-8")
        census = census_clv_modules(root)
        assert census["company/broken.py"] == ["<unparseable>"]
        unregistered, _ = unregistered_clv_modules(root)
        assert "company/broken.py" in unregistered


def test_the_old_horizon_vocabulary_is_not_reintroduced_here():
    """This module took a name that had been wrong for eight passes.

    `company/core/three_horizon_clv.py` answered a variance question under this atom's
    name until the first commit of this draw renamed it. The register must keep saying
    the two are different questions, or the collision returns as a comment.
    """
    disposition, reason = CLV_SEAM_REGISTER["company/core/commitment_actual_forecast.py"]
    assert disposition == "DIFFERS"
    assert "variance" in reason.lower() or "points in time" in reason.lower()
    out = subprocess.run(
        ["git", "-C", str(REPO_ROOT), "ls-files", "company/core/three_horizon_clv.py"],
        capture_output=True, text=True, check=False,
    )
    assert out.stdout.strip() == "", "the renamed module is back in the index"


# ---------------------------------------------------------------------------
# PUBLICATION — the estimator's output has to leave the process to be worth anything.
#
# Each control below names the defect it fires on, and each was run against a
# deliberately broken `as_published_dict` before being run against the shipped one.
# The pattern being guarded is the one this atom has already committed twice: a
# number that exists in an object and reaches no reader is indistinguishable from a
# number that was never computed.
# ---------------------------------------------------------------------------


def _published_four_cells() -> dict:
    return estimate_book(FOUR_CELLS).as_published_dict()


def test_the_published_book_is_json_safe_all_the_way_down():
    """DEFECT: an Enum, a dataclass or a tuple survives into the artefact.

    `json.dumps` on the shipped output is the whole control — a `BookCLV` handed
    straight to a writer raises here, which is what a caller would have hit at the
    end of a nine-minute run rather than in a test.
    """
    payload = _published_four_cells()
    round_tripped = json.loads(json.dumps(payload))
    assert round_tripped == payload, "the payload is not its own JSON round trip"


def test_the_published_book_states_the_basis_its_aggregate_was_built_on():
    """DEFECT: a portfolio mean published with no horizon and no discount rate.

    All three horizons exist for every account, so an aggregate figure without its
    basis is uninterpretable rather than merely under-labelled. The two are read
    from the CALL, so a book aggregated on a different horizon says so.
    """
    on_contract = estimate_book(
        FOUR_CELLS, horizon=Horizon.CONTRACT_TERM
    ).as_published_dict()
    on_cohort = estimate_book(
        FOUR_CELLS, horizon=Horizon.PORTFOLIO_COHORT, discount_rate=0.05
    ).as_published_dict()

    assert on_contract["aggregate_horizon"] == Horizon.CONTRACT_TERM.value
    assert on_contract["discount_rate"] == DISCOUNT_RATE
    assert on_cohort["aggregate_horizon"] == Horizon.PORTFOLIO_COHORT.value
    assert on_cohort["discount_rate"] == 0.05
    # Independence: the label moved because the AGGREGATE moved, not because a
    # string was copied. A different horizon counts a different population here.
    assert (
        on_contract["portfolio"]["population"]["counted"]
        != on_cohort["portfolio"]["population"]["counted"]
    )


def test_the_basis_cannot_be_omitted_by_a_caller_that_forgets_it():
    """DEFECT: `aggregate_horizon` defaulted, so a future construction site drops it.

    The same shape as `still_supplied`: a field that may be forgotten is a field
    that will be, and this one decides whether a published figure means anything.
    """
    with pytest.raises(TypeError):
        BookCLV(  # type: ignore[call-arg]
            accounts=(),
            cohorts={},
            portfolio=estimate_book(FOUR_CELLS).portfolio,
        )


def test_a_structural_blank_survives_publication_as_null_not_as_zero():
    """DEFECT: the serialiser coerces `None` to 0.0 and publishes 'worth nothing'.

    `A_sb` is supplied with NO observed margin — the cell the live book cannot
    supply. Its contract-term value must arrive as `null` carrying its reason, and
    the reason must be the named exclusion rather than an empty dict.
    """
    payload = _published_four_cells()
    blank = next(a for a in payload["accounts"] if a["account_id"] == "A_sb")
    contract = blank[Horizon.CONTRACT_TERM.value]
    assert contract["value_gbp"] is None
    assert contract["population"]["reasons"] == {Exclusion.NO_MARGIN_OBSERVED.value: 1}

    valued = next(a for a in payload["accounts"] if a["account_id"] == "A_sv")
    assert valued[Horizon.CONTRACT_TERM.value]["value_gbp"] is not None
    # Independence from the assertion above: the blank and the valued account differ
    # in the artefact, so a serialiser that emitted `None` for everything would fail.
    assert valued[Horizon.CONTRACT_TERM.value]["time_model"] == (
        TimeModel.CONSTANT_HAZARD_FIXED_TERM.value
    )


def test_the_published_population_carries_the_denominator_that_was_available():
    """DEFECT: `available` is dropped at the seam and re-derived downstream.

    A reader of JSON has no properties. `counted + excluded` recomputed in three
    publishers is three chances to recompute it differently; it is written once by
    the object that owns it.
    """
    payload = _published_four_cells()
    population = payload["portfolio"]["population"]
    assert population["available"] == population["counted"] + population["excluded"]
    assert population["available"] == len(FOUR_CELLS)
    # The ceased accounts are excluded UNDER THEIR NAME, not silently absent.
    assert population["reasons"].get(Exclusion.CEASED.value) == 2


def test_an_empty_cohort_publishes_a_null_verdict_not_a_false_one():
    """DEFECT: `is_profitable` re-derived downstream as `mean > 0`, so `None` -> False.

    A cohort with no counted member and a cohort that loses money must not publish
    the same boolean. Here every member of the `gone` segment has ceased, so the
    cohort exists and counts nobody.
    """
    ceased_only = [
        _account("G1", still_supplied=False, margin=100.0, segment="gone"),
        _account("G2", still_supplied=False, margin=100.0, segment="gone"),
        SUPPLIED_AND_VALUED,
    ]
    payload = estimate_book(ceased_only).as_published_dict()
    gone = payload["cohorts"]["gone"]
    assert gone["mean_value_gbp"] is None
    assert gone["is_profitable"] is None, "an empty cohort published a verdict"
    assert gone["population"]["counted"] == 0
    assert payload["cohorts"]["residential"]["is_profitable"] is True


def test_the_published_book_is_deterministic_and_ordered():
    """DEFECT: dict/tuple iteration order leaks into the artefact, so two identical
    runs produce two different files and every diff of a published report is noise."""
    shuffled = list(reversed(FOUR_CELLS))
    assert estimate_book(FOUR_CELLS).as_published_dict() == (
        estimate_book(shuffled).as_published_dict()
    )
    ids = [a["account_id"] for a in _published_four_cells()["accounts"]]
    assert ids == sorted(ids)


def test_every_account_publishes_all_three_horizons():
    """DEFECT: the serialiser publishes only the aggregate horizon, which would make
    the artefact unable to answer the question the atom is named for."""
    payload = _published_four_cells()
    for account in payload["accounts"]:
        for horizon in Horizon:
            assert horizon.value in account, (
                f"{account['account_id']} is missing {horizon.value}"
            )
            assert account[horizon.value]["horizon"] == horizon.value
