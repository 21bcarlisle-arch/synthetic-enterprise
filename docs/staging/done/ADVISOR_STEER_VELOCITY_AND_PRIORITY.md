# ADVISOR_STEER — enforce fan-out, fix priority inversion (P1, corrective)

**Staged:** 2026-07-12 by advisor, director-prompted ("is it parallel? is it
prioritising well? stuck on trivial requests?"). Honest audit says: serial not
parallel; one real priority inversion; trivial items flattened into the deep
queue by the advisor's own batched staging. Corrections:

## 1. Fan-out is not happening — enforce it
SUNDAY_WIDE mandated 5-10 concurrent subagents as the DEFAULT on non-build
turns; observed behaviour since the 05:13 C-suite walk is serial single-doc
consumption ~7 min apart. From now, EVERY non-build turn launches a parallel
batch (discovery, hardening, red-team, charter-deepening, ideation) ALONGSIDE
its main action, and REPORTS the fan-out count in each digest. A serial turn
must state why in one line. This is the standing instruction; stop reverting
to serial.

## 2. Priority inversion — the SC fix outranks ALL cosmetic work
Published net has been frozen at £1,524,058 across every auto-process run
since 2026-07-11. The standing-charge double-charge fix (delegated Fri
evening) has NOT landed in published figures. This is historical-money
correctness and it currently sits BEHIND footer/crawler/cosmetic items.
Re-rank: the SC fix (and confirming its published impact) is the top build
priority now, above all site-polish and all P2/P3 registration. Report its
status explicitly in the next digest: landed or not, and the before/after net.

## 3. Stop interleaving trivial with deep (advisor's error, agent's fix)
The footer/entity/crawler items were staged in the same batch as affordability
physics and governance; they are Tier-2 cosmetic and must NOT consume a
priority slot ahead of P1 mechanism work. Batch ALL low-effort site-cosmetic
items and run them together in ONE fan-out lane, not interleaved one-per-turn
with deep work. Deep build work (SC fix, M2, affordability thin-start) runs in
the hot lane uninterrupted.

## 4. Auto-process noise
Three identical-net auto-process runs committed within 30 minutes (06:34/
06:47/07:00, all £1,524,058). The change-detection SKIP gate is meant to
suppress no-delta republishes — verify it's actually firing; if these are
re-running and re-committing identical output, that's wasted cycles. R4 the
gate.

## DoD
Fan-out counts in digests; SC-fix status + before/after net reported next
digest; cosmetic items batched into one lane; auto-process gate verified.
One digest line.
