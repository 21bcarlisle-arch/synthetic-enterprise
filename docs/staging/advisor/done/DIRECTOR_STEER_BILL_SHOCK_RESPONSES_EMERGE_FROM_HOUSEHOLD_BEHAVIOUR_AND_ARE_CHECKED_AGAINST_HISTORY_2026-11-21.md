**Severity:** BLOCKING · **Lane:** W2_customer_generator · **Epoch:** unassigned · **Atom:** `unminted`

**Knowledge:** how-households-behave-toward-a-supplier

# [DIRECTOR-STEER] Bill-shock responses emerge from household behaviour, and are checked against history

**Type:** STEER, through the advisor channel. It answers `for_the_director` row `your-12-oct-ruling-build-the-world` (DD4b), and goes further than the row asked. The advisor recommended building DD4b on a range starting at zero, and asked for any practitioner figure. The director answered with a design instead. His words, verbatim, from chat, Sat 21 Nov 07:15 GMT:

> "For bill shock I think there are different types. One is catch up bills, where estimates are updated or usage has changed. Or where a mistake is made. These results in a few actions. First people refuse to pay it, or if they don't have the money in their account the DD the DD fails. Some will not notice for while. Some will notice and call. This probably varies by payment method a lot. How the issue is handled then affects the likelihood to churn. The other type is where prices go up, due to variable price changes or end of fixed term. These odds need to come from the human behaviour assumed below in the SIM. Some will lapse, some will get the next best deal front he supplier. Some will shop around at this point. This is complex and thinking through the subtlty is important and valuable. I want to drive behaviour from a range of human responses to events driven by financial need and different engagement and attitude. I want to cross check that this matches approx events in history. IE total churn. IE. The spikes in churn we see when SVT tariff rises are announced. (NB the price shock for svt is also the announcements, the effective date and then when the impact hits the DD level). The biggest spike is media coverage. Then smaller ones are hard to see. What we know about fixed customers is that very few leave mid term, even without termination fees. Prices have to fall very far for people to bother, unless promoted by the supplier to take a lower price deal."

Under K4 this is the practitioner starting point, not the answer. Under K8, it is checked against published evidence before it is built.

## What he is saying, structured by the advisor (check it against his words above)

**1. Bill shock is not one thing. There are at least two families.**

- **Catch-up and correction shocks.** Causes: a stale estimate is corrected, usage changed, or the supplier made a mistake. The household responses form a set:
  - refuse to pay;
  - the DD fails for lack of funds;
  - does not notice for a while;
  - notices and calls.

  The mix **varies strongly by payment method**. **How the supplier handles the contact then moves the odds of churn.** This is the supplier's lever, and it must be visible in the world's response.
- **Price shocks.** Causes: a variable (SVT) price rise, or the end of a fixed term. The household responses:
  - lapse onto the default;
  - take the supplier's next-best retention deal;
  - shop around.

  For SVT, the shock has **three moments**: the announcement, the effective date, and the date the change reaches the DD amount. **The biggest response is driven by media coverage.** The smaller ones are hard to see in the data.

**2. Responses come from people, not from a fitted amplitude.**

- Drive them from a range of human responses to events, shaped by **financial need** and **engagement and attitude**.
- These are the hidden household traits already being built: the parsimony factors, the needs and the hidden utility.
- No single "shock raises shopping odds by X" constant is wanted. The aggregate should emerge.

**3. Check against history; do not fit to it.**

- The emergent behaviour must roughly reproduce:
  - **total churn** levels;
  - **the spikes when SVT rises are announced**, largest where media coverage was largest;
  - **the near-absence of mid-term leaving by fixed customers**, even with no exit fee. Prices must fall very far before they bother, unless the supplier itself promotes a lower-priced deal.

## What is asked (the machine owns the design)

