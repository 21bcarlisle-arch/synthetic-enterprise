# [SEAT FINDING] The two-arm figures name their substrate by a path that is rewritten under them

**Severity:** RECORDED · **Lane:** D_billing_metering · **Epoch:** 3 · **Atom:** unminted
**Found:** 2026-09-03, by re-running a landed claim's own measurement from the tree it was landed
from, rather than reading the commit message that asserted it.

## Class registration

Belongs to `figures_on_a_superseded_clock`.

## What was claimed, and what the tree said an hour later

`e07449df5` published the opening direct-debit two-arm comparison and carried a control in its own
message:

> CONTROL FIRST: run_output_latest.json predates the organ, so its own DD books ARE the flat arm as
> the real run computed them. The reconstruction reproduces dd_balance_book byte-identically and
> annual_dd_review on all 806 events and every summary field.

Re-run from the working tree on 2026-09-03, that control reports:

    FLAT ARM REPRODUCES THE PUBLISHED PRE-ORGAN BOOK:
      annual_dd_review: NO
      dd_balance_book: NO

The tool's own docstring says what a NO means: *"If it does not reproduce, the reconstruction is
wrong and every number this module prints is void."* On its face, the published comparison had just
voided itself.

## It had not. The substrate moved, not the reconstruction

`docs/reports/run_output_latest.json` is rewritten in the working tree by `process_run_complete`
every time a run finishes. The committed blob at HEAD and the working-tree copy standing at the
same path differ in **75 of 104 keys**, all three DD keys among them.

Run against the **committed blob**, the published artefact reproduces **exactly** — every figure,
byte for byte:

| | published artefact | committed blob | working-tree copy |
|---|---|---|---|
| reproduces published figures | — | **YES (exact)** | no |
| flat peak held credit | 3394.32 | **3394.32** | 3396.74 |

So the figures on the page are sound and attributable. What was not sound is the **clock**. It read:

    "clock": {"substrate": "docs/reports/run_output_latest.json", "n_bills": 10906, ...}

A path, and nothing else. That path is a moving pointer, so the clock said *"these figures came from
whatever is standing there now"* — which was already false when it was written, and no reader,
session or control could have told.

## Why this is the class and not a one-off

This is `figures_on_a_superseded_clock` in its purest form: the figure is right, the label is right,
and the label's *referent* changed underneath both. It is not caught by the basis gate, which asks
whether a figure carries a clock — this one did. **A basis label naming a mutable path is not a
clock, and the gate cannot see the difference between a name and an identity.**

It also produced the exact false alarm the catalogue warns about: a control reporting a true RED for
the wrong reason. A future session reading `NO` would have concluded the reconstruction was broken
and either rebuilt a working experiment or withdrawn a sound published figure.

## The repair, landed with this record

1. `tools/dd_opening_arms.py` stamps `substrate_sha256` — the digest of the bytes the run actually
   read — into the clock, and carries it through `publish_view` to the reader's feed.
2. When the flat arm does not reproduce, the tool now **says which of the two failures it is**,
   because they have opposite repairs and a bare `NO` cannot distinguish them:

       SUBSTRATE HAS MOVED since the published artefact was written:
       214e79d39daa -> 955694b1336a. Any NO above is about the SUBSTRATE,
       not about the reconstruction.

3. Both published artefacts are stamped with `214e79d3…`, the digest of the substrate **proved by
   exact reproduction** to be the one that produced them. The figures were not regenerated: a
   regeneration against today's substrate would have silently replaced a pre-organ baseline with a
   post-organ one and destroyed the comparison the artefact exists to carry.
4. Two controls in `tests/tools/test_dd_opening_arms.py`, both mutation-proven: the clock must carry
   a recomputable identity, and the reader's feed and the report may not disagree about which
   substrate the figures came from.

**Deliberately not controlled:** that the recorded digest equals the substrate on disk. Those
legitimately differ the moment any run completes; a control asserting equality would be keyed to
today's answer and would wedge every lane. Naming *which* side moved is the tool's job, and it now
does it.

## What this does not close

The substrate is still a working-tree file no commit pins. The digest makes drift **detectable and
attributable**; it does not make the pre-organ substrate durable. If `run_output_latest.json`'s
committed blob is ever regenerated, the artefact becomes unreproducible from anything on disk and
the honest response is a named refusal on the surface, not a re-run against a different world.
That is a live gap, stated rather than closed.
