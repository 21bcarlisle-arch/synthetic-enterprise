"""W2_36: the company switch decides whether the billing run is handed the theft screen's list."""

from __future__ import annotations

import dataclasses

from company.policy.decision_policy import CURRENT_POLICY
from simulation.run_phase4c_on_phase2b import theft_screen_request


def test_the_switch_is_off_by_default_and_on_hands_the_list_and_the_tenancy_links():
    """Defect: the screen runs with the switch off (the 19 Oct publish moves), or never runs with
    it on, or the incoming account is linked to anything but its outgoing account."""
    result = {"home_move_ins": [{"customer_id": "OCC-1", "premise": "C1", "commodity": "electricity"}]}
    on = dataclasses.replace(CURRENT_POLICY, theft_screen_in_billing_run=True)
    assert (theft_screen_request(None, result), theft_screen_request(on, result)) == (
        (None, {}), ([], {"OCC-1": "C1"}))
