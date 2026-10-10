"""A published GBP/MWh must say WHICH GBP/MWh, and the one called effective must be the whole bill.

WHAT WAS PUBLISHED, AND WHAT READ IT. `site/data/customers.json` carried `avg_rate_gbp_per_mwh`.
It was the volume-weighted COMMODITY leg — `saas/bill_generator` computes
`average_unit_rate_gbp_per_mwh` as `commodity_amount / MWh`, wholesale energy and nothing else: no
network charges, no policy levies, no standing charge, no VAT. Nothing about the name said so.

Measured over the whole book on 2026-08-31, the day this landed:

    commodity leg   102.57 GBP/MWh          effective   156.42 GBP/MWh      1.53x understated
    per account     median ratio 1.59x      worst 4.17x

**The misreading had already happened.** `tools/couple_value_based_pricing.compare` took the field
as `current_rate_gbp_per_mwh` — "what this customer currently pays" — and derived
`base_rate = current_rate - TARGET_MARGIN` from it, so an entire pricing arm was anchored on two
thirds of the real price. The end-to-end journey walk predicted this reader in as many words
(*"the next reader who needs 'what the customer paid' cannot take this field and be quietly
wrong"*) and the reader was already there.

A bill legitimately has both rates and both are worth publishing. What was missing was anything
saying which a field is, so both are published and both are named.

THE CATCH-UP EXCLUSION IS PART OF THE CLAIM, NOT HOUSEKEEPING. A catch-up bill reconciles earlier
estimated reads: its MONEY spans up to thirteen periods while its VOLUME spans one, so
total/volume on that row is not a rate. 959 of 11,167 bills carry one and **178 of them have a
negative GBP/MWh** — the sign is the only reason the defect is ever visible, and every other
catch-up bill is wrong by an amount nothing announces.
"""
from __future__ import annotations

import json
import pathlib

import pytest

PROJECT = pathlib.Path(__file__).resolve().parents[2]
PUBLISHED = PROJECT / "site" / "data" / "customers.json"
RUN = PROJECT / "docs" / "reports" / "run_output_latest.json"

#: A published rate whose name does not distinguish it from the other rate on the same bill. It is
#: named here rather than described, because the whole finding is that a reader cannot tell.
_AMBIGUOUS = "avg_rate_gbp_per_mwh"


@pytest.fixture(scope="module")
def legs() -> list[dict]:
    """The published legs, GENERATED FROM THE RUN OUTPUT IN THIS TREE rather than read off disk.

    THE FIRST VERSION READ `site/data/customers.json` AND PINNED A FLOOR OF 200 LEGS, and it fired
    on its first run in a different checkout -- correctly. That tree's `run_output_latest.json` is a
    1,600-bill artefact against the 11,167-bill one the control was written beside, so the published
    surface there has 19 legs. The floor did its job and the SUBJECT was wrong: a control keyed to
    how big the book happens to be goes red when the book legitimately changes size, and stays green
    when the claim rots. That is exactly backwards, and it is this repo's most-repeated shape.

    So the subject is the GENERATOR against the run output beside it, which is a property that holds
    at any book size. The floor that remains is the one that means something: a scan with no
    subjects is not a pass. The live artefact is checked separately, and only for the one thing that
    is true of it whatever the publisher last did — see the ambiguous-name leg.
    """
    if not RUN.exists():
        pytest.skip(f"{RUN} has not been generated in this tree")

    import tempfile

    from tools.generate_customers_json import generate

    with tempfile.TemporaryDirectory() as tmp:
        out = pathlib.Path(tmp) / "customers.json"
        generate(RUN, out)
        data = json.loads(out.read_text())

    legs = [leg for c in data.get("customers", []) for leg in (c.get("legs") or {}).values()]
    assert len(legs) >= 10, (
        f"only {len(legs)} legs generated from {RUN}. A scan with no subjects is not a pass — "
        "either the generator changed shape or the run output is empty."
    )
    return legs


def test_no_published_rate_carries_the_name_that_could_mean_either(legs):
    """The ambiguous name is gone, and it must not come back under a new reader.

    MUTATION: re-add `avg_rate_gbp_per_mwh` to `generate_customers_json` and this fires.
    """
    offenders = sorted({k for leg in legs for k in leg if k == _AMBIGUOUS})
    # THE LIVE ARTEFACT IS DELIBERATELY NOT ASSERTED ON, and the reason is a defect found while
    # writing this: `site/data/customers.json` on `origin/main` publishes **251 legs** while
    # `docs/reports/run_output_latest.json` in the same commit holds **19 accounts and 1,600
    # bills**. The published surface is derived from a run artefact that is not in the tree.
    #
    # A leg asserting on that file would be asserting across two different populations -- exactly
    # the defect this whole module exists to stop -- and would go red or green according to when
    # the publisher last ran rather than according to whether the code is right. The GENERATOR is
    # the subject; the artefact is regenerated on every publish. The inconsistency itself is filed
    # separately, because it is a finding about the publish path and not about these rates.
    assert offenders == [], (
        f"{_AMBIGUOUS} is published again. A GBP/MWh on a bill is either the commodity leg or the "
        "effective rate and they differ by 1.5x; a field that does not say which will be read as "
        "whichever the reader needed — which is how the value-based pricing arm came to price "
        "against two thirds of the real price."
    )


