**Severity:** RECORDED · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** none — Lane 0 delivery

# PRE-REGISTRATION — why the two three-arm runs in world `39a192ce04c1eda8` disagree eighteen times about the composition of the advantage

**Filed:** 2026-09-22, BEFORE any contrast was computed. Drawn as Lane 0 delivery,
`the-arms-page-cannot-say-whether-the-advantage-is-choosing-or-the-price-level`.

Everything below was written from artefact METADATA only — `generated_at`, `producing_commit`,
`world_identity`, `book_identity`, `folded_from`, `value_arm_pairing` — and from the two headline
numbers the item itself quotes. **No selection figure, no level share, and no spread from any floor
family had been read when this was written.** That is the whole point of filing it: the instrument
being tested is my own attribution, and an attribution filed after its answer is not one.

---

## 1. What is being asked

The published headline says the advantage is **98.5% price level, 1.5% selection**
(`value_cycle_ab_s1_three_arm_20260908.json`, selection £270.21). The run that fixed the
population defect says **5.5% level** (`..._20260918.json`, selection £4,327.01). One book, one
world, one question — and the two answers are each other's opposite, an ~18× gap in level share.

Three things moved between them and so **nothing is attributable as it stands**:

| | `three_arm_20260908` | `three_arm_20260918` |
|---|---|---|
| producing commit | `04361d6c7` | `b329e702b` |
| book — control arm accounts settled | **164** | **154** |
| book — elec / gas / dual / end-of-window | 146 / 105 / 87 / 73 | 136 / 90 / 72 / 55 |
| the arms' own populations | 281 vs 215 — **two populations** | 110 vs 107 — resolved |

## 2. The fourth variable the item does not name, and which I think is the answer

The item names book, commit and arm code. There is a fourth, and the metadata makes me think it
dominates all three: **`level_share` is a ratio whose denominator contains a quantity this repo has
already published as having no determinable sign.** `site/data/value_arms.json` carries
`current_world.selection_leg.no_sign` — the selection contrast re-drawn nine times falls on both
sides of zero — and `selection_distinguishable_from_zero: false` on the nine-seed floor.

A share built on a numerator that straddles zero is not a composition. It is a ratio that can take
any value on the line, and two draws of it can differ by eighteen times without any of book, commit
or arm code having done anything at all.

## 3. THE PREDICTIONS — filed before the answer

**P1 (the main one). The redraw noise alone spans BOTH published answers, so no variable is needed
to explain the disagreement.** Concretely: in the eighteen-seed single-arm family
(`..._noise_floor_folded18_single_arm_20260917.json`, what `NOISE_FLOOR_PATH` names),
`level_share_spread` will have **min < 0.0551 and max > 0.9848**. Both headlines lie inside one
family's ordinary re-draw range, at a fixed book, a fixed world and — by that family's own
`value_arm_pairing.same_value_arm: true`, `differing_paths: []` — a fixed value arm.

*Refuted if* either published share falls outside the family's observed range.

**P2. The honest one-book pairing cannot state the selection leg's sign, and the page's job this
turn is to say how many seeds it needs rather than to state one.** The only floor families on disk
that record a REALISED book are the two twelve-seed ones (`next12_20260917` @ `a178b56d6`,
`next12_at_18327d977` @ `18327d977`), and both realise **154 accounts — the `20260918` run's book,
not the published headline's 164.** The prior lane measured that family's sd at 5,398 against the
eighteen-seed family's 1,631. At n=12 that is a sem near 1,558; for the mean to clear zero it would
need to sit beyond ±3,200, and every centre this repo has measured for this leg has been between
−1,078 and −624. **So P2 predicts t < 2.2 and p > 0.05 on the twelve-seed one-book pairing: NO
SIGN.**

*Refuted if* the one-book pairing yields p ≤ 0.05.

**P3. The pairing the page publishes today cannot be checked at all, and that is the defect worth
landing.** `CURRENT_WORLD_NOISE_FLOOR_PATH` resolves to `..._noise_floor_20260909b.json`, whose
`book_identity` is **`null`** — the field is absent, not disagreeing. That family was drawn at
commit `c066c114b` on 2026-09-09, a day after the headline run it is used to put an error bar on.
**A floor that cannot name its book agrees with every book**, including the 164-account one it is
paired with and the 154-account one every later family realises. I predict the feed has no check on
this — that nothing in `tools/generate_value_arms_data.py` compares the floor's book to the run's
book — and therefore that the error bar under the headline is unpaired by construction rather than
by accident.

*Refuted if* a book-pairing check already exists and fires.

**P4 (the cost, taken from the artefact's own record).** `value_arm_pairing` on the eighteen-seed
family records that when the value arm last differed, the step between two code trees was
**£671.31, 20.4 sems from zero**, between `c066c114` and `9f0ab066`. £671.31 is **2.5× the entire
published selection figure of £270.21.** I predict this is decisive for the commit variable: the
code-tree step alone is larger than the headline it would be explaining, so "the commit moved"
cannot be dismissed as second-order — but it also cannot be the 18×, because it is an order of
magnitude below the £4,327 gap. Both variables are real and neither is sufficient; **P1 is what
carries it.**

## 4. What I will do with each outcome

* **P1 holds** → the page stops owing an explanation for the 18×, because there is no 18× to
  explain: it is one family's spread read as two findings. The page must say so.
* **P1 refuted** → the gap is real and attributable, and the one-variable re-run at one commit over
  one book is owed for real. I will name the run and its cost rather than launch it inside a
  bounded tick.
* **P2 holds** → the page says how many seeds it needs. That is the deliverable, and it is a
  result, not a failure.
* **P3 holds** → a book-pairing refusal goes into the feed and
  `error_bar.selection_leg.sign_withheld_because` gains a reason it can actually fire on.

## 5. Marking

The marking goes in the RESULT note filed beside this one, **and beside each prediction, not over
it.** A prediction revised after its answer is not a prediction.
