"""R15 proof for the wall-side control on the two-sided-wall exhibit.

The point of this file is NOT that `site/explore/index.html` is currently clean -- a checker
that returns `[]` for every input also proves that. Each mutation below takes the REAL page,
breaks it in one named way, and asserts the check fires. That is the difference between a
control and a decoration, and the ruling SITE2 was minted from says so in as many words.

Atom: SITE2_two_sided_wall_exhibit, exit criteria 1, 3 and 8.
"""

from __future__ import annotations

import pytest

from tools import explore_wall_sides as ws


@pytest.fixture(scope="module")
def html() -> str:
    return ws.read_exhibit()


# --------------------------------------------------------------------------- the page is clean


def test_the_live_exhibit_has_no_wall_side_violations(html):
    assert ws.check_page(html) == []


def test_every_panel_on_the_page_declares_one_of_the_three_sides(html):
    panels = ws.parse_panels(html)
    assert panels, "no panels parsed -- the checker is disconnected from the page"
    assert {p["side"] for p in panels} <= set(ws.SIDES)
    # All three vantages are actually USED. An exhibit about the wall that only ever renders one
    # side is not the exhibit the ruling kept -- it is the leak-free page it deliberately refused.
    assert {p["side"] for p in panels} == set(ws.SIDES)


def test_the_page_renders_the_named_sim_only_and_company_only_figures(html):
    """The exhibit still SHOWS all three layers -- exit criterion 'keep all three layers'.

    Without this, deleting the company and sim panels outright would make every other test in
    this file pass, and the control would be enforcing the opposite of the ruling.
    """
    sides = {p["side"]: p["text"] for p in ws.parse_panels(html)}
    assert "sim_truth" in sides["sim"], "the belief-vs-truth panel no longer shows sim truth"
    assert "cost_to_serve_gbp" in sides["company"], "the company panel no longer shows cost to serve"


# ------------------------------------------------------------------- MUTATIONS: it must fail

def test_a_handwritten_panel_with_no_side_is_caught(html):
    """Exit criterion 1: adding a panel without declaring a side FAILS."""
    mutant = html.replace(
        'panel("customer", "Meter reads behind it",',
        '\'<div class="panel"><h3>Meter reads behind it</h3>\' + (',
        1,
    )
    assert mutant != html, "mutation did not apply -- the anchor text has moved"
    found = ws.check_no_handwritten_panels(mutant)
    assert found, "an undeclared panel was added and the control stayed green"
    assert "no declared wall side" in found[0]
    assert ws.check_page(mutant), "check_page did not surface the undeclared panel"


def test_a_side_outside_the_vocabulary_is_caught(html):
    mutant = html.replace('panel("customer", "For them"', 'panel("household", "For them"', 1)
    assert mutant != html, "mutation did not apply -- the anchor text has moved"
    found = ws.check_declared_sides(mutant)
    assert found and "'household' is not one of" in found[0].replace('"', "'")


def test_moving_the_sim_truth_panel_onto_the_company_side_is_caught(html):
    """Exit criterion 3, the named instance: the causal/belief chain is SIM-only.

    `sim_truth` is the household's real probability of leaving. Attributing the panel that
    prints it to the company asserts a supplier can read a figure no supplier can.
    """
    mutant = html.replace(
        'panel("sim", "Belief against truth, at each renewal"',
        'panel("company", "Belief against truth, at each renewal"',
        1,
    )
    assert mutant != html, "mutation did not apply -- the anchor text has moved"
    found = ws.check_no_cross_wall_leaks(mutant)
    assert found, "a SIM-only figure moved under a company panel and the control stayed green"
    assert "sim_truth" in found[0] and "company-attributed" in found[0]


def test_moving_a_company_only_figure_into_the_customer_subset_is_caught(html):
    """Exit criterion 3, the other direction and the other named instance."""
    mutant = html.replace('panel("company", "For us"', 'panel("customer", "For us"', 1)
    assert mutant != html, "mutation did not apply -- the anchor text has moved"
    found = ws.check_no_cross_wall_leaks(mutant)
    assert found, "cost-to-serve moved into the customer-eye subset and the control stayed green"
    assert any("cost_to_serve_gbp" in f and "customer-eye subset" in f for f in found)


def test_the_private_journey_state_is_caught_in_the_customer_subset(html):
    """The household's private disposition is the ruling's third named SIM-only figure."""
    mutant = html.replace(
        'panel("sim", "Everything it did not",',
        'panel("customer", "Everything it did not", (d.reaction_chain||[]).filter(function(e){'
        'return e.event_type === "journey_state";}) && ',
        1,
    )
    assert mutant != html, "mutation did not apply -- the anchor text has moved"
    found = ws.check_no_cross_wall_leaks(mutant)
    assert found and any("journey_state" in f for f in found)


# ------------------------------------------------------- the checker's own fail-open corners


def test_a_page_with_no_panels_is_a_violation_not_a_pass():
    """FAIL-OPEN guard. Renaming the helper must red the gate, not silently check nothing."""
    violations = ws.check_page("<html><body><p>nothing here</p></body></html>")
    assert violations, "an empty page passed -- the control is fail-open"
    assert "disconnected from the page" in violations[0]


def test_a_comment_mentioning_a_figure_is_not_a_leak(html):
    """The page's own prose names these figures. A checker that counted comments would be
    unusable, and its first false positive would be the last time anyone read its output."""
    mutant = html.replace(
        'panel("customer", "For them"',
        '/* cost_to_serve_gbp sim_truth journey_state */ panel("customer", "For them"',
        1,
    )
    assert mutant != html, "mutation did not apply -- the anchor text has moved"
    assert ws.check_no_cross_wall_leaks(mutant) == []


def test_the_helpers_own_error_string_is_not_parsed_as_a_call(html):
    """The helper throws with the text "panel() needs a wall side". Locating calls in a
    string-blanked view is what keeps that from reading as an undeclared call site."""
    assert 'panel() needs a wall side' in html
    assert all(p["side"] is not None for p in ws.parse_panels(html))


def test_the_control_is_reachable_from_a_page_edit():
    """FAIL-SILENT guard, and the half that makes the rest of this file matter.

    A control that only runs when its own module is edited is silent on exactly the commit that
    breaks it -- the selection-layer defect tools/pre_commit_test_gate.py documents against its
    own STORE_CONTRACT_TESTS. This asserts the wiring, not the intent.
    """
    from tools import pre_commit_test_gate as gate

    assert "tests/tools/test_explore_wall_sides.py" in gate.SITE_SURFACE_TESTS
    assert gate.SITE_SURFACE_PREFIX == "site/"
