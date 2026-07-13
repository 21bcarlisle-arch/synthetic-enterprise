"""Segment-correct debt policy objects -- atom C11_segment_debt_policy.

Company-side (INSIDE the wall). The company applies the correct debt terms &
conditions to an arrears account from the OBSERVABLE customer segment and
PUBLISHED regulation ONLY -- never from any SIM ground-truth "correct policy"
read. A company MISREADING the law stays structurally possible (real UK
suppliers get fined for exactly that); this module is the company's OWN
reading, and the harness (A6_coupled_triad_gap_metric) measures the gap
between it and the world atom's correct obligation (W2_9_segment_debt_tnc).
This module never imports the world/SIM side -- it only knows the segment on
its own account and the law it can read.

Three sub-policies, each with a real regulatory anchor (mirrors the
vat_by_segment shape in domain_invariants.py -- W2_9's own FRAME pass named
that as the exact working template for this atom):

  1. Statutory late-payment interest -- applies to BUSINESS debts ONLY.
     Late Payment of Commercial Debts (Interest) Act 1998 (LPCDCA): a
     business creditor may charge statutory interest at the Bank of England
     base rate on the LPCDCA reference date (31 Dec for H1, 30 Jun for H2)
     plus a fixed 8 percentage-point margin. Domestic debts are EXCLUDED --
     the Act covers commercial debts between businesses, not consumer
     contracts, so a domestic arrears account may NOT be charged this
     interest.

  2. Late-payment CHARGES -- NOT applied to DOMESTIC accounts (Ofgem SLC /
     Consumer Duty fairness; domestic late-payment charges are largely
     regulated out). Permitted under a BUSINESS commercial contract.

  3. Payment-conditioned tariff eligibility (DD-discount / good-payer gating)
     -- LAWFUL for both segments (a real commercial policy: direct-debit
     discount tariffs, good-payer gating), but constrained. A DD tariff must
     be set off a realistic consumption estimate and must NOT be used to
     over-collect credit (Ofgem Direct Debit Market Compliance Review, an
     active 2026 enforcement effort). Modelled here as a permitted-but-
     constrained flag, not a free parameter.

Time-indexed (REGULATION_COMMONS_DOCTRINE.md item 3, backfilled with real
anchored dates only -- never fabricated). The statutory interest RATE moves
with the Bank of England base rate, so it is a genuine per-period history
across the simulation's 2016-2025 span, not one hardcoded current value
(W2_9's FRAME pass named this requirement explicitly).

C-S2 (idempotency/determinism): every function here is pure -- same segment +
same as-of date -> identical policy object, no hidden state, safe to replay.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from enum import Enum
from typing import Optional


class Segment(str, Enum):
    """The three customer segments this company serves. Canonical internal
    values; `canonical_segment()` maps the several observed spellings
    (resi/residential/domestic, SME/sme, I&C/iandc) onto these."""
    DOMESTIC = "domestic"
    SME = "sme"
    IANDC = "iandc"


# The company observes segment on its own account records in several
# spellings (grep of company/ shows: resi, sme/SME, I&C, domestic,
# residential). Normalise defensively rather than trusting one spelling --
# a mis-spelled segment silently defaulting to "domestic" would be the C6
# SME-as-Household class all over again, so an UNKNOWN spelling raises
# rather than guessing.
_SEGMENT_ALIASES = {
    "resi": Segment.DOMESTIC,
    "residential": Segment.DOMESTIC,
    "domestic": Segment.DOMESTIC,
    "household": Segment.DOMESTIC,
    "sme": Segment.SME,
    "i&c": Segment.IANDC,
    "iandc": Segment.IANDC,
    "i_and_c": Segment.IANDC,
    "ic": Segment.IANDC,
    "industrial_and_commercial": Segment.IANDC,
}


def canonical_segment(raw: object) -> Segment:
    """Map an observed segment label onto the canonical Segment. Raises on an
    unrecognised/missing label -- fail closed, never silently default to
    domestic (that silent-default is exactly the mislabel class R10 names)."""
    if raw is None:
        raise ValueError("segment is required (got None) -- cannot select debt policy")
    key = str(raw).strip().lower()
    if key not in _SEGMENT_ALIASES:
        raise ValueError(f"unrecognised customer segment: {raw!r}")
    return _SEGMENT_ALIASES[key]


def is_business(segment: Segment) -> bool:
    """SME and I&C are business segments; domestic is not. The single binary
    that gates statutory interest and late charges."""
    return segment in (Segment.SME, Segment.IANDC)


# --- Statutory late-payment interest rate history (LPCDCA) ---

# LPCDCA s.6 / Late Payment of Commercial Debts Regulations 2002: statutory
# interest = the "reference rate" (Bank of England official Bank Rate on the
# relevant reference date) + a fixed 8 percentage-point margin. The reference
# date is 31 December for interest that starts to run in H1 (1 Jan-30 Jun) and
# 30 June for H2 (1 Jul-31 Dec). Source for each base value: Bank of England
# official Bank Rate history on those two dates each year; the resulting
# statutory rates match the gov.uk published "interest on late commercial
# payments" table. Real anchored values, NOT fabricated -- see W2_6/W2_9
# DISCOVER passes, which independently reconfirmed the current (mid-2026)
# 11.75% = base 3.75% + 8pts against the same real source.
_LPCDCA_MARGIN = 0.08


@dataclass(frozen=True)
class StatutoryInterestPeriod:
    effective_from: date
    effective_to: date  # inclusive last day the rate applies
    reference_base_rate: float
    statutory_rate: float  # reference_base_rate + 8pts

    def covers(self, as_of: date) -> bool:
        return self.effective_from <= as_of <= self.effective_to


def _period(y_from: int, m_from: int, d_from: int,
            y_to: int, m_to: int, d_to: int, base: float) -> StatutoryInterestPeriod:
    return StatutoryInterestPeriod(
        effective_from=date(y_from, m_from, d_from),
        effective_to=date(y_to, m_to, d_to),
        reference_base_rate=base,
        statutory_rate=round(base + _LPCDCA_MARGIN, 4),
    )


# BoE Bank Rate on the LPCDCA reference date -> statutory rate for the
# following half-year period. Spans the simulation's 2016-2025 modelled range.
_STATUTORY_INTEREST_HISTORY: list[StatutoryInterestPeriod] = [
    _period(2016, 1, 1, 2016, 6, 30, 0.0050),   # base @31Dec2015 0.50% -> 8.50%
    _period(2016, 7, 1, 2016, 12, 31, 0.0050),  # base @30Jun2016 0.50% -> 8.50%
    _period(2017, 1, 1, 2017, 6, 30, 0.0025),   # base @31Dec2016 0.25% -> 8.25%
    _period(2017, 7, 1, 2017, 12, 31, 0.0025),  # base @30Jun2017 0.25% -> 8.25%
    _period(2018, 1, 1, 2018, 6, 30, 0.0050),   # base @31Dec2017 0.50% -> 8.50%
    _period(2018, 7, 1, 2018, 12, 31, 0.0050),  # base @30Jun2018 0.50% -> 8.50%
    _period(2019, 1, 1, 2019, 6, 30, 0.0075),   # base @31Dec2018 0.75% -> 8.75%
    _period(2019, 7, 1, 2019, 12, 31, 0.0075),  # base @30Jun2019 0.75% -> 8.75%
    _period(2020, 1, 1, 2020, 6, 30, 0.0075),   # base @31Dec2019 0.75% -> 8.75%
    _period(2020, 7, 1, 2020, 12, 31, 0.0010),  # base @30Jun2020 0.10% -> 8.10%
    _period(2021, 1, 1, 2021, 6, 30, 0.0010),   # base @31Dec2020 0.10% -> 8.10%
    _period(2021, 7, 1, 2021, 12, 31, 0.0010),  # base @30Jun2021 0.10% -> 8.10%
    _period(2022, 1, 1, 2022, 6, 30, 0.0025),   # base @31Dec2021 0.25% -> 8.25%
    _period(2022, 7, 1, 2022, 12, 31, 0.0125),  # base @30Jun2022 1.25% -> 9.25%
    _period(2023, 1, 1, 2023, 6, 30, 0.0350),   # base @31Dec2022 3.50% -> 11.50%
    _period(2023, 7, 1, 2023, 12, 31, 0.0500),  # base @30Jun2023 5.00% -> 13.00%
    _period(2024, 1, 1, 2024, 6, 30, 0.0525),   # base @31Dec2023 5.25% -> 13.25%
    _period(2024, 7, 1, 2024, 12, 31, 0.0525),  # base @30Jun2024 5.25% -> 13.25%
    _period(2025, 1, 1, 2025, 6, 30, 0.0475),   # base @31Dec2024 4.75% -> 12.75%
    _period(2025, 7, 1, 2025, 12, 31, 0.0425),  # base @30Jun2025 4.25% -> 12.25%
]

# The Act's commencement -- the real anchored effective_from for the
# business-debt statutory-interest right as a broad rule. LPCDCA 1998 came
# into force 1 November 1998 (initially small-business creditors; extended to
# all business-to-business debts by 7 August 2002). Cited, not fabricated.
LPCDCA_EFFECTIVE_FROM = date(1998, 11, 1)

# The rate table only covers the modelled 2016-2025 span. A lookup outside it
# returns None (fail closed -- do not extrapolate a base rate we have not
# anchored), and callers must treat None as "cannot price interest, HELD".
STATUTORY_RATE_HISTORY_START = _STATUTORY_INTEREST_HISTORY[0].effective_from
STATUTORY_RATE_HISTORY_END = _STATUTORY_INTEREST_HISTORY[-1].effective_to

STATUTORY_INTEREST_TOLERANCE = 0.0005  # rate-match tolerance for the checker


def statutory_interest_rate(as_of: date) -> Optional[float]:
    """The LPCDCA statutory late-payment interest rate applicable on `as_of`
    (base rate on the reference date + 8pts). Returns None outside the
    anchored 2016-2025 history -- callers fail closed on None rather than
    guessing a rate."""
    for period in _STATUTORY_INTEREST_HISTORY:
        if period.covers(as_of):
            return period.statutory_rate
    return None


# --- The per-segment debt-terms policy object ---


@dataclass(frozen=True)
class DebtTerms:
    """The debt T&C the company applies to an arrears account of a given
    segment on a given date. Immutable value object -- the OUTPUT of the
    company's own reading of the law, independent of what any billing engine
    actually did (the checker below compares an APPLIED set against this)."""
    segment: Segment
    as_of: date
    late_payment_interest_applies: bool
    late_payment_interest_annual_rate: Optional[float]
    late_payment_charges_permitted: bool
    payment_conditioned_tariff_permitted: bool
    basis: str


_DOMESTIC_BASIS = (
    "Domestic: LPCDCA 1998 does not cover consumer debt (no statutory interest); "
    "Ofgem SLC / Consumer Duty -- no domestic late-payment charges. DD-discount "
    "tariff eligibility lawful but fairness-constrained (Ofgem DD Market Review)."
)
_BUSINESS_BASIS = (
    "Business (SME/I&C): LPCDCA 1998 statutory late-payment interest applies "
    "(base rate on the reference date + 8pts); late-payment charges permitted "
    "under commercial T&C; payment-conditioned tariff eligibility lawful."
)


def select_debt_terms(raw_segment: object, as_of: date) -> DebtTerms:
    """Select the applicable debt T&C for a customer from OBSERVABLE segment +
    PUBLISHED regulation. This is the company's capability: the RIGHT terms
    per segment. It reads nothing but its own account's segment and the law.

    Business segments get statutory interest (rate from the LPCDCA history);
    domestic gets none, and no late charges. A business account whose `as_of`
    falls outside the anchored rate history gets applies=True but rate=None --
    the company knows interest is DUE but cannot price it, which the consumer
    must treat as HELD, not as zero interest."""
    segment = canonical_segment(raw_segment)
    if not isinstance(as_of, date):
        raise TypeError(f"as_of must be a date, got {type(as_of).__name__}")
    if is_business(segment):
        return DebtTerms(
            segment=segment,
            as_of=as_of,
            late_payment_interest_applies=True,
            late_payment_interest_annual_rate=statutory_interest_rate(as_of),
            late_payment_charges_permitted=True,
            payment_conditioned_tariff_permitted=True,
            basis=_BUSINESS_BASIS,
        )
    return DebtTerms(
        segment=segment,
        as_of=as_of,
        late_payment_interest_applies=False,
        late_payment_interest_annual_rate=None,
        late_payment_charges_permitted=False,
        payment_conditioned_tariff_permitted=True,
        basis=_DOMESTIC_BASIS,
    )


# --- The control: does an APPLIED set of debt terms match the law for the
# --- segment? Independent of the applied terms (derives the correct policy
# --- from segment + law, NOT from the applied object), fails CLOSED on
# --- missing/malformed input (R15).

_REQUIRED_APPLIED_KEYS = ("interest_applied", "late_charge_applied")


def check_debt_terms_lawful_for_segment(
    raw_segment: object, applied: object, as_of: date
) -> bool:
    """The Tier-1 control (R15-shaped): returns True iff the debt T&C actually
    APPLIED to an account are lawful for its segment, and False (FIRES) when a
    WRONG-SEGMENT term is applied. Named defects it must fire on:
      - a DOMESTIC account charged late-payment interest (LPCDCA is
        business-only);
      - a DOMESTIC account charged a late-payment charge;
      - a BUSINESS account charged interest at a rate other than the LPCDCA
        statutory rate for the period (over/under-charging interest).

    INDEPENDENCE (anti-tautology, R15): the "correct" side is derived from the
    observed segment + the law here, NOT from the `applied` object being
    checked -- so it can catch a mislabel/mis-application, unlike a check that
    reads the expected value from the same source it validates.

    FAIL CLOSED (R15 fail-open killer): a missing/malformed `applied` payload,
    an unrecognised segment, or a business interest charge the company cannot
    price (rate history exhausted) all return False (HELD), never a silent
    pass. An unverifiable control is a FAILED control.

    ONE-DIRECTIONAL where honesty demands it: not charging lawful business
    interest is a commercial choice, not an unlawful act, so it does NOT fire
    -- only the unlawful directions (a domestic charge, a wrong rate) do."""
    # Fail closed on a segment we cannot canonicalise.
    try:
        segment = canonical_segment(raw_segment)
    except (ValueError, TypeError):
        return False

    if not isinstance(applied, dict):
        return False
    for k in _REQUIRED_APPLIED_KEYS:
        if k not in applied or not isinstance(applied[k], bool):
            return False

    interest_applied = applied["interest_applied"]
    late_charge_applied = applied["late_charge_applied"]

    if not is_business(segment):
        # DOMESTIC: neither statutory interest nor a late charge is lawful.
        if interest_applied:
            return False
        if late_charge_applied:
            return False
        return True

    # BUSINESS: interest and late charges are permitted. If interest is
    # applied, it MUST be at the LPCDCA statutory rate for the period.
    if interest_applied:
        applied_rate = applied.get("interest_rate")
        if not isinstance(applied_rate, (int, float)):
            return False  # fail closed: interest applied but no verifiable rate
        expected = statutory_interest_rate(as_of)
        if expected is None:
            return False  # fail closed: cannot verify the rate for this date
        if abs(applied_rate - expected) > STATUTORY_INTEREST_TOLERANCE:
            return False  # wrong statutory rate -- over/under-charging interest
    return True