1. **K8 first.** Amend or write the knowledge page on bill-shock responses by family and by payment method. Build on what exists:
   - the 7 Nov evidence pack `DIRECTOR_EVIDENCE_WHAT_HOUSEHOLDS_DO_AFTER_A_PAIN_POINT` (two-layer grievance and trigger-window model; Centrica's roughly 4x monthly loss spike after the 2018 rise; 42% with cause not complaining; 46% whose DD doubled not challenging it; 19% acting at the end of a fix);
   - `does_a_bill_shock_event_raise_the_odds_a_household_shops.md`;
   - Ofgem switching statistics (monthly series, for the spikes);
   - price-rise announcement dates and media intensity, 2016-2025;
   - mid-term fixed-tariff leaving rates.
2. **Model the events as events.** Each household reacts through its own traits (financial need, engagement, attitude, payment method) and its hidden utility. The world's existing pieces carry it:
   - activation energy;
   - grievance (the resentment ledger);
   - payment behaviour;
   - DD failure on the Bacs rails;
   - contact.

   Extend these rather than adding a parallel "shock response" table. Where a rate is not published, it is a stated belief with a range, under K2 and F11, not an invented point value.
3. **Media coverage is a world input,** dated, at the national level. It reaches households through their engagement. Find a published or measurable proxy for its intensity, for example the count of national news stories on each price-rise announcement. Do not invent one.
4. **The supplier's handling matters.** The world must let a good response to a catch-up shock lower churn and a bad one raise it, so the supplier has something real to learn. The supplier's handling itself is supplier-lane work.
5. **Validation is a gate, not a fit.** Name the historical targets and their tolerances before running:
   - annual and monthly churn;
   - the size and timing of announcement spikes;
   - mid-term fixed leaving.

   Report where the emergent behaviour lands. A miss is a finding about the behaviour, not a dial to turn.
6. **DD4b and the payment-plan engine's grade.** Build the price-shock and catch-up families as above. The 12 Oct ruling's intent (the world reacts to a DD shock before the engine is graded) now comes from this design, not from a single amplitude. Until it lands, the advisor's interim recommendation stands as a fallback that has been accepted: grade the engine at both ends of a range that starts at zero, not parked indefinitely.
7. **Place it in the world lane** in Monday's weekly review, with its cost. It joins the meter-data faults as world behaviour items. The knowledge page may be split across two weeks.

Close row `your-12-oct-ruling-build-the-world` with this steer as its resolution.

## Addendum, Sat 21 Nov 07:20 GMT: research it, from what customers themselves say

The director's words: "This is my knowledge. But I'd imagine this can be researched and this should be a key part of the knowledge base. I'd have thought that customer review sites are full oft his kind reaction"

What this adds:

1. **His account is a hypothesis to test, not the source.** The knowledge page on bill-shock responses becomes a **key page of the customer-behaviour corpus**, built from evidence.
2. **Mine what customers say, not only what surveys summarise.**
   - **Review sites:** Trustpilot pages for GB suppliers, and comparison-site reviews. Read within their terms. Sample and code by hand, or use published analyses of them. Do not bulk-scrape.
   - **Energy Ombudsman decisions and annual reports.**
   - **Citizens Advice:** supplier star ratings, complaint data and published case studies.
   - **Consumer forums:** MoneySavingExpert energy boards.
   - **Ofgem's consumer engagement surveys and switching statistics.**

   For each account, code:
   - the shock family (catch-up, mistake, SVT rise, end of fix);
   - the moment (announcement, effective date, DD change);
   - payment method;
   - the first response (ignore, refuse, DD failure, call, complain, switch);
   - how the supplier handled it;
   - the outcome (stayed, switched, escalated).
3. **Know the bias.** Reviews over-represent the angry and the delighted. The world's own feedback model already has this U-shape, at `simulation/feedback_survey.py`. Use review text to establish **which responses exist and how they chain**: the paths and their order. Take **rates** from representative sources (Ofgem surveys, Ombudsman volumes, switching statistics). State that split on the page.
4. **The same coding feeds the supplier side later.** Real reviews show what good and bad handling looks like. That is the evidence behind "how the issue is handled then affects the likelihood to churn".
5. **No personal data.** Store codes and short paraphrased examples only, never reviewers' names, under W11.

The advisor offers to run a first research pass after the Mon 23 Nov reset, to stage as evidence for the machine to check against primary sources, as with the 7 Nov packs. Use it if it arrives, but do not wait for it.

## Done

Actioned by the delivery seat, 21 Nov 2026, as direction. The build it asks for spans several
sessions, so it is placed and handed on here, not done in one turn.

- **Row closed.** `your-12-oct-ruling-build-the-world` is answered `changed` in
  `docs/direction/DIRECTION.yaml`: he answered the range-from-zero recommendation with a design. The
  advisor's interim (grade the payment-plan engine at both ends of a range starting at zero) is
  recorded there as the accepted fallback. The commitment is
  `bill-shock-responses-knowledge-page-with-the-customer-voice-coding-scheme`, due 4 Dec. It is done
  when the K8 page on bill-shock responses (by family, moment and payment method) lands, with the
  customer-voice coding scheme proven on it, paths from coded accounts, rates from representative
  sources, and the historical targets named with tolerances before any run.
- **Handed on, in the order the steer sets.** First the K8 page, building on the 7 Nov pain-point
  pack and on `what_bill_shock_is.md`, `BILL_SHOCK_EVENT_TYPES_ANCHORS.md`,
  `does_a_bill_shock_event_raise_the_odds_a_household_shops.md` and
  `satisfaction_drivers_and_the_three_bill_shocks.md`. Then the media-coverage world input (a
  published or counted proxy, never invented). Then the world build, extending activation energy,
  grievance, payment behaviour, Bacs DD failure and contact, with no parallel shock table. Last, the
  validation gate.
- **Placed for Monday's weekly review (23 Nov)** in the world lane, beside the meter-data faults,
  with the knowledge page allowed to span two weeks. Its cost is set there by
  `tools.work_cost_estimate`, not guessed here.
- **The advisor's offered research pass** after the 23 Nov reset will be used as evidence and checked
  against primary sources. The work does not wait for it.

Decision: fidelity changed
