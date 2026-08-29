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

---

## DISCHARGED 2026-08-30 (worker tick) — built by a later tick, and this is its first live firing

**The repair the section above declines to build was built the same day**, in
`background/delivery_lane.py` at `3f33d92fa`: `DRAW_LEDGER_FILE` remembers `first_drawn_at` per
focus id across releases, and `record_landing` compares a commit against the id's FIRST draw rather
than against the `claimed_at` a re-draw rewrote. The module docstring carries the reasoning under
*"A RE-ISSUED CLAIM COULD NEVER BE CREDITED…"*.

**This tick is the first time it has been exercised on a real orphaned commit, rather than on a
fixture.** The trap sprang in full and the fix caught it:

| | |
|---|---|
| focus id | `land-the-founder-book-controls-that-are-in-no-commit` |
| `first_drawn_at` | 1788039503 — 2026-08-29T21:38:23Z |
| commit that satisfied it | `cea3ff2d7`, 1788039888 — 2026-08-29T21:44:48Z, **385s after the first draw** |
| that tick called `--landed` | **no** — step 1 of the sequence above, verbatim |
| swept, re-drawn (`claimed_at`) | 1788044916 — 2026-08-29T23:08:35Z, **5,028s after the commit** |
| brief handed to this tick | "still uncommitted", naming three `.held` artefacts already deleted in HEAD |

Under the pre-`3f33d92fa` rule this tick would have got `bound NOTHING` and the commit would have
been out of reach by 5,028s, permanently. It got `bound 8 path(s)` — the three test files, the three
`.held` deletions, `docs/design/held/README.md` and `docs/design/FOUNDER_BOOK.yaml` — and the claim
was released rather than re-implemented.

**What the fix does not cover, stated so the next reader does not mistake this for closed.** The
lane still cannot tell "not done" from "done but unbound" *at draw time*: the brief this tick was
handed asserted uncommitted work about a tree where all of it was in HEAD and green, and only the
reader's own check found that. The fix makes the record recoverable AFTER the fact; it does not stop
a stale brief being issued. That residue is deliberately left un-mechanised — a draw-time verifier
of the lane's own briefs is a control over the controls, and CLAUDE.md's rule is to prefer doing the
work. **The cheap reader-side check is the section above and it cost this tick ninety seconds:**
`git cat-file -e HEAD:<each path the brief names>` before believing a word of it.

Verification run for the discharged work itself, against the tree HEAD would create
(`git archive HEAD | tar -x` — never the shared tree, which measures three other lanes):
`tests/simulation/test_founder_book.py`, `test_live_population_seam.py`, `test_customer_events.py`
→ **80 passed**.
