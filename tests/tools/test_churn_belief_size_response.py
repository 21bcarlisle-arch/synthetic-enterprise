"""Controls on the size dimension of the company's churn belief — `tools/churn_belief_size_response.py`.

The defect this file was written for is
`SEAT_RESULT_THE_COMPANYS_CHURN_BELIEF_IS_FLAT_IN_THE_DIMENSION_THE_WORLD_RESPONDS_TO_2026-09-22.md`:
`estimate_churn_probability` reads `annual_consumption_kwh` in exactly one place, a bill-stress
hinge that is identically zero below GBP 3,000 of previous annual bill, so the belief's derivative
with respect to household size is exactly zero across almost the whole book — while the world's
`churn_position_multiplier` scales by each household's OWN annual spend and spans an order of
magnitude over those same accounts.

WHY ONE CONTROL OVER THE WHOLE PARTITION AND NOT A LEG PER CLAIM. The claim being published is
"the belief is flat here". An instrument that returns a constant for EVERY input satisfies that
claim at every point and would pass any number of individually-correct flatness legs — this
project's most expensive recurring shape, entered three times in one afternoon through three
different doors. So the partition is asserted in one function: flat below the knee, MOVING above
it, the world varying below it where the belief does not, and the world flat above it for the one
segment where the belief varies. A guard that reports "flat" for everything fails the second leg;
a guard that reports "varies" for everything fails the first; an instrument that has stopped
reading the world at all fails the third.

MUTATION RECORD (2026-09-22), per `docs/design/CONTROLS_THAT_CANNOT_FAIL.md`. Each mutation was
applied to an INJECTED copy of the subject module, never to the shared tree, and an unmutated
baseline run is recorded first so a leg that fires on everything would be visible:

  * baseline, no mutation — SILENT. Nothing fires without a mutation.
  * `BILL_STRESS_SENSITIVITY = 0.25 -> 0.0` — CAUGHT by
    `test_the_belief_is_flat_in_size_exactly_where_the_world_is_not` (leg 3) and by
    `test_the_knee_is_a_bill_and_not_a_consumption`. The belief goes flat at every consumption,
    so the partition collapses AND `knee_kwh` correctly returns None at every rate.
  * `BILL_STRESS_THRESHOLD_GBP = 3000.0 -> 500.0` — CAUGHT by
    `test_the_belief_is_flat_in_size_exactly_where_the_world_is_not` (leg 1) alone. The knee drops
    below the probe pair and the two domestic households stop agreeing. The knee control does NOT
    fire, and correctly so: a knee at GBP 500 is still a bill and still moves in kWh with rate.
  * `max(0.0, ...) -> abs(...)` in `churn_model`'s bill-stress line — CAUGHT by
    `test_the_belief_is_flat_in_size_exactly_where_the_world_is_not` (leg 1) and by
    `test_the_knee_is_a_bill_and_not_a_consumption`. A two-sided hinge makes the belief vary below
    the knee, and leaves no flat arm for the bisection to find.
  * `bill_scale_for` non-domestic branch `None -> bill_gbp` — CAUGHT by
    `test_the_belief_is_flat_in_size_exactly_where_the_world_is_not` (leg 4). This is the leg that
    stops the mirror claim being asserted about a world that no longer has the asymmetry.
  * `PROBE_DIFFERENTIAL_PCT = 0.12 -> 0.30` — SILENT, and it is an EQUIVALENCE, not a missing leg.
    Every world leg here is a strict comparison BETWEEN two bills at ONE differential, and
    `churn_position_multiplier` is monotone in the bill at any positive differential, so the
    ordering asserted is invariant to where the probe sits. Recorded rather than patched: pinning
    the probe position would key the control to today's answer instead of to the property, which
    is the failure mode named in CLAUDE.md.
  * `_KNEE_TOLERANCE_KWH = 1.0 -> 100.0` — SILENT, and it is an EQUIVALENCE for these legs: the
    knee control asserts the derived knee is a BILL (one figure across three rates, to within GBP
    10) and a coarser bisection still resolves that well inside the bar. It is NOT an equivalence
    for the precision of `knee.by_rate[].knee_kwh`, which no leg here reads — so the honest
    statement is that this control does not cover the bisection's precision and does not claim to.
"""
from __future__ import annotations

