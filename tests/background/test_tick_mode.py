"""The director's one-word tick mode: each mode holds or admits what it says, a mode set with an
expiry reverts on its own, and each of the three routes that spend tokens actually asks it."""
import json
import types

import pytest

from background import tick_mode as tm

H = 3600
T0 = 1_790_000_000.0


@pytest.fixture
def files(tmp_path):
    return {"mode_path": tmp_path / "mode.json", "spawn_path": tmp_path / "spawns.json"}


def _gate(route, now, files):
    return tm.gate(route, now, **files)


def test_every_route_can_be_both_admitted_and_held_across_the_modes(files):
    """The partition control: a gate that held everything, or admitted everything, fails here."""
    seen = {r: set() for r in tm.ROUTES}
    for mode in tm.MODES:
        tm.set_mode(mode, now=T0, path=files["mode_path"], history=files["mode_path"].parent / "h")
        for r in tm.ROUTES:
            seen[r].add(_gate(r, T0 + 1, files)[0])
    assert all(v == {True, False} for v in seen.values()), seen


def test_off_holds_all_three_and_normal_admits_all_three(files):
    h = files["mode_path"].parent / "h"
    tm.set_mode("off", now=T0, path=files["mode_path"], history=h)
    assert [(_gate(r, T0 + 1, files)[0]) for r in tm.ROUTES] == [False, False, False]
    assert "tick mode off" in _gate("worker-tick", T0 + 1, files)[2]
    tm.set_mode("normal", now=T0, path=files["mode_path"], history=h)
    assert [(_gate(r, T0 + 1, files)[0]) for r in tm.ROUTES] == [True, True, True]


def test_fold_only_leaves_only_the_executor(files):
    tm.set_mode("fold-only", now=T0, path=files["mode_path"], history=files["mode_path"].parent / "h")
    assert {r: _gate(r, T0 + 1, files)[0] for r in tm.ROUTES} == {
        "worker-tick": False, "seat-executor": True, "delivery-seat": False}


def test_slow_spaces_spawns_and_normal_does_not(files):
    h = files["mode_path"].parent / "h"
    tm.set_mode("slow", now=T0, path=files["mode_path"], history=h)
    assert _gate("worker-tick", T0 + 1, files)[0]          # no spawn yet: admitted
    tm.note_spawn("worker-tick", now=T0 + 2, path=files["spawn_path"])
    held = _gate("worker-tick", T0 + 2 + H, files)
    assert not held[0] and "every 4h" in held[2]
    assert _gate("worker-tick", T0 + 3 + 4 * H, files)[0]
    tm.note_spawn("delivery-seat", now=T0 + 2, path=files["spawn_path"])
    assert not _gate("delivery-seat", T0 + 2 + 5 * H, files)[0]   # 12h, not the tick's 4h
    assert _gate("delivery-seat", T0 + 3 + 12 * H, files)[0]
    tm.set_mode("normal", now=T0 + 3, path=files["mode_path"], history=h)
    assert _gate("worker-tick", T0 + 2 + H, files)[0]


def test_a_mode_with_an_expiry_reverts_by_itself_with_no_timer(files):
    tm.set_mode("off", until=T0 + 10 * H, now=T0, path=files["mode_path"],
                history=files["mode_path"].parent / "h")
    assert tm.current(T0 + 9 * H, files["mode_path"])["mode"] == "off"
    after = tm.current(T0 + 10 * H, files["mode_path"])
    assert after["mode"] == "normal" and after["reverted_from"] == "off"
    assert _gate("worker-tick", T0 + 10 * H, files)[0]


def test_an_expiry_can_revert_to_a_named_mode(files):
    tm.set_mode("off", until=T0 + H, then="slow", now=T0, path=files["mode_path"],
                history=files["mode_path"].parent / "h")
    assert tm.current(T0 + 2 * H, files["mode_path"])["mode"] == "slow"


def test_a_broken_dial_reads_normal_and_says_why(files):
    assert tm.current(T0, files["mode_path"])["why"] == "no mode set"
    files["mode_path"].write_text("{not json")
    cur = tm.current(T0, files["mode_path"])
    assert cur["mode"] == "normal" and "unreadable" in cur["why"]
    files["mode_path"].write_text(json.dumps({"mode": "sloww"}))
    cur = tm.current(T0, files["mode_path"])
    assert cur["mode"] == "normal" and "sloww" in cur["why"]


def test_set_refuses_what_it_cannot_honour(files):
    with pytest.raises(ValueError):
        tm.set_mode("quiet", path=files["mode_path"])
    with pytest.raises(ValueError):
        tm.set_mode("off", until=T0 - 1, now=T0, path=files["mode_path"])
    assert tm.main(["off", "--for", "soon"]) == 2


def test_the_cli_sets_with_one_word_and_an_expiry(monkeypatch, tmp_path, capsys):
    assert tm.main(["slow", "--for", "36h"]) == 0
    rec = json.loads(tm.MODE_FILE.read_text())
    assert rec["mode"] == "slow" and rec["until"] > rec["set_at"] + 35 * H
    assert "tick mode: slow" in capsys.readouterr().out


