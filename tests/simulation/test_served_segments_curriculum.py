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
