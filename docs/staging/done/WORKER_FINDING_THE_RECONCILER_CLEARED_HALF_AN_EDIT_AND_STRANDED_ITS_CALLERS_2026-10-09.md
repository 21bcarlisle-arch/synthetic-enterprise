*Archived 2026-10-10: the repair landed in `470f2a746` (`origin_reconcile.stranded_caller_verdicts` + its control are on origin/main). The named better act, clearing the callers together with the cleared copy, is unbuilt and stays the refusal it is today.*

**Severity:** LATENT · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted` · **Claim:** `the-executors-crash-on-a-half-cleared-edit` (Lane 0 delivery)

# The reconciler cleared one file of a three-file edit and left the two callers live

## What happened

An uncommitted edit made on 2026-10-01 touched three files. It defined
`delivery_lane.held_at_dispatch` and made `worker_tick.py` and `seat_executor.py` call it. At 09:18
on 10-09, origin's advance wrote `delivery_lane.py`, so that file blocked the fast-forward. It had
sat for more than 48 hours, so the abandoned class preserved it to `07941f1b4` and cleared it.

**Why the callers were left: they were never asked about.** The task framed it as "cleared
`delivery_lane.py` but left `worker_tick.py`", which suggests a verdict was reached on
`worker_tick.py`. None was. `paths_blocking_fast_forward` lists only the paths origin writes, and
every class judges those paths one file at a time. Origin wrote neither caller. Their age did not
matter: no class ever saw them. From then on, every worker-tick and seat-executor run died with
`AttributeError` at dispatch, until the interactive lane restored both callers at 14:53.

## The repair, landed with this note

- `origin_reconcile.stranded_caller_verdicts` runs last, over everything about to be cleared. For
  each `.py` file it finds the top-level names the local copy binds and origin's copy does not.
  It then looks for references to any of those names in every dirty `.py` file that stays, in
  either form: `module.name` or `from module import name`.
- Any reference holds that path. Under the all-or-nothing rule that refuses the whole advance, and
  the refusal names the caller and the name.
- The real 10-01 bytes produce exactly `held_at_dispatch` in both callers, and nothing in origin's
  copies.
- Control: `tests/background/test_clearing_one_file_of_an_edit_cannot_strand_its_callers.py`, which
  includes a partition leg. Turning off the `if hits:` branch reds both behaviour legs.

## Not done, named

- **Neither, not both.** The safe act today is to refuse. The better act would clear the callers
  together with the cleared copy. No class has a proof for the callers, because they are not
  blockers, so that is left for later.
- **The feature itself landed whole in `f951bbfe4`** (the interactive lane), with both callers and
  a control, while this note was being gated. The preserved refs remain for the record:
  `refs/preserved/held-at-dispatch-20261009/{worker_tick,seat_executor}` (the 10-01 blobs, which
  the incident test reads).
- **Lanes are back.** seat-executor finished cleanly at 14:55, and this turn is the next run.
  worker-tick spawned a worker at 14:53. The interactive lane is watching for the second
  consecutive clean run.
