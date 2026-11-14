import datetime as dt

import pytest

from company.billing.winter_moratorium import (
    DisconnectionRisk,
    MoratoriumRecord,
    MoratoriumType,
    WinterMoratoriumRegister,
    is_winter_period,
)
from company.regulatory.priority_services_register import HouseholdComposition, PSRCategory


def make_record(account_id="A1",
                mtype=MoratoriumType.WINTER_DOMESTIC,
                start=dt.date(2023, 11, 1),
                end=dt.date(2024, 3, 31),
                reason="winter protection"):
    return MoratoriumRecord(
        account_id=account_id, moratorium_type=mtype,
        start_date=start, end_date=end, reason=reason,
    )


class TestIsWinterPeriod:
    def test_november_is_winter(self):
        assert is_winter_period(dt.date(2023, 11, 15)) is True

    def test_december_is_winter(self):
        assert is_winter_period(dt.date(2023, 12, 25)) is True

    def test_january_is_winter(self):
        assert is_winter_period(dt.date(2024, 1, 15)) is True

    def test_march_is_winter(self):
        assert is_winter_period(dt.date(2024, 3, 31)) is True

    def test_april_is_not_winter(self):
        assert is_winter_period(dt.date(2024, 4, 1)) is False

    def test_june_is_not_winter(self):
        assert is_winter_period(dt.date(2024, 6, 15)) is False

    def test_october_is_winter_because_the_published_winter_starts_there(self):
        # This leg asserted the opposite until 2026-10-07: a Nov-Mar winter, one month short
        # of the commons' October-March in the direction that removes protection.
        assert is_winter_period(dt.date(2023, 10, 1)) is True

    def test_september_is_not_winter(self):
        assert is_winter_period(dt.date(2023, 9, 30)) is False


class TestMoratoriumRecord:
    def test_is_active_within_dates(self):
        r = make_record(start=dt.date(2023, 11, 1), end=dt.date(2024, 3, 31))
        assert r.is_active(dt.date(2024, 1, 15)) is True

    def test_is_active_false_before_start(self):
        r = make_record(start=dt.date(2023, 11, 1))
        assert r.is_active(dt.date(2023, 10, 1)) is False

    def test_is_active_false_after_end(self):
        r = make_record(start=dt.date(2023, 11, 1), end=dt.date(2024, 3, 31))
        assert r.is_active(dt.date(2024, 4, 1)) is False

    def test_is_active_true_ongoing_none_end(self):
        r = make_record(end=None, mtype=MoratoriumType.VULNERABLE_YEAR_ROUND)
        assert r.is_active(dt.date(2025, 7, 1)) is True

    def test_protection_status_protected(self):
        r = make_record()
        assert r.protection_status(dt.date(2024, 1, 1)) == DisconnectionRisk.PROTECTED

    def test_protection_status_no_risk_after_end(self):
        r = make_record(end=dt.date(2024, 3, 31))
        assert r.protection_status(dt.date(2024, 5, 1)) == DisconnectionRisk.NO_RISK

    def test_frozen(self):
        r = make_record()
        with pytest.raises((AttributeError, TypeError)):
            r.account_id = "X"


