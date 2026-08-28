**Severity:** LATENT · **Lane:** H_harness · **Epoch:** 3 · **Atom:** `H45_the_queue_is_chained_to_the_map`

# Finding: a re-issued Lane 0 claim can never be credited with the work that already landed, so the lane re-draws finished work forever

## What happened, on this tick

The 2026-08-28 21:00 tick was handed the Lane 0 brief
*"wire the sourced acquisition and retention costs"* — replace `COST_PER_ACQUISITION`, move the I&C
trail to `broker_commission_gbp()`, remove `RESI_OFFER_COST_GBP`, leave a control.

**All of it was already at HEAD.** Commit `0850eadcd` (2026-08-28 20:46:18 BST) landed R1–R5 of
`WORKER_FINDING_THE_SOURCED_ACQUISITION_MODEL_IS_UNWIRED_AND_THE_INVENTED_ONE_IS_LIVE`, including
the control (`tests/saas/test_sourced_acquisition_costs.py`) and its complement
(`tests/architecture/test_a_cited_constant_has_a_caller.py`). The tick was drawn to do work that
was done fourteen minutes before it started.

The claims file explains why:

```
"wire-the-sourced-acquisition-and-retention-costs": {
  "claimed_at": 1787946897.17,   # 2026-08-28 20:54:57 BST
  "paths": []                     # <-- nothing ever bound
}
```

The commit is `1787946378` (20:46:18). The claim is `1787946897` (20:54:57). **The claim is 8m39s
younger than the commit that satisfied it.**

`background/delivery_lane.record_landing` then refuses, by design and with the reason stated:

```python
if when <= since:
    return []
```

> *"the commit is NOT NEWER than the claim. A commit that predates the claim is somebody else's
> work, or this tick's own earlier work, and crediting the claim with it would restart a deadline on
> something that had already happened."*

## The defect is in what that reasoning does not cover

The refusal is correct for a **continuing** claim: an old commit must not restart a live deadline.

It is wrong for a **re-issued** one. The sequence that produces the trap:

1. A tick lands the work at T1 and exits without calling `--landed` (the documented failure mode —
   this project already carries `feedback_landed_work_not_bound_to_its_delivery_claim_gets_swept_and_redrawn`).
2. The sweep sees `paths: []`, concludes nothing landed, and returns the focus to the pool.
3. The focus is re-drawn at T2 > T1, writing a **fresh `claimed_at`**.
4. From that moment the T1 commit is unbindable **by anyone, forever**. Every future tick that
   correctly runs `--landed` gets `bound NOTHING`.

**The lane cannot distinguish "not done" from "done but unbound", and step 3 makes the distinction
permanently unrecoverable.** The failure is not that a binding was missed once; it is that the
missed binding is converted into a standing instruction to redo finished work. A tick that obeys
its brief literally would re-implement R1–R5 on top of themselves.

This is the FAIL-OPEN shape from the R15 catalogue pointing the wrong way: the progress measure
reads zero when the evidence exists and is simply out of reach of the check.

## Why this is LATENT and not an annoyance

The cost is a whole tick each time, and it does not self-clear — the same brief comes back with the
same unbindable history. The lane's own justification for existing is in its docstring at line 70:
*"Twelve alarms were filed saying 'nothing has landed'; at least five had landed real work."* **This
is that same false negative, re-entering through the re-draw rather than through the missing call.**

## The repair, and what I did not do

The cheap fix is to make the re-issue carry its history: when a focus id is re-drawn, seed the new
record's `claimed_at` from the **previous** claim of the same id rather than from now — or let
`record_landing` compare against the earliest claim of that focus id still on file. Either restores
the ability to credit a commit that a sweep orphaned, without letting an unrelated older commit
restart a live deadline (the case the current check is defending, which stays defended because the
commit must still postdate the *first* claim).

**I have not built it.** A change to how the lane measures its own progress is a control over the
controls, and this file is the evidence it needs rather than the second mechanism. What this tick
did instead was the part of the brief that genuinely was not done — the arms re-run, pre-registered
in `WORKER_PREREGISTRATION_WHAT_THE_SOURCED_COST_RERUN_MUST_SHOW_2026-08-28.md`.

## The one thing a reader should check before trusting any "nothing landed" alarm

`git log --oneline --since=<claimed_at>` is not enough, because the satisfying commit may sit just
**before** `claimed_at`. Check the claim's subject against HEAD directly. On this tick the brief's
own words — `COST_PER_ACQUISITION`, `RESI_OFFER_COST_GBP` — were both already absent from the
files it named, which took one grep and settled it.
