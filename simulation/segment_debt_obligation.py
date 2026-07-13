"""WORLD ground truth for segment debt T&C -- atom W2_9_segment_debt_tnc.

This is SIM/WORLD side (the ANSWER KEY). It holds the CORRECT per-segment debt
obligation: given a customer's TRUE segment and a date, what debt T&C SHOULD
lawfully apply. The company's OWN reading of that same law is C11
(company/compliance/segment_debt_policy.py); the harness scores C11 against
THIS module (background/gap_metric.py + tools/couple_w2_9_c11.py).

REGULATION-COMMONS DOCTRINE (CLAUDE.md). The regulatory TEXT is a shared
commons -- law is published in reality, readable by every lane. So this world
module and the company's C11 both encode the SAME real statutes. Independence
(R15 anti-tautology) does NOT come from encoding a DIFFERENT law -- it comes
from WHERE each side gets the customer's SEGMENT:

  * This world module scores against the customer's TRUE segment (SIM ground
    truth -- what the customer actually is).
  * C11 acts on the OBSERVED segment recorded on the company's own account book
    (`observed_segment()` below), which can be MISCLASSIFIED at onboarding.

A company that has mis-recorded a microbusiness as a domestic account (a real,
documented UK problem -- see below) will apply DOMESTIC debt terms to a
BUSINESS customer, or vice versa. The belief-vs-truth GAP is exactly the
fraction of accounts where the wrong-segment T&C is applied. This is a genuine
compliance/fairness gap, NOT a tautology: even though both sides read identical
law, they disagree because the company cannot see the true segment -- only its
(imperfect) record. This deliberately mirrors the C6 SME-as-Household mislabel
class R10 already names.

THE THREE REAL REGULATORY ANCHORS (cited, never fabricated; time-indexed per
REGULATION_COMMONS_DOCTRINE.md item 3):

  1. STATUTORY LATE-PAYMENT INTEREST -- BUSINESS ONLY. Late Payment of
     Commercial Debts (Interest) Act 1998 (LPCDCA), in force 1 November 1998
     (extended to all business-to-business debts by 7 August 2002). Statutory
     interest = Bank of England base rate on the reference date (31 Dec for
     H1, 30 Jun for H2) + a fixed 8 percentage-point margin. The Act covers
     COMMERCIAL debts between businesses -- domestic consumer contracts are
     EXCLUDED, so a domestic arrears account may NOT be charged this interest.

  2. DOMESTIC LATE-PAYMENT CHARGES -- NOT PERMITTED. Ofgem Standard Licence
     Conditions / Consumer Duty fairness: domestic late-payment charges are
     largely regulated out. Permitted under a business commercial contract.

  3. PAYMENT-CONDITIONED TARIFF ELIGIBILITY -- LAWFUL FOR BOTH, CONSTRAINED.
     Direct-debit-discount / good-payer-gated tariffs are lawful commercial
     policy for both segments, but constrained by the Ofgem Direct Debit
     Market Compliance Review (an active 2026 enforcement effort): a DD tariff
     must be set off a realistic consumption estimate and must not be used to
     over-collect credit. Modelled as a permitted-but-constrained flag.

The statutory interest RATE moves with the BoE base rate, so it is a genuine
per-period history across the 2016-2025 modelled span -- the real values are
DELIBERATELY held here independently of C11's copy (both read the same public
BoE Bank Rate history; agreeing on a real fact is regulation-commons, not a
copy). The GAP does not even depend on the rate -- it depends on which
SEGMENT's terms apply -- so rate agreement cannot manufacture a tautological
gap.

DETERMINISM (C-S2). Every function is pure OR seeds a NAMED RNG substream from
a stable hash of its inputs -- same customer -> same observed segment on every
run, no wall-clock, no global RNG, replay-safe. `observed_segment()` uses the
named substream "w2_9_segment_observation" so a draw here can never perturb any
other subsystem's stream.
"""
from __future__ import annotations

import hashlib
from dataclasses import dataclass
from datetime import date
from typing import Optional

# ---------------------------------------------------------------------------
# Segment -> obligation-class (independent of C11's Segment enum; the world
# normalises the observed spellings on its own terms).
# ---------------------------------------------------------------------------

# The obligation differs on ONE binary axis: is this a BUSINESS customer
# (SME / I&C -> commercial T&C) or a DOMESTIC one (consumer protection)?
DOMESTIC_TERMS = "domestic_terms"
BUSINESS_TERMS = "business_terms"

_DOMESTIC_LABELS = {"resi", "residential", "domestic", "household", "home"}
_SME_LABELS = {"sme", "small_business", "microbusiness", "micro_business"}
_IANDC_LABELS = {"iandc", "i&c", "i_and_c", "ic", "industrial_and_commercial", "ind_comm"}
_BUSINESS_LABELS = _SME_LABELS | _IANDC_LABELS


def _norm(raw: object) -> str:
    if raw is None:
        raise ValueError("segment is required (got None) -- cannot fix the debt obligation")
    return str(raw).strip().lower()


