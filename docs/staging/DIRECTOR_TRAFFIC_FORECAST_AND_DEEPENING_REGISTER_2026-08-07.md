# [DIRECTOR-RULING] — Traffic forecast + deepening register (2026-08-07)

**Type:** [DECISION]. Advisor-drafted, director-ratified in conversation 2026-08-07 ("all fine" — no corrections). This is the ARCHITECTED-OUT programme's director-authored input to `TARGET_DESIGN.md`: the Birth-Certificate "bound" applied at system level. Orders of magnitude only, by design — re-ratified at each epoch boundary. See-and-correct applies; nothing here waits on approval.

## The three ruled calls
1. **Design posture:** preclude nothing at 10⁶ customers, engineer for 10⁵, probe at 10⁴.
2. **Go-live book:** ~10³ customers is the Epoch-5 planning assumption.
3. **Smart penetration at scale:** ≥90% — personalisation-led abatement demands HH data; the reads artery is designed near-all-smart.

## Table A — the arteries (per day unless marked; GL = go-live ~10³ custs, BE = break-even ~10⁵, DC = design ceiling ~10⁶)

| Artery | GL | BE | DC | Driver |
|---|---|---|---|---|
| Customer accounts (total) | 10³ | 10⁵ | 10⁶ | dual fuel ⇒ meters ≈1.5× |
| Meter readings in | 10⁵ | 10⁷ | 10⁸ | 48 HH × meters, near-all-smart |
| Settlement rows | 10⁵ | 10⁷–10⁸ | 10⁹ | reads × MHHS rerun versions |
| Bills issued | 10¹–10² | 10³–10⁴ | 10⁴–10⁵ | monthly cycle |
| Payment events | 10² | 10⁴ | 10⁵ | collections + 1–3% failures |
| Customer interactions | 10¹ | 10³–10⁴ | 10⁴–10⁵ | 2–6 contacts/cust/yr + digital ×10 |
| Market data in | 10⁴–10⁵ | same | same | flat — book-independent |
| Event-log writes (the spine) | 10⁵–10⁶ | 10⁸ | 10⁹ | sum of all, × amendments |

## Table B — the deepening register (knowingly basic today; the SEAM is built wide now, internals stay simple)

| Subsystem | Today, honestly | Coming | Seam to build wide |
|---|---|---|---|
| Tariff engine | flat/simple SVT+fix | ToU, dynamic, EV/solar/battery permutations | price-per-period request interface |
| Payments | DD-centric | prepay/PAYG estate, Faster Payments, full failure taxonomy | payment-event contract |
| Metering ingest | daily synthetic pull | DUIS-shaped SRVs, missing-data physics | typed flow adapter |
| Settlement | single simplified pass | MHHS multi-run true-ups on three clocks | settlement-statement events |
| Customer model | archetypes | rich life-event streams | event-stream schema |
| Hedging/forward | parametric curve | real term-structure trading, ECVN API 2027 | forward-curve provider interface |
| Collections | basic ladder | full journey + SLC27 physics | debt-event contract |
| Switching CoT/CoS | minimal | REC message flows | switching-message adapter |

## What this changes at write time
- The write-time gate's standing question gains its numbers: **"does this choice die at 10⁵?"** must be answerable for anything touching an artery above.
- The 10⁴ scale probe (`ADVISOR_REVIEW_DATA_ARCHITECTURE_AND_SCALE_PROBE`) now has expected values — its prediction register confirms or refutes Table A, and a surprise ordering remains the most valuable outcome.
- KNIFE's tie-breaker is now fully armed: the graph proposes, THIS forecast disposes.
- The worker folds this verbatim into `TARGET_DESIGN.md` when drafting it; deviations are findings, not edits.

— Ruled 2026-08-07; falsifiable by probe; re-ratified at epoch close.
