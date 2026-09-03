"""Work items 4 and 5: the comparison that files every difference, and the run that needs nobody.

WHAT THE FIRST FULL RUN FOUND, AND IT FOUND THE VALIDATOR. 310 differences over 11,549 bills, every
one exactly one penny. Fifteen of them were on the two reconstructible money lines and **fifteen out
of fifteen were in the biller's favour** — a one-sidedness that reads like a systematic overcharge
and was nothing of the kind. Every instance sat on an exact half-penny, where Python's builtin
`round()` applies BANKER'S rounding and goes to the even penny while `saas/money.quantize_gbp`
declares ROUND_HALF_UP and says why. The validator was wrong.

Then repairing it exposed two more layers, each found only by re-running:

  * `8303.3 - 8090.8` is exactly 212.5 kWh in decimal and 212.4999999999991 in binary float, so the
    energy line came out at GBP 40.544999999999824 instead of exactly GBP 40.545 — a hair BELOW the
    boundary, rounding down, one penny out. **Fixing the rounding did not fix this; the subtraction
    had already lost it.**
  * and fixing the subtraction moved a SECOND bill from agreeing-by-luck to disagreeing, because
    `212.5 * 19.08 / 100` in float is 40.544999999999995 — the multiply reintroduced the same error
    the subtraction had just stopped making. A decimal quantity times a decimal rate has to stay
    decimal all the way to the quantize.

Three separate float-boundary defects, in a reconstruction whose arithmetic was correct throughout,
found by comparing it to a second implementation. That is the brief's whole argument, demonstrated
on the brief's own validator: *"each piece is locally plausible and the whole quietly stops adding
up."*

WHAT SURVIVES, AND IT IS NOT SMOOTHED AWAY. 295 VAT differences remain, all exactly one penny, net
GBP -1.33 across the book. The obvious explanation — the validator computes VAT on the base of
ROUNDED printed lines while the biller computes it upstream on unrounded components — was TESTED
and accounts for only **137 of 295**. It is therefore recorded as a candidate and not as the cause,
and the experiment cannot be pushed further from here: two of the three base components can be had
unrounded, and the third is the bundled network-and-policy line that nothing can reconstruct. The
uncheckable line does not merely block rebuilding VAT; it blocks diagnosing a VAT difference.
"""
from __future__ import annotations

import json
from decimal import Decimal

import pytest

from tools import bill_validation_comparison as cmp
from tools import independent_bill_validator as validator

# --------------------------------------------------------------------------- #
# §4.3 — the validator does not see the statement until it has rebuilt         #
# --------------------------------------------------------------------------- #

def test_the_STATEMENT_is_not_reached_until_the_reconstruction_EXISTS():
    """The property that makes the whole exercise worth anything, enforced rather than asserted.

    `statement_of` is a CALLABLE, so `compare_account` decides when the statement comes into
    existence. Here it raises if it is reached before the reconstruction has been produced — so an
    implementation that fetched the statement first, or in parallel, or "just to size the loop",
    fails here rather than being caught by a reviewer.

    MUTATION (must fire): move the `statement_of(...)` call above `reconstruct(...)`.
    """
    order: list[str] = []

    def reconstruct(raw):
        order.append("rebuild")
        return {"customer_id": raw.get("customer_id"), "periods": [], "curtain": "test"}

    def statement_of(customer_id, record):
        if "rebuild" not in order:
            raise AssertionError("the statement was reached before the reconstruction existed")
        order.append("statement")
        return {"issued_bills": [], "customer_id": customer_id}

    out = cmp.compare_account(
        "acct", {"segment": "resi", "invoices": []},
        raw_of=lambda cid, rec: {"customer_id": cid, "segment": "resi", "periods": []},
        reconstruct=reconstruct, statement_of=statement_of)

    assert order == ["rebuild", "statement"]
    assert out["reconstruction_digest"] and out["statement_digest"]
    assert out["reconstruction_digest"] != out["statement_digest"]


