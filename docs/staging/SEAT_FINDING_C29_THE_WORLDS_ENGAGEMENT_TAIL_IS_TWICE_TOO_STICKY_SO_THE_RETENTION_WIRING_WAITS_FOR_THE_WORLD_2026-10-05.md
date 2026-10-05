**Severity:** RECORDED · **Lane:** C_customer_ops · **Epoch:** 4 · **Atom:** `C29_decisions_stop_being_lookup_tables`

# The world's engagement tail is about twice too sticky, so the retention wiring waits for the world

Claim `c29-retention-reads-engagement-after-sourcing-the-archetype-spread` (C29 increment 2). At draw
time the duplicate-work note named this same id as already held. The only holder was this
invocation (`ps`: no rival seat or `surgical_land` on C29), so the note was the draw's own write. The
premise check said the cited commits 635bd7dfd and 1e687e06b are on origin. They are the
estimate's landing, not this work: nothing reads `company/crm/engagement_estimate` outside its tool
and test, so the premise is unspent.

## Step 1: source the archetype spread. Done, and the answer is no.

`docs/market_research/does_a_households_renewal_engagement_persist.md` holds the evidence. The
knowledge-map row is *Does a household's renewal engagement persist? (C29)*.

- **Established:** a never-switch STOCK tail of about 20% (CMA 2016 22%; Ofgem RMI Oct-2025 20.3%
  on default 3+ yrs). The shares 0.45/0.35/0.20 stand.
- **Not established, and contradicted:** the per-renewal 0.65/0.15/0.02. The test is Ofgem's
  *Sustained Engagement* (2020) follow-up of the 2018 Collective Switch RCT. In its no-letter
  control of 5,000 customers on SVT for 3+ years, **33% switched within 17 months**. The world gives
  **0.149** for the same cohort; I predicted about 0.15 by hand before the run. In that control a
  switch in the trial window **did not predict** the next (31% vs 33%). The world makes it a ×2.7
  predictor (0.255 vs 0.096).

## What that does to C29's lift

The +0.545 lift (ρ 0.73 vs 0.19) is measured in a world whose per-household persistence is
stronger than the published record allows. The estimator is honest by construction. It is
empirical Bayes, so a narrower world spread shrinks it toward the channel rate on its own. But
the *size* of the lift, and any value a retention decision then earns from it, would be inflated by
the world and not earned by the method. That is exactly the transfer-vs-creation confusion the
mission forbids, with the world on the wrong side of it.

**Alternative explanations, ranked by evidence:**

1. **The world's spread is too wide.** This is the leading explanation: two independent legs
   disagree in the same direction.
2. **Regime.** 2018–19 was a high-switching year. This could explain the level gap, and the cap
   arriving in the window may have spurred internal switches. It cannot explain the persistence leg:
   a ×0.94 ratio is not a regime artefact.
3. **The cohort is one large supplier's customers.** Possible, and it cuts both ways.

## Step 2: wire the retention decision. Deliberately NOT done this turn.

The direction said "THEN make the decision read the estimate". The knowledge-first rule says:
establish, run it against what is built, and only then decide the order. Run against the world,
the evidence says the thing the decision would be graded in is wrong in the one property the
decision depends on. Wiring now would produce a value figure that measures the world's stickiness.
So the order is:

1. **World (sim lane, a fidelity reason found from published evidence, blind to company value):**
   refit the per-renewal probabilities so the 3+-year default cohort chooses at about 0.33 over 17
   months in a non-crisis year, with within-tail persistence near ×1. The shares stay as ratified.
   Budget the value-arms retake: an anchor move reds about 25 world-digest controls.
2. **Re-grade the lift** with `python3 -m tools.c29_engagement_ranking` on the refitted world.
   If it falls inside the shuffle null, the frame's own refutation clause applies. Decision #1
   cannot be made per-account on engagement, and the next candidate is the dunning ladder (#5).
3. **Only then wire**, if the lift survives. The design needs no new constant. The retention guard
   at `simulation/run_phase2b.py` (`expected_margin + acq_cost_saved > ret_cost`) weighs the value
   protected with no probability at all. The opt-in reading would weigh it by the account's
   engagement estimate, which is formed point-in-time from the company's own term record as the
   time-ordered `while all_terms` loop reaches each anniversary. The discount SIZE stays the
   P(leave) tiers, a PB5 value question. No per-band discount is picked.

Both are handed on as continuations.
