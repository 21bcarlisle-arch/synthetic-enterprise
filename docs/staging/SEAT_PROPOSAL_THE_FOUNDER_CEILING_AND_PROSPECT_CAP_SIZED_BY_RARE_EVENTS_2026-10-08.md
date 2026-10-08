**Severity:** LATENT · **Lane:** W2_customer_generator · **Epoch:** unassigned · **Atom:** `unminted`

# SEAT PROPOSAL — the founder ceiling and the prospect cap, sized by rare events and book-level money (2026-10-08)

**For the director. Both numbers are yours** (`docs/design/FOUNDER_BOOK.yaml` `founder_accounts` 80,
ceiling `max_founder_accounts` 120; `simulation/net_new_acquisition.py` `PROSPECTS_PER_YEAR` 400).
Sized against the questions you named, not against scale.

## What a bigger book can buy today

| Event | In the world now? | Customer-years (or accounts) for ~30 events |
|---|---|---|
| Arrears at a point in time (Ofgem Q2 2026: 4.0% elec) | **On** | 750 accounts |
| Persistent long-unread meter (q2 toggle 1%; assumes about half the book read-exposed) | **On** | ~6,000 accounts |
| Home move (EHS 2024-25 mix, about 8.5%/yr) | **Off** (`home_moves_activation.json`) | 353 cust-yrs |
| Debtor moving home (4% × 8.5%) | Off (needs moves) | ~8,800 cust-yrs |
| Theft detected (q6: 1% × 5.8%/yr) | **No generator** | ~52,000 cust-yrs |
| Void after move-out | **No generator** (q1 void toggle is a GAP) | — |
| Vulnerable customer in winter (PSR 13%, 2016) | **Not drawn**: PSR is rule-based | — |

Three of the five rare events cannot appear at any book size because nothing generates them, and a
fourth is switched off. Theft needs about 52,000 customer-years for 30 detections, which no settled
book on this box reaches, so it belongs to a premise-level study in the minutes tier.

## The menu

| Founders | Live book | Cust-yrs (committed) | Arrears stock | Debtor moves / decade | Memory, as first written | **Memory, corrected** | Wall, as first written | **Wall, corrected** |
|---|---|---|---|---|---|---|---|---|
| 80 (now) | ~280 | ~1,750 | ~11 | ~6 | ~3.6 GB | **~3.3 GB** (production measures 3.3-4.0) | ~0.6-0.9 h | **~0.7 h** (production 0.65-0.74) |
| 400 | ~600 | ~5,000 | ~24 | ~17 | ~7.3 GB | **~5.1-5.5 GB** | ~1.8-2.6 h | **~1.5 h** |
| 1,000 | ~1,200 | ~10,000 | ~48 | ~34 | ~12.8 GB | **~7.2-8.1 GB** | ~3.7-5.3 h | **~2.4 h** |

*As first written:* memory used the founders-only slope (1.11 MB per settled customer-year plus a
~1.7 GB base), and wall used 1.9 s per customer-year less 15-40% for the parallel trace build
(9288dea24).

**Corrected 2026-10-08, and which slope it uses.** A second document on this subject,
`SEAT_FINDING_WHAT_STOPS_THE_SETTLED_BOOK_REACHING_THOUSANDS_2026-10-08.md`, priced the live path at
2.69-3.06 MB/cy. On that slope this table would read ~15.0 GB at 400 and ~29.4 GB at 1,000. **That
slope is old code.** It was taken at `06b7c821a`, before the trace became arrays. Re-measured at
`20719d272` on two small runs (same seed, full window), a campaign customer-year costs 1.22 MB per
settled cy and a founder's ~1.02. **This table now uses both measured slopes, each on its own share of
the book.** The campaign share matters little, because the two slopes are close. What changed the
figures is a **unit error in the first version**: the 1.11 slope is per *settled* year, and it was
multiplied by *committed* years. Founders commit ~2× what they settle (80 founders commit 758.6 to the
2026 horizon and settle 384.6, because they churn), while a campaign win commits about what it settles.
So, per row: founder settled cy = founders × 4.81, at 1.02; campaign committed = Cust-yrs − founders ×
9.48, settled × 1.05, at 1.22; base 1,616 MB (the 80-founder run's 2,009 MB peak less its founders'
share). The low end of each range uses those two slopes; the high end prices founders at 1.22 too. The
80 row lands on production's own measurement, which neither the first version nor the old slope
did. **Still an extrapolation:** it assumes founders at 400 or 1,000 churn as they do at 80. If they
churned not at all, the ceiling is the first version's figure again (~7.8 GB and ~13.8 GB at 1.22).
Wall: 1.07 s per settled cy plus ~150 s, measured with two runs sharing the box, scaled ×1.5 to
production's own 2,332-2,672 s at 1,750.

**A precondition this table does not show:** the budget counts the founders' own committed years. At
400 founders they commit ~3,793 alone, above today's `SETTLEMENT_CUSTOMER_YEAR_BUDGET` of 1,750. Unless
the budget rises with the ceiling (~5,000 for this row), the campaign admits no wins at all.

## Recommendation

1. **Keep 80 founders until home moves are switched on.** Until then the bigger book buys only the
   arrears stock, and provisioning by age band can be studied on the coin-drawn decision set.
2. **When moves switch on, raise to 400 founders (ceiling 120 -> 500)** for the periodic end-to-end
   run and book-level provisioning: about 24 accounts in arrears at a time and about 17 debtor moves
   a decade, at about 7 GB and 2-2.5 h *[corrected: ~5.1-5.5 GB and ~1.5 h, with the settlement budget raised to
   ~5,000 alongside the ceiling; see the table note]*. That run states its case under the new over-an-hour rule.
3. **Leave the prospect cap at 400.** It binds in four years of ten, but the rare-event and
   book-money questions are carried by founders, and raising it eases the world (R13).
4. **Do not size for theft, voids or vulnerability yet.** Each needs its generator first; size
   then, from its own rate.

Reversible: both are values in curriculum files. The seat carries on with the run review either way.
