"""`--module` indexed dotted names and refused paths by blaming the caller count.

THE DEFECT THIS NAMES (delivery seat, 2026-09-06). The screen's ranked table prints dotted module
names; every finding, commit message and staged direction in this project spells the same module as
a PATH. `--module tools/generate_company_data.py` therefore matched nothing, and the refusal said
`is not a converged module (<3 first-party callers, or not a repo module)` and exited 0.

Both stated reasons were false and the true one -- "I index dotted names and you gave me a path" --
was not among them. It sent the seat looking for a caller that had never disappeared, on the
subject the sweep had ranked NEXT. **A refusal that offers plausible reasons instead of the true one
is worse than a bare refusal: it is a wrong answer with a rationale attached.** That is this
project's own rule (`CLAUDE.md`, "write refusals that name their reason") failing on the instrument
that ranks the work.

R15: these legs are keyed to the PROPERTY, not to today's screen. No module name, caller count or
threshold value is pinned -- the below-threshold subject is discovered from the screen at run time,
so this file goes green when the census changes and red when the lookup breaks.
"""
from __future__ import annotations

import pytest

from tools.converged_contract_screen import (
    CONVERGED_AT,
    _as_module_name,
    main,
    screen,
)


@pytest.fixture(scope="module")
def rows():
    return screen()


@pytest.mark.parametrize("given", [
    "tools/converged_contract_screen.py",
    "tools/converged_contract_screen",
    "tools.converged_contract_screen",
])
def test_the_three_spellings_of_one_subject_are_one_subject(given):
    assert _as_module_name(given) == "tools.converged_contract_screen"


def test_a_converged_module_is_found_by_its_path_not_only_its_dotted_name(rows, capsys):
    """The leg that was red before this repair. Uses whatever the screen ranks FIRST, so it
    cannot rot into a test of one module that happened to be converged in September."""
    subject = rows[0]["module"]
    path = subject.replace(".", "/") + ".py"

    assert main(["--module", path]) == 0
    assert subject in capsys.readouterr().out, (
        f"{path} is the ordinary way this repo spells {subject} and the screen must resolve it"
    )


def test_a_name_that_is_not_a_repo_module_says_so_and_exits_nonzero(capsys):
    """A failed LOOKUP and the answer 'below the threshold' are different claims, and a script
    asking for a subject's row has to be able to tell them apart."""
    rc = main(["--module", "tools/there_is_no_module_with_this_name_at_all.py"])
    out = capsys.readouterr().out

    assert rc == 2
    assert "does not resolve to a module in this repo" in out
    assert "first-party caller" not in out, (
        "the old message blamed the caller count for a name that has no callers to count"
    )


def test_a_real_module_below_the_threshold_reports_its_actual_caller_count(rows, capsys):
    """The other side of the partition, and the reason the refusal above cannot just be
    `return 2` for everything: a repo module that is simply not converged is an ANSWER."""
    converged = {r["module"] for r in rows}
    below = next((r for r in screen(converged_at=1)
                  if r["module"] not in converged and r["n_callers"] < CONVERGED_AT), None)
    if below is None:
        pytest.skip("no first-party module sits below the threshold in this tree")

    rc = main(["--module", below["module"].replace(".", "/") + ".py"])
    out = capsys.readouterr().out

    assert rc == 0, "a module that exists and is under-called is answered, not failed"
    assert str(below["n_callers"]) in out and "below the" in out, (
        "the refusal must report the count it actually measured, not recite the threshold"
    )
