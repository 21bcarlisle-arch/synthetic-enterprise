**Severity:** LATENT · **Lane:** W2_customer_generator · **Epoch:** unassigned · **Atom:** `unminted`

# [DIRECTOR-STEER] Pain points drive the loop: knowledge first, then the world reacts to them, then the supplier tests against them, and repeat (2026-10-30)

**Type:** STEER, through the advisor channel. The director's words, from chat on Fri 30 Oct, 07:30 GMT, following his 07:26 ruling on new-account estimates:

- 07:30 GMT: "But don't just do what I said and thought of quicker. Create knowledge in this area and in unbilled. What do different people do. What are the pros and cons. What do customers experience. What pain points should we measure. Is the SIM making customers react and behave to pain points? As it's this that should drive the supplier to optimise."
- 07:30 GMT: "So we need knowledge. SIM enhancement. And supplier testing to optimise versus this. Once it's settled we can look to make the SIM more real and more nuanced and the cycle contines."

## The loop, as a standing method

1. **Knowledge.** For each area, write down:
   - what suppliers actually do, how they differ, and the pros and cons of each approach;
   - what customers experience;
   - which pain points are measurable;
   - the published evidence on how customers react: complaints, Ombudsman escalation, churn, non-payment, DD cancellation, calls, and trust.
2. **SIM enhancement.** World households **react** to each pain point. The reaction is drawn from that evidence and conditioned on the household's own traits, such as payment stress, engagement and vulnerability. It is hidden from the supplier, so the supplier sees only the consequences.
3. **Supplier testing.** The supplier pre-registers variants against the baseline and grades them on the outcome metrics. It optimises against what the world does, not against a rule.
4. **Settle, then add nuance.** Once a result holds, make the world more real in that area and run the loop again.

## First two areas

1. **A new account's first months:** quote consumption, opening read, first DD and early review. See today's ruling, `DIRECTOR_RULING_A_NEW_ACCOUNTS_ESTIMATE_STARTS_AT_STANDARD_PRACTICE_AND_THE_SUPPLIER_EXPERIMENTS_2026-10-30.md`.
2. **Unbilled energy:**
   - estimates, missing reads, smart meters in dumb mode, and held or exception bills;
   - catch-up bills and back-billing (SLC 21BA);
   - unbilled revenue on the supplier's side and the settlement truth arriving late.

The advisor is writing one evidence pack for each area now. Each pack ends with a table with one row per pain point, giving: how the customer meets it, the measurable signal, the evidence of reaction, and a suggested simulation behaviour. It also lists supplier levers with the outcome metrics they move. The packs will land beside this file today.

## Ask now: an audit, not a build

Answer the director's question, **"Is the SIM making customers react and behave to pain points?"**, for these pain points as they exist today. For each one, say whether a world household currently reacts to it, how, and what evidence the reaction was drawn from:

- a DD step-up;
- a catch-up or shock bill;
- a run of estimates;
- a refused credit refund or a large credit balance;
- a billing error or complaint;
- a debt letter;
- a price rise or renewal.

Where a household does not react, the supplier has nothing to optimise against in that area. Name those gaps.

**Order of work.** The audit is cheap and is drawn now, inside the correctness stretch, because it explains what the graded outcomes mean. The SIM enhancement and the supplier experiments are drawn after the correctness exit test, unless one of them is needed to close it. File both on the customer-outcomes roadmap.

## Done

2026-10-30, the delivery seat. The audit this file asked for "now" is
`docs/staging/SEAT_FINDING_THE_WORLD_REACTS_TO_ONE_PAIN_POINT_IN_SEVEN_AND_ITS_RENEWAL_SHOCK_IS_THE_SUPPLIERS_OWN_CHURN_CURVE_2026-10-30.md`.

**Coverage.** Of the seven pain points:
- a price rise or renewal: the world reacts in full;
- a DD step-up: only the departure leg is on; its cancellation, failure and complaint legs ship at 0;
- a catch-up bill: calls only;
- a complaint: a roll per renewal term;
- a debt letter: a small on-time payment effect;
- a run of estimates and a refused refund or credit balance: no reaction;
- a billing error: no trigger exists.

**Wall-shaped item.** The world's renewal-shock hazard calls the supplier's `saas.churn_model.churn_probability` (`simulation/customer_events.py:770`). Fixing it is a SIM enhancement.

**Filing.** There was no "customer-outcomes roadmap" file, so the finding holds the three candidates in order:
1. the DD4b legs, switched on and sourced;
2. the world's own shock uplift;
3. a reaction to estimate runs and to held credit.

**What is left.** The SIM enhancement and the supplier experiments wait for the correctness exit test, as this file sequenced them. The loop's design is carried by the later steer, `DIRECTOR_STEER_OWN_THE_DESIGN_OF_THE_WORLD_SUPPLIER_IMPROVEMENT_LOOP_2026-10-30.md`.

**A second, independent pass agrees (the worker, same day).** `docs/staging/records/SEAT_READING_DOES_THE_WORLD_REACT_TO_PAIN_POINTS_THE_AUDIT_THE_DIRECTOR_ASKED_FOR_2026-10-30.md` was read at 38960f39cc. It reaches the same verdict on every one of the seven pain points, and it adds that the resentment ledger is never fed into the churn roll. It did not find the renewal-shock leg reading `saas.churn_model`; the finding above did. A customer-outcomes list now exists: `docs/direction/priority_order.yaml` `customer_outcomes_candidates` (`unbilled-energy-pain-points-react`, `new-account-first-months-experiment`). The finding's three SIM-enhancement candidates belong there.
