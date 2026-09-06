**Severity:** BLOCKING · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** A49_the_ceiling_comes_before_the_programme_on_r3_and_r4

# R1's magnitude was never a coverage problem, and the rung that fixes it had been measured and never landed

**Found:** 2026-09-07, delivery seat, claim `r1-ceiling-coverage-is-what-buys-a-magnitude`.
Repaired in `tools/r1_inference_ceiling.py`, controlled by four tests in
`tests/tools/test_r1_inference_ceiling.py`, all four mutation-proven. Pre-registered before any
measurement: `docs/staging/PREREG_WHICH_FIELD_COLLAPSES_THE_R1_PAIR_BOOK_2026-09-07.md`.

---

## The direction, and what was actually true

The drawn work said: *populate the pair fields on every household so R1's pair rung can carry a
three-way split*, naming `perceived_bill_saving_gbp`, `portfolio_premium_pct` and
`mean_recent_margin_rate` as **the fields that collapse 164 households to 69**.

Measured on `run_output_5a256cd6d_20260906T214423Z.json`, which is the newest book:

| field | households | scope |
|---|---|---|
| `unit_rate_gbp_per_mwh`, `svt_rate_gbp_per_mwh`, `rate_vs_svt_pct`, `company_eac_kwh`, **`mean_recent_margin_rate`**, **`portfolio_premium_pct`** | **164** | account_state |
| `company_churn_estimate`, `resentment_score`, **`perceived_bill_saving_gbp`** | 69 | decision_only |
| `expected_term_margin_gbp` | 56 | decision_only |
| `discount_pct` | 35 | decision_only |

**Two of the three named fields already cover the whole book.** They were lifted into
`account_state_log` on 2026-09-06 and the direction's diagnosis was written against the state
before that landed. Only `perceived_bill_saving_gbp` sits at 69.

**And populating that one would be a defect, not a fix.** `simulation/run_phase2b.py:1420` refuses
it in terms, deliberately: `company_churn_estimate`, `resentment_score` and
`perceived_bill_saving_gbp` exist only where a renewal window opened, and *"manufacturing any of
them for a term that had no decision would be inventing the coverage rather than recording it."*
That refusal is right. A household that never renewed has no renewal to perceive a saving against.

So the ask as written — populate the fields — was **already done where it was honest, and
forbidden where it was not.** The prediction that this would move the magnitude is refuted.

## What the refusal was actually about

**A ranked sweep reports its WINNER, so the rung's `n` is the winner's `n` and not the book's.**
The winner on this book is `perceived_bill_saving_gbp x portfolio_premium_pct` at n=69. The book is
164. The magnitude refuses at 5.00 households per cell, and its refusal message reads *"this rung
gives 5.00 per cell"* — which a reader takes as a statement about the book. It never was. **No
amount of coverage on any other field can move it**, because the field that wins is the field that
sets the population.

## The repair, and why it could not simply be copied

The fix was designed and measured on 2026-09-06 — declare each observable's scope in the source
**before any run**, then publish a second rung restricted to the fields the company holds on every
account. It was never landed. Two live comments already cite
`tools/r1_inference_ceiling.py::OBSERVABLE_FIELD_SCOPE` as though it existed
(`simulation/run_phase2b.py:1427`, `company/pricing/renewal_rate_chain.py:124`); at HEAD it did
not. **A dangling reference in two modules, pointing at a mechanism that lived only in one
worktree's uncommitted copy.**

That copy could not be adopted. It is a **194-line-shorter, divergent lineage**: it carries
`OBSERVABLE_FIELD_SCOPE`, `whole_book_fields`, `field_provenance` and `honest_point_estimate`, and
it is missing `three_way_split`, `three_way_null`, `magnitude_verdict`, `global_folds`,
`SPLIT_FOLDS`, `MIN_FOLD_HOUSEHOLDS`, `verdict_across_runs` and `shrunk_toward_the_null` — the
entire magnitude machinery A49 gates on. Landing it would have deleted the thing it was meant to
supply. Ported **additively** onto HEAD's lineage instead, symbol set compared both ways first.

## What it now says

The whole-book rung runs the **same** three-way split, on the **same** global fold assignment, over
the six `account_state` fields (15 pairs, n=164):

```
three-way split, pair rung     : REFUSED (-0.0452 under-powered, NOT an estimate)
  fit fold holds 5.00 households/cell (needs 8)
three-way split, whole book    : +0.2513   vs its own noise floor +0.1628 (p=0.01)
  fit fold holds 13.75 households/cell (needs 8) -- populations: True
```

**R1 has a magnitude for the first time: +0.2513, on 164 households, 55 on the fit fold, 13.75 per
cell.** The direction predicted ~55 per fold and ~14 per cell. **Its arithmetic was exactly right
and its mechanism was wrong** — the coverage it asked for was already bought, and what was missing
was a rung that could use it.

## The tension, published rather than resolved

The whole-book rung's **ceiling does not clear its selection-corrected null** (best pair
`rate_vs_svt_pct x mean_recent_margin_rate`, held-out +0.1963, p=0.4726), while its **magnitude
exceeds its own noise floor** (p=0.01). These are not in contradiction — the null for a selected
maximum is inflated by the search, and the three-way estimate removes that inflation, so it is
graded against a tighter floor — but they must be read together and neither may be quoted alone.
**Both rungs are published side by side, because a rung reported alone is a rung chosen.**

Note also that the winning whole-book pair scores +0.1963 held-out against +0.4737 in-sample: it
does NOT show the overshoot signature the 69-household winner does (+0.5760 against +0.1977).

## What this does NOT license

- It does not say R1's ceiling is real. On the whole-book rung it does not clear.
- It does not make the all-candidate rung's magnitude available. It is still `None`, correctly, and
  `magnitude_three_way_split.estimate` still refuses.
- **A49 must decide, explicitly and in view, which rung it gates R3 and R4 on.** The two answer
  different questions over different populations. Gating on whichever one has a number is exactly
  the outcome-driven selection this whole mechanism exists to prevent. That decision is the next
  piece of work and it is handed on, not made here.

## Controls, and that they can fail

Four new tests, each poisoned and each killed by the intended control (baseline green first, target
presence asserted before every patch, so no survival is a patch that never applied):

| mutation | killed by |
|---|---|
| `whole_book_fields` returns `list(fields)` — no filter | scope-keys + decision-only-winner |
| `.get(f, ("account_state",...))` — fails OPEN on an undeclared field | scope-keys |
| `whole_book_fields` returns `[]` | scope-keys + decision-only-winner |
| a field loses its scope declaration | partition + scope-keys |
| `field_provenance` keys on the supply-point leg | provenance |

The sharpest is `test_the_whole_book_restriction_keys_on_DECLARED_SCOPE_and_never_on_coverage`: it
puts the two possible criteria in **disagreement** — a `decision_only` field with more households
than an `account_state` one — and asserts the declaration wins. A restriction that followed coverage
would be a second bite at the search and would look identical on this book.
