import pytest

from company.crm.cos_process import CoSProcess, CoSRegister, CoSStage, ObjectionReason


def test_initial_stage_is_requested():
    proc = CoSProcess("C1", "2022-01-01", "SUPPLIER_B", "SUPPLIER_A")
    assert proc.current_stage == CoSStage.SWITCH_REQUESTED


def test_clear_objection_window():
    proc = CoSProcess("C1", "2022-01-01", "B", "A")
    proc.clear_objection_window("2022-01-06")
    assert proc.current_stage == CoSStage.OBJECTION_CLEARED


def test_object_to_switch():
    proc = CoSProcess("C1", "2022-01-01", "B", "A")
    proc.object_to_switch("2022-01-03", ObjectionReason.DEBT)
    assert proc.is_objected is True
    assert proc.current_stage == CoSStage.OBJECTED


def test_full_happy_path():
    proc = CoSProcess("C1", "2022-01-01", "B", "A")
    proc.clear_objection_window("2022-01-06")
    proc.request_final_read("2022-01-06")
    proc.receive_final_read("2022-01-07", kwh=12_450.0)
    proc.complete("2022-01-08")
    assert proc.is_complete is True
    assert proc.current_stage == CoSStage.SWITCH_COMPLETE


def test_final_read_stored():
    proc = CoSProcess("C1", "2022-01-01", "B", "A")
    proc.clear_objection_window("2022-01-06")
    proc.request_final_read("2022-01-06")
    ev = proc.receive_final_read("2022-01-07", kwh=5000.0)
    assert abs(ev.final_read_kwh - 5000.0) < 0.01


def test_cancel_switch():
    proc = CoSProcess("C1", "2022-01-01", "B", "A")
    proc.cancel("2022-01-03")
    assert proc.is_cancelled is True


def test_open_switch_register():
    reg = CoSRegister()
    proc = reg.open_switch("C1", "2022-01-01", "B", "A")
    assert proc.account_id == "C1"
    assert len(reg.active_for_account("C1")) == 1


def test_active_excludes_completed():
    reg = CoSRegister()
    proc = reg.open_switch("C1", "2022-01-01", "B", "A")
    proc.clear_objection_window("2022-01-06")
    proc.request_final_read("2022-01-06")
    proc.receive_final_read("2022-01-07", 5000.0)
    proc.complete("2022-01-08")
    assert len(reg.active_for_account("C1")) == 0


def test_cos_summary():
    reg = CoSRegister()
    p1 = reg.open_switch("C1", "2022-01-01", "B", "A")
    p1.clear_objection_window("2022-01-06")
    p1.request_final_read("2022-01-06")
    p1.receive_final_read("2022-01-07", 5000.0)
    p1.complete("2022-01-08")
    reg.open_switch("C2", "2022-01-01", "B", "A")
    s = reg.cos_summary()
    assert s["total_switches"] == 2
    assert s["completed"] == 1
    assert s["in_progress"] == 1


# --- Phase KA depth tests ---

def test_event_id_format():
    proc = CoSProcess('C1', '2022-01-01', 'B', 'A')
    assert proc._events[0].event_id == 'C1_0'


def test_gaining_losing_supplier_stored():
    proc = CoSProcess('C1', '2022-01-01', 'SUPPLIER_B', 'SUPPLIER_A')
    ev = proc._events[0]
    assert ev.gaining_supplier == 'SUPPLIER_B'
    assert ev.losing_supplier == 'SUPPLIER_A'


def test_objection_reason_stored_in_event():
    proc = CoSProcess('C1', '2022-01-01', 'B', 'A')
    ev = proc.object_to_switch('2022-01-03', ObjectionReason.DEBT)
    assert ev.objection_reason == ObjectionReason.DEBT


def test_stage_after_receive_final_read():
    proc = CoSProcess('C1', '2022-01-01', 'B', 'A')
    proc.clear_objection_window('2022-01-06')
    proc.request_final_read('2022-01-06')
    proc.receive_final_read('2022-01-07', kwh=3000.0)
    assert proc.current_stage == CoSStage.FINAL_READ_RECEIVED


def test_is_complete_false_before_complete():
    proc = CoSProcess('C1', '2022-01-01', 'B', 'A')
    assert proc.is_complete is False


