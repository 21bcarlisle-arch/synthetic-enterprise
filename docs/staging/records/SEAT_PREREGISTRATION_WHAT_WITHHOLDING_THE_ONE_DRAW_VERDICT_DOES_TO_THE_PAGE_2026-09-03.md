**Severity:** RECORDED · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** none — Lane 0 delivery

# Pre-registration: what withholding the one-draw verdict does to the page

*Delivery seat, 2026-09-03, claim `current-world-bound-can-never-be-true`. Written BEFORE the edit,
against `site/data/value_arms.json` as published at `7304bbe51` (`current_world.resolved: true`,
`bound_available: true`, bound stdev £991.455146, n=3, min £450.99, max £2,433.70).*

Subject: actioning the recommendation in
`docs/staging/SEAT_FINDING_THE_RESOLVED_VERDICT_IS_ONE_DRAWS_AND_A_THIRD_OF_THE_REDRAWS_REVERSE_IT_2026-09-03.md`
— option 2, **scoped to the current-world block only**. `_resolvable` has six callers and its
semantics are NOT changed; changing them would move figures no pre-registration covers.

---

## What I am about to do

Add a stability test on the CURRENT-WORLD block: substitute each floor seed's own
`value_advantage_gbp` for the point estimate against the same bound. If the per-seed verdicts are
not unanimous, the block states no binary verdict and publishes the re-draw range instead.

The third state is named, not folded into an existing one. Before this edit `resolved: None` means
exactly one thing — *no bound was read*. After it, `None` can mean two things, and a reader who
cannot tell them apart is the state-conflation defect this project has shipped before. So the
withheld case carries its own key with its own reason, and `bound_available` stays `true`.

## Predictions

**P1 — the re-draws straddle.** The floor's three seed rows for `value_advantage_gbp` on
`value_cycle_ab_s1_noise_floor_20260903.json` are £1,467.23, £2,433.70 and £450.99 against
stdev £991.455146. Substituted one at a time they give True, True, **False** — not unanimous.
*(Stated in the finding, so this is confirmation of a read, not a discovery.)*

**P2 — the payload withholds.** After the edit `current_world.resolved` is `null` while
`current_world.bound_available` stays `true`, and a NEW key states the reason in words that do not
collide with `why_no_bound`.

**P3 — the reader sees the range, not a verdict.** The rendered headline stops containing
`CLEARS` and gains the re-draw range £451–£2,434. The point estimate £2,336 and its date stay.

**P4 — the existing door rung goes RED, and that is correct.**
`site/test_the_baseline_comparison_reaches_the_reader.py:2081`
(`if cw.get("bound_available"): assert cw.get("resolved") is not None`) fails against the new feed.
It is keyed to TODAY'S ANSWER — "a bound implies a verdict" — and the property is "a bound implies a
verdict OR a named reason there is none". I will re-key it, not delete it. **If it does NOT go red,
my change did not reach the feed** and I should look there before believing anything else.

**P5 — nothing else on the page moves.** No figure outside `current_world` changes: not the
2026-08-31 headline £12,071, not `selection_gbp`, not the provisioned panel, not the DD blocks.
This is the prediction I am least sure of and the reason this file exists — `**bound` is spread into
the block and the clause composer is shared. **A move anywhere else is a defect in my edit, not a
finding about the page**, and I will report it as such rather than rationalising it.

**P6 — the withheld verdict is not the flattering direction.** Withholding removes a `true` the page
currently publishes. If the edit somehow leaves a `resolved: true` standing on a straddling floor,
that is fail-open in the flattering direction and the whole repair failed.

## Constraints that must hold

- `_resolvable` is byte-identical after this edit; its five other call sites are untouched.
- No test is deleted. The rung at 2081 is re-keyed to the property and keeps a subject on both legs.
- Each new guard is mutation-proven separately, under `python3 -B` (a stale `.pyc` has reported
  SURVIVED here before).
- The straddle guard has a SOLE WITNESS distinct from the world/leg guards' witnesses, or it is an
  equivalence riding on theirs.

## What would refute the whole approach

If the re-draw range turns out to be an artefact of n=3 rather than of the quantity — i.e. if a
larger seed family collapses it — then withholding is over-conservative and the right repair is a
proper interval on the mean. I cannot settle that in this tick and am NOT claiming it is settled:
withholding a verdict is reversible and publishing a wrong one is what is on the page now.

---

## GRADED, after the edit — 2026-09-03

**All six confirmed. None refuted, and P4 and P5 are the two that carried information.**

| | prediction | outcome |
|---|---|---|
| P1 | re-draws straddle | **CONFIRMED** — £1,467.23 / £2,433.70 / £450.99 read from the artefact's own `seeds`; verdicts True, True, False |
| P2 | payload withholds, `bound_available` stays true | **CONFIRMED** — `resolved: null`, `bound_available: true`, `verdict_withheld_because` set |
| P3 | reader sees range, not verdict | **CONFIRMED** — headline drops `CLEARS`, gains "spans £451 to £2,434" |
| P4 | the door rung goes RED | **CONFIRMED** — red at `site/test_the_baseline_comparison_reaches_the_reader.py:2083`, re-keyed not deleted |
| P5 | nothing else moves | **CONFIRMED** — see below |
| P6 | withholding is not the flattering direction | **CONFIRMED** — a published `true` was removed; no `resolved: true` survives on a straddling floor |

**P5, stated exactly.** Five keys changed outside `current_world`/`headline`: `/generated_at`,
`/producing_commit/publishing_tree_commit`, `/producing_commit/reading`,
`/book/produced_by/publishing_tree_commit`, `/book/produced_by/reading`. All five are the
regeneration stamp and the publishing-tree hash moving from `0b8a8156f` to `7304bbe51` — they move
on **any** regeneration and are not caused by this edit. **No domain value moved anywhere on the
page.** `_resolvable` is byte-identical and its five other call sites are untouched.

**Two predictions I did not write down and should have.** Two *existing* generator controls also
went red — `test_the_current_world_bound_takes_only_the_undecomposed_leg_of_this_world` and
`test_the_generator_reads_the_current_world_floor_from_its_own_constant`. I predicted the door rung
would break and did not think to ask which other controls carried the same "a bound implies a
verdict" assumption. Both were keyed to today's answer in exactly the way P4 anticipated, and I
found them by running the suite rather than by reasoning. The prediction was too narrow; the
underlying diagnosis was right and generalised one layer further than I applied it.

**Mutations, run under `python3 -B` and reverted.** Four, each red on its own witness:
(1) guard removed → straddle control red; (2) withhold unconditionally → **the unanimous witness
red**, which is what proves the guard is a judgement and not a constant; (3) reason named but
verdict still published → red; (4) payload withholds while the page still prints it → door rung
red. After revert: 98 generator tests and 78 door tests pass, and the payload is byte-identical to
the pre-mutation one.

**What is NOT settled, restated because withholding is easy to mistake for answering.** Whether the
advantage is real remains unmeasured. This page now says so instead of saying `true`. The n=3
question in "what would refute the whole approach" above is untouched and is the next measurement,
not a closed one.
