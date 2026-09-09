"""A coverage, ceiling or sufficiency claim says what it reduces over, or nothing can read it.

THE DEFECT THIS FILE OWNS.
`docs/staging/DIRECTOR_CANON_THE_DEMAND_VECTOR_2026-09-07.md`, WORK THIS CREATES item 3. Twice in
two days a coverage claim was measured against a single number where the thing being served is
several: demand coverage on total annual kWh (13 cases), and three weather grids of 21/21/5 that
reduce over the drivers ONE AT A TIME while the project's own measurement says the response to each
depends on the fabric.

WHY NOTHING WENT RED, WHICH IS THE WHOLE REASON THIS EXISTS. Both figures were correct arithmetic on
the quantity they named. No control over a number could have caught either, because neither number
was wrong -- what was missing sat upstream of the arithmetic, in the fact that nothing at the site
said which axes the figure varied over and therefore which it averaged away. The canon: *"It
flatters in a consistent direction -- always making the sample look smaller and the coverage look
better -- which is why it must be looked for rather than waited for."*

WHAT IT HOLDS, AND IT IS THE PROPERTY AND NOT TODAY'S ANSWER. Not "demand coverage must be measured
on five axes" and not "the weather partition must be joint" -- both go red when the code becomes
MORE honest, and both are the delivery seat's questions rather than the canon's. The property is
that a claim NAMES its subject vector, NAMES the dimensions it is measured on, and accounts for
every component as either reduced over or explicitly blind. A one-axis claim about a five-component
vector stays legal here for ever. What is refused is one that does not say so.

TWO LEGS, AND EITHER ALONE IS FAIL-OPEN:
  * the DECLARATION (`declare`) refuses a claim that cannot say what it reduces over -- but it only
    binds claims that call it;
  * the CENSUS (`claim_modules` / `unexpected_silence`) finds the claims, so a new one cannot arrive
    silent.
    A census nobody proves REACHES anything is the shape that reported ten survivals against a tree
    with no data, so `test_the_census_can_see_a_claim_that_declares_nothing` is the poison round and
    runs before any of the green ones mean anything.

R15 -- the mutations, each a real way this repair could rot:
  * accept an empty `reduces_over` -> `test_a_claim_that_names_no_reduction_dimension_is_refused`.
  * drop the exhaustiveness leg and merely check the list is non-empty ->
    `test_a_component_neither_reduced_over_nor_declared_blind_is_refused`. This is the one that
    matters: a declaration that only LISTS axes is theatre, because the author who forgot the
    half-hourly shape lists four axes and passes.
  * let `joint` default -> `test_a_multi_dimension_claim_must_say_whether_it_is_joint`, whose second
    leg is the null control: a declaration saying the same thing about a separable claim and a
    joint one declares nothing, and 21/21/5 was read as a joint statement for exactly that reason.
  * narrow the census scope back to public SYMBOL names ->
    `test_a_claim_in_class_by_its_filename_alone_is_found`. `tools/r3_carbon_score_ceiling.py`
    publishes a ceiling and no public symbol in it carries the word. A symbol-only rule is aimed at
    the concept word rather than at how it is actually spelled, which is the shape that once left 67
    constants outside a rule written for them.
  * widen the census to the claim word alone -> `test_a_claim_word_outside_the_subject_is_not_in
    _class`. `INSUFFICIENT_FUNDS` in a payments module is not a claim about the drawn population,
    and a control that fires on it is a control someone switches off.
  * point `DECLARATION` at a name nothing publishes -> every census test red at once.
  * let the outstanding-debt list absorb a new silent claim ->
    `test_the_outstanding_debt_is_shrink_only`. Without it the live leg is satisfiable by writing the
    defect down, which is the allowlist failure this repo has hit repeatedly.
  * let a debt row outlive the blocker it cites ->
    `test_every_outstanding_row_names_a_document_that_still_exists`. A row whose finding has been
    archived is an inherited amnesty, and nothing else would ever look at it again.
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest

from tools.reduction_dimension import (
    DEMAND_VECTOR,
    OUTSTANDING,
    Declaration,
    UndeclaredReduction,
    claim_modules,
    declare,
    unexpected_silence,
)

#: A well-formed declaration, used as the base every refusal test breaks ONE leg of. Breaking one
#: leg at a time is the point: a fixture that fails for two reasons proves neither.
WELL_FORMED = dict(
    kind="coverage",
    of=("annual_gas_kwh", "annual_electricity_kwh", "seasonal_gas_shape"),
    reduces_over=("annual_gas_kwh",),
    blind_to=("annual_electricity_kwh", "seasonal_gas_shape"),
    joint=True,
)


def test_the_base_fixture_is_accepted_so_every_refusal_below_names_its_own_leg():
    """The null control for the whole file. If the base were refused for some unrelated reason,
    every test after this would pass while proving nothing about the leg it names."""
    declaration = declare("a well-formed claim", **WELL_FORMED)
    assert isinstance(declaration, Declaration)
    assert declaration.reduces_over == ("annual_gas_kwh",)


def test_a_claim_that_names_no_reduction_dimension_is_refused():
    """The canon's own words: a claim that does not declare the dimension it reduces over."""
    broken = dict(WELL_FORMED, reduces_over=(), blind_to=DEMAND_VECTOR[:3])
    with pytest.raises(UndeclaredReduction) as refusal:
        declare("a claim reducing over nothing", **broken)
    assert "names no reduction dimension" in str(refusal.value)


