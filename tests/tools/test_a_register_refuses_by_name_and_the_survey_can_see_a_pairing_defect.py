"""Three defects, all of which this repo has actually shipped.

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

DEFECT 3 -- A DETECTOR SO NARROW ITS OWN HEADLINE HAD A FLOOR. The guard detector saw a
comprehension `if` and an enclosing `if`, and not the early-return idiom this repo actually writes,
so it called 13 accessors bare-refusing when 6 was the figure. Seven of them could not be reached
with a missing key at all, and two of those already raised a `KeyError` naming it. A count with an
unreachable floor cannot be driven to zero, so no control could key to it to prove the class shut.

Every leg is written to fail on the code that shipped the defect, and each was checked against it.
"""
from __future__ import annotations

import ast
import datetime as dt
import textwrap

import pytest

from simulation.churn_journey import ChurnJourneyRegister
from tools.conditional_registration_survey import (
    _ClassScan,
    _repo_root,
    prove_on_the_known_instance,
    run_survey,
)


def _raw_loads(source: str) -> dict:
    """Which books does the single class in `source` read raw -- i.e. can raise KeyError on?"""
    tree = ast.parse(textwrap.dedent(source))
    cls = next(n for n in ast.walk(tree) if isinstance(n, ast.ClassDef))
    return _ClassScan(cls).raw_loads


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


# --- DEFECT 3: a detector so narrow its own headline has a floor no repair can move. -------------
#
# `_membership_guarded` saw a comprehension `if` and an enclosing `if`, and not the early-return
# idiom this repo actually writes. Seven accessors that CANNOT be reached with an absent key were
# counted as raise-on-missing ones, two of them already raising a KeyError naming the key. The BARE
# headline read 13 when 6 was the true figure, and no control could key to BARE == 0 because 13 of
# it was unreachable code nobody could write.


def test_the_detector_can_still_say_UNGUARDED_before_anything_asserts_what_it_guards():
    """A guard-detector that returns True for EVERYTHING passes every leg below it.

    One control over the whole partition, per CLAUDE.md: the same book, read once behind a guard
    and once bare, must come back differently. MUTATION: `return True` at the top of
    `_membership_guarded` and this is the leg that reds."""
    guarded = _raw_loads("""
        class Book:
            def __init__(self): self._items = {}
            def add(self, k, v): self._items[k] = v
            def read(self, k):
                if k not in self._items:
                    return None
                return self._items[k]
    """)
    bare = _raw_loads("""
        class Book:
            def __init__(self): self._items = {}
            def add(self, k, v): self._items[k] = v
            def read(self, k):
                return self._items[k]
    """)

    assert "_items" in bare, (
        "an unguarded raw read is not reported as one, so the detector cannot see the defect class "
        "at all and every 'this shape is guarded' leg below is vacuous"
    )
    assert "_items" not in guarded, (
        "the early-return guard is still unseen -- this is the 13-vs-6 floor under the BARE headline"
    )


@pytest.mark.parametrize("leaving", ["return None", "raise KeyError(f'no {k} in the book')"])
def test_an_early_leave_on_absence_is_a_guard_whether_it_returns_or_raises(leaving):
    """The two shapes in the live tree. `issue_alert` and `add_contract` use the raise form and
    ALREADY name the key -- counting them as the bare-refusal defect pointed the reader at code
    that was already right."""
    loads = _raw_loads(f"""
        class Book:
            def __init__(self): self._items = {{}}
            def add(self, k, v): self._items[k] = v
            def read(self, k):
                if k not in self._items:
                    {leaving}
                return self._items[k]
    """)
    assert "_items" not in loads, f"an early `{leaving}` on absence still reads as raise-on-missing"


