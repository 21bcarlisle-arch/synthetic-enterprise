"""A published surface must be reproducible from the artefacts committed BESIDE it.

THE DEFECT THIS EXISTS FOR, measured 2026-08-31 and re-measured 2026-09-01.
`site/data/customers.json` published 164 households / 251 legs. The generator that derives it,
`tools/generate_customers_json`, reads `docs/reports/run_output_latest.json` — and the copy of that
file committed in the same tree held **19 account legs**. Running the generator against the
committed input produced **14 households / 19 legs** against a published 164 / 251.

WHICH OF THE TWO WAS WRONG, which the finding explicitly refused to guess, is now measured. The
published surface is the honest one: run the generator against the run output that was sitting
UNCOMMITTED in the working tree and it reproduces the published book exactly — 164 households, 251
legs, identical household ids in identical order. So the input was the reduced artefact (a scale
probe committed over the real one on 2026-08-19 and never replaced), and twelve days of publishes
shipped the OUTPUT without the INPUT. The page was right and the tree could not show it.

WHY THIS IS NOT ALREADY COVERED. `publish_provenance.json`, the banner adoption control and the
basis gate each check that a published figure carries a CLOCK. None of them checks that the figure's
INPUT is the input in the same commit. A figure can carry a perfect timestamp and still be
underivable from everything shipped with it, and that is the state this repo was actually in.

IT ALSO SILENTLY DEFEATS EVERY OTHER CONTROL OVER THE SURFACE. A control asserting on
`customers.json` goes red or green according to when the publisher last ran rather than according to
whether the code is right. `tests/tools/test_a_published_rate_says_which_rate_it_is` hit exactly
that wall and had to assert against the generator instead of the artefact, saying so in its own
docstring. That workaround is only needed while this control does not exist.

WHAT IT DOES NOT COVER, stated rather than left to be discovered. One pair — `customers.json` from
`run_output_latest.json`. The other ~30 `site/data/*.json` generators are not wired here. Most read
the same run output and would be one row each; several read artefacts that are themselves generated,
which is a chain rather than a pair and wants its own thinking. Extending the table is the rest of
the finding's ask and is recorded as outstanding in the disposition, not quietly closed by this file.

READ AS COMMITTED, NEVER AS EDITED. Both artefacts are read from `HEAD`, not from the working tree.
In this shared tree the working-tree copies routinely agree with each other while the committed ones
do not — which is precisely the defect, so a disk read would have been green throughout the twelve
days it was live. The one place disk is read instead is the landing checkout that
`tools/surgical_land` builds (`git archive | tar -x` then a fresh `git init`, so HEAD resolves to
nothing): there the files on disk ARE the tree being graded, which is the same property by a
different route. Any other git failure is a refusal, not a fallback — a control over what is
committed must not go green because it could not find out.
"""
from __future__ import annotations

import json
import pathlib
import subprocess

import pytest

from tools.generate_customers_json import generate as generate_customers

PROJECT = pathlib.Path(__file__).resolve().parents[2]

#: The published surface, its generator, and the artefact the generator reads. Counts, not bytes:
#: `generated` is a wall-clock stamp and moves on every run, so byte-equality would fail forever
#: while proving nothing.
PUBLISHED = "site/data/customers.json"
INPUT = "docs/reports/run_output_latest.json"


def _head_resolves() -> bool:
    """Does this checkout have a commit to read? The landing checkout does not."""
    try:
        done = subprocess.run(["git", "rev-parse", "--verify", "HEAD"], cwd=str(PROJECT),
                              capture_output=True, text=True, check=False)
    except (OSError, subprocess.SubprocessError):
        return False
    return done.returncode == 0