def test_a_component_neither_reduced_over_nor_declared_blind_is_refused():
    """THE LEG THAT MAKES THIS MORE THAN A NON-EMPTY CHECK, and the defect's actual shape.

    An author who forgot the seasonal shape declares one axis and two blind components out of a
    four-component vector. Every "is the list non-empty" test passes. The partition must be
    exhaustive, and the refusal must NAME the component that fell out of it -- otherwise the author
    is told the declaration is wrong without being told which half of it.
    """
    broken = dict(WELL_FORMED, of=WELL_FORMED["of"] + ("half_hourly_electricity_shape",))
    with pytest.raises(UndeclaredReduction) as refusal:
        declare("a claim that forgot a component", **broken)
    message = str(refusal.value)
    assert "half_hourly_electricity_shape" in message
    assert "neither reduces over nor declares itself blind" in message


def test_a_placeholder_declares_nothing():
    """`tbd` passes a non-empty check and reads as an answer, which is worse than silence."""
    with pytest.raises(UndeclaredReduction) as refusal:
        declare("a claim with a placeholder", **dict(WELL_FORMED, reduces_over=("tbd",)))
    assert "placeholder" in str(refusal.value)


def test_a_dimension_the_subject_vector_does_not_have_must_say_what_it_is_made_of():
    """A total is not a component. It is components summed, and saying so is what makes the
    collapse visible -- so a derived dimension with no `derived_from` is a name nobody can connect
    to the thing being served."""
    with pytest.raises(UndeclaredReduction) as refusal:
        declare("a claim on an unexplained total",
                **dict(WELL_FORMED, reduces_over=("total_annual_kwh",), blind_to=()))
    assert "nothing says what it is made of" in str(refusal.value)

    fine = declare("a claim on an explained total",
                   **dict(WELL_FORMED, reduces_over=("total_annual_kwh",), blind_to=(),
                          derived_from={"total_annual_kwh": WELL_FORMED["of"]}))
    assert fine.collapsed == ("total_annual_kwh",)


def test_a_component_cannot_be_both_reduced_over_and_blind():
    """Two opposite statements about one component. Whichever is true, the declaration is not."""
    with pytest.raises(UndeclaredReduction) as refusal:
        declare("a claim contradicting itself",
                **dict(WELL_FORMED, blind_to=WELL_FORMED["of"]))
    assert "declared blind AND reduced over" in str(refusal.value)


