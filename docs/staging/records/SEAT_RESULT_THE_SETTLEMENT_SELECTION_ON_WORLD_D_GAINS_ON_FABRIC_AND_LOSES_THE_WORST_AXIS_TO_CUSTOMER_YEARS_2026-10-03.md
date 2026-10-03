# The settlement selection on world D gains on fabric; its worst-axis edge over the cull is gone (seed 42 reads 0.95)

**Filed 2026-10-03 by the delivery seat.** Measured with `python3 -m tools.settlement_per_axis_gain --seed 42`
at `fdbf2316d`, in world level `cf823b185f8ca51c`, homes `35f8efe8ff02f245`. The PB4 fourth refit moved
the level digest (c3939e7b1), and no evidence had been filed for this world, so
`tests/tools/test_settlement_evidence_is_graded_only_against_the_world_it_was_measured_in.py`
was red on origin. This is the re-file that test asks for. No tolerance was widened and no earlier
entry was re-pointed.

## The scalars, as the tool's self-check reads them

| | cull (uniform count) | chosen (weighted) |
|---|---|---|
| settled | 62 | 55 |
| committed customer-years | 1045.1 | 1044.2 |
| KS floor_area_m2 | 0.04345 | 0.04947 |
| KS fabric_w_per_k | 0.06795 | 0.06308 |
| KS raw_infiltration_ach | 0.04836 | 0.02797 |
| KS customer_years | 0.01590 | 0.07179 |
| **worst axis (max over CHOICE_AXES)** | **0.06795** (fabric_w_per_k) | **0.07179** (customer_years) |
| JOINT (not a CHOICE_AXIS) | 0.1484 | 0.09895 |

**Worst-axis ratio, cull / chosen: 0.9465.** Filed worlds: 1.553 (2026-09-11) and 1.66
(2026-09-16).

## What this says, plainly

- **P1, judged as filed on the worst single axis, INVERTS on world D.** The chosen sample is
  slightly worse than the count cull on its worst axis, at 0.0718 against 0.0680.
- **The chooser still wins on all three fabric axes' worst case and on the joint distribution**
  (0.099 against 0.148).
- **P1b, "the gain is concentrated on the fabric axes rather than cost", HOLDS,** sharply.
  - Gain on the fabric axes is 0.88-1.73.
  - Gain on customer-years is 0.22.
  - The spread is 7.8x.

On this world the choosing pays for its fabric match in customer-year representativeness. That
trade did not bind on the earlier worlds.

The pre-repair arm (`fit_weights` with `groups=None`) gives the same settled counts. Its
profile is cost 0.16 against fabric 1.20-1.97, so the year-group repair is not what moves the
customer-year axis.

**Three more seeds, read the same way, the same night (seconds each):**

| seed | settled cull / chosen | worst-axis cull / chosen | ratio | JOINT cull / chosen | P1b |
|---|---|---|---|---|---|
| 42 (filed) | 62 / 55 | 0.06795 / 0.07179 | 0.947 | 0.148 / 0.099 | HOLDS |
| 43 | 61 / 53 | 0.08370 / 0.08345 | 1.003 | 0.128 / 0.116 | HOLDS |
| 44 | 57 / 47 | 0.07318 / 0.07310 | 1.001 | 0.131 / 0.139 | HOLDS |
| 45 | 58 / 50 | 0.17537 / 0.09858 | 1.779 | 0.222 / 0.126 | HOLDS |

So the seed-42 "inversion" is mostly seed noise around parity. Three of four seeds sit at a ratio
of 0.95-1.00, and one is a large win. On world D the chooser no longer reliably beats the count cull on the
worst single axis, which it did by 1.55-1.66x on the earlier worlds at seed 42. The gain profile
claim (P1b) holds on every seed. Only seed 42 is filed as the self-check's evidence, since that is
the seed the earlier entries used.
