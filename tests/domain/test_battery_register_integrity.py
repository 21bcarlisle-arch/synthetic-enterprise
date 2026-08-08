"""AO8 -- the control over the battery register, and the proof it can fail.

The register's whole claim is "no purchased battery line was dropped, and
nothing is marked done that is not running." That claim is only worth anything
if a violation makes the suite red. Every rule in `validate()` therefore has a
MUTATION TEST below that poisons a register in memory with that rule's OWN named
defect and asserts the rule fires (R15).

The killer patterns this file is written against:

  TAUTOLOGY   -- the oracle parses the BRIEFS; the register is a separate file.
                 If both came from the same place, agreement would prove nothing.
  FAIL-OPEN   -- an empty oracle, an empty brief, or zero mechanised lines would
                 make completeness pass over nothing. Each is an explicit
                 VACUOUS check, and each has its own mutation below.
  FAIL-SILENT -- a `check` naming a deleted test would keep reading as covered.
                 resolve_check imports it, so the name must really be there.
"""
from __future__ import annotations

import dataclasses
import re
from pathlib import Path

import pytest

from tests.domain import battery_register as br

REGISTER = br.load_register()
BRIEFS = br.registered_briefs()
ORACLE = br.build_oracle(BRIEFS)


# ---------------------------------------------------------------------------
# The live control
# ---------------------------------------------------------------------------


def test_the_register_is_faithful_to_the_briefs() -> None:
    """THE control: every purchased battery line is present and dispositioned."""
    problems = br.validate(REGISTER, ORACLE)
    assert not problems, "battery register integrity:\n  - " + "\n  - ".join(problems)


def test_every_brief_is_registered() -> None:
    """A brief added to the tree but not to the register is invisible coverage.

    Completeness is measured per registered brief, so an UNREGISTERED brief
    would never be measured at all -- the register would look complete while
    silently ignoring a whole battery. This closes that hole by discovering
    briefs from the filesystem instead of from the register.
    """
    found = {
        p.name
        for root in br.BRIEF_SEARCH_ROOTS
        if root.is_dir()
        for p in root.glob("ADVISOR_SCOPE_BRIEF_*.md")
    }
    unregistered = found - set(BRIEFS)
    assert not unregistered, (
        f"scope briefs present but absent from the register: {sorted(unregistered)}. "
        "Run tools/build_battery_register.py after adding the brief to its BRIEFS map."
    )


def test_the_oracle_is_not_vacuous() -> None:
    """Guard the guard: the oracle must really be reading the briefs."""
    assert len(BRIEFS) >= 8, f"only {len(BRIEFS)} briefs registered"
    total = sum(len(v) for v in ORACLE.values())
    assert total >= 70, f"oracle parsed only {total} battery lines across {len(BRIEFS)} briefs"
    assert len(REGISTER) == total, (
        f"register holds {len(REGISTER)} entries but the briefs carry {total} lines"
    )


def test_no_battery_check_can_skip_itself() -> None:
    """The atom's own named failure mode: a check that skips when data is absent.

    "A battery line converted into a check that silently skips when its data is
    absent is worse than leaving it as prose, because it reads as covered."
    A skipped test is green. So the battery checks may not carry skip markers.
    """
    source = (Path(__file__).parent / "test_battery_checks.py").read_text(encoding="utf-8")
    banned = re.findall(r"(pytest\.skip|skipif|pytest\.mark\.skip|pytest\.xfail)", source)
    assert not banned, (
        f"tests/domain/test_battery_checks.py uses {sorted(set(banned))}. A battery "
        "check must FAIL when its data is missing, never skip -- a skip reads as covered."
    )


def test_mechanised_checks_are_all_in_the_battery_module() -> None:
    """Both directions of the register<->test pairing.

    Forward (register names a real test) is covered by validate(). This is the
    REVERSE: a test living in the battery module that no register line claims
    is either an unregistered conversion or a stray, and both mean the counts
    in the delta report are wrong.
    """
    import tests.domain.test_battery_checks as checks

    claimed = {
        e.check.split("::", 1)[1]
        for e in REGISTER
        if e.disposition == "mechanised" and e.check
    }
    defined = {
        name
        for name in dir(checks)
        if name.startswith("test_") and callable(getattr(checks, name))
    }
    # Coverage/vacuity helpers are deliberately not register lines; they guard
    # the guards. They are named `..._scan_reaches...` / `..._is_not_vacuous`.
    guards = {n for n in defined if "reaches" in n or "vacuous" in n}
    unclaimed = defined - claimed - guards
    assert not unclaimed, (
        f"tests in the battery module claimed by no register line: {sorted(unclaimed)}"
    )
    missing = claimed - defined
    assert not missing, f"register names tests that do not exist: {sorted(missing)}"


def test_the_reported_status_is_not_stale() -> None:
    """The delta must be REPORTED, and a stale report is not a report.

    BATTERY_CONVERSION.md's counts are generated. Without this, the doc would
    keep quoting "3 of 76" long after the register moved, and a stale number
    quoted as evidence is the failure this project has hit before.
    """
    import tools.build_battery_register as builder

    lines = [
        (f"{br._slug_for(brief)}-{line.label}", brief, line)
        for brief in builder.BRIEFS.values()
        for line in br.parse_battery_lines(brief)
    ]
    expected = builder.render_status(lines)
    doc = (br.ROOT / "docs" / "design" / "BATTERY_CONVERSION.md").read_text(encoding="utf-8")
    assert builder.BEGIN in doc and builder.END in doc, "status markers missing from the doc"
    actual = doc.split(builder.BEGIN, 1)[1].split(builder.END, 1)[0].strip()
    assert actual == expected.strip(), (
        "BATTERY_CONVERSION.md's status block is stale -- "
        "re-run tools/build_battery_register.py"
    )


