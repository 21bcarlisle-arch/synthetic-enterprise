# The renewal belief does not order who leaves, and the grade was already on disk

**2026-09-22 · delivery seat · landed on the arms page (`/capabilities/`)**

## What this is

The thesis has one direct test. *"It beats average precisely to the degree it understands and
predicts the truth behind the SIM better than average"* resolves, on the route where the priced
per-customer decisions are actually made, to a single question: does
`company.crm.churn_model.estimate_churn_probability` put the accounts that **left** above the
accounts that **stayed**?

It was measured on 2026-09-22 — 2,000-permutation null, an oracle ceiling on the identical rows,
a per-factor decomposition — and it **reached no reader**, because the artefact holding it is
`docs/observability/svt_drift_belief_grade.json` and the filename names the *other* route. The
renewal block sat under `per_route.renewal`, unread, on the one claim this company exists to test.
This is the publishing job. No measurement was commissioned.

## The reading, as published

| | Orders who left | A signal with no information reaches | Verdict |
|---|---|---|---|
| **The company's belief** (`company_churn_estimate`) | 0.4988 | 0.3829–0.6241 | we cannot tell |
| The world's own hazard (the ceiling), same rows | 0.7400 | 0.3794–0.6206 | orders who leaves |

144 renewal decisions, 32 departures, 427 comparable pairs. One capture, one population.

The belief reads **the null's own median**. Not "weak" — indistinguishable from a signal carrying
no information at all, on the route where the choosing happens.

## The four things the direction asked for

**(1) The exposure offset does not apply here, and that is established rather than assumed.**
The grader keys the correction to the PROPERTY and never to the route name —
`measure_churn_heterogeneity.route_carries_exposure` requires every row to carry a positive
`sim_segment_days` — and the renewal capture carries that field on **0 of its 144 rows**. So
`belief_exposure_offset` returned `None`, the arm carries no `exposure_offset` block and no
`belief_auc_superseded_by` pointer, and the bare `belief_auc` is this route's *only* reading rather
than its flattering one. The domain reason is the same fact from the other side: a renewal is one
decision at a fixed contract anniversary, not a window of variable length, so there is no duration
for a belief to be accidentally ordered by.

**The refusal is still armed, which is the part that matters.** If the capture ever gains
`sim_segment_days` the grader stamps a superseding pointer without anyone editing the generator,
and this surface would publish a withdrawn number under a `clears_the_null` flag — the defect
`delivery.json.what_it_got_wrong` already records this project publishing once. Any pointer at
all, or any `exposure_offset` block, is refused outright. `_svt_drift_belief` refuses a pointer
naming the *wrong* key; this refuses a pointer naming *any* key, because on this route the correct
number of superseding pointers is zero. Both shapes are swept in
`tests/tools/test_generate_value_arms_data.py`.

**(2) The different-world caveat reaches one of the two claims and not the other.** It is neither
inherited wholesale nor dropped. `world_identity.digest` is null and the capture's own per-year
departure-level anchors disagree with the live world on 10 of 10 years, by up to +3.41 against a
captured 3.23.

* **Within the capture, and it survives.** Belief and ceiling are graded on the *same* 144
  decisions, the *same* 32 departures and the *same* 427 pairs, each against a permutation null
  drawn from those same rows. "The belief did not order these departures while the world's own
  hazard did" is a comparison of two orderings of one list. It does not become truer or falser if
  the world has moved, because it is not about the world. **Published, as a resolved direction.**
* **About the live world, and it does not survive.** How much orderable signal today's renewal book
  holds is exactly what the departure level decides, and the departure level is what disagrees on
  all ten years. `ceiling_is_the_live_worlds_signal` is `None` — never `False`, never omitted —
  with the capture's own measured reason rendered beneath the table.

This is **not** a relaxation of `_svt_drift_belief`'s rule. That block publishes its ceiling as
"there is this much signal there to find", which is a statement about a world, and withholds it
correctly. This is a narrower claim carrying its own name, so a reader can see which of the two
they were given.

