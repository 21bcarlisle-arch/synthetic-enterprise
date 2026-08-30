"""The two curriculum dials the 2026-08-24 director console created, and their controls.

WHY THIS FILE EXISTS. `simulation/live_population.py` grew two readers of
`docs/design/curriculum/` in one pass -- `served_segments()` (which segments the supplier
takes) and `founding_capital_gbp()` (its opening balance sheet) -- and neither had a test.
Both are R13 CURRICULUM: the director's dials, read from disk, deciding which world the
company lives in. A curriculum dial with no control is the worst kind of unproven mechanism,
because the failure is silent by construction -- a dial that has quietly stopped moving the
world looks exactly like a dial nobody has turned.

BOTH READERS FAIL OPEN ON PURPOSE, which is the opposite direction to almost every guard in
this repo, so the tests below pin the fail-open direction EXPLICITLY. That is deliberate: a
future hardening pass that "fixes" these to fail closed would be reverting a decision, and it
should have to delete a test that says so rather than quietly flip a branch. The reason is
stated at both call sites -- an unreadable JSON file must not empty a published book or zero a
balance sheet, because losing every customer to a parse error is a far worse published figure
than serving a segment somebody meant to suspend.

R15 -- WHAT MAKES THESE CONTROLS ABLE TO FAIL. Every claim below is asserted against the REAL
shipped roster and the REAL curriculum files, never a fabricated fixture, and every suspension
test carries a NULL CONTROL: the same call with nothing suspended, asserted to return MORE
accounts. Without that pairing "no I&C in the book" passes just as happily on a filter that
returns the empty list, on a roster that never had an I&C account, and on a suspension that
does nothing because the book was assembled before the filter ran.
"""
from __future__ import annotations

import json

import pytest

from saas.customers import CUSTOMERS
from simulation import live_population as lp
from simulation.segment_vocabulary import CANONICAL_SEGMENTS


# --- the roster this is all about -------------------------------------------------------
def _segments_of(book):
    return {lp._canonical(c.get("segment")) for c in book}


def test_the_shipped_roster_really_does_carry_every_segment():
    """PRECONDITION for everything below. If the roster stopped carrying I&C accounts, every
    'I&C is gone' assertion in this file would pass for the wrong reason -- the wrong-subject
    shape. Asserted rather than assumed, so the suspension tests cannot go quietly vacuous."""
    present = _segments_of(CUSTOMERS)
    for segment in CANONICAL_SEGMENTS:
        assert segment in present, f"roster no longer carries {segment!r}: {present}"


# --- served_segments(): reading the dial ------------------------------------------------
def test_the_dial_is_read_from_the_committed_curriculum_file():
    """The shipped default is whatever the director's file says -- not a constant in code."""
    on_disk = json.loads(lp._SERVED_SEGMENTS_CURRICULUM.read_text())["served"]["value"]
    assert lp.served_segments() == tuple(on_disk)


def test_the_env_override_wins_over_the_file(monkeypatch):
    monkeypatch.setenv("SE_SERVED_SEGMENTS", "resi")
    assert lp.served_segments() == ("resi",)


def test_an_unreadable_curriculum_file_serves_every_segment(monkeypatch, tmp_path):
    """FAIL-OPEN, PINNED. A missing file must not suspend the whole book."""
    monkeypatch.delenv("SE_SERVED_SEGMENTS", raising=False)
    monkeypatch.setattr(lp, "_SERVED_SEGMENTS_CURRICULUM", tmp_path / "gone.json")
    assert lp.served_segments() == CANONICAL_SEGMENTS


@pytest.mark.parametrize(
    "body",
    ['{"served": {"value": []}}', '{"served": {"value": null}}', "not json at all", "{}"],
    ids=["empty-list", "null", "malformed", "no-key"],
)
def test_a_malformed_curriculum_file_serves_every_segment(monkeypatch, tmp_path, body):
    monkeypatch.delenv("SE_SERVED_SEGMENTS", raising=False)
    path = tmp_path / "served.json"
    path.write_text(body)
    monkeypatch.setattr(lp, "_SERVED_SEGMENTS_CURRICULUM", path)
    assert lp.served_segments() == CANONICAL_SEGMENTS


