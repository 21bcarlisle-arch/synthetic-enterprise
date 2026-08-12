"""The derived-artefact register: completeness, staleness, and HEAD-sourced repair.

WHY THIS EXISTS. Four publish-gate wedges on 2026-08-09/10 shared one cause: a `docs/design/*.md`
projection went stale because an ordinary act (minting an atom, archiving a finding) moved its
sources and nothing regenerated it. `background/derived_artefact_register.py` closes that class.
This file is the proof that the closure can FAIL (R15) rather than merely being present.

MUTATION PROOFS, both directions, executed by the tests below rather than asserted in prose:
  * completeness  -- writing a NEW module that takes `--write` and owns a `docs/design/*.md`
                     path makes `unregistered()` name it; removing it makes the set empty again.
                     This is the direction that matters: the register must not be a hand-kept
                     index that the next derived artefact silently escapes.
  * orphan        -- a register entry whose module does not exist is named by `orphaned()`.
  * staleness     -- corrupting a rendering makes `stale_in()` name it; restoring it clears it.
  * repair        -- a corrupted rendering is restored from a clean source root, and the repair
                     reports convergence.
"""
from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from background import derived_artefact_register as dar  # noqa: E402

MUTANT_SOURCE = '''\
from pathlib import Path
import argparse
PROJECT_DIR = Path(__file__).resolve().parent.parent
MUTANT_DOC_PATH = PROJECT_DIR / "docs" / "design" / "MUTANT_DERIVED_ARTEFACT.md"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    ap.parse_args()
'''


@pytest.fixture
def head_checkout(tmp_path):
    """A throwaway checkout of HEAD to mutate.

    The staleness and repair mutations must corrupt a rendering to prove the control fires. Doing
    that in the REAL tree would transiently plant exactly the defect this register exists to
    prevent -- and a test killed between the corruption and its `finally` would wedge publishing
    for everyone. So the mutations happen in a private `git archive HEAD` extract, which is also
    the production shape: `repair_from` is designed to render from committed truth.

    A CHECKOUT WITH NO HISTORY IS NOT A CHECKOUT OF HEAD. The first version of this fixture
    extracted the archive and stopped there; every repair test then failed, because
    `blocked_atom_visibility`'s clock probe shells out to `git blame` and died with "not a git
    repository". That is the same defect that wedged publishing once already (closed in
    production by `_make_checkout_a_repo`), so the fixture reuses the production helper rather
    than growing a second, weaker copy of it.
    """
    dest = tmp_path / "head"
    dest.mkdir()
    head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=str(REPO_ROOT),
                          capture_output=True, text=True, timeout=60)
    if head.returncode != 0:
        pytest.skip("no HEAD to check out")
    archive = subprocess.run(["git", "archive", "HEAD"], cwd=str(REPO_ROOT),
                             capture_output=True, timeout=300)
    if archive.returncode != 0:
        pytest.skip("could not materialise a HEAD checkout: {}".format(
            archive.stderr.decode(errors="replace")[:200]))
    untar = subprocess.run(["tar", "-x", "-C", str(dest)], input=archive.stdout,
                           capture_output=True, timeout=300)
    if untar.returncode != 0:
        pytest.skip("could not extract the HEAD checkout")
    from background.process_run_complete import _make_checkout_a_repo
    if not _make_checkout_a_repo(dest, head.stdout.strip()):
        pytest.skip("could not make the checkout a real git repo")
    return dest


@pytest.fixture
def mutant_module():
    """Plant a real derived-artefact module in the tree, then remove it.

    Deliberately a REAL file in `tools/` rather than a monkeypatched discovery result: the
    control under test scans the source tree, so a fake that bypasses the scan would prove
    nothing about the scan (the tautology pattern R15 names).
    """
    path = REPO_ROOT / "tools" / "_mutant_derived_artefact.py"
    path.write_text(MUTANT_SOURCE, encoding="utf-8")
    try:
        yield path
    finally:
        path.unlink(missing_ok=True)


