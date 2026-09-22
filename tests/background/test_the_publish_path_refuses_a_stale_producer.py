"""THE DEFECT THIS NAMES: the stale-copy refusal guards a COMMIT, and the publisher never goes
through it.

`tools/stale_copy_refusal.py` is wired into `surgical_land` and into the pre-commit hook, so a
working copy that reverts its own last landing cannot be COMMITTED. The publish path does not
commit those bytes -- it IMPORTS the working-tree copy of `tools/generate_*.py`, runs it, and
writes `site/data/*.json`. Those outputs carry the clock of the moment they were written, so
`clock_judge` exempts them by construction, and no control anywhere in the tree could tell a feed
regenerated from HEAD from one regenerated from a copy that reverts HEAD.

Measured on the live tree, 2026-09-22: `tools/generate_value_arms_data.py` was a working copy that
reinstated "MEMORY IS NOT WHAT BINDS ... slack by 4.5x" and deleted the whole-run measurement that
refuted it by 29.2x. The only thing between the site and that paragraph was that nothing happened
to run the generator first.
"""

from __future__ import annotations

import os
import subprocess
import sys
from contextlib import contextmanager
from pathlib import Path

import pytest

from background import process_run_complete as prc
from tools import stale_copy_refusal as scr


def _run(root: Path, *args: str) -> str:
    out = subprocess.run(["git", *args], cwd=str(root), capture_output=True, text=True, check=True)
    return out.stdout


def _commit(root: Path, path: str, text: str, message: str) -> str:
    (root / path).parent.mkdir(parents=True, exist_ok=True)
    (root / path).write_text(text)
    _run(root, "add", path)
    _run(root, "commit", "-qm", message)
    return _run(root, "rev-parse", "HEAD").strip()


BEFORE = (
    "OUT_PATH = 'site/data/x.json'\n\n\n"
    "def generate():\n"
    '    """MEMORY IS NOT WHAT BINDS -- the ceiling is tens of thousands of customer-years."""\n'
    "    return stage_cost_arithmetic()\n"
)

LANDED = (
    "OUT_PATH = 'site/data/x.json'\n\n\n"
    "def generate():\n"
    '    """CORRECTED: memory does bind, and the old note was optimistic by 29.2x."""\n'
    "    measured = whole_run_rss_curve()\n"
    "    return measured\n"
)

#: The revert -- older than the landing and carrying none of it.
STALE = BEFORE + "\n\ndef helper():\n    return 0\n"

#: MERELY DIRTY, which is the state the guard must NOT refuse: an edit made ON TOP of the landing,
#: after it, by a lane doing ordinary work. Far and away the commonest state of a producer on this
#: tree, and refusing it would wedge publishing and become the pressure toward bypass.
DIRTY = LANDED + "\n\ndef a_new_helper():\n    return 1\n"


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    """A real git repo, for the reason `test_stale_copy_refusal` gives: this control's subject is
    git trees, and a fake tree reader is a fake more permissive than its subject."""
    root = tmp_path / "r"
    (root / "tools").mkdir(parents=True)
    _run(root, "init", "-q", "-b", "main")
    _run(root, "config", "user.email", "t@t")
    _run(root, "config", "user.name", "t")
    (root / "README").write_text("x\n")
    _run(root, "add", "README")
    _run(root, "commit", "-qm", "base")
    return root


def _producer(root: Path, name: str, on_disk: str | None, *, older: bool = True) -> str:
    """Land `LANDED` over `BEFORE` for `tools/<name>.py`, then optionally put `on_disk` there."""
    path = "tools/{}.py".format(name)
    _commit(root, path, BEFORE, "the producer as it stood")
    sha = _commit(root, path, LANDED, "lane B lands the correction")
    if on_disk is not None:
        (root / path).write_text(on_disk)
        landed_at = scr.committed_at(root, sha)
        offset = -60 if older else 60
        os.utime(root / path, (landed_at + offset, landed_at + offset))
    return path