def test_a_multi_dimension_claim_must_say_whether_it_is_joint():
    """THE INPUT-SIDE HALF, and the second assertion is the null control.

    Three dimensions reduced one at a time and three reduced together read identically as a list of
    three names -- which is exactly how 21/21/5 was read as a statement about the weather a
    household sees. A declaration that cannot tell the two apart declares nothing.
    """
    three = dict(kind="coverage", of=("winter_temp", "annual_wind", "annual_sun"),
                 reduces_over=("winter_temp", "annual_wind", "annual_sun"))
    with pytest.raises(UndeclaredReduction):
        declare("a claim that will not say", **three, joint="yes")

    separable = declare("one at a time", **three, joint=False)
    together = declare("together", **three, joint=True)
    assert separable.separable and not together.separable
    assert separable.banner() != together.banner()


def test_the_collapse_is_computed_and_never_asserted():
    """A claim does not have to confess. Two components consumed by one dimension IS the collapse,
    and a derived dimension standing for a single component is a rename rather than a reduction."""
    collapsing = declare("a total", kind="coverage", of=("gas", "electricity"),
                         reduces_over=("total",), derived_from={"total": ("gas", "electricity")},
                         joint=True)
    renaming = declare("a rename", kind="coverage", of=("gas", "electricity"),
                       reduces_over=("gas_kwh",), derived_from={"gas_kwh": ("gas",)},
                       blind_to=("electricity",), joint=True)
    assert collapsing.collapsed == ("total",)
    assert renaming.collapsed == ()


# --------------------------------------------------------------------------------------------
# The census. Everything above is about a claim that CALLS the declaration; these are about
# finding the ones that do not.
# --------------------------------------------------------------------------------------------

def _fake_tree(tmp_path, *, filename: str, body: str) -> None:
    for package in ("tools", "simulation"):
        (tmp_path / package).mkdir(parents=True, exist_ok=True)
    (tmp_path / "tools" / filename).write_text(body)


def test_the_census_can_see_a_claim_that_declares_nothing(tmp_path):
    """THE POISON ROUND, and it runs before any green result in this file means anything.

    A census proved only by its own tree passing is a census that could be scanning nothing at all
    -- the shape that once graded ten contracts against an extract with no data and reported ten
    survivals. So a claim module that declares nothing is planted, and the census must find it.
    """
    _fake_tree(tmp_path, filename="fake_demand_probe.py", body=(
        "from tools import need_stock_joint\n\n\n"
        "def coverage(k):\n"
        "    return 0.99\n"
    ))
    found = dict(claim_modules(tmp_path))
    assert "tools.fake_demand_probe" in found, (
        "the census cannot see a planted undeclared claim, so its silence on the real tree "
        "says nothing")
    assert "coverage" in found["tools.fake_demand_probe"]


def test_a_claim_word_outside_the_subject_is_not_in_class(tmp_path):
    """The false-positive guard. `INSUFFICIENT_FUNDS` in a payments module is a claim word and is
    not a claim about the drawn population. A control that fires on it is one someone switches off,
    and then it protects nothing."""
    _fake_tree(tmp_path, filename="fake_payments.py", body=(
        "INSUFFICIENT_FUNDS = 'insufficient_funds'\n\n\n"
        "def coverage_of_direct_debits():\n"
        "    return 1.0\n"
    ))
    assert "tools.fake_payments" not in dict(claim_modules(tmp_path))


def test_a_claim_in_class_by_its_filename_alone_is_found(tmp_path):
    """THE LEG AIMED AT HOW THE CONCEPT IS ACTUALLY SPELLED.

    `tools/r3_carbon_score_ceiling.py` publishes a ceiling and no public symbol in it carries the
    word, so a symbol-only rule reads it as out of scope. Proved on a planted module rather than on
    the real one, because a test that only asserts today's tree cannot tell a working filename leg
    from a module that happens to also match on a symbol.
    """
    _fake_tree(tmp_path, filename="fake_thing_ceiling.py", body=(
        "from simulation import premise_population\n\n\n"
        "def measure():\n"
        "    return 1.0\n"
    ))
    found = dict(claim_modules(tmp_path))
    assert "tools.fake_thing_ceiling" in found
    assert any("filename" in reason for reason in found["tools.fake_thing_ceiling"])


