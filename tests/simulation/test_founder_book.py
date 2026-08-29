"""The founder book — R13 curriculum, director-decided 2026-08-28: "take the 80 founders".

WHAT THE PARAMETER IS FOR. Three instruments hit the same wall on 2026-08-28 — the price
ladder's 17 binary decisions, the chase-on/chase-off comparison, and A48's method skill on 12
decisions across 5 accounts. All three said the same thing in different units: there are not
enough decisions. Book depth is upstream of all of them, and it is a curriculum question because
it changes what the machine can be ASKED, not how faithful the world is.

THE SAFETY PROPERTY THE DESIGN RESTS ON. Drawn founders take the EXISTING founders' role: they
predate the stock, claim no premise, and are therefore not candidates for PB2's subset verdict —
the same structural exclusion the hand-authored 13 already had, for the same stated reason. That
is what stops an 80-account opening book colliding with the campaign's premise slice or the
trickle's reserved tail.
"""
from __future__ import annotations

import pathlib

import pytest

import simulation.live_population as lp

SEED = lp._DEFAULT_BASE_SEED


# ── the curriculum surface ───────────────────────────────────────────────────────────────────

def test_the_directors_number_is_read_from_the_curriculum_file():
    """R13: the number lives in a director-authored artefact, not in this module.

    Fires on: hard-coding the count, which would make a curriculum act a code change.
    """
    assert lp.FOUNDER_BOOK_PATH.is_file(), lp.FOUNDER_BOOK_PATH
    assert lp.founder_accounts() == 80


def test_an_unreadable_file_falls_back_to_the_ROSTER_and_never_to_zero(monkeypatch, tmp_path):
    """FAIL-SILENT killer. A YAML typo must not silently empty the book a supplier launched
    with. The fallback is the pre-decision state, which is also how the act is reverted."""
    roster = len([c for c in lp._STATIC_ROSTER if lp._serves(c, lp.served_segments())])
    for content in ("", "not a mapping", "founder_accounts: 'eighty'",
                    "founder_accounts: true", "founder_accounts: 5000"):
        path = tmp_path / "FOUNDER_BOOK.yaml"
        path.write_text(content, encoding="utf-8")
        monkeypatch.setattr(lp, "FOUNDER_BOOK_PATH", path)
        assert lp.founder_accounts() == roster, content
    monkeypatch.setattr(lp, "FOUNDER_BOOK_PATH", tmp_path / "absent.yaml")
    assert lp.founder_accounts() == roster


def test_the_file_cannot_SHRINK_the_hand_authored_roster(monkeypatch, tmp_path):
    """The roster is history. A number below it is a request this parameter has no authority to
    honour, and honouring it would delete accounts the world already settled."""
    roster = len([c for c in lp._STATIC_ROSTER if lp._serves(c, lp.served_segments())])
    path = tmp_path / "FOUNDER_BOOK.yaml"
    path.write_text("founder_accounts: 1\nmin_founder_accounts: 1\nmax_founder_accounts: 120\n",
                    encoding="utf-8")
    monkeypatch.setattr(lp, "FOUNDER_BOOK_PATH", path)
    assert lp.founder_accounts() == roster
    assert len(lp.founder_book(SEED)) == roster


# ── the book it produces ─────────────────────────────────────────────────────────────────────

def test_the_opening_book_is_the_number_the_director_set():
    book = lp.founder_book(SEED)
    assert len(book) == lp.founder_accounts() == 80


def test_every_founder_is_dated_at_the_windows_START():
    """An account acquired in 2024 cannot compound however many of them there are — which is the
    entire reason the parameter exists.

    Fires on: drawing founders across the trickle's 2021-2025 window, which would produce 80
    accounts and not 80 founders.
    """
    years = {c["acquisition_date"][:4] for c in lp.founder_book(SEED)}
    assert years == {str(lp.FOUNDER_ACQUISITION_YEAR)}, years


