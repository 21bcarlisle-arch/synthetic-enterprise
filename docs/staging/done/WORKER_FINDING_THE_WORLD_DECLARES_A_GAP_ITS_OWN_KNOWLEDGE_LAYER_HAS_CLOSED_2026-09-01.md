# [WORKER FINDING] The world declares a gap its own knowledge layer has closed

**Severity:** LATENT · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** `A46_the_priced_menu`
**Found:** 2026-09-01, while deciding whether to model prepayment or exclude it, by asking where the
two-member `PaymentChannel` got its authority.

## Class registration

Belongs to `no_caller_and_never_runs`. This is the £55-versus-£150 shape at its second address: a
sourced anchor sitting in `docs/market_research/` that reaches no code, while the code that needs it
carries a comment saying the anchor does not exist.

## The two statements, both in this repository

`simulation/household_segments.py:279-288`, on why `PaymentChannel` has two members:

> *Anchor: DESNZ "Quarterly Energy Prices: June 2026" commentary, "Payment methods" section (fetched
> 2026-07-08) — Direct Debit was 72% of standard electricity customers and 75% of gas customers…
> **The remaining ~25-28% (prepayment + standard credit combined) has NO published sub-split in the
> fetched commentary text (genuine registered gap, not guessed)** — so that remainder is collapsed
> into one STANDARD_CREDIT bucket here rather than inventing an unanchored three-way split.*

`docs/market_research/dd_attribution_confound_w2_10.md:22-24`, under the heading
**"Anchors [L] (real, sourced — never fabricated)"**:

> *Payment-method mix: **~74% direct debit / 13% standard credit / 13% prepayment** (Ofgem, 2026).
> Recorded in the W2_10 DISCOVER pass (`docs/design/maturity_map.yaml`). → `_TARGET_DD_SHARE = 0.74`.*

**The sub-split the enum says is unpublished is recorded, as a real anchor, one directory away** —
and was republished this morning in `docs/market_research/what_bill_shock_is.md`, the page the
director asked for before any more measuring.

## What is and is not being claimed

**The comment was not wrong when it was written, and it is not lying now.** It is scoped to *its*
source: the DESNZ commentary genuinely does not carry the sub-split, and the module says "in the
fetched commentary text", which is exact. The defect is narrower and more familiar than dishonesty:

**the module's stated REASON for its shape — "rather than inventing an unanchored three-way split" —
no longer holds, because an anchored three-way split is available in this repository.** A reader
arriving at that comment concludes the world cannot model prepayment. It can.

Nothing points from the anchor to the code, or from the code to the anchor. `_TARGET_DD_SHARE = 0.74`
is the only part of that anchor that reached anything; the 13/13 half of the same sentence reached
nothing, and the module that would consume it records the subject as an open gap. **One page,
containing both the sourced figure and, by omission, the reason nobody looked.**

## What it costs, concretely and today

Our book is **0% prepayment against a published ~13%**, and the non-DD remainder is folded into
standard credit — so measured on the live book, 251 accounts: **68.1% direct debit (171) / 31.9%
standard credit (80) / 0% prepayment.** That makes our standard-credit population **2.5× the
published share**, and because bill shock is *defined* by payment method rather than merely
correlated with it, roughly half of the 912 events in the published `bill` population are prepayment
households wearing a standard-credit label — households the established definition says have **no
bill to be shocked by at all**.

That is measured and published in
`WORKER_PREREGISTRATION_WHAT_EXCLUDING_PREPAYMENT_ON_THE_SURFACE_MUST_SHOW_2026-09-01`, and it is
why that pre-registration takes the disclosure route rather than the filter route: **you cannot
exclude a population that is not labelled.**

## What is owed

1. **Correct the comment where it stands**, so the next reader is not told the gap is open. The
   fold can remain — it is a legitimate simplification — but its stated reason must become "a world
   change we have not made", not "an anchor that does not exist".
2. **Adding the third channel is now anchored, and is a WORLD change**: it alters which households
   exist and what they do, and `payment_channel_for_customer` already feeds `arrears_engine`,
   `final_bill_outcome` and `sim_satisfaction`, and through them churn and the P&L. Under the
   baseline/curriculum wall that is decided for fidelity reasons, named and versioned in a file the
   director reads — not by a worker tick. **This finding makes it drawable; it does not authorise it.**
3. **Neither is done here.** Both are separate from the bill-shock commits this was found inside.

## What this finding does not claim

Not that the DD share is wrong — 68.1% against ~74% is close and its residual is the absent third
channel, not a mis-fit. Not that the binary fold was a mistake: `dd_attribution_confound_w2_10.md`
declares it in terms, for the question it was asking, which was DD-discount confounding. The claim
is only that **the code's reason for the fold cites an absence its own knowledge layer has since
filled, and nothing in either file can notice.**
