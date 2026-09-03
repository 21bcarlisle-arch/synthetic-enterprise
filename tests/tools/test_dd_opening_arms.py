"""Controls on the two-arm direct-debit comparison in `tools/dd_opening_arms.py`.

Each test names the defect it exists to catch. The subject is an EXPERIMENT, and an
experiment that quietly compares two different populations, or that averages a
household in credit against one in debit, produces a number that reads as a result
and is not one — which is precisely the class this repository has paid for most.
"""
from __future__ import annotations

from tools.dd_opening_arms import (
    _basis_and_rate_by_customer,
    _matched_window0,
    _split_credit_debit,
    basis_precedence_view,
    diff_run_outputs,
    flat_opening_by_customer,
)

# Two customers, three bills each, the first bill deliberately NOT the smallest so
# a rule that took min() rather than first-by-date would be caught too.
BILLS = [
    {"customer_id": "A", "period_end": "2019-01-31", "total_amount_gbp": 90.0,
     "segment": "resi", "commodity": "electricity"},
    {"customer_id": "A", "period_end": "2019-02-28", "total_amount_gbp": 40.0,
     "segment": "resi", "commodity": "electricity"},
    {"customer_id": "B", "period_end": "2019-03-31", "total_amount_gbp": 25.0,
     "segment": "resi", "commodity": "gas"},
    {"customer_id": "B", "period_end": "2019-04-30", "total_amount_gbp": 60.0,
     "segment": "resi", "commodity": "gas"},
]


def test_the_flat_arm_is_the_first_issued_bill_and_not_any_other_bill():
    """DEFECT: the baseline arm silently stops being the rule the organ displaced.

    The whole comparison is worthless if the flat arm is not `seq[0][1]`. A rule that
    took the mean, the min or the last bill would still produce a plausible-looking
    diff, and nothing else in the experiment would notice.
    """
    flat = flat_opening_by_customer(BILLS, direct_debit_only=False)
    assert flat == {"A": 90.0, "B": 25.0}


def test_the_dd_filtered_map_is_a_subset_of_the_unfiltered_one():
    """DEFECT: the two organs group differently and one map is used for both.

    `dd_balance_book` filters to direct-debit bills before taking `seq[0]`;
    `dd_review_runner` does not. Feeding one map to both would put a customer's
    non-DD first bill into the DD book's opening amount.
    """
    unfiltered = flat_opening_by_customer(BILLS, direct_debit_only=False)
    filtered = flat_opening_by_customer(BILLS, direct_debit_only=True)
    assert set(filtered) <= set(unfiltered)


def test_credit_and_debit_are_reported_separately_and_never_netted():
    """DEFECT: a household +200 in credit and one -200 in debit average to zero.

    "The mean drift is about zero" is the exact shape CLAUDE.md names — two
    populations with different experiences and different remedies, differenced into
    one number that describes neither. If this ever returns a single mean, the
    published drift figure becomes a statement nobody can act on.
    """
    split = _split_credit_debit([200.0, -200.0, 50.0])
    assert split["in_credit"]["n"] == 2
    assert split["in_debit"]["n"] == 1
    assert split["in_credit"]["mean_gbp"] == 125.0
    assert split["in_debit"]["mean_gbp"] == -200.0
    # There is no netted field to read by accident.
    assert "mean_gbp" not in split


def test_a_sample_of_one_earns_no_interval():
    """DEFECT: a one-observation interval of [x, x] publishes perfect confidence.

    A figure published without the bound its sample size earns is worse than no
    figure, and the fail-open reading of a bound is a zero-width one.
    """
    split = _split_credit_debit([42.0])
    assert split["in_credit"]["n"] == 1
    assert split["in_credit"]["ci95_gbp"] == [None, None]


def test_the_matched_comparison_holds_the_population_fixed():
    """DEFECT: comparing the arms over their UNION attributes the refusal to the rule.

    The estimate arm refuses every pre-2019 account, so its book is smaller. If the
    matched block took the union rather than the intersection it would compare 178
    accounts under one rule with 96 under the other and call the difference the
    rule's doing. Mutating `&` to `|` in `_matched_window0` turns this red.
    """
    flat_w = {"A": {0: -100.0}, "B": {0: -300.0}, "C": {0: -50.0}}
    est_w = {"A": {0: -10.0}, "B": {0: -400.0}}
    m = _matched_window0(flat_w, est_w)
    assert m["n_matched_accounts"] == 2
    assert m["flat"]["n_accounts"] == 2
    assert m["estimate"]["n_accounts"] == 2
    # A closer to zero, B further: the paired counts must split, not both fall one way.
    assert m["n_estimate_closer_to_zero"] == 1
    assert m["n_flat_closer_to_zero"] == 1