def test_the_draw_is_deterministic():
    """A curriculum act must give the same world twice, or no comparison across it means
    anything."""
    first = [c["customer_id"] for c in lp.founder_book(SEED)]
    second = [c["customer_id"] for c in lp.founder_book(SEED)]
    assert first == second
    assert len(set(first)) == len(first), "the founder draw produced duplicate accounts"


def test_the_hand_authored_roster_is_still_in_the_book():
    """The drawn accounts TOP UP the roster; they do not replace it. Fires on: a draw that
    substitutes for the founders the world has already settled ten years of history for."""
    served = lp.served_segments()
    roster_ids = {c["customer_id"] for c in lp._STATIC_ROSTER if lp._serves(c, served)}
    book_ids = {c["customer_id"] for c in lp.founder_book(SEED)}
    assert roster_ids <= book_ids, sorted(roster_ids - book_ids)


# ── the isolation the whole design rests on ──────────────────────────────────────────────────

def test_the_founder_draw_does_not_perturb_the_trickle():
    """The Profile-B trickle must be byte-identical to the pre-decision run: adding founders may
    change what the book OPENS with and nothing else.

    HONEST ABOUT WHAT THIS PROVES. Swapping the founder draw onto the trickle's own seed does NOT
    red this — `iter_acquisition_events` builds a fresh generator per call, so neither draw can
    consume the other's stream and the isolation holds by construction rather than by the offset.
    What it does catch is a founder draw wired INTO the trickle's own call, which is the version
    of this mistake that would silently change every drawn household.
    """
    before = [sc.to_customer_dict() for sc in lp._drawn_trickle(SEED)]
    lp.founder_book(SEED)                      # draw founders in between
    after = [sc.to_customer_dict() for sc in lp._drawn_trickle(SEED)]
    assert before == after


def test_founder_ids_never_collide_with_the_rest_of_the_book():
    """THE CORRUPTION THAT WOULD MATTER, and the reason the isolation test above is not enough.

    Perturbation changes which households the world draws; a COLLISION puts two different
    accounts under one id, and every per-customer figure downstream silently describes whichever
    one was written last. Founders sit at 2016 and the trickle at 2021-2025, so today the ranges
    are disjoint — this pins that rather than trusting it, because widening either range is a
    one-line change that would make the overlap real.

    Found by a mutation that did NOT fire: swapping the founder draw onto the trickle's own seed
    passed every other test here, which meant the seed offset was defensive and the property
    worth testing was somewhere else.
    """
    founders = [c["customer_id"] for c in lp.founder_book(SEED)]
    trickle = [sc.to_customer_dict()["customer_id"] for sc in lp._drawn_trickle(SEED)]
    assert len(set(founders)) == len(founders), "the founder draw repeats an id"
    assert not (set(founders) & set(trickle)), sorted(set(founders) & set(trickle))
    book = [c["customer_id"] for c in lp._pre_growth_book(SEED)]
    assert len(set(book)) == len(book), (
        "the opening book contains a duplicate account id: {}".format(
            sorted({i for i in book if book.count(i) > 1})))


def test_founders_claim_no_premise_and_stay_outside_the_subset_verdict():
    """PB2's exclusion reason must continue to hold WORD FOR WORD: founders "predate the stock,
    carry no premise, and are not candidates for membership in the first place".

    Fires on: founders claiming premise slots, which would collide with the campaign's
    `[0, PROSPECTS_PER_YEAR)` slice or the trickle's reserved tail and make the subset verdict a
    statement about a book that overlaps itself.
    """
    verdict = lp.book_subset_verdict(SEED)
    assert verdict["ok"] is True, verdict.get("failures")
    assert verdict["n_founders"] == len(lp.founder_book(SEED))


def test_the_exclusion_reports_the_whole_founder_book_not_just_the_roster():
    """"An exclusion nobody can count is an exclusion nobody can check" — the verdict's own
    words. It counted the 13 hand-authored accounts while excluding 80.

    Fires on: reverting `n_founders` to the roster's size.
    """
    verdict = lp.book_subset_verdict(SEED)
    assert verdict["n_founders"] == 80
    assert verdict["n_founders_hand_authored"] == 13
    assert verdict["n_founders"] > verdict["n_founders_hand_authored"], (
        "the two counts are equal, so this test cannot tell whether the whole book is reported")


