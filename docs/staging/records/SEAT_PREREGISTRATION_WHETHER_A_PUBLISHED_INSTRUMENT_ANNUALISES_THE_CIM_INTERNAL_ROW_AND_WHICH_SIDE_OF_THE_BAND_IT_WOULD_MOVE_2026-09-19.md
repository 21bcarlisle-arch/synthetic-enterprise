**Severity:** LATENT · **Lane:** W2_customer_generator · **Atom:** none — Lane 0 delivery, "SVT
internal conversion ceiling needs annualisation to bite"

# Pre-registration: does a published instrument annualise the CIM internal row, and which side of the band would such a fact move?

*A bound that cannot refuse is not a defect. A bound annualised in the WRONG DIRECTION would be
one, and this is the step at which that error is available — which is why the direction is
predicted here rather than concluded later.*

**Filed 2026-09-19, delivery seat, Lane 0, BEFORE any fetch or any arithmetic on a number not
already in the tree.** Claim `svt-internal-conversion-ceiling-needs-annualisation-to-bite`.

**Subject:** `tools.published_route_split.svt_internal_conversion_ceiling` (0.2659 per SVT household
per six months, binding at W6) and `svt_internal_conversion_floor` (0.0449, binding at W4), and
`tools.fit_year_level_anchor._internal_return_vs_the_published_ceiling`, which judges the world's
0.1859 per SVT account-year against the first of those.

---

## 0. The question as the claim states it

> Establish whether a published GB domestic instrument supports ANNUALISING the CIM six-month
> internal-switching rate — i.e. how much repeat internal switching a household does within one
> year. Then re-derive the ceiling in annual units and re-run `fit_year_level_anchor
> --internal-return`.

The claim's stated motive is that *"a repeat-switching figure is the single published fact that
turns this bound from live into firing"*.

**I am pre-registering a prediction that the motive is wrong in DIRECTION**, and the prediction is
filed here, before the fetch, precisely because it would be worthless filed after it.

---

## 1. What each quantity counts — said out loud before any of them is divided by another

| symbol | what it counts | population | window |
|---|---|---|---|
| `I` | share of households reporting **at least one** internal switch — an INCIDENCE, one per household however many times they moved | all CIM respondents, both fuels | past **6 months** |
| `p` | the same thing, written as a probability, for the SVT segment: `J_svt` per six months | SVT households | 6 months |
| `P12` | share of SVT households with **at least one** internal switch in a year | SVT households | **12 months** |
| `q` | share of SVT households switching internally in **BOTH** half-years | SVT households | 12 months |
| `r` | share of 12-month internal switchers who switched **more than once** — the "repeat-switching figure" the claim asks for | 12-month internal switchers | 12 months |
| WORLD | `returned_to_fixed` stints ÷ SVT account-years of exposure — an EVENT COUNT over exposure, not an incidence | this book's resi electricity accounts | per account-**year** |

---

## 2. The algebra, registered before it is used

Under stationarity across the two half-years:

```
P12 = 2p − q                                    (inclusion–exclusion, exact)
q   ≤ r · P12                                   (switching in both halves ⟹ more than once; not conversely)
```

Substituting the second into the first:

```
P12 = 2p − q  ≥  2p − r·P12    ⟹    P12  ≥  2p / (1 + r)
```

**A published `r` therefore bounds the annual incidence from BELOW and not from above.**

- `r = 1` (every annual switcher repeats) gives `P12 ≥ p` — which is the bound the floor already
  makes, un-annualised. **So the current floor is not merely "un-annualised": it is the annualised
  floor evaluated at the most conservative corner of `r`.**
- `r = 0` (nobody repeats) gives `P12 ≥ 2p` — the floor doubles.
- The assumption-free ceiling is `P12 ≤ 2p` at every `r`, by the union bound, and **no value of `r`
  lowers it**, because `r` bounds `q` from above and the ceiling needs `q` bounded from below.

---

## 3. PREDICTIONS, filed before the fetch

**P1 — direction (confidence: high; this is algebra, not evidence, and it is registered so the
fetch cannot be read as having decided it).** A repeat-switching figure of the published shape
("X% of switchers switched more than once in the last 12 months") **cannot tighten the ceiling**.
It can only raise it, or leave it where the union bound already puts it. The claim's stated motive
is therefore refuted on direction regardless of what the fetch returns.

**P2 — direction, other side (confidence: high).** The same figure **does** tighten the floor, via
`P12 ≥ 2p/(1+r)`, and the tightening is large: at the binding wave the floor would move from 0.0449
toward 0.1676 as `r` falls from 1 to 0. That is the side of the band annualisation earns something
on.

**P3 — availability (confidence: medium-high, ~0.75 that this is how it lands).** No published GB
domestic instrument gives `r`, or a 12-month internal-switching incidence on a base comparable to
CIM C4's. Specifically I expect:
  - the **switching-count series** (Ofgem/Elexon/DESNZ meter-point transfers) to be unable to give
    it, because it has no household in it — already established in
    `household_switching_response_amplitude.md` §1 and not re-derived here;
  - the **Ofgem Consumer Survey** 12-month series to be a DIFFERENT instrument — different panel,
    mode and base — whose level runs ~1.5× the record (same file, §2.2), so the ratio of its
    12-month rate to CIM's 6-month rate is an instrument effect plus an annualisation effect, not
    an annualisation factor;
  - any **engagement** cut to be outcome-defined, per §2.3 of that file.

**P4 — what I expect to be able to land (confidence: medium).** An `annualisation` reading in
`published_route_split` that (a) states the assumption-free annual ceiling `2 × I/s_min` and says
plainly that it is LOOSER than the six-month bar now in force, (b) exposes the floor as the
one-parameter family in `r` it actually is, with `r = 1` named as the corner it currently sits at,
and (c) refuses to supply `r`, with the reason named — a **fourth** refusal, and the claim's own
warning is that a fourth refusal quietly reversed is the defect.

---

## 4. The decision rule, written before the evidence

- If a published `r` or a comparable 12-month internal incidence **is** located: derive both bounds
  at it, publish the annual ceiling **beside** the six-month one and never in place of it, and say
  in the returned dict which of the two is the bar.
- If it is **not** located: the annual ceiling is `2 × I/s_min` = 0.5318 and is the honest one, the
  six-month bar stays as the published bar **because it is the harsher of the two and the harsh
  direction is the safe one here**, and the module carries the gap explicitly rather than a factor
  picked to make a bound bite.
- **In neither branch does the world's rate get compared against a bar chosen after seeing which
  way the comparison lands.** The bar is chosen by the rule above and the verdict is whatever it is.

## 5. What would refute me

P1 is refuted by any published instrument that bounds `q` from **below** — e.g. a series reporting
the share of households switching internally in each of two consecutive half-years, or a panel
following the same households across waves. P3 is refuted by locating `r`. Either refutation is the
result and gets written beside this file, not over it.
