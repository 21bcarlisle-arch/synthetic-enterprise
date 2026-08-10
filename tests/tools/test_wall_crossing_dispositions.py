"""R15 proof for `tools/wall_crossing_dispositions.py` — every guard fires ALONE.

WHY THIS SUITE IS SHAPED THIS WAY
----------------------------------
The register it guards is the mechanism behind KNIFE pass 3's first exit clause
("no edge survives unexamined"). A register control that cannot fail is worse
than no register: it would let a future pass cut the easy twenty, close, and
leave sixty-eight edges unlooked-at behind a green tick.

So every guard below is mutation-proven against a SYNTHETIC register and a
SYNTHETIC crossing set, never against the live tree. That is deliberate and it
is the repair pass 3's own first step had to make to the KNIFE ledger's mutation
proofs: two of those pinned whichever real overlap the tree happened to carry,
and both died the moment pass 2 drove the overlap to zero. A control whose
fixture needs a LIVE instance of the defect dies exactly when the codebase
reaches its goal state — and for this register the goal state (every edge cut,
nothing owed) is precisely the state in which a live-fixture proof would go
vacuous.

Every mutation test therefore asserts BOTH directions: the defect produces its
own named finding, AND the same fixture without the defect produces none. A
guard that fires on everything is as uninformative as one that fires on nothing.
"""
from __future__ import annotations

from pathlib import Path

import pytest

from tools import wall_crossing_dispositions as wcd

REPO_ROOT = Path(__file__).resolve().parents[2]


# ---------------------------------------------------------------------------
# Synthetic fixtures. The clean register is the CONTROL: every mutation below
# is this document with exactly one thing wrong.
# ---------------------------------------------------------------------------

CLEAN_DESIGN = """<!-- WALL-CROSSING-DESIGN D_move_the_thing
Move the offending module to the side of the wall it belongs on, because it is
world physics filed on the company side and has no company-side importer.
WALL-CROSSING-DESIGN -->"""

CLEAN_EDGES = """<!-- WALL-CROSSING-EDGES
# a comment line is ignored
edge: simulation.a -> company.b | disposition=owed | design=D_move_the_thing
edge: simulation.c -> saas.d | disposition=grandfathered | reason=the world legitimately observes this published figure
edge: simulation.e -> company.f | disposition=cut | reason=the composition moved above both layers in pass 1
WALL-CROSSING-EDGES -->"""

CLEAN_DOC = f"# register\n\n{CLEAN_DESIGN}\n\n{CLEAN_EDGES}\n"

# `simulation.e -> company.f` is deliberately ABSENT: it is the `cut` row.
LIVE = {("simulation.a", "company.b"), ("simulation.c", "saas.d")}


def run(doc: str = CLEAN_DOC, live=None):
    rows, designs = wcd.parse_register(doc)
    return wcd.reconcile(rows, designs, LIVE if live is None else live)[0]


def partition_gap(rows, report) -> int:
    """Rows MINUS (live crossings + cut rows). Zero iff the register is complete.

    The population invariant behind the live-register test, extracted so it can
    be mutation-proven on fixtures instead of asserted only against the real
    tree — where it can be exercised in exactly one state (today's) and cannot
    be made to fail on purpose.
    """
    cut = sum(1 for r in rows if r.disposition == "cut")
    return report["rows"] - (report["measured_crossings"] + cut)


def only(findings, needle: str):
    """Exactly one finding, and it is the named one."""
    assert len(findings) == 1, f"expected exactly one finding, got {findings}"
    assert needle in findings[0], f"{needle!r} not in {findings[0]!r}"


# ---------------------------------------------------------------------------
# The control: no defect, no findings. Without this every test below is vacuous.
# ---------------------------------------------------------------------------

def test_the_clean_register_produces_no_findings():
    assert run() == []


def test_the_clean_register_exercises_all_three_dispositions():
    """The control must actually reach each branch, or its silence proves nothing.

    The live register happens to carry zero `cut` and zero `grandfathered` rows
    (stated in the register's own section 2c). If the fixture did not exercise
    those branches either, their guards would be proven only in the negative.
    """
    rows, _ = wcd.parse_register(CLEAN_DOC)
    assert {r.disposition for r in rows} == wcd.DISPOSITIONS


