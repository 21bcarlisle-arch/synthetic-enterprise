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

| Founders | Live book | Cust-yrs | Arrears stock | Debtor moves / decade | Memory | Wall |
|---|---|---|---|---|---|---|
| 80 (now) | ~280 | ~1,750 | ~11 | ~6 | ~3.6 GB | ~0.6-0.9 h |
| 400 | ~600 | ~5,000 | ~24 | ~17 | ~7.3 GB | ~1.8-2.6 h |
| 1,000 | ~1,200 | ~10,000 | ~48 | ~34 | ~12.8 GB | ~3.7-5.3 h |

Memory uses the founders-only slope at current code (1.11 MB per settled customer-year plus a ~1.7 GB
base); wall uses 1.9 s per customer-year, less the measured 15-40% from the parallel trace build
(9288dea24). These are extrapolations from small runs, not measured at these sizes.

## Recommendation

1. **Keep 80 founders until home moves are switched on.** Until then the bigger book buys only the
   arrears stock, and provisioning by age band can be studied on the coin-drawn decision set.
2. **When moves switch on, raise to 400 founders (ceiling 120 -> 500)** for the periodic end-to-end
   run and book-level provisioning: about 24 accounts in arrears at a time and about 17 debtor moves
   a decade, at about 7 GB and 2-2.5 h. That run states its case under the new over-an-hour rule.
3. **Leave the prospect cap at 400.** It binds in four years of ten, but the rare-event and
   book-money questions are carried by founders, and raising it eases the world (R13).
4. **Do not size for theft, voids or vulnerability yet.** Each needs its generator first; size
   then, from its own rate.

Reversible: both are values in curriculum files. The seat carries on with the run review either way.
