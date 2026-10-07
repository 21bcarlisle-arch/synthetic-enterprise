> **Discharged 2026-10-06 as a duplicate.** The text is the director's 2026-10-06T03:35Z console message, sent again by NTFY at 20:44Z (`FlNOHLX2fXfH`). Both parts had already landed: the knowledge and the toggles in `fbe24afea`, and the 4,000-founder book in `b8808f4ad` (the cost curve was re-measured in `da6d70053`). The one open tail, re-pricing `SETTLEMENT_CUSTOMER_YEAR_BUDGET` (1,050) from the runner's fixed-code peak, is a queued continuation. The director was told by NTFY (`kvQwQkkmf42r`).


> **Correction, 2026-10-07: the scale half was NOT done, and this note overstated it.** `b8808f4ad` made a
> book of 4,000 founders *runnable*, in a ONE-YEAR run (1,890 customer-years). The live book still
> launches at the director's 80 founders (`docs/design/FOUNDER_BOOK.yaml`) and settles about 280
> accounts by 2025, because `PROSPECTS_PER_YEAR` (400) and the settlement budget (now 1,750
> customer-years, re-priced in `358d59a42`) both bind. The knowledge half stands. The scale half is
> reopened as work: a holdout able to see a two-point churn move needs about 3,000-6,000 decisions per
> arm, roughly 10,000 settled customer-years, about 27 GB at today's 2.7 MB each. The store has to get
> leaner before the dials can move. The director caught this ("I can't see any work on it yet").

# [DIRECTOR-STEER] — Knowledge on three areas, and a book of a few thousand (2026-10-07)

**Type:** [STEER — work direction, not canon. Severity: LATENT. Staged by the advisor because the director's console session is unreachable; the same text arrived by NTFY at 2026-10-06 20:44Z and was queued for a seat that may not exist. If it has already been acted on, discharge this as a duplicate.]

**Knowledge:** none — a work steer; the knowledge it asks for lands on the relevant area pages.

Don't stop what you're doing — take this as the next work after the current piece. It supersedes the "re-check the toggles" part of the director's message of 2026-10-06.

## 1. Proper knowledge work on three areas

Back-billing and liability, read access and theft duties, and bad debt provisioning each deserve proper knowledge work, not a re-check of a toggle value. Treat them like the step-1 areas: sources, what's established, what isn't, written up as knowledge. Then set the toggles from what you find.

The director's practitioner starting points, not the answer:
- **Back-billing and moves.** Dividing total change-of-tenancy debt by moves says nothing about who is liable — the incoming occupier, the landlord for void periods — or what the 12-month back-billing limit lets a supplier recover.
- **Reads.** MHHS may set a minimum read frequency for non-smart meters — check what it actually requires. No access clusters in a minority of homes for years, and long-term no access triggers theft and safety duties, including investigating and, if necessary, forcing access. Model the distribution, not an average rate.
- **Debt.** Writing a debt off means accepting — sometimes agreeing with the customer — that it won't be collected. Old, low-value debt sells for very little. Don't create unrealistic profit: default recovery after write-off to near zero, with any debt sale at realistic low prices. What matters for pricing and customer value is provisioning — how debt of each age and risk profile turns into write-off — and CLV and pricing must read the same assumptions.

## 2. A book of a few thousand customers

Holdout groups are useless at about 80 decisions because the sample is too small. Measuring whether an offer moved churn by a couple of points takes thousands of decisions per group, so the book needs to reach a few thousand customers without the machine falling over.

The known constraints are ours, not physics: about 4.3 MB per customer-year settled, the simulation allowed a quarter of the machine's memory, and prospects capped at 400 a year. Find out what actually breaks at a few thousand before choosing a fix. Possible levers — a leaner store for each customer's half-hourly data, a bigger memory share, experiments run on the cheap per-decision method while full settlement stays for calibration — but measure first and say what you'd do.

— Director steer, 2026-10-07, staged by the advisor.