def _as_committed(rel: str) -> str:
    """The bytes of `rel` in the tree being graded.

    `HEAD` when there is one; the file on disk in a landing checkout, where disk IS the tree. A
    path that git has but cannot produce is a FAILURE and not a skip: the whole claim is about what
    is committed, so "I could not tell" has to be red.
    """
    if not _head_resolves():
        on_disk = PROJECT / rel
        assert on_disk.is_file(), (
            f"{rel} is neither at HEAD nor on disk. The tree being graded does not contain the "
            "artefact this control is about."
        )
        return on_disk.read_text()
    done = subprocess.run(["git", "show", f"HEAD:{rel}"], cwd=str(PROJECT),
                          capture_output=True, text=True, check=False)
    assert done.returncode == 0, (
        f"`git show HEAD:{rel}` failed rc={done.returncode}: {done.stderr.strip()[-300:]}\n"
        "A published surface and the input it is derived from must both be IN the commit that "
        "ships them. If this path is untracked, that is the finding, not a reason to skip."
    )
    return done.stdout


def _population(surface: dict) -> list[tuple[str, tuple[str, ...]]]:
    """Who is in the book, and which fuel legs each of them has.

    Stronger than a count and still invariant to every timestamp, rounding and money field — a
    surface can only match if it names the same households for the same reasons.
    """
    return [
        (c["customer_group"], tuple(sorted((c.get("legs") or {}).keys())))
        for c in surface.get("customers", [])
    ]


def test_the_published_customer_book_is_reproducible_from_the_run_output_committed_beside_it(
    tmp_path,
):
    """Regenerate the surface from the committed input; the population must be the same one.

    THE DEFECT THIS FAILS ON: `site/data/customers.json` shipping a book the run output committed
    with it cannot produce — 164 households published against 14 derivable, which is the state
    measured at `847503708`.
    """
    published = json.loads(_as_committed(PUBLISHED))

    run_json = tmp_path / "committed_input.json"
    run_json.write_text(_as_committed(INPUT))
    rebuilt = generate_customers(run_json, tmp_path / "rebuilt.json")

    want, got = _population(published), _population(rebuilt)

    # FAIL CLOSED ON AN EMPTY BOOK. Two empty populations compare equal, so without this the
    # control certifies a surface with no households in it from an input with no accounts in it.
    # The floor is EMPTINESS and not today's 164: the director's ruling on this very artefact was
    # that a book which honestly shrinks should be published at its smaller size with the reason
    # beside it, and a control pinned to the current count would go red for exactly that.
    assert want, (
        f"{PUBLISHED} at HEAD publishes no households at all. An empty book cannot certify itself "
        "reproducible."
    )

    assert got == want, (
        "THE PUBLISHED SURFACE IS NOT DERIVABLE FROM THE ARTEFACTS SHIPPED WITH IT.\n"
        f"  {PUBLISHED} publishes {len(want)} households / {sum(len(f) for _, f in want)} legs\n"
        f"  {INPUT} regenerates {len(got)} households / {sum(len(f) for _, f in got)} legs\n"
        f"  published but not derivable: {sorted(set(dict(want)) - set(dict(got)))[:10]}\n"
        f"  derivable but not published: {sorted(set(dict(got)) - set(dict(want)))[:10]}\n"
        "Either the input was not committed with the surface it produced, or the surface is "
        "carried forward from a run the tree no longer holds. Publish the page from the input in "
        "this commit, and if that book is smaller, say on the page why it moved."
    )


def test_the_control_reads_the_commit_and_not_the_working_copy():
    """The reader is `git show HEAD:`, so an unlanded edit cannot make the surface look derivable.

    THE DEFECT THIS FAILS ON: reading `site/data/customers.json` and the run output off disk. In
    this tree those two working copies agreed with each other for the whole twelve days the
    committed pair disagreed, so a disk-reading version of the leg above would have been green
    throughout and is the single most likely way this control gets quietly neutered later.
    """
    if not _head_resolves():
        pytest.skip("landing checkout: there is no HEAD, and disk IS the tree being graded")

    committed = _as_committed(PUBLISHED)
    on_disk = (PROJECT / PUBLISHED).read_text()
    if committed == on_disk:
        pytest.skip(f"{PUBLISHED} is unmodified, so the two readers cannot be told apart here")

    assert json.loads(committed)["generated"] != json.loads(on_disk)["generated"], (
        "the working copy differs from HEAD but carries the same stamp — cannot establish which "
        "of the two the control above read"
    )
