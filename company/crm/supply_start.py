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

**The observable floor (atom C15) — why the `successor_of` test was not enough.**
That test reads *paperwork*, which can go missing; when it does, a successor is
indistinguishable from a base customer and the anchor rule emits the
predecessor's genesis date — the phantom above, returning through a different
door. This atom's registered law
(`SUPPLY_START_NOT_BEFORE_FIRST_OBSERVABLE`) is instead stated against what
cannot go missing: a supply start can never predate the earliest thing we ever
observed about the account, because a supplier that is not reading the meter is
not supplying. The derivation disagreed with that law — measurably, on the real
population — so it now carries the same floor (`_not_before_first_observable`).

Two deliberate asymmetries with the auditing invariant, both load-bearing:

- *Absent observables do not constrain the derivation* (the registry-seeding
  path, whose records carry none): nothing observed means nothing contradicted.
  The auditor instead FAILS such a record, because an unavailable check is a
  failed check (R15) — a statement about a record it must judge, not about what
  may be derived.
- *This module must not import the checker.* Borrowing the auditor's predicate
  would make the audit tautological: the guard could never again fire on this
  derivation, including when the derivation is wrong (R15 killer pattern 1). The
  two agree because both are right, not because one asks the other, and
  `test_the_floor_and_the_invariant_read_the_same_observables` fails if their
  keysets drift.
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


#: Fields on a CRM account record that each bound the earliest point we knew the
#: account existed. Any one of them is enough to floor a derived supply start.
#: Kept as a fixed tuple, and deliberately a SEPARATE declaration from the
#: auditing invariant's own list -- see the module docstring on why this module
#: must not import the checker. Drift between the two is a test failure, not a
#: silent divergence.
OBSERVABLE_FLOOR_FIELDS = (
    "acquisition_event_date",
    "first_meter_read_date",
    "first_issued_bill_date",
)


def _observable_floor(customer: Mapping) -> Optional[dt.date]:
    """The earliest date this account was ever observed, or None if never.

    None means "no observable on this record", which imposes no constraint --
    not "the check passed". A field that is present but malformed raises, in
    keeping with the rest of this module: a corrupt observable must not quietly
    become an absent one, because that would turn the floor off exactly when the
    data is least trustworthy.
    """
    earliest: Optional[dt.date] = None
    for field in OBSERVABLE_FLOOR_FIELDS:
        raw = customer.get(field)
        if raw is None:
            continue
        observed = _parse_iso_date(raw, field)
        if earliest is None or observed < earliest:
            earliest = observed
    return earliest


def _not_before_first_observable(
    candidate: Optional[str],
    customer: Mapping,
) -> Optional[str]:
    """`candidate`, unless the account's own observables contradict it.

    A start earlier than something we already observed about the account is not
    a start we can have witnessed, whatever rule produced it. Such a candidate
    is dropped to UNKNOWN rather than clamped -- the observables bound the true
    start from ABOVE, so the floor tells us the candidate is wrong without
    telling us what is right.
    """
    if candidate is None:
        return None
    floor = _observable_floor(customer)
    if floor is None:
        return candidate
    if _parse_iso_date(candidate, "derived supply_start") < floor:
        return None
    return candidate


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

    **Every branch is then floored** at the account's own earliest observable,
    so no rule here can emit a start that predates something we already saw.
    That is what catches step 2 when the `successor_of` link went missing: the
    only remaining evidence that the anchor is someone else's is that we were
    reading this account's meter years after the date it claims. It applies to
    step 1 too -- an activation event contradicting a meter read means the
    observables disagree, and two conflicting facts do not license picking one.
    """
    account_id = customer.get("customer_id")
    activation = (activation_by_account or {}).get(account_id)
    if activation is not None:
        _parse_iso_date(activation, f"activation date for {account_id}")
        return _not_before_first_observable(activation, customer)

    if customer.get("successor_of"):
        return None

    acquisition_date = customer.get("acquisition_date")
    if not acquisition_date:
        return None
    _parse_iso_date(acquisition_date, "acquisition_date")
    return _not_before_first_observable(acquisition_date, customer)


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
