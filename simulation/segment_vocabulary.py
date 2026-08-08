"""W2_sme_segment_case_normalisation -- the canonical market-segment
vocabulary, and the single normaliser every segment test must route through.

WHY THIS MODULE EXISTS (the defect it closes)
---------------------------------------------
`saas/customers.py` stores segments in their CANONICAL spelling -- "resi",
"SME", "I&C" -- and those strings travel unchanged onto every bill record as
`bill["segment"]`. Two sim-side modules tested them case-SENSITIVELY against
lower-case literals:

  simulation/arrears_engine.payment_method:      `segment == "sme"`
  simulation/payment_behaviour_source:           `segment in ("ic", "I&C", "sme")`

so a real SME bill (segment "SME") matched NEITHER, and C5/C6 -- the two
microbusiness accounts in the population -- were silently routed through the
RESIDENTIAL payment-channel model: billed as if they were households.

That is one instance of a CLASS: any segment comparison anywhere in the sim
that spells a segment in a non-canonical case is a silent mis-route, and it
fails silently (a customer takes the wrong branch; nothing raises). R10 says
an absurdity-class defect may not be closed with an instance fix, so this
module + `tools/segment_case_guard.py` close the class:

  - `normalise_segment()` is the ONLY sanctioned way to test a segment, and it
    accepts every spelling that has ever reached this code.
  - the guard AST-scans `simulation/` and FAILS on any segment string literal
    that is not in canonical form, so a new `== "sme"` written next year is
    caught at commit time rather than by a customer being mis-billed.

NOT TO BE CONFUSED WITH `simulation/segments.py`
------------------------------------------------
That module is the population-COHORT vocabulary ("resi_standard",
"sme_smart", "gas_resi") -- a different axis entirely. This module is the
MARKET segment recorded on a customer/bill record. The two are deliberately
kept apart, and `normalise_segment()` REJECTS a cohort id rather than guessing
that "sme_standard" means "SME": the collision between the two vocabularies is
precisely the kind of silent coercion this module exists to prevent.

CANONICAL SPELLINGS ARE NOT THIS MODULE'S CHOICE
------------------------------------------------
They are whatever `saas/customers.py` actually stores, because that is the
system of record the bills are built from -- measured, not decided here:
`Counter({'resi': 11, 'I&C': 5, 'SME': 2})`. `saas/smart_meter_rollout.py`
independently spells the corporate segment "IC" (no ampersand), and
`arrears_engine` accepted a lower-case "ic", so both are accepted ALIASES that
normalise onto "I&C" -- an alias table is the honest representation of a
vocabulary that really did drift, and collapsing it silently would just move
the mis-route somewhere else.

WALL DISCIPLINE (.claude/rules/epistemic-wall-sim.md)
-----------------------------------------------------
Pure vocabulary. Imports nothing from `company.*` or `saas.*` -- the canonical
spellings are recorded here as literals precisely so this module does not have
to reach across the wall to learn them.
"""
from __future__ import annotations

#: The canonical spelling of every market segment, exactly as
#: `saas/customers.py` stores it on the customer record (and therefore exactly
#: as it arrives on `bill["segment"]`).
RESIDENTIAL = "resi"
SME = "SME"
INDUSTRIAL_AND_COMMERCIAL = "I&C"

CANONICAL_SEGMENTS = (RESIDENTIAL, SME, INDUSTRIAL_AND_COMMERCIAL)

#: Every spelling that has ever reached sim-side segment code, mapped to its
#: canonical form. Keys are casefolded: lookup is case-insensitive by
#: construction, so "SME"/"sme"/"Sme" all resolve without needing an entry
#: each. The non-obvious entries are the ones that caused real drift:
#: "ic" (arrears_engine's own lower-case alias) and "IC" (the spelling
#: `saas/smart_meter_rollout.Segment` declares).
_ALIASES = {
    "resi": RESIDENTIAL,
    "residential": RESIDENTIAL,
    "domestic": RESIDENTIAL,
    "sme": SME,
    "microbusiness": SME,
    "micro": SME,
    "i&c": INDUSTRIAL_AND_COMMERCIAL,
    "ic": INDUSTRIAL_AND_COMMERCIAL,
    "i and c": INDUSTRIAL_AND_COMMERCIAL,
}

#: The segments that are BUSINESS customers -- i.e. billed on a corporate
#: payment rail (BACS/CHAPS) rather than a household one. SME is in here and
#: I&C is in here, but they do NOT share an outcome model (see
#: `simulation/sme_payment_behaviour.py` for why conflating them deletes bad
#: debt).
BUSINESS_SEGMENTS = (SME, INDUSTRIAL_AND_COMMERCIAL)


class UnknownSegmentError(ValueError):
    """Raised for a segment string that is not a known alias.

    Deliberately an ERROR and not a silent fallback to "resi": falling back is
    exactly the failure mode this module exists to remove -- an unrecognised
    business segment quietly becoming a household is how C5/C6 were mis-billed
    for the entire history without anything ever going red.
    """


def normalise_segment(segment, *, default: str | None = RESIDENTIAL) -> str:
    """Return the canonical spelling of `segment`.

    `default` is used ONLY for a genuinely absent segment (None or blank) --
    the long-standing convention at every call site, which reads
    `bill.get("segment", "resi")`. Pass `default=None` to make absence an
    error too.

    A PRESENT-but-unrecognised segment always raises `UnknownSegmentError`,
    whatever `default` is: absent and wrong are different, and only the first
    has a defensible default.
    """
    if segment is None or (isinstance(segment, str) and not segment.strip()):
        if default is None:
            raise UnknownSegmentError("segment is absent and no default was allowed")
        return default
    if not isinstance(segment, str):
        raise UnknownSegmentError("segment must be a string, got %r" % (segment,))
    key = segment.strip().casefold()
    try:
        return _ALIASES[key]
    except KeyError:
        raise UnknownSegmentError(
            "unknown segment %r -- known aliases: %s"
            % (segment, ", ".join(sorted(_ALIASES)))
        ) from None


def is_business(segment) -> bool:
    """True for a segment billed on a corporate payment rail (SME or I&C)."""
    return normalise_segment(segment) in BUSINESS_SEGMENTS
