"""C2_discovery_through_interfaces: the live legs of the wiring tests.

The caller and consumer legs (onboarding opening a belief through the home registry, and the
decarbonisation recommender reading it) were archived on 8 Nov 2026 with their three modules, in
archive increment 4b: no run reached any of them. They are at
archive/unhooked_supplier/tests/company/crm/test_c2_discovery_wired.py. What stays checks
that the two belief-layer modules still live, property_discovery and property_model, import
no ground truth, and that the import guard itself can fail.
"""
import datetime as dt


SWITCH_DATE = dt.date(2024, 1, 5)
ACCT = "C-WIRED-1"
UPRN = "100012345678"


# --- CALLER: onboarding opens a belief at signup, at the right confidences --


# --- CONSUMER: a real decision reads the belief, not ground truth ----------


# --- THE WALL HOLDS: consumer never imports/reads saas ground truth --------


def _import_lines(module):
    import inspect
    lines = []
    for raw in inspect.getsource(module).splitlines():
        s = raw.strip()
        if s.startswith('import ') or s.startswith('from '):
            lines.append(s)
    return lines


def _ground_truth_import_violations(import_lines):
    """Return the import lines (if any) that reach for sim-side ground truth
    -- the saas belief-of-record property model, or any simulation/sim module.

    The company belief layer builds its property picture from OBSERVED events
    only (company.crm.property_model / property_discovery). Importing
    saas/property_model.py (the ground-truth home record) or a simulation
    module here would be an epistemic-wall breach: the plan would then be able
    to read a truth a real supplier could never see. This is the shared
    checker behind every wall-guard test below; a violation is any offending
    import line.
    """
    bad = []
    for line in import_lines:
        if 'saas' in line or 'simulation' in line:
            bad.append(line)
        elif line.startswith('import sim') or line.startswith('from sim'):
            bad.append(line)
    return bad


def test_ground_truth_import_guard_actually_fires():
    # R15 -- the wall guard must be able to FAIL on its own named defect, or it
    # is theatre. Prove BOTH directions: it passes clean input and it flags
    # every forbidden ground-truth import form.
    clean = [
        'from company.crm.property_model import Property',
        'import datetime as dt',
        'from company.crm import property_discovery',
    ]
    assert _ground_truth_import_violations(clean) == []
    dirty = [
        'from saas.property_model import Property',   # the sim-side ground truth
        'import simulation.population_draw',
        'from sim.market import prices',
    ]
    assert len(_ground_truth_import_violations(dirty)) == 3


# The discovery module and the registry are the SIBLING HALVES of the same wall
# (C2 file_scope). Their docstrings PROMISE they import no ground truth --
# property_discovery.py: "nothing in this module imports from sim/ or
# simulation/, or from saas/property_model.py". Nothing enforced that promise
# until now, so a future edit adding `from saas.property_model import Property`
# to the very heart of the discovery mechanism would have shipped green.

def test_property_discovery_imports_no_ground_truth():
    from company.crm import property_discovery
    assert _ground_truth_import_violations(_import_lines(property_discovery)) == []


def test_belief_property_model_imports_no_ground_truth():
    # The company's BELIEF-side property model must never pull the saas
    # ground-truth property record it is deliberately kept separate from.
    from company.crm import property_model
    assert _ground_truth_import_violations(_import_lines(property_model)) == []
