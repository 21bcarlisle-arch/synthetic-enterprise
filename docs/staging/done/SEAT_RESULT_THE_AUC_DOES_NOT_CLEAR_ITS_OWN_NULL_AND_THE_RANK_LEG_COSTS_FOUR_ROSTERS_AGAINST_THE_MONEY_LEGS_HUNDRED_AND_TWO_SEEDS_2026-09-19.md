# SEAT RESULT — the AUC does not clear its own null, no single draw does, and the rank leg costs about four rosters against the money leg's 102 seeds

**Severity:** RECORDED · **Lane:** A_strategy_governance

Lane: A_strategy_governance · 2026-09-19 · delivery seat, Lane 0
Claim: `price-the-discrimination-auc-against-its-own-null`
Subject: `docs/observability/value_cycle_ab_s1_noise_floor_next12_20260917.json`,
`tools/generate_value_arms_data.py`, `site/capabilities/index.html`

---

## The verdict, on the surface

**0.5629 does not clear its null.** Across the twelve seeds of the next12 family the mean
discrimination AUC is 0.56290 on a population of ~106 scored renewals. The statistic's own null
standard deviation on the widest of those populations (64 retained × 41 departed) is 0.05802, so
the mean sits **1.08 null SDs** above the no-information point against the 1.96 a direction needs.
The exact Mann–Whitney null is 0.3864–0.6136, two-sided p = 0.281. **Inside it.**

**No single draw clears it either.** Graded each against its OWN population's null rather than the
family's: 0 of 12, the widest reading 1.50. That is a different claim from the mean's and it had
never been made — twelve draws each sitting 1.1 SDs out and twelve straddling chance have the same
mean and license opposite next actions.

**The advantage now rests on neither leg.** The money leg states no sign (0.69 SEMs from zero,
`selection_distinguishable_from_zero: false`) and the rank leg does not clear its null. Both
readings are "we cannot tell", and both are on the page.

## What pooling is worth, with the dependence measured

Dividing the single-draw null by `sqrt(12)` moves the reading from **1.08 to 3.77 null SDs** and
states the advantage. It is refused, and the refusal is now evidence rather than an argument:

* **Twelve rows carry ten distinct AUC values.** Seeds 3100001/3100007 and 3100008/3100009 each
  return the identical figure to sixteen significant digits — the same labelling scored twice.
* The scored roster barely moves across the family: 60–68 retained against 41–43 departed.
* The family's own spread (sd 0.01569) is **0.27 of one draw's null sd**. Twelve independent
  rosters would scatter by about a whole one.

The replication unit for a rank statistic is the **roster**, not the seed. A seed here re-draws the
per-household elasticity *inside* one book; it does not add households, and the null's width comes
from the two outcome counts and from nothing else. So the independent end is not an optimistic
reading of this family — it is credit for the wrong unit. Both ends are now published, because the
gap between them is the finding.

## The price of a sign, in the unit that actually replicates

At this distance, and only if it stayed there, a sign needs about **4 independent rosters** —
against the **102 seeds** the money leg prices in the same artefact. Different units, and both
counts are now published out of ONE file so the comparison cannot become a two-artefact mispairing.
This is the actionable half: 102 seeds is roughly six days of continuous compute on the only box;
four independently drawn books is not, and the rank question is the one nobody had costed.

## Three things the drawn direction got wrong, kept beside the work

1. **"The rank statistic has never been priced" was stale.** `_auc_against_its_own_null` has
   existed in `tools/generate_value_arms_data.py` since 2026-09-17, computes exactly this null,
   already refuses the `sqrt(n)`, and **already renders** on the capabilities page via `ownNull`.
   What did not exist was the per-seed bound, the pooled bound stated as an interval with its
   dependence measured, and the price. Those are what landed.

2. **The permutation the direction asked for cannot be computed from disk, and a stronger thing
   already was.** "Permuting the retained/left labels over each seed's scored roster" needs the
   per-decision roster. The floor producer (`tools/run_value_cycle_ab.py`, the seed-row writer)
   records `discrimination_auc`, `auc_population` and `auc_scored_share_of_priced` and **drops
   `scored_decisions`** — so no floor artefact on disk carries a roster, for any seed, at any
   commit. The exact Mann–Whitney enumeration in `_auc_null` is the same null computed
   combinatorially rather than sampled, over all arrangements, and it is what the page publishes.
   *(Owed, one line: the floor row should carry `scored_decisions` so a per-seed tie-corrected null
   becomes possible. Filed as the next item, not done here.)*