# ---------------------------------------------------------------------------
# R15 mutation proofs -- each rule fires on its OWN named defect
# ---------------------------------------------------------------------------


def _fresh() -> list[br.RegisterEntry]:
    return list(REGISTER)


def test_mutation_a_dropped_line_is_caught() -> None:
    poisoned = [e for e in _fresh() if e.id != "GAS-8"]
    problems = br.validate(poisoned, ORACLE)
    assert any(p.startswith("DROPPED: GAS-8") for p in problems), problems


def test_mutation_a_reworded_line_is_caught() -> None:
    poisoned = _fresh()
    idx = next(i for i, e in enumerate(poisoned) if e.id == "ELEC-4")
    poisoned[idx] = dataclasses.replace(poisoned[idx], text="Negative prices are fine actually.")
    problems = br.validate(poisoned, ORACLE)
    assert any(p.startswith("DRIFTED: ELEC-4") for p in problems), problems


def test_mutation_a_phantom_line_is_caught() -> None:
    poisoned = _fresh()
    poisoned.append(
        br.RegisterEntry(
            id="GAS-99",
            brief="ADVISOR_SCOPE_BRIEF_GAS_2026-08-04.md",
            label="99",
            text="A line the advisor never wrote.",
            disposition="pending_capability",
            reason="invented out of thin air by a builder",
        )
    )
    problems = br.validate(poisoned, ORACLE)
    assert any(p.startswith("PHANTOM: GAS-99") for p in problems), problems


def test_mutation_mechanised_pointing_at_a_dead_test_is_caught() -> None:
    """FAIL-SILENT killer: the named check no longer exists."""
    poisoned = _fresh()
    idx = next(i for i, e in enumerate(poisoned) if e.id == "GAS-8")
    poisoned[idx] = dataclasses.replace(
        poisoned[idx], check="tests.domain.test_battery_checks::test_deleted_long_ago"
    )
    problems = br.validate(poisoned, ORACLE)
    assert any(p.startswith("UNBACKED: GAS-8") for p in problems), problems


def test_mutation_mechanised_pointing_at_a_dead_module_is_caught() -> None:
    poisoned = _fresh()
    idx = next(i for i, e in enumerate(poisoned) if e.id == "ELEC-4")
    poisoned[idx] = dataclasses.replace(poisoned[idx], check="tests.domain.no_such_module::test_x")
    problems = br.validate(poisoned, ORACLE)
    assert any(p.startswith("UNBACKED: ELEC-4") for p in problems), problems


def test_mutation_a_gap_without_a_blocker_is_caught() -> None:
    poisoned = _fresh()
    idx = next(i for i, e in enumerate(poisoned) if e.disposition == "pending_capability")
    poisoned[idx] = dataclasses.replace(poisoned[idx], reason="")
    problems = br.validate(poisoned, ORACLE)
    assert any("requires a reason" in p for p in problems), problems


def test_mutation_a_thin_blocker_is_caught() -> None:
    poisoned = _fresh()
    idx = next(i for i, e in enumerate(poisoned) if e.disposition == "pending_capability")
    poisoned[idx] = dataclasses.replace(poisoned[idx], reason="not done")
    problems = br.validate(poisoned, ORACLE)
    assert any("too thin" in p for p in problems), problems


def test_mutation_an_empty_oracle_is_caught_not_passed() -> None:
    """FAIL-OPEN killer, and the most important mutation in this file.

    If the briefs went missing, every completeness rule would iterate an empty
    dict and report nothing wrong. That is the state where the control reads
    green precisely because it has lost its evidence.
    """
    problems = br.validate(_fresh(), {})
    assert any(p.startswith("VACUOUS") for p in problems), problems


def test_mutation_one_empty_brief_is_caught_not_passed() -> None:
    poisoned_oracle = dict(ORACLE)
    poisoned_oracle["ADVISOR_SCOPE_BRIEF_GAS_2026-08-04.md"] = []
    problems = br.validate(_fresh(), poisoned_oracle)
    assert any("VACUOUS" in p and "GAS" in p for p in problems), problems


def test_mutation_a_register_with_nothing_mechanised_is_caught() -> None:
    """Prose with extra steps must not read as conversion."""
    poisoned = [
        dataclasses.replace(e, disposition="pending_capability", check=None,
                            reason="downgraded by the mutation to prove the floor fires")
        if e.disposition == "mechanised" else e
        for e in _fresh()
    ]
    problems = br.validate(poisoned, ORACLE)
    assert any("no battery line is mechanised" in p for p in problems), problems


def test_mutation_a_missing_brief_raises_rather_than_returning_empty() -> None:
    """Fail-closed resolution: a cited brief that is gone is an error, not [].

    Returning an empty battery here would feed the vacuity path; raising keeps
    a broken citation loud.
    """
    with pytest.raises(FileNotFoundError):
        br.parse_battery_lines("ADVISOR_SCOPE_BRIEF_DOES_NOT_EXIST.md")


def test_mutation_the_brief_parser_bounds_its_section() -> None:
    """The unbounded-parser class: a battery section must stop at the trailer.

    An unterminated scan swallows the Sources paragraph and the attribution
    line, inventing phantom battery lines that read as extra coverage.
    """
    lines = br.parse_battery_lines("ADVISOR_SCOPE_BRIEF_GAS_2026-08-04.md")
    assert len(lines) == 12, f"expected 12 gas battery lines, parsed {len(lines)}"
    joined = " ".join(line.text for line in lines)
    assert "Sources:" not in joined, "parser ran past the battery into the sources trailer"
    assert "Advisor scope brief" not in joined, "parser ran past the battery into the attribution"