class TestCompleteness:
    def test_the_register_agrees_with_the_source_tree(self):
        assert dar.unregistered() == set(), (
            "a derived docs/design artefact exists that the register does not list -- add it to "
            "REGISTER so the publish path repairs it")
        assert dar.orphaned() == set(), (
            "the register lists an artefact the source tree no longer has")

    def test_completeness_fires_on_a_new_unregistered_artefact(self, mutant_module):
        """R15 MUTATION: the control must NAME a newly-added derived artefact."""
        missing = dar.unregistered()
        assert ("tools._mutant_derived_artefact",
                "docs/design/MUTANT_DERIVED_ARTEFACT.md") in missing

    def test_completeness_is_clean_again_once_the_mutant_is_gone(self):
        """The other half of the mutation: it is not simply always-red."""
        assert dar.unregistered() == set()

    def test_orphaned_fires_on_a_register_entry_with_no_module(self, monkeypatch):
        """R15 MUTATION, the other direction: a stale register line must be named."""
        ghost = dar.DerivedArtefact("background.no_such_module_at_all",
                                    "docs/design/NO_SUCH_DOC.md")
        monkeypatch.setattr(dar, "REGISTER", dar.REGISTER + (ghost,))
        assert ("background.no_such_module_at_all", "docs/design/NO_SUCH_DOC.md") in dar.orphaned()

    def test_discovery_does_not_read_the_register(self, monkeypatch):
        """Independence, proven FUNCTIONALLY: emptying the register must not change discovery.

        R15 names the tautology pattern -- a checked value derived from the same source it
        checks. If `discover()` consulted REGISTER, the completeness test could never fail. The
        first version of this test grepped the function's source text for the string "REGISTER",
        which is brittle and proves nothing about behaviour; this drives the actual code.
        """
        before = dar.discover()
        monkeypatch.setattr(dar, "REGISTER", ())
        assert dar.discover() == before, "discover() changed when the register did -- tautology"
        assert before, "discovery found nothing at all; it cannot be an oracle"
        # With an empty register, every discovered artefact must be reported unregistered.
        assert dar.unregistered() == before


@pytest.fixture
def head_checkout_running_tree_code(head_checkout):
    """A HEAD checkout whose registered-artefact MODULES are the working tree's.

    TWO REASONS, and the second is the one that was learned the hard way.

    1. The subject of a control test is the code under review, not the last commit's. `stale_in`
       drives `python -m <module> --check` with `cwd=root`, so a plain HEAD checkout tests the
       COMMITTED oracle -- which means a repair to an oracle could never be proven by its own
       test until after it had landed.
    2. That is not merely awkward, it is the wedge shape this whole register exists to close:
       a repair that sits downstream of its own gate cannot land (filed as
       `WORKER_FINDING_A_REPAIR_DOWNSTREAM_OF_ITS_OWN_GATE_CANNOT_LAND_2026-08-10`). Fixing a
       blind `--check` would have required committing past a gate that the blindness itself
       reds.

    The SOURCES stay HEAD's, which is what `repair_from` is specified against. Only the code
    moves.
    """
    for art in dar.REGISTER:
        src = REPO_ROOT / art.source_file
        if src.is_file():
            shutil.copyfile(src, head_checkout / art.source_file)
    return head_checkout


class TestStaleness:
    def test_staleness_fires_for_EVERY_registered_artefact(
            self, head_checkout_running_tree_code):
        """R15 MUTATION over the POPULATION, not over one member.

        THE DEFECT THIS EXISTS FOR (2026-08-10, eighth publish wedge). The mutation below was
        previously run against `REGISTER[0]` alone. `REGISTER[1]`
        (`background.forward_attachment_register`) had a `--check` that compared only the
        (atom_id, source) PAIRS parsed back out of its rendering -- a strict SUBSET of the
        whole-text equality its own blocking test asserts. So drift in any other dimension
        (there: an atom's `L0→L2 · build_` annotation becoming `L2→L2 · harden_`) was invisible
        to `stale_in`, the publish path's self-healing repair reported "nothing stale", and the
        gate red-ed for ~15h across 91 failures on an artefact the register was supposed to
        cover. One member of a population passing is not the population passing.

        The injected drift is deliberately OUTSIDE any structured field: a trailing comment
        changes no entry, no atom, no count. An oracle that only re-parses its own rows cannot
        see it, and an oracle that compares against a fresh rendering must.

        ONE CHECKOUT, NOT ONE PER ARTEFACT, and the loop reports EVERY blind oracle rather than
        stopping at the first. Parametrising this would read better in a test id, but each
        instance costs a ~130MB `git archive` extraction into a 7.8G tmpfs that this very tick
        found at 100% full -- a suite that exhausts /tmp reds 96 unrelated tests and wedges
        publishing, which is wedge cause #3 all over again. Collecting the failures also means
        a second blind artefact is not hidden behind the first.
        """
        checkout = head_checkout_running_tree_code
        dar.repair_from(checkout, checkout)
        blind, always_red = [], []
        for art in dar.REGISTER:
            doc = checkout / art.rendered
            fresh = doc.read_text(encoding="utf-8")
            assert art not in dar.stale_in(checkout), (
                "{} is not fresh after a repair -- cannot mutation-test from here".format(
                    art.module))

            doc.write_text(fresh + "\n<!-- injected drift -->\n", encoding="utf-8")
            if art not in dar.stale_in(checkout):
                blind.append(art.module)

            doc.write_text(fresh, encoding="utf-8")
            if art in dar.stale_in(checkout):
                always_red.append(art.module)

        assert not blind, (
            "these --check oracles did NOT fire on a drifted rendering: {}. Each covers less "
            "than its own blocking test asserts, so the publish path's self-healing repair is "
            "blind to real staleness in it -- this is the eighth-wedge defect, not a test "
            "artefact.".format(", ".join(blind)))
        assert not always_red, (
            "these --check oracles are always-red, not controls: {}".format(", ".join(always_red)))

    def test_every_registered_artefact_is_currently_fresh(self):
        stale = dar.stale_in(REPO_ROOT)
        assert stale == [], "stale derived artefact(s): {}".format(
            [a.rendered for a in stale])

    def test_staleness_fires_on_a_corrupted_rendering(self, head_checkout):
        """R15 MUTATION: corrupt one rendering; the check must name it, then clear.

        The baseline is established by repairing the checkout FIRST rather than by trusting the
        committed copy. HEAD may legitimately be stale at this moment -- that is the condition
        the register exists for -- and an earlier version of this test restored the committed
        text and then asserted freshness, which reds on the bug rather than on the control.
        """
        art = dar.REGISTER[0]
        dar.repair_from(head_checkout, head_checkout)
        doc = head_checkout / art.rendered
        fresh = doc.read_text(encoding="utf-8")
        assert art not in dar.stale_in(head_checkout), "baseline is not fresh after a repair"

        doc.write_text(fresh + "\n<!-- injected drift -->\n", encoding="utf-8")
        assert art in dar.stale_in(head_checkout), "a corrupted rendering was not reported stale"

        doc.write_text(fresh, encoding="utf-8")
        assert art not in dar.stale_in(head_checkout), "the check is always-red, not a control"


