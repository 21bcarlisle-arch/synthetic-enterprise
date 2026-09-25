**Severity:** LATENT · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** `PB4_engagement_separated_from_elasticity`

# PRE-REGISTRATION — building the offer-conditional seam with its amplitude declared absent

Written BEFORE any of the three measurements below was run. Drawn on the scheduled tick of
2026-09-24 as LANE 1 BUILD, `PB4_engagement_separated_from_elasticity`, level 1→3,
`loop_stage: build`.

## What I am about to build, and why the brief's own wording is not what gets built

The atom's `level_hold_note` names three residuals to L3. (a) is PB6's and cannot be earned here.
(c) is an expert hour. **(b) is the only build gap, and it is stated like this:**

> `active_renewal_probability_for_customer` takes a customer id and NO comparison offer, so
> engagement is a static per-household probability rather than a gate that a bill shock, a renewal
> letter **or a price rise past a threshold** opens.

That note was written 2026-09-15. On **2026-09-22**, seven days later, this repository's own
research pass established that the third of those three is the wrong shape AND the wrong variable
(`docs/market_research/is_there_a_bill_level_at_which_switching_rises.md` §6). Nothing connects the
two documents, and a session drawing this atom is pointed at the refuted mechanism by the note it
is instructed to read first. **That is the finding this pass files; the build below is what the
evidence supports instead.**

## The three predictions, each falsifiable, recorded before measuring

**P1 — the engagement path contains no bill-magnitude term today.** I have read
`active_renewal_probability_for_customer` and it is archetype × channel, so I hold this with high
confidence and record it anyway because the CALLEES are what I have not read to the bottom.
*Refuted if any transitive callee reads a price, a bill or a consumption figure.*

**P2 — the seam moves no published figure, identically and not approximately.** With the amplitude
declared absent, every existing caller passes one argument and must receive the same float it
receives today, bit for bit. This is the claim that matters: an engagement change made blind to the
director's baseline is a level move, and R12 forbids choosing parameters to hit an output in either
direction. *Refuted by any difference at all in the returned value for any customer id.*

**P3 — no control anywhere currently refuses a bill-magnitude term entering the WORLD's engagement
path.** The 2026-09-22 refutation landed against the COMPANY-side twin
(`company/crm/churn_model.BILL_STRESS_THRESHOLD_GBP`); I predict its world-side counterpart is
ungoverned. *Refuted if such a control exists.*

## What "done" means for this turn, decided here rather than after the answer

Not the atom's level. The level cannot move: (a) is blocked on PB6 and this pass does not touch it.
Done is **the structure landed with the answer honestly absent** — which is precisely what the
director's own cul-de-sac warning asks for, and the `level_hold_note` already observed that the
warning "is about precisely that argument":

> anything built now against P2–P6 should be built so that P1 changes its **answers**, not its
> **structure**.

So: the seam exists, the amplitude is a declared `None` with a named reason, and a household that
arrives at a boundary carrying a bill shock gets a **refusal that names why the world cannot yet
answer** rather than a silent "nothing happened". A silent pass-through would be a fail-open: it
would publish the claim *a bill shock does not affect whether a household shops*, which is a claim
this world has no evidence for and which the director's P4 asserts is false.