def test_is_cancelled_false_initially():
    proc = CoSProcess('C1', '2022-01-01', 'B', 'A')
    assert proc.is_cancelled is False


def test_active_excludes_cancelled():
    reg = CoSRegister()
    proc = reg.open_switch('C1', '2022-01-01', 'B', 'A')
    proc.cancel('2022-01-03')
    assert len(reg.active_for_account('C1')) == 0


def test_completed_switches_register():
    reg = CoSRegister()
    p = reg.open_switch('C1', '2022-01-01', 'B', 'A')
    p.clear_objection_window('2022-01-06')
    p.request_final_read('2022-01-06')
    p.receive_final_read('2022-01-07', 5000.0)
    p.complete('2022-01-08')
    assert len(reg.completed_switches()) == 1


def test_objected_switches_register():
    reg = CoSRegister()
    p = reg.open_switch('C1', '2022-01-01', 'B', 'A')
    p.object_to_switch('2022-01-03', ObjectionReason.CONTRACT_IN_FORCE)
    assert len(reg.objected_switches()) == 1


def test_cos_summary_objected_count():
    reg = CoSRegister()
    p = reg.open_switch('C1', '2022-01-01', 'B', 'A')
    p.object_to_switch('2022-01-03', ObjectionReason.DEBT)
    s = reg.cos_summary()
    assert s['objected'] == 1
    assert s['completed'] == 0


# --- registration-loss notices (EP12, interface/contracts/registration_loss_seam.py) ---

_CSS_CREDENTIAL = "css-provider-01::participant-credential::v1"

#: The points this test supplier holds on its book.
_BOOK = frozenset({"C1"})


def _loss_wire(point="C1", sefd="2023-03-01", seq=0, sender="CSS-PROVIDER-01",
               credential=_CSS_CREDENTIAL, notification_type="css_registration_secured_inactive",
               **extra_payload):
    """A framed notice exactly as a registration service hands it over."""
    payload = {"registration_ref": f"{point}@{sefd}", "supply_point_id": point,
               "supply_effective_from_date": sefd, **extra_payload}
    observed = "2023-02-28T17:00:00"
    return {
        "sender": sender, "credential": credential, "handed_over_at": observed,
        "envelope": {
            "notification_id": f"{sender}-{seq}",
            "notification_type": notification_type,
            "schema_version": 2, "sender": sender, "sequence": seq,
            "observed_at": observed, "valid_time": sefd, "payload": payload,
        },
    }


def test_a_loss_notice_opens_a_losing_side_process_once():
    """Defect guarded: a notice filed twice on redelivery (the stream is
    at-least-once), or filed as if this supplier had sent the request."""
    reg = CoSRegister(holds=_BOOK.__contains__)
    assert reg.receive_loss_wire(_loss_wire()) is True
    assert reg.receive_loss_wire(_loss_wire()) is False
    assert reg.losses_notified() == [{
        "supply_point_id": "C1", "registration_ref": "C1@2023-03-01",
        "supply_effective_from": "2023-03-01", "notified_on": "2023-02-28",
        "stage": CoSStage.OBJECTION_CLEARED.value,
    }]
    (proc,) = reg.active_for_account("C1")
    assert proc.gaining_supplier is None



def test_a_pending_notice_is_filed_as_pending_and_never_as_a_loss():
    """Defect guarded: an Invitation to Intervene filed as a lost registration (the switch can
    still be cancelled), or a notice of a type the contract does not declare filed as either.
    Both kinds are filed from one register, so the branch that tells them apart is taken."""
    reg = CoSRegister(holds=_BOOK.__contains__)
    pending = _loss_wire(seq=0, notification_type="css_switch_pending_invitation_to_intervene")
    assert reg.receive_loss_wire(pending) is True
    assert reg.losses_notified() == [] and reg.active_for_account("C1") == []
    assert reg.receive_loss_wire(_loss_wire(seq=1)) is True
    assert [p["supply_point_id"] for p in reg.pending_switches_notified()] == ["C1"]
    assert [r["supply_point_id"] for r in reg.losses_notified()] == ["C1"]
    with pytest.raises(ValueError, match="neither a loss"):
        reg.receive_loss_wire(_loss_wire(seq=2, notification_type="css_something_else"))

