"""The account classes that mean "the company FOUND this one" are spelled in three places.

THE DEFECT THIS FIRES ON. `tools/decisions_by_account_class.FOUND_ACCOUNT_CLASSES` holds its own
literal tuple rather than importing `run_value_cycle_ab._FOUND_ACCOUNT_CLASSES`, and that is
deliberate: the module is on the site publisher's import graph and `run_value_cycle_ab` drags
`simulation` onto it. A second literal is one name and two answers, which is this project's most
expensive recurring shape -- so the pairing is HELD HERE instead of being trusted.

`tools/generate_value_arms_data._WON_OR_DRAWN_CLASSES` is the third copy, on the same page, and it
is in scope for the same reason: a run whose class was renamed in two of the three would publish a
decision population over one set of classes and a priced count over another, and the two figures
would sit in the same sentence.

WHAT IT DOES NOT ASSERT: that the classes are today's two, or what they are named. The subject is
AGREEMENT. Add a third found class to the world's vocabulary and this control asks only that all
three spellings gain it.
"""
from __future__ import annotations

from tools.decisions_by_account_class import FOUND_ACCOUNT_CLASSES
from tools.generate_value_arms_data import _WON_OR_DRAWN_CLASSES
from tools.run_value_cycle_ab import _FOUND_ACCOUNT_CLASSES


def test_all_three_spellings_of_the_found_classes_agree():
    """MUTATION: drop or misspell one entry in any of the three tuples -> this reds, naming which.

    Sets, not sequences: the order of the two is meaningless and pinning it would make this a
    control about a literal's layout. What is load-bearing is membership.
    """
    producer = set(_FOUND_ACCOUNT_CLASSES)
    derived = set(FOUND_ACCOUNT_CLASSES)
    publisher = set(_WON_OR_DRAWN_CLASSES)
    assert producer == derived, (
        "the artefact producer and the per-term decision population disagree about which classes "
        "mean the company FOUND the account: producer-only {}, derived-only {}".format(
            sorted(producer - derived), sorted(derived - producer)))
    assert producer == publisher, (
        "the artefact producer and the page publisher disagree: producer-only {}, "
        "publisher-only {}".format(sorted(producer - publisher), sorted(publisher - producer)))


def test_the_found_classes_are_a_subset_of_the_worlds_own_acquisition_vocabulary():
    """MUTATION: add a found class the world can never write -> this reds.

    `ACCOUNT_CLASS_BY_ACQUISITION_TYPE` is the world's own `acquisition_type` field mapped to a
    class name; a "found" class outside its values is a class no roster can ever produce, so every
    share computed over it would be a share over an empty population that reads as a real one.
    The founder class is deliberately NOT in that map -- nothing acquired a founder account -- so
    this control would also catch the founder class being counted as found.
    """
    from tools.run_value_cycle_ab import (
        ACCOUNT_CLASS_BY_ACQUISITION_TYPE,
        FOUNDER_ACCOUNT_CLASS,
    )

    writable = set(ACCOUNT_CLASS_BY_ACQUISITION_TYPE.values())
    assert set(FOUND_ACCOUNT_CLASSES) <= writable, (
        "found class(es) {} are outside the world's own acquisition vocabulary {}, so no roster "
        "can produce them and every population counted over them is empty".format(
            sorted(set(FOUND_ACCOUNT_CLASSES) - writable), sorted(writable)))
    assert FOUNDER_ACCOUNT_CLASS not in FOUND_ACCOUNT_CLASSES, (
        "the founder class is counted as FOUND -- the enterprise-value claim is about the "
        "customers the method finds, and folding in the accounts the company started with is the "
        "flattering answer produced by one extra tuple entry")
