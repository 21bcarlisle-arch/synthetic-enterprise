**Severity:** LATENT · **Lane:** A_strategy_governance · **Epoch:** unassigned · **Atom:** `unminted`

# [DIRECTOR-STEER] Show everything we have learned, mined from the record rather than from memory (2026-10-23)

**Type:** STEER, through the advisor channel. It follows this morning's three control-stack steers (`DIRECTOR_STEER_SHOW_THE_HARNESS_AS_A_LIVE_CONTROL_STACK_2026-10-23.md` and its two additions) and closes that series. The director's words, from chat on Fri 23 Oct:

- 09:27 BST: "What else? It feels we've learned and done more than all of this along the way"

## Why this is a different kind of ask

He is right, and the advisor's three additions show why. Each one came from what an advisor chat happened to discuss. That covers a fraction of the record. The record itself, measured from origin this morning, holds:
- about 13,900 commits since 7 June;
- about 4,400 staged items actioned and filed to done;
- 19 retrospectives;
- 17 numbered harness rules;
- 168 numbered principles in the canon across 14 areas: mission, phases, the wall, building the world, knowledge, priority, the customer and the money, fairness and protection, carbon, governance, the director and the reader, harness, running the simulation, and other.

Most of that has no public face. Fairness and protection, carbon as a diagnostic that is never a target, the validation ladder, "the world must be able to defeat the company", how a trial is run, and "nothing structural happens at night" are a few examples. Another round of the advisor naming themes from chat would only reproduce the same bias. The machine holds the record, so the machine should mine it.

## The outcome wanted

A reader can see **the whole body of what this project has learned**, organised so it can be taken in, and each lesson traceable to where it came from and what now holds it in place.

The distinctive shape, which is the advisor's suggestion and yours to improve: each lesson is shown as a chain.
1. what happened: the incident, finding or ruling;
2. the principle it produced, in plain words;
3. the mechanism that now enforces it, or plainly "prose only";
4. live evidence that the mechanism fires.

Most rulebooks state rules. Very few can show, rule by rule, the cause behind it and the check holding it. The share of principles that reach step 3 is itself the most honest headline. Show it whichever way it reads. `tools/canon_drift_check.py` and `docs/design/canon_claims.yaml` cover part of that today.

Mine it from the canon, the retrospectives, the class documents, the R-rules and the done queue. Do not mine it from the advisor's lists. Where the canon and the code disagree, that is a finding, as usual.

## Where and when

- **Do not let this delay Monday's publish.** The control stack and the page rework come first. This can follow in the next stretch.
- It probably belongs on How it's built, beside the control stack, or as a second section under it. Where it lives and how it is grouped is yours. Avoid a page that only the machine would navigate. Group by what a reader cares about, not by canon letter.
- Pick a handful of the best chains as lesson cards near the top, for example the VAT rule, the 20 August phantom outage, and the dial that did not choose. Keep the full set browsable below.

## Requirements

- Generated from the record at publish, never hand-curated into a static list that goes stale.
- Plain words. Canon letters and rule numbers can appear as a quiet reference, never as the headline.
- Nothing internal or private leaks. Director-only material stays off the page, the same as the main steer.
- "Not yet enforced" is stated plainly, beside the lesson, not hidden.

## Risk

Touches: How it's built and a generator that reads canon, retrospectives and staging records.
Blast radius: one public page, which is reversible.
Probable failure mode: a mechanical extraction that publishes internal jargon or half-parsed canon text. Run the same cold energy and tech readers on it before it ships.
Proportionality: reversible and narrow — just do it.

— Director steer, 23 Oct 2026, his words above; the counts and drafting are the advisor's.

## Remaining (24 Oct, seat executor)

Drawn together with the 24 Oct "nothing stale" steer, which is now in `done/`. Landed from this one: the corrections list generated from the record, newest first; the rules in the canon's current words; the class register backfilled with three classes. NOT done: the lessons as cause, principle, mechanism and evidence chains mined from canon, retrospectives, class documents and the done queue. The page still carries three hand-written lesson cards (Aug-Sep). Next piece: generate the chains at publish from `docs/retrospectives/` and the class documents, newest first.

## Remaining (24 Oct, afternoon, worker tick)

Landed from this one: every canon principle on How it's built, in the canon's own current words, read at publish (`tools/canon_lessons.py`), grouped by the canon's fourteen areas, each with the code that holds it where that is known (`docs/design/canon_mechanisms.yaml`) and whether a test has been seen to fail on that code. The headline, as it reads: 19 of 168 principles name the code that holds them, 18 of those with a test seen to fail. The other 149 are shown as "no mechanism named yet", not as prose only, because no join can be read from the record: the canon names its own code for 3 principles, and a bare-id search of the code reads 134 "held", nearly all of it collisions with other id families (R7, C1, D48). NOT done: (a) binding the 149, which is judgement row by row; (b) step 1 from incidents, the retrospective or finding that produced each principle, beyond the ruling date shown now; (c) the lesson cards near the top generated from the chains; the three Aug-Sep cards are still hand-written; (d) the cold energy and tech readers on the new block.

## Done

**Moved, not shipped (seat executor, 24 Oct).** The advisor channel refuses this file as unsigned because two machine commits (833ef83e8, cfe4d94be) edited it in place. The director's words are the signed bytes at 946d21916; read those, not this copy (`git show 946d21916:docs/staging/advisor/DIRECTOR_STEER_SHOW_EVERYTHING_WE_HAVE_LEARNED_FROM_THE_RECORD_NOT_FROM_MEMORY_2026-10-23.md`). The ask is part shipped: How it's built now draws corrections and rules from the record at publish (05831e868, 833ef83e8, cfe4d94be). The rest, the lessons as cause-principle-mechanism-evidence chains and the cold read, is carried by the continuations `how-its-built-steer-rest` and `lessons-as-cause-principle-mechanism-evidence-chains`. It stays an open row on the director-asks ledger until those land.

**Shipped (seat executor, 24 Oct, later).** The lessons are generated at publish as chains (`tools/canon_lessons.chains`). Each chain gives what happened, the principle, what holds it or "Not yet enforced", and whether a test has been seen to fail on that code's defect. 26 chains, newest first, are drawn from the canon's 17 permanent rules and the 9 registered classes. The headline reads 11 of 26 held by code, 9 of those proven. A cold read was taken. Not mined yet: the retrospectives and the done queue, so the 20 Aug outage, the VAT rule and the dial that did not choose have no chain of their own. The stretch-log entry of 24 Oct says so.
