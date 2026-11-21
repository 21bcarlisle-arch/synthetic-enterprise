"""The world answers a phone staffing plan with a wait (simulation/contact_centre.py, phone_queue).

Each test names the defect it catches."""
import math
import random

import pytest

from simulation.contact_centre import (
    HANDLE_TIME_GAP,
    draw_phone_wait_seconds,
    erlang_c,
    phone_queue,
)


def _erlang_c_closed_form(a: float, n: int) -> float:
    top = a**n / math.factorial(n) * n / (n - a)
    return top / (sum(a**k / math.factorial(k) for k in range(n)) + top)


def test_a_missing_handle_time_is_refused_with_its_gap_named():
    """Defect: a default handle time slipped in, so a run waits on an invented number."""
    with pytest.raises(ValueError, match="unpublished"):
        phone_queue(120, None, 20)
    assert "s.5" in HANDLE_TIME_GAP


def test_the_recursion_is_erlang_c():
    """Defect: the stable recursion drifted from the textbook formula it replaces."""
    for a in (0.5, 3.0, 8.0, 16.0, 24.0):
        for n in range(math.floor(a) + 1, math.floor(a) + 12):
            assert erlang_c(a, n) == pytest.approx(_erlang_c_closed_form(a, n), rel=1e-9)


def test_both_sides_of_the_cliff_are_reachable_and_one_agent_crosses_it():
    """Defect: a queue that is always saturated, or never, passes every other test here."""
    over = phone_queue(120, 8, 16)   # load 16 Erlangs, 16 agents
    under = phone_queue(120, 8, 17)
    assert over.saturated and over.mean_wait_seconds is None
    assert not under.saturated and under.mean_wait_seconds > 0


def test_another_agent_never_lengthens_the_wait():
    """Defect: a sign error in the conditional wait makes staffing up cost the caller time."""
    waits = [phone_queue(120, 8, n).mean_wait_seconds for n in range(17, 40)]
    assert all(b <= a for a, b in zip(waits, waits[1:]))
    assert waits[-1] < 1.0


def test_the_drawn_waits_average_to_the_queues_mean():
    """Defect: the per-caller draw ignores P(wait) and gives every caller the conditional mean."""
    q = phone_queue(120, 8, 18)
    rng = random.Random(7)
    draws = [draw_phone_wait_seconds(q, rng) for _ in range(40_000)]
    assert sum(draws) / len(draws) == pytest.approx(q.mean_wait_seconds, rel=0.05)
    zero_share = sum(d == 0.0 for d in draws) / len(draws)
    assert zero_share == pytest.approx(1 - q.probability_of_waiting, abs=0.01)
    assert draw_phone_wait_seconds(phone_queue(120, 8, 16), rng) is None
