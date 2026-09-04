**Severity:** BLOCKING · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0 delivery
· **Class:** publish_gate_and_wedge

# FINDING: the reconciler and the publisher each stand down for the other, and the tree stayed behind origin

**Found:** 2026-09-04 16:10–16:15Z, delivery seat, working the Lane 0 direction *"the figures
stopped reaching the reader and no direction ever named the path"*. Every number below is measured
from a ledger named beside it, not inferred.

---

## The direction's stated wedge was already discharged — and the symptom was still true

The doorbell said the site lane was wedged on untracked controls and eight `run_complete_*.md` were
queued. At this orientation: `git ls-files` shows `site/harness/test_the_deployment_reading_reaches_the_reader.py`
and `site/harness/_render_harness.mjs` **tracked**; `git status --porcelain site/` is **clean**; and
there are **zero** `run_complete_*.md` in `docs/staging/` (1,516 in `done/`). The repair described as
unlanded in `SEAT_FINDING_A_CLEAN_PUBLISH_INSIDE_AN_OPEN_EPISODE...` is **landed, both halves**.

**And the reader was still five hours stale.** Last successful publish `10:53Z`; at `16:10Z` the
page still served `run_output_8c5b18ca1_20260904T084511Z.json`. Every stated cause was fixed and the
symptom was unchanged — which is the signal that the cause on the doorbell was never the cause.

## The race, measured rather than estimated

`SEAT_FINDING_THE_PUBLISHER_CHECKS_BEHIND_ORIGIN_ONCE...` predicted this and asked for the
measurement over a longer window than the one morning it had. Here it is. **Say what each number
counts before dividing them:**

* **672s** — median duration of ONE publish gate cycle. Source: `docs/observability/publish_gate_duration.jsonl`,
  the publisher's own scoped gate, last 7 cycles: 664, 650, 672, 651, 690, 689, 715s. Notably
  **stable** — the spread is 65s, so this is not a tail problem.
* **3.8 min** — median gap between consecutive commits on `origin/main`, last 6 hours, n=61.
  Source: `git log origin/main --since='6 hours ago'`.

Their ratio is a real quantity: **~2.9 commits arrive on origin during one publish cycle.**
`BEHIND_ORIGIN` is evaluated once, at the END of that cycle. A one-shot check against a target that
moves three times per cycle is not a guard; it passes only by luck, and today it did not.

Observed, every one after a GREEN gate and a verified provenance:
`13:05`, `14:27`, `15:48` — *"Done, but THE PUBLISH DID NOT LAND (outcome: behind_origin)"*.

## The new part: the two mechanisms each correctly stand down for the other

This is not the race, and it is why the race is never survived. Both refusals are RIGHT.

* **The reconciler stands down for the gate.** `origin_reconcile.reconcile()` returns `GATE_RUNNING`
  while `process_run_complete` holds its run lock — *"reconciling under a running gate spends the
  whole run and refuses it at the last step"*. Correct.
* **The publisher stands down for the fork.** `_divergence_refusal()` returns `BEHIND_ORIGIN` before
  staging — *"a commit created here could only be rejected non-fast-forward and would widen the fork
  by one more"*. Correct.
* **And `deadmans_switch._check_origin_fork` has already ruled out the obvious repair, on the
  record:** *"ON THIS CADENCE AND NOT IN THE PUBLISH PATH, which is the objection the publish path's
  own refusal raises and it is a fair one: a gated merge takes longer than a publish cycle."*

So the reconcile window is only whatever gap is left BETWEEN publish cycles, and each publish cycle
re-opens the fork the next reconcile must close. **Nobody is wrong and the tree stays behind.** I hit
this live: `reconcile()` at 16:12Z returned `GATE_RUNNING` and left the tree 2 behind.

## The instance that made it stick: a lossless twin nobody is allowed to delete

At `16:04Z` and `16:08Z` the reconciler reported `NOT_ADVANCED`, naming its cause:

    Refused by 2 path(s):
      docs/staging/SEAT_FINDING_THE_CADENCE_LEVER_WAS_LIVE_..._2026-09-04.md
        (untracked here, and origin adds its own copy)
      docs/staging/SEAT_PREREGISTRATION_WHETHER_THE_CADENCE_LEVER_..._2026-09-04.md
        (untracked here, and origin adds its own copy)

Both were **byte-identical to origin's blobs** — verified, not assumed:

```
local  4bf0e9e24756f2f1eb287a6c1f9645dbc8b4e01d   origin 4bf0e9e24756f2f1eb287a6c1f9645dbc8b4e01d
local  d200bacc5f3c9897d382d0362082476b90bbde8e   origin d200bacc5f3c9897d382d0362082476b90bbde8e
```

**Nobody's work was at stake and no mechanism was permitted to say so.** The reconciler will not
delete files it did not create — a correct refusal, since an untracked path is normally a lane's
unlanded work. But when the local content hashes EQUAL origin's blob at that path, removal is
provably lossless: the merge restores the identical bytes as tracked. That case is indistinguishable
from the dangerous one under the current rule, so the tree waits for a human for a deletion that
costs nothing. I removed one by hand; the other was removed concurrently by another lane mid-turn.

## The remedy — and who owns it

**`background/origin_reconcile.py` is being edited RIGHT NOW by another lane, uncommitted**, and I
have deliberately not touched it. They have built the *naming* half of exactly this refusal
(`paths_blocking_fast_forward`, `FF_UNTRACKED`, `FF_MODIFIED`) and it is good work — the refusal
text quoted above is theirs. What is missing is the *acting* half, and it is small:

> When a path blocking `merge --ff-only` is `FF_UNTRACKED` **and** `git hash-object <path>` equals
> `git rev-parse origin/main:<path>`, remove it and retry the fast-forward once. Refuse exactly as
> now on any hash mismatch, and name the paths removed.

That is one leg, it fails closed, and its control writes itself: a tree with an untracked twin
fast-forwards; a tree with an untracked file whose content DIFFERS still returns `NOT_ADVANCED`.
**Write both legs** — a guard that removes nothing passes the second on its own.

Handing it to the lane holding the file is the point. Two lanes fixing one function concurrently is
how the merge becomes the place you find out.

## What is NOT claimed here

The race itself is untouched, and this finding does not fix it. It makes the mutual stand-down
visible and quantified, and it removes one recurring instance. **The open judgement is unchanged and
still wants deciding:** give the publisher `surgical_land`'s bounded lost-the-race retry (re-gate on
the new base), or have it commit THROUGH `surgical_land`. Both touch the commit path, which is a
wall, so it needs its own design and its own controls — it is not a bounded-tick change, and it is
not this turn's.

I also did not disposition the second live red
(`test_self_clearing_alarm_census.py::test_every_live_hit_is_dispositioned`), for the same reason
the previous seat did not: marking another lane's control benign to unblock my own commit is the
fail-open that census exists to refuse.