# ---------------------------------------------------------------------------
# GUARD 1 — the unexamined edge. This is the clause the whole register serves.
# ---------------------------------------------------------------------------

def test_a_live_crossing_with_no_row_is_a_finding():
    findings = run(live=LIVE | {("simulation.ghost", "company.unruled")})
    only(findings, "LIVE CROSSING WITH NO DISPOSITION")


def test_the_unexamined_guard_is_silent_when_every_edge_is_ruled():
    assert run(live=LIVE) == []


# ---------------------------------------------------------------------------
# GUARD 2 — a `cut` claim is verified against the walker, never against itself.
# ---------------------------------------------------------------------------

def test_cut_claimed_while_the_import_is_still_live_is_a_finding():
    findings = run(live=LIVE | {("simulation.e", "company.f")})
    only(findings, "ruled `cut` but the import IS STILL IN THE TREE")


def test_cut_with_a_decorative_reason_is_a_finding():
    doc = CLEAN_DOC.replace(
        "disposition=cut | reason=the composition moved above both layers in pass 1",
        "disposition=cut | reason=TBD",
    )
    only(run(doc), "`cut` carries no substantive reason")


# ---------------------------------------------------------------------------
# GUARD 3 — grandfathering. Both the corpse case and the empty-reason case.
# ---------------------------------------------------------------------------

def test_grandfathering_an_edge_that_is_not_live_is_a_finding():
    findings = run(live={("simulation.a", "company.b")})
    only(findings, "grandfathered but the edge is NOT LIVE")


def test_grandfathered_with_a_decorative_reason_is_a_finding():
    doc = CLEAN_DOC.replace(
        "reason=the world legitimately observes this published figure", "reason=see above"
    )
    only(run(doc), "grandfathered with no named reason")


def test_grandfathered_with_a_too_short_reason_is_a_finding():
    doc = CLEAN_DOC.replace(
        "reason=the world legitimately observes this published figure", "reason=it is fine"
    )
    only(run(doc), "grandfathered with no named reason")


def test_grandfathered_carrying_a_cut_design_is_a_finding():
    doc = CLEAN_DOC.replace(
        "disposition=grandfathered | reason=the world legitimately observes this published figure",
        "disposition=grandfathered | design=D_move_the_thing "
        "| reason=the world legitimately observes this published figure",
    )
    only(run(doc), "grandfathered rows carry a reason, not a `design=`")


# ---------------------------------------------------------------------------
# GUARD 4 — `owed` is the class that carries the weight, so it is the class
# with the most ways to go decorative.
# ---------------------------------------------------------------------------

def test_owed_against_an_edge_that_is_not_live_is_a_finding():
    findings = run(live={("simulation.c", "saas.d")})
    only(findings, "ruled `owed` but the edge is NOT LIVE")


@pytest.mark.parametrize("placeholder", ["TBD", "later", "n/a", "", "see below", "?"])
def test_owed_naming_a_decorative_design_is_a_finding(placeholder):
    """Not `only`: emptying the reference legitimately orphans the design too.

    That second finding is the symmetric guard doing its job on a knock-on
    effect of the same mutation, not a second defect — so this asserts the named
    finding is PRESENT, and the test below asserts it is not merely the orphan
    guard firing for both.
    """
    doc = CLEAN_DOC.replace("design=D_move_the_thing\n", f"design={placeholder}\n")
    findings = run(doc)
    assert any("`owed` names no cut design" in f for f in findings), findings


def test_the_decorative_design_guard_is_not_the_orphan_guard_in_disguise():
    """A decorative reference must fire the `owed` guard even with no orphan.

    Add a second row that keeps the design block referenced. If the only finding
    were the orphan one, this fixture would come back clean and the parametrized
    test above would have been proving the wrong guard.
    """
    doc = CLEAN_DOC.replace(
        "edge: simulation.a -> company.b | disposition=owed | design=D_move_the_thing\n",
        "edge: simulation.a -> company.b | disposition=owed | design=TBD\n"
        "edge: simulation.g -> company.h | disposition=owed | design=D_move_the_thing\n",
    )
    findings = run(doc, live=LIVE | {("simulation.g", "company.h")})
    only(findings, "`owed` names no cut design")