def test_the_whole_producer_partition_is_reachable_in_one_tree(repo: Path) -> None:
    """A CONTROL OVER THE PARTITION, NOT A LEG PER BRANCH. `refused_to_run` hardwired to `{}`
    passes every clean and dirty leg; hardwired to refuse everything passes the stale one. Only
    asking for all three answers of one tree at once refuses both, and "a producer that is stale,
    one that is merely dirty, and one that is clean" is the whole population a publish cycle meets.
    """
    stale = _producer(repo, "generate_stale", STALE)
    dirty = _producer(repo, "generate_dirty", DIRTY, older=False)
    clean = _producer(repo, "generate_clean", None)

    refused = scr.refused_to_run([stale, dirty, clean], root=repo)

    assert stale in refused, (
        "a producer whose working copy reverts its own last landing was not refused, so the "
        "publish path would regenerate its feed from the revert")
    assert dirty not in refused, (
        "an ordinary edit made after the landing was refused -- this guard now wedges publishing "
        "on the normal state of a shared checkout, which is the pressure toward bypass")
    assert clean not in refused, "an unmodified producer was refused"


def test_the_refusal_names_the_path_and_the_landing_it_predates(repo: Path) -> None:
    """A REFUSAL THAT NAMES NEITHER CANNOT BE ACTED ON AND CANNOT BE SHOWN TO BE WRONG. The reader
    is a log line in a 25-minute publish cycle; "a producer was stale" sends nobody anywhere."""
    stale = _producer(repo, "generate_stale", STALE)
    sha = _run(repo, "log", "-1", "--format=%H", "--", stale).strip()
    text = scr.producer_refusal(scr.refused_to_run([stale], root=repo)[stale])

    assert stale in text, "the refusal does not name the path"
    assert sha[:9] in text, "the refusal does not name the landing the copy predates"
    assert "refresh_to_head" in text, "the refusal names no route out"
    assert "NOT refreshed" in text, (
        "the refusal does not say the artefact was left alone, so a reader could take it for a "
        "warning about a feed that was regenerated anyway")


def test_a_refused_producer_raises_at_the_import_and_is_put_back_after(repo: Path) -> None:
    """THE REFUSAL IS DELIVERED AT THE IMPORT, so the step's own `except` records which artefact it
    did NOT refresh -- the machinery built for the 199 swallowed generator crashes, which is
    exactly the shape a producer refused for staleness has.

    AND IT IS LIFTED ON THE WAY OUT. This is a long-lived daemon: a stand-in left in `sys.modules`
    would refuse that producer on every later cycle too, including the cycle after the copy was
    restored, and a refusal that outlives its own reason is a wedge."""
    dotted = "tools.a_producer_that_does_not_exist_on_disk"
    sentinel = object()
    sys.modules[dotted] = sentinel  # stands for "already imported by an earlier cycle"
    try:
        loss = scr.Loss("tools/p.py", scr.PREDATES, ("a landed line",), "abc123def", gains=())
        stale_producers = {"tools/p.py": loss}
        lines: list[str] = []

        def _refused_to_run(paths, root=None):
            return {p: stale_producers[p] for p in paths if p in stale_producers}

        original = scr.refused_to_run
        scr.refused_to_run = _refused_to_run
        try:
            with prc.refuse_stale_producers(log_fn=lines.append,
                                            producers={dotted: "tools/p.py"}) as poisoned:
                assert poisoned == frozenset({dotted}), "the producer was not poisoned"
                with pytest.raises(scr.StaleProducer):
                    sys.modules[dotted].generate
                with pytest.raises(scr.StaleProducer):
                    sys.modules[dotted].main
        finally:
            scr.refused_to_run = original

        assert sys.modules[dotted] is sentinel, (
            "the stand-in outlived the block, so this producer is refused for the rest of the "
            "daemon's life -- including after the copy is restored")
        assert lines and "tools/p.py" in lines[0], "the refusal was not said out loud"
    finally:
        sys.modules.pop(dotted, None)


def test_a_census_that_will_not_run_leaves_the_site_publishing_and_says_so(repo: Path) -> None:
    """FAILS OPEN ON ITS OWN FAILURE, DELIBERATELY, AND THE LOG LINE IS THE SURFACE. The census
    shells out to git. The thing this guards against is rare; a dead publisher is not, and a guard
    that takes the site down when git hiccups is a worse bargain than the one it replaces. What is
    NOT negotiable is silence -- an unarmed guard that says nothing is the shape this file already
    paid for once, in 199 swallowed generator crashes."""
    original = scr.refused_to_run

    def _explode(paths, root=None):
        raise RuntimeError("git would not answer")

    scr.refused_to_run = _explode
    lines: list[str] = []
    try:
        with prc.refuse_stale_producers(log_fn=lines.append,
                                        producers={"tools.x": "tools/x.py"}) as poisoned:
            assert poisoned == frozenset(), "a census that did not run refused a producer anyway"
    finally:
        scr.refused_to_run = original

    assert lines and "UNGRADED" in lines[0], (
        "the census failed and nothing said so, so the cycle reads as graded-and-clean")


