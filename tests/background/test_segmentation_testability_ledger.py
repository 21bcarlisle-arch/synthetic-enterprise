"""CA3 — R15 both-ways tests for the segmentation-testability ledger + gate.

The control's whole job is to hold the pool-vs-book line: cohort activation (CA1)
gives the WORLD variety; it must NOT be read as the company BOOK's segmentation
becoming testable. R15 demands the gate can FAIL — so each guard is proven to
fire on its own named defect and to clear when the defect is removed.

Guards proven here (background/segmentation_testability_ledger.py::review_register):
  * happy path — the real register at the current book is honestly untestable → green.
  * FAIL-OPEN (claim above reality) — testable=True below the floor → red.
  * STALE (both-ways) — untestable while book >= floor → red; and green once the
    book is below the floor again (proving the marking is not unconditionally green).
  * MISSING UNLOCK — an untestable capability with no unlock → red.
  * STRUCTURAL — missing key / non-finite floor → red.
  * FAIL-CLOSED — missing / malformed register file → LedgerUnavailable-driven red,
    never a silent green.
  * INDEPENDENCE — the gate never reads the book itself (pure fn of its argument).
"""

import json

import pytest

import background.segmentation_testability_ledger as stl


# --------------------------------------------------------------------------- #
# Fixtures / helpers
# --------------------------------------------------------------------------- #

def _cap(**over):
    base = {
        "id": "x",
        "name": "X",
        "testable_at_current_book": False,
        "min_book_for_testability": 36,
        "reason": "too small",
        "unlock": "acquisition becomes a decision variable — growth session.",
    }
    base.update(over)
    return base


def _register(caps):
    return {"capabilities": caps}


# --------------------------------------------------------------------------- #
# Happy path — the SHIPPED register at the current book
# --------------------------------------------------------------------------- #

def test_shipped_register_is_green_at_current_book():
    """The real register + the real book size: every segmentation capability is
    honestly recorded untestable-at-current-book with a named unlock."""
    book = stl.current_book_size()
    result = stl.review_register(book)
    assert result.passed, result.reasons
    # And it is non-trivial: the register actually lists capabilities.
    reg = stl.load_register()
    assert len(stl.capabilities(reg)) >= 1


def test_shipped_register_all_untestable_and_below_floor():
    """Sanity: at the current book EVERY listed capability is below its floor and
    marked untestable — so the green above is meaningful, not vacuous."""
    book = stl.current_book_size()
    for c in stl.capabilities(stl.load_register()):
        assert c["testable_at_current_book"] is False
        assert book < c["min_book_for_testability"]
        assert isinstance(c["unlock"], str) and c["unlock"].strip()


# --------------------------------------------------------------------------- #
# FAIL-OPEN — a capability claiming testable below its floor
# --------------------------------------------------------------------------- #

def test_claim_testable_below_floor_reds():
    reg = _register([_cap(testable_at_current_book=True, min_book_for_testability=36)])
    result = stl.review_register(18, register=reg)
    assert not result.passed
    assert any("below its cell floor" in r or "< floor" in r for r in result.reasons)


def test_claim_testable_below_floor_clears_when_marked_untestable():
    """Both-ways: fix the same capability back to untestable → green."""
    reg = _register([_cap(testable_at_current_book=False, min_book_for_testability=36)])
    assert stl.review_register(18, register=reg).passed


# --------------------------------------------------------------------------- #
# STALE — untestable while the book has grown past the floor (both-ways)
# --------------------------------------------------------------------------- #

def test_untestable_above_floor_reds():
    reg = _register([_cap(testable_at_current_book=False, min_book_for_testability=36)])
    result = stl.review_register(999, register=reg)
    assert not result.passed
    assert any("crossed the knee" in r or ">= " in r for r in result.reasons)


def test_untestable_below_floor_is_green_proving_not_unconditional():
    """The same untestable marking is GREEN below the floor — proving the gate is
    a real function of the book, not unconditionally green (independence)."""
    reg = _register([_cap(testable_at_current_book=False, min_book_for_testability=36)])
    assert stl.review_register(10, register=reg).passed


def test_testable_above_floor_is_green():
    """The intended post-unlock state: book past the floor + marked testable → green."""
    reg = _register([_cap(testable_at_current_book=True, min_book_for_testability=36)])
    assert stl.review_register(50, register=reg).passed


# --------------------------------------------------------------------------- #
# MISSING UNLOCK — the CA3 requirement
# --------------------------------------------------------------------------- #

@pytest.mark.parametrize("bad_unlock", ["", "   ", None])
def test_untestable_without_unlock_reds(bad_unlock):
    reg = _register([_cap(testable_at_current_book=False, unlock=bad_unlock)])
    result = stl.review_register(18, register=reg)
    assert not result.passed
    assert any("names no unlock" in r for r in result.reasons)


# --------------------------------------------------------------------------- #
# STRUCTURAL guards
# --------------------------------------------------------------------------- #

def test_missing_required_key_reds():
    bad = _cap()
    del bad["min_book_for_testability"]
    result = stl.review_register(18, register=_register([bad]))
    assert not result.passed
    assert any("missing required key" in r for r in result.reasons)


@pytest.mark.parametrize("bad_floor", [0, -5, float("nan"), float("inf"), "36", True])
def test_non_finite_or_nonpositive_floor_reds(bad_floor):
    reg = _register([_cap(min_book_for_testability=bad_floor)])
    result = stl.review_register(18, register=reg)
    assert not result.passed
    assert any("min_book_for_testability" in r for r in result.reasons)


def test_non_bool_testable_flag_reds():
    reg = _register([_cap(testable_at_current_book="no")])
    result = stl.review_register(18, register=reg)
    assert not result.passed


# --------------------------------------------------------------------------- #
# FAIL-CLOSED — an unreadable register is a FAILED check, not a silent pass
# --------------------------------------------------------------------------- #

def test_missing_register_file_reds(tmp_path):
    missing = tmp_path / "nope.json"
    result = stl.review_register(18, register_path=missing)
    assert not result.passed
    assert any("unavailable" in r for r in result.reasons)


def test_malformed_json_register_reds(tmp_path):
    p = tmp_path / "bad.json"
    p.write_text("{ not json", encoding="utf-8")
    result = stl.review_register(18, register_path=p)
    assert not result.passed
    assert any("unavailable" in r for r in result.reasons)


def test_capabilities_not_a_list_reds(tmp_path):
    p = tmp_path / "bad2.json"
    p.write_text(json.dumps({"capabilities": {"x": 1}}), encoding="utf-8")
    result = stl.review_register(18, register_path=p)
    assert not result.passed


def test_load_register_raises_on_missing(tmp_path):
    with pytest.raises(stl.LedgerUnavailable):
        stl.load_register(tmp_path / "absent.json")


# --------------------------------------------------------------------------- #
# INDEPENDENCE — the gate does not read the book; passing a size is load-bearing
# --------------------------------------------------------------------------- #

def test_gate_verdict_flips_purely_on_the_passed_book_size():
    reg = _register([_cap(testable_at_current_book=False, min_book_for_testability=36)])
    assert stl.review_register(18, register=reg).passed          # below floor: honest
    assert not stl.review_register(100, register=reg).passed     # above floor: stale
    # Same register, opposite verdicts — the book size is the only thing that moved.