def test_a_PRESENCE_test_that_leaves_is_not_a_guard_it_is_the_defect_inverted():
    """THE FAIL-OPEN THE WIDENING COULD HAVE SHIPPED, and the reason this leg reads the operator
    instead of the characters.

    `if k in self._items: return` followed by `self._items[k]` matches the textual needle
    `in self._items` exactly as the real guard does -- and it leaves the read reachable on
    PRECISELY the paths where it raises. Widening on text would have moved this accessor out of the
    catalogue while making it the worst instance in it.

    MUTATION: replace `_tests_absence_from`'s body with `return f'in self.{book}' in
    ast.unparse(test)` and this reds while every other leg stays green."""
    loads = _raw_loads("""
        class Book:
            def __init__(self): self._items = {}
            def add(self, k, v): self._items[k] = v
            def read(self, k):
                if k in self._items:
                    return None
                return self._items[k]
    """)
    assert "_items" in loads, (
        "a presence test that leaves was read as a guard: the detector matched the guard's TEXT "
        "and not its polarity, and this read raises on every path that reaches it"
    )


def test_absence_under_an_OR_guards_and_absence_under_an_AND_does_not():
    """`if x is None or k not in self._items: return` -- absence alone reaches the leave, so the
    read below is safe. Under `and` it does not: the read stays reachable with a missing key
    whenever the other operand is False. MUTATION: admit `ast.And` alongside `ast.Or` and the
    second half reds."""
    or_form = _raw_loads("""
        class Book:
            def __init__(self): self._items = {}
            def add(self, k, v): self._items[k] = v
            def read(self, k, x):
                if x is None or k not in self._items:
                    return None
                return self._items[k]
    """)
    and_form = _raw_loads("""
        class Book:
            def __init__(self): self._items = {}
            def add(self, k, v): self._items[k] = v
            def read(self, k, x):
                if x is None and k not in self._items:
                    return None
                return self._items[k]
    """)

    assert "_items" not in or_form, "absence on either side of an `or` still reaches the leave"
    assert "_items" in and_form, (
        "an `and` was read as a guard -- absence alone does not trigger it, so a missing key "
        "reaches the read whenever the other operand is False"
    )


def test_a_guard_body_that_falls_through_is_not_a_guard():
    """Logging the miss and carrying on is the shape that looks like a guard and is not.
    MUTATION: drop the `_always_leaves` conjunct and this reds."""
    loads = _raw_loads("""
        class Book:
            def __init__(self): self._items = {}
            def add(self, k, v): self._items[k] = v
            def read(self, k):
                if k not in self._items:
                    self._log.append(k)
                return self._items[k]
    """)
    assert "_items" in loads, (
        "a guard body that falls through was counted as protecting the read below it"
    )


def test_the_seven_accessors_that_cannot_be_reached_absent_are_out_of_the_refusal_catalogue():
    """Keyed to the PROPERTY, not to today's BARE count, which moves with every accessor anyone
    writes: an accessor that cannot be reached with an absent key is not a raise-on-missing
    accessor, so it has no refusal to name and does not belong in the catalogue at all.

    The catalogue must also still be non-empty -- an instrument that reports nothing has not proved
    the class is closed, it has stopped looking."""
    result = run_survey(_repo_root())
    refusals = result["refusals"]

    cannot_be_reached_absent = {
        "COTBook.void_days",
        "CustomerCommPreferenceRegister.can_contact",
        "PaymentBehaviourAnalytics.get_score",
        "PaymentBehaviourAnalytics.get_metrics",
        "PSRBook.update_needs",
        "TriadNotificationBook.issue_alert",
        "HedgingSchedule.add_contract",
    }
    still_listed = sorted(cannot_be_reached_absent & set(refusals))
    assert not still_listed, (
        f"{still_listed} are guarded by an early leave on absence and cannot raise KeyError, yet "
        "the survey still asks them to name a refusal they can never make"
    )
    assert refusals, (
        "the refusal catalogue is empty, which on this tree means the walk stopped finding "
        "raise-on-missing accessors rather than that there are none"
    )