def test_the_producer_register_is_the_publish_paths_own_imports(repo: Path) -> None:
    """A HAND-KEPT REGISTER IS WRONG THE FIRST TIME A GENERATOR IS WIRED IN WITHOUT IT, and the
    wiring is the only evidence that matters. All three import shapes are live in that file, so all
    three are asked for here; a reader that handles two of them is silently scoped to a subset,
    which is this project's commonest way to ship a guard that looks total."""
    found = prc._site_producers(
        "from tools.generate_one import generate\n"
        "from tools import generate_two\n"
        "import tools.generate_three\n"
        "from background.notify import notify\n"
        "from tools import stale_copy_refusal\n")

    assert found == {
        "tools.generate_one": "tools/generate_one.py",
        "tools.generate_two": "tools/generate_two.py",
        "tools.generate_three": "tools/generate_three.py",
    }, "an import shape the publish path actually uses is invisible to the register"

    live = prc._site_producers()
    assert "tools.generate_value_arms_data" in live, (
        "the generator this guard was written for is not in its own register")
    assert "tools.stale_copy_refusal" not in live, (
        "the guard poisons the module that IS the guard")


def test_the_entry_point_holds_the_refusal_over_every_return_below_it(repo: Path) -> None:
    """THE WIRING, NOT A RESTATEMENT OF IT. `generate_dashboard_json` has several returns -- the
    coverage gate's early one among them -- so the refusal is a WRAPPER and not a first statement
    in the body: any early return would otherwise leave the stand-ins in `sys.modules`.

    THE SUBJECT IS WHAT THE BODY SEES, NOT WHAT THE WRAPPER SAYS. A first draft of this asked
    whether `inspect.getsource` contained "refuse_stale_producers", and unwiring the guard entirely
    left it GREEN -- the wrapper's own DOCSTRING contains the name. A control a comment can satisfy
    is not a control, and this one is keyed to the property instead: at the moment the body runs, a
    stale producer must already be poisoned in `sys.modules`."""
    dotted = "tools.a_producer_the_body_would_import"
    seen: dict[str, object] = {}

    def _probe(json_path, git_hash="unknown"):
        seen["at_body"] = type(sys.modules.get(dotted)).__name__
        return "the body ran"

    def _refused_to_run(paths, root=None):
        return {p: scr.Loss(p, scr.PREDATES, ("a landed line",), "abc123def", gains=())
                for p in paths}

    originals = (prc._generate_dashboard_json, prc._site_producers, scr.refused_to_run)
    prc._generate_dashboard_json = _probe
    prc._site_producers = lambda source=None: {dotted: "tools/p.py"}
    scr.refused_to_run = _refused_to_run
    try:
        result = prc.generate_dashboard_json("site/data/dashboard.json", git_hash="deadbeef")
    finally:
        (prc._generate_dashboard_json, prc._site_producers, scr.refused_to_run) = originals
        sys.modules.pop(dotted, None)

    assert result == "the body ran", "the wrapper no longer reaches the body it wraps"
    assert seen.get("at_body") == "_RefusedProducer", (
        "the publish path's entry point reached its body with a stale producer un-poisoned, so "
        "every generator below it is ungraded again")
    assert not isinstance(sys.modules.get(dotted), prc._RefusedProducer), (
        "the wrapper returned without lifting the refusal")


