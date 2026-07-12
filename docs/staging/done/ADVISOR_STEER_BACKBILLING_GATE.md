# ADVISOR_STEER — D3 vs the back-billing law + oracle jurisdiction discipline (P1)

**Staged:** 2026-07-12 by advisor after reviewing REGULATORY_RULES_AS_FIDELITY_ORACLE
(director-decided; correctly archived). The oracle's #1 finding collides with
last night's build — resolve before D3's L3 claim stands.

## 1. Verify D3 against SLC 21BA — immediately, before further M2 build
D3 catch-up rebilling reached L3 overnight. The oracle establishes the law it
must obey: charges for energy consumed >12 months before an ACCURATE bill was
issued cannot be recovered (domestic + microbusiness analogue); the clock
anchors on the accurate-bill date; exceptions require CUSTOMER FAULT
(obstruction/tamper/theft — and failing to submit reads is explicitly NOT
fault, the estimation risk is the supplier's); the unrecoverable tranche is a
WRITE-OFF — a real P&L event (write-off machinery exists since the C1 fix).
Non-micro business: 6-year Limitation Act instead.
Check D3 now: does it enforce the cap, the anchor, the fault gate, and emit
the write-off event? If ANY are missing: (a) it is a compliance gap in a live
mechanism — Tier-1-adjacent, fix before other M2 work; (b) D3's level_current
reverts to 2 until the fix passes the loop (an L3 "fails like reality" claim
cannot exclude the single most litigated failure of its own domain); (c) add
the cap as a pre-bill Tier-1 invariant (a catch-up bill breaching 12 months
without a recorded fault attribution is HELD). Report which of the four
elements existed before this steer — honestly.

## 2. Jurisdiction discipline for the oracle (make it operational)
Only UK rules may become live invariants or company logic NOW. AU/FR/BE
content routes to: the portability design-constraints register (as lenses)
and the domain artefact library (tagged, for Epoch-3+). A non-UK rule firing
as a validator on UK output is a false oracle — add a jurisdiction field to
the invariants library schema so this is structural, not remembered.

## 3. Process note (record, no action)
The oracle doc arrived via a second staging pen (director's other chat, by
accident, acknowledged). Standing convention restated: other windows output
TEXT; this window stages. The doc's quality is not in question — its top
finding is why this steer exists.
