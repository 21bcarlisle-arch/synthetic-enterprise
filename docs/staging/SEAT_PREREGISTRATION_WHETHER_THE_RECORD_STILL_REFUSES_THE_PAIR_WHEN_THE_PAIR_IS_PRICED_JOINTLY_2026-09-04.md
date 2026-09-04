**Severity:** LATENT · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** none — Lane 0 delivery

# PRE-REGISTRATION — whether the record still refuses the pair when the pair is priced jointly

**Filed:** 2026-09-04, delivery seat, Lane 0, claim
`departure-level-emerges-from-the-household-not-the-solver`, at `7c9f9131e`, **before** the joint
reading was written as code and before any year other than 2017 was computed.

Graded in `SEAT_FINDING_THE_LEVEL_IS_CLAMPED_AND_THE_MECHANISM_UNDER_IT_IS_COMPRESSED_NOT_MISDIRECTED_2026-09-03.md`
§12, beside the result.

---

## What is being measured, and why §11 left it owed

§11 closed with two things owed. One is a sourcing job (φ, the external share of active fixed-term
renewals). The other is not:

> *"**§9's and §10's readings must be re-run jointly, not separately.** Result 2 above is only
> visible when the hazard and the share move together, and each of those readings holds the other's
> subject fixed by construction."*

§11 took the first step and it took it with a mixed pair. `where_the_worlds_point_falls`
computes `phi_admitting_required` by feeding §9's `required_hazard` — which was solved **holding the
world's own, lower, SVT share fixed** — into a composition evaluated at the **published** share. That
is not "both repairs land". It is one repair sized to close the whole gap alone, applied on top of
another repair that has already closed part of it. It double-counts by construction, and the
double-count is what produced §11's result 2 (*"the record refuses the pair"*) and its **REFUSED**
mark against 2017.

The self-consistent question has never been asked:

> At the published SVT account-day share, with the renewal route rescaled to its complement, what
> hazard per SVT-account-year does the world still need — and **is that** admissible against the
> record's interval computed at **the same share**?

§10 already publishes the first half as `hazard_multiple_still_required_at_band_low`. Nothing
multiplies it by the world's hazard and takes the product to `phi_admitting`.

## The disclosure this pre-registration owes

**I have done 2017 by hand, from the two committed artefacts, before writing this file.** Filing a
prediction while concealing that would make the document worthless. So, all-domestic basis, published
share at its high endpoint, `renewal_rescaled`:

- world hazard 0.13266 × §10's still-required multiple 1.507 = **`H_joint` ≈ 0.1999**
- §11's admissible interval at 2017, all-domestic: **[0.0029, 0.2260]** — `H_joint` is INSIDE it
- §11's own table marks 2017 **REFUSED**, because §9's 0.2841 is above 0.2260

So I know at filing time that at least one year's verdict flips, and I know which. What I do not know
is the other four comparable years, the as-published basis anywhere, the φ intervals, or whether the
flip survives the `renewal_held` accounting.

## The predictions

**P1 — arithmetically forced, filed weak on purpose so the strong ones are not judged by it.**
`H_joint < H_required(§9)` in every comparable year and on every basis, by approximately the
composition multiple `s_world / s_published`. This is a consequence of the definitions and I claim no
credit for it. It is here because if it comes out FALSE the implementation is wrong, and that is
worth knowing before the interesting predictions are read.

**P2 — 2017's verdict FLIPS from refused to admissible, and it is the only flip.** Derived by hand
above for the all-domestic basis, so it is disclosed rather than predicted there. What is predicted:
it flips on the **as-published** basis too (§11's as-published admissible interval at 2017 is
[−0.027, 0.246], and `H_joint` on that basis will be larger than 0.1999 because the published share
is smaller — I predict it lands in 0.21–0.24 and stays inside, i.e. the flip survives but narrowly).
And I predict **no other year flips in either direction**, because §11 already found 2018, 2019, 2023
and 2024 admissible at §9's *higher* required hazard, and lowering a value that is already inside an
interval whose floor is near zero cannot push it out.

**P3 — §11's result 2 is REFUTED as stated, in all five comparable years.** *"Applied together at
2017 they overshoot the record, needing φ of −0.227 to −0.146 (as-published) or −0.360 to −0.270
(all-domestic). The record refuses the pair."* I predict the jointly-priced pair needs **φ ≥ 0 in
every comparable year on both bases**, so the record refuses the pair in none of them, and that the
2017 φ interval comes out in **[0.00, 0.15]** — low, positive, and therefore a constraint on φ rather
than a refusal of it. The record turns out to admit both repairs landing together; what it says
instead is that they leave very little room for the fixed route.

**P4 — the joint requirement lands inside or below the published SVT recent band (0.15–0.20) in at
least 3 of the 5 comparable years**, where §9's required hazard was above 0.20 in three of five and
its required multiple ran 1.46–2.14. If this holds, the honest headline is not *"the world needs 1.7×
its own source"* but *"the world needs its own source, at the record's composition"* — and §9's
1.67×/1.71× figures are then measurements of the share gap wearing the hazard's name. I file the
converse explicitly: if `H_joint` is still above 0.20 in most years, composition is a second-order
correction and §9's headline stands.

**P5 — the two accountings do not change any verdict.** `renewal_held` is arithmetically incoherent
and more generous; I predict it moves `H_joint` down by under 0.01 everywhere and flips nothing, so
the result cannot be picked by choosing an accounting.

**P6 — no new refusal appears.** 2020 and 2021 stay refused for want of a published share, the
denominator stays 5 of 7, and `EXTERNAL_SHARE_OF_ACTIVE_RENEWALS` stays `None`.

## The constraint this inherits, unchanged

No constant is picked. No solver aim point moves. `YEAR_LEVEL_ANCHOR` is not edited. The reading is
taken at `NO_LEVEL_CORRECTION` on the committed capture, and the published share stays a CHECK on
output and never an input. §4's constraint 4, an eighth time.

## What would make this pre-registration worthless

If the joint hazard is evaluated against an admissible interval computed at a **different** published
share endpoint or a different basis from the one that produced it — that is the mixed pair this whole
reading exists to correct, and doing it again while claiming to have fixed it would be worse than not
running it. If only the years that flip are reported. If P3 is graded against a φ range widened after
the numbers were seen. The grading in §12 must name all five comparable years on both bases, and must
say plainly if 2017's flip is the only substantive movement — in which case this reading corrects one
sentence of §11 and changes nothing about where the repair is aimed.

— Delivery seat, 2026-09-04.