def test_owed_naming_a_design_that_does_not_exist_is_a_finding():
    doc = CLEAN_DOC.replace(
        "| design=D_move_the_thing\n", "| design=D_a_plan_nobody_wrote\n"
    )
    findings = run(doc)
    assert any("is not a design block in this register" in f for f in findings)
    assert any("referenced by no edge row" in f for f in findings)


# ---------------------------------------------------------------------------
# GUARD 5 — the symmetric guard: a design nobody uses, and an empty design.
# ---------------------------------------------------------------------------

def test_a_design_block_no_row_references_is_a_finding():
    orphan = (
        "<!-- WALL-CROSSING-DESIGN D_orphan\n"
        "A perfectly well written plan that no edge in this register points at.\n"
        "WALL-CROSSING-DESIGN -->"
    )
    only(run(CLEAN_DOC + "\n" + orphan), "referenced by no edge row")


def test_a_design_block_with_no_substantive_body_is_a_finding():
    doc = CLEAN_DOC.replace(
        "Move the offending module to the side of the wall it belongs on, because it is\n"
        "world physics filed on the company side and has no company-side importer.",
        "soon",
    )
    only(run(doc), "has no substantive body")


def test_duplicate_design_names_are_a_finding():
    only(run(CLEAN_DOC + "\n" + CLEAN_DESIGN), "duplicate design block name")


# ---------------------------------------------------------------------------
# GUARD 6 — one edge, one ruling; and unknown dispositions.
# ---------------------------------------------------------------------------

def test_two_rulings_for_one_edge_is_a_finding():
    doc = CLEAN_DOC.replace(
        "edge: simulation.a -> company.b | disposition=owed | design=D_move_the_thing\n",
        "edge: simulation.a -> company.b | disposition=owed | design=D_move_the_thing\n"
        "edge: simulation.a -> company.b | disposition=owed | design=D_move_the_thing\n",
    )
    only(run(doc), "duplicate ruling for simulation.a -> company.b")


def test_an_unknown_disposition_is_a_finding():
    doc = CLEAN_DOC.replace("disposition=owed", "disposition=probably_fine", 1)
    findings = run(doc)
    assert any("unknown disposition 'probably_fine'" in f for f in findings)


def test_an_unknown_disposition_does_not_silently_satisfy_the_edge():
    """The dangerous shape: a typo'd disposition passing as 'examined'."""
    doc = CLEAN_DOC.replace("disposition=owed", "disposition=examined", 1)
    assert run(doc), "a nonsense disposition must never count as a ruling"


# ---------------------------------------------------------------------------
# GUARD 7 — the vacuity shapes. An empty register and an empty tree are ERRORS,
# not agreement. These are the fail-open patterns R15 names.
# ---------------------------------------------------------------------------

def test_zero_rows_parsed_is_a_finding_not_a_pass():
    findings, _ = wcd.reconcile([], [], LIVE)
    assert any("parsed ZERO edge rows" in f for f in findings)


def test_zero_rows_and_zero_crossings_is_still_a_finding():
    """The purest fail-open: nothing measured, nothing ruled, everything 'agrees'."""
    findings, _ = wcd.reconcile([], [], set())
    assert findings, "an empty register agreeing with an empty tree must not pass"


def test_a_walker_measuring_zero_crossings_raises(monkeypatch):
    monkeypatch.setattr(wcd, "live_crossings", lambda: {})
    with pytest.raises(wcd.MeasurementError, match="ZERO crossings"):
        wcd.measure_crossings()


def test_a_walker_that_cannot_run_raises_rather_than_skipping(monkeypatch):
    def boom():
        raise ImportError("no walker here")

    monkeypatch.setattr(wcd, "live_crossings", boom)
    with pytest.raises(wcd.MeasurementError, match="could not run"):
        wcd.measure_crossings()


