"""The company's CONTACT-PROGRAMME door: which arm of a contact programme an account is in.

REUSE: company/interfaces/contact_programme.py
CLASS: CUSTOM
INDEX: searched "contact", "holdout", "send_contact" under company/interfaces/. `sim_interface`
       carries the send itself (COMPANY -> WORLD, W2_39) and answers only whether it went; the
       save-offer and renewal-offer doors answer a price. Whether to send at all is a separate
       decision of the company's, so it is a separate door.

In: the account, the share the run's policy holds out (`DecisionPolicy.svt_contact_holdout_share`),
and a salt naming the run. Out: "treated", "holdout", or None when the policy holds nobody out.
The coin is `company/crm/next_best_action.in_contact_holdout`; the run sends only to "treated" and
None, and records the arm so the company can read its own holdout back (C34).

`sends_at_segment` is when (C30): at every default segment, the flat rule, or once per stint at its
first, read off the company's own record of when the account rolled onto its default.
"""
from __future__ import annotations

from company.crm.next_best_action import in_contact_holdout

__all__ = ["contact_arm", "sends_at_segment"]


def contact_arm(account_id: str, holdout_share: float | None, run_salt: str) -> str | None:
    if holdout_share is None:
        return None
    return "holdout" if in_contact_holdout(account_id, holdout_share, run_salt) else "treated"


def sends_at_segment(segment_start: str, stint_start: str, once_per_stint: bool) -> bool:
    return not once_per_stint or segment_start == stint_start