import pytest

from company.crm.enriched_churn_estimate import enriched_churn_estimate
from simulation.market_switching_propensity import bill_scale_for, churn_position_multiplier
from tools import churn_belief_size_response as cb

#: The probe deck. GBP 250/MWh puts the knee at 12,000 kWh, so both "below" households are real
#: domestic sizes and the "above" one is the item's own 25,000 kWh probe.
_OLD_RATE = 250.0
_OFFER = 280.0
_SMALL_KWH = 1_500.0
_LARGE_KWH = 6_000.0
_ABOVE_KNEE_KWH = 25_000.0


def _belief(kwh: float, segment: str = "resi") -> float:
    return enriched_churn_estimate(_OLD_RATE, _OFFER, 3.0, kwh, segment=segment)


def _world(kwh: float, segment: str = "resi") -> float:
    bill = _OLD_RATE * kwh / 1000.0
    return churn_position_multiplier(cb.PROBE_DIFFERENTIAL_PCT, bill_scale_for(segment, bill))


def test_the_belief_is_flat_in_size_exactly_where_the_world_is_not():
    """The whole partition. Catches a belief that is flat everywhere AND one that varies everywhere.

    Four legs, and each one kills a different degenerate instrument:
      1. flat below the knee          -- the finding itself
      2. the world varies there       -- so the flatness is a real difference, not an equivalence
      3. the belief MOVES above it    -- so "flat" is not what this instrument says about everything
      4. the world is flat for SME    -- so the mirror claim is about a world that has the asymmetry
    """
    # 1. Two domestic households, four times apart in size, both below the knee. The company's
    #    belief cannot tell them apart -- not approximately, exactly.
    assert _belief(_SMALL_KWH) == _belief(_LARGE_KWH)

    # 2. And that is a difference the world makes, in the direction size predicts. Without this
    #    leg the flatness could be an equivalence -- two routes to one correct answer.
    assert _world(_SMALL_KWH) < _world(_LARGE_KWH)

    # 3. The belief is NOT constant in consumption at every input: above the knee it moves. An
    #    estimator that had stopped reading consumption altogether fails here, which is what stops
    #    leg 1 from being passed by a guard that reports "flat" for everything.
    assert _belief(_ABOVE_KNEE_KWH) > _belief(_LARGE_KWH)

    # 4. The mirror, and it is the sharper half of the finding: the world scales by the
    #    household's own bill for DOMESTIC supply only, so for a non-domestic account the world is
    #    flat in size by construction -- and that is the one segment where the belief does vary.
    assert _world(_SMALL_KWH, "SME") == _world(_ABOVE_KNEE_KWH, "SME")
    assert _belief(_ABOVE_KNEE_KWH, "SME") > _belief(_SMALL_KWH, "SME")


def test_the_knee_is_a_bill_and_not_a_consumption():
    """Keyed to the PROPERTY, not to 12,000 kWh — which is only the knee at GBP 250/MWh.

    A control pinned to the kWh location goes red the next time the price deck moves and stays
    green while the mechanism rots. What is durable is that the knee sits at a fixed number of
    POUNDS and therefore at a DIFFERENT number of kilowatt-hours at every rate.
    """
    derived = [cb.knee_kwh(rate) for rate in cb.PROBE_RATES_GBP_PER_MWH]
    assert all(kwh is not None for kwh in derived), "the belief never moves at any consumption"

    bills = [rate * kwh / 1000.0
             for rate, kwh in zip(cb.PROBE_RATES_GBP_PER_MWH, derived)]
    # One bill, to within the bisection's own resolution.
    assert max(bills) - min(bills) < 10.0
    # Three different consumptions. This is the leg that fails if the knee ever becomes a kWh
    # constant -- at which point the belief WOULD be a size term and this finding would be spent.
    assert len(set(round(kwh) for kwh in derived)) == len(derived)
    assert max(derived) / min(derived) > 2.0