def true_terms_class(raw_segment: object) -> str:
    """The obligation CLASS a customer of this TRUE segment must lawfully be on:
    BUSINESS_TERMS for SME/I&C, DOMESTIC_TERMS for domestic. Raises on an
    unrecognised label -- fail closed, never silently default (the silent
    SME-as-domestic default is exactly the mislabel class R10 forbids)."""
    key = _norm(raw_segment)
    if key in _DOMESTIC_LABELS:
        return DOMESTIC_TERMS
    if key in _BUSINESS_LABELS:
        return BUSINESS_TERMS
    raise ValueError(f"unrecognised customer segment: {raw_segment!r}")


def is_business_segment(raw_segment: object) -> bool:
    return true_terms_class(raw_segment) == BUSINESS_TERMS


# ---------------------------------------------------------------------------
# LPCDCA statutory late-payment interest rate history (WORLD copy).
# BoE official Bank Rate on the LPCDCA reference date + 8pts. Real anchored
# values across the simulation's 2016-2025 span; the reference-date rule is
# 31 Dec (for H1) / 30 Jun (for H2). Agreeing with C11's copy of these public
# BoE figures is regulation-commons, not a tautology (see module docstring).
# ---------------------------------------------------------------------------

LPCDCA_MARGIN = 0.08
# LPCDCA 1998 commencement -- the real anchored effective_from for the
# business statutory-interest right (aligned with C11's LPCDCA_EFFECTIVE_FROM).
LPCDCA_EFFECTIVE_FROM = date(1998, 11, 1)


@dataclass(frozen=True)
class _RatePeriod:
    effective_from: date
    effective_to: date  # inclusive
    base_rate: float

    @property
    def statutory_rate(self) -> float:
        return round(self.base_rate + LPCDCA_MARGIN, 4)

    def covers(self, as_of: date) -> bool:
        return self.effective_from <= as_of <= self.effective_to


def _rp(yf, mf, df, yt, mt, dt, base) -> _RatePeriod:
    return _RatePeriod(date(yf, mf, df), date(yt, mt, dt), base)


# BoE Bank Rate on the reference date -> statutory rate for the following
# half-year. Real values, 2016-2025.
_RATE_HISTORY: list[_RatePeriod] = [
    _rp(2016, 1, 1, 2016, 6, 30, 0.0050),
    _rp(2016, 7, 1, 2016, 12, 31, 0.0050),
    _rp(2017, 1, 1, 2017, 6, 30, 0.0025),
    _rp(2017, 7, 1, 2017, 12, 31, 0.0025),
    _rp(2018, 1, 1, 2018, 6, 30, 0.0050),
    _rp(2018, 7, 1, 2018, 12, 31, 0.0050),
    _rp(2019, 1, 1, 2019, 6, 30, 0.0075),
    _rp(2019, 7, 1, 2019, 12, 31, 0.0075),
    _rp(2020, 1, 1, 2020, 6, 30, 0.0075),
    _rp(2020, 7, 1, 2020, 12, 31, 0.0010),
    _rp(2021, 1, 1, 2021, 6, 30, 0.0010),
    _rp(2021, 7, 1, 2021, 12, 31, 0.0010),
    _rp(2022, 1, 1, 2022, 6, 30, 0.0025),
    _rp(2022, 7, 1, 2022, 12, 31, 0.0125),
    _rp(2023, 1, 1, 2023, 6, 30, 0.0350),
    _rp(2023, 7, 1, 2023, 12, 31, 0.0500),
    _rp(2024, 1, 1, 2024, 6, 30, 0.0525),
    _rp(2024, 7, 1, 2024, 12, 31, 0.0525),
    _rp(2025, 1, 1, 2025, 6, 30, 0.0475),
    _rp(2025, 7, 1, 2025, 12, 31, 0.0425),
]

RATE_HISTORY_START = _RATE_HISTORY[0].effective_from
RATE_HISTORY_END = _RATE_HISTORY[-1].effective_to


def statutory_interest_rate(as_of: date) -> Optional[float]:
    """Correct LPCDCA statutory rate on `as_of`, or None outside the anchored
    2016-2025 history (fail closed -- never extrapolate an unanchored rate)."""
    for p in _RATE_HISTORY:
        if p.covers(as_of):
            return p.statutory_rate
    return None


# ---------------------------------------------------------------------------
# The correct obligation (the ANSWER KEY).
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class DebtObligation:
    """The CORRECT debt T&C the law requires for a customer of a given TRUE
    segment on a given date. This is the ground truth C11's applied terms are
    scored against."""
    terms_class: str                     # BUSINESS_TERMS | DOMESTIC_TERMS
    as_of: date
    statutory_interest_lawful: bool      # LPCDCA interest may be charged
    statutory_interest_rate: Optional[float]
    late_charge_lawful: bool             # a late-payment CHARGE may be levied
    payment_conditioned_tariff_lawful: bool
    basis: str

    def statutory_interest_due(self, arrears_gbp: float, days_overdue: int) -> float:
        """The correct statutory interest AMOUNT owed on `arrears_gbp` overdue
        `days_overdue` days (0.0 for a domestic account, or a business account
        outside the anchored rate history -- fail closed). Simple daily accrual
        on the annual statutory rate; determinism holds (pure)."""
        if not self.statutory_interest_lawful or self.statutory_interest_rate is None:
            return 0.0
        if arrears_gbp <= 0 or days_overdue <= 0:
            return 0.0
        return round(arrears_gbp * self.statutory_interest_rate * (days_overdue / 365.0), 2)


