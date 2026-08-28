**Severity:** RECORDED · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** `A46_book_depth_is_a_curriculum_question`

# P9 returned with its cost: four ways to buy book depth, what each costs, and the one I'd take

`DIRECTOR_GUIDANCE_THE_WORLD_MUST_PRESS_2026-08-28`, WORK THIS CREATES item 4 — *"P9 returned to
the director as a curriculum question with its cost, not decided."* This is that. **The decision
is yours** (R13: which worlds the company lives through is curriculum, named and versioned, never
agent-set, because the agent controls both sides of that wall). **The pricing is mine**, and it
is below, with a recommendation, because an ask without one is a defect.

---

## The cost law, and it is exact rather than estimated

Contract terms are **365 days** (`simulation/settlement.py::CONTRACT_LENGTH_DAYS`), so renewals
count tenure years. Settlement is budgeted in **customer-years**
(`net_new_acquisition.SETTLEMENT_CUSTOMER_YEAR_BUDGET = 1200.0`). Therefore:

> **N accounts each carrying ≥ R renewals costs at least N × R customer-years.**

Nothing about that is a modelling choice; it is what the two units mean.

## Where the 1,200 currently goes, which is the actual finding

From `docs/observability/book_growth_campaign.json`, the live run:

| | |
|---|---|
| Customer-year budget | 1,200 |
| Committed | **1,112.1 (93%)** |
| Accounts at 2025-12 | 264 |
| Won through the funnel | 241 |
| Founders (held at 2016-01) | **18** |
| Accounts with ≥5 renewals | **37** |

Those 37 cost **185 customer-years**. The other **1,015 — 85% of the budget — is spent on
accounts that cannot compound.**

The book is back-loaded because acquisition is capital-gated: 5 wins in 2016 against 48 in 2023,
and the binding constraint flips from `growth_rate` to `capital` in 2023. The company could not
afford to buy customers early, so it bought them late, and **late customer-years are the
expensive kind** — they cost the same to settle and carry no renewals.

**So depth is not blocked by the budget. It is blocked by WHEN the budget is spent**, and that
is a curriculum question rather than an engineering one, which is exactly why it is yours.

---

## The four options, priced

### Option 1 — A founder book. **My recommendation, at 80.**

Raise `accounts_held_at_start` from 18. The parameter already exists and is already threaded
through `plan_growth_campaign`.

| founders | their cost | left for growth | resulting book | accounts ≥5 renewals |
|---|---|---|---|---|
| 18 (today) | 180 c-y | 1,020 | 264 | **37** |
| 50 | 500 c-y | 700 | ~215 | **~65** |
| **80** | **800 c-y** | **400** | **~180** | **~95** |
| 120 | 1,200 c-y | 0 | 120 | 120, and no growth story at all |

**Cost in wall-clock: none.** Same customer-year budget, same 12.4-minute settle, same 30-minute
cadence. **Cost in width: 264 → ~180 accounts.** **Cost in fidelity: none that I can see** — a
supplier launching by acquiring a portfolio and then growing organically is an ordinary GB
shape, not a convenience.

**What it buys:** ~95 accounts at 9–10 renewals apiece, against today's 37 at 5+. That is the
difference between a book where nothing compounds and one where a per-customer pricing policy
has something to compound *on*.

**What it costs you that matters:** the growth story gets quieter. 241 funnel wins is currently
evidence that acquisition works; at 80 founders it is ~100. If the acquisition funnel is the
capability you want demonstrated, this option dilutes it — and that trade is the reason this is
yours and not mine.

### Option 2 — Raise the settlement budget. Buys both, and costs the publish cadence.

1,200 c-y ≈ **12.4 minutes** to settle, leaving 17 of the 30-minute cycle for the publisher's
gate. The relationship is superlinear (the recorded figure is 3.91, not 1.0), so 2,400 is
**~25 minutes** and leaves 5 minutes for a gate that needs 17. **Infeasible at the current
cadence.**

It becomes feasible at a **60-minute publish cadence**, and I should say plainly that this may
cost less than it sounds: the weekend stand-down was resolved on 2026-08-24 when two full-cadence
days moved zero levels, so publish frequency was never what was binding progress. This is the
only option that buys depth *and* keeps width.