def test_the_reconstruction_DIGEST_is_taken_before_the_statement_exists():
    """§4.3 is unfalsifiable after the fact unless something is recorded at the time. The digest is
    that record: a reconstruction produced after the statement was opened cannot be presented as
    one produced before, because its digest would have had to be written before it existed."""
    import inspect

    source = " ".join(inspect.getsource(cmp.compare_account).split())
    rebuild_at = source.index("reconstruction_digest = hashlib")
    statement_at = source.index("statement = statement_of(")

    assert rebuild_at < statement_at, (
        "the digest must be taken before the statement is fetched, or it records nothing"
    )


# --------------------------------------------------------------------------- #
# §4.4 — every difference is filed, none is smoothed, the validator wins       #
# --------------------------------------------------------------------------- #

def _bill(**over):
    bill = {"invoice_number": 1, "period_start": "2020-01-01", "period_end": "2020-01-31",
            "total_amount_gbp": 10.50, "parts_sum_gbp": 10.50,
            "lines": [
                {"label": "Energy", "amount_gbp": 5.00, "inputs": {"consumption_kwh": 100.0}},
                {"label": "Standing charge", "amount_gbp": 3.00, "inputs": {}},
                {"label": "Network and policy costs", "amount_gbp": 2.00, "inputs": {}},
                {"label": "VAT", "amount_gbp": 0.50, "inputs": {}},
            ]}
    bill.update(over)
    return bill


def _rebuilt(energy=5.00, standing=3.00):
    return {"period_start": "2020-01-01", "period_end": "2020-01-31", "lines": [
        {"label": "Energy", "status": validator.RECONSTRUCTED, "amount_gbp": energy, "how": "x"},
        {"label": "Standing charge", "status": validator.RECONSTRUCTED, "amount_gbp": standing},
        {"label": "Network and policy costs", "status": validator.UNCHECKABLE, "why": "no rate"},
    ]}


def _verdict(claims, name):
    return next(c["verdict"] for c in claims if c["claim"] == name)


def test_a_ONE_PENNY_difference_is_FILED_and_not_forgiven():
    """The whole book's 295 surviving differences are a penny each. A comparison with a tolerance
    wide enough to absorb them would report "the arithmetic agrees", which is not true — "295 bills
    disagree by a penny" and "the arithmetic agrees" are different statements.

    MUTATION (must fire): widen `PENNY` to 0.02, or round both sides before comparing.
    """
    claims = cmp.compare_bill(_rebuilt(energy=5.00), _bill(), statutory_vat={"rate": 0.05},
                              read_volume_kwh=100.0)
    assert _verdict(claims, "energy_gbp") == cmp.AGREED

    claims = cmp.compare_bill(_rebuilt(energy=5.01), _bill(), statutory_vat={"rate": 0.05},
                              read_volume_kwh=100.0)
    assert _verdict(claims, "energy_gbp") == cmp.DISAGREED
    energy = next(c for c in claims if c["claim"] == "energy_gbp")
    assert energy["difference"] == -0.01
    assert energy["authority"] == "validator"


def test_UNCHECKABLE_is_never_counted_as_AGREEMENT():
    """A comparison that returned only mismatches would report "no differences" over a bill it
    barely read. Half of every bill here is genuinely unverifiable, and that belongs in the output
    as its own verdict rather than as silence.

    MUTATION (must fire): skip the uncheckable claims instead of emitting them.
    """
    claims = cmp.compare_bill(_rebuilt(), _bill(), statutory_vat={"rate": None, "why": "no rate"},
                              read_volume_kwh=None)
    kinds = {c["claim"]: c["verdict"] for c in claims}

    assert kinds["network_and_policy_gbp"] == cmp.UNCHECKABLE
    assert kinds["volume_kwh"] == cmp.UNCHECKABLE
    assert kinds["vat_gbp"] == cmp.UNCHECKABLE
    assert cmp.AGREED not in (kinds["network_and_policy_gbp"], kinds["vat_gbp"])