def test_the_book_census_counts_every_leg_on_one_side_or_the_other():
    """A census whose filters empty the evidence reads as 'no complaint'. This asserts it did not.

    `share_below_the_knee` is the published figure; a census that dropped the accounts it could
    not classify would report a clean share over a population it had quietly shrunk.
    """
    import json

    book = json.loads(cb.BOOK_PATH.read_text(encoding="utf-8"))
    dist = cb.book_distribution(book, 3000.0)
    assert dist["available"]
    assert dist["supply_legs"] > 0
    assert dist["legs_above_the_knee"] + dist["legs_below_the_knee"] == dist["supply_legs"]
    # BOTH sides are populated. A book entirely below the knee would make leg 3 of the partition
    # control unreachable on real data, and saying "the belief is flat across the book" would then
    # be unfalsifiable rather than measured.
    assert dist["legs_above_the_knee"] > 0
    assert dist["legs_below_the_knee"] > 0
    # The claim the page publishes is about the MAJORITY, so the census must be able to say which.
    assert 0.0 < dist["share_below_the_knee"] <= 1.0


def test_the_reading_refuses_rather_than_reporting_an_absence():
    """A refusal that names its reason, per the standing rule. Reachable, not decorative."""
    empty = cb.book_distribution({"customers": []}, 3000.0)
    assert empty["available"] is False
    reading = cb._reading(cb.knee(), cb.partition(), empty)
    assert reading.startswith("REFUSED:")


@pytest.mark.parametrize("field", ["population_is_not_the_published_arms_book",
                                   "bill_is_an_upper_bound"])
def test_the_census_carries_what_it_could_not_establish(field):
    """The 154-account arms book is not this book, and the bill here is an upper bound.

    Both caveats are load-bearing: the first is the difference `generate_value_arms_data` already
    refuses to smooth over, and the second is what makes the below-the-knee count safe in the
    direction it is claimed.
    """
    import json

    book = json.loads(cb.BOOK_PATH.read_text(encoding="utf-8"))
    assert cb.book_distribution(book, 3000.0)[field].strip()


# ----------------------------------------------------------------------------------------------
# THE ARMS' OWN BOOK (2026-09-22, second pass)
#
# The first pass measured the tree's current 164-account book and recorded the 154-account book the
# PUBLISHED arms were scored over as NOT ESTABLISHED, on the stated ground that its per-account
# rows are not persisted. They are: `site/data/customers.json` is one row per billing account and
# git holds it at the commit the run recorded. `arms_book` reads it there.
#
# WHAT CAN GO WRONG IS NOT "THE NUMBERS ARE WRONG", IT IS "THE NUMBERS ARE ABOUT SOMEBODY ELSE".
# A commit-pinned blob is an inference about which book ran, and the whole of this second pass
# rests on turning that inference into evidence by reconciling four counts the run published about
# its own book. So the control is over the IDENTIFICATION partition, in one function: it must
# accept the real book, REFUSE a roster that disagrees on any reconciled count, refuse each broken
# link in the chain with a DISTINGUISHABLE reason, and — the fail-open leg — the published reading
# must name which of the two books it is quoting and quote that one's figures.
#
# MUTATION RECORD, injected per-call rather than into the shared tree:
#   * baseline, no mutation — SILENT.
#   * drop one account from the roster blob — CAUGHT (leg 2), naming
#     `billing_accounts_settled_in_window`.
#   * move one account's gas leg off — CAUGHT (leg 2), naming `with_a_gas_leg` and `dual_fuel`.
#   * `_BOOK_IDENTITY_COUNTS` truncated to the accounts row alone — CAUGHT (leg 2's gas mutation
#     stops being seen), which is the leg that keeps the check from shrinking to one count.
#   * `_roster_at_commit` returns None — CAUGHT (leg 3), with a reason distinct from leg 2's.
#   * `_roster_at_commit` ignores its commit and returns whatever the checkout holds — SILENT at
#     first, and that was a MISSING LEG, not an equivalence. HEAD's own committed roster is a
#     154-account book, so in a clean checkout the mutation reconciles on all four counts and
#     every published figure stays correct; in the shared tree, where the working copy has been
#     regenerated to 164 accounts, the same mutation measures the wrong population and says
#     nothing. Repaired by leg 1's "a commit that cannot exist produces nothing" pair, which pins
#     the property (the read is keyed to the commit) instead of today's agreement between two
#     books. NOW CAUGHT.
#   * the reconciliation's `if disagreed:` deleted so it publishes anyway — CAUGHT (leg 2).
#   * `_reading` quoting `dist` unconditionally while still printing "the 154-account book" —
#     CAUGHT (leg 4). This is the mutation the leg exists for: every figure stays plausible and
#     the sentence becomes a claim about a population that was never measured.
#   * `PROBE_DIFFERENTIAL_PCT` moved — SILENT here, and an EQUIVALENCE for the same reason the
#     partition control records: no leg below reads the world multiplier's LEVEL, only which book
#     it was taken over.
# ----------------------------------------------------------------------------------------------

