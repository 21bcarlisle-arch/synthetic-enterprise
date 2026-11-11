**Severity:** BLOCKING · **Lane:** A_strategy_governance · **Epoch:** unassigned · **Atom:** `unminted`

# [DIRECTOR-RULING] End the feature freeze: about a third to features, correctness first, and a balance review before each week

**Type:** RULING, through the advisor channel. The director's words, from chat, Wed 11 Nov:

- 07:23 GMT: "Is it doing. Productive work? What progress, what next? Who is the balance between clearing backlogs, fixing the harness and feature build for sim and for supplier?"
- 07:27 GMT, answering the advisor's recommendation: "Go ahead. But we need to review the right balance before we start each week of new tokens, and perhaps accelerate some things if we have excess tokens at the end of the week"

## What the advisor put to him (and he accepted)

Origin's last 18 hours split as follows: about 55% correctness and backlog, 25% harness, 10% model trials, 5% knowledge, and about 0% features. That is by design, under the 26 Oct correctness ruling. The exit test, "one cold read finds no new class", is not converging. The tenth read, done in a new reader's trade, found four new classes. Each new trade finds what the last could not, so the test may never pass on its own. Meanwhile the world and supplier work he has steered sits behind it:

- the PV, battery, EV and load range;
- asset operation;
- the supplier persuading homes to change and invest;
- needs and reactions.

## The ruling

1. **The publish gate does not change.** Nothing reaches the site unless it passes every gate. Correctness has the first claim on capacity whenever a book is refused.
2. **The full freeze on features ends.** Features get **about a third** of capacity. That means the world and the supplier, drawn from the queued director steers in the machine's own priority order. Correctness and backlog keep first claim. Harness work is held to what keeps the machine running and learning. The 26 Oct ruling is amended to this, not withdrawn.
3. **The exit test is narrowed.** The stretch's exit becomes "one cold read finds no new **serious** class". A serious class is one that changes money (a bill, a balance, a payment, a P&L figure) or a customer outcome (a dunning step, a refund, a supply or switching event). New presentation and diagnostic classes are still fixed and still get gate rows, but they no longer hold the exit. The machine states the dividing rule in its own words and applies it the same way to every read.
4. **There is a weekly balance review before each new week of tokens.** Before each Monday 03:00 GMT reset, the machine proposes the coming week's split across correctness and backlog, harness, world features, supplier features and knowledge. It bases the proposal on the past week's measures:
   - the learning loop's hit rates;
   - regressions;
   - serious classes per read;
   - whether the site published;
   - the week's usage curve.

   The proposal names what each share is for. The advisor puts it to the director. **If he has not answered by the reset, the proposal stands**, and he can change it at any time.
5. **Accelerate at the end of the week when there is spare.** The machine keeps a short, ranked **accelerate list**: work that is ready to draw and worth pulling forward, such as extra books, extra knowledge passes or a feature slice. From Saturday, if the week's usage curve shows more than the reserve unspent, draw from that list to spend the excess before the reset. The reserve is about 10 points kept for Monday. The list is decided in the weekly review, not on the day.

## Now

- This week's split is about 55-60% correctness and backlog (the close-refund fix and the next book first), about 30% features, and the rest harness and knowledge. The machine may adjust it, and says so if it does.
- This morning's trim still applies: the burn is running about a day short, and there are no more model-comparison arms this week. The feature third is drawn inside that budget, not on top of it.
- First weekly review: before Mon 16 Nov 03:00 GMT.

## Done

Actioned on 11 Nov by the worker tick:

1. **The publish gate is unchanged.** Nothing was touched on that path.
2. **The full freeze ends; features get about a third.** `priority_order.yaml`
   `correctness_stretch.feature_share: 0.33` is read by `supervisor.correctness_stretch_feature_share()`.
   On that fraction of BUILD draws, the stretch's held atoms (steps 6 to 13 and `holds`) are the pool.
   On the rest they are refused as before. The stretch is amended, not withdrawn. Lane 0 no longer
   refuses the seat's own focus while a share is set, because the seat spends the share there. If the
   share is unreadable, it fails closed to the 26 Oct freeze. Control:
   `test_the_feature_share_gives_held_atoms_a_turn_in_its_fraction_of_draws` (0 of 300 draws at
   share 0, 300 of 300 at share 1, about a third at 0.33). Dropping the branch makes it fire, which I
   checked. To return to the full freeze, including while a book is refused: `feature_share: 0`.
3. **The exit test is narrowed to SERIOUS classes.** It is restated in `exit_test`, and the dividing
   rule is in `serious_class_rule`, in the machine's words. A class is serious if it changes money
   (an amount billed, owed, paid or refunded, a balance, a payment's size or date, or a P&L figure),
   or if it changes whether or when a dunning step, refund, supply event or switching event happens.
   A class that is unproven either way counts as serious (F11).
4. **A weekly balance review before each reset.** The Friday step of `background/weekly_rhythm.py`
   now carries "The balance for the coming week". It proposes the five-way split from the past week's
   measured hit rates, regressions, serious classes per read, publish state and usage curve, and
   names what each share is for. It is staged to the advisor and stands at the reset unless he
   answers. The first one is Fri 13 Nov, which is before Mon 16 Nov 03:00 GMT.
5. **The accelerate list.** `priority_order.yaml` `accelerate: []` is ranked and decided in that
   review. It stays empty until the first review fills it.

This week's split (55 to 60% correctness and backlog, about 30% features) is what the 0.33 share
gives the BUILD draw. The seat's focus currently holds W3_3, W2_18 and W2_19 in `not_now` for
attribution under the exit-test book. That is the seat's call to revisit, now that the share exists.
