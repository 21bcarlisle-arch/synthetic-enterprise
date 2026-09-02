"""THE DEFECT THIS CONTROL EXISTS TO CATCH: a customer's standing direct debit
being opened from their FIRST ISSUED BILL.

Until 2026-09-02 both ``company/billing/dd_review_runner.py`` and
``simulation/dd_balance_book.py`` did exactly that -- ``standing = seq[0][1]``,
commented "initial estimate = first issued bill" -- which makes the monthly
payment an accident of which month the account happened to open in. The
director's correction of 2026-09-01: *"There's no such thing as a half-month
direct debit -- an annualised plan divides estimated annual cost by twelve
whatever the start date."*

**KEYED TO THE PROPERTY, NOT TO TODAY'S ANSWER.** These tests do not pin the
current opening figure, the current review count, or the current estimator. They
assert the structural property that survives any future change to how the
estimate is made: *the opening standing DD tracks the supplied opening amount and
is independent of the first bill.* A control pinned to a current value goes red
when the code becomes more honest and green when the claim rots.

The discriminating construction is a pair of portfolios **identical except for
the first bill's amount**. If the opening DD is taken from the first bill, the
two disagree. If it comes from a supplied estimate, they are identical. That
pair is what makes the test unable to pass for the wrong reason: it cannot be
satisfied by the estimate merely *existing*, only by the first bill not being
read.

MUTATION-PROVEN under ``python3 -B`` (never a stale .pyc): restoring
``standing_dd = seq[0][1]`` in ``run_annual_reviews`` turns
``test_the_opening_dd_is_independent_of_the_first_bill_amount`` and
``test_a_customer_with_no_opening_estimate_is_refused_not_invented`` red.
"""
from __future__ import annotations

import pytest

from company.billing.dd_review_runner import run_annual_reviews


def _bills(cid: str, monthly_amounts: list[float], start=(2020, 1)) -> list[dict]:
    out = []
    y, m = start
    for amt in monthly_amounts:
        out.append(
            {
                "customer_id": cid,
                "period_end": f"{y:04d}-{m:02d}-28",
                "total_amount_gbp": amt,
            }
        )
        m += 1
        if m > 12:
            m, y = 1, y + 1
    return out


def test_the_opening_dd_is_independent_of_the_first_bill_amount():
    """Two portfolios differing ONLY in the first bill must review identically.

    This is the whole defect in one assertion. Under the old code the standing
    DD was the first bill, so a £20 opening bill and a £500 opening bill
    produced completely different variances, actions and shock flags from the
    same year of spending.
    """
    # The two arms bill the SAME AMOUNTS over the year -- the first two months
    # are merely swapped -- so the year's actual spend (£1,200) is identical and
    # the ONLY difference is which amount landed first. Any divergence between
    # the arms is therefore attributable to the first bill and nothing else.
    swapped_tail = [100.0] * 10 + [100.0]  # 11 more bills; the 13th closes the year
    cheap_first = _bills("C1", [20.0, 180.0] + swapped_tail)
    dear_first = _bills("C1", [180.0, 20.0] + swapped_tail)

    cheap = run_annual_reviews(cheap_first, opening_dd_gbp={"C1": 100.0})
    dear = run_annual_reviews(dear_first, opening_dd_gbp={"C1": 100.0})

    assert cheap.events, "expected a completed-year review in both arms"
    assert len(cheap.events) == len(dear.events)

    cheap_ev, dear_ev = cheap.events[0], dear.events[0]
    # Same year of spending, so every reviewed quantity must agree.
    assert cheap_ev.actual_annual_spend_gbp == dear_ev.actual_annual_spend_gbp
    # The standing DD entering the review is the SUPPLIED amount in both arms...
    assert cheap_ev.current_dd_gbp == 100.0
    assert dear_ev.current_dd_gbp == 100.0
    # ...and therefore so are the variance and the action.
    assert cheap_ev.variance_pct == dear_ev.variance_pct
    assert cheap_ev.action == dear_ev.action
    # Under the defect this control exists to catch, these arms diverged wildly:
    # standing £20 implied £240 against £1,200 actual (a +400% INCREASE) versus
    # standing £180 implied £2,160 (a -44% DECREASE) -- from identical spending.


