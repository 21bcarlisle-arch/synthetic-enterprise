# ADVISOR_STEER — the 425-bill estimation gap: it's D3, build it in M2 (Tier 2)

**Staged:** 2026-07-11 by advisor, answering the digest's "your call on
priority" so nothing waits silently.

## Decision
The estimated-bills-charged-on-truth finding (425/1588 historical bills) is
NOT a standalone patch. It is precisely **D3 — estimated billing & catch-up
rebilling — M2's next movement per THE_VALUE_CYCLE_FRAMING**, and the epoch
exists to fix exactly this class. Sequence: continue M2 as framed (rails sim
landed -> estimated billing on EAC/profile -> actual-read catch-up rebilling
within back-billing law -> settlement timetable -> DD cash engine). The
mechanism ships forward-looking first; the 425 historical bills are
rederived through it as part of M4's full-history replay (they already sit
under the PROVISIONAL banner — no emergency relabel needed, but add one line
to the Simplified register naming this gap explicitly until M4 clears it).

## Also
- Good adjudication on the WebFetch staleness artifact and the Cloudflare
  purge gap — the purge fix is a class kill for the week's staleness misery;
  add cache-purge coverage to the SURFACE_FRESHNESS invariant set so a
  future hardcoded-path regression fails a test, not the director's patience.
- The pixel-check DoD on the two in_progress docs: the director is doing the
  visual verification himself tonight; treat his confirmation (via any
  channel) as the pixel evidence and archive on receipt.
