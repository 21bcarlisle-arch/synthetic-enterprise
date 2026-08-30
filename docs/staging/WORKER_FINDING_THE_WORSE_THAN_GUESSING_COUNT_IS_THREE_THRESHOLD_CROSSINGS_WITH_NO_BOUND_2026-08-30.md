**Severity:** LATENT · **Lane:** G_data_learning · **Epoch:** 3 · **Atom:** `A45_the_canon_is_a_standing_subject`

# "Where the company does worse than guessing" is a count of threshold crossings, two of which are inside the noise

**Found:** 2026-08-30, sweeping for other instances of the standing rule
(`docs/design/INDEPENDENCE_IS_NOT_INFERENCE_2026-08-30.md`) rather than waiting to be shown the
next one. The director's instruction was *"Apply it yourself from here; don't bring me the next
instance"* — this one is brought because it is a **different figure on a different page** and the
judgement about severity is worth recording, not because a decision is wanted.

## What is published

`site/harness/index.html` renders four counts under *"Where belief and truth diverge"*, and says of
the last one:

> "The last figure is the one that matters most: a company doing *worse than guessing* has a model
> that is actively misleading it, which is more dangerous than having no model. **Those are the ones
> the build queue is ordered by.**"

So it is not only published — it **orders work**.

## The count is 3, and here is what the 3 are

`background.gap_metric._normalise` computes `gap = raw_gap / g0` and returns it. A gap above 1.0
means worse than the no-skill baseline. The comparison is a bare point estimate against **exactly
1.0**, with no interval and, for most rows, no sample size anywhere in the record.

Live ledger, 16 rows:

| metric | gap | what bounds it | distance from the line |
|---|---|---|---|
| belief | **1.034** | `n_cells_eligible = 20` | **+3.4%** |
| prediction | **1.039** | no sample size in components | **+3.9%** |
| belief | 2.529 | `available_accounts = 263` | +153% |
| belief | 0.830 | no sample size in components | −17% |

**One of the three is unambiguous. Two are decided 3-4% the wrong side of a line, one of them on
twenty cells.** A twenty-cell verdict that lands 3.4% past its threshold is a coin flip wearing a
finding's clothes, and it is currently one third of a headline figure that orders the build queue.

And the row at 0.830 is the same problem with the sign reversed: 17% the *right* side of the line
with nothing bounding it, counted as fine.

**Only 4 of 16 rows expose a sample size at all**, so for the other 12 the bound cannot be computed
from the ledger even in principle.

## Why this is the same class the standing rule names

The rule says a reading that sits inside the interval a random signal produces must be reported as
*we cannot tell*, in those words. A gap of 1.034 on twenty cells is that reading: the threshold is
1.0, the sampling spread of a ratio of mean absolute errors on n=20 is comfortably wider than 3.4%,
and nothing on the page or in the ledger says so. The concordance on the capabilities page was
repaired this evening for precisely this shape. This is the same defect on a different figure.

## Why the repair is NOT a presentation fix, which is why it is not done here

The bound cannot be added at the ledger or the page, because the ledger stores **summary
components** and not the per-case errors. A ratio of mean absolute errors needs its sampling
distribution bootstrapped over the underlying cases, and those cases exist only inside each metric
at production time. So the honest repair is **per-metric**, in `background/gap_metric.py`'s
producers: each carries its own n and its own bootstrap interval, and `_normalise` grows a verdict
that can say *too close to the line to call*.

Two things were considered and rejected:

* **An arbitrary "within X% counts as too close" threshold.** That is exactly the invented constant
  this project's own rules forbid — it would be load-bearing within a week and unattributable within
  a month.
* **Withholding the count until every metric carries a bound.** The count is *self-critical*: it is
  a statement that our own models are bad. Suppressing it would remove an unflattering number and
  publish a friendlier page, which is the wrong direction to move in while waiting for a bound.

**The minimum honest interim, and it is what should ship first:** keep the count and state beside it
how many of its members sit within a few percent of the line and on what sample. Strictly more
information, and it flatters nobody.

## The severity judgement, recorded so it can be overturned

This meets the **letter of BLOCKING** — *"a control or instrument in this area is untrustworthy"* is
true, and the instrument orders the build queue. It is filed **LATENT** on three grounds, and the
call is the delivery seat's:

1. The exposure is a count that is **self-critical rather than self-serving**. A reader misled by it
   thinks worse of this project's models than the evidence supports, not better. That is the
   direction this project errs in deliberately everywhere else.
2. The repair is **per-metric research work**, not a one-line correction, so BLOCKING would hold the
   tree closed for days rather than for the length of a fix.
3. A BLOCKING finding refuses **every commit tree-wide**, and a live lane is mid-flight on C1b
   tonight. Stopping another lane's landed work for a figure whose error direction is against us is
   not a trade I will make without being told to.

If the director reads point 1 differently — that a wrong self-criticism is as bad as a wrong boast,
because it makes the whole page's honesty performative — then this is BLOCKING and I will escalate
it on that word.

---

## INTERIM SHIPPED, same evening — the margins are now on the page

The section above called the margins "the minimum honest interim … and it is what should ship
first". It has, rather than being left in a queue:

* `tools/generate_proof_data` publishes `worse_than_blind_margins` — for each crossing, its value,
  how far past 1.0 it is, and the sample size **or `None`**.
* `site/harness/index.html` renders them beneath the count, naming each atom, its margin, and
  either its case count or the words *"nothing in the record says how many cases it rests on"*.

What a reader now meets, live:

| atom | value | past the line | cases |
|---|---|---|---|
| `W2_2_population_draw` | 1.034 | **+3.4%** | **20** |
| `W1_5_premise_demand_shape` | 1.039 | **+3.9%** | **unknown** |
| `EP1_clv_three_horizon` | 2.529 | +152.9% | 263 |

**No "too close to call" classifier was added**, deliberately — choosing the percentage at which a
crossing stops counting would be the invented constant this project's own rules forbid. The margins
are published and the reader weighs them.

`_sample_size` fails to `None` and never to `0`: *"we do not know how many cases this rests on"* and
*"it rests on no cases"* are different sentences, and the second would tell a reader the crossing is
meaningless rather than unbounded.

**Four mutations, all firing after one was tightened.** Dropping the render, rendering it
unconditionally, and dropping the unbounded wording each fired first time. The fourth — a producer
returning `0` for an unknown sample — **survived**, because the assertion was `str(n) in body` and
`"20"` sits inside `"152.9%"`. Re-keyed to the phrase `on {n} cases` plus a direct check that a
sample size is `None` or positive; it now fires. Recorded because a mutation that survives a loose
assertion is the same defect this finding is about, one level up.

**The finding stays open at LATENT.** The margins let a reader weigh the count; they are not the
bound. The real repair is still per-metric bootstrapping inside `background/gap_metric.py`, and
until it lands this page shows distances from a line rather than a probability of being the wrong
side of it.
