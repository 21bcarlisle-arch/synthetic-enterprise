**Severity:** LATENT · **Lane:** D_billing_metering · **Epoch:** unassigned · **Atom:** `unminted`

# [DIRECTOR-STEER] Front-line gaps: knowledge first, then build (2026-11-10)

**Type:** [STEER] — knowledge work, queued by the priority order. Build nothing until its knowledge has landed.

**The director's words, from chat on Tue 10 Nov (GMT):**

- 06:42: "Do we, the SIM or th me supplier, have all the processes and issues it. This is a great source of real world issues and situations"
- 07:32: "So want are the gaps, which ones should we close?"
- 07:34: "Paper versus paperless is UK thing too. Bring that into stage 2"
- 07:34: "Also, marketing permission is a key thing to manage too. Legitimate interest. This is key for cross sale"
- 07:35: "It should produce knowledge for each of these first"

The item list below is the advisor's proposal, which the director shaped with the messages above. Under K8 and G9, any item the knowledge shows to be wrong or unimportant is closed on the seat's own recommendation.

**Where this came from.** The director and the advisor compared the repo against a supplier front-line knowledge base: the Good Egg Energy help centre (https://goodeggenergy.knowledgeowl.com/help, about 60 articles), which is a KnowledgeOwl demo. Its billing, statements, quarterly billing and glossary pages are a US utility template ($, sales tax, a disconnection on day 60); its metering, vulnerability, PSR, emergency, complaints, switching and low-carbon pages read as GB. **It is a lead, never a source.** Every figure must come from a GB primary source (Ofgem, ICO, Energy Ombudsman, Citizens Advice, DESNZ, Elexon/Xoserve, HSE/Gas Safe, or the legislation itself).

**The director, in substance:** close the gaps that matter to billing correctness and to the moments where personalisation acts; for each one, produce the knowledge first.

## The rule for every item

1. A discovery page in `docs/market_research/` that answers the questions listed below. Each figure gets its source and date. Anything that couldn't be found is written up as a named GAP; nothing gets guessed.
2. Rows in `ASSUMPTIONS.md` for every number the world or the company will use. Values that need a ruling become toggles in `assumption_toggles.yaml`.
3. Each item's open gaps go into `docs/institutional/knowledge_map.md`.
4. The page says where the item lives: **world**, **company**, or **both**, and what crosses the seam.
5. Only after that: a build slice, in the stage shown below. If the knowledge shows an item doesn't matter, the page says so, and the seat closes the item on its own recommendation.

## Items

### Stage 1 (world physics)

**1. Read errors the world makes.**
- How often do customer self-reads contain transposed digits, misread dials or the wrong register?
- How often do meters roll over, and what is the GB stock of five-digit versus other registers?
- How common are crossed meters (wrong MPAN/MSN pairing), and how are they found and fixed?
- What do the Ombudsman and Citizens Advice say about the causes of disputed-usage cases?
- Extend the existing `meter_read_latency_estimation_2026.md` rather than starting a new page if that reads better.

**2. Complaints from their causes (wiring `simulation/complaint_generation.py`).** Its anchors are 2014 and 2024.
- Is there a newer published cause mix?
- What are the current Ofgem complaints-per-100k figures?
- What does the module need before anything can consume it?

**3. Low-carbon tech adoption as a step change in demand.** For heat pumps, EVs, home solar and batteries:
- What are the published before-and-after consumption shapes?
- When does each change show up on the bill?
- What is known about how households experience the change: bill shock, contact, whether they review their direct debit?
- Check against the existing `SEAT_FINDING_AN_EV_LIFE_EVENT…_2026-10-26` and `adoption_physics_c4.md`.

**4. Gas safety roles.**
- Who does what in a reported gas escape or CO incident: the supplier, the gas distribution network / National Gas Emergency Service, Gas Safe, HSE (RIDDOR)?
- Test `company/billing/gas_safety_incident_register.py`'s claim that the supplier "makes the supply safe". The advisor believes that duty is the network's, not the supplier's. Confirm or refute this from primary sources, and correct the module if it is wrong.

### Stage 2 (correct billing)

**5. Billing disputes, investigation to resolution.**
- What separates a query, a complaint and a dispute in the GB standards?
- Which resolution routes exist: correction, explanation, goodwill, payment plan?
- What does the meter accuracy dispute process require: who tests the meter, which statutory accuracy limits apply to each fuel, who pays, how long it takes?
- What are the published goodwill and redress norms (Ombudsman remedies, GSOP)?

**6. Smart Export Guarantee billing and bereavement closure.**
- SEG: the supplier obligation threshold, the metering requirement, MCS, payment mechanics, and how export sits beside an import bill.
- Bereavement: Ofgem's expectations on the deceased's account, exit fees, refunding credit to the estate, evidence, and timescales.

**7. Bill delivery: paper, paperless or both.**
- What do Ofgem and the licence rules say about paper bills, fees, and paperless discounts or penalties?
- What alternative formats does the PSR require?
- What are the published figures on digital exclusion by segment?
- What does a supplier pay to print and post a bill?
- How does the delivery channel relate to engagement and to how often customers see their usage?

**8. Marketing permissions and lawful basis.**
- UK GDPR legitimate interest (with the balancing test) and the right to object.
- PECR soft opt-in for existing customers: what counts as "similar products and services" for an energy supplier. Is an EV or heat-pump tariff similar? Is boiler cover?
- TPS screening.
- Where the line falls between a service message and marketing, with ICO guidance and enforcement cases from the energy sector. **This page must give the director what he needs to rule on whether personalised tariff and usage advice is a service message or marketing.** That ruling sets how many customers Poesys can reach.
- What share of customers object or opt out, by channel?
- Build is split: the permission state is account data in stage 2; enforcing it before any offer (`next_best_action`, retention, cross-sell) is stage 3.

## Deferred, not dropped

- **Workforce and cost to serve.** Agents, handle time and escalation tiers become a cost per contact by type in the epoch-2 cost-to-serve work.
- **Power cuts.** The DNO's job. Only PSR messaging and contact volume matter here.

## Out of scope

- Safeguarding call handling (the duty stays in the obligations register).
- Authorised users, power of attorney and identity verification, until epoch 3's walled interfaces.
- Quarterly billing.

## Work this creates

*Minted by the worker tick on 11 Nov from the body above, because the steer arrived without this block
(§4 of the 27 Jul work-definition ruling). **Author: please confirm or amend it.** Every item is a
knowledge page first. A build slice is drawn only once its page has landed, and only if the page says
the item matters. Under the 11 Nov ruling, the build slices draw from the feature third, and the pages
draw as knowledge.*

| # | Knowledge page (`docs/market_research/`) | Then, if the page says it matters | Side | State on 11 Nov |
|---|---|---|---|---|
| 1 | Read errors: transposition, misread dial, wrong register, rollover, crossed meters (extend `meter_read_latency_estimation_2026.md`) | World draws read errors at the published rates | world | not started |
| 2 | Complaints by cause after 2024, and Ofgem's per-100k figures | Wire `simulation/complaint_generation.py` to a consumer | world | not started |
| 3 | Low-carbon adoption as a demand step: before and after shapes, when it reaches the bill, household reaction | Adoption events move demand and bill shock | both | not started |
| 4 | Gas safety roles | Register corrected | company | **knowledge landed** in 038bdef0ea (`who_does_what_in_a_gas_escape_or_co_incident_2026-11-11.md`). Open finding: `WORKER_FINDING_THE_GAS_SAFETY_REGISTER_RECORDS_THE_NETWORKS_MAKE_SAFE_AS_THE_SUPPLIERS_OWN_ACT_2026-11-11.md` |
| 5 | Disputes: query, complaint or dispute; resolution routes; meter accuracy testing; goodwill and GSOP | Dispute path on the account | company | not started |
| 6 | SEG billing, and bereavement closure | Export line on the bill; estate closure | company | not started |
| 7 | Bill delivery: paper, paperless, PSR formats, digital exclusion, print and post cost | Delivery channel on the account | both | not started |
| 8 | Marketing permissions: legitimate interest, PECR soft opt-in, TPS, service message or marketing | Permission state (stage 2), enforced before any offer (stage 3) | company | not started. **The page ends in a ruling the director owes:** is personalised advice a service message? |

— Advisor, via the staging channel, on the director's instruction.
