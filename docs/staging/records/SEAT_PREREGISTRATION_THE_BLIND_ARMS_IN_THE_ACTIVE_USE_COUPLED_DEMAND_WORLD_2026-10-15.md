**Severity:** RECORDED · **Lane:** W_world · **Epoch:** 4 · **Atom:** `unminted` · **Claim:** `retake-the-value-arms-in-the-l2-4-coupled-demand-world`

# Pre-registration: the four blind-envelope arms re-taken in demand world 87d94399c9a414ed

Written 2026-10-15 ~10:30 BST, before any arm was launched.

## Which value-arms artefacts read the demand world

I checked this rather than assuming it. In `tools/generate_value_arms_data.py`, exactly one block
checks `world_home_identity.home_demand_identity`: the blind envelope
(`_blind_envelope_demand_refusal`, which reads `docs/design/blind_envelope_arms_2026-09-11.json`).
The noise floor, the size-term pair and the other bounds check only
`departure_level_anchor.world_level_identity`. That is the departure level, and `aa8a7c444` did not
move it (`cdba75ebb9197b33` before and after). So the blind envelope is the only artefact the
demand change visibly stales.

The `run_value_cycle_ab` arms are measured in the demand world too, but nothing checks which one.
Their re-take is already queued and held behind the stayers control
(`SEAT_PREREG_THE_VALUE_ARMS_RETAKEN_ON_WRITER_ONES_CORRECTED_BASIS_2026-10-14.md`), pinned at origin.
Any pin taken now includes `aa8a7c444`, so it lands in this world without a separate re-take. This
item does not duplicate it.

## The state found

- The page refuses the blind envelope now. The artefact says demand `b422b3dd8de98b8c` (fc47cd363),
  and the live demand is `87d94399c9a414ed`.
- **The 2026-10-11 re-take ran and was never filed.** Its four arms completed at d06b039e7, in
  demand `7d6195c5eb1562ab`, and sit in `~/.cache/seat_lane0_20261011_priceresp/` (each about 1 h
  20 min, two lanes). Nothing put them into the artefact, so the page went on refusing.
- **`7d6195c5eb1562ab` is the demand at `aa8a7c444^`**, which I measured from a `git archive` of that
  parent. The only demand move since the unfiled re-take is therefore `aa8a7c444`, and those four
  runs are the nearest "before" there is. They are not a one-variable control: there are 322 commits
  between d06b039e7 and cd2fda5c6, many of them in the company (writer one's basis and others).

The unfiled 10-11 figures, per settlement-weighted win:

| arm | settled | gross | revenue | net | net after CTS | bad debt |
|---|---:|---:|---:|---:|---:|---:|
| B chosen | 221 | 1,984 ± 145 | 3,572 ± 275 | 794 ± 58 | 529 ± 46 | 20.5 |
| A cull | 223 | 2,050 ± 134 | 3,805 ± 265 | 797 ± 55 | 526 ± 42 | 17.8 |
| C cull221 | 221 | 2,060 ± 134 | 3,865 ± 268 | 794 ± 55 | 510 ± 41 | 17.7 |
| D tenure | 229 | 2,359 ± 402 | 4,266 ± 695 | 889 ± 126 | 625 ± 107 | 10.4 |

## What runs

The same `arm_rerun.py` as 2026-10-07 and 2026-10-11 (byte-identical), run from a clean
`git archive` of origin/main `cd2fda5c6` at `~/.cache/arm_rerun_cd2fda5c6`. I read the digests
there: demand `87d94399c9a414ed`, homes `35f8efe8ff02f245`, departure `cdba75ebb9197b33`. It runs
with `SIM_FAST_MODE=1`, in two lanes: `chosen` then `tenure`, and `cull` then `cull<N>`, where N is
B's own settled count. ARM C' is not re-run.

## Predictions

- **Q1** All four arms stamp demand `87d94399c9a414ed`, homes `35f8efe8ff02f245` and one departure
  digest. Once filed, `_blind_envelope_demand_refusal` stops firing. 85%.
- **Q2** B's settled count is within ±5 of 221. 60%. The chooser places on fabric axes, which
  `aa8a7c444` did not touch, but the funnel runs through company decisions that read metered demand.
- **Q3** In every arm, revenue per weighted win moves by less than one of its own 10-11 standard
  errors. 60%. `aa8a7c444` scales active use by (always-on/90 W)^0.7 per home, which is up for some
  homes and down for others. Its mean effect on annual electricity kWh was never printed, and
  electricity is only part of revenue. This is a guess, not a derivation, and the 322 company
  commits can move it on their own.
- **Q4** B against the blind arms, per weighted win, is NOT PREDICTED. On 10-11, B's gross (1,984)
  was below all three blind arms, and its net (794) tied the bottom of their span.
- **Q5** No per-win difference between B and any blind arm exceeds twice the larger of the two
  standard errors. Nothing separates the chosen book from the blind books at one seed. 75%.

## What done means

The four arms are filed into `docs/design/blind_envelope_arms_2026-09-11.json` with their stamps.
The 10-11 and 10-07 figures are kept beside them as prior readings. `site/data/value_arms.json` is
regenerated so the block publishes, or refuses for a named reason that is not the demand stamp.
Q1–Q5 are graded in a result record.

**What this cannot attribute:** it cannot say how much of any move comes from `aa8a7c444`. That needs
the same commit run with `active_use=1.0` against the coupled run. That pair is not run here (R5):
the question this item asks is whether the page's envelope describes the live world.

## Not launched: decision written 2026-10-15 ~11:30 BST, before any arm ran

**No arm ran, and Q1–Q5 are ungraded.** Lane 1 sat queued for about an hour behind the sim-runner's
annual-report run (7 GB resident, against a 23,008 MB budget). Then the worker on claim
`a-storage-home-charges-off-peak-in-both-streams` reported that it was about to land a change that
moves the demand digest from `87d94399c9a414ed` to `2876e687`. That change is
`fabric_physics.storage_charge_kwh`, which moves electric-storage space heat into 00:30–07:30. They
also reported a second stream: hot water, SAP Table 13, see
`docs/market_research/` → `068928f47`. It will move the digest again in a later turn. The page
refuses on any stamp mismatch, so arms filed at `87d94399` would refuse as soon as the first of
those changes lands. That is about 3 h of box spent on a world that would be gone within hours. I
cancelled the queued launch, which had never started a unit. **The re-take runs once, after stream
2 lands**, with these predictions carried over unchanged. Because I am writing this before any
figure exists, it does not count as a change to a prediction.

**What the next lane inherits:**
- The harness is `~/.cache/seat_lane0_20261015_activeuse/`: `lane.sh` (two lanes: `chosen tenure`
  and `cull cullB`), `per_win.py`, and `file_retake.py`. `file_retake.py` files the four arms and
  keeps the unfiled 10-11 readings and the fc47cd363 figures as priors. Re-point `EX`/`OUT`/
  `ARM_PRODUCING_COMMIT` in `lane.sh` and the strings in `file_retake.py` at the new origin, and use a
  fresh `git archive`. Then read the three digests there before launching.
- **One arm's peak memory has never been measured.** I declared 7,000 MB as a guess. The 11,200 MB
  figure belongs to a three-pass value cycle and over-prices one arm. Sample the first arm's RSS and
  admit the second lane on that measurement. The 10-11 lanes took ~1 h 20 min per arm and ran two
  at a time.
- `cannot_attribute` gets wider: the move from the 10-11 readings will now sum `aa8a7c444`, both
  storage streams and every company commit in between.
