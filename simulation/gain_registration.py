"""What the registration service and the losing supplier tell a GAINING supplier about one won
switch: the day the transfer completed, and whether the two suppliers later agreed it had been made
without a valid contract (an erroneous transfer).

Knowledge: `docs/market_research/switching_mechanics_2026-10-25.md` s.4 (rates) and s.6 (the
regulations as read). The company answers for these facts under regs 6ZA and 6ZB through
`company.interfaces.switching_gsop`; this module states them and never grades them.

WHAT IS DRAWN AND WHAT IS NOT
-----------------------------
* **Erroneous transfer, before CSS go-live only.** Drawn per won switch at
  `ERRONEOUS_TRANSFER_SHARE_PRE_CSS`. After 18 July 2022 no rate is published (named gap 2), so no
  erroneous transfer is drawn and the book UNDERSTATES 6ZB payments from that day by an unknown
  amount. Before 1 May 2020 an erroneous transfer still happens; reg 6ZB did not exist, so nothing
  is owed, and the door says so.
* **Registration delay: not drawn.** How often a GB switch misses 15 or 5 working days is not
  published (s.6 (b), named gap 3). The world still completes every switch on the day supply starts,
  and the supplier's information day is that same day, so reg 6ZA is judged on every gain and can
  never be failed. That UNDERSTATES 6ZA payments; ``registration_delay_working_days`` carries
  ``None`` with this reason rather than a zero that would read as measured.
* **Not built:** an erroneously transferred customer is returned to its old supplier (reg 6C, the
  OLD supplier's duty) within about 21 working days. The world keeps the household on supply, so the
  book carries about 0.5% of pre-CSS gains it should have lost. Owed as the next increment.
"""
from __future__ import annotations

import random
from datetime import date, timedelta

from simulation.bacs_processing_day import is_bacs_processing_day

#: CSS go-live, the day registration moved to the Central Switching Service. REC Schedule 23 v2.2
#: change history: version 1.0, implementation date "18 July 2022". The same day as
#: `interface.contracts.registration_loss_seam.CSS_GO_LIVE`, not imported from it: the world states
#: the day it holds, and an import would add an edge to the live wall for one date.
CSS_GO_LIVE = date(2022, 7, 18)

#: Share of domestic switches that were erroneous transfers: "about 0.5%" among the six large
#: suppliers in 2016 (roughly 25,000 a year), against about 1% in 2014. Ofgem, *Erroneous transfers
#: policy issue paper*, Aug 2016,
#: https://www.ofgem.gov.uk/sites/default/files/docs/2016/08/erroneous_transfers-policy_issue_paper.pdf ;
#: `docs/market_research/switching_mechanics_2026-10-25.md` s.4. The most recent published figure is
#: taken for 2016 to CSS go-live; the stated range is [0.005, 0.01], and a small supplier's own rate
#: is not published (it may sit above the six large suppliers').
ERRONEOUS_TRANSFER_SHARE_PRE_CSS = 0.005

#: Reg 6A of S.I. 2015/1544 (as inserted by S.I. 2019/218): old and new supplier agree "within 20
#: working days of the customer notification" whether the transfer had a valid contract
#: (`docs/market_research/switching_mechanics_2026-10-25.md` s.6). A STATED BELIEF on the dates: the
#: customer notices at the switch itself (the loss notice or the welcome pack arrives then), and the
#: agreement is taken on the last day 6A allows, so the payment is dated as late as the regulations
#: let it be. The true day lies in [supply start, this day].
ERRONEOUS_TRANSFER_AGREEMENT_WORKING_DAYS = 20

_DELAY_GAP = ("registration delay not drawn: no published share of GB switches missing 15 or 5 "
              "working days, 2016-2025 (switching_mechanics_2026-10-25.md s.6 (b), named gap 3)")
_POST_CSS_GAP = ("no erroneous transfer drawn after CSS go-live: no published post-CSS rate "
                 "(switching_mechanics_2026-10-25.md s.6 (c), named gap 2)")


def _working_day_end(first_day: date, working_days: int) -> date:
    """The last day of `working_days` England and Wales working days beginning with `first_day`."""
    d, counted = first_day, 0
    while True:
        if is_bacs_processing_day(d):
            counted += 1
            if counted == working_days:
                return d
        d += timedelta(days=1)


def draw_gain_registration(customer_id: str, supply_start: date, seed: str) -> dict:
    """The registration facts of one won switch, as the gaining supplier receives them.

    ``registration_confirmed_on`` is the day the registration service confirms the supplier is
    responsible; ``information_received_on`` and ``contract_on`` are the supplier's own records of
    the switch (both the supply start: the world has no delay to put between them).
    ``erroneous_transfer_agreed_on`` is the day the two suppliers agreed the transfer had no valid
    contract, or ``None``. Plain JSON-serialisable values only.
    """
    erroneous = False
    reasons = [_DELAY_GAP]
    if supply_start < CSS_GO_LIVE:
        erroneous = random.Random(f"{seed}_erroneous_transfer").random() < ERRONEOUS_TRANSFER_SHARE_PRE_CSS
    else:
        reasons.append(_POST_CSS_GAP)
    agreed = (_working_day_end(supply_start, ERRONEOUS_TRANSFER_AGREEMENT_WORKING_DAYS)
              if erroneous else None)
    return {
        "customer_id": customer_id,
        "information_received_on": supply_start.isoformat(),
        "contract_on": supply_start.isoformat(),
        "registration_confirmed_on": supply_start.isoformat(),
        "registration_delay_working_days": None,
        "erroneous_transfer_agreed_on": agreed.isoformat() if agreed else None,
        "not_drawn": reasons,
        # A drawn event, not a record of one: the real switch dates are not in our data.
        "data_regime": "synthetic",
    }
