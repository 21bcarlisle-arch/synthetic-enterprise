"""The gate's selection reaches the controls whose subject is the INDEX or the test corpus.

REUSE: tests/tools/test_the_gate_reaches_the_git_oracled_controls.py
CLASS: CUSTOM
INDEX: searched "gate selection", "control tests", "always run list", "surface trigger",
       "whole tree subject". `tests/tools/test_pre_commit_test_gate_censused_batch.py` grades the
       CENSUSED batch and is the closest sibling -- it is not extended, because its docstring is
       explicit that its batch IS whatever `whole_tree_subject_census` returns and it grades every
       member with that census's own predicate. The five graded here are precisely the ones that
       predicate CANNOT SEE, so folding them in would mean weakening the sibling's earning leg to
       admit them. `tests/tools/test_pre_commit_gate_store_surface.py` and
       `test_pre_commit_gate_site_surface.py` each grade ONE surface trigger and are the pattern
       this file follows for the two new triggers; neither covers a `CONTROL_TESTS` batch.
       `tests/tools/test_pre_commit_test_gate.py` covers `tests_for`/`staged_files` mechanics.

WHAT THIS GRADES. `tools/pre_commit_test_gate.py` gained, on 2026-09-22:

  * `GIT_ORACLED_AND_TEST_CORPUS_SUBJECTS` -- five always-run entries whose subject is the whole
    git index or the whole `tests/` tree;
  * `DISCHARGE_SURFACE_PREFIX` / `DISCHARGE_SURFACE_TESTS` -- a staged `docs/staging/**.md` record;
  * one `STORE_CONTRACT_TESTS` entry -- a staged `docs/design/simplifications/**.yaml` store;
  * `SUBJECT_TESTS` -- a guard whose subject is ONE module and whose filename is the aspect.

All seven controls those reach were RED AT `origin/main` simultaneously, and no commit's selection
reached any of them. The two surface triggers exist because always-run cannot catch the direction
that matters most for a RECORD: a closure claim written in a pure-docs commit. Measured before the
lines were written -- a staging record selected ZERO test files and an atom store selected three, of
which none was the control whose subject it is.

WHY THE FIRST CONTROL IS A POSITIVE ONE, and the order is deliberate, copied from the sibling for
the reason the sibling gives: a selector that returns NOTHING passes every "is X excluded"
assertion ever written, and quietly selecting the empty set is this mechanism's failure mode.

WHAT THESE ARE KEYED TO. The property, never today's answer. Nothing here asserts the batch has
five members, or that the gate selects any particular count. What is asserted is that for each
commit SHAPE that can falsify one of these controls, the gate selects that control -- and that the
fast path for a commit which can break nothing is still fast.

A CONTROL WAS CONSIDERED AND NOT WRITTEN, recorded so the next session does not write it: "no
member of this batch is reachable by filename stem". The sibling file deleted exactly that one,
because a fabricated stem matches nothing by construction (a tautology) and a real stem that later
appears would red on a non-defect. Stem-unreachability is why the batch exists; re-asserting it
here buys nothing either way.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools import pre_commit_test_gate as gate  # noqa: E402

#: Bound to the MODULE, never re-typed. A second copy of the list here would let the two disagree
#: the moment one of them changed, and the disagreement would favour whichever file was edited last
#: -- the same reason the censused-batch sibling imports rather than restates.
BATCH = gate.GIT_ORACLED_AND_TEST_CORPUS_SUBJECTS

#: A path that cannot exist, so no stem can map it to anything. This is the shape of the commit the
#: batch exists for: a NEW file in a tree some control counts as its whole population.
NEW_MODULE = "background/zz_a_daemon_that_does_not_exist_yet.py"

#: A record and a store that really are in the tree. The trigger is on the DIRECTORY and the
#: extension, so any committed member answers; these are named rather than globbed so a rename
#: shows up as a red here instead of as a silently empty probe.
A_STAGING_RECORD = (
    "docs/staging/done/WORKER_FINDING_A_GAP_ROW_IS_ATTRIBUTED_TO_ANY_WRITER_THAT_MERELY_NAMES_IT"
    "_2026-08-19.md"
)
A_STORE = (
    "docs/design/simplifications/"
    "A51_the_plain_english_report_on_the_use_case_register_reaches_the_director.yaml"
)


def test_a_brand_new_module_selects_every_member_of_the_batch():
    """THE POSITIVE LEG, first on purpose.

    DEFECT: a FAIL-OPEN in the gate itself. `select_targets` adds
    `t for t in CONTROL_TESTS if (ROOT / t).exists()`, so a member RENAMED or MOVED by other work
    leaves its line pointing at nothing and that entry is dropped IN SILENCE -- no error, no
    warning, a green gate, and a control that has stopped running for the same reason it never ran
    before. This asserts the whole batch is selected by a commit no stem can reach, which is both
    the reachability claim and the not-silently-dropped claim in one.

    MUTATION (must fire): rename any member, or delete its line.
    """
    assert BATCH, (
        "the git-oracled batch is EMPTY, so every assertion in this file is vacuous -- an empty "
        "always-run batch is the state this whole file exists to make impossible")
    selected = set(gate.select_targets([NEW_MODULE]))
    missing = [m for m in BATCH if m not in selected]
    assert not missing, (
        "a brand-new module does not select these members of the git-oracled batch, so the commit "
        "that can break them cannot run them -- which is the defect the batch was written to "
        "close:\n    " + "\n    ".join(missing))


def test_every_member_of_the_batch_is_a_file_that_exists():
    """DEFECT: the silent drop above, asserted directly rather than only through the selection.

    Kept as its own leg because the two fail in different places: the positive leg goes red if the
    gate stops consulting `CONTROL_TESTS` at all, and this one goes red if a member's path rots
    while the gate is working perfectly. A batch whose lines point at nothing selects nothing and
    reports nothing.
    """
    absent = [m for m in BATCH if not (ROOT / m).is_file()]
    assert not absent, (
        "these always-run entries name no file, so `select_targets` drops them in silence:\n    "
        + "\n    ".join(absent))


def test_a_staging_record_on_its_own_selects_the_discharge_control():
    """DEFECT: a closure claim written in a pure-docs commit, checked by nothing.

    This is the direction always-run cannot catch. `**Discharged:** <test path>::<node>` in a
    `docs/staging/` record is the register a level rests on; before this trigger, staging such a
    record selected ZERO test files, because `docs/staging/` is not under `CODE_PREFIXES` and an
    `.md` maps to no tests by stem. Both stale citations found at `origin/main` on 2026-09-22 were
    written into records exactly this way.

    MUTATION (must fire): drop `discharge_surface_changed` from either the skip decision or the
    target union in `select_targets`.
    """
    assert (ROOT / A_STAGING_RECORD).is_file(), (
        f"{A_STAGING_RECORD} is not in the tree, so this probe would test the trigger against a "
        "path the gate cannot see -- name a record that exists")
    selected = set(gate.select_targets([A_STAGING_RECORD]))
    assert selected, (
        "a staging record selects NO tests at all, so the gate still reads a committed closure "
        "claim as a pure docs commit that cannot break a control")
    missing = [t for t in gate.DISCHARGE_SURFACE_TESTS if t not in selected]
    assert not missing, (
        "a staged staging record does not select the discharge control(s):\n    "
        + "\n    ".join(missing))


def test_an_atom_store_on_its_own_selects_the_store_falsifier_control():
    """DEFECT: a store note crediting a falsifier that is in no commit, in a commit staging no `.py`.

    The store-contract list already carried three controls and this was not among them, so a store
    could claim a closure and the commit writing it would select the three that check the map
    contract and not the one that checks the claim. A51's note was the live instance.

    MUTATION (must fire): remove the entry from `STORE_CONTRACT_TESTS`.
    """
    assert (ROOT / A_STORE).is_file(), (
        f"{A_STORE} is not in the tree, so this probe would test the store trigger against a path "
        "the gate cannot see -- name a store that exists")
    selected = set(gate.select_targets([A_STORE]))
    wanted = "tests/architecture/test_no_committed_store_claims_an_unlanded_falsifier.py"
    assert wanted in selected, (
        f"a staged atom store does not select {wanted}, so a store can credit a falsifier the "
        "index does not carry and the commit that writes it is green")


def test_a_new_test_file_selects_the_ratchet_over_the_whole_test_CORPUS():
    """DEFECT: the reason `tests` is excluded from the census's `SOURCE_ROOTS` is false for a
    repo-wide ratchet.

    That exclusion reads: "a test whose subject is other tests is reached by staging those tests,
    which the stem selector does handle (a changed test file selects itself)". Self-selection runs
    the changed file's OWN assertions; it does not run a ratchet over the corpus that file just
    joined. FIVE offenders accumulated in the tree while that ratchet was red, each arriving commit
    green, which is this leg's reachability evidence on real bytes.

    MUTATION (must fire): remove the ratchet's line from the batch.
    """
    a_test = "tests/sim/test_scenario_spine_consumption.py"
    assert (ROOT / a_test).is_file(), f"{a_test} is not in the tree -- name a test that exists"
    selected = set(gate.select_targets([a_test]))
    ratchet = "tests/architecture/test_no_tree_scan_passes_on_an_empty_population.py"
    assert ratchet in selected, (
        f"staging a test file does not select {ratchet}, so a test joining the corpus cannot run "
        "the ratchet over the corpus")


def test_the_module_subject_guard_is_selected_by_its_SUBJECT_and_not_by_a_stem():
    """DEFECT: a guard whose whole subject is one module's prose, unreachable from that module.

    `tests_for` maps a module to `test_<stem>.py` and `test_<stem>_*.py`. A guard named for the
    ASPECT with no stem prefix is mapped to nothing, and this one -- 43s, the most expensive file in
    the selection -- must not be paid on every code commit to fix that. `SUBJECT_TESTS` declares the
    relationship instead.

    KEYED TO THE DECLARATION, not to today's filenames: every key must select every one of its
    values. That stays true through a rename of either side and reds if the map rots.

    MUTATION (must fire): empty `SUBJECT_TESTS`, or drop its union from `select_targets`.
    """
    assert gate.SUBJECT_TESTS, (
        "SUBJECT_TESTS is empty, so this leg is vacuous -- if the last entry was retired because "
        "its guard gained a stem route, delete this control with it rather than leaving it green "
        "over nothing")
    for module, wanted in gate.SUBJECT_TESTS.items():
        assert (ROOT / module).is_file(), (
            f"SUBJECT_TESTS keys {module}, which is not a file -- the entry can never fire")
        assert wanted, f"SUBJECT_TESTS maps {module} to nothing, which declares no relationship"
        selected = set(gate.select_targets([module]))
        missing = [t for t in wanted if t not in selected]
        assert not missing, (
            f"staging {module} does not select the guard(s) declared as taking it for a "
            "subject:\n    " + "\n    ".join(missing))


def test_a_commit_that_can_break_nothing_still_selects_nothing():
    """THE NULL CONTROL, and it is what stops every leg above being satisfied by "run everything".

    DEFECT: a new surface trigger whose predicate is too wide turns the fast path off for every
    lane. Without a null leg, `DISCHARGE_SURFACE_PREFIX = "docs/"` would pass every other test in
    this file.

    THREE PROBES, ONE PER WAY THE TRIGGER CAN BE WIDENED, and the second and third were both added
    after RUNNING the mutations rather than reasoning about them. The trigger is a CONJUNCTION of
    prefix and extension, so each clause needs a probe that isolates it:

      * `docs/reports/run_output_latest.json` -- neither clause. The general fast-path claim, and it
        catches NEITHER widening on its own, which is what the first draft of this leg got wrong.
      * `docs/status/LATEST.md` -- a `.md` OUTSIDE `docs/staging/`. Isolates the PREFIX.
      * `docs/staging/assets/*.svg` -- under the prefix, not a `.md`. Isolates the EXTENSION. Six
        non-`.md` files are tracked under `docs/staging/` (a `.gitkeep`, an SVG, a `.jsonl`, an
        extensionless instruction, a parked `.py.txt`), so the extension clause is a real narrowing
        rather than an equivalence -- established by counting them, because a mutation that does not
        fire is a missing test or an equivalence and assuming the flattering one is the whole trap.

    MUTATION (all three run): widen `DISCHARGE_SURFACE_PREFIX` to `docs/` -> probe 2 reds. Drop the
    `.endswith(".md")` clause -> probe 3 reds. Do both -> probe 1 stays green, which is why it is not
    the leg that carries this.
    """
    assert gate.select_targets(["docs/reports/run_output_latest.json"]) == [], (
        "a pure regenerated-output commit now selects tests, so a surface trigger added for a "
        "record has dropped its extension clause and taken the gate's fast path with it")
    outside = "docs/status/LATEST.md"
    assert (ROOT / outside).is_file(), (
        f"{outside} is not in the tree, so this probe cannot exercise the prefix at all -- name a "
        "`.md` that exists OUTSIDE docs/staging/, or this leg is the empty-set pass it exists to "
        "prevent")
    assert gate.select_targets([outside]) == [], (
        f"{outside} is a `.md` outside docs/staging/ and now selects tests, so the discharge "
        "trigger's PREFIX has been widened past the records it was written for")
    not_a_record = "docs/staging/assets/poesys_model_on_a_page_v4.svg"
    assert (ROOT / not_a_record).is_file(), (
        f"{not_a_record} is not in the tree, so the EXTENSION clause has no probe -- name another "
        "tracked non-`.md` under docs/staging/ (there were six) rather than deleting this leg")
    assert gate.select_targets([not_a_record]) == [], (
        f"{not_a_record} is under docs/staging/ and is not a record, yet it now selects tests -- "
        "the discharge trigger has dropped its EXTENSION clause and fires on the whole directory")


def test_this_control_is_itself_on_the_always_run_list():
    """DEFECT: the file that keeps the batch honest, selectable only by editing itself.

    Its subject is the gate's selection over every commit shape, so leaving it stem-selected would
    make it the next instance of the class it guards -- which is the sibling's argument, asserted
    here rather than trusted to a comment.
    """
    me = "tests/tools/" + Path(__file__).name
    assert me in gate.CONTROL_TESTS, (
        f"{me} is not on CONTROL_TESTS, so the only commit that runs it is one editing it -- and "
        "that is never the commit that breaks the wiring it grades")