def test_the_BILLERS_OWN_IDENTITY_is_checked_and_the_validator_supplies_no_term():
    """A bill whose printed parts do not reach its own total is wrong whatever any reconstruction
    says. This is the one claim where the validator is not the authority on the arithmetic — only
    on the fact that it must hold."""
    claims = cmp.compare_bill(_rebuilt(), _bill(total_amount_gbp=11.00),
                              statutory_vat={"rate": 0.05}, read_volume_kwh=100.0)

    assert _verdict(claims, "bill_total_gbp") == cmp.DISAGREED


def test_a_MISALIGNED_PERIOD_stops_the_comparison_and_says_why():
    """Both sides are built from the same invoice list in the same order, so a mismatch here is
    structurally impossible — which is exactly the sort of thing that turns out to be wrong once a
    re-issue lands. Every other claim on the bill would be comparing two different things.

    MUTATION (must fire): drop the alignment check and compare anyway.
    """
    claims = cmp.compare_bill(_rebuilt(), _bill(period_end="2020-02-29"),
                              statutory_vat={"rate": 0.05}, read_volume_kwh=100.0)

    assert [c["claim"] for c in claims] == ["period_alignment"]
    assert claims[0]["verdict"] == cmp.DISAGREED


def test_a_BILL_WITH_NO_RECONSTRUCTION_and_a_period_with_no_bill_are_BOTH_filed():
    """Coverage in both directions. A statement bill the export cannot support is a gap in the
    export; an exported period we never billed is a missing bill. Both are ours, and a comparison
    that only zipped the shorter list would report neither."""
    raw = {"customer_id": "a", "segment": "resi", "periods": []}
    more_bills = cmp.compare_account(
        "a", {}, raw_of=lambda c, r: raw,
        reconstruct=lambda r: {"periods": [], "curtain": "t"},
        statement_of=lambda c, r: {"issued_bills": [_bill()], "customer_id": c})
    assert any(d["claim"] == "reconstruction_exists" for d in more_bills["differences"])

    more_periods = cmp.compare_account(
        "a", {}, raw_of=lambda c, r: raw,
        reconstruct=lambda r: {"periods": [_rebuilt()], "curtain": "t"},
        statement_of=lambda c, r: {"issued_bills": [], "customer_id": c})
    assert any(d["claim"] == "bill_exists" for d in more_periods["differences"])


# --------------------------------------------------------------------------- #
# The three float defects the comparison found in the validator                #
# --------------------------------------------------------------------------- #

@pytest.mark.parametrize("value, half_up, bankers", [
    (38.735, 38.74, 38.73),
    (11.625, 11.63, 11.62),
    (2.855, 2.86, 2.85),
])
def test_money_rounds_HALF_UP_and_not_to_the_EVEN_penny(value, half_up, bankers):
    """15 of 15 differences on the reconstructible lines were in the biller's favour, which reads
    like a systematic overcharge and was banker's rounding.

    MUTATION (must fire): use the builtin `round(value, 2)`.
    """
    assert validator.round_money(value) == half_up
    assert round(value, 2) == bankers, "the builtin is what this exists to not be"


def test_a_decimal_quantity_is_read_as_the_number_a_human_sees():
    """`Decimal(0.1)` is 0.1000000000000000055...; `Decimal("0.1")` is 0.1. A meter reading is a
    decimal printed on a bill, so `str()` is the faithful reading."""
    assert validator._dec(0.1) == Decimal("0.1")
    assert validator._dec(0.1) != Decimal(0.1)


def test_the_VOLUME_is_subtracted_in_DECIMAL_so_an_exact_reading_stays_exact():
    """`8303.3 - 8090.8` is 212.5 exactly, and 212.4999999999991 in binary float. One bill in
    11,549 was a penny out for that reason and no other.

    MUTATION (must fire): subtract the two floats directly.
    """
    period = {"volume_basis": "reads",
              "reads": [{"read_kwh": 8090.8}, {"read_kwh": 8303.3}]}

    volume, why = validator._volume_from_reads(period)

    assert why == ""
    assert volume == 212.5
    assert (8303.3 - 8090.8) != 212.5, "the float path is what this exists to not be"