# ---------------------------------------------------------------------------
# GUARD 8 — bounded parsing. A malformed register is an ERROR, never a register
# with fewer rows in it.
# ---------------------------------------------------------------------------

def test_an_unterminated_edge_block_raises():
    with pytest.raises(wcd.RegisterError, match="never terminated"):
        wcd.parse_register(CLEAN_DOC.replace(wcd.EDGE_CLOSE, ""))


def test_an_unterminated_design_block_raises():
    with pytest.raises(wcd.RegisterError, match="never terminated"):
        wcd.parse_register(CLEAN_DOC.replace(wcd.DESIGN_CLOSE, "", 1))


def test_an_unnamed_design_block_raises():
    with pytest.raises(wcd.RegisterError, match="has no name"):
        wcd.parse_register(
            "<!-- WALL-CROSSING-DESIGN\nbody\nWALL-CROSSING-DESIGN -->\n"
        )


def test_an_unknown_field_key_raises_rather_than_being_ignored():
    doc = CLEAN_DOC.replace("| design=D_move_the_thing", "| desgin=D_move_the_thing")
    with pytest.raises(wcd.RegisterError, match="unknown field"):
        wcd.parse_register(doc)


def test_a_row_with_no_disposition_raises():
    doc = CLEAN_DOC.replace("disposition=owed | ", "")
    with pytest.raises(wcd.RegisterError, match="no `disposition=`"):
        wcd.parse_register(doc)


def test_a_duplicate_field_raises():
    doc = CLEAN_DOC.replace(
        "| design=D_move_the_thing", "| design=D_move_the_thing | design=D_move_the_thing"
    )
    with pytest.raises(wcd.RegisterError, match="duplicate field"):
        wcd.parse_register(doc)


def test_a_field_that_is_not_key_value_raises():
    doc = CLEAN_DOC.replace("| design=D_move_the_thing", "| D_move_the_thing")
    with pytest.raises(wcd.RegisterError, match="not `key=value`"):
        wcd.parse_register(doc)


def test_a_malformed_edge_line_raises():
    doc = CLEAN_DOC.replace("edge: simulation.a -> company.b |", "edge: simulation.a |")
    with pytest.raises(wcd.RegisterError, match="not a valid edge row"):
        wcd.parse_register(doc)


def test_a_missing_register_file_raises(tmp_path):
    with pytest.raises(wcd.RegisterError, match="missing"):
        wcd.load_register(tmp_path / "nope.md")


def test_text_outside_the_blocks_is_not_parsed_as_rows():
    """A block terminator must actually bound the block."""
    doc = CLEAN_DOC + "\nedge: simulation.loose -> company.loose | disposition=cut\n"
    rows, _ = wcd.parse_register(doc)
    assert ("simulation.loose", "company.loose") not in {r.key for r in rows}


# ---------------------------------------------------------------------------
# ANTI-TAUTOLOGY — the rulings and the measurement must come from different
# places. This is the independence R15 asks for, asserted rather than promised.
# ---------------------------------------------------------------------------

def test_no_measured_location_is_carried_in_the_register():
    """A file:line column would be a measured value copied into the document.

    That is the same-source defect: the register would then 'agree' with the
    tree because it was written from it, and it would rot silently besides.
    """
    assert "at=" not in wcd.REGISTER_DOC.read_text(encoding="utf-8")
    assert set(wcd.EdgeRow.__dataclass_fields__) == {
        "src", "dst", "disposition", "design", "reason", "lineno"
    }


def test_reconcile_cannot_reach_the_tree():
    """`reconcile` takes the measurement as a PARAMETER — it cannot go and look.

    A synthetic crossing set that contradicts the real tree must be honoured in
    full, or the guards below could be quietly reading the live walker instead
    of the fixture, and every mutation proof here would be measuring nothing.
    """
    findings, report = wcd.reconcile([], [], {("not.a", "real.edge")})
    assert report["measured_crossings"] == 1
    assert any("not.a -> real.edge" in f for f in findings)