class TestWinterMoratoriumRegister:
    def test_register_and_active(self):
        reg = WinterMoratoriumRegister()
        reg.register(make_record())
        assert len(reg.active_protections(dt.date(2024, 1, 1))) == 1

    def test_end_moratorium(self):
        reg = WinterMoratoriumRegister()
        reg.register(make_record(account_id="A1", end=None,
                                 mtype=MoratoriumType.DEBT_MORATORIUM))
        result = reg.end_moratorium("A1", dt.date(2024, 4, 1))
        assert result is not None
        assert result.end_date == dt.date(2024, 4, 1)
        assert not reg.is_protected("A1", dt.date(2024, 5, 1))

    def test_is_protected_true(self):
        reg = WinterMoratoriumRegister()
        reg.register(make_record(account_id="A1"))
        assert reg.is_protected("A1", dt.date(2024, 1, 1)) is True

    def test_is_protected_false_after_end(self):
        reg = WinterMoratoriumRegister()
        reg.register(make_record(account_id="A1", end=dt.date(2024, 3, 31)))
        assert reg.is_protected("A1", dt.date(2024, 5, 1)) is False

    def test_can_disconnect_false_protected(self):
        reg = WinterMoratoriumRegister()
        reg.register(make_record(account_id="A1"))
        assert reg.can_disconnect("A1", dt.date(2024, 1, 1), categories=()) is False

    def test_the_licence_rule_is_asked_and_every_answer_is_reachable(self):
        """One control over the partition: a household with no needs category in winter MAY
        be disconnected (the blanket winter rule this module used to hold is in no licence
        condition), a pensionable-age household of unknown composition may NOT, and one
        living alone may not either. A version that refused everything passes the last two.
        """
        reg = WinterMoratoriumRegister()
        jan = dt.date(2024, 1, 15)
        assert reg.can_disconnect("B1", jan, categories=()) is True
        assert reg.can_disconnect(
            "B1", jan, categories=(PSRCategory.PENSIONABLE_AGE,)) is False
        assert reg.can_disconnect(
            "B1", jan, categories=(PSRCategory.PENSIONABLE_AGE,),
            household=HouseholdComposition.LIVES_ALONE) is False

    def test_october_protects_where_the_old_november_start_did_not(self):
        reg = WinterMoratoriumRegister()
        assert reg.can_disconnect(
            "B1", dt.date(2023, 10, 15), categories=(PSRCategory.PENSIONABLE_AGE,),
            household=HouseholdComposition.LIVES_ALONE) is False

    def test_the_safety_net_holds_all_year_and_nothing_else_is_swept_in(self):
        """The company's own Safety Net (commons S5, adopted on canon M3's floor, 2026-11-14).

        The licence decider says a July household on home oxygen, disabled, chronically sick or
        of pensionable age has no licence protection; this supplier still does not disconnect it.
        One control over the partition: each Safety Net category blocks in July and in January,
        while no category still may be disconnected in July -- so a version that refused
        everything reds as surely as one that dropped the net. (A category outside the six was
        the permitted leg until C32's sixth pass; it now blocks, see the test below.)
        """
        from company.billing.winter_moratorium import SAFETY_NET_CATEGORIES
        from company.regulatory.priority_services_register import disconnection_protection

        reg = WinterMoratoriumRegister()
        jul, jan = dt.date(2024, 7, 15), dt.date(2024, 1, 15)
        assert SAFETY_NET_CATEGORIES
        for category in SAFETY_NET_CATEGORIES:
            # The licence alone would permit it in July: the net is what blocks.
            assert disconnection_protection((category,), as_of=jul).may_disconnect
            assert reg.can_disconnect("S1", jul, categories=(category,)) is False
            assert reg.can_disconnect("S1", jan, categories=(category,)) is False
        assert reg.can_disconnect("S1", jul, categories=()) is True

    def test_categories_must_be_stated(self):
        reg = WinterMoratoriumRegister()
        with pytest.raises(TypeError):
            reg.can_disconnect("B1", dt.date(2024, 7, 1))

    def test_vulnerable_protections(self):
        reg = WinterMoratoriumRegister()
        reg.register(make_record(account_id="A1", end=None,
                                 mtype=MoratoriumType.VULNERABLE_YEAR_ROUND))
        reg.register(make_record(account_id="A2"))
        assert len(reg.vulnerable_protections(dt.date(2024, 7, 1))) == 1

    def test_winter_protections(self):
        reg = WinterMoratoriumRegister()
        reg.register(make_record(account_id="A1"))
        assert len(reg.winter_protections(dt.date(2024, 1, 1))) == 1
        assert len(reg.winter_protections(dt.date(2024, 7, 1))) == 0

    def test_summary_keys(self):
        reg = WinterMoratoriumRegister()
        s = reg.moratorium_summary(dt.date(2024, 1, 1))
        for k in ("total_records", "active_protections", "vulnerable_year_round",
                  "winter_domestic", "in_winter_period"):
            assert k in s

    def test_summary_winter_flag(self):
        reg = WinterMoratoriumRegister()
        assert reg.moratorium_summary(dt.date(2024, 1, 1))["in_winter_period"] is True
        assert reg.moratorium_summary(dt.date(2024, 7, 1))["in_winter_period"] is False