def test_the_opening_book_reaches_the_growth_plan():
    """`accounts_held_at_start` is what the campaign sizes itself against. A founder book the
    growth plan cannot see would change the world and not the plan built on it."""
    assert len(lp._pre_growth_book(SEED)) >= len(lp.founder_book(SEED))


def test_every_founder_REACHES_THE_SERVED_BOOK_and_not_only_the_growth_plan(monkeypatch,
                                                                            tmp_path):
    """The defect this file shipped with, and the reason the test above was not enough.

    THE TWO SIDES ARE DIFFERENT FUNCTIONS. `_pre_growth_book` is what the campaign PLANS
    against; `live_population` is what the company SERVES, bills and publishes. The test above
    pins the first and passed the whole time the second was wrong: `live_population` rebuilt its
    opening book from the 13-account `CUSTOMERS` literal, so the campaign committed 800 of its
    1,200 customer-years to 80 founders — refusing 335 of its own funnel wins to pay for them —
    and 67 of those founders then reached no served book at all. Measured at the shipped seed:
    the run published 100 accounts while paying the settlement cost of 82 opening ones, and the
    curriculum act bought to make the book DEEPER made it four times SHALLOWER (398 -> 100) for
    six extra accounts at 5+ renewals. Charged for and never delivered.

    A COUNT WOULD NOT CATCH IT. This asserts the founders are in the book BY ID, because the
    published book is the right size for the wrong reason as soon as the campaign's wins make up
    the difference — which is exactly what hid this: 13 + 2 + 85 = 100 looks like a book.
    """
    monkeypatch.setattr(lp, "_CAMPAIGN_RECORD", tmp_path / "campaign.json")
    monkeypatch.setattr(lp, "_SUBSET_VERDICT_RECORD", tmp_path / "verdict.json")
    lp._CAMPAIGN_MEMO.clear()
    try:
        served_ids = {c["customer_id"] for c in lp.live_population(SEED)}
    finally:
        lp._CAMPAIGN_MEMO.clear()

    founder_ids = {c["customer_id"] for c in lp.founder_book(SEED)}
    missing = founder_ids - served_ids
    assert not missing, (
        f"{len(missing)} of {len(founder_ids)} founders are in the plan the campaign was "
        f"charged for but not in the book the company serves"
    )
    assert len(founder_ids) > len([c for c in lp._STATIC_ROSTER
                                   if lp._serves(c, lp.served_segments())]), (
        "the founder book is only the hand-authored roster here, so this test cannot tell "
        "whether the DRAWN founders reach the served book"
    )


# ── the reversal named in the curriculum file ────────────────────────────────────────────────

def test_setting_the_number_back_to_the_roster_restores_the_pre_decision_book(
        monkeypatch, tmp_path):
    """The file says reverting is setting the number back. That has to be TRUE, not a hope —
    an act whose stated reversal does not work is an act nobody can undo."""
    served = lp.served_segments()
    roster = [c for c in lp._STATIC_ROSTER if lp._serves(c, served)]
    path = tmp_path / "FOUNDER_BOOK.yaml"
    path.write_text("founder_accounts: {}\nmin_founder_accounts: {}\nmax_founder_accounts: 120\n"
                    .format(len(roster), len(roster)), encoding="utf-8")
    monkeypatch.setattr(lp, "FOUNDER_BOOK_PATH", path)
    assert [c["customer_id"] for c in lp.founder_book(SEED)] == \
        [c["customer_id"] for c in roster]


def test_the_curriculum_file_records_who_decided_and_when():
    """R13: a difficulty change is a NAMED, VERSIONED, director-authored artefact. Fires on: a
    number landing with no provenance, which is how a curriculum drifts."""
    import yaml

    loaded = yaml.safe_load(pathlib.Path(lp.FOUNDER_BOOK_PATH).read_text(encoding="utf-8"))
    assert loaded["decided_by"] == "director"
    assert loaded["decided_on"] == "2026-08-28"
    assert isinstance(loaded["version"], int)
