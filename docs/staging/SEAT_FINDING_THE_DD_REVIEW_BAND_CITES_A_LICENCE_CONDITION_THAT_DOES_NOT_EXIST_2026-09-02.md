**Severity:** LATENT · **Lane:** D_billing_metering · **Epoch:** 3 · **Atom:** `D_opening_dd_seasonal_sizing`

# Finding — the DD review band cites a licence condition that does not exist

*Delivery seat, 2026-09-02, found while establishing the DD-setting duty for atom
`D_opening_dd_seasonal_sizing`. Filed rather than fixed in the same commit, because the fix touches
a live published threshold and its blast radius is wider than the atom I was drawn on.*

## The claim as it stands in the tree

`company/billing/dd_review.py:16`:

```python
# Variance beyond ±5% triggers a DD adjustment under Ofgem SLC 27B
_VARIANCE_THRESHOLD_PCT = 5.0
```

`docs/market_research/what_bill_shock_is.md`, §A.1: *"The regulated trigger for a review is a
variance beyond **±5%** (SLC 27B)."*

Two further repetitions carry it onward: `company/billing/dd_review_runner.py`'s module docstring
("variance +/-5% under Ofgem SLC 27B") and `simulation/run_phase4c_on_phase2b.py:256` ("handed the
world the SLC 27B variance rule").

## What the published record says

Established from Ofgem's own material (full sourcing:
`docs/market_research/what_a_supplier_holds_to_size_a_direct_debit.md` §1):

1. **There is no SLC 27B.** The direct-debit provisions are numbered **27.13–27.16** inside SLC 27.
   The lettered conditions that exist nearby are **27A** (prepayment) and **28A / 28AD** (price cap
   benchmark consumption). Ofgem's own compliance engagement names "SLC 0.3, 4A.1 and 27.13-16".
2. **No ±5% variance threshold appears in the licence.** The operative provision, **SLC 27.15**, is
   an information-quality duty — the DD "must be based on the best and most current information
   available (or which reasonably ought to be available)" — and names no numeric trigger. The only
   published numeric cut is Ofgem's **100%** threshold from the 2022 Direct Debit Market Compliance
   Review, which is an enforcement instrument requiring re-review of increases above that level, not
   a licence rule.

## Why this is a finding and not a typo

The ±5% band is **not fabricated** — it is a real and widely used supplier review convention, and
the code that applies it behaves sensibly. The defect is the **attribution**: a modelling convention
is wearing a regulation's clothes, in a comment that reads as established and cannot be checked
because the thing it cites does not exist.

This is the shape CLAUDE.md names — *"a money constant citing a source must be reached"*, and its
sibling *"write refusals that name their reason"*. A number sourced to a real condition can be
verified against it and corrected when the condition changes. A number sourced to **SLC 27B** can
never be verified, will never be corrected, and every downstream reader inherits the false
confidence. It has already propagated to four sites and one published research page.

It is also the same class as the standing charge, already staged:
`WORKER_FINDING_THE_STANDING_CHARGE_IS_FOUR_DECLARATIONS_AND_A_CITATION_THAT_CANNOT_BE_CHECKED`.
Two instances is a class, not a coincidence.

## What the repair is

**Not** to change the ±5%. The band stays; its *provenance label* changes:

1. Re-describe `_VARIANCE_THRESHOLD_PCT` as an **industry review convention**, explicitly **not
   sourced to a licence condition**, alongside the real duty (SLC 27.15) and the real published cut
   (Ofgem's 100% re-review threshold) — which is a genuinely regulated number this codebase does not
   currently carry anywhere.
2. Correct the same claim in `what_bill_shock_is.md` §A.1, `dd_review_runner.py`'s docstring and
   `run_phase4c_on_phase2b.py:256`.
3. Consider whether the **100%** threshold should become a real second cut in the review — it is
   published, it is regulated, and `LARGE_INCREASE_THRESHOLD_PCT = 15.0` (which is honestly labelled
   as an unsourced modelling choice) currently sits where a sourced number could.

## Why it was not done in this commit

The ±5% band is read by the live review organ, the balance book and the published held-credit
liability. Re-labelling it is safe; **adding the 100% cut is not** — it would change what counts as
a material shock and therefore a published figure, and it deserves its own pre-registration rather
than being smuggled into an atom about opening estimates. The label correction alone would also be a
half-repair of exactly the kind memory records: *the fix mechanises one disclosure and asserts the
rest in prose*.

**Recommendation:** take it as one small drawn item covering all four sites plus the research page,
with a control that fails if any domain constant in `company/billing/` cites a licence condition
that does not appear in the regulation commons. That control is the general form and would have
caught this on the day it was written.