def test_the_report_names_both_sources_separately():
    _, report = wcd.reconcile(*wcd.parse_register(CLEAN_DOC), LIVE)
    assert report["ruled_source"].endswith("WALL_CROSSING_DISPOSITION_REGISTER.md")
    assert report["measured_source"] == "tools.epistemic_wall.live_crossings"


# ---------------------------------------------------------------------------
# THE LIVE REGISTER — the one place the real tree is used, and only to assert
# the mechanism is actually wired to it.
# ---------------------------------------------------------------------------

def test_the_live_register_examines_every_live_crossing():
    rows, designs = wcd.load_register()
    measured = wcd.measure_crossings()
    findings, report = wcd.reconcile(rows, designs, measured)
    assert findings == [], f"the live register has unexamined edges: {findings}"

    # REPAIRED 2026-08-09, at the STATISTIC rather than the threshold. This used
    # to read `report["rows"] == report["measured_crossings"]`, which holds only
    # while ZERO edges have been cut — a control that dies exactly when the
    # codebase reaches its goal state, the same defect this pass already repaired
    # in the KNIFE ledger's own mutation fixtures. The first seven cuts reddened
    # it (88 rows vs 81 live) for doing precisely what it exists to encourage.
    #
    # The invariant that actually holds, and holds forever: a cut row is KEPT
    # (deleting it is how a re-entry becomes invisible), so rows partition into
    # exactly the live edges plus the cut ones. `reconcile` has already proven
    # each `cut` row absent from the tree and each live edge present, so this is
    # a population check on top of that, not a second opinion about the same
    # thing.
    assert partition_gap(rows, report) == 0, (
        f"{report['rows']} rows != {report['measured_crossings']} live + "
        f"{sum(1 for r in rows if r.disposition == 'cut')} cut — a row was "
        "deleted rather than ruled `cut`, which is how a re-entry becomes "
        "invisible"
    )


def test_the_partition_invariant_holds_on_the_clean_fixture():
    """Vacuity guard: the invariant must PASS on a register with a cut in it.

    The clean fixture is 3 rows = 2 live + 1 cut, i.e. the exact shape that broke
    the old `rows == measured` assertion. If this ever needed the cut count to be
    zero, the mutation proof below would be measuring nothing.
    """
    rows, designs = wcd.parse_register(CLEAN_DOC)
    _, report = wcd.reconcile(rows, designs, LIVE)
    assert sum(1 for r in rows if r.disposition == "cut") == 1
    assert partition_gap(rows, report) == 0


def test_the_partition_invariant_reds_when_a_live_row_is_deleted():
    """R15 mutation: delete a LIVE edge's row instead of ruling it.

    This is the failure the invariant exists to catch and the one `reconcile`
    alone would only half-catch — it reports the unruled edge, but nothing would
    notice that the register's own population had silently shrunk.
    """
    mutated = CLEAN_DOC.replace(
        "edge: simulation.a -> company.b | disposition=owed | design=D_move_the_thing\n",
        "",
    )
    assert mutated != CLEAN_DOC, "the mutation did not apply"
    rows, designs = wcd.parse_register(mutated)
    _, report = wcd.reconcile(rows, designs, LIVE)
    assert partition_gap(rows, report) == -1


def test_the_live_register_is_not_vacuous():
    """It must actually contain the population it claims to examine."""
    rows, designs = wcd.load_register()
    assert len(rows) > 50, "the register is suspiciously small for this pass"
    assert len(designs) >= 2, "one catch-all design would make `design=` decorative"
    assert all(r.disposition in wcd.DISPOSITIONS for r in rows)


def test_main_returns_nonzero_when_an_edge_is_unexamined(monkeypatch, capsys):
    real = wcd.measure_crossings

    def with_a_ghost(at_head: bool = False):
        return real(at_head=at_head) | {("simulation.ghost", "company.unruled")}

    monkeypatch.setattr(wcd, "measure_crossings", with_a_ghost)
    assert wcd.main([]) == 2
    assert "NO DISPOSITION" in capsys.readouterr().out


def test_main_returns_zero_on_the_live_tree(capsys):
    assert wcd.main([]) == 0
    assert "every live crossing is examined" in capsys.readouterr().out
