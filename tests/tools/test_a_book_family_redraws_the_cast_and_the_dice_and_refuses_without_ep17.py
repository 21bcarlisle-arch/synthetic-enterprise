"""`--book-seeds`: a book family must redraw the cast AND the dice, and must not run without EP17.

The defects this names:
  * A book seed changes WHO sits behind a founder id (77 of 80 ids are shared across two seeds),
    but `churn_roll_for_renewal` hashes (id, date) with no seed. Unpatched, a different household
    under a shared id takes the SAME renewal roll in every book, and the between-book spread comes
    out narrow in the flattering direction.
  * A non-default book seed is `EP17_varied_population_draw`, which is R13 curriculum. A flag
    that ran it on the seat's own say-so would have crossed the baseline/curriculum split.

No simulation pass runs here. The rosters take about 0.03 s, and the member loop is driven by an
injected spawn.
"""
from __future__ import annotations

import json
import subprocess
import sys

import simulation.customer_events as customer_events
import tools.run_value_cycle_ab as ab
from simulation.live_population import _DEFAULT_BASE_SEED, founder_book

OTHER = 61001
TERM = "2016-01-01"


def _record(tmp_path, seeds, activated=True, authority="Director console: vary the book."):
    path = tmp_path / "varied_population_draw_activation.json"
    path.write_text(json.dumps({
        "_meta": {"authority": authority},
        "activated": {"value": activated},
        "base_seeds": {"value": seeds},
    }), encoding="utf-8")
    return path


def _shared_id_with_a_different_household():
    a = {r["customer_id"]: r for r in founder_book(_DEFAULT_BASE_SEED)}
    b = {r["customer_id"]: r for r in founder_book(OTHER)}
    moved = sorted(k for k in set(a) & set(b) if a[k] != b[k])
    return a, b, moved


def test_two_book_seeds_put_different_households_behind_the_same_ids():
    a, b, moved = _shared_id_with_a_different_household()
    assert moved, "no shared id holds a different household -- the book seed varies nothing"
    assert [r for r in a.values()] != [r for r in b.values()]


def test_the_patched_roll_follows_the_book_seed_on_a_shared_id_and_the_real_one_does_not():
    _, _, moved = _shared_id_with_a_different_household()
    account = moved[0]
    real = customer_events.churn_roll_for_renewal
    # THE DEFECT, SHOWN: unpatched, the roll ignores which book this is.
    assert real(account, TERM) == real(account, TERM)
    rolls = {}
    for seed in (_DEFAULT_BASE_SEED, OTHER):
        calls = {"n": 0, "redrawn": 0, "held": 0, "ids": set()}
        _, _, factory = ab.resolve_redraw_target("churn_roll")
        rolls[seed] = factory(real, seed, lambda _a: True, calls)(account, TERM)
        assert calls["redrawn"] == 1
    assert rolls[_DEFAULT_BASE_SEED] != rolls[OTHER]


def test_the_authorisation_refusal_can_fire_and_can_pass(tmp_path):
    missing = tmp_path / "varied_population_draw_activation.json"
    fired = ab.book_seed_authorisation_refusal([_DEFAULT_BASE_SEED, OTHER], missing)
    assert fired and "EP17_varied_population_draw" in fired and str(missing) in fired
    # The default book alone is every published run's book and needs no ruling.
    assert ab.book_seed_authorisation_refusal([_DEFAULT_BASE_SEED], missing) is None
    record = _record(tmp_path, [OTHER])
    assert ab.book_seed_authorisation_refusal([_DEFAULT_BASE_SEED, OTHER], record) is None
    # A ruling covers the seeds it lists, and no others.
    unlisted = ab.book_seed_authorisation_refusal([OTHER, OTHER + 1], record)
    assert unlisted and str(OTHER + 1) in unlisted
    assert ab.book_seed_authorisation_refusal(
        [OTHER], _record(tmp_path, [OTHER], activated=False))
    assert ab.book_seed_authorisation_refusal([OTHER], _record(tmp_path, [OTHER], authority=""))


