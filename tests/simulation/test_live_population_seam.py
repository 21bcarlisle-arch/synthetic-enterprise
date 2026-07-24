"""R15 both-ways tests for the LIVE POPULATION SEAM (generator draw-wiring,
default-OFF, director-reserved activation).

The seam is the reversible half of the draw-wiring: DEFAULT-OFF it is byte
identical to the static book; ACTIVATED it additively appends the synthetic
SYN-* acquisition cohort. R15 demands the control can FAIL: these tests prove
the wire is LOAD-BEARING (flag-on adds SYN-*) AND that removing/omitting the
activation reverts exactly to the static book (mutation both-ways), and that
the epistemic wall holds (the drawn ground-truth `cohort` never surfaces).
"""

import importlib

import pytest

from saas.customers import CUSTOMERS
from simulation import live_population as lp


@pytest.fixture(autouse=True)
def _clear_flag(monkeypatch):
    """Ensure each test controls the activation flag explicitly (default OFF)."""
    monkeypatch.delenv("SE_DRAW_POPULATION", raising=False)
    yield


def test_default_off_flag_predicate_is_false():
    assert lp.draw_population_enabled() is False


def test_default_off_is_static_book_byte_identical():
    """Flag OFF: the seam returns exactly the static CUSTOMERS content."""
    book = lp.live_population()
    assert book == list(CUSTOMERS)
    # A fresh list (mutating it must not corrupt the shared literal).
    assert book is not CUSTOMERS


def test_default_off_returns_fresh_list_each_call():
    a = lp.live_population()
    a.append({"customer_id": "MUTANT"})
    b = lp.live_population()
    assert not any(c.get("customer_id") == "MUTANT" for c in b)
    assert b == list(CUSTOMERS)


def test_activation_adds_synthetic_acquisitions(monkeypatch):
    """Flag ON: the book is CUSTOMERS + additive SYN-* acquisitions (the wire
    is load-bearing — its presence is what adds the cohort)."""
    monkeypatch.setenv("SE_DRAW_POPULATION", "1")
    assert lp.draw_population_enabled() is True
    book = lp.live_population()
    # Additive-not-replacive: every static customer survives, in order, first.
    assert book[: len(CUSTOMERS)] == list(CUSTOMERS)
    extra = book[len(CUSTOMERS):]
    assert len(extra) >= 1, "activation must add at least one drawn acquisition"
    assert all(c["customer_id"].startswith("SYN-") for c in extra)
    # Fills the post-2020 acquisition gap the FRAME found.
    assert all(int(c["acquisition_date"][:4]) >= 2021 for c in extra)


def test_mutation_flag_off_reverts_exactly(monkeypatch):
    """MUTATION (both-ways): with the flag turned back off, the SYN-* cohort
    disappears and the book is exactly the static one again — proving the SYN
    entries come from the flag, not from an unconditional code path."""
    monkeypatch.setenv("SE_DRAW_POPULATION", "1")
    assert any(c["customer_id"].startswith("SYN-") for c in lp.live_population())
    monkeypatch.delenv("SE_DRAW_POPULATION", raising=False)
    off = lp.live_population()
    assert off == list(CUSTOMERS)
    assert not any(c["customer_id"].startswith("SYN-") for c in off)


def test_activation_is_deterministic_replay(monkeypatch):
    """C-S2 deterministic replay: activated twice yields an identical book."""
    monkeypatch.setenv("SE_DRAW_POPULATION", "1")
    assert lp.live_population() == lp.live_population()


def test_wall_drawn_book_never_exposes_ground_truth_cohort(monkeypatch):
    """EPISTEMIC WALL: no saas-shaped dict the seam returns carries the hidden
    ground-truth `cohort` field — the company must discover, never read it."""
    monkeypatch.setenv("SE_DRAW_POPULATION", "1")
    for c in lp.live_population():
        assert "cohort" not in c


def test_seam_module_does_not_import_company():
    """Wall hygiene: the seam bridges sim<->saas only; it must not import any
    company logic (that would be a discovery-side read of a supply-side book)."""
    src = importlib.util.find_spec("simulation.live_population").origin
    with open(src, "r", encoding="utf-8") as fh:
        text = fh.read()
    assert "import company" not in text
    assert "from company" not in text
