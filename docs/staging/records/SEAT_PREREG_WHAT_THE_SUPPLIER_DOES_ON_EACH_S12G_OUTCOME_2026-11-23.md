**Severity:** RECORDED · **Lane:** G_data_learning · **Epoch:** unassigned · **Atom:** `unminted`

# Pre-registration: what the supplier does next on each outcome of s.12g (23 Nov 2026, 05:20Z)

**Filed before the result exists.** At 05:07Z on 23 Nov, `/var/tmp/vtn-out/A/member_13131_14141.json` did not
exist. Nothing under `/var/tmp/vtn-out/` was opened or listed to write this. The only check was a bare `test -e`
on that one path. s.12g (`docs/design/THE_VALUE_TEST_REDESIGN.md` §12g, predictions P1–P4 filed 21 Nov 09:38Z)
ends at about 05:30Z on 24 Nov. The reader is continuation `s12g-has-a-reader-when-it-ends`.

**Why this exists.** A next lever chosen after P1 is read cannot be told apart from a lever fitted to P1. That
has happened once already, with the 0.12 cut (§12e, §12f). This record fixes the choice for each outcome before
the outcome is known. The reader grades against it and opens the run it names. It does not pick again.

## The quantity and how it maps to the outcomes

The quantity is P1 as §12g defines it: on book 61118, churn pair 13131/14141, per household, (cut run: value arm
minus flat book) minus (twin run: value arm minus flat book). It is in £ per household-year over the twin's
control-arm household-years, averaged over the two seeds, with a 95% interval from 2,000 household resamples
(seed 20261117), as printed by `grade_new_book.py` (sha256 `3cb5f92d5f10…`).

The outcome here is set by the **interval**:
- **ABOVE:** the lower bound is above zero.
- **STRADDLE:** the interval contains zero.
- **BELOW:** the upper bound is below zero.

P1's own verdict is still published by its own rule, which the 21 Nov filing set and this record does not
change: refuted when the point is below zero, held only on ABOVE, "cannot tell" otherwise. Under that rule, a
STRADDLE with a negative point is P1-refuted. The lever choice below still treats it as STRADDLE, because the
interval cannot tell the arms apart. Both labels are published side by side, so neither can be swapped for the
other later. §12g predicted −£0.40 (−£2.00 to +£1.20), which is a STRADDLE with a negative point.

