**Severity:** BLOCKING · **Lane:** A_strategy_governance · **Epoch:** unassigned · **Atom:** `unminted`

# [DIRECTOR-STEER] Explore becomes a live feature demo, three views of real households, and it proves the features actually work (2026-10-23)

**Type:** STEER, through the advisor channel. It replaces item 6 (Explore) of `DIRECTOR_STEER_THE_OTHER_PAGES_MATCH_THE_FRONT_DOOR_2026-10-23.md`. The director's words, from chat on Fri 23 Oct:

- 08:50 BST: "I'd like explore to show case the data. How different interesting customers, maybe not all, but a selection, have interesting usage patterns or demonstrate the feature we have with billing etc. Maybe we want to show off features. Winning, moving, estimates, renewal, debt, EV, etc. … (I quite liked showing CRM like software interface) Or maybe even better make it look like the customers portal? Flip between what the SIM knows about the customer and their property household etc. And what the customer sees. Usage, bills etc. like they would on a website. And also show what the SIM knows that the supplier producing the portal with billing info etc doesn't know, but can infer"
- 09:06 BST: "What about time? … How do we keep this simple but look impressive and professional? Also we've built variants of this before haven't we?"
- 09:18 BST: "Mock up please. How do we keep this live? Is the almost a form of automatics feature demo?"
- 09:30 BST: "This is another good reason to do it. To actually check features really work!!!"

**When:** build now, beside the other pages' rewrite. It needs to be live by the Monday 26 Oct publish. If the full cast can't be ready by then, ship the page with the slots that are ready, and have every other slot say plainly why it's empty (item 4).

---

## The design he approved

A mock-up made by the advisor, interactive, using real figures from household SYN-2016-306 on the 19 Oct run, is committed at `docs/design/explore_three_views_mockup_2026-10-23/Main.dc.html`. It is a reference for layout and behaviour, not code to ship. Build the page in the site's own stack, under the Poesys brand tokens.

- **Cast.** Six to eight households, one per feature, each shown as a tab with the feature name and a one-line story.
- **Time.** A 2016–2025 strip carries four to six key moments drawn from that household's real timeline. Step with ‹ ›, or press "Play the story". The page opens on the most telling moment, not on a free slider.
- **Three views of the same moment,** side by side or one at a time:
  1. **What the customer sees.** A Poesys account portal, watermarked "Simulated household": tariff, how they pay, balance or overdue, 12 months of usage for both fuels, latest bills marked Estimated or Actual read, and the message the customer received. Reuse the supplier's own portal (`company/portal/templates/`: dashboard, bills, consumption, direct debit) rendered from the run. Then the page can truthfully say this is the supplier's portal, not a picture of one.
  2. **What the supplier sees.** The back office as known on that date: churn risk, next best action and its expected value, payment record, read counts and last actual read, debt stage, inferred traits, and a decision log line.
  3. **What is really true.** The simulation's ground truth: the household, the property, finances, life events, hidden mood, the true chance of leaving, and why it really did what it did.
- **The gap strip.** "The supplier believed / The truth was / What it cost or meant", coloured by outcome.
- **What already exists, used rather than rebuilt:**
  - the current Explore page's truth-and-belief plumbing and its customer-only view;
  - `site/data/customers/*.json`: invoices, ledger, timeline and reaction chain;
  - `site/data/customer_sample.json`: ground truth;
  - `site/data/case_studies.json`: the rule-based cast selection.

## WORK THIS CREATES

1. **The cast is chosen by rule at every publish, one rule per feature.** Nothing is hand-picked. Start with:
   - **the switch-in:** quote, credit check, cooling-off, first bill;
   - **the renewal:** the largest gap between belief and truth at a renewal decision, with an offer made or withheld;
   - **the estimate trap:** the longest run of estimated bills, ending in a catch-up or credit;
   - **the mover:** move-out, final bill, new occupant, and gas following the household once the 22 Oct mover fix lands;
   - **the debt journey:** missed bill, notices, then a payment plan, offset or write-off;
   - **the EV home:** overnight load, with the supplier's inference set against the truth;
   - **storage heating:** a PC2 home, billed on its meter and bought on its profile;
   - **the 2022 shock:** bill shock and the direct-debit reassessment.

   Add a slot whenever a new feature lands.
2. **The moments are chosen by rule from each household's own event log,** and the words are generated. Use one plain-English template per event type, filled with that household's numbers. Never state a motive the data does not record. Where the reason is unknown, say what was true (the true probability, the mood, the life event), not a story.
3. **No look-ahead, proven rather than claimed.** The supplier view at a moment shows only what the company held on that date. Store the belief at decision time, and read it back from that store, never by recomputing with later data. Add a control that reds if any supplier-view field draws on a record dated after the moment.
4. **Explore is a feature-coverage test, the director's 09:30 point.** Each cast rule is also a check that its feature really works end to end in the published run:
   - If no household qualifies, the slot says so on the page ("No household in this run reached a payment plan"), and the stretch log records it as a finding.
   - If a household qualifies but its numbers break a published rule, the slot flags it, and the finding is raised. Examples: a bill above the cap, a back-bill beyond 12 months, a gas leg left behind at a move.
   - Run the same checks in the Monday end-to-end step, so a feature that silently stops working turns the build red before a reader sees it. Mutation-prove them (R15).
5. **Three things the mock-up found, to check first,** using `SYN-2016-306` on the 19 Oct run:
   - **Bills that look above the cap.** November 2022 billed £282.19 for 519 kWh of electricity and £407.08 for 2,703 kWh of gas. That is about 54p/kWh and 15p/kWh all-in, against Energy Price Guarantee unit rates of about 34p and 10p. Check whether a capped tariff billed above the cap, or whether something else is in these bills.
   - **Insulation that never reached the bills.** The truth says use fell 20% for electricity and 24% for gas from February 2022. Billed gas use stayed at about 23,000 kWh a year through 2024, despite actual gas reads in December 2022, April 2023, August 2023, November 2023 and March 2024. Find out whether the estimate ignores actual reads, or whether the truth's change never reached the meter.
   - **A debt that was never chased.** £85.35 overdue since 2018–19 (£68.50 electricity, £16.85 gas) sat unchased for five years, then was written off and passed to an agency 13 days after the household left. Check this against the collections policy and the debt-and-collections knowledge page. Also, the gas account's timeline labels its renewals `"commodity": "electricity"`, at an electricity £/MWh rate.
6. **Keep it phone-friendly and accessible.** It must work at phone width, with real buttons, keyboard steps and text contrast that passes. Render the first moment static at publish, so the page shows without JavaScript.

## Report

One stretch-log entry with:
- the cast rules, and which slots filled on the run;
- the coverage findings (empty slots and rule breaches);
- the three checks in item 5, with their answers;
- the no-look-ahead control;
- a cold-reader pass on the page, one energy reader and one tech reader, asking what they learned and how impressive it is.

— Director steer, 23 Oct 2026, his words above; the mock-up, findings and drafting are the advisor's.
