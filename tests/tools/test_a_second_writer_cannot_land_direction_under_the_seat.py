"""A non-seat commit of DIRECTION.yaml is refused while the delivery seat orients; nothing else is."""
from __future__ import annotations

from tools import direction_seat_window as w

D = w.DIRECTION_YAML
WORKER = "0::/user.slice/user@1000.service/app.slice/worker-tick.service\n"
SEAT = "0::/user.slice/user@1000.service/app.slice/delivery-seat.service\n"


def test_the_refusal_can_be_taken_and_every_way_round_it_stays_open():
    # The whole partition in one control: a guard that refuses everything fails the passes, and one
    # that refuses nothing fails the first line.
    assert not w.verdict([D, "a.py"], "activating", WORKER)[0]
    assert not w.verdict([D], "active", WORKER)[0]
    assert w.verdict([D], "activating", SEAT)[0], "the seat's own landing must pass"
    assert w.verdict([D], "inactive", WORKER)[0], "with the seat idle anyone may write it"
    assert w.verdict([D], "failed", WORKER)[0]
    assert w.verdict(["docs/direction/decisions.jsonl"], "activating", WORKER)[0]


def test_the_refusal_names_its_reason_and_the_two_ways_out():
    ok, why = w.verdict([D], "activating", WORKER, "Wed 2026-11-11 18:22:57 GMT")
    assert not ok
    assert "18:22:57" in why and "unstage" in why and "wait_for.py --pid" in why


def test_an_unaskable_systemd_fails_open(monkeypatch, capsys):
    monkeypatch.setattr(w, "_staged", lambda: [D])

    def boom():
        raise RuntimeError("no user bus")
    monkeypatch.setattr(w, "_seat", boom)
    assert w.main() == 0
    assert "not blocking" in capsys.readouterr().err


def test_main_refuses_through_the_real_wiring(monkeypatch):
    monkeypatch.setattr(w, "_staged", lambda: [D])
    monkeypatch.setattr(w, "_seat", lambda: ("activating", "now"))
    monkeypatch.setattr(w, "_cgroup", lambda: WORKER)
    assert w.main() == 1
    monkeypatch.setattr(w, "_cgroup", lambda: SEAT)
    assert w.main() == 0
