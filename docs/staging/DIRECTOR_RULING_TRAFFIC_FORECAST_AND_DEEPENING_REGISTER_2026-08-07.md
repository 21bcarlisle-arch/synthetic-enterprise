# [DIRECTOR-RULING] — Traffic forecast + deepening register (2026-08-07)

**Type:** [DECISION — binding design input]. Ratified by the director in conversation 2026-08-07. This is the load section TARGET_DESIGN.md (ARCHITECTED-OUT §2) consumes, and the system-level "bound" the Birth-Certificate law was missing (retro, hardening 1). From today, the write-time gate's question for any load-bearing choice is: **"does this die at 10⁵?"** — and the 10k probe (data-architecture review) now has expected values to confirm or refute. Orders of magnitude only, per day unless marked. See-and-correct applies: the worker consumes and files this without approval loops; the director corrects retrospectively.

## Ratified posture (the three calls)
1. **Preclude nothing at 10⁶ customers; engineer for 10⁵; probe at 10⁴.** Seams must survive the design ceiling; internals need only the current rung.
2. **Go-live book ≈ 10³** — the Epoch-5 planning assumption.
3. **Smart penetration ≥90% at scale** — personalisation-led abatement requires HH data; the reads artery is designed near-all-smart.

## Table A — the arteries (GL = go-live 10³ custs · BE = break-even 10⁵ · DC = design ceiling 10⁶)

| Artery | GL | BE | DC | Driver |
|---|---|---|---|---|
| Customer accounts (total) | 10³ | 10⁵ | 10⁶ | dual fuel ⇒ meters ≈1.5× |
| Meter readings in /day | 10⁵ | 10⁷ | 10⁸ | 48 HH × meters, near-all-smart |
| Settlement rows /day | 10⁵ | 10⁷–10⁸ | 10⁹ | reads × MHHS rerun versions |
| Bills issued /day | 10¹–10² | 10³–10⁴ | 10⁴–10⁵ | monthly cycle |
| Payment events /day | 10² | 10⁴ | 10⁵ | collections + 1–3% failure tail |
| Customer interactions /day | 10¹ | 10³–10⁴ | 10⁴–10⁵ | 2–6 contacts/cust/yr; digital ×10 |
| Market data in /day | 10⁴–10⁵ | flat | flat | book-independent |
| Event-log writes /day (the spine) | 10⁵–10⁶ | 10⁸ | 10⁹ | sum of all, × amendments |

## Table B — the deepening register (knowingly basic; seam built wide NOW, internals stay simple)

| Subsystem | Today, honestly | Coming | Seam to build wide |
|---|---|---|---|
| Tariff engine | flat/simple SVT+fix | ToU, dynamic, EV/solar/battery permutations | price-per-period request interface |
| Payments | DD-centric | prepay/PAYG estate, Faster Payments, full failure taxonomy | payment-event contract |
| Metering ingest | daily synthetic pull | DUIS-shaped SRVs, missing-data physics | typed flow adapter |
| Settlement | single simplified pass | MHHS multi-run true-ups, three clocks | settlement-statement events |
| Customer model | archetypes | rich life-event streams | event-stream schema |
| Hedging/forward | parametric curve | term-structure trading; ECVN API from 2027 | forward-curve provider interface |
| Collections | basic ladder | full journey + SLC27 physics | debt-event contract |
| Switching CoT/CoS | minimal | REC message flows | switching-message adapter |

## Binding effects (worker sequences; register in the map under the naming law)
TARGET_DESIGN consumes both tables as its load section. The write-time gate adds the scale question for load-bearing seams. KNIFE's tie-breaker — *the graph proposes, the forecast disposes* — now has a forecast to dispose with. Deepening-register rows are interface commitments, not implementations: building any row's internals ahead of need remains the ghost-suburb failure, not compliance.

— Ruled 2026-08-07; staged by the advisor. Revisable only by a later director ruling.
