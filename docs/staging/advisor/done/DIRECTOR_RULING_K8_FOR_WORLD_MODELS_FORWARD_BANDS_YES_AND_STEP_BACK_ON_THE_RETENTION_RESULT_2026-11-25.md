**Severity:** BLOCKING · **Lane:** A_strategy_governance · **Epoch:** unassigned · **Atom:** `unminted`

# [DIRECTOR-RULING] K8 covers world models: yes. Forward bands: yes. The retention result: no rerun. Step back and ask what reality says should happen

**Type:** RULING and STEER, through the advisor channel. It answers three `for_the_director` rows. The director's words, from chat, Wed 25 Nov 12:31 GMT:

> "Yes. Yes. No, think about it, what's going on. What should we really expect to happen? I don't get why offering less doesn't make more money, even if fewer are retained. What is the thesis? What is the knowledge here we are seeking replicate?"

## 1. `k8-knowledge-before-build-covers-supplier-capabilities`: yes

Adopt the one-sentence extension: K8 covers world models as well as supplier capabilities. Land it in canon with `Director-doc: his-words`, citing this ruling. Close the row.

## 2. `the-forward-world-has-bands-for-gas`: yes

Use the published bands for transmission demand and interconnector net flow (NESO FES), and the published band for carbon (DESNZ carbon values or traded-price projections, as the row proposed). Record them in `forward_years.json` as his curriculum choice. Close the row.

## 3. `s-12g-rank-at-q-run-graded`: no rerun. Think first

He rejects both options: the conservative reading and the volume-matched rerun. The result does not make sense to him, and he wants to know why before any more runs. This is the 22 Nov curiosity steer and the 24 Nov knowledge check, applied to the thesis test itself.

**His puzzle, in the advisor's words.** A retention offer is a discount. Offering fewer of them gives away less margin. Even if a few more customers leave, a supplier that offers less should often make **more** money, not less. That is the whole loyalty-penalty story of GB retail: inert customers rolled onto the default tariff paid more and mostly stayed. Yet rank-at-q offered to 11% of renewals against the twin's 28%, and made **£2.45 per household-year less**. **For that to happen in the world, each extra offer must have paid for itself**, with retained margin outweighing the discount given. Is that what reality does?

**What is asked, in this order:**

1. **Decompose the £2.45 before anything else.** For every renewal in both arms:
   - discount given (margin forgone on households who would have stayed anyway);
   - margin kept on households the offer actually retained;
   - margin lost on households who left;
   - the default-tariff margin earned by households who were not offered and stayed.

   Do it by year, separately for pre-cap, the cap era before 2021, and 2021-23, when fixes were priced above the cap and a "retention offer" may have been **dearer** than the default. If offers cost the supplier nothing in some years, or earned it money, "fewer offers lose money" may simply be that.
2. **Knowledge check on retention (24 Nov steer: is it there, deep, broad, right?).** What does the real GB record say should happen at the end of a fix?
   - What share roll onto the default, take the supplier's retention fix, or switch away? Sources: Ofgem 2016 survey; the 2019 end-of-fix trial (19% act in six weeks, 28% with a better notice, external switching unchanged at 6%); 53%/51% on default in April 2019; the CMA 2016 investigation's loyalty-penalty findings (detriment of about £1.4bn a year).
   - How much more does a default customer pay, and how much more likely are they to leave, than a fixed one, by period?
   - What does the uplift literature say? Ascarza (2018, "Retention futility"): targeting by churn risk is the wrong rule; target by the effect of the offer (uplift). Ascarza 2016 found an offer that raised churn.
   - Then **check the world against it.** Do the world's households, offered nothing at the end of a fix, leave at the real rate or much faster? If the world makes un-offered customers too likely to leave, it inflates the value of every offer. The result is then the world's error, not the supplier's.
3. **Restate the thesis for this test, and measure against it.** The mission is to create value for a household and share in it (M2, M3). Money moved is not value created. A retention discount to someone who would have stayed is a transfer to the household. A default-tariff margin on an inert household is a transfer to the supplier. **The thesis is not "the per-customer arm makes more money".** It is that the per-customer arm finds the households where a different offer **creates** value, both shares counted, and that a flat rule cannot. The money comparison alone cannot answer that. Say:
   - what this test's money result can and cannot tell us about the thesis;
   - what measure would answer it (household value plus supplier margin, and transfer shown apart, as the 13 Nov utility ruling set);
   - which of the arms' differences is creation and which is transfer.
4. **Only then propose the next run, if one is still needed**, with what it will settle and its predictions filed first. Explaining why the world behaves as it does comes before testing more levers inside it.

Put the decomposition and the knowledge check first in the supplier share. Give the director a plain-English answer to "what's going on, and what should we expect" within two days. The advisor will relay it.

## In hand, not done (25 Nov, seat executor)

Parts 1 and 2 are actioned. K8's extension is in canon, landed with `Director-doc: his-words`. Both
rows are closed `yes`. The forward bands and the K8 one-leg test are handed off as
`the-forward-world-has-bands-for-gas` and `k8-covers-world-models-one-leg-test`. Part 3's row is
closed `no`. Its work is handed off as
`the-retention-result-decomposed-and-checked-against-reality`, due 27 Nov. This file stays here until
that answer lands, because its three questions are open in the question register. A reader drawing
this file should do part 3 and nothing else.

## Done

Part 3 answered 25 Nov from the s.12g records; no run launched. The decomposition, cause, thesis and a re-grade
proposal (predictions filed) are in
`docs/staging/SEAT_FINDING_AN_OFFERED_LEAVER_IS_ANSWERED_ON_A_DIE_THE_FLOOR_DID_NOT_REDRAW_2026-11-25.md`. The
knowledge check is `docs/market_research/what_happens_at_the_end_of_a_fix_and_whether_the_world_does_it_2026-11-25.md`.
In short: offering less should make more money, and the world's stated physics agrees. The run said otherwise
because an offer was answered on a die the noise floor did not re-draw (`simulation/retention_offer.py`, fixed).
The three questions are closed in `docs/observability/open_question_register.json`.

Decision: none -- his words answer three for_the_director rows, each coded on its row when parts 1-3 were actioned (11a4387c6: yes, yes, no); coding this file as well would count them twice
