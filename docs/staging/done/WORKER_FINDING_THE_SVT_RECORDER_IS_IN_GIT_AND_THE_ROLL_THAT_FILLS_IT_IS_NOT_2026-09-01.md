**Severity:** RECORDED · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** `union-the-departure-routes-and-declare-the-denominator`

**Class:** `uncommitted_and_orphaned_work` (existing class, so this instance is born archived).

# The SVT recorder is in git and the roll that fills it is not, so the native capture is native by half

`WORKER_PREREGISTRATION_WHAT_A_NATIVE_SVT_CAPTURE_MUST_SHOW_2026-09-01.md` rests its whole frame on
one sentence:

> **So this is the first capture in this repo's history whose SVT sibling has a producer in git.**

**That sentence is false, and it is false for exactly the reason the prereg gives one paragraph
earlier about the artefact it is distancing itself from.** Of the foreign 1,266-row sibling the
prereg writes that it *"came from a working tree carrying another lane's uncommitted roll and
recorder"*. It then verified the **recorder** was in git and did not verify the **roll**.

## What is actually in git, checked at `83946eb44`

The recorder is there, exactly where the prereg says:

```
$ git show HEAD:simulation/run_phase2b.py | grep -n "_svt_decisions"
1419:    _svt_decisions: list[dict] = []
1656:            _svt_decisions.append({
3244:        "svt_decisions": _svt_decisions,
```

The roll is not. At HEAD the only mention of the product in the renewal builder is a pass-through
that fires when the roster *already* says SVT:

```
$ git show HEAD:simulation/renewals.py | grep -n "SVT_TARIFF_TYPE\|build_svt_schedule"
41:from simulation.svt_product import SVT_TARIFF_TYPE, build_svt_schedule
100:    if tariff_type == SVT_TARIFF_TYPE:
101:        return build_svt_schedule(
```

and `simulation/svt_product.py` at the same HEAD states the consequence in its own docstring, in
its own words:

> **An account on this product cannot currently leave.** … here only for a customer record that
> says `tariff_type: "svt"`, and **no roster writes that**.

The code that writes it — the C1b passive roll, `rolls_active_renewal(...) → build_svt_schedule(...)`
— is **56 uncommitted lines in `simulation/renewals.py`**, mtime `2026-08-31 09:37`, in no commit
and not on `origin/main`:

```
$ git diff --stat origin/main -- simulation/renewals.py
 simulation/renewals.py | 56 ++++++++++++++++++++++++++++++++++++++++++++++++++
```

## Why this is load-bearing and not pedantry

**It decides P1, and P1 is the prediction the prereg said it was least sure of.** P1 asks whether
the sibling is written non-empty. The prereg names the live alternative precisely — *"if no roster
assigns the SVT product in a default `run_phase2b`, the recorder runs and records nothing"* — and
then treats `6db30a350` landing the recorder as what settles it. It does not. **The uncommitted
`renewals.py` settles it.** Run this capture on the working tree and P1 passes; run the identical
command on a clean checkout of the same HEAD and P1 lands empty, because nothing puts an account on
SVT. P1 as written therefore measures the working tree, not the commit it names.

**And it means the capture now in flight is, on the provenance question, the same kind of artefact
as the one it was built to replace.** Not the same defect — the two files do describe one run this
time, which is a real improvement and the thing the prereg most wanted — but the producer is still
not reconstructible from git alone. The correct claim is narrower:

> *This is the first capture whose renewal table and SVT sibling come from a single run. Its
> producer is still not wholly in git: the recorder is, at `6db30a350`; the roll that populates it
> is 56 uncommitted lines in `simulation/renewals.py`.*

## What was NOT done about it, deliberately

**The uncommitted `renewals.py` and `departure_level_anchor.py` were not committed to make this
capture reproducible.** Two reasons, both binding:

1. `simulation/departure_level_anchor.py` in the working tree carries a **pasted `YEAR_LEVEL_ANCHOR`
   block fitted on `ladder_churn_factors.json`** — the foreign capture. Lane 0 for today named "no
   constant pasted into `simulation/departure_level_anchor.py`" as a thing that must not happen on
   the strength of this run. Committing that block as a side effect of a provenance repair is that
   prohibition being broken sideways.
2. Both files are another lane's in-flight work. Landing them on their behalf, from a tick whose
   pathspec merely happens to include `simulation/`, is the sweep the pathspec rule exists to stop.

**So the capture was run on the working tree, and the tree state it was run on is recorded** rather
than laundered — `/tmp/svtcap/PROVENANCE.txt` carries the launch time, the HEAD, and the sha256 of
all five run-relevant modules as run, with the three that differ from `origin/main` named as dirty.
A capture whose provenance is written down is not the same thing as a capture whose provenance is
clean, and this one is the first kind.

## The owed item

**Land the C1b passive roll.** Until `simulation/renewals.py` is in a commit, every SVT sibling this
repo produces is irreproducible from git, no anchor fitted on one can be adopted, and the next
reader will re-derive this finding. It is in another lane and it is the binding item for the
whole-book anchor — the same shape as, and the direct successor to, the binding item
`WORKER_FINDING_THE_SVT_ROUTE_CAN_NOW_SEE_THE_MARKET_AND_THE_NEXT_GATE_IS_A_STALE_CAPTURE_2026-09-01.md`
recorded and the prereg believed discharged.

## Related

* `WORKER_FINDING_A_PUBLISHED_CAPTURE_WAS_PRODUCED_BY_CODE_THAT_WAS_NEVER_COMMITTED_2026-08-31.md`
  — the same class, one turn of the crank earlier.
* `WORKER_FINDING_A_FOREIGN_SVT_SIBLING_IS_WHAT_MAKES_THE_ACCOUNT_DENOMINATOR_CONTROL_PASS_2026-08-31.md`
  — what an unreproducible sibling does to a control downstream.
