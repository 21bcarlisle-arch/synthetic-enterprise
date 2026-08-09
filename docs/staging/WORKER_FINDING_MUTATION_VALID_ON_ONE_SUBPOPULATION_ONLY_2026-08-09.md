# [WORKER-FINDING] An R15 mutation can be valid on one subpopulation and INVERTED on another (2026-08-09)

**Found during:** `W1_12_premise_trace_generator` L2 -> L3, building the R15 proof for the new
heating-conditioned L1.1 band.
**Status:** the instance is fixed and pinned in this tick. Filed because the CLASS is not.
**Advances:** EP16_anchored_generators — an anchored generator is only as good as the mutation
that proves its band can fire, and this is a way for that mutation to be quietly hollow.
**Every number below is `observed-with-evidence`**, measured on a matched pair from the real
generator at HEAD, not inferred.

## Observed

`tests/harness/test_premise_two_level.py::_smooth` is this suite's mutation for L1.1 texture:
replace each period with a centred rolling mean across the same period on neighbouring days.
Mean-preserving, texture-destroying. It has been the R15 proof for the L1.1 band since the
band was written, and on a gas home it is sound.

On a MATCHED PAIR — the same household spec (semi-detached, 1965-80, partial insulation, 3
bedrooms, 3 people, seed 7, same weather), differing ONLY in heating system:

```
gas home  G1 : texture 0.2471 --_smooth--> 0.1539   (down, as intended)
heat pump HP1: texture 0.1069 --_smooth--> 0.1430   (UP)
```

**On the heat-pump home the mutation moves the statistic the wrong way.** Cross-day averaging
at a fixed period removes day-specific appliance noise but leaves the heat pump's repeated
diurnal cycle standing, and the median step of what survives is LARGER than the median step of
the original. Texture is `median |x[t] - x[t-1]| / mean(x)`, and the median is what does it: the
raw series carries many near-zero overnight steps that the mutation removes.

## Why it is a class, not an instance

A mutation is the evidence that a band can fail. If the mutation had simply been reused for the
new electrically-heated band, the R15 proof would have been **vacuous in the only direction that
matters** — a mutation that RAISES the statistic cannot demonstrate that an `at_least` band
fires. It would not have errored. It would have failed loudly here only by luck (the smoothed
value 0.1430 still clears the 0.0705 electric band, so the assertion would have failed rather
than passed) — but a slightly different band, or an `at_most` statistic, and the same mistake
lands as a GREEN R15 proof of a control that cannot fire.

The general shape: **a mutation is validated against a population, and inherits that
population's composition.** When a band is later conditioned — by heating system here, but the
same applies to any segment, tariff, meter type or geography — the mutation does not
automatically transfer, and nothing in the harness notices. This is the R15 fail-silent pattern
one level up: not "the control is unavailable", but "the control's PROOF is unavailable and
still reports".

A second, narrower observation in the same family: `_smooth` does not even fire the gas band on
every gas home. On the matched-pair gas home it lands at 0.1539, still above the 0.15 floor. The
existing `test_L1_1_texture_FIRES_when_the_trace_is_smoothed` passes because it uses the
fixture's first home, which happens to be smoothable past the band. A mutation proof that holds
on one member of a population and not another is thinner evidence than its name suggests.

## The fix applied (instance only)

`_flatten_blend(grid, weight)` — blend each day toward its own flat daily mean. Monotone in
`weight`, exactly 0 texture at `weight=1`, and every day's TOTAL preserved at every weight, so
it attacks within-day shape and nothing else. Verified monotone across (0, 0.25, 0.5, 0.75, 1.0)
before being used as a proof.

It also made a stronger claim testable than "the band can fail". Expressed as the CRITICAL
FLATTEN WEIGHT — how far toward a flat day a home must be pushed before its own band fires —
two bands with different thresholds become comparable:

```
heat pump HP1 against the 0.0705 electric band : fires at 0.349
gas home  G1  against the 0.1500 gas band      : fires at 0.396
```

On a matched pair, the new band is if anything the STRICTER of the two in sensitivity to the
actual defect. That is the answer to "you lowered a threshold so the thing it judges would stop
failing", and it could not have been made with `_smooth`.

## Not asserted / the drawable half

* **How many other bands in this repo rest on a mutation validated against one composition.**
  Not swept. The sweep is the work: for every control with an R15 mutation proof, does the
  mutation still move the statistic in the right direction on every subpopulation the control
  is applied to? A cheap first cut is any control whose threshold was later conditioned or
  segmented after its mutation was written.
* **Whether a mutation-direction assertion should be mechanised.** A mutation used as an R15
  proof could be required to assert its own direction on the specific fixture it mutates
  (`assert after < before` for `at_least`), which would have caught this at the point of reuse
  rather than at the point of a surprised author. Not built — it is a change to how every R15
  proof in the repo is written, which is an atom, not a side-effect.

— Worker finding, 2026-08-09, during `W1_12_premise_trace_generator` L2 -> L3.
