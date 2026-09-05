**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0 delivery
· **Class:** publish_gate_and_wedge

# PRE-REGISTRATION: what does an EPISODE of commit refusal cost, and is the 48% governance-gate share a problem or the gates working correctly?

**Filed:** 2026-09-05, delivery seat, continuing the Lane 0 direction *"measure and attribute
commit_refused"*. **Written before any duration was computed.** The predecessor finding
(`SEAT_FINDING_THE_272_COMMIT_REFUSALS_ARE_175_CYCLES_AND_THE_RATE_IS_FOUR_TIMES_WHAT_THE_LIFETIME_COUNT_IMPLIES_2026-09-05.md`)
closed with the next question named and deliberately unanswered:

> *"The next question is **episode duration by cause**, which converts this share into a cost and
> decides whether the 48% governance-gate share is a problem or the gates working correctly."*

That is what this measures. What is already established and is NOT re-litigated here: 175 refused
cycles of 442 in the observable window (39.6%); named red 40%, non-test governance gates 48%,
unattributable 12%; 46 contiguous runs, longest 41, runs of ≥5 holding 61%.

---

## The definitional work, done BEFORE the count, because the last three defects in this direction were all definitional

**An episode's length in CYCLES is not its cost.** The publisher runs roughly every 36 minutes
(median gap between cycle starts 2160s, established 2026-09-04). A cost is wall clock, and the
conversion is not a constant — the gap has p90 5534s and max 19454s, so 5 cycles can be 3 hours or
27. Cycles must be converted, not multiplied.

**Three quantities that are not the same, named now so they cannot be silently substituted:**

* **span** — last refused attempt minus first refused attempt inside one run. A 1-cycle episode has
  span 0. Honest, and it systematically understates: it excludes the recovery.
* **outage** — first refused attempt until the start of the next attempt that LANDED. This is the
  quantity that answers "how long could the publisher not publish", and it is the one I will treat
  as the cost. A 1-cycle episode has a real, non-zero outage.
* **inter-attempt gap** — how often the publisher tries. Not a cost; it is the conversion factor,
  and it belongs in the record because outage is bounded below by it.

**A run-breaker must be a LANDING, not "a cycle that was not refused for this reason."** The
predecessor's run computation marks a cycle refused only on `commit_refused`, so a `behind_origin`
or `commit_timeout` cycle in the middle of a wedge reads as a *recovery* and ends the run. For a
CYCLE-share question that is defensible. For a COST question it is wrong: the publisher did not
land, and calling that the end of an outage understates the outage. I will compute both and report
which is which rather than replacing one with the other.

**Right-censoring is reported, never averaged in.** If the log ends inside an open run there is no
terminating landing, so that episode's outage is a lower bound. It is the episode most likely to be
the longest — an ongoing wedge is exactly the one nobody has cleared — so folding a censored lower
bound into a median or a max would bias the headline toward comfort. It gets its own line.

**An episode with more than one cause is not attributed to one.** Same discipline as the
unattributable bucket in the predecessor: a MIXED episode is its own category and is never assigned
to the side that makes the split cleaner.

---

## Predictions, and what would refute each

**P1 — the cost distribution is heavy-tailed: the single longest outage holds ≥20% of all outage
wall-clock in the window.** *Reasoning:* the cycle-share version of this held at 23.4%, and wall
clock should concentrate at least as hard because a long wedge also spans the overnight period when
gaps are longest. **REFUTED IF** <20%.

**P2 — red-test episodes are the expensive ones: their median outage is ≥2× the median outage of
governance-gate episodes.** *Reasoning:* a governance gate names a specific artefact (an
unclassified finding, an unwired module) and the owning lane clears it in its next turn; a red test
needs a diagnosis. **REFUTED IF** the ratio is <2×, and **REVERSED** if governance-gate episodes are
the longer ones — which would be the strong form of "the publisher is held hostage by whole-tree
state it cannot fix". *Caution recorded in advance:* the predecessor already found a 26-long
red-test streak, so I hold this weakly; it is the direction of the effect I am predicting, not its
existence.

**P3 — the run-breaker defect is material: defining the breaker as a LANDING rather than as
"not commit_refused" merges episodes and reduces the episode count by ≥10%.** *Reasoning:* 17
`behind_origin` and 14 `commit_timeout` cycles exist and there is no reason they avoid wedges;
they should fall inside them at least as often as chance. **REFUTED IF** the reduction is <10%.

**P4 — mixed causes are common: ≥25% of multi-cycle episodes carry more than one cause.**
*Reasoning:* a wedge is whole-tree state, and while it stands, an unrelated red can arrive and
depart. **REFUTED IF** <25%.

---

## The decision rule, declared before the numbers

This is the point of the exercise, and it is written now so it cannot be fitted afterwards.

* **If governance-gate episodes are SHORT** — median outage inside one publish gap, i.e. the gate
  refuses and the next cycle lands — **the gates are working correctly.** A refusal that costs one
  delayed cycle is 0.9% of one declared 7-day cadence, and the correct action is to change NOTHING
  and record why. The 48% share would then be a share of a cheap event, and mistaking it for a
  problem is the same error as mistaking 9.2% for a rate.
* **If governance-gate episodes are LONG** — median outage spanning several gaps — **the publisher
  is being held hostage by whole-tree state it did not create and cannot fix**, and that is
  structural: the daemon commits regenerated site data and is refused because another lane left a
  finding unclassified. The action then follows from WHICH gate, which is why the by-gate
  breakdown is carried through to duration rather than stopping at the count.
* **If the two are indistinguishable**, the cause split does not predict cost, and the episode —
  not the cause — is the unit worth acting on. Say so and stop, rather than reaching for the
  cause-shaped answer because the cause is what was already measured.

**No mechanism will be built in the same turn as this measurement**, for the reason the predecessor
gave: a control written before the distribution is known is keyed to today's answer. If the numbers
warrant one, it is the next turn's work and it will be keyed to the property, not the figure.