# ── what product-only and fold-only admit ────────────────────────────────────────────────────

ATOMS = [
    {"id": "W2_19_who_lives_where", "lane": "W2_customer_generator"},
    {"id": "H_draw_excludes_things", "lane": "H_harness"},
]


@pytest.mark.parametrize("item,expect", [
    ({"id": "a", "what": "extend W2_19 layer one"}, True),
    ({"id": "a", "what": "repair H_draw_excludes_things"}, False),
    ({"id": "a", "what": "think about the residual"}, False),
    ({"id": "a", "what": "think about the residual", "lane": "W2_customer_generator"}, True),
    ({"id": "a", "what": "think about it", "lane": "H_harness"}, False),
    ({"id": "a", "what": "edit site/data/value_arms.json and docs/staging/X.md"}, True),
    ({"id": "a", "what": "edit site/x.js and background/supervisor.py"}, False),
])
def test_product_only_classifies_what_an_item_names(item, expect):
    ok, why = tm.item_is_product(item, atoms=ATOMS)
    assert ok is expect and why


def test_fold_only_admits_an_item_naming_a_registered_long_job():
    recs = [{"job": "floor18", "unit": "longjob-floor18", "artefact": "/var/tmp/x/folded18.json"}]
    assert tm.item_is_fold({"what": "fold folded18.json into the page"}, recs)[0]
    assert not tm.item_is_fold({"what": "build a thing"}, recs)[0]


def test_product_draw_blocks_harness_atoms_in_a_view_and_restores_the_map(monkeypatch):
    from background import supervisor as s
    real = types.SimpleNamespace(load_atoms=lambda *a, **k: [dict(x) for x in ATOMS])
    monkeypatch.setattr(s, "map_store", real)
    monkeypatch.setattr(s, "_priority_zero_active", lambda: False)
    monkeypatch.setattr(s, "_real_staged_instructions", lambda: ["SEAT_FINDING_X.md"])
    monkeypatch.setattr(s, "_maturity_map_draw", lambda rng=None: ",".join(
        a["id"] for a in s.map_store.load_atoms() if not s._is_externally_blocked(a)))
    out = tm.product_draw()
    assert "W2_19_who_lives_where" in out and "H_draw" not in out and "SEAT_FINDING" not in out
    assert s.map_store is real
    # a landing blocker goes through whole
    monkeypatch.setattr(s, "_priority_zero_active", lambda: True)
    monkeypatch.setattr(s, "_self_refill_draw", lambda: "PUBLISH GATE WEDGED")
    assert tm.product_draw() == "PUBLISH GATE WEDGED"


# ── each route asks ────────────────────────────────────────────────────────────────────────────

def test_the_worker_tick_is_held_by_the_mode_before_it_draws(tmp_path, monkeypatch):
    from background import worker_tick as wt
    for name, f in (("ENABLE_FLAG", ".e"), ("SCHEDULED_FLAG", ".s"), ("LOCK_FILE", ".l"),
                    ("LOG_FILE", "log"), ("HEALTH_FILE", "h.json"), ("HEARTBEAT_FILE", "hb.json")):
        monkeypatch.setattr(wt, name, tmp_path / f)
    (tmp_path / ".e").write_text("")
    (tmp_path / ".s").write_text("")
    drew = []
    monkeypatch.setattr(wt, "_draw", lambda **k: drew.append(k) or ("unprocessed staging -- X.md", False))
    monkeypatch.setattr(wt, "spawn_invocation", lambda reason: None)
    tm.set_mode("off")
    d = wt.run_tick()
    assert d.outcome == "MODE_HELD" and drew == []
    tm.set_mode("product-only")
    wt.run_tick()
    assert drew == [{"product_only": True}]
    tm.set_mode("normal")
    wt.run_tick()
    assert drew[-1] == {}


def test_the_executor_stands_down_on_off_and_narrows_on_product_only(monkeypatch):
    from background import seat_executor as se
    monkeypatch.setattr(se, "_another_executor_is_running", lambda: False)
    monkeypatch.setattr(se, "log", lambda m: None)
    seen = {}
    monkeypatch.setattr(se.delivery_lane, "next_item",
                        lambda now=None, admit=None: seen.setdefault("admit", admit) and None)
    tm.set_mode("off")
    ran, why = se.run_once(dry_run=True)
    assert not ran and "tick mode off" in why and "admit" not in seen
    tm.set_mode("product-only")
    ran, why = se.run_once(dry_run=True)
    assert not ran and "product-only" in why
    assert seen["admit"]({"what": "x", "lane": "W2_customer_generator"}) is True
    assert seen["admit"]({"what": "x", "lane": "H_harness"}) is False


