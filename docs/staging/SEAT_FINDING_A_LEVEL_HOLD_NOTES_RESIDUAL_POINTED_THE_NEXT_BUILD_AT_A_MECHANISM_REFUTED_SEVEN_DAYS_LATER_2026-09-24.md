**Severity:** BLOCKING · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** `PB4_engagement_separated_from_elasticity`

# FINDING — a level-hold note's residual named, as a build gap, a mechanism this repo refuted seven days after the note was written

Drawn on the scheduled tick of 2026-09-24 as LANE 1 BUILD: `PB4_engagement_separated_from_elasticity`,
lane `W2_customer_generator`, dial 45, level 1→3, `loop_stage: build`. The draw carried the
instruction *"LEVEL HELD BEFORE — 4,777 B of recorded reason why 1→3 did not follow last time. READ
IT BEFORE BUILDING"*, which is the instruction that surfaced this.

Answers `docs/staging/records/SEAT_PREREG_WHETHER_THE_OFFER_CONDITIONAL_SEAM_MOVES_ANY_PUBLISHED_FIGURE_2026-09-24.md`.
All three predictions **confirmed** — recorded below beside the predictions, not instead of them.

## Severity, and why BLOCKING rather than LATENT

The note is the *first thing the draw instructs a session to read*, and it names the refuted
mechanism as the atom's remaining build work. The next session to draw PB4 and do as it is told
builds a bill-level threshold into the world's engagement gate. That is not a hypothetical failure
mode: **the identical defect is already in the tree on the company side of the wall**
(`company/crm/churn_model.BILL_STRESS_THRESHOLD_GBP = 3000.0`), and the 2026-09-22 pass that
refuted it deliberately left it standing as a named gap rather than re-picking it. A second
implementation on the world side would have been the VAT shape again — one claim, two
implementations, refuted in one and live in the other, with nothing able to notice.

## The defect

`PB4`'s `level_hold_note` (written 2026-09-15) states residual (b):

> the brief's OFFER-CONDITIONAL clause, which is unbuilt and is not a control gap but a build gap —
> `active_renewal_probability_for_customer` takes a customer id and NO comparison offer, so
> engagement is a static per-household probability rather than a gate that a bill shock, a renewal
> letter **or a price rise past a threshold** opens

Three claims are carried as one verdict, and they grade differently.

**1. "a price rise past a threshold" — REFUTED, seven days after the note was written.**
`docs/market_research/is_there_a_bill_level_at_which_switching_rises.md` §6 (2026-09-22):
a knee in bill level is the wrong SHAPE and bill level is the wrong VARIABLE. Ofgem/BMG (n=3,235)
put the spend-to-switching Spearman at **−0.07 to +0.05** and the publisher says in words that
spend has "a very limited impact on how consumers evaluate prospective deals". The one
population-wide natural experiment runs the other way: DESNZ QEP 2.7.1 has switching **15.57%
(2021) → 3.06% (2022)** while every household's bill rose.

**2. "a renewal letter" — ALREADY BUILT, and was when the note was written.**
`active_renewal_probability_for_customer` is consulted *only* at a fixed-term anniversary
(`simulation/renewals.py:211` gates on `not first_term and tariff_type == "fixed" and segment ==
"resi"`), and `ftc_withdrawn_at` forces the boundary passive when there was no deal to take. The
gate was already event-conditional. What it was not is **offer**-conditional.

**3. "a bill shock" — THE ONE LIVE CLAIM, and it splits again: the TRIGGER is defined and the
AMPLITUDE is not.** `what_bill_shock_is.md` settles the trigger per population — for the ~74% on a
level direct debit the shock is a material change in the **payment**; for the ~13% on standard
credit the **bill itself** is the shock — and this module already draws that channel, so the world
can say which definition applies to whom. **No published source gives the amplitude.** The closest
are Ofgem CIM w6 Table 56's arrears 1.6× and bill-difficulty 1.7×, and they cannot be substituted:
both are ratios over a binary **state** rather than responses to an **event**, both are the weakest
rows in that table, and that source's own §5 records that nothing separates them from the
payment-method banner — **which is the 3.4× this module already multiplies in**. Stacking them
would multiply two marginals known to be confounded and call the product a model.

