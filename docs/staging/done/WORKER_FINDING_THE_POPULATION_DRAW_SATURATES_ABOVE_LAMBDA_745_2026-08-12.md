# [WORKER-FINDING] The population draw saturates above λ≈745 and says nothing

**Severity:** LATENT · **Lane:** W2_customer_generator

**Found:** 2026-08-12, by `AO12_scale_probe_10k` while building a 10k-customer book.
**Owner:** the lane that owns `simulation/population_draw.py` (W2_2_population_draw).
**Disposition:** QUEUE (SELF-INTERRUPT DISCIPLINE) — the probe worked around it and did not fix
it. Nothing is blocked.

## Observed, with evidence

`simulation.population_draw._poisson` is Knuth's algorithm:

```python
target = math.exp(-lam)
k, p = 0, 1.0
while True:
    p *= rng.random()
    if p <= target:
        return k
    k += 1
```

`math.exp(-lam)` underflows to **exactly 0.0** for λ ≳ 745 (`math.exp(-745)` is 5e-324, the
smallest subnormal; `math.exp(-750)` is 0.0). With an unreachable target the loop terminates
only when the running product of uniform draws denormalises to zero, which takes ~700
multiplications **regardless of λ**.

Measured directly (`random.Random(1)`):

| λ | `math.exp(-λ)` | returned |
|---|---|---|
| 20 | 2.06e-09 | 14 |
| 700 | 9.86e-305 | 703 |
| 745 | 5e-324 | 788 |
| 750 | **0.0** | 703 |
| 10000 | **0.0** | 733 |

**A request for 10,000 acquisitions returns ~733, with no exception and no warning.** Every
request above the saturation point returns roughly the same meaningless number.

## Why it matters beyond the probe

The failure mode is silence, and it is silent in the reassuring direction. Any consumer that
asks this generator for a large book gets a small one and a plausible-looking count. A
per-customer cost computed against the *requested* N rather than the *realised* N is understated
by the ratio — which for a 10k request is 13×.

Today the shipped default (`DEFAULT_ACQUISITIONS_PER_YEAR_LAMBDA`) is far below the saturation
point, and `simulation/live_population.py`'s draw seam is default-OFF, so **no live run is
affected**. This is a latent defect on a path the scale work is the first to walk.

## What the probe did instead

`tools/scale_probe_10k.py::_draw_book` calls the shipped generator repeatedly at λ=250 (well
below saturation), with a per-batch seed and a per-batch customer-id prefix (the generator
numbers from 1 within each year, so un-prefixed batches would collide and silently shrink the
book again — the same defect one layer up). It then **refuses to proceed if it did not get the
book it asked for**.

It did not fix the generator, for two reasons that are not stylistic:
- `simulation/population_draw.py` is outside `AO12`'s `file_scope`.
- The draw is a director-owned CURRICULUM instrument (R13). A change to it alters which world
  every run faces, and a fix must be byte-identical at the shipped λ to avoid being a silent
  curriculum edit. That is the owning lane's call, not a measurement tool's.

## Suggested repair, for whoever picks it up

Work in log space (`log(p) += log(rng.random())` against `-lam`), or switch to a
transformed-rejection method above λ≈30. Either is byte-identical below the saturation point
only if the draw sequence is preserved — which it is **not** for a log-space rewrite, so the
substitution needs the same substream-isolation and byte-identical-by-default proof
`test_cohort_draw_default_off_is_byte_identical` established for the cohort work.

Whatever the repair, `tests/tools/test_scale_probe_10k.py::test_the_generator_saturates_above_745`
fails the moment λ=10000 starts returning ~10000, which is the signal to revisit the probe's
batching rather than leave it behind as cargo.

## Evidence

- `tests/tools/test_scale_probe_10k.py::test_the_generator_saturates_above_745` (pins it)
- `tests/tools/test_scale_probe_10k.py::test_the_probe_refuses_a_book_it_did_not_get`
- `tests/tools/test_scale_probe_10k.py::test_batched_draw_yields_unique_ids`
- `docs/design/SCALE_PROBE_10K.md` §2.5
