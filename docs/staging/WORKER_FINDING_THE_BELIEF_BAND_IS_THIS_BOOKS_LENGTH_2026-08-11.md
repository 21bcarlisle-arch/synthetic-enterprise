# H27 Expert Hour #12 — the belief band is this book's length, and the scored company is off the end of it

**Date:** 2026-08-11 · **Atom:** `H27_payment_belief_gap` (HARDEN, self-refill draw 2→3)
**Subject:** `tools/couple_w2_11_d5.py` · **Reshape minted as:** `D30_the_belief_band_is_this_books_length` (L0)
**Held at L2.** Twelve Hours, twelve defects, and this Hour changed the instrument again.

---

## The lead this took, and why it was the right one

Hour #11 left three leads. Lead 2 was the census:

> The census of confounder-removing constants is now two of an unknown number.
> `DD_FAILURE_WINDOW_DAYS = 400` (D27) and `AS_OF_BUFFER_DAYS = 30` (D29) were each found by
> tripping over them. `BILLING_CYCLE_SPREAD_DAYS`, `N_PERIODS` and the reconciliation grace window
> have not been put through the same question.

Both constants carry a comment saying they were chosen to *remove a confounder* — "generous on
purpose", "comfortably past". Both reasons are sound. Both are also silent **resolution** decisions,
and each was found only when an Hour happened to sweep across it. There was no census: the set of
harness constants bounding what this instrument can resolve was being enumerated **by accident, one
Hour at a time**, and nobody could say how many were left.

---

## The finding, measured not asserted

`n=300`, seeds 7/11/23, **every run identical on all three**.

The two belief dimensions resolve a company memory error **only between the youngest and the oldest
invoice age this book presents at `as_of`**. That interval is `[30d, 92d]` — a band **62 days wide**
— and it is not a sensitivity of the instrument. It is arithmetic over four harness constants:

```
youngest = AS_OF_BUFFER_DAYS                                          # 30
oldest   = AS_OF_BUFFER_DAYS
         + PERIOD_SPACING_DAYS * (N_PERIODS - 1)                      # + 42
         + BILLING_CYCLE_SPREAD_DAYS - 1                              # + 20  = 92
```

Predicted from the constants alone and cross-checked against the built book on every seed: measured
youngest 30, measured oldest 92, on 7, 11 and 23.

### 1. The upper edge was attributed away from the harness entirely

D29 gave the register a saturation **owner per edge** — the right shape — and filled it in:

| edge | D29's owner | what actually sets it |
|---|---|---|
| below (`-371`) | `D29_the_as_of_buffer_floors_the_memory_grid` | `AS_OF_BUFFER_DAYS` ✓ |
| above (`-308` / `-309`) | `D27…` — *"the company's memory outruns the book"* | `N_PERIODS`, `PERIOD_SPACING_DAYS`, `BILLING_CYCLE_SPREAD_DAYS`, `AS_OF_BUFFER_DAYS` |

"The company's memory outruns the book" is a **restatement, not an attribution**. The book stops at
92 days because `N_PERIODS` is 3 and `PERIOD_SPACING_DAYS` is 21 — two constants no Hour had asked.
Naming the company as the owner of that edge attributes the **harness's own calendar** to the company
being graded, which is the same shape D25 closed on the ageing dimension one register over.

And the arithmetic was already written down. The entry's own `own_why`, two lines below the owner
field, says: *"the book's oldest observed failure is 92d old at `as_of` (N_PERIODS x
PERIOD_SPACING_DAYS + AS_OF_BUFFER_DAYS + the cycle spread)"*. It was **observed in prose and no rule
was built from it** — Hour #11's *a lead is not a control*, one register field over, and the eighth
sighting of that class.

### 2. The instrument cannot resolve the company it scores

The scored company holds `DD_FAILURE_WINDOW_DAYS = 400` days of memory. The band tops out at 92. So
**every published `belief` and `belief_population_mix` figure is read 308 days inside the saturated
tail**, at a point where the one company parameter those two dimensions depend on is inert by
construction.

That is not an external-realism claim needing a source — it is arithmetic on this repo's own two
constants. A reader of either belief number is reading a measurement taken off the end of its own
scale.

