**Severity:** BLOCKING · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** `union-the-departure-routes-and-declare-the-denominator`

# FINDING — the level anchor's new guard is green at HEAD and red in the tree the world actually runs from, and the block that reddens it is in no commit

**Found 2026-09-01 ~20:20Z, delivery seat, Lane 0, on the drawn Lane 0 item.** The drawn item's own
"done means" was discharged before this tick opened — the capture ran to completion, the five
predictions are graded at `68ec6825b` / `39967d018` / `83cdb7dd4`, the stale docstring was corrected
at `342d72159` and `7cb667126`, and the whole-book fit emitted. That is established in
`WORKER_PREREGISTRATION_WHAT_A_NATIVE_SVT_CAPTURE_MUST_SHOW_2026-09-01.md` and is not re-derived
here. **This stretch followed the interconnection instead**, which is what the seat is for: of what
landed since the last orientation, what else assumes it, and does that assumption still hold.

It does not.

---

## The finding, measured

`9fd700366` (2026-09-01 20:44:18 +0100 = **19:44Z**) landed a fail-closed guard on
`simulation/departure_level_anchor.year_level_anchor`: a year **inside** the published record with no
fitted anchor now raises instead of silently taking the reference year's value. It landed with a new
control, `tests/simulation/test_departure_risks.py::test_a_year_inside_the_published_record_with_no_fitted_anchor_refuses_instead_of_falling_back`,
and that control was mutation-proven. All of that is sound and none of it is in question.

**The control is green at HEAD and red in this working tree, and has been from the instant it
landed.**

```
$ cd /tmp/headchk && git archive HEAD | tar -x   # clean extract of HEAD
$ python3 -B -m pytest tests/simulation/test_departure_risks.py -k no_fitted_anchor -q
1 passed, 21 deselected

$ cd /home/rich/synthetic-enterprise    # the shared tree
$ python3 -B -m pytest tests/simulation/test_departure_risks.py -k no_fitted_anchor -q
>           assert year_level_anchor(y) == YEAR_LEVEL_ANCHOR[y]
E           KeyError: 2016
1 failed, 1 passed, 20 deselected
```

The cause is not the guard and not the control. It is that this tree carries an **uncommitted
seven-year `YEAR_LEVEL_ANCHOR` block** where HEAD carries the committed ten-year one:

| | years | source |
|---|---|---|
| HEAD (`0e316d3e9`) | 2016–2025, all ten | committed since `71242c941` |
| this working tree | 2017–2021, 2023, 2024 — **2016, 2022, 2025 absent** | in **no commit** |

Checked, not assumed: `git log --all -S'4.547299' -- simulation/departure_level_anchor.py` and the
same for `0.364038` both return **nothing**, and a scan of every commit touching the file finds none
whose content matches the working tree's sha256 `1ece30c4…`. The block exists only here.

## Why nobody saw it, and why the grading could not have

**The tree was never written by the landing.**

```
$ stat -c '%y' simulation/departure_level_anchor.py
2026-08-31 20:14:35   # the guard landed 2026-09-01 19:44Z, twenty-three hours later
$ git worktree list
/home/rich/synthetic-enterprise   0e316d3e9 [main]
/var/tmp/se-ladder                2eeaa69ea (detached HEAD)      ... and five more
```

The landing lane worked in one of the sibling worktrees. HEAD moved out from under this checkout and
this checkout's copy of the file has not been touched since **2026-08-31 20:14:35** — which is also,
exactly, the content the native capture ran at 17:31Z: the working tree's sha256 is
`1ece30c41f3cec3c7a91f00e432b55013b4a7a92df82971f6b04034d1f117236`, byte-identical to
`PROVENANCE.txt`'s as-run entry. So this is **old content that HEAD has since superseded**, not new
work by a live lane.

**The grading's own constraint check therefore ran against a different tree than this one.** That
prereg certifies constraint 1 — *"no constant pasted, edited or deleted"* — with *"`git diff -U0`
filtered to `YEAR_LEVEL_ANCHOR` and any year line returns empty"*, and explicitly contrasts itself
with its two predecessors, which certified the same constraint *"by recalling what their author had
not done"*. Reading the artefact was the right instinct and it is the reason that grading is better
than the two before it. **But in this tree that check cannot return empty** — ten year-lines differ
from HEAD. The certification is true of the tree it was run in and false of the tree the world runs
from, and nothing in its wording says which tree it meant.

