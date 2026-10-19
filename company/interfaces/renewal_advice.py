"""The company's RENEWAL-ADVICE door: the desk that decides C34 at each renewal notice, per household.

REUSE: company/interfaces/renewal_advice.py
CLASS: CUSTOM
INDEX: searched "renewal", "advice", "next_best_action" under company/interfaces/. The decision and
       its record live in `company/crm/renewal_advice_desk.py`; this door only hands the run the
       desk, as `contact_programme` hands it the holdout coin.

In: the run's policy, then per leg the company's own observables at the roll. Out, at the end of
the run: the decision rows. Nothing crosses back into the world.
"""
from __future__ import annotations

from company.crm.renewal_advice_desk import RenewalAdviceDesk

__all__ = ["RenewalAdviceDesk"]