def test_the_register_spans_every_first_party_root_the_publisher_runs(repo: Path) -> None:
    """A CONTROL OVER THE ROOT PARTITION, NOT A LEG PER ROOT. The register's first filter was the
    prefix `tools.`, which passes every assertion anyone thought to write about a generator and is
    BLIND to two producers named in `background/publish_scope.py`'s own PUBLISH_PATH_SOURCES:
    `simulation.publish_market_feed` and `simulation.publish_consumption_data`, which `_process`
    imports, runs, and publishes `docs/market_data/*.json` from.

    Asking for all four roots of one parse at once is what makes this unpassable by a filter
    scoped to a minority: `tools`-only fails the simulation and saas legs, and a filter widened to
    "every first-party import" fails the background leg. A guard that refuses everything and a
    guard that refuses one root are both caught here, which is the point -- neither is caught by a
    leg that only asks whether the root it was written for is present."""
    found = prc._site_producers(
        "from tools.generate_one import generate\n"
        "from simulation.publish_market_feed import publish\n"
        "from simulation import publish_consumption_data\n"
        "from saas.reporting.annual_report import render\n"
        "import tools.generate_three\n"
        "from background.notify import notify\n"
        "from background import naive_organ\n")

    assert found == {
        "tools.generate_one": "tools/generate_one.py",
        "tools.generate_three": "tools/generate_three.py",
        "simulation.publish_market_feed": "simulation/publish_market_feed.py",
        "simulation.publish_consumption_data": "simulation/publish_consumption_data.py",
        "saas.reporting.annual_report": "saas/reporting/annual_report.py",
    }, (
        "the producer register does not span the roots the publish path actually runs -- a root "
        "it cannot see is a root whose reverted copy regenerates a published feed unrefused")

    live = prc._site_producers()
    assert "simulation.publish_market_feed" in live, (
        "the live register cannot see simulation.publish_market_feed, which _process imports and "
        "publishes docs/market_data/price_feed.json from")
    assert not any(d.startswith("background.") for d in live), (
        "the register poisons the publisher's own machinery -- background.notify is how a refusal "
        "is REPORTED, so poisoning it trades a wrong number for a silent one")


def test_the_refusal_is_held_over_the_producers_process_runs_after_the_dashboard(repo: Path) -> None:
    """THE SCOPE, AND IT IS THE HALF THAT WAS STILL OPEN. `generate_dashboard_json`'s wrapper
    covers its own ~40 generators and lifts the stand-ins on the way out -- but `_process` then
    imports and runs six more producers of its own: revenue_sanity_check, the two simulation
    feeds, the grid-intensity feed, generate_explore_carbon and couple_value_based_pricing.

    Measured on the live tree 2026-09-22: the census REFUSED
    `tools/couple_value_based_pricing.py` (a working copy predating c4809c5fc) while the guard as
    landed would have imported and run it -- the exact defect this door exists for, alive inside
    the door's own blind spot.

    KEYED TO THE PROPERTY, NOT TO THE WIRING'S TEXT, for the reason its sibling records: a control
    that greps `main` for "refuse_stale_producers" is satisfied by this docstring. The subject is
    what `_process` SEES: at the moment its body runs, a stale producer must already be poisoned."""
    dotted = "tools.a_producer_process_imports_after_the_dashboard"
    seen: dict[str, object] = {}

    def _probe(marker_path_str):
        seen["at_body"] = type(sys.modules.get(dotted)).__name__
        return 0

    def _refused_to_run(paths, root=None):
        return {p: scr.Loss(p, scr.PREDATES, ("a landed line",), "abc123def", gains=())
                for p in paths}

    @contextmanager
    def _always_acquired():
        yield True

    originals = (prc._process, prc._site_producers, scr.refused_to_run, prc._run_lock)
    prc._process = _probe
    prc._site_producers = lambda source=None: {dotted: "tools/p.py"}
    scr.refused_to_run = _refused_to_run
    prc._run_lock = _always_acquired
    try:
        result = prc.main("staging/run_complete_x.md")
    finally:
        (prc._process, prc._site_producers, scr.refused_to_run, prc._run_lock) = originals
        sys.modules.pop(dotted, None)

    assert result == 0, "the cycle entry point no longer reaches the body it wraps"
    assert seen.get("at_body") == "_RefusedProducer", (
        "_process ran with a stale producer un-poisoned, so every producer it imports after "
        "generate_dashboard_json returns is ungraded -- which is where the live one was")
    assert not isinstance(sys.modules.get(dotted), prc._RefusedProducer), (
        "the refusal outlived the cycle; this is a long-lived daemon and that is a wedge")