# --- _serves(): the filter itself -------------------------------------------------------
def test_suspending_a_segment_actually_suspends_it():
    """THE POSITIVE CLAIM. Every canonical spelling of a suspended segment is refused."""
    for spelling in ("I&C", "IC", "i and c"):
        assert lp._serves({"segment": spelling}, ("resi",)) is False, spelling


def test_a_served_segment_survives_in_any_spelling():
    for spelling in ("resi", "RESI", "residential", "domestic"):
        assert lp._serves({"segment": spelling}, ("resi",)) is True, spelling


def test_the_filter_is_not_a_constant():
    """NULL CONTROL for `_serves`: the same account is served or not depending ONLY on the
    dial, so the filter is not one branch that always answers the same way."""
    account = {"segment": "I&C"}
    assert lp._serves(account, CANONICAL_SEGMENTS) is True
    assert lp._serves(account, ("resi",)) is False


@pytest.mark.parametrize(
    "account",
    [{}, {"segment": None}, {"segment": "wibble"}, {"segment": "resi_standard"}],
    ids=["absent", "none", "unknown-word", "cohort-id-not-a-segment"],
)
def test_an_unreadable_account_segment_is_served_and_does_not_raise(account):
    """FAIL-OPEN, PINNED -- and this is the one that was actually broken.

    `normalise_segment` RAISES on a present-but-unrecognised spelling (it defaults only for a
    genuinely absent one), and the first version of `_serves` called it bare. The documented
    behaviour was 'serve it'; the real behaviour was to take down every run that assembles a
    book. A `pytest.raises`-free assertion is not enough here, so the return value is checked
    too: the account must be SERVED, not merely fail to explode.
    """
    assert lp._serves(account, ("resi",)) is True


def test_a_curriculum_typo_serves_everyone_rather_than_no_one():
    """The same fail-open direction on the DIAL side. A `served` list whose entries are all
    unreadable must not resolve to an empty allow-set, which would suspend the entire book --
    fail-CLOSED, and the single worst outcome available to this filter."""
    for account in ({"segment": "resi"}, {"segment": "I&C"}, {"segment": "SME"}):
        assert lp._serves(account, ("residental", "nonsense")) is True, account


def test_one_bad_entry_does_not_void_the_rest_of_the_dial():
    """A typo alongside a good entry narrows the dial to the good entry -- it neither voids
    the suspension nor widens it back to everything."""
    assert lp._serves({"segment": "resi"}, ("resi", "residental")) is True
    assert lp._serves({"segment": "I&C"}, ("resi", "residental")) is False


# --- the wiring: the dial reaches the real book -----------------------------------------
def test_the_dial_moves_the_real_book_and_the_null_control_moves_it_back(monkeypatch):
    """THE LOAD-BEARING TEST. Everything above judges `_serves` in isolation; this judges the
    shipped `live_population()`, because a perfect filter nothing calls suspends nothing.

    Both books come from the same function on the same seed and differ only in the dial, so
    the comparison cannot be satisfied by a filter that returns the empty list (asserted
    non-empty), by a roster with no I&C (asserted above), or by a suspension applied after the
    book was assembled (the residential count is asserted UNCHANGED).
    """
    monkeypatch.setenv("SE_SERVED_SEGMENTS", ",".join(CANONICAL_SEGMENTS))
    everything = lp.live_population(base_seed=20260824)

    monkeypatch.setenv("SE_SERVED_SEGMENTS", "resi")
    resi_only = lp.live_population(base_seed=20260824)

    assert resi_only, "suspension emptied the book -- fail-closed, not a suspension"
    assert len(resi_only) < len(everything), "the dial moved nothing"
    assert _segments_of(resi_only) <= {"resi", None}, _segments_of(resi_only)
    assert "I&C" in _segments_of(everything), "null control never served I&C"

    n_resi = sum(1 for c in everything if lp._canonical(c.get("segment")) == "resi")
    assert sum(1 for c in resi_only if lp._canonical(c.get("segment")) == "resi") == n_resi, (
        "suspending I&C changed the number of HOUSEHOLDS -- the filter is not independent of "
        "the segment it is filtering on"
    )


