import datetime as dt
import pytest
from company.regulatory.network_code_modification_register import (
    IndustryCode, ModificationStatus, ImpactLevel, BallotPosition,
    NetworkCodeModificationRecord, NetworkCodeModificationRegister,
    _IMPLEMENTATION_WARNING_DAYS,
)

RAISED = dt.date(2024, 1, 10)
AS_OF = dt.date(2024, 6, 1)


def make_record(status=ModificationStatus.RAISED, impact=ImpactLevel.NONE):
    return NetworkCodeModificationRecord(
        record_id="NCM-00001", code=IndustryCode.BSC,
        modification_ref="BSC P354", short_title="Faster Settlement",
        raised_date=RAISED, status=status, impact_level=impact)


class TestNetworkCodeModificationRecord:
    def test_is_active_raised(self):
        assert make_record().is_active
    def test_is_active_consultation(self):
        assert make_record(ModificationStatus.CONSULTATION).is_active
    def test_is_active_ballot(self):
        assert make_record(ModificationStatus.BALLOT).is_active
    def test_is_active_impl_date_set(self):
        assert make_record(ModificationStatus.IMPLEMENTATION_DATE_SET).is_active
    def test_is_not_active_implemented(self):
        assert not make_record(ModificationStatus.IMPLEMENTED).is_active
    def test_is_not_active_rejected(self):
        assert not make_record(ModificationStatus.REJECTED).is_active
    def test_is_high_impact_high(self):
        assert make_record(impact=ImpactLevel.HIGH).is_high_impact
    def test_is_high_impact_critical(self):
        assert make_record(impact=ImpactLevel.CRITICAL).is_high_impact
    def test_is_not_high_impact_medium(self):
        assert not make_record(impact=ImpactLevel.MEDIUM).is_high_impact
    def test_is_implementation_due_soon_within_window(self):
        r = NetworkCodeModificationRecord(
            record_id="X", code=IndustryCode.BSC,
            modification_ref="P354", short_title="Test",
            raised_date=RAISED, status=ModificationStatus.IMPLEMENTATION_DATE_SET,
            implementation_date=AS_OF + dt.timedelta(days=_IMPLEMENTATION_WARNING_DAYS - 1))
        assert r.is_implementation_due_soon(AS_OF)
    def test_is_not_due_soon_when_distant(self):
        r = NetworkCodeModificationRecord(
            record_id="X", code=IndustryCode.BSC,
            modification_ref="P354", short_title="Test",
            raised_date=RAISED, status=ModificationStatus.IMPLEMENTATION_DATE_SET,
            implementation_date=AS_OF + dt.timedelta(days=_IMPLEMENTATION_WARNING_DAYS + 1))
        assert not r.is_implementation_due_soon(AS_OF)
    def test_is_not_due_soon_when_implemented(self):
        r = NetworkCodeModificationRecord(
            record_id="X", code=IndustryCode.BSC,
            modification_ref="P354", short_title="Test",
            raised_date=RAISED, status=ModificationStatus.IMPLEMENTED,
            implementation_date=AS_OF + dt.timedelta(days=30))
        assert not r.is_implementation_due_soon(AS_OF)
    def test_is_not_due_soon_when_no_date(self):
        assert not make_record().is_implementation_due_soon(AS_OF)
    def test_days_to_implementation(self):
        r = NetworkCodeModificationRecord(
            record_id="X", code=IndustryCode.BSC,
            modification_ref="P354", short_title="Test",
            raised_date=RAISED, status=ModificationStatus.IMPLEMENTATION_DATE_SET,
            implementation_date=AS_OF + dt.timedelta(days=45))
        assert r.days_to_implementation(AS_OF) == 45
    def test_days_to_implementation_none_when_no_date(self):
        assert make_record().days_to_implementation(AS_OF) is None
    def test_modification_summary(self):
        s = make_record().modification_summary()
        assert "NCM-00001" in s and "BSC" in s and "Faster Settlement" in s
    def test_frozen(self):
        r = make_record()
        with pytest.raises((AttributeError, TypeError)):
            r.status = ModificationStatus.IMPLEMENTED