def test_the_company_refuses_a_notice_carrying_world_truth_by_name():
    """Defect guarded: the company-side belt -- a departure field riding on the
    notice is refused AS A LEAK (not merely as an unexpected key), and nothing is filed."""
    reg = CoSRegister(holds=_BOOK.__contains__)
    with pytest.raises(Exception, match="carries world truth: \\['random_roll'\\]"):
        reg.receive_loss_wire(_loss_wire(random_roll=0.42))
    assert reg.losses_notified() == []


def test_only_a_registration_service_can_report_a_lost_registration():
    """Defect guarded: an authenticated counterparty of another seam (the Bacs
    bureau) filing a loss. The control arm is the CSS notice above, which files."""
    from simulation.payment_seam_adapter import PARTICIPANT_CREDENTIAL as BACS_CREDENTIAL

    reg = CoSRegister(holds=_BOOK.__contains__)
    with pytest.raises(ValueError, match="is not a registration service"):
        reg.receive_loss_wire(_loss_wire(sender="BACS-BUREAU-01", credential=BACS_CREDENTIAL))
    assert reg.losses_notified() == []


def test_a_forged_credential_is_refused_before_anything_is_filed():
    """Defect guarded: a loss believed because it was well-formed."""
    reg = CoSRegister(holds=_BOOK.__contains__)
    with pytest.raises(Exception, match="BAD_CREDENTIAL|did not present"):
        reg.receive_loss_wire(_loss_wire(credential="guess"))
    assert reg.losses_notified() == []


def test_a_payload_that_is_not_a_loss_notice_is_refused():
    """Defect guarded: any unsolicited payload filed as a lost registration."""
    from interface.contracts.wall_envelope import WallNotification

    class NotALoss:
        supply_point_id = "C1"

    notification = WallNotification(
        notification_id="x", notification_type="t", schema_version=2, sender="CSS-PROVIDER-01",
        sequence=0, observed_at=__import__("datetime").datetime(2023, 2, 28, 17),
        valid_time=None, payload=NotALoss(),
    )
    with pytest.raises(ValueError, match="not a registration-loss notice"):
        CoSRegister(holds=_BOOK.__contains__).receive_loss_notice(notification)


def test_a_gaining_side_process_is_not_reported_as_a_loss():
    """Defect guarded: `losses_notified` reading every process, so a switch this
    supplier is GAINING would be counted as one it lost."""
    reg = CoSRegister(holds=_BOOK.__contains__)
    reg.open_switch("C9", "2023-01-01", gaining="us", losing="them")
    reg.receive_loss_wire(_loss_wire())
    assert [r["supply_point_id"] for r in reg.losses_notified()] == ["C1"]


def test_a_loss_notice_for_a_point_off_this_book_is_an_exception_not_a_loss():
    """Defect guarded: a notice filed as a loss for a point this supplier never held -- a
    real registration service sends a loser notices only for its own registrations, so one
    that is not is an exception to investigate. Both branches in one register, both
    non-empty, so a register that refuses everything cannot pass."""
    reg = CoSRegister(holds=_BOOK.__contains__)
    assert reg.receive_loss_wire(_loss_wire(point="C1", seq=0)) is True
    assert reg.receive_loss_wire(_loss_wire(point="STRANGER", seq=1)) is False
    assert reg.receive_loss_wire(_loss_wire(point="STRANGER", seq=1)) is False  # redelivered
    assert [r["supply_point_id"] for r in reg.losses_notified()] == ["C1"]
    assert reg.loss_exceptions() == [{
        "supply_point_id": "STRANGER", "registration_ref": "STRANGER@2023-03-01",
        "sender": "CSS-PROVIDER-01", "reason": "no registration on this supplier's book",
    }]
    assert reg.active_for_account("STRANGER") == []


def test_the_book_is_asked_when_the_notice_arrives_not_when_the_register_opens():
    """Defect guarded: a register that snapshots the book at opening, so a point won
    mid-run is an exception when it later leaves."""
    book: set[str] = set()
    reg = CoSRegister(holds=book.__contains__)
    book.add("C1")
    assert reg.receive_loss_wire(_loss_wire(point="C1")) is True
    assert reg.loss_exceptions() == []


def test_a_register_with_no_book_refuses_to_file_a_loss_by_name():
    """Defect guarded: a register opened without the book quietly filing everything."""
    with pytest.raises(ValueError, match="opened without the supply book"):
        CoSRegister().receive_loss_wire(_loss_wire())
