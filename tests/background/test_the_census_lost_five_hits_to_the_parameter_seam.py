"""The census stopped seeing a carrier the moment the carrier was repaired correctly.

`background/self_clearing_alarm_census.py` attributes a state file by MODULE-LEVEL SYMBOL: it
sees `RUN_HISTORY_PATH.read_text()`. The 2026-09-05 loader sweep (`c30738d77`) repaired six
carriers by routing every read through `background/episode_prior`, whose loaders take the path as
an ARGUMENT -- and inside `episode_prior` no module symbol names it. Derived over the tree either
side of that commit, the census went from **34 hits to 29**:

    LOST: run_history.json  .harden_cooldown.json  .ntfy_digest_state.json
          .supervisor_map_exhausted_state.json  retired_paths_served.json

`run_history.json` dropped to ZERO recorded readers while `count_run_history_total` reads it on
every dashboard build. Nothing anywhere could notice: `census_is_vacuous()` only refuses a
TOTALLY empty census, and `undispositioned()` only checks a hit with no row -- never a row whose
hit disappeared. A path that stops being a hit needs no disposition and `--check` exits 0.

THE FAIL-OPEN WAS GETTING STRONGER WITH ADOPTION, which is what makes it worth a control rather
than five patched rows: the more correctly a carrier was repaired -- through the shared helper
rather than a hand-rolled loop, which is what this project asks for -- the more certainly it left
the class the census enumerates. Twelve further paths already dispositioned in earlier eras had
been eroded the same way and were silently absent from the live census.

WHAT IS PINNED IS THE PROPERTY: a state file whose read happens behind a path-taking helper is
still attributed to its caller. These tests do not assert a hit count -- a count would go red the
day someone legitimately deletes a carrier, and stay green while the seam re-opened.

MUTATIONS THESE MUST CATCH (each verified to fail this file):
  * `_attribute_through_parameters` never called from `derive()`
  * its fixpoint reduced to a single pass (`while changed` -> one iteration)
  * `_param_names` returning the ALIAS rather than the root parameter (`p`, not `path`)
  * `_is_path_shaped` widened to accept any expression (contents become a path alias)
  * `_preserve_if_unreadable` deleted from `seat_work_in_hand.claim` / `.release`
"""
from __future__ import annotations

import ast
import json
import sys
import tempfile
from pathlib import Path

import pytest

PROJECT_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_DIR))

from background import seat_work_in_hand as swh  # noqa: E402
from background import self_clearing_alarm_census as census  # noqa: E402

#: The five the sweep's own repair removed from the census. Named individually rather than
#: counted: the point is these carriers, not "five of something".
LOST_TO_THE_SEAM = (
    "run_history.json",
    ".harden_cooldown.json",
    ".ntfy_digest_state.json",
    ".supervisor_map_exhausted_state.json",
    "retired_paths_served.json",
)

#: Every way a state file can exist and not be usable. All but the first two PARSE, which is why
#: an `except JSONDecodeError` never saw them.
UNREADABLE_RAW = pytest.mark.parametrize("raw", [
    pytest.param("", id="empty-file"),
    pytest.param('{"a": 1', id="truncated"),
    pytest.param("null", id="json-null"),
    pytest.param("[1, 2, 3]", id="list-of-ints"),
    pytest.param('"abc"', id="a-bare-string"),
])

#: A live prior of two OTHER lanes' claims. Without this leg every assertion below is satisfied
#: by a harness that destroys the store itself, and "the corrupt case matches the good case"
#: would read as a pass.
LIVE_CLAIMS = {
    "lane-a": {"claimed_at": 1000.0, "note": "another lane", "paths": ["x.py"]},
    "lane-b": {"claimed_at": 2000.0, "note": "a third lane", "paths": ["y.py"]},
}


@pytest.fixture(scope="module")
def live():
    return census.derive()


# ── the seam itself ────────────────────────────────────────────────────────────────────────

