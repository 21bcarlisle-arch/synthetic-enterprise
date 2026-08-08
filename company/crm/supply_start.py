"""Company Layer — supply-start semantics for the CRM.

One date field was doing two jobs. This module separates them and names them.

- **Term anchor** (`term_anchor_date`) — the date the 365-day fixed-term renewal
  grid is counted from. For a successor account this is deliberately pinned to
  the *predecessor's* genesis date so the term boundaries stay on one grid
  (`saas/customers.py` SUCCESSOR_CUSTOMERS, `simulation/renewals.py`). That is
  correct and load-bearing; nothing here changes it.
- **Supply start** (`supply_start`) — the date *this* customer's supply with us
  actually began. This is what "customer since", tenure, loyalty eligibility,
  vulnerability duration and acquisition-cohort all mean when they read a date.

Feeding the anchor into `supply_start` gave a re-contracted customer a phantom
history: the predecessor's genesis date reads as their relationship start, so
their apparent tenure never resets to the truth and every tenure-derived number
downstream inherits the error.

**Where the real date comes from — and why reading it is wall-legal.** The
activation date is supplied by the caller as an observable customer event
(the acquisition/registration event: `{event_type, customer_id, event_date,
channel, predecessor_id}`). A real UK supplier's CRM records supply-start from
exactly that registration/switch event. This module never imports or reads
simulation internals; it takes an observation and applies a stated rule.

**UNKNOWN is a legitimate value, back-dating is not.** Where no activation
observable exists and the record's own anchor is known to be someone else's
(a successor), the honest answer is that we do not know when this relationship
started. That is recorded as `None`/NULL, never silently back-filled from the
anchor: a fabricated tenure is worse than an absent one, and back-filling is
the exact shape of a Historical Ground Truth breach.
"""

import datetime as dt
from typing import Mapping, Optional

# The anchor default that `seed_from_customers` has always applied when a
# record carries no `acquisition_date`. Preserved verbatim for the *anchor*
# (semantic A is unchanged by this module) but deliberately NOT used as a
# supply-start fallback -- see `derive_supply_start`.
DEFAULT_TERM_ANCHOR = "2016-01-01"


def _parse_iso_date(value: str, field: str) -> dt.date:
    """Parse an ISO date, raising on anything malformed.

    Deliberately fail-loud. A malformed activation date must not fall back to
    the anchor: a silent fallback would reintroduce exactly the phantom this
    module exists to remove, and would do it invisibly.
    """
    if not isinstance(value, str):
        raise ValueError(f"{field} must be an ISO date string, got {type(value).__name__}")
    try:
        return dt.date.fromisoformat(value)
    except ValueError as exc:
        raise ValueError(f"{field} is not a valid ISO date: {value!r}") from exc


def derive_term_anchor(customer: Mapping) -> str:
    """The term/billing anchor for a customer record.

    Unchanged behaviour: the record's `acquisition_date`, defaulting to
    `DEFAULT_TERM_ANCHOR`. For a successor this is the predecessor's genesis
    date, which is what keeps the renewal grid aligned.
    """
    anchor = customer.get("acquisition_date") or DEFAULT_TERM_ANCHOR
    _parse_iso_date(anchor, "acquisition_date")
    return anchor


def derive_supply_start(
    customer: Mapping,
    activation_by_account: Optional[Mapping[str, str]] = None,
) -> Optional[str]:
    """The date this customer's supply with us actually began, or None.

    Resolution order:

    1. **An activation observable for this account wins, always.** This is the
       registration/switch event a real CRM would record supply-start from.
    2. Otherwise, if the record has no `successor_of`, its `acquisition_date`
       genuinely *is* its own relationship start (base and fresh-market
       customers are acquired on the date the field carries) -- use it.
    3. Otherwise -- a successor with no activation observable -- return
       ``None``. The only date on the record belongs to the *predecessor*, so
       there is nothing here to derive a truthful answer from. UNKNOWN is
       recorded; the anchor is never borrowed.

    A record with no `acquisition_date` at all also resolves to ``None`` rather
    than to `DEFAULT_TERM_ANCHOR`: that default is an anchor convention, and
    stamping it as a relationship start would invent a tenure.
    """
    account_id = customer.get("customer_id")
    activation = (activation_by_account or {}).get(account_id)
    if activation is not None:
        _parse_iso_date(activation, f"activation date for {account_id}")
        return activation

    if customer.get("successor_of"):
        return None

    acquisition_date = customer.get("acquisition_date")
    if not acquisition_date:
        return None
    _parse_iso_date(acquisition_date, "acquisition_date")
    return acquisition_date


def migrate_legacy_supply_start(
    legacy_supply_start: Optional[str],
    successor_of: Optional[str],
) -> Optional[str]:
    """The stated, recorded rule for back-filling an existing registry row.

    Legacy rows carry ONE date, written from `acquisition_date` -- so what the
    `supply_start` column actually held was the *anchor*. Splitting it:

    - `term_anchor_date` := the legacy value (that is what it really was).
    - `supply_start`     := the legacy value **only** where `successor_of` is
      NULL, because for a non-successor the anchor and the relationship start
      coincide. For a successor the legacy value is the predecessor's genesis
      date and is not recoverable as this customer's supply start, so it
      becomes UNKNOWN (``None``).

    Callers holding an activation observable for a migrated account should
    re-seed it; this rule covers only what can be concluded from the row itself.
    """
    if successor_of:
        return None
    return legacy_supply_start