3. **The closed form was validated against a real roster before it was relied on.** Monte-Carlo
   permutation, 200,000 shuffles, over the real scored roster in
   `value_cycle_ab_s1_three_arm_20260918.json` (104 decisions, 60 retained / 44 departed, real
   tied `believed_p_retain` scores): permutation sd **0.057814** against the tie-corrected analytic
   **0.057552** — agreement to 0.5%. Ties are immaterial on this belief (83 distinct scores in 104;
   the tie term shrinks the null variance by 0.066%), so the untied closed form is not a
   hand-wave. The same permutation puts that roster's own 0.5566 at two-sided **p = 0.329** — also
   inside, on a different run at a different instrument.

## What moved

* `AUC_FAMILY_FLOOR_PATH` moved from the **3-seed** auc3 floor to the **12-seed** next12 floor.
  Same instrument by the block's own stated test (`git diff c9bd2eae7 a178b56d6` over the four
  value-arm paths is empty), same world `39a192ce04c1eda8`, same redraw key and mode. **The move is
  in the unflattering direction** — auc3 read 0.5697 at 1.21 null SDs, next12 reads 0.5629 at 1.09 —
  which is the evidence the family was chosen on draws and not on its answer. It also buys the
  one-artefact pairing with the money leg, which auc3 could not make: it carries no
  `distance_to_a_sign`.
* Per-seed bound, `pooled_bound`, `rosters_to_state_a_sign` and `against_the_money_legs_price` are
  new fields on `error_bar.discrimination_across_the_family.against_the_statistics_own_null`, and
  all four render.

## Controls

Producer side, each mutation run and reverted (`tests/tools/test_generate_value_arms_data.py`):
grade every row by the family's ruler → the per-seed leg reds; publish the independent end as the
headline → the pooling leg reds; count rows instead of distinct values → the dependence leg reds;
price a sign at a constant → the monotonicity leg reds. One mutation did **not** fire and it was an
**equivalence, not a missing leg**, recorded as such: falling back to `NOISE_FLOOR_PATH`'s money leg
changes nothing because that artefact carries `distance_to_a_sign: null`; against a fallback that
does carry one (next12, 102 seeds) the leg fires.

Reader side (`site/test_the_baseline_comparison_reaches_the_reader.py`): two legs, both observed
red before the renderer change and green after — the per-draw verdict, the refused pooling labelled
as refused, and the two prices with their units on them.

## Correction, added 2026-09-19 by the next invocation of this claim: "what moved" had not moved

The section above was written before its bytes were landed, and they were not landed. Measured on a
freshly fetched shared tree at `69df071a7`:

* `site/data/value_arms.json` **was** at HEAD carrying the full 12-seed block — `seeds_read: 12`,
  `pooled_bound`, `rosters_to_state_a_sign`, `against_the_money_legs_price`, all of it. It got there
  inside `c42338422 Auto-process run complete: report + LATEST.md + site/`: the publishing daemon
  regenerated `site/` from the **working tree** and committed the output.
* `tools/generate_value_arms_data.py` at HEAD still read `AUC_FAMILY_FLOOR_PATH = ..._auc3_...` and
  `AUC_FAMILY_SOURCE = "the 3-seed AUC-carrying floor of 2026-09-17"`. The generator's +285 lines,
  the renderer's +54, and all +210 lines of the two control files were staged in the shared index
  and **in no commit**.

So the published page said 12 seeds and the only committed code able to produce it said 3. A
checkout of HEAD that regenerated the feed would have reverted the reading to `auc3` — 0.5697 at
1.21 null SDs — silently, and the verdict would have survived the revert because both families are
inside their null. **The output landed and its source did not**, which is the mirror of the class
already on the queue this morning (a correction made in the rendering and not in the source). The
daemon is the mechanism: anything left dirty under `site/` gets published on its next tick, so an
unlanded generator change ships its consequences and hides its cause.

Measured before landing, not asserted: the working generator regenerated into a gitignored path
reproduces the committed feed's `error_bar` **byte-identically**, AUC block included. The three
top-level keys that differ (`book`, `realised`, `producing_commit`) differ only in
`publishing_tree_commit`, which moves with HEAD by construction. That is what makes these the bytes
that produced the published reading rather than a plausible substitute for them.

Controls re-run on the shared tree before landing: `tests/tools/test_generate_value_arms_data.py`
260 passed; `site/test_the_baseline_comparison_reaches_the_reader.py` 170 passed, 1 skipped.

**What is still owed is unchanged and is item 2 above** — the floor row should carry
`scored_decisions` so a per-seed tie-corrected permutation null becomes possible. Nothing in this
correction touches the verdict: 0.5629 does not clear its null, 0 of 12 draws clear theirs, and the
rank leg costs about four rosters against the money leg's 102 seeds.

## What would refute this

A per-seed permutation over real scored rosters that put the per-seed null materially below
0.058 — which needs the producer change in item 2 above. Or four independently drawn books whose
mean AUC holds near 0.563: that clears the bound and settles the thesis on ranking. Nothing here
argues the belief is uninformative; 106 renewals cannot tell either way, and the mirrored overclaim
is the same defect.