_BUSINESS_BASIS = (
    "Business (SME/I&C): LPCDCA 1998 statutory late-payment interest lawful "
    "(BoE base rate on the reference date + 8pts); late-payment charges lawful "
    "under commercial T&C; payment-conditioned tariff eligibility lawful."
)
_DOMESTIC_BASIS = (
    "Domestic: LPCDCA 1998 excludes consumer debt (no statutory interest); "
    "Ofgem SLC / Consumer Duty -- no domestic late-payment charges. "
    "DD-discount tariff eligibility lawful but fairness-constrained."
)


def correct_obligation(true_segment: object, as_of: date) -> DebtObligation:
    """The world's answer key: the CORRECT debt obligation for a customer of
    this TRUE segment on `as_of`. Business gets statutory interest + late
    charges; domestic gets neither; both may be on a (constrained) payment-
    conditioned tariff. Pure/deterministic."""
    if not isinstance(as_of, date):
        raise TypeError(f"as_of must be a date, got {type(as_of).__name__}")
    if is_business_segment(true_segment):
        return DebtObligation(
            terms_class=BUSINESS_TERMS,
            as_of=as_of,
            statutory_interest_lawful=True,
            statutory_interest_rate=statutory_interest_rate(as_of),
            late_charge_lawful=True,
            payment_conditioned_tariff_lawful=True,
            basis=_BUSINESS_BASIS,
        )
    return DebtObligation(
        terms_class=DOMESTIC_TERMS,
        as_of=as_of,
        statutory_interest_lawful=False,
        statutory_interest_rate=None,
        late_charge_lawful=False,
        payment_conditioned_tariff_lawful=True,
        basis=_DOMESTIC_BASIS,
    )


# ---------------------------------------------------------------------------
# The segment-OBSERVATION channel -- the WORLD decides both the customer's
# TRUE segment and what got RECORDED on the company's book (the wall: the
# company sees only the record). This is the SIM depth that creates the gap.
# ---------------------------------------------------------------------------

# ILLUSTRATIVE CURRICULUM CONSTANTS (R13), NOT sourced regulation -- flagged as
# such per the anchored-noise law. The DIRECTION is real and documented: the
# dominant real UK misclassification is a MICROBUSINESS recorded as / left on a
# DOMESTIC or deemed contract (Ofgem microbusiness-protection work repeatedly
# addresses microbusinesses wrongly treated as, or confused with, domestic
# customers). The reverse (a domestic account mislabelled business) is real but
# rarer. Large I&C accounts are heavily KYC'd and essentially never
# misclassified. The RATES below are a plausible illustrative severity ordering
# for the coupled scenario -- NOT tuned to hit any gap number (R12/R13), and
# marked here so a director can set them as curriculum later.
_MISCLASSIFY_SME_AS_DOMESTIC = 0.08     # microbusiness-on-domestic-contract
_MISCLASSIFY_DOMESTIC_AS_SME = 0.02     # reverse mislabel, rarer
_MISCLASSIFY_IANDC = 0.005              # large accounts ~always classified right

_OBSERVATION_SUBSTREAM = "w2_9_segment_observation"


def _u01(*parts: object) -> float:
    """Deterministic uniform(0,1) from a stable sha256 of the NAMED substream +
    parts (C-S2). Same inputs -> same draw everywhere; isolated from every
    other subsystem's RNG by the substream prefix."""
    key = ":".join(str(p) for p in (_OBSERVATION_SUBSTREAM, *parts))
    digest = hashlib.sha256(key.encode("utf-8")).digest()
    return int.from_bytes(digest[:8], "big") / float(1 << 64)


def observed_segment(true_segment: object, customer_id: object) -> str:
    """The segment label RECORDED on the company's account book for this
    customer -- what C11 acts on. Usually equals the true segment; with the
    illustrative misclassification rates above it is sometimes wrong (a
    microbusiness left on a domestic contract, etc). Deterministic per
    customer_id via the named observation substream (C-S2): the same customer
    is always mis/correctly recorded the same way on replay.

    Returns a label in the company's own vocabulary ('resi' / 'sme' / 'iandc')
    so it can be fed straight into C11.select_debt_terms unchanged."""
    key = _norm(true_segment)
    draw = _u01(customer_id)
    if key in _DOMESTIC_LABELS:
        return "sme" if draw < _MISCLASSIFY_DOMESTIC_AS_SME else "resi"
    if key in _SME_LABELS:
        return "resi" if draw < _MISCLASSIFY_SME_AS_DOMESTIC else "sme"
    if key in _IANDC_LABELS:
        # A misrecorded I&C is (rarely) dropped to domestic.
        return "resi" if draw < _MISCLASSIFY_IANDC else "iandc"
    raise ValueError(f"unrecognised customer segment: {true_segment!r}")