**R12: nothing was tuned.** No published number moved in this commit. What moved is what the
instrument admits about itself.

---

## What was closed at the class (R10), and what was not

**Not fixed on sight.** Giving the scored population a book whose invoice ages straddle a memory a
real supplier might plausibly hold — more periods, a longer spine, or an `as_of` that does not start
30 days past the last event — moves **every published belief figure on this pair**, so the reshape is
minted as atom **`D30_the_belief_band_is_this_books_length`** at L0.

Closed here:

1. **`SCENARIO_CONSTANT_CENSUS`, fail-closed on a derived keyset.** The subject is every module
   constant `build_scenario` reads, taken off its **AST** (`scenario_constants`, asserted never to
   read the census — deriving the subject *from* the census is the D28/D29
   asked-where-it-answered class). A ninth scenario constant left uncensused **raises**, instead of
   waiting for an Hour to trip over it. That is the difference between a census and a tally.
2. **The effect is measured, never declared.** `bounds_resolution` and the edge each constant sets
   are answered by **perturbing the predictor one day** and recording which edges move — both
   directions, so a constant that silently enters the span arithmetic cannot be declared inert, and
   one declared to bound resolution gets no free credit either.
3. **The predictor is independent and cross-checked.** `predict_event_age_span_from_constants` takes
   no records, no seed and no draw (asserted against its AST) and is compared against the band the
   **built** book presents, on every seed. Disagreement raises: an ownership claim about a band
   nobody presents is worthless.
4. **`_check_edge_owners_are_censused`** — the defect above, as a rule. A saturation edge owned by an
   atom the census does not put on that edge now fails. The upper-edge owner moved `D27` → `D30` on
   both belief entries; `D27` keeps `own_debt_atom`, because it owns where the *scored company* sits
   (the 308d of headroom), which is a different fact from where the *edge* is.
5. **Stamped at source, note AND components (D22).** The band, its owning constants and the scored
   company's headroom travel with both belief figures — the ledger writer, the live wiring and the
   dashboard read `components` and never the prose.
6. **A live-population guard.** `score_triad` also scores `run_phase2b` books these constants do not
   build. Quoting this scenario's `[30, 92]` over somebody else's population would be publishing one
   book's limit against another's figure, so the caveat reports the band it **measured** and declines
   to attribute it to the constants unless they demonstrably describe the book in hand. Proven on the
   flat book (`cycle_spread_days=1`), where the band is `[30, 72]` and the attribution is withheld.

**Declared residual, not implied away.** The census answers *which constants set the band*. It does
not say *what the band should be* — that is D30's own question, and it needs a view on what memory a
real supplier holds, which this harness does not have offline.

---

## R15, both ways

**6 census/register mutations** — an uncensused constant; a census entry outliving its constant; a
band constant declared inert (parametrised over all four); an inert constant declared to bound the
band; a band constant with no owning atom; an edge owner outside the census (this is the pre-Hour
state of both belief entries, and it fires with exactly 2 violations).

**Plus source-side mutations** — the span arithmetic drifted off `build_scenario` in each of its four
terms, caught by the cross-check against the built book; and an empty book, which must fail rather
than read like an agreeing one.

---

## Hour #13 leads, in order

1. **`PAYMENT_TERMS_DAYS` is censused as inert on the age band and it bounds a different
   dimension** — detection latency (D23/D24). The census proves it sets no *invoice age*; nobody has
   asked whether the **latency** band has the same shape, i.e. whether a second census is owed on the
   grace window and the issue-date spine.
2. **The interior collapses still have no owner of their own** (Hour #11's lead 1, untaken).
   `{-358,-357,-356}`, `{-333,-332}`, `{-331,-330}` are quantisation *inside* the sighted region, and
   they point at D27 because the generic `own_saturation_atom` field does — the same
   wrong-owner shape this Hour just closed on the edges, one field over.
3. **The two leads Hour #8 left and no Hour has taken:** the pinned generated value
   `assert c["n_recon_detected_undated"] == 0`, and whether the other dimensions' normalisation notes
   have the same gap between what they DENY and what they ESTABLISH.