def test_the_delivery_seat_records_a_mode_hold_as_a_skip(monkeypatch):
    from background import delivery_seat as ds
    monkeypatch.setattr(ds, "build_brief", lambda now: {
        "since": "s", "commit_count": 1, "substantive_count": 1, "previous_focus_drawn": []})
    monkeypatch.setattr(ds, "is_material", lambda b: (True, "material"))
    monkeypatch.setattr(ds, "map_levels", lambda: {})
    monkeypatch.setattr(ds, "_log", lambda m: None)
    monkeypatch.setattr(ds, "run_session", lambda b: pytest.fail("spawned under off"))
    tm.set_mode("off")
    row = ds.orient(dry_run=True)
    assert row["outcome"] == "skipped" and "tick mode off" in row["why"]
    tm.set_mode("normal")
    assert ds.orient(dry_run=True)["outcome"] == "would-orient"


def test_the_lane_walk_skips_what_admit_refuses_in_both_sources_and_keeps_walking(monkeypatch):
    from background import delivery_lane as dl
    monkeypatch.setattr(dl, "sweep_stale", lambda now=None, path=None: [])
    monkeypatch.setattr(dl, "held", lambda path=None: set())
    monkeypatch.setattr(dl, "_retired_ids", lambda: set())
    monkeypatch.setattr(dl, "_embargoed", lambda item, now: False)
    monkeypatch.setattr(dl, "_self_issued_chain", lambda path=None: 0)
    monkeypatch.setattr(dl, "_atom_ids", lambda: set())
    cont = [{"id": "mach", "lane": "H_harness"}, {"id": "prod", "lane": "W2_customer_generator"}]
    focus = [{"id": "fmach", "lane": "H_harness"}, {"id": "fprod", "lane": "W1_market_weather"}]
    monkeypatch.setattr(dl.seat_continuation, "live", lambda now=None: list(cont))
    monkeypatch.setattr(dl.direction_mod, "unreachable_focus", lambda ids: list(focus))

    def admit(it):
        return it.get("lane") != "H_harness"
    assert dl.next_item()["id"] == "mach"
    assert dl.next_item(admit=admit)["id"] == "prod"
    cont.clear()
    assert dl.next_item(admit=admit)["id"] == "fprod"


# ── a focus item carries its lane to the executor ───────────────────────────────────────────

def _record(**focus_extra):
    return {"version": 1, "oriented_at": "2026-09-27T12:00:00Z", "not_now": [{"what": "x", "why": "y"}],
            "focus": [{"id": "is-the-residual-book-depth-luck", "what": "think", "why": "w", **focus_extra}]}


def test_a_focus_lane_is_validated_against_the_map_and_both_verdicts_are_reachable(monkeypatch):
    """The partition first: absent, known and unknown lanes must give three different answers, or a
    check that refuses every lane (or none) would pass a leg-by-leg test. MUTATION: drop the
    `_lane_problems` call from `direction.validate` and the unknown leg goes green."""
    from background import direction, seat_continuation
    monkeypatch.setattr(seat_continuation, "_map_lanes", lambda: {"W2_customer_generator", "H_harness"})
    absent, known, unknown = (direction.validate(_record(**kw)) for kw in
                              ({}, {"lane": "W2_customer_generator"}, {"lane": "W9_nowhere"}))
    assert absent == [] and known == [] and unknown, (absent, known, unknown)
    assert "W9_nowhere" in unknown[0] and "focus[0].lane" in unknown[0]
    assert direction.validate(_record(lane=""))


def test_a_promoted_focus_item_keeps_its_lane_so_product_only_can_still_admit_it(monkeypatch, tmp_path):
    """`hand_off_focus` is the route a focus row takes to a tick; a lane dropped there is a lane
    product-only never sees. MUTATION: remove `lane=item.get("lane")` from `hand_off_focus`."""
    from background import delivery_lane as dl
    from background import seat_continuation as sc
    monkeypatch.setattr(sc, "STORE", tmp_path / "continuations.json")
    monkeypatch.setattr(sc, "_map_lanes", lambda: {"W2_customer_generator"})
    monkeypatch.setattr(sc, "retirement_orientation", lambda *_a, **_k: None)
    monkeypatch.setattr(dl, "_atom_ids", lambda: set())
    monkeypatch.setattr(dl.direction_mod, "unreachable_focus", lambda *_a, **_k: [
        {"id": "is-the-residual-book-depth-luck", "what": "think about the residual", "why": "w",
         "lane": "W2_customer_generator"}])
    dl.hand_off_focus("is-the-residual-book-depth-luck", "a sourced answer", now=1_000_000.0)
    [row] = [r for r in sc.live(now=1_000_001.0) if r["id"] == "is-the-residual-book-depth-luck"]
    assert tm.item_is_product(row, atoms=ATOMS) == (True, "declares lane W2_customer_generator")


def test_the_orienting_prompt_asks_for_a_focus_lane():
    """The seat writes what the prompt's schema shows it; a field the prompt never names is never
    written. MUTATION: delete the `lane:` line from the schema in `delivery_seat.CHARTER`."""
    from background import delivery_seat
    schema = delivery_seat.CHARTER.split("focus:", 1)[1].split("not_now:", 1)[0]
    assert "lane:" in schema