def test_the_effective_rate_exceeds_the_commodity_leg_on_every_account(legs):
    """THE PROPERTY, not today's numbers: the whole bill is more than one of its terms.

    Keyed this way on purpose. A control pinned to 122.76 and 206.65 would go red the moment the
    world's prices moved and stay green if the two fields were swapped — exactly backwards. Every
    account pays network charges, levies, a standing charge and VAT on top of commodity, so
    effective > commodity is true of every bill in every year, whatever the prices are.
    """
    priced = [leg for leg in legs
              if leg.get("avg_commodity_rate_gbp_per_mwh") and leg.get("avg_effective_rate_gbp_per_mwh")]
    assert len(priced) >= 10, f"only {len(priced)} legs carry both rates"

    wrong = [
        (leg["cid"], leg["avg_commodity_rate_gbp_per_mwh"], leg["avg_effective_rate_gbp_per_mwh"])
        for leg in priced
        if leg["avg_effective_rate_gbp_per_mwh"] <= leg["avg_commodity_rate_gbp_per_mwh"]
    ]
    assert wrong == [], (
        "these accounts publish an effective rate at or below their commodity leg, which cannot "
        f"happen while non-commodity, standing charge and VAT are all positive: {wrong[:5]}"
    )


def test_the_effective_rate_is_the_whole_bill_over_the_volume_those_bills_covered(legs):
    """Recomputed from the run output rather than trusting the generator's own arithmetic.

    This is the leg that would catch the effective rate quietly becoming something else —
    commodity plus VAT, say, or a mean of per-bill rates instead of a volume weighting. The
    denominator matters as much as the numerator: a mean over bills weights a 300 kWh month the
    same as a 3,000 kWh one, and that is a different quantity wearing the same name.
    """
    if not RUN.exists():
        pytest.skip("no run output in this tree")
    bills = json.loads(RUN.read_text()).get("bills", [])
    assert len(bills) >= 500, f"population floor: only {len(bills)} bills in the run output"

    expected: dict[str, list[float]] = {}
    for bill in bills:
        if bill.get("catchup_applied"):
            continue
        acc = expected.setdefault(bill["customer_id"], [0.0, 0.0])
        acc[0] += bill.get("total_amount_gbp", 0) or 0
        acc[1] += bill.get("total_consumption_kwh", 0) or 0

    checked = 0
    for leg in legs:
        want = expected.get(leg.get("cid"))
        if not want or want[1] <= 0:
            continue
        assert leg["avg_effective_rate_gbp_per_mwh"] == pytest.approx(
            want[0] / (want[1] / 1000), abs=0.01
        ), f"{leg['cid']}: the published effective rate is not total money over total volume"
        checked += 1
    # RELATIVE, not a magic number: the control must have reconciled essentially the whole
    # published population, whatever size that population is.
    assert checked >= max(10, int(0.9 * len(legs))), (
        f"only {checked} of {len(legs)} legs could be reconciled against the run output")


def test_the_excluded_catchup_bills_are_declared_and_the_exclusion_is_real(legs):
    """A rate published without saying what it left out is the shape this whole change fixes.

    Two things, and the second is what stops the exclusion becoming a comforting no-op: the count
    is published per leg, AND it is non-zero across the book. If catch-up bills stopped being
    marked, this leg goes red rather than silently reporting a clean exclusion of nothing —
    which is the ratchet-with-no-floor failure this repo has shipped before.
    """
    for leg in legs:
        assert "effective_rate_bills_excluded" in leg, (
            f"{leg.get('cid')} publishes an effective rate with no declared denominator"
        )
    total_excluded = sum(leg["effective_rate_bills_excluded"] for leg in legs)
    assert total_excluded > 0, (
        "no bill anywhere in the book was excluded from the effective rate. Either catch-up bills "
        "have stopped being flagged, or the exclusion has stopped being applied — and both of "
        "those publish a rate whose money and volume count different periods."
    )


def test_the_pricing_arm_prices_against_what_the_customer_actually_pays():
    """Keyed to the SEAT of the defect: the reader, not the field.

    The generator could publish both rates perfectly and the pricing arm could carry on reading
    the commodity one — which is precisely the state this repo was in, with a correctly computed
    field and a caller quietly using it as the price. So this asserts what `compare` actually
    picks up, by feeding it a leg where the two rates are far apart and watching which it takes.
    """
    from tools import couple_value_based_pricing as cvp

    book = {"customers": [{"legs": {"electricity": {
        "cid": "TEST-1", "total_kwh": 48000.0, "bill_count": 12,
        "avg_commodity_rate_gbp_per_mwh": 100.0,
        "avg_effective_rate_gbp_per_mwh": 250.0,
    }}}]}
    run = {"per_customer_lifetime": {"TEST-1": {
        "segment": "domestic", "acquisition_date": "2020-01-01", "cost_to_serve_gbp": 120.0,
    }}}

    # WATCH WHAT IS PASSED TO THE DECISION, not what comes out of it. `compare`'s per-account
    # record does not republish `current_rate_gbp_per_mwh`, so the only place the choice is
    # observable is the argument -- which is also the right subject: the defect was that the wrong
    # number reached `decide_margin`, whatever the report said afterwards.
    seen: list[float] = []
    real_decide = cvp.decide_margin

    def _spy(**kwargs):
        seen.append(kwargs["current_rate_gbp_per_mwh"])
        return real_decide(**kwargs)

    monkeypatch = pytest.MonkeyPatch()
    monkeypatch.setattr(cvp, "decide_margin", _spy)
    try:
        cvp.compare(run, book)
    finally:
        monkeypatch.undo()

    assert seen, "the pricing arm priced no account at all, so this asserts nothing"
    assert seen[0] == pytest.approx(250.0), (
        "the pricing arm is anchored on the commodity leg again. `base_rate = current_rate - "
        "TARGET_MARGIN` on a rate that is not the price makes every comparison below it wrong by "
        "the difference — measured at 1.53x across the book when this was found."
    )
