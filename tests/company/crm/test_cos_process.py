import pytest
from company.crm.cos_process import (
    CoSRegister, CoSProcess, CoSStage, ObjectionReason
)


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
