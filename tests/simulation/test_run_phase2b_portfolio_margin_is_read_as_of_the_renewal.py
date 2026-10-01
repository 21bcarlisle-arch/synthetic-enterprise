"""A renewal's portfolio premium may only read margins of terms that had ENDED before it starts.

The defect: `main` settles each term to its end inside a start-ordered loop and appended its margin
straight away, so a renewal priced in July 2024 read a term settling to February 2025. Each test
here names the shape of that defect it would catch.
"""

from simulation.run_phase2b import EndedTermMargins


def test_a_running_term_is_held_while_an_ended_one_is_released():
    # Both branches in one control: a queue that released nothing, or everything, fails here.
    book = EndedTermMargins()
    book.settled("2024-06-30", "electricity", 0.10)   # ended before the renewal
    book.settled("2025-02-14", "electricity", -0.30)  # started earlier in the loop, still running
    book.as_of("2024-07-01")
    assert book.electricity == [0.10]
    book.as_of("2025-02-15")
    assert book.electricity == [0.10, -0.30]


def test_a_term_whose_last_day_is_the_renewals_first_day_is_not_yet_seen():
    book = EndedTermMargins()
    book.settled("2024-07-01", "gas", 0.05)
    book.as_of("2024-07-01")
    assert book.gas == []


def test_terms_join_in_the_order_they_ended_not_the_order_they_were_settled():
    # The lookback takes the LAST N entries, so a settle-ordered list would call a term that
    # ended long ago "recent".
    book = EndedTermMargins()
    book.settled("2024-12-31", "electricity", 0.01)
    book.settled("2024-03-31", "electricity", 0.02)
    book.as_of("2025-01-01")
    assert book.electricity == [0.02, 0.01]


def test_each_fuel_reads_only_its_own_terms():
    book = EndedTermMargins()
    book.settled("2024-01-31", "electricity", 0.03)
    book.settled("2024-01-31", "gas", 0.04)
    book.as_of("2024-02-01")
    assert (book.electricity, book.gas) == ([0.03], [0.04])
