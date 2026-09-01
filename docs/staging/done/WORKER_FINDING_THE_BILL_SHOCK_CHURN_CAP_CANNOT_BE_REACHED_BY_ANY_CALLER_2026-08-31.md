**Severity:** LATENT · **Lane:** H_harness · **Epoch:** 3 · **Atom:** `OPS10_finding_class_consolidation`

# The 0.95 churn cap cannot be reached by any caller, and a word ending in "ons" was discharging citations

**Found:** 2026-08-31, renaming `saas/churn_model.MAX_CHURN_PROBABILITY` to
`MAX_BILL_SHOCK_CHURN_PROBABILITY` — the last of the five name collisions the domain-constant
register was built to force out. The rename was the instruction. Giving the renamed constant an
origin, which was the other half of it, is what turned up both defects below.

---

## 1. The cap is inert: no live caller can reach it

`saas/churn_model.churn_probability` is `min(0.05 + k * 0.03, 0.95)` where `k` is the bill-shock
count. Reaching 0.95 needs **k = 30**: `(0.95 - 0.05) / 0.03`.

`build_churn_risk` derives `k` by counting `bill_shock_triggered` **billing periods** inside the
twelve months before a renewal. Billing periods are `"YYYY-MM"`, so a twelve-month window holds at
most twelve of them. Printed at the extremes rather than argued:

| input | reachable p |
|---|---|
| `churn_probability(12)` — every month of the year a bill shock | **0.41** |
| `combined_churn_probability(12, CRITICAL, satisfaction=0.0)` — the only other reader, adding its largest payment (+0.20) and satisfaction (+0.10) uplifts | **0.71** |
| the cap | 0.95 |

**The `min()` never binds.** Every test that reaches it does so by calling `churn_probability(100)`
directly — an input no production path can produce. So the constant the director named as one of
his four bad ones ("a 0.95 churn cap") is not merely unsourced: **no run this company has ever
executed could tell you whether the value is right**, because nothing has ever been at it.

This is the `no_caller_and_never_runs` class one level down from its usual shape. The usual
instance is code nothing reaches; this is a *bound* nothing reaches, which is harder to see because
the line it sits on executes on every call.

**Not repaired here, and the reason is R12.** Lowering the cap to something reachable would be
moving a calibrated-looking number so that an arm behaves — the exact move
`tests/company/crm/test_captive_floor_and_market_netting.py` records refusing on the company side
("Move the cap so the arm behaves. That is goal-seeking against a calibrated belief."). What landed
instead is the constant saying so itself, as a NAMED SIMPLIFICATION, with what it would take:

> TO DO IT PROPERLY takes two things this repository does not have: a sourced residual-inertia
> figure for the cap to be set against and graded on, and a caller whose reachable range includes
> it. Until both exist the number is INERT and must not be read as calibrated.

**What was searched and did not have it.** The knowledge layer, the market-research anchors and the
regulation commons hold no residual-inertia ceiling on annual domestic churn — no published figure
for the share of households who stay whatever their bill does. What the record *does* publish is
the market-wide annual switching rate (~15–23% across 2016–2025,
`docs/market_research/gb_switching_rate_denominators.md`). That is a flow across a whole market and
not a bound on one household's response to its own supplier; reading it as this ceiling is exactly
the category error `simulation/market_switching_propensity.py` already records at its `_MAX_RATE`.
So the honest origin is a simplification and not a citation, and the gap is filed rather than
filled with the nearest available number.

---

## 2. `ONS\b` with no leading boundary: an English plural discharged a constant's debt

`tools/domain_constant_origins._CITED` listed the short publisher abbreviations as `CMA\b` and
`ONS\b` — a **trailing** word boundary and no **leading** one. Under `re.I`, `ONS\b` therefore
matched inside `comparisons`, `commons`, `reasons`, `seasons`.

Found by walking into it: the origin comment written above says the "regulation **commons**" does
not establish the figure, and the scanner classified the constant `cited`. `_classify` tests CITED
first, so the mislabel also outranked the honest `simplification` behind it.

**Pre-registered before measuring** (the prediction is kept beside its answer):

> Of the 26 constants currently classified `cited`, I expect a NON-TRIVIAL minority — my guess is
> **2 to 8** — are cited ONLY by that accident. I do not expect zero, because "reasons"/
> "assumptions" are common words in this repository's comment style.

**Answer: 2**, at the bottom of the predicted range. One is the new constant, which reclassified to
`simplification` where it belongs. The other is a live pre-existing defect:

- `company/regulatory/seg_book.py::_SEG_RATE_P_PER_KWH_BY_YEAR` — *"Supplier-set SEG rates
  (illustrative competitive rates, p/kWh) / Based on publicly available SEG rate **comparisons**
  2020-2024"*. An illustrative year-keyed rate table naming no publisher and no path, counted among
  the cited since the register was built.

**The direction is what makes this worth a finding.** A false CITED *shrinks* the debt, and
`test_the_unsourced_domain_constant_debt_only_SHRINKS` is a ratchet — it catches increases. So the
whole register could have been discharged one plural at a time with the gate green throughout, and
the debt floor added on 2026-08-30 (which exists for precisely this class) would not have caught it
either: 189 is still comfortably above 150.

**Repaired**, both anchors, with `test_a_word_ending_in_ons_is_not_a_CITATION` guarding it. The
control carries its own vacuity guard — the abbreviations must still match when they *are* the real
thing — because a `_CITED` that matches nothing would pass the three negative assertions alone.

**Mutation-proven** (`python3 -B`, per the stale-`.pyc` lesson): dropping the leading `\b` from
`ONS` in `_CITED` → **1 failed, 6 passed**. Restored → 7 passed.

`CMA`'s leading boundary is defensive rather than evidenced — no ordinary English word contains
"cma", so unlike `ONS` it has never mislabelled anything. Anchored anyway because the two were
written as a pair, and recorded as such in the test so the next reader does not go looking for the
instance that justified it.

---

## What moved

| | before | after |
|---|---|---|
| name collisions | 1 (`MAX_CHURN_PROBABILITY`) | **0** |
| `KNOWN_NAME_COLLISIONS` | `{"MAX_CHURN_PROBABILITY"}` | `frozenset()` — all five struck |
| `cited` | 26 | 24 (two were plurals) |
| `simplification` | 0 | **1** — the first one in the codebase |
| NO ORIGIN | 188 | 189 (`_SEG_RATE_P_PER_KWH_BY_YEAR` returned to the debt it owes) |

The debt going **up** by one is the finding working. Ceiling 197, floor 150; neither is threatened.

## What is owed

1. **A sourced residual-inertia figure**, or an explicit ruling that none exists and the cap should
   be deleted rather than declared. Until then `MAX_BILL_SHOCK_CHURN_PROBABILITY` is inert and its
   comment says so.
2. **`_SEG_RATE_P_PER_KWH_BY_YEAR`** now sits in the debt with no origin. It is an illustrative
   table; it wants either a real source or a named simplification.
3. **The remaining long publisher names in `_CITED`** (`Ofgem`, `DESNZ`, `Elexon`, `NESO`, `BEIS`,
   `Cornwall`) are unanchored on both sides. No English word contains any of them, so this is
   latent rather than live, and it is recorded rather than repaired: anchoring them changes only
   whether inflected forms like "Ofgems" match, which is a judgement call about the matcher and not
   the same defect as the two that were already written as anchored and half-done.