def _scan_source(src: str) -> dict:
    """Scan a source string as if it were a module under a scanned root."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td) / "background"
        root.mkdir()
        f = root / "m.py"
        f.write_text(src)
        return census._scan_module(f, Path(td))


def test_a_parameter_alias_is_recorded_as_the_parameter_a_caller_can_bind():
    """`p = Path(path)` then `p.read_text()` is a read of the PARAMETER `path`.

    Recording the alias `p` instead is the defect that made the first cut of this repair restore
    only one of the five carriers: a caller binds arguments to `path`, and `p` means nothing to
    it. This asserts the root, so returning the alias fails here."""
    facts = _scan_source(
        "from pathlib import Path\n"
        "def loader(path):\n"
        "    p = Path(path)\n"
        "    return p.read_text()\n"
    )
    fn = facts["background/m.py::loader"]
    assert fn["params"] == ["path"]
    assert fn["param_reads"] == ["path"], (
        "the alias must resolve to the parameter a caller can bind, not to the local name")


def test_a_files_contents_never_become_an_alias_of_its_path():
    """`raw = p.read_text()` must NOT make `raw` a path alias.

    The taint has to stop at the read. If it does not, every function taking the PARSED DATA
    onward is recorded as reading the state file, and the census's writer/reader sets inflate
    until the intersection means nothing -- the failure mode `_record_callsite` and
    `_is_path_shaped` both exist to prevent."""
    facts = _scan_source(
        "from pathlib import Path\n"
        "def loader(path):\n"
        "    p = Path(path)\n"
        "    raw = p.read_text()\n"
        "    other(raw)\n"
        "    return raw\n"
        "def other(blob):\n"
        "    return blob\n"
    )
    fn = facts["background/m.py::loader"]
    calls = {c[0] for c in fn["callsites"]}
    assert "other" not in calls, (
        "the contents of the file were recorded as naming the file: a read's RESULT became a "
        "path alias, and the parameter walk will now attribute reads that never happened")


def test_a_keyed_argument_is_walked_into_the_helper_that_reads_it():
    """The whole repair in one shape: `helper(STATE_PATH)` where `helper` reads its parameter is
    a read of that state file BY THE CALLER."""
    facts = _scan_source(
        'STATE = "docs/observability/.example_state.json"\n'
        "from pathlib import Path\n"
        "def helper(path):\n"
        "    return Path(path).read_text()\n"
        "def caller():\n"
        "    return helper(STATE)\n"
    )
    assert census._attribute_through_parameters(facts) > 0
    assert ".example_state.json" in facts["background/m.py::caller"]["reads"]


def test_the_walk_reaches_through_a_pass_through_helper():
    """Two hops, which is what `episode_prior` actually is: `load_episode_prior(path)` hands its
    own parameter to `classify_prior`.

    THE DEFINITION ORDER IS REVERSED ON PURPOSE, and it is the whole control. Functions are
    visited in definition order, so with `inner` first a SINGLE pass already reaches the caller
    and a non-fixpoint implementation passes -- which is exactly what happened: the
    "reduce the fixpoint to one pass" mutation survived this file until the order was flipped.
    Defined caller-first, one pass learns `outer` reads its parameter but has already been past
    `caller`, so only a second iteration attributes the key. A carrier's helpers are in whatever
    order their module happens to declare them, so the walk cannot depend on a lucky one."""
    facts = _scan_source(
        'STATE = "docs/observability/.example_state.json"\n'
        "from pathlib import Path\n"
        "def caller():\n"
        "    return outer(STATE)\n"
        "def outer(path):\n"
        "    return inner(path)\n"
        "def inner(p):\n"
        "    return Path(p).read_text()\n"
    )
    census._attribute_through_parameters(facts)
    assert facts["background/m.py::outer"]["param_reads"] == ["path"]
    assert ".example_state.json" in facts["background/m.py::caller"]["reads"], (
        "the walk stopped after one hop, so a carrier two helpers deep is invisible")


def test_a_keyed_argument_to_a_writing_parameter_counts_as_writing_it_here():
    """`preserve_unreadable(STATE_PATH)` writes the state file AT THE CALL SITE.

    `_writes_at_close_range` already counts "through one hop into a writer helper" as writing it
    yourself, so a recovered write has to join `direct_writes` too -- otherwise the carrier is a
    reader-only path and can never be a hit."""
    facts = _scan_source(
        'STATE = "docs/observability/.example_state.json"\n'
        "from pathlib import Path\n"
        "def writer(path, data):\n"
        "    Path(path).write_text(data)\n"
        "def caller():\n"
        "    writer(STATE, 'x')\n"
    )
    census._attribute_through_parameters(facts)
    caller = facts["background/m.py::caller"]
    assert ".example_state.json" in caller["writes"]
    assert ".example_state.json" in caller["direct_writes"]


# ── the live tree: the five carriers, and the erosion made loud ───────────────────────────

@pytest.mark.parametrize("key", LOST_TO_THE_SEAM)
def test_a_carrier_repaired_through_the_shared_helper_stays_in_the_class(live, key):
    """THE PROPERTY. Routing a read through `episode_prior` is the repair this project asks for,
    and it must not remove the carrier from the census that found it."""
    assert key in live["hits"], (
        "{} is repaired through the shared loader and has fallen out of the census -- the "
        "parameter seam has re-opened".format(key))


def test_the_published_run_count_has_a_reader_on_record(live):
    """`count_run_history_total` IS the Project tab's "Sim runs" KPI. After the sweep the census
    recorded ZERO readers for the file it reads -- keyed to the named function, not to a count,
    so this stays green if other readers come and go."""
    readers = live["state_paths"]["run_history.json"]["readers"]
    assert any(r.endswith("::count_run_history_total") for r in readers), (
        "the KPI's own reader is not on record as reading run_history.json")


def test_the_parameter_walk_is_what_puts_them_there(monkeypatch, live):
    """THE ORDERING LEG: the two derivations must give DIFFERENT answers.

    Without this, every assertion above is satisfiable by a census that would have found those
    carriers anyway, and the parameter walk could be deleted with the file still green. Disabling
    the walk must LOSE the carriers -- that is what makes the walk load-bearing rather than
    decorative."""
    monkeypatch.setattr(census, "_attribute_through_parameters", lambda facts: 0)
    without = set(census.derive()["hits"])
    lost = set(LOST_TO_THE_SEAM) - without
    assert lost, (
        "disabling the parameter walk changed nothing, so it is not what attributes these "
        "carriers and this file is proving something else")
    assert set(LOST_TO_THE_SEAM) <= set(live["hits"])


def test_the_artefact_records_how_many_attributions_the_seam_recovered(live):
    """Zero here over a non-empty tree is the erosion returning silently. Recorded in the
    artefact for the same reason the classifiers are: a derivation nobody can audit is one
    nobody can dispute."""
    assert live["parameter_attributions"] > 0


# ── the carrier this exposed: the seat's own claims store ─────────────────────────────────

def _claim_over(raw, tmp_path):
    """Run a real `claim()` over a store in state `raw` (None = no file), on a live prior of two
    OTHER lanes' claims where the state is readable. Returns (store_after, sidecars).

    The store gets its OWN directory: `tmp_path` itself carries other fixtures' files, and
    listing it whole once made this read three unrelated names as preserved copies."""
    d = tmp_path / "claims_store"
    d.mkdir()
    p = d / "claims.json"
    if raw is not None:
        p.write_text(raw)
    swh.claim("mine", "new work", ["z.py"], path=p, now=9000.0)
    return json.loads(p.read_text()), sorted(q.name for q in d.iterdir()
                                             if q.name != "claims.json")


def test_a_readable_store_keeps_every_other_lanes_claim(tmp_path):
    """THE LIVE-PRIOR CONTROL LEG, asserted FIRST. Without it a harness that destroys the store
    itself would make every corrupt-state assertion below pass for the wrong reason."""
    after, _ = _claim_over(json.dumps(LIVE_CLAIMS), tmp_path)
    assert sorted(after) == ["lane-a", "lane-b", "mine"]
    assert after["lane-a"]["claimed_at"] == 1000.0, "an untouched claim's episode start moved"


@UNREADABLE_RAW
def test_an_unreadable_claims_store_is_preserved_before_it_is_rebuilt_over(raw, tmp_path):
    """Measured at HEAD before this repair: all five unreadable states silently wrote a
    ONE-claim store over both live claims, with no crash and no copy kept -- and `claimed_at` is
    what `last_progress`/`stale_claims` derive `idle_seconds` from, so every surviving claim's
    staleness episode restarted at zero.

    The loss is made RECOVERABLE, not prevented: refusing to claim on a corrupt byte would wedge
    the seat, which is a worse failure than a preserved sidecar and a re-claim."""
    _, sidecars = _claim_over(raw, tmp_path)
    assert sidecars, (
        "an unreadable claims store was rebuilt over with no copy kept -- the other lanes' "
        "claims are gone and nothing recorded that they existed")


def test_an_absent_store_preserves_nothing(tmp_path):
    """ABSENT IS NOT UNREADABLE. No file means no claim was ever recorded, so there is nothing to
    preserve and a sidecar here would be litter beside every first claim on a fresh checkout."""
    _, sidecars = _claim_over(None, tmp_path)
    assert sidecars == []


@UNREADABLE_RAW
def test_releasing_from_an_unreadable_store_writes_nothing(raw, tmp_path):
    """`release` finds nothing to pop in a `{}` store and returns False BEFORE writing. The
    preserve belongs with the write; asserting it here would pin the wrong seam."""
    p = tmp_path / "claims.json"
    p.write_text(raw)
    before = p.read_bytes()
    assert swh.release("mine", path=p) is False
    assert p.read_bytes() == before, "a no-op release rewrote the store it could not read"