class TestRepair:
    def test_repair_restores_a_corrupted_rendering_and_reports_convergence(self, head_checkout):
        """The repair must actually WRITE, and must say so — a no-op that returns success is
        the fail-open shape this whole register exists to prevent."""
        art = dar.REGISTER[0]
        dar.repair_from(head_checkout, head_checkout)  # baseline; HEAD itself may be stale
        doc = head_checkout / art.rendered
        fresh = doc.read_text(encoding="utf-8")
        doc.write_text("totally wrong\n", encoding="utf-8")

        res = dar.repair_from(head_checkout, head_checkout)

        assert art.rendered in res["repaired"], res
        assert res["converged"], res
        assert doc.read_text(encoding="utf-8") == fresh, (
            "the repair wrote something other than the derivation of committed truth")

    def test_repair_copies_the_rendering_out_to_the_write_root(self, head_checkout, tmp_path):
        """Production shape: render in the HEAD checkout, land the file in the real tree."""
        art = dar.REGISTER[0]
        (head_checkout / art.rendered).write_text("wrong\n", encoding="utf-8")
        write_root = tmp_path / "write"
        (write_root / Path(art.rendered).parent).mkdir(parents=True)

        res = dar.repair_from(head_checkout, write_root)

        assert res["converged"], res
        landed = write_root / art.rendered
        assert landed.exists(), "the repair never wrote into the write_root"
        assert landed.read_text(encoding="utf-8") == (head_checkout / art.rendered).read_text(
            encoding="utf-8")

    def test_repair_is_idempotent(self, head_checkout):
        """A second repair must find nothing to do.

        Asserted as idempotence rather than as "a fresh checkout is never stale": HEAD may
        legitimately carry a stale projection at the moment this runs -- that is the very
        condition the repair exists for -- so a test demanding a clean HEAD would red on the
        bug instead of on the control.
        """
        first = dar.repair_from(head_checkout, head_checkout)
        assert first["converged"], first

        second = dar.repair_from(head_checkout, head_checkout)
        assert second["repaired"] == [], "repair is not idempotent: {}".format(second)
        assert second["converged"], second


class TestSeatGuard:
    def test_the_entrypoint_is_seat_guarded(self):
        """A new background/*.py entrypoint must refuse foreign soil (test_seat_guard_daemons)."""
        source = (REPO_ROOT / "background" / "derived_artefact_register.py").read_text()
        assert 'refuse_if_foreign("derived_artefact_register")' in source


class TestCli:
    def test_completeness_cli_is_green_on_the_real_tree(self):
        proc = subprocess.run(
            [sys.executable, "-m", "background.derived_artefact_register", "--completeness"],
            cwd=str(REPO_ROOT), capture_output=True, text=True, timeout=300)
        assert proc.returncode == 0, proc.stderr
