"""Phase 118: DTN message log tests."""

from company.market.dtn_log import DtnMessage, DtnLog, _KNOWN_FLOWS


def _msg(flow="D0001", direction="inbound", status="received"):
    return DtnMessage(
        flow_id=flow, direction=direction,
        timestamp="2026-06-26T09:00:00Z",
        customer_id="C1", mpan_or_mprn="1012345678901",
        status=status,
    )


def test_record_and_count():
    log = DtnLog()
    log.record(_msg())
    assert len(log.inbound()) == 1


def test_outbound_separation():
    log = DtnLog()
    log.record(_msg(direction="inbound"))
    log.record(_msg(direction="outbound"))
    assert len(log.inbound()) == 1
    assert len(log.outbound()) == 1


def test_by_flow():
    log = DtnLog()
    log.record(_msg("D0001"))
    log.record(_msg("D0010"))
    log.record(_msg("D0001"))
    assert len(log.by_flow("D0001")) == 2


def test_for_customer():
    log = DtnLog()
    m = DtnMessage("D0001", "inbound", "2026-06-26T09:00:00Z", customer_id="C1")
    log.record(m)
    assert len(log.for_customer("C1")) == 1
    assert len(log.for_customer("C2")) == 0


def test_rejected():
    log = DtnLog()
    log.record(_msg(status="received"))
    log.record(_msg(status="rejected"))
    assert len(log.rejected()) == 1


def test_summary_totals():
    log = DtnLog()
    log.record(_msg("D0001", "inbound"))
    log.record(_msg("D0301Z", "outbound"))
    s = log.summary()
    assert s["total"] == 2
    assert s["inbound"] == 1
    assert s["outbound"] == 1


def test_summary_by_flow():
    log = DtnLog()
    log.record(_msg("D0001"))
    log.record(_msg("D0001"))
    log.record(_msg("D0010"))
    s = log.summary()
    assert s["by_flow"]["D0001"] == 2
    assert s["by_flow"]["D0010"] == 1


def test_flow_description():
    m = _msg("D0001")
    assert "Meter read" in m.flow_description


def test_unknown_flow_description():
    m = _msg("X9999")
    assert "Unknown" in m.flow_description


def test_known_flows_contains_standard_ids():
    log = DtnLog()
    flows = log.known_flows()
    assert "D0001" in flows
    assert "D0301Z" in flows
    assert "806" in flows


# --- Phase LB depth tests ---

def test_flow_id_stored():
    m = _msg('D0150')
    assert m.flow_id == 'D0150'


def test_direction_stored():
    m = _msg(direction='outbound')
    assert m.direction == 'outbound'


def test_timestamp_stored():
    m = _msg()
    assert m.timestamp == '2026-06-26T09:00:00Z'


def test_customer_id_stored():
    m = DtnMessage('D0001', 'inbound', '2022-01-01T00:00:00Z', customer_id='C_LB')
    assert m.customer_id == 'C_LB'


def test_mpan_stored():
    m = DtnMessage('D0001', 'inbound', '2022-01-01T00:00:00Z', mpan_or_mprn='MPAN_LB')
    assert m.mpan_or_mprn == 'MPAN_LB'


def test_status_default_received():
    m = DtnMessage('D0001', 'inbound', '2022-01-01T00:00:00Z')
    assert m.status == 'received'


def test_notes_default_empty():
    m = DtnMessage('D0001', 'inbound', '2022-01-01T00:00:00Z')
    assert m.notes == ''


def test_log_inbound_empty_initially():
    log = DtnLog()
    assert log.inbound() == []


def test_log_for_customer_empty_unknown():
    log = DtnLog()
    assert log.for_customer('UNKNOWN') == []


def test_log_rejected_empty_when_none():
    log = DtnLog()
    assert log.rejected() == []
