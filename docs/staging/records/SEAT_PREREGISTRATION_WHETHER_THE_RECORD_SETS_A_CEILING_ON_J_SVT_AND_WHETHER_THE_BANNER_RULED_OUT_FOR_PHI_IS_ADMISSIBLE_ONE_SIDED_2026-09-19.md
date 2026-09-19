**Severity:** LATENT · **Lane:** W2_customer_generator · **Atom:** the world's product mix

# Pre-registration: does the published record set a CEILING on `J_svt`, and is the tariff-type banner — ruled out for φ — admissible one-sidedly for one?

**Filed 2026-09-19, delivery seat, claim
`svt-internal-conversion-needs-a-ceiling-not-a-better-floor`, BEFORE Table 109 is opened and BEFORE
the world is measured against any ceiling.** The workbook is on disk
(`~/.cache/cim_w6_ceiling/cim_w6_tables.xlsx`, 27,440,744 bytes, fetched this turn from the URL
`gb_domestic_switcher_split_cim_2022_2025.md` §7 records) and has not been parsed.

The drawn item states the case: the floor landed, the world sits 4.14× above it, and a one-sided
bound four times below the thing it bounds constrains nothing. What is wanted is the other side.

---

## 0. What is already derived, recorded as derived and NOT as a prediction

Before writing this file I did the arithmetic that needs no new source, because it decides whether
there is anything to pre-register at all. It is set down here so that nothing below can be read as
having been predicted when it was computed:

The same identity that gives the floor gives a ceiling, and the ceiling needs *less* than the floor
did. From `I = s·J_svt + (1−s)·0.35·(1−φ)` and `(1−s)·0.35·(1−φ) ≥ 0` — true at φ = 1, and φ ≤ 1
is not an assumption but the definition of a share:

```
J_svt  ≤  I / s
```

Driven at the published inputs, taking `s` at the SMALLEST published default share across the recall
window (the mirror of the floor's `s_max`; a smaller SVT population concentrates the same internal
switching into fewer households and pushes the ceiling UP, which is the conservative direction for a
ceiling exactly as `s_max` was for a floor):

| wave | I (6 mo.) | s_min | ceiling on J_svt |
|---|---|---|---|
| W1 | 0.131816 | 0.80 | 0.164770 |
| W2 | 0.124771 | 0.80 | 0.155964 |
| W3 | 0.144883 | 0.80 | 0.181104 |
| W4 | 0.110427 | 0.80 | 0.138034 |
| W5 | 0.115861 | 0.80 | 0.144826 |
| W6 | 0.170192 | 0.64 | **0.265925** |

The binding ceiling is the **MAX** across waves, 0.265925 — the mirror of the floor's MIN, and for
the same reason the floor gives: it is the bound *every* wave permits, rather than the tightest one
some wave would allow, and the waves are at different times so a single `J_svt` need not satisfy all
six.

**This much is arithmetic over inputs already in the tree and is not a finding.** What follows is.

---

## 1. Predictions

**P1 — the world clears the ceiling at book level, and the ceiling is close to biting where the
floor was not.** The world's 0.185887 per SVT account-year will come out BELOW 0.265925, at
0.69–0.71× of it. Stated against the floor's 4.14×: the same world sits at 4.1× its lower bound and
0.7× its upper one, so the ceiling is the side of the band that is nearly live.

**P2 — at least one individual YEAR breaches the ceiling.** The per-year spread that put three years
below the floor is wide; I expect it to put at least one year above 0.265925. This is the prediction
I am least sure of and the one worth filing. If it is false the per-year ceiling verdict is uniform,
and then a control keyed to non-uniformity — which is what the floor's control is keyed to — would
be green for a reason that is not the mechanism, and must not be written that way.