def test_the_estimate_arm_can_actually_call_the_live_door():
    """DEFECT: the instrument dies on a TypeError and its whole suite stays green.

    THIS ONE ALREADY HAPPENED. `e07449df5` landed this module at 04:30 passing
    `metered_annual_kwh=` and `declared_annual_kwh=`; `4e1502524` narrowed
    `estimate_annual_consumption` to the two rungs the opening instant reaches at 06:09
    and removed both parameters. From that commit every invocation of
    `python3 -m tools.dd_opening_arms` raised `TypeError` — and the six controls beside
    this one passed in 0.06s, because not one of them crossed into `run()`. A published
    comparison whose producer cannot run is a frozen artefact nobody can reproduce, and
    the suite said it was fine.

    So this control does the one thing the others do not: it CALLS the estimate arm's
    company-side entry with a real customer record. It asserts the KEY it gets back and
    not the value, because the value depends on the price cap series and the point here
    is signature compatibility, not arithmetic.
    """
    customers = [
        # A post-cap electricity account carrying a registration EAC: reaches REGISTRY_EAC.
        {"customer_id": "A", "acquisition_date": "2021-06-01",
         "commodity": "electricity", "eac_kwh": 3100.0},
        # No EAC, so the walk falls through to the published TDCV rung.
        {"customer_id": "B", "acquisition_date": "2021-06-01", "commodity": "gas"},
    ]
    out = _basis_and_rate_by_customer(customers)

    assert set(out) == {"A", "B"}, "the estimate arm did not reach every account handed to it"
    for cid, info in out.items():
        assert set(info) >= {"basis", "estimate_kwh", "has_published_rate"}, (
            "account {} came back without the fields the per-account report reads".format(cid))
    # The rung each account resolved to is a real rung of the live precedence, not a
    # string this test invented.
    from company.billing.annual_consumption_estimate import ConsumptionBasis

    for cid, info in out.items():
        assert info["basis"] in {b.value for b in ConsumptionBasis}, (
            "account {} resolved to a basis the company module does not define".format(cid))
    assert out["A"]["basis"] == ConsumptionBasis.REGISTRY_EAC.value, (
        "an account handed a registration EAC did not resolve to the EAC rung, so the "
        "instrument is no longer measuring the rule the live route walks")


def test_an_unreachable_rung_is_published_as_a_reason_and_never_as_a_zero():
    """DEFECT: the page prints `our own meter reads 0` and the reader believes we looked.

    A rung the opening instant CANNOT reach is not a rung that scored nothing. One is a
    measurement, the other is a structural absence, and rendering both as `0` tells the
    reader the supplier considered a source it has no way to consult. The two exclusions
    also differ in KIND — metered history is definitional and permanent, a customer
    declaration is a world gap that lifts — so each must carry its own reason.

    Mutating `basis_precedence_view` to fold `excluded` into `walked` with `n_accounts:
    0`, or to drop the `reason`, turns this red.
    """
    view = basis_precedence_view({"registry_eac": 142})

    walked_names = [r["basis"] for r in view["walked"]]
    excluded_names = [r["basis"] for r in view["excluded"]]
    assert not set(walked_names) & set(excluded_names), (
        "a rung is published as both walked and excluded")
    assert excluded_names, (
        "no rung is published as unreachable, so the precedence reads as fully exercised")
    for row in view["excluded"]:
        assert row.get("reason"), (
            "excluded rung {} is published without the reason it cannot be "
            "reached".format(row["basis"]))
        assert "n_accounts" not in row, (
            "excluded rung {} carries a count, which is exactly the zero that reads as a "
            "measurement".format(row["basis"]))
    # The reasons are DISTINCT. One boilerplate reason repeated over both rungs would
    # satisfy every assertion above and lose the whole distinction.
    reasons = {row["reason"] for row in view["excluded"]}
    assert len(reasons) == len(view["excluded"]), (
        "two unreachable rungs share one reason, so their different kinds are lost")


