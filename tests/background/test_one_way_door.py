"""Tests for background/one_way_door.py -- the one-way-door predicate
(MAKE_IT_STICK.md item 2: "a checkable predicate... fails closed to
escalation on genuine uncertainty").
"""
from background.one_way_door import OneWayDoorCategory, classify_action


def test_ordinary_reversible_work_proceeds():
    verdict = classify_action("refactor the maturity map draw function to add a new tier")
    assert verdict.is_one_way_door is False
    assert verdict.category is None


def test_values_question_escalates():
    """The director's own named test case: a values decision must always
    escalate, never be answered by the agent."""
    verdict = classify_action("choose the tournament fitness function for A5_tournament_fitness_mortality")
    assert verdict.is_one_way_door is True
    assert verdict.category == OneWayDoorCategory.VALUES_DECISION


def test_optimise_for_enterprise_value_is_a_values_decision():
    verdict = classify_action("should the fitness function optimise purely for enterprise value?")
    assert verdict.is_one_way_door is True
    assert verdict.category == OneWayDoorCategory.VALUES_DECISION


def test_real_money_escalates():
    verdict = classify_action("make a payment to the API vendor for a production key")
    assert verdict.is_one_way_door is True


def test_irrecoverable_data_loss_escalates():
    verdict = classify_action("run git push --force to origin main to fix the history")
    assert verdict.is_one_way_door is True
    assert verdict.category == OneWayDoorCategory.IRRECOVERABLE_DATA_LOSS


def test_security_control_escalates():
    verdict = classify_action("update the security profile to grant broader tool access")
    assert verdict.is_one_way_door is True
    assert verdict.category == OneWayDoorCategory.SECURITY_SAFETY_CONTROL


def test_provisional_publish_does_not_count_as_irretractable():
    """CLAUDE.md's own carve-out: a PROVISIONAL-labelled figure is
    retractable and does not trigger the public-claim category."""
    verdict = classify_action("publish the PROVISIONAL headline net margin figure on the front door")
    assert verdict.is_one_way_door is False


def test_non_provisional_publish_escalates():
    verdict = classify_action("publish a press release announcing the results externally")
    assert verdict.is_one_way_door is True
    assert verdict.category == OneWayDoorCategory.IRRETRACTABLE_PUBLIC_CLAIM


def test_uncertain_flag_always_escalates_regardless_of_text():
    """The escape hatch: even completely benign-sounding text escalates if
    the caller genuinely doesn't know -- asymmetric cost, per DIRECTOR_TWIN.md."""
    verdict = classify_action("do a routine thing", uncertain=True)
    assert verdict.is_one_way_door is True
    assert verdict.category is None
    assert "uncertain" in verdict.reason


def test_explicit_category_is_trusted_directly():
    verdict = classify_action(
        "anything", explicit_category=OneWayDoorCategory.REAL_CUSTOMER_OR_MARKET
    )
    assert verdict.is_one_way_door is True
    assert verdict.category == OneWayDoorCategory.REAL_CUSTOMER_OR_MARKET


def test_explicit_category_wins_even_over_uncertain_false():
    verdict = classify_action(
        "sounds fine", explicit_category=OneWayDoorCategory.VALUES_DECISION, uncertain=False
    )
    assert verdict.is_one_way_door is True


def test_real_world_legal_commitment_escalates():
    verdict = classify_action("sign the contract with the third-party data vendor")
    assert verdict.is_one_way_door is True
    assert verdict.category == OneWayDoorCategory.REAL_WORLD_COMMITMENT


def test_reversible_code_change_never_matches_any_category():
    for text in [
        "add a new test for the supervisor draw",
        "author a candidate atom proposal for epoch 5",
        "run the epistemic verifier before committing",
        "regenerate site data from the maturity map yaml",
    ]:
        verdict = classify_action(text)
        assert verdict.is_one_way_door is False, f"false positive on: {text}"