def test_the_flag_refuses_and_names_ep17_when_no_ruling_is_recorded(tmp_path, monkeypatch, capsys):
    # Pointed at a tmp path, so the day the director's ruling lands this still cannot launch a pass.
    missing = tmp_path / "varied_population_draw_activation.json"
    monkeypatch.setattr(ab, "BOOK_SEED_AUTHORISATION", missing)
    assert ab.main(["--book-seeds", "{},{}".format(_DEFAULT_BASE_SEED, OTHER),
                    "--out", str(tmp_path / "family.json")]) == 2
    said = capsys.readouterr().out
    assert "EP17_varied_population_draw" in said and str(missing) in said
    assert not (tmp_path / "family.json").exists()


def _member(seed, recorded=None, redrawn=5):
    return {"book_seed": seed, "run_base_seed": seed if recorded is None else recorded,
            "draw_calls": 9, "draws_redrawn": redrawn, "selection_gbp": 1.0,
            "billing_accounts_settled_in_window": 164, "result": {}}


def _spawner(members, spawned):
    def spawn(seed, _end, path):
        spawned.append(seed)
        path.write_text(json.dumps(members[seed]), encoding="utf-8")
        return 0
    return spawn


def test_every_refusal_can_fire_and_the_family_can_pass(tmp_path):
    record = _record(tmp_path, [OTHER, OTHER + 1])
    seeds = [_DEFAULT_BASE_SEED, OTHER]
    good = {s: _member(s) for s in seeds + [OTHER + 1]}

    spawned = []
    family = ab.book_seeds(seeds, None, tmp_path / "m", spawn=_spawner(good, spawned),
                           record=record)
    assert family["available"] and spawned == seeds
    assert [m["run_base_seed"] for m in family["members"]] == seeds

    cases = {
        "duplicate": ([OTHER, OTHER], good),
        "unauthorised": ([_DEFAULT_BASE_SEED, OTHER + 2], good),
        "wrong_book": (seeds, {**good, OTHER: _member(OTHER, recorded=_DEFAULT_BASE_SEED)}),
        "no_redraw": (seeds, {**good, OTHER: _member(OTHER, redrawn=0)}),
    }
    for label, (case_seeds, members) in cases.items():
        spawned = []
        out = ab.book_seeds(case_seeds, None, tmp_path / label,
                            spawn=_spawner(members, spawned), record=record)
        assert not out["available"], label
        if label in ("duplicate", "unauthorised"):
            assert spawned == [], "{} must refuse before any book is paid for".format(label)
    assert "EP17" in ab.book_seeds([_DEFAULT_BASE_SEED, OTHER + 2], None, tmp_path / "x",
                                   spawn=_spawner(good, []), record=record)["why_not"]


def test_a_member_reads_the_seed_its_book_was_drawn_at_and_restores_the_roll():
    real = customer_events.churn_roll_for_renewal

    seen = []

    def runner():
        seen.append(customer_events.churn_roll_for_renewal("SYN-2016-001", TERM))
        return {}

    member = ab.book_member(OTHER, runner=runner)
    assert customer_events.churn_roll_for_renewal is real
    # The dice the pass took are the ones floor seed == book seed draws, not the label alone.
    _, _, factory = ab.resolve_redraw_target("churn_roll")
    expected = factory(real, OTHER, lambda _a: True,
                       {"n": 0, "redrawn": 0, "held": 0, "ids": set()})("SYN-2016-001", TERM)
    assert seen == [expected]
    assert member["draws_redrawn"] == 1 and member["churn_roll_floor_seed"] == OTHER
    # THIS process drew its book at the default, so the member must NOT read as book OTHER.
    assert member["run_base_seed"] == _DEFAULT_BASE_SEED
    assert ab.book_member_refusal(OTHER, member)


def test_the_member_preamble_reaches_the_book_before_anything_draws_it():
    probe = ab.BOOK_MEMBER_PREAMBLE + (
        "_lp.live_population()\n"
        "print(_lp._RUN_BASE_SEED)\n")
    out = subprocess.run([sys.executable, "-c", probe, str(OTHER)], capture_output=True,
                         text=True, check=True, cwd=ab.PROJECT_DIR)
    assert out.stdout.strip().splitlines()[-1] == str(OTHER)
    assert "book_member_main" in ab.BOOK_MEMBER_BOOTSTRAP and callable(ab.book_member_main)
