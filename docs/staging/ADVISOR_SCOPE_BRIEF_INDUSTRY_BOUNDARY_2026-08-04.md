# [ADVISOR-SCOPE-BRIEF] — The industry boundary: which counterparties a GB supplier must talk to, and what each one does to it (2026-08-04)

**Type:** [SCOPE BRIEF]. Written from the domain before consulting the repository. **Assemble against it; the delta is the finding.** Refute freely where the code already covers something.

## 0. Why this before the behaviours

The director's call, and it is the better one: **simulate the boundary first, and the behaviours arrive through it.**

Three reasons it is stronger than modelling behaviours directly. The blindfold becomes **structural** — if the company can only reach the world through typed adapters, it *cannot* see simulation internals, rather than being trusted not to. The messiness arrives **as a consequence** rather than being bolted on — late reads, failed switches, debt on arrival are properties of the counterparty, not features to remember to add. And per canon, **the wall is the go-live seam**: an adapter set with a simulated implementation on one side is one substitution away from a real one.

**The design principle:** model **what each counterparty does to the company** — what it sends, when, how late, how wrong, and what it charges — **not how the counterparty works internally.** File formats and message schemas are not the point; consequences are.

## 1. The counterparty set (the enumeration is the deliverable)

A GB domestic supplier is defined by the parties it must deal with. The list is finite.

**REGISTRATION AND SWITCHING — the Central Switching Service (CSS)**, under the Retail Energy Code, run via the DCC. Since Faster Switching, both fuels register through one central service. **What it does to the company:** grants or refuses ownership of a meter point; imposes a defined switch timetable; carries objections; produces erroneous transfers that must be reversed; and notifies losses as well as gains. **Also:** the Gas Enquiry Service and equivalent electricity enquiry services provide pre-switch validation — what the company can *know* about a prospect before signing them. That is an epistemic wall in its own right.

**SMART METER DATA — the DCC**, over the specified user interface. **What it does:** delivers half-hourly consumption for smart meters and only smart meters; fails, delays, and returns nothing for meters that are unreachable; requires the meter to have been commissioned and migrated. **Consequence:** *the company's ability to personalise is a function of which meters answer.* That is the single most mission-critical property on this list.

**NON-SMART METER DATA — MPAS/MPRS, data collectors and aggregators.** Estimated reads, actual reads arriving late, profile-class-based settlement. **Consequence:** for a large part of the book, consumption is an estimate corrected months later.

**SETTLEMENT — Elexon for electricity, Xoserve/UK Link for gas.** **What it does:** tells the company months later what it actually consumed and owes, in successive reconciliation runs; charges imbalance at a price unknown until after the period; corrects earlier runs. **Consequence:** the P&L is provisional for months. Note **Market-wide Half-Hourly Settlement** is the direction of travel and changes what settlement even means for domestic customers.

**NETWORKS — DNOs and the transmission operator.** Distribution and transmission charges, published in advance, changing annually, varying by region and time band. **Consequence:** a large, non-commodity, regionally-varying cost the company must recover in tariffs.

**PAYMENTS — Bacs.** Direct debit collection, mandate setup, and **return codes** (unpaid, account closed, mandate cancelled) arriving days after the attempt. **Consequence:** cash is not certain when billed, and failure is discovered late. The existing detection-latency work sits exactly here.

**WHOLESALE — exchanges, brokers, the clearing house.** Prices, tradeable products with real liquidity limits, bid-offer spread, and **margin calls when the position moves.** Already partly modelled; the credit and collateral side is the exposed part.

**REGULATORY — Ofgem.** The price cap in advance, licence conditions, data requests, and enforcement. **Consequence:** a ceiling on revenue and a set of duties that constrain collections and vulnerability handling.

**SCHEMES AND OBLIGATIONS — the Warm Home Discount, the Energy Company Obligation, renewables obligations and certificates, the low-carbon contracts body.** **Consequence:** obligations sized to the customer base, paid whether or not the company planned for them, and **the failure mode that mutualised costs in 2021.**

**DEBT AND CREDIT — collection agencies, credit reference agencies.** Already partly present in the arrears work.

## 2. What each adapter must express

For every counterparty, the interface should carry — because these are what actually bite:

- **What it sends, and when** — including the lag between event and notification.
- **What it can refuse**, and why: objections, rejections, unreachable meters, invalid requests.
- **What it gets wrong**: erroneous transfers, estimated reads later corrected, settlement re-runs that move the answer.
- **What it charges**, and whether the amount is known in advance.
- **What the company may ask it** — the query surface, which is the boundary of what the company can know.

**Every adapter must be able to fail, be late, and be wrong.** An interface that always answers correctly is not a wall, it is a convenience — and it will make the company look far better than it is.

## 3. What this makes possible, in order

Once the boundary exists, behaviours stop being separate builds: **change of tenancy** becomes a registration event with debt attached; **erroneous transfers** become a refusal path; **meter estate** becomes which adapters answer; **prepayment** becomes a payment-and-metering counterparty rather than a bolt-on; and **go-live** becomes swapping one implementation for another.

## 4. Disqualification battery

1. Any adapter that cannot fail, delay or return an error.
2. The company reading anything not delivered through an adapter.
3. Settlement modelled as a single figure rather than successive runs that move.
4. Switching without objections, refusals or erroneous transfers.
5. Meter data that always arrives for every customer.
6. Payments treated as certain at the point of billing.
7. Network and policy costs absent or modelled as a flat national number.
8. No pre-switch enquiry limit — the company knowing things about prospects it could not know.
9. Obligations and scheme costs missing.
10. Adapters coupled to simulation internals rather than to a typed contract.

**Sources:** Ofgem Switching Programme end-to-end solution architecture and CSS service definition; Retail Energy Code / RECCo API documentation via Xoserve (supply point switching, supply point enquiry, meter asset enquiry); DCC switching and smart-metering material; Elexon MHHS programme glossary and settlement documentation.

— Advisor scope brief, written before consulting the repository, 2026-08-04.