**Cost: publish cadence 30 → 60 minutes.** Everything else unchanged.

### Option 3 — Shorter contract terms. Cheapest, and I recommend against it.

182-day terms double renewals per customer-year at **zero** settlement cost. It is by far the
cheapest depth on the table.

**It is also a baseline change made for the company's benefit, which R13 forbids.** The baseline
world may change only for fidelity-to-reality reasons decided blind to company P&L, and the GB
domestic norm is a 12-month fixed term. I can see no fidelity argument for 6 months that I did
not construct backwards from wanting the renewals. Listed because it is real and cheap, and
flagged because taking it would put a thumb on the scale in a way that is hard to see later.

### Option 4 — Extend the window backwards. Expensive, and the foundation thins.

2016 → 2012 adds four years of tenure to every founder. It costs four more years of
customer-years for the whole book (roughly +40% on the budget, so it needs Option 2 first), and
the settlement-data foundation is thinner before 2016. **Not recommended now**; it becomes the
natural follow-on if Option 2 is taken and depth is still short.

---

## What is bounded until this lands, so it is not discovered later

Every comparison that depends on compounding is bounded by the 37, and this includes the
per-customer pricing thesis itself. The published baseline comparison — flat £153,245 against
per-customer £157,913, the choosing worth −£175 with an error bar 25× the estimate — is bounded
**twice**: once by C2 (the market cannot react) and once here (nothing has enough renewals to
compound). Those are separate bounds and fixing either alone does not lift the other.

**These interact, and it is worth knowing which order costs less.** P1 makes the world press;
P9 gives it something to press on for long enough to matter. If both are taken, **P9 should
land first or alongside** — a competitor arriving against a book where 227 of 264 accounts
cannot compound would be measured on a book that cannot show the effect, and that is a
recalibration nobody wants to pay for twice.

---

## ADDENDUM (2026-08-28, added when `A48` reached L2) — the ground this is argued on has changed

This does not change the menu, the costs, or my recommendation, and it does not settle the
question. It changes what the question is *about*, and leaving that unsaid would have let you
decide on a framing the mission had already superseded.

**Under the old mission, width was the growth story and depth was the science.** A wider book
was more customers and a bigger number; depth was what you bought to make a comparison
readable. That is the trade the four options above are priced against.

**Under the mission of 2026-08-28 they are two halves of one asset.** The enterprise value is
the automated *method* of finding customers we can create value for. Width is the **finding**
half — how reliably the machine locates a customer worth having. Depth is the
**creating-and-sharing** half — whether the relationship it opened actually compounds value for
both sides. So Option 1's "cost in width: 264 → ~180 accounts" is no longer a growth cost paid
for a science benefit; it is **buying resolution on one half of the asset by giving up
resolution on the other.**

That reframing is not rhetorical, because the instrument now exists to feel it. `A48` landed
`tools/run_value_cycle_ab.method_skill()` — a rank statistic asking whether the arm's own
per-customer price ranks the *joint* value created, household plus company, per priced term.
It is the first figure in this project that measures the method rather than the book. And it is
bounded by exactly the number this document is about: it scores priced decisions, clustered on
the handful of accounts with renewals, so its confidence interval is wide for the same reason
every other compounding comparison's is. **`A46` is upstream of `A48` being worth much**, and
the A48 FRAME says so in its own section 5 rather than discovering it later.

**What this does NOT do is decide it.** Both halves are real, the trade between them is genuine,
and which resolution is worth more is a curriculum judgement under R13 — yours, named and
versioned, never mine. I am recording that the ground moved, as the finding that raised it
asked me to.

---

## What I need from you

One word on which option, or a different one. If nothing comes back, **I take Option 1 at 80
founders** as the reversible default and record it — it needs no cadence change, no baseline
change, and no new parameter, and it is a `git revert` away. Silence is validation; I would
rather you overrule a running experiment than approve a stationary one.

`A46_book_depth_is_a_curriculum_question` is `loop_stage: build` and `blocked_on: null`
deliberately: the DECISION is yours, and the priced menu you need in order to take it was mine
to produce. Parking the atom on your answer would have made the thing you are waiting for
unbuildable — which is how a real reserved-class item and a permission ceremony end up looking
identical.