def test_the_MONEY_stays_decimal_through_the_MULTIPLY_and_not_only_the_subtraction():
    """Repairing the subtraction alone moved a SECOND bill from agreeing-by-luck to disagreeing:
    `212.5 * 19.08 / 100` in float is 40.544999999999995, so the multiply reintroduced exactly the
    error the subtraction had stopped making.

    MUTATION (must fire): compute the energy amount as `volume * rate_p / 100.0`.
    """
    period = {"volume_basis": "reads", "commodity": "electricity",
              "reads": [{"read_kwh": 8090.8}, {"read_kwh": 8303.3}],
              "unit_rate_p_per_kwh": 19.08, "days_in_period": 31,
              "standing_charge_gbp_per_day": 0.24,
              "period_start": "2020-01-01", "period_end": "2020-01-31"}

    rebuilt = validator.rebuild_period(period, segment="resi")
    energy = next(ln for ln in rebuilt["lines"] if ln["label"] == "Energy")

    assert energy["amount_gbp"] == 40.55
    assert float(212.5 * 19.08 / 100.0) != 40.545, "the float path is what this exists to not be"


def test_the_ROUNDING_CONVENTION_is_DECLARED_as_ours_and_not_claimed_as_published():
    """It is the one input to the reconstruction that is a convention rather than a fetched rule.
    Saying so is the difference between an honest reconstruction and one that implies a legal
    basis it does not have."""
    assert "HALF_UP" in validator.ROUNDING
    assert "NOT READ FROM A PUBLISHED RECORD" in validator.ROUNDING_SOURCE


def test_the_CURTAIN_still_holds_after_the_decimal_repair():
    """`decimal` is stdlib, but the repair was a chance to reach for `saas.money`, which has
    exactly this function. Importing it would have made the two sides agree on every boundary by
    construction — the tautology the curtain exists to prevent."""
    assert validator.imports_into_the_repository() == []
    validator.assert_curtain()


# --------------------------------------------------------------------------- #
# §4.5 and §4.6 — every account every run, with provenance                     #
# --------------------------------------------------------------------------- #

def test_a_FULL_RUN_covers_every_account_in_the_ledger():
    """MUTATION (must fire): sample, or cap, the account list on the normal path."""
    report = cmp.compare_all()

    assert report["accounts_compared"] == report["accounts_in_ledger"] > 0
    assert report["truncated"] is None
    assert report["bills_compared"] > 0


def test_a_LIMITED_run_SAYS_SO_so_it_cannot_be_read_as_a_full_one():
    """`--limit` exists for tests. A truncated run that looked like a full one is how a coverage
    figure becomes a lie nobody told."""
    report = cmp.compare_all(limit=2)

    assert report["accounts_compared"] == 2
    assert "not a full run" in report["truncated"]
    assert "LIMITED TO 2" in cmp.render(report)


def test_AGREEMENT_carries_the_same_provenance_as_any_published_figure():
    """§4.6, and it is about agreement specifically: a disagreement is self-evidently a claim, and
    an agreement with no clock is a claim about a tree nobody can name."""
    report = cmp.compare_all(limit=1)

    assert report["run_id"].startswith("billval-")
    assert report["commit"] and report["generated_at"]
    assert report["counts"][cmp.AGREED] > 0
    assert report["commit"] in report["run_id"] or report["commit"][:9] in report["run_id"]


# --------------------------------------------------------------------------- #
# §4.5 — it needs nobody present                                               #
# --------------------------------------------------------------------------- #

def test_the_RUNNER_pages_on_a_DELTA_and_never_on_a_cycle():
    """A runner that pages every hour is a heartbeat, and a heartbeat is what gets muted.

    MUTATION (must fire): notify whenever `DISAGREED` is non-zero.
    """
    report = {"counts": {cmp.DISAGREED: 295}, "differences_by_claim": {"vat_gbp": 295},
              "accounts_compared": 251, "differences": []}

    assert cmp.delta_against(report, report) == []
    assert cmp.delta_against(None, report) == []


