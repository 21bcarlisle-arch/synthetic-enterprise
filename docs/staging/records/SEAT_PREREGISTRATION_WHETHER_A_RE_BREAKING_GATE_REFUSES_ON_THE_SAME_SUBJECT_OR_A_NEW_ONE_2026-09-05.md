**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0 delivery
· **Class:** publish_gate_and_wedge

# PRE-REGISTRATION: when a gate re-breaks, does it refuse on the SAME subject or a new one?

**Filed:** 2026-09-05, delivery seat, fourth turn on the Lane 0 direction *"measure and attribute
commit_refused"*. **Written before any subject was extracted or any pair classified.**

The predecessor finding
(`SEAT_FINDING_THE_FIRING_ORDER_CONCEALS_RE_ARRIVALS_RATHER_THAN_FAKING_THEM_AND_82_PERCENT_OF_THE_COST_IS_A_GATE_THAT_RE_BROKE_2026-09-05.md`)
closed by naming this and refusing to answer it:

> *"What re-breaks them is NOT established and is not guessed at here; the log records which gate
> refused and never what changed between attempts, so the next question needs the tree state between
> consecutive refused cycles."*

## The predecessor's proposed instrument is the wrong one, and I say so before using another

It named **tree state between consecutive refused cycles** as the route. I am not taking it, and the
reason is a base rate I checked before designing anything else:

```
git log --all --since=2026-08-13 --pretty=%cI | cut -c1-10 | sort | uniq -c
   60 2026-08-13 …  102 2026-08-20 …  161 2026-09-03  191 2026-09-04
```

**60–191 commits a day, against a median 3300s gap between publish attempts.** A commit lands in
essentially every inter-attempt window. "Did the tree move between two refusals?" therefore answers
YES for re-breaks and YES for non-re-breaks alike, and a difference-in-rates against that ceiling is
not a quantity this log can resolve. Dividing "windows with a landing" by "re-break windows" would
be two correct numbers whose ratio is not a quantity — the shape CLAUDE.md names.

## The instrument I am using instead, and why it is better

**The predecessor's premise is false: the log DOES record what changed.** Not the tree state — the
*subject the gate objected to*, in the gate's own words, inside the retained hook block:

| gate | subject line it prints | subject identity |
|---|---|---|
| finding-class consolidation | `- STALE SEVERITY <F>.md: …` / `- UNCONSOLIDATED <F>.md: …` | the `.md` filenames |
| level-promotion gate | `§0: level_current 2->3 on <ATOM> declares a level for source…` | the atom names |
| orphan-ratchet | indented module lines under `THIS COMMIT ADDS WORK THAT NOTHING RUNS.` | the module paths |
| site-lane gate / RED TEST | pytest's own `FAILED <nodeid>` short summary | the node IDs |

So the question the predecessor could not reach is answerable **from the log alone**, with no
base-rate confound at all.

## The definitional work, done BEFORE the classification

CLAUDE.md: *before measuring a thing, say what it is.* "Re-break" is one word covering two distinct
experiences that call for **opposite** remedies:

- **STANDING RED.** The gate refuses on the *same subject* it refused on before. Nothing was
  repaired between attempts; the publisher is retrying, on a ~55-minute rhythm, into a red that no
  one is working. The remedy is to make the refusal *reach someone*. Batching more causes per round
  trip does nothing.
- **ARRIVAL STREAM.** The gate refuses on a *different subject*. The old one was cleared and new
  offending work landed from another lane. The gate is a shared-tree tax on a busy tree, the remedy
  is at the arrival, and telling the publisher about more gates per trip does not touch it either.

A count that does not separate these is the *average unit rate* failure again.

**Pair.** Within one bounded cost-episode, take that episode's refused cycles in log order; for each
gate `g`, take `g`'s own refusals in order; every adjacent `(r_i, r_i+1)` is one pair. Pairs are
per-gate: two different gates refusing in sequence is the queueing question, already settled.

**Verdict per pair**, on the subject SETS:

| verdict | when |
|---|---|
| `SAME` | sets equal and non-empty |
| `GREW` | strict superset — old subject still unfixed, new work arrived on top |
| `SHRANK` | strict subset — partial repair, remainder still red |
| `CHANGED` | neither a subset nor a superset, and they intersect or do not |
| `UNKNOWN` | either side has no extractable subject |

`UNKNOWN` is **fail-closed and is never folded onto either side of the headline split** — the same
discipline the existing `UNATTRIBUTABLE` bucket already holds in this module.

**ESTABLISHED re-arrival pair** (reusing the predecessor's proven rank logic, not re-deriving it): a
pair where some refusal *between* `r_i` and `r_i+1` names a gate of strictly HIGHER rank than `g`.
The chain is serial and `|| exit 1`, so that intervening cycle is a positive observation that `g`
**passed**. Any other pair is order-consistent and establishes nothing about passing.

---

## Predictions

Thresholds fixed here. A prediction filed after the answer is not a prediction.

**P1 — over ALL extractable pairs, `SAME` is the majority.** Threshold: **≥50%** `SAME`.
*Why:* the 68.8h episode ran 48 cycles; the orphan-ratchet blocks I read while checking the log was
parseable at all showed `tools.migrate_atom_names` twice, and the site-lane blocks showed one
identical node ID twice. **Declared WEAKLY INDEPENDENT:** those four blocks were read before this
was written. I have not counted, ordered, paired or classified anything.

**P2 — over ESTABLISHED re-arrival pairs only, `SAME` is the MINORITY.** Threshold: **<50%** `SAME`.
*Why:* this is the sharp one, and it is the near-opposite of P1 on a different population by
construction. A gate that demonstrably PASSED had its old subject cleared; refusing next on the
identical subject would mean repaired work was re-introduced, or the gate is non-deterministic.
Either is a worse finding than the arrival stream, so **if P2 is refuted, that is the result**, not
a reason to revise the prediction.

**P3 — `GREW` is observed at least twice.** Threshold: **≥2** pairs. *Why:* an unfixed subject with
new work piling on top is the mechanism that makes an episode long rather than merely repeated, and
239.6h of outage over 38 episodes is not made of single-subject blips.

**P4 — a material share of pairs is `UNKNOWN`, and it bounds every number above.** Threshold:
**≥10%** `UNKNOWN`. *Why:* the log retains only `git/hook output (last 40 lines)`. pytest's dot
progress and per-file test lists are verbose, so a subject printed above that cut is simply gone. If
P4 confirms, no percentage here may be quoted without it.

## The analytic control, fixed before running

The rank logic says an `ESTABLISHED` pair requires an intervening HIGHER-ranked refusal. So
**every `ESTABLISHED` pair must have at least 3 refusals between its endpoints inclusive**, and the
set of `ESTABLISHED` pairs must be a strict subset of all pairs. If any `ESTABLISHED` pair is found
with exactly 2 cycles between endpoints inclusive, the pairing or the rank lookup is wrong and every
number in the finding is void. This is keyed to the property, not to today's answer.

## What I will NOT claim

`CHANGED` does **not** establish that the earlier subject was repaired — only that it was not named
again. A gate stops at its first objection, so a still-broken subject can be masked by a new one it
sorts behind. `SHRANK` is the only verdict that positively evidences repair, and `CHANGED` will be
reported as *not established as repair* rather than as an arrival.