**Correction to the drawing item's wording.** The item says the 0.12 cut is "now tested on the same pair it was
fitted on". That is not what s.12g does. The 0.12 was fitted on the default book at churn pair 11111/22222
(§12e: the lowest cut that reaches 6 of §12c's 9 flips). s.12g tests it on book 61118 at 13131/14141. No
earlier run used that churn pair. Of the 9 flips, 2 recur in 61118 by id (SYN-2016-557, SYN-2016-498), and both
are re-drawn households (§12g). What this record has to answer is what each outcome says about that in-sample
fit.

## Decomposition the reader prints first, whatever the outcome

On the advantage measure, P1 (cut − twin) = (cut − A) + (A − twin). P2 is the second term. P3 minus P3b is the
first: P3 is its value-arm part, and P3b is its flat-book part. The reader quotes all three before naming the
branch. They do **not** choose the branch. Only P1's interval
does. They say which part of the branch's explanation is carrying it.

## ABOVE: the lower bound is above zero

**What it means for the 0.12 fit.** On a book the cut was not fitted to, the per-customer arm beats flat rules.
At most 2 of the 9 fitted households recur, and both are re-drawn, so "the cut reaches the households it was
chosen for" cannot carry P1. The fit is no longer the explanation of the sign. It is still a measured constant
from one book, now held on a second. Its origin line in `growth_desk.py` should say exactly that, and no more.

**The next lever: the policy carries it, on today's code.** This is the open row
`the-live-renewal-belief-ranks-leavers-backwards` (`docs/direction/wrong_triage.yaml`). Its owner is
`company/policy/decision_policy.py`, where a policy carries the corrected ending-term belief. Both switches,
`renewal_belief_by_ending_term` and `retention_cut_at_the_flips`, are on origin, default off. s.12g ran at
`870201d1e7` plus a port. Origin has since moved (the MSC, dunning, won-switch supply, roster). So the open
question is whether the result survives the world the live company now runs in.

**The run (two configurations, about 23 h).** Origin at the launch commit, book 61118, churn pair 13131/14141,
the same driver shape and grader method. Configurations: (1) both switches on; (2) both off, which is the twin.
The one variable inside the run is the pair of switches, cut against twin. Across runs, the variable is the tree,
pin against origin.
- **Holds:** P1's own rule, ABOVE on origin.
- **Refuted:** the point is below zero.
- **Also graded on this run:** the row's own switch-on rule, the departure interval of a clean-book grade.

**What does not move on this outcome.** Turning either switch on by default waits for the row's rule and for the
director's 24 Oct ruling (levers after the basics). The reader raises it in `for_the_director` with a
recommendation, and does not switch anything.

## STRADDLE: the interval contains zero

**What it means for the 0.12 fit.** The in-sample read was −£0.33 (−£1.77 to +£0.96), also a straddle. So the
out-of-sample read neither shows the fit was harmless nor shows that the fit made the gain. "The cut wins back
A's loss against the twin, and no more" survives. The 0.12 stays an in-sample constant with no out-of-sample
support for either sign.

**The next lever: the cut on rank at the twin's volume, so that no fitted number is left.** Two things differ
between the cut run and the twin: whose belief ranks the renewals, and how many renewals get offered. The 0.12
fixes the volume through a level fitted on another book. The thesis is about who is offered, not how many. So
the lever offers to the **same share** of renewals the twin offers, chosen by A's belief.
- The switch: offer at a renewal when A's conditioned belief is at or above the q-quantile of the desk's own
  beliefs on the previous 12 months' renewals. That is learned in-run, and a real supplier could observe it.
- **q is fixed by rule now:** the twin run's value-arm share of renewals offered on 61118, pooled over
  13131/14141, as read from the twin's sidecar after the reader has published P1. q is a volume control taken
  from the comparator. It is not tuned on any outcome.
- Default off. Knowledge page first (K8), with this record as its origin.

**The run (one configuration, about 11.5 h).** The pinned tree `/var/tmp/value-test-cut012` plus that switch
alone (re-pinned, and the deviation stated in §12g's style), book 61118, 13131/14141, with A's belief on. It is
graded against the twin and the cut files already on disk, so it uses no new box-time for comparators.
- **Holds:** rank-at-q minus twin, P1's measure, is ABOVE.
- **Refuted:** the point is below zero.
- **Also printed:** rank-at-q minus cut, the one-variable effect of replacing 0.12 with the volume match.

**Measured first, in minutes, before the box is asked.** If 0.12 sits within ±5 percentile points of q in the cut
run's value-arm belief distribution on 61118, the two rules select nearly the same set. Then the run cannot
answer anything the cut run did not, and it is **not launched**. The reader then files that finding, and the
lever falls to BELOW's second step. Writing this threshold down now is what stops it being picked after the
distribution is seen.

## BELOW: the upper bound is below zero

**What it means for the 0.12 fit.** Out of sample, the per-customer arm loses to flat rules by more than the
interval allows. The in-sample near-parity (−£0.33) was then at least partly the fit: the cut was chosen to
reach the households it was graded on. The 0.12 is not carried anywhere. Its origin line records that it failed
out of sample. The row `the-live-renewal-belief-ranks-leavers-backwards` stays open, and its "a policy carries
the corrected belief" owner is suspended for the retention decision. A belief with AUC 0.806 that loses money to
one with AUC 0.333 says the money is not in the ranking. That goes to `for_the_director` as a thesis result, with
the reader's recommendation, in the same commit that publishes P1 ([FOR-THE-DIRECTOR]).

**The next lever, two steps, with the order fixed now.** A loss has two explanations:
- A chooses **worse** households.
- A chooses **fewer**, and the twin's broad offering buys the multi-year retention the split found. §12f's split
  put £1.041 of £0.996 on retention beyond one term, and the value test prices one term.

Only an equal-volume run separates the two.
1. **First:** the same rank-at-q run STRADDLE names, with the same q rule and the same measure-first threshold.
   - If rank-at-q minus twin is not below zero, the loss was volume. Go to step 2.
   - If it is below zero, A ranks worse where money is made. The lever is the belief, not the gate. The next item
     is a finding against the corrected belief's money grade, and no retention lever is run.
2. **Second, only on "volume":** value a kept household at its expected tenure, not at one term. The value test's
   `expected_margin` would become term margin times the desk's own expected terms remaining, learned from its
   closed renewals. That is a new default-off switch, and its knowledge page comes first.
   - **Run:** A plus that switch against A, on 61118 at 13131/14141. One configuration, about 11.5 h, with A's
     files on disk.
   - **Measure first:** count the value-arm renewals in A's 61118 sidecar that reached the value test and were
     refused on value. If fewer than 10, the switch cannot act on this book and is not run. That is
     `C3`'s rule from §12e, applied again.

## What the reader does, in order

1. Re-check the pin hash, as the continuation already says.
2. Publish P1 to P4 and the founder/win split in §12g, unrevised, quoting `grade_new_book.out`.
3. State the outcome by the interval, and P1's verdict by its own rule, side by side.
4. Quote this record's branch for that outcome verbatim, by section heading, and name the run.
5. Do the branch's "measured first" step where it has one. Then either arm the run through `launch_long_job` (a
   watcher, behind the box), or record why it is not launched.
6. Grade this record: one line for the branch taken, `held` if the step-5 reading allowed the named run and
   `missed` if the measure-first rule stopped it.

**What would show this record was wrong to write this way.** Suppose the reader finds the outcome cannot be
mapped: the grader exits non-zero, or prints no interval. Then no branch is taken, the grader is fixed and re-run
on the same files, and nothing here is revised.

**Reverse:** nothing to reverse. This is a record, and it launches nothing.

## Graded (24 Nov 2026, read at 05:47Z)

- **Outcome: STRADDLE.** P1 = −£0.140 (−£1.389 to +£1.025). P1's own verdict is REFUTED, because the point is
  below zero. The full publication is in §12g, under "s.12g graded".
- **Decomposition:** (cut − A) +£0.721 = P3 +£0.916 − P3b +£0.195, plus (A − twin) −£0.861.
- **Measured-first:** q = 0.7563 (211 of 279 twin value-arm renewals offered). 0.12 sits at the 16.2nd
  percentile of the cut run's value-arm renewal beliefs, against the rank-at-q threshold at the 24.4th: a gap
  of 8.2 points, beyond ±5. The other readings of the rule's wording also pass.
- **Branch taken: STRADDLE. Grade: held.** The step-5 reading allows the named run: rank-at-q on the pinned
  tree, book 61118, 13131/14141, A's belief on, graded against the twin and cut files on disk. Its build and
  launch are recorded in §12g.
