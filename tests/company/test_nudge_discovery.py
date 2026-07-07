from company.analytics.nudge_discovery import (
    FramingSegmentLift,
    compute_framing_lift_by_segment,
    assess_framing_consumer_duty,
)


def _customers(pairs):
    return [dict(customer_id=cid, segment=seg) for cid, seg in pairs]


def test_compute_framing_lift_by_segment_basic_counts():
    retention_log = [
        dict(customer_id="C1", framing_type="loss_framed", outcome="retained"),
        dict(customer_id="C2", framing_type="loss_framed", outcome="churned_despite_offer"),
        dict(customer_id="C3", framing_type="gain_framed", outcome="retained"),
    ]
    customers = _customers([("C1", "resi"), ("C2", "resi"), ("C3", "resi")])
    lift = compute_framing_lift_by_segment(retention_log, customers)
    by_key = dict(((x.framing_type, x.segment), x) for x in lift)
    loss_resi = by_key[("loss_framed", "resi")]
    assert loss_resi.offers_made == 2
    assert loss_resi.retained_count == 1
    assert loss_resi.retention_rate == 0.5
    gain_resi = by_key[("gain_framed", "resi")]
    assert gain_resi.offers_made == 1
    assert gain_resi.retained_count == 1
    assert gain_resi.retention_rate == 1.0


def test_compute_framing_lift_ignores_pending_and_missing_framing():
    retention_log = [
        dict(customer_id="C1", framing_type="loss_framed", outcome="pending"),
        dict(customer_id="C2", outcome="retained"),  # no framing_type
        dict(customer_id="C3", framing_type="gain_framed", outcome="retained"),
    ]
    customers = _customers([("C1", "resi"), ("C2", "resi"), ("C3", "resi")])
    lift = compute_framing_lift_by_segment(retention_log, customers)
    assert len(lift) == 1
    assert lift[0].framing_type == "gain_framed"


def test_compute_framing_lift_defaults_missing_segment_to_resi():
    retention_log = [
        dict(customer_id="C9", framing_type="loss_framed", outcome="retained"),
    ]
    lift = compute_framing_lift_by_segment(retention_log, customers=[])
    assert lift[0].segment == "resi"


def test_assess_consumer_duty_green_when_no_concentration():
    lift = [
        FramingSegmentLift("loss_framed", "resi", 10, 5, 0.5),
        FramingSegmentLift("gain_framed", "resi", 10, 5, 0.5),
        FramingSegmentLift("loss_framed", "SME", 10, 5, 0.5),
        FramingSegmentLift("gain_framed", "SME", 10, 5, 0.5),
    ]
    assessment = assess_framing_consumer_duty(lift, "2025-12-31")
    assert assessment.rag.value == "green"


def test_assess_consumer_duty_amber_when_resi_concentration_high():
    lift = [
        FramingSegmentLift("loss_framed", "resi", 10, 9, 0.9),
        FramingSegmentLift("gain_framed", "resi", 10, 3, 0.3),
        FramingSegmentLift("loss_framed", "SME", 10, 5, 0.5),
        FramingSegmentLift("gain_framed", "SME", 10, 5, 0.5),
        FramingSegmentLift("loss_framed", "I&C", 10, 5, 0.5),
        FramingSegmentLift("gain_framed", "I&C", 10, 5, 0.5),
    ]
    assessment = assess_framing_consumer_duty(lift, "2025-12-31")
    assert assessment.rag.value == "amber"
    assert assessment.metric_value > 0.15


def test_assess_consumer_duty_green_when_insufficient_data():
    assessment = assess_framing_consumer_duty([], "2025-12-31")
    assert assessment.rag.value == "green"
    assert "Insufficient" in assessment.narrative