This is the catalogued class *a green test in the shared worktree measures several lanes, not your
change* — running the other way round. The usual failure is a tree that is greener than HEAD. Here
HEAD is greener than the tree, and a change proven correct at HEAD is red where the work happens.
**`G4`'s stated refuter, *"any red that is not present at clean HEAD"*, is exactly blind to this**:
it is the right refuter for a pre-existing red, and it cannot see a red that the change creates only
in composition with uncommitted work. G4 was named as the prediction its author was least sure of,
and it was refuted-shaped for a reason one step past the one it braced for.

## The forward hazard, which is worse than the red

The two halves are individually defensible and jointly fatal. Measured by composing HEAD's function
with this tree's block:

```
2016 -> ValueError: no fitted level anchor for 2016, which is INSIDE the published switching record (2016-2025)…
2022 -> ValueError: …
2025 -> ValueError: …
2024 -> 3.053619      # fitted, fine
2030 -> 3.053619      # outside the record, fallback preserved, fine
```

`year_level_anchor` is called on the **hot path of the run**, not in a report:
`simulation/customer_events.py:610`, and `simulation/run_phase2b.py:1634`, `:1667`, `:1719`, each on
`int(term_start_str[:4])`. The window is 2016–2025, so 2016, 2022 and 2025 term starts all occur.
**If the seven-year block is landed on top of the guard, `run_phase2b` raises mid-run on three of
the ten record years.**

And the two texts disagree in prose, which is how you can tell this is a real collision and not a
merge artefact. HEAD's docstring says a missing in-record year is *"a refusal and not a fallback"*.
The tree's docstring says *"TWO KINDS OF YEAR REACH THAT FALLBACK NOW … 2016, 2022 and 2025 are IN
the record and still land here"*. Each is internally consistent; they are opposite answers to one
question, and whichever lands second silently decides it.

## What I did NOT do, and why

**I did not touch `simulation/departure_level_anchor.py`.** The drawn pathspec for this stretch
nominally covers `simulation/`, and that is precisely the catalogued class *a drawn pathspec can be
the careless pathspec it warns about*. Three specific restraints:

1. **No `git checkout` and no `git show HEAD: >` over the file.** The seven-year block is in no
   commit; overwriting it destroys it irrecoverably. The red is reversible and visible, the deletion
   would not be. The house rule against `git stash`/`git checkout <path>` on this tree exists for
   exactly this.
2. **No reconciliation.** Keeping both halves — the guard plus the seven-year block — is the
   crashing state above. Choosing between them is a design decision belonging to the lane that fitted
   the block, on evidence about which capture the block should come from, and it is not mine to take
   by pathspec accident at 20:20Z.
3. **No constant adopted into `YEAR_LEVEL_ANCHOR`.** The standing constraint from all three preregs
   on this file is honoured by not touching the table, discharged by reading the artefact:
   `git status --porcelain simulation/departure_level_anchor.py` is ` M` (unstaged, unchanged by me)
   and it is excluded from this stretch's commit.

**So this stretch's pathspec is narrowed to this document alone**, and the narrowing is the finding's
point rather than an omission from it.

## What is owed next

1. **Decide the collision deliberately, in the lane that owns the fit.** Either the seven-year block
   is superseded — in which case this tree's copy should be brought to HEAD *by the lane that knows
   it is dead*, not by whoever commits `simulation/` next — or the block is live, in which case
   landing it requires answering what `year_level_anchor(2016 | 2022 | 2025)` should do, because the
   guard now makes that a crash rather than a silent 1.98x. **Until then every lane that commits a
   file selecting `tests/simulation/test_departure_risks.py` from this checkout is wedged on a red
   it did not cause.**
2. **A guard that a sibling worktree can arm is a shape, not an incident.** `9fd700366` is correct,
   proven, and made this tree red without touching it. Six worktrees share this repository and HEAD
   moves under all of them; a control keyed to agreement between a committed table and a committed
   record is silently keyed to *whichever copy of the table the runner has*. Whether that is worth a
   mechanism or only a habit is a separate judgement — filed here, not built here, because a control
   that only guards our own controls is usually not worth having.
3. **Unchanged from the two preregs and not re-derived:** the band control's emptied subject (7 years,
   not 8) is still red at HEAD and is still the only thing holding the level anchor accountable; and
   `tools/population_anchor.py`'s five 2022 consumers still resolve `.get("sim_churn_rate", 0.0)` to
   a published measured zero. Both remain outside this pathspec.
