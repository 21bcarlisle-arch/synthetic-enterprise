**Severity:** LATENT · **Lane:** H_harness · **Epoch:** 3 · **Atom:** (Lane 0 delivery — the two finished runs' artefacts reach origin and the envelope renders)

# The door knew the envelope was unpublished and said so seven times a run, as a skip

**2026-09-15, delivery seat.** The [LAUNCH UNLANDED] alarm fired **107 times over 106 hours**
saying the register claimed work git did not have. Every one of those hours, the control that
exists to catch exactly this defect was *running*, *correct*, and *reporting it* — as a **skip**:

> `SKIPPED [7] site/test_the_baseline_comparison_reaches_the_reader.py:5923: this publish carries
> no available blind envelope (None) — 'test_a_blind_envelope_the_producer_WITHHELD_renders_its_
> reason' owns that branch`

Seven controls, every run, for four days. A skip is not a red, so nothing ever blocked.

## Why this is not the door's fault, and where the defect actually is

`_live_feed()` → `published_json` → `published_blob` reads `git show :<path>` — **the index, never
the working tree** — and fails closed with the path named. That is right, and its docstring already
says the thing this finding is about:

> *"a `site/data/value_arms.json` that exists on disk and has never been committed is the defect,
> not the excuse."*

The door was load-bearing and it was correct. The defect is the **disposition**: `_blind(feed)`
treats "the feed has no `blind_envelope` key at all" and "the producer deliberately withheld the
block" as the same outcome, and routes both to `pytest.skip`. Those are two different worlds:

| feed state | what it means | what it deserves |
|---|---|---|
| key present, `available: False`, `why_not` set | the producer looked and refused, and said why | a skip — a named other control owns that branch |
| **key absent entirely** | **nothing at this ref can produce the block** | **a red** |

The skip message itself carried the evidence and nobody read it: it printed `why_not=**None**`,
which is `{}.get("why_not")` — the dict was **empty**. A block the producer withheld always names
its reason; only an absent key yields `None`. The control was one `is None` away from being able to
distinguish "refused with a reason" from "does not exist here", and that one distinction is the
whole 106 hours.

## The class this belongs to

This is *"nothing noticed it" — when it had been surfaced thousands of times into an undifferentiated
channel.* The signal was not missing, it was **indistinguishable**: seven skips per run sat in a
suite that legitimately skips for a dozen benign reasons, so the one skip that meant "this feature
reaches no reader at any ref" read exactly like "the error bar and the point estimate come from the
same run — nothing to say".

The same shape has now been paid for twice in this file's neighbourhood. A control that **fails
closed on a read** is not enough; it must also **fail loudly on an absence it cannot attribute**.

## What was done about it in this turn

The envelope is now published, so all seven controls RUN rather than skip — the door went from
`137 passed / 8 skipped` to `144 passed / 1 skipped` against the landed bytes. That removes today's
instance and **does not fix the class**: the next feature whose feed key never reaches the index
will skip seven times a run in exactly the same way.

**Recommended remedy, not done here and deliberately named rather than silently dropped:** split
the `_blind` gate on `"blind_envelope" in feed`. Absent key → `pytest.fail` naming the ref and the
path; present-and-withheld → skip as today. It is a two-line change and it is a *different* subject
from landing the envelope, so it goes to whoever draws this next rather than riding along inside a
delivery commit. The control over it must assert the **failing** branch is reachable — a guard that
refuses everything passes every test of a guard.

## Second, smaller finding, for anyone verifying this class of work

The instruction that drew this work specified verification by `git archive origin/main` into a
directory, then running the door there. **That cannot work and produces a false red.** An archive
extract has **no index**, so every `published_blob` call in it fails closed — the door would report
the feature broken at a ref where it is fine. Verification of any index-reading control needs a
real checkout. This is the third time an archive extract has been mistaken for a valid harness here.