def test_the_published_precedence_is_derived_and_not_a_count_someone_typed():
    """DEFECT: the block is keyed to today's answer and rots the next time a rung moves.

    The sentence this replaced said "SLC 27.15's four sources ... three of the four are
    unreached". It was true when written and false two hours later, and nothing could
    notice because the four was prose. A replacement that hard-codes "two" is the same
    defect with a different number.

    So: the walked rungs must BE `BASIS_ORDER`, in its order, and the excluded ones must
    BE `NOT_REACHABLE_AT_OPENING`. Adding a rung to either tuple moves this page without
    anyone editing it — and turns this test red if the view stops deriving.
    """
    from company.billing.annual_consumption_estimate import (
        BASIS_ORDER,
        NOT_REACHABLE_AT_OPENING,
    )

    view = basis_precedence_view({})
    assert [r["basis"] for r in view["walked"]] == [b.value for b in BASIS_ORDER], (
        "the published precedence is not the one the company module declares, or is not "
        "in its order -- best-first is the whole content of SLC 27.15's instruction")
    assert [r["basis"] for r in view["excluded"]] == [
        x.basis.value for x in NOT_REACHABLE_AT_OPENING], (
        "the published exclusions are not the ones the company module names")
    # A basis the run resolved to that the declared precedence does not name is a
    # disagreement between the organ and its contract, and must surface rather than be
    # quietly dropped on the floor.
    stray = basis_precedence_view({"registry_eac": 3, "some_future_rung": 7})
    assert stray["unaccounted_for"] == {"some_future_rung": 7}, (
        "a basis outside the declared precedence was discarded silently")


def test_the_substrate_fingerprint_reaches_the_reader_and_is_not_recomputed():
    """DEFECT: an honest republish silently deletes a true provenance field.

    `site/data/dd_opening_arms.json` was published carrying `substrate_sha256` while
    NO code in the tree emitted it -- a lane computed it in an uncommitted
    `publish_view` and landed the output without the producer. The value was correct,
    which is what made it dangerous: the next person to regenerate the feed honestly
    would have dropped it, and the diff would have read as a deliberate removal of
    provenance.

    `run_output_latest.json` is a MOVING name, rewritten every publish, so the
    fingerprint is the only thing that says which book this comparison was measured
    over. And it must be CARRIED from the artefact, never recomputed in `publish_view`
    -- recomputing would stamp today's substrate onto a measurement made against a
    different one, which is worse than publishing nothing.
    """
    from tools.dd_opening_arms import publish_view

    result = {
        "clock": {"substrate": "docs/reports/run_output_latest.json",
                  "substrate_sha256": "deadbeef", "n_bills": 10906},
        "whole_run_output_diff": {"moved_keys": ["dd_balance_book"], "unmoved_keys": ["x"]},
        "per_account": {
            "window0_end_balance_drift_matched_population": {"n_matched_accounts": 2},
            "unestimated": {"estimate_n": 0},
            "basis_split_of_estimated_accounts": {"registry_eac": 2},
        },
    }
    block = publish_view(result)
    assert block["substrate_sha256"] == "deadbeef", (
        "the substrate fingerprint does not reach the reader, so the published comparison "
        "cannot be tied to the book it was measured over")

    # An artefact made before the fingerprint existed publishes None, not a hash of
    # whatever file happens to be on disk now.
    del result["clock"]["substrate_sha256"]
    assert publish_view(result)["substrate_sha256"] is None, (
        "publish_view invented a fingerprint for an artefact that carries none, which "
        "attributes today's substrate to yesterday's measurement")


def test_the_diff_states_what_did_not_move_as_well_as_what_did():
    """DEFECT: "only the DD keys moved" is a claim about the keys nobody looked at.

    A diff that returns only its hits cannot distinguish "101 keys were compared and
    held" from "101 keys were never read". The complement is the evidence.
    """
    a = {"x": 1, "y": 2, "z": 3}
    b = {"x": 1, "y": 99, "z": 3}
    d = diff_run_outputs(a, b)
    assert d["moved_keys"] == ["y"]
    assert d["unmoved_keys"] == ["x", "z"]
    assert not set(d["moved_keys"]) & set(d["unmoved_keys"])
    assert d["leaf_diffs"]["y"] == ["y: 2 -> 99"]
