**Severity:** RECORDED · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** value-arms-error-bar

# The AUC reaches the reader against its own null, and 0.5697 does not clear it

**Claim:** `publish-the-auc-against-its-own-null-not-the-floors-spread`
**Discharges the "what should happen next" of:**
`SEAT_RESULT_THE_AUC_IS_MEASURED_FOR_THE_FIRST_TIME_AND_THE_FLOOR_FAMILY_IS_THE_WRONG_RULER_FOR_IT_2026-09-17.md`

---

## Premise, re-measured before starting

The drawn item's premise check said its cited commit `ab71cf877` was already an ancestor of
`origin/main` and the work might have landed by another route. **It had not.** Measured at
19:30Z on a freshly fetched tree at `e231f862c`:

- `site/data/value_arms.json` published `error_bar.discrimination_across_the_family` with
  `state: asked_and_unanswerable`, `seeds_carrying_an_auc: 0`, `seeds_in_family: 18` — a count,
  and no reading.
- `tools/generate_value_arms_data.py` had no reference to `auc_population` anywhere near the
  block, and no path constant reaching `..._auc3_20260917.json`.
- The rendered page (`site/capabilities/index.html`, `familyDiscrimination`) had no branch that
  could print a null reading at all.

**The duplicate-work check named a live sibling claim**
(`the-selection-leg-is-six-seeds-short-of-a-sign-and-its-point-estimate-is-negative`, which holds
`site/data/value_arms.json`). It is **genuinely different work on the same subject** and the
disposition is *carry on*, not *release*: that claim is drawing twelve more **advantage** seeds to
try to sign the **selection leg**. This claim publishes a **discrimination** reading against a
**null that needs no seeds at all**. Neither can do the other's job, and this landing deliberately
does not touch `tools/fold_noise_floor_family.py`, `NOISE_FLOOR_PATH`, or which family the
advantage is bounded over — all of which are the sibling's.

## What the reader now meets

Rendered through the real door, off the published feed:

> **Against the statistic's own null — 0.5697, 1.21 null SDs from chance.** Discrimination reads
> 0.5697 across 3 draw(s), measured over a DIFFERENT family from the one the advantage above is
> bounded over (the 3-seed AUC-carrying floor of 2026-09-17) […] on 63 retained against 42
> departed renewals a signal carrying nothing at all scatters with a standard deviation of 0.0578.
> This figure sits 1.21 of those above 0.5. That is INSIDE its own exact 95% null
> (0.3870–0.6130, two-sided p=0.231), so **DISCRIMINATION IS NOT DEMONSTRATED HERE** — in either
> direction. An arm that beat the control while scoring at chance won by charging and not by
> knowing, and this book cannot yet tell those apart.
>
> The seed family's own spread is 6.9× narrower than this null and is NOT the interval on this
> figure.

**The thesis stands where it stood, and now it says so on the page.** The level leg is determined
positive at 16.85 sems over 21 seeds. The inference leg's only measured discrimination does not
clear its own null. *The advantage we can demonstrate is the price, not the knowing* — and that is
now on the surface rather than in a commit message.

## The reading, and one number that moved

| | Item's figure (from `ab71cf877`'s record) | Published |
|---|---|---|
| mean AUC over 3 seeds | 0.5697 | 0.5697338 |
| null sd | 0.0576 (64×42) | **0.05778 (63×42)** |
| null SDs above 0.5 | 1.21 | 1.207 |
| exact 95% null | — | 0.3870–0.6130, p=0.231 |
| family sd / null sd | 6.9× too narrow | 6.93× |

**Why the null sd differs from the item's:** the three rows do not share a population (64×42,
64×42, 63×42) and the publisher takes **the widest null among them**, which is the smallest
population's. That is the direction that makes the reading *harder* to clear, and it is stated in
the payload (`null_sd_population`) rather than left for a reader to assume it went the other way.
The verdict is identical either way.

