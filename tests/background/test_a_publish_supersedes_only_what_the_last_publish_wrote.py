"""The publisher declares as drops only the paths the previous publish wrote and nothing touched since.

Defect it names: the 6fe7827ab2 publish refused because the stale-copy guard read 19aa987bc's own
3 Nov page stamps as landed work (11 Nov) -- or the opposite, a declaration wide enough to let the
publish revert another lane's landing."""
from pathlib import Path
from types import SimpleNamespace

from background import process_run_complete as prc


def _git(history):
    def run(argv, **_kw):
        args = argv[1:]
        if args[0] == "log" and "--grep=^" + prc.PUBLISH_SUBJECT_PREFIX in args:
            out = "P\n"
        elif args[0] == "show":
            out = "\n".join(history["published"])
        elif args[0] == "log":
            out = "\n".join(history["since"])
        else:  # diff --name-only HEAD -- <relative>
            out = "\n".join(history["changed"])
        return SimpleNamespace(returncode=0, stdout=out, stderr="")
    return run


def test_the_last_publishs_own_output_is_superseded_and_a_later_landing_is_not():
    history = {"published": ["site/code/index.html", "site/capabilities/index.html", "docs/status/LATEST.md"],
               "since": ["site/capabilities/index.html"],  # a lane landed here after the publish
               "changed": ["site/code/index.html", "site/capabilities/index.html", "site/data/new.json"]}
    got = prc.publisher_superseded_paths(Path("."), ["site"], _run=_git(history))
    assert got == {"site/code/index.html"}


def test_an_unanswerable_history_declares_nothing():
    def broken(argv, **_kw):
        return SimpleNamespace(returncode=128, stdout="", stderr="fatal")
    assert prc.publisher_superseded_paths(Path("."), ["site"], _run=broken) == frozenset()