class TestNetworkCodeModificationRegister:
    def setup_method(self):
        self.reg = NetworkCodeModificationRegister()

    def test_track_modification_stored(self):
        r = self.reg.track_modification(IndustryCode.BSC, "P354", "Faster Settlement", RAISED)
        assert r.status == ModificationStatus.RAISED

    def test_auto_id_increments(self):
        r1 = self.reg.track_modification(IndustryCode.BSC, "P354", "Faster Settlement", RAISED)
        r2 = self.reg.track_modification(IndustryCode.UNC, "UNC0678", "Gas Flow Reform", RAISED)
        assert r1.record_id != r2.record_id

    def test_assess_impact(self):
        r = self.reg.track_modification(IndustryCode.BSC, "P354", "Test", RAISED)
        assessed = self.reg.assess_impact(r.record_id, ImpactLevel.HIGH)
        assert assessed.impact_level == ImpactLevel.HIGH

    def test_record_ballot_position(self):
        r = self.reg.track_modification(IndustryCode.BSC, "P354", "Test", RAISED)
        ballot = self.reg.record_ballot_position(r.record_id, BallotPosition.SUPPORT)
        assert ballot.status == ModificationStatus.BALLOT
        assert ballot.ballot_position == BallotPosition.SUPPORT

    def test_set_implementation_date(self):
        r = self.reg.track_modification(IndustryCode.BSC, "P354", "Test", RAISED)
        impl_date = dt.date(2024, 10, 1)
        impl = self.reg.set_implementation_date(r.record_id, impl_date)
        assert impl.status == ModificationStatus.IMPLEMENTATION_DATE_SET
        assert impl.implementation_date == impl_date

    def test_mark_implemented(self):
        r = self.reg.track_modification(IndustryCode.BSC, "P354", "Test", RAISED)
        done = self.reg.mark_implemented(r.record_id, dt.date(2024, 10, 5))
        assert done.status == ModificationStatus.IMPLEMENTED
        assert done.implemented_date == dt.date(2024, 10, 5)

    def test_reject(self):
        r = self.reg.track_modification(IndustryCode.BSC, "P354", "Test", RAISED)
        rej = self.reg.reject(r.record_id)
        assert rej.status == ModificationStatus.REJECTED

    def test_update_missing_raises(self):
        with pytest.raises(KeyError):
            self.reg.reject("NCM-99999")

    def test_active_modifications(self):
        r = self.reg.track_modification(IndustryCode.BSC, "P354", "Test", RAISED)
        self.reg.reject(r.record_id)
        self.reg.track_modification(IndustryCode.UNC, "UNC0678", "Gas Reform", RAISED)
        assert len(self.reg.active_modifications()) == 1

    def test_high_impact(self):
        r = self.reg.track_modification(IndustryCode.BSC, "P354", "Test", RAISED)
        self.reg.assess_impact(r.record_id, ImpactLevel.HIGH)
        self.reg.track_modification(IndustryCode.UNC, "UNC0678", "Gas Reform", RAISED)
        assert len(self.reg.high_impact()) == 1

    def test_due_soon(self):
        r = self.reg.track_modification(IndustryCode.BSC, "P354", "Test", RAISED)
        impl_date = AS_OF + dt.timedelta(days=30)
        self.reg.set_implementation_date(r.record_id, impl_date)
        assert len(self.reg.due_soon(AS_OF)) == 1

    def test_by_code(self):
        self.reg.track_modification(IndustryCode.BSC, "P354", "Test1", RAISED)
        self.reg.track_modification(IndustryCode.UNC, "UNC0678", "Test2", RAISED)
        assert len(self.reg.by_code(IndustryCode.BSC)) == 1

    def test_pending_ballot(self):
        r = self.reg.track_modification(IndustryCode.BSC, "P354", "Test", RAISED)
        self.reg.record_ballot_position(r.record_id, BallotPosition.SUPPORT)
        self.reg.track_modification(IndustryCode.UNC, "UNC0678", "Gas Reform", RAISED)
        assert len(self.reg.pending_ballot()) == 1

    def test_modification_summary(self):
        self.reg.track_modification(IndustryCode.BSC, "P354", "Test", RAISED)
        s = self.reg.modification_summary(AS_OF)
        assert "1 modifications" in s and "1 active" in s

    def test_empty_summary(self):
        s = self.reg.modification_summary(AS_OF)
        assert "0 modifications" in s
