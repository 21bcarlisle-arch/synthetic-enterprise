**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0 delivery
· **Class:** publish_gate_and_wedge

# 78% of re-refusals are the IDENTICAL complaint, and one red was retried 24 times unchanged

Fourth turn on the Lane 0 direction *"measure and attribute commit_refused"*. Pre-registration:
`docs/staging/records/SEAT_PREREGISTRATION_WHETHER_A_RE_BREAKING_GATE_REFUSES_ON_THE_SAME_SUBJECT_OR_A_NEW_ONE_2026-09-05.md`,
written before any subject was extracted.

## The predecessor's premise was false, and that is the finding's foundation

It closed with:

> *"the log records which gate refused and never what changed between attempts, so the next
> question needs the tree state between consecutive refused cycles."*

**The log does record what changed.** Not the tree state — the *artefact the gate objected to*,
printed in the gate's own words inside the hook block the log already retains:
`§0: level_current 2->3 on <ATOM>`, `- TWO ROOMS <F>.md`, `FAILED <nodeid>`, the orphan ratchet's
indented module list. The instrument it proposed is also the wrong one, and I checked that before
designing anything else: `git log --all --since=2026-08-13` is **60–191 commits a day** against a
median 3300s gap between attempts, so *"did the tree move between two refusals"* answers YES for
re-breaks and non-re-breaks alike. That is two correct numbers whose ratio is not a quantity.

## The definition, fixed before counting

"Re-break" is one word over two experiences with **opposite** remedies:

- **STANDING RED** — the gate refuses on the *same subject*. Nothing was repaired; the publisher is
  retrying into a red no one is working.
- **ARRIVAL STREAM** — the gate refuses on a *different subject*. The old one cleared, new offending
  work landed from another lane.

## What it is

Over the observable window (2026-08-13 22:23 on), 107 pairs of consecutive refusals by **one** gate
inside one bounded episode; 99 with an extractable subject.

| verdict | n | share of extractable |
|---|---|---|
| **SAME** — standing red | **77** | **77.8%** |
| CHANGED | 14 | 14.1% |
| SHRANK — the only positive evidence of repair | 5 | 5.1% |
| GREW | 3 | 3.0% |
| UNKNOWN | 8 | 7.5% *of all pairs* |

- **194.7h of 239.6h bounded outage (81.2%)** sits in episodes carrying at least one standing-red
  pair. 10 episodes (50.8h, 21.2%) are standing red and *nothing else*.
- **102 of the 175 refusals** fall inside a run of ≥2 consecutive refusals on an identical subject.
- The worst: inside the 68.8h episode of 2026-08-14, **24 consecutive refusals naming the identical
  set of failed node IDs**, then 10 more on another identical set. Roughly a day of the publisher
  re-running a six-minute test suite to be told the same thing 24 times.
- The **level-promotion gate never once refused on a different atom**: 7 pairs, 7 SAME.

## What this does to the deferred change — it retires it as the fix

Three predecessors deferred telling the publisher about more than one refusal per round trip. That
change collapses a queue of *distinct* causes. **The dominant experience is not a queue of distinct
causes; it is one cause, stated identically, up to 24 times.** Batching cannot compress a repetition
it is not looking at. It remains worth making and it is not the fix, and shipping it against this
measurement would carry a justification that reads as though it addressed the 81.2%.

## Predictions: three confirmed, one REFUTED

- **P1 — SAME is the majority of extractable pairs (≥50%).** CONFIRMED, 77.8%. Declared WEAKLY
  INDEPENDENT in the pre-registration, and it is: four blocks were read while checking the log
  parsed at all.
- **P2 — over ESTABLISHED re-arrival pairs, SAME is the MINORITY (<50%).** CONFIRMED, 37.5%
  (3 of 8; CHANGED 5). **n = 8, and every statement about this population is bounded by that.** It
  is the one place the arrival-stream reading holds, and it is the smallest population here.
- **P3 — GREW observed ≥2 times.** CONFIRMED, 3.
- **P4 — ≥10% of pairs UNKNOWN, from the log's `last 40 lines` truncation.** **REFUTED: 7.5%, and
  the stated mechanism was wrong too.** Recorded as refuted, not revised. Truncation cost **zero**
  subjects: all 8 UNKNOWN pairs belong to gates that have no extractor at all (UNATTRIBUTABLE,
  UNNAMED, scope-evidence). Every pair whose gate *can* name its subject, did.

**The pre-registered analytic control HELD:** an established pair needs a cycle strictly between its
endpoints, so its span must be ≥3. Minimum observed span over the 8 established pairs: exactly 3.

## The instrument defect, caught by printing against the real log rather than by thinking

The first draft anchored the finding-class subject on the trailing colon, to stop `RESURRECTED
<F>.md: superseded by <CLASS>.md` capturing the *supersedor* instead of the subject. That anchor
silently dropped a fifth objection kind — `MISSING CLASS DOC <F>.md`, which ends at the filename
with no colon — taking **8 of 61 finding-class subjects** out of the analysis. This is the
predecessor's own defect repeated: *a fail-closed fix whose table read clean because its biggest
entries had left it.* Both near-misses now sit in one control, because a fixture carrying only one
is passed by a pattern that fails the other.

Two mutations survived and were run down rather than assumed benign. One was a **missing test** —
the alignment fixture was palindromic, so reversing the subject list left it byte-identical. One was
a **genuine equivalence**, established empirically and not by reasoning: inserting `.*?` before the
capture returns an identical 61-subject list over the whole log, because leftmost-minimal matching
already prefers the empty skip. The orphan ratchet's prose guard turned out unreachable on the real
log (its end marker always precedes), so a control now builds the unterminated block that reaches it.

## What I do NOT claim

`CHANGED` does **not** establish the earlier subject was repaired — a gate stops at its first
objection, so a still-broken subject can be masked by a new one sorting ahead of it. `SHRANK` (5
pairs) is the only verdict that positively evidences repair. Nothing here establishes *why* a
standing red stood: the log records what the gate said, never who was or was not looking at it.

## Still no mechanism, for the fourth turn running — and now the next one is named

The predecessor's reason was good and it has changed. The mechanism this evidence supports is not
batching: it is that **a refusal identical to the previous one is not news, and the publisher
currently cannot tell.** It re-runs a six-minute suite on its own rhythm and re-reports a byte-
identical complaint as a fresh failure. The smallest thing that can fail: carry the previous
refusal's subject set, and when the next refusal matches it, say *"unchanged, Nth time, since T"*
rather than reporting a new one. That is a one-leg change with an obvious mutation, and it is what
the 24× run would have surfaced on its second cycle instead of its twenty-fourth.

I am not building it in the same turn that measured it, because the measurement is what makes it
justifiable and the two should be separable in the record.

**Evidence:** `python3 -m tools.commit_refusal_attribution` (final section). Controls:
`tests/tools/test_commit_refusal_attribution.py`, 34 tests, the 9 new ones mutation-proven.

## Class registration

Belongs to `publish_gate_and_wedge`.

*Declared 2026-09-05 by the delivery seat, on the director's instruction to fold findings into the class registers rather than leave them as individual documents. Classified on the MECHANISM THIS DOCUMENT DESCRIBES (its body), not on its title: the registered classifier greps titles, and the titles have outgrown its vocabulary — which is why 92 findings sat `unclassed` while the six classes held 138 instances. The body carries 7 matches for `publish_gate_and_wedge` against 3 for the runner-up, which is the threshold used; anything below it was left for a reader rather than graded from a sibling.*
