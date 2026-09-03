**Severity:** LATENT · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** `A46_the_priced_menu`

# A published capture was produced by code that was never committed — and a careless `git checkout` proved it

**Filed 2026-08-31 by the delivery seat, against itself.**

## What happened

Working the Lane 0 item *put-the-company-beside-the-ceiling-on-the-route-its-own-belief-did-not-seed*,
I ran a mutation harness over `simulation/run_phase2b.py` and restored it afterwards with:

```
git checkout simulation/run_phase2b.py
```

That path had **160 lines of uncommitted work** in it — the entire C1b standard-variable departure
route, plus the SVT segment decision log, plus the `estimate_svt_drift` wiring. `git checkout` on a
pathspec restores from the index, and none of it was staged. **It was destroyed outright.** No
reflog entry, no dangling object: git had never been given a copy.

Recovered from `stash@{0}` (2026-08-31 01:18), which held an earlier increment of the same work —
the hazard, the propensity and the departure event, but only the 50 DEPARTURES, not the 1,266
decisions, and no belief wiring. The remaining delta was reconstructed by hand and verified by
regenerating the capture and diffing it row-for-row against the committed artefact.

## The finding, which is not the mistake

**`docs/reports/ladder_churn_factors_continuous_satisfaction_svt_segment_decisions.json` is
committed, is published, is cited on the ladder page and in three findings — and the code that
produced it was not in any commit.** Six of this stretch's commits quote figures computed from it:
the SVT ceiling of 0.6721, the exposure-offset 0.6091, the "50 of 82 departures" that is the
headline of a HIGH finding.

At HEAD, before this repair, `tools/capture_departure_factors.py` would have read
`result["svt_decisions"]` from a `run_phase2b` that does not populate it, written an **empty**
companion file, and printed its own loud warning — which nobody would have seen, because nobody
re-runs a capture that already exists on disk.

**So the check that would have caught this is the one this project already believes in and did not
apply here: an artefact is only as reproducible as the commit that can regenerate it.** The publish
gate grades HEAD; it does not ask whether a committed *artefact* can be *rebuilt* from HEAD. A
capture whose producer is uncommitted is indistinguishable, to every reader and every control, from
one that can be reproduced on demand.

## Why it survived so long

Three things each hid it:

* **The artefact was in the commit and the producer was not.** Committing by pathspec — which is
  the rule here, and the right rule — makes this easy: `docs/reports/*.json` lands, `simulation/*`
  does not, and nothing compares them.
* **Every reader reads the artefact, never the producer.** `measure_churn_heterogeneity`,
  `population_anchor`, `departure_population` and the ladder page all load the JSON. A capture is
  the kind of thing you *read*, so nothing had cause to run the thing that writes it.
* **The tree was green.** The tests that mention SVT segment decisions read fixtures or the
  committed artefact, so a `run_phase2b` with no SVT route at all passes them.

## What is owed

1. **A control that a committed capture can be regenerated from HEAD.** Not a full re-run per
   commit — that is a decade run and would be slower than the tree's landing cadence, which never
   converges. The cheap one-leg version: for each committed capture, assert that the result key its
   producer reads (`svt_decisions`) is *written* somewhere in the committed source. That is a
   static check, it is fast, and it would have gone red the moment the artefact landed without its
   producer.
2. **The reconstruction is verified but not certified.** The regenerated capture matches the
   committed one row-for-row on every field the committed one carries. That proves the restored
   code reproduces the published population; it does not prove it is line-for-line what was lost.
   Anything downstream that depended on a *comment* in the destroyed version is gone and unrecorded.
3. **`git checkout <path>` on this tree is the same class as `git stash`,** which is already a
   named rule here. It silently discards uncommitted work in a tree where several lanes write. The
   rule that exists says never `git stash -u` the shared tree; it does not name `checkout`, and the
   two have identical blast radius. Same rule, one more verb.

## The mutation-harness pattern that caused it

The harness backed up the *test* file it was mutating and restored that by copy, correctly. For the
*source* file it mutated it reached for git — because the source was "already tracked", which felt
like the safer assumption and was the fatal one. **A mutation harness must restore every file it
touches by the same mechanism it saved it, and it must save before it mutates.** Backing up by copy
and restoring by git is not a round trip; it is a round trip only if the file was clean, and this
one had a lane's afternoon in it.
