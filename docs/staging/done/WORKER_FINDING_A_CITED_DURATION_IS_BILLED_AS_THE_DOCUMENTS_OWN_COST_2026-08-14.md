# WORKER FINDING — a duration a document merely CITES is billed as that document's own cost, and the class total moves with it

**Severity:** LATENT · **Lane:** H_harness
**found:** 2026-08-14, discharging control 2 of
`WORKER_FINDING_THE_WEDGE_WAS_FIVE_INSTANCES_OF_ONE_CLASS_AND_pytest_x_SERVED_THEM_ONE_AT_A_TIME_2026-08-14.md`
**status:** OPEN — observed with evidence, not repaired (SELF_INTERRUPT_DISCIPLINE: registered,
not fixed on sight). The instance that provoked it was reworded, so no live class document
currently carries the mis-attribution.

## What was observed (observed-with-evidence)

`background/finding_classes.py` renders each class document's **"Cumulative cost, measured from
the instances' own recorded evidence"** section by harvesting a duration phrase out of each
instance's prose. Its own stated definition is *"Each instance contributes the LARGEST duration it
records with evidence"* — the document's **own** episode.

It cannot tell that from a duration the document merely mentions.

Observed directly. While writing the discharge for the control-2 build, one sentence explained a
budget derivation by referring to a **different** episode already recorded elsewhere in the tree:

> a wrapper bound that drifted from the work it wrapped is the 41-hour wedge already recorded at
> `PUBLISH_PATH_ALLOWANCE_SECONDS`

`python3 -m background.finding_classes --render` immediately billed those hours to the discharging
document, which has never measured its own damage in hours at all:

| | before the sentence | after it |
|---|---|---|
| this instance's recorded cost | 0h (contributed nothing) | **41h** |
| `CLASS_PUBLISH_GATE_AND_WEDGE` total | 152.0h across 9 of 27 | **193.0h across 10 of 27** |

The 41 hours are real and are already counted — under the episode that actually spent them. The
render therefore double-counts them, and attributes them to a document whose subject is a
different wedge entirely.

## Why it matters more than the arithmetic

The class total is the figure that argues one repair against a cumulative cost — it is what makes
a class BLOCKING rather than housekeeping. Its integrity rests entirely on the definition quoted
above, and that definition is enforced by nothing: the harvester reads a regex over prose, so any
document that *explains itself by referring to another episode* inflates its own cost and the
class's. The direction is the dangerous one — costs only ever grow, never shrink, so a class can
argue itself louder purely by being well cross-referenced.

This is the wrong-subject shape the project has filed before: the number is attached to whatever
document the phrase was found in, not to what the phrase is ABOUT.

## What is NOT claimed

- No claim that any other instance is currently mis-billed. The harvest was not walked
  document-by-document — one instance was observed, in the act of creating it. The base rate is
  unmeasured, and one observed divergence is not a base rate.
- No claim that the totals published to date are wrong. They may be; nothing here establishes it.
- No claim that the regex is the wrong mechanism. Prose is what these documents are.

## The repair (not applied here)

The harvester needs the document to say which duration is ITS OWN, rather than inferring it from
proximity. The cheapest form that can actually fail: a structured `**Episode-cost:**` header field
(the same shape as `**Discharged:**`, which is already parsed and filesystem-checked), with prose
harvesting kept ONLY as a fallback for the documents written before it — and a control asserting
that a duration appearing in a document that also declares the field is never taken from the
prose. Mutation test: put a cited duration larger than the declared one in the body and assert the
declared one still wins; a version that takes the maximum fails.

Cheaper interim, if the field is too much: refuse to harvest a duration from a sentence that also
names another document or a code constant — i.e. treat a citation context as a disqualifier
rather than a source. Weaker, and it would not have caught a bare restatement.

**Evidence:** `background/finding_classes.py` (cost harvest + the definition paragraph it
renders) · `docs/staging/CLASS_PUBLISH_GATE_AND_WEDGE_2026-08-12.md`, the 152.0h → 193.0h → 152.0h
sequence across three `--render` runs on 2026-08-14, the middle one with the citing sentence in
the tree and the last with it reworded.

**Related:** [[feedback_a_wrong_population_may_have_no_live_producer]],
[[feedback_one_observed_divergence_is_not_a_base_rate]],
[[feedback_a_harnesss_convenience_chose_the_controls_subject]],
[[feedback_a_reconciliation_gap_can_be_the_quantity_it_seems_to_measure_the_error_of]].