def _run_artefact() -> dict:
    import json

    from tools.generate_value_arms_data import THREE_ARM_PATH
    return json.loads(THREE_ARM_PATH.read_text(encoding="utf-8"))


def _identity() -> dict:
    return (_run_artefact().get("book_identity") or {}).get("control_arm") or {}


def test_the_arms_book_is_identified_and_a_near_miss_is_refused(monkeypatch):
    """One control over the whole identification partition.

    Leg 1 — the real book is accepted, and it is the RUN's book: every reconciled count matches
            what the run itself published, not merely "a roster of about the right size".
    Leg 2 — a roster that disagrees on ANY reconciled count is refused, with the field named. Run
            over each count separately, because a check that has quietly shrunk to one of them
            would pass a single mutation and miss the other three.
    Leg 3 — a broken link earlier in the chain refuses for a DIFFERENT, nameable reason. A reader
            who cannot tell "git has no such blob" from "that blob is another book" is being
            handed an absence dressed as a measurement.
    Leg 4 — the published reading names which book it quotes AND quotes that book's figures. This
            is the fail-open leg: silently falling back to the 164-account book leaves every
            number plausible and the sentence about a population nobody measured.
    """
    import copy
    import json

    knee_bill = 3000.0
    identity = _identity()

    # ---- leg 1: accepted, and reconciled against the run's own counts ----------------------
    real = cb.arms_book(knee_bill)
    assert real["available"] is True, real.get("unavailable_because")
    assert real["billing_accounts"] == identity["billing_accounts_settled_in_window"]
    assert real["identified_by"]["all_four_agree"] is True
    assert len(real["identified_by"]["reconciled_counts"]) == len(cb._BOOK_IDENTITY_COUNTS)
    # The partition it exists to report is populated on BOTH sides over this book too, or the
    # published "flat for N of M" sentence would be unfalsifiable rather than measured.
    assert real["legs_above_the_knee"] > 0 and real["legs_below_the_knee"] > 0

    commit = real["identified_by"]["producing_commit"]
    blob = cb._roster_at_commit(commit)
    assert blob is not None

    # ...and the read is actually KEYED TO THE COMMIT. Asserting only that the counts reconcile
    # cannot see a reader that ignores its argument and hands back whatever the checkout holds:
    # HEAD's committed roster is itself a 154-account book, so in any clean checkout that mutation
    # reconciles perfectly and every figure stays right. Found by mutation, and it is a MISSING
    # LEG rather than an equivalence — in the shared tree, where the working copy has been
    # regenerated to 164 accounts, the same mutation measures the wrong population silently. A
    # commit that cannot exist must therefore produce nothing at all.
    assert cb._roster_at_commit("0" * 40) is None
    assert cb._roster_at_commit("not-a-commit") is None

    # ---- leg 2: disagreement on any reconciled count refuses, naming the field --------------
    def _refusal_for(mutate) -> str:
        mutated = copy.deepcopy(blob)
        mutate(mutated)
        monkeypatch.setattr(cb, "_roster_at_commit", lambda _c, _m=mutated: _m)
        out = cb.arms_book(knee_bill)
        assert out["available"] is False
        monkeypatch.undo()
        return out["unavailable_because"]

    def _drop_account(book):
        book["customers"] = book["customers"][:-1]

    def _drop_gas(book):
        for customer in book["customers"]:
            if ((customer.get("legs") or {}).get("gas") or {}).get("cid"):
                customer["legs"].pop("gas")
                return
        raise AssertionError("no gas leg to drop — the fixture book cannot exercise this leg")

    def _drop_electricity(book):
        for customer in book["customers"]:
            legs = customer.get("legs") or {}
            if (legs.get("electricity") or {}).get("cid") and (legs.get("gas") or {}).get("cid"):
                legs.pop("electricity")
                return
        raise AssertionError("no dual-fuel account — the fixture book cannot exercise this leg")

    assert "billing_accounts_settled_in_window" in _refusal_for(_drop_account)
    gas_refusal = _refusal_for(_drop_gas)
    assert "with_a_gas_leg" in gas_refusal and "dual_fuel" in gas_refusal
    elec_refusal = _refusal_for(_drop_electricity)
    assert "with_an_electricity_leg" in elec_refusal and "dual_fuel" in elec_refusal
    # Every refusal above carries the numbers that disagreed, not just the field name.
    assert "run=" in gas_refusal and "roster=" in gas_refusal

    # ---- leg 3: an earlier break in the chain refuses for a different, nameable reason -------
    monkeypatch.setattr(cb, "_roster_at_commit", lambda _c: None)
    no_blob = cb.arms_book(knee_bill)
    monkeypatch.undo()
    assert no_blob["available"] is False
    assert "git could not produce" in no_blob["unavailable_because"]
    assert "NOT the book the arms ran on" not in no_blob["unavailable_because"]

    headless = copy.deepcopy(_run_artefact())
    headless["producing_commit"]["commit"] = ""
    written = tmp_run_artefact(monkeypatch, headless)
    assert written["available"] is False
    assert "producing_commit" in written["unavailable_because"]
    assert "git could not produce" not in written["unavailable_because"]

    # ---- leg 4: the reading names the book it quotes, and quotes that book -------------------
    k, part = cb.knee(), cb.partition()
    tree = cb.book_distribution(json.loads(cb.BOOK_PATH.read_text(encoding="utf-8")), knee_bill)
    arms_reading = cb._reading(k, part, tree, real)
    assert "154-account book the published arms were scored over" in arms_reading
    arms_resi = real["by_segment"]["resi"]
    assert "{} of this book's {}".format(
        arms_resi["legs"] - arms_resi["above_the_knee"], arms_resi["legs"]) in arms_reading
    assert "{}x".format(real["world_multiplier_spread"]) in arms_reading

    fallback = cb._reading(k, part, tree, {"available": False, "unavailable_because": "probe"})
    assert "the book this tree holds today" in fallback
    tree_resi = tree["by_segment"]["resi"]
    assert "{} of this book's {}".format(
        tree_resi["legs"] - tree_resi["above_the_knee"], tree_resi["legs"]) in fallback
    # And the two are genuinely different sentences — a fallback nobody can detect is the whole
    # defect this leg is written for.
    assert arms_reading != fallback