## What was built, and what was deliberately not

Landed: the **structure**, with the answer honestly absent — which is what the director's
cul-de-sac warning the note itself cited actually asks for (*"built so that P1 changes its ANSWERS,
not its STRUCTURE"*).

- `active_renewal_probability_for_customer(customer_id, bill_shock=None)` — the seam exists.
- `BILL_SHOCK_ENGAGEMENT_MULTIPLIER: float | None = None` — a declared absence on the
  `tools.published_route_split.SVT_INTERNAL_CONVERSION_RATE` pattern, with `BILL_SHOCK_ENGAGEMENT_GAP`
  carrying the reason beside it so a refusal can quote it.
- A shocked household is **refused, with the gap named**, rather than silently handed the
  unmodified probability. That pass-through is the fail-open that matters: it would publish the
  claim *a bill shock does not change whether a household shops*, which nothing establishes and
  which the director's own P4 asserts is false.

Not built, deliberately: any amplitude. Closing the gap by picking a number to clear the refusal is
the forbidden operation, and the refusal's own message says so.

## Evidence

**P1 — the engagement path contains no bill-magnitude term. CONFIRMED.** Measured by AST over the
six functions in the path, comparing executable statements only with docstrings stripped: zero hits
for price/bill/consumption/kwh/spend/cost/tariff. The substring scan alone would have reported
false hits — the docstring quotes the director's "bill shock" line.

**P2 — the seam moves no published figure, identically. CONFIRMED.** 3,000 households, before and
after, `sha256 986303100ac6f27feed8314fed505cf6d369f94be03d790a2d9943b2b12eb03e` both sides, mean
0.34939, 9 distinct values. `bill_shock=False` identical to the unasked call. **No level moved
blind to the director's baseline**, which is the R12 property this had to clear.

**P3 — no control governed the world side. CONFIRMED.** Eight test modules reach the engagement
path; none coupled it to a bill term. The 2026-09-22 refutation landed against the company-side
twin only.

**Four mutations, each caught by the leg written for it** (checked by name, because a mutation
caught by a different leg is the flattering reading):

| mutation | caught by |
|---|---|
| delete the refusal (fail-open restored) | `…_a_shocked_household_is_refused_and_the_refusal_names_its_reason` |
| delete `scaled *= …` (mechanism gone, refusal remains) | `…_the_refusal_is_keyed_to_the_gap_and_not_unconditional` |
| flip the optional arg's **default** to `True` | 6 legs, incl. `…_the_seam_moves_no_answer…` |
| make the refusal **unconditional** (`if True:`) | 6 legs |

The third matters because a control that names `bill_shock` in every leg goes green against the
default-flip — the one mutation that would silently re-level the whole book. One leg calls with a
single positional argument for exactly that reason. The fourth is the anti-tautology arm: it
supplies an amplitude by monkeypatch and requires the refusal to **lift** and the answer to
**move**, keyed to the mechanism rather than to the refusal's wording.

12 passed. `tools.epistemic_verifier` PASS. `ruff --select I001` clean.

## The level did not move, and why that is the right outcome

PB4 stays at **1**. Residual (a) — evidence on a deployed surface — is PB6's and untouched here;
(c) is an expert hour. This pass closed the *build* half of (b) and **converted its remainder into a
research question**: the amplitude by which a bill-shock event raises engagement. That is now the
atom's stated residual, recorded in the `level_hold_note` beside the original text rather than over
it.

## The class, not the instance

A `level_hold_note` is a *current statement about an atom* that the store lets a session overwrite —
but nothing re-asks whether the evidence it rests on still holds. This one was correct when written
and was falsified by a research pass in a different lane six days later, and the two documents do
not reference each other in either direction. **A bounded tick cannot see this**; the note is read
at draw time and the research is read at knowledge time, and only the seat sits in both. Worth
asking whether a note that names a mechanism as unbuilt should carry the sources it checked, so a
later refutation of one of them has something to collide with.
