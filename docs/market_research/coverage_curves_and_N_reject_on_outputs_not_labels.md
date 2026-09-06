**Severity:** RECORDED · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** W2_22_the_sample_is_space_filling_and_rejects_on_outputs

**Knowledge:** none -- the housing knowledge page is deliverable 4 of the housing ruling and is not
yet written. These are the coverage curves it will publish; the declaration is replaced when the
page lands.

# The coverage curves, N, and the fourteen-fold reason to reject on outputs rather than labels

**Measured 2026-09-06**, delivery seat, `W2_22`. Source: DESNZ NEED `anon2026_50k.csv`. Output
space is **metered 2024 gas × electricity** — 37,074 of the 50,000 dwellings carry both.

---

## The curve, and the N it sets

Houses chosen greedily to fill the output space; coverage is the share of dwellings whose nearest
drawn house is within 5% of the normalised gas×electricity range.

| N | output coverage |
|---:|---:|
| 2 | 19.5% |
| 11 | 23.5% |
| 21 | 40.5% |
| 31 | 50.8% |
| 51 | 68.8% |
| 76 | 93.9% |
| **101** | **99.6%** |
| 151 | 100.0% |

**N ≈ 100 houses covers 99.6% of the metered output space.**

> **CORRECTED the same day, 2026-09-06 — do not quote the 100.** Adding ONE further output
> dimension the use cases actually need (inter-year consumption volatility, i.e. bill-shock
> exposure, which use case 2.1 exists to remove) takes N = 100 from 99.2% coverage to
> **32.7%**; at N = 250 it is 87.7% and still short of 99. The figure below was an artefact
> of measuring the two dimensions that were easiest to obtain, not a lower bound with
> headroom. See `N_was_a_hundred_because_the_sample_was_blind_to_what_the_use_cases_need.md`.
> The rest of this document — the shape of the curve, and the label-versus-output finding —
> stands unchanged.
>
> The sentence that stood here — "the ruling's target is 99% of variance including tails, so this
> is the number it asked for" — is withdrawn with the figure. It was true of the two dimensions
> measured and false of the target, which is variance in the outputs the use cases are scored on.

The curve is not linear and the shape matters: the first fifty houses buy less than the next
twenty-five. Under ~20 houses the sample is covering the dense middle over and over — which is the
"two London terraces on one street" the director described, arrived at from the data.

## The measurement that justifies rejecting on OUTPUTS

The ruling insists similarity is judged on outputs, never on type/age/size labels. Both samples
below hold **the same N = 84**; one takes a dwelling per occupied input cell (104 cells exist,
84 in the 4,000-dwelling working pool), the other fills the output space.

| | overall output coverage | **top-1% tail** |
|---|---:|---:|
| reject on **input labels** | 91.8% | **6.1%** |
| reject on **outputs** | 97.8% | **85.4%** |

Overall, the label-based sample looks fine — 92% is a number nobody would question. **It covers
6.1% of the top-1% dwellings.** Fourteen times worse than the output-based sample, on exactly the
population the ruling says carries the money and the risk.

That is failure mode (a) from the ruling's own §6, measured: *a sample that matches every marginal
and misses the joint corners*. And it is invisible from the headline: a label-based sample reports
92% coverage while being almost blind to the tail.

## Why this is the same finding as the independence one, one layer up

`independence_invents_one_house_in_five_that_does_not_exist.md` showed an independent draw putting
19.6% of houses in cells the stock does not contain, while under-producing detached >200 m² by
5.15×. This shows that even a draw which *does* respect the cells — one house per real input cell —
still misses the output tail, because a cell is not a behaviour: two houses in the same
type × band × age × fuel cell can differ several-fold in metered consumption.

So the two repairs are not alternatives. Fit the joint so the cells are real; then fill on outputs
so the corners inside them are reached.

## Limits, stated

- The output space here is **level only** — annual gas and electricity. The ruling also wants shape
  and weather gradient in the similarity test; neither is in NEED, and both need the half-hourly
  draw. **N ≈ 100 is therefore a LOWER bound**: adding dimensions can only require more houses.
- The 5% radius is a Choice, not an anchor. A tighter radius raises N; the curve's shape, not its
  absolute level, is what carries the argument.
- 12,926 of 50,000 dwellings lack one or both metered figures, and the censoring is at the tails
  (below 1,000 and above 50,000 kWh gas), so the true tail is **wider** than measured and the
  6.1%/85.4% gap is, if anything, understated.
- Coverage is a property of the ensemble of runs, not one run. This measures a single sample; the
  visited-corner ledger across lives is what the ruling actually asks for and is not built here.
