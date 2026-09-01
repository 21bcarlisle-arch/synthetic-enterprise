# [WORKER FINDING] The dissatisfaction dose is bounded by two pages we already hold, and the world sits under the bound

**Severity:** LATENT · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** `A46_the_priced_menu`
**Found:** 2026-09-01, by the delivery seat, while sizing the repair named by
`WORKER_FINDING_THE_WORLDS_SERVICE_RISK_IS_CANCELLED_BY_A_MODULATOR_THAT_SHARES_ITS_DRIVER_2026-08-31`.

## Class registration

Belongs to `measurements_that_mirror` — **and is REFUSED consolidation into it, correctly.**
That class register carries lane `H_harness`; this finding is `W2_customer_generator`. Severity is
lane-scoped, so filing it there would remove the W2 lane's finding while recording it under
someone else's. The register lists it under *"Refused consolidation — out of lane, still live"*
and this document stays in the queue. Recorded here because the trap is easy to walk into: I
archived it once on the strength of having declared a class, and an out-of-lane document that is
archived belongs to neither list and vanishes from both.

## The claim being examined

`simulation/satisfaction_churn.py` declares its two multipliers the only unsourced numbers on the
page, and says why:

> *"Nothing in the knowledge layer establishes the DOSE — how much a unit of dissatisfaction
> converts into switching. … To do it properly: a published dose-response between service
> experience and supplier switching, which the Ofgem Consumer Impacts and Consumer Satisfaction
> surveys do not currently give (they publish satisfaction levels and switching rates, never the
> two crossed at the individual level)."*

That is scrupulous and it is **very nearly right**. It is wrong in one way that matters: the two
are never crossed *directly*, but the knowledge layer holds enough to **bound** the dose, in two
pages, neither of which the module cites.

## What we already hold

**`docs/market_research/gb_switching_rate_denominators.md` §7** — Ofgem Consumer Impacts Monitor
wave 5 (Jan–Feb 2024, base 174 switchers), reasons given for switching:

> cheaper tariff 44%; good reputation 19%; issues with current supplier or tariff 16%;
> **poor customer service 16%**; offers good service 15%

**`docs/market_research/ASSUMPTIONS.md`** — Ofgem/Citizens Advice Consumer Satisfaction Survey
Wave 20 (Jan 2025, n=3,854): **dissatisfied + very dissatisfied = 6%** of GB bill-payers.

Those two cross by Bayes into exactly the quantity the module says is missing:

    P(switch | dissatisfied) = P(cited service | switched) x P(switch) / P(dissatisfied)

## The arithmetic, and the one thing that makes it robust

**The RATIO is invariant to the switching rate.** It cancels. Computed at the published GB rates
for 2023 (12.32%), 2024 (14.96%) and 2024's upper reading (16.1%), the multiplier is **2.98× in
every case**. So the result does not depend on which year's denominator you take, which was the
first thing that could have made it worthless.

| P(cited service \| switched) | P(dissatisfied) | implied multiplier |
|---|---|---|
| 0.16 — CIM w5, *"poor customer service"* (a **push** reason) | 0.06 — Wave 20 dissatisfied+ | **2.98×** |
| 0.06 — CIM w6, *"better rated customer service"* (a **pull** reason) | 0.06 | 1.00× |
| 0.16 | 0.19 — including *"neither satisfied nor dissatisfied"* | 0.81× |
| 0.06 | 0.19 | 0.27× |

**The world's `_LOW_SATISFACTION_MULTIPLIER` is 1.30.**

## What this does and does not establish

**It does NOT establish the dose.** The table spans 0.27× to 2.98×, which is "no effect" to
"threefold", and a number picked out of that range would be a number picked. The module was right
to refuse.

**It DOES bound it, once the question is matched.** Two of those four rows ask the wrong question
and they are the two that land low:

* CIM wave 6's *"better rated customer service"* is a **pull** reason — why I chose the new
  supplier — not a **push** reason. A dissatisfaction dose needs the push.
* Folding *"neither satisfied nor dissatisfied"* into the dissatisfied denominator widens it to a
  population the multiplier's low band is not about.

Take the matched pairing — a push reason against the dissatisfied share — and the implied
multiplier is **2.98×**. And a **disjoint** source agrees: Ofgem's complaint-handling consumer
research, cited in `docs/market_research/f1_simulating_conversations.md`, reports that **nearly one
in two complainants had already switched or planned to switch as a result of their complaints
experience** — ~50% against a ~15% base, i.e. **>3×**, from a different instrument, a different
year and a severer tail.

**So: every matched reading of the published evidence puts the dose at or above ~3×, and two
disjoint sources agree. The world uses 1.30.** That is not a calibration quibble — it is below the
bottom of the matched range, and the direction is the one that matters: **the world understates how
much dissatisfaction moves a household**, on the axis the director's brief puts at 32% of the
switching decision.

## Why it is `measurements_that_mirror`

Not because the arithmetic mirrors anything — because of **how the gap survived**. The module
asked "is the dose published?", got "no", and stopped. The dose is not published and is
*derivable*, and the derivation needed one figure from each of two research pages this project
wrote itself. **A search for a published ANSWER, where what exists is published INPUTS, returns
"nothing establishes it" and reads exactly like a genuine gap.**

This is the shape CLAUDE.md holds up as the canonical failure, at a new address: *"`saas/opex_ledger.py` held a sourced £55 acquisition cost, cited and tested, and reached no code for seven weeks while an invented £150 was what the campaign actually spent — and the knowledge map recorded the sourced figure and listed the same subject as a gap, in one file. Nothing told the reader to look."* Here nothing told the reader that the switching-denominators page and the satisfaction page are two halves of one question.

## What is owed

1. **Raise the dose to the matched bound, or record why not** — with a pre-registration and a
   one-variable run, because it moves every financial figure. It must NOT be done in the same
   change as the sign repair below, or neither can be attributed.
2. **It is second in order, not first.** `..._SERVICE_RISK_IS_CANCELLED_BY_A_MODULATOR_THAT_SHARES_ITS_DRIVER_2026-08-31`
   is right that tuning a dose that is being cancelled anyway moves a number and changes nothing.
   The sign goes first. This finding's contribution is that when the sign is fixed, the dose is
   already known to be too weak, and by roughly how much.
3. **A cross-reference that would have prevented this.** The switching-denominators page and the
   satisfaction module are two halves of one question and neither points at the other. The general
   repair is not a bigger knowledge map — it is that a module declaring a constant UNSOURCED should
   name the search it ran, so the next reader can see it searched for an answer and not for inputs.

## What this finding does NOT claim

It does not claim 2.98× is the right value; it claims 1.30 is below the matched range. It does not
claim the module's author was careless — the quoted paragraph is more careful than most. It does
not claim any published figure is wrong today: the level is set elsewhere, and this is a mechanism
defect whose consequence is that the company is inferring against a signal the world has made too
faint, which is the wrong bias for a project whose thesis is that inference advantage is real.