@pytest.mark.parametrize("changed, needle", [
    ({"counts": {cmp.DISAGREED: 294}}, "disagreements"),
    ({"differences_by_claim": {"vat_gbp": 294, "energy_gbp": 1}}, "claim mix"),
    ({"accounts_compared": 250}, "accounts compared"),
])
def test_a_DROP_is_as_loud_as_a_RISE(changed, needle):
    """A silent drop is how a control gets quietly disarmed — the disagreement count falling
    because the comparison stopped looking reads identically to it falling because the biller was
    fixed, and only one of those is good news."""
    base = {"counts": {cmp.DISAGREED: 295}, "differences_by_claim": {"vat_gbp": 295},
            "accounts_compared": 251, "differences": []}
    now = {**base, **changed}

    notes = cmp.delta_against(base, now)

    assert any(needle in n for n in notes), notes


def test_a_difference_LARGER_THAN_A_PENNY_pages_on_its_FIRST_occurrence():
    """Every difference on record is exactly 1p. The first one that is not is the defect this
    programme was built to find, and waiting for a count to move would be waiting for a second."""
    report = {"counts": {cmp.DISAGREED: 1}, "differences_by_claim": {"energy_gbp": 1},
              "accounts_compared": 251,
              "differences": [{"claim": "energy_gbp", "difference": -4.20, "customer_id": "C1",
                               "invoice_number": 7, "validator_says": 40.0, "biller_says": 35.8}]}

    notes = cmp.delta_against(report, report)

    assert notes and "LARGER THAN A PENNY" in notes[0]


def test_the_SCHEDULE_is_declared_so_an_unarmed_timer_is_LOUD():
    """Item 5 is not "a tool exists". A validator that runs once is a demonstration and one that
    runs every cycle is a control, and the difference is entirely whether the timer is armed —
    which `schedule_reconciler` can only report on units this manifest declares.

    MUTATION (must fire): ship the units without declaring them; the reconciler then reports
    UNDECLARED_UNIT, which is the drift it exists to catch.
    """
    from background.schedule_reconciler import load_manifest

    declared = {u["name"]: u for u in load_manifest()["systemd_units"]}

    assert "bill-validation.timer" in declared
    assert declared["bill-validation.timer"]["enabled"] is True
    assert declared["bill-validation.timer"]["active"] is True, (
        "a timer that is enabled but never started is fail-silent (R15)"
    )
    assert declared["bill-validation.service"]["active"] is False, (
        "a oneshot is inactive between firings; flagging it down would be wrong"
    )


def test_the_SERVICE_runs_the_WHOLE_BOOK_with_no_coverage_dial():
    """A validator with a `--limit` on its scheduled path is one whose coverage becomes a decision
    somebody makes under time pressure, and the slow part is always what gets dialled down."""
    from pathlib import Path

    unit = Path(cmp.PROJECT_DIR / "background" / "bill-validation.service").read_text()
    exec_line = next(ln for ln in unit.splitlines() if ln.startswith("ExecStart="))

    assert "tools.bill_validation_comparison" in exec_line
    assert "--limit" not in exec_line
    assert "--notify" in exec_line


def test_the_committed_REPORT_is_a_full_run_and_not_a_sample():
    """The artefact a reader finds in the tree must be the whole book. A committed report from a
    `--limit` run would be a coverage claim nobody made on purpose."""
    report = json.loads(cmp.REPORT_PATH.read_text(encoding="utf-8"))

    assert report["truncated"] is None
    assert report["accounts_compared"] == report["accounts_in_ledger"]
    assert report["counts"][cmp.UNCHECKABLE] > 0, (
        "a report claiming nothing was uncheckable would mean the network and policy line had "
        "become reconstructible, which would be news"
    )
