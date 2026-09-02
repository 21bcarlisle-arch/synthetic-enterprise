"""THE HEAD-RED ACCEPTANCE LIST, in a module that reads it and nothing else.

WHY THIS MODULE EXISTS (2026-09-02, the publish-gate wedge)
-----------------------------------------------------------
`background/head_red_register.py` reached `tools/head_green_census.py` for ONE pure JSON
reader, `load_baseline`. The census imports `background/process_run_complete.py`, which is a
declared `publish_scope.PUBLISH_PATH_SOURCES` member, so that single edge put the harness's
whole draw/queue brain inside the publish gate:

    background/supervisor.py
        -> background/staging_rooms.py
        -> background/head_red_register.py
        -> tools/head_green_census.py
        -> background/process_run_complete.py

`tests/background/test_publish_scope.py::test_the_supervisor_does_not_import_the_publish_path`
is what named it, and this is the cut it asks for. It is the same shape, and the same remedy, as
`background/publish_gate_blocking_read.py`: the edge existed because of an import, not because
of a risk — nothing in the register can make a figure on the live site wrong.

The edge was also a CYCLE. `tools/head_green_census.py` already imports
`background/head_red_register.py` (it writes the register after each census run), so the two
modules imported each other. Moving the reader DOWN into a leaf both cuts the publish path and
leaves one direction of travel.

WHY THE READER AND NOT THE WHOLE CENSUS
---------------------------------------
The acceptance list is a HUMAN-MAINTAINED input to two different consumers — the census, which
diffs a run against it, and the register, which reports what is owed against it. Neither owns
it, so neither is the honest home for the path, and a copy in each would be two things to keep
equal. This module is the one place both ask.

THE ANTI-LAUNDERING PROPERTY IS WHY THERE IS NO WRITER HERE
------------------------------------------------------------
A control that folds its own new failures into its own baseline cannot fail. `tests/tools/
test_head_green_census.py::test_nothing_in_this_module_writes_the_baseline` held that
structurally over the census's source; now that `BASELINE_PATH` lives here, that test scans
THIS module too. Keeping the module reader-only is not a convention — it is what makes the scan
mean something, and adding any write here is the edit that control exists to name.
"""
from __future__ import annotations

import json
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent

#: The human-maintained known-red set. Written by a person accepting a red BY NAME, never by any
#: control that measures reds -- see the anti-laundering property above.
BASELINE_PATH = PROJECT_DIR / "docs" / "observability" / "head_red_baseline.json"


def load_baseline(path: Path = BASELINE_PATH) -> set:
    """The known-red set. A missing/malformed baseline is EMPTY, so every red reads as new.

    Fail direction is towards NOISE, never towards silence: an unreadable baseline that resolved
    to "everything is known" would turn this control off exactly when its state is broken.
    """
    try:
        data = json.loads(path.read_text())
    except (OSError, ValueError):
        return set()
    known = data.get("known_red")
    return set(known) if isinstance(known, list) else set()
