# WORKER FINDING (QUEUED) — a roll inside the sole write path did not fire

**Severity:** LATENT · **Lane:** H_harness

**Found by:** the H_GAP tenth Expert Hour tick, 2026-08-12, as a blocker rather than as
its subject. Queued per SELF-INTERRUPT DISCIPLINE — the instance is cleared, the class
is not, and this is an atom for `tools/simplifications_store.py`, not for H_GAP.

**Status:** the instance is CLEARED (H27 drained, HEAD green). The mechanism question
below is OPEN and is what needs an owner.

## Observed, with evidence

* `tests/design/test_simplifications_store.py::test_the_live_store_has_roll_headroom`
  was **RED on HEAD** (2b80066ac) before this tick touched anything:
  `H27_payment_belief_gap.yaml: 70158 B over the 65536 B watermark`.
* That file at 2b80066ac is **byte-identical** to what
  `simplifications_store._dump` produces from its own parsed content (70,158 B both
  ways, `raw == redump` True). **It was written by the store's own writer**, not
  hand-edited around it.
* `_write_tenants` calls `_roll` whenever the body exceeds `ROLL_WATERMARK`, and only
  `MAX_FILE_BYTES` (100 KB) raises — so a write that plans no chunks lands over the
  watermark **silently**.
* Calling the maintenance entrypoint `roll_for_atom("H27_payment_belief_gap")` on that
  same content **drained 2 entries with no content change**, 70,158 → 63,930 B, register
  verbatim (26 notes, 17 + 17 records, concatenated view hash-identical).

## Inferred, and NOT established

The roll appears to have planned no chunks at write time on content a later forced roll
drained without difficulty. Why is not established: `_roll` returning an empty plan (in
which case `_write_tenants` keeps the un-rolled body and writes it), a chunk-packing
interaction with the existing `014` chunk, and an ordering effect against the archive
state are all consistent with the evidence above and none has been distinguished. **No
cause is asserted here.**

## Why it matters, and the class to test for

The seventh H_GAP Hour's own claim for this mechanism was *"it runs INSIDE
`_write_tenants`, the sole write path, so no tick has to remember to drain"*. What is
observed is a write through that exact path leaving the file over the watermark, and the
tenth standing control (`test_the_live_store_has_roll_headroom`) catching it **one lane
later** — it reds HEAD for whoever commits next, which on this occasion was a different
atom's Expert Hour.

> Candidate class: **a drain that runs on the write path but can plan nothing has no
> way to say so.** The bound raises; the WATERMARK does not — it writes, returns
> normally, and the standing control converts a silent non-drain into someone else's
> red tree.

## What a fix probably has to include (not decided here)

1. A reproduction: the smallest tenant state on which `_write_tenants` writes a body
   over `ROLL_WATERMARK`. Until that exists, R4 says do not fix.
2. R15 on the failure the reproduction shows — a plan-nothing roll must be observable
   at the moment it happens, not one commit later.
3. A decision on whether an un-drainable write should RAISE at the watermark (it
   currently only raises at the cap), weighed against the record store's own principle
   that it must fail toward keeping the record.
