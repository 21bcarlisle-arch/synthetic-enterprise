"""Two defects, both of which this repo has actually shipped.

DEFECT 1 -- A REFUSAL THAT NAMES NOTHING. `ChurnJourneyRegister.advance` raised bare
`KeyError: 'SYN-2016-008'` 880s into a value-arm pass on 2026-09-19. The key, and nothing about
which book refused or what should have registered it. The caller was repaired at `3a8d15185`; a
refusal that names its reason is what survives the NEXT caller, and until 2026-09-21 this accessor
did not have one.

DEFECT 2 -- A SURVEY THAT REPORTS ZERO BECAUSE IT CANNOT SEE. `tools/conditional_registration_survey`
reports how many `advance`-like calls sit outside their own registration's guard. It currently
reports ZERO live instances, and that number is worth exactly nothing unless the walk is shown to
fire on the one instance we know existed. The proof runs it against `simulation/run_phase2b.py` at
`3a8d15185^` and at HEAD and demands they classify differently.

Both legs are written to fail on the pre-repair code and were checked against it.
"""
from __future__ import annotations

import datetime as dt

import pytest

from simulation.churn_journey import ChurnJourneyRegister
from tools.conditional_registration_survey import (
    _repo_root,
    prove_on_the_known_instance,
    run_survey,
)


def test_the_rare_branch_is_reachable_at_all_before_anything_asserts_what_it_says():
    """A guard that refuses EVERYTHING passes every test of what it refuses. So: the register must
    serve a REGISTERED account and refuse an unregistered one, in one control over the partition."""
    reg = ChurnJourneyRegister()
    reg.register_customer("SYN-KNOWN", tenure_years=2.0)

    served = reg.advance("SYN-KNOWN", dt.date(2020, 1, 1))
    assert served is not None, "the register refuses even a registered account: the test below is vacuous"

    with pytest.raises(KeyError):
        reg.advance("SYN-ABSENT", dt.date(2020, 1, 1))


def test_advance_refuses_an_unregistered_account_by_name_and_not_with_a_bare_key():
    """MUTATION: restore `journey = self._journeys[customer_id]` with no try/except and this reds --
    a bare KeyError stringifies to just the quoted key, so every assertion below fails."""
    reg = ChurnJourneyRegister()
    reg.register_customer("SYN-KNOWN", tenure_years=1.0)

    with pytest.raises(KeyError) as excinfo:
        reg.advance("SYN-2016-008", dt.date(2017, 3, 29))

    message = str(excinfo.value)
    assert "SYN-2016-008" in message, "the refusal must name the account it refused"
    assert "register_customer" in message, (
        "the refusal must name what should have happened first -- without it the reader has the "
        "symptom and no route to the cause, which is exactly what cost the 2026-09-19 pass"
    )
    assert "1 accounts are registered" in message, (
        "the refusal must say how full the book is: an empty book and a book missing one account "
        "are different failures and the bare KeyError made them look identical"
    )


def test_the_survey_can_see_the_one_pairing_defect_we_know_existed():
    """MUTATION: make `_guard_chain` return `[]` unconditionally -- every chain compares equal, the
    pre-repair site classifies PAIRED, and `proven` goes False. The survey's zero is only worth
    reading because this leg is green."""
    proof = prove_on_the_known_instance(_repo_root())
    assert proof["proven"], proof["reason"]
    assert proof["pre_repair_narrower"] >= 1, (
        "the walk cannot see the pre-repair defect, so its count of live ones is uninterpretable"
    )
    assert proof["post_repair_narrower"] == 0, (
        "the walk still calls the REPAIRED site a defect -- it is reading the "
        "`if get_journey(x) is None:` idempotence guard as a narrowing one"
    )


def test_the_survey_reports_its_own_blind_spot_rather_than_dropping_it():
    """A survey that silently discards the receivers it could not type reads as 'covered
    everything'. MUTATION: drop the `unbound` append and this reds.

    Keyed to the PROPERTY -- that the uncovered set is counted and non-empty -- and not to today's
    figure, which moves with every call site anyone adds."""
    result = run_survey(_repo_root())

    assert result["unbound_receiver_sites"] > 0, (
        "no receiver at all was untypeable, which on a tree this size means the counter is not "
        "wired rather than that coverage is total"
    )
    assert set(result["counts"]) == {"NARROWER", "PAIRED", "UNSETTLED"}
    assert result["call_sites"] == sum(result["counts"].values()), (
        "a verdict bucket has gone missing from the totals"
    )
