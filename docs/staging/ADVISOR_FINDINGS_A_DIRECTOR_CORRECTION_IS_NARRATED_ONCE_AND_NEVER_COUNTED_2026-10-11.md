# [ADVISOR] A director correction is narrated once and never counted
**Knowledge:** none -- a director or advisor ruling, steer or record, not domain research

**Fate (2026-10-13, clear-the-decks):** ATOM -- n/a No banner. P3 -- proposes a mechanism to count/classify repeated director corrections (not just narrate them in prose); unbuilt, advisor itself says "nothing here claims priority over drawn work."

**Severity:** LATENT · **Lane:** A_strategy_governance · **Epoch:** unassigned · **Atom:** `unminted` — lane set by the scale lane: `unassigned` is not a lane and the severity gate refused every merge of origin

Date: 2026-10-11. Staged at the director's request after reading an external thought piece with him
(see "Where this came from"). One problem with evidence, offered for the seat to weigh, scope and
sequence. Whether there is a build at all is the seat's call. Nothing here claims priority over
drawn work.

Measured against origin at `98279d52` (2026-10-11 06:54Z).

## The problem

When the director corrects the machine, the correction changes behaviour once and then survives only
as prose about itself. Nothing counts corrections, classifies them, or notices when the same one
arrives twice.

Evidence, all from this week:

- `docs/status/SEAT_STRETCH_LOG.md`, today's entry, records a correction in narrative: the reactive
  save went live as a supplier capability before its knowledge said whether matching the best deal
  had any published basis; the director caught it; it is recorded as a design choice; and
  knowledge-before-build became his standing rule. That sentence is the whole record. It is written
  by the seat about the seat, in prose, in a file that is read by humans and by nothing else.
- `docs/direction/decisions.jsonl` holds 335 orientation records. One item for the director
  (`the-end-to-end-review-of-claude`) has been carried **65 times**, every orientation from
  2026-10-04 to 2026-10-11, with `status: open` and an empty `resolution`. The structure tracks
  whether a thing is answered. It does not carry what the answer changed.
- A search of the tree for anything holding director corrections as data found only domain
  correction registers (`company/market/mpas_standing_data_correction_register.py` and similar).
  Those are corrections to meter data, not to the machine's own judgement.

So three states are invisible:

- **the repeat** — the same correction arriving a second and third time, which is the signal that a
  rule is missing rather than that an instance was wrong;
- **the delta** — the difference between what the machine proposed and what the director approved,
  which is the only direct evidence of his curation standard;
- **the rate** — how often corrections land at all, and whether it is falling.

## Why it matters here specifically

The 2026-10-10 staging recorded three ideas held back from the same reading. One was a fuse that
steps automation back after two reversals by a human in one week. **That cannot be built**: there is
no reversal count to fire it. This problem is upstream of that one.

It is also the mirror of the sourced-fact problem already staged on 2026-10-10. That finding says a
knowledge entry has no identity, so nothing can point at it. This says a correction has no identity
either, so nothing can count it. Whether the two share one answer is the seat's judgement, not a
claim made here.

## What the seat may want to consider (problems, not remedies)

- What counts as a correction. A struck proposal, a reworded ruling and a plain factual fix are not
  the same act, and a scheme that cannot tell them apart will count noise.
- Where it would already be cheapest to capture. Corrections pass through the console and the
  orientation record, and the stretch log is written as part of finishing work rather than as a
  separate step — so a capture that is a by-product of an existing write is likelier to survive than
  a new duty.
- Whether anything should read it. A count nobody reads is a register, and CLAUDE.md warns that a
  file made of rules breeds rules. The smallest useful consumer may be a single line on an existing
  surface, not a new one.
- How a repeat should read. Twice is a coincidence and a rule is a strong response to it; the honest
  threshold is the seat's to argue from what the count turns out to be.

**Measure before arguing:** over the stretch log as it stands, how many entries contain a director
correction, and how many of those are the same correction in different words? That count says
whether this is worth a mechanism or worth nothing.

## Where this came from

The director shared an external brief on agentic corporate memory. Most of its target architecture
describes what this project already runs: staged proposals with human approval, a sandbox with
enforced ground truth, findings promoted upward. Three of its recommendations were rejected on
evidence already in this repository — a resident local model (reversed in August, finished unwinding
2026-09-27), an approval dashboard (the console and the staging channel already carry this), and the
claim that shared memory drives coordination cost to zero (refuted by the £55 acquisition cost that
sat cited and unused for seven weeks inside the shared store).

Its one idea not already present here is the subject above: that the difference between a draft and
the human's edit of it is itself information, and discarding it throws away the cheapest signal the
organisation produces. Recorded alongside it, for whoever reads this later: the brief has no concept
of when a fact was true or knowable, which is the gap the 2026-10-10 staging identified as the more
valuable one. On that axis this project is already ahead of the source.

---

## Risk

- **Touches:** this file only. No executable path, gate, published figure, simulation output or
  canon document.
- **Blast radius:** seat attention, and — if taken badly — a new register plus a new duty at the end
  of every stretch. That is the likely failure, and it is the failure CLAUDE.md names.
- **Mitigation, inline:** the problem is stated as a problem; the remedy, its size, and whether it
  is worth building at all are the seat's. The measurement above is cheap and comes first, so a
  mechanism is only argued for once the count justifies it. Preference stated for a by-product of an
  existing write over a new step.
- **Consume path:** the seat orients roughly three-hourly and last oriented at 05:20Z today; it read
  the 2026-10-10 advisor staging within hours. No known blockage.
- **Proportionality:** reversible / narrow.