def test_no_claim_about_the_drawn_population_arrives_silent():
    """THE LIVE TREE, AND THE PROPERTY IS THAT A NEW CLAIM CANNOT ARRIVE SILENT.

    Not `undeclared() == []`. That reads stricter and is not: it also refuses a claim whose
    declaration is written and blocked in another lane, and there this control has no move -- which
    is why it spent two days uncommittable while nine landed declarations went unguarded. The debt is
    named in `OUTSTANDING` with the document that discharges it. Anything else silent is the defect
    this leg owns, and the refusal names the module.
    """
    unexpected = unexpected_silence()
    assert unexpected == [], (
        "claims about the drawn population that declare no reduction dimension and are not named "
        "debt in tools.reduction_dimension.OUTSTANDING: "
        + "; ".join(f"{module} ({', '.join(reasons)})" for module, reasons in unexpected))


def test_the_outstanding_debt_is_shrink_only():
    """The amnesty guard. Without it the leg above is satisfiable by adding a row, so a new silent
    claim lands by being written down. FREE IN THE HONEST DIRECTION: paying the debt shrinks the list
    and this still passes, which is the direction a control must never refuse."""
    assert len(OUTSTANDING) <= 1, (
        "the outstanding-debt list has grown to "
        f"{len(OUTSTANDING)} rows ({', '.join(sorted(OUTSTANDING))}). A silent claim is not made "
        "legal by being listed -- land its declaration, or lower this ceiling to what is really "
        "blocked and say what blocks it")


def test_every_outstanding_row_names_a_document_that_still_exists():
    """THE ROUTE OUT OF THE LIST, and the reason this is not a permanent allowlist.

    Each row cites the finding whose discharge unblocks the declaration. When that document is
    archived out of `docs/staging/` the citation stops resolving and this goes red -- so the debt is
    re-measured by whoever discharged it rather than inherited by everyone after. Keyed to the
    document rather than to the module's disk state on purpose: the shared working tree and every
    clean HEAD extract disagree about which modules are silent, so a leg keyed to that is green in
    one tree and red in the other, which is the defect that produced this list.
    """
    project = Path(__file__).resolve().parent.parent.parent
    for dotted, reason in OUTSTANDING.items():
        cited = re.findall(r"docs/[\w./-]+\.md", reason.replace("\n", ""))
        assert cited, f"{dotted}'s outstanding row cites no document, so nothing discharges it"
        for path in cited:
            assert (project / path).exists(), (
                f"{dotted}'s outstanding row cites {path}, which is not in the tree. Either the "
                "blocker is discharged -- delete the row and land the declaration -- or the "
                "citation is wrong")


def test_the_census_holds_the_two_claims_the_canon_names():
    """The canon points at two live claims by name. A census that had drifted off either of them
    would be a control about something else wearing this file's name."""
    found = dict(claim_modules())
    assert "tools.demand_case_coverage" in found
    assert "tools.weather_cell_derivation" in found


def test_the_two_named_claims_state_what_they_average_away():
    """KEYED TO THE PROPERTY, NOT TO 13 OR TO 21/21/5. Neither figure is asserted here and neither
    is withdrawn: what is asserted is that each says which components of its subject it cannot see.
    If the demand claim is later measured on the whole vector, `blind_to` empties and this still
    passes -- which is the direction a control should be free in.
    """
    from tools import demand_case_coverage, weather_cell_derivation

    demand = demand_case_coverage.REDUCES_OVER
    assert demand.blind_to, "the 13-case claim must say which components it cannot distinguish"
    assert demand.collapsed, "it reduces over a total, and the total must say what it is made of"

    per_driver = weather_cell_derivation.REDUCES_OVER[0]
    assert per_driver.separable, (
        "the 21/21/5 read comes off the per-driver curve, and a claim that partitions on each "
        "driver alone must declare itself separable")
    assert "dwelling_fabric" in per_driver.blind_to
