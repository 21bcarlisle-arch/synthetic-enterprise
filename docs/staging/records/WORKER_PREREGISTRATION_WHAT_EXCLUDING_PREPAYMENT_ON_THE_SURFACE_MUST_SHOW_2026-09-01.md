# [WORKER PREREGISTRATION] What excluding prepayment on the surface must show

**Severity:** RECORDED · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** `A46_the_priced_menu`
**Filed:** 2026-09-01, **before the change.** Every number below was measured on the published
`run_output_latest.json` and on `simulation.household_segments.payment_channel_for_customer`
BEFORE any code was edited, and none was written after a result.
**Knowledge:** `docs/market_research/what_bill_shock_is.md` — the definition, established and NOT re-opened.
**Finding:** `WORKER_FINDING_THE_WORLD_KNOWS_HOW_EACH_HOUSEHOLD_PAYS_AND_BILL_SHOCK_IS_THE_ONE_ORGAN_NOT_TOLD_2026-09-01`, item 2.
**Predecessor:** the split, which restricted `avg_shock_pct` to the `bill` population and published
`out_of_scope` as a null with the gap named. This is the separate commit that instruction (c) reserved.

## The decision, and why this one

The instruction offers two honest routes: **model prepayment as a third channel**, or **exclude it
explicitly with the reason named on the surface.** I am taking the second, and filing the first as
its own drawable item rather than doing it here.

**Why not model it.** Adding a third `PaymentChannel` member is a **world change**. It alters which
households exist and what they do, and `payment_channel_for_customer` already feeds three organs —
`arrears_engine`, `final_bill_outcome`, `sim_satisfaction` — and through them churn and the P&L. That
is many published figures moving in one step, which is unattributable by this project's own rule, and
under the baseline/curriculum wall a world change is made for fidelity reasons, named and versioned
in a file the director reads. It is not a bounded worker tick's call.

**What is no longer a reason not to.** `simulation/household_segments.py:282` declares the
prepayment-versus-standard-credit sub-split a *"genuine registered gap, not guessed"*, citing DESNZ's
June 2026 commentary, which does not carry it. **That is now stale.** `docs/market_research/
dd_attribution_confound_w2_10.md` records ~74% / 13% / 13% (Ofgem, 2026) under "Anchors [L] (real,
sourced — never fabricated)", and `what_bill_shock_is.md` republished it this morning. The anchor
exists, in this repository, and the code that would use it says it does not. Filed separately as
`WORKER_FINDING_THE_WORLD_DECLARES_A_GAP_ITS_OWN_KNOWLEDGE_LAYER_HAS_CLOSED_2026-09-01` — this is the
£55-versus-£150 shape exactly, and it is what makes the modelling route drawable instead of blocked.

## THE PROBLEM WITH "EXCLUDE PREPAYMENT", STATED BEFORE I DO IT

**You cannot exclude what is not labelled, and in this world prepayment is not labelled — it is
wearing a standard-credit label.**

`PaymentChannel` has two members, so the published non-DD remainder is folded into
`STANDARD_CREDIT`. Measured on the live book, 251 accounts:

| | our world | published GB |
|---|---:|---:|
| direct debit | **68.1%** (171) | ~74% |
| standard credit | **31.9%** (80) | ~13% |
| prepayment | **0%** (0) | ~13% |

Published non-DD is 26%, split **exactly half and half** between standard credit and prepayment. Our
non-DD is 31.9%, all of it labelled standard credit. So **roughly half of our 80 non-DD accounts —
about 40, some 16% of the book — are prepayment households wearing a standard-credit label**, and
they are already inside definition B. Our definition-B population is **2.5× the published standard
credit share**.

In event terms: the split publishes **912 `bill`-population events**, and under the published
sub-split **roughly 456 of them belong to households who, in GB, would have no bill to be shocked by
at all.**

**So an exclusion that filters on `bill_shock_population == "out_of_scope"` removes exactly nothing,
today and for as long as the channel has two members.** Writing one and calling item (c) done would
be a control that cannot fail — this repository's most-filed defect class — dressed as a repair.

**What the surface must therefore say is not "prepayment is excluded". It is that the population
`avg_shock_pct` is a mean over CANNOT have prepayment excluded from it, because prepayment is not
separately labelled, and it is therefore about twice the size of the population the definition
names.** That is the honest disclosure. The filter is the cheap half; the disclosure is the half
that is true.

## The change, in one line

`monthly_ops` states, beside the figure, that its `bill` population folds standard credit and
prepayment together and by how much — and the exclusion of `out_of_scope` is proven by a control
that can fail on a fixture even though the world cannot produce the event.

## The predictions

**X1 — NO PUBLISHED PERCENTAGE MOVES.** This is disclosure and a filter over an empty set. Every
`avg_shock_pct`, `median_shock_pct`, `max_shock_pct`, both CI bounds, `mixed_all_population_avg_pct`
and every `shock_by_population` figure is identical across all 113 months. Only new keys appear. **Any
movement refutes the claim that this commit changes no measurement**, and would mean the filter is
catching something the split already excluded — i.e. that the two disagree.

**X2 — `out_of_scope` stays n=0 in all 113 months**, and publishes `avg_pct: null`, never `0.0`.
The channel still has two members; nothing here adds a household.

**X3 — the disclosure carries its SIZE, not just its existence.** The surface names 68.1 / 31.9 / 0
against 74 / 13 / 13, and says the `bill` population is about twice the published standard-credit
share. A note saying only "prepayment is not modelled" would leave a reader believing the remaining
population is the right one.

**X4 — THE CONTROL THAT IS NOT A TAUTOLOGY.** A synthetic `out_of_scope` event of 900% must not reach
`avg_shock_pct`, and must be counted in its own population. This is the one assertion here that would
still fail if the exclusion were deleted; every assertion keyed to today's `n=0` would not. If the
new control passes with the exclusion removed, it is decorative and must be rewritten before landing.

**X5 — the shares on the surface must be derived from the constants, not typed beside them.** The
published mix and the note that quotes it are one artefact or two; if two, only one gets edited
(`a_hand_authored_public_claim_and_its_machine_readable_form_are_two_artefacts_and_only_one_gets_edited`).
The note is built from the named constants, so a share cannot drift away from its own prose.

## What would refute this, stated before the run

- Any change to any published percentage refutes X1 and means the split and this filter disagree
  about which events are in `bill`.
- A control that stays green when the `out_of_scope` exclusion is removed refutes X4 and the commit
  does not land.
- An `out_of_scope` count above zero anywhere refutes X2 and would mean a channel appeared without a
  world change, which would be a wall breach, not a success.

## What this commit explicitly does NOT do

1. **It does not add a prepayment channel.** That is a world change, filed as its own item with the
   anchor now named.
2. **It does not touch the split, the £5 baseline floor, or the bound.** All three landed and stand.
3. **It does not measure definition A.** The DD amount is still not a modelled quantity — the
   director's own correction, out of scope by instruction.

---

## OUTCOME — scored after the change, against the predictions above

*To be written after the run. Nothing above this line is to be edited.*
