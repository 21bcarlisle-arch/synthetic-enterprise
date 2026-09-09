"""THE DEFECT: a gate's `git diff --cached` handed a GIT_DIR-less env reads an EMPTY index from a
linked worktree, finds nothing to object to, and PASSES having examined nothing.

Not hypothetical arithmetic. Measured 2026-09-09 on a main-plus-linked pair in `/tmp`, hook fired
from the worktree: with the inherited environment `git diff --cached --name-only` executed with
`cwd=<MAIN tree>` returned `SECOND_WORKTREE_FILE.txt`; with `GIT_DIR`/`GIT_INDEX_FILE` scrubbed the
SAME command returned nothing. `core.hooksPath` here is an absolute path into the main tree, so
every hook-chain gate is in exactly that position on every commit made from a worktree — and this
repository already carries two functions built to strip `GIT_*` (`site_lane_gate._gitless_env`,
`pre_commit_test_gate._gitless_env`). Both are aimed at `pytest` today. The distance to the defect
is one argument.

WHY THE POISON ROUND COMES FIRST. "The check passed" has two causes — the property holds, or the
census went blind and had nothing to judge. `test_the_refusal_can_fire` establishes reach BEFORE
`test_the_tree_is_clean_today` is allowed to mean anything, because a green from an empty row set
is exactly the fail-open this module exists to catch.
"""
from __future__ import annotations

from tools.git_subject_census import census, census_source, violations

# A gate that scrubs the environment and then asks git about the commit it is gating.
POISONED = '''
import subprocess
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent

def staged():
    return subprocess.run(["git", "diff", "--cached", "--name-only"],
                          cwd=str(ROOT), env={"PATH": "/usr/bin"},
                          capture_output=True, text=True).stdout
'''

# The same gate, inheriting the environment — which is what every real gate does.
CLEAN = POISONED.replace('env={"PATH": "/usr/bin"},', "")

# A pytest child handed a gitless env: CORRECT, and the reason the refusal is not simply
# "no scrubbed env near a gate". If this ever fails the control has become a blanket ban.
LEGITIMATE = '''
import os, subprocess, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent

def run_tests():
    gitless = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    return subprocess.run([sys.executable, "-m", "pytest"], cwd=str(ROOT), env=gitless)
'''


# The scrubbed env BOUND TO A LOCAL NAME first. This is the shape that makes "a bare name is
# acceptable" a fail-open, and it is one character from `write_time_gate`'s legitimate one.
POISONED_VIA_NAME = '''
import os, subprocess
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent

def staged():
    gitless = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    return subprocess.run(["git", "diff", "--cached", "--name-only"],
                          cwd=str(ROOT), env=gitless,
                          capture_output=True, text=True).stdout
'''

# `write_time_gate`'s real shape: environ-derived, passed by name. Must NOT be refused.
LEGITIMATE_VIA_NAME = '''
import os, subprocess
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent

def staged():
    env = {k: v for k, v in os.environ.items() if k != "GIT_PREFIX"}
    return subprocess.run(["git", "diff", "--cached", "--name-only"],
                          cwd=str(ROOT), env=env,
                          capture_output=True, text=True).stdout
'''


def test_a_scrubbed_env_passed_by_NAME_is_still_refused():
    """The fail-open the name-resolution was one edit from introducing.

    `env=gitless` and `env=env` are both bare names; only one is safe. A control that accepted
    bare names to clear the `write_time_gate` false positive would pass this file silently.
    """
    assert violations(census_source(POISONED_VIA_NAME, "poisoned_name.py")), \
        "a GIT_-stripping env passed by name was accepted -- the narrowing is a fail-open"


def test_an_environ_derived_env_passed_by_NAME_is_accepted():
    """`write_time_gate.staged_additions`, which the first draft of this control refused."""
    assert not violations(census_source(LEGITIMATE_VIA_NAME, "legit_name.py"))


def test_an_unresolvable_env_name_is_refused():
    """'I could not tell' must not read as 'it is fine'."""
    mystery = LEGITIMATE_VIA_NAME.replace(
        '    env = {k: v for k, v in os.environ.items() if k != "GIT_PREFIX"}\n', "")
    assert violations(census_source(mystery, "mystery.py"))


def test_the_refusal_can_fire():
    """POISON ROUND. Without this a pass below could mean the census parsed nothing."""
    rows = census_source(POISONED, "poisoned.py")
    assert rows, "census found no git callsite at all -- it is blind, not clean"
    assert violations(rows), "the scrubbed-env git call was not refused -- the control cannot fail"


def test_inheriting_the_environment_is_accepted():
    """The control must not fire on the shape every real gate uses, or it is a blanket ban."""
    rows = census_source(CLEAN, "clean.py")
    assert rows, "census lost the callsite when `env=` was removed"
    assert not violations(rows)


def test_a_gitless_env_on_a_NON_git_child_is_not_refused():
    """`_gitless_env` around pytest is the fix for a REAL index corruption. Keep it legal."""
    assert not violations(census_source(LEGITIMATE, "legit.py"))


def test_a_call_that_names_its_subject_is_immune_even_when_scrubbed():
    """`delivery_lane`'s shape: an explicit commit answers identically from every worktree."""
    named = POISONED.replace('"--cached", "--name-only"', '"--name-only", "origin/main", commit')
    assert not violations(census_source(named, "named.py"))


def test_the_tree_is_clean_today():
    """Only meaningful because the poison round above proved the refusal reaches."""
    rows = census()
    assert rows, "census over the real tree returned nothing -- blind, not clean"
    assert [c for c in rows if c.reads_local_state], "no local-state reader found -- blind"
    bad = violations(rows)
    assert not bad, "a git call gating a commit was handed a GIT_DIR-less env: " + "; ".join(
        f"{c.module}:{c.lineno} env={c.env}" for c in bad)
