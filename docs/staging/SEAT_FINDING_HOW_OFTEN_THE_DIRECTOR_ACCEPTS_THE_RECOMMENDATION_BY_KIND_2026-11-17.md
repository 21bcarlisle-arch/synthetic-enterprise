**Severity:** LATENT · **Lane:** A_strategy_governance · **Epoch:** unassigned · **Atom:** `unminted`

# How often the director accepts the recommendation, by kind of decision (2026-11-17)

*From the director's steer of 17 Nov 07:35 ("Do it"):
`docs/staging/advisor/done/DIRECTOR_STEER_MEASURE_HOW_OFTEN_THE_DIRECTOR_ACCEPTS_THE_RECOMMENDATION_AND_LET_THE_SURE_KINDS_BE_DECIDED_2026-11-17.md`.
Claes's stage 2 to stage 3: compare what was suggested with what was picked, then let the machine decide
where the picks almost always match.*

## Pre-registration (written before any count; the results section is below it and was written after)

**What was seen before writing this.** The resolutions of 3 of the 45 closed `for_the_director` rows,
which were printed while I checked the store's format: all three approved, two of them with amendments. Also
one fact about silence, found while looking for sources: one resolution among the 45 mentions it, and no
structured field records silence anywhere. Nothing else had been read.

**The unit.** One recommendation put to the director and one answer from him.

**Sources.**
- (A) Every closed `for_the_director` row: `background.director_concerns.closes_on_record()`, which merges
  `decisions.jsonl`, the committed revisions of `DIRECTION.yaml` and both live copies. Each row holds the
  machine's `proposal` and his `resolution`.
- (B) `docs/staging/advisor/done/DIRECTOR_RULING_*`: his answer to a recommendation, quoted.
- (C) `docs/staging/advisor/done/DIRECTOR_STEER_*`, only where the quoted words answer a recommendation the
  advisor put to him ("Do it" or "yes" on "the advisor's recommendation"). A steer that is only his own
  initiative is not a decision on a recommendation, and is excluded.
- Excluded: `DIRECTOR_READING_*` (usage readings), `DIRECTOR_EVIDENCE_*` (data he supplied), notices and
  questions. They answer no recommendation.

**Answer codes.** YES: as recommended. AMENDED: approved with a change of substance. NO: rejected, or he
chose otherwise. REDIRECT: he answered a different question or asked for more. SILENCE: taken as yes because
he did not answer. WITHDRAWN: the machine withdrew it, which is excluded from every rate.

**Kinds.** One per decision, assigned by the subject of the recommendation. Where two apply, the first in
this order wins:
1. a G5 wall;
2. strategy, vision or canon intent;
3. a curriculum or world choice (which world the company lives through);
4. a fidelity change (making the world or the supplier more like the real thing);
5. adopting or rejecting an outside source;
6. a measurement or trial;
7. a harness or efficiency change.

**Near-certain.** The Wilson 95% lower bound on explicit plain YES must be at least 0.80. AMENDED counts
against it: an amendment is a case where deciding for him would have been wrong. SILENCE never counts toward
it.

**Predictions.**
- P1. Harness/efficiency: plain YES at least 85%. It is the only kind I expect could reach near-certain, and
  I expect even it to fall short on count (n under 20).
- P2. Measurement or trial: plain YES at least 85%.
- P3. Outside source: YES plus AMENDED at least 90%, because he shares the sources he wants adopted.
- P4. Fidelity: plain YES about 70%, AMENDED about 20%.
- P5. Strategy, vision or canon: plain YES at most 60%, AMENDED at least 30%.
- P6. Curriculum and G5: fewer than 5 each, too few to rate.
- P7. NO is under 10% overall.
- P8. Sources (B) and (C) over-represent YES. A file is written once he engages, and a recommendation he
  turned down in chat may never be filed.
- P9. SILENCE cannot be measured from the record (observed, not predicted; see above).