# --- the third arrival path: the campaign's own winners ----------------------------------
# THE SUBJECT HAS TO BE MADE TO ARRIVE. A book reaches `live_population`'s caller by three
# routes -- the static roster, the drawn trickle, and the growth campaign's winners -- and the
# test above only proves the dial on the first two, because the shipped funnel has never won a
# non-residential prospect. That is the whole difficulty: on the real funnel a campaign filter
# that works and a campaign filter that is missing entirely produce byte-identical books, so
# neither an assertion about the real run nor a mutation of the filter could tell them apart.
# The winners are therefore INJECTED, which is the only way this control can be made to fail.
_INJECTED_WINNERS = [
    {"customer_id": "TEST-CAMPAIGN-WIN-RESI", "segment": "resi",
     "acquisition_date": "2026-08-26", "acquisition_type": "net_new_won"},
    {"customer_id": "TEST-CAMPAIGN-WIN-IC", "segment": "I&C",
     "acquisition_date": "2026-08-26", "acquisition_type": "net_new_won"},
]


def _ids(book):
    return {c.get("customer_id") for c in book}


def test_a_campaign_win_in_a_suspended_segment_never_joins_the_book(monkeypatch):
    """THE GUARD, AND THE NULL CONTROL THAT PROVES IT IS NOT VACUOUS (2026-08-26).

    `live_population` filtered `static` and `drawn` and let the campaign's winners through
    unfiltered. Nothing published was ever wrong because of it -- the funnel only ever won
    households -- which is exactly why it survived unnoticed: a guard whose subject never
    arrives looks identical to a guard that works.

    Both halves are load-bearing and neither is sufficient alone:

    * SUSPENDED -- the injected I&C winner must be absent. Revert the `_serves` filter at the
      campaign call site and this assertion reds; that is the mutation.
    * NULL CONTROL -- the same injected I&C winner must be PRESENT when nothing is suspended.
      Without it the first half passes just as happily on a campaign path that is dead, on an
      injection that never reaches the book, and on a `_won_customer_dicts` patch that simply
      failed to take -- the wrong-subject shape this file's docstring names.

    The residential winner is asserted present in BOTH directions, so the filter cannot pass by
    discarding every campaign win rather than the suspended one.
    """
    monkeypatch.setattr(lp, "_won_customer_dicts", lambda outcome: list(_INJECTED_WINNERS))

    monkeypatch.setenv("SE_SERVED_SEGMENTS", ",".join(CANONICAL_SEGMENTS))
    everything = _ids(lp.live_population(base_seed=20260826))

    monkeypatch.setenv("SE_SERVED_SEGMENTS", "resi")
    resi_only = _ids(lp.live_population(base_seed=20260826))

    assert "TEST-CAMPAIGN-WIN-IC" in everything, (
        "NULL CONTROL FAILED: the injected I&C winner never reached the book even with every "
        "segment served, so the suspension assertion below would pass for the wrong reason"
    )
    assert "TEST-CAMPAIGN-WIN-IC" not in resi_only, (
        "a campaign win in a SUSPENDED segment joined the book -- the filter is applied to the "
        "static roster and the drawn trickle but not to the campaign's winners"
    )
    assert "TEST-CAMPAIGN-WIN-RESI" in everything and "TEST-CAMPAIGN-WIN-RESI" in resi_only, (
        "the served campaign win was dropped too -- this is not a segment filter, it is a "
        "campaign filter"
    )


# --- founding_capital_gbp(): the balance sheet dial --------------------------------------
def test_founding_capital_is_read_from_the_committed_curriculum_file():
    on_disk = json.loads(lp._FOUNDING_CAPITAL_CURRICULUM.read_text())
    expected = on_disk["founding_capital_gbp"]["value"]
    assert lp.founding_capital_gbp(fallback=1.0) == float(expected)