def test_the_safety_net_reaches_what_the_record_only_suggests():
    """The net was read on ESTABLISHED categories only, so in July a household whose only
    evidence was a code 26 ("oxygen use"), a code 22, a PSR registration naming no need, an
    agent's `serious_illness` or `elderly` flag, or a birth date making it 80 was permitted:
    the licence permits all six then, and the counterfactual that weighs them ran against the
    licence alone (C32 fifth Expert Hour, 2026-11-14).

    One control over the partition: each of those is refused in July by the company while the
    licence still permits it (so the licence answer stays readable), and a household with no
    evidence, or a birth date making it 39, is still permitted in July. A decider that refused
    everything reds on the second half. Language support, job loss and bereavement were on the
    permitted side until C32's sixth pass found each was a Safety Net breach.
    """
    from company.crm.vulnerability_register import VulnerabilityFlag, VulnerabilityRecord
    from company.regulatory.priority_services_register import PSRRecord

    def psr(categories=(), codes=()):
        return PSRRecord(account_id="N1", categories=tuple(categories), services_enrolled=(),
                         registration_date=dt.date(2020, 1, 1),
                         review_due_date=dt.date(2030, 1, 1), needs_codes=tuple(codes))

    def flagged(*flags):
        return VulnerabilityRecord("N1", tuple(flags), dt.date(2020, 1, 1))

    reg = WinterMoratoriumRegister()
    jul = dt.date(2024, 7, 15)
    refused = [
        (psr(codes=(26,)), None), (psr(codes=(22,)), None), (psr(), None),
        (flagged(VulnerabilityFlag.SERIOUS_ILLNESS), None),
        (flagged(VulnerabilityFlag.ELDERLY), None),
        (flagged(), dt.date(1944, 5, 1)),
        # The commitment's "health" and "age" grounds (fifth pass, item 5).
        (psr(categories=(PSRCategory.MENTAL_HEALTH,), codes=(30,)), None),
        (psr(categories=(PSRCategory.CHILD_UNDER_5,), codes=(29,)), None),
        # C32's sixth pass, items 1 to 3: the welfare test is live and unassessed.
        (psr(categories=(PSRCategory.LANGUAGE_SUPPORT,), codes=(17,)), None),
        (flagged(VulnerabilityFlag.JOB_LOSS), None),
        (flagged(VulnerabilityFlag.BEREAVEMENT), None),
    ]
    permitted = [
        (flagged(), None),
        (flagged(), dt.date(1985, 5, 1)),
    ]
    for record, born in refused + permitted:
        assert record.disconnection_protection(jul, date_of_birth=born).may_disconnect
    assert [reg.can_disconnect("N1", jul, record=r, date_of_birth=b) for r, b in refused] \
        == [False] * len(refused)
    assert [reg.can_disconnect("N1", jul, record=r, date_of_birth=b) for r, b in permitted] \
        == [True] * len(permitted)


def test_any_vulnerability_evidence_held_blocks_a_summer_disconnection():
    """C32's sixth blind pass, items 1 to 3. The net applied S5's welfare test as six
    categories, so on 15 Jul 2024 the company permitted disconnecting a blind household
    (codes 8, 9), a deaf one (35), one on post-hospital recovery or any other uncategorised
    need, and one an agent had flagged bereaved, out of work, in payment difficulty or in fuel
    poverty. The company holds no welfare assessment, so any evidence it holds now reads
    CANNOT_DETERMINE (commons s.4).

    One control over the whole partition, in July and January: every needs code on the
    published list, every register category and every agent flag is refused, and a household
    holding no evidence at all is permitted, so a refuse-everything decider reds. The six net
    categories stay PROHIBITED and the rest are CANNOT_DETERMINE, because a future welfare
    assessment may clear the second and never the first.
    """
    from company.billing.winter_moratorium import (
        SAFETY_NET_CATEGORIES,
        safety_net_on_record,
        safety_net_protection,
    )
    from company.crm.vulnerability_register import VulnerabilityFlag, VulnerabilityRecord
    from company.regulatory.priority_services_register import (
        DisconnectionProtection,
        NeedsCodeEvidence,
        PSRRecord,
        needs_code_grade,
    )

    def graded(code):
        try:
            return needs_code_grade(code)
        except ValueError:
            return None

    codes = [c for c in range(1, 100) if graded(c) is not None]
    uncategorised = [c for c in codes if graded(c).category is None]
    assert len(codes) > 20 and uncategorised

    def psr(code):
        m = graded(code)
        held = (m.category,) if m.evidence is NeedsCodeEvidence.EVIDENCED else ()
        return PSRRecord(account_id="E1", categories=held, services_enrolled=(),
                         registration_date=dt.date(2020, 1, 1),
                         review_due_date=dt.date(2030, 1, 1), needs_codes=(code,))

    reg = WinterMoratoriumRegister()
    nobody = VulnerabilityRecord("E1", (), dt.date(2020, 1, 1))
    for day in (dt.date(2024, 7, 15), dt.date(2024, 1, 15)):
        permitted = [c for c in codes if reg.can_disconnect("E1", day, record=psr(c))]
        permitted += [c.value for c in PSRCategory
                      if reg.can_disconnect("E1", day, categories=(c,))]
        permitted += [f.value for f in VulnerabilityFlag if reg.can_disconnect(
            "E1", day, record=VulnerabilityRecord("E1", (f,), dt.date(2020, 1, 1)))]
        assert permitted == [], (day, permitted)
        assert reg.can_disconnect("E1", day, categories=()) is True
        assert reg.can_disconnect("E1", day, record=nobody) is True
    jul = dt.date(2024, 7, 15)
    assert {c for c in PSRCategory
            if safety_net_protection((c,), as_of=jul).protection
            is DisconnectionProtection.PROHIBITED} == SAFETY_NET_CATEGORIES
    assert safety_net_on_record(
        VulnerabilityRecord("E1", (VulnerabilityFlag.JOB_LOSS,), jul), jul
    ).protection is DisconnectionProtection.CANNOT_DETERMINE


def test_exactly_one_of_categories_or_record():
    reg = WinterMoratoriumRegister()
    with pytest.raises(TypeError):
        reg.can_disconnect("B1", dt.date(2024, 7, 1), categories=(), record=object())