**P3 — the direction of flattering INVERTS between the two bounds, and this is the trap in the
work.** A six-month floor read as an annual bar is *lower* than the true annual floor, so clearing it
is the weak verdict — that is what `_internal_return_vs_the_published_floor` already says. A
six-month *ceiling* read as an annual bar is also lower than the true annual ceiling, and for a
ceiling that makes it a *harsher* bar: "under the ceiling" becomes the STRONG verdict and "breaches
the ceiling" the WEAK one, because the true annual ceiling is at least as high. I predict the
un-annualised ceiling is therefore safe to publish for a *clears* verdict and must not be used to
call any year's breach established.

**P4 — the tariff-type banner, ruled out for φ, is admissible ONE-SIDEDLY for a ceiling.**
`gb_domestic_switcher_split_cim_2022_2025.md` §3 disqualifies Table 109 because *"tariff type is
recorded after the switch, so a household that switched onto a fix is counted in the fixed column
whichever route it came from"*, and §6 names it as the obvious next reach that does not work. That
contamination is fatal for φ, which needs the column to mean the tariff the respondent was on
*before*. **It is harmless in one direction for a ceiling on `J_svt`, because it runs the safe way:**
a `J_svt` event is by definition a move onto a fix, so the household reports a FIXED tariff at
interview, so every `J_svt` event in the window sits in the fixed column. The fixed column's internal
count is therefore an upper bound on the `J_svt` count, and the variable column's internal switchers
(SVT households moving to another *variable* tariff with the same supplier) are correctly excluded
because they are not `J_svt` events either. I predict this yields a ceiling **tighter** than
0.265925 at W6.

**P5 — the reconstruction I can already do from in-tree numbers will be confirmed by the workbook.**
Table 56 gives W6 external switching by tariff type (fixed 7.0%, n=2127; variable 2.5%, n=1316) and
§3 of the switcher-split note gives φ_survey spans by tariff type (fixed 0.221–0.398, variable
0.356–0.540). Reading W6 at the LOW end of each span and using the unweighted bases as weights:

```
I_fixed = 0.070/0.221 − 0.070 = 0.2467      I_var = 0.025/0.356 − 0.025 = 0.0452
f = 2127/3458 = 0.6151                      1−f_var = 1316/3458 = 0.3805
reconstructed I_total = 0.6151·0.2467 + 0.3805·0.0452 = 0.1690   vs published 0.170192
reconstructed E_total = 0.6151·0.070  + 0.3805·0.025  = 0.0526   vs published 0.052892
```

I predict the workbook's own W6 tariff-type cells land within **±0.02 absolute** of
`I_fixed = 0.247` and `I_var = 0.045`, and that the resulting W6 ceiling
`f·I_fixed / s_min = 0.6151·0.2467/0.64` lands within **±0.02** of **0.237**.

**P6 — and it will not be a large gain.** 0.237 against 0.266 is 11% tighter. I predict the banner
route does not change any verdict P1 or P2 produces. If that is how it comes out, the tighter ceiling
is worth recording as evidence and is NOT worth making the published bar, because it costs a
reconstruction chain — a range endpoint attributed to a wave, unweighted bases used as weights for
weighted rates — where the assumption-free ceiling costs nothing.

---

## 2. What would refute the whole approach

If the workbook's Table 109 turns out to cut C4 by a tariff type recorded at a point BEFORE the move
— i.e. if §3's disqualification is wrong about *when* the variable is measured — then P4's safe
direction is not safe and the banner is admissible for φ after all, which is a much larger result
than this item asks for and would be filed as its own finding rather than folded in here.

If `I / s` turns out not to be a valid ceiling because some wave's internal row is defined on a base
that is not all households, the floor built on the same identity is wrong too, and that is the
finding.

## 3. What is NOT being attempted

No world-side constant. `SVT_INTERNAL_CONVERSION_RATE` stays `None` unless a *point estimate* is
established, and a ceiling is not one — the same reason the floor was refused that slot. Nothing in
`simulation/`, `company/` or `saas/` moves. No annualisation of either bound.