def test_the_run_actually_uses_it():
    """WIRING, not intent. `run_phase2b.STARTING_TREASURY_GBP` is the number the whole P&L is
    computed from; if the curriculum figure never reaches it, the dial is decoration.

    Compared against the curriculum file rather than a literal, so the test does not have to
    be edited every time the director moves the dial -- and asserted DIFFERENT from the legacy
    EAC-scaled formula, without which this would pass on the un-wired code it replaced.
    """
    from simulation.run_phase2b import (
        EFFECTIVE_EAC,
        ORIGINAL_4_CUSTOMER_EAC_KWH,
        STARTING_TREASURY_GBP,
    )

    expected = json.loads(lp._FOUNDING_CAPITAL_CURRICULUM.read_text())
    expected = float(expected["founding_capital_gbp"]["value"])
    legacy = 3250.0 * (EFFECTIVE_EAC / ORIGINAL_4_CUSTOMER_EAC_KWH)

    assert STARTING_TREASURY_GBP == expected
    assert STARTING_TREASURY_GBP != pytest.approx(legacy), (
        "the curriculum figure and the formula it replaced are indistinguishable, so this "
        "test could not tell a wired dial from an unwired one"
    )


@pytest.mark.parametrize(
    "body",
    [
        '{"founding_capital_gbp": {"value": null}}',
        '{"founding_capital_gbp": {"value": 0}}',
        '{"founding_capital_gbp": {"value": -5}}',
        '{"founding_capital_gbp": {"value": "lots"}}',
        "not json",
        "{}",
    ],
    ids=["null", "zero", "negative", "not-a-number", "malformed", "no-key"],
)
def test_an_unusable_capital_figure_returns_the_callers_fallback(monkeypatch, tmp_path, body):
    """FAIL-OPEN, PINNED. `null` is the documented restore path; zero and negative are the
    dangerous ones -- a company with no capital cannot trade, so they must be refused rather
    than believed. The fallback is returned EXACTLY, not recomputed."""
    monkeypatch.delenv("SE_FOUNDING_CAPITAL_GBP", raising=False)
    path = tmp_path / "capital.json"
    path.write_text(body)
    monkeypatch.setattr(lp, "_FOUNDING_CAPITAL_CURRICULUM", path)
    assert lp.founding_capital_gbp(fallback=12345.67) == 12345.67


def test_a_missing_capital_file_returns_the_callers_fallback(monkeypatch, tmp_path):
    monkeypatch.delenv("SE_FOUNDING_CAPITAL_GBP", raising=False)
    monkeypatch.setattr(lp, "_FOUNDING_CAPITAL_CURRICULUM", tmp_path / "gone.json")
    assert lp.founding_capital_gbp(fallback=99.5) == 99.5


def test_the_capital_env_override_wins_and_a_bad_one_falls_back(monkeypatch):
    monkeypatch.setenv("SE_FOUNDING_CAPITAL_GBP", "777")
    assert lp.founding_capital_gbp(fallback=1.0) == 777.0
    monkeypatch.setenv("SE_FOUNDING_CAPITAL_GBP", "not-a-number")
    assert lp.founding_capital_gbp(fallback=1.0) == 1.0


# ── THE DIAL IS A FILTER ON THE COMPANY'S BOOK, NEVER A CHANGE TO THE WORLD ──────────────────
# Director's ruling, 2026-08-30, on his own 2026-08-24 suspension:
#
#   "the SIM keeps creating those accounts and only the company's book changes. A dial that
#    alters which households exist is the opposite of that, and it invalidates every comparison
#    across it. The segment choice belongs at the company's acquisition decision, not in the
#    world's draw."
#
# THE DEFECT THESE FIRE ON, measured before the repair on one seed: serving all segments gave
# {resi 238, SME 9, I&C 11}; serving resi only gave {resi 257}. Suspending a segment ADDED
# nineteen households, and the sets were not nested in either direction -- 7 residential
# accounts existed only when I&C was served and 10 only when it was suspended. Four separate
# places read the dial while DRAWING: `founder_book` filtered the roster and then sized its
# top-up against the filtered length; `_founder_roster_size` and `founder_accounts` did the
# same; and `_drawn_founder_pairs` skipped non-served accounts INSIDE the draw loop, so the
# dial changed how far down the stream it walked to reach `wanted`.
#
# WHY THE SET AND NOT THE COUNT. The pre-existing control asserted the residential COUNT, which
# is why it took a nineteen-account swing to fire at all. A dial that swapped ten households for
# ten others would have passed it silently -- and that is the confound, not the size change.

