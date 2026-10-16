"""EP17's switch: `SE_POPULATION_SEED` chooses the book seed, and unset it changes nothing.

Each leg names the defect it catches:
  - the default argument drew a different cast from the bare call (the 2026-10-19 publish would
    stop being a one-variable reading);
  - the seed reached nothing, so every "varied" run faced the same cast;
  - a foreign seed ran without the director's record, or the gate refused every seed;
  - the run output did not say which cast it faced.
"""
from __future__ import annotations

import json

import pytest

import simulation.live_population as lp
import tools.book_seed_authorisation as bsa


@pytest.fixture
def restore_run_seed():
    before = lp._RUN_BASE_SEED
    yield
    lp._RUN_BASE_SEED = before


def _cast(book):
    return json.dumps(book, sort_keys=True, default=str)


def test_unset_is_no_argument_and_the_default_draws_the_bare_calls_cast(monkeypatch, restore_run_seed):
    monkeypatch.delenv(lp._POPULATION_SEED_ENV, raising=False)
    assert lp.population_seed_argument() is None
    bare = _cast(lp.live_population())
    assert _cast(lp.live_population(base_seed=lp.population_seed_argument())) == bare
    assert _cast(lp.live_population(base_seed=lp._DEFAULT_BASE_SEED)) == bare
    assert lp.run_base_seed() == lp._DEFAULT_BASE_SEED


def test_two_seeds_draw_different_casts_and_the_run_records_which(restore_run_seed):
    a = lp.live_population(base_seed=0)
    assert lp.run_base_seed() == 0
    b = lp.live_population(base_seed=3)
    assert lp.run_base_seed() == 3
    assert _cast(a) != _cast(b)
    assert _cast(lp.live_population(base_seed=0)) == _cast(a)


def test_a_foreign_seed_is_refused_without_the_record_and_admitted_with_one(
        monkeypatch, tmp_path):
    monkeypatch.setattr(bsa, "BOOK_SEED_AUTHORISATION", tmp_path / "absent.json")
    monkeypatch.setenv(lp._POPULATION_SEED_ENV, "3")
    with pytest.raises(RuntimeError, match="EP17_varied_population_draw"):
        lp.population_seed_argument()

    record = tmp_path / "varied.json"
    record.write_text(json.dumps({"_meta": {"authority": "test"}, "activated": {"value": True},
                                  "base_seeds": {"value": [3]}}), encoding="utf-8")
    monkeypatch.setattr(bsa, "BOOK_SEED_AUTHORISATION", record)
    assert lp.population_seed_argument() == 3

    monkeypatch.setenv(lp._POPULATION_SEED_ENV, str(lp._DEFAULT_BASE_SEED))
    monkeypatch.setattr(bsa, "BOOK_SEED_AUTHORISATION", tmp_path / "absent.json")
    assert lp.population_seed_argument() == lp._DEFAULT_BASE_SEED

    monkeypatch.setenv(lp._POPULATION_SEED_ENV, "three")
    with pytest.raises(ValueError, match="not an integer"):
        lp.population_seed_argument()


def test_the_run_output_is_stamped_with_the_seed_the_book_was_drawn_at(monkeypatch, restore_run_seed):
    import contextlib

    import simulation.run_phase2b as rp
    from simulation import run_cost

    monkeypatch.setattr(rp, "_box_admission", contextlib.nullcontext)
    monkeypatch.setattr(rp, "_main", lambda **_k: {})
    monkeypatch.setattr(run_cost, "record", lambda *a, **k: None)
    lp._RUN_BASE_SEED = 61106
    assert rp.main()["population_seed"] == 61106


def test_run_phase2b_reads_the_switch_when_it_draws_its_book():
    """The book is drawn at import, so the import is where a refused seed must stop the run. If
    `run_phase2b` called `live_population()` bare, this seed would be ignored and the import
    would succeed on the default cast."""
    import os
    import subprocess
    import sys

    assert bsa.book_seed_authorisation_refusal([3]), (
        "the director's record now lists seed 3; pick a seed it does not list")
    env = dict(os.environ, **{lp._POPULATION_SEED_ENV: "3"})
    done = subprocess.run([sys.executable, "-c", "import simulation.run_phase2b"], env=env,
                          capture_output=True, text=True, timeout=600, cwd=bsa.PROJECT_DIR)
    assert done.returncode != 0
    assert "SE_POPULATION_SEED=3 refused" in done.stderr
