"""Company realized-margin feedback into renewal tariff (Phase 16c).

A real energy supplier observes its own billing revenue and wholesale
hedging cost at the end of each contract term. If the term was loss-making,
the pricing team applies a recovery surcharge at the next renewal to begin
recovering the loss. This is entirely observable-data: the company issues
the bills and records the hedge cost from its own trading records.

Algorithm:
  loss_fraction = max(0, -term_margin / term_revenue)
  surcharge = min(MAX, max(0, loss_fraction - THRESHOLD))

Where:
  THRESHOLD = 0.05  — ignore small losses (noise / margin variance)
  MAX = 0.20        — cap recovery surcharge at 20%

At 5% loss → surcharge = 0% (below threshold, not material)
At 15% loss → surcharge = 10% (15% - 5% threshold)
At 30% loss → surcharge = 20% (capped)

The surcharge is applied multiplicatively to the base unit_rate computed
from the company's forward price estimate.

Applies only to electricity contracts (term_index ≥ 1). Gas uses
separate renewal logic and smaller margins that don't trigger the
threshold in normal years.
"""

FEEDBACK_LOSS_THRESHOLD = 0.05   # loss must exceed 5% of revenue to trigger
FEEDBACK_MAX_SURCHARGE = 0.20    # surcharge capped at 20%


def compute_margin_surcharge(prev_margin_gbp: float, prev_revenue_gbp: float) -> float:
    """Recovery surcharge fraction based on prior-term realized margin.

    prev_margin_gbp: net margin (after capital cost) for the prior contract term.
        Negative if the company lost money on this customer.
    prev_revenue_gbp: total billing revenue for the prior contract term.
        Used to normalize the loss into a fraction.

    Returns: surcharge fraction in [0.0, FEEDBACK_MAX_SURCHARGE].
        Multiply against base unit_rate: new_rate = base_rate × (1 + surcharge).
    """
    if prev_revenue_gbp <= 0:
        return 0.0
    loss_fraction = max(0.0, -prev_margin_gbp / prev_revenue_gbp)
    if loss_fraction <= FEEDBACK_LOSS_THRESHOLD:
        return 0.0
    return min(FEEDBACK_MAX_SURCHARGE, loss_fraction - FEEDBACK_LOSS_THRESHOLD)