def test_the_residential_SET_is_identical_across_dial_positions(monkeypatch):
    """THE LOAD-BEARING ONE. Same seed, two dial positions, byte-identical households.

    An A/B across this dial is only attributable if the population is held fixed. A count test
    cannot establish that; only the identities can.
    """
    monkeypatch.setenv("SE_SERVED_SEGMENTS", ",".join(CANONICAL_SEGMENTS))
    everything = lp.live_population(base_seed=20260824)
    monkeypatch.setenv("SE_SERVED_SEGMENTS", "resi")
    resi_only = lp.live_population(base_seed=20260824)

    def resi_ids(book):
        return {c["customer_id"] for c in book if lp._canonical(c.get("segment")) == "resi"}

    served_all, served_resi = resi_ids(everything), resi_ids(resi_only)
    assert served_all, "no residential accounts at all -- the test has lost its subject"
    only_when_served = sorted(served_all - served_resi)
    only_when_suspended = sorted(served_resi - served_all)
    assert served_all == served_resi, (
        f"the dial changed WHICH households exist, not just how many: "
        f"{len(only_when_served)} present only when the business segments are served "
        f"({only_when_served[:5]}), {len(only_when_suspended)} present only when they are "
        f"suspended ({only_when_suspended[:5]}). The world must be a function of the seed alone."
    )


def test_suspending_a_segment_is_a_strict_subset_and_removes_only_that_segment(monkeypatch):
    """The other half: a filter may only ever REMOVE, and only the thing it filters on."""
    monkeypatch.setenv("SE_SERVED_SEGMENTS", ",".join(CANONICAL_SEGMENTS))
    everything = lp.live_population(base_seed=20260824)
    monkeypatch.setenv("SE_SERVED_SEGMENTS", "resi")
    resi_only = lp.live_population(base_seed=20260824)

    all_ids = {c["customer_id"] for c in everything}
    kept_ids = {c["customer_id"] for c in resi_only}
    assert kept_ids <= all_ids, (
        f"suspension ADDED {len(kept_ids - all_ids)} account(s) -- a filter cannot add")
    removed = all_ids - kept_ids
    assert removed, "the dial removed nothing -- it is not reaching the book"
    removed_segments = {lp._canonical(c.get("segment")) for c in everything
                        if c["customer_id"] in removed}
    assert removed_segments <= {"SME", "I&C"}, (
        f"suspending the business segments removed {removed_segments} -- it took households "
        f"with it, which is the defect this pair exists to refuse")


def test_the_world_itself_is_untouched_by_the_dial(monkeypatch):
    """Upstream of the company's book: the WORLD's opening book and the campaign's planning
    roster must both be functions of the seed alone.

    This is the property the repair actually installed; the two tests above are its observable
    consequence. Asserted separately so a future change that re-filters the draw and then
    re-filters the book back into agreement still reds here.
    """
    monkeypatch.setenv("SE_SERVED_SEGMENTS", ",".join(CANONICAL_SEGMENTS))
    founders_all = [c["customer_id"] for c in lp.founder_book(20260824)]
    plan_all = [c["customer_id"] for c in lp._pre_growth_book(20260824)]
    monkeypatch.setenv("SE_SERVED_SEGMENTS", "resi")
    founders_resi = [c["customer_id"] for c in lp.founder_book(20260824)]
    plan_resi = [c["customer_id"] for c in lp._pre_growth_book(20260824)]

    assert founders_all == founders_resi, (
        "the world's opening book moved with the dial -- founder_book is reading it again")
    assert plan_all == plan_resi, (
        "the campaign's planning roster moved with the dial, so the funnel draws a different "
        "sequence and wins a different set of households")
