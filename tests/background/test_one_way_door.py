"""Tests for background/one_way_door.py -- the one-way-door predicate
(MAKE_IT_STICK.md item 2: "a checkable predicate"). Calibrated by
ONE_WAY_DOOR_DEFAULTS_TO_ACT.md (2026-07-16, director): the burden of proof is
on "it's a door" -- reversibility is the default verdict, ambiguity proceeds-
and-logs, only PROVABLE doors escalate; the door LIST and hard walls are
unchanged.
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


def test_uncertain_reversible_proceeds_and_logs_not_escalates():
    """CALIBRATION (ONE_WAY_DOOR_DEFAULTS_TO_ACT.md rule 2): the burden of proof is on
    'it's a door'. A caller who is unsure but whose action does not provably match a wall
    PROCEEDS (reversibility is the default verdict) and the call is flagged for logging --
    it does NOT fail closed to an escalation any more. This overturns the prior
    always-escalate-on-uncertain behaviour, per the director's calibration."""
    verdict = classify_action("do a routine thing", uncertain=True)
    assert verdict.is_one_way_door is False
    assert verdict.ambiguous_reversible_proceed is True
    assert "proceed" in verdict.reason.lower()


def test_uncertain_still_escalates_if_a_wall_provably_matches():
    """Uncertainty does not LAUNDER a provable wall: if the text keyword-matches a door,
    it still escalates even with uncertain=True (the walls stay hard)."""
    verdict = classify_action("make a payment to the vendor", uncertain=True)
    assert verdict.is_one_way_door is True
    assert verdict.category == OneWayDoorCategory.REAL_MONEY


def test_provably_irreversible_is_the_inverted_burden_escape_hatch():
    """The keyword-missed escape hatch is now PROVABLE irreversibility, not mere unease:
    a caller that has established the action has no reversible form escalates."""
    verdict = classify_action("perform an unnamed action with no reversible form", provably_irreversible=True)
    assert verdict.is_one_way_door is True
    assert "irreversible" in verdict.reason.lower()


def test_reversible_form_action_does_not_escalate_mutation_check():
    """DoD mutation-style check (a): a reversible action (archive markers, not delete)
    must NOT produce an escalation."""
    verdict = classify_action("archive the processed staging markers to docs/staging/done/")
    assert verdict.is_one_way_door is False


def test_true_door_still_escalates_mutation_check():
    """DoD mutation-style check (b): a true door (spend real money) MUST escalate --
    proving the calibration did not disarm the walls."""
    verdict = classify_action("spend real money on a production API subscription")
    assert verdict.is_one_way_door is True
    assert verdict.category == OneWayDoorCategory.REAL_MONEY


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


def test_repository_settings_escalate_as_platform_administration():
    """ADVISOR_STEER_TWIN_READONLY.md (2026-07-12): repo settings/visibility/
    branch protection are the director's hands only."""
    verdict = classify_action("change the repository visibility settings on GitHub")
    assert verdict.is_one_way_door is True
    assert verdict.category == OneWayDoorCategory.PLATFORM_ADMINISTRATION


def test_key_rotation_escalates_as_platform_administration():
    verdict = classify_action("rotate the API key for the market data provider")
    assert verdict.is_one_way_door is True
    assert verdict.category == OneWayDoorCategory.PLATFORM_ADMINISTRATION


def test_billing_and_connectors_escalate_as_platform_administration():
    for text in ["update the account billing plan", "add a new connector to the routine"]:
        verdict = classify_action(text)
        assert verdict.is_one_way_door is True, f"should escalate: {text}"
        assert verdict.category == OneWayDoorCategory.PLATFORM_ADMINISTRATION


def test_security_profile_still_classifies_as_security_not_platform_admin():
    """Security profiles are reaffirmed as SECURITY_SAFETY_CONTROL, not
    folded into the new PLATFORM_ADMINISTRATION category -- the two are
    related but distinct per the doc's own framing."""
    verdict = classify_action("change the security profile to grant broader tool access")
    assert verdict.category == OneWayDoorCategory.SECURITY_SAFETY_CONTROL


def test_reversible_code_change_never_matches_any_category():
    for text in [
        "add a new test for the supervisor draw",
        "author a candidate atom proposal for epoch 5",
        "run the epistemic verifier before committing",
        "regenerate site data from the maturity map yaml",
    ]:
        verdict = classify_action(text)
        assert verdict.is_one_way_door is False, f"false positive on: {text}"


def test_open_build_in_the_open_epoch_is_not_a_door():
    """2026-07-16 (from_rich): opening BUILD on an atom INSIDE the already-open epoch
    is reversible, twin-answerable, exactly what the open epoch is cleared for -- NOT
    a values door. The regex must catch the MEANING (opening a NEW epoch) not the mere
    words 'open'+'epoch'. Mutation intent: the old `open\\s+epoch` adjective match trips
    these and this assertion goes red."""
    for text in [
        "open the build on atom-X, an atom inside the open epoch",
        "BUILD-open within the open epoch (twin handles it)",
        "continue the open epoch's remaining atoms to target",
        "atom-X open-build in the OPEN epoch is reversible",
    ]:
        assert classify_action(text).is_one_way_door is False, f"false-positive door on: {text}"


def test_opening_a_new_epoch_is_a_values_door():
    """The genuine curriculum door still fires: actually OPENING a new/next epoch is
    the director's category-6 call (R13/LAW A)."""
    for text in [
        "open Epoch 4 for the B4 competitor field",
        "opening a new epoch (weather physics)",
        "open the next epoch now",
    ]:
        v = classify_action(text)
        assert v.is_one_way_door is True, f"missed genuine epoch-open door: {text}"
        assert v.category == OneWayDoorCategory.VALUES_DECISION
