"""The commit gate finds a data file's readers when they open it through a path built from parts.

Defect each test names: `sim/scenario/spine.py` opens `CURRICULUM_DIR / f"{world_id}.yaml"`, names no
file, and so had no route from `history_replay.yaml` to its tests; the one test selected was selected
because its docstring named the file (docs/staging/records/SEAT_PREREG_ASSEMBLED_PATH_READERS_CENSUS_2026-11-17.md).
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools import pre_commit_test_gate as gate  # noqa: E402
from tools.assembled_path_readers import directories_read, readers_of  # noqa: E402

MODULE = "sim/scenario/fake.py"


def test_each_spelling_of_a_directory_resolves_and_a_coincidence_does_not():
    """One control over the partition: the route must be able to say yes, in every spelling the
    census found, AND say no when the directory and the assembled name are never joined. A
    resolver that answered yes to everything, or no to everything, fails here."""
    here = 'from pathlib import Path\nD = Path(__file__).resolve().parent / "curriculum"\n' \
           'def load(w, d=None):\n    base = Path(d) if d is not None else D\n' \
           '    return base / f"{w}.yaml"\n'
    rooted = 'P = Path(__file__).parent.parent\nS = P / "docs" / "design" / "store"\n' \
             'def _dir(x=None):\n    return x if x is not None else S\n' \
             'def path_for(a):\n    return _dir() / f"{a}.yaml"\n'
    in_fstring = 'W = "sim/weather_data"\ndef load(c):\n    return open(f"{W}/{c}.csv")\n'
    joined = 'import os\nH = "sim/hh_data"\ndef load(c):\n    return os.path.join(H, c + ".csv")\n'
    coincidence = 'from pathlib import Path\nD = "sim/weather_data"\nprint(D)\n' \
                  'def out(c):\n    return Path("sim/out") / f"{c}.csv"\n'

    assert "sim/scenario/curriculum" in directories_read(MODULE, ".yaml", here)
    assert "docs/design/store" in directories_read(MODULE, ".yaml", rooted)
    assert "sim/weather_data" in directories_read(MODULE, ".csv", in_fstring)
    assert "sim/hh_data" in directories_read(MODULE, ".csv", joined)
    assert directories_read(MODULE, ".csv", coincidence) & {"sim/weather_data"} == set()
    assert "sim/out" in directories_read(MODULE, ".csv", coincidence)
    assert "sim/scenario/curriculum" not in directories_read(MODULE, ".csv", here), "suffix kept"


def test_the_curriculum_reader_is_found_without_any_file_naming_it():
    assert "sim/scenario/spine.py" in readers_of(
        "sim/scenario/curriculum/history_replay.yaml", gate.CODE_PREFIXES)


def test_markdown_is_out_of_scope():
    assert readers_of("docs/staging/anything.md", gate.CODE_PREFIXES) == ()


def test_the_gate_reaches_the_spine_test_through_the_reader_not_through_a_docstring():
    """With the main selection treated as empty, the import-derived run alone still reaches
    test_scenario_spine: a docstring edit can no longer blind the gate to it."""
    extras = gate.import_derived_extras(["sim/scenario/curriculum/history_replay.yaml"], [])
    assert "tests/sim/test_scenario_spine.py" in extras


def test_a_weather_archive_selects_its_readers_named_tests():
    assert "tests/simulation/test_premise_trace.py" in gate.data_surface_tests(
        "sim/weather_data/C1.csv")


def test_the_observability_exclusion_holds_and_is_the_only_one():
    """The exclusion is keyed to a stated red, so it must not widen silently; and the route must
    still fire for the directory beside it."""
    assert gate.ASSEMBLED_ROUTE_EXCLUDED == ("docs/observability/",)
    assert gate._assembled_path_readers("docs/observability/open_question_register.json") == ()
    assert gate._assembled_path_readers("sim/scenario/curriculum/history_replay.yaml")