**A prediction registered before it was run, and confirmed:** the exact Mann-Whitney enumeration
would place 0.5697 *inside* its null. It does (p=0.231). It also cross-checks the closed form:
the exact half-width is 0.1130 and 1.96 × 0.05778 is 0.1133 — agreement to three places, asserted
in a control rather than assumed, because a closed form that has drifted from the enumeration it
approximates is a ruler nobody would notice was wrong.

## The wrong repair, refused by a control

P2 of the prior turn refuted the obvious move — publish the family's spread as the AUC's error
bar — **before** anyone built it. That refutation is now enforced, not just recorded:

`test_MUTATION_the_seed_familys_own_spread_is_NEVER_this_figures_interval` checks the published
`null_sd` against the **half-width of the exact combinatorial null**, an independent derivation.
A family spread substituted there cannot satisfy it at any sample size: 1.96 × 0.00834 = 0.016
against a half-width of 0.113. The refuted ruler is still published — as
`family_spread_is_not_the_interval`, with the ratio that refutes it — because a reader shown only
the right ruler cannot tell that the wrong one was considered and rejected.

## R15 — eight mutations, each run and reverted, each firing on one control

| Mutation | Control that reds |
|---|---|
| `null_sd = statistics.stdev(aucs)` | `..._spread_is_NEVER_this_figures_interval` |
| distance divided by `null_sd / sqrt(n)` | `..._earns_no_sqrt_n` |
| call site drops `auc_family` | `..._REACHES_the_error_bar_off_the_LIVE_artefacts` |
| `_auc_rows` defaults a missing population | `..._counted_out_not_defaulted` |
| the "DIFFERENT family" label made unconditional | `..._says_so_in_its_own_sentence` |
| refusal branch drops `ownNull(...)` | `..._AGAINST_ITS_OWN_NULL_and_not_as_a_count` |
| spread rendered with no "seed sensitivity" label | `..._NEVER_renders_as_the_AUCs_interval` |
| `ownNull` returns `""` on an absent block | `..._says_so_rather_than_going_quiet` |

Mutations were applied in this isolated worktree, never in the shared tree.

## What landed

- `tools/generate_value_arms_data.py` — `_auc_null_sd`, `_auc_rows`, `_auc_against_its_own_null`,
  `_auc_null_reading`; `AUC_FAMILY_FLOOR_PATH` + `AUC_FAMILY_SOURCE`; the new key on all four
  branches of `_family_discrimination`; `auc_family` threaded through
  `generate` → `build` → `_error_bar`.
- `site/capabilities/index.html` — `ownNull`, rendered on **every** branch including the refusal,
  plus the seed-sensitivity label on the measured branch's spread.
- `site/data/value_arms.json` — regenerated. **Proved to own only its own fields:** the diff is
  the new block, `generated_at` and `publishing_tree_commit`. Nothing else moved.
- Six controls in `tests/tools/test_generate_value_arms_data.py`, three in
  `site/test_the_baseline_comparison_reaches_the_reader.py`.

## What this turn did NOT do

- **Did not fold `auc3` into the published advantage family.** It would move the advantage from 18
  draws to 21 (the sibling's subject, with twelve more seeds in flight) and would *lose the served
  book* — `folded18` declares none. Nothing about the discrimination reading needs that fold: the
  null comes from the figure's own outcome counts.
- **Did not touch `tools/fold_noise_floor_family.py`.** The sibling holds it.
- **The reading is over three seeds of one instrument, and says so.** It is not a bound on the
  advantage and never renders as one.

## What should happen next

When the AUC-carrying family grows — or when any future floor records `discrimination_auc` on
every row — `_family_discrimination` moves to `state: measured` **and the null reading follows the
rows automatically**, because it reads the family's own seeds first and falls back to
`AUC_FAMILY_FLOOR_PATH` only when they carry nothing. On that day
`AUC_FAMILY_FLOOR_PATH` becomes dead weight and should be deleted with the branch that reads it;
the control `..._REACHES_the_error_bar_off_the_LIVE_artefacts` stays green through the change,
which is the direction a control must stay green in.