**(3) The chain, stated rather than left to adjacency.** Of the four world factors the ceiling
decomposes into, `sim_bill_shock_base` is the **only one that clears its own null alone** (0.7014,
contribution 0.1335); the other three are inside their nulls alone. So the orderable signal in this
world's renewal departures is concentrated in **bill shock** — and the `churn_belief_size` panel
directly above establishes that the company's belief reaches a household's bill through a single
term identically zero for **217 of 226** supply legs of this page's own book. *The belief is flat
in the one dimension the world orders departures by.* That is why the choosing has nothing to
choose with, and it is the account the negative selection leg has been missing.

The joining sentence is built from the size block's **own counts**, passed into the reader rather
than re-read, so the two panels cannot come to state different numbers for one population.

**(4) The second grade is recorded, not merged, and never averaged.**
`docs/observability/renewal_churn_belief_grade.json` (2026-08-30) grades the same question on a
larger, different book. It carries **no permutation null** and **no world identity**. A rank
statistic with no null is not a reading, so **nothing is quoted from it** — not its AUC, not its
oracle, not a difference against either. What is published is that it exists, what book it is over
(708 renewals, 40 departures), and the named reason it is not quotable: a second measurement a
reader could find and this page did not mention is how a surface loses the right to be believed.

The reason for declining it is itself measured. "It carries no null" is scanned **recursively**;
a top-level scan would publish that reason as true while a null sat one key deeper — fail-open, in
the flattering direction, on the sentence doing the refusing.

## What this does not say

It does not price the gap. It is not an instruction to make the belief discriminate. **R12 stands
and no figure here is a target.** A belief that cannot order its departures is a complete answer.
The epistemic wall is untouched either way: the ceiling is the *world's* hazard and never reaches
`company/`; it is read from a capture on a published surface.

## The controls

* `site/test_the_renewal_belief_reaches_the_reader.py` — 13 legs, driving the **real door** through
  its own boot path against the **published (index)** bytes. Every leg mutates the feed and asserts
  the render follows, so a literal reds on the mutation and passes on the live feed. The null rung
  is `test_a_belief_that_CLEARS_its_null_renders_the_other_words`: the page must stop saying "we
  cannot tell" when the numbers stop saying it. The load-bearing leg is
  `test_the_live_world_claim_is_WITHHELD_with_its_reason` — a page that renders the live-world
  claim because it may render the within-capture one has published the flattering half of a split
  caveat.
* `tests/tools/test_generate_value_arms_data.py` — 12 producer legs: both superseding-pointer
  shapes, the tautology guard, the whole four-state partition asserted in one control rather than
  a leg per branch, every refusal naming a distinct reason with a live-artefact control proving the
  guard is not refusing everything, and the recursive null scan.

**One control's own bug was caught and is recorded rather than quietly fixed.** The first draft of
`_renewal_grade_with` re-read `gva.SVT_BELIEF_GRADE` *after* monkeypatching it, so successive
mutations in one test compounded: the partition leg silently measured three of its four states and
reported the subject as unreachable. The bug was in the control. The helper now reads the pristine
path, held apart from the constant it patches.

## Why a second reader rather than a widened one

`_svt_drift_belief()` is one `.get("svt_segment")` from this block and widening it was the cheaper
move. It would have been wrong: that function's one non-negotiable line is that the uncorrected
`belief_auc` key is REFUSED and only the per-exposure-day reading is quotable, a discipline that
exists because SVT cap segments run 1–92 days. The renewal route has no such key. A single function
would need a branch on route at exactly the point where its one load-bearing rule lives. The
refusal is the same *shape* and is re-armed here against this route's own pointer; what is not
shared is the key it reads.

## Incidentally repaired

`sources` on the arms feed states its own rule — it names what `generate` **opens** — and it had
gone stale inside itself: `svt_drift_belief_grade.json` has been opened by `_svt_drift_belief`
since that block landed and never appeared in the citation list. Both grades are now named.

## What is still open

* The capture is in a different world from the live one, and the only remedy is a fresh capture:
  `python3 -m tools.capture_departure_factors`. Re-running the grader cannot move it — it reads a
  capture, and the capture is where the world is. Until then the ceiling's **level** is a
  measurement on this capture and is not transported.
* `docs/observability/svt_drift_belief_grade.json` carries an uncommitted `world_identity` block in
  the shared tree (another lane's live work). This landing reads the **committed** artefact and its
  reader handles both states: with the block, the withheld reason is the capture's own measured
  one; without it, the fallback names the same remedy. Nothing here blocks that lane landing.