def tmp_run_artefact(monkeypatch, payload: dict) -> dict:
    """Point `arms_book` at a substitute run artefact and return what it made of it."""
    import json
    import tempfile
    from pathlib import Path

    import tools.generate_value_arms_data as gva

    with tempfile.TemporaryDirectory() as raw:
        path = Path(raw) / "three_arm.json"
        path.write_text(json.dumps(payload), encoding="utf-8")
        monkeypatch.setattr(gva, "THREE_ARM_PATH", path)
        out = cb.arms_book(3000.0)
        monkeypatch.undo()
    return out


def test_the_artefact_publishes_both_books_and_says_which_one_the_reading_quotes():
    """The two populations are both on the page's feed, and the feed says which is quoted.

    Keyed to the PROPERTY and not to 154: the assertion is that the quoted book's own resi counts
    are the ones in the sentence, so this stays green when the book changes and goes red when the
    sentence stops describing the book it names.
    """
    import json

    data = json.loads(cb.DEFAULT_ARTEFACT.read_text(encoding="utf-8"))
    assert data["book"]["available"] is True
    assert data["which_book_the_reading_quotes"].strip()
    quoted = data["arms_book"] if data["arms_book"].get("available") else data["book"]
    assert quoted is not data["book"] or not data["arms_book"].get("available")
    resi = quoted["by_segment"]["resi"]
    assert "{} of this book's {}".format(
        resi["legs"] - resi["above_the_knee"], resi["legs"]) in data["reading"]
    # DELIBERATELY NOT "the two books differ". They do today -- 164 against 154 -- but that is a
    # fact about when the roster was last regenerated, not a property, and a control pinned to it
    # would go red the day the tree's book and the arms' book legitimately coincide. What must
    # hold is that each block says which population it is, which is asserted above.