def test_the_opening_dd_tracks_the_supplied_estimate():
    """Move the estimate, and the standing DD moves with it -- the PASS branch
    is reachable and the control is not a constant verdict."""
    bills = _bills("C1", [100.0] * 13)
    for opening in (40.0, 100.0, 250.0):
        result = run_annual_reviews(bills, opening_dd_gbp={"C1": opening})
        assert result.events[0].current_dd_gbp == opening


def test_a_customer_with_no_opening_estimate_is_refused_not_invented():
    """No estimate must mean NO review and a counted refusal -- never a silent
    fallback to the first bill.

    This is the leg that catches the naive repair. A future edit that
    "helpfully" restores ``or seq[0][1]`` when the mapping misses a customer
    reinstates the exact fail-open this work removed, and it would pass every
    other test in this file.
    """
    bills = _bills("C1", [100.0] * 13)

    missing = run_annual_reviews(bills, opening_dd_gbp={})
    assert missing.events == []
    assert missing.summary()["total_reviews"] == 0
    assert missing.summary()["unestimated_customers"] == 1
    assert "C1" in missing.unestimated_customers

    # Not supplying the mapping at all is the same refusal, not a licence to guess.
    none_at_all = run_annual_reviews(bills)
    assert none_at_all.events == []
    assert none_at_all.summary()["unestimated_customers"] == 1


@pytest.mark.parametrize("bad_opening", [0.0, -12.0])
def test_a_nonpositive_opening_is_a_refusal_not_a_zero_direct_debit(bad_opening):
    """A zero or negative opening is a missing field, not a household that pays
    nothing. Letting it through would publish a measured zero for an
    unobservable cause, and would also divide by a zero implied annual."""
    result = run_annual_reviews(
        _bills("C1", [100.0] * 13), opening_dd_gbp={"C1": bad_opening}
    )
    assert result.events == []
    assert result.summary()["unestimated_customers"] == 1


def test_the_refusal_count_reaches_the_serialised_surface():
    """A fail-closed verdict composed into an artefact no surface reads is not a
    control. The refusal count must survive serialisation."""
    result = run_annual_reviews(_bills("C1", [100.0] * 13), opening_dd_gbp={})
    assert result.serialise()["summary"]["unestimated_customers"] == 1


def test_the_first_bill_is_not_read_as_an_estimate_anywhere_in_the_dd_path():
    """The source-level half: neither module may reopen the artefact.

    A behavioural test can be satisfied by a caller that happens to pass the
    first bill in as the "estimate". This leg names the shape itself. It is
    deliberately narrow -- it looks for the specific first-element-of-the-bill-
    sequence read that both modules carried -- so it cannot go red for an
    unrelated edit.
    """
    import io
    import tokenize
    from pathlib import Path

    repo = Path(__file__).resolve().parents[3]
    for rel in (
        "company/billing/dd_review_runner.py",
        "simulation/dd_balance_book.py",
    ):
        src = (repo / rel).read_text()

        # TOKENISED, not grepped. Both modules now DOCUMENT the removed defect
        # by name, and a plain text search cannot tell the fix's own account of
        # itself from the defect coming back -- it would go red for the comment
        # that explains why it is green. Dropping STRING and COMMENT tokens
        # leaves only code.
        code = []
        for tok in tokenize.generate_tokens(io.StringIO(src).readline):
            if tok.type in (tokenize.STRING, tokenize.COMMENT):
                continue
            code.append((tok.string, tok.start[0]))

        # `seq[0][1]` is the first issued bill's AMOUNT. Reading `seq[0][0]`
        # (the first bill's DATE, the legitimate 12-month anniversary anchor)
        # stays allowed -- the anniversary genuinely does start at the first
        # bill. So the pattern sought is the subscript chain ending in [1].
        offending = []
        for i in range(len(code) - 6):
            window = [t for t, _ in code[i : i + 7]]
            if window == ["seq", "[", "0", "]", "[", "1", "]"]:
                offending.append(code[i][1])

        assert not offending, (
            f"{rel} reads the first issued bill's amount (seq[0][1]) as a "
            f"standing DD again, at line(s) {offending}"
        )
